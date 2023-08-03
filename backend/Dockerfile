FROM python:3.10-slim

ENV PYTHONUNBUFFERED=true \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  DEBIAN_FRONTEND=noninteractive

RUN python -m pip install --no-cache-dir --upgrade pip

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN --mount=type=cache,target=/root/.cache/pip python3.10 -m pip install --no-cache-dir --upgrade -r requirements.txt

RUN python -c "import nltk; nltk.download('punkt')"

COPY ./alembic.ini /alembic.ini
COPY ./migrations /migrations
COPY ./app /app
COPY ./pb /pb
COPY ./clonr /clonr

# Testing. We'll remove all of this in prod and have two dockerfiles
RUN poetry export -f requirements.txt --output requirements_only_dev.txt --only dev
RUN --mount=type=cache,target=/root/.cache/pip python3.10 -m pip install -r requirements_only_dev.txt

COPY ./tests /tests
COPY ./.env.dev /.env

# To test, run: docker exec -it <container-id-here> pytest -v--disable-warnings ./tests

ENTRYPOINT [ "python", "-m", "app.main"]