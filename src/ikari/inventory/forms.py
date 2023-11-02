import datetime

from django import forms
from django.forms import ModelChoiceField

from companies.models import Company
from inventory.models import TransactionCode, StockTransaction, StockTransactionDetail
from locations.models import Location
from utilities.constants import INV_IN_OUT_FLAG, INV_PRICE_FLAG, INV_DOC_TYPE, COSTING_METHOD, TRN_CODE_TYPE_DICT, \
    SLS_NUM_DOC_TYPE, PUR_NUM_DOC_TYPE


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class TransCodeForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(
                               attrs={'class': 'form-control', 'required': 'required', 'maxlength': 10}))
    name = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    io_flag = forms.ChoiceField(choices=tuple([status[::-1] for status in INV_IN_OUT_FLAG]), required=False,
                                widget=forms.Select(attrs={'class': 'form-control'}))
    price_flag = forms.ChoiceField(choices=INV_PRICE_FLAG, required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    doc_type = forms.ChoiceField(choices=(('', '--select document type--'),))
    AUTO_GEN_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )
    auto_generate = forms.BooleanField(widget=forms.RadioSelect(choices=AUTO_GEN_CHOICES),
                                       required=False, initial=True)
    ics_prefix = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_no = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    update_date = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    class Meta:
        model = TransactionCode
        fields = (
            'code', 'name', 'io_flag', 'price_flag', 'doc_type', 'auto_generate', 'ics_prefix', 'update_date', 'last_no')

    def __init__(self, menu_type=None, *args, **kwargs):
        super(TransCodeForm, self).__init__(*args, **kwargs)
        if int(menu_type) == int(TRN_CODE_TYPE_DICT['Inventory Code']):
            self.fields['doc_type'] = forms.ChoiceField(choices=INV_DOC_TYPE, required=False,
                                                        widget=forms.Select(attrs={'class': 'form-control'}))
        elif int(menu_type) == int(TRN_CODE_TYPE_DICT['Sales Number File']):
            self.fields['doc_type'] = forms.ChoiceField(choices=SLS_NUM_DOC_TYPE, required=False,
                                                        widget=forms.Select(attrs={'class': 'form-control'}))
        elif int(menu_type) == int(TRN_CODE_TYPE_DICT['Purchase Number File']):
            self.fields['doc_type'] = forms.ChoiceField(choices=PUR_NUM_DOC_TYPE, required=False,
                                                        widget=forms.Select(attrs={'class': 'form-control'}))


