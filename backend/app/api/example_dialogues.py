from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.auth.users import current_active_user
from app import models, schemas
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/example-dialogues",
    tags=["example-dialogues"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.ExampleDialogue)
async def create_example_dialogue(
    example_dialogue: schemas.ExampleDialogueCreate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    new_example_dialogue = models.ExampleDialogue(**example_dialogue.dict())
    user.example_dialogues.append(new_example_dialogue)
    db.add(new_example_dialogue)
    await db.commit()
    await db.refresh(new_example_dialogue)
    return new_example_dialogue


@router.get("/{id}", response_model=schemas.ExampleDialogue)
async def get_example_dialogue(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    example_dialogue = await db.get(models.ExampleDialogue, id)
    if example_dialogue is None or example_dialogue.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    return example_dialogue


@router.put("/{id}", response_model=schemas.ExampleDialogue)
async def update_example_dialogue(
    id: str,
    updated_example_dialogue: schemas.ExampleDialogueUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    promise = await db.scalars(
        update(models.ExampleDialogue)
        .where(models.ExampleDialogue.id == id)
        .values(**updated_example_dialogue.dict(exclude_unset=True))
        .returning(models.ExampleDialogue)
    )
    clone = promise.first()
    await db.commit()
    await db.refresh(clone)
    return clone


@router.delete("/{id}", response_model=schemas.ExampleDialogue)
async def delete_example_dialogue(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if (example_dialogue := await db.get(models.ExampleDialogue, id)) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    db.delete(example_dialogue)
    await db.commit()
    return example_dialogue


@router.get("/conversation/{conversation_id}", response_model=List[schemas.Fact])
async def get_example_dialogues_for_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    example_dialogues = await db.execute(
        select(models.ExampleDialogue)
        .filter(models.ExampleDialogue.conversation_id == conversation_id)
        .join(models.Clone)
        .filter(
            models.Clone.conversation_id == conversation_id
            and models.Clone.user_id == user.id
        )
    )
    return example_dialogues.scalars().all()
