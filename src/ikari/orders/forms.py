import datetime
from datetime import date
from django import forms
from django.conf import settings as s
from django.db.models import Q
from django.forms import ModelChoiceField

from accounts.models import Account, AccountType
from companies.models import CostCenters
from contacts.models import Contact
from countries.models import Country
from currencies.models import Currency
from customers.models import Delivery, Customer
from inventory.models import TransactionCode
from locations.models import Location
from orders.models import OrderHeader, Order, OrderItem, OrderDelivery
from suppliers.models import Supplier
from accounting.models import PaymentCode
from taxes.models import Tax
from transactions.models import TransactionMethod, Transaction
from utilities.constants import ORDER_TYPE, TRN_CODE_TYPE_DICT, GR_DOC_TYPE, GR_DOC_TYPE_DICT, TAX_TRX_TYPES_DICT, PAYMENT_CODE_TYPE_DICT


class CodeNameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return obj.name + " (" + str(obj.code) + ") "
        except AttributeError:
            return obj.name


class CodeNameChoiceField1(ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return str(obj.code) + " - " + str(obj.name)
        except AttributeError:
            return obj.name


class NameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return obj.name
        except AttributeError:
            return obj.name


class CodeChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return obj.code
        except AttributeError:
            return obj.code


class TaxChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.code if obj.code else ' ') + " (" + str(obj.rate) + '%' + " )"


class GoodReceiveSearchForm(forms.Form):
    document_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Document Number'}))
    date_from = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control dpd1', 'data-date-format': 'yyyy-mm-dd'}))
    date_to = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control dpd2', 'data-date-format': 'yyyy-mm-dd'}))

    def __init__(self, *args, **kwargs):
        super(GoodReceiveSearchForm, self).__init__(*args, **kwargs)


class OrderHeaderForm(forms.ModelForm):
    label = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}))
    value = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sub Title'}))

    class Meta:
        model = OrderHeader
        fields = ('label', 'value')


class ExtraValueFormRight(forms.ModelForm):
    label = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Label'}))
    value = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Value'}))

    class Meta:
        model = OrderHeader
        fields = ('label', 'value')


class ExtraValueFormLeft(forms.ModelForm):
    label = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Label'}))
    value = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Value'}))

    class Meta:
        model = OrderHeader
        fields = ('label', 'value')


class ExtraValueFormCode(forms.ModelForm):
    label = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Label'}), )
    value = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Value'}))

    class Meta:
        model = OrderHeader
        fields = ('label', 'value')


