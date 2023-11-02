from django.db import models
from companies.models import Company
from currencies.models import Currency
from countries.models import Country
from taxes.models import Tax
from transactions.models import TransactionMethod
from locations.models import Location
from accounts.models import Account, AccountSet, DistributionCode
from datetime import date
from items.models import Item
from utilities.constants import CUSTOMER_DEFAULT_MSG


# Create your models here.
class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True, db_index=True)
    postal_code = models.CharField(max_length=20, null=True)
    address = models.TextField(null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    payment_mode = models.ForeignKey(TransactionMethod, on_delete=models.CASCADE, null=True)
    payment_code = models.ForeignKey('accounting.PaymentCode', on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    credit_limit = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    payment_term = models.CharField(max_length=10, null=True)
    account_set = models.ForeignKey(AccountSet, on_delete=models.CASCADE, null=True, related_name='account_set')
    account_receivable = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    interest_profile = models.ForeignKey(AccountSet, on_delete=models.CASCADE, null=True, related_name='interest_profile')
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    fax = models.CharField(max_length=20, null=True)
    note1 = models.TextField(null=True)
    note2 = models.TextField(null=True)
    note3 = models.TextField(null=True)
    customer_type = models.IntegerField(null=True, default=0)
    pricing_type = models.CharField(max_length=10, null=True, default=0)
    interest_flag = models.CharField(max_length=10, null=True, default=0)
    statement = models.CharField(max_length=10, null=True, default=0)
    interest_1 = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    interest_2 = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    interest_3 = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    interest_4 = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    interest_5 = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    accode_ar = models.CharField(max_length=20, null=True, default=0)
    accode_sal = models.CharField(max_length=20, null=True, default=0)
    accode_exc = models.CharField(max_length=20, null=True, default=0)
    accode_int = models.CharField(max_length=20, null=True, default=0)
    accode_bnk = models.CharField(max_length=20, null=True, default=0)
    accode_chr = models.CharField(max_length=20, null=True, default=0)
    center_ar = models.CharField(max_length=20, null=True, default=0)
    center_sal = models.CharField(max_length=20, null=True, default=0)
    center_exc = models.CharField(max_length=20, null=True, default=0)
    center_int = models.CharField(max_length=20, null=True, default=0)
    center_bnk = models.CharField(max_length=20, null=True, default=0)
    center_chr = models.CharField(max_length=20, null=True, default=0)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
    distribution_code = models.ForeignKey(DistributionCode, on_delete=models.CASCADE, null=True)
    email_msg = models.CharField(max_length=1000, null=True, default=CUSTOMER_DEFAULT_MSG)

# add dependency between customer with item as in new requirement


class CustomerItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    sales_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    new_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    leading_days = models.CharField(max_length=500, null=True)
    effective_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


class Delivery(models.Model):
    code = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100)
    attention = models.CharField(max_length=500, null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=50, null=True)
    fax = models.CharField(max_length=20, null=True)
    note_1 = models.CharField(max_length=4000, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=500, null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
