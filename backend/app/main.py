import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from opentelemetry import metrics

from app import api, schemas
from app.auth.users import (
    auth_backend,
    discord_oauth_client,
    facebook_oauth_client,
    google_oauth_client,
    reddit_oauth_client,
)
from app.db import clear_db, create_superuser, init_db, wait_for_db, wait_for_redis
from app.deps.users import fastapi_users
from app.embedding import wait_for_embedding
from app.middleware.rate_limiter import IpAddrRateLimitMiddleware
from app.middleware.tracing import setup_tracing
from app.settings import settings

if not settings.DEV:
    import sentry_sdk

    sentry_sdk.init(
        dsn="https://foo@sentry.io/123",
        traces_sample_rate=1.0,
    )


meter = metrics.get_meter(settings.APP_NAME)

req_meter = meter.create_counter(
    name="io_requests_total",
    description="Total count of requests by method and path.",
    unit="responses",
)

hist_meter = meter.create_histogram(
    name="jonny_time_requests_total",
    description="Total count of requests by method and path.",
    unit="responses",
)


async def run_async_upgrade():
    cmd = "alembic upgrade head"
    await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )


async def run_async_downgrade():
    cmd = "alembic downgrade base"
    await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Waiting for db...")
    await wait_for_db()

    logger.info("Waiting for redis...")
    await wait_for_redis()

    logger.info("Waiting for Embedding gRPC server...")
    name = await wait_for_embedding()
    logger.info(f"gRPC server up and running with model: {name}")

    if settings.USE_ALEMBIC:
        logger.info("Running migration upgrades")
        await run_async_upgrade()
    else:
        # If not using Alembic run this
        logger.info("Creating database")
        await init_db()

    logger.info(f"Creating superuser: {settings.SUPERUSER_EMAIL}")
    user = await create_superuser()
    logger.info(json.dumps(jsonable_encoder(user, exclude={"creator"}), indent=2))

    yield

    if settings.USE_ALEMBIC:
        logger.warning("Running migration downgrades")
        await run_async_downgrade()
    else:
        logger.warning("Erasing database")
        await clear_db()
    logger.warning("Clearing Redis cache")
    # await clear_redis()


app = FastAPI(lifespan=lifespan)

if not settings.DEV:
    app.add_middleware(
        IpAddrRateLimitMiddleware, rate_limit=settings.IP_ADDR_RATE_LIMIT
    )

app.include_router(router=api.creator_router)
app.include_router(router=api.clones_router)
app.include_router(router=api.conversations_router)
app.include_router(router=api.tags_router)
app.include_router(router=api.stripe_router)
app.include_router(router=api.subscriptions_router)
app.include_router(router=api.signups_router)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/cookies", tags=["auth"]
)

if settings.DEV:
    app.include_router(
        fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
        prefix="/auth",
        tags=["auth"],
    )

app.include_router(
    fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        settings.AUTH_SECRET,
        redirect_url=settings.OAUTH_REDIRECT_URL,
    ),
    prefix="/auth/google",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        facebook_oauth_client,
        auth_backend,
        settings.AUTH_SECRET,
        redirect_url=settings.OAUTH_REDIRECT_URL,
    ),
    prefix="/auth/facebook",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        reddit_oauth_client,
        auth_backend,
        settings.AUTH_SECRET,
        redirect_url=settings.OAUTH_REDIRECT_URL,
    ),
    prefix="/auth/reddit",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        discord_oauth_client,
        auth_backend,
        settings.AUTH_SECRET,
        redirect_url=settings.OAUTH_REDIRECT_URL,
    ),
    prefix="/auth/discord",
    tags=["auth"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=200)
def health_check():
    return {"success": True}


setup_tracing(app=app)


if __name__ == "__main__":
    p = Path(__file__).parent.parent
    reload_dirs = [str((p / x).resolve()) for x in ["app", "clonr"]]
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEV,
        reload_dirs=reload_dirs,
    )
