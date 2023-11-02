# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2021-09-28 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_auto_20190621_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationitem',
            name='back_order_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='booked_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='last_closing_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='last_open_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='max_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='min_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='month_closing_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='month_open_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='mv_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='onhand_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='reorder_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='stock_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='locationitem',
            name='year_open_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]