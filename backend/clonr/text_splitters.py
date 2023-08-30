import re
import warnings
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Literal, TypeVar

from loguru import logger

try:
    from nltk.tokenize import sent_tokenize as _nltk_sent_tokenize

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
try:
    import spacy

    SPACY_AVAILABLE = True

    @lru_cache(maxsize=None)
    def _load_spacy_tokenizer():
        return spacy.load("en_core_web_sm")

except ImportError:
    SPACY_AVAILABLE = False

from clonr.data_structures import Chunk, Document
from clonr.tokenizer import Tokenizer

T = TypeVar("T")

# TODO (Jonny): We need a tokenizer that can split on lines of dialogue! Should
# be able to rig this by using the regex_split function.
# NOTE (Jonny): default chunk sizes and overlaps were tested manually, and gave the best results.
# For our type of retrieval it's often better to select a larger passage, and indexing more nodes
# upfront is acceptable. rule of thumb: 1 token = 4 chars


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


def regex_split(text: str, pattern: str, include_separator: bool) -> list[str]:
    """The recommended way to write a pattern would be something like this:
    r'[\?\!\.]+'. This captures stuff like What?!?! or ok... Note (Jonny): that if you
    wrap in parenthesis () with include_separator=False, you'll get chunks that
    consist of only the separator. Not a bug, but a feature I guess :)."""
    _validate_regex_split_pattern(pattern)
    if include_separator:
        pattern = pattern if pattern[0] == "(" else f"({pattern})"
    raw_splits = re.split(pattern, text)
    splits = [x for x in raw_splits if isinstance(x, str)]
    if include_separator:
        splits = ["".join(splits[i : i + 2]) for i in range(0, len(splits), 2)]
    return [x for x in splits if x]


def _chunk_with_overlap(
    arr: list[T],
    size: int,
    overlap: int,
) -> list[list[T]]:
    res: list[list[T]] = []
    stride = size - overlap
    for i in range(0, N := len(arr), stride):
        res.append(arr[i : i + size])
        if i + size > N:
            break
    return res


def _chunk_evenly(arr: list[T], max_size: int) -> list[list[T]]:
    N = len(arr)
    if max_size >= N:
        return [arr]
    # the last part says if there's leftover, add one more chunk
    n_splits = N // max_size + bool(N % max_size)
    chunk_size, remainder = divmod(N, n_splits)
    res: list[list[T]] = []
    index = 0
    for i in range(n_splits):
        # for each leftover, add a new section size that's +1 bigger
        size = chunk_size + int(i <= remainder)
        res.append(arr[index : index + size])
        index += size
    return res


def chunk(arr: list[T], size: int, overlap: int) -> list[list[T]]:
    assert overlap < size, "Overlap cannot be >= chunk size."
    if not arr:
        return []
    size = max(1, size)
    overlap = max(0, overlap)
    if overlap <= 0:
        return _chunk_evenly(arr, max_size=size)
    else:
        return _chunk_with_overlap(arr, size=size, overlap=overlap)


def aggregate_with_overlaps(
    arr: list[T], size_arr: list[int], max_chunk_size: int, overlap: int
) -> list[list[T]]:
    assert overlap < max_chunk_size
    assert len(arr) == len(size_arr)
    assert all(
        x <= max_chunk_size for x in size_arr
    ), "Run split large chunks first to ensure no chunks are above max size, i.e. stepping would never happen."
    l, r, N = 0, 0, len(arr)
    chunks: list[list[T]] = []
    while r < N:
        # forward step until you've collected up to max_chunk_size tokens
        size = 0
        while r < N and (size + size_arr[r]) <= max_chunk_size:
            size += size_arr[r]
            r += 1
        chunks.append(arr[l:r])

        # backtrack until you've collected up to an amount "overlap" of tokens, but still at least one step
        # forward from the last chunk
        cur_overlap = 0
        while r > l + 1 and (cur_overlap + size_arr[r - 1]) <= overlap:
            cur_overlap += size_arr[r - 1]
            r -= 1
        l = r
    return chunks


