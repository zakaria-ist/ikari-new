from django import forms
from django.forms import ModelChoiceField

from accounting.models import PaymentCode
from accounts.models import Account, AccountSet, DistributionCode
from companies.models import Company
from countries.models import Country
from currencies.models import Currency
from customers.models import Customer, Delivery
from locations.models import Location
from taxes.models import Tax
from utilities.constants import TERMS_CODE, DIS_CODE_TYPE_REVERSED, ACCOUNT_SET_TYPE_DICT, TAX_TRX_TYPES_DICT, PAYMENT_CODE_TYPE_DICT


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code

class CountryCodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class CodeModelChoiceNameField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class TaxNameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CustomerForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    note_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    note_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    postal_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = CodeModelChoiceNameField(queryset=Country.objects.none(), required=False,
                                   empty_label='Select Country Code',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    currency = CodeModelChoiceNameField(queryset=Currency.objects.none(), required=False,
                                    empty_label='Select Country Code',
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(), required=False,
                                        empty_label='Select Payment Code',
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    tax = CodeModelChoiceField(queryset=Tax.objects.none(), required=False,
                               empty_label='Select Tax Code',
                               widget=forms.Select(attrs={'class': 'form-control'}))
    location = CodeModelChoiceField(queryset=Location.objects.none(), required=False,
                                    empty_label='Select Location Stock Code',
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    payment_term = forms.ChoiceField(choices=TERMS_CODE, required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    attention = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(initial=True, required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'styled'}))

    pricing_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    interest_flag = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    distribution_code = CodeModelChoiceField(queryset=DistributionCode.objects.none(), required=False,
                                             empty_label='Select distribution Code',
                                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Customer
        fields = ('code',
                  'name',
                  'phone',
                  'email',
                  'fax',
                  'note_1',
                  'note_2',
                  'postal_code',
                  'country',
                  'currency',
                  'payment_code',
                  'tax',
                  'location',
                  'payment_term',
                  'interest_flag',
                  'pricing_type',
                  'address',
                  'is_active', 'distribution_code'
                  )

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id')
        super(CustomerForm, self).__init__(*args, **kwargs)

        self.fields['country'].queryset = Country.objects.filter(is_hidden=0).order_by('code')
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0).order_by('code')
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=self.company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
        self.fields['tax'].queryset = Tax.objects.filter(is_hidden=0, company_id=self.company_id).order_by('code')
        self.fields['location'].queryset = Location.objects.filter(company_id=self.company_id, is_active=1, is_hidden=0) \
            .order_by('code')
        self.fields['distribution_code'].queryset = DistributionCode.objects. \
            filter(is_hidden=False, company_id=self.company_id,
                   type=dict(DIS_CODE_TYPE_REVERSED)['AR Distribution Code']). \
            order_by('code')


class DeliveryForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    note_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    attention = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(initial=True, required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'styled'}))

    class Meta:
        model = Delivery
        fields = ('code',
                  'name',
                  'attention',
                  'phone',
                  'email',
                  'fax',
                  'note_1',
                  'address',
                  'is_active'
                  )


