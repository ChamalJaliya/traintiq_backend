import os
from dotenv import load_dotenv

# Load local config first, then Docker config as backup
load_dotenv('config.env.local')  # Local development
load_dotenv('config.env')        # Docker config as backup  
load_dotenv()                    # .env as final backup

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or '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'
    
    # MySQL configuration - use environment variables or defaults
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'lenacjnv7')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql')  # Docker service name
    MYSQL_DB = os.environ.get('MYSQL_DATABASE', 'traintiq_db')
    
    # SQLAlchemy - check for full DATABASE_URL first, then build from parts
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or 
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Documentation
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    
    # CORS
    CORS_HEADERS = 'Content-Type' 