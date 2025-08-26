import os
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from models import PaymentTransaction, User, SubscriptionTier, SUBSCRIPTION_PLANS
from database import db_manager
from auth import TrialManager

class PaymentService:
    def __init__(self):
        self.stripe_api_key = os.environ.get('STRIPE_API_KEY')
        if not self.stripe_api_key:
            raise ValueError("STRIPE_API_KEY environment variable is required")
        
        self.checkout = None
        logging.info("PaymentService initialized")
    
    def _get_stripe_checkout(self, host_url: str) -> StripeCheckout:
        """Initialize Stripe checkout with webhook URL"""
        webhook_url = f"{host_url.rstrip('/')}/api/webhook/stripe"
        return StripeCheckout(api_key=self.stripe_api_key, webhook_url=webhook_url)
    
    async def create_subscription_checkout(
        self, 
        email: str, 
        plan: SubscriptionTier, 
        origin_url: str,
        host_url: str
    ) -> Tuple[CheckoutSessionResponse, PaymentTransaction]:
        """Create Stripe checkout session for subscription"""
        
        # Get plan configuration
        plan_config = SUBSCRIPTION_PLANS.get(plan.value)
        if not plan_config:
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        # Create trial user
        user = TrialManager.create_trial_user(email)
        
        # Initialize Stripe checkout
        stripe_checkout = self._get_stripe_checkout(host_url)
        
        # Prepare checkout session request
        success_url = f"{origin_url.rstrip('/')}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url.rstrip('/')}/cancel"
        
        checkout_request = CheckoutSessionRequest(
            amount=plan_config["price"],
            currency=plan_config["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "tenant_id": user.tenant_id,
                "email": email,
                "subscription_tier": plan.value,
                "trial_user": "true"
            }
        )
        
        # Create checkout session
        try:
            session = await stripe_checkout.create_checkout_session(checkout_request)
            
            # Create payment transaction record
            transaction = PaymentTransaction(
                session_id=session.session_id,
                user_id=user.id,
                email=email,
                tenant_id=user.tenant_id,
                amount=plan_config["price"],
                currency=plan_config["currency"],
                subscription_tier=plan,
                payment_status="pending",
                status="initiated",
                metadata={
                    "subscription_tier": plan.value,
                    "trial_user": "true",
                    "plan_name": plan_config["name"]
                }
            )
            
            # Save user and transaction to database
            await db_manager.create_user(user)
            await db_manager.create_payment_transaction(transaction)
            
            logging.info(f"Created checkout session for {email}: {session.session_id}")
            return session, transaction
            
        except Exception as e:
            logging.error(f"Error creating checkout session: {e}")
            raise HTTPException(status_code=500, detail="Failed to create checkout session")
    
    async def check_payment_status(self, session_id: str, host_url: str) -> Dict[str, Any]:
        """Check payment status and update user subscription"""
        
        # Get transaction from database
        transaction = await db_manager.get_payment_transaction_by_session(session_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Initialize Stripe checkout
        stripe_checkout = self._get_stripe_checkout(host_url)
        
        try:
            # Get status from Stripe
            checkout_status = await stripe_checkout.get_checkout_status(session_id)
            
            # Update transaction status
            status_updates = {
                "payment_status": checkout_status.payment_status,
                "status": checkout_status.status,
                "updated_at": datetime.utcnow()
            }
            
            await db_manager.update_payment_transaction(session_id, status_updates)
            
            # If payment successful and not already processed
            if (checkout_status.payment_status == "paid" and 
                transaction.payment_status != "paid"):
                
                await self._activate_subscription(transaction, checkout_status)
            
            return {
                "session_id": session_id,
                "payment_status": checkout_status.payment_status,
                "status": checkout_status.status,
                "amount_total": checkout_status.amount_total,
                "currency": checkout_status.currency,
                "subscription_tier": transaction.subscription_tier,
                "user_id": transaction.user_id,
                "tenant_id": transaction.tenant_id
            }
            
        except Exception as e:
            logging.error(f"Error checking payment status: {e}")
            raise HTTPException(status_code=500, detail="Failed to check payment status")
    
    async def _activate_subscription(self, transaction: PaymentTransaction, checkout_status: CheckoutStatusResponse):
        """Activate user subscription after successful payment"""
        
        try:
            # Calculate subscription end date (1 month from now)
            subscription_end = datetime.utcnow() + timedelta(days=30)
            
            # Update user subscription
            subscription_updates = {
                "subscription_status": "active",
                "subscription_tier": transaction.subscription_tier,
                "subscription_end_date": subscription_end,
                "stripe_customer_id": checkout_status.metadata.get("customer_id"),
                "trial_end_date": None,  # Clear trial
                "updated_at": datetime.utcnow()
            }
            
            await db_manager.update_user_subscription(transaction.user_id, subscription_updates)
            
            logging.info(f"Activated subscription for user: {transaction.user_id}")
            
        except Exception as e:
            logging.error(f"Error activating subscription: {e}")
            raise
    
    async def handle_webhook(self, request: Request) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        try:
            # Get request body and signature
            body = await request.body()
            signature = request.headers.get("Stripe-Signature")
            
            if not signature:
                raise HTTPException(status_code=400, detail="Missing Stripe signature")
            
            # Initialize Stripe checkout with dummy host (webhook URL not used here)
            stripe_checkout = self._get_stripe_checkout("https://dummy.com")
            
            # Handle webhook
            webhook_response = await stripe_checkout.handle_webhook(body, signature)
            
            # Process webhook event
            if webhook_response.event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
                await self._process_successful_payment_webhook(webhook_response)
            elif webhook_response.event_type in ["invoice.payment_failed", "customer.subscription.deleted"]:
                await self._process_failed_payment_webhook(webhook_response)
            
            logging.info(f"Processed webhook event: {webhook_response.event_type}")
            return {"status": "success", "event_type": webhook_response.event_type}
            
        except Exception as e:
            logging.error(f"Webhook processing error: {e}")
            raise HTTPException(status_code=400, detail="Webhook processing failed")
    
    async def _process_successful_payment_webhook(self, webhook_response):
        """Process successful payment webhook"""
        session_id = webhook_response.session_id
        
        # Get transaction
        transaction = await db_manager.get_payment_transaction_by_session(session_id)
        if not transaction:
            logging.warning(f"Transaction not found for webhook session: {session_id}")
            return
        
        # Update transaction if not already processed
        if transaction.payment_status != "paid":
            await db_manager.update_payment_transaction(session_id, {
                "payment_status": "paid",
                "status": "completed"
            })
            
            # Activate subscription
            checkout_status = CheckoutStatusResponse(
                status="completed",
                payment_status="paid",
                amount_total=int(transaction.amount * 100),  # Convert to cents
                currency=transaction.currency,
                metadata=webhook_response.metadata
            )
            
            await self._activate_subscription(transaction, checkout_status)
    
    async def _process_failed_payment_webhook(self, webhook_response):
        """Process failed payment webhook"""
        session_id = webhook_response.session_id
        
        # Update transaction status
        if session_id:
            await db_manager.update_payment_transaction(session_id, {
                "payment_status": "failed",
                "status": "failed"
            })
    
    async def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Get subscription information for user"""
        user = await db_manager.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        plan_config = SUBSCRIPTION_PLANS.get(user.subscription_tier.value, {})
        
        # Calculate trial/subscription remaining days
        remaining_days = 0
        if user.subscription_status == "trial" and user.trial_end_date:
            remaining_days = max(0, (user.trial_end_date - datetime.utcnow()).days)
        elif user.subscription_status == "active" and user.subscription_end_date:
            remaining_days = max(0, (user.subscription_end_date - datetime.utcnow()).days)
        
        return {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "subscription_tier": user.subscription_tier,
            "subscription_status": user.subscription_status,
            "remaining_days": remaining_days,
            "plan_name": plan_config.get("name", "Unknown"),
            "plan_price": plan_config.get("price", 0),
            "plan_features": plan_config.get("features", []),
            "plan_limits": plan_config.get("limits", {}),
            "trial_end_date": user.trial_end_date,
            "subscription_end_date": user.subscription_end_date
        }

# Global payment service instance
payment_service = PaymentService()