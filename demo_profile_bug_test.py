import requests
import sys
import json
from datetime import datetime

class DemoProfileBugTester:
    def __init__(self, base_url="https://ai-coach-bridge.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_user_id = None
        self.demo_access_token = None
        self.database_user_id = None

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

    def test_1_create_demo_user(self):
        """Test 1: Create a demo user via POST /api/demo/access"""
        print("\n" + "="*80)
        print("TEST 1: CREATE DEMO USER VIA /api/demo/access")
        print("="*80)
        
        demo_data = {
            "email": "profile.bug.test@example.com"
        }
        
        success, response = self.run_test(
            "Create Demo User",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if success:
            # Store demo user information
            user = response.get('user', {})
            self.demo_user_id = user.get('id')
            self.demo_access_token = response.get('access_token')
            
            print(f"\n📋 DEMO USER CREATED:")
            print(f"   Demo User ID: {self.demo_user_id}")
            print(f"   Email: {user.get('email')}")
            print(f"   Subscription Tier: {user.get('subscription_tier')}")
            print(f"   Subscription Status: {user.get('subscription_status')}")
            print(f"   Access Token: {self.demo_access_token[:20]}...")
            
            # Verify demo user has ID but is NOT in users collection yet
            if self.demo_user_id:
                print(f"   ✅ Demo user has ID: {self.demo_user_id}")
                return True
            else:
                print("   ❌ Demo user missing ID")
                return False
        
        return False

    def test_2_verify_demo_user_not_in_users_collection(self):
        """Test 2: Verify the demo user exists and has an ID but is not in the users collection"""
        print("\n" + "="*80)
        print("TEST 2: VERIFY DEMO USER NOT IN USERS COLLECTION")
        print("="*80)
        
        if not self.demo_user_id:
            print("❌ No demo user ID available for testing")
            return False
        
        # Try to get the demo user from users collection - should return 404
        success, response = self.run_test(
            "Get Demo User from Users Collection (Should Fail)",
            "GET",
            f"users/{self.demo_user_id}",
            404  # Should return 404 because demo user is not in users collection
        )
        
        if success:
            print(f"   ✅ CORRECT: Demo user {self.demo_user_id} is NOT in users collection (404 returned)")
            print("   ✅ This confirms the bug scenario - demo user exists for JWT but not in database")
            return True
        else:
            print(f"   ❌ UNEXPECTED: Demo user found in users collection - this may indicate the bug is already fixed or test setup issue")
            return False

    def test_3_create_profile_for_demo_user(self):
        """Test 3: Attempt to create a profile for that demo user via POST /api/users with profile data"""
        print("\n" + "="*80)
        print("TEST 3: CREATE PROFILE FOR DEMO USER VIA POST /api/users")
        print("="*80)
        
        if not self.demo_user_id:
            print("❌ No demo user ID available for testing")
            return False
        
        # Create comprehensive profile data for the demo user
        profile_data = {
            "diabetes_type": "type2",
            "age": 42,
            "gender": "female",
            "activity_level": "moderate",
            "health_goals": ["blood_sugar_control", "weight_loss"],
            "food_preferences": ["mediterranean", "low_carb"],
            "cultural_background": "Mediterranean",
            "allergies": ["nuts", "shellfish"],
            "dislikes": ["liver", "brussels_sprouts"],
            "cooking_skill": "intermediate",
            "phone_number": "+15551234567",
            "plan": "standard"
        }
        
        print(f"\n📋 CREATING PROFILE FOR DEMO USER:")
        print(f"   Demo User ID: {self.demo_user_id}")
        print(f"   Profile Data: {json.dumps(profile_data, indent=2)}")
        
        success, response = self.run_test(
            "Create Profile for Demo User",
            "POST",
            "users",
            200,
            data=profile_data
        )
        
        if success:
            # Store the new database user ID
            self.database_user_id = response.get('id')
            
            print(f"\n📋 PROFILE CREATION RESULT:")
            print(f"   Original Demo User ID: {self.demo_user_id}")
            print(f"   New Database User ID: {self.database_user_id}")
            print(f"   Diabetes Type: {response.get('diabetes_type')}")
            print(f"   Age: {response.get('age')}")
            print(f"   Health Goals: {response.get('health_goals')}")
            print(f"   Food Preferences: {response.get('food_preferences')}")
            print(f"   Allergies: {response.get('allergies')}")
            
            # Verify the profile creation succeeded and returned a new database user ID
            if self.database_user_id and self.database_user_id != self.demo_user_id:
                print(f"   ✅ SUCCESS: Profile creation returned new database user ID")
                print(f"   ✅ Demo user ID ({self.demo_user_id}) != Database user ID ({self.database_user_id})")
                
                # Verify all profile fields were saved correctly
                all_fields_correct = True
                for field, expected_value in profile_data.items():
                    actual_value = response.get(field)
                    if actual_value == expected_value:
                        print(f"   ✅ {field}: Saved correctly")
                    else:
                        print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                        all_fields_correct = False
                
                return all_fields_correct
            else:
                print(f"   ❌ FAILED: Profile creation did not return valid new database user ID")
                return False
        else:
            print(f"   ❌ FAILED: Profile creation failed with error")
            return False

    def test_4_verify_profile_retrieval_with_database_id(self):
        """Test 4: Verify the profile creation succeeds and returns a new database user ID"""
        print("\n" + "="*80)
        print("TEST 4: VERIFY PROFILE RETRIEVAL WITH DATABASE USER ID")
        print("="*80)
        
        if not self.database_user_id:
            print("❌ No database user ID available for testing")
            return False
        
        success, response = self.run_test(
            "Get Profile with Database User ID",
            "GET",
            f"users/{self.database_user_id}",
            200
        )
        
        if success:
            print(f"\n📋 PROFILE RETRIEVAL RESULT:")
            print(f"   Database User ID: {self.database_user_id}")
            print(f"   Retrieved User ID: {response.get('id')}")
            print(f"   Diabetes Type: {response.get('diabetes_type')}")
            print(f"   Age: {response.get('age')}")
            print(f"   Health Goals: {response.get('health_goals')}")
            print(f"   Food Preferences: {response.get('food_preferences')}")
            print(f"   Allergies: {response.get('allergies')}")
            
            # Verify the retrieved profile matches what we created
            if response.get('id') == self.database_user_id:
                print(f"   ✅ SUCCESS: Profile retrieved with correct database user ID")
                
                # Verify key profile fields
                expected_fields = {
                    'diabetes_type': 'type2',
                    'age': 42,
                    'gender': 'female',
                    'activity_level': 'moderate'
                }
                
                all_fields_correct = True
                for field, expected_value in expected_fields.items():
                    actual_value = response.get(field)
                    if actual_value == expected_value:
                        print(f"   ✅ {field}: {actual_value}")
                    else:
                        print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                        all_fields_correct = False
                
                return all_fields_correct
            else:
                print(f"   ❌ FAILED: Retrieved user ID doesn't match database user ID")
                return False
        else:
            print(f"   ❌ FAILED: Could not retrieve profile with database user ID")
            return False

    def test_5_verify_profile_update_with_database_id(self):
        """Test 5: Test that the backend profile endpoints (GET, PUT) work correctly with the new database user ID"""
        print("\n" + "="*80)
        print("TEST 5: VERIFY PROFILE UPDATE WITH DATABASE USER ID")
        print("="*80)
        
        if not self.database_user_id:
            print("❌ No database user ID available for testing")
            return False
        
        # Update profile data
        update_data = {
            "age": 43,
            "health_goals": ["blood_sugar_control", "weight_loss", "energy_boost"],
            "food_preferences": ["mediterranean", "low_carb", "organic"],
            "allergies": ["nuts", "shellfish", "dairy"],
            "cooking_skill": "advanced"
        }
        
        print(f"\n📋 UPDATING PROFILE:")
        print(f"   Database User ID: {self.database_user_id}")
        print(f"   Update Data: {json.dumps(update_data, indent=2)}")
        
        success, response = self.run_test(
            "Update Profile with Database User ID",
            "PUT",
            f"users/{self.database_user_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"\n📋 PROFILE UPDATE RESULT:")
            print(f"   Updated User ID: {response.get('id')}")
            print(f"   Age: {response.get('age')}")
            print(f"   Health Goals: {response.get('health_goals')}")
            print(f"   Food Preferences: {response.get('food_preferences')}")
            print(f"   Allergies: {response.get('allergies')}")
            print(f"   Cooking Skill: {response.get('cooking_skill')}")
            
            # Verify all updated fields were saved correctly
            all_fields_correct = True
            for field, expected_value in update_data.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: Updated correctly to {actual_value}")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    all_fields_correct = False
            
            # Verify unchanged fields are preserved
            if response.get('diabetes_type') == 'type2':
                print("   ✅ Unchanged field preserved (diabetes_type still type2)")
            else:
                print(f"   ❌ Unchanged field modified: diabetes_type = {response.get('diabetes_type')}")
                all_fields_correct = False
            
            if all_fields_correct:
                print(f"   ✅ SUCCESS: Profile update works correctly with database user ID")
                return True
            else:
                print(f"   ❌ FAILED: Some profile fields not updated correctly")
                return False
        else:
            print(f"   ❌ FAILED: Profile update failed")
            return False

    def test_6_verify_no_user_not_found_errors(self):
        """Test 6: Confirm no 404 'User not found' errors during profile operations"""
        print("\n" + "="*80)
        print("TEST 6: VERIFY NO 'USER NOT FOUND' ERRORS")
        print("="*80)
        
        if not self.database_user_id:
            print("❌ No database user ID available for testing")
            return False
        
        print(f"\n📋 TESTING MULTIPLE PROFILE OPERATIONS:")
        print(f"   Database User ID: {self.database_user_id}")
        
        # Test 1: GET profile (should work)
        success1, response1 = self.run_test(
            "GET Profile - No User Not Found Error",
            "GET",
            f"users/{self.database_user_id}",
            200
        )
        
        if success1:
            print(f"   ✅ GET /api/users/{self.database_user_id} - SUCCESS (no 404 error)")
        else:
            print(f"   ❌ GET /api/users/{self.database_user_id} - FAILED (unexpected error)")
            return False
        
        # Test 2: PUT profile update (should work)
        update_data = {"age": 44}
        success2, response2 = self.run_test(
            "PUT Profile - No User Not Found Error",
            "PUT",
            f"users/{self.database_user_id}",
            200,
            data=update_data
        )
        
        if success2:
            print(f"   ✅ PUT /api/users/{self.database_user_id} - SUCCESS (no 404 error)")
        else:
            print(f"   ❌ PUT /api/users/{self.database_user_id} - FAILED (unexpected error)")
            return False
        
        # Test 3: Verify the original demo user ID still returns 404 (as expected)
        if self.demo_user_id and self.demo_user_id != self.database_user_id:
            success3, response3 = self.run_test(
                "GET Original Demo User ID - Should Still Return 404",
                "GET",
                f"users/{self.demo_user_id}",
                404
            )
            
            if success3:
                print(f"   ✅ GET /api/users/{self.demo_user_id} - CORRECTLY returns 404 (demo user not in database)")
            else:
                print(f"   ❌ GET /api/users/{self.demo_user_id} - Should return 404 but didn't")
                return False
        
        print(f"\n✅ SUCCESS: All profile operations work correctly with database user ID")
        print(f"✅ SUCCESS: No 'User not found' errors encountered during profile operations")
        print(f"✅ SUCCESS: Demo user profile bug fix is working correctly")
        
        return True

    def test_7_edge_case_demo_user_without_email(self):
        """Test 7: Edge case - Demo user created without email should also work"""
        print("\n" + "="*80)
        print("TEST 7: EDGE CASE - DEMO USER WITHOUT EMAIL")
        print("="*80)
        
        # Create demo user without email
        demo_data = {}  # No email provided
        
        success, response = self.run_test(
            "Create Demo User Without Email",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if success:
            user = response.get('user', {})
            demo_user_id_2 = user.get('id')
            
            print(f"\n📋 DEMO USER WITHOUT EMAIL CREATED:")
            print(f"   Demo User ID: {demo_user_id_2}")
            print(f"   Generated Email: {user.get('email')}")
            
            # Create profile for this demo user
            profile_data = {
                "diabetes_type": "type1",
                "age": 35,
                "gender": "male",
                "activity_level": "high"
            }
            
            success2, response2 = self.run_test(
                "Create Profile for Demo User Without Email",
                "POST",
                "users",
                200,
                data=profile_data
            )
            
            if success2:
                database_user_id_2 = response2.get('id')
                print(f"   ✅ SUCCESS: Profile created for demo user without email")
                print(f"   Original Demo ID: {demo_user_id_2}")
                print(f"   New Database ID: {database_user_id_2}")
                
                # Verify profile retrieval works
                success3, response3 = self.run_test(
                    "Get Profile for Demo User Without Email",
                    "GET",
                    f"users/{database_user_id_2}",
                    200
                )
                
                if success3:
                    print(f"   ✅ SUCCESS: Profile retrieval works for demo user without email")
                    return True
                else:
                    print(f"   ❌ FAILED: Profile retrieval failed for demo user without email")
                    return False
            else:
                print(f"   ❌ FAILED: Profile creation failed for demo user without email")
                return False
        else:
            print(f"   ❌ FAILED: Could not create demo user without email")
            return False

    def run_all_tests(self):
        """Run all demo profile bug fix tests"""
        print("\n" + "="*100)
        print("DEMO USER PROFILE SUBMISSION BUG FIX TESTING")
        print("="*100)
        print("Testing the fix for demo users created via /api/demo/access")
        print("Issue: Demo users trying to update profile with PUT /api/users/{id}")
        print("       but that ID doesn't exist in database, causing 'User not found' errors")
        print("Fix: Route demo users to POST /api/users (create) instead")
        print("="*100)
        
        tests = [
            ("Create Demo User", self.test_1_create_demo_user),
            ("Verify Demo User Not in Users Collection", self.test_2_verify_demo_user_not_in_users_collection),
            ("Create Profile for Demo User", self.test_3_create_profile_for_demo_user),
            ("Verify Profile Retrieval", self.test_4_verify_profile_retrieval_with_database_id),
            ("Verify Profile Update", self.test_5_verify_profile_update_with_database_id),
            ("Verify No User Not Found Errors", self.test_6_verify_no_user_not_found_errors),
            ("Edge Case - Demo User Without Email", self.test_7_edge_case_demo_user_without_email)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if not result:
                    print(f"\n❌ TEST FAILED: {test_name}")
                    break
                else:
                    print(f"\n✅ TEST PASSED: {test_name}")
            except Exception as e:
                print(f"\n💥 TEST ERROR: {test_name} - {str(e)}")
                break
        
        # Print final results
        print("\n" + "="*100)
        print("FINAL TEST RESULTS")
        print("="*100)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Demo user profile submission bug fix is working correctly")
            print("✅ Demo users can successfully create profiles via POST /api/users")
            print("✅ Profile operations (GET, PUT) work with new database user IDs")
            print("✅ No 'User not found' errors encountered")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} TEST(S) FAILED")
            print("❌ Demo user profile submission bug fix may not be working correctly")
        
        print("="*100)

if __name__ == "__main__":
    tester = DemoProfileBugTester()
    tester.run_all_tests()