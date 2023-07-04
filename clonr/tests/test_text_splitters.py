from pathlib import Path

import pytest

from clonr.data.text_splitters import (
    CharSplitter,
    SentenceSplitter,
    TokenSplitter,
    _is_asian_language,
    _is_english,
    _regex_split,
)
from clonr.utils.shared import get_tiktoken_tokenizer


@pytest.fixture
def corpus():
    path = Path(__file__).parent.parent / "data" / "assets" / "lebron-wiki.txt"
    with open(path, "r") as f:
        return f.read()


def test_language_heuristics():
    assert not _is_asian_language("привет, меня зовут Джонни")
    assert not _is_asian_language("hola como está?")
    assert not _is_english("привет, меня зовут Джонни")
    assert _is_english("hi how are you?")
    assert _is_asian_language("我做出了可怕的人生选择, lol this is chinese")
    assert not _is_english("hola como está?")


def test_regex_split():
    s = "foo. bar!?! and baz... ok."
    r = ["foo.", " bar!?!", " and baz...", " ok."]
    assert _regex_split(s, r"[\?\!\.]+", True) == r
    assert _regex_split(s, r"[\?\!\.]+", False) == ["foo", " bar", " and baz", "ok"]


@pytest.mark.parametrize("overlap", [0])
@pytest.mark.parametrize("size", [128])
def test_splitters(corpus, size, overlap):
    splitter = SentenceSplitter(max_chunk_size=size, min_chunk_size=0, overlap=overlap)
    arr = splitter.split(corpus)
    assert len(arr) > 1
    assert len(corpus) - 500 < sum(map(len, arr)) < len(corpus) + 500

    tokenizer = get_tiktoken_tokenizer("gpt-3.5-turbo")
    splitter = TokenSplitter(
        tokenizer=tokenizer, chunk_size=size, chunk_overlap=overlap
    )
    arr = splitter.split(corpus)
    assert len(arr) > 1
    assert len(corpus) - 500 < sum(map(len, arr)) < len(corpus) + 500

    splitter = CharSplitter(tokenizer=tokenizer, chunk_size=size, chunk_overlap=overlap)
    arr = splitter.split(corpus)
    assert len(arr) > 1
    assert len(corpus) - 500 < sum(map(len, arr)) < len(corpus) + 500
