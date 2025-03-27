import os

from celery import Celery

celery_app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://"),
)


celery_app.conf.task_routes = {
    "src.tasks.emails.send_welcome_email": {"queue": "emails"},
}
