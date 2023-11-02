from datetime import date

from django.db import models

from countries.models import Country
from currencies.models import Currency


def content_file_name(instance, filename):
    return '/'.join(['company', str(instance.id), filename])

def bs_template_container(instance, filename):
    return '/'.join(['company', str(instance.id)+'/files/BS', filename])

def pl_template_container(instance, filename):
    return '/'.join(['company', str(instance.id)+'/files/PL', filename])


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=100, null=True)
    company_number = models.CharField(max_length=10, null=True)
    code = models.CharField(max_length=10, null=True)
    postal_code = models.CharField(max_length=10, null=True)
    address = models.TextField(null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    web = models.CharField(max_length=500, null=True)
    fax = models.CharField(max_length=20, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=content_file_name, null=True)
    header_logo = models.ImageField(upload_to=content_file_name, null=True)
    footer_logo = models.ImageField(upload_to=content_file_name, null=True)
    closing_date = models.DateField(null=True)
    fiscal_period = models.DateField(null=True)
    current_period_month = models.CharField(max_length=2, null=True)
    current_period_year = models.CharField(max_length=4, null=True)
    current_period_month_sp = models.CharField(max_length=2, null=True)
    current_period_year_sp = models.CharField(max_length=4, null=True)
    current_period_month_ic = models.CharField(max_length=2, null=True)
    current_period_year_ic = models.CharField(max_length=4, null=True)
    is_inventory = models.BooleanField(default=True)
    is_active = models.BooleanField()
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()

    code_size = models.CharField(max_length=2, null=True)
    category_size = models.CharField(max_length=2, null=True)
    extent_item = models.CharField(max_length=2, null=True)
    group_item = models.CharField(max_length=2, null=True)
    uom_item = models.CharField(max_length=10, null=True)
    stock_take = models.CharField(max_length=10, null=True)
    price_decimal = models.CharField(max_length=10, null=True)
    cost_method = models.CharField(max_length=2, null=True)
    remit_remark = models.CharField(max_length=500, null=True)
    use_segment = models.BooleanField(default=False)
    is_multicurrency = models.BooleanField(default=False)
    rate_type = models.CharField(max_length=10, null=True)
    gain_loss_type = models.CharField(max_length=10, null=True)
    fiscal_period_number = models.CharField(max_length=10, null=True)

    bs_template = models.FileField(upload_to=bs_template_container, null=True)
    pl_template = models.FileField(upload_to=pl_template_container, null=True)

    copy_from = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                                                   related_name='company_copy_from')

class CostCenters(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=4000, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField()
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True, blank=True)
    is_hidden = models.BooleanField()
