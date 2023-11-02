import datetime
from decimal import Decimal

from django import forms
from django.forms import ModelChoiceField

from accounting.models import Journal, PaymentCode, DOCUMENT_TYPES, \
    Batch, FiscalCalendar, RecurringEntry, Schedule, AROptions, APOptions, RecurringBatch
from accounts.models import Account, AccountSet
from banks.models import Bank
from currencies.models import Currency, ExchangeRate
from customers.models import Customer
from suppliers.models import Supplier
from taxes.models import Tax
from transactions.models import Transaction
from utilities.common import round_number
from utilities.constants import PAYMENT_TYPE, PAYMENT_TRANSACTION_TYPES, RECEIPT_TRANSACTION_TYPES, SOURCE_APPLICATION, \
    PAYMENT_TRANSACTION_TYPES_DICT, RECEIPT_TRANSACTION_TYPES_DICT, ACCOUNT_SET_TYPE_DICT, TAX_TRX_TYPES_DICT, RECURRING_ENTRY_MODE, \
    RECUR_EXCHANGE_RATE_TYPE, RECURRING_PERIOD, WEEKDAYS, MOTNHDATES, WEEK_NUMBER, MONTH_NAMES, \
    RECURRING_PERIOD_DICT, AP_INV_DOCUMENT_TYPES, AR_INV_DOCUMENT_TYPES, PAYMENT_CODE_TYPE_DICT


class NameModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class CodeNnameModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class RateModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.rate


class ARInvoiceInfoForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control  text-right', 'readonly': 'readonly',
                                                         'tabindex': '-1'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    customer = CodeModelChoiceField(queryset=Customer.objects.none(), required=True, empty_label='Select Customer',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    customer_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required', 'readonly': 'readonly', 'tabindex': '-1'}))
    customer_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(), required=True,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    account_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled sended', 'tabindex': '-1'}))
    document_number = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled readonly', 'required': 'required'}))
    document_amount = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended numeric_amount', 'required': 'required', 'readonly': 'readonly'}))
    document_type = forms.CharField(required=True,
                                    widget=forms.Select(choices=AR_INV_DOCUMENT_TYPES, attrs={'class': 'form-control sended'}))
    po_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    order_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    document_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    posting_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}), initial=0)
    tax = NameModelChoiceField(queryset=None, required=False, empty_label=None,
                               widget=forms.Select(attrs={'class': 'form-control sended'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    total_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required',
                                               'tabindex': '-1'}))
    currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}))
    tax_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended numeric_rate', 'required': 'required'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended numeric_rate', 'required': 'required'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                            widget=forms.Select(
                                                attrs={'class': 'form-control no-select disabled hidden'}))

    class Meta:
        model = Journal
        fields = (
            'code', 'name', 'customer', 'customer_name', 'customer_code', 'account_set', 'is_manual_doc',
            'document_number',
            'document_amount', 'document_type', 'po_number', 'order_number', 'document_date', 'posting_date', 'amount',
            'tax', 'tax_amount', 'total_amount', 'currency', 'exchange_rate', 'exchange_rate_fk', 'tax_exchange_rate')

    def __init__(self, journal_id=None, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(ARInvoiceInfoForm, self).__init__(*args, **kwargs)
        if self.session_date:
            self.fields['document_date'].initial = self.session_date
            self.fields['posting_date'].initial = self.session_date
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=0,
            company_id=self.company_id,
            tax_group__company_id=self.company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Sales']))
        self.fields['exchange_rate_fk'].queryset = ExchangeRate.objects.filter(is_hidden=False,
                                                                               company_id=self.company_id,
                                                                               flag='ACCOUNTING')
        self.fields['customer'].queryset = Customer.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AR Account Set']
                                                                        ).order_by('code')
        if journal_id:
            try:
                journal = Journal.objects.get(pk=journal_id)
                customer = Customer.objects.get(pk=journal.customer_id)
                if journal.tax_exchange_rate == 0:
                    self.initial['tax_exchange_rate'] = Decimal('0')
                if journal.currency.is_decimal:
                    self.initial['document_amount'] = round_number(journal.document_amount, 2)
                    self.initial['amount'] = round_number(journal.amount, 2)
                    self.initial['tax_amount'] = round_number(journal.tax_amount, 2)
                    self.initial['total_amount'] = round_number(journal.total_amount, 2)
                else:
                    self.initial['document_amount'] = round_number(journal.document_amount, 0)
                    self.initial['amount'] = round_number(journal.amount, 0)
                    self.initial['tax_amount'] = round_number(journal.tax_amount, 0)
                    self.initial['total_amount'] = round_number(journal.total_amount, 0)
                self.fields['customer'].initial = customer.id if customer else ''
                self.fields['customer_name'].initial = customer.name if customer else ''
                self.fields['customer_code'].initial = customer.code if customer else ''
                if journal.account_set:
                    account_set = AccountSet.objects.get(pk=journal.account_set_id)
                    if account_set:
                        self.fields['account_set'].initial = account_set.id if account_set else ''
                        self.fields['account_code'].initial = account_set.code if account_set else ''
                if customer and customer.currency:
                    currency = Currency.objects.get(id=customer.currency_id)
                    self.fields['currency_code'].initial = currency.code if currency else ''
                    self.fields['currency'].initial = currency.id if currency else ''
                    self.fields['account_set'].queryset = \
                        AccountSet.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id,
                                                  type=ACCOUNT_SET_TYPE_DICT['AR Account Set'],
                                                  currency_id=currency.id).order_by('code')
            except:
                self.fields['customer'].initial = ''
                self.fields['customer_name'].initial = ''
                self.fields['customer_code'].initial = ''
                self.fields['account_set'].initial = ''
                self.fields['account_code'].initial = ''
                self.fields['currency_code'].initial = ''
                self.fields['currency'].initial = ''
        else:
            self.initial['document_amount'] = Decimal('0.000000')
            self.initial['amount'] = Decimal('0.000000')
            self.initial['tax_amount'] = Decimal('0.000000')
            self.initial['total_amount'] = Decimal('0.000000')


class APInvoiceInfoForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    order_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), required=True, empty_label='Select Supplier',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    supplier_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly', 'tabindex': '-1'}))
    supplier_code = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(), required=True,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    account_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    document_number = forms.CharField(required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control sended disabled readonly',
                                                                    'required': 'required'}))
    document_amount = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended numeric_amount', 'required': 'required', 'readonly': 'readonly'}))
    document_type = forms.ChoiceField(choices=AP_INV_DOCUMENT_TYPES, required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    po_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    order_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    document_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    posting_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}), initial=0)
    tax = NameModelChoiceField(queryset=None, required=False, empty_label=None,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    total_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required', 'tabindex': '-1'}))
    currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled sended', 'tabindex': '-1'}))
    tax_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right numeric_rate', 'required': 'required'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right numeric_rate', 'required': 'required'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                            widget=forms.Select(
                                                attrs={'class': 'form-control no-select disabled hidden'}))

    class Meta:
        model = Journal
        fields = ('code', 'name', 'supplier', 'supplier_name', 'supplier_code', 'account_set', 'document_number',
                  'document_amount', 'document_type', 'po_number', 'order_number', 'order_id', 'is_manual_doc',
                  'document_date', 'posting_date', 'amount', 'tax', 'tax_amount', 'total_amount', 'currency',
                  'exchange_rate', 'exchange_rate_fk', 'tax_exchange_rate')

    def __init__(self, journal_id=None, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(APInvoiceInfoForm, self).__init__(*args, **kwargs)

        if self.session_date:
            self.fields['document_date'].initial = self.session_date
            self.fields['posting_date'].initial = self.session_date
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=0,
            company_id=self.company_id,
            tax_group__company_id=self.company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
        self.fields['exchange_rate_fk'].queryset = ExchangeRate.objects.filter(is_hidden=False,
                                                                               company_id=self.company_id,
                                                                               flag='ACCOUNTING')
        self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AP Account Set']
                                                                        ).order_by('code')
        if journal_id:
            try:
                journal = Journal.objects.get(pk=journal_id)
                supplier = Supplier.objects.get(pk=journal.supplier_id)
                if journal.tax_exchange_rate == 0:
                    self.initial['tax_exchange_rate'] = Decimal('0')
                if journal.currency.is_decimal:
                    self.initial['document_amount'] = round_number(journal.document_amount, 2)
                    self.initial['amount'] = round_number(journal.amount, 2)
                    self.initial['tax_amount'] = round_number(journal.tax_amount, 2)
                    self.initial['total_amount'] = round_number(journal.total_amount, 2)
                else:
                    self.initial['document_amount'] = round_number(journal.document_amount, 0)
                    self.initial['amount'] = round_number(journal.amount, 0)
                    self.initial['tax_amount'] = round_number(journal.tax_amount, 0)
                    self.initial['total_amount'] = round_number(journal.total_amount, 0)
                self.fields['supplier'].initial = supplier.id if supplier else ''
                self.fields['supplier_name'].initial = supplier.name if supplier else ''
                self.fields['supplier_code'].initial = supplier.code if supplier else ''
                if supplier and supplier.currency:
                    currency = Currency.objects.get(id=supplier.currency_id)
                    self.fields['currency_code'].initial = currency.code if currency else ''
                    self.fields['currency'].initial = currency.id if currency else ''
                    self.fields['account_set'].queryset = \
                        AccountSet.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id,
                                                  type=ACCOUNT_SET_TYPE_DICT['AP Account Set'],
                                                  currency_id=currency.id).order_by('code')
                if journal.account_set:
                    account_set = AccountSet.objects.get(pk=journal.account_set_id)
                    if account_set:
                        self.fields['account_set'].initial = account_set.id if account_set else ''
                        self.fields['account_code'].initial = account_set.code if account_set else ''
            except:
                self.fields['supplier'].initial = ''
                self.fields['supplier_name'].initial = ''
                self.fields['supplier_code'].initial = ''
                self.fields['account_set'].initial = ''
                self.fields['account_code'].initial = ''
                self.fields['currency_code'].initial = ''
                self.fields['currency'].initial = ''
        else:
            self.initial['document_amount'] = Decimal('0.000000')
            self.initial['amount'] = Decimal('0.000000')
            self.initial['tax_amount'] = Decimal('0.000000')
            self.initial['total_amount'] = Decimal('0.000000')


class PaymentCodeForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
                           error_messages={'required': 'This field is required.'})
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
                           error_messages={'required': 'This field is required.'})
    update_date = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%d-%m-%Y'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'readonly': 'readonly'}))
    payment_type = forms.ChoiceField(choices=PAYMENT_TYPE, required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'styled'}))

    class Meta:
        model = PaymentCode
        fields = ('code', 'name', 'update_date', 'payment_type', 'is_active')


class PaymentARForm(forms.ModelForm):
    journal = forms.CharField(required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    journal_total_amount = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}))
    bank = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    bank_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    currency = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    currency_code = forms.CharField(required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    transaction_type = forms.CharField(required=True,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    payment_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd'}))
    posting_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd'}))
    supplier = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    supplier_code = forms.CharField(required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    supplier_name = forms.CharField(required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    supplier_currency = forms.CharField(required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    payment_code = forms.CharField(required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    payment_code_code = forms.CharField(required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    payment_check_number = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}))
    document_number = forms.CharField(required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))

    payment_amount = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'tabindex': '-1'}))
    vendor_amount = forms.CharField(required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    advance_credit = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))

    class Meta:
        model = Account
        fields = ('bank', 'currency', 'code', 'name', 'transaction_type', 'payment_date', 'posting_date', 'supplier',
                  'payment_code', 'payment_check_number', 'document_number')

    def __init__(self, payment_id=None, *args, **kwargs):
        company_id = kwargs.pop('company_id')
        super(PaymentARForm, self).__init__(*args, **kwargs)
        if payment_id:
            try:
                payment = Account.objects.get(pk=payment_id)
                # Load Bank
                bank = Bank.objects.get(pk=payment.bank_id)
                self.fields['bank'] = bank.id if bank else ''
                self.fields['bank_name'] = bank.name if bank else ''
                # Load Currency
                currency = Currency.objects.get(pk=payment.payment_currency_id)
                self.fields['currency'] = currency.id if currency else ''
                self.fields['currency_code'] = currency.code if currency else ''
                # Load Supplier
                supplier = Supplier.objects.get(pk=payment.supplier_id)
                self.fields['supplier'] = supplier.id if supplier else ''
                self.fields['supplier_code'] = supplier.code if supplier else ''
                self.fields['supplier_name'] = supplier.name if supplier else ''
                self.fields['supplier_currency'].initial = supplier.currency.code if supplier else ''
                # Load PaymentCode
                payment_code = PaymentCode.objects.get(pk=payment.payment_code_id if payment.payment_code_id else None)
                self.fields['payment_code'] = payment_code.id if payment_code else ''
                self.fields['payment_code_code'] = payment_code.code if payment_code else ''
            except:
                self.fields['bank'] = ''
                self.fields['bank_name'] = ''
                self.fields['currency'] = ''
                self.fields['currency_code'] = ''
                self.fields['supplier'] = ''
                self.fields['supplier_code'] = ''
                self.fields['supplier_name'] = ''
                self.fields['supplier_currency'] = ''
                self.fields['payment_code'] = ''
                self.fields['payment_code_code'] = ''


class JournalGLForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(
                               attrs={'id': 'trxnum', 'class': 'form-control  text-center', 'readonly': 'readonly', 'tabindex': '-1'}))
    name = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata'}))
    # source_type = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={'id': 'txtsource_code', 'class': 'form-control fieldset hdrdata', 'required': 'required'}))
    document_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'id': 'document_date',
               'required': 'required',
               'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker fieldset hdrdata',
               'data-date-format': 'yyyy-mm-dd'}))

    class Meta:
        model = Journal
        fields = (
            'code', 'name', 'document_date',
        )

    def __init__(self, journal_id=None, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(JournalGLForm, self).__init__(*args, **kwargs)

        if self.session_date:
            self.fields['document_date'].initial = self.session_date


class ARReceiptInfoForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true',
                                                         'tabindex': '-1'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    bank = CodeModelChoiceField(queryset=Bank.objects.none(), required=True,
                                widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required',
                                               'tabindex': '-1'}))
    posting_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    transaction_type = forms.ChoiceField(choices=RECEIPT_TRANSACTION_TYPES, required=True,
                                         widget=forms.Select(attrs={'class': 'form-control sended'}))
    document_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    customer = CodeModelChoiceField(queryset=Customer.objects.none(), required=False, empty_label='Select Customer',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    customer_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true',
                                                                  'tabindex': '-1'}))
    customer_currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                             widget=forms.Select(attrs={'class': 'form-control no-select disabled',
                                                                        'tabindex': '-1'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=False,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control sended'}))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=True, empty_label='Select Payment',
                                        widget=forms.Select(
                                            attrs={'class': 'form-control sended', 'required': 'required'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control sended disabled',
                                                                    'readonly': 'true'}))
    reference = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    invoice_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    amount = forms.DecimalField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true', 'tabindex': '-1'}))
    tax_amount = forms.DecimalField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true', 'tabindex': '-1'}))
    total_amount = forms.DecimalField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true', 'tabindex': '-1'}))
    payment_check_number = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled', 'tabindex': '-1'}))
    original_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled text-right', 'type': 'text', 'readonly': 'true', 'tabindex': '-1'}))
    payment_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended text-right numeric_amount', 'type': 'text'}))
    receipt_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled text-right', 'type': 'text', 'readonly': 'true', 'tabindex': '-1'}))
    customer_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled text-right', 'type': 'text', 'readonly': 'true', 'tabindex': '-1'}))
    original_currency_id = forms.IntegerField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_currency_id = forms.IntegerField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    orig_exch_rate = forms.DecimalField(required=False, decimal_places=10, widget=forms.TextInput(
        attrs={'class': 'form-control text-right hidden'}))
    tax_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended hidden'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                        widget=forms.Select(
                                            attrs={'class': 'form-control no-select disabled hidden'}))

    class Meta:
        model = Journal
        fields = ('code', 'name', 'bank', 'currency', 'posting_date', 'transaction_type', 'document_date', 'customer',
                  'customer_name', 'customer_currency', 'account_set', 'payment_code', 'document_number', 'reference',
                  'invoice_number', 'amount', 'tax_amount', 'total_amount', 'payment_check_number', 'is_manual_doc',
                  'original_amount', 'payment_amount', 'original_currency_id', 'payment_currency_id', 'orig_exch_rate',
                  'receipt_unapplied', 'customer_unapplied', 'exchange_rate', 'exchange_rate_fk', 'tax_exchange_rate')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        self.journal_id = kwargs.pop('journal_id') if 'journal_id' in kwargs else None
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(ARReceiptInfoForm, self).__init__(*args, **kwargs)
        currency_list = Currency.objects.filter(is_hidden=0)
        if self.session_date:
            self.fields['document_date'].initial = self.session_date
            self.fields['posting_date'].initial = self.session_date
        self.fields['currency'].queryset = currency_list
        self.fields['customer_currency'].queryset = currency_list
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=self.company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
        self.fields['bank'].queryset = Bank.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id)
        self.fields['customer'].queryset = Customer.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AR Account Set']
                                                                        ).order_by('code')
        if self.instance.id:
            if self.instance.tax_exchange_rate == 0:
                self.fields['tax_exchange_rate'].initial = Decimal('1.0')
            if self.instance.currency.is_decimal:
                self.fields['amount'].initial = round_number(self.instance.amount, 2) if self.instance.amount else 0.00
                self.fields['tax_amount'].initial = round_number(self.instance.tax_amount, 2) if self.instance.tax_amount else 0.00
                self.fields['total_amount'].initial = round_number(self.instance.total_amount, 2) if self.instance.total_amount else 0.00
            else:
                self.fields['amount'].initial = round_number(self.instance.amount, 0) if self.instance.amount else 0
                self.fields['tax_amount'].initial = round_number(self.instance.tax_amount, 0) if self.instance.tax_amount else 0
                self.fields['total_amount'].initial = round_number(
                    self.instance.total_amount, 0) if self.instance.total_amount else 0
        if self.journal_id and self.journal_id != 0:
            try:
                journal = Journal.objects.get(pk=self.journal_id)
                if journal.tax_exchange_rate == 0:
                    self.initial['tax_exchange_rate'] = Decimal('1.0')
                if journal.currency.is_decimal:
                    self.initial['amount'] = round_number(journal.amount, 2)
                    self.initial['tax_amount'] = round_number(journal.tax_amount, 2)
                    self.initial['total_amount'] = round_number(journal.total_amount, 2)
                else:
                    self.initial['amount'] = round_number(journal.amount, 0)
                    self.initial['tax_amount'] = round_number(journal.tax_amount, 0)
                    self.initial['total_amount'] = round_number(journal.total_amount, 0)
                self.fields['tax_amount'].initial = round_number(
                    journal.tax_amount, 2) if journal.tax_amount else 0.00
                account_set = AccountSet.objects.get(pk=journal.account_set_id)
                if account_set:
                    self.fields['account_set'].initial = account_set.id if account_set else ''
            except:
                self.fields['account_set'].initial = ''
        else:
            self.fields['amount'].initial = 0
            self.fields['tax_amount'].initial = 0
            self.fields['total_amount'].initial = 0


class ARReceiptTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ()

    def __init__(self, *args, **kwargs):
        super(ARReceiptTransactionForm, self).__init__(*args, **kwargs)


class APPaymentInfoForm(forms.ModelForm):
    bank = CodeModelChoiceField(queryset=Bank.objects.none(), required=True, empty_label='Select Bank',
                                widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required', 'tabindex': '-1'}))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true', 'tabindex': '-1'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    transaction_type = forms.ChoiceField(choices=PAYMENT_TRANSACTION_TYPES, required=True,
                                         widget=forms.Select(attrs={'class': 'form-control sended'}))
    document_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    posting_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd'}))
    supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), required=False, empty_label='Select Supplier',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    supplier_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true', 'tabindex': '-1'}))
    supplier_currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                             widget=forms.Select(attrs={'class': 'form-control no-select disabled', 'tabindex': '-1'    }))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=True, empty_label='Select Supplier',
                                        widget=forms.Select(
                                            attrs={'class': 'form-control sended', 'required': 'required'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=False,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(
                                           attrs={'class': 'form-control sended', 'required': 'required'}))
    payment_check_number = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control hidden sended', 'tabindex': '-1'}))
    amount = forms.DecimalField(required=False, decimal_places=6, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    tax_amount = forms.DecimalField(required=False, decimal_places=6, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    total_amount = forms.DecimalField(required=False, decimal_places=6, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    tax = NameModelChoiceField(queryset=Tax.objects.none(), required=False, empty_label='Select Tax',
                               widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control sended disabled readonly'}))
    invoice_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended', }))
    reference = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled', 'tabindex': '-1'}))
    original_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled readonly text-right', 'type': 'text', 'tabindex': '-1'}))
    payment_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled readonly text-right', 'type': 'text', 'tabindex': '-1'}))
    original_currency_id = forms.IntegerField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_currency_id = forms.IntegerField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    orig_exch_rate = forms.DecimalField(required=False, decimal_places=10, widget=forms.TextInput(
        attrs={'class': 'form-control text-right hidden'}))
    tax_exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended hidden'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                        widget=forms.Select(
                                            attrs={'class': 'form-control no-select disabled hidden'}))

    # Not Used Yet, Will delete later
    original_currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control original-currency-code', 'readonly': 'true', 'style': 'width: 50%'}))

    account_set_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    account_set_code = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_code_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_code_code = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))

    
    payment_currency_id = forms.IntegerField(required=False,
                                             widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control payment-currency-code', 'readonly': 'true', 'style': 'width: 50%'}))
    
    receipt_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00'}))
    customer_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00'}))

    ##########

    class Meta:
        model = Journal
        fields = ('bank', 'currency', 'code', 'name', 'document_date', 'transaction_type', 'posting_date', 'supplier',
                  'supplier_name', 'payment_code', 'payment_check_number', 'account_set', 'tax', 'document_number',
                  'invoice_number', 'reference', 'is_manual_doc', 'amount', 'tax_amount', 'total_amount',
                  'original_currency_id', 'orig_exch_rate', 'exchange_rate', 'exchange_rate_fk',
                  'account_set_id', 'account_set_code', 'payment_code_id', 'payment_code_code', 'payment_amount',
                  'payment_currency_id', 'original_amount', 'receipt_unapplied', 'customer_unapplied',
                  'payment_currency_code', 'tax_exchange_rate')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(APPaymentInfoForm, self).__init__(*args, **kwargs)
        currency_list = Currency.objects.filter(is_hidden=0)
        if self.session_date:
            self.fields['document_date'].initial = self.session_date
            self.fields['posting_date'].initial = self.session_date
        self.fields['currency'].queryset = currency_list
        self.fields['supplier_currency'].queryset = currency_list
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=self.company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')
        self.fields['bank'].queryset = Bank.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AP Account Set']
                                                                        ).order_by('code')
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=False,
            company_id=self.company_id,
            tax_group__company_id=self.company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))

        if self.instance.id:
            if self.instance.tax_exchange_rate == 0:
                self.fields['tax_exchange_rate'].initial = Decimal('1.0')
            if self.instance.currency.is_decimal:
                self.fields['amount'].initial = round_number(self.instance.amount, 2) if self.instance.amount else 0.00
                self.fields['tax_amount'].initial = round_number(self.instance.tax_amount, 2) if self.instance.tax_amount else 0.00
                self.fields['total_amount'].initial = round_number(self.instance.total_amount, 2) if self.instance.total_amount else 0.00
            else:
                self.fields['amount'].initial = round_number(self.instance.amount, 0) if self.instance.amount else 0
                self.fields['tax_amount'].initial = round_number(self.instance.tax_amount, 0) if self.instance.tax_amount else 0
                self.fields['total_amount'].initial = round_number(self.instance.total_amount, 0) if self.instance.total_amount else 0
                
            self.fields['supplier_name'].initial = self.instance.supplier.name if self.instance.supplier else ''
            self.fields['supplier_currency'].initial = self.instance.supplier.currency \
                if self.instance.supplier else None

        else:
            self.initial['bank_code'] = ''
            self.initial['currency_code'] = ''
            self.initial['customer_number'] = ''
            self.initial['customer_name'] = ''
            self.initial['original_currency_code'] = ''
            self.initial['account_set_code'] = ''
            self.initial['payment_code_code'] = ''
            self.initial['payment_currency_code'] = ''
            self.initial['customer_name'] = ''
            self.initial['original_amount'] = 0.00
            self.initial['payment_amount'] = 0.00
            self.initial['receipt_unapplied'] = 0.00
            self.initial['customer_unapplied'] = 0.00
            self.initial['advance_credit'] = 0.00
            self.initial['check_no'] = ''
            self.initial['amount'] = Decimal('0.000000')
            self.initial['tax_amount'] = Decimal('0.000000')
            self.initial['total_amount'] = Decimal('0.000000')


