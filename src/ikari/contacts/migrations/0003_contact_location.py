# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 06:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
        ('contacts', '0002_auto_20180215_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='locations.Location'),
        ),
    ]
