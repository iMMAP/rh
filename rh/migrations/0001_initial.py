# Generated by Django 4.0.6 on 2022-11-09 08:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('ocha_code', models.CharField(blank=True, max_length=200, null=True)),
                ('title', models.CharField(max_length=200)),
                ('indicator', models.TextField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('fields', models.JSONField(blank=True, default=dict, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='ActivityPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boys', models.IntegerField(blank=True, null=True)),
                ('girls', models.IntegerField(blank=True, null=True)),
                ('men', models.IntegerField(blank=True, null=True)),
                ('women', models.IntegerField(blank=True, null=True)),
                ('elderly_men', models.IntegerField(blank=True, null=True)),
                ('elderly_women', models.IntegerField(blank=True, null=True)),
                ('households', models.IntegerField(blank=True, null=True)),
                ('activity_fields', models.JSONField(blank=True, null=True)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.activity')),
            ],
            options={
                'verbose_name': 'Activity Plan',
                'verbose_name_plural': 'Activity Plans',
            },
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(blank=True, max_length=200, null=True)),
                ('code2', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
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
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=0)),
                ('code', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('original_name', models.CharField(blank=True, max_length=200, null=True)),
                ('type', models.CharField(blank=True, choices=[('Country', 'Country'), ('Province', 'Province'), ('District', 'District')], default='Country', max_length=15, null=True)),
                ('lat', models.FloatField(blank=True, null=True)),
                ('long', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('parent', models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='rh.location')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('budget', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('activities', models.ManyToManyField(to='rh.activity')),
                ('budget_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.currency')),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('locations', models.ManyToManyField(to='rh.location')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
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
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('countires', models.ManyToManyField(to='rh.country')),
            ],
        ),
        migrations.AddField(
            model_name='activityplan',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.project'),
        ),
        migrations.AddField(
            model_name='activity',
            name='clusters',
            field=models.ManyToManyField(to='rh.cluster'),
        ),
        migrations.AddField(
            model_name='activity',
            name='countries',
            field=models.ManyToManyField(to='rh.country'),
        ),
    ]
