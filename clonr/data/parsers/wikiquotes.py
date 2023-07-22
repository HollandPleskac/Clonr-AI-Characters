import requests
from bs4 import BeautifulSoup
from clonr.data_structures import Document
from clonr.data.parsers.base import Parser, ParserException
from clonr.utils.shared import instance_level_lru_cache
from loguru import logger


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

        search_results = soup.find_all("li", {"class": "mw-search-result"})
        if not search_results:
            raise ParserException(f"No results found for {character_name}.")

        character_link = search_results[0].find("a")["href"]
        character_url = f"{base_url}{character_link}"

        response = requests.get(character_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        quote_sections = soup.find_all("span", {"class": "mw-headline"})

        quotes = []
        for section in quote_sections[:10]:
            section_name = section.text.strip()
            quotes_list = section.find_next("ul")
            for quote in quotes_list:
                quotes.append(quote.text.strip())

        # dedup
        quotes = list(set(quotes))

        return Document(content="\n\n".join(quotes))

    def extract(self, character_name: str):
        logger.info(
            f"Attempting to extract Wikiquotes, character_name: {character_name}"
        )
        r = self._extract(character_name)
        logger.info("✅ Extracted for character name.")
        return r
