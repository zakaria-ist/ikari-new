from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from django import forms


class UserForm(ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}),
                               error_messages={'required': 'This field is required.'})
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}),
        error_messages={'required': 'This field is required.'})
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
                            error_messages={'required': 'This field is required.'})

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        fields_required = ['username', 'password', 'email']


class ChangePasswordForm(forms.Form):
    password_old = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}))
    password_new = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}))
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}),
        error_messages={'required': 'This field is required.'})

    class Meta:
        model = User
        fields = ('old_pass', 'new_pass', 'confirm_pass')
        fields_required = ['old_pass', 'new_pass', 'confirm_pass']


class GroupForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))

    class Meta:
        model = Group
        fields = ('name')
        fields_required = ['name']
