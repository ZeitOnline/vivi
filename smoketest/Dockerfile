# See https://github.com/ZeitOnline/gh-action-workflows/blob/main/.github/workflows/nightwatch-build.yaml
FROM python:3.13.3-slim@sha256:60248ff36cf701fcb6729c085a879d81e4603f7f507345742dc82d4b38d16784 as nightwatch
WORKDIR /app
RUN pip --no-cache-dir install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv sync
RUN pipenv run playwright install firefox --with-deps
COPY *.py ./
# See https://github.com/ZeitOnline/kustomize/blob/main/components/nightwatch/deployment.yaml
ENTRYPOINT ["pipenv", "run", "pytest", "--tb=native"]
