# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2021-09-29 09:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_account_deactivate_period'),
        ('suppliers', '0005_auto_20200514_0437'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='account_payable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Account'),
        ),
    ]
