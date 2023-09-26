import pandas as pd
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from PIL import Image
import re
from markdownify import markdownify
from markdownify import MarkdownConverter
import wikipedia
import sqlalchemy as sa
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential
import pandas as pd
from tqdm import tqdm

tqdm.pandas()
import numpy as np
import uuid
import trafilatura
import time
import random
import json
import itertools
import requests
import trafilatura
from typing import Optional
from urllib.parse import urlparse
from scrapers.clean_dialogues import clean_jinja_roles, lightly_clean_dialogues
from fastapi.encoders import jsonable_encoder
from io import BytesIO


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


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_tags, back_populates="tags"
    )


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
    tags: Mapped[list["Tag"]] = relationship(
        secondary=clones_to_tags, back_populates="clones", lazy="joined"
    )
    images: Mapped[list["ImageModel"]] = relationship(
        secondary=clones_to_images, back_populates="clones", lazy="joined"
    )
    documents: Mapped[list["Document"]] = relationship(
        secondary=clones_to_documents, back_populates="clones", lazy="joined"
    )


DATABASE_URL = f"sqlite:///launch-clones.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=False)  # type: ignore


markdown_converter = MarkdownConverter()


def find_extended_domains(url: str, data=None) -> list[str]:
    domain = url.rstrip(urlparse(url).path)
    if data is None:
        r = requests.get(url)
        r.raise_for_status()
        data = r.content
    soup = BeautifulSoup(data, "html.parser")

    new_links: list[str] = []
    for tag in soup.find_all("a"):
        if new_link := tag.get("href", ""):
            if new_link.startswith("/"):
                new_link = domain + new_link
            if new_link == url:
                continue
            p = urlparse(new_link)
            if p.query or p.params:
                continue
            if new_link.startswith(url):
                new_links.append(new_link)

    return sorted(set(new_links))


def remove_empty_markdown(s, depth=0):
    changes = False
    new: list[str] = []
    for line in s.split("\n"):
        if line.startswith("#") and new and new[-1].startswith("#"):
            new.pop()
            changes = True
        new.append(line)
    s = "\n".join(new)
    if changes and depth < 8:
        return remove_empty_markdown(s, depth=depth + 1)
    return s


def extract_character_info(soup: BeautifulSoup) -> str:
    character = {}
    character_info = soup.find("aside")
    for br in character_info.find_all("br"):
        br.replace_with(", ")
    character_info.extract()
    character["name"] = character_info.h2.text.strip()

    character["dialogue"] = ""

    for dialogue_section in soup.find_all("div", class_="dialogue"):
        dialogue_list_section = dialogue_section.find("dl")
        dialogue_items = dialogue_list_section.find_all("dd")
        dialogue_text = ""
        if not dialogue_items[0].b:
            continue

        for item in dialogue_items:
            try:
                # logger.info(item.get_text(strip=True))
                dialogue_text += f"{item.get_text(strip=True)}\n\n"
            except Exception as e:
                continue

        character["dialogue"] += dialogue_text.strip()

    items = character_info.findAll(
        "div", "pi-item pi-data pi-item-spacing pi-border-color"
    )
    for item in items:
        # if h3 not in item, continue
        if not item.find("h3"):
            continue
        key = item.find("h3").text
        tag = item.find("div", "pi-data-value pi-font")
        if tag.name in ["ul", "ol", "dl"]:
            value = markdown_converter.convert_soup(tag)
        else:
            value = tag.get_text(strip=False)
        character[key] = value
    return "\n".join(f"{k}: {v}." for k, v in character.items())


