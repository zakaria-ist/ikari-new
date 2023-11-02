from django.forms import ModelChoiceField
from reports.models import Report
from suppliers.models import Supplier
from companies.models import Company
from customers.models import Customer, Delivery
from items.models import Item, ItemCategory
from orders.models import Order, OrderItem
from django import forms
from django.db.models import Q


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class DocNoModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.document_number


class CusPOModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.customer_po_no


class POModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.document_number

class DeliveryModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class ReportForm(forms.ModelForm):
    code = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))

    lbCL2400Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbCL2400Supplier'}))

    lbCL2400ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbCL2400ToSupplier'}))

    lbDL2400Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbDL2400Supplier'}))

    lbDL2400ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbDL2400ToSupplier'}))

    lbSR8300Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8300Supplier'}))

    lbSR8300ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8300ToSupplier'}))

    lbSR7202Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7202Supplier'}))

    lbSR7202ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7202ToSupplier'}))

    lbSR8801Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8801Supplier'}))

    lbSR8801ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8801ToSupplier'}))

    lbSR7203Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7203Supplier'}))

    lbSR7203ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7203ToSupplier'}))

    lbSR8301Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8301Supplier'}))

    lbSR8301ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8301ToSupplier'}))

    lbSR7204Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7204Supplier'}))

    lbSR7204ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7204ToSupplier'}))

    lbSR7205Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7205Supplier'}))

    lbSR7205ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7205ToSupplier'}))

    lbSR834Document = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR834Document'}))

    lbSR834ToDocument = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR834ToDocument'}))

    lbSR7201Document = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7201Document'}))

    lbSR7201ToDocument = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7201ToDocument'}))

    lbSL3A0Document = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL3A0Document'}))

    lbSL3A0ToDocument = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL3A0ToDocument'}))

    lbSL330Document = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL330Document'}))

    lbSL330ToDocument = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL330ToDocument'}))

    lbSL3A0Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL3A0Supplier'}))

    lbSL3A0ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL3A0ToSupplier'}))

    lbSL330CCustomer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL330CCustomer'}))

    lbSL330ToCCustomer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL330ToCCustomer'}))

    lbSL3A0Cutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL3A0Cutomer'}))

    lbSL3A0ToCutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL3A0ToCutomer'}))

    lbSL330Cutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL330Cutomer'}))

    lbSL330ToCutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSL330ToCutomer'}))

    lbSR7203Cutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7203Cutomer'}))

    lbSR7203ToCutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7203ToCutomer'}))

    lbSR8301Cutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8301Cutomer'}))

    lbSR8301ToCutomer = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8301ToCutomer'}))

    lbSR7204PartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7204PartNo'}))

    lbSR7204ToPartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7204ToPartNo'}))

    lbSR7102PartGrp = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7102PartGrp'}))

    lbSR7102ToPartGrp = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7102ToPartGrp'}))

    lbSR7205PartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7205PartNo'}))

    lbSR7205ToPartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7205ToPartNo'}))

    lbSR7404PartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7404PartNo'}))

    lbSR7404ToPartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7404ToPartNo'}))

    lbSR7404PartGrp = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7404PartGrp'}))

    lbSR7404ToPartGrp = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7404ToPartGrp'}))

    fromSACustomer = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'fromSACustomer'}))

    toSACustomer = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'toSACustomer'}))

    toSAPartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'toSAPartNo'}))

    fromSAPartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'fromSAPartNo'}))

    fromSACustomerPo = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'fromSACustomerPo'}))

    toSACustomerPo = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'toSACustomerPo'}))

    lbSR8400Customer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8400Customer'}))

    lbSR8400ToCustomer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR8400ToCustomer'}))

    lbSR7402Customer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7402Customer'}))

    lbSR7402ToCustomer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7402ToCustomer'}))

    lbSR7403Customer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7403Customer'}))

    lbSR7403ToCustomer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7403ToCustomer'}))

    lbSR7403Supplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7403Supplier'}))

    lbSR7403ToSupplier = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7403ToSupplier'}))

    lbSR7404Customer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7404Customer'}))

    lbSR7404ToCustomer = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'lbSR7404ToCustomer'}))

    txtPartNoSR7503 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartNoSR7503'}))
                            
    txtPartNoToSR7503 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartNoToSR7503'}))

    txtPartGrpSR7503 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartGrpSR7503'}))
                            
    txtPartGrpToSR7503 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartGrpToSR7503'}))

    txtSuppplierNoSR7504 = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtSuppplierNoSR7504'}))

    txtToSuppplierNoSR7504 = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtToSuppplierNoSR7504'}))

    txtSuppplierCodeSR7601 = CodeModelChoiceField(queryset=ItemCategory.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtSuppplierCodeSR7601'}))

    totxtSuppplierCodeSR7601 = CodeModelChoiceField(queryset=ItemCategory.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'totxtSuppplierCodeSR7601'}))

    txtSuppplierCodeSR7602 = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtSuppplierCodeSR7602'}))

    totxtSuppplierCodeSR7602 = CodeModelChoiceField(queryset=Customer.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'totxtSuppplierCodeSR7602'}))

    txt7300SuppplierNo = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txt7300SuppplierNo'}))

    txt7300ToSuppplierNo = CodeModelChoiceField(queryset=Supplier.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txt7300ToSuppplierNo'}))

    txtDocumentNoSR7300 = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtDocumentNoSR7300'}))

    txtDocumentNoSR7300_to = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtDocumentNoSR7300_to'}))

    txtPartNoSR7301 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartNoSR7301'}))

    txtPartNoToSR7301 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartNoToSR7301'}))

    txtCustomerPoSR7301 = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtCustomerPoSR7301'}))

    txtCustomerPoToSR7301 = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtCustomerPoToSR7301'}))

    txtPartNoSR7302 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartNoSR7302'}))

    txtPartNoToSR7302 = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtPartNoToSR7302'}))

    txtDocumentNoSR7302 = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtDocumentNoSR7302'}))

    txtDocumentNoToSR7302 = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtDocumentNoToSR7302'}))

    txtDocNoFromSR7401 = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtDocNoFromSR7401'}))

    txtDocNoToSR7401 = DocNoModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtDocNoToSR7401'}))

    txtCustPONoFromSR7401 = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtCustPONoFromSR7401'}))

    txtCustPONoToSR7401 = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtCustPONoToSR7401'}))

    txtCustPONoFromSR7503 = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtCustPONoFromSR7503'}))

    txtCustPONoToSR7503 = CusPOModelChoiceField(queryset=OrderItem.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'txtCustPONoToSR7503'}))
    
    fromPONo = POModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'fromPONo'}))

    toPONo = POModelChoiceField(queryset=Order.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'toPONo'}))

    sr8500PartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'sr8500PartNo'}))

    sr8500ToPartNo = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'sr8500ToPartNo'}))

    sr8500Location = CodeModelChoiceField(queryset=Item.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'sr8500Location'}))

    po_alternate_address = DeliveryModelChoiceField(queryset=Delivery.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'po_alternate_address'}))

    do_alternate_address = DeliveryModelChoiceField(queryset=Delivery.objects.none(), empty_label='', required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'do_alternate_address'}))
    
    is_hidden = forms.BooleanField(initial=True, required=False,
                            widget=forms.CheckboxInput(attrs={'class': 'styled'}))
    category = MyModelChoiceField(queryset=Report.objects.none(), empty_label=None, required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'report_category'}))

    update_date = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}))

    class Meta:
        model = Report
        fields = ('code',
                  'name',
                  'is_hidden',
                  'category',
                  'update_date'
                  )

    def __init__(self, company_id, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)

        if company_id:
            company = Company.objects.get(pk=company_id)
            if company.is_inventory:
                category_list = Report.objects.filter(is_hidden=0, is_category=1).order_by('id')
            else:
                category_list = Report.objects.filter(is_hidden=0, is_category=1).exclude(Q(name='Outstanding Stock Balance')).order_by('id')
            self.fields['category'].queryset = category_list
            self.initial['category'] = category_list.first().name
