#!/usr/bin/env python3
"""
Debug script to test a single API request and see detailed error responses.

This script is useful for debugging API issues and testing the new
areas_of_interest parameter functionality.

Updated for the new .env configuration system.
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
LOGIN_USERNAME = "david"
LOGIN_PASSWORD = "Connie97"

def login_and_get_token():
    """Logs in to the API and returns the authentication token."""
    login_url = f"{API_BASE_URL}/auth/login"
    headers = {"Content-Type": "application/json"}
    payload = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}

    try:
        response = requests.post(login_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to log in: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def test_simple_request(auth_token):
    """Test a simple request to see what validation errors occur."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test with minimal payload
    payload = {
        "message": "Hello",
        "chat_history": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello there!"}
        ]
    }
    
    print(f"🧪 Testing minimal payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"✅ Response status: {response.status_code}")
        print(f"📝 Response body: {response.text[:500]}...")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response headers: {dict(e.response.headers)}")
            try:
                error_detail = e.response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response text: {e.response.text}")
        return None

def test_areas_of_interest_request(auth_token):
    """Test a request with areas_of_interest parameter."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test with areas_of_interest
    payload = {
        "message": "I visited San Francisco and New York City.",
        "chat_history": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello there!"}
        ],
        "areas_of_interest": [
            {
                'min_lat': 32.50,
                'max_lat': 42.10,
                'min_lon': -124.50,
                'max_lon': -114.10,
            }
        ]
    }
    
    print(f"\n🧪 Testing areas_of_interest payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"✅ Response status: {response.status_code}")
        print(f"📝 Response body: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            enhanced_msg = data.get('enhanced_user_message', 'No enhancement')
            print(f"\n🎯 Enhanced message: {enhanced_msg}")
            
            # Check if areas_of_interest filtering is working
            # Look for the actual XML format: <LOC lat="..." lon="..." zoom_level="...">San Francisco</LOC>
            if '<LOC' in enhanced_msg and 'San Francisco' in enhanced_msg:
                print("✅ San Francisco was enhanced (within California)")
            else:
                print("❌ San Francisco was not enhanced")
                
            if '<LOC' in enhanced_msg and 'New York City' in enhanced_msg:
                print("❌ New York City was enhanced (should not be - outside California)")
            else:
                print("✅ New York City was not enhanced (correct - outside California)")
        
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response headers: {dict(e.response.headers)}")
            try:
                error_detail = e.response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response text: {e.response.text}")
        return None

def test_invalid_payload(auth_token):
    """Test with invalid payload to see validation errors."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test with invalid areas_of_interest format
    payload = {
        "message": "Hello",
        "chat_history": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello there!"}
        ],
        "areas_of_interest": [
            {
                'min_lat': "invalid",  # Invalid type
                'max_lat': 42.10,
                'min_lon': -124.50,
                'max_lon': -114.10,
            }
        ]
    }
    
    print(f"\n🧪 Testing invalid payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code != 200:
            print("✅ Validation correctly caught invalid payload")
        else:
            print("⚠️  Validation should have caught invalid payload")
            
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def main():
    print("Debug API Request")
    print("="*50)
    print("Testing API endpoints and areas_of_interest parameter")
    print("Updated for new .env configuration system")
    
    # Get token
    token = login_and_get_token()
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    try:
        # Test various scenarios
        print("\n" + "="*50)
        print("1. Testing minimal request...")
        result1 = test_simple_request(token)
        
        print("\n" + "="*50)
        print("2. Testing areas_of_interest request...")
        result2 = test_areas_of_interest_request(token)
        
        print("\n" + "="*50)
        print("3. Testing invalid payload...")
        result3 = test_invalid_payload(token)
        
        print("\n" + "="*50)
        print("🎉 Debug testing completed!")
        print("="*50)
        
        if result1:
            print("✅ Minimal request: SUCCESS")
        else:
            print("❌ Minimal request: FAILED")
            
        if result2:
            print("✅ Areas of interest request: SUCCESS")
        else:
            print("❌ Areas of interest request: FAILED")
            
        if result3:
            print("⚠️  Invalid payload: Unexpectedly succeeded")
        else:
            print("✅ Invalid payload: Correctly failed")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Debug testing interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during debug testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
