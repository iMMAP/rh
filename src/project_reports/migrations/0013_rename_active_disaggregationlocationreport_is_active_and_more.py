# Generated by Django 5.0.6 on 2024-07-25 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0012_alter_disaggregationlocationreport_target_required'),
    ]

    operations = [
        migrations.RenameField(
            model_name='disaggregationlocationreport',
            old_name='active',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='projectmonthlyreport',
            old_name='active',
            new_name='is_active',
        ),
    ]
