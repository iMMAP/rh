# Generated by Django 4.0.6 on 2023-12-20 05:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0006_alter_organization_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetlocation',
            name='classification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_classification', to='rh.location'),
        ),
    ]
