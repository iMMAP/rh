# Generated by Django 4.0.6 on 2024-03-20 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0006_disaggregation_lower_limat_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='disaggregation',
            old_name='lower_limat',
            new_name='lower_limit',
        ),
        migrations.RenameField(
            model_name='disaggregation',
            old_name='upper_limat',
            new_name='upper_limit',
        ),
    ]
