# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: embed.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x65mbed.proto\"\"\n\x12\x45ncodeQueryRequest\x12\x0c\n\x04text\x18\x01 \x03(\t\"$\n\x14\x45ncodePassageRequest\x12\x0c\n\x04text\x18\x01 \x03(\t\"6\n\x13RankingScoreRequest\x12\r\n\x05query\x18\x01 \x01(\t\x12\x10\n\x08passages\x18\x02 \x03(\t\"&\n\x14RankingScoreResponse\x12\x0e\n\x06scores\x18\x01 \x03(\x02\"\x1e\n\tEmbedding\x12\x11\n\tembedding\x18\x01 \x03(\x02\"3\n\x11\x45mbeddingResponse\x12\x1e\n\nembeddings\x18\x01 \x03(\x0b\x32\n.Embedding2\xc5\x01\n\x05\x45mbed\x12:\n\rEncodeQueries\x12\x13.EncodeQueryRequest\x1a\x12.EmbeddingResponse\"\x00\x12=\n\x0e\x45ncodePassages\x12\x15.EncodePassageRequest\x1a\x12.EmbeddingResponse\"\x00\x12\x41\n\x10GetRankingScores\x12\x14.RankingScoreRequest\x1a\x15.RankingScoreResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'embed_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_ENCODEQUERYREQUEST']._serialized_start=15
  _globals['_ENCODEQUERYREQUEST']._serialized_end=49
  _globals['_ENCODEPASSAGEREQUEST']._serialized_start=51
  _globals['_ENCODEPASSAGEREQUEST']._serialized_end=87
  _globals['_RANKINGSCOREREQUEST']._serialized_start=89
  _globals['_RANKINGSCOREREQUEST']._serialized_end=143
  _globals['_RANKINGSCORERESPONSE']._serialized_start=145
  _globals['_RANKINGSCORERESPONSE']._serialized_end=183
  _globals['_EMBEDDING']._serialized_start=185
  _globals['_EMBEDDING']._serialized_end=215
  _globals['_EMBEDDINGRESPONSE']._serialized_start=217
  _globals['_EMBEDDINGRESPONSE']._serialized_end=268
  _globals['_EMBED']._serialized_start=271
  _globals['_EMBED']._serialized_end=468
# @@protoc_insertion_point(module_scope)
