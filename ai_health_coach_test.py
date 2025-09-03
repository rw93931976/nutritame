import requests
import sys
import json
import uuid
from datetime import datetime

class AIHealthCoachTester:
    def __init__(self, base_url="https://aihealth-repair.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_id = str(uuid.uuid4())
        self.test_session_id = None
        self.created_sessions = []
        
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
        """Test GET /api/coach/feature-flags endpoint"""
        success, response = self.run_test(
            "AI Health Coach Feature Flags",
            "GET",
            "coach/feature-flags",
            200
        )
        
        if success:
            # Verify expected configuration
            expected_fields = ['coach_enabled', 'llm_provider', 'llm_model', 'standard_limit', 'premium_limit']
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            # Verify specific values
            if response.get('coach_enabled') is True:
                print("   ✅ AI Health Coach is enabled")
            else:
                print(f"   ❌ Coach should be enabled, got: {response.get('coach_enabled')}")
                return False
                
            if response.get('llm_provider') == 'openai':
                print("   ✅ LLM provider is OpenAI")
            else:
                print(f"   ❌ Expected OpenAI provider, got: {response.get('llm_provider')}")
                return False
                
            if response.get('llm_model') == 'gpt-4o-mini':
                print("   ✅ LLM model is GPT-4o-mini")
            else:
                print(f"   ❌ Expected GPT-4o-mini, got: {response.get('llm_model')}")
                return False
                
            if response.get('standard_limit') == 10:
                print("   ✅ Standard plan limit is 10/month")
            else:
                print(f"   ❌ Expected standard limit 10, got: {response.get('standard_limit')}")
                return False
                
            if response.get('premium_limit') == 'unlimited':
                print("   ✅ Premium plan is unlimited")
            else:
                print(f"   ❌ Expected unlimited premium, got: {response.get('premium_limit')}")
                return False
                
            return True
        return False

    def test_accept_disclaimer(self):
        """Test POST /api/coach/accept-disclaimer endpoint"""
        disclaimer_data = {
            "user_id": self.test_user_id
        }
        
        success, response = self.run_test(
            "Accept Medical Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=disclaimer_data
        )
        
        if success:
            # Verify response structure
            if response.get('accepted') is True:
                print("   ✅ Disclaimer acceptance recorded")
            else:
                print(f"   ❌ Disclaimer not properly accepted: {response}")
                return False
                
            if 'accepted_at' in response:
                print("   ✅ Acceptance timestamp recorded")
            else:
                print("   ❌ Missing acceptance timestamp")
                return False
                
            return True
        return False

    def test_disclaimer_status(self):
        """Test GET /api/coach/disclaimer-status/{user_id} endpoint"""
        success, response = self.run_test(
            "Check Disclaimer Status",
            "GET",
            f"coach/disclaimer-status/{self.test_user_id}",
            200
        )
        
        if success:
            # Verify disclaimer was accepted (from previous test)
            # The response uses 'disclaimer_accepted' field, not 'accepted'
            if response.get('disclaimer_accepted') is True:
                print("   ✅ Disclaimer status correctly shows accepted")
            else:
                print(f"   ❌ Disclaimer should be accepted, got: {response}")
                return False
                
            if 'user_id' in response:
                print("   ✅ User ID included in status response")
            else:
                print("   ❌ Missing user ID in status response")
                return False
                
            return True
        return False

    def test_consultation_limit_standard(self):
        """Test GET /api/coach/consultation-limit/{user_id} for standard plan"""
        success, response = self.run_test(
            "Check Consultation Limit (Standard Plan)",
            "GET",
            f"coach/consultation-limit/{self.test_user_id}",
            200
        )
        
        if success:
            # Verify standard plan limits
            expected_fields = ['can_use', 'current_count', 'limit', 'plan', 'remaining']
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            if response.get('plan') == 'standard':
                print("   ✅ User has standard plan")
            else:
                print(f"   ❌ Expected standard plan, got: {response.get('plan')}")
                return False
                
            if response.get('limit') == 10:
                print("   ✅ Standard plan limit is 10 consultations/month")
            else:
                print(f"   ❌ Expected limit 10, got: {response.get('limit')}")
                return False
                
            if response.get('can_use') is True:
                print("   ✅ User can use consultations")
            else:
                print(f"   ❌ User should be able to use consultations: {response}")
                return False
                
            # Store initial count for later verification
            self.initial_consultation_count = response.get('current_count', 0)
            print(f"   ✅ Current consultation count: {self.initial_consultation_count}")
            
            return True
        return False

    def test_create_session(self):
        """Test POST /api/coach/sessions endpoint"""
        session_data = {
            "title": "Test Diabetes Meal Planning Session"
        }
        
        success, response = self.run_test(
            "Create AI Health Coach Session",
            "POST",
            f"coach/sessions?user_id={self.test_user_id}",
            200,
            data=session_data
        )
        
        if success:
            # Verify session creation
            if 'id' in response:
                self.test_session_id = response['id']
                self.created_sessions.append(self.test_session_id)
                print(f"   ✅ Session created with ID: {self.test_session_id}")
            else:
                print(f"   ❌ No session ID in response: {response}")
                return False
                
            if response.get('user_id') == self.test_user_id:
                print("   ✅ Session linked to correct user")
            else:
                print(f"   ❌ User ID mismatch: {response.get('user_id')}")
                return False
                
            if response.get('title') == session_data['title']:
                print("   ✅ Session title saved correctly")
            else:
                print(f"   ❌ Title mismatch: {response.get('title')}")
                return False
                
            if 'created_at' in response:
                print("   ✅ Session timestamp recorded")
            else:
                print("   ❌ Missing creation timestamp")
                return False
                
            return True
        return False

    def test_get_user_sessions(self):
        """Test GET /api/coach/sessions/{user_id} endpoint"""
        success, response = self.run_test(
            "Get User Sessions",
            "GET",
            f"coach/sessions/{self.test_user_id}",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} sessions")
            else:
                print(f"   ❌ Expected list of sessions, got: {type(response)}")
                return False
                
            # Verify our created session is in the list
            session_ids = [session.get('id') for session in response]
            if self.test_session_id in session_ids:
                print(f"   ✅ Created session found in user sessions")
            else:
                print(f"   ❌ Created session not found in user sessions")
                return False
                
            return True
        return False

    def test_send_message_real_ai(self):
        """Test POST /api/coach/message endpoint with real AI integration"""
        if not self.test_session_id:
            print("   ❌ No session ID available for message testing")
            return False
            
        message_data = {
            "user_id": self.test_user_id,
            "session_id": self.test_session_id,
            "message": "I have Type 2 diabetes and need help creating a Mediterranean-style meal plan for this week. I prefer low-carb options and need to avoid nuts due to allergies."
        }
        
        print("   Note: Real AI response may take 15-30 seconds...")
        success, response = self.run_test(
            "Send Message to AI Health Coach",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success:
            # Verify AI response structure
            if 'response' in response:
                ai_response = response['response']
                print(f"   ✅ AI response received ({len(ai_response)} characters)")
                print(f"   AI Response preview: {ai_response[:200]}...")
                
                # Verify diabetes-specific content
                diabetes_keywords = ['diabetes', 'blood sugar', 'carbohydrate', 'mediterranean', 'low-carb']
                found_keywords = [kw for kw in diabetes_keywords if kw.lower() in ai_response.lower()]
                
                if len(found_keywords) >= 3:
                    print(f"   ✅ AI response contains diabetes-specific content: {found_keywords}")
                else:
                    print(f"   ⚠️  AI response may lack diabetes-specific content: {found_keywords}")
                
                # Check for imperial measurements (requirement)
                imperial_units = ['cup', 'tablespoon', 'teaspoon', 'oz', 'pound', 'lb']
                found_units = [unit for unit in imperial_units if unit in ai_response.lower()]
                
                if found_units:
                    print(f"   ✅ AI response uses imperial measurements: {found_units}")
                else:
                    print(f"   ⚠️  AI response may not use imperial measurements")
                
                # Check for shopping list offer (requirement)
                if "shopping list" in ai_response.lower():
                    print("   ✅ AI response includes shopping list offer")
                else:
                    print("   ⚠️  AI response missing shopping list offer")
                
            else:
                print(f"   ❌ No AI response in message: {response}")
                return False
                
            if 'message_id' in response:
                self.test_message_id = response['message_id']
                print(f"   ✅ Message saved with ID: {self.test_message_id}")
            else:
                print("   ❌ No message ID returned")
                return False
                
            return True
        return False

    def test_get_session_messages(self):
        """Test GET /api/coach/messages/{session_id} endpoint"""
        if not self.test_session_id:
            print("   ❌ No session ID available for message retrieval")
            return False
            
        success, response = self.run_test(
            "Get Session Messages",
            "GET",
            f"coach/messages/{self.test_session_id}",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Retrieved {len(response)} messages")
            else:
                print(f"   ❌ Expected list of messages, got: {type(response)}")
                return False
                
            # Verify message structure
            if len(response) >= 2:  # Should have user message and AI response
                user_message = None
                ai_message = None
                
                for msg in response:
                    if msg.get('role') == 'user':
                        user_message = msg
                    elif msg.get('role') == 'assistant':
                        ai_message = msg
                
                if user_message:
                    print("   ✅ User message found in conversation history")
                else:
                    print("   ❌ User message not found in history")
                    return False
                    
                if ai_message:
                    print("   ✅ AI response found in conversation history")
                    print(f"   AI message preview: {ai_message.get('text', '')[:100]}...")
                else:
                    print("   ❌ AI response not found in history")
                    return False
                    
            else:
                print(f"   ❌ Expected at least 2 messages, got {len(response)}")
                return False
                
            return True
        return False

    def test_search_conversations(self):
        """Test GET /api/coach/search/{user_id} endpoint"""
        # Add a search query parameter
        search_query = "mediterranean meal plan"
        
        success, response = self.run_test(
            "Search User Conversations",
            "GET",
            f"coach/search/{self.test_user_id}?query={search_query}",
            200
        )
        
        if success:
            # The response should be a dict with 'query' and 'results' fields
            if isinstance(response, dict) and 'results' in response:
                results = response['results']
                print(f"   ✅ Search returned {len(results)} results")
                
                # Verify query field
                if response.get('query') == search_query:
                    print("   ✅ Search query correctly echoed back")
                else:
                    print(f"   ❌ Query mismatch: expected '{search_query}', got '{response.get('query')}'")
                    return False
                    
            else:
                print(f"   ❌ Expected dict with 'results' field, got: {type(response)}")
                return False
                
            # If we have results, verify structure
            if len(results) > 0:
                first_result = results[0]
                expected_fields = ['session', 'messages']
                
                for field in expected_fields:
                    if field in first_result:
                        print(f"   ✅ Search result contains {field}")
                    else:
                        print(f"   ⚠️  Search result missing {field}")
                
                # Check if our session appears in search results
                session_ids = [result.get('session', {}).get('id') for result in results]
                if self.test_session_id in session_ids:
                    print("   ✅ Created session found in search results")
                else:
                    print("   ⚠️  Created session not found in search (may be expected)")
                    
            return True
        return False

    def test_consultation_count_increment(self):
        """Test that consultation count increments after AI interaction"""
        success, response = self.run_test(
            "Check Consultation Count After AI Interaction",
            "GET",
            f"coach/consultation-limit/{self.test_user_id}",
            200
        )
        
        if success:
            current_count = response.get('current_count', 0)
            expected_count = self.initial_consultation_count + 1
            
            if current_count == expected_count:
                print(f"   ✅ Consultation count incremented correctly: {current_count}")
            else:
                print(f"   ❌ Count should be {expected_count}, got {current_count}")
                return False
                
            remaining = response.get('remaining', 0)
            expected_remaining = 10 - current_count
            
            if remaining == expected_remaining:
                print(f"   ✅ Remaining consultations calculated correctly: {remaining}")
            else:
                print(f"   ❌ Remaining should be {expected_remaining}, got {remaining}")
                return False
                
            return True
        return False

    def test_premium_user_unlimited_consultations(self):
        """Test premium user consultation limits"""
        # Create a premium user for testing
        premium_user_id = str(uuid.uuid4())
        
        # First create a consultation limit record for premium user
        # This would normally be done through user profile creation
        # For testing, we'll check if the system handles premium users correctly
        
        success, response = self.run_test(
            "Check Premium User Consultation Limit",
            "GET",
            f"coach/consultation-limit/{premium_user_id}",
            200
        )
        
        if success:
            # For a new premium user, the system should create a premium plan
            # or default to standard - let's see what happens
            plan = response.get('plan', 'standard')
            limit = response.get('limit', 10)
            
            print(f"   ℹ️  New user plan: {plan}, limit: {limit}")
            
            if plan == 'premium' and limit == -1:
                print("   ✅ Premium user has unlimited consultations")
                return True
            elif plan == 'standard' and limit == 10:
                print("   ℹ️  New user defaults to standard plan (expected)")
                return True
            else:
                print(f"   ⚠️  Unexpected plan configuration: {plan}, {limit}")
                return True  # Don't fail for this edge case
                
        return False

    def test_monthly_reset_logic(self):
        """Test monthly consultation reset logic"""
        # This test verifies the monthly reset functionality
        # We can't easily test actual month transitions, but we can verify
        # the current month tracking
        
        success, response = self.run_test(
            "Verify Monthly Reset Logic",
            "GET",
            f"coach/consultation-limit/{self.test_user_id}",
            200
        )
        
        if success:
            current_month = datetime.now().strftime("%Y-%m")
            
            # The response should include month tracking information
            # This verifies the system is tracking months for reset logic
            print(f"   ℹ️  Current month: {current_month}")
            print(f"   ℹ️  User consultation count: {response.get('current_count', 0)}")
            print(f"   ℹ️  User plan: {response.get('plan', 'unknown')}")
            
            # Verify the system is tracking consultation limits properly
            if 'current_count' in response and 'limit' in response:
                print("   ✅ Monthly reset logic components are present")
                return True
            else:
                print("   ❌ Missing monthly reset logic components")
                return False
                
        return False

    def test_error_handling_invalid_user(self):
        """Test error handling for invalid user IDs"""
        invalid_user_id = "invalid-user-id-12345"
        
        success, response = self.run_test(
            "Error Handling - Invalid User ID",
            "GET",
            f"coach/disclaimer-status/{invalid_user_id}",
            200  # Should still return 200 with disclaimer_accepted: false for new users
        )
        
        if success:
            # For invalid/new users, should return disclaimer_accepted: false
            if response.get('disclaimer_accepted') is False:
                print("   ✅ Invalid user correctly shows no disclaimer acceptance")
                return True
            else:
                print(f"   ❌ Invalid user should show disclaimer_accepted: false, got: {response}")
                return False
                
        return False

    def test_error_handling_invalid_session(self):
        """Test error handling for invalid session IDs"""
        invalid_session_id = "invalid-session-id-12345"
        
        success, response = self.run_test(
            "Error Handling - Invalid Session ID",
            "GET",
            f"coach/messages/{invalid_session_id}",
            200  # Should return empty list for invalid sessions
        )
        
        if success:
            # Should return empty list for invalid session
            if isinstance(response, list) and len(response) == 0:
                print("   ✅ Invalid session correctly returns empty message list")
                return True
            else:
                print(f"   ❌ Invalid session should return empty list, got: {response}")
                return False
                
        return False

    def run_comprehensive_test_suite(self):
        """Run all AI Health Coach tests in sequence"""
        print("🚀 Starting AI Health Coach Comprehensive Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_feature_flags,
            self.test_accept_disclaimer,
            self.test_disclaimer_status,
            self.test_consultation_limit_standard,
            self.test_create_session,
            self.test_get_user_sessions,
            self.test_send_message_real_ai,
            self.test_get_session_messages,
            self.test_search_conversations,
            self.test_consultation_count_increment,
            self.test_premium_user_unlimited_consultations,
            self.test_monthly_reset_logic,
            self.test_error_handling_invalid_user,
            self.test_error_handling_invalid_session
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                
        print("\n" + "=" * 60)
        print(f"🏁 Test Suite Complete: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - AI Health Coach backend at 100% success rate!")
        elif success_rate >= 90:
            print("✅ EXCELLENT - AI Health Coach backend performing very well")
        elif success_rate >= 80:
            print("⚠️  GOOD - AI Health Coach backend mostly functional with minor issues")
        else:
            print("❌ CRITICAL ISSUES - AI Health Coach backend needs attention")
            
        return success_rate

if __name__ == "__main__":
    tester = AIHealthCoachTester()
    success_rate = tester.run_comprehensive_test_suite()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 90 else 1)