class BatchInfoForm(forms.ModelForm):
    batch_no = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control  text-right', 'readonly': 'true', 'tabindex': '-1'}))
    description = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control txtbatchdesc fieldset hdrdata sended', 'required': 'required'}))
    no_entries = forms.IntegerField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control  text-right', 'readonly': 'true', 'tabindex': '-1'}))
    batch_amount = forms.DecimalField(required=False, decimal_places=6,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control text-right', 'readonly': 'readonly',
                                                 'tabindex':'-1'}))
    credit_amount = forms.DecimalField(required=False, decimal_places=6,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    debit_amount = forms.DecimalField(required=False, decimal_places=6,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control text-right', 'readonly': 'readonly', 'tabindex': '-1'}))
    batch_date = forms.DateField(required=False,
                                 widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                               'class': 'sended form-control form-control-inline input-medium default-date-picker',
                                                               'data-date-format': 'yyyy-mm-dd'}))

    class Meta:
        model = Batch
        fields = ('batch_no', 'description', 'no_entries', 'batch_amount', 'batch_date')

    def __init__(self, *args, **kwargs):
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(BatchInfoForm, self).__init__(*args, **kwargs)
        if self.session_date:
            self.fields['batch_date'].initial = self.session_date
        if self.instance.id:
            self.fields['batch_no'].initial = self.instance.batch_no
            self.fields['description'].initial = self.instance.description
            self.fields['no_entries'].initial = self.instance.no_entries
            self.fields['batch_amount'].initial = self.instance.batch_amount
            self.fields['credit_amount'].initial = self.instance.batch_amount
            self.fields['debit_amount'].initial = self.instance.batch_amount
            self.fields['batch_date'].initial = self.session_date if self.session_date else self.instance.batch_date
        else:
            self.initial['batch_no'] = ''
            self.initial['description'] = ''
            self.initial['no_entries'] = 0
            self.initial['batch_amount'] = Decimal('0.000000')
            self.initial['credit_amount'] = Decimal('0.000000')
            self.initial['debit_amount'] = Decimal('0.000000')

class RecBatchInfoForm(forms.ModelForm):
    batch_no = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control  text-right', 'readonly': 'true', 'tabindex': '-1'}))
    description = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control txtbatchdesc fieldset hdrdata sended', 'required': 'required'}))
    no_entries = forms.IntegerField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control  text-right', 'readonly': 'true', 'tabindex': '-1'}))
    batch_amount = forms.DecimalField(required=False, decimal_places=6,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control text-right', 'readonly': 'readonly',
                                                 'tabindex':'-1'}))
    credit_amount = forms.DecimalField(required=False, decimal_places=6,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    debit_amount = forms.DecimalField(required=False, decimal_places=6,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    batch_date = forms.DateField(required=False,
                                 widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                               'class': 'sended form-control form-control-inline input-medium default-date-picker',
                                                               'data-date-format': 'yyyy-mm-dd'}))

    class Meta:
        model = RecurringBatch
        fields = ('batch_no', 'description', 'no_entries', 'batch_amount', 'batch_date')

    def __init__(self, *args, **kwargs):
        super(RecBatchInfoForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['batch_no'].initial = self.instance.batch_no
            self.fields['description'].initial = self.instance.description
            self.fields['no_entries'].initial = self.instance.no_entries
            self.fields['batch_amount'].initial = self.instance.batch_amount
            self.fields['credit_amount'].initial = self.instance.batch_amount
            self.fields['debit_amount'].initial = self.instance.batch_amount
            self.fields['batch_date'].initial = self.instance.batch_date
        else:
            self.initial['batch_no'] = ''
            self.initial['description'] = ''
            self.initial['no_entries'] = 0
            self.initial['batch_amount'] = Decimal('0.000000')
            self.initial['credit_amount'] = Decimal('0.000000')
            self.initial['debit_amount'] = Decimal('0.000000')


class ReverseTransactionForm(forms.ModelForm):
    bank = CodeModelChoiceField(queryset=Bank.objects.none(), required=True,
                                widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    description = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    bank_account_number = forms.CharField(required=False,
                                          widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required', }))
    journal_type = forms.ChoiceField(choices=SOURCE_APPLICATION, widget=forms.Select(attrs={'class': 'form-control'}))
    payment_no = CodeModelChoiceField(queryset=Journal.objects.none(), required=True,
                                      widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    class Meta:
        model = Journal
        fields = ('bank', 'currency', 'journal_type')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(ReverseTransactionForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['bank'].queryset = Bank.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id)
        self.fields['journal_type'].queryset = Journal.objects.filter(company_id=self.company_id, is_hidden=False)


class FiscalCalendarForm(forms.ModelForm):
    fiscal_year = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control  text-right', 'readonly': 'true'}))
    period = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    start_date = forms.DateField(required=False,
                                 widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime("%d-%m-%Y"),
                                                               'class': 'form-control form-control-inline input-medium',
                                                               'style': 'width:110px;',
                                                               'data-date-format': 'dd-mm-yyyy'}))
    end_date = forms.DateField(required=False,
                               widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime("%d-%m-%Y"),
                                                             'class': 'form-control form-control-inline input-medium',
                                                             'style': 'width:110px;',
                                                             'data-date-format': 'dd-mm-yyyy'}))
    is_ic_locked = forms.BooleanField(initial=False, required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'hidden'}))
    is_sp_locked = forms.BooleanField(initial=False, required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'hidden'}))
    is_ap_locked = forms.BooleanField(initial=False, required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'hidden'}))
    is_ar_locked = forms.BooleanField(initial=False, required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'hidden'}))
    is_gl_locked = forms.BooleanField(initial=False, required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'hidden'}))
    is_bank_locked = forms.BooleanField(initial=False, required=False,
                                        widget=forms.CheckboxInput(attrs={'class': 'hidden'}))

    class Meta:
        model = FiscalCalendar
        fields = ('fiscal_year', 'period', 'start_date', 'end_date', 'is_ic_locked', 'is_sp_locked', 'is_ar_locked',
                  'is_ap_locked', 'is_gl_locked', 'is_bank_locked')

    def __init__(self, *args, **kwargs):
        super(FiscalCalendarForm, self).__init__(*args, **kwargs)


class RecurringEntryForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'id': 'trxnum', 'class': 'form-control  text-center', 'readonly': True}))
    name = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata'}))
    description = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata'}))
    schedule_code = forms.CharField(required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control  text-center', 'required': 'required'} ))
    schedule_desc = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata', 'disabled': True}))
    journal_desc = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata'}))
    rounding_acc = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata'}))
    start_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'id': 'start_date',
               'required': 'required',
               'value': datetime.datetime.now().strftime('%d-%m-%Y'),
               'class': 'form-control form-control-inline input-medium default-date-picker fieldset hdrdata',
               'data-date-format': 'dd-mm-yyyy'}))
    expire_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'id': 'expire_date',
               'value': datetime.datetime.now().strftime('%d-%m-%Y'),
               'class': 'form-control form-control-inline input-medium default-date-picker fieldset hdrdata',
               'data-date-format': 'dd-mm-yyyy'}))
    run_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'id': 'run_date',
            #    'required': 'required',
            #    'value': datetime.datetime.now().strftime('%d-%m-%Y'),
               'class': 'form-control form-control-inline input-medium default-date-picker fieldset hdrdata',
               'data-date-format': 'dd-mm-yyyy'}))
    maintained_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'id': 'maintained_date',
            #    'required': 'required',
            #    'value': datetime.datetime.now().strftime('%d-%m-%Y'),
               'class': 'form-control form-control-inline input-medium default-date-picker fieldset hdrdata',
               'data-date-format': 'dd-mm-yyyy'}))
    is_active = forms.BooleanField(initial=True, required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    is_auto_reverse = forms.BooleanField(initial=False, required=False,
                                         widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    is_expire = forms.BooleanField(initial=False, required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    entry_mode = forms.ChoiceField(widget=forms.RadioSelect, choices=RECURRING_ENTRY_MODE)
    exch_rate_type = forms.CharField(required=False,
                                     widget=forms.TextInput(attrs={'class': 'form-control sended', 'disabled': True}))
    source_type = forms.CharField(
        widget=forms.TextInput(
            attrs={'id': 'txtsource_code', 'class': 'form-control fieldset hdrdata', 'required': 'required'}))

    class Meta:
        model = RecurringEntry
        fields = (
            'code', 'description', 'source_type', 'journal_desc', 'rounding_acc', 'start_date', 'expire_date',
            'run_date', 'maintained_date', 'is_active', 'is_auto_reverse', 'is_expire', 'entry_mode', 'exch_rate_type'
        )

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(RecurringEntryForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['code'].initial = self.instance.code if self.instance.code else ''
            self.fields['name'].initial = self.instance.name if self.instance.name else ''
            self.fields['description'].initial = self.instance.description if self.instance.description else ''
            self.fields['journal_desc'].initial = self.instance.journal_desc if self.instance.journal_desc else ''
            self.fields['rounding_acc'].initial = self.instance.rounding_acc if self.instance.rounding_acc else ''
            self.fields['is_active'].initial = self.instance.is_active if self.instance.is_active else False
            self.fields['is_expire'].initial = self.instance.is_expire if self.instance.is_expire else False
            self.fields['is_auto_reverse'].initial = self.instance.is_auto_reverse if self.instance.is_auto_reverse else False
            self.fields['entry_mode'].initial = self.instance.entry_mode if self.instance.entry_mode else 0
            self.fields['exch_rate_type'].initial = 'Current Rate'
            self.initial['run_date'] = self.instance.run_date.strftime('%d-%m-%Y') if self.instance.run_date else ''
            self.initial['maintained_date'] = self.instance.maintained_date.strftime('%d-%m-%Y') if self.instance.maintained_date else ''
        else:
            self.initial['code'] = '1'
            self.initial['name'] = ''
            self.initial['description'] = ''
            self.initial['journal_desc'] = ''
            self.initial['rounding_acc'] = ''
            self.initial['start_date'] = datetime.datetime.now().strftime('%d-%m-%Y')
            self.initial['expire_date'] = datetime.datetime.now().strftime('%d-%m-%Y')
            self.initial['is_active'] = True
            self.initial['is_expire'] = False
            self.initial['is_auto_reverse'] = False
            self.initial['entry_mode'] = 0
            self.initial['exch_rate_type'] = 'Current Rate'


class ScheduleEntryForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(
                               attrs={'id': 'trxnum', 'class': 'form-control  text-center schedule_code'}))
    description = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended fieldset hdrdata'}))
    recur_period = forms.ChoiceField(
        widget=forms.RadioSelect, choices=RECURRING_PERIOD)
    daily_frequency = forms.IntegerField(required=False,
                                         widget=forms.TextInput(attrs={'class': 'form-control schedule_frequency'}))
    weekly_frequency = forms.IntegerField(required=False,
                                          widget=forms.TextInput(attrs={'class': 'form-control schedule_frequency'}))
    monthly_frequency = forms.IntegerField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control schedule_frequency'}))
    semi_monthly_frequency_1st = forms.ChoiceField(
        widget=forms.Select(), choices=MOTNHDATES)
    semi_monthly_frequency_2nd = forms.ChoiceField(
        widget=forms.Select(), choices=MOTNHDATES)
    monthly_frequency_choice = forms.ChoiceField(
        widget=forms.Select(), choices=MOTNHDATES)
    monthly_week_choice = forms.ChoiceField(
        widget=forms.Select(), choices=WEEK_NUMBER)
    week_days_choice = forms.ChoiceField(
        widget=forms.Select(), choices=WEEKDAYS)
    year_monthly_frequency_choice = forms.ChoiceField(
        widget=forms.Select(), choices=MOTNHDATES)
    year_monthly_week_choice = forms.ChoiceField(
        widget=forms.Select(), choices=WEEK_NUMBER)
    year_week_days_choice = forms.ChoiceField(
        widget=forms.Select(), choices=WEEKDAYS)
    year_months_choice = forms.ChoiceField(
        widget=forms.Select(), choices=MONTH_NAMES)
    week_day = forms.ChoiceField(
        widget=forms.RadioSelect, choices=WEEKDAYS)
    week_days = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=WEEKDAYS)

    class Meta:
        model = Schedule
        fields = (
            'code', 'description', 'recur_period', 'user_mode', 'daily_frequency', 'weekly_frequency',
            'monthly_frequency',
            'frequency_week_of_month', 'frequency_weekday_index', 'frequency_bimonthly_date1',
            'frequency_bimonthly_date2',
            'frequency_date', 'frequency_month', 'monthly_choice', 'yearly_choice', 'daily_choice',
            'semi_monthly_frequency_1st',
            'semi_monthly_frequency_2nd', 'monthly_frequency_choice', 'monthly_week_choice', 'week_days_choice',
            'year_monthly_frequency_choice',
            'year_monthly_week_choice', 'year_week_days_choice', 'year_months_choice', 'week_day', 'week_days'
        )

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(ScheduleEntryForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['code'].initial = self.instance.code if self.instance.code else '1'
            self.fields['description'].initial = self.instance.description if self.instance.description else ''
            self.fields['recur_period'].initial = self.instance.recur_period if self.instance.recur_period else \
                RECURRING_PERIOD_DICT['Daily']
            if self.instance.recur_period:
                if RECURRING_PERIOD_DICT['Daily'] == self.instance.recur_period:
                    self.fields['daily_frequency'].initial = self.instance.daily_frequency
                elif RECURRING_PERIOD_DICT['Weekly'] == self.instance.recur_period:
                    self.fields[
                        'weekly_frequency'].initial = self.instance.weekly_frequency if self.instance.weekly_frequency else ''
                    self.fields[
                        'week_day'].initial = self.instance.frequency_weekday_index if self.instance.frequency_weekday_index else ''
            elif RECURRING_PERIOD_DICT['Monthly'] == self.instance.recur_period:
                self.fields[
                    'monthly_frequency'].initial = self.instance.monthly_frequency if self.instance.monthly_frequency else ''
                self.fields['monthly_frequency_choice'].initial = str(
                    self.instance.frequency_date) if self.instance.frequency_date else ''
            elif RECURRING_PERIOD_DICT['Yearly'] == self.instance.recur_period:
                self.fields['year_months_choice'].initial = str(
                    self.instance.frequency_month) if self.instance.frequency_month else ''
                self.fields['year_monthly_frequency_choice'].initial = str(
                    self.instance.frequency_date) if self.instance.frequency_date else ''


class ARInvoiceREForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control  text-right', 'readonly': 'readonly'}))
    re_description = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    description = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    customer = CodeModelChoiceField(queryset=Customer.objects.none(), required=True, empty_label='Select Customer',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    customer_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required', 'readonly': 'readonly'}))
    customer_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(), required=True,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    account_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled sended'}))
    document_number = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control sended', 'required': 'required'}))
    document_amount = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended numeric_amount', 'required': 'required', 'readonly': 'readonly'}))
    document_type = forms.CharField(required=True,
                                    widget=forms.Select(choices=AR_INV_DOCUMENT_TYPES, attrs={'class': 'form-control sended'}))
    po_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    order_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    document_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    posting_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}), initial=0)
    tax = NameModelChoiceField(queryset=None, required=False, empty_label=None,
                               widget=forms.Select(attrs={'class': 'form-control sended'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    total_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required', }))
    currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right numeric_rate', 'required': 'required'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                            widget=forms.Select(
                                                attrs={'class': 'form-control no-select disabled hidden'}))

    class Meta:
        model = RecurringEntry
        fields = (
            'code', 're_description', 'description', 'name', 'customer', 'customer_name', 'customer_code', 'account_set', 'is_manual_doc',
            'document_number', 'po_number', 'order_number',
            'document_amount', 'document_type', 'document_date', 'posting_date', 'amount',
            'tax', 'tax_amount', 'total_amount', 'currency', 'exchange_rate', 'exchange_rate_fk')

    def __init__(self, id=None, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(ARInvoiceREForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=0,
            company_id=self.company_id,
            tax_group__company_id=self.company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Sales']))
        self.fields['exchange_rate_fk'].queryset = ExchangeRate.objects.filter(is_hidden=False,
                                                                               company_id=self.company_id,
                                                                               flag='ACCOUNTING')
        self.fields['customer'].queryset = Customer.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AR Account Set']
                                                                        ).order_by('code')
        if id:
            try:
                journal = RecurringEntry.objects.get(pk=id)
                self.fields['re_description'].initial = journal.re_description
                self.fields['description'].initial = journal.description
                self.fields['name'].initial = journal.name
                customer = Customer.objects.get(pk=journal.customer_id)
                self.fields['customer'].initial = customer.id if customer else ''
                self.fields['customer_name'].initial = customer.name if customer else ''
                self.fields['customer_code'].initial = customer.code if customer else ''
                if journal.account_set:
                    account_set = AccountSet.objects.get(pk=journal.account_set_id)
                    if account_set:
                        self.fields['account_set'].initial = account_set.id if account_set else ''
                        self.fields['account_code'].initial = account_set.code if account_set else ''
                if customer and customer.currency:
                    currency = Currency.objects.get(id=customer.currency_id)
                    self.fields['currency_code'].initial = currency.code if currency else ''
                    self.fields['currency'].initial = currency.id if currency else ''
                    self.fields['account_set'].queryset = \
                        AccountSet.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id,
                                                  type=ACCOUNT_SET_TYPE_DICT['AR Account Set'],
                                                  currency_id=currency.id).order_by('code')
            except:
                self.fields['customer'].initial = ''
                self.fields['customer_name'].initial = ''
                self.fields['customer_code'].initial = ''
                self.fields['account_set'].initial = ''
                self.fields['account_code'].initial = ''
                self.fields['currency_code'].initial = ''
                self.fields['currency'].initial = ''
        else:
            self.initial['document_amount'] = Decimal('0.000000')
            self.initial['amount'] = Decimal('0.000000')
            self.initial['tax_amount'] = Decimal('0.000000')
            self.initial['total_amount'] = Decimal('0.000000')


class APInvoiceREForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    re_description = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    description = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    order_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control hidden'}))
    supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), required=True, empty_label='Select Supplier',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    supplier_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}))
    supplier_code = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(), required=True,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    account_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    document_number = forms.CharField(required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control sended disabled readonly',
                                                                    'required': 'required'}))
    document_amount = forms.DecimalField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended numeric_amount', 'required': 'required', 'readonly': 'readonly'}))
    document_type = forms.ChoiceField(choices=AP_INV_DOCUMENT_TYPES, required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    po_number = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    order_number = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    document_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    posting_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}), initial=0)
    tax = NameModelChoiceField(queryset=None, required=False, empty_label=None,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    tax_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    total_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required', }))
    currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled sended'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right numeric_rate', 'required': 'required'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                            widget=forms.Select(
                                                attrs={'class': 'form-control no-select disabled hidden'}))

    class Meta:
        model = RecurringEntry
        fields = ('code', 're_description', 'description', 'name', 'supplier', 'supplier_name', 'supplier_code', 'account_set', 'document_number',
                  'document_amount', 'document_type', 'po_number', 'order_number', 'order_id', 'is_manual_doc',
                  'document_date', 'posting_date', 'amount', 'tax', 'tax_amount', 'total_amount', 'currency',
                  'exchange_rate', 'exchange_rate_fk')

    def __init__(self, id=None, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(APInvoiceREForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=0,
            company_id=self.company_id,
            tax_group__company_id=self.company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
        self.fields['exchange_rate_fk'].queryset = ExchangeRate.objects.filter(is_hidden=False,
                                                                               company_id=self.company_id,
                                                                               flag='ACCOUNTING')
        self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[
                                                                            self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AP Account Set']
                                                                        ).order_by('code')
        if id:
            try:
                journal = RecurringEntry.objects.get(pk=id)
                self.fields['re_description'].initial = journal.re_description
                self.fields['description'].initial = journal.description
                self.fields['name'].initial = journal.name
                supplier = Supplier.objects.get(pk=journal.supplier_id)
                self.fields['supplier'].initial = supplier.id if supplier else ''
                self.fields['supplier_name'].initial = supplier.name if supplier else ''
                self.fields['supplier_code'].initial = supplier.code if supplier else ''
                if supplier and supplier.currency:
                    currency = Currency.objects.get(id=supplier.currency_id)
                    self.fields['currency_code'].initial = currency.code if currency else ''
                    self.fields['currency'].initial = currency.id if currency else ''
                    self.fields['account_set'].queryset = \
                        AccountSet.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id,
                                                  type=ACCOUNT_SET_TYPE_DICT['AP Account Set'],
                                                  currency_id=currency.id).order_by('code')
                if journal.account_set:
                    account_set = AccountSet.objects.get(pk=journal.account_set_id)
                    if account_set:
                        self.fields['account_set'].initial = account_set.id if account_set else ''
                        self.fields['account_code'].initial = account_set.code if account_set else ''
            except:
                self.fields['supplier'].initial = ''
                self.fields['supplier_name'].initial = ''
                self.fields['supplier_code'].initial = ''
                self.fields['account_set'].initial = ''
                self.fields['account_code'].initial = ''
                self.fields['currency_code'].initial = ''
                self.fields['currency'].initial = ''
        else:
            self.initial['document_amount'] = Decimal('0.000000')
            self.initial['amount'] = Decimal('0.000000')
            self.initial['tax_amount'] = Decimal('0.000000')
            self.initial['total_amount'] = Decimal('0.000000')


class APPaymentREForm(forms.ModelForm):
    bank = CodeModelChoiceField(queryset=Bank.objects.none(), required=True, empty_label='Select Bank',
                                widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required', }))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true'}))
    re_description = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    description = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    transaction_type = forms.ChoiceField(choices=PAYMENT_TRANSACTION_TYPES, required=True,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    document_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    posting_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd'}))
    supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), required=False, empty_label='Select Supplier',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    supplier_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    supplier_currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                             widget=forms.Select(attrs={'class': 'form-control no-select disabled'}))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=True, empty_label='Select Supplier',
                                        widget=forms.Select(
                                            attrs={'class': 'form-control sended', 'required': 'required'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=False,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(
                                           attrs={'class': 'form-control sended', 'required': 'required'}))
    payment_check_number = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control hidden sended'}))
    amount = forms.DecimalField(required=False, decimal_places=6, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    tax_amount = forms.DecimalField(required=False, decimal_places=6, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    total_amount = forms.DecimalField(required=False, decimal_places=6, widget=forms.TextInput(
        attrs={'class': 'form-control text-right', 'readonly': 'readonly'}))
    tax = NameModelChoiceField(queryset=Tax.objects.none(), required=False, empty_label='Select Tax',
                               widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control sended disabled readonly'}))
    invoice_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended', }))
    reference = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled'}))

    # Not Used Yet, Will delete later
    original_currency_id = forms.IntegerField(required=False,
                                              widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    original_currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control original-currency-code', 'readonly': 'true', 'style': 'width: 50%'}))

    account_set_id = forms.IntegerField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    account_set_code = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_code_id = forms.IntegerField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_code_code = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control numeric_amount', 'type': 'number', 'step': '0.01', 'min': '0.00'}))
    payment_currency_id = forms.IntegerField(required=False,
                                             widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_currency_code = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control payment-currency-code', 'readonly': 'true', 'style': 'width: 50%'}))
    original_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00'}))
    receipt_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00'}))
    customer_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00'}))
    orig_exch_rate = forms.DecimalField(required=False, decimal_places=10, widget=forms.TextInput(
        attrs={'class': 'form-control text-right hidden'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended hidden'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                            widget=forms.Select(
                                            attrs={'class': 'form-control no-select disabled hidden'}))

    ##########

    class Meta:
        model = RecurringEntry
        fields = ('bank', 'currency', 'code', 're_description', 'description', 'name', 'document_date', 'transaction_type', 'posting_date', 'supplier',
                  'supplier_name', 'payment_code', 'payment_check_number', 'account_set', 'tax', 'document_number',
                  'invoice_number', 'reference', 'is_manual_doc', 'amount', 'tax_amount', 'total_amount',
                  'original_currency_code',
                  'account_set_id', 'account_set_code', 'payment_code_id', 'payment_code_code', 'payment_amount',
                  'payment_currency_id', 'original_amount', 'receipt_unapplied', 'customer_unapplied',
                  'payment_currency_code',)

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(APPaymentREForm, self).__init__(*args, **kwargs)
        currency_list = Currency.objects.filter(is_hidden=0)
        self.fields['currency'].queryset = currency_list
        self.fields['supplier_currency'].queryset = currency_list
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=self.company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')
        self.fields['bank'].queryset = Bank.objects.filter(
            is_hidden=False, is_active=True, company_id=self.company_id)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[
                                                                            self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AP Account Set']
                                                                        ).order_by('code')
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=False,
            company_id=self.company_id,
            tax_group__company_id=self.company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))

        if self.instance.id:
            self.fields['re_description'].initial = self.instance.re_description
            self.fields['description'].initial = self.instance.description
            self.fields['name'].initial = self.instance.name
            self.fields['amount'].initial = self.instance.amount if self.instance.amount else 0.00
            self.fields['tax_amount'].initial = self.instance.tax_amount if self.instance.tax_amount else 0.00
            self.fields['total_amount'].initial = self.instance.total_amount if self.instance.total_amount else 0.00
            self.fields['original_amount'].initial = self.instance.original_amount if self.instance.original_amount else 0.00
            self.fields['payment_amount'].initial = self.instance.payment_amount if self.instance.payment_amount else 0.00
            if self.instance.transaction_type == PAYMENT_TRANSACTION_TYPES_DICT['Payment']:
                self.fields['supplier_name'].initial = self.instance.supplier.name if self.instance.supplier else ''
                self.fields['supplier_currency'].initial = self.instance.supplier.currency \
                    if self.instance.supplier.currency else ''

        else:
            self.initial['bank_code'] = ''
            self.initial['currency_code'] = ''
            self.initial['customer_number'] = ''
            self.initial['customer_name'] = ''
            self.initial['original_currency_code'] = ''
            self.initial['account_set_code'] = ''
            self.initial['payment_code_code'] = ''
            self.initial['payment_currency_code'] = ''
            self.initial['customer_name'] = ''
            self.initial['original_amount'] = 0.00
            self.initial['payment_amount'] = 0.00
            self.initial['receipt_unapplied'] = 0.00
            self.initial['customer_unapplied'] = 0.00
            self.initial['advance_credit'] = 0.00
            self.initial['check_no'] = ''
            self.initial['amount'] = Decimal('0.000000')
            self.initial['tax_amount'] = Decimal('0.000000')
            self.initial['total_amount'] = Decimal('0.000000')


class ARReceiptREForm(forms.ModelForm):
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': 'true'}))
    re_description = forms.CharField(required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    description = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control sended', 'required': 'required'}))
    bank = CodeModelChoiceField(queryset=Bank.objects.none(), required=True,
                                widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=True, empty_label='',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control no-select disabled', 'required': 'required'}))
    posting_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    transaction_type = forms.ChoiceField(choices=RECEIPT_TRANSACTION_TYPES, required=True,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    document_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
               'class': 'form-control form-control-inline input-medium default-date-picker sended',
               'data-date-format': 'yyyy-mm-dd', 'required': 'required'}))
    customer = CodeModelChoiceField(queryset=Customer.objects.none(), required=False, empty_label='Select Customer',
                                    widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    customer_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    customer_currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                             widget=forms.Select(attrs={'class': 'form-control no-select disabled'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=False,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control sended'}))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=True, empty_label='Select Payment',
                                        widget=forms.Select(
                                            attrs={'class': 'form-control sended', 'required': 'required'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control sended disabled readonly'}))
    reference = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    invoice_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    amount = forms.DecimalField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    tax_amount = forms.DecimalField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    total_amount = forms.DecimalField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_check_number = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control sended'}))
    is_manual_doc = forms.BooleanField(initial=True, required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    original_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled text-right', 'type': 'text', 'readonly': 'true', 'tabindex': '-1'}))
    payment_amount = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended text-right numeric_amount', 'type': 'text'}))
    receipt_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled text-right', 'type': 'text', 'readonly': 'true', 'tabindex': '-1'}))
    customer_unapplied = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control sended disabled text-right', 'type': 'text', 'readonly': 'true', 'tabindex': '-1'}))
    original_currency_id = forms.IntegerField(required=False,
                                              widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_currency_id = forms.IntegerField(required=False,
                                             widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    orig_exch_rate = forms.DecimalField(required=False, decimal_places=10, widget=forms.TextInput(
        attrs={'class': 'form-control text-right hidden'}))
    exchange_rate = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control text-right sended hidden'}))
    exchange_rate_fk = RateModelChoiceField(queryset=ExchangeRate.objects.none(), required=False, empty_label='',
                                            widget=forms.Select(
                                            attrs={'class': 'form-control no-select disabled hidden'}))

    class Meta:
        model = RecurringEntry
        fields = ('code', 're_description', 'description', 'name', 'bank', 'currency', 'posting_date', 'transaction_type', 'document_date', 'customer',
                  'customer_name', 'customer_currency', 'account_set', 'payment_code', 'document_number', 'reference',
                  'invoice_number', 'amount', 'tax_amount', 'total_amount', 'payment_check_number', 'is_manual_doc',
                  'original_amount', 'payment_amount', 'original_currency_id', 'payment_currency_id', 'orig_exch_rate',
                  'receipt_unapplied', 'customer_unapplied', 'exchange_rate', 'exchange_rate_fk')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(ARReceiptREForm, self).__init__(*args, **kwargs)
        currency_list = Currency.objects.filter(is_hidden=0)
        self.fields['currency'].queryset = currency_list
        self.fields['customer_currency'].queryset = currency_list
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=self.company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
        self.fields['bank'].queryset = Bank.objects.filter(is_hidden=False, is_active=True, company_id=self.company_id)
        self.fields['customer'].queryset = Customer.objects.filter(is_hidden=False, is_active=True,
                                                                   company_id=self.company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(is_hidden=False, is_active=True,
                                                                        company_id__in=[self.company_id, None],
                                                                        type=ACCOUNT_SET_TYPE_DICT['AR Account Set']
                                                                        ).order_by('code')
        if self.instance.id:
            self.fields['posting_date'].initial = self.instance.posting_date
            self.fields['re_description'].initial = self.instance.re_description
            self.fields['description'].initial = self.instance.description
            self.fields['name'].initial = self.instance.name
            self.fields['bank'].initial = self.instance.bank
            self.fields['currency'].initial = self.instance.currency
            self.fields['payment_code'].initial = self.instance.payment_code
            self.fields['payment_check_number'].initial = self.instance.payment_check_number
            self.fields['is_manual_doc'].initial = self.instance.is_manual_doc
            self.fields['document_number'].initial = self.instance.document_number if self.instance.document_number else ''
            self.fields['reference'].initial = self.instance.reference
            self.fields['transaction_type'].initial = self.instance.transaction_type
            self.fields['amount'].initial = round_number(self.instance.amount, 2) if self.instance.amount else 0.00
            self.fields['tax_amount'].initial = round_number(self.instance.tax_amount, 2) if self.instance.tax_amount else 0.00
            self.fields['total_amount'].initial = round_number(self.instance.total_amount, 2) if self.instance.total_amount else 0.00
            self.fields['customer'].initial = self.instance.customer if self.instance.customer else ''
            self.fields['customer_name'].initial = self.instance.customer.name if self.instance.customer else ''
            self.fields['customer_currency'].initial = self.instance.customer.currency \
                if self.instance.customer else ''
            self.fields['account_set'].initial = self.instance.account_set
        
            self.fields['invoice_number'].initial = self.instance.invoice_number
        else:
            self.fields['amount'].initial = 0
            self.fields['tax_amount'].initial = 0
            self.fields['total_amount'].initial = 0


class AROptionsNumberForm(forms.ModelForm):
    invoice_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    invoice_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    invoice_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    cnote_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    cnote_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    cnote_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    dnote_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    dnote_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    dnote_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    interest_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    interest_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    interest_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    # recurring_prefix = forms.CharField(required=True,
    #                        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    # recurring_length = forms.IntegerField(required=True,
    #                         widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    # recurring_next_number = forms.IntegerField(required=True,
    #                         widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    prepayment_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    prepayment_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    prepayment_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    ucash_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    ucash_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    ucash_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    adjustment_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    adjustment_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    adjustment_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    receipt_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    receipt_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    receipt_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    refund_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    refund_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    refund_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    
    class Meta:
        model = AROptions
        fields = (
            'invoice_prefix', 'invoice_length', 'invoice_next_number', 'cnote_prefix', 'cnote_length', 'cnote_next_number',
            'dnote_prefix', 'dnote_length', 'dnote_next_number', 'interest_prefix', 'interest_length', 'interest_next_number',
            'prepayment_prefix', 'prepayment_length', 'prepayment_next_number', 'ucash_prefix', 'ucash_length', 'ucash_next_number', 
            'adjustment_prefix', 'adjustment_length', 'adjustment_next_number', 'receipt_prefix', 'receipt_length', 'receipt_next_number', 
            'refund_prefix', 'refund_length', 'refund_next_number')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(AROptionsNumberForm, self).__init__(*args, **kwargs)


class AROptionsStatementForm(forms.ModelForm):
    aging_period_1 = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    aging_period_2 = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    aging_period_3 = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    

    class Meta:
        model = AROptions
        fields = ('aging_period_1', 'aging_period_2', 'aging_period_3')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(AROptionsStatementForm, self).__init__(*args, **kwargs)



class APOptionsNumberForm(forms.ModelForm):
    recurring_pay_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    recurring_pay_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    recurring_pay_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    prepayment_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    prepayment_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    prepayment_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    payment_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    payment_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    payment_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    adjustment_prefix = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    adjustment_length = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    adjustment_next_number = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))

    class Meta:
        model = APOptions
        fields = ('recurring_pay_prefix', 'recurring_pay_length', 'recurring_pay_next_number', 'prepayment_prefix', 'prepayment_length', 
            'prepayment_next_number', 'adjustment_prefix', 'adjustment_length', 'adjustment_next_number', 'payment_prefix', 
            'payment_length', 'payment_next_number')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(APOptionsNumberForm, self).__init__(*args, **kwargs)


class APOptionsStatementForm(forms.ModelForm):
    aging_period_1 = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    aging_period_2 = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    aging_period_3 = forms.IntegerField(required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control text-right', 'required': 'required'}))
    

    class Meta:
        model = APOptions
        fields = ('aging_period_1', 'aging_period_2', 'aging_period_3')

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(APOptionsStatementForm, self).__init__(*args, **kwargs)
