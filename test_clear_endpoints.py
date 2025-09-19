#!/usr/bin/env python3
"""
Test script for the new clear conversation history and wellness data endpoints.
This script demonstrates how to use the new clearing functionality.
"""

import requests
import json

# Base URL for the API (adjust if needed)
BASE_URL = "http://localhost:5000/api"

def test_clear_conversation_history(user_id="test_user"):
    """Test clearing conversation history for a user."""
    print(f"\n🗑️  Testing: Clear conversation history for user '{user_id}'")
    
    url = f"{BASE_URL}/conversations/clear"
    params = {"user_id": user_id}
    
    try:
        response = requests.delete(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def test_clear_specific_conversation(conversation_id="test_conversation_123"):
    """Test clearing a specific conversation."""
    print(f"\n🗑️  Testing: Clear specific conversation '{conversation_id}'")
    
    url = f"{BASE_URL}/conversations/{conversation_id}/clear"
    
    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def test_clear_wellness_data(user_id="test_user"):
    """Test clearing wellness data for a user."""
    print(f"\n🗑️  Testing: Clear wellness data for user '{user_id}'")
    
    url = f"{BASE_URL}/wellness/clear"
    params = {"user_id": user_id}
    
    try:
        response = requests.delete(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def test_clear_all_wellness_data():
    """Test clearing all wellness data (admin function)."""
    print(f"\n🗑️  Testing: Clear ALL wellness data (admin function)")
    
    url = f"{BASE_URL}/wellness/clear-all"
    
    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all tests."""
    print("🧪 Testing Clear Endpoints for Ruh App")
    print("=" * 50)
    
    # Test conversation clearing
    test_clear_conversation_history("user123")
    test_clear_specific_conversation("conv_456")
    
    # Test wellness data clearing
    test_clear_wellness_data("user123")
    test_clear_all_wellness_data()
    
    print("\n✅ Test script completed!")
    print("\n📝 Usage Examples:")
    print("1. Clear user's conversation history:")
    print("   DELETE /api/conversations/clear?user_id=USER_ID")
    print("\n2. Clear specific conversation:")
    print("   DELETE /api/conversations/CONVERSATION_ID/clear")
    print("\n3. Clear user's wellness data:")
    print("   DELETE /api/wellness/clear?user_id=USER_ID")
    print("\n4. Clear all wellness data (admin):")
    print("   DELETE /api/wellness/clear-all")

if __name__ == "__main__":
    main()