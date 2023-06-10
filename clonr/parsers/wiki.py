from typing import Any, List

from clonr.data_structures import Document
from clonr.parsers.base import Parser, ParserException


class WikipediaParser(Parser):
    def extract(
        self, pages: str | list[str], lang: str = "en", **load_kwargs: Any
    ) -> Document | list[Document]:
        if not isinstance(pages, list):
            return self.extract([pages], lang=lang, **load_kwargs)[0]

        documents = []
        for page in pages:
            try:
                import wikipedia
            except ImportError:
                raise ImportError(
                    "Please install the `wikipedia` package: `pip install wikipedia`"
                )

            wikipedia.set_lang(lang)

            try:
                page_content = wikipedia.page(page, **load_kwargs).content
            except wikipedia.exceptions.DisambiguationError as e:
                raise ParserException(
                    f"Failed to parse Wikipedia page: {page}. Reason: {str(e)}"
                )
            except wikipedia.exceptions.PageError as e:
                raise ParserException(f"Wikipedia page not found: {page}")

            documents.append(Document(content=page_content))

        return documents
