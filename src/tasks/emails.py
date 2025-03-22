from .celery_app import celery_app


@celery_app.task
def send_welcome_email(user_email: str):
    print(f"Sending welcome email to {user_email}")
