# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2021-08-18 04:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0044_recurringentrydetail_is_manual_tax_input'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='payment_number',
            field=models.IntegerField(default=0),
        ),
    ]