from celery import Celery
from pydantic import EmailStr
from asgiref.sync import async_to_sync
from utils.mail import send_email
from config import settings


celery = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


@celery.task
def send_verfification_email(email: EmailStr, token: str):
    verification_url = f"{settings.DOMAIN}auth/verify/{token}"
    subject = "Verify Your Email"

    async_to_sync(send_email)(
        email,
        subject,
        template_name="verification.html",
        template_data={"verification_url": verification_url},
    )


@celery.task
def send_password_reset_email(email: EmailStr, token: str):
    verification_url = f"{settings.DOMAIN}auth/password_reset_confirm/{token}"
    subject = "Reset Your Password "

    async_to_sync(send_email)(
        email,
        subject,
        template_name="reset_password.html",
        template_data={"verification_url": verification_url},
    )
