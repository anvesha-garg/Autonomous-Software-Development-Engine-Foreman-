from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Foreman API"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.groq.com/openai/v1"
    MODEL_NAME: str = "openai/gpt-oss-120b"
    DATABASE_URL: str = "sqlite+aiosqlite:///./foreman.db"
    DOCKER_SANDBOX_IMAGE: str = "python:3.12-slim"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()