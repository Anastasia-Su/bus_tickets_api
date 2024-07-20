from django.db import models
from rest_framework.exceptions import ValidationError

from bus.constants import TOTAL_SEAT_COUNT


class Journey(models.Model):
    route = models.CharField()
    departure_time = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.route} ({self.departure_time.strftime('%d.%m.%y, %H:%M')})"
        )

    class Meta:
        ordering = ("departure_time",)


class Ticket(models.Model):
    name = models.CharField(max_length=255, default="")
    email = models.EmailField(default="")
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )

    def clean(self) -> None:
        if not (1 <= self.seat <= TOTAL_SEAT_COUNT):
            raise ValidationError(
                {
                    "seat": f"Seat must be in range 1–{TOTAL_SEAT_COUNT}.",
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.journey)} ({self.seat})"

    class Meta:
        unique_together = ("journey", "seat")
        ordering = ("journey", "seat")
