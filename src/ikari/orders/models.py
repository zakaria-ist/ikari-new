from datetime import date
from django.contrib.auth.admin import User
from django.db import models
from accounts.models import DistributionCode
from companies.models import Company, CostCenters
from contacts.models import Contact
from countries.models import Country
from currencies.models import Currency, ExchangeRate
from customers.models import Customer
from customers.models import Delivery
from items.models import Item, ItemMeasure
from locations.models import Location
from suppliers.models import Supplier
from taxes.models import Tax
from utilities.constants import ORDER_STATUS, ORDER_TYPE, GR_DOC_TYPE, GR_DOC_TYPE_DICT


class Order(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='parent_order')
    document_date = models.DateField(default=date.today)
    invoice_date = models.DateField(default=date.today)
    delivery_date = models.DateField(default=date.today, null=True)
    order_code = models.CharField(max_length=50, null=True)
    document_number = models.CharField(max_length=50, null=True)
    transport_responsibility = models.CharField(max_length=100, null=True)
    reference_number = models.CharField(max_length=50, null=True)
    due_date = models.DateField(default=date.today)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    status = models.SmallIntegerField(null=True, choices=tuple([status[::-1] for status in ORDER_STATUS]))
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    discount = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=6)
    total = models.DecimalField(max_digits=20, decimal_places=6)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    balance = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    order_type = models.SmallIntegerField(null=True, choices=tuple([status[::-1] for status in ORDER_TYPE]))
    cost_center = models.ForeignKey(CostCenters, on_delete=models.CASCADE, null=True)
    header_text = models.CharField(max_length=4000, null=True)
    footer = models.CharField(max_length=4000, null=True)
    note = models.CharField(max_length=4000, null=True)
    remark = models.CharField(max_length=4000, null=True)
    packing_number = models.CharField(max_length=50, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_hidden = models.BooleanField(default=False)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    is_confirm = models.CharField(max_length=2, null=True)
    document_type = models.CharField(max_length=1, null=True, choices=GR_DOC_TYPE,
                                     default=GR_DOC_TYPE_DICT['D/O and Invoice'])
    tax_exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    supllier_exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    ship_from = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, related_name="ship_from")
    ship_to = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, related_name="ship_to")
    uom = models.ForeignKey(ItemMeasure, on_delete=models.CASCADE, null=True)
    via = models.CharField(max_length=100, null=True)
    distribution_code = models.ForeignKey(DistributionCode, on_delete=models.CASCADE, null=True)
    exchange_rate_fk = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True)
    exchange_rate_date = models.DateField(null=True)
    payment_mode = models.ForeignKey("accounting.PaymentCode", on_delete=models.SET_NULL, null=True, related_name='order_payment_code')
    payment_term = models.CharField(max_length=10, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reference = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reference_id', null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='orderitem_from_currency',
                                      null=True)
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='orderitem_to_currency', null=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    line_number = models.IntegerField(null=True)
    refer_line = models.CharField(max_length=11, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=1)
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    delivery_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    receive_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    return_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    bkord_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    customer_po_no = models.CharField(max_length=50, null=True)
    refer_code = models.CharField(max_length=50, null=True)
    refer_number = models.CharField(max_length=50, null=True)
    wanted_date = models.DateField(null=True)
    schedule_date = models.DateField(null=True)
    last_receive_date = models.DateField(null=True)
    last_delivery_date = models.DateField(null=True)
    price = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    amount = models.DecimalField(max_digits=20, decimal_places=6, null=True, default=0)
    origin_country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    carton_no = models.CharField(max_length=50, null=True)
    carton_total = models.IntegerField(null=True, default=0)
    pallet_no = models.CharField(max_length=50, null=True)
    net_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    gross_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    m3_number = models.DecimalField(max_digits=9, decimal_places=4, null=True, default=0)
    description = models.TextField(null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_hidden = models.BooleanField(default=False)
    last_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=0)
    last_purchase_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)


class OrderHeader(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    x_position = models.IntegerField()
    y_position = models.IntegerField()
    label = models.CharField(max_length=300, null=True, blank=True)
    value = models.CharField(max_length=300, null=True, blank=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_hidden = models.BooleanField(default=False)


class OrderDelivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    attention = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    note_1 = models.TextField(null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_hidden = models.BooleanField(default=False, blank=True)
