# Generated by Django 4.0.6 on 2024-03-24 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0007_rename_lower_limat_disaggregation_lower_limit_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='disaggregation',
            name='type',
        ),
        migrations.AddField(
            model_name='disaggregation',
            name='gender',
            field=models.CharField(choices=[('Male', 'male'), ('Female', 'female'), ('Other', 'other')], max_length=200, null=True),
        ),
    ]
