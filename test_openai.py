#!/usr/bin/env python3
"""
Test OpenAI API connectivity
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv('config.env')
load_dotenv()

def test_openai():
    print("🧪 Testing OpenAI API")
    print("=" * 30)
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key: {api_key[:20]}..." if api_key else "No API Key")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        from openai import OpenAI
        print("✅ OpenAI package imported successfully")
        
        # Try basic initialization
        print("🔧 Initializing OpenAI client...")
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Test API call
        print("📞 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, just testing!"}],
            max_tokens=10
        )
        
        print("✅ API call successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai() 