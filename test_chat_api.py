#!/usr/bin/env python3
"""
Test script for TraintiQ Chat API
Verifies that the chat system is working correctly.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000/api/chat"
FRONTEND_URL = "http://localhost:4200"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_chat_message():
    """Test sending a chat message"""
    print("\n💬 Testing chat message...")
    
    test_message = "Hello! What services does TraintiQ offer?"
    
    payload = {
        "message": test_message,
        "session_id": f"test_session_{int(time.time())}"
    }
    
    try:
        print(f"📤 Sending: {test_message}")
        response = requests.post(
            f"{API_BASE_URL}/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received:")
            print(f"📝 Message: {data['response'][:100]}...")
            print(f"🎯 Quick replies: {data.get('quick_replies', [])}")
            print(f"⚡ Model used: {data.get('model_used', 'N/A')}")
            print(f"🔢 Tokens used: {data.get('tokens_used', 'N/A')}")
            return True
        else:
            print(f"❌ Chat message failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat message error: {str(e)}")
        return False

def test_multiple_messages():
    """Test conversation flow with multiple messages"""
    print("\n🔄 Testing conversation flow...")
    
    session_id = f"test_conversation_{int(time.time())}"
    
    test_messages = [
        "Hi there!",
        "What are your pricing plans?",
        "Tell me more about the Professional plan",
        "How can I contact support?"
    ]
    
    success_count = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📤 Message {i}: {message}")
        
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/message",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response {i}: {data['response'][:80]}...")
                print(f"🎯 Quick replies: {data.get('quick_replies', [])[:3]}")
                success_count += 1
            else:
                print(f"❌ Message {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Message {i} error: {str(e)}")
    
    print(f"\n📊 Conversation test: {success_count}/{len(test_messages)} messages successful")
    return success_count == len(test_messages)

def check_frontend_accessibility():
    """Check if the frontend is accessible"""
    print("\n🌐 Checking frontend accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost:4200")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 TraintiQ Chat System Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Health Check
    test_results.append(test_health_check())
    
    # Test 2: Single Chat Message
    test_results.append(test_chat_message())
    
    # Test 3: Conversation Flow
    test_results.append(test_multiple_messages())
    
    # Test 4: Frontend Accessibility
    test_results.append(check_frontend_accessibility())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your chat system is working perfectly!")
        print("\n🔗 Quick Links:")
        print(f"   • Frontend: {FRONTEND_URL}")
        print(f"   • API Health: {API_BASE_URL}/health")
        print(f"   • Chat API: {API_BASE_URL}/message")
        
        print("\n💡 Next Steps:")
        print("   1. Open your browser to http://localhost:4200")
        print("   2. Look for the chat button in the bottom-right corner")
        print("   3. Click to start chatting with the AI assistant!")
        print("   4. Try asking about TraintiQ services, pricing, or support")
        
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting Tips:")
        print("   • Make sure both servers are running (Flask & Angular)")
        print("   • Check your OpenAI API key is configured correctly")
        print("   • Verify MySQL database is running and accessible")
        print("   • Check console logs for detailed error messages")

if __name__ == "__main__":
    main() 