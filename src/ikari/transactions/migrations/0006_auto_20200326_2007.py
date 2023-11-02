# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-03-26 12:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_transaction_is_auto_exch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='source_type',
            field=models.CharField(choices=[('GL-AD', 'Audit Adjustments (G/L Entry)'), ('GL-CL', 'G/L Closing Entry'), ('GL-CV', 'G/L Data Conversion Entry'), ('GL-JE', 'G/L Journal Entry'), ('GL-PV', 'G/L Payment Voucher'), ('GL-RV', 'G/L Revaluation Transactions'), ('AP-AD', 'A/P Adjustments'), ('AP-CR', 'A/P Credit Note'), ('AP-DB', 'A/P Debit Note'), ('AP-GL', 'A/P Revaluation'), ('AP-IN', 'A/P Invoice'), ('AP-PY', 'A/P Check'), ('AP-RD', 'A/P Rounding'), ('AP-RV', 'A/P Revaluation'), ('AR-AD', 'A/R Adjustments'), ('AR-CR', 'A/R Credit Note'), ('AR-DB', 'A/R Debit Note'), ('AR-GL', 'A/R Revaluation'), ('AR-IN', 'A/R Invoice'), ('AR-PY', 'A/R Payment Received'), ('AR-RD', 'A/R Rounding'), ('AR-RV', 'A/R Revaluation')], max_length=50, null=True),
        ),
    ]