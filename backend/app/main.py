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

from app import api
from app.db import clear_db, create_superuser, init_db, wait_for_db, wait_for_redis
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


meter = metrics.get_meter(settings.BACKEND_APP_NAME)

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

    if settings.DEV:
        user = await create_superuser()
        logger.info(
            json.dumps(
                jsonable_encoder(user, exclude={"creator", "sessions"}), indent=2
            )
        )

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
app.include_router(router=api.users_router)


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
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEV,
        reload_dirs=reload_dirs,
    )
