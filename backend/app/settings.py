from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    AUTH_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    PORT: int = 8000
    REDIS_PASSWORD: str
    REDIS_PORT: str
    USE_ALEMBIC: bool = False
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str


settings = Settings()
