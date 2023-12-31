# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2019-06-21 03:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='mtd',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='tax',
            name='mtdoc',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='tax',
            name='rate',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='tax',
            name='ytd',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='tax',
            name='ytdoc',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
    ]
