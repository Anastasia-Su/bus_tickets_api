from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class MainOptionsDisplay:
    def __init__(self, bot_instance):
        self.bot_instance = bot_instance

    def send_proceed_cancel(self, chat_id: int) -> None:
        """A user can choose to proceed with ticket order or to cancel it."""

        self.bot_instance.bot.send_message(chat_id, "Please check your order.")
        self.bot_instance.bot.send_message(
            chat_id,
            f"Name: {self.bot_instance.user_name}\n"
            f"Route: {self.bot_instance.selected_route}\n"
            f"Seat Number: {self.bot_instance.seat_number}\n",
        )
        markup_invite = InlineKeyboardMarkup()
        proceed = InlineKeyboardButton(
            "Proceed",
            callback_data="proceed",
        )
        cancel = InlineKeyboardButton(
            "Cancel",
            callback_data="cancel",
        )
        markup_invite.add(proceed, cancel)
        self.bot_instance.bot.send_message(
            chat_id,
            "Would you like to proceed?",
            reply_markup=markup_invite,
        )

    def send_options_message(self, chat_id: int) -> None:
        """Three main commands in the bot"""

        markup = InlineKeyboardMarkup(row_width=2)
        check_available = InlineKeyboardButton(
            "Check available tickets",
            callback_data="check_available_tickets",
        )
        check_my = InlineKeyboardButton(
            "Check my tickets",
            callback_data="check_my_tickets",
        )
        goodbye = InlineKeyboardButton(
            "Goodbye",
            callback_data="goodbye",
        )
        markup.add(check_available, check_my, goodbye)
        self.bot_instance.bot.send_message(
            chat_id, "What do you want to do?", reply_markup=markup
        )
