from typing import AsyncGenerator

from app.clone.shared import (
    SHARED_DYNAMIC_SPLITTER,
    SHARED_TOKENIZER,
    DynamicTextSplitter,
)
from clonr.tokenizer import Tokenizer


async def get_text_splitter() -> AsyncGenerator[DynamicTextSplitter, None]:
    yield SHARED_DYNAMIC_SPLITTER


async def get_tokenizer() -> AsyncGenerator[Tokenizer, None]:
    yield SHARED_TOKENIZER
