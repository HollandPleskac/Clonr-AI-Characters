FROM python:3.10-slim

ENV PYTHONUNBUFFERED=true \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY ./models ./models

RUN python -m pip install --no-cache-dir --upgrade pip

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN --mount=type=cache,target=/root/.cache/pip python3.10 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app ./app

ENTRYPOINT [ "python", "-m", "app.main"]