from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.clone.controller import Controller
from app.embedding import EmbeddingClient
from clonr.tokenizer import Tokenizer

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)

FREE_MESSAGE_LIMIT = 10


# TODO (Jonny): put a paywall behind this dependency
async def get_conversation(
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Creator, Depends(deps.get_paying_user)],
) -> models.Conversation:
    convo = await db.get(models.Conversation, conversation_id)
    if not convo or not convo.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation ({conversation_id}) not found.",
        )
    if not user.is_superuser and not convo.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return convo


# TODO (Jonny): put a paywall behind this endpoint after X messages, need to add user permissions
@router.post(
    "/", response_model=schemas.Conversation, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    obj: schemas.ConversationCreate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_free_limit_user)],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    tokenizer: Annotated[Tokenizer, Depends(deps.get_tokenizer)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
):
    clone = await db.get(models.Clone, obj.clone_id)
    if not clone or not clone.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clone ({obj.clone_id}) not found.",
        )
    if not user.is_subscribed:
        user.num_free_messages_sent += 1

    # NOTE (Jonny): not sure if this is a security risk. Indirectly exposing the
    # UUID of a private clone, by getting a different status code.
    # you can chat with your own clone, but you can't chat with private clones.
    if not clone.is_public and not clone.creator_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if obj.user_name is None:
        obj.user_name = user.private_chat_name
    if obj.user_name.lower() == clone.name.lower():
        detail = (
            f"User's private chat name ({obj.user_name}) collides with the clone name. "
            "Please retry with a different user_name. Case does not matter."
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
    convo = await Controller.create_conversation(
        obj=obj,
        clone=clone,
        db=db,
        user=user,
        conn=conn,
        tokenizer=tokenizer,
        embedding_client=embedding_client,
    )

    return convo


@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation_by_id(
    conversation: Annotated[models.Conversation, Depends(get_conversation)],
):
    return conversation


@router.patch("/{conversation_id}", response_model=schemas.Conversation)
async def patch_conversation(
    obj: schemas.ConversationUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    conversation: Annotated[models.Conversation, Depends(get_conversation)],
):
    data = obj.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    for k, v in data.items():
        setattr(conversation, k, v)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    from fastapi.encoders import jsonable_encoder

    convo = schemas.Conversation(**jsonable_encoder(conversation))
    return convo


@router.delete("/{conversation_id}", response_class=Response)
async def delete_conversation(
    conversation_id: Annotated[str, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Conversation, Depends(deps.get_superuser)],
):
    convo = await db.get(models.Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(convo)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------- Messages ----------- #


async def get_messages(
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Creator, Depends(deps.get_paying_user)],
) -> models.Conversation:
    convo = await db.get(models.Conversation, conversation_id)
    if not convo or not convo.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation ({conversation_id}) not found.",
        )
    if not user.is_superuser and not convo.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return convo
