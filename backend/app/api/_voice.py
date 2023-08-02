# DEPRECATED (Jonny): this route is currently not in use as we are not doing live voice chat.

from typing import Annotated, List

import elevenlabs
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, utils
from app.db import get_async_session

router = APIRouter(
    prefix="/voice",
    tags=["voices"],
    responses={404: {"description": "Not found"}},
)


@router.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    print(dir(files[0]))
    return {"filenames": [file.filename for file in files]}


@router.get("/")
async def main():
    content = """
<body>
<form action="/voice/uploadfiles" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
