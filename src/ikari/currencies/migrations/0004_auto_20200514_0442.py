# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-05-13 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0003_auto_20190307_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='code',
            field=models.CharField(db_index=True, max_length=20, null=True),
        ),
    ]
