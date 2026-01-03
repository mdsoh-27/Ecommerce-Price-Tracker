"""
Configuration management for E-commerce Price Tracker
Loads settings from environment variables with sensible defaults
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database settings
    DB_PATH = os.getenv('DB_PATH', 'tracker.db')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 3600))
    CACHE_SCRAPER_TIMEOUT = int(os.getenv('CACHE_SCRAPER_TIMEOUT', 3600))  # 1 hour
    CACHE_DB_TIMEOUT = int(os.getenv('CACHE_DB_TIMEOUT', 300))  # 5 minutes
    
    # Scraper settings
    SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', 10))  # seconds
    SCRAPER_MAX_RETRIES = int(os.getenv('SCRAPER_MAX_RETRIES', 3))
    SCRAPER_RETRY_DELAY = int(os.getenv('SCRAPER_RETRY_DELAY', 2))  # seconds
    
    # Scheduler settings
    SCHEDULER_INTERVAL_HOURS = int(os.getenv('SCHEDULER_INTERVAL_HOURS', 6))
    SCHEDULER_PRODUCTS = os.getenv('SCHEDULER_PRODUCTS', 'iphone,laptop,headphones').split(',')
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append(f"Invalid PORT: {cls.PORT}. Must be between 1 and 65535.")
        
        if cls.CACHE_DEFAULT_TIMEOUT < 0:
            errors.append(f"Invalid CACHE_DEFAULT_TIMEOUT: {cls.CACHE_DEFAULT_TIMEOUT}. Must be >= 0.")
        
        if cls.SCRAPER_MAX_RETRIES < 0:
            errors.append(f"Invalid SCRAPER_MAX_RETRIES: {cls.SCRAPER_MAX_RETRIES}. Must be >= 0.")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
        
        return True
