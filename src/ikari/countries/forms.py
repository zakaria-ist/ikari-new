from django import forms

from countries.models import Country
from utilities.constants import ATTRS_TXT
from utilities.common import get_form_field_attr


class CompanyForm(forms.ModelForm):
    name = forms.CharField(
        max_length=250,
        required=True,
        widget=forms.TextInput(
            attrs=get_form_field_attr(ATTRS_TXT, 'Company Name', required=True, autofocus=True)
        )
    )

    class Meta:
        model = Country
        fields = ['name', ]