class file_control(forms.ModelForm):
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Company Address'}),
        required=False)
    name = forms.CharField(required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    currency = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    costing_method = forms.BooleanField(widget=forms.RadioSelect(choices=COSTING_METHOD, attrs={'disabled': 'true'}),
                                        required=False, initial=True)
    AUTO_GEN_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )
    decimal_amount = forms.BooleanField(widget=forms.RadioSelect(choices=AUTO_GEN_CHOICES, attrs={'disabled': 'true'}),
                                        required=False, initial=True)
    fiscal_period = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium', 'data-date-format': 'mm-yyyy', 'disabled': 'true'}))
    current_Period = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-date-format': 'mm-yyyy', 'disabled': 'true'}))
    closing_date = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'mm-yyyy', 'disabled': 'true'}))
    update_date = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    cl_1 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_2 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_3 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_4 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_5 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_6 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_7 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_8 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_9 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_10 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_11 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    cl_12 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker',
               'data-date-format': 'dd-mm-yyyy'}))
    op_1 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_2 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_3 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_4 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_5 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_6 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_7 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_8 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_9 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_10 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_11 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    op_12 = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-inline input-medium default-date-picker hide',
               'data-date-format': 'yyyy-mm-dd'}))
    code_size = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    category_size = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    extent_item = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    group_item = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    uom_item = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    stock_take = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))
    price_decimal = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    class Meta:
        model = Company
        fields = (
            'code_size', 'category_size', 'extent_item', 'group_item', 'uom_item', 'stock_take', 'price_decimal',
            'address', 'name', 'code',
            'closing_date', 'update_date', 'country', 'phone', 'currency', 'fiscal_period', 'current_period_month',
            'current_period_year')

    def __init__(self, company_id, fiscal_array, *args, **kwargs):
        super(file_control, self).__init__(*args, **kwargs)
        company = Company.objects.get(pk=company_id)
        self.initial['address'] = company.address
        self.initial['name'] = company.name
        self.initial['fiscal_period'] = company.fiscal_period.strftime("%m-%Y")
        self.initial['current_period_month_ic'] = company.current_period_month_ic
        self.initial['current_period_year_ic'] = company.current_period_year_ic
        if fiscal_array:
            self.initial['cl_1'] = fiscal_array[0]['end_date'] if fiscal_array[0]['end_date'] else ''
            self.initial['cl_2'] = fiscal_array[1]['end_date'] if fiscal_array[1]['end_date'] else ''
            self.initial['cl_3'] = fiscal_array[2]['end_date'] if fiscal_array[2]['end_date'] else ''
            self.initial['cl_4'] = fiscal_array[3]['end_date'] if fiscal_array[3]['end_date'] else ''
            self.initial['cl_5'] = fiscal_array[4]['end_date'] if fiscal_array[4]['end_date'] else ''
            self.initial['cl_6'] = fiscal_array[5]['end_date'] if fiscal_array[5]['end_date'] else ''
            self.initial['cl_7'] = fiscal_array[6]['end_date'] if fiscal_array[6]['end_date'] else ''
            self.initial['cl_8'] = fiscal_array[7]['end_date'] if fiscal_array[7]['end_date'] else ''
            self.initial['cl_9'] = fiscal_array[8]['end_date'] if fiscal_array[8]['end_date'] else ''
            self.initial['cl_10'] = fiscal_array[9]['end_date'] if fiscal_array[9]['end_date'] else ''
            self.initial['cl_11'] = fiscal_array[10]['end_date'] if fiscal_array[10]['end_date'] else ''
            self.initial['cl_12'] = fiscal_array[11]['end_date'] if fiscal_array[11]['end_date'] else ''

            self.initial['op_1'] = fiscal_array[0]['start_date'] if fiscal_array[0]['start_date'] else ''
            self.initial['op_2'] = fiscal_array[1]['start_date'] if fiscal_array[1]['start_date'] else ''
            self.initial['op_3'] = fiscal_array[2]['start_date'] if fiscal_array[2]['start_date'] else ''
            self.initial['op_4'] = fiscal_array[3]['start_date'] if fiscal_array[3]['start_date'] else ''
            self.initial['op_5'] = fiscal_array[4]['start_date'] if fiscal_array[4]['start_date'] else ''
            self.initial['op_6'] = fiscal_array[5]['start_date'] if fiscal_array[5]['start_date'] else ''
            self.initial['op_7'] = fiscal_array[6]['start_date'] if fiscal_array[6]['start_date'] else ''
            self.initial['op_8'] = fiscal_array[7]['start_date'] if fiscal_array[7]['start_date'] else ''
            self.initial['op_9'] = fiscal_array[8]['start_date'] if fiscal_array[8]['start_date'] else ''
            self.initial['op_10'] = fiscal_array[9]['start_date'] if fiscal_array[9]['start_date'] else ''
            self.initial['op_11'] = fiscal_array[10]['start_date'] if fiscal_array[10]['start_date'] else ''
            self.initial['op_12'] = fiscal_array[11]['start_date'] if fiscal_array[11]['start_date'] else ''
        self.initial['closing_date'] = company.closing_date.strftime("%d-%m-%Y")
        self.initial['group_item'] = company.group_item
        self.initial['update_date'] = company.update_date.strftime("%d-%m-%Y")
        self.initial['cost_method'] = company.cost_method

        # Now it's not used, so we hardcode
        self.initial['code_size'] = 25  # company.code_size
        self.initial['category_size'] = 1  # company.category_size
        self.initial['extent_item'] = 1  # company.extent_item
        self.initial['uom_item'] = 'PCS'  # company.uom_item
        self.initial['stock_take'] = 'S/T'  # company.stock_take
        self.initial['price_decimal'] = 6  # company.price_decimal


