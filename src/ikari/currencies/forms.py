from django import forms
from django.forms import ModelChoiceField
from currencies.models import ExchangeRate
from currencies.models import Currency
from datetime import datetime


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code + ' - ' + obj.name


class ExchangeRateForm(forms.ModelForm):
    from_currency = MyModelChoiceField(queryset=None, empty_label=None, required=True,
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
                                       error_messages={'required': 'This field is required.'})
    to_currency = MyModelChoiceField(queryset=None, empty_label=None, required=True,
                                     widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
                                     error_messages={'required': 'This field is required.'})
    rate = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
                              required=True,
                              error_messages={'required': 'This field is required.'}, max_digits=20, decimal_places=10)
    exchange_date = forms.CharField(
        widget=forms.TextInput(
            attrs={'value': datetime.now().strftime('%Y-%m-%d'),
                   'class': 'form-control form-control-inline input-medium default-date-picker',
                   'required': 'required'}), required=True,
        error_messages={'required': 'This field is required.'})
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = ExchangeRate
        fields = ('from_currency', 'to_currency', 'rate', 'exchange_date', 'description')
        fields_required = ['from_currency', 'to_currency', 'rate', 'exchange_date']

    def __init__(self, *args, **kwargs):
        super(ExchangeRateForm, self).__init__(*args, **kwargs)
        self.fields['from_currency'].queryset = Currency.objects.filter(is_hidden=0)
        self.fields['to_currency'].queryset = Currency.objects.filter(is_hidden=0)
