# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-04-27 05:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0036_journal_error_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='reverse_reconciliation',
            field=models.BooleanField(default=False),
        ),
    ]
