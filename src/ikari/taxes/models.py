from datetime import date

from django.db import models

from accounts.models import Account
from companies.models import Company
from currencies.models import Currency
from utilities.constants import RETAINAGE_REPORT_TYPES, TAX_BASE_TYPES, TAX_REPORT_LEVEL, TAX_TRX_TYPES, \
    TAX_CALCULATION_METHOD, TAX_TYPE_DICT


# Create your models here.
class Tax(models.Model):
    code = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100, null=True)
    rate = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    number = models.IntegerField(null=True)  # tax_classes
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
    shortname = models.CharField(max_length=30, null=True)

    # additional fields from the old system
    tax_type = models.IntegerField(default=int(TAX_TYPE_DICT['Customer/Vendor']))  # 1=Customers/Vendors; 2=Items
    tax_account_code = models.ForeignKey('accounts.Account', related_name='tax_account_code',
                                         on_delete=models.CASCADE, null=True)
    distribution_code = models.ForeignKey('accounts.DistributionCode', related_name='distribution_code',
                                          on_delete=models.CASCADE, null=True)
    ytd = models.DecimalField(max_digits=20, null=True, decimal_places=6)
    mtd = models.DecimalField(max_digits=20, null=True, decimal_places=6)
    ytdoc = models.DecimalField(max_digits=20, null=True, decimal_places=6)
    mtdoc = models.DecimalField(max_digits=20, null=True, decimal_places=6)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    tax_authority = models.ForeignKey("taxes.TaxAuthority", on_delete=models.CASCADE, null=True)
    tax_group = models.ForeignKey("taxes.TaxGroup", on_delete=models.CASCADE, null=True)
    # end additional field from the old system


class TaxAuthority(models.Model):
    code = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    retainage_rpt_type = models.CharField(max_length=50, null=True, choices=RETAINAGE_REPORT_TYPES)
    max_tax_allowable = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    no_tax_charged_below = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    tax_base = models.CharField(max_length=50, null=True, choices=TAX_BASE_TYPES)
    report_level = models.CharField(max_length=50, null=True, choices=TAX_REPORT_LEVEL)
    liability_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                                          related_name='liability_account')
    is_recoverable = models.BooleanField(default=False)
    recoverable_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                                            related_name='recoverable_account')
    recoverable_rate = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    is_expense_separately = models.BooleanField(default=False)
    expense_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='expense_account')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


class TaxGroup(models.Model):
    code = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100, null=True)
    transaction_type = models.CharField(max_length=50, null=True, choices=TAX_TRX_TYPES)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    calculation_method = models.CharField(max_length=50, null=True, choices=TAX_CALCULATION_METHOD)
    tax_authority = models.ForeignKey(TaxAuthority, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='tax_authority')
    is_taxable = models.BooleanField(default=False)
    is_surtax = models.BooleanField(default=False)
    surtax_authority = models.ForeignKey(TaxAuthority, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='surtax_authority')
    surtax_authority_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
