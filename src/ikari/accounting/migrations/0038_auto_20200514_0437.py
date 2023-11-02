# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-05-13 20:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0037_journal_reverse_reconciliation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='document_date',
            field=models.DateField(db_index=True, default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='journal',
            name='document_number',
            field=models.CharField(db_index=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='journal',
            name='document_type',
            field=models.CharField(choices=[('1', 'Invoice'), ('2', 'Debit Note'), ('3', 'Credit Note'), ('4', 'Interest'), ('5', 'Unapplied Cash'), ('6', 'Prepayment'), ('7', 'Receipt'), ('8', 'Refund'), ('9', 'Payment'), ('10', 'Adjustment'), ('11', 'Miscellaneous Receipt'), ('12', 'Miscellaneous Payment')], db_index=True, default='0', max_length=2),
        ),
    ]
