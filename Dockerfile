FROM python:3.12-slim

WORKDIR /app
# Устанавливаем git вместе с другими пакетами
RUN apt-get update && apt-get install -y make build-essential git && apt-get clean
COPY pyproject.toml poetry.lock ./
RUN pip install "poetry==1.5.1"
RUN poetry config virtualenvs.create false && poetry install --no-root
CMD ["gunicorn", "src.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers=4"]
