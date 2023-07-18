from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EncodeQueryRequest(_message.Message):
    __slots__ = ["text"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, text: _Optional[_Iterable[str]] = ...) -> None: ...

class EncodePassageRequest(_message.Message):
    __slots__ = ["text"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, text: _Optional[_Iterable[str]] = ...) -> None: ...

class RankingScoreRequest(_message.Message):
    __slots__ = ["query", "passages"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    PASSAGES_FIELD_NUMBER: _ClassVar[int]
    query: str
    passages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, query: _Optional[str] = ..., passages: _Optional[_Iterable[str]] = ...) -> None: ...

class RankingScoreResponse(_message.Message):
    __slots__ = ["scores"]
    SCORES_FIELD_NUMBER: _ClassVar[int]
    scores: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, scores: _Optional[_Iterable[float]] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ["embedding"]
    EMBEDDING_FIELD_NUMBER: _ClassVar[int]
    embedding: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, embedding: _Optional[_Iterable[float]] = ...) -> None: ...

class EmbeddingResponse(_message.Message):
    __slots__ = ["embeddings"]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    embeddings: _containers.RepeatedCompositeFieldContainer[Embedding]
    def __init__(self, embeddings: _Optional[_Iterable[_Union[Embedding, _Mapping]]] = ...) -> None: ...
