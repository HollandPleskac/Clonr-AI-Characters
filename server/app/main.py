import os
import time
from contextlib import asynccontextmanager
from typing import Annotated, List

import uvicorn
from app import api
from app.db import clear_db, get_async_session, init_db, wait_for_db
from app.settings import settings
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Waiting for db...")
    await wait_for_db()
    logger.info("Creating database")
    await init_db()
    yield
    logger.info("Erasing database")
    await clear_db()


app = FastAPI(lifespan=lifespan)
app.include_router(api.users_router)
app.include_router(api.clones_router)
app.include_router(api.conversations_router)
app.include_router(api.messages_router)
app.include_router(api.documents_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return "Hello, world!"


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
