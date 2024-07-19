from django.shortcuts import render

from bus.models import Ticket, Journey


#
# def index(request):
#     routes = Journey.objects.values_list("route", "departure_time")
#     bought_seats_by_route = {}
#     total_seats = 20
#
#     for route in routes:
#         departure_time = route["departure_time"]
#         bought_seats = Ticket.objects.filter(journey__route=route).values_list(
#             "seat", flat=True
#         )
#         bought_seats_by_route[route] = {
#             "seats": list(bought_seats),
#             "departure_time": departure_time,
#         }
#
#     context = {
#         "bought_seats_by_route": bought_seats_by_route,
#         "total_seats": total_seats,
#         "seat_numbers": list(range(1, total_seats + 1)),
#     }
#
#     return render(request, "../templates/index.html", context)
def index(request):
    # Fetch routes with departure times
    routes_with_times = Journey.objects.values(
        "route", "departure_time"
    ).distinct()
    bought_seats_by_route = {}
    total_seats = 20

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
