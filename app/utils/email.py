import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.config import settings

EMAIL = settings.SENDER_EMAIL
PASSWORD = settings.SENDER_EMAIL_PASSWORD
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()