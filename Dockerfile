FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y make build-essential && apt-get clean
COPY Makefile ./  
COPY ./src ./src
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY ./src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
