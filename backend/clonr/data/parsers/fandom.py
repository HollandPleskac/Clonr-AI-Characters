import re

import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache


def convert_to_markdown(tag: Tag) -> str:
    if tag.name == "h1":
        return f"# {tag.get_text(strip=True)}\n\n"
    elif tag.name == "h2":
        return f"## {tag.get_text(strip=True)}\n\n"
    elif tag.name == "h3":
        return f"### {tag.get_text(strip=True)}\n\n"
    elif tag.name == "h4":
        return f"#### {tag.get_text(strip=True)}\n\n"
    elif tag.name == "h5":
        return f"##### {tag.get_text(strip=True)}\n\n"
    elif tag.name == "p":
        return f"{tag.get_text(strip=True)}\n\n"
    elif tag.name == "li":
        return f"- {tag.get_text(strip=True)}\n"
    elif tag.name == "ul" or tag.name == "ol":
        items = tag.find_all(["li", "p"])
        list_type = "*" if tag.name == "ul" else "1."
        x = "\n".join(f"{list_type} {item.get_text(strip=True)}" for item in items)
        return f"\n{x}\n\n"
    else:
        return ""


def extract_character_info(soup: BeautifulSoup) -> str:
    character = {}
    character_info = soup.find("aside")
    for br in character_info.find_all("br"):
        br.replace_with(", ")
    character_info.extract()
    character["name"] = character_info.h2.text.strip()
    items = character_info.findAll(
        "div", "pi-item pi-data pi-item-spacing pi-border-color"
    )
    for item in items:
        key = item.find("h3").text
        tag = item.find("div", "pi-data-value pi-font")
        if tag.name in ["ul", "ol"]:
            value = convert_to_markdown(tag)
        else:
            value = tag.get_text(strip=False)
        character[key] = value
    return "\n".join(f"{k}: {v}." for k, v in character.items())


class FandomParser(Parser):
    def _is_valid_url(self, url: str):
        if re.match(r"https://[\.a-zA-Z0-9_-]+\.fandom.com/wiki/.*", url) is None:
            msg = "Invalid Fandom URL"
            logger.error(msg)
            raise ParserException(msg)

    @instance_level_lru_cache(maxsize=None)
    def _extract(self, url: str, type: str) -> Document:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")

        for a_tag in soup.find_all("a"):
            text = a_tag.get_text(strip=False)
            a_tag.replace_with(
                f"<|FUCK|> {text}"
            )  # whitespace around hyperlinks is stripped

        for tag in soup.find_all("cite"):
            tag.decompose()

        for tag in soup.find_all("svg"):
            tag.decompose()

        try:
            char_info = extract_character_info(soup)
        except Exception as e:
            logger.warning(f"Failed to parse character info, will continue. Error: {e}")
            char_info = None

        # not sure if this one is gonna break
        root_div = soup.find(class_="mw-parser-output")

        for br in root_div.find_all("br"):
            br.replace_with("\n")

        res = "".join(convert_to_markdown(tag) for tag in root_div.children if tag.name)

        if char_info:
            res = f"{char_info.strip()}\n\n{res.strip()}"

        res = res.replace("<|FUCK|>", " ")
        res = re.sub(r"\[\d+\]", " ", res)  # remove citations [1], [2] etc.

        return Document(content=res, url=url, type=type)

    def extract(self, url: str, type: str = "fandom") -> Document:
        logger.info(f"Attempting to parse text from Fandom URL: {url}")
        self._is_valid_url(url=url)
        r = self._extract(url=url, type=type)
        logger.info("✅ Extracted from url.")
        return r


class JonnyURLParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, url: str, type: str) -> Document:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        for a_tag in soup.find_all("a"):
            text = a_tag.get_text(strip=False)
            a_tag.replace_with(text)
        for tag in soup.find_all("cite"):
            tag.decompose()
        for br in soup.find_all("br"):
            br.replace_with("\n")
        res = "".join(convert_to_markdown(tag) for tag in soup.find_all() if tag.name)
        return Document(content=res, url=url, type=type)

    def extract(self, url: str, type: str = "web-markdown") -> Document:
        logger.info(f"Attempting to parse text to markdown from URL: {url}")
        r = self._extract(url=url, type=type)
        logger.info("✅ Extracted from url.")
        return r
