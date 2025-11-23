from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "TransFlow API"
    APP_VERSION: str = "1.0.0"
    
    MONGO_URL: str = "mongodb://mongo:27017"
    MONGO_DB_NAME: str = "transflow_db"
    
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()