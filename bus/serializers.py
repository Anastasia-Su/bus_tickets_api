from rest_framework import serializers

from bus.models import Journey, Ticket


class JourneySerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Journey
        fields = ("id", "departure_time", "route")


class JourneyListSerializer(JourneySerializer):
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "departure_time", "route", "tickets_available")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "name", "email", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    pass


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("seat",)


class JourneyDetailSerializer(JourneySerializer):
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Journey
        fields = ("id", "departure_time", "route", "taken_places")
