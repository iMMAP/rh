# Generated by Django 5.1.4 on 2025-01-12 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0039_rename_modality_transfermechanismtype_modility'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
