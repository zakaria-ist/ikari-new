# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-08-21 04:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20200819_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='gross_weight',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='net_weight',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]
