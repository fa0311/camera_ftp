FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential
RUN apt-get install -y --no-install-recommends \
    libraw-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir -U pip setuptools wheel \
    && pip install --no-cache-dir -e .
COPY src /app/src
COPY configs /app/configs
