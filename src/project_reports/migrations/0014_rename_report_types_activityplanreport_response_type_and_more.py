# Generated by Django 5.0.7 on 2024-08-06 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0013_rename_active_disaggregationlocationreport_is_active_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activityplanreport',
            old_name='report_types',
            new_name='response_type',
        ),
        migrations.RenameField(
            model_name='disaggregationlocationreport',
            old_name='target',
            new_name='reached',
        ),
        migrations.RemoveField(
            model_name='activityplanreport',
            name='implementing_partners',
        ),
        migrations.RemoveField(
            model_name='activityplanreport',
            name='indicator',
        ),
        migrations.RemoveField(
            model_name='activityplanreport',
            name='target_achieved',
        ),
        migrations.RemoveField(
            model_name='disaggregationlocationreport',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='disaggregationlocationreport',
            name='target_required',
        ),
        migrations.RemoveField(
            model_name='projectmonthlyreport',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='projectmonthlyreport',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='country',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='district',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='facility_id',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='facility_lat',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='facility_long',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='facility_monitoring',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='facility_name',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='facility_site_type',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='nhs_code',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='province',
        ),
        migrations.RemoveField(
            model_name='targetlocationreport',
            name='zone',
        ),
        migrations.AlterField(
            model_name='projectmonthlyreport',
            name='state',
            field=models.CharField(blank=True, choices=[('todo', 'Todo'), ('pending', 'Pending'), ('submited', 'Submitted'), ('rejected', 'Rejected'), ('completed', 'Completed'), ('archived', 'Archived')], default='todo', max_length=15, null=True),
        ),
    ]