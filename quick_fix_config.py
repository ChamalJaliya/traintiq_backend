#!/usr/bin/env python3
"""
Quick fix script for TraintiQ configuration issues
This will help you resolve the OpenAI API and database connection problems
"""

import os
import sys
from pathlib import Path

def fix_configuration():
    """Fix common configuration issues"""
    
    print("🔧 TraintiQ Quick Configuration Fix")
    print("=" * 40)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_file = script_dir / 'config.env'
    
    print(f"📁 Using config file: {config_file}")
    
    # Read current config
    current_config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    current_config[key] = value
    
    print("\n🔍 Current Issues Detected:")
    
    # Check OpenAI API Key
    openai_key = current_config.get('OPENAI_API_KEY', '')
    if not openai_key or 'placeholder' in openai_key or 'your_openai' in openai_key:
        print("❌ OpenAI API Key: Not configured (shows as 'unavailable')")
    else:
        print("✅ OpenAI API Key: Configured")
    
    # Check Database
    db_url = current_config.get('DATABASE_URL', '')
    if 'sqlite:///traintiq.db' in db_url:
        print("✅ Database: Using SQLite (should work)")
    else:
        print("⚠️  Database: Using MySQL (check connection)")
    
    print("\n🛠️ Solutions:")
    print("1. 🔑 To fix OpenAI API:")
    print("   - Get your API key from: https://platform.openai.com/api-keys")
    print("   - Edit config.env and replace the OPENAI_API_KEY value")
    print("   - Example: OPENAI_API_KEY=sk-your-actual-key-here")
    
    print("\n2. 🗄️ Database is already set to SQLite (should work)")
    print("   - If you want MySQL, make sure MySQL is running")
    print("   - Check credentials in config.env")
    
    print("\n3. 🚀 Test the fixes:")
    print("   - Restart your Flask server")
    print("   - Visit: http://localhost:5000/api/chat/health")
    
    # Option to interactively set API key
    print("\n" + "="*40)
    update = input("Would you like to set your OpenAI API key now? (y/n): ").lower().strip()
    
    if update == 'y':
        print("\n🔑 Setting OpenAI API Key:")
        api_key = input("Enter your OpenAI API key (starts with 'sk-'): ").strip()
        
        if api_key and api_key.startswith('sk-'):
            # Update config file
            lines_to_write = []
            
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        lines_to_write.append(f'OPENAI_API_KEY={api_key}\n')
                    else:
                        lines_to_write.append(line)
            
            with open(config_file, 'w') as f:
                f.writelines(lines_to_write)
            
            print("✅ OpenAI API key updated successfully!")
            print("🔄 Please restart your Flask server to apply changes")
            
        else:
            print("❌ Invalid API key format. OpenAI keys start with 'sk-'")
    
    print("\n📋 Quick Test Commands:")
    print("   python run.py                    # Start server")
    print("   curl http://localhost:5000/api/chat/health  # Test health")
    
    print("\n🎉 Configuration fix complete!")

def check_current_status():
    """Check current system status"""
    
    print("🔍 Current System Status Check")
    print("=" * 30)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv('config.env')
    
    # Check OpenAI
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key and openai_key.startswith('sk-') and 'placeholder' not in openai_key:
        print("✅ OpenAI API Key: Configured")
        
        # Test API connection
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            print("✅ OpenAI API: Connection successful")
        except Exception as e:
            print(f"❌ OpenAI API: Connection failed - {str(e)}")
    else:
        print("❌ OpenAI API Key: Not configured or invalid")
    
    # Check Database
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from config import Config
        from sqlalchemy import text
        
        app = Flask(__name__)
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            print("✅ Database: Connection successful")
    except Exception as e:
        print(f"❌ Database: Connection failed - {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_current_status()
    else:
        fix_configuration() 