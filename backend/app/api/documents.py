from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.auth.users import current_active_user
from app import models, schemas
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Document)
async def create_document(
    document: schemas.DocumentCreate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    new_document = models.Document(**document.dict())
    user.documents.append(new_document)
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    return new_document


@router.get("/{id}", response_model=schemas.Document)
async def get_document(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    document = await db.get(models.Document, id)
    if document is None or document.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document


@router.put("/{id}", response_model=schemas.Document)
async def update_document(
    id: str,
    updated_document: schemas.DocumentUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    document = await db.get(models.Document, id)
    if document is None or document.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    for field, value in updated_document.dict(exclude_unset=True).items():
        setattr(document, field, value)
    await db.commit()
    await db.refresh(document)
    return document


@router.delete("/{id}", response_model=schemas.Document)
async def delete_document(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    document = await db.get(models.Document, id)
    if document is None or document.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    db.delete(document)
    await db.commit()
    return document


@router.get("/clone/{clone_id}", response_model=List[schemas.Document])
async def get_documents_for_clone(
    clone_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    documents = await db.execute(
        select(models.Document)
        .filter(models.Document.clone_id == clone_id)
        .join(models.Clone)
        .filter(models.Clone.creator_id == user.id)
    )
    return documents.scalars().all()
