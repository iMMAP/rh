# Generated by Django 4.0.6 on 2023-06-19 06:54

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0011_alter_indicator_activity_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityplan',
            name='indicator',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='activity_detail', chained_model_field='activity_details', null=True, on_delete=django.db.models.deletion.CASCADE, to='rh.indicator'),
        ),
    ]
