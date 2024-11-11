# Generated by Django 5.1 on 2024-11-06 10:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_stockreports_from_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockreports',
            name='warehouse_location',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='stock.warehouselocation'),
            preserve_default=False,
        ),
    ]
