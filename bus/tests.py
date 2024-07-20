from datetime import datetime

from django.db.models import Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from bus.constants import TOTAL_SEAT_COUNT
from bus.models import Ticket, Journey
from bus.serializers import JourneyListSerializer, TicketListSerializer

TICKET_URL = reverse("bus:ticket-list")
JOURNEY_URL = reverse("bus:journey-list")


def sample_journey(**params):
    defaults = {
        "route": "test_route",
        "departure_time": "2024-07-25 14:00:00",
    }
    defaults.update(params)

    return Journey.objects.create(**defaults)


def sample_ticket(**params):
    defaults = {
        "name": "User1",
        "email": "test@test.com",
        "seat": 1,
        "journey": sample_journey(),
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)


class BusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        """Tests that login is not required to display tickets."""

        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_routes(self):
        """Tests that the list routes work."""

        sample_journey(
            route="test_route1", departure_time="2024-07-21 14:00:00"
        )
        sample_journey(
            route="test_route2", departure_time="2024-07-25 15:00:00"
        )

        res = self.client.get(JOURNEY_URL)
        journeys = Journey.objects.annotate(
            tickets_available=(TOTAL_SEAT_COUNT - Count("tickets"))
        )
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_tickets_by_route(self):
        """Tests that filtering by route work."""

        journey1 = sample_journey(
            route="test1", departure_time=datetime(2024, 7, 20, 14, 0)
        )
        journey2 = sample_journey(
            route="test2", departure_time=datetime(2024, 7, 20, 14, 0)
        )
        journey3 = sample_journey(
            route="journey1", departure_time=datetime(2024, 7, 20, 14, 0)
        )

        ticket1 = sample_ticket(seat=1, journey=journey1)
        ticket2 = sample_ticket(seat=2, journey=journey2)
        ticket3 = sample_ticket(seat=3, journey=journey3)

        res = self.client.get(TICKET_URL, {"route": "test"})

        serializer1 = TicketListSerializer(ticket1)
        serializer2 = TicketListSerializer(ticket2)
        serializer3 = TicketListSerializer(ticket3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_tickets_by_date(self):
        """Tests that filtering by date work."""
        journey1 = sample_journey(departure_time=datetime(2024, 7, 20, 14, 0))
        journey2 = sample_journey(departure_time=datetime(2024, 7, 19, 14, 0))

        ticket1 = sample_ticket(seat=1, journey=journey1)
        ticket2 = sample_ticket(seat=2, journey=journey2)

        res = self.client.get(TICKET_URL, {"date": "20.07.24"})

        serializer1 = TicketListSerializer(ticket1)
        serializer2 = TicketListSerializer(ticket2)

        for item in res.data:
            self.assertIn(serializer1.data["journey"], item["journey"])
            self.assertNotIn(serializer2.data["journey"], item["journey"])
