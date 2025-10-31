from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{os.getenv('USER')}@localhost:5432/swift_processing"
    )
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure DATABASE_URL uses asyncpg driver
        if self.DATABASE_URL.startswith('postgresql://'):
            self.DATABASE_URL = self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)


settings = Settings()

