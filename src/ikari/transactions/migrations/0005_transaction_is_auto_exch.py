# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-02-03 03:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_transaction_is_manual_tax_input'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='is_auto_exch',
            field=models.BooleanField(default=True),
        ),
    ]
