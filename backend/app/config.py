from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{os.getenv('USER')}@localhost:5432/swift_processing"
    )
    
    class Config:
        env_file = ".env"


settings = Settings()

