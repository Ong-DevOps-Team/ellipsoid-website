#!/usr/bin/env python3
"""
Test program for areas_of_interest parameter in the chat/rag API endpoint.

This program tests the API with different areas_of_interest configurations:
1. None (no filtering)
2. One area (California)
3. Two areas (California + New York)
4. Three areas (California + New York + Florida)

For each configuration, it tests with geographic entities that are:
- Inside the specified areas
- Outside the specified areas

Updated to work with the new .env configuration system.
"""

import requests
import json
import sys
from typing import List, Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"

# Test areas of interest
CALIFORNIA = [{
    'min_lat': 32.50,
    'max_lat': 42.10,
    'min_lon': -124.50,
    'max_lon': -114.10,
}]

NEW_YORK = [{
    'min_lat': 40.4774,
    'max_lat': 40.9176,
    'min_lon': -74.2591,
    'max_lon': -73.7004,
}]

FLORIDA = [{
    'min_lat': 24.3963,
    'max_lat': 31.0000,
    'min_lon': -87.6348,
    'max_lon': -79.9743,
}]

# Test texts with geographic entities
TEST_TEXTS = [
    "I visited San Francisco and Los Angeles in California.",
    "I went to New York City and Boston on the East Coast.",
    "I traveled to Miami and Orlando in Florida.",
    "I visited Seattle and Portland in the Pacific Northwest.",
    "I went to Chicago and Detroit in the Midwest.",
    "I traveled to London and Paris in Europe.",
    "I visited Tokyo and Beijing in Asia.",
    "I went to Sydney and Melbourne in Australia."
]

def login_and_get_token(username: str, password: str) -> str:
    """Logs in to the API and returns the authentication token."""
    login_url = f"{API_BASE_URL}/auth/login"
    headers = {"Content-Type": "application/json"}
    payload = {"username": username, "password": password}

    try:
        response = requests.post(login_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Failed to log in: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)

