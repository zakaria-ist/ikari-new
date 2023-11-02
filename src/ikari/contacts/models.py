from datetime import date
from django.db import models
from companies.models import Company
from customers.models import Customer, Delivery
from locations.models import Location
from suppliers.models import Supplier
from utilities.constants import CONTACT_TYPES_DICT


# Create your models here.
class Contact(models.Model):
    code = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100)
    attention = models.CharField(max_length=200)
    note = models.TextField(null=True)
    company_name = models.CharField(max_length=500, null=True)
    designation = models.CharField(max_length=500, null=True)
    contact_type = models.IntegerField(default=int(CONTACT_TYPES_DICT['Undefined']), null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name="customer_contact")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True)
    consignee = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name="consignee_contact")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    web = models.CharField(max_length=500, null=True)
    fax = models.CharField(max_length=20, null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
