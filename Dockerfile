# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-api.txt .
# pip's download cache is kept on the server between builds (clear: docker builder prune)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-api.txt

# Application code only. Species data (birds/, _index/, images/, translations/) is bind-mounted
# from the git checkout at runtime — so a data change does not rebuild this image.
COPY _scripts/ ./_scripts/
COPY _schemas/ ./_schemas/
COPY _templates/ ./_templates/
RUN mkdir -p birds _index images translations

EXPOSE 8000

# Two workers by default: slow work in one request (a cache miss, a busy MeiliSearch) cannot hold up the other process
CMD ["sh", "-c", "exec uvicorn _scripts.api:app --host 0.0.0.0 --port 8000 --workers ${API_WORKERS:-2}"]
