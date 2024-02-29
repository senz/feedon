# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.11-alpine AS builder

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip apk add --no-cache musl-dev libffi-dev gcc curl bash \
&& curl -sSL https://bootstrap.pypa.io/get-pip.py | python3 \
&& python3 -m pip install --no-cache-dir pipx \
&& python3 -m pipx ensurepath

COPY . /app

RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --no-cache-dir poetry==1.8.1 \
    && poetry install --no-dev --no-root

ENTRYPOINT ["poetry", "run", "flask", "run"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
