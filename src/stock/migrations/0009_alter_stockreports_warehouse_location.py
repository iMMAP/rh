# Generated by Django 5.1 on 2024-11-06 10:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_stockreports_warehouse_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockreports',
            name='warehouse_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stock.warehouselocation'),
        ),
    ]
