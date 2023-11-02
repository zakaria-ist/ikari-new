from django.db import models
from banks.models import Bank
from companies.models import Company
from currencies.models import Currency
from countries.models import Country
from taxes.models import Tax
from transactions.models import TransactionMethod
from items.models import Item
from accounts.models import Account, AccountSet, DistributionCode
from datetime import date
from utilities.constants import VENDOR_DEFAULT_MSG


# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True, db_index=True)
    address = models.TextField(null=True)
    postal_code = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    fax = models.CharField(max_length=20, null=True)
    term_days = models.CharField(max_length=10, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True)
    payment_mode = models.ForeignKey(TransactionMethod, on_delete=models.CASCADE, null=True)
    payment_code = models.ForeignKey('accounting.PaymentCode', on_delete=models.CASCADE, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    credit_limit = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    account_set = models.ForeignKey(AccountSet, on_delete=models.CASCADE, null=True)
    account_payable = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    distribution = models.ForeignKey(DistributionCode, on_delete=models.CASCADE, null=True)
    ship_via = models.CharField(max_length=500, null=True, default=0)
    accode_ap = models.CharField(max_length=20, null=True, default=0)
    accode_pur = models.CharField(max_length=20, null=True, default=0)
    accode_exc = models.CharField(max_length=20, null=True, default=0)
    accode_bnk = models.CharField(max_length=20, null=True, default=0)
    accode_chr = models.CharField(max_length=20, null=True, default=0)
    center_ap = models.CharField(max_length=20, null=True, default=0)
    center_pur = models.CharField(max_length=20, null=True, default=0)
    center_exc = models.CharField(max_length=20, null=True, default=0)
    center_bnk = models.CharField(max_length=20, null=True, default=0)
    center_chr = models.CharField(max_length=20, null=True, default=0)
    ship_info_1 = models.TextField(null=True)
    ship_info_2 = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
    email_msg = models.CharField(max_length=1000, null=True, default=VENDOR_DEFAULT_MSG)
    remittance = models.CharField(max_length=5, null=True, default=0)
    transport = models.CharField(max_length=20, null=True, default=0)
    
    def __str__(self):
        return self.name


class SupplierItem(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
    # bound supplier to item as in new requirements
    purchase_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    new_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    leading_days = models.CharField(max_length=500, null=True)
    effective_date = models.DateField(null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
