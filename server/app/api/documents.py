from typing import Annotated, List

from app import models, schemas
from app.db import get_async_session
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{document_id}", response_model=schemas.Document)
async def get_document(
    document_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    document = await db.get(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/", response_model=schemas.Document, status_code=201)
async def create_document(
    document_create: schemas.DocumentCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    async with db.begin():
        document = models.Document(**document_create.dict())
        db.add(document)
        await db.refresh(document)
        return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    async with db.begin():
        document = await db.get(models.Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        db.delete(document)
        return {"message": "Document deleted"}


@router.get(
    "/document_collection/{document_collection_id}",
    response_model=List[schemas.Document],
)
async def get_document_collection_documents(
    document_collection_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    documents = await db.filter(
        models.Document.document_collection_id == document_collection_id
    ).all()
    if not documents:
        raise HTTPException(status_code=404, detail="Documents not found")
    return documents
