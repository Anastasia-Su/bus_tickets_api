from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bus.constants import TOTAL_SEAT_COUNT
from bus.models import Ticket, Journey


def index(request: HttpRequest) -> HttpResponse:
    """Renders the index page with a list of routes,
    along with the list of bought seats for each route."""

    routes_with_times = Journey.objects.values(
        "route", "departure_time"
    ).distinct()
    bought_seats_by_route = {}
    total_seats = TOTAL_SEAT_COUNT

    for route_info in routes_with_times:
        route = route_info["route"]
        departure_time = route_info["departure_time"]
        bought_seats = Ticket.objects.filter(journey__route=route).values_list(
            "seat", flat=True
        )
        bought_seats_by_route[route] = {
            "seats": list(bought_seats),
            "departure_time": departure_time,
        }

    context = {
        "bought_seats_by_route": bought_seats_by_route,
        "total_seats": total_seats,
        "seat_numbers": list(range(1, total_seats + 1)),
    }

    return render(request, "../templates/index.html", context)
