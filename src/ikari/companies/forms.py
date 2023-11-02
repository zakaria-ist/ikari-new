from django import forms
from companies.models import CostCenters


class CostCentersForm(forms.ModelForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
                           error_messages={'required': 'This field is required.'})
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'}), required=False)
    update_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = CostCenters
        fields = ('name', 'code', 'description', 'address', 'postal_code', 'phone', 'email')
        fields_required = ['code']

class SegmentForm(forms.ModelForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
                           error_messages={'required': 'This field is required.'})
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                           error_messages={'required': 'This field is required.'}, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    update_date = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    
    class Meta:
        model = CostCenters
        fields = ('name', 'description', 'code', 'update_date')
        fields_required = ['code']

    def __init__(self, company_id, *args, **kwargs):
        super(SegmentForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.initial['name'] = self.instance.name if self.instance.name else ''
            self.initial['code'] = self.instance.code if self.instance.code else ''
            self.initial['description'] = self.instance.description if self.instance.description else ''
