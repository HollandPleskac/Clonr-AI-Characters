from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.auth.users import current_active_user
from app import models, schemas
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/facts",
    tags=["facts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Fact)
async def create_fact(
    fact: schemas.FactCreate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    new_fact = models.Fact(**fact.dict())
    user.facts.append(new_fact)
    db.add(new_fact)
    await db.commit()
    await db.refresh(new_fact)
    return new_fact


@router.get("/{id}", response_model=schemas.Fact)
async def get_fact(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    fact = await db.get(models.Fact, id)
    if fact is None or fact.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fact not found"
        )
    return fact


@router.put("/{id}", response_model=schemas.Fact)
async def update_fact(
    id: str,
    updated_fact: schemas.FactUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    fact = await db.get(models.Fact, id)
    if fact is None or fact.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fact not found"
        )
    for field, value in updated_fact.dict(exclude_unset=True).items():
        setattr(fact, field, value)
    await db.commit()
    await db.refresh(fact)
    return fact


@router.delete("/{id}", response_model=schemas.Fact)
async def delete_fact(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    fact = await db.get(models.Fact, id)
    if fact is None or fact.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fact not found"
        )
    db.delete(fact)
    await db.commit()
    return fact


@router.get("/clone/{clone_id}", response_model=List[schemas.Fact])
async def get_facts_for_clone(
    clone_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    facts = await db.execute(
        select(models.Fact)
        .filter(models.Fact.clone_id == clone_id)
        .join(models.Clone)
        .filter(models.Clone.user_id == user.id)
    )
    return facts.scalars().all()
