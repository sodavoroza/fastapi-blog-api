```markdown

# FastAPI Blog API

Проект представляет собой REST API для блога маркетплейса, реализованный на FastAPI. Сервис обеспечивает функционал аутентификации, управления статьями и категориями, фейкового удаления, а также асинхронную обработку задач (email-уведомления) через Celery и интеграцию с S3-хранилищем (Minio).

## Стек технологий

- Python 3.12
- FastAPI
- PostgreSQL
- Async SQLAlchemy
- Celery + RabbitMQ
- Minio (S3-compatible storage)
- Docker / Docker Compose
- Poetry
- Pytest
- Ruff, Black, MyPy

## 🚀 Быстрый старт

### Локальный запуск

1. Установите зависимости:
   ```bash
   poetry install
   ```
2. Примените миграции:
   ```bash
   poetry run alembic upgrade head
   ```
3. Запустите сервер разработки:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```
   API будет доступен по адресу [http://localhost:8000](http://localhost:8000).

### Запуск с Docker Compose

1. Создайте файл `.env` (см. раздел ниже).
2. Запустите контейнеры:
   ```bash
   docker-compose up --build
   ```
   Сервис будет доступен по адресу [http://localhost:8000](http://localhost:8000).

## 🔧 Полезные команды

| Команда           | Описание                                             |
|-------------------|------------------------------------------------------|
| `make up`         | Запуск Docker Compose (сборка и запуск контейнеров)  |
| `make down`       | Остановка всех контейнеров                           |
| `make migrate`    | Выполнение миграций (Alembic)                        |
| `make test`       | Запуск тестов (pytest + coverage)                    |
| `make lint`       | Запуск линтеров (pre-commit)                         |
| `make mypy`       | Проверка типов (MyPy)                                |
| `make shell`      | Открыть shell в контейнере веб-приложения            |
| `make logs`       | Просмотр логов веб-контейнера                        |

## 🧪 Тестирование и линтинг

Запуск тестов:
```bash
make test
```

Линтинг и форматирование:
```bash
make lint
make format
```

## 🚦 CI/CD

При каждом пуше и pull request запускаются:
- Линтинг и форматирование (Ruff, Black)
- Статическая типизация (MyPy)
- Тесты (Pytest)

Состояние CI: [![CI](https://github.com/sodavoroza/fastapi-blog-api/actions/workflows/ci.yml/badge.svg)](https://github.com/sodavoroza/fastapi-blog-api/actions)

## 📚 Документация API

Документация доступна в режиме разработки:
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🛠️ Настройки окружения (.env)

```env
# PostgreSQL
POSTGRES_DB=blog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/blog

# JWT
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery & RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//

# Minio (S3)
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minio_access
MINIO_SECRET_KEY=minio_secret

# Miscellaneous
DEBUG=True
```
