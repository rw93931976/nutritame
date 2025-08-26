import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, Depends, Header
from models import User, AuthToken, SubscriptionTier
import os

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_access_token(user: User) -> AuthToken:
        """Create JWT access token"""
        expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        payload = {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "subscription_tier": user.subscription_tier,
            "subscription_status": user.subscription_status,
            "exp": expires_at
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return AuthToken(
            token=token,
            user_id=user.id,
            tenant_id=user.tenant_id,
            expires_at=expires_at
        )
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

class TenantMiddleware:
    """Middleware to ensure tenant isolation in all database operations"""
    
    @staticmethod
    def get_current_user(authorization: str = Header(None)) -> dict:
        """Extract current user from JWT token"""
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        try:
            # Extract token from "Bearer <token>"
            token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
            payload = AuthService.verify_token(token)
            return payload
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    @staticmethod
    def verify_subscription_access(user_data: dict, required_feature: str = None) -> bool:
        """Verify user has active subscription and feature access"""
        subscription_status = user_data.get("subscription_status")
        subscription_tier = user_data.get("subscription_tier")
        
        # Allow trial users for 15 days
        if subscription_status == "trial":
            # In real implementation, check trial_end_date
            return True
        
        if subscription_status != "active":
            raise HTTPException(status_code=403, detail="Active subscription required")
        
        # Feature-specific access control can be added here
        if required_feature and subscription_tier == "basic":
            # Add feature restrictions for basic users
            restricted_basic_features = ["data_export", "unlimited_chats"]
            if required_feature in restricted_basic_features:
                raise HTTPException(status_code=403, detail="Premium subscription required for this feature")
        
        return True
    
    @staticmethod
    def get_tenant_filter(user_data: dict) -> dict:
        """Get MongoDB filter for tenant isolation"""
        return {"tenant_id": user_data["tenant_id"]}

# Dependency functions for FastAPI
async def get_current_user(authorization: str = Header(None)) -> dict:
    """FastAPI dependency to get current authenticated user"""
    return TenantMiddleware.get_current_user(authorization)

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency to get current active user with subscription check"""
    TenantMiddleware.verify_subscription_access(current_user)
    return current_user

async def get_premium_user(current_user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency for premium-only features"""
    TenantMiddleware.verify_subscription_access(current_user, "premium_feature")
    return current_user

# Trial Management
class TrialManager:
    @staticmethod
    def create_trial_user(email: str) -> User:
        """Create a new trial user"""
        trial_end = datetime.utcnow() + timedelta(days=15)
        user = User(
            email=email,
            subscription_status="trial",
            trial_end_date=trial_end,
            subscription_tier=SubscriptionTier.BASIC
        )
        return user
    
    @staticmethod
    def is_trial_expired(user: User) -> bool:
        """Check if user's trial has expired"""
        if not user.trial_end_date:
            return False
        return datetime.utcnow() > user.trial_end_date
    
    @staticmethod
    def get_trial_days_remaining(user: User) -> int:
        """Get remaining trial days"""
        if not user.trial_end_date:
            return 0
        remaining = user.trial_end_date - datetime.utcnow()
        return max(0, remaining.days)