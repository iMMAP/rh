# Generated by Django 4.0.6 on 2024-02-19 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0028_cluster_has_nhs_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="targetlocation",
            name="nhs_code",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
