from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

**Objective:** To create simple, enjoyable, and practical meal plans that fit seamlessly into a person's daily life while supporting healthy blood sugar management. The plans should focus on foods the user actually likes, easy preparation methods, and flexible options that reduce stress around eating. The goal is to make living with diabetes feel less restrictive and more empowering, helping users build confidence and consistency in their everyday choices.

**Context:** Users of this app may have Type 1 or Type 2 diabetes and are looking for meal guidance that feels realistic and supportive. They may struggle with knowing what to eat, balancing meals, managing blood sugar spikes, or feeling restricted by their condition. Some may have additional goals like losing weight, maintaining energy, or eating with their family. The app should provide clear, trustworthy, and encouraging guidance that adapts to different lifestyles, food preferences, cultural traditions, and cooking skills. It should feel like a reliable partner that makes daily meal planning less stressful and more enjoyable.

**Instructions:**
1. Start with the user profile: Ask about diabetes type (Type 1, Type 2, prediabetes), age, gender, activity level, and any relevant health goals (e.g., weight loss, energy, blood sugar control). Identify food preferences, cultural traditions, allergies, dislikes, and cooking skill level.
2. Set daily nutrition goals: Determine calorie range if relevant. Balance macronutrients with an emphasis on managing carbohydrates. Recommend fiber-rich foods, lean proteins, healthy fats, and limited added sugars.
3. Build the meal plan: Divide into meals and snacks that evenly space carbohydrate intake. Suggest realistic portion sizes with clear examples (e.g., "½ cup cooked brown rice = 1 serving"). Include variety and options to prevent monotony. Incorporate easy swaps (e.g., "If you don't like salmon, try grilled chicken or tofu").
4. Keep it practical: Suggest meals that can be prepared quickly or in advance. Offer grocery shopping tips and cost-conscious substitutions. Provide cooking guidance that matches the user's skill level.
5. Support and motivate: Use positive, encouraging language. Frame choices as flexible, not restrictive. Reinforce the benefits (steady energy, confidence, improved blood sugar control).
6. Provide education when helpful: Briefly explain why certain foods or combinations are recommended. Share strategies for dining out, handling cravings, or special occasions.
7. Adapt and refine: Encourage feedback from the user. Adjust future meal plans based on what worked, what didn't, and evolving goals.

**Notes:**
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
- Do not diagnose conditions or recommend changes to medication—always direct users back to their healthcare team for medical decisions."""

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

class MealPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    meals: List[dict]  # Flexible structure for meals
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
            if key in ['created_at', 'timestamp'] and isinstance(value, str):
                item[key] = datetime.fromisoformat(value)
    return item

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
    # Get existing profile
    existing_user = await db.user_profiles.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update with non-None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    if update_data:
        await db.user_profiles.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
    
    # Return updated profile
    updated_user = await db.user_profiles.find_one({"id": user_id})
    updated_user = parse_from_mongo(updated_user)
    return UserProfile(**updated_user)

@api_router.get("/users", response_model=List[UserProfile])
async def list_user_profiles():
    """List all user profiles"""
    users = await db.user_profiles.find().to_list(1000)
    return [UserProfile(**parse_from_mongo(user)) for user in users]

# AI Chat Endpoints
@api_router.post("/chat", response_model=ChatMessage)
async def chat_with_ai(chat_request: ChatMessageCreate):
    """Chat with the AI health coach"""
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
        
        # Initialize AI chat
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

# Meal Plan Endpoints
@api_router.get("/meal-plans/{user_id}", response_model=List[MealPlan])
async def get_user_meal_plans(user_id: str):
    """Get meal plans for a user"""
    plans = await db.meal_plans.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [MealPlan(**parse_from_mongo(plan)) for plan in plans]

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "GlucoPlanner API - Your AI-powered diabetic meal planning assistant"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "GlucoPlanner API"}

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