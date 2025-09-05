#!/usr/bin/env python3
"""
CORS Configuration Fix Validation Test Suite
============================================

This test suite validates the critical CORS configuration fix for the AI Health Coach backend
to resolve preflight blocking issues for frontend requests from:
https://coach-consent.preview.emergentagent.com

PRIMARY OBJECTIVES:
1. CORS Validation: Verify CORS preflight (OPTIONS) and actual POST requests work correctly
2. API Contract Verification: Confirm POST endpoints accept {"user_id": "uuid"} in request body
3. No Regressions: Ensure all 9 AI Health Coach endpoints still work at 100% success rate

CORS CONFIGURATION CHANGES TESTED:
- CORS_ORIGINS: "https://coach-consent.preview.emergentagent.com,https://localhost:3000"
- CORSMiddleware: allow_credentials=False, allow_methods=["GET","POST","OPTIONS"], 
  allow_headers=["Content-Type","Authorization"], max_age=86400
"""

import requests
import json
import uuid
from datetime import datetime

class CORSValidationTester:
    def __init__(self, base_url="https://ai-coach-bridge.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.frontend_origin = "https://coach-consent.preview.emergentagent.com"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_id = None
        self.access_token = None
        self.session_id = None
        
        print(f"🎯 CORS CONFIGURATION FIX VALIDATION")
        print(f"Backend URL: {self.base_url}")
        print(f"Frontend Origin: {self.frontend_origin}")
        print("=" * 80)

    def run_cors_test(self, name, method, endpoint, expected_status, data=None, test_preflight=True):
        """Run a CORS test with preflight validation"""
        url = f"{self.api_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        success = True
        
        # Test CORS preflight (OPTIONS) if requested
        if test_preflight and method in ['POST', 'PUT']:
            print(f"   Testing CORS preflight (OPTIONS)...")
            
            preflight_headers = {
                'Origin': self.frontend_origin,
                'Access-Control-Request-Method': method,
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            try:
                preflight_response = requests.options(url, headers=preflight_headers, timeout=30)
                
                if preflight_response.status_code == 200:
                    print(f"   ✅ Preflight: Status 200 OK")
                    
                    # Check required CORS headers
                    cors_headers = {
                        'Access-Control-Allow-Origin': self.frontend_origin,
                        'Access-Control-Allow-Methods': method,
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                        'Access-Control-Max-Age': '86400'
                    }
                    
                    for header, expected_value in cors_headers.items():
                        actual_value = preflight_response.headers.get(header)
                        if header == 'Access-Control-Allow-Methods':
                            # Check if method is in the allowed methods
                            if actual_value and method in actual_value:
                                print(f"   ✅ {header}: {method} allowed in {actual_value}")
                            else:
                                print(f"   ❌ {header}: {method} not in {actual_value}")
                                success = False
                        elif header == 'Access-Control-Allow-Headers':
                            # Check if required headers are allowed
                            if actual_value and 'Content-Type' in actual_value and 'Authorization' in actual_value:
                                print(f"   ✅ {header}: Required headers allowed")
                            else:
                                print(f"   ❌ {header}: Missing required headers in {actual_value}")
                                success = False
                        else:
                            if actual_value == expected_value:
                                print(f"   ✅ {header}: {actual_value}")
                            else:
                                print(f"   ❌ {header}: Expected {expected_value}, got {actual_value}")
                                success = False
                else:
                    print(f"   ❌ Preflight failed: Status {preflight_response.status_code}")
                    success = False
                    
            except Exception as e:
                print(f"   ❌ Preflight error: {str(e)}")
                success = False
        
        # Test actual request
        print(f"   Testing actual {method} request...")
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': self.frontend_origin
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'OPTIONS':
                response = requests.options(url, headers=headers, timeout=30)

            if response.status_code == expected_status:
                print(f"   ✅ Request: Status {response.status_code}")
                
                # Check CORS headers in response
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                if cors_origin == self.frontend_origin:
                    print(f"   ✅ CORS Origin: {cors_origin}")
                else:
                    print(f"   ❌ CORS Origin: Expected {self.frontend_origin}, got {cors_origin}")
                    success = False
                
                try:
                    response_data = response.json()
                    if success:
                        self.tests_passed += 1
                    return success, response_data
                except:
                    if success:
                        self.tests_passed += 1
                    return success, response.text
            else:
                print(f"   ❌ Request failed: Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"   ❌ Request error: {str(e)}")
            return False, {}

    def test_cors_preflight_disclaimer_endpoint(self):
        """Test CORS preflight for POST /api/coach/accept-disclaimer"""
        print("\n🎯 TESTING CORS PREFLIGHT FOR DISCLAIMER ENDPOINT")
        
        # Test OPTIONS request specifically
        url = f"{self.api_url}/coach/accept-disclaimer"
        
        preflight_headers = {
            'Origin': self.frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        try:
            response = requests.options(url, headers=preflight_headers, timeout=30)
            
            print(f"   URL: {url}")
            print(f"   Origin: {self.frontend_origin}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Preflight successful (200 OK)")
                
                # Check all required CORS headers
                required_headers = {
                    'Access-Control-Allow-Origin': self.frontend_origin,
                    'Access-Control-Allow-Methods': 'POST',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Max-Age': '86400'
                }
                
                all_headers_correct = True
                for header, expected in required_headers.items():
                    actual = response.headers.get(header)
                    if header == 'Access-Control-Allow-Methods':
                        if actual and 'POST' in actual:
                            print(f"   ✅ {header}: POST allowed")
                        else:
                            print(f"   ❌ {header}: POST not allowed in {actual}")
                            all_headers_correct = False
                    elif header == 'Access-Control-Allow-Headers':
                        if actual and 'Content-Type' in actual and 'Authorization' in actual:
                            print(f"   ✅ {header}: Required headers allowed")
                        else:
                            print(f"   ❌ {header}: Missing required headers")
                            all_headers_correct = False
                    else:
                        if actual == expected:
                            print(f"   ✅ {header}: {actual}")
                        else:
                            print(f"   ❌ {header}: Expected {expected}, got {actual}")
                            all_headers_correct = False
                
                return all_headers_correct
            else:
                print(f"   ❌ Preflight failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Preflight error: {str(e)}")
            return False

    def test_cors_preflight_sessions_endpoint(self):
        """Test CORS preflight for POST /api/coach/sessions"""
        print("\n🎯 TESTING CORS PREFLIGHT FOR SESSIONS ENDPOINT")
        
        url = f"{self.api_url}/coach/sessions"
        
        preflight_headers = {
            'Origin': self.frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        try:
            response = requests.options(url, headers=preflight_headers, timeout=30)
            
            print(f"   URL: {url}")
            print(f"   Origin: {self.frontend_origin}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Preflight successful (200 OK)")
                
                # Verify CORS headers
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                cors_methods = response.headers.get('Access-Control-Allow-Methods')
                cors_headers = response.headers.get('Access-Control-Allow-Headers')
                cors_max_age = response.headers.get('Access-Control-Max-Age')
                
                success = True
                
                if cors_origin == self.frontend_origin:
                    print(f"   ✅ Access-Control-Allow-Origin: {cors_origin}")
                else:
                    print(f"   ❌ Access-Control-Allow-Origin: Expected {self.frontend_origin}, got {cors_origin}")
                    success = False
                
                if cors_methods and 'POST' in cors_methods:
                    print(f"   ✅ Access-Control-Allow-Methods: POST allowed")
                else:
                    print(f"   ❌ Access-Control-Allow-Methods: POST not in {cors_methods}")
                    success = False
                
                if cors_headers and 'Content-Type' in cors_headers and 'Authorization' in cors_headers:
                    print(f"   ✅ Access-Control-Allow-Headers: Required headers allowed")
                else:
                    print(f"   ❌ Access-Control-Allow-Headers: Missing required headers in {cors_headers}")
                    success = False
                
                if cors_max_age == '86400':
                    print(f"   ✅ Access-Control-Max-Age: {cors_max_age}")
                else:
                    print(f"   ❌ Access-Control-Max-Age: Expected 86400, got {cors_max_age}")
                    success = False
                
                return success
            else:
                print(f"   ❌ Preflight failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Preflight error: {str(e)}")
            return False

    def test_api_contract_disclaimer_endpoint(self):
        """Test POST /api/coach/accept-disclaimer accepts user_id in request body"""
        print("\n🎯 TESTING API CONTRACT - DISCLAIMER ENDPOINT")
        
        # Create a test user ID
        test_user_id = str(uuid.uuid4())
        
        # Test data with user_id in request body
        test_data = {
            "user_id": test_user_id
        }
        
        success, response = self.run_cors_test(
            "POST /api/coach/accept-disclaimer with user_id in body",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=test_data,
            test_preflight=True
        )
        
        if success:
            print(f"   ✅ API accepts user_id in request body")
            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
            
            # Verify response structure
            if 'message' in response and response.get('accepted') is True:
                print(f"   ✅ Response structure correct")
                return True
            else:
                print(f"   ❌ Unexpected response structure: {response}")
                return False
        else:
            print(f"   ❌ API contract test failed")
            return False

    def test_api_contract_sessions_endpoint(self):
        """Test POST /api/coach/sessions accepts user_id in request body"""
        print("\n🎯 TESTING API CONTRACT - SESSIONS ENDPOINT")
        
        # Create a test user ID
        test_user_id = str(uuid.uuid4())
        
        # First accept disclaimer for this user
        disclaimer_data = {"user_id": test_user_id}
        disclaimer_success, _ = self.run_cors_test(
            "Accept disclaimer for sessions test",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=disclaimer_data,
            test_preflight=False
        )
        
        if not disclaimer_success:
            print(f"   ❌ Failed to accept disclaimer for sessions test")
            return False
        
        # Test sessions endpoint with user_id in request body
        sessions_data = {
            "user_id": test_user_id,
            "title": "Test Session"
        }
        
        success, response = self.run_cors_test(
            "POST /api/coach/sessions with user_id in body",
            "POST",
            "coach/sessions",
            200,
            data=sessions_data,
            test_preflight=True
        )
        
        if success:
            print(f"   ✅ API accepts user_id in request body")
            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
            
            # Verify response structure
            if 'id' in response and response.get('user_id') == test_user_id:
                print(f"   ✅ Response structure correct")
                self.session_id = response.get('id')
                return True
            else:
                print(f"   ❌ Unexpected response structure: {response}")
                return False
        else:
            print(f"   ❌ API contract test failed")
            return False

    def test_all_9_ai_coach_endpoints(self):
        """Test all 9 AI Health Coach endpoints for regression"""
        print("\n🎯 TESTING ALL 9 AI HEALTH COACH ENDPOINTS (REGRESSION TEST)")
        
        # Create test user and accept disclaimer
        test_user_id = str(uuid.uuid4())
        
        # Create comprehensive user profile for AI integration
        profile_data = {
            "diabetes_type": "type2",
            "age": 45,
            "gender": "female",
            "activity_level": "moderate",
            "health_goals": ["blood_sugar_control", "weight_loss"],
            "food_preferences": ["mediterranean", "low_carb"],
            "cultural_background": "Mediterranean",
            "allergies": ["nuts", "shellfish"],
            "dislikes": ["liver"],
            "cooking_skill": "intermediate"
        }
        
        # Create user profile
        profile_success, profile_response = self.run_cors_test(
            "Create user profile for AI testing",
            "POST",
            "users",
            200,
            data=profile_data,
            test_preflight=False
        )
        
        if profile_success and 'id' in profile_response:
            test_user_id = profile_response['id']
            print(f"   ✅ Created test user: {test_user_id}")
        else:
            print(f"   ❌ Failed to create test user profile")
            return False
        
        endpoints_tested = 0
        endpoints_passed = 0
        
        # 1. GET /api/coach/feature-flags
        print(f"\n   1️⃣ Testing GET /api/coach/feature-flags")
        success, response = self.run_cors_test(
            "Feature Flags",
            "GET",
            "coach/feature-flags",
            200,
            test_preflight=False
        )
        endpoints_tested += 1
        if success and response.get('coach_enabled') is True:
            print(f"      ✅ Feature flags working (coach_enabled: {response.get('coach_enabled')})")
            endpoints_passed += 1
        else:
            print(f"      ❌ Feature flags failed")
        
        # 2. POST /api/coach/accept-disclaimer
        print(f"\n   2️⃣ Testing POST /api/coach/accept-disclaimer")
        disclaimer_data = {"user_id": test_user_id}
        success, response = self.run_cors_test(
            "Accept Disclaimer",
            "POST",
            "coach/accept-disclaimer",
            200,
            data=disclaimer_data,
            test_preflight=True
        )
        endpoints_tested += 1
        if success and response.get('accepted') is True:
            print(f"      ✅ Disclaimer acceptance working")
            endpoints_passed += 1
        else:
            print(f"      ❌ Disclaimer acceptance failed")
        
        # 3. GET /api/coach/disclaimer-status/{user_id}
        print(f"\n   3️⃣ Testing GET /api/coach/disclaimer-status/{test_user_id}")
        success, response = self.run_cors_test(
            "Disclaimer Status",
            "GET",
            f"coach/disclaimer-status/{test_user_id}",
            200,
            test_preflight=False
        )
        endpoints_tested += 1
        if success and response.get('disclaimer_accepted') is True:
            print(f"      ✅ Disclaimer status working")
            endpoints_passed += 1
        else:
            print(f"      ❌ Disclaimer status failed")
        
        # 4. GET /api/coach/consultation-limit/{user_id}
        print(f"\n   4️⃣ Testing GET /api/coach/consultation-limit/{test_user_id}")
        success, response = self.run_cors_test(
            "Consultation Limit",
            "GET",
            f"coach/consultation-limit/{test_user_id}",
            200,
            test_preflight=False
        )
        endpoints_tested += 1
        if success and 'can_use' in response:
            print(f"      ✅ Consultation limit working (can_use: {response.get('can_use')})")
            endpoints_passed += 1
        else:
            print(f"      ❌ Consultation limit failed")
        
        # 5. POST /api/coach/sessions
        print(f"\n   5️⃣ Testing POST /api/coach/sessions")
        session_data = {"user_id": test_user_id, "title": "Test Session"}
        success, response = self.run_cors_test(
            "Create Session",
            "POST",
            "coach/sessions",
            200,
            data=session_data,
            test_preflight=True
        )
        endpoints_tested += 1
        if success and 'id' in response:
            session_id = response['id']
            print(f"      ✅ Session creation working (session_id: {session_id[:8]}...)")
            endpoints_passed += 1
        else:
            print(f"      ❌ Session creation failed")
            session_id = None
        
        # 6. GET /api/coach/sessions/{user_id}
        print(f"\n   6️⃣ Testing GET /api/coach/sessions/{test_user_id}")
        success, response = self.run_cors_test(
            "Get Sessions",
            "GET",
            f"coach/sessions/{test_user_id}",
            200,
            test_preflight=False
        )
        endpoints_tested += 1
        if success and isinstance(response, list):
            print(f"      ✅ Session retrieval working ({len(response)} sessions)")
            endpoints_passed += 1
        else:
            print(f"      ❌ Session retrieval failed")
        
        # 7. POST /api/coach/message (Real AI Integration Test)
        if session_id:
            print(f"\n   7️⃣ Testing POST /api/coach/message (Real AI Integration)")
            message_data = {
                "session_id": session_id,
                "message": "Create a Mediterranean breakfast plan for Type 2 diabetes with no nuts or shellfish",
                "user_id": test_user_id
            }
            print(f"      Note: AI response may take 10-15 seconds...")
            success, response = self.run_cors_test(
                "Send Message to AI",
                "POST",
                "coach/message",
                200,
                data=message_data,
                test_preflight=True
            )
            endpoints_tested += 1
            if success and 'response' in response:
                ai_response = response['response']
                print(f"      ✅ AI integration working (response: {len(ai_response)} chars)")
                print(f"      AI Response preview: {ai_response[:100]}...")
                
                # Check for diabetes-specific content
                diabetes_keywords = ['diabetes', 'blood sugar', 'carb', 'mediterranean', 'breakfast']
                found_keywords = [kw for kw in diabetes_keywords if kw.lower() in ai_response.lower()]
                if found_keywords:
                    print(f"      ✅ AI response contains diabetes-specific content: {found_keywords}")
                
                endpoints_passed += 1
            else:
                print(f"      ❌ AI integration failed")
        else:
            print(f"\n   7️⃣ Skipping POST /api/coach/message (no session_id)")
            endpoints_tested += 1
        
        # 8. GET /api/coach/messages/{session_id}
        if session_id:
            print(f"\n   8️⃣ Testing GET /api/coach/messages/{session_id}")
            success, response = self.run_cors_test(
                "Get Messages",
                "GET",
                f"coach/messages/{session_id}",
                200,
                test_preflight=False
            )
            endpoints_tested += 1
            if success and isinstance(response, list):
                print(f"      ✅ Message retrieval working ({len(response)} messages)")
                endpoints_passed += 1
            else:
                print(f"      ❌ Message retrieval failed")
        else:
            print(f"\n   8️⃣ Skipping GET /api/coach/messages (no session_id)")
            endpoints_tested += 1
        
        # 9. GET /api/coach/search/{user_id}
        print(f"\n   9️⃣ Testing GET /api/coach/search/{test_user_id}")
        success, response = self.run_cors_test(
            "Search Conversations",
            "GET",
            f"coach/search/{test_user_id}?query=mediterranean",
            200,
            test_preflight=False
        )
        endpoints_tested += 1
        if success:
            print(f"      ✅ Search working")
            endpoints_passed += 1
        else:
            print(f"      ❌ Search failed")
        
        # Calculate success rate
        success_rate = (endpoints_passed / endpoints_tested) * 100 if endpoints_tested > 0 else 0
        
        print(f"\n🎯 REGRESSION TEST RESULTS:")
        print(f"   Endpoints tested: {endpoints_tested}/9")
        print(f"   Endpoints passed: {endpoints_passed}/9")
        print(f"   Success rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print(f"   ✅ ALL 9 ENDPOINTS WORKING - NO REGRESSIONS")
            return True
        elif success_rate >= 90.0:
            print(f"   ⚠️  MINOR ISSUES - {endpoints_passed}/9 endpoints working")
            return True
        else:
            print(f"   ❌ CRITICAL REGRESSIONS - Only {endpoints_passed}/9 endpoints working")
            return False

    def run_all_cors_tests(self):
        """Run all CORS validation tests"""
        print(f"\n🚀 STARTING COMPREHENSIVE CORS VALIDATION TESTS")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        all_tests = [
            ("CORS Preflight - Disclaimer Endpoint", self.test_cors_preflight_disclaimer_endpoint),
            ("CORS Preflight - Sessions Endpoint", self.test_cors_preflight_sessions_endpoint),
            ("API Contract - Disclaimer Endpoint", self.test_api_contract_disclaimer_endpoint),
            ("API Contract - Sessions Endpoint", self.test_api_contract_sessions_endpoint),
            ("All 9 AI Coach Endpoints Regression", self.test_all_9_ai_coach_endpoints)
        ]
        
        results = []
        
        for test_name, test_func in all_tests:
            print(f"\n" + "="*60)
            print(f"🧪 {test_name}")
            print(f"="*60)
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"\n✅ {test_name}: PASSED")
                else:
                    print(f"\n❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"\n💥 {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Final summary
        print(f"\n" + "="*80)
        print(f"🎯 CORS CONFIGURATION FIX VALIDATION SUMMARY")
        print(f"="*80)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Major test categories: {passed_tests}/{total_tests}")
        print(f"Overall success rate: {success_rate:.1f}%")
        
        print(f"\nDetailed Results:")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        if success_rate == 100.0:
            print(f"\n🎉 SUCCESS: CORS configuration fix is working perfectly!")
            print(f"✅ CORS preflight requests work correctly")
            print(f"✅ API contracts accept user_id in request body")
            print(f"✅ All 9 AI Health Coach endpoints maintain functionality")
            print(f"✅ No regressions detected")
        elif success_rate >= 80.0:
            print(f"\n⚠️  MOSTLY SUCCESSFUL: CORS fix working with minor issues")
            print(f"✅ Core CORS functionality working")
            print(f"⚠️  Some endpoints may need attention")
        else:
            print(f"\n❌ CRITICAL ISSUES: CORS configuration needs attention")
            print(f"❌ Multiple test failures detected")
            print(f"❌ Frontend access may still be blocked")
        
        print(f"\n" + "="*80)
        return success_rate >= 80.0

if __name__ == "__main__":
    tester = CORSValidationTester()
    success = tester.run_all_cors_tests()
    
    if success:
        print(f"\n🎯 CORS VALIDATION: SUCCESS")
        exit(0)
    else:
        print(f"\n🎯 CORS VALIDATION: FAILED")
        exit(1)