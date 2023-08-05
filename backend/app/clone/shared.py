from app.settings import settings
from clonr.text_splitters import DynamicTextSplitter, SentenceSplitter, TokenSplitter
from clonr.tokenizer import Tokenizer

if settings.LLM == "mock":
    SHARED_TOKENIZER = Tokenizer.from_openai("gpt-3.5-turbo")
else:
    SHARED_TOKENIZER = Tokenizer.from_openai(settings.LLM)

SHARED_DYNAMIC_SPLITTER = DynamicTextSplitter(
    sentence_splitter=SentenceSplitter(tokenizer=SHARED_TOKENIZER, use_tokens=True),
    token_splitter=TokenSplitter(
        tokenizer=SHARED_TOKENIZER,
    ),
)
