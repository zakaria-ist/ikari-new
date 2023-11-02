# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-06-15 03:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_auto_20200326_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=10, default=1, max_digits=20),
        ),
    ]
