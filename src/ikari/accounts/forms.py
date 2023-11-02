from django import forms
from django.forms import ModelChoiceField

from accounts.models import Account, AccountSet, RevaluationCode
from companies.models import Company
from currencies.models import Currency
from utilities.constants import SOURCE_TYPES_GL_KEY


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class AccountSetForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    currency = CodeModelChoiceField(queryset=Currency.objects.none(),
                                    required=True,
                                    widget=forms.Select(attrs={'class': 'form-control',
                                                               'required': 'required'}))
    control_account = CodeModelChoiceField(queryset=Account.objects.none(),
                                           required=True,
                                           widget=forms.Select(attrs={'class': 'form-control account-select',
                                                                      'required': 'required'}))
    discount_account = CodeModelChoiceField(queryset=Account.objects.none(),
                                           required=True,
                                           widget=forms.Select(attrs={'class': 'form-control account-select',
                                                                      'required': 'required'}))
    prepayment_account = CodeModelChoiceField(queryset=Account.objects.none(),
                                           required=True,
                                           widget=forms.Select(attrs={'class': 'form-control account-select',
                                                                      'required': 'required'}))
    writeoff_account = CodeModelChoiceField(queryset=Account.objects.none(),
                                           required=False,
                                           widget=forms.Select(attrs={'class': 'form-control account-select',
                                                                      'required': 'required'}))
    revaluation_account = CodeModelChoiceField(queryset=Account.objects.none(),
                                               required=False,
                                               empty_label='Select Account',
                                               widget=forms.Select(
                                                   attrs={'class': 'form-control'}))
    control_account_name = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    discount_account_name = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    prepayment_account_name = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    writeoff_account_name = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    revaluation_account_name = forms.CharField(required=False,
                                               widget=forms.TextInput(
                                                   attrs={'class': 'form-control', 'readonly': 'true'}))

    # Revaluation accounts

    revaluation_unrealized_gain = CodeModelChoiceField(queryset=Account.objects.none(),
                                                       required=False,
                                                       empty_label='Select Account',
                                                       widget=forms.Select(
                                                           attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_unrealized_gain_name = forms.CharField(required=False,
                                                       widget=forms.TextInput(
                                                           attrs={'class': 'form-control', 'readonly': 'true'}))

    revaluation_unrealized_loss = CodeModelChoiceField(queryset=Account.objects.none(),
                                                       required=False,
                                                       empty_label='Select Account',
                                                       widget=forms.Select(
                                                           attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_unrealized_loss_name = forms.CharField(required=False,
                                                       widget=forms.TextInput(
                                                           attrs={'class': 'form-control', 'readonly': 'true'}))

    revaluation_realized_gain = CodeModelChoiceField(queryset=Account.objects.none(),
                                                     required=False,
                                                     empty_label='Select Account',
                                                     widget=forms.Select(
                                                         attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_realized_gain_name = forms.CharField(required=False,
                                                     widget=forms.TextInput(
                                                         attrs={'class': 'form-control', 'readonly': 'true'}))

    revaluation_realized_loss = CodeModelChoiceField(queryset=Account.objects.none(),
                                                     required=False,
                                                     empty_label='Select Account',
                                                     widget=forms.Select(
                                                         attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_realized_loss_name = forms.CharField(required=False,
                                                     widget=forms.TextInput(
                                                         attrs={'class': 'form-control', 'readonly': 'true'}))

    revaluation_rounding = CodeModelChoiceField(queryset=Account.objects.none(),
                                                required=False,
                                                empty_label='Select Account',
                                                widget=forms.Select(
                                                    attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_rounding_name = forms.CharField(required=False,
                                                widget=forms.TextInput(
                                                    attrs={'class': 'form-control', 'readonly': 'true'}))

    currency_name = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))

    class Meta:
        model = AccountSet
        fields = ('code', 'name', 'currency', 'control_account', 'discount_account', 
                  'prepayment_account', 'writeoff_account', 'revaluation_account',
                  'control_account_name', 'discount_account_name', 'prepayment_account_name', 
                  'writeoff_account_name', 'revaluation_account_name', 'currency_name',
                  'revaluation_unrealized_gain',  'revaluation_unrealized_gain_name', 
                  'revaluation_unrealized_loss', 'revaluation_unrealized_loss_name', 
                  'revaluation_realized_gain', 'revaluation_realized_gain_name', 
                  'revaluation_realized_loss', 'revaluation_realized_loss_name', 
                  'revaluation_rounding', 'revaluation_rounding_name')

    def __init__(self, request, *args, **kwargs):
        super(AccountSetForm, self).__init__(*args, **kwargs)
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        account_list = Account.objects.filter(
            is_hidden=False, is_active=True, company_id=company_id).order_by('account_segment', 'code')

        self.fields['control_account'].queryset = account_list
        self.fields['discount_account'].queryset = account_list
        self.fields['prepayment_account'].queryset = account_list
        self.fields['writeoff_account'].queryset = account_list
        self.fields['revaluation_account'].queryset = account_list.order_by('code')
        self.fields['revaluation_unrealized_gain'].queryset = account_list.order_by('code')
        self.fields['revaluation_unrealized_loss'].queryset = account_list.order_by('code')
        self.fields['revaluation_realized_gain'].queryset = account_list.order_by('code')
        self.fields['revaluation_realized_loss'].queryset = account_list.order_by('code')
        self.fields['revaluation_rounding'].queryset = account_list.order_by('code')
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=False).order_by('code')

        if self.instance.id:
            self.initial['control_account'] = self.instance.control_account if self.instance.control_account else ''
            self.initial['discount_account'] = self.instance.discount_account if self.instance.discount_account else ''
            self.initial['prepayment_account'] = self.instance.prepayment_account if self.instance.prepayment_account else ''
            self.initial['writeoff_account'] = self.instance.writeoff_account if self.instance.writeoff_account else ''
            self.initial['revaluation_account'] = self.instance.revaluation_account \
                if self.instance.revaluation_account else ''
            self.initial['currency'] = self.instance.currency if self.instance.currency else ''

            self.initial['control_account_name'] = self.instance.control_account.name \
                if self.instance.control_account else ''
            self.initial['discount_account_name'] = self.instance.discount_account.name \
                if self.instance.discount_account else ''
            self.initial['prepayment_account_name'] = self.instance.prepayment_account.name \
                if self.instance.prepayment_account else ''
            self.initial['writeoff_account_name'] = self.instance.writeoff_account.name \
                if self.instance.writeoff_account else ''
            self.initial['revaluation_account_name'] = self.instance.revaluation_account.name \
                if self.instance.revaluation_account else ''

            self.initial['revaluation_unrealized_gain_name'] = self.instance.revaluation_unrealized_gain.name \
                if self.instance.revaluation_unrealized_gain else ''
            self.initial['revaluation_unrealized_loss_name'] = self.instance.revaluation_unrealized_loss.name \
                if self.instance.revaluation_unrealized_loss else ''
            self.initial['revaluation_realized_gain_name'] = self.instance.revaluation_realized_gain.name \
                if self.instance.revaluation_realized_gain else ''
            self.initial['revaluation_realized_loss_name'] = self.instance.revaluation_realized_loss.name \
                if self.instance.revaluation_realized_loss else ''
            self.initial['revaluation_rounding_name'] = self.instance.revaluation_rounding.name \
                if self.instance.revaluation_rounding else ''

            self.initial['currency_name'] = self.instance.currency.name if self.instance.currency else ''

        else:
            company = Company.objects.get(pk=company_id)
            self.initial['control_account'] = ''
            self.initial['revaluation_account'] = ''
            self.initial['currency'] = ''
            self.initial['control_account_name'] = ''
            self.initial['discount_account_name'] = ''
            self.initial['prepayment_account_name'] = ''
            self.initial['writeoff_account_name'] = ''
            self.initial['revaluation_account_name'] = ''
            self.initial['revaluation_unrealized_gain'] = ''
            self.initial['revaluation_unrealized_loss'] = ''
            self.initial['revaluation_realized_gain'] = ''
            self.initial['revaluation_realized_loss'] = ''
            self.initial['revaluation_rounding'] = ''
            self.initial['revaluation_unrealized_gain_name'] = ''
            self.initial['revaluation_unrealized_loss_name'] = ''
            self.initial['revaluation_realized_gain_name'] = ''
            self.initial['revaluation_realized_loss_name'] = ''
            self.initial['revaluation_rounding_name'] = ''
            self.initial['currency_name'] = ''

            if company and company.currency:
                self.initial['currency'] = company.currency
                self.initial['currency_name'] = company.currency.name

class RevaluationCodeForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required',
                                                         'tabindex': '-1'}))
    description = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    rate_type = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    rate_type_name = forms.CharField(required=False,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    source_type = forms.ChoiceField(required=True,
                                  choices=SOURCE_TYPES_GL_KEY)
    
    # Revaluation accounts

    revaluation_unrealized_gain = CodeModelChoiceField(queryset=Account.objects.none(),
                                                       required=False,
                                                       empty_label='Select Account',
                                                       widget=forms.Select(
                                                           attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_unrealized_gain_name = forms.CharField(required=False,
                                                       widget=forms.TextInput(
                                                           attrs={'class': 'form-control', 'readonly': 'true',
                                                                  'tabindex': '-1'}))

    revaluation_unrealized_loss = CodeModelChoiceField(queryset=Account.objects.none(),
                                                       required=False,
                                                       empty_label='Select Account',
                                                       widget=forms.Select(
                                                           attrs={'class': 'form-control revaluation-account-select'}))

    revaluation_unrealized_loss_name = forms.CharField(required=False,
                                                       widget=forms.TextInput(
                                                           attrs={'class': 'form-control', 'readonly': 'true',
                                                                  'tabindex': '-1'}))

    class Meta:
        model = RevaluationCode
        fields = ('code', 'description', 'rate_type', 'source_type', 'revaluation_unrealized_gain',  'revaluation_unrealized_gain_name', 
                  'revaluation_unrealized_loss', 'revaluation_unrealized_loss_name')

    def __init__(self, request, *args, **kwargs):
        super(RevaluationCodeForm, self).__init__(*args, **kwargs)
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        account_list = Account.objects.filter(
            is_hidden=False, is_active=True, company_id=company_id).order_by('account_segment', 'code')

        self.fields['revaluation_unrealized_gain'].queryset = account_list.order_by('code')
        self.fields['revaluation_unrealized_loss'].queryset = account_list.order_by('code')
        
        if self.instance.id:
            self.initial['revaluation_unrealized_gain_name'] = self.instance.revaluation_unrealized_gain.name \
                if self.instance.revaluation_unrealized_gain else ''
            self.initial['revaluation_unrealized_loss_name'] = self.instance.revaluation_unrealized_loss.name \
                if self.instance.revaluation_unrealized_loss else ''

        else:
            company = Company.objects.get(pk=company_id)
            self.initial['description'] = ''
            self.initial['revaluation_unrealized_gain'] = ''
            self.initial['revaluation_unrealized_loss'] = ''
            self.initial['revaluation_unrealized_gain_name'] = ''
            self.initial['revaluation_unrealized_loss_name'] = ''
