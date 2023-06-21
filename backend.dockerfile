FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN apt update && \
        apt install -y curl && \
        curl -sSL https://install.python-poetry.org | python3 - && \
        /root/.local/bin/poetry config virtualenvs.create false && \
        /root/.local/bin/poetry install

COPY migrations/ tunetime/ alembic.ini ./tunetime/
CMD ["uvicorn", "tunetime.app:app", "--port", "5555", "--host", "0.0.0.0"]
