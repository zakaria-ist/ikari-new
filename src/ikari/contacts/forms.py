from django.forms import ModelChoiceField
from customers.models import Customer, Delivery
from suppliers.models import Supplier
from contacts.models import Contact
from locations.models import Location
from django import forms


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ContactForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    attention = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    designation = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    supplier = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    location = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    delivery = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    consignee = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(initial=True, required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    web = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))

    class Meta:
        model = Contact
        fields = ('code',
                  'name',
                  'attention',
                  'note',
                  'company_name',
                  'designation',
                  'customer',
                  'supplier',
                  'location',
                  'delivery',
                  'consignee',
                  'address',
                  'phone',
                  'email',
                  'fax',
                  'web',
                  'is_active'
                  )

    def __init__(self, company_id, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        if company_id:
            customer_list = Customer.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.fields['customer'].queryset = customer_list
            self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.fields['location'].queryset = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.fields['delivery'].queryset = Delivery.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.fields['consignee'].queryset = customer_list
