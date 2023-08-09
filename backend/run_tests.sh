EMBEDDINGS_GRPC_HOST=localhost \
REDIS_HOST=localhost \
POSTGRES_HOST=localhost \
LLM=mock \
pytest -v --disable-warnings --pdb ./tests 

