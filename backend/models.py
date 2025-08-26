from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Subscription Tiers
class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"

# User Authentication Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    tenant_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscription_tier: SubscriptionTier = SubscriptionTier.BASIC
    subscription_status: str = "trial"  # trial, active, inactive, cancelled
    trial_end_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    # Profile data (tenant-isolated)
    age: Optional[int] = None
    gender: Optional[str] = None
    diabetes_type: Optional[str] = None
    activity_level: Optional[str] = None
    health_goals: Optional[List[str]] = []
    food_preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    cooking_skill: Optional[str] = None
    phone_number: Optional[str] = None

# Payment Transaction Model
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    payment_id: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    tenant_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    subscription_tier: SubscriptionTier
    payment_status: str = "pending"  # pending, paid, failed, expired
    status: str = "initiated"  # initiated, completed, cancelled
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Chat Session Model (Tenant-Isolated)
class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str  # CRITICAL: Always required for data isolation
    user_id: str
    messages: List[Dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Restaurant Model (Tenant-Isolated)
class Restaurant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str  # CRITICAL: Always required for data isolation
    place_id: str
    name: str
    address: str
    rating: Optional[float] = None
    price_level: Optional[int] = None
    latitude: float
    longitude: float
    phone_number: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Shopping List Model (Tenant-Isolated)
class ShoppingList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str  # CRITICAL: Always required for data isolation
    user_id: str
    title: str
    items: List[Dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# API Usage Tracking (Tenant-Isolated)
class APIUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str  # CRITICAL: Always required for data isolation
    service: str
    calls_made: int = 0
    monthly_limit: int
    last_reset: datetime = Field(default_factory=datetime.utcnow)

# Admin Models
class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    role: str = "admin"  # admin, super_admin
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

# Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic Plan",
        "price": 9.00,
        "currency": "usd",
        "interval": "month",
        "features": [
            "AI Health Coach",
            "Basic Restaurant Search",
            "Shopping Lists",
            "5 chat sessions per day"
        ],
        "limits": {
            "daily_chat_sessions": 5,
            "restaurant_searches_per_day": 10,
            "shopping_lists": 5
        }
    },
    "premium": {
        "name": "Premium Plan", 
        "price": 19.00,
        "currency": "usd",
        "interval": "month",
        "features": [
            "AI Health Coach",
            "Advanced Restaurant Search",
            "Unlimited Shopping Lists",
            "Unlimited chat sessions",
            "Recipe favorites",
            "Export data",
            "Priority support"
        ],
        "limits": {
            "daily_chat_sessions": -1,  # unlimited
            "restaurant_searches_per_day": -1,  # unlimited
            "shopping_lists": -1  # unlimited
        }
    }
}

# Request/Response Models
class SubscriptionRequest(BaseModel):
    plan: SubscriptionTier
    origin_url: str

class UserRegistrationResponse(BaseModel):
    user: User
    checkout_url: str
    session_id: str

class AuthToken(BaseModel):
    token: str
    user_id: str
    tenant_id: str
    expires_at: datetime

# GDPR/HIPAA Compliance Models
class DataExportRequest(BaseModel):
    user_id: str
    tenant_id: str
    export_type: str = "full"  # full, chat_history, profile_only

class DataDeletionRequest(BaseModel):
    user_id: str
    tenant_id: str
    deletion_type: str = "full"  # full, chat_history, profile_only
    confirmation_token: str