def extract_from_wikipedia(url) -> str:
    from urllib.parse import unquote

    # _, title = re.findall(r"https://(\w{2,})\.wikipedia\.org/wiki/(.+)", url)
    if q := urlparse(url).query:
        if "title=" in q:
            title = re.findall(r"title=(.*)", q)[0]
    else:
        title = urlparse(url).path.replace("/wiki/", "")
    try:
        page = wikipedia.page(title=unquote(title), auto_suggest=False)
    except Exception:
        page = wikipedia.page(
            title=unquote(title.replace("%25", "%")), auto_suggest=False
        )
    bad_headers = r"== (Bibliography|See also|References|Futher reading)"
    content = page.content
    content = re.split(bad_headers, content)[0]
    # This removes some unsalvageable html styling (things like latex, bold),
    content = re.sub(r"[ \t]+", " ", content)
    content = re.sub(r"\s*\n+\s*", "\n", content)
    content = "\n".join(
        x for x in content.split("\n") if len(x) > 1 and not x.startswith("{")
    )
    content = re.sub(r"([^A-Z])\.([A-Z])", r"\1. \2", content)
    return content


def extract_from_fandom(data) -> str:
    soup = BeautifulSoup(data, "html.parser")
    try:
        card_data = extract_character_info(soup)
    except:
        card_data = ""
    text = trafilatura.extract(
        data, include_comments=False, include_tables=False, include_formatting=True
    )
    text = remove_empty_markdown(text)
    content = f"{card_data}\n{text}".strip()
    return content


def extract_anything_else(data) -> str:
    text = trafilatura.extract(
        data, include_comments=False, include_tables=False, include_formatting=True
    )
    return (text or "").strip()


def get_all_links():
    all_links: list[str] = []

    with SessionLocal() as db:
        all_clones = db.query(Clone).all()
        for c in all_clones:
            orig_links = json.loads(c.doc_links)
            expanded_links = json.loads(c.expanded_links)
            all_links.extend(orig_links)
            new_links = []
            for x in orig_links:
                if "fandom" in x:
                    for ex in expanded_links:
                        if (
                            ex != x
                            and ex.startswith(x.rstrip("/") + "/")
                            and "#" not in ex
                            and ":~" not in ex
                        ):
                            new_links.append(ex)
            all_links.extend(new_links)

    print("before deduping:", len(all_links))
    all_links = [
        x
        for x in all_links
        if "#" not in x
        and ".jp" not in x
        and ".gg" not in x
        and "tvtropes" not in x
        and "allthetropes" not in x
        and "static.wikia" not in x
        and ":~" not in x
    ]
    print("After deduping all links:", len(all_links))
    all_links = sorted(set(all_links))
    return all_links


if __name__ == "__main__":
    import sys

    idx = int(sys.argv[1])

    # with open("all_links.json", "r") as f:
    #     all_links = json.load(f)
    all_links = get_all_links()

    print("Possible scrapes to do:", len(all_links))

    with SessionLocal() as db:
        for link in tqdm(all_links):
            doc_exists = db.query(Document).where(Document.url == link).first()

            if doc_exists:
                continue

            # make the request
            r = requests.get(link)

            # doc stuff
            if "fandom" in link:
                content = extract_from_fandom(r.content)
                name = (
                    urlparse(link).netloc.split(".com")[0] + "-" + link.split("/")[-1]
                )
            elif "wikipedia" in link:
                try:
                    content = extract_from_wikipedia(link)
                except wikipedia.DisambiguationError:
                    print(link)
                    continue
                except Exception as e:
                    print(f"Exception {e} on link: {link}")
                    continue
                name = "wikipedia-" + link.split("/")[-1]
            else:
                content = extract_anything_else(r.content)
                name = urlparse(link).netloc + "-" + link.split("/")[-1]
            doc = Document(content=content, name=name, type="fandom", url=link)
            db.add(doc)

            # Grab the title image from this page while we're here
            tmp = trafilatura.extract(r.content, output_format="json")
            if tmp:
                image_url = json.loads(tmp).get("image", "")

                if (
                    image_url
                    and not db.query(ImageModel.url)
                    .where(ImageModel.url == image_url)
                    .first()
                ):
                    try:
                        r = requests.get(image_url)
                        buf = BytesIO()
                        img = Image.open(BytesIO(r.content))
                        img.save(buf, format="webp")
                        image = ImageModel(
                            url=image_url,
                            source=link,
                            content=buf.getvalue(),
                            format="webp",
                        )
                        db.add(image)
                    except:
                        pass

            db.commit()
