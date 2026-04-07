FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN python -m venv .venv \
    && uv sync --no-group dev

FROM python:3.12.13-alpine3.23
LABEL author=ahagbes89@gmail.com
RUN adduser -u 10001 -D -h /app todo

WORKDIR /app
RUN apk add --no-cache zlib=1.3.2-r0
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /app/.venv /app/.venv
COPY *.py ./
COPY data.json ./

EXPOSE 8000
USER 10001

ENTRYPOINT ["/app/.venv/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]