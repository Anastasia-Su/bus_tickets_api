from django.db.models import QuerySet
from bus.models import Ticket, Journey


class TicketManager:
    @staticmethod
    def create_ticket(
        email: str, username: str, journey: Journey, seat_number: int
    ) -> None:
        """Creates new ticket in db."""

        Ticket.objects.create(
            name=username,
            email=email,
            journey=journey,
            seat=seat_number,
        )

    @staticmethod
    def get_bought_seats(route: str) -> QuerySet[Ticket]:
        """Gets seats bought from route."""

        return Ticket.objects.filter(journey__route=route).values_list(
            "seat", flat=True
        )

    @staticmethod
    def get_user_tickets(email: str) -> QuerySet[Ticket]:
        """Gets seats bought from user."""

        return Ticket.objects.filter(email=email)

    @staticmethod
    def get_username(email: str) -> str:
        """Gets username from db."""

        filtered = Ticket.objects.filter(email=email)
        if len(filtered):
            return filtered[0].name

    @staticmethod
    def email_exists(email: str) -> bool:
        """Checks if email exists in db."""

        return Ticket.objects.filter(email=email).exists()
