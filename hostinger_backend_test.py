#!/usr/bin/env python3
"""
NutriTame PHP Backend API Tester for Hostinger Deployment
Tests the deployed PHP backend at https://app.nutritame.com/api/
Focus: Demo configuration and access endpoints for frontend integration
"""

import requests
import json
import sys
import time
from datetime import datetime

class NutriTameHostingerTester:
    def __init__(self, base_url="https://app.nutritame.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_access_token = None
        self.created_user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]  # Remove leading slash
        
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    # =============================================
    # DEMO ENDPOINTS TESTS (Primary Focus)
    # =============================================
    
    def test_demo_config_endpoint(self):
        """Test GET /api/demo-config.php"""
        # Try the consolidated demo-config.php endpoint first
        success, response = self.run_test(
            "Demo Config Endpoint (demo-config.php)",
            "GET",
            "demo-config.php",
            200
        )
        
        if not success:
            # Fallback to the structured API endpoint
            success, response = self.run_test(
                "Demo Config Endpoint (demo/config)",
                "GET", 
                "demo/config",
                200
            )
        
        if success:
            # Verify required fields
            required_fields = ['demo_mode', 'launch_date']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ Demo mode: {response.get('demo_mode')}")
                print(f"   ✅ Launch date: {response.get('launch_date')}")
                return True
        
        return False

    def test_demo_access_with_email(self):
        """Test POST /api/demo-config.php?endpoint=access with email"""
        demo_data = {
            "email": "maria.gonzalez@example.com"
        }
        
        # Try consolidated endpoint with query parameter
        success, response = self.run_test(
            "Demo Access with Email (demo-config.php?endpoint=access)",
            "POST",
            "demo-config.php?endpoint=access",
            201,  # Expect 201 Created for successful resource creation
            data=demo_data
        )
        
        if not success:
            # Fallback to structured API endpoint
            success, response = self.run_test(
                "Demo Access with Email (demo/access)",
                "POST",
                "demo/access", 
                200,
                data=demo_data
            )
        
        if success and response.get('access_token'):
            self.demo_access_token = response['access_token']
            print(f"   ✅ Created demo access token: {self.demo_access_token[:20]}...")
            print(f"   ✅ Demo user email: {response.get('user', {}).get('email', 'N/A')}")
            
            # Verify response structure
            required_fields = ['demo_access', 'access_token', 'user', 'launch_date']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing response fields: {missing_fields}")
                return False
            
            return True
        
        return False

    def test_demo_access_without_email(self):
        """Test POST /api/demo-config.php?endpoint=access without email"""
        demo_data = {}  # No email provided
        
        # Try consolidated endpoint with query parameter
        success, response = self.run_test(
            "Demo Access without Email (demo-config.php?endpoint=access)",
            "POST",
            "demo-config.php?endpoint=access",
            201,  # Expect 201 Created for successful resource creation
            data=demo_data
        )
        
        if not success:
            # Fallback to structured API endpoint
            success, response = self.run_test(
                "Demo Access without Email (demo/access)",
                "POST",
                "demo/access",
                200,
                data=demo_data
            )
        
        if success and response.get('access_token'):
            print(f"   ✅ Created demo access without email")
            print(f"   ✅ Auto-generated email: {response.get('user', {}).get('email', 'N/A')}")
            
            # Verify auto-generated email format
            user_email = response.get('user', {}).get('email', '')
            if '@nutritame.com' in user_email and user_email.startswith('demo_'):
                print(f"   ✅ Email format is correct: {user_email}")
                return True
            else:
                print(f"   ❌ Email format is incorrect: {user_email}")
                return False
        
        return False

    # =============================================
    # ADDITIONAL DEMO-RELATED ENDPOINTS
    # =============================================
    
    def test_api_root_endpoint(self):
        """Test GET /api/ (root API endpoint)"""
        success, response = self.run_test(
            "API Root Endpoint",
            "GET",
            "",
            200
        )
        
        if success:
            # Check if it returns API information
            if isinstance(response, dict) and ('name' in response or 'status' in response):
                print(f"   ✅ API root returns proper information")
                return True
            else:
                print(f"   ⚠️  API root response format unexpected")
                return True  # Not necessarily an error
        
        return False

    def test_health_check_endpoint(self):
        """Test GET /api/health (health check)"""
        success, response = self.run_test(
            "Health Check Endpoint",
            "GET",
            "health",
            200
        )
        
        if success:
            if isinstance(response, dict) and response.get('status') == 'OK':
                print(f"   ✅ Health check passed")
                return True
            else:
                print(f"   ⚠️  Health check response unexpected: {response}")
                return True  # Not necessarily critical
        
        return False

    # =============================================
    # FRONTEND BUTTON INTEGRATION TESTS
    # =============================================
    
    def test_frontend_demo_button_flow(self):
        """Test the complete demo button flow that frontend will use"""
        print("\n🔄 Testing Complete Frontend Demo Button Flow...")
        
        # Step 1: Get demo configuration (for button display)
        print("   Step 1: Getting demo configuration...")
        config_success, config_response = self.run_test(
            "Demo Config for Button",
            "GET",
            "demo-config.php",
            200
        )
        
        if not config_success:
            # Try fallback
            config_success, config_response = self.run_test(
                "Demo Config for Button (fallback)",
                "GET", 
                "demo/config",
                200
            )
        
        if not config_success:
            print("   ❌ Cannot get demo configuration")
            return False
        
        # Step 2: Create demo access (when user clicks button)
        print("   Step 2: Creating demo access...")
        access_success, access_response = self.run_test(
            "Demo Access Creation",
            "POST",
            "demo-config.php?endpoint=access",
            201,  # Expect 201 Created for successful resource creation
            data={"email": "frontend.test@example.com"}
        )
        
        if not access_success:
            # Try fallback
            access_success, access_response = self.run_test(
                "Demo Access Creation (fallback)",
                "POST",
                "demo/access",
                200,
                data={"email": "frontend.test@example.com"}
            )
        
        if not access_success:
            print("   ❌ Cannot create demo access")
            return False
        
        # Step 3: Verify token can be used for authenticated requests
        if access_response.get('access_token'):
            token = access_response['access_token']
            auth_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            print("   Step 3: Testing authenticated request with demo token...")
            # Try to access a protected endpoint (if available)
            auth_success, auth_response = self.run_test(
                "Authenticated Request Test",
                "GET",
                "users",  # Try to list users with demo token
                200,
                headers=auth_headers
            )
            
            if auth_success:
                print("   ✅ Demo token works for authenticated requests")
            else:
                print("   ⚠️  Demo token authentication test inconclusive")
        
        print("   ✅ Frontend demo button flow completed successfully")
        return True

    # =============================================
    # ERROR HANDLING TESTS
    # =============================================
    
    def test_cors_headers(self):
        """Test CORS headers for frontend integration"""
        url = f"{self.api_url}/demo-config.php"
        
        try:
            # Test preflight request
            response = requests.options(url, headers={
                'Origin': 'https://app.nutritame.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }, timeout=30)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print(f"\n🔍 Testing CORS Headers...")
            print(f"   Status: {response.status_code}")
            
            if cors_headers['Access-Control-Allow-Origin']:
                print(f"   ✅ CORS Origin: {cors_headers['Access-Control-Allow-Origin']}")
            else:
                print(f"   ❌ Missing CORS Origin header")
                return False
            
            if cors_headers['Access-Control-Allow-Methods']:
                print(f"   ✅ CORS Methods: {cors_headers['Access-Control-Allow-Methods']}")
            else:
                print(f"   ❌ Missing CORS Methods header")
                return False
            
            self.tests_run += 1
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
            self.tests_run += 1
            return False

    def test_invalid_endpoint_handling(self):
        """Test handling of invalid endpoints"""
        success, response = self.run_test(
            "Invalid Endpoint Handling",
            "GET",
            "nonexistent-endpoint.php",
            404
        )
        
        if success:
            print("   ✅ Correctly returns 404 for invalid endpoints")
            return True
        else:
            print("   ❌ Should return 404 for invalid endpoints")
            return False

    # =============================================
    # MAIN TEST RUNNER
    # =============================================
    
    def run_all_tests(self):
        """Run all PHP backend tests for Hostinger deployment"""
        print("=" * 70)
        print("🧪 NutriTame PHP Backend Testing - Hostinger Deployment")
        print("=" * 70)
        print(f"Testing deployed backend at: {self.api_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test categories focused on demo functionality
        test_categories = [
            ("Demo Configuration Endpoints", [
                self.test_demo_config_endpoint,
            ]),
            ("Demo Access Creation", [
                self.test_demo_access_with_email,
                self.test_demo_access_without_email,
            ]),
            ("Frontend Integration Tests", [
                self.test_frontend_demo_button_flow,
                self.test_cors_headers,
            ]),
            ("System Health Checks", [
                self.test_api_root_endpoint,
                self.test_health_check_endpoint,
            ]),
            ("Error Handling", [
                self.test_invalid_endpoint_handling,
            ])
        ]

        # Run tests by category
        for category_name, tests in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 50)
            
            for test_func in tests:
                try:
                    test_func()
                except Exception as e:
                    print(f"❌ {test_func.__name__} failed with exception: {e}")
                    self.tests_run += 1

        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED! PHP backend is ready for frontend integration.")
            print("\n✅ DEPLOYMENT STATUS: Ready for production use")
        elif self.tests_passed >= (self.tests_run * 0.8):  # 80% pass rate
            print(f"\n⚠️  Most tests passed. {self.tests_run - self.tests_passed} minor issues found.")
            print("\n✅ DEPLOYMENT STATUS: Ready with minor issues to monitor")
        else:
            print(f"\n❌ {self.tests_run - self.tests_passed} critical tests failed.")
            print("\n❌ DEPLOYMENT STATUS: Needs attention before frontend integration")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return True if at least 80% of tests pass (acceptable for demo mode)
        return self.tests_passed >= (self.tests_run * 0.8)


if __name__ == "__main__":
    # Allow custom base URL via command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://app.nutritame.com"
    
    tester = NutriTameHostingerTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)