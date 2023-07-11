import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Literal, Sequence, TypeVar

try:
    from nltk.tokenize import sent_tokenize as _nltk_sent_tokenize

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    warnings.warn(
        (
            "NLTK sent tokenize was not found. `pip install nltk` "
            "and ensure python -c 'import nltk; nltk.download('punkt') "
            "has been run. This downloads the english tokenizer."
        )
    )
try:
    import spacy

    SPACY_AVAILABLE = True

    @lru_cache(maxsize=None)
    def _load_spacy_tokenizer():
        return spacy.load("en_core_web_sm")

except ImportError:
    SPACY_AVAILABLE = False
    warnings.warn(
        (
            "Spacy was not found. `pip install spacy` "
            "and check that the en_core_web_sm pipeline is loaded."
        )
    )

from clonr.data_structures import Chunk, Document
from clonr.tokenizer import Tokenizer

T = TypeVar("T")


# TODO (Jonny): We need a tokenizer that can split on lines of dialogue! Should
# be able to rig this by using the regex_split function.


@dataclass
class DEFAULTS:
    max_chunk_size_chars: int = 512
    min_chunk_size_chars: int = 64
    max_chunk_size_tokens: int = 128
    min_chunk_size_tokens: int = 16
    overlap_chars: int = 128
    overlap_tokens: int = 32


def _is_asian_language(s: str):
    # Seems like the asian languages start at 0x2E80 or 11905 in base10
    # https://jrgraphix.net/r/Unicode/
    # Heuristic that counts if at least 25% of characters are asian
    return sum(ord(x) < 11900 for x in s) < 0.75 * len(s)


def _is_english(s: str):
    """Heuristic that counts if 95% of characters are latin"""
    return sum(ord(x) < 128 for x in s) > 0.95 * len(s)


@lru_cache(maxsize=None)
def _validate_regex_split_pattern(s: str) -> None:
    if not s:
        raise ValueError("Cannot have empty split pattern.")
    if (l := s.count("(")) != s.count(")"):
        raise ValueError("Regex split pattern is missing parenthesis")
    if l > 1:
        raise ValueError("Regex split may only have one capturing group")
    if l and not (s.startswith("(") and s.endswith(")")):
        raise ValueError(
            "Regex split must capture the entire pattern or nothing at all."
        )


def regex_split(text: str, pattern: str, include_separator: bool) -> str:
    """The recommended way to write a pattern would be something like this:
    r'[\?\!\.]+'. This captures stuff like What?!?! or ok... Note (Jonny): that if you
    wrap in parenthesis () with include_separator=False, you'll get chunks that
    consist of only the separator. Not a bug, but a feature I guess :)."""
    _validate_regex_split_pattern(pattern)
    if include_separator:
        pattern = pattern if pattern[0] == "(" else f"({pattern})"
    splits = re.split(pattern, text)
    if include_separator:
        splits = ["".join(splits[i : i + 2]) for i in range(0, len(splits), 2)]
    return [x for x in splits if x]


def _chunk_with_overlap(
    arr: Sequence[T],
    size: int,
    overlap: int,
) -> T:
    res = []
    stride = size - overlap
    for i in range(0, N := len(arr), stride):
        res.append(arr[i : i + size])
        if i + size > N:
            break
    return res


def _chunk_evenly(arr: Sequence[T], max_size: int) -> list[T]:
    N = len(arr)
    if max_size >= N:
        return [arr]
    # the last part says if there's leftover, add one more chunk
    n_splits = N // max_size + bool(N % max_size)
    chunk_size, remainder = divmod(N, n_splits)
    res, index = [], 0
    for i in range(n_splits):
        # for each leftover, add a new section size that's +1 bigger
        size = chunk_size + int(i <= remainder)
        res.append(arr[index : index + size])
        index += size
    return res


def chunk(arr: Sequence[T], size: int, overlap: int) -> list[list[T]]:
    assert overlap < size, "Overlap cannot be >= chunk size."
    if not arr:
        return arr
    size = max(1, size)
    overlap = max(0, overlap)
    if overlap <= 0:
        return _chunk_evenly(arr, max_size=size)
    else:
        return _chunk_with_overlap(arr, size=size, overlap=overlap)


