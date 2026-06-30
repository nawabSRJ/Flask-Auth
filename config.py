import os
class Config:
    DEBUG=False                                 # fallback if .env missing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')


class DevelopmentConfig(Config):
    DEBUG=True

class ProductionConfig(Config):
    DEBUG=False

