# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 06:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banks', '0001_initial'),
        ('accounts', '0002_auto_20180215_1454'),
        ('currencies', '0001_initial'),
        ('companies', '0002_auto_20180215_1454'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='revaluation_count',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='recurringentrydetail',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='recurringentrydetail',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='recurringentrydetail',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='recurringentrydetail',
            name='exch_rate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.ExchangeRate'),
        ),
        migrations.AddField(
            model_name='recurringentrydetail',
            name='rec_entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.RecurringEntry'),
        ),
        migrations.AddField(
            model_name='recurringentry',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='recurringentry',
            name='exch_rate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.ExchangeRate'),
        ),
        migrations.AddField(
            model_name='recurringentry',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Schedule'),
        ),
        migrations.AddField(
            model_name='journal',
            name='account_set',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='journal_account_set', to='accounts.AccountSet'),
        ),
        migrations.AddField(
            model_name='journal',
            name='bank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='banks.Bank'),
        ),
        migrations.AddField(
            model_name='journal',
            name='batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Batch'),
        ),
        migrations.AddField(
            model_name='journal',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='journal',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency'),
        ),
    ]
