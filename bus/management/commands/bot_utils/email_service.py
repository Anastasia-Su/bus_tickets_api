import io

from django.conf import settings
from django.core.mail import EmailMessage


class EmailService:
    @staticmethod
    def send_ticket_email(
        user_email: str, username: str, image_file: io.BytesIO
    ) -> None:
        """Sends an email to user inbox."""

        email = EmailMessage(
            subject="You have bought a ticket",
            body=f"Hello {username},\n\n\nPlease find your ticket attached.",
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email],
        )
        email.attach(image_file.name, image_file.getvalue(), "image/jpeg")
        email.send(fail_silently=False)
