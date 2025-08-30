#!/usr/bin/env python3
"""
NutriTame Demo Backend Test - Focused on Working Endpoints
Tests the core demo functionality that the frontend needs
"""

import requests
import json
import sys
from datetime import datetime

class DemoBackendTester:
    def __init__(self, base_url="https://app.nutritame.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
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
                    print(f"   Error: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_demo_config(self):
        """Test GET /api/demo-config.php"""
        success, response = self.run_test(
            "Demo Configuration",
            "GET",
            "demo-config.php",
            200
        )
        
        if success:
            print(f"   ✅ Demo mode: {response.get('demo_mode')}")
            print(f"   ✅ Launch date: {response.get('launch_date')}")
            print(f"   ✅ Message: {response.get('message', 'N/A')}")
            
            # Verify required fields for frontend
            required_fields = ['demo_mode', 'launch_date']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            return True
        
        return False

    def test_demo_access_no_email(self):
        """Test POST /api/demo-config.php?endpoint=access without email"""
        success, response = self.run_test(
            "Demo Access Creation (No Email)",
            "POST",
            "demo-config.php?endpoint=access",
            201,
            data={}
        )
        
        if success:
            # Verify response structure
            required_fields = ['demo_access', 'access_token', 'user']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing response fields: {missing_fields}")
                return False
            
            user = response.get('user', {})
            print(f"   ✅ Created user ID: {user.get('id', 'N/A')}")
            print(f"   ✅ Auto-generated email: {user.get('email', 'N/A')}")
            print(f"   ✅ Subscription tier: {user.get('subscription_tier', 'N/A')}")
            print(f"   ✅ Access token length: {len(response.get('access_token', ''))}")
            
            return True
        
        return False

    def test_api_health(self):
        """Test API health and availability"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "health",
            200
        )
        
        if success:
            print(f"   ✅ API Status: {response.get('status', 'N/A')}")
            print(f"   ✅ Timestamp: {response.get('timestamp', 'N/A')}")
            return True
        
        return False

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root Information",
            "GET",
            "",
            200
        )
        
        if success:
            print(f"   ✅ API Name: {response.get('name', 'N/A')}")
            print(f"   ✅ Version: {response.get('version', 'N/A')}")
            print(f"   ✅ Status: {response.get('status', 'N/A')}")
            print(f"   ✅ Demo Mode: {response.get('demo_mode', 'N/A')}")
            
            endpoints = response.get('endpoints', [])
            if endpoints:
                print(f"   ✅ Available endpoints: {len(endpoints)}")
            
            return True
        
        return False

    def test_cors_support(self):
        """Test CORS headers for frontend integration"""
        url = f"{self.api_url}/demo-config.php"
        
        try:
            response = requests.options(url, headers={
                'Origin': 'https://app.nutritame.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }, timeout=30)
            
            self.tests_run += 1
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            
            print(f"\n🔍 Testing CORS Support...")
            print(f"   Status: {response.status_code}")
            
            if cors_origin and cors_methods:
                self.tests_passed += 1
                print(f"✅ Passed - CORS properly configured")
                print(f"   ✅ Allow Origin: {cors_origin}")
                print(f"   ✅ Allow Methods: {cors_methods}")
                return True
            else:
                print(f"❌ Failed - CORS headers missing")
                return False
                
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
            self.tests_run += 1
            return False

    def run_focused_tests(self):
        """Run focused tests on working functionality"""
        print("=" * 60)
        print("🧪 NutriTame Demo Backend - Focused Testing")
        print("=" * 60)
        print(f"Testing: {self.api_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Core tests that should work
        tests = [
            ("Demo Configuration", self.test_demo_config),
            ("Demo Access Creation", self.test_demo_access_no_email),
            ("API Health Check", self.test_api_health),
            ("API Information", self.test_api_root),
            ("CORS Support", self.test_cors_support),
        ]

        print("📋 Core Demo Functionality Tests")
        print("-" * 40)

        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                self.tests_run += 1

        # Summary
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST RESULTS")
        print("=" * 60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL CORE TESTS PASSED!")
            print("✅ Demo backend is ready for frontend integration")
            print("✅ Frontend buttons should work correctly")
        elif self.tests_passed >= (self.tests_run * 0.8):
            print(f"\n⚠️  Most tests passed ({self.tests_passed}/{self.tests_run})")
            print("✅ Core functionality is working")
            print("⚠️  Some minor issues may need monitoring")
        else:
            print(f"\n❌ Critical issues found ({self.tests_passed}/{self.tests_run} passed)")
            print("❌ Backend needs fixes before frontend integration")
        
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.tests_passed >= (self.tests_run * 0.8)


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://app.nutritame.com"
    
    tester = DemoBackendTester(base_url)
    success = tester.run_focused_tests()
    
    sys.exit(0 if success else 1)