class AccCustomerForm(forms.ModelForm):
    account_receivable = CodeModelChoiceField(queryset=Account.objects.none(),
                                           required=False,
                                           empty_label='Select Account Receivable',
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    account_receivable_name = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',  'autofocus': 'true'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                    widget=forms.Select(attrs={'class': 'form-control no-select', 'disabled': 'disabled'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=True,
                                       empty_label='Select Account',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    interest_profile = CodeModelChoiceField(queryset=AccountSet.objects.none(), required=False,
                                            empty_label='Select Account',
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=False, empty_label='Select Payment Code',
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    payment_term = forms.ChoiceField(choices=TERMS_CODE, required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    credit_limit = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))
    tax = TaxNameChoiceField(queryset=Tax.objects.none(), required=False,
                             empty_label='Select Tax Code',
                             widget=forms.Select(attrs={'class': 'form-control'}))
    account_set_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    account_set_code = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    account_set_name = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    interest_profile_id = forms.IntegerField(required=False,
                                             widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    interest_profile_code = forms.CharField(required=False,
                                            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    interest_profile_name = forms.CharField(required=False,
                                            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_code_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_code_code = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_code_name = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    tax_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    tax_code = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    tax_name = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    currency_id = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    currency_code = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    currency_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    email_msg = forms.CharField(required=False,
                                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    country = CountryCodeModelChoiceField(queryset=Country.objects.none(), required=False, empty_label='',
                                    widget=forms.Select(attrs={'class': 'form-control no-select'
                                                               }))
    address = forms.CharField(required=False,
                                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    postal_code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Customer
        fields = ('code', 'name', 'email', 'currency',
                  'payment_code', 'account_set', 'interest_profile', 'payment_term', 'credit_limit',
                  'account_set_id', 'account_set_code', 'payment_code_id', 'payment_code_code',
                  'interest_profile_id', 'interest_profile_code', 'email_msg',
                  'account_set_name', 'interest_profile_name', 'payment_code_name',
                  'currency_id', 'currency_code', 'currency_name',
                  'address', 'postal_code', 'phone', 'country', 'account_receivable', 'account_receivable_name')

    def __init__(self, request, *args, **kwargs):
        super(AccCustomerForm, self).__init__(*args, **kwargs)
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        accountset_list = AccountSet.objects.filter(is_hidden=False, is_active=True, company_id=company_id,
                                                    type=ACCOUNT_SET_TYPE_DICT['AR Account Set']).order_by('code')
        self.fields['account_receivable'].queryset = Account.objects.filter(is_hidden=False, is_active=True,
                                                                            company_id=company_id).order_by('account_segment', 'code')
        self.fields['account_set'].queryset = accountset_list
        self.fields['interest_profile'].queryset = accountset_list
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=False).order_by('code')
        self.fields['country'].queryset = Country.objects.filter(is_hidden=False).order_by('code')
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=0,
            company_id=company_id,
            tax_group__company_id=company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Sales'])).order_by('code')

        if self.instance.id:
            self.initial['account_receivable'] = self.instance.account_receivable if self.instance.account_receivable else ''
            self.initial['account_receivable_name'] = self.instance.account_receivable.name if self.instance.account_receivable else ''
            self.initial['account_set'] = self.instance.account_set if self.instance.account_set else ''
            self.initial[
                'interest_profile'] = self.instance.interest_profile if self.instance.interest_profile else ''
            self.initial['payment_code'] = self.instance.payment_code if self.instance.payment_code else ''
            self.initial['payment_term'] = self.instance.payment_term if self.instance.payment_term else ''
            try:
                self.initial['tax'] = self.instance.tax if self.instance.tax else None
            except:
                self.initial['tax'] = None
            self.initial['currency'] = self.instance.currency if self.instance.currency else ''

            self.initial['account_set_id'] = self.instance.account_set.id if self.instance.account_set else ''
            self.initial['account_set_code'] = self.instance.account_set.code if self.instance.account_set else ''
            self.initial['account_set_name'] = self.instance.account_set.name if self.instance.account_set else ''
            self.initial[
                'interest_profile_id'] = self.instance.interest_profile.id if self.instance.interest_profile else ''
            self.initial[
                'interest_profile_code'] = self.instance.interest_profile.code if self.instance.interest_profile else ''
            self.initial[
                'interest_profile_name'] = self.instance.interest_profile.name if self.instance.interest_profile else ''
            self.initial['payment_code_id'] = self.instance.payment_code.id if self.instance.payment_code else ''
            self.initial['payment_code_code'] = self.instance.payment_code.code if self.instance.payment_code else ''
            self.initial['payment_code_name'] = self.instance.payment_code.name if self.instance.payment_code else ''
            try:
                self.initial['tax_id'] = self.instance.tax.id if self.instance.tax else ''
                self.initial['tax_code'] = self.instance.tax.code if self.instance.tax else ''
                self.initial['tax_name'] = self.instance.tax.name if self.instance.tax else ''
            except:
                self.initial['tax_id'] = ''
                self.initial['tax_code'] = ''
                self.initial['tax_name'] = ''
            self.initial['currency_id'] = self.instance.currency.id if self.instance.currency else ''
            self.initial['currency_code'] = self.instance.currency.code if self.instance.currency else ''
            self.initial['currency_name'] = self.instance.currency.name if self.instance.currency else ''
            self.initial['email_msg'] = self.instance.email_msg if self.instance.email_msg else ''
            self.initial['email'] = self.instance.email if self.instance.email else ''
            self.initial['country'] = self.instance.country if self.instance.country else ''
            self.initial['phone'] = self.instance.phone if self.instance.phone else ''
            self.initial['postal_code'] = self.instance.postal_code if self.instance.postal_code else ''
            self.initial['address'] = self.instance.address if self.instance.address else ''

        else:
            company = Company.objects.get(pk=company_id)
            self.initial['account_receivable'] = ''
            self.initial['account_receivable_name'] = ''
            self.initial['account_set'] = ''
            self.initial['interest_profile'] = ''
            self.initial['payment_code'] = ''
            self.initial['payment_term'] = 30
            self.initial['currency'] = ''
            self.initial['tax'] = ''

            self.initial['account_set_id'] = ''
            self.initial['account_set_code'] = ''
            self.initial['account_set_name'] = ''
            self.initial['interest_profile_id'] = ''
            self.initial['interest_profile_code'] = ''
            self.initial['interest_profile_name'] = ''
            self.initial['payment_code_id'] = ''
            self.initial['payment_code_code'] = ''
            self.initial['payment_code_name'] = ''
            self.initial['tax_id'] = ''
            self.initial['tax_code'] = ''
            self.initial['tax_name'] = ''
            self.initial['currency_id'] = ''
            self.initial['currency_code'] = ''
            self.initial['currency_name'] = ''
            self.initial['email_msg'] = ''
            self.initial['email'] = ''
            self.initial['credit_limit'] = 0.00
            self.initial['country'] = ''
            self.initial['phone'] = ''
            self.initial['postal_code'] = ''
            self.initial['address'] = ''

            if company and company.currency:
                self.initial['currency'] = company.currency
                self.initial['currency_id'] = company.currency.id
                self.initial['currency_code'] = company.currency.code
                self.initial['currency_name'] = company.currency.name


class CustomerOldSystemColumn(forms.ModelForm):
    interest_1 = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))
    interest_2 = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))
    interest_3 = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))
    interest_4 = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))
    interest_5 = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))

    accode_ar = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    accode_sal = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    accode_exc = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    accode_int = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    accode_bnk = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    accode_chr = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    center_ar = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    center_sal = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    center_exc = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    center_int = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    center_bnk = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    center_chr = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Customer
        fields = ('interest_1', 'interest_2', 'interest_3', 'interest_4', 'interest_5',
                  'accode_ar', 'accode_sal', 'accode_exc', 'accode_int', 'accode_bnk', 'accode_chr',
                  'center_ar', 'center_sal', 'center_exc', 'center_int', 'center_bnk', 'center_chr')

    def __init__(self, *args, **kwargs):
        super(CustomerOldSystemColumn, self).__init__(*args, **kwargs)
