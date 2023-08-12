import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app import deps, models, schemas
from app.clone.controller import Controller
from app.clone.db import CloneDB
from app.clone.shared import DynamicTextSplitter
from app.embedding import EmbeddingClient
from clonr.data_structures import Document, Monologue

# # llm is not needed for the basic list index! We can revisit TreeIndex in the future
# # but for now, it's too much complexity for a yet to be demonstrated reward
from clonr.index import IndexType, ListIndex
from clonr.llms import LLM
from clonr.tokenizer import Tokenizer

router = APIRouter(
    prefix="/clones",
    tags=["clones"],
    responses={404: {"description": "Not found"}},
)

# reddit uses 60 * 60 * 5.4, but we will roughly double the time,
# since we expect the bot lifecycle to refresh slower than reddit's post lifecycle
HOT_TIME: float = 60 * 60 * 12

# TODO (Jonny): the query stuff doesn't properly filter out column-level is_public flags
# we should maybe just make a class to only return like name, short_desc, prof_pic, num_messages, num_convos


class CloneSortType(str, Enum):
    hot: str = "hot"
    top: str = "top"
    newest: str = "newest"
    oldest: str = "oldest"


async def get_clone(
    clone_id: Annotated[uuid.UUID, Path(description="Clone ID")],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
) -> models.Clone:
    if (clone := await db.get(models.Clone, clone_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clone does not exist."
        )
    return clone


async def get_document(
    document_id: Annotated[uuid.UUID, Path(description="Document ID")],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
) -> models.Document:
    if not (doc := await db.get(models.Document, document_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document does not exist."
        )
    return doc


async def get_monologue(
    monologue_id: Annotated[uuid.UUID, Path(description="Monologue ID")],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
) -> models.Monologue:
    if not (doc := await db.get(models.Monologue, monologue_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Monologue does not exist."
        )
    return doc


def clone_sort_selectable(query: sa.Select, sort: CloneSortType):
    match sort:
        case CloneSortType.newest:
            return query.order_by(models.Clone.created_at.desc())
        case CloneSortType.oldest:
            return query.order_by(models.Clone.created_at.asc())
        case CloneSortType.hot:
            # Uses the Reddit algorithm for returning "hot" clones.
            # https://www.evanmiller.org/deriving-the-reddit-formula.html
            # The algorithm is something like score = ln(likes - dislikes) + age / (60s * 60 * 5.43).
            # Rule of thumb is the No. of likes needed to beat a new post doubles for every 5 hours
            # FixMe (Jonny): should be base-10 log here, but too lazy to figure out how to do it
            seconds = sa.func.extract("epoch", models.Clone.created_at).cast(sa.Float)
            time_factor = seconds / HOT_TIME
            like_factor = sa.func.log(models.Clone.num_messages + 1)
            score = (like_factor + time_factor).label("score")
            return query.order_by(score.desc())
        case CloneSortType.top:
            return query.order_by(models.Clone.num_messages)
    raise TypeError(f"Invalid sort type: {sort}")


@router.post("/", response_model=schemas.Clone, status_code=status.HTTP_201_CREATED)
async def create_clone(
    obj: schemas.CloneCreate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    creator: Annotated[models.Creator, Depends(deps.get_current_active_creator)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
):
    data = obj.model_dump(exclude_none=True)
    if obj.tags:
        r = await db.scalars(sa.select(models.Tag).where(models.Tag.name.in_(obj.tags)))
        tags = r.all()
        if len(tags) != len(obj.tags):
            for t in obj.tags:
                if t not in tags:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Tag {t} is not a valid tag.",
                    )
        data["tags"] = tags

    clone = models.Clone(**data, creator_id=creator.user_id)

    if clone.long_description:
        clone.embedding = (
            await embedding_client.encode_passage(clone.long_description)
        )[0]
        clone.embedding_model = await embedding_client.encoder_name()
    db.add(clone)
    await db.commit()

    # (Jonny): the second argument forces sqlalchemy to load in the result
    # if you get a greenlet spawn error, that's why. Could do lazy=joined too
    # or add , ["tags"] to the refresh.
    await db.refresh(clone)
    return clone


# TODO (Jonny): add routes for top clones, trending, and recent
# TODO (Jonny): add an order by for these queries
@router.get("/", response_model=list[schemas.CloneSearchResult])
async def query_clones(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
    tags: Annotated[list[str] | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
    sort: Annotated[CloneSortType, Query()] = CloneSortType.top,
    similar: Annotated[str | None, Query()] = None,
    created_after: Annotated[datetime | None, Query()] = None,
    created_before: Annotated[datetime | None, Query()] = None,
    offset: Annotated[int, Query(title="database row offset", ge=0)] = 0,
    limit: Annotated[int, Query(title="database row return limit", ge=1, le=60)] = 10,
):
    query = sa.select(models.Clone)
    if not user.is_superuser:
        query = query.where(models.Clone.is_active).where(models.Clone.is_public)
    if tags is not None:
        query = query.where(models.Clone.tags.in_(tags))
    if name is not None:
        query = query.where(models.Clone.case_insensitive_name.ilike(f"%{name}%"))
        # This doesn't seem to work well for short names. Looks like it's better on long ones
        # await db.execute(sa.text("SET pg_trgm.word_similarity_threshold = 0.7"))
        # sml = models.Clone.case_insensitive_name.word_similarity(name)
        # query = query.where(models.Clone.case_insensitive_name.op("%>")(name))
        # query = query.order_by(sml.desc())
    if created_after is not None:
        query = query.where(models.Clone.created_at >= created_after)
    if created_before is not None:
        query = query.where(models.Clone.created_at <= created_before)
    if similar:
        emb = (await embedding_client.encode_query(similar))[0]
        dist = models.Clone.embedding.max_inner_product(emb).label("distance")
        query = query.where(models.Clone.embedding.is_not(None)).order_by(
            dist.asc()
        )  # it must have an embedding!
    else:
        query = clone_sort_selectable(query=query, sort=sort)
    query = query.offset(offset=offset).limit(limit=limit)
    clones = await db.scalars(query)
    return clones.unique().all()


# NOTE (Jonny): wild card paths have to come at the end otherwise order of resolution is messed up
# and you'll get the similar route being viewed as something like below
@router.get("/{clone_id}", response_model=schemas.Clone)
async def get_clone_by_id(
    clone: Annotated[models.Clone, Depends(get_clone)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    if user.is_superuser or clone.creator_id == user.id:
        return clone
    if not clone.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clone does not exist."
        )
    response = schemas.Clone.from_orm(clone)
    if not clone.is_long_description_public:
        response.long_description = None
    if not clone.is_short_description_public:
        response.short_description = None
    if not clone.is_greeting_message_public:
        response.greeting_message = None
    return response


@router.patch("/{clone_id}", response_model=schemas.Clone)
async def patch_clone(
    obj: schemas.CloneUpdate,
    clone: Annotated[models.Clone, Depends(get_clone)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
):
    if user.is_superuser or clone.creator_id == user.id:
        not_modified = True
        for k, v in obj.model_dump(exclude_unset=True).items():
            if getattr(clone, k) == v:
                continue
            not_modified = False
            setattr(clone, k, v)
            # TODO (Jonny): combine with the create endpoint
            if k == "long_description" and len(v) > 16:
                clone.embedding = (
                    await embedding_client.encode_passage(clone.long_description)
                )[0]
                clone.embedding_model = await embedding_client.encoder_name()
        if not_modified:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
        else:
            db.add(clone)
            await db.commit()
            await db.refresh(clone)
            return clone
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Insufficient privileges"
    )


# (Jonny): We can't delete a clone, because that will cause a cascade that
# deletes the conversation and message history, which is also necessary
# for tracking stats and payment! Be careful, don't do this unless you're sure.
@router.delete(
    "/{clone_id}", response_class=Response, dependencies=[Depends(deps.get_superuser)]
)
async def delete(
    clone: Annotated[models.Clone, Depends(get_clone)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    await db.delete(clone)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# # ------------ Long Description ------------ #
# Lol the similarity of an expensive route vs a cheap route low-key scares me.
@router.post(
    "/{clone_id}/generate_long_description",
    response_model=schemas.LongDescription,
    dependencies=[Depends(deps.get_superuser)],
    status_code=201,
)
async def generate_long_desc(
    llm: Annotated[LLM, Depends(deps.get_llm_with_clone_id)],
    clone: Annotated[models.Clone, Depends(get_clone)],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    long_desc = await Controller.generate_long_description(
        llm=llm, clone=clone, clonedb=clonedb
    )
    return long_desc


@router.get(
    "/{clone_id}/long_descriptions",
    response_model=list[schemas.LongDescription],
)
async def view_generated_long_descs(
    clone: Annotated[models.Clone, Depends(get_clone)],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    r = await clonedb.db.scalars(
        sa.select(models.LongDescription)
        .where(models.LongDescription.clone_id == clone.id)
        .options(joinedload(models.LongDescription.documents))
        .order_by(models.LongDescription.updated_at.desc())
    )
    long_descs = r.unique().all()
    return long_descs


# ------------ Documents ------------ #
@router.post(
    "/{clone_id}/documents",
    response_model=schemas.Document,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    doc_create: schemas.DocumentCreate,
    clone_id: Annotated[uuid.UUID, Path()],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
    tokenizer: Annotated[Tokenizer, Depends(deps.get_tokenizer)],
    splitter: Annotated[DynamicTextSplitter, Depends(deps.get_text_splitter)],
):
    if z := await clonedb.db.scalar(
        sa.select(models.Document.id)
        .where(models.Document.name == doc_create.name)
        .where(models.Document.clone_id == clone_id)
    ):
        from loguru import logger

        logger.exception(z)
        raise ValueError("fuck everything and fuck this world")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document with name {doc_create.name} already exists.",
        )
    doc = Document(
        index_type=IndexType.list, **doc_create.model_dump(exclude_unset=True)
    )
    index = ListIndex(tokenizer=tokenizer, splitter=splitter)
    nodes = await index.abuild(doc=doc)
    doc_model = await clonedb.add_document(doc=doc, nodes=nodes)
    return doc_model


@router.get("/{clone_id}/documents", response_model=list[schemas.Document])
async def get_documents(
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    clone: Annotated[models.Clone, Depends(get_clone)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    offset: Annotated[int, Query(title="database row offset", ge=0)] = 0,
    limit: Annotated[int, Query(title="database row return limit", ge=1, le=60)] = 10,
    description: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
    created_after: Annotated[datetime | None, Query()] = None,
    created_before: Annotated[datetime | None, Query()] = None,
):
    if not user.is_superuser and not user.id == clone.creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    q = sa.select(models.Document).where(models.Document.clone_id == clone.id)
    if description is not None:
        q = q.where(
            sa.and_(
                models.Document.description.is_not(None),
                sa.func.lower(models.Document.description).ilike(description.lower()),
            )
        )
    if name is not None:
        q = q.where(
            sa.and_(
                models.Document.name.is_not(None),
                sa.func.lower(models.Document.name).ilike(f"%{name.lower()}%"),
            )
        )
    if created_before is not None:
        q = q.where(models.Document.created_at <= created_before)
    if created_after is not None:
        q = q.where(models.Document.created_at >= created_after)
    q = (
        q.offset(offset=offset)
        .limit(limit=limit)
        .order_by(models.Document.created_at.desc())
    )
    docs = await db.scalars(q)
    return docs.unique().all()


@router.patch("/{clone_id}/documents/{document_id}", response_model=schemas.Document)
async def update_document(
    doc_update: schemas.DocumentUpdate,
    doc: Annotated[models.Document, Depends(get_document)],
    clonedb: Annotated[
        CloneDB, Depends(deps.get_clonedb)
    ],  # used only for auth, to make sure that user has access to edit this clone
):
    data = doc_update.model_dump(exclude_unset=True)
    not_modified = True
    for k, v in data.items():
        if getattr(doc, k) == v:
            continue
        not_modified = False
        setattr(doc, k, v)
    if not_modified:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    clonedb.db.add(doc)
    await clonedb.db.commit()
    await clonedb.db.refresh(doc)
    return doc


@router.delete(
    "/{clone_id}/documents/{document_id}",
)
async def delete_document(
    doc: Annotated[models.Document, Depends(get_document)],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    await clonedb.delete_document(doc=doc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{clone_id}/documents/{document_id}", response_model=schemas.Document)
async def get_document_by_id(
    doc: Annotated[models.Document, Depends(get_document)],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    return doc


# ------------ Monologues ------------ #
@router.patch("/{clone_id}/monologues/{monologue_id}", response_model=schemas.Monologue)
async def update_monologue(
    monologue_update: schemas.DocumentUpdate,
    monologue: Annotated[models.Monologue, Depends(get_monologue)],
    clonedb: Annotated[
        CloneDB, Depends(deps.get_clonedb)
    ],  # used only for auth, to make sure that user has access to edit this clone
):
    data = monologue_update.model_dump(exclude_unset=True)
    not_modified = True
    for k, v in data.items():
        if getattr(monologue, k) == v:
            continue
        not_modified = False
        setattr(monologue, k, v)
    if not_modified:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    clonedb.db.add(monologue)
    await clonedb.db.commit()
    await clonedb.db.refresh(monologue)
    return monologue


@router.delete("/{clone_id}/monologues/{monologue_id}")
async def delete_monologue(
    monologue: Annotated[models.Monologue, Depends(get_monologue)],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    await clonedb.delete_monologue(monologue=monologue)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{clone_id}/monologues/{monologue_id}", response_model=schemas.Monologue)
async def get_monologue_by_id(
    monologue: Annotated[models.Document, Depends(get_monologue)],
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    return monologue


@router.post(
    "/{clone_id}/monologues",
    response_model=schemas.Monologue,
    status_code=status.HTTP_201_CREATED,
)
async def create_monologue(
    monologue_create: schemas.MonologueCreate,
    clonedb: Annotated[CloneDB, Depends(deps.get_clonedb)],
):
    monologue = Monologue(**monologue_create.model_dump(exclude_none=True))
    m = await clonedb.add_monologues([monologue])
    if not m:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED, detail="Monologue already exists."
        )
    return m[0]


@router.get("/{clone_id}/monologues", response_model=list[schemas.Monologue])
async def get_monologues(
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    clone: Annotated[models.Clone, Depends(get_clone)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    offset: Annotated[int, Query(title="database row offset", ge=0)] = 0,
    limit: Annotated[int, Query(title="database row return limit", ge=1, le=60)] = 10,
    content: Annotated[str | None, Query()] = None,
    source: Annotated[str | None, Query()] = None,
    created_after: Annotated[datetime | None, Query()] = None,
    created_before: Annotated[datetime | None, Query()] = None,
):
    if not user.is_superuser and not user.id == clone.creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    q = sa.select(models.Monologue).where(models.Monologue.clone_id == clone.id)
    if content is not None:
        q = q.where(
            sa.and_(
                models.Monologue.description.is_not(None),
                sa.func.lower(models.Monologue.description).ilike(content.lower()),
            )
        )
    if source is not None:
        q = q.where(
            sa.and_(
                models.Monologue.name.is_not(None),
                sa.func.lower(models.Monologue.name).ilike(source.lower()),
            )
        )
    if created_before is not None:
        q = q.where(models.Monologue.created_at <= created_before)
    if created_after is not None:
        q = q.where(models.Monologue.created_at >= created_after)
    q = (
        q.offset(offset=offset)
        .limit(limit=limit)
        .order_by(models.Monologue.created_at.desc())
    )
    m = await db.scalars(q)
    return m.unique().all()


# TODO (Jonny): Create a route for generating the long description. This is a function in clonr.generate
# we just need to run some checks (like auth and making sure docs exist) and set this up.
