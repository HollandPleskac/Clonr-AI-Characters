from clonr.text_splitters import DynamicTextSplitter, SentenceSplitter, TokenSplitter
from clonr.tokenizer import Tokenizer

SHARED_TOKENIZER = Tokenizer.from_huggingface("hf-internal-testing/llama-tokenizer")

# if settings.LLM == "mock":
#     SHARED_TOKENIZER = Tokenizer.from_openai("gpt-3.5-turbo")
# elif settings.LLM in ["llamacpp", "colab"]:
#     name = "hf-internal-testing/llama-tokenizer"
#     SHARED_TOKENIZER = Tokenizer.from_huggingface(name)
# elif settings.LLM.startswith("gpt"):
#     SHARED_TOKENIZER = Tokenizer.from_openai(settings.LLM)
# else:
#     raise ValueError(settings.LLM)

SHARED_DYNAMIC_SPLITTER = DynamicTextSplitter(
    sentence_splitter=SentenceSplitter(tokenizer=SHARED_TOKENIZER, use_tokens=True),
    token_splitter=TokenSplitter(
        tokenizer=SHARED_TOKENIZER,
    ),
)
