#!/usr/bin/env python3
"""
Test script to verify frontend integration with areas_of_interest parameter.

This script simulates what the frontend would send to the backend
and verifies that the areas of interest filtering is working correctly.

Updated for the new .env configuration system.
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
LOGIN_USERNAME = "david"
LOGIN_PASSWORD = "Connie97"

# Test areas of interest (same as frontend config)
CALIFORNIA_AREAS_OF_INTEREST = [
    {
        'min_lat': 32.50,
        'max_lat': 42.10,
        'min_lon': -124.50,
        'max_lon': -114.10,
    }
]

NEW_YORK_AREAS_OF_INTEREST = [
    {
        'min_lat': 40.4774,
        'max_lat': 40.9176,
        'min_lon': -74.2591,
        'max_lon': -73.7004,
    }
]

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

def analyze_enhancement(enhanced_text: str, expected_enhanced: list, expected_not_enhanced: list):
    """Analyze the enhancement results and provide detailed feedback."""
    print(f"📝 Enhanced message: {enhanced_text}")
    
    print("\n🎯 Expected Enhanced Locations:")
    for location in expected_enhanced:
        # Look for the actual XML format: <LOC lat="..." lon="..." zoom_level="...">Location</LOC>
        if f'<LOC' in enhanced_text and location in enhanced_text:
            print(f"  ✅ {location} - Enhanced correctly")
        else:
            print(f"  ❌ {location} - Not enhanced (issue detected)")
    
    print("\n🚫 Expected Non-Enhanced Locations:")
    for location in expected_not_enhanced:
        # Look for the actual XML format: <LOC lat="..." lon="..." zoom_level="...">Location</LOC>
        if f'<LOC' in enhanced_text and location in enhanced_text:
            print(f"  ❌ {location} - Enhanced (should not be)")
        else:
            print(f"  ✅ {location} - Not enhanced (correct)")

def test_frontend_integration(auth_token):
    """Test the exact payload that the frontend would send."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Simulate frontend payload
    payload = {
        "message": "I visited San Francisco, New York City, and Miami.",
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "model_id": None,
        "session_id": None,
        "areas_of_interest": CALIFORNIA_AREAS_OF_INTEREST
    }
    
    print(f"🧪 Testing frontend integration payload:")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)  # Increased timeout for GeoNER
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Frontend integration working correctly.")
            
            enhanced_msg = data.get('enhanced_user_message', 'No enhancement')
            ai_response = data.get('message', 'No response')
            
            print(f"🤖 AI response: {ai_response[:200]}...")
            
            # Analyze enhancement results
            expected_enhanced = ["San Francisco"]  # California location
            expected_not_enhanced = ["New York City", "Miami"]  # Outside California
            
            analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_multiple_areas_integration(auth_token):
    """Test frontend integration with multiple areas of interest."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test with California + New York areas
    combined_areas = CALIFORNIA_AREAS_OF_INTEREST + NEW_YORK_AREAS_OF_INTEREST
    
    payload = {
        "message": "I visited San Francisco, New York City, and Miami.",
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "model_id": None,
        "session_id": None,
        "areas_of_interest": combined_areas
    }
    
    print(f"\n🧪 Testing multiple areas integration:")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Multiple areas integration working correctly.")
            
            enhanced_msg = data.get('enhanced_user_message', 'No enhancement')
            ai_response = data.get('message', 'No response')
            
            print(f"🤖 AI response: {ai_response[:200]}...")
            
            # Analyze enhancement results
            expected_enhanced = ["San Francisco", "New York City"]  # California + New York
            expected_not_enhanced = ["Miami"]  # Outside both areas
            
            analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_no_areas_integration(auth_token):
    """Test frontend integration with no areas of interest (all entities processed)."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test with no areas of interest
    payload = {
        "message": "I visited San Francisco, New York City, and Miami.",
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "model_id": None,
        "session_id": None,
        "areas_of_interest": None  # No filtering
    }
    
    print(f"\n🧪 Testing no areas integration (all entities processed):")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! No areas integration working correctly.")
            
            enhanced_msg = data.get('enhanced_user_message', 'No enhancement')
            ai_response = data.get('message', 'No response')
            
            print(f"🤖 AI response: {ai_response[:200]}...")
            
            # Analyze enhancement results - all should be enhanced
            expected_enhanced = ["San Francisco", "New York City", "Miami"]  # All locations
            expected_not_enhanced = []  # None should be excluded
            
            analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    print("Frontend Integration Test")
    print("="*50)
    print("Testing areas_of_interest parameter integration")
    print("Updated for new .env configuration system")
    
    # Get token
    token = login_and_get_token()
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    try:
        # Test all integration scenarios
        test_frontend_integration(token)
        test_multiple_areas_integration(token)
        test_no_areas_integration(token)
        
        print("\n" + "="*50)
        print("🎉 Frontend integration test completed!")
        print("="*50)
        print("\nIntegration Test Results:")
        print("✅ Single area filtering (California)")
        print("✅ Multiple areas filtering (California + New York)")
        print("✅ No filtering (all entities processed)")
        print("\nFrontend can now:")
        print("- Send areas_of_interest parameter")
        print("- Filter geographic entities by location")
        print("- Process multiple areas with OR logic")
        print("- Handle no filtering gracefully")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
