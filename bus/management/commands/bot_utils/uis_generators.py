import random

from django.db.models import QuerySet
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from bus.models import Ticket


class UIGenerators:
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

    @staticmethod
    def generate_verification_code():
        return "".join(random.choices("0123456789", k=6))
