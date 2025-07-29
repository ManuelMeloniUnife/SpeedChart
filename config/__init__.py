# config/__init__.py
"""Configuration module for SpeedChart application"""

import os

class Config:
    """Base configuration class"""
    
    # Percorso assoluto alla cartella data
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')
    
    # Database configuration
    DATABASE_PATH = os.path.join(DATA_DIR, 'speedchart.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask configuration
    SECRET_KEY = 'speedchart-secret-key-change-in-production'
    
    # Application configuration
    DEFAULT_WHEEL_CIRCUMFERENCE = 1.52  # meters
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.STATIC_IMG_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
