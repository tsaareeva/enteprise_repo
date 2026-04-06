from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MODE: str = "mock"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    EMAIL_QUEUE: str = "email.queue"
    REPORT_QUEUE: str = "report.queue"
    CUSTOMER_TOPIC: str = "customer.events.topic"

    DATABASE_URL: str = "sqlite+aiosqlite:///./customers.db"

    class Config:
        env_file = ".env"

settings = Settings()