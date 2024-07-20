from datetime import datetime

from django.db.models import Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from bus.constants import TOTAL_SEAT_COUNT
from bus.models import Journey, Ticket
from bus.serializers import (
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.annotate(
        tickets_available=(TOTAL_SEAT_COUNT - Count("tickets"))
    )

    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("journey")
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        if self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer

    def get_queryset(self):
        route = self.request.query_params.get("route")
        date = self.request.query_params.get("date")

        queryset = self.queryset

        if route:
            queryset = queryset.filter(journey__route__icontains=route)

        if date:
            date = datetime.strptime(date, "%d.%m.%y").date()
            queryset = queryset.filter(journey__departure_time__icontains=date)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description="Filter by route part (ex. ?route=Kyiv)",
            ),
            OpenApiParameter(
                "date",
                type=OpenApiTypes.STR,
                description="Filter by date (ex. ?date=20.07.24)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
