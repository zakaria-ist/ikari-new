from django.db import models
from companies.models import Company
from currencies.models import Currency
from countries.models import Country
# from customers.models import Customer
# from suppliers.models import Supplier
from accounts.models import Account
from datetime import date


# Create your models here.
class Bank(models.Model):
    code = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    account_owner = models.CharField(max_length=100, null=True)
    account_number = models.CharField(max_length=50, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='main_account')
    description = models.TextField(null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    # supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    # gain & loss account
    gain_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='gain_account')
    loss_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='loss_account')
    round_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='round_account')
