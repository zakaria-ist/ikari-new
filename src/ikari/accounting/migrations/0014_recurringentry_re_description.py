# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-03-08 08:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0013_remove_recurringentrydetail_discount_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringentry',
            name='re_description',
            field=models.CharField(max_length=60, null=True),
        ),
    ]