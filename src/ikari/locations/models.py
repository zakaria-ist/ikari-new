from django.db import models
from companies.models import Company
from items.models import Item
from datetime import date
from utilities.constants import LOCATION_PRICE_TYPE, LOCATION_STOCK_CLASS


# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=20, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    attention = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=500, null=True)
    phone = models.CharField(max_length=20, null=True)
    fax = models.CharField(max_length=20, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()

    # Update DB from old system
    pricing_type = models.CharField(max_length=2, null=True, choices=LOCATION_PRICE_TYPE)
    stock_class = models.CharField(max_length=1, null=True, choices=LOCATION_STOCK_CLASS)
    stock_limit = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    stock_take_flag = models.CharField(max_length=50, null=True)
    stock_take_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)


class LocationItem(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    #onhand_qty is the remaining item qty in the store location
    onhand_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    onhand_amount = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    booked_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    booked_amount = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    cost_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    mv_cost_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    mv_cost_price_flag = models.CharField(max_length=50, null=True)
    mv_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    #in_qty is the received item qty in the store location
    in_qty = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=0)
    #out_qty is the delivered item qty in the store location
    out_qty = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=0)
    min_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    max_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    reorder_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    back_order_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    stock_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    last_open_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    last_closing_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    month_open_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    month_closing_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    year_open_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    is_active = models.BooleanField(default=1)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=0)
