compile_protobuf_code:
	chmod u+x ./compile_proto.sh
	./compile_proto

run_tests:
	poetry run pytest tests/

format:
	poetry run black .
	poetry run isort .

lint:
	poetry run mypy .
	poetry run black . --check
	poetry run isort . --check
	poetry run flake8 .