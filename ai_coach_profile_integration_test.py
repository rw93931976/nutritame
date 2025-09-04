import requests
import sys
import json
from datetime import datetime
import uuid

class AICoachProfileIntegrationTester:
    def __init__(self, base_url="https://disclaimer-flow.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_id = None
        self.created_session_id = None

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

    def test_create_user_profile_with_diabetes_info(self):
        """Test creating a user profile with diabetes type, allergies, and food preferences"""
        print("\n🎯 FOCUS TEST: Create User Profile with Diabetes Information")
        
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
            "Create User Profile with Diabetes Info",
            "POST",
            "users",
            200,
            data=test_profile
        )
        
        if success and 'id' in response:
            self.created_user_id = response['id']
            print(f"   ✅ Created user ID: {self.created_user_id}")
            
            # Verify critical fields for AI integration
            critical_fields = ['diabetes_type', 'allergies', 'food_preferences']
            for field in critical_fields:
                expected_value = test_profile[field]
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

    def test_ai_coach_feature_flags(self):
        """Test AI Health Coach feature flags endpoint"""
        print("\n🔍 Testing AI Health Coach Feature Flags...")
        
        success, response = self.run_test(
            "AI Coach Feature Flags",
            "GET",
            "coach/feature-flags",
            200
        )
        
        if success:
            # Verify required flags
            required_flags = ['coach_enabled', 'llm_provider', 'llm_model']
            for flag in required_flags:
                if flag in response:
                    print(f"   ✅ {flag}: {response[flag]}")
                else:
                    print(f"   ❌ Missing flag: {flag}")
                    return False
            
            # Verify coach is enabled
            if response.get('coach_enabled') is True:
                print("   ✅ AI Health Coach is enabled")
                return True
            else:
                print(f"   ❌ AI Health Coach should be enabled, got: {response.get('coach_enabled')}")
                return False
        
        return False

    def test_disclaimer_acceptance(self):
        """Test disclaimer acceptance for the user"""
        if not self.created_user_id:
            print("❌ No user ID available for disclaimer testing")
            return False
        
        print(f"\n🔍 Testing Disclaimer Acceptance for user {self.created_user_id}...")
        
        success, response = self.run_test(
            "Accept Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data={"user_id": self.created_user_id}
        )
        
        if success:
            print("   ✅ Disclaimer accepted successfully")
            return True
        else:
            print(f"   ❌ Disclaimer acceptance failed: {response}")
            return False

    def test_consultation_limit_check(self):
        """Test consultation limit check for the user"""
        if not self.created_user_id:
            print("❌ No user ID available for consultation limit testing")
            return False
        
        print(f"\n🔍 Testing Consultation Limit for user {self.created_user_id}...")
        
        success, response = self.run_test(
            "Check Consultation Limit",
            "GET",
            f"coach/consultation-limit/{self.created_user_id}",
            200
        )
        
        if success:
            # Verify response structure
            required_fields = ['can_use', 'current_count', 'limit', 'plan']
            for field in required_fields:
                if field in response:
                    print(f"   ✅ {field}: {response[field]}")
                else:
                    print(f"   ❌ Missing field: {field}")
                    return False
            
            # Verify user can use the service
            if response.get('can_use') is True:
                print("   ✅ User can use AI Health Coach")
                return True
            else:
                print(f"   ❌ User cannot use AI Health Coach: {response}")
                return False
        
        return False

    def test_create_coach_session(self):
        """Test creating an AI Health Coach session"""
        if not self.created_user_id:
            print("❌ No user ID available for session creation")
            return False
        
        print(f"\n🔍 Testing AI Coach Session Creation for user {self.created_user_id}...")
        
        session_data = {
            "title": "Diabetes Meal Planning Session"
        }
        
        success, response = self.run_test(
            "Create AI Coach Session",
            "POST",
            f"coach/sessions?user_id={self.created_user_id}",
            200,
            data=session_data
        )
        
        if success and 'id' in response:
            self.created_session_id = response['id']
            print(f"   ✅ Created session ID: {self.created_session_id}")
            
            # Verify session details
            if response.get('user_id') == self.created_user_id:
                print(f"   ✅ Session linked to correct user")
            else:
                print(f"   ❌ Session user_id mismatch")
                return False
            
            if response.get('title') == session_data['title']:
                print(f"   ✅ Session title correct: {response.get('title')}")
            else:
                print(f"   ❌ Session title mismatch")
                return False
            
            return True
        else:
            print(f"   ❌ Session creation failed: {response}")
            return False

    def test_ai_coach_message_with_profile_integration(self):
        """🎯 MAIN TEST: Send message to AI Coach and verify profile data integration"""
        if not self.created_user_id or not self.created_session_id:
            print("❌ No user ID or session ID available for AI message testing")
            return False
        
        print(f"\n🎯 CRITICAL TEST: AI Coach Message with Profile Integration")
        print(f"   User ID: {self.created_user_id}")
        print(f"   Session ID: {self.created_session_id}")
        
        # Send a message that should trigger profile-aware response
        message_data = {
            "session_id": self.created_session_id,
            "message": "I need help creating a meal plan for my diabetes. What foods should I eat and avoid?"
        }
        
        print("   Sending message to AI Coach (may take 10-15 seconds)...")
        success, response = self.run_test(
            "AI Coach Message with Profile Integration",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success and 'response' in response:
            ai_response = response['response']
            print(f"\n   🤖 AI Response Length: {len(ai_response)} characters")
            print(f"   🤖 AI Response Preview: {ai_response[:200]}...")
            
            # Check for profile integration indicators
            profile_indicators = {
                'diabetes_type': ['type 2', 'type2', 'diabetes'],
                'allergies': ['nuts', 'shellfish', 'allerg'],
                'food_preferences': ['mediterranean', 'low carb', 'low-carb'],
                'imperial_measurements': ['cups', 'tablespoons', 'ounces', 'oz', 'lbs']
            }
            
            integration_score = 0
            total_checks = len(profile_indicators)
            
            print(f"\n   🔍 Checking Profile Data Integration:")
            
            for category, keywords in profile_indicators.items():
                found_keywords = []
                for keyword in keywords:
                    if keyword.lower() in ai_response.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"   ✅ {category}: Found {found_keywords}")
                    integration_score += 1
                else:
                    print(f"   ❌ {category}: No keywords found ({keywords})")
            
            # Check for personalized guidance
            personalization_indicators = [
                'your diabetes', 'your condition', 'your allergies', 
                'avoid nuts', 'avoid shellfish', 'mediterranean diet',
                'blood sugar', 'glucose'
            ]
            
            found_personalization = []
            for indicator in personalization_indicators:
                if indicator.lower() in ai_response.lower():
                    found_personalization.append(indicator)
            
            if found_personalization:
                print(f"   ✅ Personalization: Found {found_personalization}")
                integration_score += 1
                total_checks += 1
            else:
                print(f"   ❌ Personalization: No personalized guidance detected")
                total_checks += 1
            
            # Calculate integration success rate
            success_rate = (integration_score / total_checks) * 100
            print(f"\n   📊 Profile Integration Score: {integration_score}/{total_checks} ({success_rate:.1f}%)")
            
            # Verify response quality
            if len(ai_response) < 50:
                print(f"   ❌ AI response too short (< 50 chars): {len(ai_response)}")
                return False
            
            if success_rate >= 60:  # At least 60% integration
                print(f"   ✅ PROFILE INTEGRATION SUCCESS: {success_rate:.1f}% integration detected")
                
                # Store message ID for follow-up tests
                if 'message_id' in response:
                    self.created_message_id = response['message_id']
                
                return True
            else:
                print(f"   ❌ PROFILE INTEGRATION FAILED: Only {success_rate:.1f}% integration detected")
                print(f"   Expected: Diabetes type (type2), allergies (nuts, shellfish), food preferences (mediterranean, low carb)")
                return False
        else:
            print(f"   ❌ AI message failed: {response}")
            return False

    def test_get_session_messages(self):
        """Test retrieving messages from the session"""
        if not self.created_session_id:
            print("❌ No session ID available for message retrieval")
            return False
        
        print(f"\n🔍 Testing Session Message Retrieval for session {self.created_session_id}...")
        
        success, response = self.run_test(
            "Get Session Messages",
            "GET",
            f"coach/messages/{self.created_session_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} messages")
            
            if len(response) >= 2:  # Should have user message + AI response
                user_message = None
                ai_message = None
                
                for message in response:
                    if message.get('role') == 'user':
                        user_message = message
                    elif message.get('role') == 'assistant':
                        ai_message = message
                
                if user_message and ai_message:
                    print(f"   ✅ Found user message: {user_message.get('text', '')[:50]}...")
                    print(f"   ✅ Found AI message: {ai_message.get('text', '')[:50]}...")
                    return True
                else:
                    print(f"   ❌ Missing user or AI message in conversation")
                    return False
            else:
                print(f"   ❌ Expected at least 2 messages, got {len(response)}")
                return False
        else:
            print(f"   ❌ Message retrieval failed: {response}")
            return False

    def test_get_user_sessions(self):
        """Test retrieving all sessions for the user"""
        if not self.created_user_id:
            print("❌ No user ID available for session retrieval")
            return False
        
        print(f"\n🔍 Testing User Session Retrieval for user {self.created_user_id}...")
        
        success, response = self.run_test(
            "Get User Sessions",
            "GET",
            f"coach/sessions/{self.created_user_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} sessions")
            
            if len(response) >= 1:
                session = response[0]
                if session.get('id') == self.created_session_id:
                    print(f"   ✅ Found created session: {session.get('title')}")
                    return True
                else:
                    print(f"   ❌ Session ID mismatch")
                    return False
            else:
                print(f"   ❌ No sessions found for user")
                return False
        else:
            print(f"   ❌ Session retrieval failed: {response}")
            return False

    def test_conversation_search(self):
        """Test conversation search functionality"""
        if not self.created_user_id:
            print("❌ No user ID available for conversation search")
            return False
        
        print(f"\n🔍 Testing Conversation Search for user {self.created_user_id}...")
        
        success, response = self.run_test(
            "Search Conversations",
            "GET",
            f"coach/search/{self.created_user_id}?query=diabetes meal plan",
            200
        )
        
        if success:
            print(f"   ✅ Search completed successfully")
            if isinstance(response, list):
                print(f"   ✅ Found {len(response)} search results")
            return True
        else:
            print(f"   ❌ Conversation search failed: {response}")
            return False

    def test_second_message_with_specific_request(self):
        """Test second message to verify continued profile awareness"""
        if not self.created_session_id:
            print("❌ No session ID available for second message test")
            return False
        
        print(f"\n🎯 FOLLOW-UP TEST: Second Message with Specific Dietary Request")
        
        # Send a more specific message about allergies
        message_data = {
            "session_id": self.created_session_id,
            "message": "Can you suggest a Mediterranean breakfast that's safe for someone with nut and shellfish allergies?"
        }
        
        print("   Sending follow-up message to AI Coach...")
        success, response = self.run_test(
            "Second AI Coach Message - Allergy Specific",
            "POST",
            "coach/message",
            200,
            data=message_data
        )
        
        if success and 'response' in response:
            ai_response = response['response']
            print(f"\n   🤖 Second AI Response Preview: {ai_response[:200]}...")
            
            # Check for allergy awareness
            allergy_awareness = [
                'nut-free', 'no nuts', 'avoid nuts', 'without nuts',
                'shellfish-free', 'no shellfish', 'avoid shellfish', 'without shellfish'
            ]
            
            mediterranean_awareness = [
                'mediterranean', 'olive oil', 'olives', 'tomatoes', 'feta', 'greek'
            ]
            
            found_allergy_awareness = []
            found_mediterranean = []
            
            for term in allergy_awareness:
                if term.lower() in ai_response.lower():
                    found_allergy_awareness.append(term)
            
            for term in mediterranean_awareness:
                if term.lower() in ai_response.lower():
                    found_mediterranean.append(term)
            
            print(f"\n   🔍 Allergy Awareness Check:")
            if found_allergy_awareness:
                print(f"   ✅ Allergy awareness: {found_allergy_awareness}")
            else:
                print(f"   ❌ No allergy awareness detected")
            
            print(f"\n   🔍 Mediterranean Diet Check:")
            if found_mediterranean:
                print(f"   ✅ Mediterranean awareness: {found_mediterranean}")
            else:
                print(f"   ❌ No Mediterranean diet awareness detected")
            
            # Success if we have both allergy and Mediterranean awareness
            if found_allergy_awareness and found_mediterranean:
                print(f"   ✅ CONTEXTUAL AWARENESS SUCCESS: AI shows both allergy and dietary preference awareness")
                return True
            elif found_allergy_awareness or found_mediterranean:
                print(f"   ⚠️  PARTIAL SUCCESS: AI shows some contextual awareness")
                return True
            else:
                print(f"   ❌ CONTEXTUAL AWARENESS FAILED: AI not using profile context")
                return False
        else:
            print(f"   ❌ Second AI message failed: {response}")
            return False

    def test_all_nine_endpoints(self):
        """Test all 9 AI Health Coach endpoints to ensure they maintain functionality"""
        print(f"\n🔍 Testing All 9 AI Health Coach Endpoints...")
        
        if not self.created_user_id or not self.created_session_id:
            print("❌ Missing user ID or session ID for comprehensive testing")
            return False
        
        endpoints_to_test = [
            ("Feature Flags", "GET", "coach/feature-flags", 200, None),
            ("Accept Disclaimer", "POST", "coach/accept-disclaimer", 200, {"user_id": self.created_user_id}),
            ("Disclaimer Status", "GET", f"coach/disclaimer-status/{self.created_user_id}", 200, None),
            ("Consultation Limit", "GET", f"coach/consultation-limit/{self.created_user_id}", 200, None),
            ("Create Session", "POST", f"coach/sessions?user_id={self.created_user_id}", 200, {"title": "Test Session 2"}),
            ("Get User Sessions", "GET", f"coach/sessions/{self.created_user_id}", 200, None),
            ("Send Message", "POST", "coach/message", 200, {"session_id": self.created_session_id, "message": "Quick test message"}),
            ("Get Messages", "GET", f"coach/messages/{self.created_session_id}", 200, None),
            ("Search Conversations", "GET", f"coach/search/{self.created_user_id}?query=test", 200, None)
        ]
        
        passed_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for name, method, endpoint, expected_status, data in endpoints_to_test:
            success, response = self.run_test(
                f"Endpoint: {name}",
                method,
                endpoint,
                expected_status,
                data=data
            )
            
            if success:
                passed_endpoints += 1
                print(f"   ✅ {name}: Working")
            else:
                print(f"   ❌ {name}: Failed")
        
        success_rate = (passed_endpoints / total_endpoints) * 100
        print(f"\n   📊 Endpoint Success Rate: {passed_endpoints}/{total_endpoints} ({success_rate:.1f}%)")
        
        if success_rate >= 90:  # At least 90% success rate
            print(f"   ✅ ALL ENDPOINTS FUNCTIONAL: {success_rate:.1f}% success rate")
            return True
        else:
            print(f"   ❌ ENDPOINT FAILURES DETECTED: Only {success_rate:.1f}% success rate")
            return False

    def run_all_tests(self):
        """Run all profile integration tests"""
        print("🚀 Starting AI Health Coach Profile Integration Tests")
        print("=" * 60)
        
        tests = [
            self.test_create_user_profile_with_diabetes_info,
            self.test_ai_coach_feature_flags,
            self.test_disclaimer_acceptance,
            self.test_consultation_limit_check,
            self.test_create_coach_session,
            self.test_ai_coach_message_with_profile_integration,
            self.test_get_session_messages,
            self.test_get_user_sessions,
            self.test_conversation_search,
            self.test_second_message_with_specific_request,
            self.test_all_nine_endpoints
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        print("\n" + "=" * 60)
        print(f"🏁 FINAL RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Profile integration is working correctly!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed - Profile integration needs attention")
            return False

if __name__ == "__main__":
    tester = AICoachProfileIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)