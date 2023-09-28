from typing import Optional
import sqlalchemy as sa
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import requests
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import json
from tqdm import tqdm
from sqlalchemy.orm import selectinload
import random
import re
import os
import sys

sys.path.append("backend")
from app import schemas


class Base(DeclarativeBase):
    pass


clones_to_tags = sa.Table(
    "clones_to_tags",
    Base.metadata,
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
    sa.Column("clone_id", sa.Integer, sa.ForeignKey("clones.id"), primary_key=True),
)

clones_to_images = sa.Table(
    "clones_to_images",
    Base.metadata,
    sa.Column("image_id", sa.Integer, sa.ForeignKey("images.id"), primary_key=True),
    sa.Column("clone_id", sa.Integer, sa.ForeignKey("clones.id"), primary_key=True),
)

clones_to_documents = sa.Table(
    "clones_to_documents",
    Base.metadata,
    sa.Column(
        "document_id", sa.Integer, sa.ForeignKey("documents.id"), primary_key=True
    ),
    sa.Column("clone_id", sa.Integer, sa.ForeignKey("clones.id"), primary_key=True),
)


class ImageModel(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(unique=True, index=True)
    source: Mapped[str]
    content: Mapped[bytes]
    format: Mapped[str]
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_images, back_populates="images"
    )

    def __repr__(self):
        return f"Image(id={self.id}, url={self.url}, source={self.source}, format={self.format}))"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_tags, back_populates="tags"
    )

    def __repr__(self):
        return f"Tag(id={self.id}, name={self.name})"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str]
    name: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(default=None)
    type: Mapped[Optional[str]] = mapped_column(default=None)
    url: Mapped[Optional[str]] = mapped_column(default=None, unique=True)
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_documents, back_populates="documents"
    )

    def __repr__(self):
        return (
            f"Document(name={self.name}, n_chars={len(self.content)}, url={self.url})"
        )


class Clone(Base):
    __tablename__ = "clones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    short_description: Mapped[str]
    long_description: Mapped[str]
    greeting: Mapped[str]
    example_dialogues: Mapped[str] = mapped_column(nullable=True)
    avatar_uri: Mapped[str] = mapped_column(nullable=True)
    scenario: Mapped[str] = mapped_column(nullable=True)
    scrape_source: Mapped[str]
    creator: Mapped[str] = mapped_column(nullable=True)
    num_messages: Mapped[int] = mapped_column(nullable=True)
    num_conversations: Mapped[int] = mapped_column(nullable=True)
    _metadata: Mapped[str] = mapped_column(nullable=True)
    doc_links: Mapped[str]
    expanded_links: Mapped[str]
    final_links: Mapped[str]
    tags: Mapped[list["Tag"]] = relationship(
        secondary=clones_to_tags, back_populates="clones", lazy="joined"
    )
    images: Mapped[list["ImageModel"]] = relationship(
        secondary=clones_to_images, back_populates="clones", lazy="joined"
    )
    documents: Mapped[list["Document"]] = relationship(
        secondary=clones_to_documents, back_populates="clones", lazy="joined"
    )

    def __repr__(self):
        return f"Clone(name={self.name}, short_desc={self.short_description}, scrape_source={self.scrape_source})"


def filter_doc_content(
    content: str, chars_per_section_minimum=113, alnum_per_section_minimum=0.82
) -> bool:
    arr = re.split(r"(\n#|\n\=\=|^#|^\=\=)", content)
    sections = ["".join(arr[i : i + 2]).strip() for i in range(1, len(arr) - 1, 2)]
    filtered_sections: list[str] = []
    for sec in sections:
        if re.search(r"^#+\s*quotes?|^#+\s*\w?\s*support", sec):
            continue
        _, *body = sec.split("\n")
        if body and body[0]:
            chars_per_line = sum(len(y) for y in body) / len(body)
            alnum_per_line = sum(
                z.isalnum() for y in body for z in y if z not in " \n\t"
            ) / len(body)
            if chars_per_line < chars_per_section_minimum:
                continue
            if alnum_per_line < alnum_per_section_minimum:
                continue
            filtered_sections.append(sec)
    filtered_content = "\n".join(arr[:1] + filtered_sections)
    return filtered_content


if __name__ == "__main__":
    DATABASE_URL = "sqlite:///launch-clones.sqlite"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=False)  # type: ignore

    headers = {"Cookie": "next-auth.session-token=SUPERUSER_TOKEN"}
    base = "http://localhost:8000"

    with SessionLocal() as db:
        tags = db.query(Tag).all()

    print("Creating default Tags")
    TAGS: list[str] = []
    for tag in tqdm(tags):
        r = requests.post(base + "/tags/", headers=headers, json=dict(name=tag.name))
        json_res = json.loads(r.content)
        TAGS.append(json_res)
    r = requests.get("http://localhost:8000/tags", headers=headers)
    r.raise_for_status()
    global tag2int
    tag2int = {x["name"]: x["id"] for x in r.json()}
    assert r.status_code == 200

    with SessionLocal() as db:
        clones: list[Clone] = (
            db.query(Clone)
            .options(selectinload(Clone.documents))
            .options(selectinload(Clone.images))
            .options(selectinload(Clone.tags))
            .all()
        )

    def upload_only_clone(clone):
        avatar_uri = clone.avatar_uri
        if avatar_uri and clone.scrape_source == "character_ai":
            avatar_uri = "https://characterai.io/i/400/static/avatars/" + avatar_uri
        if avatar_uri is None or "charhub" in avatar_uri:
            if clone.images:
                avatar_uri = random.choice(clone.images).url
        try:
            clone_create = schemas.CloneCreate(
                name=clone.name,
                short_description=clone.short_description,
                long_description=clone.long_description,
                greeting_message=clone.greeting,
                avatar_uri=avatar_uri,
                is_public=True,
                tags=[tag2int[tag.name] for tag in clone.tags],
            )
        except Exception as e:
            return (None, e)
        r = requests.post(
            base + "/clones/", json=clone_create.model_dump(), headers=headers
        )
        r.raise_for_status()
        clone_id = r.json()["id"]
        return (clone.id, clone_id)

    print("Uploading Clones without docs")
    with ThreadPoolExecutor(max_workers=2) as pool:
        clone_tuples = list(
            tqdm(pool.map(upload_only_clone, clones), total=len(clones))
        )

    if len(sys.argv) > 1 and sys.argv[1]:
        print("Uploading documents")
        killed_docs = []
        min_doc_content_length = 80
        with SessionLocal() as db:
            for local_id, server_id in tqdm(clone_tuples):
                clone = db.get(Clone, local_id)
                for doc in clone.documents:
                    content = filter_doc_content(doc.content)
                    if len(content) < min_doc_content_length:
                        killed_docs.append(doc.url)
                        continue
                    doc_create = schemas.DocumentCreate(
                        content=doc.content,
                        name=doc.name + str(random.randint(0, 10_000)),
                        description=doc.description,
                        type=doc.type,
                        url=doc.url,
                    )
                    r = requests.post(
                        base + f"/clones/{server_id}/documents",
                        json=doc_create.model_dump(
                            exclude_unset=True, exclude={"tags"}
                        ),
                        headers=headers,
                    )
