# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-04-27 02:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0018_journal_is_auto_reversed_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='has_opening',
            field=models.BooleanField(default=False),
        ),
    ]
