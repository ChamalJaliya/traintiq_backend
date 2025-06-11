#!/usr/bin/env python3
"""
Script to create chat-related database tables
Run this script to set up the chat functionality in your database
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.chat import ChatConversation, ChatMessage, ChatAnalytics

def create_chat_tables():
    """Create all chat-related database tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating chat database tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['chat_conversations', 'chat_messages', 'chat_analytics']
            created_tables = [table for table in expected_tables if table in tables]
            
            print(f"✅ Successfully created tables: {', '.join(created_tables)}")
            
            if len(created_tables) == len(expected_tables):
                print("✅ All chat tables created successfully!")
                
                # Create initial analytics record for today
                from datetime import date
                today = date.today()
                existing_analytics = ChatAnalytics.query.filter_by(date=today).first()
                
                if not existing_analytics:
                    initial_analytics = ChatAnalytics(
                        date=today,
                        total_conversations=0,
                        total_messages=0,
                        total_tokens_used=0,
                        unique_sessions=0
                    )
                    db.session.add(initial_analytics)
                    db.session.commit()
                    print("✅ Initial analytics record created")
                
            else:
                missing_tables = [table for table in expected_tables if table not in created_tables]
                print(f"⚠️  Some tables were not created: {', '.join(missing_tables)}")
                
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            db.session.rollback()
            return False
            
    return True

def check_openai_setup():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key is configured")
        return True
    else:
        print("⚠️  OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable")
        print("   You can get an API key from: https://platform.openai.com/api-keys")
        return False

def main():
    """Main function to set up chat functionality"""
    print("=== TraintiQ Chat Setup ===")
    print()
    
    # Check environment variables
    print("1. Checking environment configuration...")
    openai_configured = check_openai_setup()
    
    print()
    print("2. Setting up database tables...")
    tables_created = create_chat_tables()
    
    print()
    print("=== Setup Summary ===")
    print(f"Database tables: {'✅ Created' if tables_created else '❌ Failed'}")
    print(f"OpenAI API key: {'✅ Configured' if openai_configured else '⚠️  Not configured'}")
    
    if tables_created and openai_configured:
        print()
        print("🎉 Chat functionality is ready to use!")
        print("You can now start the Flask server and test the chat API")
    elif tables_created:
        print()
        print("⚠️  Database is ready, but you need to configure OpenAI API key")
        print("Add OPENAI_API_KEY to your .env file to enable AI responses")
    else:
        print()
        print("❌ Setup incomplete. Please check the errors above")

if __name__ == "__main__":
    main() 