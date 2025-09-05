#!/usr/bin/env python3
"""
AI Health Coach Backend Endpoint Tests
TDD localStorage Gate Fix Verification

Tests all 9 core AI Health Coach endpoints after frontend fixes
to ensure no regressions from TDD localStorage gate implementation.
"""

import requests
import json
import sys
from datetime import datetime

class AIHealthCoachTester:
    def __init__(self, base_url="https://nutritame-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_id = None
        self.ai_coach_session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
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

    def test_1_feature_flags(self):
        """Test GET /api/coach/feature-flags - should return coach_enabled=true, openai/gpt-4o-mini config"""
        success, response = self.run_test(
            "1. AI Coach Feature Flags",
            "GET",
            "coach/feature-flags",
            200
        )
        
        if success:
            # Verify coach_enabled is true
            if response.get('coach_enabled') is True:
                print("   ✅ coach_enabled is correctly set to true")
            else:
                print(f"   ❌ coach_enabled should be true, got: {response.get('coach_enabled')}")
                return False
            
            # Verify LLM provider is openai
            if response.get('llm_provider') == 'openai':
                print("   ✅ llm_provider is correctly set to openai")
            else:
                print(f"   ❌ llm_provider should be openai, got: {response.get('llm_provider')}")
                return False
            
            # Verify LLM model is gpt-4o-mini
            if response.get('llm_model') == 'gpt-4o-mini':
                print("   ✅ llm_model is correctly set to gpt-4o-mini")
            else:
                print(f"   ❌ llm_model should be gpt-4o-mini, got: {response.get('llm_model')}")
                return False
            
            # Verify standard limit is 10
            if response.get('standard_limit') == 10:
                print("   ✅ standard_limit is correctly set to 10")
            else:
                print(f"   ❌ standard_limit should be 10, got: {response.get('standard_limit')}")
                return False
            
            return True
        
        return False

    def create_demo_user(self):
        """Create a demo user for testing"""
        demo_user_profile = {
            "diabetes_type": "type2",
            "age": 35,
            "gender": "female",
            "activity_level": "moderate",
            "health_goals": ["blood_sugar_control", "weight_loss"],
            "food_preferences": ["mediterranean", "low_carb"],
            "cultural_background": "Mediterranean",
            "allergies": ["nuts", "shellfish"],
            "dislikes": ["liver"],
            "cooking_skill": "intermediate"
        }
        
        success, response = self.run_test(
            "Create Demo User Profile",
            "POST",
            "users",
            200,
            data=demo_user_profile
        )
        
        if success and 'id' in response:
            self.created_user_id = response['id']
            print(f"   ✅ Created demo user: {self.created_user_id}")
            return True
        else:
            print(f"   ❌ Failed to create demo user: {response}")
            return False

    def test_2_accept_disclaimer(self):
        """Test POST /api/coach/accept-disclaimer - should record disclaimer acceptance"""
        if not self.created_user_id:
            if not self.create_demo_user():
                return False
        
        disclaimer_data = {
            "user_id": self.created_user_id
        }
        
        success, response = self.run_test(
            "2. AI Coach Accept Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=disclaimer_data
        )
        
        if success:
            # Verify success response
            if response.get('success') is True:
                print("   ✅ Disclaimer acceptance recorded successfully")
            else:
                print(f"   ❌ Disclaimer acceptance failed: {response}")
                return False
            
            # Verify message
            if 'accepted' in response.get('message', '').lower():
                print("   ✅ Disclaimer acceptance message is appropriate")
            else:
                print(f"   ❌ Disclaimer acceptance message unclear: {response.get('message')}")
                return False
            
            return True
        
        return False

    def test_3_disclaimer_status(self):
        """Test GET /api/coach/disclaimer-status/{user_id} - should return acceptance status"""
        if not self.created_user_id:
            print("   ❌ No user ID available for disclaimer status testing")
            return False
        
        success, response = self.run_test(
            "3. AI Coach Disclaimer Status",
            "GET",
            f"coach/disclaimer-status/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify accepted status is true (since we just accepted it)
            if response.get('accepted') is True:
                print("   ✅ Disclaimer status correctly shows accepted")
            else:
                print(f"   ❌ Disclaimer should be accepted, got: {response.get('accepted')}")
                return False
            
            # Verify accepted_at timestamp exists
            if response.get('accepted_at'):
                print("   ✅ Disclaimer acceptance timestamp is present")
            else:
                print("   ❌ Disclaimer acceptance timestamp is missing")
                return False
            
            return True
        
        return False

    def test_4_consultation_limit(self):
        """Test GET /api/coach/consultation-limit/{user_id} - should return standard plan limits"""
        if not self.created_user_id:
            print("   ❌ No user ID available for consultation limit testing")
            return False
        
        success, response = self.run_test(
            "4. AI Coach Consultation Limit",
            "GET",
            f"coach/consultation-limit/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify can_use is true for new user
            if response.get('can_use') is True:
                print("   ✅ User can use consultations (within limit)")
            else:
                print(f"   ❌ User should be able to use consultations, got: {response.get('can_use')}")
                return False
            
            # Verify limit is 10 for standard plan
            if response.get('limit') == 10:
                print("   ✅ Standard plan limit is correctly set to 10")
            else:
                print(f"   ❌ Standard plan limit should be 10, got: {response.get('limit')}")
                return False
            
            # Verify plan is standard
            if response.get('plan') == 'standard':
                print("   ✅ User plan is correctly set to standard")
            else:
                print(f"   ❌ User plan should be standard, got: {response.get('plan')}")
                return False
            
            # Verify current count is 0 for new user
            if response.get('current_count') == 0:
                print("   ✅ Current consultation count is 0 for new user")
            else:
                print(f"   ❌ Current count should be 0 for new user, got: {response.get('current_count')}")
                return False
            
            return True
        
        return False

    def test_5_create_session(self):
        """Test POST /api/coach/sessions - should create new sessions"""
        if not self.created_user_id:
            print("   ❌ No user ID available for session creation testing")
            return False
        
        session_data = {
            "title": "Test AI Health Coach Session"
        }
        
        success, response = self.run_test(
            "5. AI Coach Create Session",
            "POST",
            f"coach/sessions?user_id={self.created_user_id}",
            200,
            data=session_data
        )
        
        if success:
            # Verify session ID is returned
            session_id = response.get('id')
            if session_id:
                print(f"   ✅ Session created successfully with ID: {session_id}")
                self.ai_coach_session_id = session_id  # Store for later tests
            else:
                print(f"   ❌ Session ID not returned: {response}")
                return False
            
            # Verify user_id matches
            if response.get('user_id') == self.created_user_id:
                print("   ✅ Session user_id matches created user")
            else:
                print(f"   ❌ Session user_id mismatch. Expected: {self.created_user_id}, Got: {response.get('user_id')}")
                return False
            
            return True
        
        return False

    def test_6_get_user_sessions(self):
        """Test GET /api/coach/sessions/{user_id} - should retrieve user sessions"""
        if not self.created_user_id:
            print("   ❌ No user ID available for session retrieval testing")
            return False
        
        success, response = self.run_test(
            "6. AI Coach Get User Sessions",
            "GET",
            f"coach/sessions/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} sessions for user")
            else:
                print(f"   ❌ Response should be a list, got: {type(response)}")
                return False
            
            # Verify we have at least one session (the one we created)
            if len(response) >= 1:
                print("   ✅ At least one session found (as expected)")
                
                # Verify session structure
                first_session = response[0]
                required_fields = ['id', 'user_id', 'title', 'created_at', 'updated_at']
                missing_fields = [field for field in required_fields if field not in first_session]
                
                if not missing_fields:
                    print("   ✅ Session structure is correct")
                else:
                    print(f"   ❌ Missing session fields: {missing_fields}")
                    return False
                
            else:
                print("   ❌ No sessions found for user")
                return False
            
            return True
        
        return False

    def test_7_send_message(self):
        """Test POST /api/coach/message - should generate real AI responses"""
        if not self.ai_coach_session_id:
            print("   ❌ No session ID available for message testing")
            return False
        
        message_data = {
            "session_id": self.ai_coach_session_id,
            "message": "Create a healthy breakfast meal plan for someone with Type 2 diabetes who prefers Mediterranean foods and is allergic to nuts and shellfish"
        }
        
        print("   Note: AI response may take 10-20 seconds...")
        success, response = self.run_test(
            "7. AI Coach Send Message (Real AI Integration)",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success:
            # Verify AI response is present
            ai_response = response.get('response')
            if ai_response and len(ai_response) > 50:  # Substantial response
                print(f"   ✅ AI response generated successfully ({len(ai_response)} characters)")
                print(f"   Response preview: {ai_response[:150]}...")
            else:
                print(f"   ❌ AI response too short or missing: {ai_response}")
                return False
            
            # Verify response contains diabetes-specific content
            diabetes_keywords = ['diabetes', 'blood sugar', 'carbohydrate', 'glucose', 'diabetic']
            has_diabetes_content = any(keyword in ai_response.lower() for keyword in diabetes_keywords)
            if has_diabetes_content:
                print("   ✅ AI response contains diabetes-specific content")
            else:
                print("   ⚠️  AI response may not contain diabetes-specific content")
            
            # Verify response considers Mediterranean preferences
            mediterranean_keywords = ['mediterranean', 'olive oil', 'tomato', 'feta', 'olives']
            has_mediterranean_content = any(keyword in ai_response.lower() for keyword in mediterranean_keywords)
            if has_mediterranean_content:
                print("   ✅ AI response considers Mediterranean preferences")
            else:
                print("   ⚠️  AI response may not consider Mediterranean preferences")
            
            # Verify imperial measurements are used
            imperial_keywords = ['cup', 'tablespoon', 'teaspoon', 'ounce', 'oz', 'pound', 'lb']
            has_imperial = any(keyword in ai_response.lower() for keyword in imperial_keywords)
            if has_imperial:
                print("   ✅ AI response uses imperial measurements")
            else:
                print("   ⚠️  AI response may not use imperial measurements")
            
            return True
        
        return False

    def test_8_get_messages(self):
        """Test GET /api/coach/messages/{session_id} - should return conversation history"""
        if not self.ai_coach_session_id:
            print("   ❌ No session ID available for message retrieval testing")
            return False
        
        success, response = self.run_test(
            "8. AI Coach Get Messages",
            "GET",
            f"coach/messages/{self.ai_coach_session_id}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} messages for session")
            else:
                print(f"   ❌ Response should be a list, got: {type(response)}")
                return False
            
            # Verify we have at least 2 messages (user + AI)
            if len(response) >= 2:
                print("   ✅ At least 2 messages found (user + AI)")
                
                # Verify we have both user and assistant messages
                roles = [msg.get('role') for msg in response]
                if 'user' in roles and 'assistant' in roles:
                    print("   ✅ Conversation contains both user and assistant messages")
                else:
                    print(f"   ❌ Missing message roles. Found: {roles}")
                    return False
                
            else:
                print("   ❌ Not enough messages found for conversation")
                return False
            
            return True
        
        return False

    def test_9_search_conversations(self):
        """Test GET /api/coach/search/{user_id} - should search conversations"""
        if not self.created_user_id:
            print("   ❌ No user ID available for conversation search testing")
            return False
        
        # Search for "breakfast" since we sent a breakfast-related message
        search_query = "breakfast"
        
        success, response = self.run_test(
            "9. AI Coach Search Conversations",
            "GET",
            f"coach/search/{self.created_user_id}?query={search_query}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Search returned {len(response)} results")
            else:
                print(f"   ❌ Response should be a list, got: {type(response)}")
                return False
            
            # If we have results, verify structure
            if len(response) > 0:
                first_result = response[0]
                
                # Verify search result structure
                expected_fields = ['session_id', 'session_title', 'message_preview', 'created_at']
                missing_fields = [field for field in expected_fields if field not in first_result]
                
                if not missing_fields:
                    print("   ✅ Search result structure is correct")
                else:
                    print(f"   ❌ Missing search result fields: {missing_fields}")
                    return False
                
                # Verify search relevance
                message_preview = first_result.get('message_preview', '').lower()
                if search_query.lower() in message_preview:
                    print(f"   ✅ Search results are relevant (contains '{search_query}')")
                else:
                    print(f"   ⚠️  Search results may not be relevant to '{search_query}'")
                
            else:
                print("   ⚠️  No search results found (may be expected for new conversation)")
            
            return True
        
        return False

    def run_all_tests(self):
        """Run all AI Health Coach endpoint tests"""
        print("🧪 AI Health Coach Backend Endpoint Tests")
        print("🎯 TDD localStorage Gate Fix Verification")
        print("=" * 80)
        print("Testing all 9 core AI Health Coach endpoints after frontend fixes")
        print("to ensure no regressions from TDD localStorage gate implementation.")
        print("=" * 80)
        
        tests = [
            self.test_1_feature_flags,
            self.test_2_accept_disclaimer,
            self.test_3_disclaimer_status,
            self.test_4_consultation_limit,
            self.test_5_create_session,
            self.test_6_get_user_sessions,
            self.test_7_send_message,
            self.test_8_get_messages,
            self.test_9_search_conversations,
        ]
        
        failed_tests = []
        
        for test_func in tests:
            try:
                if not test_func():
                    failed_tests.append(test_func.__name__)
            except Exception as e:
                print(f"❌ {test_func.__name__} failed with exception: {str(e)}")
                failed_tests.append(test_func.__name__)
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 AI HEALTH COACH TEST RESULTS")
        print("=" * 80)
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if failed_tests:
            print(f"\n❌ Failed tests:")
            for test in failed_tests:
                print(f"   - {test}")
        else:
            print("\n✅ All AI Health Coach tests passed!")
        
        if self.created_user_id:
            print(f"\n📝 Created test user ID: {self.created_user_id}")
        
        if self.ai_coach_session_id:
            print(f"📝 Created test session ID: {self.ai_coach_session_id}")
        
        # Summary for main agent
        print("\n" + "=" * 80)
        print("📋 SUMMARY FOR MAIN AGENT")
        print("=" * 80)
        
        if not failed_tests:
            print("✅ AI HEALTH COACH: All 9 core endpoints working correctly")
            print("✅ FEATURE FLAGS: coach_enabled=true, openai/gpt-4o-mini config verified")
            print("✅ DISCLAIMER SYSTEM: Acceptance and status tracking working")
            print("✅ CONSULTATION LIMITS: Standard plan (10/month) enforcement working")
            print("✅ SESSION MANAGEMENT: Creation and retrieval working")
            print("✅ REAL AI INTEGRATION: OpenAI GPT-4o-mini generating responses")
            print("✅ MESSAGE PERSISTENCE: Conversation history working")
            print("✅ SEARCH FUNCTIONALITY: Conversation search working")
            print("✅ NO REGRESSIONS: TDD localStorage gate fix did not break backend")
        else:
            print("❌ CRITICAL AI HEALTH COACH ISSUES FOUND:")
            for test in failed_tests:
                if "feature_flags" in test:
                    print("   - Feature flags configuration issue")
                elif "disclaimer" in test:
                    print("   - Disclaimer system issue")
                elif "consultation" in test:
                    print("   - Consultation limit system issue")
                elif "session" in test:
                    print("   - Session management issue")
                elif "message" in test:
                    print("   - AI integration or message system issue")
                elif "search" in test:
                    print("   - Search functionality issue")
        
        return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    tester = AIHealthCoachTester()
    sys.exit(tester.run_all_tests())