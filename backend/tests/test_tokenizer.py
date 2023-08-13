from clonr.tokenizer import HuggingFaceTokenizer, OpenAITokenizer, Tokenizer


def test_openai_tokenizer():
    tok = OpenAITokenizer("gpt-3.5-turbo")
    assert len(tok.encode("foo bar baz foo bar baz")) > 2
    assert len(tok.encode_batch(4 * ["foo bar baz foo bar baz"])) == 4
    assert type(tok.decode(tok.encode("foo bar baz foo bar baz"))) == str
    assert tok.decode_batch(tok.encode_batch("foo bar baz foo bar baz"))


def test_huggingface_tokenizer():
    tok = HuggingFaceTokenizer(model="hf-internal-testing/llama-tokenizer")
    assert len(tok.encode("foo bar baz foo bar baz")) > 2
    assert len(tok.encode_batch(4 * ["foo bar baz foo bar baz"])) == 4
    assert type(tok.decode(tok.encode("foo bar baz foo bar baz"))) == str
    assert tok.decode_batch(tok.encode_batch("foo bar baz foo bar baz"))


def test_instantiations():
    name = "hf-internal-testing/llama-tokenize"
    assert isinstance(Tokenizer.from_openai("gpt-3.5-turbo"), OpenAITokenizer)
    assert isinstance(Tokenizer.from_huggingface(name), HuggingFaceTokenizer)
