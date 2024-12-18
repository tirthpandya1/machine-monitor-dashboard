from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Machine monitoring settings
    NUM_MACHINES: int = 5
    METRICS_UPDATE_INTERVAL: float = 2.0
    
    # Kafka and streaming settings
    KAFKA_BOOTSTRAP_SERVERS: str = 'localhost:9092'
    
    # Prometheus settings
    PROMETHEUS_PORT: int = 9090
    
    # Database settings
    DATABASE_URL: str = 'sqlite:///./machine_monitor.db'
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Create a singleton settings object
settings = Settings()
