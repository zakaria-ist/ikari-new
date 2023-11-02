from django.forms import ModelChoiceField
from currencies.models import Currency
from banks.models import Bank
from accounts.models import Account
from django import forms


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class BankForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    account = CodeModelChoiceField(queryset=Account.objects.none(), required=False,
                                   empty_label='Select Account',
                                   widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    gain_account = CodeModelChoiceField(queryset=Account.objects.none(), required=False,
                                   empty_label='Select Account',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    loss_account = CodeModelChoiceField(queryset=Account.objects.none(), required=False,
                                   empty_label='Select Account',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    round_account = CodeModelChoiceField(queryset=Account.objects.none(), required=False,
                                   empty_label='Select Account',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    currency = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(initial=True, required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    account_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    account_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    account_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    gain_account_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    gain_account_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    gain_account_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    loss_account_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    loss_account_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    loss_account_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    round_account_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control hidden'}))
    round_account_code = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    round_account_name = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}))
    update_date = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    class Meta:
        model = Bank
        fields = ('code', 'name', 'currency', 'update_date', 'is_active',
                  'account', 'gain_account', 'loss_account', 'round_account'
                  )

    def __init__(self, company_id, *args, **kwargs):
        super(BankForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)

        if company_id:
            self.fields['account'].queryset = Account.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.initial['account_id'] = self.instance.account.id if self.instance.account else ''
            self.initial['account_code'] = self.instance.account.code if self.instance.account else ''
            self.initial['account_name'] = self.instance.account.name if self.instance.account else ''
            self.fields['gain_account'].queryset = Account.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.initial['gain_account_id'] = self.instance.gain_account.id if self.instance.gain_account else ''
            self.initial['gain_account_code'] = self.instance.gain_account.code if self.instance.gain_account else ''
            self.initial['gain_account_name'] = self.instance.gain_account.name if self.instance.gain_account else ''
            self.fields['loss_account'].queryset = Account.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.initial['loss_account_id'] = self.instance.loss_account.id if self.instance.loss_account else ''
            self.initial['loss_account_code'] = self.instance.loss_account.code if self.instance.loss_account else ''
            self.initial['loss_account_name'] = self.instance.loss_account.name if self.instance.loss_account else ''
            self.fields['round_account'].queryset = Account.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.initial['round_account_id'] = self.instance.round_account.id if self.instance.round_account else ''
            self.initial['round_account_code'] = self.instance.round_account.code if self.instance.round_account else ''
            self.initial['round_account_name'] = self.instance.round_account.name if self.instance.round_account else ''

