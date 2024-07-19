from django.db.models import Count
from rest_framework import viewsets

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
