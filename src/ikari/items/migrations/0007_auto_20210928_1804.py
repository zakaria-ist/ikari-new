# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2021-09-28 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0006_auto_20191126_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='backorder_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='balance_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='in_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='minimun_order',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='out_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='po_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='so_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]