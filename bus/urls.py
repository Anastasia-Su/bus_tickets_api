from django.urls import path, include
from rest_framework import routers

from .views import (
    JourneyViewSet,
    TicketViewSet,
)

router = routers.DefaultRouter()

router.register("journeys", JourneyViewSet, basename="journey")
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [path("", include(router.urls))]

app_name = "bus"
