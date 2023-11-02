from django.db import models
from companies.models import Company
from locations.models import Location
from currencies.models import Currency
from orders.models import Order
from items.models import Item
from utilities.constants import INV_DOC_TYPE, INV_IN_OUT_FLAG, INV_PRICE_FLAG, ORDER_STATUS
from datetime import date


# Create your models here.
class TransactionCode(models.Model):
    code = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=500, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    io_flag = models.CharField(max_length=50, null=True, choices=tuple([status[::-1] for status in INV_IN_OUT_FLAG]))
    price_flag = models.CharField(max_length=50, null=True, choices=INV_PRICE_FLAG)
    doc_type = models.CharField(max_length=50, null=True, choices=INV_DOC_TYPE)
    auto_generate = models.BooleanField()
    ics_prefix=models.CharField(max_length=10, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
    menu_type = models.CharField(max_length=2, null=True)
    last_no = models.IntegerField(default=0)


class StockTransaction(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    transaction_code = models.ForeignKey(TransactionCode, on_delete=models.CASCADE)
    document_date = models.DateField(default=date.today)
    document_number = models.CharField(max_length=50, null=True)
    io_flag = models.CharField(max_length=50, null=True, choices=tuple([status[::-1] for status in INV_IN_OUT_FLAG]))
    price_flag = models.CharField(max_length=50, null=True, choices=INV_PRICE_FLAG)
    doc_type = models.CharField(max_length=50, null=True, choices=INV_DOC_TYPE)
    in_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='in_location')
    out_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='out_location')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    status =  models.SmallIntegerField(null=True, choices=tuple([status[::-1] for status in ORDER_STATUS]))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    remark = models.CharField(max_length=4000, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    closing_date = models.DateField(default=date.today, null=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    is_from_sp = models.BooleanField(default=False)


class StockTransactionDetail(models.Model):
    parent = models.ForeignKey(StockTransaction, on_delete=models.CASCADE)
    line_number = models.IntegerField(null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    in_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='in_location_details')
    out_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='out_location_details')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    outstanding_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    price = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    amount = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    cost_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    cost = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    remark = models.TextField(null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class Incoming(models.Model):
    transaction_code = models.ForeignKey(TransactionCode, on_delete=models.CASCADE)
    document_number = models.CharField(max_length=50, null=True)
    line_number = models.IntegerField(null=True)
    purchase_date = models.DateField(default=date.today)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='incoming_location')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    out_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    unit_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    balance_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)

    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False)
    is_history = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

class Outgoing(models.Model):
    transaction_code = models.ForeignKey(TransactionCode, on_delete=models.CASCADE)
    document_number = models.CharField(max_length=50, null=True)
    line_number = models.IntegerField(null=True)
    sales_date = models.DateField(default=date.today)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='outgoing_location')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    out_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    in_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    unit_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    ref_line = models.IntegerField(null=True)
    ref_code = models.ForeignKey(TransactionCode, on_delete=models.CASCADE, related_name='ref_code', null=True)
    ref_no = models.CharField(max_length=50, null=True)
    purchase_date = models.DateField(default=date.today)
    document_line = models.IntegerField(null=True)
    sales_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)

    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False)
    is_history = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

class History(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    year = models.IntegerField(default=0)
    month = models.IntegerField(default=0)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='history_location')
    item_code = models.ForeignKey(Item, on_delete=models.CASCADE)
    io_flag = models.CharField(max_length=50, null=True, choices=tuple([status[::-1] for status in INV_IN_OUT_FLAG]))
    transaction_code = models.ForeignKey(TransactionCode, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    amount = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    cost = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)

    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
