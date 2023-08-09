from dotenv import load_dotenv
from pydantic_settings import BaseSettings

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
    FACEBOOK_CLIENT_ID: str
    FACEBOOK_CLIENT_SECRET: str
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    PORT: int = 8000
    REDIS_PASSWORD: str
    REDIS_PORT: str
    REDIS_HOST: str
    EMBEDDINGS_GRPC_HOST: str
    EMBEDDINGS_GRPC_PORT: str
    USE_ALEMBIC: bool = False
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    STRIPE_HOST: str
    STRIPE_KEY: str
    STRIPE_CANCEL_URL: str
    STRIPE_SUCCESS_URL: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_CONNECT_CLIENT_ID: str
    DISCORD_TOKEN: str
    OPENAI_API_KEY: str
    LLM: str


settings = Settings()
