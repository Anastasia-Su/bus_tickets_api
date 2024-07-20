import telebot
from django.conf import settings
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
from bus.management.commands.bot_utils.ticket_manager import TicketManager
from bus.models import Journey, Ticket


class TelegramBot:
    def __init__(self) -> None:
        self.bot = telebot.TeleBot(settings.TELEGRAM["bot_token"])
        self.user_email = None
        self.selected_route = None
        self.bought_seats = None

        self.setup_handlers()

    def setup_handlers(self) -> None:
        @self.bot.message_handler(commands=["start", "help"])
        def send_welcome(message: Message) -> None:
            """Handles the /start and /help commands
            by prompting the user to enter their email."""

            self.bot.send_message(message.chat.id, "Please enter your email.")

        @self.bot.message_handler(func=lambda message: True)
        def handle_email(message: Message) -> None:
            """Handles incoming messages by checking
            if the message text is an email.
            If the email exists in the system,
            it greets the user and shows options.
            """

            chat_id = message.chat.id
            if TicketManager.email_exists(message.text):
                self.user_email = message.text
                username = TicketManager.get_user_tickets(self.user_email)[
                    0
                ].name
                self.bot.send_message(
                    chat_id,
                    f"Hello, {username}!",
                )
                markup = telebot.types.InlineKeyboardMarkup()
                check_available = telebot.types.InlineKeyboardButton(
                    "Check available tickets",
                    callback_data="check_available_tickets",
                )
                check_my = telebot.types.InlineKeyboardButton(
                    "Check my tickets",
                    callback_data="check_my_tickets",
                )
                markup.add(check_available, check_my)
                self.bot.send_message(
                    chat_id, "What do you want to do?", reply_markup=markup
                )
            else:
                self.bot.send_message(
                    chat_id, "Your email does not exist in our database"
                )

        @self.bot.callback_query_handler(
            func=lambda call: call.data
            in ["check_available_tickets", "check_my_tickets"]
        )
        def handle_main_options(call: CallbackQuery) -> None:
            """Handles main options for checking
            available tickets or user tickets."""

            chat_id = call.message.chat.id
            if self.user_email:
                if call.data == "check_available_tickets":
                    routes = Journey.objects.values_list("route", flat=True)
                    route_markup = self.generate_routes(routes)
                    self.bot.send_message(
                        chat_id,
                        "Please select a route.",
                        reply_markup=route_markup,
                    )
                elif call.data == "check_my_tickets":
                    my_tickets = TicketManager.get_user_tickets(
                        self.user_email
                    )
                    my_tickets_markup = self.generate_my_tickets(my_tickets)
                    if my_tickets.exists():
                        self.bot.send_message(
                            chat_id,
                            "Here is your tickets:",
                            reply_markup=my_tickets_markup,
                        )
                    else:
                        self.bot.send_message(
                            chat_id, "You have no tickets yet."
                        )
            else:
                self.bot.send_message(chat_id, "Please enter your email.")

        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("route_")
        )
        def handle_route_selection(call: CallbackQuery) -> None:
            """Handles route selection by displaying available seats
            for the selected route."""

            chat_id = call.message.chat.id
            if self.user_email:
                selected_route = call.data.split("route_")[1]
                self.selected_route = selected_route
                self.bought_seats = TicketManager.get_bought_seats(
                    selected_route
                )
                seats_markup = self.generate_seat_grid(self.bought_seats)
                self.bot.send_message(
                    chat_id,
                    f"Click a seat if you want to buy it "
                    f"for the route {selected_route}.",
                    reply_markup=seats_markup,
                )
            else:
                self.bot.send_message(chat_id, "Please enter your email.")

        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("seat_")
        )
        def handle_seat_selection(call: CallbackQuery) -> None:
            """Handles seat selection and processes
            ticket creation and email sending."""

            chat_id = call.message.chat.id
            seat_number = int(call.data.split("_")[1])
            if self.selected_route:
                journey = Journey.objects.get(route=self.selected_route)
                username = TicketManager.get_user_tickets(self.user_email)[
                    0
                ].name
                if seat_number not in self.bought_seats:
                    TicketManager.create_ticket(
                        self.user_email, username, journey, seat_number
                    )
                    image_file = ImageGenerator.create_ticket_image(
                        username,
                        journey.route,
                        journey.departure_time,
                        seat_number,
                    )
                    image_file.name = f"{username}_ticket.jpg"
                    EmailService.send_ticket_email(
                        self.user_email, username, image_file
                    )
                    self.bot.answer_callback_query(
                        call.id,
                        f"Seat {seat_number} selected",
                    )
                    self.bot.send_message(
                        chat_id,
                        f"Ticket for seat {seat_number} created "
                        f"and sent to your email.",
                    )
            else:
                self.bot.send_message(chat_id, "Please select a route.")

    @staticmethod
    def generate_routes(routes: list[str]) -> InlineKeyboardMarkup:
        """Generates an inline keyboard markup for route selection."""

        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(text=route, callback_data=f"route_{route}")
            for route in routes
        ]
        markup.add(*buttons)
        return markup

    @staticmethod
    def generate_my_tickets(tickets: QuerySet[Ticket]) -> InlineKeyboardMarkup:
        """Generates an inline keyboard markup
        for displaying user's tickets."""

        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton(
                text=f"Route: {ticket.journey.route}, seat: {ticket.seat}",
                callback_data=f"ticket_{ticket.id}",
            )
            for ticket in tickets
        ]
        markup.add(*buttons)
        return markup

    @staticmethod
    def generate_seat_grid(
        bought_seats: QuerySet[Ticket],
    ) -> InlineKeyboardMarkup:
        """Generates an inline keyboard markup for seat selection."""

        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton(
                text=(
                    f"❌ {seat_number}"
                    if seat_number in bought_seats
                    else f"✅ {seat_number}"
                ),
                callback_data=(
                    f"bought_{seat_number}"
                    if seat_number in bought_seats
                    else f"seat_{seat_number}"
                ),
            )
            for seat_number in range(1, 21)
        ]
        markup.add(*buttons)
        return markup

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
