# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-03-02 02:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0012_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringentrydetail',
            name='discount_amount',
        ),
    ]