class TextSplitter(ABC):
    name: str = "TextSplitter"

    def __init__(
        self,
        max_chunk_size: int,
        min_chunk_size: int,
        chunk_overlap: int,
    ):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def _split_text(self, text: str) -> list[str]:
        pass

    def _split_doc(self, doc: Document) -> list[Chunk]:
        splits = self._split_text(doc.content)
        chunks = [
            Chunk(content=x, document_id=doc.id, index=i) for i, x in enumerate(splits)
        ]
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


class BaseSentenceSplitter(TextSplitter):
    """Performs splitting at the sentence level, using either
    spacy or nltk for determining sentence boundaries. Warning,
    those tools use external models which require memory and time.
    """

    def __init__(
        self,
        max_chunk_size: int,
        min_chunk_size: int,
        chunk_overlap: int,
        backend: Literal["spacy", "nltk"],
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
        if chunk_overlap > max_chunk_size:
            raise ValueError("Cannot specify overlap to be larger than the chunk size")
        super().__init__(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            chunk_overlap=chunk_overlap,
        )
        match backend:
            case "spacy":
                assert SPACY_AVAILABLE, "spacy is not available."
                self._spacy_tokenizer = _load_spacy_tokenizer()
            case "nltk":
                assert NLTK_AVAILABLE, "nltk is not available."
            case _:
                raise ValueError(f"Unsupported backend: {self.backend}")
        self.backend = backend

    def _text_to_sentences(self, text: str) -> list[str]:
        match self.backend:
            case "spacy":
                sents: list[str] = self._spacy_tokenizer(text).sents
                return sents
            case "nltk":
                # ntlk removes the left space, which is kind of weird. This could mess up newlines but whateva
                sents: list[str] = _nltk_sent_tokenize(text)
                return [" " + x.lstrip() if i else x for i, x in enumerate(sents)]
            case _:
                raise ValueError("Unsupported backend")

    def _aggregate_small_chunks_in_place(self, arr: list[T]) -> None:
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
                return None

    def _split_large_chunks(self, arr: list[T]) -> list[T]:
        return [x for y in arr for x in chunk(y, self.max_chunk_size, overlap=0)]

    def _split_text(self, text: str) -> list[str]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f"{name}(max={self.max_chunk_size}, min={self.min_chunk_size}, "
            f"overlap={self.chunk_overlap})"
        )


class SentenceSplitterTokens(BaseSentenceSplitter):
    name: str = "SentenceSplitterTokens"

    def __init__(
        self,
        tokenizer: Tokenizer,
        max_chunk_size: int = 160,
        min_chunk_size: int = 30,
        chunk_overlap: int = 100,
        backend: Literal["spacy", "nltk"] = "nltk",
    ):
        super().__init__(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            chunk_overlap=chunk_overlap,
            backend=backend,
        )
        self.tokenizer = tokenizer

    def _split_text(self, text: str) -> list[str]:
        if _is_asian_language(text):
            warnings.warn(
                "Using SentenceSplitter with non-latin alphabets will lead to errors!"
            )
        sentences = self._text_to_sentences(text)
        ids = self.tokenizer.encode_batch(sentences)
        if self.chunk_overlap > 0:
            ids = self._split_large_chunks(ids)
            size_arr = [len(x) for x in ids]
            sentences = self.tokenizer.decode_batch(ids)
            groups = aggregate_with_overlaps(
                sentences,
                size_arr=size_arr,
                max_chunk_size=self.max_chunk_size,
                overlap=self.chunk_overlap,
            )
            sentences = ["".join(g) for g in groups]
        else:
            self._aggregate_small_chunks_in_place(ids)
            ids = self._split_large_chunks(ids)
            sentences = self.tokenizer.decode_batch(ids)
        return sentences


