from typing import Optional
import sqlalchemy as sa
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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


DATABASE_URL = "sqlite:///launch-clones.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=False)  # type: ignore


# import random
# import pandas as pd
# import numpy as np


# used to improve the fandom scraper by finding irrelevant sections
# we actually get pretty smooth histograms which blows my mind
# def get_document_stats_df(docs: list[Document]) -> pd.DataFrame:
#     examples = {}
#     c = {}
#     c2 = Counter()
#     c3 = {}
#     c4 = {}
#     # c4 = {}
#     for x in tqdm(docs):
#         s = x.content
#         # sections = ['#' + y for y in re.split(r'\n#|\n==', x )]
#         arr = re.split(r'(\n#|\n\=\=|^#|^\=\=)', s)
#         sections = [''.join(arr[i:i+2]).strip() for i in range(1, len(arr) - 1, 2)]
#         for sec in sections:
#             header = sec.split('\n')[0].strip().lower()
#             c2[header] = c2.get(header, 0) + 1
#             if header not in c:
#                 c[header] = []
#                 c3[header] = []
#                 examples[header] = []
#                 c4[header] = []
#             body = sec.split('\n')[1:]
#             if body and body[0]:
#                 tot = sum([len(z) for z in body])
#                 if not tot:
#                     raise ValueError(body)
#                 c4[header].append(tot)
#                 value = np.mean([len(y) for y in body])
#                 if not value:
#                     raise ValueError(body)
#                 c[header].append(value)
#                 c3[header].append(np.mean([z.isalnum() for y in body for z in y if z not in ' \n\t']))
#                 # c4[header].append(np.mean([letter_distance(y) for y in body]))
#                 examples[header].append('\n'.join(body))

#     chars_per_section = {k:np.mean(v or [0]) for k, v in c.items()}
#     alnum_per_section = {k:np.mean(v or [0]) for k, v in c3.items()}
#     section_length = {k:np.mean(v or [0]) for k, v in c4.items()}

#     df = pd.DataFrame([
#         {
#             'section':k,
#             'freq':v,
#             'chars_per_section':chars_per_section[k],
#             'alnum_per_section':alnum_per_section[k],
#             'section_length': section_length[k]
#         }
#         for k, v in c2.items()
#     ])
#     df['example1'] = df.section.map(lambda x: random.choice(examples[x]) if examples[x] else '')
#     df['example2'] = df.section.map(lambda x: random.choice(examples[x]) if examples[x] else '')
#     df['example3'] = df.section.map(lambda x: random.choice(examples[x]) if examples[x] else '')

#     return df


# This is the new populate_db.py code

# import requests
# import aiohttp
# import json
# from tqdm import tqdm
# from sqlalchemy.orm import selectinload
# import random


# headers = {"Cookie": "next-auth.session-token=SUPERUSER_TOKEN"}
# base = 'http://localhost:8000'

# with SessionLocal() as db:
#     tags = db.query(Tag).all()

# print("Creating default Tags")
# TAGS: list[str] = []
# for tag in tqdm(tags):
#     r = requests.post(base + "/tags/", headers=headers, json=dict(name=tag.name))
#     json_res = json.loads(r.content)
#     TAGS.append(json_res)
# r = requests.get("http://localhost:8000/tags", headers=headers)
# r.raise_for_status()
# global tag2int
# tag2int = {x["name"]: x["id"] for x in r.json()}
# assert r.status_code == 200


# import re


# def filter_doc_content(
#     content: str,
#     chars_per_section_minimum = 113,
#     alnum_per_section_minimum = 0.82
# ) -> bool:
#     arr = re.split(r'(\n#|\n\=\=|^#|^\=\=)', content)
#     sections = [
#         ''.join(arr[i:i+2]).strip()
#         for i in range(1, len(arr) - 1, 2)
#     ]
#     filtered_sections: list[str] = []
#     for sec in sections:
#         if re.search(r'^#+\s*quotes?|^#+\s*\w?\s*support', sec):
#             continue
#         _, *body = sec.split('\n')
#         if body and body[0]:
#             chars_per_line = sum(len(y) for y in body) / len(body)
#             alnum_per_line = sum(z.isalnum() for y in body for z in y if z not in ' \n\t') / len(body)
#             if chars_per_line < chars_per_section_minimum:
#                 continue
#             if alnum_per_line < alnum_per_section_minimum:
#                 continue
#             filtered_sections.append(sec)
#     filtered_content = '\n'.join(arr[:1] + filtered_sections)
#     return filtered_content


# with SessionLocal() as db:
#     clones: list[Clone] = (
#         db.query(Clone)
#         .options(selectinload(Clone.documents))
#         .options(selectinload(Clone.images))
#         .options(selectinload(Clone.tags))
#         .all()
#     )

# def upload_clone(clone):
#     killed_docs = []
#     min_doc_content_length = 80
#     avatar_uri = clone.avatar_uri
#     if avatar_uri and clone.scrape_source == 'character_ai':
#         avatar_uri = 'https://characterai.io/i/400/static/avatars/' + avatar_uri
#     if avatar_uri is None or 'charhub' in avatar_uri:
#         if clone.images:
#             avatar_uri = clone.images[0].url
#     clone_create = schemas.CloneCreate(
#         name=clone.name,
#         short_description=clone.short_description,
#         long_description=clone.long_description,
#         greeting_message=clone.greeting,
#         avatar_uri=avatar_uri,
#         is_public=True,
#         tags=[tag2int[tag.name] for tag in clone.tags],
#     )
#     r = requests.post(
#         base + '/clones/',
#         json=clone_create.model_dump(),
#         headers=headers
#     )
#     r.raise_for_status()
#     clone_id = r.json()['id']
#     for doc in clone.documents:
#         content = filter_doc_content(doc.content)
#         if len(content) < min_doc_content_length:
#             killed_docs.append(doc.url)
#             continue
#         doc_create = schemas.DocumentCreate(
#             content=doc.content,
#             name=doc.name[:36] + str(random.randint(0, 10_000)),
#             description=doc.description,
#             type=doc.type,
#             url=doc.url
#         )
#         r = requests.post(
#             base + f"/clones/{clone_id}/documents",
#             json=doc_create.model_dump(
#                 exclude_unset=True,
#                 exclude={"tags"}
#             ),
#             headers=headers
#         )
#     return killed_docs


# from concurrent.futures import ThreadPoolExecutor


# with ThreadPoolExecutor(max_workers=16) as pool:
#     killed_docs = list(tqdm(pool.map(upload_clone, clones), total=len(clones)))
