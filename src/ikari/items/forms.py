from django import forms
from django.forms import ModelChoiceField
from selectable.forms import AutoComboboxWidget
from customers.models import CustomerItem
import customers.models
from items.models import Item, ItemCategory, ItemMeasure
from suppliers.lookups import SupplierLookup
from suppliers.models import Supplier, SupplierItem
from locations.models import Location
from taxes.models import Tax
from countries.models import Country
from currencies.models import Currency


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class CodeNameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name

class CodeChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code

class ItemForm(forms.ModelForm):
    supplier = forms.CharField(
        widget=AutoComboboxWidget(SupplierLookup, attrs={'class': 'selectable-control'}),
        required=False,
    )
    category = CodeChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control item_code_search', 'required': 'required'}))

    short_description = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
    name = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
    sale_price = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control text-right numeric_price'}))
    purchase_price = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control text-right'}))
    stockist_price = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control text-right'}))

    minimun_order = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control text-right numeric_qty'}))
    size = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    weight = forms.CharField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control numeric_qty'}))
    par_value = forms.CharField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control numeric_qty'}))
    book_value = forms.CharField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control numeric_qty'}))
    country = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    ratio = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control text-right numeric_qty',
                                                                               'type': "number", 'step': "0.0001"}))
    person_incharge = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    model_qty = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control text-right numeric_qty'}))
    sale_currency = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                       widget=forms.Select(attrs={'class': 'form-control'}))
    purchase_currency = CodeNameChoiceField(queryset=None, empty_label='---Select---', required=False,
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    report_measure = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    inv_measure = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    sales_measure = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                       widget=forms.Select(attrs={'class': 'form-control'}))
    purchase_measure = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    default_supplier = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    default_location = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Item
        fields = (
            'supplier', 'category',
            'short_description', 'name', 'sale_price', 'purchase_price','stockist_price',
            'par_value', 'book_value',
            'minimun_order', 'size', 'weight',
            'country', 'ratio', 'person_incharge', 'model_qty', 'sale_currency', 'code',
            'report_measure', 'inv_measure', 'sales_measure', 'purchase_measure', 'purchase_currency',
            'default_supplier', 'default_location'
        )

    def __init__(self, company_id,type_flag, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        if company_id:
            category_list = ItemCategory.objects.filter(is_hidden=0, company_id=company_id)

            # if account_list and category_list:
            self.fields['category'].queryset = category_list

            self.fields['default_supplier'].queryset = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
            self.fields['default_location'].queryset = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id)

            self.fields['supplier'].widget.lookup_class.filters = {'company_id': company_id,
                                                                   'is_active': True, 'is_hidden': False}
            self.fields['country'].queryset = Country.objects.filter(is_hidden=0).order_by('name')
            currency_qs = Currency.objects.filter(is_hidden=0)

            self.fields['sale_currency'].queryset = currency_qs
            self.fields['purchase_currency'].queryset = currency_qs

            measure_qs = ItemMeasure.objects.filter(is_hidden=0)
            self.fields['report_measure'].queryset = measure_qs
            self.fields['inv_measure'].queryset = measure_qs
            self.fields['sales_measure'].queryset = measure_qs
            self.fields['purchase_measure'].queryset = measure_qs


class ItemCategoryForm(forms.ModelForm):

    short_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    code = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=False,
                                       widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))
    tax = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ItemCategory
        fields = ('short_description',
                  'name',
                  'tax',
                  'code'
                  )

    def __init__(self, company_id, *args, **kwargs):
      super(ItemCategoryForm, self).__init__(*args, **kwargs)
      tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id)
      self.fields['tax'].queryset = tax_list


class CustomerItemForm(forms.ModelForm):
    currency = CodeNameChoiceField(queryset=None, empty_label=None, required=True,
                                  widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    sales_price = forms.DecimalField(required=True,
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required',
                                                                     'type': "number", 'step': "0.000001"}))
    leading_days = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    effective_date = forms.DateField(required=False, input_formats=('%d-%m-%Y',), widget=forms.DateInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'format': '%d-%m-%Y', 'style': 'width: 100%;'}))

    class Meta:
        model = customers.models.CustomerItem
        fields = ('currency', 'sales_price', 'leading_days', 'effective_date')

    def __init__(self, company_id, *args, **kwargs):
        super(CustomerItemForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)


