#!/usr/bin/env python3
"""
Secure environment setup script for TraintiQ Chat Bot
This script helps you safely configure your OpenAI API key and other environment variables
"""

import os
import getpass
from pathlib import Path

def setup_environment():
    """Setup environment variables securely"""
    
    print("🔐 TraintiQ Chat Bot - Secure Environment Setup")
    print("=" * 50)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    env_file = script_dir / '.env'
    
    # Check if .env file exists
    if env_file.exists():
        print(f"✅ Found existing .env file at: {env_file}")
        overwrite = input("Do you want to update the existing .env file? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    else:
        print(f"📝 Creating new .env file at: {env_file}")
    
    # Collect environment variables
    env_vars = {}
    
    print("\n🔑 OpenAI Configuration")
    print("-" * 30)
    
    # Get OpenAI API key securely
    while True:
        api_key = getpass.getpass("Enter your OpenAI API key (input will be hidden): ").strip()
        if api_key:
            if api_key.startswith('sk-'):
                env_vars['OPENAI_API_KEY'] = api_key
                print("✅ OpenAI API key added")
                break
            else:
                print("❌ Invalid API key format. OpenAI keys start with 'sk-'")
        else:
            print("❌ API key cannot be empty")
    
    print("\n🗄️ Database Configuration")
    print("-" * 30)
    
    # Database URL
    db_host = input("Database host [localhost]: ").strip() or "localhost"
    db_port = input("Database port [3306]: ").strip() or "3306"
    db_user = input("Database username: ").strip()
    db_password = getpass.getpass("Database password (input will be hidden): ").strip()
    db_name = input("Database name [traintiq_db]: ").strip() or "traintiq_db"
    
    if db_user and db_password:
        env_vars['DATABASE_URL'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print("✅ Database configuration added")
    
    print("\n🌐 Application Configuration")
    print("-" * 30)
    
    # Flask environment
    flask_env = input("Flask environment [development]: ").strip() or "development"
    env_vars['FLASK_ENV'] = flask_env
    
    # Secret key
    secret_key = input("Secret key (leave empty to generate): ").strip()
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print("✅ Generated secure secret key")
    env_vars['SECRET_KEY'] = secret_key
    
    # CORS origins
    cors_origins = input("CORS origins [http://localhost:4200]: ").strip() or "http://localhost:4200"
    env_vars['CORS_ORIGINS'] = cors_origins
    
    # Log level
    log_level = input("Log level [INFO]: ").strip() or "INFO"
    env_vars['LOG_LEVEL'] = log_level
    
    # Write to .env file
    try:
        with open(env_file, 'w') as f:
            f.write("# TraintiQ Chat Bot Environment Configuration\n")
            f.write("# Generated automatically - DO NOT COMMIT THIS FILE\n\n")
            
            f.write("# OpenAI Configuration\n")
            f.write(f"OPENAI_API_KEY={env_vars['OPENAI_API_KEY']}\n\n")
            
            if 'DATABASE_URL' in env_vars:
                f.write("# Database Configuration\n")
                f.write(f"DATABASE_URL={env_vars['DATABASE_URL']}\n\n")
            
            f.write("# Flask Configuration\n")
            f.write(f"FLASK_ENV={env_vars['FLASK_ENV']}\n")
            f.write(f"SECRET_KEY={env_vars['SECRET_KEY']}\n\n")
            
            f.write("# CORS Configuration\n")
            f.write(f"CORS_ORIGINS={env_vars['CORS_ORIGINS']}\n\n")
            
            f.write("# Logging\n")
            f.write(f"LOG_LEVEL={env_vars['LOG_LEVEL']}\n")
        
        print(f"\n✅ Environment file created successfully!")
        print(f"📁 Location: {env_file}")
        
        # Set proper file permissions (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(env_file, 0o600)  # Read/write for owner only
            print("🔒 File permissions set to owner-only access")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {str(e)}")
        return
    
    print("\n🔒 Security Recommendations")
    print("-" * 30)
    print("1. ✅ Never commit the .env file to version control")
    print("2. ✅ Regularly rotate your OpenAI API key")
    print("3. ✅ Use different API keys for development and production")
    print("4. ✅ Monitor your OpenAI usage and billing")
    print("5. ✅ Use strong database passwords")
    
    print("\n🚀 Next Steps")
    print("-" * 30)
    print("1. Run: python create_chat_tables.py")
    print("2. Run: python run.py")
    print("3. Test the chat API at: http://localhost:5000/api/chat/health")
    
    print("\n🎉 Setup complete! Your chat bot is ready to use GPT-4!")

def verify_setup():
    """Verify the environment setup"""
    
    print("\n🔍 Verifying Environment Setup")
    print("-" * 30)
    
    # Check if .env file exists
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key.startswith('sk-'):
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not configured or invalid")
        return False
    
    # Check database URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print("✅ Database URL configured")
    else:
        print("⚠️  Database URL not configured")
    
    # Test OpenAI connection
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        print("✅ OpenAI API connection successful")
        print(f"✅ Using model: gpt-4-turbo-preview")
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False
    
    print("\n🎉 Environment verification successful!")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_setup()
    else:
        setup_environment()
        
        # Ask if user wants to verify
        print()
        verify = input("Do you want to verify the setup now? (y/n): ").lower().strip()
        if verify == 'y':
            verify_setup() 