class TextSplitter(ABC):
    @abstractmethod
    def _split_text(self, text: str) -> list[str]:
        pass

    def _split_doc(self, doc: Document) -> list[Chunk]:
        splits = self._split_text(doc.content)
        chunks = [Chunk(content=x, document_id=doc.id) for x in splits]
        if len(chunks) > 1:
            for i in range(len(chunks)):
                if i:
                    chunks[i].previous = chunks[i - 1]
                if i < len(chunks) - 1:
                    chunks[i].next = chunks[i + 1]
        return chunks

    def split(self, inp: str | Document) -> list[str]:
        if isinstance(inp, Document):
            return self._split_text(inp.content)
        elif isinstance(inp, str):
            return self._split_text(inp)
        else:
            raise TypeError(f"Invalid input type to TextSplitter: ({type(inp)})")


class SentenceSplitter(TextSplitter):
    """Performs splitting at the sentence level, using either
    spacy or nltk for determining sentence boundaries. Warning,
    those tools use external models which require memory and time.
    """

    def __init__(
        self,
        max_chunk_size: int | None = None,
        min_chunk_size: int | None = None,
        overlap: int = 0,
        backend: Literal["spacy", "nltk"] = "nltk",
        tokenizer: Tokenizer | None = None,
        use_tokens: bool = False,
    ):
        """Constructor for SentenceSplitter

        A "chunk" can be one or more sentences. We start by tokenizing into
        sentences, which form the chunks. We then progressively aggregate until all
        chunks are of `min_chunk_size`. This is not done in any kind of optimal
        way, we simply go in list order merging nearest neighbors. Note,
        that max_chunk_size is not used here.

        Next, if any sentences are beyond the max_chunk_size, they are split into the largest
        sub chunks possible, and added back into the chunks list.

        Finally, the overlap specifies how many characters max we want for overlap. A value
        of zero will not do any overlap. The algo works by concat'ing as many sentences as possible up to
        max_chunk_size, then it back tracks until the tokens are more than overlap, and uses that +1 as
        the new starting point.

        The tokenizer version is alot slower, 2ms / 2200 chars vs 0.1ms / 2200 chars (20x slower to tokenize)
        It can also be destructive, if the tokenizer only uses lowercase for example. That's because to
        split on tokens, we have to run detokenize(tokenize(text)), which may not be an identity.

        Args:
            max_chunk_size (int): maximum number of characters per chunk.
            min_chunk_size (int, optional): minimum number of characters per chunk. Defaults to 0.
            overlap (int, optional): number of max chars to overlap. Defaults to 0.
            backend (Literal[&quot;spacy&quot;, &quot;nltk&quot;], optional): which backend for
                sentence tokenization. Defaults to "nltk".
            tokenizer (transformers tokenizer): If specified, will use tokens instead of characters. Defaults to None.

        Raises:
            ValueError: Overlap cannot be larger than the chunk size
            ValueError: Unsupported backend
        """
        self.use_tokens = use_tokens
        if self.use_tokens:
            max_chunk_size = (
                max_chunk_size
                if max_chunk_size is not None
                else DEFAULTS.max_chunk_size_tokens
            )
            min_chunk_size = (
                min_chunk_size
                if min_chunk_size is not None
                else DEFAULTS.min_chunk_size_tokens
            )
            overlap = overlap if overlap is None else DEFAULTS.overlap_tokens
        else:
            max_chunk_size = (
                max_chunk_size
                if max_chunk_size is not None
                else DEFAULTS.max_chunk_size_chars
            )
            min_chunk_size = (
                min_chunk_size
                if min_chunk_size is not None
                else DEFAULTS.min_chunk_size_chars
            )
            overlap = overlap if overlap is not None else DEFAULTS.overlap_chars
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        if overlap > max_chunk_size:
            raise ValueError("Cannot specify overlap to be larger than the chunk size")
        self.overlap = overlap
        self.backend = backend
        if self.backend == "spacy":
            assert SPACY_AVAILABLE, "spacy is not available."
            self._spacy_tokenizer = _load_spacy_tokenizer()
        elif self.backend == "nltk":
            assert NLTK_AVAILABLE, "nltk is not available."
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
        self.tokenizer = tokenizer
        self.use_tokens = use_tokens
        if self.use_tokens:
            assert (
                self.tokenizer is not None
            ), "If using tokens, must specify a tokenizer."

    def _text_to_sentences(self, text: str) -> list[str]:
        if self.backend == "spacy":
            return self._spacy_tokenizer(text).sents
        elif self.backend == "nltk":
            # ntlk removes the left space, which is kind of weird. This could mess up newlines but whateva
            return [
                " " + x.lstrip() if i else x
                for i, x in enumerate(_nltk_sent_tokenize(text))
            ]
        raise ValueError("Unsupported backend")

    def _sentences_to_overlapped_sentences(self, sentences: list):
        """Returns a list of sequences"""
        assert all(len(x) <= self.max_chunk_size for x in sentences)
        l, r = 0, 0
        N = len(sentences)
        res = []
        chunk = []
        chunk_len = 0
        for _ in range(N):
            # grab sentences while the chunk is under the limit
            while r < N and (chunk_len + len(sentences[r])) <= self.max_chunk_size:
                chunk.append(sentences[r])
                chunk_len += len(sentences[r])
                r += 1
            # add the completed chunk, you're now sitting on the newest element
            # if overlap were 0, you would repeat here
            if chunk and isinstance(chunk[0], str):
                chunk = " ".join(chunk)
            elif chunk and isinstance(chunk[0], list):
                chunk = [x for y in chunk for x in y]
            res.append(chunk)
            if r >= N:
                break
            overlap = 0
            # back track until you've hit no more than self.overlap characters
            # ensure at minimum you return to at least one space ahead of the last start
            while r > (l + 1) and (overlap + len(sentences[r - 1])) < self.overlap:
                r -= 1
                overlap += len(sentences[r - 1])
            l = r
            chunk = []
            chunk_len = 0
        return res

    def _aggregate_small_chunks(self, arr: list):
        no_edits = True
        for _ in range(len(arr)):
            # do this in reverse so we don't get a smaller array
            # re-allocation penalty
            for i in range(len(arr) - 1, 0, -1):
                if len(arr[i]) < self.min_chunk_size:
                    if len(arr[i - 1]) + len(arr[i]) < self.max_chunk_size:
                        arr[i - 1] += arr.pop(i)
                        no_edits = False
            if no_edits:
                return arr
        return arr

    def _split_large_chunks(self, arr: list):
        return [x for y in arr for x in chunk(y, self.max_chunk_size, overlap=0)]

    def _split_text(self, text: str) -> list[str]:
        if _is_asian_language(text):
            warnings.warn(
                (
                    "Yo you got chinese or some shit. Not gonna go well"
                    ", you better use the multilingual EmbeddingModel "
                    "and also not use nltk or these english-specific tokenizers."
                )
            )
        sentences = self._text_to_sentences(text)
        if self.tokenizer is not None:
            sentences = self.tokenizer.encode_batch(sentences)
        sentences = self._aggregate_small_chunks(sentences)
        sentences = self._split_large_chunks(sentences)
        if self.overlap > 0:
            sentences = self._sentences_to_overlapped_sentences(sentences)
        if self.tokenizer is not None:
            sentences = self.tokenizer.decode_batch(sentences)
        return sentences

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f"{name}(max={self.max_chunk_size}, min={self.min_chunk_size}, "
            f"overlap={self.overlap}, use_tokens={self.use_tokens})"
        )


