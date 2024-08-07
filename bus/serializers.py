from rest_framework import serializers

from bus.models import Journey, Ticket


class JourneySerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(format="%d.%m.%y, %H:%M")

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
    journey = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_journey(obj: Ticket) -> str:
        return (
            f"{obj.journey.route} "
            f"({obj.journey.departure_time.strftime('%d.%m.%y, %H:%M')})"
        )

    class Meta:
        model = Ticket
        fields = ("id", "name", "email", "seat", "journey")


class TicketDetailSerializer(TicketListSerializer):
    pass


class JourneyDetailSerializer(JourneySerializer):
    taken_places = serializers.SerializerMethodField()

    @staticmethod
    def get_taken_places(obj: Journey) -> str:
        seats = obj.tickets.values_list("seat", flat=True)
        return ", ".join(map(str, seats))

    class Meta:
        model = Journey
        fields = ("id", "departure_time", "route", "taken_places")
