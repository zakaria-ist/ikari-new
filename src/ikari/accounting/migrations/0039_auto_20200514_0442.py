# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-05-13 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0038_auto_20200514_0437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='journal_type',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
