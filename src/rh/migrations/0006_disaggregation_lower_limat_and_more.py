# Generated by Django 4.0.6 on 2024-03-20 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0005_remove_granttype_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='disaggregation',
            name='lower_limat',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='disaggregation',
            name='upper_limat',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
