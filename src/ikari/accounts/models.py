from decimal import Decimal

from django.db import models

from companies.models import Company, CostCenters
from currencies.models import Currency
from utilities.constants import REPORT_CATEGORY, ACCOUNT_TYPE, BALANCE_TYPE, ACCOUNT_SET_TYPE, DIS_CODE_TYPE, \
    REPORT_TEMPLATE_TYPES


class AccountType(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True)
    is_debit = models.BooleanField(default=True)
    is_credit = models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=1, choices=REPORT_CATEGORY, default='1')
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class Account(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    description = models.TextField(null=True)
    debit_amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.00'))
    credit_amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.00'))
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPE, null=True)
    balance_type = models.CharField(max_length=1, choices=BALANCE_TYPE, null=True)
    is_multicurrency = models.BooleanField(default=False)
    is_specific_currency = models.BooleanField(default=False)
    default_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    account_group = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name="account_group")
    profit_loss_group = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name="profit_loss_group",
                                          null=True)
    segment_code = models.ForeignKey(CostCenters, on_delete=models.CASCADE, null=True)
    account_segment = models.CharField(max_length=20, null=True)
    is_editable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    deactivate_date = models.DateField(null=True)
    deactivate_period = models.DateField(null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


class DistributionCode(models.Model):
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=1, choices=DIS_CODE_TYPE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    gl_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class AccountHistory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    period_month = models.CharField(max_length=10, null=True)
    period_year = models.CharField(max_length=10, null=True)
    period_date = models.DateField()
    source_currency = models.ForeignKey(Currency, on_delete=models.CASCADE,
                                        related_name='AccountHistory_source_currency', null=True)
    source_debit_amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    source_credit_amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    source_net_change = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    source_begin_balance = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    source_end_balance = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    functional_currency = models.ForeignKey(Currency, on_delete=models.CASCADE,
                                            related_name='AccountHistory_functional_currency')
    functional_debit_amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    functional_credit_amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    functional_net_change = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    functional_begin_balance = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    functional_end_balance = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0.000000'))
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class AccountSet(models.Model):
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=1, choices=ACCOUNT_SET_TYPE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='accountset_currency')
    control_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='accountset_control_account')
    discount_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='accountset_discount_account', null=True)
    prepayment_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='accountset_prepayment_account', null=True)
    writeoff_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='accountset_writeoff_account', null=True)
    revaluation_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                            related_name='accountset_revaluation_account')
    revaluation_unrealized_gain = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                                   related_name='accountset_revaluation_unrealized_gain')
    revaluation_unrealized_loss = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                                   related_name='accountset_revaluation_unrealized_loss')
    revaluation_realized_gain = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                                 related_name='accountset_revaluation_realized_gain')
    revaluation_realized_loss = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                                 related_name='accountset_revaluation_realized_loss')
    revaluation_rounding = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                             related_name='accountset_revaluation_rounding')
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)


class ReportGroup(models.Model):
    account_from = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='acct_from_id')
    account_to = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='acct_to_id')
    account_code_text = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=500, null=True)
    report_template_type = models.CharField(max_length=2, null=True, choices=REPORT_TEMPLATE_TYPES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    is_hidden = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)


class RevaluationCode(models.Model):
    code = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=500, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    is_hidden = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    rate_type = models.CharField(max_length=2, null=True)
    source_type = models.CharField(max_length=5, null=True)

    revaluation_unrealized_gain = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                                   related_name='revaluation_code_unrealized_gain')
    revaluation_unrealized_loss = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                                   related_name='revaluation_code_unrealized_loss')


class AccountCurrency(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    revaluation_code = models.ForeignKey(RevaluationCode, on_delete=models.CASCADE, null=True,
                                            related_name='AccountCurrency_revaluation_code')
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
