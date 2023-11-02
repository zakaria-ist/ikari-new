# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-10-26 03:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20200821_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_mode',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_payment_code', to='accounting.PaymentCode'),
        ),
    ]
