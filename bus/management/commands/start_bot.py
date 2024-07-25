import random
import telebot
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)

from bus.management.commands.bot_utils.email_service import EmailService
from bus.management.commands.bot_utils.image_generator import ImageGenerator
from bus.management.commands.bot_utils.main_options_display import (
    MainOptionsDisplay,
)
from bus.management.commands.bot_utils.ticket_processor import TicketProcessor
from bus.management.commands.bot_utils.ticket_manager import TicketManager
from bus.management.commands.bot_utils.uis_generators import UIGenerators
from bus.management.commands.bot_utils.user_tickets_checker import (
    UserTicketsChecker,
)
from bus.management.commands.bot_utils.validators import Validators
from bus.models import Journey, Ticket


class TelegramBot:
    def __init__(self) -> None:
        self.bot = telebot.TeleBot(settings.TELEGRAM["bot_token"])
        self.user_email = None
        self.user_name = None
        self.selected_route = None
        self.bought_seats = None
        self.seat_number = None
        self.user_states = {}
        self.verification_codes = {}

        self.setup_handlers()

    def setup_handlers(self) -> None:
        @self.bot.message_handler(commands=["start", "help"])
        def send_welcome(message: Message) -> None:
            """Handles the /start and /help commands."""

            self.bot.send_message(
                message.chat.id,
                "Welcome! I can help you buy bus tickets quickly and without registration.\n"
                "You need to enter your name and email, select route and a ticket you want to buy.\n"
                "Then you will receive an email with the ticket attached.\n"
                "You can also see all the tickets you have already purchased.\n",
            )

            main_options_sender = MainOptionsDisplay(self)
            main_options_sender.send_options_message(message.chat.id)

        @self.bot.callback_query_handler(
            func=lambda call: call.data == "goodbye"
        )
        def handle_goodbye(call: CallbackQuery) -> None:
            """Handles goodbye command."""

            self.user_email = None
            self.user_name = None
            self.selected_route = None
            self.bought_seats = None
            self.seat_number = None
            self.user_states = {}
            self.verification_codes = {}
            self.bot.send_message(call.message.chat.id, "Goodbye!")

            self.bot.send_message(
                call.message.chat.id, "To start over, type /start"
            )

        @self.bot.callback_query_handler(
            func=lambda call: call.data == "check_available_tickets"
        )
        def handle_check_available(call: CallbackQuery) -> None:
            """Handles main options for checking
            available tickets."""

            chat_id = call.message.chat.id

            routes = Journey.objects.values_list("route", flat=True)
            route_markup = UIGenerators.generate_routes(routes)
            self.bot.send_message(
                chat_id,
                "Please select a route.",
                reply_markup=route_markup,
            )

        @self.bot.callback_query_handler(
            func=lambda call: call.data == "check_my_tickets"
        )
        def handle_check_my(call: CallbackQuery) -> None:
            """Handles main options for checking
            user tickets."""

            user_tickets_checker = UserTicketsChecker(self)
            user_tickets_checker.check_my_tickets(call.message.chat.id)

        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("route_")
        )
        def handle_route_selection(call: CallbackQuery) -> None:
            """Handles route selection by displaying available seats
            for the selected route."""

            chat_id = call.message.chat.id

            selected_route = call.data.split("route_")[1]
            self.selected_route = selected_route
            self.bought_seats = TicketManager.get_bought_seats(selected_route)
            seats_markup = UIGenerators.generate_seat_grid(self.bought_seats)
            self.bot.send_message(
                chat_id,
                f"Click a seat if you want to buy it "
                f"for the route {selected_route}.",
                reply_markup=seats_markup,
            )

        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("seat_")
        )
        def handle_seat_selection(call: CallbackQuery) -> None:
            """Handles seat selection and processes
            ticket creation and email sending."""

            chat_id = call.message.chat.id
            seat_number = int(call.data.split("_")[1])
            self.seat_number = seat_number

            if seat_number not in self.bought_seats:
                if not self.user_email:
                    self.bot.send_message(chat_id, "Please enter your email.")
                    self.user_states[chat_id] = "email"

                elif self.user_email and not self.user_name:
                    self.bot.send_message(
                        chat_id,
                        "Please enter your first and last name.",
                    )
                    self.user_states[chat_id] = "name"

        @self.bot.message_handler(
            func=lambda message: self.user_states.get(message.chat.id)
            == "email"
        )
        def handle_email_message(message: Message) -> None:
            chat_id = message.chat.id

            if Validators.is_valid_email(message.text):
                send_processor = TicketProcessor(self)
                send_processor.send_verification_code(chat_id, message)

            else:
                email_status_message = (
                    f"{message.text} is invalid address.\n"
                    f"Please try again."
                )
                self.bot.send_message(
                    chat_id,
                    email_status_message,
                )

        @self.bot.message_handler(
            func=lambda message: self.user_states.get(message.chat.id)
            == "verification"
        )
        def handle_verification_message(message: Message) -> None:
            chat_id = message.chat.id
            if message.text == self.verification_codes.get(self.user_email):
                self.bot.send_message(chat_id, "Verification successful!")

                if self.seat_number:
                    self.bot.send_message(
                        chat_id,
                        "Please enter your first and last name.",
                    )
                    self.user_states[chat_id] = "name"
                else:
                    user_tickets_checker = UserTicketsChecker(self)
                    user_tickets_checker.check_my_tickets(message.chat.id)

                    main_options_sender = MainOptionsDisplay(self)
                    main_options_sender.send_options_message(chat_id)

            else:
                if Validators.is_valid_email(message.text):
                    send_processor = TicketProcessor(self)
                    send_processor.send_verification_code(chat_id, message)
                else:
                    self.bot.send_message(
                        chat_id,
                        "Verification code is incorrect. Please try again.\n"
                        "Or enter another email address.",
                    )

        @self.bot.message_handler(
            func=lambda message: self.user_states.get(message.chat.id)
            == "name"
        )
        def handle_username_message(message: Message) -> None:
            chat_id = message.chat.id
            self.user_name = message.text
            self.bot.send_message(
                chat_id,
                f"Nice to meet you, {self.user_name}.",
            )

            proceed_cancel_options = MainOptionsDisplay(self)
            proceed_cancel_options.send_proceed_cancel(chat_id)

        @self.bot.callback_query_handler(
            func=lambda call: call.data == "proceed"
        )
        def handle_proceed(call: CallbackQuery) -> None:
            """Handles command to proceed ticket creation."""

            chat_id = call.message.chat.id
            ticket_processor = TicketProcessor(self)
            ticket_processor.process_ticket(chat_id)

        @self.bot.callback_query_handler(
            func=lambda call: call.data == "cancel"
        )
        def handle_cancel(call: CallbackQuery) -> None:
            """Handles command to cancel ticket creation."""

            main_options_sender = MainOptionsDisplay(self)
            main_options_sender.send_options_message(call.message.chat.id)

    def start_polling(self) -> None:
        """Starts the bot's polling mechanism
        to receive messages and callback queries."""

        self.bot.infinity_polling(interval=0, timeout=20)


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        """Entry point for the Django management command
        to start the Telegram bot."""

        telegram_bot = TelegramBot()
        telegram_bot.start_polling()
