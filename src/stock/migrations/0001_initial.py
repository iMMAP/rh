# Generated by Django 4.0.6 on 2024-02-27 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rh', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockItemsType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cluster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.cluster')),
            ],
            options={
                'verbose_name': 'Stock Type',
                'verbose_name_plural': 'Stock Types',
            },
        ),
        migrations.CreateModel(
            name='StockLocationDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_purpose', models.CharField(blank=True, choices=[('Prepositioned', 'Prepositioned'), ('Operational', 'Operational')], default='', max_length=255, null=True)),
                ('targeted_groups', models.CharField(blank=True, choices=[('All Population', 'All Population'), ('Conflict Affected', 'Conflict Affected'), ('Natural Disaster', 'natural-disaster'), ('Returnees', 'Returnees')], default='', max_length=255, null=True)),
                ('status', models.CharField(blank=True, choices=[('Available', 'Available'), ('Reserved', 'Reserved')], default='', max_length=255, null=True)),
                ('qty_in_stock', models.IntegerField(blank=True, default=0, null=True, verbose_name='Qty in Stock')),
                ('qty_in_pipeline', models.IntegerField(blank=True, default=0, null=True, verbose_name='Qty in Pipeline')),
                ('beneficiary_coverage', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cluster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.cluster')),
                ('stock_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stock.stockitemstype')),
            ],
            options={
                'verbose_name': 'Stock Item',
                'verbose_name_plural': 'Stock Item',
            },
        ),
        migrations.CreateModel(
            name='StockUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Stock Unit',
                'verbose_name_plural': 'Stock Units',
            },
        ),
        migrations.CreateModel(
            name='WarehouseLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='district', to='rh.location')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='province', to='rh.location')),
            ],
            options={
                'verbose_name': 'Warehouse Location Plan',
                'verbose_name_plural': 'Warehouse Locations',
            },
        ),
        migrations.CreateModel(
            name='StockReports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('submitted', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('stock_location_details', models.ManyToManyField(to='stock.stocklocationdetails')),
            ],
            options={
                'verbose_name': 'Stock Report',
                'verbose_name_plural': 'Stock Reports',
            },
        ),
        migrations.AddField(
            model_name='stocklocationdetails',
            name='stock_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stock.stockunit', verbose_name='Units'),
        ),
        migrations.AddField(
            model_name='stocklocationdetails',
            name='warehouse_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stock.warehouselocation'),
        ),
    ]
