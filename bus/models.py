from django.db import models
from rest_framework.exceptions import ValidationError


class Journey(models.Model):
    route = models.CharField()
    departure_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} ({self.departure_time})"

    class Meta:
        ordering = ("departure_time",)


class Ticket(models.Model):
    name = models.CharField(max_length=255, default="")
    email = models.EmailField(default="")
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )

    def clean(self):
        if not (1 <= self.seat <= 20):
            raise ValidationError(
                {
                    "seat": "Seat must be in range 1–50.",
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.journey)} ({self.seat})"

    class Meta:
        unique_together = ("journey", "seat")
        ordering = ("journey", "seat")
