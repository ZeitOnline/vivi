# ZeitOnline/gh-action-workflows:nightwatch-build.yaml uses `target: nightwatch`
FROM python:3.13.7-slim@sha256:27f90d79cc85e9b7b2560063ef44fa0e9eaae7a7c3f5a9f74563065c5477cc24 AS nightwatch

COPY --from=ghcr.io/astral-sh/uv:0.8.13@sha256:4de5495181a281bc744845b9579acf7b221d6791f99bcc211b9ec13f417c2853 /uv /usr/bin/
ENV UV_NO_MANAGED_PYTHON=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_INDEX_PYPI_ZON_USERNAME="oauth2accesstoken"

RUN apt-get -y update &&  \ 
    apt-get install --no-install-recommends libgdk-pixbuf-xlib-2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN groupadd --gid=10000 app && \
    useradd --uid=10000 --gid=app --no-user-group \
    --create-home --home-dir /tmp app && \
    chown -R app:app /app
USER app
ENV PATH=/app/.venv/bin:$PATH

COPY pyproject.toml uv.lock ./
RUN --mount=type=secret,id=GCLOUD_TOKEN,env=UV_INDEX_PYPI_ZON_PASSWORD \
    uv sync

ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
USER root
RUN playwright install --with-deps firefox
USER app

COPY *.py ./
ENTRYPOINT ["pytest", "--tb=native"]

# Security updates run last, to intentionally bust the docker cache.
USER root
RUN apt-get update && apt-get -y upgrade && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
USER app
