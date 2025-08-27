#!/usr/bin/env python3
"""
Example usage of the areas_of_interest parameter in the chat/rag API endpoint.

This script demonstrates how to:
1. Make requests with no areas_of_interest (all entities processed)
2. Make requests with specific areas_of_interest (filtered entities)
3. Handle the API responses
4. Work with the new .env configuration system

Updated for the new backend configuration architecture.
"""

import requests
import json
import sys
from typing import List

# Configuration
API_BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Replace with actual token

# Example areas of interest
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

def make_rag_request(message: str, areas_of_interest=None):
    """Make a request to the chat/rag endpoint."""
    url = f"{API_BASE_URL}/chat/rag"
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
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
        response = requests.post(url, headers=headers, json=payload, timeout=60)  # Increased timeout for GeoNER
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

def analyze_enhancement(enhanced_text: str, expected_enhanced: List[str], expected_not_enhanced: List[str] = None):
    """Analyze the enhancement results and provide feedback."""
    print(f"📝 Enhanced message: {enhanced_text}")
    
    # Check expected enhanced locations
    print("\n🎯 Expected Enhanced Locations:")
    for location in expected_enhanced:
        # Look for the actual XML format: <LOC lat="..." lon="..." zoom_level="...">Location</LOC>
        if f'<LOC' in enhanced_text and location in enhanced_text:
            print(f"  ✅ {location} - Enhanced correctly")
        else:
            print(f"  ❌ {location} - Not enhanced (issue detected)")
    
    # Check expected non-enhanced locations
    if expected_not_enhanced:
        print("\n🚫 Expected Non-Enhanced Locations:")
        for location in expected_not_enhanced:
            # Look for the actual XML format: <LOC lat="..." lon="..." zoom_level="...">Location</LOC>
            if f'<LOC' in enhanced_text and location in enhanced_text:
                print(f"  ❌ {location} - Enhanced (should not be)")
            else:
                print(f"  ✅ {location} - Not enhanced (correct)")

def example_no_filtering():
    """Example: No geographic filtering - all entities processed."""
    print("="*60)
    print("EXAMPLE 1: No areas_of_interest (all entities processed)")
    print("="*60)
    
    message = "I visited San Francisco, New York City, and London last year."
    print(f"Input: {message}")
    
    response = make_rag_request(message)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
        ai_response = response.get('message', 'No response')
        
        print(f"✅ Success! API responded correctly.")
        print(f"🤖 AI response: {ai_response[:100]}...")
        
        # Analyze enhancement
        expected_enhanced = ["San Francisco", "New York City", "London"]
        analyze_enhancement(enhanced_msg, expected_enhanced)

def example_california_only():
    """Example: Only California entities processed."""
    print("\n" + "="*60)
    print("EXAMPLE 2: California areas_of_interest only")
    print("="*60)
    
    message = "I visited San Francisco, New York City, and London last year."
    print(f"Input: {message}")
    
    response = make_rag_request(message, CALIFORNIA)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
        ai_response = response.get('message', 'No response')
        
        print(f"✅ Success! API responded correctly.")
        print(f"🤖 AI response: {ai_response[:100]}...")
        
        # Analyze enhancement
        expected_enhanced = ["San Francisco"]  # California only
        expected_not_enhanced = ["New York City", "London"]  # Outside California
        analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)

def example_multiple_areas():
    """Example: Multiple areas of interest."""
    print("\n" + "="*60)
    print("EXAMPLE 3: California + New York areas_of_interest")
    print("="*60)
    
    message = "I visited San Francisco, New York City, and London last year."
    print(f"Input: {message}")
    
    combined_areas = CALIFORNIA + NEW_YORK
    response = make_rag_request(message, combined_areas)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
        ai_response = response.get('message', 'No response')
        
        print(f"✅ Success! API responded correctly.")
        print(f"🤖 AI response: {ai_response[:100]}...")
        
        # Analyze enhancement
        expected_enhanced = ["San Francisco", "New York City"]  # California + New York
        expected_not_enhanced = ["London"]  # Outside both areas
        analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)

def example_edge_case():
    """Example: Edge case with boundary locations."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Edge case - boundary locations")
    print("="*60)
    
    message = "I visited San Diego (southern CA), Eureka (northern CA), and Tijuana (Mexico)."
    print(f"Input: {message}")
    
    response = make_rag_request(message, CALIFORNIA)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
        ai_response = response.get('message', 'No response')
        
        print(f"✅ Success! API responded correctly.")
        print(f"🤖 AI response: {ai_response[:100]}...")
        
        # Analyze enhancement
        expected_enhanced = ["San Diego", "Eureka"]  # Within California
        expected_not_enhanced = ["Tijuana"]  # Outside California
        analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)

def example_three_areas():
    """Example: Three areas of interest."""
    print("\n" + "="*60)
    print("EXAMPLE 5: California + New York + Florida areas_of_interest")
    print("="*60)
    
    message = "I visited San Francisco, New York City, Miami, and London last year."
    print(f"Input: {message}")
    
    three_areas = CALIFORNIA + NEW_YORK + FLORIDA
    response = make_rag_request(message, three_areas)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        enhanced_msg = response.get('enhanced_user_message', 'No enhancement')
        ai_response = response.get('message', 'No response')
        
        print(f"✅ Success! API responded correctly.")
        print(f"🤖 AI response: {ai_response[:100]}...")
        
        # Analyze enhancement
        expected_enhanced = ["San Francisco", "New York City", "Miami"]  # All three areas
        expected_not_enhanced = ["London"]  # Outside all areas
        analyze_enhancement(enhanced_msg, expected_enhanced, expected_not_enhanced)

def main():
    """Run all examples."""
    print("Areas of Interest API Examples")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:10]}..." if AUTH_TOKEN != "YOUR_AUTH_TOKEN_HERE" else "Auth Token: NOT SET")
    print("\nUpdated for new .env configuration system")
    
    if AUTH_TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("\n⚠️  WARNING: Please set AUTH_TOKEN to a valid token before running examples.")
        print("You can get a token by logging in through the frontend or using the auth endpoint.")
        print("\nTo set the token:")
        print("1. Log in through the frontend")
        print("2. Check the browser console for the token")
        print("3. Update AUTH_TOKEN in this file")
        return
    
    try:
        # Run examples
        example_no_filtering()
        example_california_only()
        example_multiple_areas()
        example_edge_case()
        example_three_areas()
        
        print("\n" + "="*60)
        print("🎉 All examples completed!")
        print("="*60)
        print("\nKey Benefits of the New Configuration System:")
        print("✅ Environment-based configuration (.env files)")
        print("✅ Automatic secret management")
        print("✅ Azure-ready deployment")
        print("✅ Configurable areas of interest")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
