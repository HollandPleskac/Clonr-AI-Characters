import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


@sa.event.listens_for(models.Message, "after_insert")
async def increment_clone_num_messages(
    mapper, db: AsyncSession, target: models.Message
):
    clone = await db.get(models.Clone, target.clone_id)
    clone.num_messages += 1
    db.add(clone)
    await db.commit()


@sa.event.listens_for(models.Message, "after_delete")
async def decrement_clone_num_messages(
    mapper, db: AsyncSession, target: models.Message
):
    clone = await db.get(models.Clone, target.clone_id)
    clone.num_messages -= 1
    db.add(clone)
    await db.commit()


@sa.event.listens_for(models.Conversation, "after_insert")
async def increment_clone_num_conversations(
    mapper, db: AsyncSession, target: models.Message
):
    clone = await db.get(models.Clone, target.clone_id)
    clone.num_conversations += 1
    db.add(clone)
    await db.commit()


@sa.event.listens_for(models.Conversation, "after_delete")
async def decrement_clone_num_conversations(
    mapper, db: AsyncSession, target: models.Message
):
    clone = await db.get(models.Clone, target.clone_id)
    clone.num_conversations -= 1
    db.add(clone)
    await db.commit()
