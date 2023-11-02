from django.db import models
from companies.models import Company
from currencies.models import Currency
from countries.models import Country
from taxes.models import Tax
from datetime import date


# from orders.models import Order


# Create your models here.
class ItemMeasure(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


# Create your models here.
class ItemCategory(models.Model):
    code = models.CharField(max_length=30, null=True)
    short_description = models.TextField(null=True)
    name = models.TextField(null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    type = models.IntegerField(null=True) # NOW, 1=sp , 2=all , 3 = ics  NOMORE -> 1: Use For S&P, 2: Use For Inventory, else: all
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()

# Create your models here.
class Item(models.Model):
    code = models.CharField(max_length=30, null=True)
    short_description = models.TextField(null=True)
    name = models.TextField(null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name="item_category",null=True)
    sale_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="sale_currency", null=True)
    purchase_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="purchase_currency",null=True)
    sale_price = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    purchase_price = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    stockist_price = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    cost_price = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    retail_price = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    last_purchase_price = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    last_purchase_doc = models.CharField(max_length=50, null=True)
    last_purchase_date = models.DateField(null=True)

    minimun_order = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    size = models.CharField(max_length=50, null=True)
    weight = models.CharField(max_length=50, null=True)

    po_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    so_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    backorder_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    in_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    out_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    balance_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    balance_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    par_value = models.CharField(max_length=50, null=True)
    book_value = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=True)

    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    move_date = models.DateField(default=date.today, null=True)
    update_by = models.CharField(max_length=50, null=True)

    is_hidden = models.BooleanField()
    # add fields based on new requirement

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="country_id", null=True)
    inv_measure = models.ForeignKey(ItemMeasure, on_delete=models.CASCADE, related_name="inv_measure", null=True)
    sales_measure = models.ForeignKey(ItemMeasure, on_delete=models.CASCADE, related_name="sales_measure", null=True)
    purchase_measure = models.ForeignKey(ItemMeasure, on_delete=models.CASCADE, related_name="purchase_measure", null=True)
    report_measure = models.ForeignKey(ItemMeasure, on_delete=models.CASCADE, related_name="report_measure", null=True)
    model_qty = models.IntegerField(null=True)
    person_incharge = models.CharField(max_length=500, null=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    default_supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.CASCADE, null=True,
                                         related_name="item_default_supplier")
    default_location = models.ForeignKey("locations.Location", on_delete=models.CASCADE, null=True,
                                         related_name="item_default_location")


