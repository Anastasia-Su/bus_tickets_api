import smtplib

from django.core.mail import send_mail

from bus.management.commands.bot_utils.email_service import EmailService
from bus.management.commands.bot_utils.image_generator import ImageGenerator
from bus.management.commands.bot_utils.main_options_display import (
    MainOptionsDisplay,
)
from bus.management.commands.bot_utils.ticket_manager import TicketManager
from bus.management.commands.bot_utils.uis_generators import UIGenerators
from bus.management.commands.bot_utils.validators import Validators
from bus.models import Journey
from bus_tickets_api import settings


class TicketProcessor:
    def __init__(self, bot_instance):
        self.bot_instance = bot_instance

    def send_verification_code(self, chat_id: int, message) -> None:
        verification_code = UIGenerators.generate_verification_code()
        send_mail(
            "Verification Code",
            f"Your verification code is: {verification_code}",
            settings.EMAIL_HOST_USER,
            [message.text],
            fail_silently=False,
        )

        self.bot_instance.bot.send_message(
            chat_id,
            f"A verification code has been sent to "
            f"{message.text}. Please enter the code here.\n"
            f"Or enter another email, if previous one is incorrect.",
        )

        self.bot_instance.user_email = message.text
        self.bot_instance.verification_codes[message.text] = verification_code
        self.bot_instance.user_states[chat_id] = "verification"

    def process_ticket(self, chat_id: int) -> None:
        journey = Journey.objects.get(route=self.bot_instance.selected_route)

        TicketManager.create_ticket(
            self.bot_instance.user_email,
            self.bot_instance.user_name,
            journey,
            self.bot_instance.seat_number,
        )
        image_file = ImageGenerator.create_ticket_image(
            self.bot_instance.user_name,
            journey.route,
            journey.departure_time,
            self.bot_instance.seat_number,
        )
        image_file.name = f"{self.bot_instance.user_name}_ticket.jpg"

        EmailService.send_ticket_email(
            self.bot_instance.user_email,
            self.bot_instance.user_name,
            image_file,
        )
        email_status_message = (
            f"Ticket for seat {self.bot_instance.seat_number} created and "
            "sent to your email."
        )
        self.bot_instance.bot.send_message(
            chat_id,
            email_status_message,
        )
        del self.bot_instance.user_states[chat_id]
        main_options_sender = MainOptionsDisplay(self.bot_instance)
        main_options_sender.send_options_message(chat_id)
