FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libraw-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src

RUN pip install --no-cache-dir -U pip setuptools wheel \
    && pip install --no-cache-dir .

FROM runtime AS worker
ENTRYPOINT ["cameraftp", "worker"]
CMD ["-l", "INFO", "-P", "solo"]

FROM runtime AS serve
ENTRYPOINT ["cameraftp", "serve"]
CMD ["--host", "0.0.0.0", "--user", "user", "--password", "pass"]

FROM runtime AS cli
ENTRYPOINT ["cameraftp"]
CMD ["--help"]
