# Generated by Django 4.0.6 on 2024-02-12 09:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0027_remove_activityplan_facility_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cluster",
            name="has_nhs_code",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
