# Generated by Django 5.0.7 on 2024-07-18 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Journey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("route", models.CharField()),
                ("departure_time", models.DateTimeField()),
            ],
            options={
                "ordering": ("-departure_time",),
            },
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("seat", models.IntegerField()),
                (
                    "journey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="bus.journey",
                    ),
                ),
            ],
            options={
                "ordering": ("journey", "seat"),
                "unique_together": {("journey", "seat")},
            },
        ),
    ]
