# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 06:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('items', '0001_initial'),
        ('currencies', '0001_initial'),
        ('inventory', '0001_initial'),
        ('locations', '0001_initial'),
        ('companies', '0002_auto_20180215_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktransactiondetail',
            name='in_location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='in_location_details', to='locations.Location'),
        ),
        migrations.AddField(
            model_name='stocktransactiondetail',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.Item'),
        ),
        migrations.AddField(
            model_name='stocktransactiondetail',
            name='out_location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='out_location_details', to='locations.Location'),
        ),
        migrations.AddField(
            model_name='stocktransactiondetail',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.StockTransaction'),
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='in_location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='in_location', to='locations.Location'),
        ),
    ]
