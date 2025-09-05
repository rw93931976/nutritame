#!/usr/bin/env python3
"""
Comprehensive AI Health Coach Backend Endpoint Tests
v2.2.9 Session Reference Fixes Verification

Tests all 9 core AI Health Coach endpoints after v2.2.9 session reference fixes
to verify real AI integration with OpenAI GPT-4o-mini and ensure no regressions.

Expected success rate: 100% (all 9 endpoints working).
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class ComprehensiveAIHealthCoachTester:
    def __init__(self, base_url="https://coach-consent.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_id = None
        self.created_session_id = None
        self.test_results = []

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
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response": response_data
                    })
                    return True, response_data
                except:
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response": response.text
                    })
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "error": error_data,
                        "expected_status": expected_status,
                        "actual_status": response.status_code
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "error": response.text,
                        "expected_status": expected_status,
                        "actual_status": response.status_code
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "FAILED",
                "error": str(e)
            })
            return False, {}

    def create_test_user_profile(self):
        """Create a comprehensive test user profile for AI Health Coach testing"""
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
            "Create Test User Profile for AI Coach",
            "POST",
            "users",
            200,
            data=test_profile
        )
        
        if success and 'id' in response:
            self.created_user_id = response['id']
            print(f"   ✅ Created test user ID: {self.created_user_id}")
            return True
        else:
            print(f"   ❌ Failed to create test user profile: {response}")
            return False

    def test_1_feature_flags(self):
        """Test 1: GET /api/coach/feature-flags - should return coach_enabled=true, openai/gpt-4o-mini config"""
        print("\n" + "="*80)
        print("TEST 1: AI Health Coach Feature Flags")
        print("="*80)
        
        success, response = self.run_test(
            "GET /api/coach/feature-flags",
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

    def test_2_accept_disclaimer(self):
        """Test 2: POST /api/coach/accept-disclaimer - should accept disclaimer properly"""
        print("\n" + "="*80)
        print("TEST 2: AI Health Coach Accept Disclaimer")
        print("="*80)
        
        if not self.created_user_id:
            print("   ❌ No user ID available for disclaimer testing")
            return False
        
        disclaimer_data = {
            "user_id": self.created_user_id
        }
        
        success, response = self.run_test(
            "POST /api/coach/accept-disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=disclaimer_data
        )
        
        if success:
            # Check for acceptance confirmation - be flexible with response format
            accepted = (response.get('success') is True or 
                       response.get('accepted') is True or
                       'accepted' in response.get('message', '').lower())
            
            if accepted:
                print("   ✅ Disclaimer acceptance recorded successfully")
                return True
            else:
                print(f"   ❌ Disclaimer acceptance failed: {response}")
                return False
        
        return False

    def test_3_disclaimer_status(self):
        """Test 3: GET /api/coach/disclaimer-status/{user_id} - should retrieve disclaimer status"""
        print("\n" + "="*80)
        print("TEST 3: AI Health Coach Disclaimer Status")
        print("="*80)
        
        if not self.created_user_id:
            print("   ❌ No user ID available for disclaimer status testing")
            return False
        
        success, response = self.run_test(
            "GET /api/coach/disclaimer-status/{user_id}",
            "GET",
            f"coach/disclaimer-status/{self.created_user_id}",
            200
        )
        
        if success:
            # Check for disclaimer acceptance status - be flexible with response format
            accepted = (response.get('disclaimer_accepted') is True or 
                       response.get('accepted') is True)
            
            if accepted:
                print("   ✅ Disclaimer status correctly shows accepted")
                return True
            else:
                print(f"   ❌ Disclaimer status should show accepted: {response}")
                return False
        
        return False

    def test_4_consultation_limit(self):
        """Test 4: GET /api/coach/consultation-limit/{user_id} - should show standard plan limits"""
        print("\n" + "="*80)
        print("TEST 4: AI Health Coach Consultation Limits")
        print("="*80)
        
        if not self.created_user_id:
            print("   ❌ No user ID available for consultation limit testing")
            return False
        
        success, response = self.run_test(
            "GET /api/coach/consultation-limit/{user_id}",
            "GET",
            f"coach/consultation-limit/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify standard plan limits
            if response.get('limit') == 10:
                print("   ✅ Standard plan limit correctly set to 10")
            else:
                print(f"   ❌ Standard plan limit should be 10, got: {response.get('limit')}")
                return False
            
            # Verify plan type
            if response.get('plan') == 'standard':
                print("   ✅ Plan type correctly set to standard")
            else:
                print(f"   ❌ Plan type should be standard, got: {response.get('plan')}")
                return False
            
            # Verify can_use flag
            if response.get('can_use') is True:
                print("   ✅ User can use consultation service")
            else:
                print(f"   ❌ User should be able to use consultation service: {response}")
                return False
            
            return True
        
        return False

    def test_5_create_session(self):
        """Test 5: POST /api/coach/sessions - should create sessions correctly"""
        print("\n" + "="*80)
        print("TEST 5: AI Health Coach Create Session")
        print("="*80)
        
        if not self.created_user_id:
            print("   ❌ No user ID available for session creation testing")
            return False
        
        session_data = {
            "title": "Test AI Health Coach Session"
        }
        
        # Include user_id as query parameter
        success, response = self.run_test(
            "POST /api/coach/sessions",
            "POST",
            f"coach/sessions?user_id={self.created_user_id}",
            200,
            data=session_data
        )
        
        if success:
            # Verify session creation
            if 'id' in response:
                self.created_session_id = response['id']
                print(f"   ✅ Session created successfully with ID: {self.created_session_id}")
            else:
                print(f"   ❌ Session creation failed - no ID returned: {response}")
                return False
            
            # Verify user_id is linked
            if response.get('user_id') == self.created_user_id:
                print("   ✅ Session correctly linked to user")
            else:
                print(f"   ❌ Session not properly linked to user: {response}")
                return False
            
            # Verify title
            if response.get('title') == "Test AI Health Coach Session":
                print("   ✅ Session title correctly set")
            else:
                print(f"   ❌ Session title not set correctly: {response}")
                return False
            
            return True
        
        return False

    def test_6_get_sessions(self):
        """Test 6: GET /api/coach/sessions/{user_id} - should retrieve user sessions"""
        print("\n" + "="*80)
        print("TEST 6: AI Health Coach Get User Sessions")
        print("="*80)
        
        if not self.created_user_id:
            print("   ❌ No user ID available for session retrieval testing")
            return False
        
        success, response = self.run_test(
            "GET /api/coach/sessions/{user_id}",
            "GET",
            f"coach/sessions/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} sessions")
            else:
                print(f"   ❌ Response should be a list of sessions: {response}")
                return False
            
            # Verify we have at least one session (the one we created)
            if len(response) >= 1:
                print("   ✅ At least one session found")
                
                # Verify session structure
                first_session = response[0]
                if 'id' in first_session and 'user_id' in first_session:
                    print("   ✅ Session structure is correct")
                else:
                    print(f"   ❌ Session structure missing required fields: {first_session}")
                    return False
                
                # Verify user_id matches
                if first_session.get('user_id') == self.created_user_id:
                    print("   ✅ Session belongs to correct user")
                else:
                    print(f"   ❌ Session user_id mismatch: {first_session}")
                    return False
                
                return True
            else:
                print("   ❌ No sessions found for user")
                return False
        
        return False

    def test_7_send_message(self):
        """Test 7: POST /api/coach/message - should send messages to real OpenAI AI and get responses"""
        print("\n" + "="*80)
        print("TEST 7: AI Health Coach Send Message (Real AI Integration)")
        print("="*80)
        
        if not self.created_user_id or not self.created_session_id:
            print("   ❌ No user ID or session ID available for message testing")
            return False
        
        message_data = {
            "session_id": self.created_session_id,
            "message": "Create a Mediterranean breakfast meal plan for someone with Type 2 diabetes who is allergic to nuts and shellfish"
        }
        
        print("   Note: AI response may take 10-30 seconds...")
        success, response = self.run_test(
            "POST /api/coach/message",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success:
            # Check for AI response in various possible response formats
            ai_response = None
            
            # Check different possible response structures
            if 'ai_message' in response and 'text' in response['ai_message']:
                ai_response = response['ai_message']['text']
            elif 'ai_response' in response and isinstance(response['ai_response'], dict) and 'text' in response['ai_response']:
                ai_response = response['ai_response']['text']
            elif 'ai_response' in response and isinstance(response['ai_response'], str):
                ai_response = response['ai_response']
            elif 'response' in response:
                ai_response = response['response']
            elif 'message' in response and isinstance(response['message'], str):
                ai_response = response['message']
            
            if ai_response and len(ai_response) > 50:  # Substantial response
                print(f"   ✅ AI response received (length: {len(ai_response)} chars)")
                print(f"   Response preview: {ai_response[:200]}...")
                
                # Verify diabetes-specific content
                diabetes_keywords = ['diabetes', 'blood sugar', 'glucose', 'carb', 'mediterranean']
                found_keywords = [kw for kw in diabetes_keywords if kw.lower() in ai_response.lower()]
                
                if found_keywords:
                    print(f"   ✅ AI response contains diabetes-specific content: {found_keywords}")
                else:
                    print("   ⚠️  AI response may not contain diabetes-specific content")
                
                # Check for allergy awareness
                if 'nuts' not in ai_response.lower() and 'shellfish' not in ai_response.lower():
                    print("   ✅ AI response respects allergy restrictions (no nuts/shellfish)")
                else:
                    print("   ⚠️  AI response may contain allergens")
                
                # Check for Mediterranean content
                mediterranean_keywords = ['olive oil', 'mediterranean', 'tomato', 'feta', 'olives']
                found_med = [kw for kw in mediterranean_keywords if kw.lower() in ai_response.lower()]
                
                if found_med:
                    print(f"   ✅ AI response contains Mediterranean content: {found_med}")
                else:
                    print("   ⚠️  AI response may not contain Mediterranean content")
                
                return True
            else:
                print(f"   ❌ AI response too short or missing. Full response: {response}")
                return False
        
        return False

    def test_8_get_messages(self):
        """Test 8: GET /api/coach/messages/{session_id} - should retrieve conversation history"""
        print("\n" + "="*80)
        print("TEST 8: AI Health Coach Get Messages")
        print("="*80)
        
        if not self.created_session_id:
            print("   ❌ No session ID available for message retrieval testing")
            return False
        
        success, response = self.run_test(
            "GET /api/coach/messages/{session_id}",
            "GET",
            f"coach/messages/{self.created_session_id}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} messages")
            else:
                print(f"   ❌ Response should be a list of messages: {response}")
                return False
            
            # Verify we have at least 2 messages (user + assistant)
            if len(response) >= 2:
                print("   ✅ At least 2 messages found (user + assistant)")
                
                # Verify message structure
                user_message = None
                assistant_message = None
                
                for msg in response:
                    if msg.get('role') == 'user':
                        user_message = msg
                    elif msg.get('role') == 'assistant':
                        assistant_message = msg
                
                if user_message and assistant_message:
                    print("   ✅ Both user and assistant messages found")
                    
                    # Verify message content
                    if 'text' in user_message and len(user_message['text']) > 0:
                        print("   ✅ User message has content")
                    else:
                        print(f"   ❌ User message missing content: {user_message}")
                        return False
                    
                    if 'text' in assistant_message and len(assistant_message['text']) > 50:
                        print("   ✅ Assistant message has substantial content")
                    else:
                        print(f"   ❌ Assistant message missing or too short: {assistant_message}")
                        return False
                    
                    return True
                else:
                    print(f"   ❌ Missing user or assistant messages: {response}")
                    return False
            else:
                print("   ❌ Not enough messages found in conversation")
                return False
        
        return False

    def test_9_search_conversations(self):
        """Test 9: GET /api/coach/search/{user_id} - should search conversations"""
        print("\n" + "="*80)
        print("TEST 9: AI Health Coach Search Conversations")
        print("="*80)
        
        if not self.created_user_id:
            print("   ❌ No user ID available for search testing")
            return False
        
        # Test search with query parameter
        success, response = self.run_test(
            "GET /api/coach/search/{user_id}",
            "GET",
            f"coach/search/{self.created_user_id}?query=mediterranean",
            200
        )
        
        if success:
            # Handle different response formats
            search_results = response
            if isinstance(response, dict) and 'results' in response:
                search_results = response['results']
            
            if isinstance(search_results, list):
                print(f"   ✅ Search returned {len(search_results)} results")
                
                # If we have results, verify structure
                if len(search_results) > 0:
                    first_result = search_results[0]
                    if 'session' in first_result or 'session_id' in first_result or 'id' in first_result:
                        print("   ✅ Search results have proper structure")
                    else:
                        print(f"   ❌ Search result structure missing required fields: {first_result}")
                        return False
                
                return True
            elif isinstance(response, dict) and 'results' in response:
                # Handle dict response format
                results = response['results']
                if isinstance(results, list):
                    print(f"   ✅ Search returned {len(results)} results in dict format")
                    return True
                else:
                    print(f"   ❌ Search results should be a list: {results}")
                    return False
            else:
                print(f"   ❌ Search response should be a list or dict with results: {response}")
                return False
        
        return False

    def run_comprehensive_test(self):
        """Run all 9 AI Health Coach endpoint tests"""
        print("🎯 STARTING COMPREHENSIVE AI HEALTH COACH ENDPOINT TESTING")
        print("Testing NutriTame AI Health Coach backend after v2.2.9 session reference fixes")
        print("Focus: Verify all 9 core endpoints are working correctly")
        print("Expected success rate: 100% (all 9 endpoints working)")
        print("="*80)
        
        # Create test user profile first
        if not self.create_test_user_profile():
            print("❌ CRITICAL: Failed to create test user profile. Cannot proceed with tests.")
            return False
        
        # Run all 9 tests in order
        test_methods = [
            self.test_1_feature_flags,
            self.test_2_accept_disclaimer,
            self.test_3_disclaimer_status,
            self.test_4_consultation_limit,
            self.test_5_create_session,
            self.test_6_get_sessions,
            self.test_7_send_message,
            self.test_8_get_messages,
            self.test_9_search_conversations
        ]
        
        passed_tests = 0
        failed_tests = []
        
        for i, test_method in enumerate(test_methods, 1):
            try:
                if test_method():
                    passed_tests += 1
                    print(f"✅ TEST {i} PASSED")
                else:
                    failed_tests.append(f"Test {i}: {test_method.__name__}")
                    print(f"❌ TEST {i} FAILED")
            except Exception as e:
                failed_tests.append(f"Test {i}: {test_method.__name__} - Exception: {str(e)}")
                print(f"❌ TEST {i} FAILED WITH EXCEPTION: {str(e)}")
        
        # Print final results
        print("\n" + "="*80)
        print("🎯 FINAL TEST RESULTS")
        print("="*80)
        print(f"Total Tests Run: {len(test_methods)}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {len(failed_tests)}")
        print(f"Success Rate: {(passed_tests/len(test_methods)*100):.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for failed_test in failed_tests:
                print(f"   - {failed_test}")
        
        if passed_tests == len(test_methods):
            print("\n🎉 SUCCESS: All 9 AI Health Coach endpoints are working correctly!")
            print("✅ Real AI integration with OpenAI GPT-4o-mini is functional")
            print("✅ No regressions detected from v2.2.9 session reference fixes")
            return True
        else:
            print(f"\n⚠️  WARNING: {len(failed_tests)} out of {len(test_methods)} tests failed")
            print("❌ Some AI Health Coach endpoints may have issues")
            return False

def main():
    """Main function to run AI Health Coach tests"""
    tester = ComprehensiveAIHealthCoachTester()
    
    print("🚀 COMPREHENSIVE AI HEALTH COACH ENDPOINT TESTER")
    print("Testing NutriTame AI Health Coach backend endpoints")
    print("Focus: Verify all 9 core endpoints after v2.2.9 session reference fixes")
    print("="*80)
    
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ ALL TESTS PASSED - AI Health Coach backend is ready for production")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - Review issues before production deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()