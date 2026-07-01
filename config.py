import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG       = False
    SECRET_KEY  = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False