class StockTransForm(forms.ModelForm):
    transaction_code = CodeModelChoiceField(queryset=TransactionCode.objects.none(), required=True,
                                            empty_label='Select Transaction Code',
                                            widget=forms.Select(
                                                attrs={'class': 'form-control', 'required': 'required'}))

    document_date_fake = forms.CharField(required=False,
                                         widget=forms.TextInput(
                                             attrs={'value': datetime.datetime.now().strftime('%d-%m-%Y'),
                                                    'class': 'form-control form-control-inline input-medium default-date-picker'}))
    document_date = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'value': datetime.datetime.now().strftime('%Y-%m-%d'),
                                                                  'class': 'form-control form-control-inline input-medium hide'}))
    document_number = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))

    io_flag = forms.CharField(required=False,
                                      widget=forms.HiddenInput(attrs={'class': 'form-control disabled', 'tabindex': '-1'}))

    price_flag = forms.CharField(required=False,
                                      widget=forms.HiddenInput(attrs={'class': 'form-control disabled', 'tabindex': '-1'}))

    io_flag_name = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control disabled', 'tabindex': '-1'}))

    price_flag_name = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control disabled', 'tabindex': '-1'}))

    # io_flag = forms.ChoiceField(choices=tuple([status[::-1] for status in INV_IN_OUT_FLAG]), required=False,
    #                             widget=forms.Select(attrs={'class': 'form-control disabled', 'tabindex': '-1'}))
    # price_flag = forms.ChoiceField(choices=INV_PRICE_FLAG, required=False,
    #                                widget=forms.Select(attrs={'class': 'form-control disabled', 'tabindex': '-1'}))

    doc_type = forms.ChoiceField(choices=INV_DOC_TYPE, required=False,
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    currency_id = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'display: none'}))
    currency = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'tabindex': '-1'}))
    in_location = CodeModelChoiceField(queryset=Location.objects.none(), required=False, empty_label='Select In Location',
                                       widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    out_location = CodeModelChoiceField(queryset=Location.objects.none(), required=False, empty_label='Select Out Location',
                                        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    remark = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = StockTransaction
        fields = (
            'transaction_code', 'document_date', 'document_number', 'io_flag', 'price_flag', 'doc_type',
            'currency_id', 'in_location', 'out_location', 'remark')

    def __init__(self, company_id, *args, **kwargs):
        try:
            self.session_date = kwargs.pop('session_date')
        except:
            self.session_date = None
        super(StockTransForm, self).__init__(*args, **kwargs)
        company = Company.objects.get(pk=company_id)

        doc_type = dict([doc_type[::-1] for doc_type in INV_DOC_TYPE])
        self.fields['transaction_code'].queryset = TransactionCode.objects.filter(is_hidden=False,
                                                                                  company_id=company_id,
                                                                                  menu_type=int(TRN_CODE_TYPE_DICT[
                                                                                                    'Inventory Code']),
                                                                                  doc_type__lte=doc_type['Inventory'])

        self.fields['in_location'].queryset = Location.objects.filter(is_hidden=False, is_active=True,
                                                                      company_id=company_id)
        self.fields['out_location'].queryset = Location.objects.filter(is_hidden=False, is_active=True,
                                                                       company_id=company_id)
        self.fields['currency_id'].initial = company.currency_id
        self.fields['currency'].initial = company.currency.name
        self.fields['document_date'].initial = self.session_date if self.session_date else datetime.datetime.now().strftime('%Y-%m-%d')
        self.fields['document_date_fake'].initial = self.session_date.strftime('%d-%m-%Y') if self.session_date else datetime.datetime.now().strftime('%d-%m-%Y')

        if self.instance.id:
            if self.instance.document_date:
                self.fields['document_date_fake'].initial = self.instance.document_date.strftime("%d-%m-%Y")
            if self.instance.currency:
                self.fields['currency_id'].initial = self.instance.currency_id
                self.fields['currency'].initial = self.instance.currency.name
            if self.instance.transaction_code:
                self.fields['transaction_code'].queryset = TransactionCode.objects.filter(
                    pk=self.instance.transaction_code.id)
                if self.instance.transaction_code.auto_generate:
                    self.fields['document_number'].widget.attrs['class'] = 'form-control disabled'
            if self.instance.price_flag:
                price_flag_dict = dict(INV_PRICE_FLAG)
                self.fields['price_flag_name'].initial = price_flag_dict.get(self.instance.price_flag)
            if self.instance.io_flag:
                io_flag_dict = dict([status[::-1] for status in INV_IN_OUT_FLAG])
                self.fields['io_flag_name'].initial = io_flag_dict.get(self.instance.io_flag)




class StockTransItemForm(forms.ModelForm):
    line_number = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'display: none'}))
    item_inv_measure = forms.CharField(required=False,
                                       widget=forms.TextInput(
                                           attrs={'class': 'form-control', 'style': 'width: 100px;',
                                                  'disabled': 'true'}))
    item_name = forms.CharField(required=False,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'style': 'width: 300px;', 'disabled': 'true'}))
    item_onhand = forms.CharField(required=False,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control', 'style': 'text-align: right; width: 120px;',
                                             'disabled': 'true'}))
    item_code = forms.CharField(required=True,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'required': 'required', 'style': 'display: none'}))
    item_id = forms.CharField(required=True,
                              widget=forms.TextInput(
                                  attrs={'class': 'form-control', 'required': 'required', 'style': 'display: none'}))
    quantity = forms.DecimalField(required=False,
                                  widget=forms.NumberInput(
                                      attrs={'class': 'form-control-item numeric_qty', 'style': 'text-align: right; width: 120px;',
                                             'required': 'required', 'step': '0.01'}))
    price = forms.DecimalField(required=False,
                               widget=forms.NumberInput(
                                   attrs={'class': 'form-control-item numeric_price', 'style': 'text-align: right;  width: 120px;',
                                          'required': 'required'}))
    amount = forms.DecimalField(required=False,
                                widget=forms.NumberInput(
                                    attrs={'class': 'form-control-item',
                                           'style': 'text-align: right;  width: 100%; display: none;'}))
    remark = forms.CharField(required=False,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control lastElement',
                                        'style': 'text-align: right; width: 200px;'}))
    long_items = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    stock_qty = forms.DecimalField(required=False,
                                   widget=forms.NumberInput(
                                       attrs={'class': 'form-control-item', 'style': 'text-align: right',
                                              'style': 'display: none; width: 100%;'}))

    class Meta:
        model = StockTransactionDetail
        fields = (
            'line_number', 'item_inv_measure', 'item_onhand', 'item_name', 'item_id', 'quantity', 'price', 'amount',
            'remark')