class SentenceSplitterChars(BaseSentenceSplitter):
    name: str = "SentenceSplitterChars"

    def __init__(
        self,
        max_chunk_size: int = 640,
        min_chunk_size: int = 120,
        chunk_overlap: int = 400,
        backend: Literal["spacy", "nltk"] = "nltk",
    ):
        super().__init__(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            chunk_overlap=chunk_overlap,
            backend=backend,
        )

    def _split_text(self, text: str) -> list[str]:
        if _is_asian_language(text):
            warnings.warn(
                "Using SentenceSplitter with non-latin alphabets will lead to errors!"
            )
        sentences = self._text_to_sentences(text)
        if self.chunk_overlap > 0:
            sentences = self._split_large_chunks(sentences)
            size_arr = [len(x) for x in sentences]
            groups = aggregate_with_overlaps(
                sentences,
                size_arr=size_arr,
                max_chunk_size=self.max_chunk_size,
                overlap=self.chunk_overlap,
            )
            sentences = ["".join(g) for g in groups]
        else:
            self._aggregate_small_chunks_in_place(sentences)
            sentences = self._split_large_chunks(sentences)
        return sentences


class CharSplitter(TextSplitter):
    """a class to chunk of up long form text into smaller pieces.
    This is useful for creating digestible chunks for sentence embeddings,
    and also for ingesting text that is too long to fit within a context window.
    """

    name: str = "CharacterSplitter"

    def __init__(
        self,
        max_chunk_size: int = 400,
        chunk_overlap: int = 200,
        min_chunk_size: int = 1,
    ):
        super().__init__(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _split_text(self, text: str) -> list[str]:
        text_arr = list(text)
        arr = chunk(text_arr, size=self.max_chunk_size, overlap=self.chunk_overlap)
        sentences = ["".join(x) for x in arr]
        return sentences

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f"{name}(chunk_size={self.max_chunk_size}, "
            f"overlap={self.chunk_overlap})"
        )


class TokenSplitter(TextSplitter):
    name: str = "TokenSplitter"

    def __init__(
        self,
        tokenizer: Tokenizer,
        max_chunk_size: int = 100,
        chunk_overlap: int = 50,
        min_chunk_size: int = 1,
    ):
        """Shit, the token splitting process can destroy the original string,
        if for example the tokenizer is lower case.

        Args:
            chunk_size (int): _description_
            chunk_overlap (int): _description_
            tokenizer (Tokenizer): _description_
        """
        super().__init__(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_size = min_chunk_size
        self.tokenizer = tokenizer

    def _split_text(self, text: str) -> list[str]:
        arr = self.tokenizer.encode(text)
        chunks = chunk(arr, size=self.max_chunk_size, overlap=self.chunk_overlap)
        return ["".join(self.tokenizer.decode(x)) for x in chunks]

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f"{name}(chunk_size={self.max_chunk_size}, "
            f"overlap={self.chunk_overlap}, tokenizer={self.tokenizer})"
        )


ST = TypeVar("ST", bound=BaseSentenceSplitter)


# All of this is so hacky to just try to display which one was chose dynamically...
class DynamicTextSplitter(TextSplitter):
    def __init__(self, sentence_splitter: ST, token_splitter: TokenSplitter):
        self.sentence_splitter = sentence_splitter
        self.token_splitter = token_splitter
        self._max_chunk_size = None
        self._min_chunk_size = None
        self._chunk_overlap = None
        self._name = None
        self._rep = "DynamicTextSplitter()"

    def _split_text(self, text: str) -> list[str]:
        if _is_asian_language(text):
            logger.info("Detected Asian language. Switching to TokenSplitter")
            self._max_chunk_size = self.token_splitter.max_chunk_size
            self._min_chunk_size = self.token_splitter.min_chunk_size
            self._chunk_overlap = self.token_splitter.chunk_overlap
            self._name = self.token_splitter.name
            self._rep = self.token_splitter.__repr__()
            return self.token_splitter._split_text(text)
        else:
            self._max_chunk_size = self.sentence_splitter.max_chunk_size
            self._min_chunk_size = self.sentence_splitter.min_chunk_size
            self._chunk_overlap = self.sentence_splitter.chunk_overlap
            self._name = self.sentence_splitter.name
            self._rep = self.sentence_splitter.__repr__()
            return self.sentence_splitter._split_text(text)

    def __repr__(self):
        return self._rep

    @property
    def name(self):
        return self._name

    @property
    def max_chunk_size(self):
        return self._max_chunk_size

    @property
    def min_chunk_size(self):
        return self._min_chunk_size

    @property
    def chunk_overlap(self):
        return self._chunk_overlap
