from app.clone.shared import (
    SHARED_DYNAMIC_SPLITTER,
    SHARED_TOKENIZER,
    DynamicTextSplitter,
)
from clonr.tokenizer import Tokenizer


async def get_text_splitter() -> DynamicTextSplitter:
    yield SHARED_DYNAMIC_SPLITTER


async def get_tokenizer() -> Tokenizer:
    yield SHARED_TOKENIZER
