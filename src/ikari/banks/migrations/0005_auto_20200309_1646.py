# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-03-09 08:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0004_bank_supplier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bank',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='bank',
            name='supplier',
        ),
    ]
