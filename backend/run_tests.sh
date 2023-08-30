set -e
export EMBEDDINGS_GRPC_HOST=localhost
export REDIS_HOST=localhost
export POSTGRES_HOST=localhost
export LLM=mock
export OTEL_EXPORTER_OTLP_ENDPOINT=localhost:4317
export DEV=True

echo "---- RUNNING UNIT TESTS ----"
pytest \
    -v \
    --disable-warnings \
    --pdb \
    --cov-report term-missing:skip-covered \
    --cov-report html \
    --cov=app \
    ./tests 

echo "\n---- RUNNING INTEGRATION TESTS ----"
pytest -v -o log_cli=True --log-cli-level=INFO --disable-warnings --pdb ./integration_tests 
