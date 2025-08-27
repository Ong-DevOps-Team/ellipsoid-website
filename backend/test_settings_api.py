#!/usr/bin/env python3
"""
Standalone test program for Settings API endpoints
Tests GET, POST, and PUT operations for user settings
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
SETTINGS_URL = f"{BASE_URL}/settings"
LOGIN_URL = f"{BASE_URL}/auth/login"

class SettingsAPITester:
    def __init__(self):
        self.access_token = None
        self.username = None
        
    def login(self, username: str, password: str) -> bool:
        """Login and get access token"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            print(f"🔐 Logging in as {username}...")
            response = requests.post(LOGIN_URL, json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.username = username
                print(f"✅ Login successful! Token received.")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if not self.access_token:
            raise Exception("Not logged in. Please login first.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_settings(self) -> bool:
        """Test GET /settings endpoint"""
        try:
            print("\n📋 Testing GET /settings...")
            
            headers = self.get_headers()
            response = requests.get(SETTINGS_URL, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ GET /settings successful!")
                print(f"Success: {data['success']}")
                print(f"Message: {data['message']}")
                
                if data['settings']:
                    print("📊 Current Settings:")
                    print(f"  User ID: {data['settings']['userId']}")
                    print(f"  ChatGIS Salutation: {data['settings']['chatGIS']['salutation']}")
                    print(f"  GeoRAG Model: {data['settings']['geoRAG']['selectedModel']}")
                    print(f"  Areas Enabled: {data['settings']['geoRAG']['enableAreasOfInterest']}")
                    print(f"  Version: {data['settings']['metadata']['version']}")
                else:
                    print("ℹ️  No settings found for user (this is normal for new users)")
                
                return True
            else:
                print(f"❌ GET /settings failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ GET /settings error: {e}")
            return False
    
    def test_post_settings(self) -> bool:
        """Test POST /settings endpoint (create/upsert)"""
        try:
            print("\n💾 Testing POST /settings...")
            
            # Create test settings data
            test_settings = {
                "userId": self.username,
                "settingsType": "user_settings",
                "chatGIS": {
                    "salutation": "Sir"
                },
                "geoRAG": {
                    "selectedModel": "Claude 3.5 Sonnet v2",
                    "enableAreasOfInterest": True,
                    "areas": [
                        {
                            "areaId": "area1",
                            "enabled": True,
                            "coordinates": {
                                "minLat": 33.1,
                                "maxLat": 33.3,
                                "minLon": -117.4,
                                "maxLon": -117.2
                            },
                            "presetArea": "oceanside-ca"
                        },
                        {
                            "areaId": "area2",
                            "enabled": False,
                            "coordinates": {
                                "minLat": 0,
                                "maxLat": 0,
                                "minLon": 0,
                                "maxLon": 0
                            },
                            "presetArea": "custom"
                        },
                        {
                            "areaId": "area3",
                            "enabled": False,
                            "coordinates": {
                                "minLat": 0,
                                "maxLat": 0,
                                "minLon": 0,
                                "maxLon": 0
                            },
                            "presetArea": "custom"
                        }
                    ]
                },
                "metadata": {
                    "createdAt": datetime.utcnow().isoformat() + "Z",
                    "updatedAt": datetime.utcnow().isoformat() + "Z",
                    "version": "1.0"
                }
            }
            
            headers = self.get_headers()
            response = requests.post(SETTINGS_URL, json=test_settings, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ POST /settings successful!")
                print(f"Success: {data['success']}")
                print(f"Message: {data['message']}")
                
                if data['settings']:
                    print("📊 Saved Settings:")
                    print(f"  User ID: {data['settings']['userId']}")
                    print(f"  ChatGIS Salutation: {data['settings']['chatGIS']['salutation']}")
                    print(f"  GeoRAG Model: {data['settings']['geoRAG']['selectedModel']}")
                    print(f"  Areas Enabled: {data['settings']['geoRAG']['enableAreasOfInterest']}")
                    print(f"  Area 1 Preset: {data['settings']['geoRAG']['areas'][0]['presetArea']}")
                    print(f"  Version: {data['settings']['metadata']['version']}")
                
                return True
            else:
                print(f"❌ POST /settings failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ POST /settings error: {e}")
            return False
    
    def test_put_settings(self) -> bool:
        """Test PUT /settings endpoint (update)"""
        try:
            print("\n🔄 Testing PUT /settings...")
            
            # Create update data
            update_data = {
                "chatGIS.salutation": "Madam",
                "geoRAG.selectedModel": "Amazon Nova Lite",
                "geoRAG.enableAreasOfInterest": False
            }
            
            headers = self.get_headers()
            response = requests.put(SETTINGS_URL, json=update_data, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ PUT /settings successful!")
                print(f"Success: {data['success']}")
                print(f"Message: {data['message']}")
                
                if data['settings']:
                    print("📊 Updated Settings:")
                    print(f"  User ID: {data['settings']['userId']}")
                    print(f"  ChatGIS Salutation: {data['settings']['chatGIS']['salutation']}")
                    print(f"  GeoRAG Model: {data['settings']['geoRAG']['selectedModel']}")
                    print(f"  Areas Enabled: {data['settings']['geoRAG']['enableAreasOfInterest']}")
                    print(f"  Version: {data['settings']['metadata']['version']}")
                
                return True
            else:
                print(f"❌ PUT /settings failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ PUT /settings error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all API tests"""
        print("🚀 Starting Settings API Tests...")
        print("=" * 50)
        
        if not self.access_token:
            print("❌ Not logged in. Please login first.")
            return False
        
        tests = [
            ("GET Settings", self.test_get_settings),
            ("POST Settings", self.test_post_settings),
            ("PUT Settings", self.test_put_settings),
            ("GET Settings (After Update)", self.test_get_settings)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST RESULTS SUMMARY")
        print("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Settings API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main test function"""
    print("🔧 Settings API Test Program")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend. Please ensure the backend is running on http://localhost:8000")
        print("💡 Start the backend with: python backend/main.py")
        return
    
    print("✅ Backend is running and accessible")
    
    # Get login credentials
    print("\n🔐 Please provide login credentials:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    # Create tester and run tests
    tester = SettingsAPITester()
    
    # Login
    if not tester.login(username, password):
        print("❌ Login failed. Cannot proceed with tests.")
        return
    
    # Run tests
    tester.run_all_tests()

if __name__ == "__main__":
    main()
