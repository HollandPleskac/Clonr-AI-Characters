import requests
from bs4 import BeautifulSoup
from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache


class WikiQuotesParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, character_name: str):
        base_url = "https://en.wikiquote.org"
        search_url = f'{base_url}/w/index.php?title=Special:Search&profile=default&fulltext=Search&search={character_name.replace(" ", "+")}'

        response = requests.get(search_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        no_results_div = soup.find("div", {"class": "mw-search-nonefound"})
        if no_results_div:
            raise ParserException(f"No results found for {character_name}.")

        character_link = soup.find("a", {"class": "mw-search-result-heading"})["href"]
        character_url = f"{base_url}{character_link}"

        response = requests.get(character_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        quote_sections = soup.find_all("span", {"class": "mw-headline"})

        quotes = []
        for section in quote_sections:
            # section_name = section.text.strip()
            quotes_list = section.find_next("ul")
            quotes += [quote.text.strip() for quote in quotes_list.find_all("li")]

        return Document(content="\n".join(quotes))

    def extract(self, character_name: str):
        logger.info(
            f"Attempting to extract Wikiquotes, character_name: {character_name}"
        )
        r = self._extract(character_name)
        logger.info("✅ Extracted for character name.")
        return r
