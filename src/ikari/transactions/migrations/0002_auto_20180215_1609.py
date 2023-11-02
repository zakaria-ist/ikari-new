# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 08:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='adjustment_amount',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='discount_amount',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
        ),
    ]