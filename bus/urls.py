from django.urls import path, include
from rest_framework import routers

from .views import (
    JourneyViewSet,
    TicketViewSet,
)

router = routers.DefaultRouter()

router.register("journeys", JourneyViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "bus"
