#!/usr/bin/env python3
"""
CRITICAL SESSION CREATION BUG FIX TESTING
==========================================

Focus: Verify that the critical bug fix for session creation is now working correctly.

Previous Issue: The API was expecting user_id as a query parameter instead of in the request body, causing 422 errors.

Fix Applied: Updated CoachSessionCreate model to include user_id field and modified create_coach_session endpoint to extract user_id from request body.

Critical Test:
- Create demo user and get Bearer token
- Test POST /api/coach/sessions with { "user_id": "test-uuid", "title": "Test Session" } in request body
- Verify 200 response with valid session_id (NOT 422 error)
- Test complete message flow with the created session
"""

import requests
import json
import uuid
from datetime import datetime

class SessionCreationTester:
    def __init__(self, base_url="https://coach-consent.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_user_id = None
        self.access_token = None
        self.session_id = None

    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        self.log(f"Testing {name}...")
        self.log(f"URL: {url}")
        
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
                self.log(f"✅ PASSED - Status: {response.status_code}", "SUCCESS")
                try:
                    response_data = response.json()
                    self.log(f"Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, response.text
            else:
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"Error: {error_data}", "ERROR")
                except:
                    self.log(f"Error: {response.text}", "ERROR")
                return False, {}

        except Exception as e:
            self.log(f"❌ FAILED - Exception: {str(e)}", "ERROR")
            return False, {}

    def test_create_demo_user(self):
        """Step 1: Create demo user and get Bearer token"""
        self.log("=" * 60)
        self.log("STEP 1: Creating demo user and getting Bearer token")
        self.log("=" * 60)
        
        demo_data = {
            "email": f"session.test.{uuid.uuid4().hex[:8]}@demo.nutritame.com"
        }
        
        success, response = self.run_test(
            "Create Demo User",
            "POST",
            "demo/access",
            200,
            data=demo_data
        )
        
        if success:
            self.access_token = response.get('access_token')
            user = response.get('user', {})
            self.demo_user_id = user.get('id')
            
            if self.access_token and self.demo_user_id:
                self.log(f"✅ Demo user created successfully")
                self.log(f"User ID: {self.demo_user_id}")
                self.log(f"Access token: {self.access_token[:20]}...")
                return True
            else:
                self.log("❌ Missing access token or user ID in response", "ERROR")
                return False
        else:
            self.log("❌ Failed to create demo user", "ERROR")
            return False

    def test_session_creation_with_body_parameters(self):
        """Step 2: Test POST /api/coach/sessions with user_id in request body (THE CRITICAL FIX)"""
        self.log("=" * 60)
        self.log("STEP 2: Testing session creation with user_id in request body")
        self.log("=" * 60)
        
        if not self.access_token or not self.demo_user_id:
            self.log("❌ No access token or user ID available", "ERROR")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        # First accept disclaimer (required for session creation)
        self.log("📋 Step 2a: Accepting disclaimer (required for session creation)")
        disclaimer_success, _ = self.run_test(
            "Accept Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data={"user_id": self.demo_user_id},
            headers=headers
        )
        
        if not disclaimer_success:
            self.log("❌ Failed to accept disclaimer", "ERROR")
            return False
        
        # THE CRITICAL TEST: user_id in request body, NOT query parameter
        session_data = {
            "user_id": self.demo_user_id,
            "title": "Critical Bug Fix Test Session"
        }
        
        self.log("🎯 CRITICAL TEST: POST /api/coach/sessions with user_id in request body")
        self.log(f"Request body: {json.dumps(session_data, indent=2)}")
        
        success, response = self.run_test(
            "Session Creation with Body Parameters",
            "POST",
            "coach/sessions",
            200,  # Should return 200, NOT 422
            data=session_data,
            headers=headers
        )
        
        if success:
            self.session_id = response.get('id')
            if self.session_id:
                self.log(f"✅ SUCCESS: Session created with ID: {self.session_id}")
                self.log("✅ NO 422 ERROR: user_id in request body is working correctly")
                return True
            else:
                self.log("❌ Session created but no session ID returned", "ERROR")
                return False
        else:
            self.log("❌ CRITICAL BUG: Session creation failed - likely still expecting query parameter", "ERROR")
            return False

    def test_old_query_parameter_method(self):
        """Step 3: Test the old query parameter method (should still work for backward compatibility)"""
        self.log("=" * 60)
        self.log("STEP 3: Testing old query parameter method (backward compatibility)")
        self.log("=" * 60)
        
        if not self.access_token or not self.demo_user_id:
            self.log("❌ No access token or user ID available", "ERROR")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        # Test old method with query parameter
        session_data = {
            "title": "Backward Compatibility Test Session"
        }
        
        self.log("🔄 Testing backward compatibility: POST /api/coach/sessions?user_id=...")
        
        success, response = self.run_test(
            "Session Creation with Query Parameter",
            "POST",
            f"coach/sessions?user_id={self.demo_user_id}",
            200,
            data=session_data,
            headers=headers
        )
        
        if success:
            session_id = response.get('id')
            if session_id:
                self.log(f"✅ Backward compatibility maintained: Session ID: {session_id}")
                return True
            else:
                self.log("❌ Session created but no session ID returned", "ERROR")
                return False
        else:
            self.log("⚠️  Old query parameter method no longer works (acceptable if intentionally removed)")
            return True  # This is acceptable - we don't require backward compatibility

    def test_complete_message_flow(self):
        """Step 4: Test complete message flow with the created session"""
        self.log("=" * 60)
        self.log("STEP 4: Testing complete message flow with created session")
        self.log("=" * 60)
        
        if not self.access_token or not self.demo_user_id or not self.session_id:
            self.log("❌ Missing required data for message flow test", "ERROR")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        # Send a message to the session (disclaimer already accepted in step 2)
        self.log("💬 Sending message to session")
        message_data = {
            "session_id": self.session_id,
            "message": "Create a simple meal plan for Type 2 diabetes",
            "user_id": self.demo_user_id
        }
        
        self.log(f"Message data: {json.dumps(message_data, indent=2)}")
        
        success, response = self.run_test(
            "Send Message to Session",
            "POST",
            "coach/message",
            200,
            data=message_data,
            headers=headers
        )
        
        if success:
            # Check if we got an AI response
            if 'response' in response or 'ai_response' in response:
                ai_response = response.get('response') or response.get('ai_response', '')
                ai_preview = str(ai_response)[:100] if ai_response else "No response"
                self.log(f"✅ AI Response received: {ai_preview}...")
                
                # Verify message was saved
                self.log("📚 Verifying message history")
                history_success, history_response = self.run_test(
                    "Get Message History",
                    "GET",
                    f"coach/messages/{self.session_id}",
                    200,
                    headers=headers
                )
                
                if history_success and isinstance(history_response, list):
                    self.log(f"✅ Message history retrieved: {len(history_response)} messages")
                    return True
                else:
                    self.log("❌ Failed to retrieve message history", "ERROR")
                    return False
            else:
                self.log("❌ No AI response received", "ERROR")
                return False
        else:
            self.log("❌ Failed to send message", "ERROR")
            return False

    def test_no_regressions(self):
        """Step 5: Verify no regressions in other functionality"""
        self.log("=" * 60)
        self.log("STEP 5: Testing for regressions in other functionality")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        # Test feature flags
        self.log("🚩 Testing feature flags")
        flags_success, flags_response = self.run_test(
            "Get Feature Flags",
            "GET",
            "coach/feature-flags",
            200,
            headers=headers
        )
        
        if not flags_success:
            self.log("❌ Feature flags endpoint failed", "ERROR")
            return False
        
        # Test disclaimer status
        self.log("📋 Testing disclaimer status")
        disclaimer_success, _ = self.run_test(
            "Get Disclaimer Status",
            "GET",
            f"coach/disclaimer-status/{self.demo_user_id}",
            200,
            headers=headers
        )
        
        if not disclaimer_success:
            self.log("❌ Disclaimer status endpoint failed", "ERROR")
            return False
        
        # Test consultation limits
        self.log("📊 Testing consultation limits")
        limits_success, _ = self.run_test(
            "Get Consultation Limits",
            "GET",
            f"coach/consultation-limit/{self.demo_user_id}",
            200,
            headers=headers
        )
        
        if not limits_success:
            self.log("❌ Consultation limits endpoint failed", "ERROR")
            return False
        
        self.log("✅ No regressions detected in other functionality")
        return True

    def run_all_tests(self):
        """Run all critical session creation tests"""
        self.log("🎯 CRITICAL SESSION CREATION BUG FIX TESTING")
        self.log("=" * 80)
        self.log("Testing the fix for user_id in request body vs query parameter")
        self.log("=" * 80)
        
        all_passed = True
        
        # Step 1: Create demo user
        if not self.test_create_demo_user():
            all_passed = False
            self.log("❌ CRITICAL: Cannot proceed without demo user", "ERROR")
            return False
        
        # Step 2: Test the critical fix
        if not self.test_session_creation_with_body_parameters():
            all_passed = False
            self.log("❌ CRITICAL: Session creation with body parameters failed", "ERROR")
        
        # Step 3: Test backward compatibility (optional)
        self.test_old_query_parameter_method()
        
        # Step 4: Test complete message flow
        if not self.test_complete_message_flow():
            all_passed = False
            self.log("❌ CRITICAL: Complete message flow failed", "ERROR")
        
        # Step 5: Test for regressions
        if not self.test_no_regressions():
            all_passed = False
            self.log("❌ CRITICAL: Regressions detected", "ERROR")
        
        # Final summary
        self.log("=" * 80)
        if all_passed:
            self.log("🎉 SUCCESS: All critical session creation tests PASSED", "SUCCESS")
            self.log("✅ POST /api/coach/sessions with user_id in body returns 200")
            self.log("✅ Session creation returns valid session_id")
            self.log("✅ No 422 'User ID required' errors")
            self.log("✅ Complete message flow works")
            self.log("✅ No regressions in other functionality")
        else:
            self.log("❌ FAILURE: Critical session creation tests FAILED", "ERROR")
            self.log("The bug fix may not be working correctly")
        
        self.log(f"Tests run: {self.tests_run}, Passed: {self.tests_passed}")
        self.log("=" * 80)
        
        return all_passed

if __name__ == "__main__":
    tester = SessionCreationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)