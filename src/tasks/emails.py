import os
import smtplib
import ssl

from .celery_app import celery_app


@celery_app.task
def send_welcome_email(email: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.example.com")
    smtp_user = os.getenv("SMTP_USER", "noreply@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "password")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(smtp_user, smtp_password)

        subject = "Welcome to our Blog!"
        body = (
            "Hello!\n\n"
            "We are glad you joined our platform.\n"
            "Your account has been created successfully.\n\n"
            "Best regards,\n"
            "Our Blog Team"
        )

        message = f"""\
From: {smtp_user}
To: {email}
Subject: {subject}

{body}
"""
        server.sendmail(smtp_user, email, message)


@celery_app.task
def send_new_article_notification(email: str, article_title: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.example.com")
    smtp_user = os.getenv("SMTP_USER", "noreply@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "password")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(smtp_user, smtp_password)

        subject = "New Article Published!"
        body = (
            f"Hello!\n\n"
            f'A new article "{article_title}" was just published.\n'
            f"Check it out in our blog!\n\n"
            "Regards,\n"
            "Our Blog Team"
        )

        message = f"""\
From: {smtp_user}
To: {email}
Subject: {subject}

{body}
"""
        server.sendmail(smtp_user, email, message)
