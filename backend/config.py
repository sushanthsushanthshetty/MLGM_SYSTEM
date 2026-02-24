# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Flask Configuration
# =====================================================

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mlgms-secret-key-2026-government-portal'
    
    # MySQL Database Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''  # Default XAMPP has no password
    MYSQL_DB = 'mlgms_db'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # CORS Configuration
    CORS_ORIGINS = '*'
    
    # Security
    WTF_CSRF_ENABLED = False  # Disabled for API
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with environment variables for production
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'mlgms_db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MYSQL_DB = 'mlgms_db_test'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}