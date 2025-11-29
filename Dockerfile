FROM python:3.13-alpine3.22

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev

ENV PYTHONPATH=/app

COPY ./pyproject.toml ./pyproject.toml
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/
COPY ./uv.lock /app/ 
COPY ./app /app/app
COPY ./entrypoint.sh /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["celery", "-A", "app.celery", "worker", "--loglevel=INFO", "-B", "--logfile=logs/celery.log", "--concurrency", "1"]