class CharSplitter(TextSplitter):
    """a class to chunk of up long form text into smaller pieces.
    This is useful for creating digestible chunks for sentence embeddings,
    and also for ingesting text that is too long to fit within a context window.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = (
            chunk_size if chunk_size is not None else DEFAULTS.max_chunk_size_chars
        )
        self.chunk_overlap = (
            chunk_overlap if chunk_overlap is not None else DEFAULTS.overlap_chars
        )

    def _split_text(self, document: Document) -> list[str]:
        arr = chunk(document.content, size=self.chunk_size, overlap=self.overlap)
        sentences = ["".join(x) for x in arr]
        return sentences

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(chunk_size={self.chunk_size}, " f"overlap={self.overlap})"


class TokenSplitter(TextSplitter):
    def __init__(
        self,
        tokenizer: Tokenizer,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        """Shit, the token splitting process can destroy the original string,
        if for example the tokenizer is lower case.

        Args:
            chunk_size (int): _description_
            chunk_overlap (int): _description_
            tokenizer (Tokenizer): _description_
        """
        self.chunk_size = (
            chunk_size if chunk_size is not None else DEFAULTS.max_chunk_size_tokens
        )
        self.chunk_overlap = (
            chunk_overlap if chunk_overlap is not None else DEFAULTS.overlap_tokens
        )
        self.tokenizer = tokenizer

    def _split_text(self, text: str) -> list[str]:
        arr = self.tokenizer.encode(text)
        chunks = chunk(arr, size=self.chunk_size, overlap=self.chunk_overlap)
        return ["".join(self.tokenizer.decode(x)) for x in chunks]

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f"{name}(chunk_size={self.chunk_size}, "
            f"overlap={self.chunk_overlap}, tokenizer={self.tokenizer})"
        )
