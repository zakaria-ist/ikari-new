# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2022-05-24 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0053_journal_real_adjustment'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='has_old_rate',
            field=models.BooleanField(default=False),
        ),
    ]
