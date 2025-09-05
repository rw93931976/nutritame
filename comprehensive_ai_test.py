#!/usr/bin/env python3
"""
COMPREHENSIVE AI HEALTH COACH TESTING
=====================================

Testing all 9 AI Health Coach endpoints after session creation bug fix
"""

import requests
import json
import uuid
from datetime import datetime

class ComprehensiveAITester:
    def __init__(self, base_url="https://ai-coach-bridge.preview.emergentagent.com"):
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
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}", "SUCCESS")
                try:
                    response_data = response.json()
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

    def setup_demo_user(self):
        """Setup demo user for testing"""
        self.log("Setting up demo user...")
        
        demo_data = {
            "email": f"comprehensive.test.{uuid.uuid4().hex[:8]}@demo.nutritame.com"
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
                self.log(f"✅ Demo user setup complete - ID: {self.demo_user_id}")
                return True
        
        self.log("❌ Failed to setup demo user", "ERROR")
        return False

    def test_all_endpoints(self):
        """Test all 9 AI Health Coach endpoints"""
        if not self.access_token or not self.demo_user_id:
            self.log("❌ No demo user available", "ERROR")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        endpoint_results = {}
        
        # 1. Feature Flags
        self.log("=" * 60)
        self.log("1/9: Testing GET /api/coach/feature-flags")
        success, response = self.run_test(
            "Feature Flags",
            "GET",
            "coach/feature-flags",
            200,
            headers=headers
        )
        endpoint_results['feature-flags'] = success
        if success:
            self.log(f"Config: coach_enabled={response.get('coach_enabled')}, model={response.get('llm_model')}")
        
        # 2. Accept Disclaimer
        self.log("=" * 60)
        self.log("2/9: Testing POST /api/coach/accept-disclaimer")
        success, response = self.run_test(
            "Accept Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data={"user_id": self.demo_user_id},
            headers=headers
        )
        endpoint_results['accept-disclaimer'] = success
        
        # 3. Disclaimer Status
        self.log("=" * 60)
        self.log("3/9: Testing GET /api/coach/disclaimer-status/{user_id}")
        success, response = self.run_test(
            "Disclaimer Status",
            "GET",
            f"coach/disclaimer-status/{self.demo_user_id}",
            200,
            headers=headers
        )
        endpoint_results['disclaimer-status'] = success
        if success:
            accepted = response.get('disclaimer_accepted')
            self.log(f"Disclaimer accepted: {accepted}")
        
        # 4. Consultation Limit
        self.log("=" * 60)
        self.log("4/9: Testing GET /api/coach/consultation-limit/{user_id}")
        success, response = self.run_test(
            "Consultation Limit",
            "GET",
            f"coach/consultation-limit/{self.demo_user_id}",
            200,
            headers=headers
        )
        endpoint_results['consultation-limit'] = success
        if success:
            self.log(f"Limit info: {response.get('current_count')}/{response.get('limit')} used")
        
        # 5. Create Session (THE CRITICAL FIX - user_id in body)
        self.log("=" * 60)
        self.log("5/9: Testing POST /api/coach/sessions (CRITICAL BUG FIX - user_id in body)")
        session_data = {
            "user_id": self.demo_user_id,
            "title": "Comprehensive Test Session"
        }
        success, response = self.run_test(
            "Create Session",
            "POST",
            "coach/sessions",
            200,
            data=session_data,
            headers=headers
        )
        endpoint_results['create-session'] = success
        if success:
            self.session_id = response.get('id')
            self.log(f"✅ Session created: {self.session_id}")
        
        # 6. Get Sessions
        self.log("=" * 60)
        self.log("6/9: Testing GET /api/coach/sessions/{user_id}")
        success, response = self.run_test(
            "Get Sessions",
            "GET",
            f"coach/sessions/{self.demo_user_id}",
            200,
            headers=headers
        )
        endpoint_results['get-sessions'] = success
        if success and isinstance(response, list):
            self.log(f"Found {len(response)} sessions")
        
        # 7. Send Message (Real AI Integration)
        self.log("=" * 60)
        self.log("7/9: Testing POST /api/coach/message (Real AI Integration)")
        if self.session_id:
            message_data = {
                "session_id": self.session_id,
                "message": "Create a Mediterranean breakfast for Type 2 diabetes with no nuts",
                "user_id": self.demo_user_id
            }
            success, response = self.run_test(
                "Send Message",
                "POST",
                "coach/message",
                200,
                data=message_data,
                headers=headers
            )
            endpoint_results['send-message'] = success
            if success:
                ai_response = response.get('ai_response', {})
                if isinstance(ai_response, dict):
                    ai_text = ai_response.get('text', '')
                else:
                    ai_text = str(ai_response)
                self.log(f"✅ AI Response: {ai_text[:100]}...")
        else:
            self.log("❌ No session ID available for message test")
            endpoint_results['send-message'] = False
        
        # 8. Get Messages
        self.log("=" * 60)
        self.log("8/9: Testing GET /api/coach/messages/{session_id}")
        if self.session_id:
            success, response = self.run_test(
                "Get Messages",
                "GET",
                f"coach/messages/{self.session_id}",
                200,
                headers=headers
            )
            endpoint_results['get-messages'] = success
            if success and isinstance(response, list):
                self.log(f"Found {len(response)} messages in conversation")
        else:
            self.log("❌ No session ID available for messages test")
            endpoint_results['get-messages'] = False
        
        # 9. Search Conversations
        self.log("=" * 60)
        self.log("9/9: Testing GET /api/coach/search/{user_id}")
        success, response = self.run_test(
            "Search Conversations",
            "GET",
            f"coach/search/{self.demo_user_id}",
            200,
            headers=headers
        )
        endpoint_results['search'] = success
        if success:
            if isinstance(response, dict) and 'results' in response:
                results = response['results']
                self.log(f"Search returned {len(results)} results")
            elif isinstance(response, list):
                self.log(f"Search returned {len(response)} results")
        
        return endpoint_results

    def run_comprehensive_test(self):
        """Run comprehensive AI Health Coach test"""
        self.log("🤖 COMPREHENSIVE AI HEALTH COACH TESTING")
        self.log("=" * 80)
        self.log("Focus: Verify session creation bug fix and all endpoint functionality")
        self.log("=" * 80)
        
        # Setup
        if not self.setup_demo_user():
            return False
        
        # Test all endpoints
        results = self.test_all_endpoints()
        
        # Summary
        self.log("=" * 80)
        self.log("FINAL RESULTS SUMMARY")
        self.log("=" * 80)
        
        passed_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        for endpoint, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            self.log(f"{status}: {endpoint}")
        
        self.log("=" * 80)
        success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
        self.log(f"SUCCESS RATE: {passed_count}/{total_count} ({success_rate:.1f}%)")
        
        # Critical assessment
        critical_endpoints = ['create-session', 'send-message', 'get-messages']
        critical_passed = sum(1 for ep in critical_endpoints if results.get(ep, False))
        
        if passed_count == total_count:
            self.log("🎉 ALL AI HEALTH COACH ENDPOINTS WORKING PERFECTLY!", "SUCCESS")
        elif critical_passed == len(critical_endpoints):
            self.log("✅ CRITICAL ENDPOINTS WORKING - Session creation bug fix successful!", "SUCCESS")
        else:
            self.log("❌ CRITICAL ISSUES - Session creation or messaging not working", "ERROR")
        
        self.log("=" * 80)
        return critical_passed == len(critical_endpoints)

if __name__ == "__main__":
    tester = ComprehensiveAITester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)