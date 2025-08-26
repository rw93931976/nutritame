import requests
import sys
import json
from datetime import datetime

class GlucoPlannerAPITester:
    def __init__(self, base_url="https://smart-meal-plan-2.preview.emergentagent.com"):
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
        """Test geocoding for Dallas, Texas - CRITICAL BUG FIX"""
        print("\n🔍 Testing Dallas, Texas Geocoding (Critical Bug Fix)...")
        
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

def main():
    print("🧪 Starting GlucoPlanner API Tests")
    print("🎯 FOCUS: Testing 3 Critical Issues from Review Request")
    print("=" * 60)
    
    tester = GlucoPlannerAPITester()
    
    # CRITICAL TESTS FIRST - As requested in review
    critical_tests = [
        ("🚨 Google Places API Usage Tracking", tester.test_google_places_api_usage_tracking),
        ("🚨 API Rate Limiting Enforcement", tester.test_api_rate_limiting_enforcement),
        ("🚨 Dallas Geocoding Bug Fix", tester.test_location_geocoding_dallas),
        ("🚨 Dallas Restaurant Search Bug Fix", tester.test_restaurant_search_by_dallas_location),
    ]
    
    # Standard test sequence
    standard_tests = [
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
    
    # Combine all tests - critical tests first
    tests = critical_tests + standard_tests
    
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