import sqlalchemy as sa
from loguru import logger
from sqlalchemy.orm import Session

from app import models


@sa.event.listens_for(models.Message, "after_insert")
def increment_clone_num_messages(
    mapper, connection: sa.Connection, target: models.Message
):
    db = Session(bind=connection)
    try:
        if clone := db.get(models.Clone, target.clone_id):
            clone.num_messages += 1
            db.add(clone)
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
        if clone := db.get(models.Clone, target.clone_id):
            clone.num_messages -= 1
            db.add(clone)
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
        if clone := db.get(models.Clone, target.clone_id):
            clone.num_conversations += 1
            db.add(clone)
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
        if clone := db.get(models.Clone, target.clone_id):
            clone.num_conversations -= 1
            db.add(clone)
            db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise
    finally:
        db.close()
