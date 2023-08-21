import asyncio
import json
import logging
import math
import random
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from opentelemetry import metrics

from app import api, deps, models, schemas
from app.auth.users import (
    auth_backend,
    discord_oauth_client,
    facebook_oauth_client,
    google_oauth_client,
    reddit_oauth_client,
)
from app.db import (
    clear_db,
    clear_redis,
    create_superuser,
    init_db,
    wait_for_db,
    wait_for_redis,
)
from app.deps.users import fastapi_users
from app.embedding import wait_for_embedding
from app.settings import settings
from app.tracing import setup_tracing

# import sentry_sdk
# sentry_sdk.init(
#     dsn="https://foo@sentry.io/123",
#     traces_sample_rate=1.0,
# )


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


async def moderation_middleware(
    request: Request, user: models.User = Depends(deps.get_current_active_user)
):
    if user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned!")
    return request


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
    await clear_redis()


app = FastAPI(lifespan=lifespan)
app.include_router(router=api.creator_router)
app.include_router(router=api.clones_router)
app.include_router(router=api.conversations_router)
app.include_router(router=api.tags_router)
app.include_router(router=api.stripe_router)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/cookies", tags=["auth"]
)
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
        google_oauth_client, auth_backend, settings.AUTH_SECRET
    ),
    prefix="/auth/google",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        facebook_oauth_client, auth_backend, settings.AUTH_SECRET
    ),
    prefix="/auth/facebook",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        reddit_oauth_client, auth_backend, settings.AUTH_SECRET
    ),
    prefix="/auth/reddit",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        discord_oauth_client, auth_backend, settings.AUTH_SECRET
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


@app.get("/health")
def health_check():
    return {"success": True}


# Below are temporary just for running Locust
def box_muller():
    R = math.sqrt(-2 * math.log(random.random()))
    theta = 2 * math.pi * random.random()
    return R * math.abs(math.cos(theta))


@app.get("/")
async def read_root():
    logging.error("Hello World")
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    hist_meter.record(amount=box_muller(), attributes=dict(path="items"))
    logging.error("items")
    return {"item_id": item_id, "q": q}


@app.get("/io_task")
async def io_task():
    time.sleep(1)
    hist_meter.record(amount=box_muller(), attributes=dict(path="io"))
    logging.error("io task")
    return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
    req_meter.add(amount=1, attributes=dict(path="cpu_task"))
    for i in range(1000):
        i * i * i
    logging.error("cpu task")
    return "CPU bound task finish!"


@app.get("/random_status")
async def random_status(response: Response):
    req_meter.add(amount=1, attributes=dict(path="random_status"))
    response.status_code = random.choice([200, 200, 300, 400, 500])
    logging.error("random status")
    return {"path": "/random_status"}


@app.get("/random_sleep")
async def random_sleep(response: Response):
    req_meter.add(amount=1, attributes=dict(path="random_sleep"))
    time.sleep(random.randint(0, 5))
    logging.error("random sleep")
    return {"path": "/random_sleep"}


@app.get("/error_test")
async def error_test(response: Response):
    logging.error("got error!!!!")
    raise ValueError("value error")


setup_tracing(app=app)


if __name__ == "__main__":
    p = Path(__file__).parent.parent
    reload_dirs = [str((p / x).resolve()) for x in ["app", "clonr"]]
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        reload_dirs=reload_dirs,
    )
