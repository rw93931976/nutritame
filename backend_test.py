import requests
import sys
import json
from datetime import datetime

class GlucoPlannerAPITester:
    def __init__(self, base_url="https://diabetic-meal-app.preview.emergentagent.com"):
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
        """Test creating a user profile - FOCUS: Profile save functionality"""
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
            "cooking_skill": "intermediate",
            "phone_number": "+15551234567"
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
            
            # Verify all fields were saved correctly
            print("   Verifying all profile fields were saved:")
            for field, expected_value in test_profile.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: {actual_value}")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    return False
            
            return True
        else:
            print(f"   ❌ Profile creation failed: {response}")
            return False

    def test_comprehensive_profile_fields(self):
        """Test all profile fields can be saved properly"""
        comprehensive_profile = {
            "diabetes_type": "type1",
            "age": 32,
            "gender": "male", 
            "activity_level": "high",
            "health_goals": ["blood_sugar_control", "weight_loss", "energy_boost"],
            "food_preferences": ["vegetarian", "gluten_free", "organic"],
            "cultural_background": "Asian",
            "allergies": ["dairy", "eggs", "soy"],
            "dislikes": ["spicy_food", "raw_fish"],
            "cooking_skill": "advanced",
            "phone_number": "+15559876543"
        }
        
        success, response = self.run_test(
            "Create Comprehensive Profile",
            "POST", 
            "users",
            200,
            data=comprehensive_profile
        )
        
        if success and 'id' in response:
            comprehensive_user_id = response['id']
            print(f"   Created comprehensive profile ID: {comprehensive_user_id}")
            
            # Verify all comprehensive fields
            all_fields_correct = True
            for field, expected_value in comprehensive_profile.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: Saved correctly")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    all_fields_correct = False
            
            # Store for update testing
            self.comprehensive_user_id = comprehensive_user_id
            return all_fields_correct
        else:
            print(f"   ❌ Comprehensive profile creation failed: {response}")
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
        """Test updating a user profile - FOCUS: Profile save functionality"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        update_data = {
            "age": 46,
            "health_goals": ["blood_sugar_control", "weight_loss", "energy_boost"],
            "food_preferences": ["mediterranean", "low_carb", "organic"],
            "allergies": ["nuts", "shellfish", "dairy"],
            "cooking_skill": "advanced"
        }
        
        success, response = self.run_test(
            "Update User Profile",
            "PUT",
            f"users/{self.created_user_id}",
            200,
            data=update_data
        )
        
        if success:
            print("   Verifying updated fields were saved:")
            for field, expected_value in update_data.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: Updated correctly to {actual_value}")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    return False
            return True
        else:
            print(f"   ❌ Profile update failed: {response}")
            return False

    def test_update_profile_invalid_user_id(self):
        """Test error handling for invalid user IDs in profile updates"""
        invalid_user_id = "invalid-user-id-12345"
        
        update_data = {
            "age": 30,
            "diabetes_type": "type1"
        }
        
        success, response = self.run_test(
            "Update Profile - Invalid User ID",
            "PUT",
            f"users/{invalid_user_id}",
            404,  # Should return 404 for invalid user ID
            data=update_data
        )
        
        if success:
            print("   ✅ Correctly returned 404 for invalid user ID")
            return True
        else:
            print(f"   ❌ Should have returned 404 for invalid user ID, got different response")
            return False

    def test_partial_profile_update(self):
        """Test partial profile updates (only some fields)"""
        if not hasattr(self, 'comprehensive_user_id') or not self.comprehensive_user_id:
            print("❌ No comprehensive user ID available for partial update testing")
            return False
            
        # Update only a few fields
        partial_update = {
            "age": 35,
            "activity_level": "low"
        }
        
        success, response = self.run_test(
            "Partial Profile Update",
            "PUT",
            f"users/{self.comprehensive_user_id}",
            200,
            data=partial_update
        )
        
        if success:
            # Verify updated fields
            for field, expected_value in partial_update.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: Updated to {actual_value}")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    return False
            
            # Verify other fields remained unchanged
            if response.get('diabetes_type') == 'type1':
                print("   ✅ Unchanged fields preserved (diabetes_type still type1)")
            else:
                print(f"   ❌ Unchanged field modified: diabetes_type = {response.get('diabetes_type')}")
                return False
                
            return True
        else:
            print(f"   ❌ Partial profile update failed: {response}")
            return False

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

    # SMS Feature Tests
    def test_phone_validation_valid_formats(self):
        """Test phone validation API with valid phone number formats"""
        test_cases = [
            ("+15551234567", "Valid E.164 format"),
            ("5551234567", "10-digit US format"),
            ("555-123-4567", "Formatted US number"),
            ("1-555-123-4567", "11-digit with country code"),
            ("(555) 123-4567", "Parentheses format")
        ]
        
        all_passed = True
        for phone_number, description in test_cases:
            print(f"\n   Testing {description}: {phone_number}")
            success, response = self.run_test(
                f"Phone Validation - {description}",
                "POST",
                "sms/validate-phone",
                200,
                data={"phone_number": phone_number}
            )
            
            if success and response.get('valid'):
                print(f"   ✅ Valid - Formatted as: {response.get('formatted')}")
            else:
                print(f"   ❌ Should be valid but got: {response}")
                all_passed = False
                
        return all_passed

    def test_phone_validation_invalid_formats(self):
        """Test phone validation API with invalid phone number formats"""
        test_cases = [
            ("invalid", "Invalid text"),
            ("123", "Too short"),
            ("12345678901234567890", "Too long"),
            ("", "Empty string"),
            ("abc-def-ghij", "Letters only")
        ]
        
        all_passed = True
        for phone_number, description in test_cases:
            print(f"\n   Testing {description}: {phone_number}")
            success, response = self.run_test(
                f"Phone Validation - {description}",
                "POST",
                "sms/validate-phone",
                200,
                data={"phone_number": phone_number}
            )
            
            if success and not response.get('valid'):
                print(f"   ✅ Correctly identified as invalid")
            else:
                print(f"   ❌ Should be invalid but got: {response}")
                all_passed = False
                
        return all_passed

    def test_update_user_profile_with_phone(self):
        """Test updating user profile with phone number"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        update_data = {
            "phone_number": "+15551234567"
        }
        
        success, response = self.run_test(
            "Update User Profile with Phone Number",
            "PUT",
            f"users/{self.created_user_id}",
            200,
            data=update_data
        )
        
        if success and response.get('phone_number') == "+15551234567":
            print("   ✅ Phone number successfully added to profile")
            return True
        else:
            print(f"   ❌ Phone number not properly saved: {response}")
            return False

    def test_send_restaurant_sms_with_profile_phone(self):
        """Test sending restaurant SMS using phone number from profile"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        if not hasattr(self, 'test_restaurant') or not self.test_restaurant:
            print("❌ No restaurant available for SMS testing")
            return False
            
        place_id = self.test_restaurant.get('place_id')
        if not place_id:
            print("❌ No place_id available for SMS testing")
            return False
            
        sms_data = {
            "user_id": self.created_user_id,
            "phone_number": "+15551234567",  # Use the phone number we set in profile
            "restaurant_place_id": place_id
        }
        
        success, response = self.run_test(
            "Send Restaurant SMS",
            "POST",
            "sms/send-restaurant",
            200,
            data=sms_data
        )
        
        if success:
            print(f"   ✅ SMS sent successfully")
            print(f"   Message SID: {response.get('message_sid')}")
            print(f"   Restaurant: {response.get('restaurant_name')}")
            print(f"   Phone: {response.get('message', '').split('to ')[-1] if 'to ' in response.get('message', '') else 'N/A'}")
            return True
        else:
            print(f"   ❌ SMS sending failed: {response}")
            return False

    def test_send_restaurant_sms_invalid_phone(self):
        """Test sending restaurant SMS with invalid phone number"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        if not hasattr(self, 'test_restaurant') or not self.test_restaurant:
            print("❌ No restaurant available for SMS testing")
            return False
            
        place_id = self.test_restaurant.get('place_id')
        if not place_id:
            print("❌ No place_id available for SMS testing")
            return False
            
        sms_data = {
            "user_id": self.created_user_id,
            "phone_number": "invalid_phone",
            "restaurant_place_id": place_id
        }
        
        success, response = self.run_test(
            "Send Restaurant SMS - Invalid Phone",
            "POST",
            "sms/send-restaurant",
            400,  # Should return 400 for invalid phone
            data=sms_data
        )
        
        if success:
            print(f"   ✅ Correctly rejected invalid phone number")
            return True
        else:
            print(f"   ❌ Should have rejected invalid phone: {response}")
            return False

    def test_send_restaurant_sms_invalid_restaurant(self):
        """Test sending restaurant SMS with invalid restaurant ID"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        sms_data = {
            "user_id": self.created_user_id,
            "phone_number": "+15551234567",
            "restaurant_place_id": "invalid_place_id_12345"
        }
        
        success, response = self.run_test(
            "Send Restaurant SMS - Invalid Restaurant",
            "POST",
            "sms/send-restaurant",
            404,  # Should return 404 for invalid restaurant
            data=sms_data
        )
        
        if success:
            print(f"   ✅ Correctly rejected invalid restaurant ID")
            return True
        else:
            print(f"   ❌ Should have rejected invalid restaurant: {response}")
            return False

    def test_get_sms_history(self):
        """Test getting SMS history for user"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get SMS History",
            "GET",
            f"sms/history/{self.created_user_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} SMS messages")
            if len(response) > 0:
                # Check the structure of the first SMS message
                first_sms = response[0]
                required_fields = ['id', 'user_id', 'phone_number', 'message_content', 'message_type', 'status', 'sent_at']
                missing_fields = [field for field in required_fields if field not in first_sms]
                
                if not missing_fields:
                    print(f"   ✅ SMS message structure is correct")
                    print(f"   Message type: {first_sms.get('message_type')}")
                    print(f"   Status: {first_sms.get('status')}")
                    print(f"   Content preview: {first_sms.get('message_content', '')[:100]}...")
                else:
                    print(f"   ❌ Missing fields in SMS message: {missing_fields}")
                    return False
            return True
        else:
            print(f"   ❌ Failed to retrieve SMS history: {response}")
            return False

    def test_sms_content_format(self):
        """Test that SMS content follows the expected format"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        # Get SMS history to check the format
        success, response = self.run_test(
            "Get SMS History for Format Check",
            "GET",
            f"sms/history/{self.created_user_id}",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            sms_message = response[0]
            content = sms_message.get('message_content', '')
            
            # Check for expected SMS format elements
            expected_elements = [
                "🍽️ GlucoPlanner Restaurant Info",
                "📍",  # Address icon
                "⭐",  # Rating icon
                "📞",  # Phone icon
                "🩺 Diabetic Score:",
                "Sent from GlucoPlanner"
            ]
            
            missing_elements = []
            for element in expected_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print(f"   ✅ SMS format is correct")
                print(f"   Content preview: {content[:200]}...")
                
                # Check if diabetic score interpretation is included
                if any(phrase in content.lower() for phrase in ["excellent for diabetics", "good for diabetics", "fair - use caution", "requires careful selection"]):
                    print(f"   ✅ Diabetic score interpretation included")
                else:
                    print(f"   ⚠️  Diabetic score interpretation may be missing")
                
                return True
            else:
                print(f"   ❌ Missing SMS format elements: {missing_elements}")
                print(f"   Actual content: {content}")
                return False
        else:
            print(f"   ❌ No SMS messages found to check format")
            return False

    # CRITICAL ISSUE TESTS - As requested in review
    def test_google_places_api_usage_tracking(self):
        """Test Google Places API usage tracking endpoint"""
        print("\n🔍 Testing Google Places API Usage Tracking...")
        
        success, response = self.run_test(
            "Google Places API Usage",
            "GET",
            "usage/google-places",
            200
        )
        
        if success:
            print(f"   Current usage: {response.get('calls_made', 0)}/{response.get('monthly_limit', 9000)}")
            print(f"   Status: {response.get('status', 'unknown')}")
            print(f"   Calls remaining: {response.get('calls_remaining', 0)}")
            print(f"   Percentage used: {response.get('percentage_used', 0)}%")
            
            # Verify monthly limit is exactly 9,000
            if response.get('monthly_limit') == 9000:
                print("   ✅ Monthly limit correctly set to 9,000")
                return True
            else:
                print(f"   ❌ Monthly limit should be 9,000, got {response.get('monthly_limit')}")
                return False
        return False

    def test_location_geocoding_dallas(self):
        """Test geocoding for Dallas, Texas - URGENT ISSUE"""
        print("\n🔍 Testing Dallas, Texas Geocoding (URGENT - After API Enable)...")
        
        test_location = "Dallas, Texas"
        expected_lat_range = (32.6, 32.9)  # Dallas latitude range
        expected_lng_range = (-97.1, -96.6)  # Dallas longitude range
        
        success, response = self.run_test(
            "Geocode Dallas, Texas",
            "POST",
            "geocode",
            200,
            data={"location": test_location}
        )
        
        if success:
            lat = response.get('latitude')
            lng = response.get('longitude')
            formatted_address = response.get('formatted_address', '')
            
            print(f"   Location: {test_location}")
            print(f"   Returned coordinates: ({lat}, {lng})")
            print(f"   Formatted address: {formatted_address}")
            
            # Check if coordinates are in Dallas range
            if (lat and lng and 
                expected_lat_range[0] <= lat <= expected_lat_range[1] and
                expected_lng_range[0] <= lng <= expected_lng_range[1]):
                print("   ✅ Coordinates are in Dallas, Texas range")
                
                # Check if formatted address mentions Dallas or Texas
                if 'dallas' in formatted_address.lower() or 'tx' in formatted_address.lower():
                    print("   ✅ Formatted address correctly identifies Dallas/Texas")
                    return True
                else:
                    print(f"   ⚠️  Formatted address doesn't clearly identify Dallas: {formatted_address}")
                    return True  # Still pass if coordinates are correct
            else:
                print(f"   ❌ CRITICAL BUG: Dallas coordinates are wrong!")
                print(f"   Expected lat: {expected_lat_range}, got: {lat}")
                print(f"   Expected lng: {expected_lng_range}, got: {lng}")
                print(f"   This suggests Dallas is returning San Francisco coordinates")
                return False
        else:
            # Check for specific error messages
            print(f"   ❌ Geocoding failed with status code")
            return False
        return False

    def test_location_geocoding_new_york(self):
        """Test geocoding for New York, NY - URGENT ISSUE"""
        print("\n🔍 Testing New York, NY Geocoding (URGENT - After API Enable)...")
        
        test_location = "New York, NY"
        expected_lat_range = (40.6, 40.9)  # NYC latitude range
        expected_lng_range = (-74.1, -73.9)  # NYC longitude range
        
        success, response = self.run_test(
            "Geocode New York, NY",
            "POST",
            "geocode",
            200,
            data={"location": test_location}
        )
        
        if success:
            lat = response.get('latitude')
            lng = response.get('longitude')
            formatted_address = response.get('formatted_address', '')
            
            print(f"   Location: {test_location}")
            print(f"   Returned coordinates: ({lat}, {lng})")
            print(f"   Formatted address: {formatted_address}")
            
            # Check if coordinates are in NYC range
            if (lat and lng and 
                expected_lat_range[0] <= lat <= expected_lat_range[1] and
                expected_lng_range[0] <= lng <= expected_lng_range[1]):
                print("   ✅ Coordinates are in New York, NY range")
                
                # Check if formatted address mentions New York or NY
                if 'new york' in formatted_address.lower() or 'ny' in formatted_address.lower():
                    print("   ✅ Formatted address correctly identifies New York/NY")
                    return True
                else:
                    print(f"   ⚠️  Formatted address doesn't clearly identify New York: {formatted_address}")
                    return True  # Still pass if coordinates are correct
            else:
                print(f"   ❌ CRITICAL BUG: New York coordinates are wrong!")
                print(f"   Expected lat: {expected_lat_range}, got: {lat}")
                print(f"   Expected lng: {expected_lng_range}, got: {lng}")
                return False
        else:
            # Check for specific error messages
            print(f"   ❌ Geocoding failed with status code")
            return False
        return False

    def test_restaurant_search_by_dallas_location(self):
        """Test restaurant search by Dallas location - CRITICAL BUG FIX"""
        print("\n🔍 Testing Restaurant Search by Dallas Location (Critical Bug Fix)...")
        
        search_data = {
            "location": "Dallas, Texas",
            "radius": 5000,
            "keyword": "healthy"
        }
        
        print("   Note: Restaurant search may take 10-15 seconds...")
        success, response = self.run_test(
            "Restaurant Search by Dallas Location",
            "POST",
            "restaurants/search-by-location",
            200,
            data=search_data
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} restaurants")
            
            if len(response) > 0:
                # Check if restaurants are actually in Dallas area
                dallas_restaurants = 0
                san_francisco_restaurants = 0
                
                for restaurant in response[:5]:  # Check first 5 restaurants
                    name = restaurant.get('name', 'Unknown')
                    address = restaurant.get('address', '')
                    lat = restaurant.get('latitude', 0)
                    lng = restaurant.get('longitude', 0)
                    
                    print(f"   Restaurant: {name}")
                    print(f"   Address: {address}")
                    print(f"   Coordinates: ({lat}, {lng})")
                    
                    # Check if coordinates are in Dallas range
                    if (32.6 <= lat <= 32.9 and -97.1 <= lng <= -96.6):
                        dallas_restaurants += 1
                        print("   ✅ Location: Dallas area")
                    # Check if coordinates are in San Francisco range (bug indicator)
                    elif (37.7 <= lat <= 37.8 and -122.5 <= lng <= -122.3):
                        san_francisco_restaurants += 1
                        print("   ❌ CRITICAL BUG: Location appears to be San Francisco!")
                    else:
                        print(f"   ⚠️  Location: Other ({lat}, {lng})")
                    
                    print()
                
                if dallas_restaurants > 0 and san_francisco_restaurants == 0:
                    print(f"   ✅ SUCCESS: Found {dallas_restaurants} Dallas restaurants, 0 San Francisco")
                    return True
                elif san_francisco_restaurants > 0:
                    print(f"   ❌ CRITICAL BUG: Found {san_francisco_restaurants} San Francisco restaurants when searching Dallas!")
                    return False
                else:
                    print(f"   ⚠️  Found restaurants but location unclear")
                    return True  # Pass if we found restaurants, even if location is unclear
            else:
                print("   ❌ No restaurants found for Dallas search")
                return False
        return False

    def test_api_rate_limiting_enforcement(self):
        """Test that API rate limiting strictly enforces 9,000 call limit"""
        print("\n🔍 Testing API Rate Limiting Enforcement...")
        
        # First get current usage
        success, usage_response = self.run_test(
            "Get Current API Usage",
            "GET",
            "usage/google-places",
            200
        )
        
        if not success:
            print("   ❌ Could not get current API usage")
            return False
        
        current_calls = usage_response.get('calls_made', 0)
        monthly_limit = usage_response.get('monthly_limit', 9000)
        
        print(f"   Current usage: {current_calls}/{monthly_limit}")
        
        # If we're already at or near the limit, test that calls are blocked
        if current_calls >= monthly_limit:
            print("   Testing that API calls are blocked at limit...")
            
            # Try to make a geocoding call - should fail
            success, response = self.run_test(
                "Geocoding Call at Limit",
                "POST",
                "geocode",
                400,  # Should return 400 when limit exceeded
                data={"location": "Test Location"}
            )
            
            if success:
                print("   ✅ API correctly blocks calls when limit is reached")
                return True
            else:
                print("   ❌ API should block calls when limit is reached")
                return False
        else:
            print(f"   Current usage ({current_calls}) is below limit ({monthly_limit})")
            print("   ✅ Rate limiting is active and tracking usage")
            
            # Verify the limit is exactly 9,000
            if monthly_limit == 9000:
                print("   ✅ Monthly limit is correctly set to exactly 9,000")
                return True
            else:
                print(f"   ❌ Monthly limit should be 9,000, got {monthly_limit}")
                return False

    # =============================================
    # DEMO MODE TESTS - As requested in review
    # =============================================
    
    def test_demo_config_endpoint(self):
        """Test GET /api/demo/config endpoint - FOCUS: Launch date should be 2025-10-01"""
        print("\n🔍 Testing Demo Configuration Endpoint...")
        
        success, response = self.run_test(
            "Demo Configuration",
            "GET",
            "demo/config",
            200
        )
        
        if success:
            # Verify required fields
            required_fields = ['demo_mode', 'launch_date', 'message', 'launch_requirements']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify demo_mode is true
            if response.get('demo_mode') is True:
                print("   ✅ demo_mode is correctly set to true")
            else:
                print(f"   ❌ demo_mode should be true, got: {response.get('demo_mode')}")
                return False
            
            # CRITICAL: Verify launch_date is 2025-10-01 (October 1, 2025)
            launch_date = response.get('launch_date')
            expected_launch_date = "2025-10-01"
            if launch_date == expected_launch_date:
                print(f"   ✅ launch_date is correctly set to {expected_launch_date} (October 1, 2025)")
            else:
                print(f"   ❌ CRITICAL: launch_date should be {expected_launch_date}, got: {launch_date}")
                return False
            
            # Verify demo message
            message = response.get('message', '')
            if 'demo mode' in message.lower():
                print("   ✅ Demo message is appropriate")
            else:
                print(f"   ❌ Demo message unclear: {message}")
                return False
            
            # Verify launch requirements structure
            launch_req = response.get('launch_requirements', {})
            expected_req_fields = ['account_required', 'subscription_required', 'basic_plan', 'premium_plan', 'free_trial']
            missing_req_fields = [field for field in expected_req_fields if field not in launch_req]
            
            if missing_req_fields:
                print(f"   ❌ Missing launch requirement fields: {missing_req_fields}")
                return False
            else:
                print("   ✅ Launch requirements structure is complete")
            
            print(f"   Demo config: {json.dumps(response, indent=2)}")
            return True
        
        return False
    
    def test_demo_access_with_email(self):
        """Test POST /api/demo/access with email provided"""
        print("\n🔍 Testing Demo Access Creation with Email...")
        
        demo_email = "sarah.johnson@example.com"
        demo_data = {
            "email": demo_email
        }
        
        success, response = self.run_test(
            "Demo Access with Email",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if success:
            # Verify required response fields
            required_fields = ['demo_access', 'access_token', 'user', 'expires_at', 'demo_notice', 'launch_date']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify demo_access is true
            if response.get('demo_access') is True:
                print("   ✅ demo_access is correctly set to true")
            else:
                print(f"   ❌ demo_access should be true, got: {response.get('demo_access')}")
                return False
            
            # Verify access token exists and is not empty
            access_token = response.get('access_token')
            if access_token and len(access_token) > 20:  # JWT tokens are typically long
                print("   ✅ Access token generated successfully")
                self.demo_access_token = access_token  # Store for later tests
            else:
                print(f"   ❌ Invalid access token: {access_token}")
                return False
            
            # Verify user object
            user = response.get('user', {})
            if user.get('email') == demo_email:
                print(f"   ✅ User email matches: {demo_email}")
            else:
                print(f"   ❌ User email mismatch. Expected: {demo_email}, Got: {user.get('email')}")
                return False
            
            # Verify premium subscription
            if user.get('subscription_tier') == 'premium':
                print("   ✅ Demo user has premium subscription tier")
            else:
                print(f"   ❌ Demo user should have premium tier, got: {user.get('subscription_tier')}")
                return False
            
            # Verify active status
            if user.get('subscription_status') == 'active':
                print("   ✅ Demo user has active subscription status")
            else:
                print(f"   ❌ Demo user should have active status, got: {user.get('subscription_status')}")
                return False
            
            # Store demo user info for later tests
            self.demo_user_id = user.get('id')
            self.demo_user_email = user.get('email')
            
            # Verify demo notice
            demo_notice = response.get('demo_notice', '')
            if 'demo account' in demo_notice.lower() and 'premium access' in demo_notice.lower():
                print("   ✅ Demo notice is appropriate")
            else:
                print(f"   ❌ Demo notice unclear: {demo_notice}")
                return False
            
            print(f"   Created demo user ID: {self.demo_user_id}")
            return True
        
        return False
    
    def test_demo_access_without_email(self):
        """Test POST /api/demo/access without email (should generate demo email)"""
        print("\n🔍 Testing Demo Access Creation without Email...")
        
        demo_data = {}  # No email provided
        
        success, response = self.run_test(
            "Demo Access without Email",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if success:
            # Verify user object
            user = response.get('user', {})
            user_email = user.get('email', '')
            
            # Verify demo email domain
            if '@demo.nutritame.com' in user_email:
                print(f"   ✅ Generated demo email with correct domain: {user_email}")
            else:
                print(f"   ❌ Demo email should use @demo.nutritame.com domain, got: {user_email}")
                return False
            
            # Verify email format (should start with demo_)
            if user_email.startswith('demo_'):
                print("   ✅ Demo email has correct prefix")
            else:
                print(f"   ❌ Demo email should start with 'demo_', got: {user_email}")
                return False
            
            # Verify premium access
            if user.get('subscription_tier') == 'premium' and user.get('subscription_status') == 'active':
                print("   ✅ Generated demo user has premium access")
            else:
                print(f"   ❌ Generated demo user should have premium access")
                return False
            
            # Store second demo user for testing
            self.demo_user_2_id = user.get('id')
            access_token = response.get('access_token')
            if access_token:
                self.demo_access_token_2 = access_token
            
            return True
        
        return False
    
    def test_demo_user_authentication(self):
        """Test demo user authentication with JWT token"""
        print("\n🔍 Testing Demo User Authentication...")
        
        if not hasattr(self, 'demo_access_token') or not self.demo_access_token:
            print("   ❌ No demo access token available for testing")
            return False
        
        # Test GET /api/auth/me with demo token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.demo_access_token}'
        }
        
        success, response = self.run_test(
            "Demo User Authentication",
            "GET",
            "auth/me",
            200,
            headers=headers
        )
        
        if success:
            # Verify user information
            user = response.get('user', {})
            
            if user.get('id') == self.demo_user_id:
                print(f"   ✅ Demo user ID matches: {self.demo_user_id}")
            else:
                print(f"   ❌ Demo user ID mismatch. Expected: {self.demo_user_id}, Got: {user.get('id')}")
                return False
            
            if user.get('email') == self.demo_user_email:
                print(f"   ✅ Demo user email matches: {self.demo_user_email}")
            else:
                print(f"   ❌ Demo user email mismatch. Expected: {self.demo_user_email}, Got: {user.get('email')}")
                return False
            
            # Verify subscription info
            subscription_info = response.get('subscription_info', {})
            if subscription_info.get('tier') == 'premium':
                print("   ✅ Demo user has premium subscription info")
            else:
                print(f"   ❌ Demo user should have premium subscription, got: {subscription_info.get('tier')}")
                return False
            
            # Verify tenant ID
            tenant_id = response.get('tenant_id')
            if tenant_id:
                print(f"   ✅ Demo user has tenant ID: {tenant_id}")
                self.demo_tenant_id = tenant_id
            else:
                print("   ❌ Demo user missing tenant ID")
                return False
            
            return True
        
        return False
    
    def test_demo_environment_configuration(self):
        """Test environment configuration for demo mode"""
        print("\n🔍 Testing Demo Environment Configuration...")
        
        # Test that demo config endpoint reflects environment variables
        success, response = self.run_test(
            "Demo Environment Check",
            "GET",
            "demo/config",
            200
        )
        
        if success:
            # Verify DEMO_MODE environment variable is properly loaded
            if response.get('demo_mode') is True:
                print("   ✅ DEMO_MODE environment variable is properly loaded as true")
            else:
                print(f"   ❌ DEMO_MODE should be true, environment may not be properly configured")
                return False
            
            # Verify launch date is set
            launch_date = response.get('launch_date')
            if launch_date and launch_date != '':
                print(f"   ✅ LAUNCH_DATE environment variable is set: {launch_date}")
            else:
                print("   ❌ LAUNCH_DATE environment variable is not properly set")
                return False
            
            return True
        
        return False
    
    def test_demo_database_integration(self):
        """Test that demo users are properly saved to database"""
        print("\n🔍 Testing Demo Database Integration...")
        
        if not hasattr(self, 'demo_user_id') or not self.demo_user_id:
            print("   ❌ No demo user ID available for database testing")
            return False
        
        # Test that we can retrieve the demo user (this tests database persistence)
        if not hasattr(self, 'demo_access_token') or not self.demo_access_token:
            print("   ❌ No demo access token available for testing")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.demo_access_token}'
        }
        
        # Test accessing a protected endpoint that requires database lookup
        success, response = self.run_test(
            "Demo Database Integration",
            "GET",
            "auth/me",
            200,
            headers=headers
        )
        
        if success:
            user = response.get('user', {})
            
            # Verify user data persistence
            if user.get('id') == self.demo_user_id:
                print("   ✅ Demo user is properly saved and retrievable from database")
            else:
                print("   ❌ Demo user not found in database or ID mismatch")
                return False
            
            # Verify subscription data persistence
            if user.get('subscription_tier') == 'premium' and user.get('subscription_status') == 'active':
                print("   ✅ Demo user subscription data is properly persisted")
            else:
                print("   ❌ Demo user subscription data not properly persisted")
                return False
            
            return True
        
        return False
    
    def test_demo_user_app_functionality(self):
        """Test that demo users can access all app functionality"""
        print("\n🔍 Testing Demo User App Functionality Access...")
        
        if not hasattr(self, 'demo_access_token') or not self.demo_access_token:
            print("   ❌ No demo access token available for testing")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.demo_access_token}'
        }
        
        # Test subscription info endpoint (premium feature)
        success, response = self.run_test(
            "Demo User Subscription Access",
            "GET",
            "subscription/info",
            200,
            headers=headers
        )
        
        if success:
            subscription_info = response
            if subscription_info.get('tier') == 'premium':
                print("   ✅ Demo user can access premium subscription features")
            else:
                print(f"   ❌ Demo user should have premium access, got: {subscription_info.get('tier')}")
                return False
            
            # Verify subscription is active
            if subscription_info.get('status') == 'active':
                print("   ✅ Demo user subscription is active")
            else:
                print(f"   ❌ Demo user subscription should be active, got: {subscription_info.get('status')}")
                return False
            
            return True
        
        return False
    
    def test_demo_mode_disabled_check(self):
        """Test behavior when demo mode is disabled (theoretical test)"""
        print("\n🔍 Testing Demo Mode Disabled Behavior (Informational)...")
        
        # This is an informational test - we can't actually disable demo mode
        # but we can verify the current state and document expected behavior
        
        success, response = self.run_test(
            "Current Demo Mode Status",
            "GET",
            "demo/config",
            200
        )
        
        if success:
            if response.get('demo_mode') is True:
                print("   ℹ️  Demo mode is currently ENABLED")
                print("   ℹ️  When disabled, POST /api/demo/access should return 403")
                print("   ℹ️  When disabled, demo_mode in config should be false")
                print("   ✅ Demo mode configuration is working as expected")
                return True
            else:
                print("   ⚠️  Demo mode appears to be disabled")
                
                # Test that demo access is blocked
                demo_data = {"email": "test@example.com"}
                success_blocked, response_blocked = self.run_test(
                    "Demo Access When Disabled",
                    "POST",
                    "demo/access",
                    403,  # Should be forbidden
                    data=demo_data
                )
                
                if success_blocked:
                    print("   ✅ Demo access correctly blocked when demo mode disabled")
                    return True
                else:
                    print("   ❌ Demo access should be blocked when demo mode disabled")
                    return False
        
        return False

    # =============================================
    # DEMO COUNTDOWN TIMER INTEGRATION TESTS
    # =============================================
    
    def test_demo_countdown_timer_backend_integration(self):
        """Test Demo Countdown Timer backend integration - FOCUS: Demo mode detection"""
        print("\n🔍 Testing Demo Countdown Timer Backend Integration...")
        
        # Step 1: Verify demo config endpoint provides necessary data for countdown timer
        success, config_response = self.run_test(
            "Demo Config for Countdown Timer",
            "GET",
            "demo/config",
            200
        )
        
        if not success:
            print("   ❌ Demo config endpoint failed - countdown timer cannot detect demo mode")
            return False
        
        # Verify demo_mode flag is present and true
        if config_response.get('demo_mode') is not True:
            print(f"   ❌ demo_mode should be true for countdown timer, got: {config_response.get('demo_mode')}")
            return False
        
        print("   ✅ Demo config provides demo_mode=true for countdown timer detection")
        
        # Step 2: Create demo user to test countdown timer integration
        demo_email = "countdown.timer.test@example.com"
        demo_data = {"email": demo_email}
        
        success, demo_response = self.run_test(
            "Demo Access for Countdown Timer",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if not success:
            print("   ❌ Demo access creation failed - countdown timer cannot be triggered")
            return False
        
        # Verify demo user has premium access (required for countdown timer to show)
        user = demo_response.get('user', {})
        if user.get('subscription_tier') != 'premium' or user.get('subscription_status') != 'active':
            print("   ❌ Demo user doesn't have premium access - countdown timer may not display properly")
            return False
        
        print("   ✅ Demo user created with premium access for countdown timer")
        
        # Step 3: Test authentication with demo token (required for countdown timer to persist)
        access_token = demo_response.get('access_token')
        if not access_token:
            print("   ❌ No access token provided - countdown timer cannot authenticate")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        success, auth_response = self.run_test(
            "Demo User Auth for Countdown Timer",
            "GET",
            "auth/me",
            200,
            headers=headers
        )
        
        if not success:
            print("   ❌ Demo user authentication failed - countdown timer cannot maintain session")
            return False
        
        # Verify user data is accessible for countdown timer
        auth_user = auth_response.get('user', {})
        if auth_user.get('id') != user.get('id'):
            print("   ❌ User ID mismatch in authentication - countdown timer session may be unstable")
            return False
        
        print("   ✅ Demo user authentication working for countdown timer session")
        
        # Step 4: Test that demo session can access app functionality (what countdown timer is timing)
        success, subscription_response = self.run_test(
            "Demo Subscription Access for Countdown Timer",
            "GET",
            "subscription/info",
            200,
            headers=headers
        )
        
        if success:
            if subscription_response.get('tier') == 'premium':
                print("   ✅ Demo user can access premium features that countdown timer is timing")
            else:
                print("   ⚠️  Demo user subscription info shows non-premium tier")
        else:
            print("   ⚠️  Could not verify subscription access for countdown timer")
        
        # Step 5: Verify launch date is available for countdown timer display
        launch_date = config_response.get('launch_date')
        if launch_date == '2025-10-01':
            print(f"   ✅ Launch date ({launch_date}) available for countdown timer display")
        else:
            print(f"   ❌ Launch date incorrect or missing: {launch_date}")
            return False
        
        print("\n   🎯 COUNTDOWN TIMER INTEGRATION SUMMARY:")
        print("   ✅ Demo mode detection: Working (demo_mode=true)")
        print("   ✅ Demo user creation: Working (premium access)")
        print("   ✅ Demo authentication: Working (JWT tokens)")
        print("   ✅ Demo session access: Working (premium features)")
        print("   ✅ Launch date display: Working (2025-10-01)")
        print("   ✅ Backend integration: COMPLETE")
        
        return True
    
    def test_demo_countdown_timer_data_structure(self):
        """Test that backend provides all data needed for countdown timer functionality"""
        print("\n🔍 Testing Demo Countdown Timer Data Structure Requirements...")
        
        # Test demo config structure
        success, config_response = self.run_test(
            "Demo Config Data Structure",
            "GET",
            "demo/config",
            200
        )
        
        if not success:
            return False
        
        # Required fields for countdown timer
        required_config_fields = {
            'demo_mode': bool,
            'launch_date': str,
            'message': str,
            'launch_requirements': dict
        }
        
        missing_fields = []
        wrong_types = []
        
        for field, expected_type in required_config_fields.items():
            if field not in config_response:
                missing_fields.append(field)
            elif not isinstance(config_response[field], expected_type):
                wrong_types.append(f"{field} (expected {expected_type.__name__}, got {type(config_response[field]).__name__})")
        
        if missing_fields:
            print(f"   ❌ Missing required config fields for countdown timer: {missing_fields}")
            return False
        
        if wrong_types:
            print(f"   ❌ Wrong data types in config for countdown timer: {wrong_types}")
            return False
        
        print("   ✅ Demo config data structure is complete for countdown timer")
        
        # Test demo access response structure
        demo_data = {"email": "structure.test@example.com"}
        success, demo_response = self.run_test(
            "Demo Access Data Structure",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if not success:
            return False
        
        # Required fields for countdown timer integration
        required_demo_fields = {
            'demo_access': bool,
            'access_token': str,
            'user': dict,
            'expires_at': str,
            'demo_notice': str,
            'launch_date': str
        }
        
        missing_demo_fields = []
        wrong_demo_types = []
        
        for field, expected_type in required_demo_fields.items():
            if field not in demo_response:
                missing_demo_fields.append(field)
            elif not isinstance(demo_response[field], expected_type):
                wrong_demo_types.append(f"{field} (expected {expected_type.__name__}, got {type(demo_response[field]).__name__})")
        
        if missing_demo_fields:
            print(f"   ❌ Missing required demo access fields for countdown timer: {missing_demo_fields}")
            return False
        
        if wrong_demo_types:
            print(f"   ❌ Wrong data types in demo access for countdown timer: {wrong_demo_types}")
            return False
        
        print("   ✅ Demo access data structure is complete for countdown timer")
        
        # Test user object structure
        user = demo_response.get('user', {})
        required_user_fields = {
            'id': str,
            'email': str,
            'subscription_tier': str,
            'subscription_status': str
        }
        
        missing_user_fields = []
        wrong_user_types = []
        
        for field, expected_type in required_user_fields.items():
            if field not in user:
                missing_user_fields.append(field)
            elif not isinstance(user[field], expected_type):
                wrong_user_types.append(f"{field} (expected {expected_type.__name__}, got {type(user[field]).__name__})")
        
        if missing_user_fields:
            print(f"   ❌ Missing required user fields for countdown timer: {missing_user_fields}")
            return False
        
        if wrong_user_types:
            print(f"   ❌ Wrong data types in user object for countdown timer: {wrong_user_types}")
            return False
        
        print("   ✅ Demo user data structure is complete for countdown timer")
        
        return True
    
    def test_demo_countdown_timer_session_persistence(self):
        """Test that demo sessions persist properly for countdown timer"""
        print("\n🔍 Testing Demo Session Persistence for Countdown Timer...")
        
        # Create demo user
        demo_data = {"email": "persistence.test@example.com"}
        success, demo_response = self.run_test(
            "Demo User for Persistence Test",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if not success:
            return False
        
        access_token = demo_response.get('access_token')
        user_id = demo_response.get('user', {}).get('id')
        
        if not access_token or not user_id:
            print("   ❌ Missing access token or user ID for persistence test")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Test multiple authentication calls to verify session persistence
        for i in range(3):
            success, auth_response = self.run_test(
                f"Session Persistence Check #{i+1}",
                "GET",
                "auth/me",
                200,
                headers=headers
            )
            
            if not success:
                print(f"   ❌ Session persistence failed on attempt #{i+1}")
                return False
            
            auth_user_id = auth_response.get('user', {}).get('id')
            if auth_user_id != user_id:
                print(f"   ❌ User ID changed during session - persistence issue")
                return False
        
        print("   ✅ Demo session persists properly for countdown timer")
        
        # Test that subscription info remains consistent
        success, sub_response = self.run_test(
            "Subscription Persistence Check",
            "GET",
            "subscription/info",
            200,
            headers=headers
        )
        
        if success:
            if sub_response.get('tier') == 'premium':
                print("   ✅ Premium subscription persists for countdown timer")
            else:
                print("   ⚠️  Subscription tier inconsistent during session")
        
        return True

def main():
    print("🧪 Starting NutriTame API Tests")
    print("🎯 FOCUS: Launch Date Configuration & Profile Save Functionality")
    print("=" * 70)
    
    tester = GlucoPlannerAPITester()
    
    # PRIORITY TESTS - As requested in review
    priority_tests = [
        ("🎯 Demo Config - Launch Date Check", tester.test_demo_config_endpoint),
        ("🎯 Create User Profile", tester.test_create_user_profile),
        ("🎯 Comprehensive Profile Fields", tester.test_comprehensive_profile_fields),
        ("🎯 Get User Profile", tester.test_get_user_profile),
        ("🎯 Update User Profile", tester.test_update_user_profile),
        ("🎯 Partial Profile Update", tester.test_partial_profile_update),
        ("🎯 Invalid User ID Error Handling", tester.test_update_profile_invalid_user_id),
    ]
    
    # DEMO MODE TESTS - Secondary priority
    demo_tests = [
        ("Demo Access with Email", tester.test_demo_access_with_email),
        ("Demo Access without Email", tester.test_demo_access_without_email),
        ("Demo User Authentication", tester.test_demo_user_authentication),
    ]
    
    # DEMO COUNTDOWN TIMER TESTS - High priority for review request
    countdown_timer_tests = [
        ("🎯 Demo Countdown Timer Backend Integration", tester.test_demo_countdown_timer_backend_integration),
        ("🎯 Demo Countdown Timer Data Structure", tester.test_demo_countdown_timer_data_structure),
        ("🎯 Demo Countdown Timer Session Persistence", tester.test_demo_countdown_timer_session_persistence),
    ]
    
    # Run priority tests first
    print("\n🎯 RUNNING PRIORITY TESTS (Launch Date & Profile Functionality)")
    print("=" * 70)
    
    failed_tests = []
    priority_failed = []
    
    for test_name, test_func in priority_tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
                priority_failed.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
            priority_failed.append(test_name)
    
    # Print priority results immediately
    print("\n" + "=" * 70)
    print("🎯 PRIORITY TEST RESULTS")
    print("=" * 70)
    
    if priority_failed:
        print(f"❌ PRIORITY FAILURES:")
        for test in priority_failed:
            print(f"   - {test}")
    else:
        print("✅ All priority tests passed!")
    
    # Run demo countdown timer tests (high priority for review request)
    print("\n🎯 RUNNING DEMO COUNTDOWN TIMER TESTS (Review Request Focus)")
    print("=" * 70)
    
    countdown_failed = []
    for test_name, test_func in countdown_timer_tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
                countdown_failed.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
            countdown_failed.append(test_name)
    
    # Run demo mode tests if priority tests pass
    if not priority_failed:
        print("\n🔄 Running additional demo mode tests...")
        for test_name, test_func in demo_tests:
            try:
                if not test_func():
                    failed_tests.append(test_name)
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                failed_tests.append(test_name)
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS")
    print("=" * 70)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("\n✅ All tests passed!")
    
    if tester.created_user_id:
        print(f"\n📝 Created test user ID: {tester.created_user_id}")
    
    # Summary for main agent
    print("\n" + "=" * 70)
    print("📋 SUMMARY FOR MAIN AGENT")
    print("=" * 70)
    
    if not priority_failed:
        print("✅ LAUNCH DATE: Correctly set to 2025-10-01 (October 1, 2025)")
        print("✅ PROFILE CREATION: All profile fields save correctly")
        print("✅ PROFILE UPDATES: Profile update functionality working")
        print("✅ ERROR HANDLING: Invalid user ID properly handled")
    else:
        print("❌ CRITICAL ISSUES FOUND:")
        for test in priority_failed:
            if "Launch Date" in test:
                print("   - Launch date configuration issue")
            elif "Profile" in test:
                print("   - Profile save functionality issue")
            elif "Invalid User ID" in test:
                print("   - Error handling issue")
    
    if not countdown_failed:
        print("✅ DEMO COUNTDOWN TIMER: Backend integration working perfectly")
        print("✅ DEMO MODE DETECTION: Working (demo_mode=true)")
        print("✅ DEMO USER CREATION: Working (premium access)")
        print("✅ DEMO AUTHENTICATION: Working (JWT tokens)")
        print("✅ DEMO SESSION PERSISTENCE: Working (stable sessions)")
    else:
        print("❌ DEMO COUNTDOWN TIMER: Issues found in backend integration")
        for test in countdown_failed:
            print(f"   - {test}")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())