from app import create_app, db

def setup_database():
    """Setup the database by dropping and recreating all tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Dropping all tables...")
            db.drop_all()
            print("Creating all tables...")
            db.create_all()
            print("Database setup completed successfully!")
        except Exception as e:
            print(f"Error: {e}")
            print("\nPossible solutions:")
            print("1. Make sure MySQL server is running")
            print("2. Check if the username and password in config.py are correct")
            print("3. Verify that MySQL is running on the specified port (default: 3306)")

if __name__ == "__main__":
    setup_database() 