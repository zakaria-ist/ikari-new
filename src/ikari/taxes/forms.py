from django import forms
from django.forms import ModelChoiceField

from accounts.models import Account, DistributionCode
from currencies.models import Currency
from taxes.models import Tax, TaxAuthority, TaxGroup
from utilities.constants import RETAINAGE_REPORT_TYPES, TAX_BASE_TYPES, TAX_REPORT_LEVEL, TAX_TRX_TYPES, \
    TAX_CALCULATION_METHOD, TAX_TYPE, TAX_TRX_TYPES_2


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + '-' + obj.name


class TaxForm(forms.ModelForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'tax_code'}),
                           error_messages={'required': 'This field is required.'})
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
                           error_messages={'required': 'This field is required.'})
    rate = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
                              error_messages={'required': 'This field is required.'})

    number = forms.IntegerField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))

    # tax type
    tax_group = forms.ChoiceField(choices=(('1', 'Sales Tax'), ('2', 'Purchase Tax')),
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    tax_type = forms.ChoiceField(choices=TAX_TYPE,
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    # tax account code
    tax_account_code = CodeModelChoiceField(queryset=None, required=False, empty_label='Select Account',
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    distribution_code = CodeModelChoiceField(queryset=None, required=False, empty_label='Select Distribution',
                                             widget=forms.Select(attrs={'class': 'form-control'}))
    # year to date G/L
    ytd = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': ""}))
    # month to date G/L
    mtd = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': ""}))
    # year to date doc
    ytdoc = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': ""}))
    # month to date doc
    mtdoc = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': ""}))
    shortname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    update_date = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    class Meta:
        model = Tax
        fields = ('name', 'rate', 'code', 'number', 'ytd', 'mtd', 'ytdoc', 'mtdoc', 'tax_account_code',
                  'tax_type', 'shortname', 'update_date', 'distribution_code', 'tax_group')
        fields_required = ['name', 'rate']

    def __init__(self, company_id, *args, **kwargs):
        super(TaxForm, self).__init__(*args, **kwargs)
        self.fields['tax_account_code'].queryset = Account.objects.filter(company_id=company_id, is_hidden=False,
                                                                          is_active=True).order_by('account_segment', 'code')
        self.fields['distribution_code'].queryset = DistributionCode.objects.filter(is_hidden=False, is_active=True,
                                                                                    company_id=company_id)


class TaxAuthorityForm(forms.ModelForm):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'maxlength': '10'}),
        error_messages={'required': 'This field is required.'})
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    currency = MyModelChoiceField(queryset=None, empty_label='None', required=True,
                                  widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
                                  error_messages={'required': 'This field is required.'})
    retainage_rpt_type = forms.ChoiceField(choices=RETAINAGE_REPORT_TYPES,
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    max_tax_allowable = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 0.0}))
    no_tax_charged_below = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 0.0}))
    tax_base = forms.ChoiceField(choices=TAX_BASE_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    report_level = forms.ChoiceField(choices=TAX_REPORT_LEVEL, widget=forms.Select(attrs={'class': 'form-control'}))
    recoverable_rate = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 0.0}))

    class Meta:
        model = TaxAuthority
        fields = ('code', 'name', 'currency', 'retainage_rpt_type', 'max_tax_allowable', 'no_tax_charged_below',
                  'tax_base', 'report_level', 'recoverable_rate')

    def __init__(self, *args, **kwargs):
        super(TaxAuthorityForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=False)


class TaxGroupForm(forms.ModelForm):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'maxlength': '10'}),
        error_messages={'required': 'This field is required.'})
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    transaction_type = forms.ChoiceField(choices=TAX_TRX_TYPES_2,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    currency = MyModelChoiceField(queryset=None, empty_label='None', required=True,
                                  widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
                                  error_messages={'required': 'This field is required.'})
    calculation_method = forms.ChoiceField(choices=TAX_CALCULATION_METHOD,
                                           widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = TaxGroup
        fields = ('code', 'name', 'transaction_type', 'currency', 'calculation_method')

    def __init__(self, *args, **kwargs):
        super(TaxGroupForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=False)
