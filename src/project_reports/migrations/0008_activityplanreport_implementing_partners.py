# Generated by Django 4.0.6 on 2024-05-23 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0013_indicator_enable_retargeting'),
        ('project_reports', '0007_activityplanreport_beneficiary_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityplanreport',
            name='implementing_partners',
            field=models.ManyToManyField(blank=True, related_name='reporting_implementing_partners', to='rh.organization'),
        ),
    ]
