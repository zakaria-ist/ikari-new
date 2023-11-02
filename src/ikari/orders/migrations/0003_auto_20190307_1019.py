# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-03-07 02:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20180215_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=9, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='supllier_exchange_rate',
            field=models.DecimalField(decimal_places=9, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax_exchange_rate',
            field=models.DecimalField(decimal_places=9, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=9, max_digits=20, null=True),
        ),
    ]
