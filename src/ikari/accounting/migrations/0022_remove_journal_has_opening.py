# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-05-21 10:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0021_journal_rev_perd_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journal',
            name='has_opening',
        ),
    ]