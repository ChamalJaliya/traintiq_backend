from app import create_app, db
import pymysql
from config import Config

def init_database():
    # First, create the database if it doesn't exist
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD
    )
    try:
        with connection.cursor() as cursor:
            # Create database
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}')
            print(f"✅ Database '{Config.MYSQL_DB}' created or already exists")
            
            # Switch to the database
            cursor.execute(f'USE {Config.MYSQL_DB}')
            
            # Create companies table with JSON columns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    _id VARCHAR(24) PRIMARY KEY,
                    basicInfo JSON,
                    operational JSON,
                    contact JSON,
                    financials JSON,
                    descriptive JSON,
                    relationships JSON,
                    governance JSON,
                    digitalPresence JSON,
                    scrapedData JSON,
                    meta_info JSON,
                    customSections JSON
                )
            """)
            print("✅ Companies table created!")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return
    finally:
        connection.close()

    # Initialize Flask app context
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("✅ SQLAlchemy setup complete!")
        except Exception as e:
            print(f"❌ Error with SQLAlchemy setup: {e}")

if __name__ == "__main__":
    init_database() 