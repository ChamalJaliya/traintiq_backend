import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # MySQL configuration
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'lenacjnv7'
    MYSQL_HOST = 'localhost'
    MYSQL_DB = 'traintiq_db'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Documentation
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    
    # CORS
    CORS_HEADERS = 'Content-Type' 