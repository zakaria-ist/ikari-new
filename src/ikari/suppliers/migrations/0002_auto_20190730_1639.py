# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2019-07-30 08:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='remittance',
            field=models.CharField(default=0, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='transport',
            field=models.CharField(default=0, max_length=20, null=True),
        ),
    ]