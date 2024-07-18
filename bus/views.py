from datetime import datetime

from django.db.models import Count, F
from rest_framework import viewsets
from rest_framework.response import Response

from bus.models import Journey, Ticket
from bus.serializers import (
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    TicketSerializer,
)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.annotate(
        tickets_available=(50 - Count("tickets"))
    )

    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    # def list(self, request, *args, **kwargs):
    #     tickets = self.get_queryset()
    #     formatted_data = self.format_tickets(tickets)
    #     return Response(formatted_data)
    #
    # def format_tickets(self, tickets):
    #     formatted_data = {}
    #     for ticket in tickets:
    #         seat = ticket.seat
    #
    #         journey = str(ticket.journey)
    #         formatted_data.setdefault(journey, {}).setdefault([]).append(
    #             f"seat: {seat}"
    #         )
    #
    #     return formatted_data
