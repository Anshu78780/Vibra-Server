import os

class Config:
    """Configuration class for the Flask app"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'  # Default to False for production
    
    # Server settings
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))  # Render uses PORT environment variable
    
    # yt-dlp settings
    MAX_SEARCH_RESULTS = 50
    DEFAULT_SEARCH_RESULTS = 10
    
    # YouTube authentication (for avoiding bot detection)
    YOUTUBE_COOKIES = os.environ.get('YOUTUBE_COOKIES')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
