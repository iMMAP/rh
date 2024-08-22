# Generated by Django 5.0.7 on 2024-08-21 11:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("project_reports", "0014_alter_disaggregationlocationreport_target"),
    ]

    operations = [
        migrations.AddField(
            model_name="activityplanreport",
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
            model_name="activityplanreport",
            name="units",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name="disaggregationlocationreport",
            name="target_required",
            field=models.IntegerField(
                blank=True, default=0, null=True, verbose_name="Target Required"
            ),
        ),
    ]
