from django.db import models
from datetime import date


# Create your models here.
class Currency(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True, db_index=True)
    symbol = models.CharField(max_length=10, null=True)
    is_decimal = models.BooleanField(max_length=2, default=True)
    format = models.CharField(max_length=20, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


class ExchangeRate(models.Model):
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='from_currency', null=False)
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='to_currency', null=False)
    rate = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    exchange_date = models.DateField(default=date.today)
    description = models.CharField(max_length=4000, null=True, blank=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(null=False)
    apply_flag = models.BooleanField(null=False, default=True)
    flag = models.CharField(max_length=15, null=True, blank=True) #see constant EXCHANGE_RATE_TYPE
