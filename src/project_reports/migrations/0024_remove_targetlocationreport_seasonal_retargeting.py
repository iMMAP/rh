# Generated by Django 5.1.4 on 2024-12-23 04:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0023_rename_prev_targeted_by_targetlocationreport_prev_assisted_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='seasonal_retargeting',
        ),
    ]