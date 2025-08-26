import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from models import User, PaymentTransaction, AdminUser, SUBSCRIPTION_PLANS
from database import db_manager
from auth import AuthService
import secrets

class AdminService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def create_admin_user(self, email: str, password: str, role: str = "admin") -> AdminUser:
        """Create a new admin user"""
        # Check if admin already exists
        existing_admin = await self.get_admin_by_email(email)
        if existing_admin:
            raise ValueError("Admin user already exists")
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create admin user
        admin = AdminUser(
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        # Save to database
        admin_dict = admin.dict()
        result = db_manager.db.admin_users.insert_one(admin_dict)
        
        self.logger.info(f"Created admin user: {email}")
        return admin
    
    async def get_admin_by_email(self, email: str) -> Optional[AdminUser]:
        """Get admin user by email"""
        admin_data = db_manager.db.admin_users.find_one({"email": email})
        return AdminUser(**admin_data) if admin_data else None
    
    async def authenticate_admin(self, email: str, password: str) -> Optional[AdminUser]:
        """Authenticate admin user"""
        admin = await self.get_admin_by_email(email)
        if not admin or not AuthService.verify_password(password, admin.password_hash):
            return None
        
        # Update last login
        db_manager.db.admin_users.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return admin
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        try:
            # User statistics
            total_users = await db_manager.get_users_count()
            subscription_stats = await db_manager.get_subscription_stats()
            revenue_stats = await db_manager.get_revenue_stats()
            
            # Calculate growth metrics
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_users_30d = db_manager.db.users.count_documents({
                "created_at": {"$gte": thirty_days_ago}
            })
            
            # Active users (logged in within 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            active_users = db_manager.db.users.count_documents({
                "last_login": {"$gte": seven_days_ago}
            })
            
            # Revenue this month
            first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_revenue = list(db_manager.db.payment_transactions.aggregate([
                {
                    "$match": {
                        "payment_status": "paid",
                        "created_at": {"$gte": first_of_month}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]))
            
            monthly_revenue_data = monthly_revenue[0] if monthly_revenue else {"total": 0, "count": 0}
            
            # Churn rate (users whose subscriptions expired in last 30 days)
            expired_users = db_manager.db.users.count_documents({
                "subscription_status": "inactive",
                "subscription_end_date": {"$gte": thirty_days_ago}
            })
            
            churn_rate = (expired_users / max(total_users, 1)) * 100
            
            return {
                "overview": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "new_users_30d": new_users_30d,
                    "total_revenue": revenue_stats.get("total_revenue", 0),
                    "monthly_revenue": monthly_revenue_data["total"],
                    "monthly_transactions": monthly_revenue_data["count"],
                    "churn_rate": round(churn_rate, 2)
                },
                "subscriptions": {
                    "trial": subscription_stats.get("trial", 0),
                    "active": subscription_stats.get("active", 0),
                    "inactive": subscription_stats.get("inactive", 0),
                    "cancelled": subscription_stats.get("cancelled", 0)
                },
                "plans": {
                    "basic_users": db_manager.db.users.count_documents({"subscription_tier": "basic"}),
                    "premium_users": db_manager.db.users.count_documents({"subscription_tier": "premium"})
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard stats: {e}")
            raise
    
    async def get_users_list(self, skip: int = 0, limit: int = 50, search: str = None) -> Dict[str, Any]:
        """Get paginated list of users with search"""
        try:
            # Build query
            query = {}
            if search:
                query["$or"] = [
                    {"email": {"$regex": search, "$options": "i"}},
                    {"id": {"$regex": search, "$options": "i"}}
                ]
            
            # Get users
            users_cursor = db_manager.db.users.find(query).skip(skip).limit(limit).sort("created_at", -1)
            users = []
            
            for user_data in users_cursor:
                user = User(**user_data)
                
                # Calculate trial/subscription remaining days
                remaining_days = 0
                if user.subscription_status == "trial" and user.trial_end_date:
                    remaining_days = max(0, (user.trial_end_date - datetime.utcnow()).days)
                elif user.subscription_status == "active" and user.subscription_end_date:
                    remaining_days = max(0, (user.subscription_end_date - datetime.utcnow()).days)
                
                users.append({
                    "id": user.id,
                    "email": user.email,
                    "tenant_id": user.tenant_id,
                    "subscription_tier": user.subscription_tier,
                    "subscription_status": user.subscription_status,
                    "remaining_days": remaining_days,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                    "is_active": user.is_active
                })
            
            # Get total count
            total_count = db_manager.db.users.count_documents(query)
            
            return {
                "users": users,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count
            }
            
        except Exception as e:
            self.logger.error(f"Error getting users list: {e}")
            raise
    
    async def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get detailed user information"""
        try:
            user = await db_manager.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get user's transactions
            transactions = list(db_manager.db.payment_transactions.find({
                "user_id": user_id
            }).sort("created_at", -1).limit(10))
            
            # Get user's activity stats
            chat_sessions_count = db_manager.db.chat_sessions.count_documents({
                "tenant_id": user.tenant_id,
                "user_id": user_id
            })
            
            shopping_lists_count = db_manager.db.shopping_lists.count_documents({
                "tenant_id": user.tenant_id,
                "user_id": user_id
            })
            
            restaurants_count = db_manager.db.restaurants.count_documents({
                "tenant_id": user.tenant_id
            })
            
            return {
                "user": user.dict(),
                "activity": {
                    "chat_sessions": chat_sessions_count,
                    "shopping_lists": shopping_lists_count,
                    "restaurants_searched": restaurants_count
                },
                "transactions": [
                    {
                        "id": tx["id"],
                        "amount": tx["amount"],
                        "currency": tx["currency"],
                        "status": tx["payment_status"],
                        "created_at": tx["created_at"]
                    } for tx in transactions
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user details: {e}")
            raise
    
    async def update_user_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Admin update user subscription"""
        try:
            return await db_manager.update_user_subscription(user_id, subscription_data)
        except Exception as e:
            self.logger.error(f"Error updating user subscription: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            return await db_manager.update_user(user_id, {
                "is_active": False,
                "subscription_status": "inactive"
            })
        except Exception as e:
            self.logger.error(f"Error deactivating user: {e}")
            raise
    
    async def get_revenue_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics for specified period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Daily revenue breakdown
            daily_revenue = list(db_manager.db.payment_transactions.aggregate([
                {
                    "$match": {
                        "payment_status": "paid",
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"},
                            "day": {"$dayOfMonth": "$created_at"}
                        },
                        "revenue": {"$sum": "$amount"},
                        "transactions": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]))
            
            # Plan-wise revenue
            plan_revenue = list(db_manager.db.payment_transactions.aggregate([
                {
                    "$match": {
                        "payment_status": "paid",
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$subscription_tier",
                        "revenue": {"$sum": "$amount"},
                        "transactions": {"$sum": 1}
                    }
                }
            ]))
            
            return {
                "period_days": days,
                "daily_revenue": daily_revenue,
                "plan_revenue": plan_revenue,
                "total_revenue": sum([day["revenue"] for day in daily_revenue]),
                "total_transactions": sum([day["transactions"] for day in daily_revenue])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting revenue analytics: {e}")
            raise
    
    async def export_user_data_admin(self, user_id: str) -> Dict[str, Any]:
        """Admin export user data (GDPR compliance)"""
        try:
            user = await db_manager.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            return await db_manager.export_user_data(user_id, user.tenant_id)
            
        except Exception as e:
            self.logger.error(f"Error exporting user data: {e}")
            raise
    
    async def delete_user_data_admin(self, user_id: str, confirmation_token: str) -> bool:
        """Admin delete user data (GDPR compliance)"""
        try:
            # Verify confirmation token (in production, implement proper token verification)
            if not confirmation_token or len(confirmation_token) < 32:
                raise ValueError("Invalid confirmation token")
            
            user = await db_manager.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            return await db_manager.delete_user_data(user_id, user.tenant_id)
            
        except Exception as e:
            self.logger.error(f"Error deleting user data: {e}")
            raise

# Global admin service instance
admin_service = AdminService()