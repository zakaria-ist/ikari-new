from django.db import models
from django.contrib.auth.models import User
from companies.models import Company
from datetime import date
from django.contrib.auth.models import Group

def content_file_name(instance, filename):
    return '/'.join(['staff', str(instance.id), filename])


# Create your models here.
class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=20, null=True)
    fax = models.CharField(max_length=20, null=True)
    image = models.ImageField(upload_to=content_file_name, null=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()
    is_admin = models.BooleanField()
    notifyChangeSP = models.BooleanField(default=True)


class Permisson(models.Model):
    name = models.CharField(max_length=50, null=True)
    codename = models.CharField(max_length=20, null=True)

class GroupPermissions(models.Model):
    group = models.ForeignKey(Group)
    permission = models.ForeignKey(Permisson)


class UserPermissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permisson)






