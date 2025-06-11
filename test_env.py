#!/usr/bin/env python3
"""
Test environment variable loading
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    print("🧪 Testing Environment Variable Loading")
    print("=" * 40)
    
    # Before loading
    print("Before loading dotenv:")
    print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
    print(f"  OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'NOT SET')}")
    
    # Load .env files in same order as app
    print("\nLoading .env files...")
    result1 = load_dotenv('config.env')  # Load config.env FIRST (higher priority)
    print(f"  load_dotenv('config.env') result: {result1}")
    
    result2 = load_dotenv()  # Load .env as backup
    print(f"  load_dotenv() result: {result2}")
    
    # After loading
    print("\nAfter loading dotenv:")
    print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
    print(f"  OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'NOT SET')}")
    print(f"  SECRET_KEY: {os.environ.get('SECRET_KEY', 'NOT SET')}")
    print(f"  MYSQL_HOST: {os.environ.get('MYSQL_HOST', 'NOT SET')}")
    
    # Test config construction
    print("\n🔧 Testing Config Construction:")
    from config import Config
    
    print(f"  Config.SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")
    print(f"  Config.SECRET_KEY: {Config.SECRET_KEY[:10]}...")
    
    # Check files exist
    print("\n📁 Checking Files:")
    import pathlib
    
    env_file = pathlib.Path('.env')
    config_env_file = pathlib.Path('config.env')
    
    print(f"  .env exists: {env_file.exists()}")
    print(f"  config.env exists: {config_env_file.exists()}")
    
    if config_env_file.exists():
        print(f"  config.env size: {config_env_file.stat().st_size} bytes")
        
        # Show first few lines
        print("  config.env first 5 lines:")
        with open('config.env', 'r') as f:
            for i, line in enumerate(f):
                if i < 5:
                    print(f"    {i+1}: {line.rstrip()}")

if __name__ == "__main__":
    test_env_loading() 