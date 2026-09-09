FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh \
    && pip install --no-cache-dir ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
