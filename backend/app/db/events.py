import sqlalchemy as sa
from loguru import logger
from sqlalchemy.orm import Session

from app import models


# NOTE (Jonny): doing += or -= will make the operation happen in Python, and thus be susceptible to race conditions
@sa.event.listens_for(models.Message, "after_insert")
def increment_clone_num_messages(
    mapper, connection: sa.Connection, target: models.Message
):
    db = Session(bind=connection)
    try:
        db.execute(
            sa.update(models.Clone)
            .where(models.Clone.id == target.clone_id)
            .values(num_messages=models.Clone.num_messages + 1)
        )
        db.execute(
            sa.update(models.Conversation)
            .where(models.Conversation.id == target.conversation_id)
            .values(num_messages_ever=models.Conversation.num_messages_ever + 1)
        )
        if target.is_clone and target.is_main:
            db.execute(
                sa.update(models.Conversation)
                .where(models.Conversation.id == target.conversation_id)
                .values(last_message=target.content)
            )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise
    finally:
        db.close()


@sa.event.listens_for(models.Message, "after_update")
def update_converations_last_message(
    mapper, connection: sa.Connection, target: models.Message
):
    db = Session(bind=connection)
    try:
        # NOTE (Jonny): since the only time we can update a message is if it's the most recent
        # this should be safe for now
        if target.is_clone and target.is_main:
            db.execute(
                sa.update(models.Conversation)
                .where(models.Conversation.id == target.conversation_id)
                .values(last_message=target.content)
            )
            db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise
    finally:
        db.close()


@sa.event.listens_for(models.Message, "after_delete")
def decrement_clone_num_messages(
    mapper, connection: sa.Connection, target: models.Message
):
    db = Session(bind=connection)
    try:
        db.execute(
            sa.update(models.Clone)
            .where(models.Clone.id == target.clone_id)
            .values(num_messages=models.Clone.num_messages - 1)
        )
        db.execute(
            sa.update(models.Conversation)
            .where(models.Conversation.id == target.conversation_id)
            .values(num_messages_ever=models.Conversation.num_messages_ever - 1)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise
    finally:
        db.close()


@sa.event.listens_for(models.Conversation, "after_insert")
def increment_clone_num_conversations(
    mapper, connection: sa.Connection, target: models.Conversation
):
    db = Session(bind=connection)
    try:
        db.execute(
            sa.update(models.Clone)
            .where(models.Clone.id == target.clone_id)
            .values(num_conversations=models.Clone.num_conversations + 1)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise
    finally:
        db.close()


@sa.event.listens_for(models.Conversation, "after_delete")
def decrement_clone_num_conversations(
    mapper, connection: sa.Connection, target: models.Conversation
):
    db = Session(bind=connection)
    try:
        db.execute(
            sa.update(models.Clone)
            .where(models.Clone.id == target.clone_id)
            .values(num_conversations=models.Clone.num_conversations - 1)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise
    finally:
        db.close()
