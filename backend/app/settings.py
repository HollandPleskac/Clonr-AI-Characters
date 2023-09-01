# mypy: ignore-errors
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    NEXTAUTH_SECRET: str
    NEXTAUTH_URL: str
    PORT: int
    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_HOST: str
    EMBEDDINGS_GRPC_HOST: str
    EMBEDDINGS_GRPC_PORT: int
    USE_ALEMBIC: bool = False
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    STRIPE_HOST: str
    STRIPE_API_KEY: str
    STRIPE_CANCEL_URL: str
    STRIPE_SUCCESS_URL: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_CONNECT_CLIENT_ID: str
    OPENAI_API_KEY: str
    LLM: str
    OTEL_EXPORTER_OTLP_ENDPOINT: str
    APP_NAME: str = "clonr.server"
    DEV: bool = True
    IP_ADDR_RATE_LIMIT: str
    HOST: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    NUM_FREE_MESSAGES: int


settings = Settings()
