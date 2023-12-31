# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_recurringentry_exch_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringentry',
            name='total_amount',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
        ),

        migrations.AddField(
            model_name='recurringentry',
            name='entry_mode',
            field=models.IntegerField(choices=[(0, 'Normal'), (1, 'Quick')], default=0),
        ),
    ]