class AddItemForm(forms.ModelForm):
    line_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none;'}))
    refer_line = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: right; width: 40px;'}))
    reference_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control-item'}))
    ref_number = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_name = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_id = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control-item'}))
    identity = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control-item'}))
    supplier = CodeChoiceField(queryset=Supplier.objects.none(), required=False,
                               widget=forms.Select(
                                   attrs={'class': 'form-control', 'style': 'width: 150px; text-align: left;'}))
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier_code_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    customer_po_no = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'required': 'required', 'style': 'text-align: left; width: 250px;'}))
    backorder_qty = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    category = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    location = CodeChoiceField(queryset=None, empty_label=None, required=False,
                               widget=forms.Select(
                                   attrs={'class': 'form-control', 'style': 'width: 120px; text-align: left;'}))
    wanted_date = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control hide', 'required': 'required', 'style': 'width: 110px; text-align: right;'}))
    schedule_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control hide', 'style': 'width: 110px; text-align: right;'}))

    wanted_fake_date = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control default-date-picker', 'required': 'required', 'style': 'width: 110px; text-align: right;'}))
    schedule_fake_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control default-date-picker', 'style': 'width: 110px; text-align: right;'}))

    uom = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    bkord_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item hide', 'style': 'text-align: right; width: 120px;', 'readonly': 'True',
               'step': '0.1'}))
    quantity = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item numeric_qty', 'style': 'text-align: right; width: 140px;'}),
        error_messages={'required': 'This field is required.'})
    original_currency = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    currency_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    original_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control-item'}))
    stock_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))
    delivery_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))
    receive_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))
    last_delivery_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hide'}))
    last_receive_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hide'}))
    price = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right numeric_price', 'style': 'text-align: right; width: 140px;',
               'step': '0.000001', 'min': '0'}), error_messages={'required': 'This field is required.'})
    exchange_rate = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'style': 'text-align: right; width: 80px;',
               'step': '0.000000001'}),
        error_messages={'required': 'This field is required.'})
    amount = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right hide', 'style': 'text-align: right; width: 120px;'}))
    old_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))

    item_visible = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control-item item-amount'}))
    minimun_order = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control-item'}))
    description = forms.CharField(required=False,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control-item', 'style': 'text-align: left; width: 400px;'}))

    class Meta:
        model = OrderItem
        fields = ('line_number', 'ref_number', 'refer_line', 'reference_id', 'item_name', 'item_id', 'supplier_code',
                  'supplier_code_id', 'customer_po_no', 'code', 'category', 'location', 'wanted_date',
                  'schedule_date', 'uom', 'bkord_quantity', 'quantity', 'original_currency', 'original_price',
                  'stock_quantity', 'price', 'exchange_rate', 'amount', 'old_quantity', 'item_visible', 'minimun_order',
                  'description', 'delivery_quantity', 'receive_quantity', 'last_receive_date', 'last_delivery_date')

    def __init__(self, company_id, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.fields['location'].queryset = Location.objects.filter(is_hidden=False, company_id=company_id, is_active=1)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, company_id=company_id, is_active=1)


class OrderInfoForm(forms.ModelForm):
    customer = CodeChoiceField(queryset=Customer.objects.none(), required=False, empty_label='Select Customer',
                               widget=forms.Select(attrs={'class': 'form-control'}),
                               error_messages={'required': 'This field is required.'})
    customer_code = forms.CharField(required=False, widget=forms.TextInput(
                                attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(
                                attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier = CodeChoiceField(queryset=Supplier.objects.none(), required=False, empty_label='Select supplier',
                               widget=forms.Select(attrs={'class': 'form-control'}),
                               error_messages={'required': 'This field is required.'})
    transaction_code = CodeNameChoiceField1(queryset=None, empty_label=None, required=False,
                                            widget=forms.Select(attrs={'class': 'form-control', 'tabindex': '-1'}))
    debit_account = CodeNameChoiceField(queryset=None, empty_label=None, required=False,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    credit_account = CodeNameChoiceField(queryset=None, empty_label=None, required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    cost_center = CodeNameChoiceField(queryset=None, empty_label='---No Cost Center---', required=False,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    reference_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                     'tabindex': '0'}))
    transport_responsibility = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'tabindex': '0'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'True', 'tabindex': '-1'}))
    payment_mode = CodeChoiceField(queryset=PaymentCode.objects.none(), required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    payment_term = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    document_date = forms.CharField(required=True, help_text="Please use the following format: <em>DD-MM-YYYY</em>.",
                                    widget=forms.TextInput(attrs={'value': date.today(),
                                                                  'class': 'form-control form-control-inline input-medium default-date-picker',
                                                                  'required': 'required', 'tabindex': '0'}))
    document_date_fake = forms.CharField(required=True, help_text="Please use the following format: ",
                                         widget=forms.TextInput(
                                             attrs={'value': date.today(),
                                                    'class': 'form-control form-control-inline input-medium default-date-picker',
                                                    'required': 'required'}))
    due_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    invoice_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker'}))
    delivery_date = forms.CharField(required=False, help_text="Please use the following format: <em>DD-MM-YYYY</em>.",
                                    widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                                  'class': 'form-control form-control-inline input-medium default-date-picker'}))
    currency = CodeNameChoiceField(queryset=None, empty_label='Select Currency', required=False,
                                   widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    ship_from_code = CodeChoiceField(queryset=None, required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    ship_to_code = CodeChoiceField(queryset=None, required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    subtotal = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001', 'tabindex': '-1'}))
    tax = TaxChoiceField(queryset=None, empty_label='---No Tax---', required=False,
                         widget=forms.Select(attrs={'class': 'form-control'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001', 'tabindex': '-1'}))
    discount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'placeholder': '0.0', 'tabindex': '-1'}))
    total = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001', 'tabindex': '-1'}))
    exchange_rate_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'display: none', 'tabindex': '-1'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    tax_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Some Notes to customer'}),
        required=False)
    remark = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Some Notes for remark'}),
        required=False)
    footer = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Footer Text'}), required=False)

    class Meta:
        model = Order
        fields = ('debit_account', 'credit_account', 'cost_center', 'reference_number', 'transport_responsibility',
                  'document_number', 'payment_mode', 'payment_term', 'document_date', 'due_date', 'invoice_date', 'delivery_date',
                  'ship_from_code', 'ship_to_code', 'currency', 'subtotal', 'tax', 'tax_amount', 'discount',
                  'total', 'note', 'remark', 'footer', 'customer', 'customer_code', 'supplier_code', 'exchange_rate_date', 'exchange_rate',
                  'tax_exchange_rate', 'supplier')

    def __init__(self, company_id, order_type, *args, **kwargs):
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(OrderInfoForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

        if company_id:
            country_list = Country.objects.filter(is_hidden=False).order_by('code')

            self.fields['document_date'].initial = self.session_date if self.session_date else date.today()
            self.fields['ship_from_code'].queryset = country_list
            self.fields['ship_to_code'].queryset = country_list

            self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                       company_id=company_id).order_by('code')
            self.fields['customer'].queryset = Customer.objects.filter(is_hidden=False, is_active=True,
                                                                       company_id=company_id).order_by('code')
            if isinstance(instance, Order) and instance.customer_id:
                self.fields['customer_code'].initial = Customer.objects.get(pk=instance.customer_id).code
            if isinstance(instance, Order) and instance.supplier_id:
                self.fields['supplier_code'].initial = Supplier.objects.get(pk=instance.supplier_id).code
            account_list_filters = Account.objects.filter(
                is_hidden=0, company_id=company_id, is_active=1).order_by('account_segment', 'code')

            mydict = dict(ORDER_TYPE)
            name = list(mydict.keys())[list(mydict.values()).index(int(order_type))]
            transaction_code_list = TransactionCode.objects.filter(is_hidden=False, company_id=company_id, name__icontains=name)

            self.fields['cost_center'].queryset = CostCenters.objects.filter(is_hidden=0, is_active=1,
                                                                             company_id=company_id)
            if int(order_type) == dict(ORDER_TYPE)["SALES ORDER"] or \
                    int(order_type) == dict(ORDER_TYPE)["SALES INVOICE"]:
                self.fields['debit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_SALES)
                self.fields['credit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_RECEIVABLE)
                self.fields['transaction_code'].queryset = transaction_code_list.filter(
                    menu_type=int(TRN_CODE_TYPE_DICT['Sales Number File']))
            elif int(order_type) == dict(ORDER_TYPE)["PURCHASE ORDER"] or \
                    int(order_type) == dict(ORDER_TYPE)["PURCHASE INVOICE"]:
                self.fields['debit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_PURCHASES)
                self.fields['credit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_PAYABLE)
                self.fields['transaction_code'].queryset = transaction_code_list.filter(
                    menu_type=int(TRN_CODE_TYPE_DICT['Purchase Number File']))
            else:
                self.fields['debit_account'].queryset = account_list_filters
                self.fields['credit_account'].queryset = account_list_filters
                self.fields['transaction_code'].queryset = transaction_code_list

                group_list = []
                group_list_filter = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])
                for my_type in group_list_filter:

                    account_list_filter = account_list_filters.filter(account_group=my_type)
                    account_list = [[account.id, account.name] for account in account_list_filter]

                    new_type = [my_type.name, account_list]
                    if account_list.__len__() > 0:
                        group_list.append(new_type)

                self.fields['debit_account'].choices = group_list
                self.fields['credit_account'].choices = group_list

            if int(order_type) == dict(ORDER_TYPE)["SALES ORDER"] or \
                    int(order_type) == dict(ORDER_TYPE)["SALES INVOICE"]:
                self.fields['tax'].queryset = Tax.objects.filter(is_hidden=0, company_id=company_id,
                                                    tax_group__transaction_type=TAX_TRX_TYPES_DICT['Sales'])
            elif int(order_type) == dict(ORDER_TYPE)["PURCHASE ORDER"] or \
                    int(order_type) == dict(ORDER_TYPE)["PURCHASE INVOICE"]:
                self.fields['tax'].queryset = Tax.objects.filter(is_hidden=0, company_id=company_id,
                                                    tax_group__transaction_type=TAX_TRX_TYPES_DICT['Purchases'])
            self.fields['tax_amount'].initial = 0
            self.fields['discount'].initial = 0
            self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
            transaction_list = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
            self.fields['payment_mode'].initial = [(e.id, e.code) for e in transaction_list]
            self.fields['payment_mode'].queryset = transaction_list
            self.fields['subtotal'].initial = 0
            self.fields['total'].initial = 0


CREDIT_DEBIT_CHOICES = (('3', 'SDN - Sale Debit Note'), ('4', 'SCN - Sale Credit Note'),)


class SaleCreditDebitNoteForm(OrderInfoForm):
    document_type = forms.ChoiceField(required=False, choices=CREDIT_DEBIT_CHOICES,
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta(OrderInfoForm.Meta):
        fields = OrderInfoForm.Meta.fields + ('document_type',)


class GoodReceiveInfoForm(forms.ModelForm):
    supplier = CodeChoiceField(queryset=Supplier.objects.none(), required=False, empty_label='Select supplier',
                               widget=forms.Select(attrs={'class': 'form-control'}),
                               error_messages={'required': 'This field is required.'})
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(
                                attrs={'class': 'form-control-item', 'style': 'display: none'}))
    transaction_code = CodeNameChoiceField1(queryset=None, empty_label=None, required=True,
                                            widget=forms.Select(attrs={'class': 'form-control', 'tabindex': '-1'}))
    debit_account = CodeNameChoiceField(queryset=None, empty_label=None, required=False,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    credit_account = CodeNameChoiceField(queryset=None, empty_label=None, required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    cost_center = CodeNameChoiceField(queryset=None, empty_label='---No Cost Center---', required=False,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    reference_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    transport_responsibility = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    document_number = forms.CharField(required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    term = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'display: none'}))
    document_date = forms.CharField(required=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.",
                                    widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                                  'class': 'form-control form-control-inline input-medium default-date-picker',
                                                                  'required': 'required'}))
    document_type = forms.ChoiceField(choices=GR_DOC_TYPE, required=True,
                                      widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    due_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    invoice_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker'}))
    delivery_date = forms.CharField(required=False, help_text="Please use the following format: <em>YYYY-MM-DD</em>.",
                                    widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                                  'class': 'form-control form-control-inline input-medium default-date-picker'}))
    currency = CodeNameChoiceField(queryset=None, empty_label=None, required=True,
                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                   error_messages={'required': 'This field is required.'})
    ship_from = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ship_to = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    subtotal = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001', 'tabindex': '-1'}))
    tax = TaxChoiceField(queryset=None, empty_label='---No Tax---', required=False,
                         widget=forms.Select(attrs={'class': 'form-control'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001', 'tabindex': '-1'}))
    discount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'placeholder': '0.0'}))
    total = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Some Notes to customer'}),
        required=False)
    remark = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Some Notes for remark'}),
        required=False)
    footer = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Footer Text'}), required=False)
    exchange_rate_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'display: none'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    tax_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    supllier_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))

    class Meta:
        model = Order
        fields = ('debit_account', 'credit_account', 'cost_center', 'reference_number', 'transport_responsibility',
                  'document_number', 'term', 'document_date', 'document_type', 'due_date', 'invoice_date',
                  'delivery_date', 'ship_from', 'supplier_code',
                  'ship_to', 'currency', 'subtotal', 'tax', 'tax_amount', 'discount', 'total', 'note', 'remark',
                  'footer', 'supplier', 'exchange_rate_date', 'exchange_rate', 'tax_exchange_rate',
                  'supllier_exchange_rate')

    def __init__(self, company_id, order_type, *args, **kwargs):
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(GoodReceiveInfoForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        filter_transaction_code = TransactionCode.objects.filter(is_hidden=False, company_id=company_id)
        if company_id:
            # Good Receive
            if isinstance(instance, Order) and instance.supplier_id:
                self.fields['supplier_code'].initial = Supplier.objects.get(pk=instance.supplier_id).code
            filter_transaction_code = filter_transaction_code.filter(
                name="PURCHASE INVOICE",
                menu_type=int(TRN_CODE_TYPE_DICT['Purchase Number File']))

            self.fields['document_date'].initial = self.session_date if self.session_date else datetime.datetime.now()
            self.fields['transaction_code'].queryset = filter_transaction_code
            self.fields['transaction_code'].initial = filter_transaction_code.last().id
            self.fields['cost_center'].queryset = CostCenters.objects.filter(is_hidden=0, is_active=1,
                                                                             company_id=company_id)
            self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                       company_id=company_id).order_by('code')
            account_list_filters = Account.objects.filter(
                is_hidden=0, company_id=company_id, is_active=1).order_by('account_segment', 'code')

            if int(order_type) == dict(ORDER_TYPE)["SALES ORDER"] or int(order_type) == dict(ORDER_TYPE)[
                    "SALES INVOICE"]:
                self.fields['debit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_SALES)
                self.fields['credit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_RECEIVABLE)
            elif int(order_type) == dict(ORDER_TYPE)["PURCHASE ORDER"] or int(order_type) == dict(ORDER_TYPE)[
                    "PURCHASE INVOICE"]:
                self.fields['debit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_PURCHASES)
                self.fields['credit_account'].queryset = account_list_filters.filter(code=s.ACCOUNT_PAYABLE)
            else:
                self.fields['debit_account'].queryset = account_list_filters
                self.fields['credit_account'].queryset = account_list_filters

                group_list = []
                group_list_filter = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])

                for my_type in group_list_filter:
                    account_list = []
                    account_list_filter = account_list_filters.filter(account_group=my_type)
                    for account in account_list_filter:
                        account_list.append([account.id, account.name])

                    new_type = [my_type.name, account_list]
                    if account_list.__len__() > 0:
                        group_list.append(new_type)

                self.fields['debit_account'].choices = group_list
                self.fields['credit_account'].choices = group_list

            self.fields['tax'].queryset = Tax.objects.filter(is_hidden=0, company_id=company_id,
                                                tax_group__transaction_type=TAX_TRX_TYPES_DICT['Purchases'])
            self.fields['document_type'].initial = GR_DOC_TYPE_DICT['D/O and Invoice']
            self.fields['tax_amount'].initial = 0
            self.fields['discount'].initial = 0
            self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
            self.fields['subtotal'].initial = 0
            self.fields['total'].initial = 0


class OrderDeliveryForm(forms.ModelForm):
    delivery = CodeChoiceField(queryset=None, required=False, empty_label='No Select',
                               widget=forms.Select(attrs={'class': 'form-control'}))
    name = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    attention = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    note_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    contact = NameChoiceField(queryset=None, required=False, empty_label='No Select',
                              widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = OrderDelivery
        fields = ('delivery', 'name', 'attention', 'phone', 'address', 'note_1')

    def __init__(self, company_id, *args, **kwargs):
        super(OrderDeliveryForm, self).__init__(*args, **kwargs)
        if company_id:
            self.fields['delivery'].queryset = Delivery.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

        instance = kwargs.get('instance', None)
        contact = kwargs.get('contact', None)

        if isinstance(instance, OrderDelivery):
            self.fields['name'].initial = instance.name
            self.fields['attention'].initial = instance.contact
            self.fields['phone'].initial = instance.phone
            self.fields['address'].initial = instance.address
            self.fields['note_1'].initial = instance.note_1
        elif isinstance(instance, Contact):
            self.fields['contact'].initial = instance.id
            self.fields['name'].initial = instance.company_name
            self.fields['attention'].initial = instance.name
            self.fields['phone'].initial = instance.phone
            self.fields['address'].initial = instance.address
            self.fields['note_1'].initial = instance.note
        else:
            self.fields['name'].initial = ""
            self.fields['attention'].initial = ""
            self.fields['phone'].initial = ""
            self.fields['address'].initial = ""
            self.fields['note_1'].initial = ""


class PaymentForm(forms.ModelForm):
    currency = CodeNameChoiceField(queryset=None, empty_label='---Select---', required=True,
                                   widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    debit_account = CodeNameChoiceField(queryset=None, empty_label='---Select---', required=True,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    credit_account = CodeNameChoiceField(queryset=None, empty_label='---Select---', required=True,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    method = CodeNameChoiceField(queryset=None, empty_label='---Select---', required=False,
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    transaction_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd'}))
    amount = forms.CharField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'step': '0.000001', 'required': 'required'}))
    remark = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))
    number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Transaction
        fields = ('method', 'transaction_date', 'amount', 'currency', 'remark', 'number')

    def __init__(self, company_id, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        if company_id:
            account_list_qs = Account.objects.filter(
                is_hidden=0, is_active=1, company_id=company_id).order_by('account_segment', 'code')
            self.fields['debit_account'].queryset = account_list_qs.filter(type__is_debit=1)
            self.fields['credit_account'].queryset = account_list_qs.filter(type__is_credit=1)
            self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
            self.fields['method'].queryset = TransactionMethod.objects.filter(is_hidden=0, company_id=company_id)

            debit_group_list = []
            credit_group_list = []
            group_list_filter = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])
            for my_type in group_list_filter:
                debit_account = []
                credit_account = []
                account_list_filter = account_list_qs.filter(account_group=my_type)
                for account in account_list_filter:
                    if account.type.is_debit == 1:
                        debit_account.append([account.id, account.name])
                    if account.type.is_credit == 1:
                        credit_account.append([account.id, account.name])

                if debit_account.__len__() > 0:
                    debit_account_list = [my_type.name, debit_account]
                    debit_group_list.append(debit_account_list)
                if credit_account.__len__() > 0:
                    credit_account_list = [my_type.name, credit_account]
                    credit_group_list.append(credit_account_list)
            if debit_group_list:
                self.fields['debit_account'].choices = debit_group_list
            if credit_group_list:
                self.fields['credit_account'].choices = credit_group_list


class DOInvoiceForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    line_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    refer_line = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    ref_number = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_name = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_id = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}),
                              error_messages={'required': 'This field is required.'})
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier_code_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    customer_po_no = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'width: 200px;', 'style': 'display: none'}))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    category = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    location = CodeChoiceField(queryset=None, empty_label=None, required=False,
                               widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 150px'}))
    wanted_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker', 'style': 'width: 100px'}))
    schedule_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker', 'style': 'width: 100px'}))
    uom = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    quantity_do = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control-item numeric_qty', 'style': 'text-align: right; width: 140px;'}),
        error_messages={'required': 'This field is required.'})
    original_currency = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none;'}))
    currency_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    original_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control-item'}))
    order_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none;', 'step': '0.1'}))
    delivery_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none;', 'step': '0.1'}))
    price = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control-item numeric_price', 'style': 'text-align: right; width: 140px;'}),
        error_messages={'required': 'This field is required.'})
    exchange_rate = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'readonly': 'readonly',
               'style': 'text-align: right; width: 80px;', 'step': '0.000000001'}),
        error_messages={'required': 'This field is required.'})
    amount = forms.DecimalField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'readonly': 'readonly',
               'style': 'text-align: right; width: 100px; display: none;', 'step': '0.000001', 'min': '0'}))
    origin_country_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control input-sm', 'style': 'width: 100px; text-align: left;', 'style': 'display: none'}))
    origin_country_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none ; text-align: left;'}))
    carton_no = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: left; width: 100px;'}))
    carton_total = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: right; width: 100px;'}))
    pallet_no = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: left; width: 100px;'}))
    net_weight = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'style': 'text-align: right; width: 100px;'}))
    gross_weight = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'style': 'text-align: right; width: 100px;'}))
    m3_number = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'style': 'text-align: right; width: 100px;'}))
    remark = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'text-align: left;'}))
    location_item_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: right; width: 100px;', 'step': '0.1'}))
    reference_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control-item'}))

    class Meta:
        model = OrderItem
        fields = ('id',
            'line_number', 'refer_line', 'ref_number', 'item_name', 'item_id', 'supplier_code', 'supplier_code_id',
            'customer_po_no', 'code', 'category', 'location', 'wanted_date', 'schedule_date', 'uom', 'quantity_do',
            'original_currency', 'currency_id', 'original_price', 'order_quantity', 'delivery_quantity', 'price',
            'exchange_rate', 'amount', 'origin_country_code', 'origin_country_id', 'carton_no', 'carton_total',
            'pallet_no', 'net_weight', 'gross_weight', 'm3_number', 'remark', 'reference_id')

    def __init__(self, company_id, *args, **kwargs):
        super(DOInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(is_hidden=False, company_id=company_id, is_active=1)


class GoodReceiveAddItemForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    line_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    refer_line = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}),
                                 error_messages={'required': 'This field is required.'})
    ref_number = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_name = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_id = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}),
                              error_messages={'required': 'This field is required.'})
    reference_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control-item'}))
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier_code_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    customer_po_no = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'width: 240px;', 'style': 'display: none'}))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    category = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    location = CodeChoiceField(queryset=None, empty_label=None, required=False,
                               widget=forms.Select(
                                   attrs={'class': 'form-control', 'style': 'width: 110px; text-align: left;'}))
    wanted_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker', 'style': 'width: auto'}))
    schedule_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker', 'style': 'width: auto'}))
    uom = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    quantity = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control-item numeric_qty', 'style': 'text-align: right; width: 140px;'}),
        error_messages={'required': 'This field is required.'})
    receive_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: right; display: none;', 'min': '0', 'step': '0.1'}),
        error_messages={'required': 'This field is required.'})
    original_currency = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    currency_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    original_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control-item'}))
    stock_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))
    price = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control-item numeric_price', 'style': 'text-align: right; width: 140px;'}),
        error_messages={'required': 'This field is required.'})
    exchange_rate = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'readonly': 'readonly',
               'style': 'text-align: right; width: 80px;', 'step': '0.000000001', 'min': '0'}),
        error_messages={'required': 'This field is required.'})
    amount = forms.DecimalField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right',
               'style': 'text-align: right; width: 130px; display: none;', 'step': '0.000001', 'min': '0'}))
    old_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))

    item_visible = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control-item item-amount'}))

    minimun_order = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control-item'}))
    order_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none', 'step': '0.1'}))

    class Meta:
        model = OrderItem
        fields = ('id',
            'line_number', 'ref_number', 'refer_line', 'item_name', 'item_id', 'supplier_code', 'supplier_code_id',
            'customer_po_no', 'reference_id', 'code', 'category', 'wanted_date', 'schedule_date', 'uom', 'quantity',
            'original_currency', 'original_price', 'receive_quantity', 'order_quantity', 'stock_quantity', 'price',
            'exchange_rate', 'amount', 'old_quantity', 'item_visible', 'minimun_order')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(GoodReceiveAddItemForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(is_hidden=False, company_id=self.company_id,
                                                                   is_active=1)


class PurchaseCrDbNoteInfoForm(forms.ModelForm):
    transaction_code = CodeNameChoiceField1(queryset=None, empty_label=None, required=False,
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    currency = CodeChoiceField(queryset=None, required=False, empty_label=None,
                               widget=forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    tax_currency = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    document_date = forms.CharField(required=False, help_text="Please use the following format: <em>YYYY-MM-DD</em>.",
                                    widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                                  'class': 'form-control form-control-inline input-medium default-date-picker',
                                                                  'required': 'required'}))
    tax_exchange_rate = forms.DecimalField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'step': '0.000001'}))
    tax_code = TaxChoiceField(queryset=None, empty_label='---No Tax---', required=False,
                              widget=forms.Select(attrs={'class': 'form-control'}))
    cost_center = CodeNameChoiceField(queryset=None, empty_label='---No Cost Center---', required=False,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    supplier_exchange = forms.DecimalField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'step': '0.000001'}))
    remark = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Some Notes for remark'}),
        required=False)
    debit_account = CodeNameChoiceField(queryset=None, empty_label=None, required=False,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    credit_account = CodeNameChoiceField(queryset=None, empty_label=None, required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    # qty_or_amt = forms.ChoiceField(choices=QTY_CHOICES, required=True,
    #                                      widget=forms.Select(attrs={'class': 'form-control'}))
    subtotal = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001'}))
    total = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'step': '0.000001'}))
    tax = TaxChoiceField(queryset=None, empty_label='---No Tax---', required=False,
                         widget=forms.Select(attrs={'class': 'form-control'}))
    supplier = CodeChoiceField(queryset=Supplier.objects.none(), required=False, empty_label='Select supplier',
                               widget=forms.Select(attrs={'class': 'form-control'}),
                               error_messages={'required': 'This field is required.'})

    class Meta:
        model = Order
        fields = (
            'debit_account', 'credit_account', 'cost_center', 'supplier_exchange', 'tax_code', 'tax_exchange_rate',
            'document_number', 'document_date', 'currency', 'tax_currency', 'supplier_code', 'transaction_code',
            'subtotal', 'tax_amount', 'total', 'remark', 'tax', 'supplier')

    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id')
        super(PurchaseCrDbNoteInfoForm, self).__init__(*args, **kwargs)
        account_list_qs = Account.objects.filter(
            is_hidden=0, is_active=1, company_id=company_id).order_by('account_segment', 'code')
        self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=company_id).order_by('code')
        self.fields['tax'].queryset = Tax.objects.filter(is_hidden=0, company_id=company_id)
        self.fields['debit_account'].queryset = account_list_qs.filter(code=s.ACCOUNT_PURCHASES)
        self.fields['credit_account'].queryset = account_list_qs.filter(code=s.ACCOUNT_PAYABLE)
        self.fields['cost_center'].queryset = CostCenters.objects.filter(is_hidden=0, is_active=1,
                                                                         company_id=company_id)
        self.fields['tax_amount'].initial = 0
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['subtotal'].initial = 0
        self.fields['total'].initial = 0

        filter_transaction_code = TransactionCode.objects.filter(is_hidden=False, company_id=company_id,
                                                                 menu_type=int(TRN_CODE_TYPE_DICT['Purchase Number File']))
        # Purchase Debit/Credit Note
        filter_transaction_code = filter_transaction_code.filter(
            Q(name='PURCHASE CREDIT NOTE') | Q(name='PURCHASE DEBIT NOTE'))

        self.fields['transaction_code'].queryset = filter_transaction_code


