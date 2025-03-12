from typing import List, Optional, Dict
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr
from fastapi.templating import Jinja2Templates


from config import settings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = Path(BASE_DIR, "templates/email")

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates/email"),
    
)


mail = FastMail(config=conf)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def send_email(
    email: EmailStr,
    subject: str,
    template_name: str,
    template_data: Dict[str, str],
    recipients: Optional[List[EmailStr]] = None,
):
    if recipients is None:
        recipients = [email]

    template = templates.get_template(template_name)
    rendered_html = template.render(template_data)

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=rendered_html,
        subtype=MessageType.html,
    )

    await mail.send_message(message)
