import datetime
import json
import logging
import traceback
import django.db.transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from accounting.models import PaymentCode, Journal
from accounts.models import DistributionCode, AccountSet
from banks.models import Bank
from companies.models import Company
from contacts.models import Contact
from countries.models import Country
from currencies.models import Currency
from items.models import Item
from suppliers.forms import AccVendorInfoForm, SupplierInfoForm
from suppliers.models import Supplier, SupplierItem
from taxes.models import Tax
from utilities.constants import TERMS_CODE, DIS_CODE_TYPE_DICT, TAX_TRX_TYPES_DICT, CONTACT_TYPES_DICT, PAYMENT_CODE_TYPE_DICT, ACCOUNT_SET_TYPE_DICT

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def load_list(request):
    try:
        return render(request, 'supplier-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('suppliers.add_supplier', login_url='/alert/')
def supplier_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    currency_code_list = Currency.objects.filter(is_hidden=False)
    tax_code_list = Tax.objects.filter(is_hidden=False,
                                       company_id=company_id,
                                       tax_group__company_id=company_id,
                                       tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
    payment_code_list = PaymentCode.objects.filter(is_hidden=False, is_active=True,
                                                    company_id=company_id, 
                                                    source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')

    if request.method == 'POST':
        try:
            with django.db.transaction.atomic():
                supplier = Supplier()
                supplier.name = request.POST.get('name')
                supplier.code = request.POST.get('code')
                supplier.address = request.POST.get('address')
                supplier.ship_info_1 = request.POST.get('ship_info_1')
                supplier.accode_ap = request.POST.get('accode_ap')
                supplier.accode_pur = request.POST.get('accode_pur')
                supplier.accode_exc = request.POST.get('accode_exc')
                supplier.accode_int = request.POST.get('accode_int')
                supplier.accode_bnk = request.POST.get('accode_bnk')
                supplier.accode_chr = request.POST.get('accode_chr')
                supplier.center_ap = request.POST.get('center_ap')
                supplier.center_pur = request.POST.get('center_pur')
                supplier.center_exc = request.POST.get('center_exc')
                supplier.center_int = request.POST.get('center_int')
                supplier.center_bnk = request.POST.get('center_bnk')
                supplier.center_chr = request.POST.get('center_chr')

                supplier.company_id = company_id
                if request.POST.get('account_set') != "0" and request.POST.get('account_set'):
                    supplier.account_set_id = request.POST.get('account_set')
                else:
                    supplier.account_set = None
                if request.POST.get('term_days') != "-1" and request.POST.get('term_days'):
                    supplier.term_days = request.POST.get('term_days')
                else:
                    supplier.term_days = None
                if request.POST.get('country') != "0" and request.POST.get('country'):
                    supplier.country_id = request.POST.get('country')
                else:
                    supplier.country_id = None
                if request.POST.get('currency') != "0" and request.POST.get('currency'):
                    supplier.currency_id = request.POST.get('currency')
                else:
                    supplier.currency_id = None
                if request.POST.get('payment_code') != "0" and request.POST.get('payment_code'):
                    supplier.payment_code_id = request.POST.get('payment_code')
                else:
                    supplier.payment_code_id = None
                if request.POST.get('credit_limit') != "0" and request.POST.get('credit_limit'):
                    supplier.credit_limit = request.POST.get('credit_limit')
                else:
                    supplier.credit_limit = None
                if request.POST.get('tax') != "0" and request.POST.get('tax'):
                    supplier.tax_id = request.POST.get('tax')
                else:
                    supplier.tax_id = None
                if request.POST.get('remittance') != "0" and request.POST.get('remittance'):
                    supplier.remittance = request.POST.get('remittance')
                else:
                    supplier.remittance = None
                if request.POST.get('transport') != "0" and request.POST.get('transport'):
                    supplier.transport = request.POST.get('transport')
                else:
                    supplier.transport = None
                supplier.ship_via = request.POST.get('ship_via')
                supplier.create_date = datetime.datetime.today()
                supplier.update_date = datetime.datetime.today()
                supplier.update_by = request.user.id
                supplier.is_active = supplier.is_active
                supplier.is_hidden = 0
                supplier.is_active = True
                supplier.distribution_id = request.POST.get('distribution') if request.POST.get(
                    'distribution') else None
                supplier.save()

                contact = Contact()
                contact.contact_type = int(CONTACT_TYPES_DICT['Supplier'])
                contact.supplier_id = supplier.id
                contact.company_id = company_id
                if request.POST.get('contact_attention'):
                    contact.attention = request.POST.get('contact_attention')
                    contact.name = request.POST.get('contact_attention')
                if request.POST.get('contact_company_name'):
                    contact.company_name = request.POST.get('contact_company_name')
                if request.POST.get('contact_designation'):
                    contact.designation = request.POST.get('contact_designation')
                if request.POST.get('contact_phone'):
                    contact.phone = request.POST.get('contact_phone')
                if request.POST.get('contact_fax'):
                    contact.fax = request.POST.get('contact_fax')
                if request.POST.get('contact_email'):
                    contact.email = request.POST.get('contact_email')
                if request.POST.get('contact_web'):
                    contact.web = request.POST.get('contact_web')
                if request.POST.get('contact_address'):
                    contact.address = request.POST.get('contact_address')
                if request.POST.get('contact_remark'):
                    contact.note = request.POST.get('contact_remark')
                if request.POST.get('contact_company_name'):
                    contact.company_name = request.POST.get('contact_company_name')
                if request.POST.get('contact_designation'):
                    contact.designation = request.POST.get('contact_designation')
                contact.is_active = True
                contact.create_date = datetime.datetime.today()
                contact.update_date = datetime.datetime.today()
                contact.update_by = request.user.id
                contact.is_hidden = 0
                contact.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='supplier_add')

        return redirect('/suppliers/list/')
    else:
        form = SupplierInfoForm(request)
    return render_to_response('supplier-form.html',
                              RequestContext(request, {'form': form,
                                                       # 'country_list': country_list,
                                                       'payment_code_list': payment_code_list,
                                                       'tax_code_list': tax_code_list,
                                                       # 'account_set': account_set,
                                                       # 'term_list': term_list,
                                                       'terms_code_list': TERMS_CODE,
                                                       'currency_code_list': currency_code_list}))


@login_required
@permission_required('suppliers.change_supplier', login_url='/alert/')
def supplier_edit(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    post = get_object_or_404(Supplier, pk=supplier_id)
    supplier = Supplier.objects.get(pk=supplier_id)
    currency_code_list = Currency.objects.filter(is_hidden=False)
    contact_list = Contact.objects.filter(is_hidden=0, company_id=company_id, supplier_id=supplier_id).first()
    bank_list = Bank.objects.filter(is_hidden=0, company_id=company_id, is_active=True)
    supplieritem_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                    supplier_id=supplier_id)
    tax_code_list = Tax.objects.filter(is_hidden=False,
                                       company_id=company_id,
                                       tax_group__company_id=company_id,
                                       tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
    payment_code_list = PaymentCode.objects.filter(is_hidden=False, is_active=True,
                                                    company_id=company_id, 
                                                    source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')

    if request.method == 'POST':
        try:
            supplier.accode_ap = request.POST.get('accode_ap')
            supplier.accode_pur = request.POST.get('accode_pur')
            supplier.accode_exc = request.POST.get('accode_exc')
            supplier.accode_int = request.POST.get('accode_int')
            supplier.accode_bnk = request.POST.get('accode_bnk')
            supplier.accode_chr = request.POST.get('accode_chr')
            supplier.center_ap = request.POST.get('center_ap')
            supplier.center_pur = request.POST.get('center_pur')
            supplier.center_exc = request.POST.get('center_exc')
            supplier.center_int = request.POST.get('center_int')
            supplier.center_bnk = request.POST.get('center_bnk')
            supplier.center_chr = request.POST.get('center_chr')

            supplier.name = request.POST.get('name')
            supplier.code = request.POST.get('code')
            supplier.address = request.POST.get('address')
            supplier.ship_info_1 = request.POST.get('ship_info_1')
            supplier.company_id = company_id
            if request.POST.get('account_set') != "0" and request.POST.get('account_set'):
                supplier.account_set_id = request.POST.get('account_set')
            else:
                supplier.account_set = None
            if request.POST.get('term_days') != "-1" and request.POST.get('term_days'):
                supplier.term_days = request.POST.get('term_days')
            else:
                supplier.term_days = None
            if request.POST.get('country') != "0" and request.POST.get('country'):
                supplier.country_id = request.POST.get('country')
            else:
                supplier.country_id = None
            if request.POST.get('currency') != "0" and request.POST.get('currency'):
                supplier.currency_id = request.POST.get('currency')
            else:
                supplier.currency_id = None
            if request.POST.get('payment_code') != "0" and request.POST.get('payment_code'):
                supplier.payment_code_id = request.POST.get('payment_code')
            else:
                supplier.payment_code_id = None
            if request.POST.get('credit_limit') != "0" and request.POST.get('credit_limit'):
                supplier.credit_limit = request.POST.get('credit_limit')
            else:
                supplier.credit_limit = None
            if request.POST.get('tax') != "0" and request.POST.get('tax'):
                supplier.tax_id = request.POST.get('tax')
            else:
                supplier.tax_id = None
            if request.POST.get('remittance') != "0" and request.POST.get('remittance'):
                supplier.remittance = request.POST.get('remittance')
            else:
                supplier.remittance = None
            if request.POST.get('transport') != "0" and request.POST.get('transport'):
                supplier.transport = request.POST.get('transport')
            else:
                supplier.transport = None
            supplier.distribution_id = request.POST.get('distribution') if request.POST.get('distribution') else None
            supplier.ship_via = request.POST.get('ship_via')
            supplier.update_date = datetime.datetime.today()
            supplier.update_by = request.user.id
            supplier.is_active = supplier.is_active
            supplier.is_hidden = 0
            supplier.save()
            if contact_list:
                contact_list.designation = request.POST.get('contact_designation')
                contact_list.phone = request.POST.get('contact_phone')
                contact_list.fax = request.POST.get('contact_fax')
                # contact_list.name = request.POST.get('contact_name')
                contact_list.name = request.POST.get('contact_attention')
                contact_list.attention = request.POST.get('contact_attention')
                contact_list.save()
            else:
                cont = Contact()
                cont.designation = request.POST.get('contact_designation')
                cont.phone = request.POST.get('contact_phone')
                cont.fax = request.POST.get('contact_fax')
                cont.name = request.POST.get('contact_name')
                cont.name = request.POST.get('contact_attention')
                cont.attention = request.POST.get('contact_attention')
                cont.supplier_id = supplier_id
                cont.company_id = company_id
                cont.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='supplier_edit')
        return HttpResponsePermanentRedirect(reverse('supplier_list'))
    else:
        supplier.update_date = supplier.update_date.strftime("%d-%m-%Y")
        form = SupplierInfoForm(request, instance=post)
    return render_to_response('supplier-form.html', RequestContext(request,
                                                                   {'form': form, 'supplier': supplier,
                                                                    'contact_list': contact_list,
                                                                    'bank_list': bank_list,
                                                                    'payment_code_list': payment_code_list,
                                                                    'tax_code_list': tax_code_list,
                                                                    'supplier_item_list': supplieritem_list,
                                                                    'terms_code_list': TERMS_CODE,
                                                                    'currency_code_list': currency_code_list
                                                                    }))


@login_required
@permission_required('suppliers.delete_supplier', login_url='/alert/')
def supplier_delete(request, supplier_id, page):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            supplier = Supplier.objects.get(pk=supplier_id)
            supplier.is_active = False
            journals = Journal.objects.filter(company_id=company_id, supplier_id=supplier_id, is_hidden=0)
            orders = Order.objects.filter(company_id=company_id, supplier_id=supplier_id, is_hidden=0)
            if not len(journals) and not len(orders):
                supplier.is_hidden = True
                messages.add_message(request, messages.INFO, 'Supplier is Deleted', extra_tags='supplier_delete')
            else:
                messages.add_message(request, messages.WARNING, 'Supplier is Deactivated but not deleted. As there are some dependencies', extra_tags='supplier_delete')
            
            supplier.save()
            if page == '1':
                return redirect('/suppliers/list/')
            else:
                return redirect('/suppliers/acc_vendor_list/')

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='supplier_delete')


@login_required
def supplier_item_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    get_first_supplier = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                     supplier__company_id=company_id, supplier__is_hidden=0)[:1].get()
    supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    return render_to_response('supplier-item-list.html',
                              RequestContext(request,
                                             {'first_supplier': get_first_supplier, 'supplier_list': supplier_list}))


@login_required
def item_by_supplier(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if supplier_id == '':
        get_first_supplier = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                         supplier__company_id=company_id, supplier__is_hidden=0)[
            :1].get()
        if not get_first_supplier:
            supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
            return render_to_response('supplier-item-list.html',
                                      RequestContext(request, {'supplier_list': supplier_list}))
        else:
            supplier_id = get_first_supplier.supplier.id
            item_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                    supplier_id=supplier_id)
            supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
            return render_to_response('supplier-item-list.html',
                                      RequestContext(request, {'item_list': item_list, 'supplier_list': supplier_list,
                                                               'supplier_id': int(supplier_id)}))
    else:
        item_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                supplier_id=supplier_id)
        supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
        return render_to_response('supplier-item-list.html',
                                  RequestContext(request, {'item_list': item_list, 'supplier_list': supplier_list,
                                                           'supplier_id': int(supplier_id)}))


