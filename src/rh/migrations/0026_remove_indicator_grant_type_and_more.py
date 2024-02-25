# Generated by Django 4.0.6 on 2024-02-20 06:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0025_indidicatortypes_indicator"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="indicator",
            name="grant_type",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="implement_modility_type",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="package_type",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="transfer_category",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="transfer_mechanism_type",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="unit_type",
        ),
        migrations.RemoveField(
            model_name="indidicatortypes",
            name="activity_plan",
        ),
        migrations.AddField(
            model_name="indidicatortypes",
            name="currency",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="rh.currency"
            ),
        ),
    ]