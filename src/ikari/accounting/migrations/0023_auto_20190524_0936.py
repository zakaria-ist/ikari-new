# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2019-05-24 01:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0022_remove_journal_has_opening'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=9, default=0, max_digits=20),
        ),
    ]
