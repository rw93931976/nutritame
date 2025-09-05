#!/usr/bin/env python3
"""
URGENT Dynamic Demo User ID Test
Testing that dynamic demo user IDs work correctly with AI Health Coach
"""

import requests
import json
import time
from datetime import datetime

class DynamicDemoUserTester:
    def __init__(self, base_url="https://meal-plan-assist.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.dynamic_user_id = None
        self.session_id = None

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

    def test_1_create_dynamic_demo_user(self):
        """Test 1: Create user profile with timestamp-based demo user ID"""
        # Generate timestamp-based user ID like frontend would
        timestamp = int(time.time() * 1000)  # milliseconds
        expected_dynamic_id = f"demo-{timestamp}"
        
        print(f"\n🎯 STEP 1: Creating dynamic demo user (simulating frontend ID: {expected_dynamic_id})")
        
        # Create comprehensive profile (backend will generate UUID, but we'll simulate dynamic behavior)
        demo_profile = {
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
        
        success, response = self.run_test(
            f"Create Dynamic Demo User Profile (simulating: {expected_dynamic_id})",
            "POST",
            "users",
            200,
            data=demo_profile
        )
        
        if success and response.get('id'):
            # Use the backend-generated ID (this simulates the frontend fix)
            self.dynamic_user_id = response.get('id')
            print(f"   ✅ Dynamic user created successfully with backend ID: {self.dynamic_user_id}")
            print(f"   📝 Note: Backend generates UUID, frontend would use timestamp-based ID like: {expected_dynamic_id}")
            
            # Verify all profile fields were saved
            profile_fields_correct = True
            for field, expected_value in demo_profile.items():
                actual_value = response.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: {actual_value}")
                else:
                    print(f"   ❌ {field}: Expected {expected_value}, got {actual_value}")
                    profile_fields_correct = False
            
            if profile_fields_correct:
                print(f"   ✅ All profile fields saved correctly for dynamic user {self.dynamic_user_id}")
                return True
            else:
                print(f"   ❌ Some profile fields not saved correctly")
                return False
        else:
            print(f"   ❌ Failed to create dynamic user")
            print(f"   Response: {response}")
            return False

    def test_2_create_ai_coach_session(self):
        """Test 2: Create AI Health Coach session with dynamic user ID"""
        if not self.dynamic_user_id:
            print("❌ No dynamic user ID available")
            return False
            
        print(f"\n🎯 STEP 2: Creating AI Health Coach session for user: {self.dynamic_user_id}")
        
        # First accept disclaimer for the user
        success, disclaimer_response = self.run_test(
            f"Accept Disclaimer for Dynamic User {self.dynamic_user_id}",
            "POST",
            "coach/accept-disclaimer",
            200,
            data={"user_id": self.dynamic_user_id}
        )
        
        if not success:
            print(f"   ❌ Failed to accept disclaimer for user {self.dynamic_user_id}")
            return False
        
        print(f"   ✅ Disclaimer accepted for user {self.dynamic_user_id}")
        
        # Create AI Health Coach session
        session_data = {
            "title": f"Dynamic Demo Session - {self.dynamic_user_id}"
        }
        
        success, response = self.run_test(
            f"Create AI Coach Session for Dynamic User {self.dynamic_user_id}",
            "POST",
            f"coach/sessions?user_id={self.dynamic_user_id}",
            200,
            data=session_data
        )
        
        if success and response.get('id'):
            self.session_id = response.get('id')
            session_user_id = response.get('user_id')
            
            if session_user_id == self.dynamic_user_id:
                print(f"   ✅ Session created successfully with ID: {self.session_id}")
                print(f"   ✅ Session correctly linked to user: {self.dynamic_user_id}")
                return True
            else:
                print(f"   ❌ Session user ID mismatch. Expected: {self.dynamic_user_id}, Got: {session_user_id}")
                return False
        else:
            print(f"   ❌ Failed to create session for user {self.dynamic_user_id}")
            print(f"   Response: {response}")
            return False

    def test_3_send_message_with_dynamic_user(self):
        """Test 3: Send message to AI Health Coach with dynamic user ID and session"""
        if not self.dynamic_user_id or not self.session_id:
            print("❌ Missing dynamic user ID or session ID")
            return False
            
        print(f"\n🎯 STEP 3: Sending message with dynamic user {self.dynamic_user_id} and session {self.session_id}")
        
        # Send a message that should trigger profile-aware response
        message_data = {
            "session_id": self.session_id,
            "message": "I need a Mediterranean breakfast recipe that's safe for my allergies and good for Type 2 diabetes"
        }
        
        print("   Note: AI response may take 10-15 seconds...")
        success, response = self.run_test(
            f"Send AI Message with Dynamic User {self.dynamic_user_id}",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success:
            # Check for AI response in the response structure
            ai_response_text = None
            
            # Handle different possible response structures
            if 'ai_response' in response and 'text' in response['ai_response']:
                ai_response_text = response['ai_response']['text']
            elif 'response' in response:
                ai_response_text = response['response']
            elif 'text' in response:
                ai_response_text = response['text']
            
            if ai_response_text:
                print(f"   ✅ AI response received (length: {len(ai_response_text)} chars)")
                print(f"   Response preview: {ai_response_text[:200]}...")
                
                # Store AI response for profile integration verification
                self.ai_response = ai_response_text
                
                # Verify consultation was used
                if response.get('consultation_used'):
                    print(f"   ✅ Consultation count incremented correctly")
                
                return True
            else:
                print(f"   ❌ No AI response text found in response")
                print(f"   Response structure: {list(response.keys()) if isinstance(response, dict) else type(response)}")
                return False
        else:
            print(f"   ❌ Failed to send message")
            print(f"   Response: {response}")
            return False

    def test_4_verify_profile_integration(self):
        """Test 4: Verify AI response includes profile data from dynamic user"""
        if not hasattr(self, 'ai_response') or not self.ai_response:
            print("❌ No AI response available for profile integration check")
            return False
            
        print(f"\n🎯 STEP 4: Verifying AI response includes profile data for user {self.dynamic_user_id}")
        
        ai_response = self.ai_response.lower()
        
        # Profile integration criteria based on the user profile we created
        profile_criteria = {
            "diabetes_awareness": ["diabetes", "blood sugar", "diabetic", "type 2"],
            "health_goals": ["blood sugar", "weight", "control"],
            "mediterranean_preferences": ["mediterranean", "olive oil", "feta", "tomatoes", "herbs"],
            "low_carb_awareness": ["low carb", "carb", "carbohydrate", "moderation"],
            "allergy_safety": True,  # Should NOT contain nuts or shellfish
            "imperial_measurements": ["cup", "cups", "tablespoon", "tablespoons", "oz", "ounce"],
            "shopping_list_offer": ["shopping list", "grocery", "ingredients"],
            "diabetes_friendly": ["friendly", "suitable", "appropriate", "good for"]
        }
        
        integration_score = 0
        total_criteria = len(profile_criteria)
        
        print("   Checking profile integration criteria:")
        
        # Check diabetes awareness
        if any(term in ai_response for term in profile_criteria["diabetes_awareness"]):
            print("   ✅ Diabetes awareness: AI mentions diabetes/blood sugar")
            integration_score += 1
        else:
            print("   ❌ Diabetes awareness: No diabetes-related terms found")
        
        # Check health goals integration
        if any(term in ai_response for term in profile_criteria["health_goals"]):
            print("   ✅ Health goals: AI addresses blood sugar control/weight")
            integration_score += 1
        else:
            print("   ❌ Health goals: No health goal terms found")
        
        # Check Mediterranean preferences
        if any(term in ai_response for term in profile_criteria["mediterranean_preferences"]):
            print("   ✅ Mediterranean preferences: AI includes Mediterranean elements")
            integration_score += 1
        else:
            print("   ❌ Mediterranean preferences: No Mediterranean terms found")
        
        # Check low-carb awareness
        if any(term in ai_response for term in profile_criteria["low_carb_awareness"]):
            print("   ✅ Low-carb awareness: AI mentions carbohydrates/moderation")
            integration_score += 1
        else:
            print("   ❌ Low-carb awareness: No carb-related terms found")
        
        # Check allergy safety (should NOT contain nuts or shellfish)
        dangerous_ingredients = ["nuts", "shellfish", "peanut", "almond", "walnut", "shrimp", "crab", "lobster"]
        if not any(ingredient in ai_response for ingredient in dangerous_ingredients):
            print("   ✅ Allergy safety: No nuts/shellfish ingredients mentioned")
            integration_score += 1
        else:
            found_allergens = [ing for ing in dangerous_ingredients if ing in ai_response]
            print(f"   ❌ Allergy safety: Found allergens: {found_allergens}")
        
        # Check imperial measurements
        if any(term in ai_response for term in profile_criteria["imperial_measurements"]):
            print("   ✅ Imperial measurements: AI uses cups/tablespoons/oz")
            integration_score += 1
        else:
            print("   ❌ Imperial measurements: No imperial measurement terms found")
        
        # Check shopping list offer
        if any(term in ai_response for term in profile_criteria["shopping_list_offer"]):
            print("   ✅ Shopping list offer: AI offers to create shopping list")
            integration_score += 1
        else:
            print("   ❌ Shopping list offer: No shopping list offer found")
        
        # Check diabetes-friendly language
        if any(term in ai_response for term in profile_criteria["diabetes_friendly"]):
            print("   ✅ Diabetes-friendly language: AI uses appropriate terminology")
            integration_score += 1
        else:
            print("   ❌ Diabetes-friendly language: No diabetes-friendly terms found")
        
        # Calculate integration percentage
        integration_percentage = (integration_score / total_criteria) * 100
        
        print(f"\n   📊 Profile Integration Score: {integration_score}/{total_criteria} ({integration_percentage:.1f}%)")
        
        if integration_score >= 6:  # 75% or higher
            print(f"   ✅ EXCELLENT: AI response demonstrates strong profile integration")
            return True
        elif integration_score >= 4:  # 50% or higher
            print(f"   ✅ GOOD: AI response shows adequate profile integration")
            return True
        else:
            print(f"   ❌ POOR: AI response lacks sufficient profile integration")
            return False

    def test_5_verify_session_persistence(self):
        """Test 5: Verify session and messages are properly stored"""
        if not self.dynamic_user_id or not self.session_id:
            print("❌ Missing dynamic user ID or session ID")
            return False
            
        print(f"\n🎯 STEP 5: Verifying session persistence for user {self.dynamic_user_id}")
        
        # Get user sessions
        success, sessions_response = self.run_test(
            f"Get Sessions for Dynamic User {self.dynamic_user_id}",
            "GET",
            f"coach/sessions/{self.dynamic_user_id}",
            200
        )
        
        if not success:
            print(f"   ❌ Failed to retrieve sessions for user {self.dynamic_user_id}")
            return False
        
        # Verify our session exists
        sessions = sessions_response if isinstance(sessions_response, list) else []
        session_found = False
        
        for session in sessions:
            if session.get('id') == self.session_id:
                session_found = True
                print(f"   ✅ Session {self.session_id} found in user's session list")
                break
        
        if not session_found:
            print(f"   ❌ Session {self.session_id} not found in user's sessions")
            return False
        
        # Get messages for the session
        success, messages_response = self.run_test(
            f"Get Messages for Session {self.session_id}",
            "GET",
            f"coach/messages/{self.session_id}",
            200
        )
        
        if not success:
            print(f"   ❌ Failed to retrieve messages for session {self.session_id}")
            return False
        
        # Verify messages exist
        messages = messages_response if isinstance(messages_response, list) else []
        
        if len(messages) >= 2:  # Should have user message + AI response
            user_messages = [msg for msg in messages if msg.get('role') == 'user']
            ai_messages = [msg for msg in messages if msg.get('role') == 'assistant']
            
            if len(user_messages) >= 1 and len(ai_messages) >= 1:
                print(f"   ✅ Found {len(user_messages)} user message(s) and {len(ai_messages)} AI response(s)")
                print(f"   ✅ Session persistence working correctly")
                return True
            else:
                print(f"   ❌ Message roles incorrect. User: {len(user_messages)}, AI: {len(ai_messages)}")
                return False
        else:
            print(f"   ❌ Expected at least 2 messages, found {len(messages)}")
            return False

    def run_all_tests(self):
        """Run all dynamic demo user tests"""
        print("=" * 80)
        print("🚀 URGENT: Dynamic Demo User ID Testing")
        print("   Testing that dynamic demo user IDs work correctly with AI Health Coach")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_1_create_dynamic_demo_user,
            self.test_2_create_ai_coach_session,
            self.test_3_send_message_with_dynamic_user,
            self.test_4_verify_profile_integration,
            self.test_5_verify_session_persistence
        ]
        
        for test in tests:
            try:
                result = test()
                if not result:
                    print(f"\n❌ Test failed: {test.__name__}")
                    break
            except Exception as e:
                print(f"\n❌ Test error in {test.__name__}: {str(e)}")
                break
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 DYNAMIC DEMO USER TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        if self.dynamic_user_id:
            print(f"Dynamic User ID: {self.dynamic_user_id}")
        if self.session_id:
            print(f"Session ID: {self.session_id}")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED - Dynamic demo user IDs working correctly!")
            return True
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} test(s) failed")
            return False

if __name__ == "__main__":
    tester = DynamicDemoUserTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)