from django.db import models
from currencies.models import Currency
from datetime import date


# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
