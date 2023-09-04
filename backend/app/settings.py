# mypy: ignore-errors
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    # Redis
    REDIS_PORT: str
    REDIS_PASSWORD: str
    REDIS_HOST: str

    # Auth
    NEXTAUTH_SECRET: str
    NEXTAUTH_URL: str

    # Stripe payments
    STRIPE_HOST: str
    STRIPE_API_KEY: str
    STRIPE_CANCEL_URL: str
    STRIPE_SUCCESS_URL: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_CONNECT_CLIENT_ID: str

    # Network
    EMBEDDINGS_GRPC_HOST: str
    EMBEDDINGS_GRPC_PORT: int
    OTEL_EXPORTER_OTLP_ENDPOINT: str

    # Backend
    BACKEND_PORT: int
    BACKEND_HOST: str
    IP_ADDR_RATE_LIMIT: str
    NUM_FREE_MESSAGES: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    USE_ALEMBIC: bool = False
    BACKEND_APP_NAME: str = "clonr.server"

    # LLMs
    OPENAI_API_KEY: str
    LLM: str

    # Misc
    DEV: bool


settings = Settings()
