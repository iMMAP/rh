# Generated by Django 4.0.6 on 2023-04-17 16:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=600, null=True)),
                ('name', models.CharField(blank=True, max_length=600, null=True)),
            ],
            options={
                'verbose_name': 'Activity Detail',
                'verbose_name_plural': 'Activity Details',
            },
        ),
        migrations.CreateModel(
            name='ActivityDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Activity Domain',
                'verbose_name_plural': 'Activity Domains',
            },
        ),
        migrations.CreateModel(
            name='ActivityPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('state', models.CharField(blank=True, choices=[('draft', 'Draft'), ('in-progress', 'In Progress'), ('done', 'Completed'), ('archive', 'Archived')], default='draft', max_length=15, null=True)),
                ('title', models.CharField(blank=True, max_length=800, null=True)),
                ('beneficiary_category', models.CharField(blank=True, choices=[('disabled', 'Persons with Disabilities'), ('non-disabled', 'Non-Disabled')], default=False, max_length=15, null=True)),
                ('facility_monitoring', models.BooleanField(default=False)),
                ('facility_name', models.CharField(blank=True, max_length=200, null=True)),
                ('facility_id', models.CharField(blank=True, max_length=200, null=True)),
                ('facility_lat', models.CharField(blank=True, max_length=200, null=True)),
                ('facility_long', models.CharField(blank=True, max_length=200, null=True)),
                ('age_desegregation', models.BooleanField(default=False)),
                ('female_0_5', models.IntegerField(blank=True, default=0, null=True)),
                ('female_6_12', models.IntegerField(blank=True, default=0, null=True)),
                ('female_12_17', models.IntegerField(blank=True, default=0, null=True)),
                ('female_18', models.IntegerField(blank=True, default=0, null=True)),
                ('female_total', models.IntegerField(blank=True, default=0, null=True)),
                ('male_0_5', models.IntegerField(blank=True, default=0, null=True)),
                ('male_6_12', models.IntegerField(blank=True, default=0, null=True)),
                ('male_12_17', models.IntegerField(blank=True, default=0, null=True)),
                ('male_18', models.IntegerField(blank=True, default=0, null=True)),
                ('male_total', models.IntegerField(blank=True, default=0, null=True)),
                ('other_0_5', models.IntegerField(blank=True, default=0, null=True)),
                ('other_6_12', models.IntegerField(blank=True, default=0, null=True)),
                ('other_12_17', models.IntegerField(blank=True, default=0, null=True)),
                ('other_18', models.IntegerField(blank=True, default=0, null=True)),
                ('other_total', models.IntegerField(blank=True, default=0, null=True)),
                ('total_0_5', models.IntegerField(blank=True, default=0, null=True)),
                ('total_6_12', models.IntegerField(blank=True, default=0, null=True)),
                ('total_12_17', models.IntegerField(blank=True, default=0, null=True)),
                ('total_18', models.IntegerField(blank=True, null=True)),
                ('total', models.IntegerField(blank=True, default=0, null=True)),
                ('households', models.IntegerField(blank=True, default=0, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True)),
                ('activity_detail', smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='activity_type', chained_model_field='activity_type', null=True, on_delete=django.db.models.deletion.CASCADE, to='rh.activitydetail')),
                ('activity_domain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.activitydomain')),
            ],
            options={
                'verbose_name': 'Activity Plan',
                'verbose_name_plural': 'Activity Plans',
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
                ('activity_domain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.activitydomain')),
            ],
            options={
                'verbose_name': 'Activity Type',
                'verbose_name_plural': 'Activity Types',
            },
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('ocha_code', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, null=True)),
            ],
            options={
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='Donor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True)),
                ('cluster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.cluster')),
            ],
            options={
                'verbose_name': 'Donor',
                'verbose_name_plural': 'Donors',
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
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('level', models.IntegerField(default=0)),
                ('original_name', models.CharField(blank=True, max_length=200, null=True)),
                ('type', models.CharField(blank=True, choices=[('All', 'ALL'), ('Country', 'Country'), ('Province', 'Province'), ('District', 'District')], default='Country', max_length=15, null=True)),
                ('lat', models.FloatField(blank=True, null=True)),
                ('long', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('parent', models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='rh.location')),
            ],
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, null=True)),
            ],
            options={
                'verbose_name': 'Location Type',
                'verbose_name_plural': 'Location Types',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('type', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='Old ID')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.location')),
            ],
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
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(blank=True, choices=[('draft', 'Draft'), ('in-progress', 'In Progress'), ('done', 'Completed'), ('archive', 'Archived')], default='draft', max_length=15, null=True)),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=200)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('is_hrp_project', models.BooleanField(default=False)),
                ('has_hrp_code', models.BooleanField(default=False)),
                ('hrp_code', models.CharField(blank=True, max_length=200, null=True)),
                ('start_date', models.DateTimeField(verbose_name='start date')),
                ('end_date', models.DateTimeField(verbose_name='end date')),
                ('budget', models.IntegerField(blank=True, null=True)),
                ('budget_received', models.IntegerField(blank=True, null=True)),
                ('budget_gap', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True, null=True)),
                ('updated_at', models.DateField(auto_now=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True)),
                ('activity_domains', models.ManyToManyField(related_name='activity_domains', to='rh.activitydomain')),
                ('budget_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.currency')),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('donors', models.ManyToManyField(to='rh.donor')),
                ('implementing_partners', models.ManyToManyField(related_name='implementing_partners', to='rh.organization')),
                ('programme_partners', models.ManyToManyField(related_name='programme_partners', to='rh.organization')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
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
                ('modality_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.implementationmodalitytype')),
            ],
            options={
                'verbose_name': 'Transfer Mechanism Type',
                'verbose_name_plural': 'Transfer Mechanism Types',
            },
        ),
        migrations.CreateModel(
            name='TargetLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('state', models.CharField(blank=True, choices=[('draft', 'Draft'), ('in-progress', 'In Progress'), ('done', 'Completed'), ('archive', 'Archived')], default='draft', max_length=15, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('locations_group_by', models.CharField(blank=True, choices=[('province', 'Province/State'), ('district', 'District')], max_length=15, null=True)),
                ('group_by_province', models.BooleanField(default=True)),
                ('group_by_district', models.BooleanField(default=True)),
                ('group_by_custom', models.BooleanField(default=True)),
                ('site_name', models.CharField(blank=True, max_length=255, null=True)),
                ('site_lat', models.CharField(blank=True, max_length=255, null=True)),
                ('site_long', models.CharField(blank=True, max_length=255, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_country', to='rh.location')),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_district', to='rh.location')),
                ('implementing_partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.organization')),
                ('location_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.locationtype')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.project')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_province', to='rh.location')),
            ],
            options={
                'verbose_name': 'Target Location',
                'verbose_name_plural': 'Target Locations',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boys', models.IntegerField(blank=True, null=True)),
                ('girls', models.IntegerField(blank=True, null=True)),
                ('men', models.IntegerField(blank=True, null=True)),
                ('women', models.IntegerField(blank=True, null=True)),
                ('elderly_men', models.IntegerField(blank=True, null=True)),
                ('elderly_women', models.IntegerField(blank=True, null=True)),
                ('households', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('activity_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.activityplan')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.location')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.project')),
            ],
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
                ('activity_types', models.ManyToManyField(to='rh.activitytype')),
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
        migrations.AddField(
            model_name='donor',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.location'),
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
            name='clusters',
            field=models.ManyToManyField(to='rh.cluster'),
        ),
        migrations.AddField(
            model_name='activitytype',
            name='countries',
            field=models.ManyToManyField(to='rh.location'),
        ),
        migrations.AddField(
            model_name='activitytype',
            name='objective',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.strategicobjective'),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='activity_type',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='activity_domain', chained_model_field='activity_domain', null=True, on_delete=django.db.models.deletion.CASCADE, to='rh.activitytype'),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='beneficiary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiary', to='rh.beneficiarytype'),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='facility_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.facilitysitetype'),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='hrp_beneficiary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hrp_beneficiary', to='rh.beneficiarytype'),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='indicators',
            field=smart_selects.db_fields.ChainedManyToManyField(blank=True, chained_field='activity_type', chained_model_field='activity_types', to='rh.indicator'),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.project'),
        ),
        migrations.AddField(
            model_name='activitydomain',
            name='clusters',
            field=models.ManyToManyField(to='rh.cluster'),
        ),
        migrations.AddField(
            model_name='activitydomain',
            name='countries',
            field=models.ManyToManyField(to='rh.location'),
        ),
        migrations.AddField(
            model_name='activitydetail',
            name='activity_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.activitytype'),
        ),
    ]
