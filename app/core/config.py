from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "default-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/talf_solar"
    REDIS_URL: str = "redis://localhost:6379/0"
    ENCRYPTION_KEY: str = "default-encryption-key="
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()