class PurchaseCrDbNoteAddItem(forms.ModelForm):
    line_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    location = CodeChoiceField(queryset=None, empty_label=None, required=False,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    customer_po_no = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'width: 100px; display: none'}))
    item_code = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_id = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}),
                              error_messages={'required': 'This field is required.'})
    category = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    uom = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    quantity = forms.DecimalField(required=True, min_value=0, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'text-align: right; width: 140px!important;', 'min': '0',
               'step': '0.1'}),
        error_messages={'required': 'This field is required.'})
    price = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'readonly': 'readonly',
               'style': 'text-align: right; width: 100px!important;', 'step': '0.000001', 'min': '0'}),
        error_messages={'required': 'This field is required.'})
    amount = forms.DecimalField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control-item text-right', 'readonly': 'readonly',
               'style': 'text-align: right; width: 100px!important;', 'step': '0.000001', 'min': '0'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100px;'}),
                                  required=False)
    reference_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))

    order_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none;', 'step': '0.1'}))
    receive_quantity = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control-item', 'style': 'display: none;', 'step': '0.1'}))
    refer_line = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    ref_number = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    item_name = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))
    supplier_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control-item', 'style': 'display: none'}))

    class Meta:
        model = OrderItem
        fields = (
            'line_number', 'customer_po_no', 'category', 'quantity', 'price', 'order_quantity', 'receive_quantity',
            'location', 'item_code', 'item_id', 'uom', 'amount', 'description', 'reference_id', 'refer_line',
            'ref_number', 'item_name', 'supplier_code', 'supplier_id')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(PurchaseCrDbNoteAddItem, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(is_hidden=False, company_id=self.company_id,
                                                                   is_active=1)
