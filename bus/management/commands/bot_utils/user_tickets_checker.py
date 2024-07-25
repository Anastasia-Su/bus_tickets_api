from bus.management.commands.bot_utils.ticket_manager import TicketManager
from bus.management.commands.bot_utils.uis_generators import UIGenerators


class UserTicketsChecker:
    def __init__(self, bot_instance) -> None:
        self.bot_instance = bot_instance

    def check_my_tickets(self, chat_id: int) -> None:
        """Display user tickets, if any."""

        if self.bot_instance.user_email:
            if TicketManager.email_exists(self.bot_instance.user_email):
                my_tickets = TicketManager.get_user_tickets(
                    self.bot_instance.user_email
                )
                my_tickets_markup = UIGenerators.generate_my_tickets(
                    my_tickets
                )

                self.bot_instance.bot.send_message(
                    chat_id,
                    "Here are your tickets:",
                    reply_markup=my_tickets_markup,
                )
            else:
                self.bot_instance.bot.send_message(
                    chat_id, "You have no tickets yet."
                )

        else:
            self.bot_instance.bot.send_message(
                chat_id, "Please enter your email."
            )
            self.bot_instance.user_states[chat_id] = "email"
