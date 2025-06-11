from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv
import os

# Load environment variables - prioritize config.env
load_dotenv('config.env')  # Load config.env file FIRST (higher priority)
load_dotenv()  # Load .env file as backup

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Load configuration
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS to allow all origins
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Fields"]
        }
    })

    # Import and register blueprints
    from app.api import api
    from app.api.company_routes import company_bp
    from app.api.companies_routes import companies_bp
    from app.api.chat_routes import chat_bp

    api.init_app(app)
    app.register_blueprint(company_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(chat_bp, url_prefix='/api')

    # Add health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for Docker and monitoring"""
        try:
            from sqlalchemy import text
            # Test database connection
            db.session.execute(text('SELECT 1'))
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500

    # Import models to ensure they are created
    from app.models.chat import ChatConversation, ChatMessage, ChatAnalytics

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
