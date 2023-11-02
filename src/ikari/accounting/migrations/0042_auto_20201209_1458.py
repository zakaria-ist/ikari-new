# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-12-09 06:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0041_auto_20201111_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringentrydetail',
            name='adjustment_amount',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='recurringentrydetail',
            name='discount_amount',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
        ),
    ]
