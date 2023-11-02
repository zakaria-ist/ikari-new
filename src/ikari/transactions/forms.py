from transactions.models import TransactionMethod
from django.forms import ModelChoiceField
from transactions.models import Transaction
from accounts.models import Account, AccountType
from currencies.models import Currency
from django import forms


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class TranMethodForm(forms.ModelForm):
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    code = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    update_date = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    is_debit = forms.BooleanField(initial=False, required=False, widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    is_credit = forms.BooleanField(initial=False, required=False, widget=forms.CheckboxInput(attrs={'class': 'styled'}))

    class Meta:
        model = TransactionMethod
        fields = ('name',
                  'code',
                  'is_debit',
                  'is_credit',
                  'update_date'
                  )


class PaymentFormInline(forms.ModelForm):
    currency = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                  widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 120px;'}))
    debit_account = MyModelChoiceField(queryset=None, empty_label='---Select---', required=True,
                                       widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}))
    credit_account = MyModelChoiceField(queryset=None, empty_label='---Select---', required=True,
                                        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}))
    method = MyModelChoiceField(queryset=None, empty_label='---Select---', required=False,
                                widget=forms.Select(attrs={'class': 'form-control'}))
    transaction_date = forms.DateField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'yyyy-mm-dd', 'style': 'width: 120px;', 'required': 'required'}))
    amount = forms.CharField(required=True,
                             widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01',
                                                             'style': 'width: 100px;', 'required': 'required'}))
    remark = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 120px;'}))
    number = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 80px;'}))

    class Meta:
        model = Transaction
        fields = ('method',
                  'transaction_date',
                  'amount',
                  'currency',
                  'remark',
                  'number'
                  )

    def __init__(self, company_id, *args, **kwargs):
        super(PaymentFormInline, self).__init__(*args, **kwargs)
        if company_id:
            account_list_qs = Account.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
            self.fields['debit_account'].queryset = account_list_qs.filter(type__is_debit=1)
            self.fields['credit_account'].queryset = account_list_qs.filter(type__is_credit=1)
            self.fields['currency'].queryset = Currency.objects.filter(is_hidden=0)
            self.fields['method'].queryset = TransactionMethod.objects.filter(is_hidden=0, company_id=company_id)

            debit_group_list = []
            credit_group_list = []
            group_list_filter = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])
            for my_type in group_list_filter:

                account_list_debit = account_list_qs.filter(account_group__is_debit=1)
                debit_account = [[account.id, account.name] for account in account_list_debit]

                account_list_credit = account_list_qs.filter(account_group__is_credit=1)
                credit_account = [[account.id, account.name] for account in account_list_credit]

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
