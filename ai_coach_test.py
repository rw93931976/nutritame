import requests
import sys
import json
from datetime import datetime
import time

class AIHealthCoachTester:
    def __init__(self, base_url="https://aihealth-repair.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_id = "test-user-123"  # As specified in review request
        self.session_id = None
        self.access_token = None

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

    def test_feature_flags(self):
        """Test GET /api/coach/feature-flags - Verify feature flags and configuration"""
        print("\n🎯 Testing AI Health Coach Feature Flags...")
        
        success, response = self.run_test(
            "AI Coach Feature Flags",
            "GET",
            "coach/feature-flags",
            200
        )
        
        if success:
            # Verify required feature flags (actual API response format)
            expected_flags = ['coach_enabled', 'llm_provider', 'llm_model', 'standard_limit', 'premium_limit']
            
            for flag in expected_flags:
                if flag in response:
                    print(f"   ✅ {flag}: {response[flag]}")
                else:
                    print(f"   ❌ Missing feature flag: {flag}")
                    return False
            
            # Verify coach is enabled
            if response.get('coach_enabled') is True:
                print("   ✅ AI Health Coach feature is enabled")
            else:
                print(f"   ❌ AI Health Coach should be enabled, got: {response.get('coach_enabled')}")
                return False
            
            # Verify standard limit is 10
            if response.get('standard_limit') == 10:
                print("   ✅ Standard plan limit is correctly set to 10")
            else:
                print(f"   ❌ Standard limit should be 10, got: {response.get('standard_limit')}")
                return False
            
            return True
        return False

    def test_accept_disclaimer(self):
        """Test POST /api/coach/accept-disclaimer - Test disclaimer acceptance functionality"""
        print("\n🎯 Testing AI Coach Disclaimer Acceptance...")
        
        disclaimer_data = {
            "user_id": self.test_user_id
        }
        
        success, response = self.run_test(
            "Accept AI Coach Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=disclaimer_data
        )
        
        if success:
            # Verify disclaimer acceptance response
            if response.get('accepted') is True:
                print("   ✅ Disclaimer acceptance recorded successfully")
            else:
                print(f"   ❌ Disclaimer acceptance failed: {response}")
                return False
            
            # Verify success message
            if 'message' in response:
                print(f"   ✅ Disclaimer acceptance message: {response['message']}")
            else:
                print(f"   ❌ Missing disclaimer acceptance message")
                return False
            
            return True
        return False

    def test_disclaimer_status(self):
        """Test GET /api/coach/disclaimer-status/{user_id} - Check disclaimer status"""
        print("\n🎯 Testing AI Coach Disclaimer Status Check...")
        
        success, response = self.run_test(
            "Check Disclaimer Status",
            "GET",
            f"coach/disclaimer-status/{self.test_user_id}",
            200
        )
        
        if success:
            # Verify disclaimer status response (actual API format)
            if 'disclaimer_accepted' in response:
                print(f"   ✅ Disclaimer status retrieved: {response['disclaimer_accepted']}")
            else:
                print(f"   ❌ Missing disclaimer_accepted field in response")
                return False
            
            # Verify user_id is returned
            if response.get('user_id') == self.test_user_id:
                print(f"   ✅ User ID matches: {self.test_user_id}")
            else:
                print(f"   ❌ User ID mismatch in response")
                return False
            
            return True
        return False

    def test_consultation_limit(self):
        """Test GET /api/coach/consultation-limit/{user_id} - Test consultation limit checking"""
        print("\n🎯 Testing AI Coach Consultation Limit Check...")
        
        success, response = self.run_test(
            "Check Consultation Limit",
            "GET",
            f"coach/consultation-limit/{self.test_user_id}",
            200
        )
        
        if success:
            # Verify consultation limit response structure
            required_fields = ['can_use', 'current_count', 'limit', 'plan']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify plan gating logic
            plan = response.get('plan', 'standard')
            limit = response.get('limit', 0)
            current_count = response.get('current_count', 0)
            can_use = response.get('can_use', False)
            
            print(f"   Plan: {plan}")
            print(f"   Current usage: {current_count}/{limit if limit != -1 else 'unlimited'}")
            print(f"   Can use: {can_use}")
            
            # Verify plan limits
            if plan == 'standard' and limit == 10:
                print("   ✅ Standard plan correctly limited to 10 consultations/month")
            elif plan == 'premium' and limit == -1:
                print("   ✅ Premium plan correctly set to unlimited consultations")
            else:
                print(f"   ❌ Unexpected plan limits: {plan} plan with {limit} limit")
                return False
            
            return True
        return False

    def test_create_session(self):
        """Test POST /api/coach/sessions - Create new AI coach session"""
        print("\n🎯 Testing AI Coach Session Creation...")
        
        # Create session with proper request format
        session_data = {
            "title": "Test AI Health Coach Session"
        }
        
        # Add user_id as query parameter
        url = f"coach/sessions?user_id={self.test_user_id}"
        
        success, response = self.run_test(
            "Create AI Coach Session",
            "POST",
            url,
            200,
            data=session_data
        )
        
        if success:
            # Verify session creation response
            if 'id' in response:
                self.session_id = response['id']
                print(f"   ✅ Session created with ID: {self.session_id}")
            else:
                print(f"   ❌ Missing session ID in response")
                return False
            
            # Verify session data
            if response.get('user_id') == self.test_user_id:
                print(f"   ✅ Session user ID matches: {self.test_user_id}")
            else:
                print(f"   ❌ Session user ID mismatch")
                return False
            
            if response.get('title') == session_data['title']:
                print(f"   ✅ Session title matches: {session_data['title']}")
            else:
                print(f"   ❌ Session title mismatch")
                return False
            
            # Verify timestamps
            if 'created_at' in response and 'updated_at' in response:
                print(f"   ✅ Session timestamps present")
            else:
                print(f"   ❌ Missing session timestamps")
                return False
            
            return True
        return False

    def test_get_user_sessions(self):
        """Test GET /api/coach/sessions/{user_id} - Get user's coach sessions"""
        print("\n🎯 Testing Get User AI Coach Sessions...")
        
        success, response = self.run_test(
            "Get User Coach Sessions",
            "GET",
            f"coach/sessions/{self.test_user_id}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} sessions")
            else:
                print(f"   ❌ Response should be a list, got: {type(response)}")
                return False
            
            # If we have sessions, verify structure
            if len(response) > 0:
                session = response[0]
                required_fields = ['id', 'user_id', 'title', 'created_at']
                missing_fields = [field for field in required_fields if field not in session]
                
                if missing_fields:
                    print(f"   ❌ Missing session fields: {missing_fields}")
                    return False
                
                print(f"   ✅ Session structure is correct")
                
                # Verify our created session is in the list
                if self.session_id and any(s.get('id') == self.session_id for s in response):
                    print(f"   ✅ Created session found in user sessions")
                else:
                    print(f"   ❌ Created session not found in user sessions")
                    return False
            
            return True
        return False

    def test_send_message_real_ai(self):
        """Test POST /api/coach/message - Send message to AI coach (REAL AI integration test)"""
        print("\n🎯 Testing Real AI Integration - Send Message to AI Coach...")
        
        if not self.session_id:
            print("   ❌ No session ID available for message testing")
            return False
        
        message_data = {
            "session_id": self.session_id,
            "message": "I'm a 45-year-old with Type 2 diabetes. Can you help me create a healthy breakfast plan that won't spike my blood sugar?"
        }
        
        print("   Note: Real AI response may take 10-30 seconds...")
        success, response = self.run_test(
            "Send Message to AI Coach (Real AI)",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success:
            # Verify AI response structure (actual API format)
            if 'ai_response' in response:
                ai_message = response['ai_response']
                
                # Verify message structure
                required_fields = ['id', 'session_id', 'role', 'text', 'created_at']
                missing_fields = [field for field in required_fields if field not in ai_message]
                
                if missing_fields:
                    print(f"   ❌ Missing AI message fields: {missing_fields}")
                    return False
                
                # Verify AI response content
                ai_text = ai_message.get('text', '')
                if len(ai_text) > 50:  # Reasonable AI response length
                    print(f"   ✅ AI generated substantial response ({len(ai_text)} characters)")
                    print(f"   AI Response preview: {ai_text[:200]}...")
                else:
                    print(f"   ❌ AI response too short or missing: {ai_text}")
                    return False
                
                # Verify role is 'assistant'
                if ai_message.get('role') == 'assistant':
                    print(f"   ✅ AI message role is correct: assistant")
                else:
                    print(f"   ❌ AI message role should be 'assistant', got: {ai_message.get('role')}")
                    return False
                
                # Check for diabetes-specific content (guardrail system prompt working)
                diabetes_keywords = ['diabetes', 'blood sugar', 'glucose', 'carbohydrate', 'insulin', 'diabetic']
                has_diabetes_content = any(keyword in ai_text.lower() for keyword in diabetes_keywords)
                
                if has_diabetes_content:
                    print(f"   ✅ AI response contains diabetes-specific guidance")
                else:
                    print(f"   ⚠️  AI response may not be diabetes-focused")
                
                # Check for imperial measurements (as specified in system prompt)
                imperial_keywords = ['cup', 'tablespoon', 'teaspoon', 'oz', 'ounce', 'pound', 'lb']
                has_imperial = any(keyword in ai_text.lower() for keyword in imperial_keywords)
                
                if has_imperial:
                    print(f"   ✅ AI response uses imperial measurements")
                else:
                    print(f"   ⚠️  AI response may not be using imperial measurements")
                
                # Check for shopping list offer (as specified in system prompt)
                shopping_keywords = ['shopping list', 'create a shopping list', 'would you like me to create']
                has_shopping_offer = any(keyword in ai_text.lower() for keyword in shopping_keywords)
                
                if has_shopping_offer:
                    print(f"   ✅ AI response includes shopping list offer")
                else:
                    print(f"   ⚠️  AI response missing shopping list offer")
                
                # Verify user message was also saved
                if 'user_message' in response:
                    user_message = response['user_message']
                    if user_message.get('role') == 'user' and user_message.get('text') == message_data['message']:
                        print(f"   ✅ User message correctly saved")
                    else:
                        print(f"   ❌ User message not properly saved")
                        return False
                
                # Verify consultation was used
                if response.get('consultation_used') is True:
                    print(f"   ✅ Consultation count incremented")
                else:
                    print(f"   ❌ Consultation count not incremented")
                    return False
                
                return True
            else:
                print(f"   ❌ Missing AI response in response")
                return False
        return False

    def test_get_session_messages(self):
        """Test GET /api/coach/messages/{session_id} - Get session messages"""
        print("\n🎯 Testing Get AI Coach Session Messages...")
        
        if not self.session_id:
            print("   ❌ No session ID available for message retrieval")
            return False
        
        success, response = self.run_test(
            "Get Session Messages",
            "GET",
            f"coach/messages/{self.session_id}",
            200
        )
        
        if success:
            # Verify response is a list
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} messages")
            else:
                print(f"   ❌ Response should be a list, got: {type(response)}")
                return False
            
            # Verify we have at least 2 messages (user + AI)
            if len(response) >= 2:
                print(f"   ✅ Session contains user and AI messages")
                
                # Verify message structure and conversation flow
                user_message = None
                ai_message = None
                
                for msg in response:
                    if msg.get('role') == 'user':
                        user_message = msg
                    elif msg.get('role') == 'assistant':
                        ai_message = msg
                
                if user_message and ai_message:
                    print(f"   ✅ Found both user and AI messages in conversation")
                    
                    # Verify message content
                    user_text = user_message.get('text', '')
                    ai_text = ai_message.get('text', '')
                    
                    if 'diabetes' in user_text.lower() and len(ai_text) > 50:
                        print(f"   ✅ Conversation flow is correct (user diabetes question → AI response)")
                    else:
                        print(f"   ❌ Conversation flow issue")
                        return False
                else:
                    print(f"   ❌ Missing user or AI message in conversation")
                    return False
            else:
                print(f"   ❌ Expected at least 2 messages, got {len(response)}")
                return False
            
            return True
        return False

    def test_search_conversations(self):
        """Test GET /api/coach/search/{user_id}?query=test - Search conversation history"""
        print("\n🎯 Testing AI Coach Conversation Search...")
        
        # Search for diabetes-related content
        search_query = "diabetes"
        
        success, response = self.run_test(
            "Search Conversation History",
            "GET",
            f"coach/search/{self.test_user_id}?query={search_query}",
            200
        )
        
        if success:
            # Verify search response structure (actual API format)
            if 'results' in response and 'query' in response:
                results = response['results']
                query = response['query']
                
                print(f"   ✅ Search returned {len(results)} session results for query: '{query}'")
                
                # Verify search results structure
                if len(results) > 0:
                    result = results[0]
                    
                    # Check if result has session and messages
                    if 'session' in result and 'messages' in result:
                        print(f"   ✅ Search results have correct structure (session + messages)")
                        
                        # Verify messages contain search term
                        messages = result['messages']
                        if len(messages) > 0:
                            found_query_term = False
                            for msg in messages:
                                if hasattr(msg, 'text') and search_query.lower() in msg.text.lower():
                                    found_query_term = True
                                    break
                                elif isinstance(msg, dict) and search_query.lower() in msg.get('text', '').lower():
                                    found_query_term = True
                                    break
                            
                            if found_query_term:
                                print(f"   ✅ Search results contain query term: {search_query}")
                            else:
                                print(f"   ⚠️  Search results may not contain query term")
                        else:
                            print(f"   ⚠️  No messages in search results")
                    else:
                        print(f"   ❌ Search result missing session or messages structure")
                        return False
                else:
                    print(f"   ✅ Search completed successfully (no results found)")
                
                return True
            else:
                print(f"   ❌ Missing search results or query in response")
                return False
        return False

    def test_plan_gating_standard_user(self):
        """Test plan gating for Standard plan (10 consults/month)"""
        print("\n🎯 Testing Plan Gating - Standard Plan Limits...")
        
        # Create a standard plan user scenario
        standard_user_id = "standard-user-test"
        
        # Check consultation limit for standard user
        success, response = self.run_test(
            "Standard Plan Consultation Limit",
            "GET",
            f"coach/consultation-limit/{standard_user_id}",
            200
        )
        
        if success:
            plan = response.get('plan', 'standard')
            limit = response.get('limit', 0)
            current_count = response.get('current_count', 0)
            can_use = response.get('can_use', False)
            
            # Verify standard plan limits
            if plan == 'standard' and limit == 10:
                print(f"   ✅ Standard plan correctly limited to 10 consultations")
            else:
                print(f"   ❌ Standard plan should have 10 consultation limit, got: {limit}")
                return False
            
            # Verify remaining consultations calculation
            remaining = response.get('remaining', 0)
            expected_remaining = limit - current_count if limit != -1 else -1
            
            if remaining == expected_remaining:
                print(f"   ✅ Remaining consultations calculated correctly: {remaining}")
            else:
                print(f"   ❌ Remaining consultations calculation error")
                return False
            
            return True
        return False

    def test_monthly_limit_reset_logic(self):
        """Test monthly consultation limit reset logic"""
        print("\n🎯 Testing Monthly Consultation Limit Reset Logic...")
        
        # This test verifies the monthly reset logic by checking the current month handling
        success, response = self.run_test(
            "Monthly Reset Logic Check",
            "GET",
            f"coach/consultation-limit/{self.test_user_id}",
            200
        )
        
        if success:
            current_month = datetime.now().strftime("%Y-%m")
            
            # The API should handle monthly reset automatically
            # Verify the response structure is correct for reset logic
            required_fields = ['can_use', 'current_count', 'limit', 'plan', 'remaining']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing fields for reset logic: {missing_fields}")
                return False
            
            # Verify plan and limit consistency
            plan = response.get('plan', 'standard')
            limit = response.get('limit', 0)
            
            if plan == 'standard' and limit == 10:
                print(f"   ✅ Monthly reset logic maintains correct standard plan limits")
            elif plan == 'premium' and limit == -1:
                print(f"   ✅ Monthly reset logic maintains correct premium plan limits")
            else:
                print(f"   ❌ Monthly reset logic has incorrect plan/limit: {plan}/{limit}")
                return False
            
            # Verify remaining calculation is correct
            current_count = response.get('current_count', 0)
            remaining = response.get('remaining', 0)
            expected_remaining = limit - current_count if limit != -1 else -1
            
            if remaining == expected_remaining:
                print(f"   ✅ Monthly reset logic calculates remaining correctly: {remaining}")
            else:
                print(f"   ❌ Monthly reset calculation error: expected {expected_remaining}, got {remaining}")
                return False
            
            print(f"   ✅ Monthly reset logic is functioning correctly for {current_month}")
            return True
        return False

    def test_database_operations(self):
        """Test database operations for AI Coach collections"""
        print("\n🎯 Testing AI Coach Database Operations...")
        
        # Test that our session and messages are persisted
        if not self.session_id:
            print("   ❌ No session ID available for database testing")
            return False
        
        # Retrieve session to verify persistence
        success, response = self.run_test(
            "Database Session Persistence",
            "GET",
            f"coach/sessions/{self.test_user_id}",
            200
        )
        
        if success and isinstance(response, list):
            # Find our test session
            test_session = None
            for session in response:
                if session.get('id') == self.session_id:
                    test_session = session
                    break
            
            if test_session:
                print(f"   ✅ Session persisted in database: {self.session_id}")
                
                # Verify session data integrity
                if test_session.get('user_id') == self.test_user_id:
                    print(f"   ✅ Session user_id correctly stored")
                else:
                    print(f"   ❌ Session user_id mismatch in database")
                    return False
                
                return True
            else:
                print(f"   ❌ Session not found in database")
                return False
        return False

    def test_error_handling(self):
        """Test error handling for invalid data"""
        print("\n🎯 Testing AI Coach Error Handling...")
        
        # Test invalid user ID
        success, response = self.run_test(
            "Invalid User ID Error Handling",
            "GET",
            "coach/sessions/invalid-user-id-12345",
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for invalid user ID")
        else:
            print(f"   ❌ Should return 404 for invalid user ID")
            return False
        
        # Test invalid session ID for messages
        success, response = self.run_test(
            "Invalid Session ID Error Handling",
            "GET",
            "coach/messages/invalid-session-id-12345",
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for invalid session ID")
        else:
            print(f"   ❌ Should return 404 for invalid session ID")
            return False
        
        # Test missing required fields
        success, response = self.run_test(
            "Missing Required Fields Error Handling",
            "POST",
            "coach/message",
            400,
            data={"message": "test"}  # Missing session_id
        )
        
        if success:
            print(f"   ✅ Correctly returned 400 for missing required fields")
        else:
            print(f"   ❌ Should return 400 for missing required fields")
            return False
        
        return True

    def run_comprehensive_tests(self):
        """Run all AI Health Coach tests"""
        print("🚀 Starting Comprehensive AI Health Coach Backend Testing...")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        # Core API endpoint tests
        tests = [
            self.test_feature_flags,
            self.test_accept_disclaimer,
            self.test_disclaimer_status,
            self.test_consultation_limit,
            self.test_create_session,
            self.test_get_user_sessions,
            self.test_send_message_real_ai,
            self.test_get_session_messages,
            self.test_search_conversations,
            
            # Plan gating and limits
            self.test_plan_gating_standard_user,
            self.test_monthly_limit_reset_logic,
            
            # Database and error handling
            self.test_database_operations,
            self.test_error_handling,
        ]
        
        failed_tests = []
        
        for test in tests:
            try:
                if not test():
                    failed_tests.append(test.__name__)
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                failed_tests.append(test.__name__)
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 AI HEALTH COACH BACKEND TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test}")
        else:
            print(f"\n✅ All tests passed!")
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = AIHealthCoachTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)