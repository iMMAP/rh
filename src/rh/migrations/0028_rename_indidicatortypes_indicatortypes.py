# Generated by Django 4.0.6 on 2024-02-20 09:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0027_projectindicatortype"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="IndidicatorTypes",
            new_name="IndicatorTypes",
        ),
    ]