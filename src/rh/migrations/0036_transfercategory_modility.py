# Generated by Django 5.1.4 on 2025-01-09 05:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0035_implementationmodalitytype_type_unittype_modility'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfercategory',
            name='modility',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.implementationmodalitytype'),
        ),
    ]
