import asyncio
import json
import os
from contextlib import asynccontextmanager

import uvicorn
from app import api, schemas, utils
from app.auth.users import auth_backend, fastapi_users, google_oauth_client
from app.db import (
    clear_db,
    clear_redis,
    create_superuser,
    init_db,
    wait_for_db,
    wait_for_redis,
)
from app.settings import settings
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from fastapi import FastAPI


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

    if settings.USE_ALEMBIC:
        logger.info("Running migration upgrades")
        await run_async_upgrade()
    else:
        # If not using Alembic run this
        logger.info("Creating database")
        await init_db()

    logger.info(f"Creating superuser: {settings.SUPERUSER_EMAIL}")
    user = await create_superuser()
    logger.info(json.dumps(jsonable_encoder(user), indent=2))

    logger.info("Creating local storage directories")
    os.makedirs(str(utils.get_local_data_dir().resolve()), exist_ok=True)
    os.makedirs(str(utils.get_voice_data_dir().resolve()), exist_ok=True)

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
app.include_router(api.voice_router)
app.include_router(api.clones_router)
app.include_router(api.apikeys_router)
app.include_router(api.conversations_router)
app.include_router(api.memories_router)
# app.include_router(api.messages_router)
# app.include_router(api.documents_router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(schemas.UserRead),
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