class PartSaleItemForm(forms.ModelForm):
    line_number = forms.CharField(required=False,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control-item', 'style': 'display: none'}))
    customer_id = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'style': 'display: none'}))
    customer_code = forms.CharField(required=False,
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    customer_name = forms.CharField(required=False,
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    currency_code = forms.CharField(required=False,
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    currency_id = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'style': 'display: none'}))
    sales_price = forms.CharField(required=False,
                                     widget=forms.TextInput(attrs={'class': 'form-control text-right numeric_price', 'required': 'required',
                                                                     'style': 'width: 155px'}))
    new_price = forms.CharField(required=False,
                                   widget=forms.TextInput(
                                       attrs={'class': 'form-control text-right last-tab numeric_price', 'style': 'width: 155px'}))
    leading_days = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control leading_days', 'style': 'width: 80px', 'min': '0'}))
    effective_date = forms.DateField(required=False, input_formats=('%d-%m-%Y',), 
                                  widget=forms.DateInput(
                                      attrs={
                                          'class': 'form-control form-control-inline input-medium',
                                          'format': '%d-%m-%Y',
                                          'style': 'width: 100px'}))
    update_date = forms.DateField(required=False, input_formats=('%d-%m-%Y',),
                                  widget=forms.DateInput(
                                      attrs={
                                          'class': 'form-control form-control-inline input-medium',
                                          'style': 'width: 100px',
                                          'format': '%d-%m-%Y',
                                          'readonly': 'readonly'}))

    class Meta:
        model = CustomerItem
        fields = (
            'line_number', 'customer_id', 'customer_code', 'customer_name', 'currency_code', 'currency_id',
            'sales_price', 'new_price', 'leading_days', 'effective_date', 'update_date')


class SupplierItemForm(forms.ModelForm):
    currency = CodeNameChoiceField(queryset=None, empty_label=None, required=True,
                                  widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    purchase_price = forms.DecimalField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'required': 'required',
               'type': "number", 'step': "0.000001"}))
    leading_days = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    effective_date = forms.DateField(required=False, input_formats=('%d-%m-%Y',), widget=forms.DateInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'format': '%d-%m-%Y', 'style': 'width: 100%;'}))

    class Meta:
        model = SupplierItem
        fields = ('currency', 'purchase_price', 'leading_days', 'effective_date')

    def __init__(self, company_id, *args, **kwargs):
        super(SupplierItemForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)


class PurchaseItemForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control item_code_search', 'required': 'required'}))
    short_description = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
    name = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 1}))
    country = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    category = CodeChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    purchase_price = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control text-right numeric_price'}))
    inv_measure = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    purchase_currency = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    purchase_measure = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    model_qty = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control text-right numeric_qty'}))
    person_incharge = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    minimun_order = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control text-right numeric_qty'}))

    default_supplier = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    # default_location = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
    #                                       widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Item
        fields = ('category',
                  'short_description', 'name', 'purchase_price',
                  'minimun_order',
                  'country', 'person_incharge', 'model_qty', 'code',
                  'inv_measure', 'purchase_measure', 'purchase_currency',
                  'default_supplier' # 'default_location'
                  )

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(PurchaseItemForm, self).__init__(*args, **kwargs)
        category_list = ItemCategory.objects.filter(is_hidden=0, company_id=self.company_id)
        self.fields['category'].queryset = category_list
        self.fields['default_supplier'].queryset = Supplier.objects.filter(is_hidden=0, company_id=self.company_id, is_active=1)
        self.fields['country'].queryset = Country.objects.filter(is_hidden=0).order_by('name')
        currency_qs = Currency.objects.filter(is_hidden=0)
        self.fields['purchase_currency'].queryset = currency_qs
        measure_qs = ItemMeasure.objects.filter(is_hidden=0)
        self.fields['inv_measure'].queryset = measure_qs
        self.fields['purchase_measure'].queryset = measure_qs

