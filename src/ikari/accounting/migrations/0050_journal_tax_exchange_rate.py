# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2022-02-08 02:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0049_auto_20211021_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='tax_exchange_rate',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20),
        ),
    ]