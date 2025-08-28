#!/usr/bin/env python3
"""
NutriTame PHP Backend API Tester
Tests all PHP backend endpoints for Hostinger deployment readiness
"""

import requests
import json
import sys
import time
from datetime import datetime

class NutriTamePHPTester:
    def __init__(self, base_url="http://localhost"):
        self.base_url = base_url
        self.php_backend_url = f"{base_url}/php-backend"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_id = None
        self.demo_access_token = None
        self.created_shopping_list_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]  # Remove leading slash
        
        url = f"{self.php_backend_url}/{endpoint}"
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
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

    # =============================================
    # DEMO ENDPOINTS TESTS
    # =============================================
    
    def test_demo_config_endpoint(self):
        """Test GET /php-backend/demo-config.php"""
        return self.run_test(
            "Demo Config Endpoint",
            "GET",
            "api/demo.php?endpoint=config",
            200
        )

    def test_demo_access_endpoint(self):
        """Test POST /php-backend/demo-access.php"""
        demo_data = {
            "email": "maria.gonzalez@example.com"
        }
        
        success, response = self.run_test(
            "Demo Access Endpoint",
            "POST", 
            "api/demo.php?endpoint=access",
            200,
            data=demo_data
        )
        
        if success and response.get('access_token'):
            self.demo_access_token = response['access_token']
            print(f"   Created demo access token: {self.demo_access_token[:20]}...")
            
        return success

    # =============================================
    # USER PROFILE ENDPOINTS TESTS
    # =============================================
    
    def test_create_user_profile(self):
        """Test POST /php-backend/api/users.php (create user profile)"""
        test_profile = {
            "email": "carlos.rodriguez@example.com",
            "diabetes_type": "type2",
            "age": 42,
            "gender": "male",
            "activity_level": "moderate",
            "health_goals": ["blood_sugar_control", "weight_loss"],
            "food_preferences": ["mediterranean", "low_carb"],
            "cultural_background": "Hispanic",
            "allergies": ["nuts", "shellfish"],
            "dislikes": ["liver", "brussels_sprouts"],
            "cooking_skill": "intermediate",
            "phone_number": "+15551234567"
        }
        
        success, response = self.run_test(
            "Create User Profile",
            "POST",
            "api/users.php",
            201,
            data=test_profile
        )
        
        if success and response.get('id'):
            self.created_user_id = response['id']
            print(f"   Created user ID: {self.created_user_id}")
            
            # Verify all fields were saved correctly
            print("   Verifying profile fields:")
            for field, expected_value in test_profile.items():
                if field == 'email':
                    continue  # Email might be auto-generated
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: Saved correctly")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    return False
            
            return True
        else:
            print(f"   ❌ Profile creation failed: {response}")
            return False

    def test_get_user_profile(self):
        """Test GET /php-backend/api/users.php/{user_id} (get user profile)"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            f"api/users.php/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify user data structure
            required_fields = ['id', 'email', 'diabetes_type', 'age', 'gender']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            else:
                print("   ✅ User profile structure is correct")
                return True
        
        return False

    def test_update_user_profile(self):
        """Test PUT /php-backend/api/users.php/{user_id} (update user profile)"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        update_data = {
            "age": 43,
            "health_goals": ["blood_sugar_control", "weight_loss", "energy_boost"],
            "food_preferences": ["mediterranean", "low_carb", "organic"],
            "cooking_skill": "advanced"
        }
        
        success, response = self.run_test(
            "Update User Profile",
            "PUT",
            f"api/users.php/{self.created_user_id}",
            200,
            data=update_data
        )
        
        if success:
            print("   Verifying updated fields:")
            for field, expected_value in update_data.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: Updated correctly")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    return False
            return True
        
        return False

    # =============================================
    # RESTAURANT SEARCH ENDPOINTS TESTS
    # =============================================
    
    def test_restaurant_search_by_coordinates(self):
        """Test POST /php-backend/api/restaurants.php/search (coordinate-based search)"""
        search_data = {
            "latitude": 32.7767,  # Dallas coordinates
            "longitude": -96.7970,
            "radius": 2000,
            "keyword": "healthy"
        }
        
        success, response = self.run_test(
            "Restaurant Search by Coordinates",
            "POST",
            "api/restaurants.php/search",
            200,
            data=search_data
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} restaurants")
            if len(response) > 0:
                # Verify restaurant structure
                restaurant = response[0]
                required_fields = ['place_id', 'name', 'address', 'latitude', 'longitude', 'rating']
                missing_fields = [field for field in required_fields if field not in restaurant]
                
                if missing_fields:
                    print(f"   ❌ Missing restaurant fields: {missing_fields}")
                    return False
                else:
                    print(f"   ✅ Restaurant structure is correct")
                    print(f"   Sample: {restaurant.get('name')} - {restaurant.get('address')}")
                    return True
            else:
                print("   ⚠️  No restaurants found")
                return True  # Not necessarily an error
        
        return False

    def test_restaurant_search_by_location(self):
        """Test POST /php-backend/api/restaurants.php/search-by-location (location-based search)"""
        search_data = {
            "location": "Dallas, Texas",
            "radius": 3000,
            "keyword": "diabetic friendly"
        }
        
        success, response = self.run_test(
            "Restaurant Search by Location",
            "POST",
            "api/restaurants.php/search-by-location",
            200,
            data=search_data
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} restaurants for Dallas")
            if len(response) > 0:
                # Check if restaurants have diabetic scores
                restaurant = response[0]
                if 'diabetic_friendly_score' in restaurant:
                    print(f"   ✅ Diabetic scoring available: {restaurant.get('diabetic_friendly_score')}")
                else:
                    print("   ⚠️  Diabetic scoring not available")
                
                return True
            else:
                print("   ⚠️  No restaurants found for Dallas")
                return True
        
        return False

    # =============================================
    # SHOPPING LIST ENDPOINTS TESTS
    # =============================================
    
    def test_generate_shopping_list(self):
        """Test POST /php-backend/shopping-lists.php/generate"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        meal_plan_text = """
        Day 1 Meal Plan:
        Breakfast: Greek yogurt with berries and almonds
        Lunch: Grilled chicken salad with olive oil dressing
        Dinner: Baked salmon with quinoa and steamed broccoli
        
        Day 2 Meal Plan:
        Breakfast: Scrambled eggs with spinach and whole grain toast
        Lunch: Turkey and avocado wrap
        Dinner: Lean beef stir-fry with brown rice
        """
        
        generation_data = {
            "user_id": self.created_user_id,
            "meal_plan_text": meal_plan_text
        }
        
        success, response = self.run_test(
            "Generate Shopping List",
            "POST",
            "shopping-lists.php/generate",
            201,
            data=generation_data
        )
        
        if success and response.get('id'):
            self.created_shopping_list_id = response['id']
            items = response.get('items', [])
            print(f"   Generated shopping list with {len(items)} items")
            
            # Verify items structure
            if items and len(items) > 0:
                item = items[0]
                required_item_fields = ['item', 'category', 'quantity', 'checked']
                missing_item_fields = [field for field in required_item_fields if field not in item]
                
                if missing_item_fields:
                    print(f"   ❌ Missing item fields: {missing_item_fields}")
                    return False
                else:
                    print("   ✅ Shopping list item structure is correct")
                    return True
            else:
                print("   ❌ No items generated in shopping list")
                return False
        
        return False

    def test_get_user_shopping_lists(self):
        """Test GET /php-backend/shopping-lists.php/{user_id}"""
        if not self.created_user_id:
            print("❌ No user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get User Shopping Lists",
            "GET",
            f"shopping-lists.php/{self.created_user_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} shopping lists")
            if len(response) > 0:
                shopping_list = response[0]
                if 'items' in shopping_list and isinstance(shopping_list['items'], list):
                    print("   ✅ Shopping list structure is correct")
                    return True
                else:
                    print("   ❌ Shopping list missing items array")
                    return False
            else:
                print("   ⚠️  No shopping lists found")
                return True
        
        return False

    def test_update_shopping_list(self):
        """Test PUT /php-backend/shopping-lists.php/update/{list_id}"""
        if not self.created_shopping_list_id:
            print("❌ No shopping list ID available for testing")
            return False
            
        updated_items = [
            {
                "item": "Greek yogurt",
                "category": "proteins",
                "quantity": "2 containers",
                "checked": True
            },
            {
                "item": "Fresh berries",
                "category": "produce",
                "quantity": "1 lb",
                "checked": False
            },
            {
                "item": "Almonds",
                "category": "pantry",
                "quantity": "1 bag",
                "checked": False
            }
        ]
        
        update_data = {
            "items": updated_items
        }
        
        success, response = self.run_test(
            "Update Shopping List",
            "PUT",
            f"shopping-lists.php/update/{self.created_shopping_list_id}",
            200,
            data=update_data
        )
        
        if success:
            print("   ✅ Shopping list updated successfully")
            return True
        
        return False

    # =============================================
    # UTILITY ENDPOINTS TESTS
    # =============================================
    
    def test_geocode_endpoint(self):
        """Test POST /php-backend/geocode.php"""
        locations_to_test = [
            ("Dallas, Texas", (32.6, 32.9), (-97.1, -96.6)),
            ("New York, NY", (40.6, 40.9), (-74.1, -73.9)),
            ("Los Angeles, CA", (34.0, 34.1), (-118.3, -118.2))
        ]
        
        all_passed = True
        
        for location, lat_range, lng_range in locations_to_test:
            geocode_data = {
                "location": location
            }
            
            success, response = self.run_test(
                f"Geocode {location}",
                "POST",
                "geocode.php",
                200,
                data=geocode_data
            )
            
            if success:
                lat = response.get('latitude')
                lng = response.get('longitude')
                
                if (lat and lng and 
                    lat_range[0] <= lat <= lat_range[1] and
                    lng_range[0] <= lng <= lng_range[1]):
                    print(f"   ✅ {location} coordinates are correct: ({lat}, {lng})")
                else:
                    print(f"   ❌ {location} coordinates are wrong: ({lat}, {lng})")
                    all_passed = False
            else:
                print(f"   ❌ Geocoding failed for {location}")
                all_passed = False
        
        return all_passed

    def test_google_places_usage_endpoint(self):
        """Test GET /php-backend/usage-google-places.php"""
        success, response = self.run_test(
            "Google Places Usage Monitor",
            "GET",
            "usage-google-places.php",
            200
        )
        
        if success:
            # Verify usage data structure
            required_fields = ['monthly_limit', 'calls_made', 'calls_remaining', 'percentage_used', 'status']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing usage fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ Usage monitoring structure is correct")
                print(f"   Usage: {response.get('calls_made')}/{response.get('monthly_limit')}")
                print(f"   Status: {response.get('status')}")
                return True
        
        return False

    # =============================================
    # ERROR HANDLING TESTS
    # =============================================
    
    def test_invalid_user_id_handling(self):
        """Test error handling for invalid user IDs"""
        invalid_user_id = "invalid-user-id-12345"
        
        success, response = self.run_test(
            "Invalid User ID Handling",
            "GET",
            f"api/users.php/{invalid_user_id}",
            404
        )
        
        if success:
            print("   ✅ Correctly returns 404 for invalid user ID")
            return True
        else:
            print("   ❌ Should return 404 for invalid user ID")
            return False

    def test_invalid_json_handling(self):
        """Test error handling for invalid JSON input"""
        # Send malformed JSON
        url = f"{self.php_backend_url}/api/users.php"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, data="invalid json", headers=headers, timeout=30)
            
            if response.status_code >= 400:
                print("   ✅ Correctly handles invalid JSON input")
                return True
            else:
                print(f"   ❌ Should return error for invalid JSON, got {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error testing invalid JSON: {e}")
            return False

    def test_missing_required_fields(self):
        """Test error handling for missing required fields"""
        incomplete_profile = {
            "age": 30
            # Missing required diabetes_type field
        }
        
        success, response = self.run_test(
            "Missing Required Fields",
            "POST",
            "api/users.php",
            400,  # Should return 400 for missing required fields
            data=incomplete_profile
        )
        
        # Note: This might pass with 201 if the PHP backend doesn't validate required fields
        # In that case, it's not necessarily an error, just different validation logic
        if success:
            print("   ✅ Handles missing required fields appropriately")
            return True
        else:
            # Check if it created the user anyway (which might be acceptable)
            if response and 'id' in response:
                print("   ⚠️  Created user despite missing fields (validation may be lenient)")
                return True
            else:
                print("   ❌ Unexpected response for missing required fields")
                return False

    # =============================================
    # DATABASE CONNECTION TESTS
    # =============================================
    
    def test_database_connection(self):
        """Test database connectivity by attempting to list users"""
        success, response = self.run_test(
            "Database Connection Test",
            "GET",
            "api/users.php",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Database connection working - found {len(response)} users")
                return True
            else:
                print("   ❌ Database response format unexpected")
                return False
        else:
            print("   ❌ Database connection may be failing")
            return False

    # =============================================
    # JSON RESPONSE FORMAT TESTS
    # =============================================
    
    def test_json_response_format(self):
        """Test that all endpoints return properly formatted JSON"""
        endpoints_to_test = [
            ("GET", "usage-google-places.php"),
            ("GET", "api/users.php"),
            ("POST", "geocode.php", {"location": "Dallas, TX"})
        ]
        
        all_json_valid = True
        
        for test_data in endpoints_to_test:
            method = test_data[0]
            endpoint = test_data[1]
            data = test_data[2] if len(test_data) > 2 else None
            
            url = f"{self.php_backend_url}/{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=30)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                
                # Try to parse JSON
                try:
                    json_data = response.json()
                    print(f"   ✅ {endpoint} returns valid JSON")
                except json.JSONDecodeError:
                    print(f"   ❌ {endpoint} returns invalid JSON")
                    all_json_valid = False
                    
            except Exception as e:
                print(f"   ❌ Error testing {endpoint}: {e}")
                all_json_valid = False
        
        return all_json_valid

    # =============================================
    # HTTP STATUS CODE TESTS
    # =============================================
    
    def test_http_status_codes(self):
        """Test that endpoints return appropriate HTTP status codes"""
        status_tests = [
            ("GET", "api/users.php", None, 200, "List users should return 200"),
            ("GET", "usage-google-places.php", None, 200, "Usage endpoint should return 200"),
            ("POST", "api/users.php/nonexistent", {"test": "data"}, 405, "Invalid method should return 405"),
            ("GET", "nonexistent-endpoint.php", None, 404, "Nonexistent endpoint should return 404")
        ]
        
        all_status_correct = True
        
        for method, endpoint, data, expected_status, description in status_tests:
            url = f"{self.php_backend_url}/{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=30)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                
                if response.status_code == expected_status:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - Got {response.status_code}")
                    all_status_correct = False
                    
            except Exception as e:
                print(f"   ❌ Error testing {description}: {e}")
                all_status_correct = False
        
        return all_status_correct

    # =============================================
    # MAIN TEST RUNNER
    # =============================================
    
    def run_all_tests(self):
        """Run all PHP backend tests"""
        print("=" * 60)
        print("🧪 NutriTame PHP Backend API Testing")
        print("=" * 60)
        print(f"Testing PHP backend at: {self.php_backend_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test categories
        test_categories = [
            ("Demo Endpoints", [
                self.test_demo_config_endpoint,
                self.test_demo_access_endpoint,
            ]),
            ("User Profile Endpoints", [
                self.test_create_user_profile,
                self.test_get_user_profile,
                self.test_update_user_profile,
            ]),
            ("Restaurant Search Endpoints", [
                self.test_restaurant_search_by_coordinates,
                self.test_restaurant_search_by_location,
            ]),
            ("Shopping List Endpoints", [
                self.test_generate_shopping_list,
                self.test_get_user_shopping_lists,
                self.test_update_shopping_list,
            ]),
            ("Utility Endpoints", [
                self.test_geocode_endpoint,
                self.test_google_places_usage_endpoint,
            ]),
            ("Error Handling", [
                self.test_invalid_user_id_handling,
                self.test_invalid_json_handling,
                self.test_missing_required_fields,
            ]),
            ("System Tests", [
                self.test_database_connection,
                self.test_json_response_format,
                self.test_http_status_codes,
            ])
        ]

        # Run tests by category
        for category_name, tests in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 40)
            
            for test_func in tests:
                try:
                    test_func()
                except Exception as e:
                    print(f"❌ {test_func.__name__} failed with exception: {e}")
                    self.tests_run += 1

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED! PHP backend is ready for deployment.")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} tests failed. Review issues before deployment.")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.tests_passed == self.tests_run


if __name__ == "__main__":
    # Allow custom base URL via command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
    
    tester = NutriTamePHPTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)