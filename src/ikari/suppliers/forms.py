from django import forms
from django.forms import ModelChoiceField

from accounting.models import PaymentCode
from accounts.models import Account, AccountSet, DistributionCode
from banks.models import Bank
from companies.models import Company
from countries.models import Country
from currencies.models import Currency
from suppliers.models import Supplier
from taxes.models import Tax
from utilities.constants import TERMS_CODE, DIS_CODE_TYPE_REVERSED, ACCOUNT_SET_TYPE_DICT, DIS_CODE_TYPE_DICT, \
    TAX_TRX_TYPES_DICT, PAYMENT_CODE_TYPE_DICT


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code

class CountryCodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class TaxNameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class AccVendorInfoForm(forms.ModelForm):
    account_payable = CodeModelChoiceField(queryset=Account.objects.none(),
                                       required=False,
                                       empty_label='Select Account Payable',
                                       widget=forms.Select(attrs={'class': 'form-control'}))
    account_payable_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=True,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    account_set_id = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    code = forms.CharField(required=True, max_length=20,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'autofocus': 'true'}))

    account_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    term_days = forms.ChoiceField(choices=TERMS_CODE, required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    bank_code = CodeModelChoiceField(queryset=Bank.objects.none(), required=True,
                                     empty_label='Select Bank Set',
                                     widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    bank_name = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    bank_id = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    credit_limit = forms.DecimalField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0.00', 'max': '99999999999999'}))
    term_days = forms.ChoiceField(choices=TERMS_CODE, required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    payment_code_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_code_code = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_code_name = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=False, empty_label='Select Payment Code',
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    tax = TaxNameChoiceField(queryset=Tax.objects.none(), required=False,
                             empty_label='Select Tax Code',
                             widget=forms.Select(attrs={'class': 'form-control'}))
    tax_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    tax_code = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    tax_name = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    distribution = CodeModelChoiceField(queryset=DistributionCode.objects.none(), required=False,
                                        empty_label='Select Tax Code',
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    dis_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    dis_code = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    dis_name = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                    widget=forms.Select(attrs={'class': 'form-control no-select', 'disabled': 'disabled'
                                                               }))
    country = CountryCodeModelChoiceField(queryset=Country.objects.none(), required=False, empty_label='',
                                    widget=forms.Select(attrs={'class': 'form-control no-select'
                                                               }))
    currency_id = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    currency_code = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    currency_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email_msg = forms.CharField(required=False,
                                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    address = forms.CharField(required=False,
                                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    postal_code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Supplier
        fields = ('account_set', 'account_set_id', 'account_name', 'bank_id', 'address', 'postal_code', 'phone', 'country',
                  'term_days', 'bank_code', 'name', 'code', 'credit_limit', 'term_days', 'bank_name', 'payment_code_id', 'payment_code_code', 'payment_code', 'currency',
                  'currency_id', 'currency_code', 'currency_name', 'email', 'email_msg', 'account_payable', 'account_payable_name')

    def __init__(self, request, *args, **kwargs):
        super(AccVendorInfoForm, self).__init__(*args, **kwargs)
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.fields['name'].queryset = Supplier.objects.filter(is_hidden=False, is_active=True,
                                                               company_id=company_id).order_by('code')
        self.fields['account_set'].queryset = AccountSet.objects.filter(
            is_hidden=False,
            is_active=True,
            company_id=company_id,
            type=ACCOUNT_SET_TYPE_DICT['AP Account Set']
        ).order_by('code')
        self.fields['account_payable'].queryset = Account.objects.filter(is_hidden=False, is_active=True,
                                                                         company_id=company_id).order_by('account_segment', 'code')
        self.fields['bank_code'].queryset = Bank.objects.filter(is_hidden=False, is_active=True,
                                                                company_id=company_id).order_by('code')
        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=False).order_by('code')
        self.fields['country'].queryset = Country.objects.filter(is_hidden=False).order_by('code')
        self.fields['tax'].queryset = Tax.objects.filter(
            is_hidden=0,
            company_id=company_id,
            tax_group__company_id=company_id,
            tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases'])).order_by('code')
        self.fields['distribution'].queryset = DistributionCode.objects.filter(
            is_hidden=False, is_active=True,
            company_id=company_id,
            type=DIS_CODE_TYPE_DICT['AP Distribution Code']).order_by('code')

        if self.instance.id:
            self.initial['account_payable'] = self.instance.account_payable if self.instance.account_payable else ''
            self.initial['account_payable_name'] = self.instance.account_payable.name if self.instance.account_payable else ''
            self.initial['account_set'] = self.instance.account_set if self.instance.account_set else ''
            self.initial['account_set_id'] = self.instance.account_set.id if self.instance.account_set else ''
            self.initial['account_name'] = self.instance.account_set.name if self.instance.account_set else ''
            self.initial['payment_code'] = self.instance.payment_code if self.instance.payment_code else ''
            self.initial['payment_code_id'] = self.instance.payment_code.id if self.instance.payment_code else ''
            self.initial['payment_code_code'] = self.instance.payment_code.code if self.instance.payment_code else ''
            self.initial['payment_code_name'] = self.instance.payment_code.name if self.instance.payment_code else ''
            self.initial['bank_id'] = self.instance.bank.id if self.instance.bank else ''
            self.initial['bank_code'] = self.instance.bank if self.instance.bank else ''
            self.initial['bank_name'] = self.instance.bank.name if self.instance.bank else ''
            try:
                self.initial['tax'] = self.instance.tax if self.instance.tax else None
                self.initial['tax_id'] = self.instance.tax.id if self.instance.tax else ''
                self.initial['tax_code'] = self.instance.tax.code if self.instance.tax else ''
                self.initial['tax_name'] = self.instance.tax.name if self.instance.tax else ''
            except:
                self.initial['tax'] = None
                self.initial['tax_id'] = ''
                self.initial['tax_code'] = ''
                self.initial['tax_name'] = ''
            self.initial['distribution'] = self.instance.distribution if self.instance.distribution else ''
            self.initial['dis_id'] = self.instance.distribution.id if self.instance.distribution else ''
            self.initial['dis_code'] = self.instance.distribution.code if self.instance.distribution else ''
            self.initial['dis_name'] = self.instance.distribution.name if self.instance.distribution else ''
            self.initial['term_days'] = self.instance.term_days if self.instance.term_days else ''
            self.initial['currency'] = self.instance.currency if self.instance.currency else ''
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
            self.initial['account_payable'] = ''
            self.initial['account_payable_name'] = ''
            self.initial['account_code'] = ''
            self.initial['account_set'] = ''
            self.initial['account_set_id'] = ''
            self.initial['account_name'] = ''
            self.initial['payment_code'] = ''
            self.initial['payment_code_id'] = ''
            self.initial['payment_code_code'] = ''
            self.initial['payment_code_name'] = ''
            self.initial['tax'] = ''
            self.initial['bank_id'] = ''
            self.initial['bank_code'] = ''
            self.initial['bank_name'] = ''
            self.initial['tax_id'] = ''
            self.initial['tax_code'] = ''
            self.initial['tax_name'] = ''
            self.initial['distribution'] = ''
            self.initial['dis_id'] = ''
            self.initial['dis_code'] = ''
            self.initial['dis_name'] = ''
            self.initial['term_days'] = ''
            self.initial['currency'] = ''
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

            company = Company.objects.get(pk=company_id)
            if company and company.currency:
                self.initial['currency'] = company.currency
                self.initial['currency_id'] = company.currency.id
                self.initial['currency_code'] = company.currency.code
                self.initial['currency_name'] = company.currency.name


class SupplierInfoForm(forms.ModelForm):
    account_set = CodeModelChoiceField(queryset=AccountSet.objects.none(),
                                       required=False,
                                       empty_label='Select Account Set',
                                       widget=forms.Select(attrs={'class': 'form-control'}))

    account_set_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))

    term_days = forms.ChoiceField(choices=TERMS_CODE, required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    payment_code_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    payment_code_code = forms.CharField(required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))

    payment_code = CodeModelChoiceField(queryset=PaymentCode.objects.none(),
                                        required=False, empty_label='Select Payment Code',
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    tax = CodeModelChoiceField(queryset=Tax.objects.none(), required=False,
                               empty_label='Select Tax Code',
                               widget=forms.Select(attrs={'class': 'form-control'}))
    tax_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    tax_code = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))

    currency = MyModelChoiceField(queryset=Currency.objects.none(), required=False, empty_label='',
                                    widget=forms.Select(attrs={'class': 'form-control no-select'
                                                               }))
    currency_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    currency_code = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    country = MyModelChoiceField(queryset=Country.objects.none(), required=False,
                                   empty_label='Select Country Code',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    country_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    country_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    distribution = CodeModelChoiceField(queryset=DistributionCode.objects.none(), required=False,
                                        empty_label='Select distribution Code',
                                        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Supplier
        fields = (
            'currency', 'currency_id', 'currency_code', 'tax', 'tax_id', 'tax_code',
            'account_set', 'account_set_id', 'payment_code_id', 'payment_code_code',
            'payment_code', 'term_days', 'country', 'country_id', 'country_code', 'distribution'
        )

    def __init__(self, request, *args, **kwargs):
        super(SupplierInfoForm, self).__init__(*args, **kwargs)
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        try:
            company = Company.objects.get(pk=company_id, is_hidden=False)
            if company:
                is_inventory = company.is_inventory
        except:
            is_inventory = False

        self.fields['account_set'].queryset = AccountSet.objects.filter(
            is_hidden=False, is_active=True,
            company_id=company_id,
            type=ACCOUNT_SET_TYPE_DICT['AP Account Set']).order_by('code')

        self.fields['payment_code'].queryset = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                                    company_id=company_id, 
                                                                    source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']) \
            .order_by('code')
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=False).order_by('code')
        if is_inventory:
            tax_list = Tax.objects.filter(is_hidden=False, company_id=company_id).order_by('code')
        else:
            tax_list = Tax.objects.filter(is_hidden=False,
                                          company_id=company_id,
                                          tax_group__company_id=company_id,
                                          tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))\
                .order_by('code')
        self.fields['tax'].queryset = tax_list
        self.fields['country'].queryset = Country.objects.filter(is_hidden=False).order_by('code')
        self.fields['distribution'].queryset = DistributionCode.objects. \
            filter(is_hidden=False, company_id=company_id, type=dict(DIS_CODE_TYPE_REVERSED)['AP Distribution Code']). \
            order_by('code')

        if self.instance.id:
            self.initial['account_set'] = self.instance.account_set if self.instance.account_set else ''
            self.initial['account_set_id'] = self.instance.account_set.id if self.instance.account_set else ''
            self.initial['payment_code'] = self.instance.payment_code if self.instance.payment_code else ''
            self.initial['payment_code_id'] = self.instance.account_set.id if self.instance.account_set else ''
            self.initial['payment_code_code'] = self.instance.account_set.code if self.instance.account_set else ''
            self.initial['tax'] = self.instance.tax if self.instance.tax else ''
            self.initial['tax_id'] = self.instance.tax.id if self.instance.tax else ''
            self.initial['tax_code'] = self.instance.tax.code if self.instance.tax else ''
            self.initial['term_days'] = self.instance.term_days if self.instance.term_days else ''
            self.initial['currency'] = self.instance.currency if self.instance.currency else ''
            self.initial['currency_id'] = self.instance.currency.id if self.instance.currency else ''
            self.initial['currency_code'] = self.instance.currency.code if self.instance.currency else ''
            self.initial['country'] = self.instance.country if self.instance.country else ''
            self.initial['country_id'] = self.instance.country.id if self.instance.country else ''
            self.initial['country_code'] = self.instance.country.code if self.instance.country else ''
            self.initial['distribution'] = self.instance.distribution.code if self.instance.distribution else ''

        else:
            self.initial['account_set'] = ''
            self.initial['account_set_id'] = ''
            self.initial['payment_code'] = ''
            self.initial['payment_code_id'] = ''
            self.initial['payment_code_code'] = ''
            self.initial['tax'] = ''
            self.initial['tax_id'] = ''
            self.initial['tax_code'] = ''
            self.initial['term_days'] = ''
            self.initial['currency'] = ''
            self.initial['currency_id'] = ''
            self.initial['currency_code'] = ''
            self.initial['country'] = ''
            self.initial['country_id'] = ''
            self.initial['country_code'] = ''
            self.initial['distribution'] = ''

            company = Company.objects.get(pk=company_id)
            if company and company.currency:
                self.initial['currency'] = company.currency
                self.initial['currency_id'] = company.currency.id
                self.initial['currency_code'] = company.currency.code
