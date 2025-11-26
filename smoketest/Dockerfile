# ZeitOnline/gh-action-workflows:nightwatch-build.yaml uses `target: nightwatch`
FROM python:3.14.0-slim@sha256:0aecac02dc3d4c5dbb024b753af084cafe41f5416e02193f1ce345d671ec966e AS nightwatch

COPY --from=ghcr.io/astral-sh/uv:0.9.12@sha256:0eaa66c625730a3b13eb0b7bfbe085ed924b5dca6240b6f0632b4256cfb53f31 /uv /usr/bin/
ENV UV_NO_MANAGED_PYTHON=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_INDEX_PYPI_ZON_USERNAME="oauth2accesstoken"

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
