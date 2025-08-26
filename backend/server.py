from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import httpx
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

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

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    message: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessageCreate(BaseModel):
    user_id: str
    message: str

class RestaurantSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: Optional[int] = 2000  # Default 2km radius
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

def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse ISO string dates back to datetime objects"""
    if isinstance(item, dict):
        for key, value in item.items():
            if key in ['created_at', 'timestamp', 'cached_at'] and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass  # Keep original value if parsing fails
    return item

# Google Places API Client
class GooglePlacesClient:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
    async def search_restaurants(self, latitude: float, longitude: float, radius: int = 2000, keyword: str = None):
        """Search for restaurants using Google Places API"""
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
                logging.info(f"Making Google Places API request with params: {params}")
                response = await client.get(f"{self.base_url}/nearbysearch/json", params=params)
                response.raise_for_status()
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
        """Get detailed restaurant information"""
        async with httpx.AsyncClient() as client:
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,geometry,rating,price_level,formatted_phone_number,website,opening_hours,photos,reviews',
                'key': self.api_key
            }
            
            try:
                response = await client.get(f"{self.base_url}/details/json", params=params)
                response.raise_for_status()
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
    """Search for restaurants near a location"""
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
        
        Meal Plan:
        {meal_plan_text}
        
        Please organize items into these categories:
        - Fresh Produce
        - Proteins (Meat/Fish/Dairy) 
        - Pantry Items
        - Frozen Foods
        - Other Items
        
        For each item, estimate reasonable quantities for the meals described.
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
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
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