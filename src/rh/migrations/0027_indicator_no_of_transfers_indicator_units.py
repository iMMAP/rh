# Generated by Django 5.0.7 on 2024-08-21 11:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0026_activityplan_no_of_transfers_activityplan_units_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="indicator",
            name="no_of_transfers",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(30),
                ],
            ),
        ),
        migrations.AddField(
            model_name="indicator",
            name="units",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]