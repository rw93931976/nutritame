from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables FIRST before any other imports
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header, Form
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import httpx
import json
import asyncio
import phonenumbers
from phonenumbers import NumberParseException

# SaaS imports
from models import (
    User, PaymentTransaction, SubscriptionTier, SubscriptionRequest, 
    UserRegistrationResponse, SUBSCRIPTION_PLANS, DataExportRequest, DataDeletionRequest
)
from database import db_manager
from auth import AuthService, TenantMiddleware, get_current_user, get_current_active_user, get_premium_user, TrialManager
from payment_service import payment_service
from admin_service import admin_service

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Demo Mode Configuration
DEMO_MODE = os.environ.get('DEMO_MODE', 'true').lower() == 'true'
LAUNCH_DATE = os.environ.get('LAUNCH_DATE', '2025-02-01')  # Set your launch date

# AI Health Coach Configuration
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4o-mini') 
FEATURE_COACH = os.environ.get('FEATURE_COACH', 'true').lower() == 'true'
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Plan limits
STANDARD_CONSULTATION_LIMIT = 10
PREMIUM_CONSULTATION_LIMIT = -1  # Unlimited

# Create the main app
app = FastAPI(title="GlucoPlanner SaaS", version="2.0.0")

# Initialize SaaS on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin user"""
    try:
        # Create default admin user (change password in production!)
        try:
            await admin_service.create_admin_user(
                email="admin@glucoplanner.com",
                password="admin123",  # CHANGE IN PRODUCTION!
                role="super_admin"
            )
            logging.info("Default admin user created")
        except ValueError:
            logging.info("Admin user already exists")
        
        logging.info("GlucoPlanner SaaS started successfully")
    except Exception as e:
        logging.error(f"Startup error: {e}")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Health Coach System Prompt
HEALTH_COACH_PROMPT = """You are a knowledgeable and motivating AI health coach specializing in nutrition for people with diabetes. You combine the expertise of a registered dietitian with over 10 years of experience and a deep understanding of diabetes management. You don't just provide accurate, evidence-based meal plans—you inspire users to take control of their health. Your approach is supportive, practical, and empowering, helping users feel confident in managing blood sugar, discovering enjoyable foods, and building healthy habits that last.

RESPONSE FORMATTING RULES:
- NEVER use markdown formatting (no *, #, **, ##, etc.)
- Use clear, simple text with line breaks for readability
- Use numbered lists (1., 2., 3.) for steps or recommendations
- Use bullet points with dashes (-) for lists
- Keep paragraphs short and easy to scan
- Use conversational, friendly language
- Always end meal planning responses with: "Would you like me to create a shopping list for these meals?"

MEASUREMENT SYSTEM:
- ALWAYS use Imperial measurements (US system)
- Use cups, tablespoons, teaspoons for volume
- Use pounds (lbs), ounces (oz) for weight
- Use inches, feet for length/size
- Examples: "1 cup cooked brown rice", "4 oz grilled chicken", "2 tablespoons olive oil"
- For portions: "1/2 cup", "1/4 cup", "3 oz serving"
- Never use grams, kilograms, liters, or milliliters

OBJECTIVE: To create simple, enjoyable, and practical meal plans that fit seamlessly into a person's daily life while supporting healthy blood sugar management. The plans should focus on foods the user actually likes, easy preparation methods, and flexible options that reduce stress around eating. The goal is to make living with diabetes feel less restrictive and more empowering, helping users build confidence and consistency in their everyday choices.

CONTEXT: Users of this app may have Type 1 or Type 2 diabetes and are looking for meal guidance that feels realistic and supportive. They may struggle with knowing what to eat, balancing meals, managing blood sugar spikes, or feeling restricted by their condition. Some may have additional goals like losing weight, maintaining energy, or eating with their family. The app should provide clear, trustworthy, and encouraging guidance that adapts to different lifestyles, food preferences, cultural traditions, and cooking skills. It should feel like a reliable partner that makes daily meal planning less stressful and more enjoyable.

INSTRUCTIONS:
1. Start with the user profile: Ask about diabetes type (Type 1, Type 2, prediabetes), age, gender, activity level, and any relevant health goals (e.g., weight loss, energy, blood sugar control). Identify food preferences, cultural traditions, allergies, dislikes, and cooking skill level.

2. Set daily nutrition goals: Determine calorie range if relevant. Balance macronutrients with an emphasis on managing carbohydrates. Recommend fiber-rich foods, lean proteins, healthy fats, and limited added sugars. Use imperial measurements for all portions.

3. Build the meal plan: Divide into meals and snacks that evenly space carbohydrate intake. Suggest realistic portion sizes with clear imperial examples (e.g., "1/2 cup cooked brown rice", "4 oz grilled salmon", "1 tablespoon almond butter"). Include variety and options to prevent monotony. Incorporate easy swaps (e.g., "If you don't like salmon, try 4 oz grilled chicken or 3/4 cup tofu").

4. Keep it practical: Suggest meals that can be prepared quickly or in advance. Offer grocery shopping tips and cost-conscious substitutions. Provide cooking guidance that matches the user's skill level. Always specify imperial measurements for ingredients.

5. Support and motivate: Use positive, encouraging language. Frame choices as flexible, not restrictive. Reinforce the benefits (steady energy, confidence, improved blood sugar control).

6. Provide education when helpful: Briefly explain why certain foods or combinations are recommended. Share strategies for dining out, handling cravings, or special occasions. Use imperial measurements when discussing portions.

7. Adapt and refine: Encourage feedback from the user. Adjust future meal plans based on what worked, what didn't, and evolving goals.

RESTAURANT AND NUTRITION ANALYSIS:
When users ask about restaurants or specific foods, provide detailed analysis including:
- Carbohydrate content and glycemic impact using imperial measurements
- Recommended portion sizes for diabetic management (e.g., "3-4 oz protein", "1/2 cup starch")
- Healthier preparation methods or alternatives
- Menu modifications to improve nutritional profile
- Blood sugar management tips for dining out

SHOPPING LIST FEATURE:
When providing meal plans, always offer to create a shopping list. If the user agrees, organize the shopping list by store sections using imperial measurements:
- Fresh Produce (e.g., "2 lbs broccoli", "1 lb carrots")
- Proteins (Meat/Fish/Dairy) (e.g., "1 lb chicken breast", "8 oz salmon filets")
- Pantry Items (e.g., "1 lb brown rice", "16 oz olive oil")
- Frozen Foods (e.g., "1 lb frozen berries")
- Other Items

PORTION SIZE EXAMPLES (Imperial Only):
- Protein: 3-4 oz (size of palm)
- Vegetables: 1-2 cups
- Grains/Starches: 1/3 to 1/2 cup cooked
- Fruits: 1 medium fruit or 1/2 cup
- Fats: 1-2 tablespoons
- Dairy: 1 cup milk or 1 oz cheese

NOTES:
- Always prioritize safety: never provide medical advice beyond nutrition and lifestyle support.
- Remind users to consult their healthcare provider before making major dietary changes.
- Avoid judgmental or negative language; focus on encouragement and empowerment.
- Be mindful of cultural sensitivity in food recommendations.
- Keep explanations simple and clear—avoid overly technical jargon unless the user requests detail.
- Offer flexibility: provide options so users can adapt meals to their preferences and circumstances.
- Ensure recommendations align with evidence-based diabetes nutrition guidelines.
- Maintain a motivational and supportive tone, celebrating small wins and progress.
- Ask clarifying questions if user information is incomplete, rather than making assumptions.
- Provide alternatives for users with limited time, skills, or food access.
- Do not diagnose conditions or recommend changes to medication—always direct users back to their healthcare team for medical decisions.
- ALWAYS use imperial measurements - never metric."""

# Pydantic Models
class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    diabetes_type: str  # "type1", "type2", "prediabetes"
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None  # "low", "moderate", "high"
    health_goals: List[str] = []  # ["weight_loss", "energy", "blood_sugar_control"]
    food_preferences: List[str] = []
    cultural_background: Optional[str] = None
    allergies: List[str] = []
    dislikes: List[str] = []
    cooking_skill: Optional[str] = None  # "beginner", "intermediate", "advanced"
    phone_number: Optional[str] = None  # For SMS notifications
    plan: str = "standard"  # "standard" or "premium" 
    consultation_count: int = 0
    consultation_month: Optional[str] = None  # YYYY-MM format
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserProfileCreate(BaseModel):
    diabetes_type: str
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    health_goals: List[str] = []
    food_preferences: List[str] = []
    cultural_background: Optional[str] = None
    allergies: List[str] = []
    dislikes: List[str] = []
    cooking_skill: Optional[str] = None
    phone_number: Optional[str] = None
    plan: str = "standard"  # Default to standard plan

