# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 06:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('currencies', '0001_initial'),
        ('accounts', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='revaluationcode',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='revaluationcode',
            name='revaluation_unrealized_gain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='revaluation_code_unrealized_gain', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='revaluationcode',
            name='revaluation_unrealized_loss',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='revaluation_code_unrealized_loss', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='reportgroup',
            name='account_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='acct_from_id', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='reportgroup',
            name='account_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='acct_to_id', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='reportgroup',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='distributioncode',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='distributioncode',
            name='gl_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accounttype',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='control_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accountset_control_account', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accountset_currency', to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='revaluation_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountset_revaluation_account', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='revaluation_realized_gain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountset_revaluation_realized_gain', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='revaluation_realized_loss',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountset_revaluation_realized_loss', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='revaluation_rounding',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountset_revaluation_rounding', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='revaluation_unrealized_gain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountset_revaluation_unrealized_gain', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountset',
            name='revaluation_unrealized_loss',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountset_revaluation_unrealized_loss', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accounthistory',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accounthistory',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='accounthistory',
            name='functional_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='AccountHistory_functional_currency', to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='accounthistory',
            name='source_currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AccountHistory_source_currency', to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='accountcurrency',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountcurrency',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='accountcurrency',
            name='revaluation_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AccountCurrency_revaluation_account', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='accountcurrency',
            name='revaluation_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AccountCurrency_revaluation_code', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='account',
            name='account_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_group', to='accounts.AccountType'),
        ),
        migrations.AddField(
            model_name='account',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
        migrations.AddField(
            model_name='account',
            name='profit_loss_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profit_loss_group', to='accounts.AccountType'),
        ),
    ]
