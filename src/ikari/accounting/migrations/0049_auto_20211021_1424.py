# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2021-10-21 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0048_auto_20211020_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringentrydetail',
            name='is_auto_exch',
            field=models.BooleanField(default=False),
        ),
    ]
