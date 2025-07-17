# ZeitOnline/gh-action-workflows:nightwatch-build.yaml uses `target: nightwatch`
FROM python:3.13.5-slim@sha256:6544e0e002b40ae0f59bc3618b07c1e48064c4faed3a15ae2fbd2e8f663e8283 AS nightwatch

COPY --from=ghcr.io/astral-sh/uv:0.7.21@sha256:a64333b61f96312df88eafce95121b017cbff72033ab2dbc6398edb4f24a75dd /uv /usr/bin/
ENV UV_NO_MANAGED_PYTHON=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1

WORKDIR /app
RUN groupadd --gid=10000 app && \
    useradd --uid=10000 --gid=app --no-user-group \
    --create-home --home-dir /app app && \
    chown -R app:app /app
USER app
ENV PATH=/app/.venv/bin:$PATH

COPY pyproject.toml uv.lock ./
RUN uv sync
USER root
RUN playwright install-deps firefox
USER app
RUN playwright install firefox

COPY *.py ./
ENTRYPOINT ["pytest", "--tb=native"]

# Security updates run last, to intentionally bust the docker cache.
USER root
RUN apt-get update && apt-get -y upgrade && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
USER app
