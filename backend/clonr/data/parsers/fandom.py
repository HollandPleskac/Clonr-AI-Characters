import json
import re

import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache

try:
    import fandom

    FANDOM_AVAILABLE = True
except ImportError:
    FANDOM_AVAILABLE = False


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
    elif tag.name == "dl":
        return f"# {tag.get_text(strip=True)}\n\n"
    elif tag.name == "dd":
        return f"# {tag.get_text(strip=True)}\n\n"
    elif tag.name == "ul" or tag.name == "ol" or tag.name == "dl":
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

    character["dialogue"] = ""

    for dialogue_section in soup.find_all("div", class_="dialogue"):
        dialogue_list_section = dialogue_section.find("dl")
        dialogue_items = dialogue_list_section.find_all("dd")
        logger.info("This is dialogue_items:")
        logger.info(dialogue_items)
        dialogue_text = ""
        if not dialogue_items[0].b:
            logger.info("skipping dialogue..")
            continue

        for item in dialogue_items:
            logger.info(f"This is item: {item}")
            logger.info(item)

            try:
                # logger.info(item.get_text(strip=True))
                dialogue_text += f"{item.get_text(strip=True)}\n\n"
            except Exception as e:
                logger.info(f"Error parsing dialogues: {e}")
                continue

        logger.info(f"Dialogue text: {dialogue_text}")
        character["dialogue"] += dialogue_text.strip()

    items = character_info.findAll(
        "div", "pi-item pi-data pi-item-spacing pi-border-color"
    )
    for item in items:
        # if h3 not in item, continue
        if not item.find("h3"):
            continue
        key = item.find("h3").text
        logger.info(f"This is key: {key}")
        tag = item.find("div", "pi-data-value pi-font")
        if tag.name in ["ul", "ol", "dl"]:
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
        # if r has no content, return
        if not r.content:
            return None
        soup = BeautifulSoup(r.content, "html.parser")

        for a_tag in soup.find_all("a"):
            text = a_tag.get_text(strip=False)
            a_tag.replace_with(
                f"<|FK|> {text}"
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

        res = res.replace("<|FK|>", " ")
        res = re.sub(r"\[\d+\]", " ", res)  # remove citations [1], [2] etc.

        return Document(content=res, url=url, type=type)

    def extract(self, url: str, type: str = "fandom") -> Document:
        logger.info(f"Attempting to parse text from Fandom URL: {url}")
        self._is_valid_url(url=url)
        r = self._extract(url=url, type=type)
        logger.info("✅ Extracted from url.")
        return r


# Process lines..
def process_lines(input_lines):
    results = []
    skip_line = False

    for i, line in enumerate(input_lines):
        if skip_line:
            skip_line = False
            continue

        if line.strip().startswith("-") or line.strip().startswith("*"):
            if i + 1 < len(input_lines) and (len(input_lines[i + 1].strip("\n")) >= 20):
                results.append(line)
            else:
                skip_line = True
        else:
            if len(line.strip("\n")) >= 20:
                results.append(line)
    return "\n".join(results)


class FullURLParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, url: str, type: str) -> Document:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        for a_tag in soup.find_all("a"):
            text = a_tag.get_text(strip=False)
            # do we put text here? it was diff in diff versions
            a_tag.replace_with(text)
        for tag in soup.find_all("cite"):
            tag.decompose()
        for br in soup.find_all("br"):
            br.replace_with("\n")
        res = "".join(convert_to_markdown(tag) for tag in soup.find_all() if tag.name)

        # NEW:
        res = process_lines(res.split("\n"))

        return Document(content=res, url=url, type=type)

    def extract(self, url: str, type: str = "web-markdown") -> Document:
        logger.info(f"Attempting to parse text to markdown from URL: {url}")
        r = self._extract(url=url, type=type)
        logger.info("✅ Extracted from url.")
        return r


class FandomParserOther(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, character_name: str, wiki: str):
        if not FANDOM_AVAILABLE:
            raise ImportError("fandom package not found. `pip install fandom-py`.")
        try:
            fandom.set_wiki(wiki)
            page = fandom.page(character_name)
            page_content = json.dumps(page.content)
        except Exception:
            raise ParserException(f"No results found for {character_name}.")

        return Document(content=page_content)

    def extract(self, character_name: str, wiki: str):
        logger.info(
            f"Attempting to extract Fandom, character_name: {character_name}, wiki {wiki}"
        )
        r = self._extract(character_name, wiki)
        logger.info("✅ Extracted fandom for character name.")
        return r
