import pymysql
import json
from config import Config

def check_database():
    # Connect to MySQL
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor  # Return results as dictionaries
    )
    
    try:
        with connection.cursor() as cursor:
            # Show all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("\n📊 Tables in database:")
            for table in tables:
                table_name = table['Tables_in_' + Config.MYSQL_DB]
                print(f"\n📋 Table: {table_name}")
                
                # Show table structure
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print("\nColumns:")
                for col in columns:
                    print(f"  - {col['Field']}: {col['Type']}")
                
                # Show records
                cursor.execute(f"SELECT * FROM {table_name}")
                records = cursor.fetchall()
                print(f"\nFound {len(records)} records:")
                
                if len(records) > 0:
                    for record in records[:3]:  # Show first 3 records
                        print("\n🔍 Record:")
                        for key, value in record.items():
                            if isinstance(value, (str, bytes)) and value.startswith('{'):
                                try:
                                    # Try to pretty print JSON fields
                                    parsed = json.loads(value)
                                    print(f"  {key}:")
                                    print(json.dumps(parsed, indent=2))
                                except:
                                    print(f"  {key}: {value}")
                            else:
                                print(f"  {key}: {value}")
                print("\n" + "="*50)
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    check_database() 