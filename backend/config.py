class Config:
    SECRET_KEY = "super-secret-key-for-mad2"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "jwt-super-secret-key"
    
    # Celery & Redis Setup
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    
    # Caching Setup
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/3"
    CACHE_DEFAULT_TIMEOUT = 60