@login_required
@permission_required('suppliers.add_supplieritem', login_url='/alert/')
def item_add(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
        item_list = Item.objects.none()
        currency_list = Currency.objects.filter(is_hidden=0)
        select_item_id = request.POST.get('hdItemSelected')
    except ObjectDoesNotExist:
        messages_error = "Permission Denied."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        if select_item_id == None or select_item_id == '':
            messages_error = "Please select the an Item!"
            return render_to_response('supplier-item.html', RequestContext(request,
                                                                           {'supplier': supplier,
                                                                            'item_list': item_list,
                                                                            'currency_list': currency_list,
                                                                            'messages_error': messages_error}))
        else:
            all_supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            supplier_id=supplier_id) \
                .values_list('item_id', flat=True)
            if select_item_id and int(select_item_id) not in all_supplier_item:
                supplier_item = SupplierItem()
                supplier_item.create_date = datetime.datetime.today()
            else:
                supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            item_id=select_item_id, supplier_id=supplier_id).first()
            if supplier_item:
                try:
                    supplier_item.item_id = int(select_item_id)
                    supplier_item.supplier_id = supplier_id
                    supplier_item.currency_id = request.POST.get('currency')
                    if request.POST.get('purchase_price'):
                        supplier_item.purchase_price = request.POST.get('purchase_price')
                    if request.POST.get('leading_days'):
                        supplier_item.leading_days = request.POST.get('leading_days')
                    if request.POST.get('effective_date'):
                        supplier_item.effective_date = request.POST.get('effective_date')

                    supplier_item.create_date = datetime.datetime.today()
                    supplier_item.update_date = datetime.datetime.today()
                    supplier_item.update_by = request.user.id
                    supplier_item.is_hidden = 0
                    supplier_item.is_active = 1
                    supplier_item.save()

                    # Update default Supplier of Item
                    if select_item_id:
                        item = Item.objects.get(pk=select_item_id)
                        if item and not item.default_supplier:
                            item.default_supplier_id = supplier_id
                            item.save()
                    return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[supplier_id]))
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='supplier_add_item')
    else:
        return render(request, 'supplier-item.html', {'supplier': supplier,
                                                      'currency_list': currency_list,
                                                      'item_list': item_list})


