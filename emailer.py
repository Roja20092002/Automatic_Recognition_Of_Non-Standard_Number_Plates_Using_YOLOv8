import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


class EmailNotifier:

    def __init__(self):

        self.sender_email = os.getenv(
            "EMAIL_USER"
        )

        self.app_password = os.getenv(
            "EMAIL_PASSWORD"
        )

        self.receiver_email = os.getenv(
            "EMAIL_RECEIVER"
        )

    def send_invalid_plate_alert(
        self,
        plate,
        full_text,
        reason
    ):

        print("Sender:", self.sender_email)
        print("Receiver:", self.receiver_email)
        print("Connecting to Gmail...")

        msg = EmailMessage()

        msg["Subject"] = "ANPR Invalid Plate Alert"
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        msg.set_content(
            f"""
INVALID VEHICLE PLATE DETECTED

Detected Registration Number:
{plate}

OCR Extracted Text:
{full_text}

Reason:
{reason}

Please verify this vehicle.
"""
        )

        try:

            with smtplib.SMTP(
                "smtp.gmail.com",
                587,
                timeout=30
            ) as smtp:

                smtp.starttls()

                smtp.login(
                    self.sender_email,
                    self.app_password
                )

                smtp.send_message(msg)

            print("Email sent successfully.")

        except Exception as e:

            print("Email sending failed:")
            print(e)