class UserProfileUpdate(BaseModel):
    diabetes_type: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    health_goals: Optional[List[str]] = None
    food_preferences: Optional[List[str]] = None
    cultural_background: Optional[str] = None
    allergies: Optional[List[str]] = None
    dislikes: Optional[List[str]] = None
    cooking_skill: Optional[str] = None
    phone_number: Optional[str] = None
    plan: Optional[str] = None  # Allow plan updates

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    message: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessageCreate(BaseModel):
    user_id: str
    message: str

# AI Health Coach Models
class CoachSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "New Conversation"
    disclaimer_accepted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CoachMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # "user", "assistant", "system"
    text: str
    tokens: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CoachMessageCreate(BaseModel):
    session_id: str
    message: str

class CoachSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = "New Conversation"

class ConsultationLimit(BaseModel):
    user_id: str
    consultation_count: int = 0
    consultation_month: str  # YYYY-MM format
    plan: str = "standard"  # "standard" or "premium"
    last_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DisclaimerAcceptance(BaseModel):
    user_id: str
    accepted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disclaimer_text: str

class ConsentLedger(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    disclaimer_version: str
    consent_source: str  # "global_screen", "demo_auto"
    is_demo: bool = False
    consented_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    consent_ui_hash: str
    signature: str  # HMAC signature for verification
    country: Optional[str] = None
    locale: Optional[str] = None
    user_agent: Optional[str] = None
    # No raw IP stored for privacy

class RestaurantSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: Optional[int] = 2000  # Default 2km radius
    keyword: Optional[str] = None
    cuisine_type: Optional[str] = None

class LocationSearchRequest(BaseModel):
    location: str  # Address or city name
    radius: Optional[int] = 2000
    keyword: Optional[str] = None
    cuisine_type: Optional[str] = None

class Restaurant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    price_level: Optional[int] = None
    cuisine_types: List[str] = []
    phone_number: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None
    photos: List[str] = []
    diabetic_friendly_score: Optional[float] = None
    cached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FoodNutrition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    food_name: str
    fdc_id: Optional[str] = None  # USDA FoodData Central ID
    description: Optional[str] = None
    brand_name: Optional[str] = None
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    carbohydrates: Optional[float] = None  # grams
    sugars: Optional[float] = None  # grams
    fiber: Optional[float] = None  # grams
    protein: Optional[float] = None  # grams
    fat: Optional[float] = None  # grams
    sodium: Optional[float] = None  # mg
    glycemic_index: Optional[int] = None
    diabetic_rating: Optional[str] = None  # "excellent", "good", "moderate", "caution"
    cached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RestaurantAnalysisRequest(BaseModel):
    user_id: str
    restaurant_place_id: str
    menu_items: Optional[List[str]] = []

class MealPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    meals: List[dict]  # Flexible structure for meals
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ShoppingListItem(BaseModel):
    item: str
    category: str  # "produce", "proteins", "pantry", "frozen", "other"
    quantity: Optional[str] = None
    checked: bool = False

class ShoppingList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    items: List[ShoppingListItem] = []
    meal_plan_reference: Optional[str] = None  # Reference to related meal plan
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ShoppingListCreate(BaseModel):
    user_id: str
    title: str
    items: List[ShoppingListItem] = []
    meal_plan_reference: Optional[str] = None

class ShoppingListUpdate(BaseModel):
    title: Optional[str] = None
    items: Optional[List[ShoppingListItem]] = None

class SMSMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    phone_number: str
    message_content: str
    message_type: str  # "restaurant_info", "meal_plan", "general"
    restaurant_data: Optional[dict] = None
    status: str = "sent"  # "sent", "delivered", "failed"
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SendSMSRequest(BaseModel):
    user_id: str
    phone_number: str
    restaurant_place_id: str

class MockSMSService:
    """Mock SMS service that simulates sending SMS messages"""
    
    def __init__(self):
        self.sent_messages = []
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format (simplified for mock)"""
        try:
            # Remove all non-digit characters except +
            cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Check basic format: starts with +1 and has 11 digits total
            if cleaned.startswith('+1') and len(cleaned) == 12:
                return True
            # Or just starts with 1 and has 11 digits
            elif cleaned.startswith('1') and len(cleaned) == 11:
                return True
            # Or has 10 digits (assume US)
            elif len(cleaned) == 10:
                return True
                
            return False
        except Exception:
            return False
    
    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number to E.164 format (simplified for mock)"""
        try:
            # Remove all non-digit characters except +
            cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            if cleaned.startswith('+1'):
                return cleaned
            elif cleaned.startswith('1') and len(cleaned) == 11:
                return '+' + cleaned
            elif len(cleaned) == 10:
                return '+1' + cleaned
            else:
                return phone_number
        except Exception:
            return phone_number
    
    async def send_restaurant_sms(self, phone_number: str, restaurant: dict) -> dict:
        """Send restaurant information via SMS (mock)"""
        try:
            # Format the restaurant message
            message = self._format_restaurant_message(restaurant)
            
            # Simulate SMS sending (in real implementation, this would call Twilio)
            mock_response = {
                "sid": f"SM{uuid.uuid4().hex[:32]}",
                "status": "sent",
                "to": self.format_phone_number(phone_number),
                "from": "+15551234567",  # Mock Twilio number
                "body": message,
                "date_sent": datetime.now(timezone.utc).isoformat()
            }
            
            # Store in mock sent messages
            self.sent_messages.append(mock_response)
            
            logging.info(f"Mock SMS sent to {phone_number}: {message[:100]}...")
            
            return {
                "success": True,
                "message_sid": mock_response["sid"],
                "status": "sent",
                "formatted_phone": mock_response["to"]
            }
            
        except Exception as e:
            logging.error(f"Mock SMS sending error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_restaurant_message(self, restaurant: dict) -> str:
        """Format restaurant information for SMS"""
        name = restaurant.get('name', 'Unknown Restaurant')
        address = restaurant.get('address', 'Address not available')
        rating = restaurant.get('rating', 'N/A')
        phone = restaurant.get('phone_number', 'Not available')
        diabetic_score = restaurant.get('diabetic_friendly_score', 0)
        
        # Create diabetic rating text
        if diabetic_score >= 4:
            diabetic_text = "Excellent for diabetics"
        elif diabetic_score >= 3:
            diabetic_text = "Good for diabetics"
        elif diabetic_score >= 2:
            diabetic_text = "Fair - use caution"
        else:
            diabetic_text = "Requires careful selection"
        
        message = f"""🍽️ GlucoPlanner Restaurant Info

{name}
📍 {address}
⭐ {rating}/5.0 Google Rating
📞 {phone}

🩺 Diabetic Score: {diabetic_score:.1f}/5.0
{diabetic_text}

Sent from GlucoPlanner - Your diabetic meal planning assistant"""
        
        return message

# Initialize mock SMS service
mock_sms_service = MockSMSService()

def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse MongoDB documents for Pydantic models"""
    if isinstance(item, dict):
        # Remove MongoDB's _id field to avoid conflicts with our UUID id field
        if '_id' in item:
            del item['_id']
            
        # Parse ISO string dates back to datetime objects
        for key, value in item.items():
            if key in ['created_at', 'timestamp', 'cached_at'] and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass  # Keep original value if parsing fails
    return item

# Google Places API Client with Rate Limiting and Geocoding
class GooglePlacesClient:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode"
        self.monthly_limit = 9000  # Set monthly limit to 9,000 calls
        self.daily_limit = 300     # Approximately 9,000 / 30 days
        
    async def geocode_location(self, location: str):
        """Convert location string to coordinates using Google Geocoding API"""
        # Check usage limits before making API call
        can_proceed, usage_message = await self._check_usage_limits()
        if not can_proceed:
            logging.error(f"API limit exceeded for geocoding: {usage_message}")
            return None
        
        # Clean and validate the location input
        location = location.strip()
        if not location:
            logging.error("Empty location provided for geocoding")
            return None
            
        async with httpx.AsyncClient() as client:
            params = {
                'address': location,
                'key': self.api_key
            }
            
            try:
                logging.info(f"Making Google Geocoding API request for: '{location}'")
                response = await client.get(f"{self.geocoding_url}/json", params=params)
                response.raise_for_status()
                
                # Increment usage counter for geocoding call
                await self._increment_usage()
                
                data = response.json()
                logging.info(f"Geocoding API response status: {data.get('status')}")
                
                if data.get('status') == 'OK' and data.get('results'):
                    result = data['results'][0]
                    geometry = result.get('geometry', {})
                    location_data = geometry.get('location', {})
                    formatted_address = result.get('formatted_address')
                    
                    logging.info(f"Geocoding successful: '{location}' -> '{formatted_address}' ({location_data.get('lat')}, {location_data.get('lng')})")
                    
                    return {
                        'latitude': location_data.get('lat'),
                        'longitude': location_data.get('lng'),
                        'formatted_address': formatted_address
                    }
                else:
                    error_msg = data.get('error_message', 'Unknown error')
                    logging.error(f"Geocoding failed for '{location}': {data.get('status')} - {error_msg}")
                    return None
                    
            except Exception as e:
                logging.error(f"Geocoding API error for '{location}': {e}")
                return None
        
    async def _check_usage_limits(self):
        """Check if we're within API usage limits"""
        try:
            # Get current month's usage from database
            current_month = datetime.now(timezone.utc).strftime("%Y-%m")
            usage_doc = await db.api_usage.find_one({
                "api": "google_places",
                "month": current_month
            })
            
            if not usage_doc:
                # Create new usage tracking document
                usage_doc = {
                    "api": "google_places", 
                    "month": current_month,
                    "calls_made": 0,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
                await db.api_usage.insert_one(usage_doc)
                
            calls_made = usage_doc.get('calls_made', 0)
            
            # STRICT CHECK: Block if we've reached exactly 9,000 calls
            # This check happens BEFORE incrementing, so if calls_made is 9000, we block the next call
            if calls_made >= self.monthly_limit:
                logging.warning(f"Monthly Google Places API limit reached: {calls_made}/{self.monthly_limit}")
                return False, f"Monthly API limit reached ({calls_made}/{self.monthly_limit}). Restaurant search disabled."
            
            # Check if approaching limit (90%)
            if calls_made >= (self.monthly_limit * 0.9):
                logging.warning(f"Approaching Google Places API monthly limit: {calls_made}/{self.monthly_limit}")
            
            return True, f"Usage: {calls_made}/{self.monthly_limit} calls this month"
            
        except Exception as e:
            logging.error(f"Error checking API usage: {e}")
            return True, "Usage check failed, proceeding"
    
    async def _increment_usage(self):
        """Increment API usage counter"""
        try:
            current_month = datetime.now(timezone.utc).strftime("%Y-%m")
            await db.api_usage.update_one(
                {"api": "google_places", "month": current_month},
                {
                    "$inc": {"calls_made": 1},
                    "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}
                },
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error incrementing API usage: {e}")
        
    async def search_restaurants(self, latitude: float, longitude: float, radius: int = 2000, keyword: str = None):
        """Search for restaurants using Google Places API with rate limiting"""
        # Check usage limits before making API call
        can_proceed, usage_message = await self._check_usage_limits()
        if not can_proceed:
            logging.error(f"API limit exceeded: {usage_message}")
            return []
        
        async with httpx.AsyncClient() as client:
            # Nearby search for restaurants
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'type': 'restaurant',
                'key': self.api_key
            }
            
            if keyword:
                params['keyword'] = f"{keyword} healthy diabetic-friendly low-carb"
            else:
                params['keyword'] = "healthy diabetic-friendly"
            
            try:
                logging.info(f"Making Google Places API request. {usage_message}")
                response = await client.get(f"{self.base_url}/nearbysearch/json", params=params)
                response.raise_for_status()
                
                # Increment usage counter
                await self._increment_usage()
                
                data = response.json()
                
                logging.info(f"Google Places API response status: {data.get('status')}")
                if data.get('status') != 'OK':
                    logging.error(f"Google Places API error: {data.get('error_message', data.get('status'))}")
                    return []
                
                restaurants = []
                for place in data.get('results', [])[:10]:  # Limit to 10 results
                    restaurant = await self._parse_place_data(place)
                    if restaurant:
                        restaurants.append(restaurant)
                
                logging.info(f"Successfully parsed {len(restaurants)} restaurants")
                return restaurants
            except Exception as e:
                logging.error(f"Google Places API error: {e}")
                return []
    
    async def get_restaurant_details(self, place_id: str):
        """Get detailed restaurant information with rate limiting"""
        # Check usage limits before making API call
        can_proceed, usage_message = await self._check_usage_limits()
        if not can_proceed:
            logging.error(f"API limit exceeded: {usage_message}")
            return None
            
        async with httpx.AsyncClient() as client:
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,geometry,rating,price_level,formatted_phone_number,website,opening_hours,photos,reviews',
                'key': self.api_key
            }
            
            try:
                logging.info(f"Making Google Places Details API request. {usage_message}")
                response = await client.get(f"{self.base_url}/details/json", params=params)
                response.raise_for_status()
                
                # Increment usage counter
                await self._increment_usage()
                
                data = response.json()
                
                if data.get('status') == 'OK':
                    return await self._parse_place_details(data['result'])
                return None
            except Exception as e:
                logging.error(f"Google Places Details API error: {e}")
                return None
    
    async def _parse_place_data(self, place_data):
        """Parse basic place data from search results"""
        try:
            location = place_data.get('geometry', {}).get('location', {})
            
            # Calculate diabetic-friendly score based on keywords and rating
            diabetic_score = self._calculate_diabetic_score(place_data)
            
            return Restaurant(
                place_id=place_data.get('place_id', ''),
                name=place_data.get('name', ''),
                address=place_data.get('vicinity', ''),
                latitude=location.get('lat', 0),
                longitude=location.get('lng', 0),
                rating=place_data.get('rating'),
                price_level=place_data.get('price_level'),
                cuisine_types=place_data.get('types', []),
                diabetic_friendly_score=diabetic_score
            )
        except Exception as e:
            logging.error(f"Error parsing place data: {e}")
            return None
    
    async def _parse_place_details(self, place_details):
        """Parse detailed place information"""
        try:
            location = place_details.get('geometry', {}).get('location', {})
            
            photos = []
            if place_details.get('photos'):
                for photo in place_details['photos'][:3]:  # Limit to 3 photos
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo['photo_reference']}&key={self.api_key}"
                    photos.append(photo_url)
            
            diabetic_score = self._calculate_diabetic_score(place_details)
            
            return Restaurant(
                place_id=place_details.get('place_id', ''),
                name=place_details.get('name', ''),
                address=place_details.get('formatted_address', ''),
                latitude=location.get('lat', 0),
                longitude=location.get('lng', 0),
                rating=place_details.get('rating'),
                price_level=place_details.get('price_level'),
                phone_number=place_details.get('formatted_phone_number'),
                website=place_details.get('website'),
                opening_hours=place_details.get('opening_hours'),
                photos=photos,
                diabetic_friendly_score=diabetic_score
            )
        except Exception as e:
            logging.error(f"Error parsing place details: {e}")
            return None
    
    def _calculate_diabetic_score(self, place_data):
        """Calculate how diabetic-friendly a restaurant might be"""
        score = 3.0  # Base score out of 5
        
        name = place_data.get('name', '').lower()
        types = [t.lower() for t in place_data.get('types', [])]
        
        # Positive indicators
        healthy_keywords = ['salad', 'grill', 'fresh', 'organic', 'healthy', 'mediterranean', 'vegetarian', 'bowl']
        for keyword in healthy_keywords:
            if keyword in name:
                score += 0.5
        
        # Restaurant types that are generally better for diabetics
        good_types = ['meal_takeaway', 'health', 'vegetarian_restaurant']
        for rtype in good_types:
            if rtype in types:
                score += 0.3
        
        # Negative indicators
        fast_food_keywords = ['mcdonald', 'burger', 'pizza', 'kfc', 'taco bell', 'subway']
        for keyword in fast_food_keywords:
            if keyword in name:
                score -= 1.0
        
        # Fast food types
        fast_food_types = ['meal_delivery', 'meal_takeaway']
        if any(t in types for t in fast_food_types) and 'healthy' not in name:
            score -= 0.5
        
        # Factor in rating
        rating = place_data.get('rating', 0)
        if rating >= 4.0:
            score += 0.3
        elif rating >= 3.5:
            score += 0.1
        
        return max(1.0, min(5.0, score))  # Keep between 1-5

# USDA FoodData Central API Client
class USDANutritionClient:
    def __init__(self):
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.api_key = os.environ.get('USDA_API_KEY')
        
    async def search_food(self, query: str):
        """Search for food items in USDA database"""
        async with httpx.AsyncClient() as client:
            params = {
                'query': query,
                'pageSize': 5,
                'api_key': self.api_key
            }
            
            try:
                response = await client.get(f"{self.base_url}/foods/search", params=params)
                response.raise_for_status()
                data = response.json()
                
                foods = []
                for food in data.get('foods', []):
                    nutrition = await self._parse_food_data(food)
                    if nutrition:
                        foods.append(nutrition)
                
                return foods
            except Exception as e:
                logging.error(f"USDA API error: {e}")
                return []
    
    async def get_food_details(self, fdc_id: str):
        """Get detailed nutrition information for a specific food"""
        async with httpx.AsyncClient() as client:
            params = {
                'api_key': self.api_key
            }
            
            try:
                response = await client.get(f"{self.base_url}/food/{fdc_id}", params=params)
                response.raise_for_status()
                food_data = response.json()
                
                return await self._parse_food_data(food_data)
            except Exception as e:
                logging.error(f"USDA Food Details API error: {e}")
                return None
    
    async def _parse_food_data(self, food_data):
        """Parse USDA food data into our nutrition model"""
        try:
            nutrients = {}
            for nutrient in food_data.get('foodNutrients', []):
                nutrient_name = nutrient.get('nutrientName', '').lower()
                nutrient_value = nutrient.get('value', 0)
                
                if 'carbohydrate' in nutrient_name:
                    nutrients['carbohydrates'] = nutrient_value
                elif 'sugars' in nutrient_name and 'added' not in nutrient_name:
                    nutrients['sugars'] = nutrient_value
                elif 'fiber' in nutrient_name:
                    nutrients['fiber'] = nutrient_value
                elif 'protein' in nutrient_name:
                    nutrients['protein'] = nutrient_value
                elif 'fat' in nutrient_name and 'total' in nutrient_name:
                    nutrients['fat'] = nutrient_value
                elif 'sodium' in nutrient_name:
                    nutrients['sodium'] = nutrient_value
                elif 'energy' in nutrient_name or 'calories' in nutrient_name:
                    nutrients['calories'] = nutrient_value
            
            # Calculate diabetic rating
            diabetic_rating = self._calculate_diabetic_rating(nutrients)
            
            return FoodNutrition(
                food_name=food_data.get('description', ''),
                fdc_id=str(food_data.get('fdcId', '')),
                description=food_data.get('description', ''),
                brand_name=food_data.get('brandOwner'),
                serving_size="3.5 oz (100g)",  # USDA data is per 100g, convert to imperial reference
                **nutrients,
                diabetic_rating=diabetic_rating
            )
        except Exception as e:
            logging.error(f"Error parsing USDA food data: {e}")
            return None
    
    def _calculate_diabetic_rating(self, nutrients):
        """Calculate diabetic appropriateness rating"""
        carbs = nutrients.get('carbohydrates', 0)
        fiber = nutrients.get('fiber', 0)
        sugars = nutrients.get('sugars', 0)
        
        # Net carbs calculation
        net_carbs = carbs - fiber if fiber else carbs
        
        # Rating based on net carbs and sugar content
        if net_carbs <= 5 and sugars <= 2:
            return "excellent"
        elif net_carbs <= 10 and sugars <= 5:
            return "good"
        elif net_carbs <= 20 and sugars <= 10:
            return "moderate"
        else:
            return "caution"

# Initialize API clients
google_places = GooglePlacesClient()
usda_nutrition = USDANutritionClient()

# =============================================
# AI HEALTH COACH HELPER FUNCTIONS
# =============================================

async def check_consultation_limit(user_id: str) -> dict:
    """Check if user has remaining consultations for the month"""
    try:
        # Get current month
        current_month = datetime.now().strftime("%Y-%m")
        
        # Get user's consultation data
        consultation_doc = await db.consultation_limits.find_one({"user_id": user_id})
        
        if not consultation_doc:
            # Create new consultation limit document
            consultation_doc = {
                "user_id": user_id,
                "consultation_count": 0,
                "consultation_month": current_month,
                "plan": "standard",  # Default plan
                "last_reset": datetime.now(timezone.utc)
            }
            await db.consultation_limits.insert_one(consultation_doc)
        
        # Reset count if new month
        if consultation_doc["consultation_month"] != current_month:
            consultation_doc["consultation_count"] = 0
            consultation_doc["consultation_month"] = current_month
            consultation_doc["last_reset"] = datetime.now(timezone.utc)
            await db.consultation_limits.update_one(
                {"user_id": user_id},
                {"$set": consultation_doc}
            )
        
        # Check limits based on plan
        plan = consultation_doc.get("plan", "standard")
        limit = STANDARD_CONSULTATION_LIMIT if plan == "standard" else PREMIUM_CONSULTATION_LIMIT
        current_count = consultation_doc["consultation_count"]
        
        can_use = limit == -1 or current_count < limit  # -1 means unlimited
        
        return {
            "can_use": can_use,
            "current_count": current_count,
            "limit": limit,
            "plan": plan,
            "remaining": limit - current_count if limit != -1 else -1
        }
        
    except Exception as e:
        logging.error(f"Error checking consultation limit: {e}")
        return {"can_use": False, "error": str(e)}

async def increment_consultation_count(user_id: str):
    """Increment user's consultation count"""
    try:
        current_month = datetime.now().strftime("%Y-%m")
        await db.consultation_limits.update_one(
            {"user_id": user_id},
            {
                "$inc": {"consultation_count": 1},
                "$set": {"consultation_month": current_month}
            },
            upsert=True
        )
        return True
    except Exception as e:
        logging.error(f"Error incrementing consultation count: {e}")
        return False

async def get_ai_response(message: str, user_id: str, session_id: str) -> str:
    """Get AI response using emergentintegrations with rate limiting and retry"""
    try:
        # Get user profile for context
        user_profile = await db.user_profiles.find_one({"id": user_id})
        user_context = ""
        
        if user_profile:
            user_context = f"""
User Profile Context:
- Diabetes Type: {user_profile.get('diabetes_type', 'Not specified')}
- Age: {user_profile.get('age', 'Not specified')}
- Gender: {user_profile.get('gender', 'Not specified')}
- Activity Level: {user_profile.get('activity_level', 'Not specified')}
- Health Goals: {', '.join(user_profile.get('health_goals', []))}
- Food Preferences: {', '.join(user_profile.get('food_preferences', []))}
- Cultural Background: {user_profile.get('cultural_background', 'Not specified')}
- Allergies: {', '.join(user_profile.get('allergies', []))}
- Dislikes: {', '.join(user_profile.get('dislikes', []))}
- Cooking Skill: {user_profile.get('cooking_skill', 'Not specified')}

"""
        
        # Initialize LLM chat with guardrail prompt and user context
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=f"{HEALTH_COACH_PROMPT}\n\n{user_context}"
        )
        
        # Configure model based on environment
        if LLM_PROVIDER == "openai":
            chat.with_model("openai", LLM_MODEL)
        elif LLM_PROVIDER == "anthropic":
            chat.with_model("anthropic", LLM_MODEL)
        elif LLM_PROVIDER == "google":
            chat.with_model("gemini", LLM_MODEL)
        
        # Create user message
        user_message = UserMessage(text=message)
        
        # Get response with retry logic
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = await chat.send_message(user_message)
                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.warning(f"AI response attempt {attempt + 1} failed: {e}, retrying in {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise e
                    
    except Exception as e:
        logging.error(f"Error getting AI response: {e}")
        # Fallback response
        return "I'm sorry, I'm having trouble connecting right now. Please try again in a moment. If the issue persists, please contact support."

async def check_disclaimer_acceptance(user_id: str) -> bool:
    """Check if user has accepted the disclaimer"""
    try:
        disclaimer_doc = await db.disclaimer_acceptances.find_one({"user_id": user_id})
        return disclaimer_doc is not None
    except Exception as e:
        logging.error(f"Error checking disclaimer acceptance: {e}")
        return False

async def save_disclaimer_acceptance(user_id: str):
    """Save user's disclaimer acceptance"""
    try:
        disclaimer_doc = {
            "user_id": user_id,
            "accepted_at": datetime.now(timezone.utc),
            "disclaimer_text": "Not a medical device. The AI Health Coach provides general nutrition guidance only and is not a substitute for professional medical advice. Always consult your healthcare provider."
        }
        await db.disclaimer_acceptances.insert_one(disclaimer_doc)
        return True
    except Exception as e:
        logging.error(f"Error saving disclaimer acceptance: {e}")
        return False

# =============================================
# DEMO MODE ENDPOINTS
# =============================================

@api_router.get("/demo/config")
async def get_demo_config():
    """Get demo mode configuration"""
    return {
        "demo_mode": DEMO_MODE,
        "launch_date": LAUNCH_DATE,
        "message": "Currently in demo mode - full access without account creation",
        "launch_requirements": {
            "account_required": True,
            "subscription_required": True,
            "basic_plan": "$9/month",
            "premium_plan": "$19/month",
            "free_trial": "15 days"
        }
    }

@api_router.post("/demo/access")
async def create_demo_access(demo_request: dict):
    """Create demo access without payment"""
    if not DEMO_MODE:
        raise HTTPException(status_code=403, detail="Demo mode is not enabled")
    
    try:
        # Generate unique email for demo if not provided or if provided email already exists
        provided_email = demo_request.get("email")
        if provided_email:
            # Check if user already exists
            existing_user = await db_manager.get_user_by_email(provided_email)
            if existing_user:
                # Return existing demo user if it's already a demo user
                if existing_user.subscription_tier == SubscriptionTier.PREMIUM and existing_user.subscription_status == "active":
                    token = AuthService.create_access_token(existing_user)
                    return {
                        "demo_access": True,
                        "access_token": token.token,
                        "user": existing_user,
                        "expires_at": token.expires_at,
                        "demo_notice": "Returning existing demo account with full premium access.",
                        "launch_date": LAUNCH_DATE
                    }
                else:
                    # User exists but not a demo user, create new demo email
                    demo_email = f"demo_{uuid.uuid4().hex[:8]}@demo.nutritame.com"
            else:
                demo_email = provided_email
        else:
            demo_email = f"demo_{uuid.uuid4().hex[:8]}@demo.nutritame.com"
        
        # Create demo user with full access
        demo_user = User(
            email=demo_email,
            subscription_status="active",  # Give full access in demo
            subscription_tier=SubscriptionTier.PREMIUM,  # Premium features for demo
            trial_end_date=None,
            subscription_end_date=datetime.utcnow() + timedelta(days=365)  # Long demo access
        )
        
        # Save demo user
        await db_manager.create_user(demo_user)
        
        # Create demo access token
        token = AuthService.create_access_token(demo_user)
        
        return {
            "demo_access": True,
            "access_token": token.token,
            "user": demo_user,
            "expires_at": token.expires_at,
            "demo_notice": "This is a demo account with full premium access. Account creation will be required after launch.",
            "launch_date": LAUNCH_DATE
        }
        
    except Exception as e:
        logging.error(f"Demo access error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create demo access")

# =============================================
# SAAS AUTHENTICATION & SUBSCRIPTION ENDPOINTS
# =============================================

@api_router.post("/auth/register", response_model=UserRegistrationResponse)
async def register_user(subscription_request: SubscriptionRequest, request: Request):
    """Register new user and create Stripe checkout session"""
    try:
        host_url = str(request.base_url).rstrip('/')
        
        # Check if user already exists
        existing_user = await db_manager.get_user_by_email(subscription_request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create checkout session
        session, transaction = await payment_service.create_subscription_checkout(
            email=subscription_request.email,
            plan=subscription_request.plan,
            origin_url=subscription_request.origin_url,
            host_url=host_url
        )
        
        # Get created user
        user = await db_manager.get_user_by_email(subscription_request.email)
        
        return UserRegistrationResponse(
            user=user,
            checkout_url=session.url,
            session_id=session.session_id
        )
        
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@api_router.post("/auth/login")
async def login_user(email: str = Form(...), password: str = Form(...)):
    """Login user (for development - in production use proper OAuth)"""
    try:
        # For now, auto-login any registered user (development only)
        user = await db_manager.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if subscription is active or in trial
        if user.subscription_status not in ["trial", "active"]:
            raise HTTPException(status_code=403, detail="Subscription required")
        
        # Update last login
        await db_manager.update_user(user.id, {"last_login": datetime.utcnow()})
        
        # Create access token
        token = AuthService.create_access_token(user)
        
        return {
            "access_token": token.token,
            "token_type": "bearer",
            "user": user,
            "expires_at": token.expires_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    user = await db_manager.get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": user,
        "tenant_id": current_user["tenant_id"],
        "subscription_info": await payment_service.get_subscription_info(user.id)
    }

@api_router.get("/subscription/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "trial_period_days": 15
    }

@api_router.post("/payments/checkout")
async def create_checkout_session(
    subscription_request: SubscriptionRequest,
    request: Request
):
    """Create Stripe checkout session for subscription"""
    try:
        host_url = str(request.base_url).rstrip('/')
        
        session, transaction = await payment_service.create_subscription_checkout(
            email=subscription_request.email,
            plan=subscription_request.plan,
            origin_url=subscription_request.origin_url,
            host_url=host_url
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logging.error(f"Checkout creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@api_router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request):
    """Check payment status"""
    try:
        host_url = str(request.base_url).rstrip('/')
        return await payment_service.check_payment_status(session_id, host_url)
    except Exception as e:
        logging.error(f"Payment status check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@api_router.get("/subscription/info")
async def get_subscription_info_endpoint(current_user: dict = Depends(get_current_active_user)):
    """Get current user's subscription information"""
    return await payment_service.get_subscription_info(current_user["user_id"])

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        return await payment_service.handle_webhook(request)
    except Exception as e:
        logging.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# =============================================
# SAAS ADMIN ENDPOINTS
# =============================================

@api_router.post("/admin/login")
async def admin_login(email: str = Form(...), password: str = Form(...)):
    """Admin login"""
    try:
        admin = await admin_service.authenticate_admin(email, password)
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        # Create admin token (simplified for demo)
        from models import User
        token = AuthService.create_access_token(User(
            id=admin.id,
            email=admin.email,
            tenant_id="admin"  # Special tenant for admin
        ))
        
        return {
            "access_token": token.token,
            "token_type": "bearer",
            "admin": admin,
            "expires_at": token.expires_at
        }
        
    except Exception as e:
        logging.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Admin login failed")

@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        return await admin_service.get_dashboard_stats()
    except Exception as e:
        logging.error(f"Admin dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@api_router.get("/admin/users")
async def get_admin_users(skip: int = 0, limit: int = 50, search: str = None):
    """Get users list for admin"""
    try:
        return await admin_service.get_users_list(skip, limit, search)
    except Exception as e:
        logging.error(f"Admin users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@api_router.get("/admin/users/{user_id}")
async def get_admin_user_details(user_id: str):
    """Get detailed user information for admin"""
    try:
        return await admin_service.get_user_details(user_id)
    except Exception as e:
        logging.error(f"Admin user details error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user details")

@api_router.get("/admin/analytics/revenue")
async def get_admin_revenue_analytics(days: int = 30):
    """Get revenue analytics for admin"""
    try:
        return await admin_service.get_revenue_analytics(days)
    except Exception as e:
        logging.error(f"Admin revenue analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue analytics")

# =============================================
# SAAS GDPR/HIPAA COMPLIANCE ENDPOINTS
# =============================================

@api_router.post("/data/export")
async def export_user_data(
    export_request: DataExportRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Export user data for GDPR compliance"""
    try:
        # Verify user can only export their own data
        if export_request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Can only export your own data")
        
        tenant_id = current_user["tenant_id"]
        data = await db_manager.export_user_data(export_request.user_id, tenant_id)
        
        return {
            "export_data": data,
            "export_timestamp": datetime.utcnow().isoformat(),
            "export_type": export_request.export_type
        }
        
    except Exception as e:
        logging.error(f"Data export error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")

@api_router.post("/data/delete")
async def delete_user_data(
    deletion_request: DataDeletionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete user data for GDPR compliance"""
    try:
        # Verify user can only delete their own data
        if deletion_request.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Can only delete your own data")
        
        # In production, implement proper confirmation token verification
        if not deletion_request.confirmation_token:
            raise HTTPException(status_code=400, detail="Confirmation token required")
        
        tenant_id = current_user["tenant_id"]
        success = await db_manager.delete_user_data(deletion_request.user_id, tenant_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete data")
        
        return {
            "message": "Data deleted successfully",
            "deletion_timestamp": datetime.utcnow().isoformat(),
            "deletion_type": deletion_request.deletion_type
        }
        
    except Exception as e:
        logging.error(f"Data deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete data")

# =============================================
# UPDATED GLUCOPLANNER ENDPOINTS (Now with Multi-Tenancy)
# =============================================

# Update the chat endpoint to support tenant isolation
@api_router.post("/chat/send-saas")
async def send_chat_message_saas(
    message: dict,
    current_user: dict = Depends(get_current_active_user)
):
    """Send message to AI health coach (tenant-isolated SaaS version)"""
    try:
        tenant_id = current_user["tenant_id"]
        user_id = current_user["user_id"]
        
        # Get user profile for context
        user = await db_manager.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build context from user profile
        user_context = f"""
        User Profile:
        - Age: {user.age or 'Not specified'}
        - Gender: {user.gender or 'Not specified'}  
        - Diabetes Type: {user.diabetes_type or 'Not specified'}
        - Activity Level: {user.activity_level or 'Not specified'}
        - Health Goals: {', '.join(user.health_goals) if user.health_goals else 'Not specified'}
        - Food Preferences: {', '.join(user.food_preferences) if user.food_preferences else 'Not specified'}
        - Allergies: {', '.join(user.allergies) if user.allergies else 'None specified'}
        - Cooking Skill: {user.cooking_skill or 'Not specified'}
        """
        
        # Create AI prompt
        ai_prompt = f"""{HEALTH_COACH_PROMPT}
        
        {user_context}
        
        User Message: {message.get('message', '')}
        """
        
        # Call AI service
        llm_chat = LlmChat(api_key=os.environ.get('EMERGENT_LLM_KEY'))
        ai_response = await llm_chat.call_llm_async(
            messages=[UserMessage(content=ai_prompt)],
            model="gpt-4o-mini"
        )
        
        # Save chat session (tenant-isolated)
        chat_data = {
            "user_message": message.get('message', ''),
            "ai_response": ai_response,
            "timestamp": datetime.utcnow()
        }
        
        # Get or create chat session
        chat_sessions = await db_manager.get_chat_sessions(user_id, tenant_id)
        if chat_sessions:
            # Update existing session
            session = chat_sessions[0]
            session.messages.append(chat_data)
            await db_manager.update_chat_session(session.id, tenant_id, {"messages": session.messages})
        else:
            # Create new session
            from models import ChatSession
            new_session = ChatSession(
                tenant_id=tenant_id,
                user_id=user_id,
                messages=[chat_data]
            )
            await db_manager.create_chat_session(new_session, tenant_id)
        
        return {"response": ai_response}
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@api_router.get("/chat/history-saas")
async def get_chat_history_saas(current_user: dict = Depends(get_current_active_user)):
    """Get chat history (tenant-isolated SaaS version)"""
    try:
        tenant_id = current_user["tenant_id"]
        user_id = current_user["user_id"]
        
        chat_sessions = await db_manager.get_chat_sessions(user_id, tenant_id)
        return {"chat_sessions": chat_sessions}
        
    except Exception as e:
        logging.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

# User Profile Endpoints
@api_router.post("/users", response_model=UserProfile)
async def create_user_profile(profile: UserProfileCreate):
    """Create a new user profile"""
    profile_dict = profile.dict()
    profile_obj = UserProfile(**profile_dict)
    profile_data = prepare_for_mongo(profile_obj.dict())
    await db.user_profiles.insert_one(profile_data)
    return profile_obj

@api_router.get("/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    user = await db.user_profiles.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = parse_from_mongo(user)
    return UserProfile(**user)

@api_router.put("/users/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, updates: UserProfileUpdate):
    """Update user profile"""
    existing_user = await db.user_profiles.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    if update_data:
        await db.user_profiles.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
    
    updated_user = await db.user_profiles.find_one({"id": user_id})
    updated_user = parse_from_mongo(updated_user)
    return UserProfile(**updated_user)

@api_router.get("/users", response_model=List[UserProfile])
async def list_user_profiles():
    """List all user profiles"""
    users = await db.user_profiles.find().to_list(1000)
    return [UserProfile(**parse_from_mongo(user)) for user in users]

# Restaurant Search Endpoints
@api_router.post("/restaurants/search", response_model=List[Restaurant])
async def search_restaurants(search_request: RestaurantSearchRequest):
    """Search for restaurants near a location using coordinates"""
    try:
        restaurants = await google_places.search_restaurants(
            latitude=search_request.latitude,
            longitude=search_request.longitude,
            radius=search_request.radius,
            keyword=search_request.keyword
        )
        
        # Cache results in database
        for restaurant in restaurants:
            restaurant_data = prepare_for_mongo(restaurant.dict())
            await db.restaurants.replace_one(
                {"place_id": restaurant.place_id},
                restaurant_data,
                upsert=True
            )
        
        return restaurants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restaurant search error: {str(e)}")

@api_router.post("/restaurants/search-by-location", response_model=List[Restaurant])
async def search_restaurants_by_location(search_request: LocationSearchRequest):
    """Search for restaurants by location name (city, address, etc.)"""
    try:
        # First geocode the location to get coordinates
        location_data = await google_places.geocode_location(search_request.location)
        
        if not location_data:
            raise HTTPException(status_code=400, detail=f"Could not find location: {search_request.location}")
        
        # Search restaurants using the geocoded coordinates
        restaurants = await google_places.search_restaurants(
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            radius=search_request.radius,
            keyword=search_request.keyword
        )
        
        # Cache results in database
        for restaurant in restaurants:
            restaurant_data = prepare_for_mongo(restaurant.dict())
            await db.restaurants.replace_one(
                {"place_id": restaurant.place_id},
                restaurant_data,
                upsert=True
            )
        
        return restaurants
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location search error: {str(e)}")

@api_router.post("/geocode")
async def geocode_location_endpoint(location_data: dict):
    """Convert a location string to coordinates"""
    try:
        location = location_data.get("location")
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        result = await google_places.geocode_location(location)
        if not result:
            raise HTTPException(status_code=404, detail=f"Location not found: {location}")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")

@api_router.get("/restaurants/{place_id}", response_model=Restaurant)
async def get_restaurant_details(place_id: str):
    """Get detailed restaurant information"""
    # Check cache first
    cached_restaurant = await db.restaurants.find_one({"place_id": place_id})
    if cached_restaurant:
        cached_restaurant = parse_from_mongo(cached_restaurant)
        # Check if cache is recent (less than 24 hours)
        cache_age = datetime.now(timezone.utc) - cached_restaurant.get('cached_at', datetime.min.replace(tzinfo=timezone.utc))
        if cache_age.total_seconds() < 86400:  # 24 hours
            return Restaurant(**cached_restaurant)
    
    # Fetch fresh data
    restaurant = await google_places.get_restaurant_details(place_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Update cache
    restaurant_data = prepare_for_mongo(restaurant.dict())
    await db.restaurants.replace_one(
        {"place_id": place_id},
        restaurant_data,
        upsert=True
    )
    
    return restaurant

# Nutrition Analysis Endpoints
@api_router.get("/nutrition/search/{query}", response_model=List[FoodNutrition])
async def search_nutrition(query: str):
    """Search for nutrition information"""
    try:
        foods = await usda_nutrition.search_food(query)
        
        # Cache results
        for food in foods:
            food_data = prepare_for_mongo(food.dict())
            await db.nutrition.replace_one(
                {"fdc_id": food.fdc_id},
                food_data,
                upsert=True
            )
        
        return foods
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nutrition search error: {str(e)}")

@api_router.get("/nutrition/{fdc_id}", response_model=FoodNutrition)
async def get_nutrition_details(fdc_id: str):
    """Get detailed nutrition information"""
    # Check cache first
    cached_food = await db.nutrition.find_one({"fdc_id": fdc_id})
    if cached_food:
        cached_food = parse_from_mongo(cached_food)
        return FoodNutrition(**cached_food)
    
    # Fetch fresh data
    food = await usda_nutrition.get_food_details(fdc_id)
    if not food:
        raise HTTPException(status_code=404, detail="Nutrition information not found")
    
    # Cache result
    food_data = prepare_for_mongo(food.dict())
    await db.nutrition.insert_one(food_data)
    
    return food

# Enhanced AI Chat Endpoint
@api_router.post("/chat", response_model=ChatMessage)
async def chat_with_ai(chat_request: ChatMessageCreate):
    """Chat with the AI health coach with restaurant and nutrition context"""
    try:
        # Get user profile for context
        user_profile = await db.user_profiles.find_one({"id": chat_request.user_id})
        user_context = ""
        
        if user_profile:
            user_context = f"""
User Profile Context:
- Diabetes Type: {user_profile.get('diabetes_type', 'Not specified')}
- Age: {user_profile.get('age', 'Not specified')}
- Gender: {user_profile.get('gender', 'Not specified')}
- Activity Level: {user_profile.get('activity_level', 'Not specified')}
- Health Goals: {', '.join(user_profile.get('health_goals', []))}
- Food Preferences: {', '.join(user_profile.get('food_preferences', []))}
- Cultural Background: {user_profile.get('cultural_background', 'Not specified')}
- Allergies: {', '.join(user_profile.get('allergies', []))}
- Dislikes: {', '.join(user_profile.get('dislikes', []))}
- Cooking Skill: {user_profile.get('cooking_skill', 'Not specified')}

"""
        
        # Initialize AI chat with enhanced prompt
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"meal_planning_{chat_request.user_id}",
            system_message=f"{HEALTH_COACH_PROMPT}\n\n{user_context}"
        ).with_model("openai", "gpt-4o-mini")
        
        # Create user message
        user_message = UserMessage(text=chat_request.message)
        
        # Get AI response
        ai_response = await chat.send_message(user_message)
        
        # Create chat message object
        chat_obj = ChatMessage(
            user_id=chat_request.user_id,
            message=chat_request.message,
            response=ai_response
        )
        
        # Save to database
        chat_data = prepare_for_mongo(chat_obj.dict())
        await db.chat_messages.insert_one(chat_data)
        
        return chat_obj
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

@api_router.get("/chat/{user_id}", response_model=List[ChatMessage])
async def get_chat_history(user_id: str):
    """Get chat history for a user"""
    messages = await db.chat_messages.find({"user_id": user_id}).sort("timestamp", 1).to_list(1000)
    return [ChatMessage(**parse_from_mongo(msg)) for msg in messages]

# =============================================
# AI HEALTH COACH ENDPOINTS
# =============================================

@api_router.get("/coach/feature-flags")
async def get_coach_feature_flags():
    """Get AI Health Coach feature flags"""
    return {
        "coach_enabled": FEATURE_COACH,
        "llm_provider": LLM_PROVIDER,
        "llm_model": LLM_MODEL,
        "standard_limit": STANDARD_CONSULTATION_LIMIT,
        "premium_limit": "unlimited" if PREMIUM_CONSULTATION_LIMIT == -1 else PREMIUM_CONSULTATION_LIMIT
    }

@api_router.post("/coach/accept-disclaimer")
async def accept_disclaimer(request: dict):
    """Accept AI Health Coach disclaimer"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        # Check if already accepted
        already_accepted = await check_disclaimer_acceptance(user_id)
        if already_accepted:
            return {"message": "Disclaimer already accepted", "accepted": True}
        
        # Save acceptance
        success = await save_disclaimer_acceptance(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save disclaimer acceptance")
        
        return {"message": "Disclaimer accepted successfully", "accepted": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accepting disclaimer: {str(e)}")

@api_router.get("/coach/disclaimer-status/{user_id}")
async def get_disclaimer_status(user_id: str):
    """Check if user has accepted disclaimer"""
    try:
        accepted = await check_disclaimer_acceptance(user_id)
        return {"user_id": user_id, "disclaimer_accepted": accepted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking disclaimer status: {str(e)}")

@api_router.get("/coach/consultation-limit/{user_id}")
async def get_consultation_limit(user_id: str):
    """Get user's consultation limit status"""
    try:
        limit_info = await check_consultation_limit(user_id)
        return limit_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking consultation limit: {str(e)}")

@api_router.post("/coach/sessions")
async def create_coach_session(session_request: CoachSessionCreate):
    """Create a new AI Health Coach session with user_id in request body"""
    try:
        user_id = session_request.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required in request body")
        
        # Check disclaimer acceptance
        disclaimer_accepted = await check_disclaimer_acceptance(user_id)
        if not disclaimer_accepted:
            raise HTTPException(status_code=403, detail="Disclaimer must be accepted before using AI Health Coach")
        
        # Check consultation limits
        limit_info = await check_consultation_limit(user_id)
        if not limit_info["can_use"]:
            return {
                "error": "consultation_limit_reached",
                "message": "Monthly consultation limit reached. Upgrade to Premium for unlimited access.",
                "limit_info": limit_info
            }
        
        # Create session
        session = CoachSession(
            user_id=user_id,
            title=session_request.title,
            disclaimer_accepted_at=datetime.now(timezone.utc)
        )
        
        # Save to database
        session_data = prepare_for_mongo(session.dict())
        await db.coach_sessions.insert_one(session_data)
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating coach session: {str(e)}")

@api_router.get("/coach/sessions/{user_id}")
async def get_coach_sessions(user_id: str):
    """Get AI Health Coach sessions for user"""
    try:
        sessions = await db.coach_sessions.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        return [CoachSession(**parse_from_mongo(session)) for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting coach sessions: {str(e)}")

@api_router.post("/coach/message")
async def send_coach_message(message_request: CoachMessageCreate):
    """Send message to AI Health Coach"""
    try:
        # Get session to verify ownership
        session = await db.coach_sessions.find_one({"id": message_request.session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = session["user_id"]
        
        # Check consultation limits
        limit_info = await check_consultation_limit(user_id)
        if not limit_info["can_use"]:
            return {
                "error": "consultation_limit_reached",
                "message": "Monthly consultation limit reached. Upgrade to Premium for unlimited access.",
                "limit_info": limit_info
            }
        
        # Save user message
        user_message = CoachMessage(
            session_id=message_request.session_id,
            role="user",
            text=message_request.message
        )
        user_msg_data = prepare_for_mongo(user_message.dict())
        await db.coach_messages.insert_one(user_msg_data)
        
        # Get AI response
        ai_response_text = await get_ai_response(
            message_request.message, 
            user_id, 
            message_request.session_id
        )
        
        # Save AI response
        ai_message = CoachMessage(
            session_id=message_request.session_id,
            role="assistant",
            text=ai_response_text
        )
        ai_msg_data = prepare_for_mongo(ai_message.dict())
        await db.coach_messages.insert_one(ai_msg_data)
        
        # Increment consultation count
        await increment_consultation_count(user_id)
        
        # Update session timestamp
        await db.coach_sessions.update_one(
            {"id": message_request.session_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "user_message": user_message,
            "ai_response": ai_message,
            "consultation_used": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending coach message: {str(e)}")

@api_router.get("/coach/messages/{session_id}")
async def get_coach_messages(session_id: str):
    """Get messages for a coach session"""
    try:
        messages = await db.coach_messages.find({"session_id": session_id}).sort("created_at", 1).to_list(1000)
        return [CoachMessage(**parse_from_mongo(msg)) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting coach messages: {str(e)}")

@api_router.get("/coach/search/{user_id}")
async def search_coach_history(user_id: str, query: str):
    """Search AI Health Coach conversation history"""
    try:
        # Get user's sessions
        sessions = await db.coach_sessions.find({"user_id": user_id}).to_list(100)
        session_ids = [session["id"] for session in sessions]
        
        # Search messages
        search_results = await db.coach_messages.find({
            "session_id": {"$in": session_ids},
            "text": {"$regex": query, "$options": "i"}
        }).sort("created_at", -1).to_list(50)
        
        # Group results by session
        results_by_session = {}
        for msg in search_results:
            session_id = msg["session_id"]
            if session_id not in results_by_session:
                # Find session info
                session_info = next((s for s in sessions if s["id"] == session_id), None)
                if session_info:
                    session_info = parse_from_mongo(session_info)  # Fix ObjectId serialization
                results_by_session[session_id] = {
                    "session": session_info,
                    "messages": []
                }
            results_by_session[session_id]["messages"].append(CoachMessage(**parse_from_mongo(msg)))
        
        return {
            "query": query,
            "results": list(results_by_session.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coach history: {str(e)}")

# Restaurant Analysis Endpoint
@api_router.post("/restaurants/analyze")
async def analyze_restaurant_for_user(analysis_request: RestaurantAnalysisRequest):
    """Analyze a restaurant for diabetic-friendly options"""
    try:
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": analysis_request.user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get restaurant details
        restaurant = await get_restaurant_details(analysis_request.restaurant_place_id)
        
        # Create AI analysis prompt
        analysis_prompt = f"""
        Analyze this restaurant for a diabetic user:
        
        Restaurant: {restaurant.name}
        Address: {restaurant.address}
        Rating: {restaurant.rating}
        Cuisine Types: {', '.join(restaurant.cuisine_types)}
        
        User Profile:
        - Diabetes Type: {user_profile.get('diabetes_type')}
        - Health Goals: {', '.join(user_profile.get('health_goals', []))}
        - Food Preferences: {', '.join(user_profile.get('food_preferences', []))}
        - Allergies: {', '.join(user_profile.get('allergies', []))}
        
        Please provide:
        1. Overall diabetic-friendliness score (1-5)
        2. Recommended menu items or meal types
        3. Items to avoid
        4. Tips for ordering diabetic-friendly meals at this restaurant
        5. Portion size recommendations
        """
        
        # Get AI analysis
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"restaurant_analysis_{analysis_request.user_id}",
            system_message=HEALTH_COACH_PROMPT
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=analysis_prompt)
        ai_analysis = await chat.send_message(user_message)
        
        return {
            "restaurant": restaurant,
            "analysis": ai_analysis,
            "diabetic_friendly_score": restaurant.diabetic_friendly_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restaurant analysis error: {str(e)}")

# Shopping List Endpoints
@api_router.post("/shopping-lists", response_model=ShoppingList)
async def create_shopping_list(shopping_list: ShoppingListCreate):
    """Create a new shopping list"""
    shopping_list_obj = ShoppingList(**shopping_list.dict())
    shopping_list_data = prepare_for_mongo(shopping_list_obj.dict())
    await db.shopping_lists.insert_one(shopping_list_data)
    return shopping_list_obj

@api_router.get("/shopping-lists/{user_id}", response_model=List[ShoppingList])
async def get_user_shopping_lists(user_id: str):
    """Get shopping lists for a user"""
    lists = await db.shopping_lists.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [ShoppingList(**parse_from_mongo(shopping_list)) for shopping_list in lists]

@api_router.get("/shopping-lists/detail/{list_id}", response_model=ShoppingList)
async def get_shopping_list(list_id: str):
    """Get a specific shopping list"""
    shopping_list = await db.shopping_lists.find_one({"id": list_id})
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    shopping_list = parse_from_mongo(shopping_list)
    return ShoppingList(**shopping_list)

@api_router.put("/shopping-lists/{list_id}", response_model=ShoppingList)
async def update_shopping_list(list_id: str, updates: ShoppingListUpdate):
    """Update a shopping list"""
    existing_list = await db.shopping_lists.find_one({"id": list_id})
    if not existing_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    if update_data:
        await db.shopping_lists.update_one(
            {"id": list_id},
            {"$set": update_data}
        )
    
    updated_list = await db.shopping_lists.find_one({"id": list_id})
    updated_list = parse_from_mongo(updated_list)
    return ShoppingList(**updated_list)

@api_router.delete("/shopping-lists/{list_id}")
async def delete_shopping_list(list_id: str):
    """Delete a shopping list"""
    result = await db.shopping_lists.delete_one({"id": list_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return {"message": "Shopping list deleted successfully"}

@api_router.post("/shopping-lists/generate")
async def generate_shopping_list(request: dict):
    """Generate a shopping list from AI meal plan using AI"""
    try:
        user_id = request.get('user_id')
        meal_plan_text = request.get('meal_plan_text', '')
        
        if not user_id or not meal_plan_text:
            raise HTTPException(status_code=400, detail="user_id and meal_plan_text are required")
        
        # Use AI to parse the meal plan and generate shopping list
        shopping_list_prompt = f"""
        Based on this meal plan, create a shopping list organized by store sections. 
        Format the response as a simple list without any markdown formatting.
        Use ONLY Imperial measurements (cups, tablespoons, pounds, ounces).
        
        Meal Plan:
        {meal_plan_text}
        
        Please organize items into these categories:
        - Fresh Produce
        - Proteins (Meat/Fish/Dairy) 
        - Pantry Items
        - Frozen Foods
        - Other Items
        
        For each item, estimate reasonable quantities using Imperial measurements:
        - Use pounds (lbs) and ounces (oz) for weight
        - Use cups, tablespoons, teaspoons for volume
        - Examples: "2 lbs chicken breast", "1 cup brown rice", "8 oz salmon"
        - Never use grams, kilograms, or liters
        """
        
        # Get AI response for shopping list
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"shopping_list_{user_id}",
            system_message="You are a helpful assistant that creates organized shopping lists from meal plans. Use clear, simple formatting without markdown."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=shopping_list_prompt)
        ai_response = await chat.send_message(user_message)
        
        # Parse AI response into shopping list items (simplified parsing)
        items = []
        current_category = "other"
        category_mapping = {
            "produce": "produce",
            "fresh produce": "produce", 
            "proteins": "proteins",
            "meat": "proteins",
            "fish": "proteins",
            "dairy": "proteins",
            "pantry": "pantry",
            "pantry items": "pantry",
            "frozen": "frozen",
            "frozen foods": "frozen",
            "other": "other"
        }
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if not line or line.startswith('-') and len(line) < 3:
                continue
                
            # Check if this line indicates a category
            line_lower = line.lower().replace(':', '').replace('-', '').strip()
            if line_lower in category_mapping:
                current_category = category_mapping[line_lower]
                continue
            
            # If line starts with dash or number, it's probably an item
            if line.startswith('-') or line[0].isdigit():
                item_text = line.lstrip('- 1234567890.').strip()
                if item_text and len(item_text) > 2:
                    items.append(ShoppingListItem(
                        item=item_text,
                        category=current_category,
                        checked=False
                    ))
        
        # Create shopping list
        shopping_list = ShoppingList(
            user_id=user_id,
            title=f"Shopping List - {datetime.now().strftime('%m/%d/%Y')}",
            items=items
        )
        
        # Save to database
        shopping_list_data = prepare_for_mongo(shopping_list.dict())
        await db.shopping_lists.insert_one(shopping_list_data)
        
        return {
            "shopping_list": shopping_list,
            "ai_response": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shopping list generation error: {str(e)}")

# Meal Plan Endpoints
@api_router.get("/meal-plans/{user_id}", response_model=List[MealPlan])
async def get_user_meal_plans(user_id: str):
    """Get meal plans for a user"""
    plans = await db.meal_plans.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [MealPlan(**parse_from_mongo(plan)) for plan in plans]

# SMS Endpoints
@api_router.post("/sms/send-restaurant")
async def send_restaurant_sms(sms_request: SendSMSRequest):
    """Send restaurant information to user's phone via SMS"""
    try:
        # Get user profile to get phone number if not provided
        user_profile = await db.user_profiles.find_one({"id": sms_request.user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        phone_number = sms_request.phone_number
        if not phone_number and user_profile.get('phone_number'):
            phone_number = user_profile['phone_number']
        
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        # Validate phone number
        if not mock_sms_service.validate_phone_number(phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Get restaurant details
        restaurant = await google_places.get_restaurant_details(sms_request.restaurant_place_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Send SMS using mock service
        sms_result = await mock_sms_service.send_restaurant_sms(phone_number, restaurant.dict())
        
        if not sms_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to send SMS: {sms_result.get('error')}")
        
        # Save SMS record to database
        sms_record = SMSMessage(
            user_id=sms_request.user_id,
            phone_number=sms_result["formatted_phone"],
            message_content=mock_sms_service._format_restaurant_message(restaurant.dict()),
            message_type="restaurant_info",
            restaurant_data=restaurant.dict(),
            status="sent"
        )
        
        sms_data = prepare_for_mongo(sms_record.dict())
        await db.sms_messages.insert_one(sms_data)
        
        return {
            "success": True,
            "message": f"Restaurant information sent to {sms_result['formatted_phone']}",
            "message_sid": sms_result["message_sid"],
            "restaurant_name": restaurant.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"SMS sending error: {e}")
        raise HTTPException(status_code=500, detail=f"SMS sending failed: {str(e)}")

@api_router.get("/sms/history/{user_id}")
async def get_sms_history(user_id: str):
    """Get SMS history for a user"""
    try:
        messages = await db.sms_messages.find({"user_id": user_id}).sort("sent_at", -1).to_list(50)
        return [SMSMessage(**parse_from_mongo(msg)) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SMS history: {str(e)}")

@api_router.post("/sms/validate-phone")
async def validate_phone_number(phone_data: dict):
    """Validate a phone number format"""
    try:
        phone_number = phone_data.get("phone_number")
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        is_valid = mock_sms_service.validate_phone_number(phone_number)
        formatted_phone = mock_sms_service.format_phone_number(phone_number) if is_valid else None
        
        return {
            "valid": is_valid,
            "formatted": formatted_phone,
            "message": "Phone number is valid" if is_valid else "Invalid phone number format. Please use format: +1234567890"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phone validation error: {str(e)}")

# API Usage Monitoring Endpoints
@api_router.get("/usage/google-places")
async def get_google_places_usage():
    """Get Google Places API usage statistics"""
    try:
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        usage_doc = await db.api_usage.find_one({
            "api": "google_places",
            "month": current_month
        })
        
        if not usage_doc:
            return {
                "month": current_month,
                "calls_made": 0,
                "monthly_limit": 9000,
                "percentage_used": 0,
                "calls_remaining": 9000,
                "status": "under_limit"
            }
        
        calls_made = usage_doc.get('calls_made', 0)
        monthly_limit = 9000
        percentage_used = (calls_made / monthly_limit) * 100
        calls_remaining = monthly_limit - calls_made
        
        # Determine status
        if calls_made >= monthly_limit:
            status = "limit_exceeded"
        elif calls_made >= (monthly_limit * 0.9):
            status = "approaching_limit"
        elif calls_made >= (monthly_limit * 0.7):
            status = "moderate_usage"
        else:
            status = "under_limit"
        
        return {
            "month": current_month,
            "calls_made": calls_made,
            "monthly_limit": monthly_limit,
            "percentage_used": round(percentage_used, 2),
            "calls_remaining": calls_remaining,
            "status": status,
            "last_updated": usage_doc.get('last_updated')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage check error: {str(e)}")

@api_router.post("/usage/reset-google-places")
async def reset_google_places_usage():
    """Reset Google Places API usage counter (admin function)"""
    try:
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        await db.api_usage.update_one(
            {"api": "google_places", "month": current_month},
            {
                "$set": {
                    "calls_made": 0,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        return {"message": "Google Places API usage counter reset successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "GlucoPlanner API - Your AI-powered diabetic meal planning assistant with restaurant search"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "GlucoPlanner API", "features": ["meal_planning", "restaurant_search", "nutrition_analysis"]}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=86400,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()