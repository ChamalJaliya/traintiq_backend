#!/usr/bin/env python3
"""
MySQL Database Setup Script for TraintiQ
This script will create the MySQL database and test the connection
"""

import os
import sys
import mysql.connector
from dotenv import load_dotenv

def setup_mysql_database():
    """Setup MySQL database for TraintiQ"""
    
    print("🗄️ TraintiQ MySQL Database Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    load_dotenv('config.env')
    
    # Get MySQL configuration
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', 'lenacjnv7')
    mysql_database = os.getenv('MYSQL_DATABASE', 'traintiq_db')
    
    print(f"📊 Database Configuration:")
    print(f"  Host: {mysql_host}")
    print(f"  User: {mysql_user}")
    print(f"  Database: {mysql_database}")
    print(f"  Password: {'*' * len(mysql_password)}")
    
    try:
        # Connect to MySQL server (without specifying database)
        print("\n🔌 Connecting to MySQL server...")
        
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password
        )
        
        cursor = connection.cursor()
        print("✅ Connected to MySQL server successfully!")
        
        # Create database if it doesn't exist
        print(f"\n🏗️ Creating database '{mysql_database}' if it doesn't exist...")
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database}")
        cursor.execute(f"USE {mysql_database}")
        
        print(f"✅ Database '{mysql_database}' is ready!")
        
        # Test the full connection string
        print("\n🧪 Testing full DATABASE_URL connection...")
        
        test_connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        
        test_cursor = test_connection.cursor()
        test_cursor.execute("SELECT 1 as test")
        result = test_cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Full database connection test successful!")
        
        # Show existing tables
        test_cursor.execute("SHOW TABLES")
        tables = test_cursor.fetchall()
        
        print(f"\n📋 Existing tables in '{mysql_database}':")
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (No tables yet - will be created when Flask app starts)")
        
        # Cleanup
        test_cursor.close()
        test_connection.close()
        cursor.close()
        connection.close()
        
        print(f"\n🎉 MySQL setup completed successfully!")
        print(f"\n📝 Your DATABASE_URL is:")
        print(f"   mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_database}")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ MySQL Error: {e}")
        
        if e.errno == 1045:  # Access denied
            print("\n🔧 Possible Solutions:")
            print("1. Check your MySQL password in config.env")
            print("2. Make sure MySQL server is running")
            print("3. Verify MySQL user has proper permissions")
            
        elif e.errno == 2003:  # Can't connect to server
            print("\n🔧 Possible Solutions:")
            print("1. Make sure MySQL server is running")
            print("2. Check if MySQL is listening on port 3306")
            print("3. Verify the host address (localhost vs 127.0.0.1)")
            
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def check_mysql_status():
    """Check current MySQL connection status"""
    
    print("🔍 MySQL Connection Status Check")
    print("=" * 30)
    
    # Load environment
    load_dotenv()
    load_dotenv('config.env')
    
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', 'lenacjnv7')
    mysql_database = os.getenv('MYSQL_DATABASE', 'traintiq_db')
    
    try:
        # Test connection
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        
        cursor = connection.cursor()
        
        # Get server info
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        # Get database info
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        
        print(f"✅ MySQL Server: {version[0] if version else 'Unknown'}")
        print(f"✅ Current Database: {current_db[0] if current_db else 'None'}")
        print(f"✅ Connection: Successful")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ Tables: {len(tables)} found")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_mysql_status()
    else:
        success = setup_mysql_database()
        
        if success:
            print("\n🚀 Next Steps:")
            print("1. Run: python create_chat_tables.py")
            print("2. Run: python run.py")
            print("3. Test: http://localhost:5000/api/chat/health")
        else:
            print("\n⚠️  Please fix the MySQL connection issues above")
            sys.exit(1) 