@login_required
@permission_required('suppliers.change_supplieritem', login_url='/alert/')
def item_edit(request, supplieritem_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item_list = Item.objects.none()
    currency_list = Currency.objects.filter(is_hidden=0)
    select_item_id = request.POST.get('hdItemSelected')
    try:
        supplier_item = SupplierItem.objects.get(pk=supplieritem_id)
        supplier = Supplier.objects.get(pk=supplier_item.supplier_id)
    except ObjectDoesNotExist:
        messages_error = "Supplier Item does not exist | Permission Denied."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        if select_item_id == None or select_item_id == '':
            messages_error = "Please select the an Item!"
            return render_to_response('supplier-item.html', RequestContext(request,
                                                                           {'supplier': supplier,
                                                                            'currency_list': currency_list,
                                                                            'item_list': item_list,
                                                                            'supplieritem': supplier_item,
                                                                            'messages_error': messages_error}))
        else:
            all_supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            supplier_id=supplier_item.supplier_id) \
                .values_list('item_id', flat=True)
            if select_item_id and (int(select_item_id) not in all_supplier_item
                                   or int(select_item_id) == supplier_item.item_id):
                supplier_item = SupplierItem.objects.get(pk=supplieritem_id)
            else:
                supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            item_id=select_item_id,
                                                            supplier_id=supplier_item.supplier_id).first()
            if supplier_item:
                try:
                    supplier_item.item_id = int(request.POST.get('hdItemSelected'))
                    supplier_item.currency_id = request.POST.get('currency')
                    if request.POST.get('purchase_price'):
                        supplier_item.purchase_price = request.POST.get('purchase_price')
                    if request.POST.get('leading_days'):
                        supplier_item.leading_days = request.POST.get('leading_days')
                    else:
                        supplier_item.leading_days = None
                    if request.POST.get('effective_date'):
                        supplier_item.effective_date = request.POST.get('effective_date')
                    else:
                        supplier_item.effective_date = None
                    supplier_item.update_date = datetime.datetime.today()
                    supplier_item.update_by = request.user.id
                    supplier_item.is_hidden = 0
                    supplier_item.is_active = 1
                    supplier_item.save()
                    return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[supplier.id]))
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='supplier_add_item')

    else:
        return render(request, 'supplier-item.html', {'supplier': supplier, 'item_list': item_list,
                                                      'currency_list': currency_list,
                                                      'supplieritem': supplier_item})


