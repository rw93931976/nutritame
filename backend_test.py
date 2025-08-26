import requests
import sys
import json
from datetime import datetime

class GlucoPlannerAPITester:
    def __init__(self, base_url="https://gluco-planner.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test the health check endpoint"""
        return self.run_test("Health Check", "GET", "", 200)

    def test_create_user_profile(self):
        """Test creating a user profile"""
        test_profile = {
            "diabetes_type": "type2",
            "age": 45,
            "gender": "female",
            "activity_level": "moderate",
            "health_goals": ["blood_sugar_control", "weight_loss"],
            "food_preferences": ["mediterranean", "low_carb"],
            "cultural_background": "Mediterranean",
            "allergies": ["nuts", "shellfish"],
            "dislikes": ["liver", "brussels_sprouts"],
            "cooking_skill": "intermediate"
        }
        
        success, response = self.run_test(
            "Create User Profile",
            "POST",
            "users",
            200,
            data=test_profile
        )
        
        if success and 'id' in response:
            self.created_user_id = response['id']
            print(f"   Created user ID: {self.created_user_id}")
            return True
        return False

    def test_get_user_profile(self):
        """Test getting a user profile"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        return self.run_test(
            "Get User Profile",
            "GET",
            f"users/{self.created_user_id}",
            200
        )[0]

    def test_update_user_profile(self):
        """Test updating a user profile"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        update_data = {
            "age": 46,
            "health_goals": ["blood_sugar_control", "weight_loss", "energy_boost"]
        }
        
        return self.run_test(
            "Update User Profile",
            "PUT",
            f"users/{self.created_user_id}",
            200,
            data=update_data
        )[0]

    def test_list_users(self):
        """Test listing all user profiles"""
        return self.run_test(
            "List User Profiles",
            "GET",
            "users",
            200
        )[0]

    def test_ai_chat(self):
        """Test AI chat functionality"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        chat_data = {
            "user_id": self.created_user_id,
            "message": "I need help creating a weekly meal plan for Type 2 diabetes"
        }
        
        print("   Note: AI response may take 10-15 seconds...")
        success, response = self.run_test(
            "AI Chat",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success and 'response' in response:
            print(f"   AI Response preview: {response['response'][:100]}...")
            return True
        return False

    def test_get_chat_history(self):
        """Test getting chat history"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        return self.run_test(
            "Get Chat History",
            "GET",
            f"chat/{self.created_user_id}",
            200
        )[0]

    def test_get_meal_plans(self):
        """Test getting meal plans for user"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        return self.run_test(
            "Get User Meal Plans",
            "GET",
            f"meal-plans/{self.created_user_id}",
            200
        )[0]

    def test_restaurant_search(self):
        """Test restaurant search functionality"""
        # Test with San Francisco coordinates as specified in the request
        search_data = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "radius": 2000,
            "keyword": "healthy"
        }
        
        print("   Note: Restaurant search may take 10-15 seconds...")
        success, response = self.run_test(
            "Restaurant Search",
            "POST",
            "restaurants/search",
            200,
            data=search_data
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} restaurants")
            if len(response) > 0:
                # Store first restaurant for detail testing
                self.test_restaurant = response[0]
                print(f"   Sample restaurant: {response[0].get('name', 'Unknown')}")
            return True
        return False

    def test_restaurant_details(self):
        """Test getting restaurant details"""
        if not hasattr(self, 'test_restaurant') or not self.test_restaurant:
            print("❌ No restaurant available for testing details")
            return False
            
        place_id = self.test_restaurant.get('place_id')
        if not place_id:
            print("❌ No place_id available for testing")
            return False
            
        return self.run_test(
            "Get Restaurant Details",
            "GET",
            f"restaurants/{place_id}",
            200
        )[0]

    def test_restaurant_analysis(self):
        """Test restaurant analysis for diabetic-friendliness"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        if not hasattr(self, 'test_restaurant') or not self.test_restaurant:
            print("❌ No restaurant available for testing analysis")
            return False
            
        place_id = self.test_restaurant.get('place_id')
        if not place_id:
            print("❌ No place_id available for testing")
            return False
            
        analysis_data = {
            "user_id": self.created_user_id,
            "restaurant_place_id": place_id,
            "menu_items": ["grilled chicken salad", "quinoa bowl"]
        }
        
        print("   Note: Restaurant analysis may take 10-15 seconds...")
        success, response = self.run_test(
            "Restaurant Analysis",
            "POST",
            "restaurants/analyze",
            200,
            data=analysis_data
        )
        
        if success and 'analysis' in response:
            print(f"   Analysis preview: {response['analysis'][:100]}...")
            return True
        return False

    def test_nutrition_search(self):
        """Test nutrition database search"""
        query = "chicken breast"
        
        success, response = self.run_test(
            "Nutrition Search",
            "GET",
            f"nutrition/search/{query}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} nutrition items")
            if len(response) > 0:
                # Store first nutrition item for detail testing
                self.test_nutrition = response[0]
                print(f"   Sample food: {response[0].get('food_name', 'Unknown')}")
            return True
        return False

    def test_nutrition_details(self):
        """Test getting detailed nutrition information"""
        if not hasattr(self, 'test_nutrition') or not self.test_nutrition:
            print("❌ No nutrition item available for testing details")
            return False
            
        fdc_id = self.test_nutrition.get('fdc_id')
        if not fdc_id:
            print("❌ No fdc_id available for testing")
            return False
            
        return self.run_test(
            "Get Nutrition Details",
            "GET",
            f"nutrition/{fdc_id}",
            200
        )[0]

    def test_health_endpoint(self):
        """Test the health endpoint"""
        return self.run_test("Health Endpoint", "GET", "health", 200)[0]

    def test_create_shopping_list(self):
        """Test creating a shopping list"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        shopping_list_data = {
            "user_id": self.created_user_id,
            "title": "Test Shopping List",
            "items": [
                {
                    "item": "Chicken breast",
                    "category": "proteins",
                    "quantity": "2 lbs",
                    "checked": False
                },
                {
                    "item": "Broccoli",
                    "category": "produce",
                    "quantity": "1 bunch",
                    "checked": False
                },
                {
                    "item": "Brown rice",
                    "category": "pantry",
                    "quantity": "1 bag",
                    "checked": False
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Shopping List",
            "POST",
            "shopping-lists",
            200,
            data=shopping_list_data
        )
        
        if success and 'id' in response:
            self.created_shopping_list_id = response['id']
            print(f"   Created shopping list ID: {self.created_shopping_list_id}")
            return True
        return False

    def test_get_user_shopping_lists(self):
        """Test getting shopping lists for a user"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get User Shopping Lists",
            "GET",
            f"shopping-lists/{self.created_user_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} shopping lists")
            return True
        return False

    def test_get_shopping_list_details(self):
        """Test getting a specific shopping list"""
        if not hasattr(self, 'created_shopping_list_id') or not self.created_shopping_list_id:
            print("❌ No shopping list ID available for testing")
            return False
            
        return self.run_test(
            "Get Shopping List Details",
            "GET",
            f"shopping-lists/detail/{self.created_shopping_list_id}",
            200
        )[0]

    def test_update_shopping_list(self):
        """Test updating a shopping list"""
        if not hasattr(self, 'created_shopping_list_id') or not self.created_shopping_list_id:
            print("❌ No shopping list ID available for testing")
            return False
            
        update_data = {
            "title": "Updated Test Shopping List",
            "items": [
                {
                    "item": "Chicken breast",
                    "category": "proteins",
                    "quantity": "2 lbs",
                    "checked": True  # Mark as checked
                },
                {
                    "item": "Broccoli",
                    "category": "produce",
                    "quantity": "1 bunch",
                    "checked": False
                },
                {
                    "item": "Brown rice",
                    "category": "pantry",
                    "quantity": "1 bag",
                    "checked": False
                },
                {
                    "item": "Greek yogurt",
                    "category": "proteins",
                    "quantity": "1 container",
                    "checked": False
                }
            ]
        }
        
        return self.run_test(
            "Update Shopping List",
            "PUT",
            f"shopping-lists/{self.created_shopping_list_id}",
            200,
            data=update_data
        )[0]

    def test_generate_shopping_list_from_ai(self):
        """Test AI-powered shopping list generation"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        meal_plan_text = """
        Day 1:
        Breakfast: Greek yogurt with berries and nuts
        Lunch: Grilled chicken salad with mixed vegetables
        Dinner: Baked salmon with quinoa and steamed broccoli
        
        Day 2:
        Breakfast: Scrambled eggs with spinach and whole grain toast
        Lunch: Turkey and avocado wrap with whole wheat tortilla
        Dinner: Lean beef stir-fry with brown rice and mixed vegetables
        """
        
        generation_data = {
            "user_id": self.created_user_id,
            "meal_plan_text": meal_plan_text
        }
        
        print("   Note: AI shopping list generation may take 10-15 seconds...")
        success, response = self.run_test(
            "Generate Shopping List from AI",
            "POST",
            "shopping-lists/generate",
            200,
            data=generation_data
        )
        
        if success and 'shopping_list' in response:
            generated_list = response['shopping_list']
            print(f"   Generated list with {len(generated_list.get('items', []))} items")
            if 'ai_response' in response:
                print(f"   AI response preview: {response['ai_response'][:100]}...")
            return True
        return False

    def test_ai_chat_clean_formatting(self):
        """Test AI chat for clean formatting (no markdown)"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        chat_data = {
            "user_id": self.created_user_id,
            "message": "Create a 3-day meal plan for Type 2 diabetes"
        }
        
        print("   Note: AI response may take 10-15 seconds...")
        success, response = self.run_test(
            "AI Chat Clean Formatting Test",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success and 'response' in response:
            ai_response = response['response']
            print(f"   AI Response preview: {ai_response[:200]}...")
            
            # Check for markdown formatting that should NOT be present
            has_markdown = (
                '**' in ai_response or 
                '*' in ai_response or 
                '#' in ai_response or
                '##' in ai_response
            )
            
            # Check for shopping list prompt
            has_shopping_prompt = "Would you like me to create a shopping list" in ai_response
            
            if has_markdown:
                print("   ❌ Response contains markdown formatting (*, **, #)")
                return False
            else:
                print("   ✅ Response is clean (no markdown formatting)")
                
            if has_shopping_prompt:
                print("   ✅ Response includes shopping list prompt")
            else:
                print("   ⚠️  Response missing shopping list prompt")
                
            return True
        return False

def main():
    print("🧪 Starting GlucoPlanner API Tests")
    print("=" * 50)
    
    tester = GlucoPlannerAPITester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("Health Endpoint", tester.test_health_endpoint),
        ("Create User Profile", tester.test_create_user_profile),
        ("Get User Profile", tester.test_get_user_profile),
        ("Update User Profile", tester.test_update_user_profile),
        ("List Users", tester.test_list_users),
        ("AI Chat", tester.test_ai_chat),
        ("Get Chat History", tester.test_get_chat_history),
        ("Get Meal Plans", tester.test_get_meal_plans),
        ("Restaurant Search", tester.test_restaurant_search),
        ("Restaurant Details", tester.test_restaurant_details),
        ("Restaurant Analysis", tester.test_restaurant_analysis),
        ("Nutrition Search", tester.test_nutrition_search),
        ("Nutrition Details", tester.test_nutrition_details),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("\n✅ All tests passed!")
    
    if tester.created_user_id:
        print(f"\n📝 Created test user ID: {tester.created_user_id}")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())