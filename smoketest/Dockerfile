# See https://github.com/ZeitOnline/gh-action-workflows/blob/main/.github/workflows/nightwatch-build.yaml
FROM python:3.12.4-slim@sha256:a3e58f9399353be051735f09be0316bfdeab571a5c6a24fd78b92df85bcb2d85 as nightwatch
WORKDIR /app
RUN pip --no-cache-dir install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv sync
COPY *.py ./
# See https://github.com/ZeitOnline/kustomize/blob/main/components/nightwatch/deployment.yaml
ENTRYPOINT ["pipenv", "run", "pytest", "--tb=native"]