@login_required
@permission_required('suppliers.delete_supplieritem', login_url='/alert/')
def item_delete(request, supplieritem_id):
    if request.method == 'POST':
        try:
            supplieritem = SupplierItem.objects.get(pk=supplieritem_id)
            supplieritem.is_hidden = True
            supplieritem.is_active = False
            supplieritem.update_by = request.user.id
            supplieritem.update_date = datetime.datetime.today()
            supplieritem.save()
            return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[supplieritem.supplier_id]))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_delete_item')
        except ObjectDoesNotExist:
            messages_error = "Supplier Item does not exist."
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def SupplierList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']

    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = Supplier.objects.filter(is_hidden=0, company_id=company_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(country__code__icontains=search) |
            Q(payment_code__code__icontains=search) |
            Q(currency__code__icontains=search) |
            Q(tax__name__icontains=search) |
            Q(update_date__icontains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "code"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "3":
        column_name = "country__code"
    elif order_column == "4":
        column_name = "currency__code"
    elif order_column == "5":
        column_name = "tax__name"
    elif order_column == "6":
        column_name = "payment_code__code"
    elif order_column == "7":
        column_name = "is_active"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "customer_code": field.code,
                "customer_name": field.name,
                "country_code": field.country.code if field.country else '',
                "currency_code": field.currency.code if field.currency else '',
                "payment_mode_code": field.payment_code.code if field.payment_code else '',
                "is_active": str(field.is_active)}
        try:
            data['tax_name'] = field.tax.name if field.tax else '',
        except:
            data['tax_name'] = '',
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def supplier_By_pk(request, supp_id):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        list_filter = Supplier.objects.filter(pk=supp_id)
        array = []
        for field in list_filter:
            data = {"id": field.id,
                    "payment_code": field.payment_code.code if field.payment_code else '',
                    "payment_term": field.term_days,
                    "currency_id": field.currency.id,
                    "currency_name": field.currency.name,
                    "is_decimal": 1 if field.currency.is_decimal else 0,
                    "credit_limit": str(field.credit_limit),
                    "address": field.address,
                    "email": field.email,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "supplier_code": field.code,
                    "supplier_name": field.name,
                    "country_code": field.country.code if field.country else '',
                    "currency_code": field.currency.code if field.currency else '',
                    "tax_name": field.tax.name if field.tax else '',
                    "is_active": str(field.is_active),
                    "distribution_id": str(field.distribution_id),
                    "tax_id": field.tax.id if field.tax else '',
                    "currency_symbol": field.currency.symbol if field.currency else ''}
            array.append(data)

        content = {
            # "draw": draw,
            "data": array,
            # "recordsTotal": records_total,
            # "recordsFiltered": records_filtered
        }
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def supplier_By_code(request, supplier_code):
    try:

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        list_filter = Supplier.objects.filter(code=supplier_code, is_hidden=False, company=company)
        array = []
        for field in list_filter:
            data = {
                "id": field.id,
                "supplier_code": field.code,
                "supplier_name": field.name
            }
            array.append(data)

        content = {
            "data": array,
        }
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def SupplierItemList__asJson(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    supplier = Supplier.objects.get(pk=supplier_id)
    supplier_item_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                     supplier_id=supplier_id) \
        .values_list('item_id', flat=True)
    list_filter = Item.objects.filter(company_id=company_id, is_hidden=0, purchase_currency_id=supplier.currency.id) \
        .exclude(id__in=supplier_item_list)

    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) |
            Q(name__contains=search) |
            Q(category__code__contains=search) |
            Q(country__name__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "code"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "3":
        column_name = "category__code"
    elif order_column == "4":
        column_name = "country__name"
    elif order_column == "5":
        column_name = "purchase_price"
    elif order_column == "6":
        column_name = "purchase_currency__code"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    exchange_rate = 0
    for field in list:
        purchase_price = field.purchase_price if field.purchase_price else 0
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "item_code": field.code,
                "item_name": field.name,
                "category_code": field.category.code if field.category else '',
                "country_name": field.country.name if field.country else '',
                "purchase_price": intcomma("%.2f" % purchase_price),
                "purchase_currency": field.purchase_currency.code if field.purchase_currency else 0,
                "purchase_currency_id": field.purchase_currency_id if field.purchase_currency else 0}

        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def SupplierEditItemList__asJson(request, supplieritem_id):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    supplier_item_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                     supplier_id=supplieritem_id)
    records_total = supplier_item_list.count()

    if search:  # Filter data base on search
        supplier_item_list = supplier_item_list.filter(
            Q(item__code__contains=search) |
            Q(item__name__contains=search) |
            Q(item__category__name__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = supplier_item_list.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "item__code"
    elif order_column == "2":
        column_name = "item__name"
    elif order_column == "3":
        column_name = "item__category__name"
    elif order_column == "4":
        column_name = "purchase_price"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = supplier_item_list.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = supplier_item_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        purchase_price = field.purchase_price if field.purchase_price else 0
        currency_code = field.currency.code if field.currency else ''
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "item_code": field.item.code,
                "item_name": field.item.name,
                "category_name": field.item.category.name if field.item.category else '',
                "purchase_price": intcomma("%.2f" % purchase_price) + ' ' + currency_code,
                "is_active": str(field.item.is_active)}
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def get_item_info(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            item_code = request.POST.get('item_code')
            supplier_id = request.POST.get('supplier_id')
            supplier = Supplier.objects.get(pk=supplier_id)
            item = Item.objects.filter(is_hidden=0, code__contains=item_code, company_id=company_id).first()
            supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        supplier_id=supplier_id,
                                                        item__code__contains=item_code).first()

            response_data = {}
            response_data['id'] = item.id
            response_data['name'] = item.name
            response_data['code'] = item.code
            response_data['currency_id'] = str(item.sale_currency.id if item.sale_currency else 0)
            response_data['purchase_price'] = str(item.purchase_price if item.purchase_price else 0)
            if supplier_item:
                response_data['currency_id'] = str(supplier_item.currency.id if supplier_item.currency else
                                                   item.sale_currency.id if item.sale_currency else 0)
                response_data['purchase_price'] = str(supplier_item.purchase_price if supplier_item.purchase_price else
                                                      item.purchase_price if item.purchase_price else 0)

            if int(supplier.currency_id) != int(response_data['currency_id']):
                messages.add_message(request, messages.ERROR,
                                     "Currency of item is different with currency of supplier.",
                                     extra_tags='get_item_info')
                return HttpResponse(json.dumps({"Fail": "Currency of item is different with currency of supplier."}),
                                    content_type="application/json")

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_item_info')
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")


# Create your views here.
@login_required
def account_vendor_list(request):
    try:
        return render(request, 'acc-vendor-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('suppliers.add_supplier', login_url='/alert/')
def acc_Vendor_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    payment_code_list = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                        company_id=company_id, 
                                                        source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')
    tax_code_list = Tax.objects.filter(is_hidden=False,
                                       company_id=company_id,
                                       tax_group__company_id=company_id,
                                       tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
    dis_code_list = DistributionCode.objects.filter(is_hidden=False, is_active=True, company_id=company_id,
                                                    type=DIS_CODE_TYPE_DICT['AP Distribution Code'])
    currency_code_list = Currency.objects.filter(is_hidden=False)
    if request.method == 'POST':
        form = AccVendorInfoForm(request, request.POST)
        try:
            with transaction.atomic():
                supplier = Supplier()
                supplier.company_id = company_id
                supplier.name = request.POST.get('name')
                supplier.code = request.POST.get('code')
                if request.POST.get('account_payable'):
                    supplier.account_payable_id = request.POST.get('account_payable')
                else:
                    supplier.account_payable_id = None
                if request.POST.get('account_set'):
                    supplier.account_set_id = request.POST.get('account_set')
                else:
                    supplier.account_set_id = None

                if request.POST.get('term_days'):
                    supplier.term_days = request.POST.get('term_days')
                else:
                    supplier.term_days = None

                if request.POST.get('bank_code'):
                    supplier.bank_id = request.POST.get('bank_code')
                else:
                    supplier.bank_id = None

                if request.POST.get('payment_code'):
                    supplier.payment_code_id = request.POST.get('payment_code')
                else:
                    supplier.payment_code_id = None
                if request.POST.get('tax'):
                    supplier.tax_id = request.POST.get('tax')
                else:
                    supplier.tax_id = None
                if request.POST.get('distribution'):
                    supplier.distribution_id = request.POST.get('distribution')
                else:
                    supplier.distribution_id = None
                if request.POST.get('currency'):
                    supplier.currency_id = request.POST.get('currency')
                else:
                    supplier.currency_id = None
                if request.POST.get('credit_limit'):
                    supplier.credit_limit = request.POST.get('credit_limit')
                else:
                    supplier.credit_limit = None
                if request.POST.get('email'):
                    supplier.email = request.POST.get('email')
                else:
                    supplier.email = None
                if request.POST.get('email_msg'):
                    supplier.email_msg = request.POST.get('email_msg')
                else:
                    supplier.email_msg = None
                if request.POST.get('address'):
                    supplier.address = request.POST.get('address')
                else:
                    supplier.address = None
                if request.POST.get('phone'):
                    supplier.phone = request.POST.get('phone')
                else:
                    supplier.phone = None
                if request.POST.get('postal_code'):
                    supplier.postal_code = request.POST.get('postal_code')
                else:
                    supplier.postal_code = None
                if request.POST.get('country'):
                    supplier.country_id = request.POST.get('country')
                else:
                    supplier.country_id = None

                supplier.is_active = True
                supplier.is_hidden = False
                supplier.create_date = datetime.datetime.today()
                supplier.update_by = request.user.id
                supplier.update_date = datetime.datetime.today()
                supplier.save()
                return HttpResponsePermanentRedirect(reverse('acc_vendor_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_add')
            return HttpResponsePermanentRedirect(reverse('acc_vendor_list'))
    else:
        form = AccVendorInfoForm(request)
        form.fields['tax'].widget.attrs['data-dis-code'] = []

        for i, optionSelect in enumerate(form.fields['tax'].widget.choices.queryset):
            if optionSelect.distribution_code_id:
                form.fields['tax'].widget.attrs['data-dis-code'].append(
                    {'idtax': optionSelect.id, 'dis_code': optionSelect.distribution_code_id})
        form.fields['tax'].widget.attrs['data-dis-code'] = json.dumps(form.fields['tax'].widget.attrs['data-dis-code'])
    return render_to_response('acc-vendor.html',
                              RequestContext(request, {'form': form, 'terms_code_list': TERMS_CODE,
                                                       'payment_code_list': payment_code_list,
                                                       'tax_code_list': tax_code_list, 'dis_code_list': dis_code_list,
                                                       'currency_code_list': currency_code_list
                                                       }))


@login_required
def SBankList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Bank.objects.filter(is_hidden=0, company_id=company_id, is_active=True)

        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(
                Q(name__contains=search) | Q(code__contains=search)

            )

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "name"
        elif order_column == "1":
            column_name = "description"
        elif order_column == "2":
            column_name = "currency_code"

        order_dir = request.GET['order[0][dir]']
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        if order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "name": field.name,
                    "description": field.description,
                    "currency_code": field.currency.code if field.currency_id else '',
                    "is_active": str(field.is_active)}

            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except:
        logger.error(traceback.format_exc())


@csrf_exempt
@login_required
def load_bank_set(request):
    if request.method == 'POST':
        try:
            if 'bank_set_id' in request.POST and request.POST['bank_set_id']:
                bank_set_id = request.POST['bank_set_id']
                bank = Bank.objects.get(pk=bank_set_id)

                context = {
                    'name': bank.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@csrf_exempt
@login_required
def load_dis_code(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            if 'dis_id' in request.POST and request.POST['dis_id']:
                dis_id = request.POST['dis_id']
                dis = DistributionCode.objects.get(pk=dis_id)

                context = {
                    'name': dis.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@login_required
@permission_required('suppliers.change_supplier', login_url='/alert/')
def acc_vendor_edit(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    payment_code_list = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                        company_id=company_id, 
                                                        source_type=PAYMENT_CODE_TYPE_DICT['AP Payment Code']).order_by('code')
    tax_code_list = Tax.objects.filter(is_hidden=False,
                                       company_id=company_id,
                                       tax_group__company_id=company_id,
                                       tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
    dis_code_list = DistributionCode.objects.filter(is_hidden=False, is_active=True, company_id=company_id,
                                                    type=DIS_CODE_TYPE_DICT['AP Distribution Code'])

    post = get_object_or_404(Supplier, pk=supplier_id)

    supplier = Supplier.objects.get(pk=supplier_id)
    currency_code_list = Currency.objects.filter(is_hidden=False)
    if request.method == 'POST':
        try:
            supplier.company_id = company_id
            supplier.name = request.POST.get('name')
            supplier.code = request.POST.get('code')
            if request.POST.get('account_payable'):
                supplier.account_payable_id = request.POST.get('account_payable')
            else:
                supplier.account_payable_id = None
            if request.POST.get('account_set'):
                supplier.account_set_id = request.POST.get('account_set')
            else:
                supplier.account_set_id = None
            if request.POST.get('term_days'):
                supplier.term_days = request.POST.get('term_days')
            else:
                supplier.term_days = None
            if request.POST.get('bank_code'):
                supplier.bank_id = request.POST.get('bank_code')
            else:
                supplier.bank_id = None
            if request.POST.get('payment_code'):
                supplier.payment_code_id = request.POST.get('payment_code')
            else:
                supplier.payment_code_id = None
            if request.POST.get('tax'):
                supplier.tax_id = request.POST.get('tax')
            else:
                supplier.tax_id = None
            if request.POST.get('distribution'):
                supplier.distribution_id = request.POST.get('distribution')
            else:
                supplier.distribution_id = None
            if request.POST.get('currency'):
                supplier.currency_id = request.POST.get('currency')
            else:
                supplier.currency_id = None
            if request.POST.get('credit_limit'):
                supplier.credit_limit = request.POST.get('credit_limit')
            else:
                supplier.credit_limit = None
            if request.POST.get('email'):
                supplier.email = request.POST.get('email')
            else:
                supplier.email = None
            if request.POST.get('email_msg'):
                supplier.email_msg = request.POST.get('email_msg')
            else:
                supplier.email_msg = None
            if request.POST.get('address'):
                supplier.address = request.POST.get('address')
            else:
                supplier.address = None
            if request.POST.get('phone'):
                supplier.phone = request.POST.get('phone')
            else:
                supplier.phone = None
            if request.POST.get('postal_code'):
                supplier.postal_code = request.POST.get('postal_code')
            else:
                supplier.postal_code = None
            if request.POST.get('country'):
                supplier.country_id = request.POST.get('country')
            else:
                supplier.country_id = None

            supplier.update_date = datetime.datetime.today()
            supplier.update_by = request.user.id
            supplier.is_active = supplier.is_active
            supplier.is_hidden = 0
            supplier.save()
            return HttpResponsePermanentRedirect(reverse('acc_vendor_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='supplier_edit')
            return HttpResponsePermanentRedirect(reverse('acc_vendor_list'))
    else:
        form = AccVendorInfoForm(request, instance=post)
        form.fields['tax'].widget.attrs['data-dis-code'] = []

        for i, optionSelect in enumerate(form.fields['tax'].widget.choices.queryset):
            if optionSelect.distribution_code_id:
                form.fields['tax'].widget.attrs['data-dis-code'].append(
                    {'idtax': optionSelect.id, 'dis_code': optionSelect.distribution_code_id})
        form.fields['tax'].widget.attrs['data-dis-code'] = json.dumps(form.fields['tax'].widget.attrs['data-dis-code'])
    supplier.update_date = supplier.update_date.strftime("%d-%m-%Y")
    return render_to_response('acc-vendor.html',
                              RequestContext(request, {'form': form, 'terms_code_list': TERMS_CODE,
                                                       'payment_code_list': payment_code_list,
                                                       'tax_code_list': tax_code_list,
                                                       'dis_code_list': dis_code_list, 'supplier': supplier,
                                                       'currency_code_list': currency_code_list
                                                       }))


@login_required
def AccountSupplierList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(account_set__code__icontains=search) |
            Q(payment_code__code__icontains=search) |
            Q(currency__code__icontains=search) |
            Q(tax__code__icontains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "code"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "3":
        column_name = "account_set__code"
    elif order_column == "4":
        column_name = "currency__code"
    elif order_column == "5":
        column_name = "tax__code"
    elif order_column == "6":
        column_name = "payment_code__code"
    elif order_column == "7":
        column_name = "is_active"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "customer_code": field.code,
                "customer_name": field.name,
                "account_set": field.account_set.code if field.account_set else '',
                "currency_code": field.currency.code if field.currency else '',
                "payment_mode": field.payment_code.code if field.payment_code else '',
                "is_active": str(field.is_active)}

        try:
            data['tax_code'] = field.tax.code if field.tax else '',
        except:
            data['tax_code'] = '',
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def CountrySetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Country.objects.filter(is_hidden=0)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__icontains=search)
                                             | Q(code__icontains=search)
                                             | Q(update_date__contains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "update_date"
        elif order_column == "1":
            column_name = "code"
        elif order_column == "2":
            column_name = "name"
        order_dir = request.GET['order[0][dir]']
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        if order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')

    except:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@csrf_exempt
@login_required
def load_tax_code(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            if 'tax_id' in request.POST and request.POST['tax_id']:
                tax_id = request.POST['tax_id']
                tax = Tax.objects.get(pk=tax_id)

                context = {
                    'name': tax.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@login_required
def get_supplier_code_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    try:
        supplier_list = Supplier.objects.filter(is_hidden=False, is_active=True, company_id=company.id)\
                        .order_by('code')\
                        .values_list('id', 'code')
        content = {
            "supplier_list": list(supplier_list)
        }

    except:
        content = {
            "supplier_list": []
        }
    
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def AP_AccountSetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = AccountSet.objects.filter(is_hidden=0, company_id=company_id, is_active=True,
                                                type=ACCOUNT_SET_TYPE_DICT['AP Account Set'])
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__contains=search)
                                             | Q(code__contains=search)
                                             | Q(control_account__code__contains=search)
                                             | Q(control_account__name__contains=search)
                                             | Q(revaluation_account__code__contains=search)
                                             | Q(revaluation_account__name__contains=search)
                                             | Q(currency__code__contains=search)
                                             | Q(currency__name__contains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "control_account__code"
        elif order_column == "3":
            column_name = "currency__code"
        elif order_column == "4":
            column_name = "revaluation_account__code"
        order_dir = request.GET['order[0][dir]']
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        if order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code,
                    "control_account": (field.control_account.code + '-' + field.control_account.name)
                    if field.control_account else '',
                    "currency_code": (field.currency.code + '-' + field.currency.name) if field.currency else '',
                    "currency_id": str(field.currency_id) if field.currency else '',
                    "revaluation_account": (field.revaluation_account.code + '-' + field.revaluation_account.name)
                    if field.revaluation_account else ''}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')

    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound



@login_required
def TaxSetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Tax.objects.filter(is_hidden=0,
                                         company_id=company_id,
                                         tax_group__company_id=company_id,
                                         tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Purchases']))
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__icontains=search)
                                             | Q(code__icontains=search)
                                             | Q(rate__icontains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "rate"
        order_dir = request.GET['order[0][dir]']
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        if order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code,
                    "rate": str(field.rate)
                    }
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound

