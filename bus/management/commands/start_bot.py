import random
from io import BytesIO

import telebot

from datetime import date
from PIL import Image, ImageDraw, ImageFont

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.management.base import BaseCommand
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bus.models import Ticket, Journey


class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM["bot_token"])
        self.user_email = None
        self.selected_route = None
        self.bought_seats = None

        @self.bot.message_handler(commands=["start", "help"])
        def send_welcome(message):
            self.bot.reply_to(message, "Please enter your email.")

        @self.bot.callback_query_handler(
            func=lambda call: call.data
            in ["check_available_tickets", "check_my_tickets"]
        )
        def handle_main_options(call):
            chat_id = call.message.chat.id

            if self.user_email:
                if call.data == "check_available_tickets":
                    # Retrieve available routes and send them as inline buttons
                    routes = Journey.objects.values_list("route", flat=True)

                    route_markup = self.generate_routes(routes)

                    self.bot.send_message(
                        chat_id,
                        "Please select a route.",
                        reply_markup=route_markup,
                    )
                if call.data == "check_my_tickets":
                    # Display the user's tickets
                    my_tickets = Ticket.objects.filter(email=self.user_email)

                    my_tickets_markup = self.generate_my_tickets(my_tickets)
                    if my_tickets.exists():
                        self.bot.send_message(
                            chat_id,
                            "Here is your tickets:",
                            reply_markup=my_tickets_markup,
                        )

            else:
                self.bot.send_message(chat_id, "Please enter your email.")

        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("route_")
        )
        def handle_route_selection(call):
            chat_id = call.message.chat.id

            if self.user_email:
                selected_route = call.data.split("route_")[1]
                self.selected_route = selected_route

                bought_seats = Ticket.objects.filter(
                    journey__route=selected_route
                ).values_list("seat", flat=True)
                self.bought_seats = bought_seats

                seats_markup = self.generate_seat_grid(bought_seats)

                self.bot.send_message(
                    chat_id,
                    f"Click a seat if you want to buy it for the route {selected_route}.",
                    reply_markup=seats_markup,
                )

            else:
                self.bot.send_message(chat_id, "Please enter your email.")

        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("seat_")
        )
        def handle_seat_selection(call):
            chat_id = call.message.chat.id
            seat_number = int(call.data.split("_")[1])

            if self.selected_route:
                journey = Journey.objects.get(route=self.selected_route)
                username = Ticket.objects.filter(email=self.user_email)[0].name

                if self.bought_seats and seat_number not in self.bought_seats:
                    # Update database
                    Ticket.objects.create(
                        name=username,
                        email=self.user_email,
                        journey=journey,
                        seat=seat_number,
                    )

                    # Create image
                    image_file = self.create_ticket_image(
                        username,
                        journey.route,
                        journey.departure_time,
                        seat_number,
                    )
                    image_file.name = f"{username}_ticket.jpg"

                    # Send the email with the image attachment
                    email = EmailMessage(
                        subject="You have bought a ticket",
                        body=f"Hello {username},\n\nPlease find your ticket attached.",
                        from_email=settings.EMAIL_HOST_USER,
                        to=[
                            self.user_email,
                        ],
                    )
                    email.attach(
                        image_file.name, image_file.getvalue(), "image/jpeg"
                    )
                    email.send(fail_silently=False)

                self.bot.answer_callback_query(
                    call.id,
                    f"Seat {seat_number} selected",
                )
                self.bot.send_message(
                    chat_id,
                    f"Ticket for seat {seat_number} created and sent to your email.",
                )

            else:
                self.bot.send_message(chat_id, "Please select a route.")

        @self.bot.message_handler(func=lambda message: True)
        def handle_email(message):
            chat_id = message.chat.id

            if self.email_exists_in_database(message.text):
                self.bot.send_message(
                    chat_id,
                    f"Hello, {Ticket.objects.filter(email=message.text)[0].name}!",
                )

                self.user_email = message.text

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
                self.bot.reply_to(
                    message, "Your email does not exist in our database"
                )

    @staticmethod
    def email_exists_in_database(email):
        return Ticket.objects.filter(email=email).exists()

    @staticmethod
    def generate_routes(routes):
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = []

        for route in routes:
            buttons.append(
                InlineKeyboardButton(
                    text=route,
                    callback_data=f"route_{route}",
                )
            )

        markup.add(*buttons)
        return markup

    @staticmethod
    def generate_my_tickets(tickets):
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = []

        for ticket in tickets:
            buttons.append(
                InlineKeyboardButton(
                    text=f"Route: {ticket.journey.route}, "
                    f"seat: {ticket.seat}",
                    callback_data=f"ticket_{ticket}",
                )
            )

        markup.add(*buttons)
        return markup

    @staticmethod
    def generate_seat_grid(bought_seats):
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []

        for seat_number in range(1, 21):
            if seat_number in bought_seats:
                buttons.append(
                    InlineKeyboardButton(
                        text=f"❌ {seat_number}",
                        callback_data=f"bought_{seat_number}",
                    )
                )
            else:
                buttons.append(
                    InlineKeyboardButton(
                        text=f"✅ {seat_number}",
                        callback_data=f"seat_{seat_number}",
                    )
                )

        markup.add(*buttons)
        return markup

    @staticmethod
    def create_ticket_image(username, route, departure_time, seat_number):
        img = Image.new("RGB", (400, 200), color=(255, 255, 255))
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(img)

        draw.text((10, 10), f"Name: {username}", fill=(0, 0, 0), font=font)
        draw.text((10, 40), f"Route: {route}", fill=(0, 0, 0), font=font)
        draw.text(
            (10, 70),
            f"Departure Time: {departure_time}",
            fill=(0, 0, 0),
            font=font,
        )
        draw.text(
            (10, 100), f"Seat Number: {seat_number}", fill=(0, 0, 0), font=font
        )

        # Save the image to a BytesIO object
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)

        return img_byte_arr

    def start_polling(self):
        self.bot.infinity_polling(interval=0, timeout=20)


telegram_bot = TelegramBot()


class Command(BaseCommand):
    def handle(self, *args, **options):
        telegram_bot.start_polling()
