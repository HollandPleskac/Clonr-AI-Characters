# DEPRECATED (Jonny): this route is currently not in use as we are not doing live voice chat.


from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

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
