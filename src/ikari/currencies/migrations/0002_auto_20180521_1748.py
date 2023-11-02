# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-05-21 09:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangerate',
            name='rate',
            field=models.DecimalField(decimal_places=7, max_digits=20, null=True),
        ),
    ]