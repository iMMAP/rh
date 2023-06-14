# Generated by Django 4.0.6 on 2023-06-14 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rh', '0002_remove_activitydetail_activity_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('countries', models.ManyToManyField(to='rh.location')),
            ],
            options={
                'verbose_name': 'Activity Domain',
                'verbose_name_plural': 'Activity Domains',
            },
        ),
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('code', models.CharField(blank=True, max_length=600, null=True)),
                ('name', models.CharField(blank=True, max_length=600, null=True)),
                ('activity_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('hrp_code', models.CharField(blank=True, max_length=200, null=True)),
                ('code_indicator', models.BooleanField(blank=True, default=False, null=True)),
                ('start_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('end_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('ocha_code', models.CharField(blank=True, max_length=200, null=True)),
                ('activity_domain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.activitydomain')),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('countries', models.ManyToManyField(to='rh.location')),
            ],
            options={
                'verbose_name': 'Activity Type',
                'verbose_name_plural': 'Activity Types',
            },
        ),
        migrations.CreateModel(
            name='GrantType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Grant Type',
                'verbose_name_plural': 'Grant Types',
            },
        ),
        migrations.CreateModel(
            name='ImplementationModalityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Implementation Modality Type',
                'verbose_name_plural': 'Implementation Modality Types',
            },
        ),
        migrations.CreateModel(
            name='PackageType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Package Type',
                'verbose_name_plural': 'Package Types',
            },
        ),
        migrations.CreateModel(
            name='ReportType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Report Type',
                'verbose_name_plural': 'Report Types',
            },
        ),
        migrations.CreateModel(
            name='StrategicObjective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategic_objective_name', models.CharField(blank=True, max_length=200, null=True)),
                ('strategic_objective_description', models.CharField(blank=True, max_length=600, null=True)),
                ('output_objective_name', models.CharField(blank=True, max_length=200, null=True)),
                ('sector_objective_name', models.CharField(blank=True, max_length=200, null=True)),
                ('sector_objective_description', models.CharField(blank=True, max_length=600, null=True)),
                ('denominator', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Objective',
                'verbose_name_plural': 'Objectives',
            },
        ),
        migrations.CreateModel(
            name='TransferCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Transfer Category',
                'verbose_name_plural': 'Transfer Categories',
            },
        ),
        migrations.CreateModel(
            name='UnitType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Unit Type',
                'verbose_name_plural': 'Unit Types',
            },
        ),
        migrations.CreateModel(
            name='TransferMechanismType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('modality_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.implementationmodalitytype')),
            ],
            options={
                'verbose_name': 'Transfer Mechanism Type',
                'verbose_name_plural': 'Transfer Mechanism Types',
            },
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=600, null=True)),
                ('name', models.CharField(blank=True, max_length=600, null=True)),
                ('numerator', models.CharField(blank=True, max_length=200, null=True)),
                ('denominator', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.CharField(blank=True, max_length=1200, null=True)),
                ('activity_types', models.ManyToManyField(to='activities.activitytype')),
            ],
            options={
                'verbose_name': 'Indicator',
                'verbose_name_plural': 'Indicators',
            },
        ),
        migrations.CreateModel(
            name='FacilitySiteType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('cluster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.cluster')),
            ],
            options={
                'verbose_name': 'Facility Site Type',
                'verbose_name_plural': 'Facility Site Types',
            },
        ),
        migrations.CreateModel(
            name='Disaggregation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=200)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('indicators', models.ManyToManyField(to='activities.indicator')),
            ],
        ),
        migrations.CreateModel(
            name='BeneficiaryType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('is_hrp_beneficiary', models.BooleanField(default=False)),
                ('is_regular_beneficiary', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=600, null=True)),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.location')),
            ],
            options={
                'verbose_name': 'Beneficiary Type',
                'verbose_name_plural': 'Beneficiary Types',
            },
        ),
        migrations.AddField(
            model_name='activitytype',
            name='objective',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.strategicobjective'),
        ),
        migrations.CreateModel(
            name='ActivityDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=600, null=True)),
                ('name', models.CharField(blank=True, max_length=600, null=True)),
                ('activity_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.activitytype')),
            ],
            options={
                'verbose_name': 'Activity Detail',
                'verbose_name_plural': 'Activity Details',
            },
        ),
    ]
