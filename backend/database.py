import os
from pymongo import MongoClient
from typing import Dict, List, Optional, Any
from datetime import datetime
from models import User, PaymentTransaction, ChatSession, Restaurant, ShoppingList, APIUsage, AdminUser
import logging

# MongoDB Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'glucoplanner_saas')

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.setup_indexes()
        logging.info(f"Connected to MongoDB: {DB_NAME}")
    
    def setup_indexes(self):
        """Create necessary database indexes for performance and tenant isolation"""
        # Users collection indexes
        self.db.users.create_index("email", unique=True)
        self.db.users.create_index("tenant_id", unique=True)
        self.db.users.create_index("stripe_customer_id")
        self.db.users.create_index("subscription_status")
        
        # Payment transactions indexes
        self.db.payment_transactions.create_index("session_id", unique=True)
        self.db.payment_transactions.create_index("user_id")
        self.db.payment_transactions.create_index("tenant_id")
        self.db.payment_transactions.create_index("payment_status")
        
        # Tenant-isolated collections indexes (CRITICAL for performance)
        self.db.chat_sessions.create_index([("tenant_id", 1), ("user_id", 1)])
        self.db.restaurants.create_index([("tenant_id", 1), ("place_id", 1)])
        self.db.shopping_lists.create_index([("tenant_id", 1), ("user_id", 1)])
        self.db.api_usage.create_index([("tenant_id", 1), ("service", 1)])
        
        # Admin collection indexes
        self.db.admin_users.create_index("email", unique=True)
        
        logging.info("Database indexes created successfully")
    
    # User Management
    async def create_user(self, user: User) -> User:
        """Create a new user with tenant isolation"""
        user_dict = user.dict()
        result = self.db.users.insert_one(user_dict)
        user.id = str(result.inserted_id) if hasattr(result, 'inserted_id') else user.id
        logging.info(f"Created user: {user.email} with tenant_id: {user.tenant_id}")
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = self.db.users.find_one({"email": email})
        return User(**user_data) if user_data else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = self.db.users.find_one({"id": user_id})
        return User(**user_data) if user_data else None
    
    async def get_user_by_tenant_id(self, tenant_id: str) -> Optional[User]:
        """Get user by tenant ID"""
        user_data = self.db.users.find_one({"tenant_id": tenant_id})
        return User(**user_data) if user_data else None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        updates["updated_at"] = datetime.utcnow()
        result = self.db.users.update_one({"id": user_id}, {"$set": updates})
        return result.modified_count > 0
    
    async def update_user_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Update user subscription information"""
        updates = {
            "subscription_status": subscription_data.get("status", "active"),
            "subscription_tier": subscription_data.get("tier", "basic"),
            "stripe_customer_id": subscription_data.get("customer_id"),
            "stripe_subscription_id": subscription_data.get("subscription_id"),
            "subscription_end_date": subscription_data.get("end_date"),
            "updated_at": datetime.utcnow()
        }
        result = self.db.users.update_one({"id": user_id}, {"$set": updates})
        return result.modified_count > 0
    
    # Payment Transaction Management
    async def create_payment_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """Create a new payment transaction"""
        transaction_dict = transaction.dict()
        result = self.db.payment_transactions.insert_one(transaction_dict)
        logging.info(f"Created payment transaction: {transaction.session_id}")
        return transaction
    
    async def get_payment_transaction_by_session(self, session_id: str) -> Optional[PaymentTransaction]:
        """Get payment transaction by session ID"""
        transaction_data = self.db.payment_transactions.find_one({"session_id": session_id})
        return PaymentTransaction(**transaction_data) if transaction_data else None
    
    async def update_payment_transaction(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update payment transaction"""
        updates["updated_at"] = datetime.utcnow()
        result = self.db.payment_transactions.update_one(
            {"session_id": session_id}, 
            {"$set": updates}
        )
        return result.modified_count > 0
    
    # Tenant-Isolated Data Operations (CRITICAL SECURITY)
    async def create_chat_session(self, chat_session: ChatSession, tenant_id: str) -> ChatSession:
        """Create chat session with tenant isolation"""
        chat_session.tenant_id = tenant_id  # Ensure tenant isolation
        chat_dict = chat_session.dict()
        self.db.chat_sessions.insert_one(chat_dict)
        return chat_session
    
    async def get_chat_sessions(self, user_id: str, tenant_id: str) -> List[ChatSession]:
        """Get chat sessions for user with tenant isolation"""
        sessions = self.db.chat_sessions.find({
            "tenant_id": tenant_id,
            "user_id": user_id
        }).sort("created_at", -1)
        return [ChatSession(**session) for session in sessions]
    
    async def update_chat_session(self, session_id: str, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update chat session with tenant isolation"""
        updates["updated_at"] = datetime.utcnow()
        result = self.db.chat_sessions.update_one(
            {"id": session_id, "tenant_id": tenant_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def create_restaurant(self, restaurant: Restaurant, tenant_id: str) -> Restaurant:
        """Create restaurant with tenant isolation"""
        restaurant.tenant_id = tenant_id
        restaurant_dict = restaurant.dict()
        self.db.restaurants.insert_one(restaurant_dict)
        return restaurant
    
    async def get_restaurants(self, tenant_id: str, limit: int = 50) -> List[Restaurant]:
        """Get restaurants with tenant isolation"""
        restaurants = self.db.restaurants.find({"tenant_id": tenant_id}).limit(limit)
        return [Restaurant(**restaurant) for restaurant in restaurants]
    
    async def create_shopping_list(self, shopping_list: ShoppingList, tenant_id: str) -> ShoppingList:
        """Create shopping list with tenant isolation"""
        shopping_list.tenant_id = tenant_id
        list_dict = shopping_list.dict()
        self.db.shopping_lists.insert_one(list_dict)
        return shopping_list
    
    async def get_shopping_lists(self, user_id: str, tenant_id: str) -> List[ShoppingList]:
        """Get shopping lists with tenant isolation"""
        lists = self.db.shopping_lists.find({
            "tenant_id": tenant_id,
            "user_id": user_id
        }).sort("created_at", -1)
        return [ShoppingList(**list_item) for list_item in lists]
    
    async def get_api_usage(self, tenant_id: str, service: str) -> Optional[APIUsage]:
        """Get API usage with tenant isolation"""
        usage_data = self.db.api_usage.find_one({
            "tenant_id": tenant_id,
            "service": service
        })
        return APIUsage(**usage_data) if usage_data else None
    
    async def update_api_usage(self, tenant_id: str, service: str, calls_made: int) -> bool:
        """Update API usage with tenant isolation"""
        result = self.db.api_usage.update_one(
            {"tenant_id": tenant_id, "service": service},
            {
                "$set": {"calls_made": calls_made, "updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    # Admin Operations
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users for admin dashboard"""
        users = self.db.users.find().skip(skip).limit(limit).sort("created_at", -1)
        return [User(**user) for user in users]
    
    async def get_users_count(self) -> int:
        """Get total users count"""
        return self.db.users.count_documents({})
    
    async def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics"""
        pipeline = [
            {"$group": {
                "_id": "$subscription_status",
                "count": {"$sum": 1}
            }}
        ]
        stats = list(self.db.users.aggregate(pipeline))
        return {stat["_id"]: stat["count"] for stat in stats}
    
    async def get_revenue_stats(self) -> Dict[str, Any]:
        """Get revenue statistics"""
        pipeline = [
            {"$match": {"payment_status": "paid"}},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1}
            }}
        ]
        stats = list(self.db.payment_transactions.aggregate(pipeline))
        return stats[0] if stats else {"total_revenue": 0, "transaction_count": 0}
    
    # GDPR/HIPAA Compliance
    async def export_user_data(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        user_data = self.db.users.find_one({"id": user_id, "tenant_id": tenant_id})
        chat_sessions = list(self.db.chat_sessions.find({"tenant_id": tenant_id, "user_id": user_id}))
        shopping_lists = list(self.db.shopping_lists.find({"tenant_id": tenant_id, "user_id": user_id}))
        restaurants = list(self.db.restaurants.find({"tenant_id": tenant_id}))
        
        return {
            "user_profile": user_data,
            "chat_sessions": chat_sessions,
            "shopping_lists": shopping_lists,
            "restaurants": restaurants,
            "exported_at": datetime.utcnow().isoformat()
        }
    
    async def delete_user_data(self, user_id: str, tenant_id: str) -> bool:
        """Delete all user data for GDPR compliance"""
        try:
            # Delete all tenant-isolated data
            self.db.chat_sessions.delete_many({"tenant_id": tenant_id, "user_id": user_id})
            self.db.shopping_lists.delete_many({"tenant_id": tenant_id, "user_id": user_id})
            self.db.restaurants.delete_many({"tenant_id": tenant_id})
            self.db.api_usage.delete_many({"tenant_id": tenant_id})
            
            # Delete user account
            self.db.users.delete_one({"id": user_id, "tenant_id": tenant_id})
            
            logging.info(f"Deleted all data for user: {user_id}, tenant: {tenant_id}")
            return True
        except Exception as e:
            logging.error(f"Error deleting user data: {e}")
            return False

# Global database instance
db_manager = DatabaseManager()