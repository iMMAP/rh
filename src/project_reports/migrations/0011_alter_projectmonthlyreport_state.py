# Generated by Django 4.0.6 on 2024-07-09 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0010_disaggregationlocationreport_target_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmonthlyreport',
            name='state',
            field=models.CharField(blank=True, choices=[('todo', 'Todo'), ('pending', 'Pending'), ('submit', 'Submitted'), ('reject', 'Rejected'), ('complete', 'Completed'), ('archive', 'Archived')], default='todo', max_length=15, null=True),
        ),
    ]
