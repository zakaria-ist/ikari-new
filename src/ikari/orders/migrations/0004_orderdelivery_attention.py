# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-03 03:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20190307_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdelivery',
            name='attention',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
