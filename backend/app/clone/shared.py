from app.settings import settings
from clonr.text_splitters import (
    DynamicTextSplitter,
    SentenceSplitterTokens,
    TokenSplitter,
)
from clonr.tokenizer import Tokenizer

if settings.LLM == "mock":
    SHARED_TOKENIZER = Tokenizer.from_openai("gpt-3.5-turbo")
elif settings.LLM in ["llamacpp", "colab"]:
    name = "hf-internal-testing/llama-tokenizer"
    SHARED_TOKENIZER = Tokenizer.from_huggingface(name)
elif settings.LLM.startswith("gpt"):
    SHARED_TOKENIZER = Tokenizer.from_openai(settings.LLM)
else:
    raise ValueError(settings.LLM)

SHARED_DYNAMIC_SPLITTER = DynamicTextSplitter(
    sentence_splitter=SentenceSplitterTokens(tokenizer=SHARED_TOKENIZER),
    token_splitter=TokenSplitter(tokenizer=SHARED_TOKENIZER),
)