def make_api_request(message: str, areas_of_interest: List[Dict[str, float]] = None, auth_token: str = None) -> Dict[str, Any]:
    """Make a request to the chat/rag API endpoint."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": message,
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "model_id": None,
        "session_id": None,
        "areas_of_interest": areas_of_interest
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)  # Increased timeout for GeoNER processing
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                return {"error": f"{e} - Details: {error_detail}"}
            except:
                return {"error": f"{e} - Status: {e.response.status_code}"}
        return {"error": str(e)}

def analyze_enhancement(text: str, enhanced_text: str, expected_locations: List[str], should_be_enhanced: bool = True) -> Dict[str, Any]:
    """Analyze the enhancement results and return analysis."""
    analysis = {
        "locations_found": [],
        "locations_enhanced": [],
        "locations_not_enhanced": [],
        "enhancement_working": False
    }
    
    # Check each expected location
    for location in expected_locations:
        if location in enhanced_text:
            analysis["locations_found"].append(location)
            # Check if it was enhanced (has XML tags)
            # Look for the actual XML format: <LOC lat="..." lon="..." zoom_level="...">Location</LOC>
            if f'<LOC' in enhanced_text and location in enhanced_text:
                analysis["locations_enhanced"].append(location)
            else:
                analysis["locations_not_enhanced"].append(location)
    
    # Determine if enhancement is working as expected
    if should_be_enhanced:
        analysis["enhancement_working"] = len(analysis["locations_enhanced"]) > 0
    else:
        analysis["enhancement_working"] = len(analysis["locations_not_enhanced"]) > 0
    
    return analysis

def test_no_areas_of_interest(auth_token: str):
    """Test with no areas_of_interest (should include all geographic entities)."""
    print("\n" + "="*60)
    print("TEST 1: No areas_of_interest (no filtering)")
    print("="*60)
    
    for i, text in enumerate(TEST_TEXTS[:4], 1):
        print(f"\nTest {i}: {text}")
        response = make_api_request(text, auth_token=auth_token)
        
        if "error" in response:
            print(f"  ❌ Error: {response['error']}")
        else:
            enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
            print(f"  ✅ Response received")
            print(f"  📝 Enhanced message: {enhanced_msg[:100]}...")
            
            # Analyze enhancement
            expected_locations = ["San Francisco", "Los Angeles", "New York City", "Boston", "Miami", "Orlando"]
            analysis = analyze_enhancement(text, enhanced_msg, expected_locations, should_be_enhanced=True)
            
            if analysis["enhancement_working"]:
                print(f"  🎯 Enhancement working: {len(analysis['locations_enhanced'])} locations enhanced")
            else:
                print(f"  ⚠️  No locations enhanced - this might indicate an issue")

def test_california_only(auth_token: str):
    """Test with California area of interest only."""
    print("\n" + "="*60)
    print("TEST 2: California area_of_interest only")
    print("="*60)
    
    for i, text in enumerate(TEST_TEXTS[:4], 1):
        print(f"\nTest {i}: {text}")
        response = make_api_request(text, CALIFORNIA, auth_token=auth_token)
        
        if "error" in response:
            print(f"  ❌ Error: {response['error']}")
        else:
            enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
            print(f"  ✅ Response received")
            print(f"  📝 Enhanced message: {enhanced_msg[:100]}...")
            
            # Analyze enhancement for California locations
            california_locations = ["San Francisco", "Los Angeles"]
            non_california_locations = ["New York City", "Boston", "Miami", "Orlando"]
            
            cal_analysis = analyze_enhancement(text, enhanced_msg, california_locations, should_be_enhanced=True)
            non_cal_analysis = analyze_enhancement(text, enhanced_msg, non_california_locations, should_be_enhanced=False)
            
            print(f"  🎯 California locations: {len(cal_analysis['locations_enhanced'])}/{len(cal_analysis['locations_found'])} enhanced")
            print(f"  🚫 Non-California locations: {len(non_cal_analysis['locations_not_enhanced'])}/{len(non_cal_analysis['locations_found'])} not enhanced")

def test_california_and_newyork(auth_token: str):
    """Test with California and New York areas of interest."""
    print("\n" + "="*60)
    print("TEST 3: California + New York areas_of_interest")
    print("="*60)
    
    combined_areas = CALIFORNIA + NEW_YORK
    
    for i, text in enumerate(TEST_TEXTS[:4], 1):
        print(f"\nTest {i}: {text}")
        response = make_api_request(text, combined_areas, auth_token=auth_token)
        
        if "error" in response:
            print(f"  ❌ Error: {response['error']}")
        else:
            enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
            print(f"  ✅ Response received")
            print(f"  📝 Enhanced message: {enhanced_msg[:100]}...")
            
            # Analyze enhancement for combined areas
            combined_locations = ["San Francisco", "Los Angeles", "New York City", "Boston"]
            other_locations = ["Miami", "Orlando", "Seattle", "Portland"]
            
            combined_analysis = analyze_enhancement(text, enhanced_msg, combined_locations, should_be_enhanced=True)
            other_analysis = analyze_enhancement(text, enhanced_msg, other_locations, should_be_enhanced=False)
            
            print(f"  🎯 Combined area locations: {len(combined_analysis['locations_enhanced'])}/{len(combined_analysis['locations_found'])} enhanced")
            print(f"  🚫 Other locations: {len(other_analysis['locations_not_enhanced'])}/{len(other_analysis['locations_found'])} not enhanced")

def test_three_areas(auth_token: str):
    """Test with California, New York, and Florida areas of interest."""
    print("\n" + "="*60)
    print("TEST 4: California + New York + Florida areas_of_interest")
    print("="*60)
    
    three_areas = CALIFORNIA + NEW_YORK + FLORIDA
    
    for i, text in enumerate(TEST_TEXTS[:4], 1):
        print(f"\nTest {i}: {text}")
        response = make_api_request(text, three_areas, auth_token=auth_token)
        
        if "error" in response:
            print(f"  ❌ Error: {response['error']}")
        else:
            enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
            print(f"  ✅ Response received")
            print(f"  📝 Enhanced message: {enhanced_msg[:100]}...")
            
            # Analyze enhancement for three areas
            three_area_locations = ["San Francisco", "Los Angeles", "New York City", "Boston", "Miami", "Orlando"]
            other_locations = ["Seattle", "Portland", "Chicago", "Detroit"]
            
            three_analysis = analyze_enhancement(text, enhanced_msg, three_area_locations, should_be_enhanced=True)
            other_analysis = analyze_enhancement(text, enhanced_msg, other_locations, should_be_enhanced=False)
            
            print(f"  🎯 Three area locations: {len(three_analysis['locations_enhanced'])}/{len(three_analysis['locations_found'])} enhanced")
            print(f"  🚫 Other locations: {len(other_analysis['locations_not_enhanced'])}/{len(other_analysis['locations_found'])} not enhanced")

def test_edge_cases(auth_token: str):
    """Test edge cases and boundary conditions."""
    print("\n" + "="*60)
    print("TEST 5: Edge cases and boundary conditions")
    print("="*60)
    
    edge_cases = [
        "I visited San Diego (southern California) and Eureka (northern California).",
        "I went to Buffalo (northern NY) and New York City (southern NY).",
        "I traveled to Key West (southern Florida) and Jacksonville (northern Florida).",
        "I visited Tijuana (just south of California) and Reno (just east of California)."
    ]
    
    for i, text in enumerate(edge_cases, 1):
        print(f"\nEdge case {i}: {text}")
        response = make_api_request(text, CALIFORNIA, auth_token=auth_token)
        
        if "error" in response:
            print(f"  ❌ Error: {response['error']}")
        else:
            enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
            print(f"  ✅ Response received")
            print(f"  📝 Enhanced message: {enhanced_msg[:100]}...")
            
            # Analyze edge case enhancement
            if "San Diego" in text or "Eureka" in text:
                expected_locations = ["San Diego", "Eureka"]
                analysis = analyze_enhancement(text, enhanced_msg, expected_locations, should_be_enhanced=True)
                print(f"  🎯 California edge locations: {len(analysis['locations_enhanced'])}/{len(analysis['locations_found'])} enhanced")

def main():
    """Run all tests."""
    print("Areas of Interest API Testing Program")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print("Testing the new areas_of_interest parameter functionality")
    print("Updated for .env configuration system")
    
    # Get authentication token once at the start
    LOGIN_USERNAME = input("Enter API username: ")
    LOGIN_PASSWORD = input("Enter API password: ")
    AUTH_TOKEN = login_and_get_token(LOGIN_USERNAME, LOGIN_PASSWORD)
    print(f"✅ Auth Token obtained: {AUTH_TOKEN[:10]}...")
    
    try:
        # Run all tests
        test_no_areas_of_interest(AUTH_TOKEN)
        test_california_only(AUTH_TOKEN)
        test_california_and_newyork(AUTH_TOKEN)
        test_three_areas(AUTH_TOKEN)
        test_edge_cases(AUTH_TOKEN)
        
        print("\n" + "="*60)
        print("🎉 All tests completed!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
