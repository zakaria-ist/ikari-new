from django.db import models
from companies.models import Company
from accounts.models import Account, DistributionCode
from currencies.models import Currency
from taxes.models import Tax
from datetime import date
from utilities.constants import SOURCE_TYPES, BALANCE_TYPE


# Create your models here.
class TransactionMethod(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=10, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    is_debit = models.BooleanField(default=True)
    is_credit = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


# Create your models here.
class Transaction(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, null=True)
    journal = models.ForeignKey("accounting.Journal", on_delete=models.CASCADE, null=True, related_name='journal', db_index=True)
    is_credit_account = models.BooleanField(default=False)
    is_debit_account = models.BooleanField(default=False)
    pair = models.ForeignKey('self', null=True, blank=True, related_name='pair_transactions')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    distribution_code = models.ForeignKey(DistributionCode, on_delete=models.CASCADE, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    discount_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount discount
    adjustment_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount adjustment (+/-)
    base_tax_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0, null=True)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount - discount - (+adjustment) after tax
    transaction_date = models.DateField(default=date.today)
    remark = models.TextField(max_length=100, null=True, default='')
    method = models.ForeignKey(TransactionMethod, on_delete=models.CASCADE, null=True)
    number = models.CharField(max_length=50, null=True, default='')
    # GL Entry
    source_type = models.CharField(max_length=50, null=True, choices=SOURCE_TYPES)  # ==> Use For 5: GL
    reference = models.CharField(max_length=100, null=True, default='')
    description = models.CharField(max_length=500, null=True, default='')
    functional_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, related_name='functional_currency')
    functional_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    rate_date = models.DateField(null=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=1)
    # create this field for Payment/Receipt, not sure if necessary in future
    related_invoice = models.ForeignKey("accounting.Journal", on_delete=models.CASCADE, null=True, related_name='related_invoice', db_index=True)
    # End GL Entry
    is_tax_include = models.BooleanField(default=False)
    is_tax_transaction = models.BooleanField(default=False)
    is_manual_tax_input = models.BooleanField(default=False)
    is_close = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    functional_balance_type = models.CharField(max_length=1, choices=BALANCE_TYPE, null=True)
    is_report = models.BooleanField(default=False)
    is_clear_tax = models.BooleanField(default=False)
    is_auto_exch = models.BooleanField(default=False)

    related_journal_outstanding = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    def __str__(self):
        return str(self.id) + '-- Journal_ID: ' + str(self.journal_id) + ' - Related_invoice_id: ' + str(self.related_invoice_id)
