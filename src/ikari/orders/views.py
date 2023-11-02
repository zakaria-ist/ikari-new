import ast
import collections
import datetime
import decimal
import json
import math
import zipfile
import sys
import csv
import boto
from decimal import Decimal
from functools import partial, wraps
from io import BytesIO
from itertools import chain
from django.conf import settings as s
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.db import models
from django.db import transaction
from django.db.models import F, Q, Sum, Value as V
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce
from django.db.models.functions import Value
from django.views.decorators.csrf import csrf_exempt
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from accounting.models import FiscalCalendar
from accounts.models import Account, DistributionCode
from companies.models import Company
from contacts.models import Contact
from countries.models import Country
from currencies.models import Currency, ExchangeRate
from customers.models import Customer, CustomerItem, Delivery
from inventory.models import TransactionCode, StockTransaction
from taxes.models import TaxAuthority
from items.models import Item, ItemMeasure, ItemCategory
from locations.models import LocationItem, Location
from orders.forms import ExtraValueFormRight, ExtraValueFormLeft, AddItemForm, ExtraValueFormCode, OrderDeliveryForm, \
    OrderHeaderForm, OrderInfoForm, GoodReceiveSearchForm, DOInvoiceForm, GoodReceiveAddItemForm, GoodReceiveInfoForm, \
    PurchaseCrDbNoteAddItem, PurchaseCrDbNoteInfoForm, SaleCreditDebitNoteForm
from orders.models import Order, OrderHeader, OrderItem, OrderDelivery
from inventory.models import StockTransactionDetail
from reports.print_do_order import Print_DO_Order
from reports.print_packing_list import Print_Packing_List
from reports.print_po_order import Print_PO_Order
from reports.print_tax_invoice import Print_Tax_Invoice
from staffs.models import Staff
from suppliers.models import SupplierItem, Supplier
from taxes.models import Tax
from utilities.common import check_inventory_closing, check_sp_closing, generate_document_number, order_vs_inventory, \
    get_item_onhandqty, sp_to_acc, generate_errors, get_order_filter_range, round_number
from utilities.constants import ORDER_STATUS, ORDER_TYPE, TRN_CODE_TYPE_DICT, DIS_CODE_TYPE_REVERSED, COPY_ID, \
    TRANSACTION_TYPES, EDIT_TYPE, FLAG_TYPE_DICT, STATUS_TYPE_DICT, CONTACT_TYPES_DICT
from utilities.messages import SEND_DOC_FAILED, REFRESH_OR_GO_GET_SUPPORT, CHECK_SP_LOCKED
from transactions.models import Transaction
from .export_part_price import EXPORT_PURCHASE_PRICE_XLS, EXPORT_SALE_PRICE_XLS


# Create your views here.
@login_required
def load_list(request, order_type):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        try:
            so_template = s.SNP_TEMPLATE_ROOT + 'so_template.csv'
            po_template = s.SNP_TEMPLATE_ROOT + 'po_template.csv'
            gr_template = s.SNP_TEMPLATE_ROOT + 'gr_template.csv'
        except:
            so_template = ''
            po_template = ''
            gr_template = ''

        if int(order_type) == dict(ORDER_TYPE)['UPDATE SALES STATUS']:
            update_order_status(company_id, dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['SALES INVOICE'])
        elif int(order_type) == dict(ORDER_TYPE)['UPDATE PURCHASE STATUS']:
            update_order_status(company_id, dict(ORDER_TYPE)['PURCHASE ORDER'], dict(ORDER_TYPE)['PURCHASE INVOICE'])
        elif int(order_type) == dict(ORDER_TYPE)['UPDATE S&P STATUS']:
            update_order_status(company_id, dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['SALES INVOICE'])
            update_order_status(company_id, dict(ORDER_TYPE)['PURCHASE ORDER'], dict(ORDER_TYPE)['PURCHASE INVOICE'])
        return render_to_response('order_list.html',
                                  RequestContext(request, {'order_type': order_type, 'company': company,
                                                            'so_template': so_template,
                                                            'po_template': po_template,
                                                            'gr_template': gr_template}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def download_snp_template(request, order_type):
    s3_connection = boto.connect_s3(s.AWS_ACCESS_KEY_ID, s.AWS_SECRET_ACCESS_KEY)
    bucket = s3_connection.get_bucket(s.AWS_STORAGE_BUCKET_NAME)

    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        s3_file_path = bucket.get_key(s.SNP_TEMPLATE_ROOT + 'so_template.csv')
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        s3_file_path = bucket.get_key(s.SNP_TEMPLATE_ROOT + 'po_template.csv')
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
        s3_file_path = bucket.get_key(s.SNP_TEMPLATE_ROOT + 'gr_template.csv')
    elif int(order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
        s3_file_path = bucket.get_key(s.SNP_TEMPLATE_ROOT + 'do_template.csv')

    url = s3_file_path.generate_url(expires_in=600) # expiry time is in seconds

    return HttpResponseRedirect(url)



def update_order_status(company_id, order_type, delivery):
    # Sync SO
    order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__status__gte=dict(ORDER_STATUS)['Sent'])
    SO_items_list = order_item_list.filter(order__order_type=order_type).order_by('-order__document_number')
    DO_items_list = order_item_list.filter(order__order_type=delivery).order_by('-order__document_number')

    current_document_number = ""
    for item in SO_items_list:
        if current_document_number == item.order.document_number:
            continue

        current_document_number = item.order.document_number

        SO_items = SO_items_list.filter(order__document_number=current_document_number)
        DO_items = DO_items_list.filter(refer_number=current_document_number)

        all_DO_items_value = 0
        all_SO_items_value = 0
        for SO_item in SO_items:
            all_SO_items_value += SO_item.quantity

        for DO_item in DO_items:
            all_DO_items_value += DO_item.quantity

        if all_DO_items_value == 0:
            status = dict(ORDER_STATUS)['Sent']
        elif all_DO_items_value < all_SO_items_value:
            status = dict(ORDER_STATUS)['Partial']
        else:
            status = dict(ORDER_STATUS)['Delivered'] \
                if order_type == dict(ORDER_TYPE)['SALES ORDER'] else dict(ORDER_STATUS)['Received']

        # Save status to db
        order = Order.objects.filter(is_hidden=0, company_id=company_id,
                                     document_number=current_document_number).first()
        order.status = status
        order.save()


@login_required
@permission_required('orders.add_order', login_url='/alert/')
def order_new(request, order_type, style='N'):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    order = None

    order_status = dict(ORDER_STATUS)['Draft']
    customer, supplier, tax_id, currency_id = get_customer_supplier(request, order_type, company_id)
    currency_symbol = Currency.objects.filter(is_hidden=0).first().symbol

    form = OrderHeaderForm(request.POST)
    form_info = OrderInfoForm(company_id, order_type, request.POST, session_date=request.session['session_date'])
    items_list = OrderItem.objects.none()

    # Define formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ItemFormSet = formset_factory(wraps(AddItemForm)(partial(AddItemForm, company_id)))

    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        trn_code_type = int(TRN_CODE_TYPE_DICT['Sales Number File'])
        code = 'S/O'
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        trn_code_type = int(TRN_CODE_TYPE_DICT['Purchase Number File'])
        code = 'P/O'

    stock_transaction_code = TransactionCode.objects.filter(is_hidden=False, company_id=company_id, code=code,
                                                            menu_type=trn_code_type).first()
    if stock_transaction_code:
        doc_num_auto = stock_transaction_code.auto_generate
    else:
        doc_num_auto = True

    if request.method == 'POST':
        try:
            with transaction.atomic():
                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')

                if formset_left.is_valid() and formset_right.is_valid() and formset_item.is_valid():
                    # if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                    #     if not validate_quantity(request, company_id, formset_item):
                    #         form_delivery = OrderDeliveryForm(company_id)

                    #         return so_po_error_render(request, company, form, form_info, items_list, order_type, formset_right,
                    #                                   formset_left, formset_item, customer, supplier, currency_symbol,
                    #                                   order_status, form_delivery, doc_num_auto)
                    # order process
                    order = save_order(request, company_id, order_type)
                    save_order_header(request, order.id, formset_right, formset_left)
                    fail = save_order_item(request, order.id, order.status, formset_item, company.is_inventory,
                                           order_type)
                    if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                        form_delivery = OrderDeliveryForm(company_id, request.POST)
                        if form_delivery and form_delivery.is_valid() and not fail:
                            order_delivery = form_delivery.save(commit=False)
                            order_delivery.order_id = order.id
                            order_delivery.create_date = datetime.datetime.today()
                            order_delivery.update_date = datetime.datetime.today()
                            order_delivery.update_by_id = request.user.id
                            order_delivery.is_hidden = 0
                            if not request.POST.get('delivery'):
                                order_delivery.contact_id = request.POST.get('contact_id') if request.POST.get(
                                    'contact_id') else None
                                order_delivery.delivery_id = None
                            else:
                                order_delivery.contact_id = None
                                order_delivery.delivery_id = request.POST.get('delivery') if request.POST.get(
                                    'delivery') else None
                            order_delivery.save()
                        else:
                            print("order_PO_add form_delivery.errors, fail: ", form_delivery.errors, fail)

                    if fail == None:
                        pass
                    elif fail:
                        order.status = dict(ORDER_STATUS)['Draft']
                        # order.document_number = None
                        order.save()
                    else:  # Success
                        if order.status >= dict(ORDER_STATUS)['Sent']:
                            save_order_info(request, order, company_id, order.document_number)
                else:
                    print("order_new formset_left.errors, formset_right.errors, formset_item.errors: ",
                          formset_left.errors, formset_right.errors, formset_item.errors)
            if order:
                messages.success(request, "Document number " + order.document_number if order.document_number else '' + " was successfully created")
            else:
                messages.add_message(request, messages.ERROR, 'Error happend. Something went wrong.', extra_tags='order_new')
            return HttpResponsePermanentRedirect(reverse('order_new', args=[order_type, style]))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='order_new')

    # end if POST
    form_info = OrderInfoForm(company_id, order_type, initial={'tax': tax_id, 'currency': currency_id}, session_date=request.session['session_date'])
    form = OrderHeaderForm()
    formset_right = ExtraValueFormSetRight(prefix='formset_right')
    formset_left = ExtraValueFormSetLeft(prefix='formset_left')
    formset_item = ItemFormSet(prefix='formset_item')
    if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        form_delivery = OrderDeliveryForm(company_id)
    else:
        form_delivery = None

    return so_po_error_render(request, company, form, form_info, items_list, order_type, formset_right,
                              formset_left, formset_item, customer, supplier, currency_symbol, order_status, form_delivery, doc_num_auto, style)


@login_required
@permission_required('orders.change_order', login_url='/alert/')
def order_edit(request, order_id, order_type, copy_id, msg='0', style='N'):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    order, order_header_list, order_header, order_item = get_orders_object(order_type, order_id, company_id)
    company, currency_symbol = get_company_currencysymbol(order)
    order_status = order.status
    decimal_place = order.currency.is_decimal

    # get label and value formset right
    extra_right = order_header_list.filter(x_position=1, y_position=1).values()
    # get label and value formset left
    extra_left = order_header_list.filter(x_position=0, y_position=1).values()
    # get label and value formset code
    extra_code = order_header_list.filter(x_position=1, y_position=2).values()

    customer, supplier, tax_id, currency_id = get_customer_supplier(request, order_type, company_id, order)
    # form
    form_info = OrderInfoForm(company_id, order_type, request.POST)

    # get list if items
    items_list = get_items_list(order_type, order, supplier, company_id)

    # formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(AddItemForm)(partial(AddItemForm, company.id)))

    try:
        so_order = Order.objects.get(document_number=order.reference_number)
    except:
        so_order = None
    if so_order and so_order.customer:
        kwargs, contact = get_order_delivery_kwargs(company_id, so_order.customer.id, order_id)
    else:
        kwargs, contact = get_order_delivery_kwargs(company_id, 0, order_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                fail = False
                if int(copy_id) == dict(COPY_ID)['Edit Existing']:
                    form = OrderHeaderForm(request.POST, instance=order_header)
                    form_info = OrderInfoForm(company_id, order_type, request.POST, instance=order)
                    formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                    formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                    formset_item = ItemFormSet(request.POST, prefix='formset_item', initial=order_item)
                    if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                        form_delivery = OrderDeliveryForm(company_id, **kwargs)
                        try:
                            customer_delivery = Delivery.objects.get(pk=kwargs['instance'].delivery_id)
                        except Exception as e:
                            print(e)
                            customer_delivery = None
                    else:
                        form_delivery = None
                        customer_delivery = None

                    if form.is_valid() and form_info.is_valid() and formset_item.is_valid():
                        # auto change the refer line of related
                        sid_one = transaction.savepoint()
                        index_order_items = json.loads(request.POST.get('index_order_items', []))
                        for item in index_order_items:
                            refer_line = int(item['refer_line'])
                            new_refer_line = int(item['new_refer_line'])
                            if refer_line != new_refer_line and new_refer_line > 0:
                                OrderItem.objects.filter(pk=item['refer_id']).update(refer_line=new_refer_line)

                        if not validate_editing(request, order_type, company_id, order_id, formset_item):
                            transaction.savepoint_rollback(sid_one)
                            form_info = OrderInfoForm(company_id, order_type, instance=order)
                            formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
                            return edit_so_po_error_render(request, order_type, company, form, form_info, items_list,
                                                           formset_right, copy_id, currency_symbol, order_status,
                                                           formset_left, formset_item, supplier, order, form_delivery, 
                                                           customer_delivery, decimal_place, msg, style)

                        delete_order_header_list(order_header_list)
                        save_order_header(request, order_id, formset_right, formset_left, form)
                        info = save_header_info(request, company_id, form_info, order_id, order_status, order_type)

                        last_item_qty = delete_order_item(request, order_id, company_id)
                        fail = save_order_item(request, order.id, order.status, formset_item, company.is_inventory,
                                               order_type, last_item_qty, order_status)
                        if not fail and int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
                            new_order_item = OrderItem.objects.filter(is_hidden=0, order_id=order.id, quantity__gt=F('delivery_quantity'))
                            if new_order_item.exists():
                                partial_order_item = OrderItem.objects.filter(is_hidden=0, order_id=order.id, delivery_quantity__gt=0)
                                if partial_order_item.exists():
                                    order.status = dict(ORDER_STATUS)['Partial']
                                else:
                                    order.status = dict(ORDER_STATUS)['Sent']
                                order.save()
                            else:
                                order.status = dict(ORDER_STATUS)['Delivered']
                                order.save()
                            update_so_related_order(request, order.id, company)
                        elif not fail and int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                            new_order_item = OrderItem.objects.filter(is_hidden=0, order_id=order.id, quantity__gt=F('receive_quantity'))
                            if new_order_item.exists():
                                partial_order_item = OrderItem.objects.filter(is_hidden=0, order_id=order.id, receive_quantity__gt=0)
                                if partial_order_item.exists():
                                    order.status = dict(ORDER_STATUS)['Partial']
                                else:
                                    order.status = dict(ORDER_STATUS)['Sent']
                                order.save()
                            else:
                                order.status = dict(ORDER_STATUS)['Received']
                                order.save()
                            update_po_related_order(request, order.id, company)
                        if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                            form_delivery = OrderDeliveryForm(company_id, request.POST, **kwargs)
                            if form_delivery.is_valid() and not fail:
                                order_delivery = form_delivery.save(commit=False)
                                order_delivery.order_id = order.id
                                order_delivery.create_date = datetime.datetime.today()
                                order_delivery.update_date = datetime.datetime.today()
                                order_delivery.update_by_id = request.user.id
                                order_delivery.is_hidden = 0
                                if not request.POST.get('delivery'):
                                    order_delivery.contact_id = request.POST.get('contact_id') if request.POST.get(
                                        'contact_id') else None
                                    order_delivery.delivery_id = None
                                else:
                                    order_delivery.contact_id = None
                                    order_delivery.delivery_id = request.POST.get('delivery') if request.POST.get(
                                        'delivery') else None
                                order_delivery.save()
                            else:
                                print("order_PO_edit form_delivery.errors, fail: ", form_delivery.errors, fail)

                        if fail == None:
                            pass
                        elif fail:
                            transaction.savepoint_rollback(sid_one)
                            order.status = dict(ORDER_STATUS)['Draft']
                            # order.document_number = None
                            order.save()
                        else:  # Success
                            if int(order_status) >= dict(ORDER_STATUS)['Sent']:
                                save_order_info(request, order, company_id,
                                                info.document_number if 'info' in locals() else '')
                    else:
                        print("order_edit1 form.errors, form_info.errors, formset_item.errors: ", form.errors,
                              form_info.errors, formset_item.errors)

                elif int(copy_id) == dict(COPY_ID)['Copy']:
                    form = OrderHeaderForm(request.POST)
                    formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                    formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                    formset_item = ItemFormSet(request.POST, prefix='formset_item')
                    if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                        form_delivery = OrderDeliveryForm(company_id, request.POST, **kwargs)

                    # order process
                    if form.is_valid() and form_info.is_valid() and formset_item.is_valid():
                        copy_order = save_order(request, company_id, order_type)
                        save_order_header(request, copy_order.id, formset_right, formset_left, form)

                        last_item_qty = ast.literal_eval(request.POST['initial_item_qty_data'])
                        fail = save_order_item(request, copy_order.id, copy_order.status, formset_item,
                                               company.is_inventory,
                                               order_type, last_item_qty, order_status)
                        if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                            if form_delivery.is_valid() and not fail:
                                order_delivery = form_delivery.save(commit=False)
                                order_delivery.order_id = order.id
                                order_delivery.create_date = datetime.datetime.today()
                                order_delivery.update_date = datetime.datetime.today()
                                order_delivery.update_by_id = request.user.id
                                order_delivery.is_hidden = 0
                                if not request.POST.get('delivery'):
                                    order_delivery.contact_id = request.POST.get('contact_id') if request.POST.get(
                                        'contact_id') else None
                                    order_delivery.delivery_id = None
                                else:
                                    order_delivery.contact_id = None
                                    order_delivery.delivery_id = request.POST.get('delivery') if request.POST.get(
                                        'delivery') else None
                                order_delivery.save()
                            else:
                                print("order_PO_edit form_delivery.errors, fail: ", form_delivery.errors, fail)

                        if fail == None:
                            pass
                        elif fail:
                            order.status = dict(ORDER_STATUS)['Draft']
                            # order.document_number = None
                            order.save()
                        else:  # Success
                            if int(order_status) >= dict(ORDER_STATUS)['Sent']:
                                update_document_number(request, copy_order, company_id, order_type)
                    else:
                        print("order_edit2 form.errors, form_info.errors, formset_item.errors: ", form.errors,
                              form_info.errors, formset_item.errors)

            return HttpResponseRedirect('/orders/list/' + order_type + '/')
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='order_edit')

    # end if POST
    form = OrderHeaderForm(instance=order_header)
    form_info = OrderInfoForm(company_id, order_type, instance=order)
    # load formset values
    formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
    formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
    formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
    if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        form_delivery = OrderDeliveryForm(company_id, **kwargs)
        try:
            customer_delivery = Delivery.objects.get(pk=kwargs['instance'].delivery_id)
        except Exception as e:
            print(e)
            customer_delivery = None
    else:
        form_delivery = None
        customer_delivery = None

    return edit_so_po_error_render(request, order_type, company, form, form_info, items_list,
                                   formset_right, copy_id, currency_symbol, order_status, formset_left,
                                   formset_item, supplier, order, form_delivery, customer_delivery, 
                                   decimal_place, msg, style)


def update_so_related_order(request, order_id, company):
    try:
        current_so_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                        order_id=order_id).order_by('line_number')

        # Next we find PO, DO
        po_do_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                        order__order_type__in=(dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                                dict(ORDER_TYPE)['SALES INVOICE']),
                                                        reference_id=order_id)
        ch_cust_po_no = False
        ch_w_date = False
        ch_s_date = False
        ch_remark = False
        po_doc = ''
        gr_doc = ''
        do_doc = ''
        if po_do_order_item_list:
            for so_order_item in current_so_order_items:
                so_ln_number = so_order_item.line_number
                so_item = so_order_item.item_id
                so_cust_po = so_order_item.customer_po_no
                so_w_date = so_order_item.wanted_date
                so_s_date = so_order_item.schedule_date
                so_remark = so_order_item.description

                po_do_items = po_do_order_item_list.filter(refer_line=so_ln_number, item_id=so_item)
                for po_do_item in po_do_items:
                    if po_do_item.order.order_type == int(dict(ORDER_TYPE)['PURCHASE ORDER']):
                        po_doc = po_do_item.order.document_number
                        if po_do_item.customer_po_no != so_cust_po:
                            po_do_item.customer_po_no = so_cust_po
                            ch_cust_po_no = True
                        # if po_do_item.wanted_date != so_w_date:
                        #     po_do_item.wanted_date = so_w_date
                        #     ch_w_date = True
                        # if po_do_item.schedule_date != so_s_date:
                        #     po_do_item.schedule_date = so_s_date
                        #     ch_s_date = True
                        if po_do_item.description != so_remark:
                            po_do_item.description = so_remark
                            ch_remark = True
                            
                        # check if there is related GR
                        gr_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                        order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                        reference_id=po_do_item.order.id, refer_line=po_do_item.line_number, item_id=so_item)
                        for gr_item in gr_order_item_list:
                            gr_doc = gr_item.order.document_number
                            if gr_item.customer_po_no != so_cust_po:
                                gr_item.customer_po_no = so_cust_po
                                ch_cust_po_no = True
                            gr_item.save()

                    elif po_do_item.order.order_type == int(dict(ORDER_TYPE)['SALES INVOICE']):
                        do_doc = po_do_item.order.document_number
                        if po_do_item.customer_po_no != so_cust_po:
                            po_do_item.customer_po_no = so_cust_po
                            ch_cust_po_no = True
            
                    po_do_item.save()

        msg = ''
        if ch_cust_po_no:
            msg += '"customer_po",' + '  '
        if ch_w_date:
            msg += '"wanted_date",' + '  '
        if ch_s_date:
            msg += '"schedule_date",' + '  '
        if ch_remark:
            msg += '"remark",' + '  '
        if len(msg):
            msg += 'updated to related doc ' + po_doc + ' ' + gr_doc + ' ' + do_doc
            messages.add_message(request, messages.SUCCESS, msg,
                                    extra_tags='update_so_related_order')

    except Exception as e:
        messages.add_message(request, messages.ERROR, 'There was an error while updating related doc',
                                    extra_tags='update_so_related_order')

    return True
    

def update_po_related_order(request, order_id, company):
    try:
        current_po_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                        order_id=order_id).order_by('line_number')

        # Next we find GR
        gr_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                        order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                        reference_id=order_id)
        ch_cust_po_no = False
        ch_w_date = False
        ch_s_date = False
        ch_remark = False
        po_doc = ''
        gr_doc = ''
        do_doc = ''

        for po_order_item in current_po_order_items:
            if po_order_item.reference_id:
                po_ln_number = po_order_item.line_number
                po_item = po_order_item.item_id
                po_cust_po = po_order_item.customer_po_no
                po_w_date = po_order_item.wanted_date
                po_s_date = po_order_item.schedule_date
                po_remark = po_order_item.description

                # Next we update GR 
                gr_items = gr_order_item_list.filter(refer_line=po_ln_number, item_id=po_item)
                for gr_item in gr_items:
                    gr_doc = gr_item.order.document_number
                    if gr_item.customer_po_no != po_cust_po:
                        gr_item.customer_po_no = po_cust_po
                        ch_cust_po_no = True
                    gr_item.save()


                # Next we update SO    
                so_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                            order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                            line_number=po_order_item.refer_line, item_id=po_item,
                                                            order_id=po_order_item.reference_id)
                for so_order_item in so_order_items:
                    so_doc = so_order_item.order.document_number
                    if so_order_item.customer_po_no != po_cust_po:
                        so_order_item.customer_po_no = po_cust_po
                        ch_cust_po_no = True
                    # if so_order_item.wanted_date != po_w_date:
                    #     so_order_item.wanted_date = po_w_date
                    #     ch_w_date = True
                    # if so_order_item.schedule_date != po_s_date:
                    #     so_order_item.schedule_date = po_s_date
                    #     ch_s_date = True
                    if so_order_item.description != po_remark:
                        so_order_item.description = po_remark
                        ch_remark = True
                    so_order_item.save()

                    # check if there is related DO
                    so_item = so_order_item.item_id
                    do_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company.id,
                                                        order__order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                                        reference_id=so_order_item.order.id, refer_line=so_order_item.line_number, item_id=so_item)
                    for do_item in do_order_item_list:
                        do_doc = do_item.order.document_number
                        if do_item.customer_po_no != po_cust_po:
                            do_item.customer_po_no = po_cust_po
                            ch_cust_po_no = True
                        do_item.save()

        msg = ''
        if ch_cust_po_no:
            msg += '"customer_po",' + '  '
        if ch_w_date:
            msg += '"wanted_date",' + '  '
        if ch_s_date:
            msg += '"schedule_date",' + '  '
        if ch_remark:
            msg += '"remark",' + '  '
        if len(msg):
            msg += 'updated to related doc ' + so_doc + ' ' + gr_doc + ' ' + do_doc
            messages.add_message(request, messages.SUCCESS, msg,
                                    extra_tags='update_po_related_order')
    except Exception as e:
        messages.add_message(request, messages.ERROR, 'There was an error while updating related doc',
                                    extra_tags='update_po_related_order')
    return True


def validate_editing(request, order_type, company_id, order_id, formset_item):
    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        return validate_so_editing(request, company_id, order_id, formset_item)
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        return validate_po_editing(request, company_id, order_id, formset_item)
    return False


def validate_deleting(request, order_type, order_id):
    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        return validate_so_deleting(request, order_id)
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        return validate_po_deleting(request, order_id)
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
        return [True, '']
    elif int(order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
        return [True, '']
    return [False, '']


def validate_po_deleting(request, order_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    # First we get all the order item of the current order
    current_po_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id)
    # current_po_order_item_list = list(current_po_order_items)
    # current_po_order_customer_po_no = set([item.customer_po_no for item in current_po_order_item_list])

    # Next we find SO, GR with the same Customer PO
    gr_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                  reference_id=order_id)

    if gr_order_item_list:
        gr_order_item_list = gr_order_item_list.order_by().values("order__document_number").distinct()
        gr_order_list = ''
        for gr_order_item in gr_order_item_list:
            gr_order_list += gr_order_item['order__document_number'] + ','
        gr_order_list = gr_order_list[:-1]

        # messages.add_message(request, messages.ERROR,
        #                      "Please delete document no" + gr_order_list + "first!",
        #                      extra_tags='order_edit_so_validation_related')
        return [False, gr_order_list]

    return [True, '']


def validate_so_deleting(request, order_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    # First we get all the order item of the current order
    current_so_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id)
    current_so_order_item_list = list(current_so_order_items)

    # current_so_order_customer_po_no = set([item.customer_po_no for item in current_so_order_item_list])

    # Next we find PO, DO with the same Customer PO
    po_do_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                     order__order_type__in=(dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                            dict(ORDER_TYPE)['SALES INVOICE']),
                                                     reference_id=order_id)

    if po_do_order_item_list:
        po_do_order_item_list = po_do_order_item_list.order_by().values("order__document_number").distinct()
        po_do_order_list = ''
        for po_do_order_item in po_do_order_item_list:
            po_do_order_list += po_do_order_item['order__document_number'] + ','
        po_do_order_list = po_do_order_list[:-1]

        # messages.add_message(request, messages.ERROR,
        #                      "Please delete document no" + po_do_order_list + "first!",
        #                      extra_tags='order_edit_so_validation_related')
        return [False, po_do_order_list]

    return [True, '']


def validate_po_editing(request, company_id, order_id, formset_item):
    # First we get all the order item of the current order
    current_po_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id).order_by('line_number')
    # current_po_order_item_list = list(current_po_order_items)
    # current_po_order_customer_po_no = set([item.customer_po_no for item in current_po_order_item_list])

    # Next we find SO, GR
    ref_so_orders = current_po_order_items.filter(reference__is_hidden=0, reference__company_id=company_id,
                                                  reference__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                  ).exclude(reference_id__isnull=True)\
        .values_list('reference_id', flat=True)\
        .order_by('reference_id').distinct()
    # so_order_item_list = OrderItem.objects.filter(order_id__in=ref_so_orders, is_hidden=False)

    gr_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                  reference_id=order_id)
    #  customer_po_no__in=current_po_order_customer_po_no)

    # Create new dictionary of new PO quantity
    newquantity_dict = collections.OrderedDict()
    for form in formset_item:
        new_dict_key = form.cleaned_data.get('line_number') + form.cleaned_data.get('customer_po_no')
        newquantity_dict[new_dict_key] = form.cleaned_data.get('quantity')

    # po_order_item_length = len(formset_item)

    # If SO exist, we need to make sure SO has bigger quantity
    # so_order_item_list = so_gr_order_item_list.filter(order__order_type=dict(ORDER_TYPE)['SALES ORDER'])
    # if so_order_item_list:
    #     i = 0
    #     for po_order in current_po_order_items:
    #         if po_order.refer_line:
    #             so_line_number = po_order.refer_line
    #         else:
    #             so_line_number = 0

    #         po_customer_po_no = po_order.customer_po_no

    #         so_order_item = so_order_item_list.filter(customer_po_no=po_customer_po_no, line_number=so_line_number)

    #         # If order item is no longer found in PO
    #         if not so_order_item:
    #             messages.add_message(request, messages.ERROR,
    #                                  "Please delete document no " + po_order.reference.document_number + " first!",
    #                                  extra_tags='order_edit_po_validation_related')
    #             return False

    #         po_dict_key = str(po_order.line_number) + po_customer_po_no
    #         total_so_qty = so_order_item.aggregate(total_qty=Sum('quantity'))
    #         so_order_itm = so_order_item.first()
    #         try:
    #             if float(total_so_qty['total_qty']) < newquantity_dict[po_dict_key]:
    #                 messages.add_message(request, messages.ERROR,
    #                                      "Failed to Save this P/O ! <br />Quantity of item " +
    #                                      so_order_itm.item.code + " in S/O number " +
    #                                      so_order_itm.order.document_number +
    #                                      "  is less than this PO.<br />Please modify " +
    #                                      so_order_itm.order.document_number + " first",
    #                                      extra_tags='order_edit_po_validation_qty')
    #                 return False
    #         except Exception as e:
    #             # If the attempt is less then PO length, try the next one
    #             if i < po_order_item_length:
    #                 continue

    #             print(e)
    #             messages.add_message(request, messages.ERROR,
    #                                  "To remove item please modify " + so_order_itm.order.document_number + " first!",
    #                                  extra_tags='order_edit_po_validation_deletion')
    #             return False
    #         # If the attempt has reached PO lenght, then exit
    #         i += 1
    #         if (i == po_order_item_length):
    #             break

    # If GR exist, we need to make sure new PO has bigger quantity
    # gr_order_item_list = so_gr_order_item_list.filter(order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'])
    if gr_order_item_list:
        for gr_order in gr_order_item_list:
            po_line_number = gr_order.refer_line
            po_customer_po_no = gr_order.customer_po_no
            # po_order_item = current_po_order_items.filter(customer_po_no=po_customer_po_no, line_number=po_line_number)

            # If order item is no longer found in PO
            # if not po_order_item:
            #     messages.add_message(request, messages.ERROR,
            #                          "Please delete document no " + gr_order.reference.document_number + " first!",
            #                          extra_tags='order_edit_gr_validation_related')
            #     return False

            old_dict_key = str(po_line_number) + po_customer_po_no
            # If new amount < GR
            try:
                if newquantity_dict[old_dict_key] < gr_order.quantity:
                    messages.add_message(request, messages.ERROR,
                                         "To reduce quantiy please delete " + gr_order.order.document_number + " first!",
                                         extra_tags='order_edit_gr_validation_qty')
                    return False
            except Exception as e:
                pass
                # messages.add_message(request, messages.ERROR,
                #                      "To remove item please modify " + gr_order.order.document_number + " first!",
                #                      extra_tags='order_edit_gr_validation_deletion')
                # return False

    return True


def validate_quantity(request, company_id, formset_item):
    for form in formset_item:
        ref_so = form.cleaned_data.get('ref_number')
        ref_line = form.cleaned_data.get('refer_line')
        quantity = int(form.cleaned_data.get('quantity'))
        # check if there are po order item for this line
        if ref_so and ref_line:
            po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                   reference__document_number=ref_so, refer_line=ref_line,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                .aggregate(quantity=Sum('quantity'))['quantity']

            so_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                     order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                     order__document_number=ref_so, line_number=ref_line).last()
            if so_order_item:
                if po_item_qty:
                    quantity += po_item_qty
                if quantity > so_order_item.quantity:
                    messages.add_message(request, messages.ERROR,
                                         "Failed to Save this P/O ! <br />Quantity of item " +
                                         so_order_item.item.code + " in S/O number " +
                                         so_order_item.order.document_number +
                                         "  is " + str(so_order_item.quantity) + " which is less than this PO.<br />Please modify " +
                                         so_order_item.order.document_number + " first",
                                         extra_tags='order_po_validation_qty')

                    return False

    return True


def validate_so_editing(request, company_id, order_id, formset_item):
    # First we get all the order item of the current order
    current_so_order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id)
    # current_so_order_item_list = list(current_so_order_items)

    # current_so_order_customer_po_no = set([item.customer_po_no for item in current_so_order_item_list])

    # Next we find PO, DO
    po_do_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                     order__order_type__in=(dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                            dict(ORDER_TYPE)['SALES INVOICE']),
                                                     reference_id=order_id)
    #  customer_po_no__in=current_so_order_customer_po_no)

    # If no record in PO or DO, then user is free to change
    if not po_do_order_item_list:
        return True

    newquantity_dict = {}
    for form in formset_item:
        new_dict_key = form.cleaned_data.get('line_number') + form.cleaned_data.get('item_id')
        newquantity_dict[new_dict_key] = form.cleaned_data.get('quantity')

    # If record found, then we need to make sure the amount in PO or DO is lesser than SO
    for po_do_order_item in po_do_order_item_list:
        # First find the corresponding SO
        # so_customer_po_no = po_do_order_item.customer_po_no
        so_line_number = po_do_order_item.refer_line
        so_item = po_do_order_item.item_id
        # so_order_item = current_so_order_items.filter(customer_po_no=so_customer_po_no, line_number=so_line_number)

        # if not so_order_item:
        #     messages.add_message(request, messages.ERROR,
        #                          "Please modify document no " + po_do_order_item.order.document_number + " first!",
        #                          extra_tags='order_edit_so_validation_related')
        #     return False

        # If the SO order item is found, then compare the quantity
        # old_dict_key = str(so_line_number) + so_customer_po_no
        old_dict_key = str(so_line_number) + str(so_item)
        try:
            if newquantity_dict[old_dict_key] < po_do_order_item.quantity:
                if po_do_order_item.order.order_type == dict(ORDER_TYPE)['PURCHASE ORDER']:
                    continue
                messages.add_message(request, messages.ERROR,
                                     "To reduce quantity please modify " +
                                     po_do_order_item.order.document_number + " first!",
                                     extra_tags='order_edit_so_validation_qty')
                return False
        except Exception as e:
            pass
            # messages.add_message(request, messages.ERROR,
            #                      "To remove item please modify " + po_do_order_item.order.document_number + " first!",
            #                      extra_tags='order_edit_so_validation_deletion')
            # return False

    # End loop, no issue found
    return True


def save_order_info(request, order, company_id, wish_doc_no):
    cont = True
    while cont:
        # check one more time
        if wish_doc_no != '':
            check_order_count = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                     document_number=wish_doc_no).count()
        else:
            check_order_count = 0

        if check_order_count > 1:
            doc_no = order.document_number.split('-')
            postfix = int(doc_no[-1]) + 1
            wish_doc_no = doc_no[0] + '-' + doc_no[1] + '-' + '{:05}'.format(postfix % 100000)
            order.document_number = wish_doc_no

            order.subtotal = Decimal(request.POST.get('subtotal'))
            order.total = Decimal(request.POST.get('total'))
            order.tax_amount = Decimal(request.POST.get('tax_amount'))

            order.save()
        else:
            cont = False


def update_document_number(request, order, company_id, order_type):
    dict_key = ''
    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        dict_key = 'Sales Number File'
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        dict_key = 'Purchase Number File'

    trn_code_type = int(TRN_CODE_TYPE_DICT[dict_key])
    order.document_number = generate_document_number(company_id,
                                                     request.POST.get('document_date'),
                                                     trn_code_type,
                                                     request.POST.get('transaction_code'))

    order.subtotal = Decimal(request.POST.get('subtotal'))
    order.total = Decimal(request.POST.get('total'))
    order.tax_amount = Decimal(request.POST.get('tax_amount'))

    order.save()


def get_customer_supplier(request, order_type, company_id, order=None):
    customer = Customer.objects.none()
    supplier = Supplier.objects.none()
    tax_id = currency_id = 0
    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        if order != None:
            customer = Customer.objects.get(pk=order.customer_id)
        if not customer:
            customer = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()

        if not customer:
            messages.add_message(request, messages.ERROR,
                                 "The Company doesn't have any customer. Please add customer first and try again!",
                                 extra_tags='order_new_empty_customer')
            return HttpResponseRedirect(reverse('order_list', args=(), kwargs={'order_type': order_type}))

        tax_id = customer.tax_id if customer.tax else ''
        currency_id = customer.currency_id if customer.currency_id else ''
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        if order != None:
            if order.supplier_id != None:
                supplier = Supplier.objects.get(pk=order.supplier_id)
        if not supplier:
            supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()

        if not supplier:
            messages.add_message(request, messages.ERROR,
                                 "The Company doesn't have any supplier. Please add supplier first and try again!",
                                 extra_tags='order_new_empty_supplier')
            return HttpResponseRedirect(reverse('order_list', args=(), kwargs={'order_type': order_type}))

        tax_id = supplier.tax_id if supplier.tax else ''
        currency_id = supplier.currency_id if supplier.currency_id else ''

    return customer, supplier, tax_id, currency_id


def delete_order_header_list(order_header_list):
    order_header_list.filter(x_position=1, y_position=1).delete()
    order_header_list.filter(x_position=0, y_position=1).delete()
    order_header_list.filter(x_position=1, y_position=2).delete()


def save_order_header(request, order_id, formset_right, formset_left, form=None):
    order_header = None

    if form != None:
        if form.is_valid():
            order_header = form.save(commit=False)
        else:
            print("save_order_header form.errors: ", form.errors)
    else:
        if OrderHeaderForm(request.POST):
            order_header = OrderHeader()

    if order_header != None:
        order_header.x_position = 1
        order_header.y_position = 0
        order_header.label = request.POST.get('label')
        order_header.value = request.POST.get('value')
        order_header.create_date = datetime.datetime.today()
        order_header.update_date = datetime.datetime.today()
        order_header.update_by_id = request.user.id
        order_header.is_hidden = False
        order_header.order_id = order_id
        order_header.save()

    if formset_right.is_valid():
        for form in formset_right:
            order_header = OrderHeader()
            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                    'value') is not None:
                order_header.x_position = 1
                order_header.y_position = 1
                order_header.label = form.cleaned_data.get('label')
                order_header.value = form.cleaned_data.get('value')
                order_header.create_date = datetime.datetime.today()
                order_header.update_date = datetime.datetime.today()
                order_header.update_by_id = request.user.id
                order_header.is_hidden = False
                order_header.order_id = order_id
                order_header.save()
    else:
        print("save_order_header formset_right.errors: ", formset_right.errors)

    if formset_left.is_valid():
        for form in formset_left:
            order_header = OrderHeader()
            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                    'value') is not None:
                order_header.x_position = 0
                order_header.y_position = 1
                order_header.label = form.cleaned_data.get('label')
                order_header.value = form.cleaned_data.get('value')
                order_header.create_date = datetime.datetime.today()
                order_header.update_date = datetime.datetime.today()
                order_header.update_by_id = request.user.id
                order_header.is_hidden = False
                order_header.order_id = order_id
                order_header.save()
    else:
        print("save_order_header formset_left.errors: ", formset_left.errors)


def delete_order_item(request, order_id, company_id):
    last_item_qty = ast.literal_eval(request.POST['initial_item_qty_data'])
    order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order_id=order_id)
    for order_item in order_item_list:
        order_item.is_hidden = True
        order_item.save()

    return last_item_qty


def update_do_supplier(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order_item_list = OrderItem.objects \
        .select_related('order', 'supplier', 'item')\
        .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
        .exclude(supplier__isnull=False)

    for do in order_item_list:
        so = None
        try:
            oi = OrderItem.objects \
                .select_related('order', 'item') \
                .filter(
                    Q(order__is_hidden=0,
                        order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                        order_id=do.reference_id,
                        item_id=do.item_id,
                        line_number=do.refer_line)
                    |
                    Q(order__is_hidden=0,
                        order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                        order__document_number=do.refer_number,
                        item_id=do.item_id,
                        line_number=do.refer_line)).order_by('order__document_date')
            so = oi.first() if oi else None
            if so:
                do.supplier = so.supplier
                do.save()
        except Exception as e:
            print(e)

    messages.add_message(request, messages.SUCCESS, 'D/O orders are updated', extra_tags='do_update')
    return redirect('/orders/list/6/')


def create_so_from_csv(request):
    with transaction.atomic():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        customers = Customer.objects.filter(is_hidden=False, is_active=True, company_id=company_id) \
            .order_by('code') \
            .values_list('id', 'code')

        fail_list = []
        fail = False
        order = None
        if request.method == 'POST':
            if 'so_template' in request.FILES:
                # media_path = os.path.join(s.BASE_DIR, s.MEDIA_ROOT)
                # file_path = os.path.join(media_path, file_name)
                row_count = 1
                file = request.FILES['so_template']
                if file:
                    try:
                        str_file_value = file.read().decode('utf-8')
                        file_t = str_file_value.splitlines()
                    except Exception as e:
                        print(e)
                        messages.add_message(request, messages.ERROR, 'Error happend while processing the file.', extra_tags='csv to so')
                        return render_to_response('import_csv_to_so.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    skip = 1
                    customer_id = request.POST.get('select_customer')
                    customer = Customer.objects.get(pk=customer_id)
                    sid_one = transaction.savepoint()
                    document_date = ''
                    customer_po = ''
                    part_no = ''
                    wanted_date = ''
                    unit_price = 0
                    quantity = ''
                    try:
                        exchange_rate = None
                        for row in csv.reader(file_t, delimiter=','):
                            if skip:
                                skip = 0
                                continue
                            unit_price = str(row[5]).replace(',', '')
                            quantity = float(str(row[6]).replace(',', ''))
                            if request.POST.get('customer_po'):
                                customer_po = request.POST.get('customer_po') + row[2]
                            else:
                                customer_po = row[2]
                            part_no = row[3]
                            location = ''

                            doc_date = str(row[1])
                            if len(doc_date) > 8 or len(doc_date) < 7:
                                messages.error(request, 'Document date is in invalid format. Please use DDMMYYYY')
                                fail_list.append([row_count, '', customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            elif len(doc_date) == 7:
                                doc_date = '0' + doc_date

                            wantd_date = str(row[4])
                            if len(wantd_date) > 8 or len(wantd_date) < 7:
                                messages.error(request, 'Wanted date is in invalid format. Please use DDMMYYYY')
                                fail_list.append([row_count, '', customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            elif len(wantd_date) == 7:
                                wantd_date = '0' + wantd_date

                            try:
                                document_date = doc_date[4:8] + '-' + doc_date[2:4] + '-' + doc_date[0:2]
                                document_date = datetime.datetime.strptime(document_date, '%Y-%m-%d')
                                wanted_date = wantd_date[4:8] + '-' + wantd_date[2:4] + '-' + wantd_date[0:2]
                                wanted_date = datetime.datetime.strptime(wanted_date, '%Y-%m-%d')
                            except Exception as e:
                                messages.error(request, 'Document/Wanted date is in invalid format. Please use DDMMYYYY')
                                fail_list.append([row_count, '', customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break

                            if not exchange_rate:
                                exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                            from_currency_id=customer.currency.id,
                                                            to_currency_id=company.currency.id,
                                                            exchange_date__month=document_date.month,
                                                            exchange_date__year=document_date.year,
                                                            flag='ACCOUNTING')
                                if not exchange_rate.exists():
                                    if customer.currency.id == company.currency.id:
                                        exchange_rate = 1
                                    else:
                                        messages.error(request, 'No exchange rate found for the document date of the customer currecny ' + customer.currency.code)
                                        return render_to_response('import_csv_to_so.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                                else:
                                    exchange_rate = exchange_rate.last()

                            if company.is_inventory:
                                try:
                                    location = row[7]
                                except Exception as e:
                                    print(e)
                                if location == '':
                                    messages.error(request, 'Invalid location')
                                    fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), customer_po, part_no, quantity])
                                    fail = True
                                    order = None
                                    break
                                else:
                                    location_code = Location.objects.filter(is_hidden=False, code=location)
                                    if location_code.exists():
                                        location = location_code.first().id
                                    else:
                                        messages.error(request, location + ' Location code not found')
                                        fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), customer_po, part_no, quantity])
                                        fail = True
                                        order = None
                                        break
                            if wanted_date < document_date:
                                messages.error(request, 'Wanted date is less than Document date.')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            if not quantity:
                                messages.error(request, 'Invalid Quantity.')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break

                            order, fail = create_so_order(request, company_id, customer_id, document_date, customer_po, part_no, wanted_date, unit_price,
                                                quantity, order, row_count, exchange_rate, location)
                            if fail:
                                fail = True
                                order = None
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), customer_po, part_no, quantity])
                                row_count += 1
                            else:
                                row_count += 1
                    except Exception as e:
                        print(e)
                        fail = True
                        order = None
                        fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), customer_po, part_no, quantity])
                        messages.error(request, 'Error happend while reading the file.')

                if order:
                    messages.success(request, order.document_number + ' S/O order is being created')
                    return render_to_response('import_csv_to_so.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                else:
                    transaction.savepoint_rollback(sid_one)
                    messages.error(request, 'No new S/O is being created')
                    return render_to_response('import_csv_to_so.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))

    return render_to_response('import_csv_to_so.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))


def create_po_from_csv(request):
    with transaction.atomic():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        customers = Supplier.objects.filter(is_hidden=False, is_active=True, company_id=company_id) \
            .order_by('code') \
            .values_list('id', 'code')

        fail_list = []
        fail = False
        order = None
        if request.method == 'POST':
            if 'po_template' in request.FILES:
                row_count = 1
                file = request.FILES['po_template']
                if file:
                    try:
                        str_file_value = file.read().decode('utf-8')
                        file_t = str_file_value.splitlines()
                    except Exception as e:
                        print(e)
                        messages.error(request, 'Error happend while processing the file.')
                        return render_to_response('import_csv_to_po.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    skip = 1
                    supplier_id = request.POST.get('select_supplier')
                    supplier = Supplier.objects.get(pk=supplier_id)
                    if request.POST.get('document_date'):
                        document_date = datetime.datetime.strptime(request.POST.get('document_date'), '%d-%m-%Y')
                    else:
                        document_date = datetime.datetime.today()

                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                        from_currency_id=supplier.currency.id,
                                                        to_currency_id=company.currency.id,
                                                        exchange_date__month=document_date.month,
                                                        exchange_date__year=document_date.year,
                                                        flag='ACCOUNTING')
                    if not exchange_rate.exists():
                        if supplier.currency.id == company.currency.id:
                            exchange_rate = 1
                        else:
                            messages.error(request, 'No exchange rate found for the document date of the supplier currecny ' + supplier.currency.code)
                            return render_to_response('import_csv_to_po.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    else:
                        exchange_rate = exchange_rate.last()
                    sid_one = transaction.savepoint()
                    ref_number = ''
                    ref_line = ''
                    part_no = ''
                    wanted_date = ''
                    quantity = ''
                    customer_po = ''
                    try:
                        for row in csv.reader(file_t, delimiter=','):
                            if skip:
                                skip = 0
                                continue
                            ref_number = row[1]
                            ref_line = row[2]
                            part_no = row[3]
                            customer_po = row[4]
                            quantity = float(str(row[5]).replace(',', ''))

                            wantd_date = str(row[8])
                            if len(wantd_date) > 8 or len(wantd_date) < 7:
                                messages.error(request, 'Wanted date is in invalid format. Please use DDMMYYYY')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            elif len(wantd_date) == 7:
                                wantd_date = '0' + wantd_date
                            
                            try:
                                wanted_date = wantd_date[4:8] + '-' + \
                                    wantd_date[2:4] + '-' + wantd_date[0:2]
                                wanted_date = datetime.datetime.strptime(wanted_date, '%Y-%m-%d')
                            except:
                                messages.error(request, 'Wanted date is in invalid format. Please use DDMMYYYY')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break

                            if wanted_date < document_date:
                                messages.error(request, 'Wanted date is less than Document date.')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break

                            if not quantity:
                                messages.error(request, 'Invalid Quantity.')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            
                            order, fail = create_po_order_csv(request, company_id, supplier_id, document_date, row, order, row_count, exchange_rate)
                            if fail:
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                order = None
                                row_count += 1
                                break
                            else:
                                row_count += 1
                    except Exception as e:
                        print(e)
                        fail = True
                        order = None
                        fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                        messages.error(request, 'Error happend while reading the file.')

                if order:
                    messages.success(request, order.document_number + ' P/O order is being created')
                    return render_to_response('import_csv_to_po.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                else:
                    transaction.savepoint_rollback(sid_one)
                    messages.error(request, 'No new P/O is being created')
                    return render_to_response('import_csv_to_po.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))

    return render_to_response('import_csv_to_po.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))


def create_gr_from_csv(request):
    with transaction.atomic():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        customers = Supplier.objects.filter(is_hidden=False, is_active=True, company_id=company_id) \
            .order_by('code') \
            .values_list('id', 'code')

        fail_list = []
        fail = False
        order = None
        newStockTrans = None
        if request.method == 'POST':
            if 'gr_template' in request.FILES:
                row_count = 1
                file = request.FILES['gr_template']
                if file:
                    try:
                        str_file_value = file.read().decode('utf-8')
                        file_t = str_file_value.splitlines()
                    except Exception as e:
                        print(e)
                        messages.error(request, 'Error happend while processing the file.')
                        return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    skip = 1
                    supplier_id = request.POST.get('select_supplier')
                    supplier = Supplier.objects.get(pk=supplier_id)
                    if request.POST.get('document_date'):
                        document_date = datetime.datetime.strptime(request.POST.get('document_date'), '%d-%m-%Y')
                    else:
                        document_date = datetime.datetime.today()

                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                        from_currency_id=supplier.currency.id,
                                                        to_currency_id=company.currency.id,
                                                        exchange_date__month=document_date.month,
                                                        exchange_date__year=document_date.year,
                                                        flag='ACCOUNTING')
                    if not exchange_rate.exists():
                        if supplier.currency.id == company.currency.id:
                            exchange_rate = 1
                        else:
                            messages.error(request, 'No exchange rate found for the document date of the supplier currecny ' + supplier.currency.code)
                            return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    else:
                        exchange_rate = exchange_rate.last()
                    sid_one = transaction.savepoint()
                    ref_number = ''
                    ref_line = ''
                    part_no = ''
                    quantity = ''
                    customer_po = ''
                    try:
                        for row in csv.reader(file_t, delimiter=','):
                            if skip:
                                skip = 0
                                continue
                            ref_number = row[1]
                            ref_line = row[2]
                            customer_po = row[3]
                            # part_no = row[5]
                            quantity = float(str(row[5]).replace(',', ''))
                            

                            if not quantity:
                                messages.error(request, 'Invalid Quantity.')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            
                            order, newStockTrans, fail = create_gr_order_csv(request, company_id, supplier_id, document_date, row, order, row_count, exchange_rate, newStockTrans)
                            if fail:
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                order = None
                                break
                            else:
                                row_count += 1
                    except Exception as e:
                        print(e)
                        fail = True
                        order = None
                        fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                        messages.error(request, 'Error happend while reading the file.')

                if order:
                    if newStockTrans:
                        newStockTrans.generate()
                    messages.success(request, order.document_number + ' G/R order is being created')
                    return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                else:
                    transaction.savepoint_rollback(sid_one)
                    messages.error(request, 'No new G/R is being created')
                    return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))

    return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))


def create_do_from_csv(request):
    with transaction.atomic():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        customers = Customer.objects.filter(is_hidden=False, is_active=True, company_id=company_id) \
            .order_by('code') \
            .values_list('id', 'code')

        fail_list = []
        fail = False
        order = None
        newStockTrans = None
        if request.method == 'POST':
            if 'do_template' in request.FILES:
                row_count = 1
                file = request.FILES['do_template']
                if file:
                    try:
                        str_file_value = file.read().decode('utf-8')
                        file_t = str_file_value.splitlines()
                    except Exception as e:
                        print(e)
                        messages.error(request, 'Error happend while processing the file.')
                        return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    skip = 1
                    customer_id = request.POST.get('select_customer')
                    customer = Customer.objects.get(pk=customer_id)
                    if request.POST.get('document_date'):
                        document_date = datetime.datetime.strptime(request.POST.get('document_date'), '%d-%m-%Y')
                    else:
                        document_date = datetime.datetime.today()

                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                        from_currency_id=customer.currency.id,
                                                        to_currency_id=company.currency.id,
                                                        exchange_date__month=document_date.month,
                                                        exchange_date__year=document_date.year,
                                                        flag='ACCOUNTING')
                    if not exchange_rate.exists():
                        if customer.currency.id == company.currency.id:
                            exchange_rate = 1
                        else:
                            messages.error(
                                request, 'No exchange rate found for the document date of the supplier currecny ' + customer.currency.code)
                            return render_to_response('import_csv_to_gr.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                    else:
                        exchange_rate = exchange_rate.last()
                    sid_one = transaction.savepoint()
                    ref_number = ''
                    ref_line = ''
                    part_no = ''
                    quantity = ''
                    customer_po = ''
                    try:
                        for row in csv.reader(file_t, delimiter=','):
                            if skip:
                                skip = 0
                                continue
                            ref_number = row[1]
                            ref_line = row[2]
                            customer_po = row[3]
                            part_no = row[5]
                            quantity = float(str(row[6]).replace(',', ''))
                            

                            if not quantity:
                                messages.error(request, 'Invalid Quantity.')
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                fail = True
                                order = None
                                break
                            
                            order, newStockTrans, fail = create_do_order_csv(
                                request, company_id, customer_id, document_date, row, order, row_count, exchange_rate, newStockTrans)
                            if fail:
                                fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                                order = None
                                break
                            else:
                                row_count += 1
                    except Exception as e:
                        print(e)
                        fail = True
                        order = None
                        fail_list.append([row_count, document_date.strftime('%d-%m-%Y'), ref_number, ref_line, customer_po, part_no, quantity])
                        messages.error(request, 'Error happend while reading the file.')

                if order:
                    if newStockTrans:
                        newStockTrans.generate()
                    messages.success(request, order.document_number + ' D/O order is being created')
                    return render_to_response('import_csv_to_do.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))
                else:
                    transaction.savepoint_rollback(sid_one)
                    messages.error(request, 'No new D/O is being created')
                    return render_to_response('import_csv_to_do.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))

    return render_to_response('import_csv_to_do.html', RequestContext(request, {'customers': customers, 'fail': fail, 'fail_list': fail_list}))


def update_item_price(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        order_type = request.POST.get('select_document_type')
        code = request.POST.get('select_customer')
        part_no = request.POST.get('select_part_no')
        new_price = request.POST.get('new_price')
        date = request.POST.get('effective_date').split('-')
        effective_date = date[2] + '-' + date[1] + '-' + date[0]

        try:
            # Update Order
            if order_type == 'SO':
                order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                                   order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                                                   order__customer__code=code, item__code=part_no,
                                                                                   order__document_date__gte=effective_date)
            elif order_type == 'PO':
                order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                                   order__supplier__code=code, item__code=part_no,
                                                                                   order__document_date__gte=effective_date)

            for order_item in order_item_list:
                old_amount = order_item.amount
                order_item.price = new_price
                order_item.amount = float(order_item.quantity) * float(new_price)
                order_item.save()

                # Update order total
                order_item.order.subtotal = float(order_item.order.subtotal) - float(old_amount) + float(order_item.amount)
                order_item.order.total = float(order_item.order.total) - float(old_amount) + float(order_item.amount)
                order_item.order.balance = order_item.order.total
                order_item.order.save()

            if order_type == 'SO':  # Update Customer Item Master Data
                customer_item = CustomerItem.objects.select_related('customer', 'item').filter(is_hidden=0, is_active=1,
                                                                                               customer__code=code, item__code=part_no).last()
                customer_item.new_price = new_price
                customer_item.effective_date = effective_date
                customer_item.save()

            elif order_type == 'PO':  # Update Supplier Item Master Data
                supplier_item = SupplierItem.objects.select_related('supplier', 'item').filter(is_hidden=0, is_active=1,
                                                                                               supplier__code=code, item__code=part_no).last()
                supplier_item.new_price = new_price
                supplier_item.effective_date = effective_date
                supplier_item.save()

            messages.add_message(request, messages.SUCCESS,
                                 "Data is updated for the Part No. " + part_no,
                                 extra_tags='update_item_unit_price')
        except Exception as e:
            print(e)
            messages.add_message(request, messages.ERROR,
                                 "Operation is not succesfull",
                                 extra_tags='update_item_unit_price')

    part_list = Item.objects.filter(is_hidden=0, company_id=company_id).order_by('code').values_list('code', flat=True).distinct()

    return render_to_response('update_item_price.html', RequestContext(request, {'part_list': part_list}))


def update_item_price_list(request, order_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item_list = []
    if order_type == 'SO':
        item_list = Customer.objects.filter(is_hidden=0, is_active=1, company_id=company_id) \
            .order_by('code').values_list('code', flat=True).distinct()
    elif order_type == 'PO':
        item_list = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id) \
            .order_by('code').values_list('code', flat=True).distinct()

    data = list(item_list)
    json_content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def update_delivery_date(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        order_type = request.POST.get('select_document_type')
        doc_no = request.POST.get('select_document')
        customer_po = request.POST.get('select_cust_po_no')
        date = request.POST.get('delivery_date').split('-')
        new_wanted_date = date[2] + '-' + date[1] + '-' + date[0]
        try:
            if order_type == 'SO':
                order_items = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                                               order__document_number=doc_no, customer_po_no=customer_po)
            elif order_type == 'PO':
                order_items = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                               order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                               order__document_number=doc_no, customer_po_no=customer_po)
            for order_item in order_items:
                order_item.wanted_date = new_wanted_date
                order_item.schedule_date = new_wanted_date
                order_item.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Delivery Date is updated for the Customer PO No. " + customer_po,
                                 extra_tags='update_delivery_date')
        except Exception as e:
            print(e)
            messages.add_message(request, messages.ERROR,
                                 "Operation is not succesfull",
                                 extra_tags='update_delivery_date')

    return render_to_response('update_delivery_date.html', RequestContext(request, {}))


def update_delivery_order_list(request, order_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order_item_list = []
    if order_type == 'SO':
        order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                           order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('delivery_quantity')) \
            .order_by('order__document_number').values_list('order__document_number', flat=True).distinct()
    elif order_type == 'PO':
        order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                           order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('receive_quantity')) \
            .order_by('order__document_number').values_list('order__document_number', flat=True).distinct()

    data = list(order_item_list)
    json_content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def update_delivery_order_list_po(request, order_type, doc_no):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order_item_list = []
    if order_type == 'SO':
        order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                           order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                                           order__document_number=doc_no) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('delivery_quantity')) \
            .order_by('customer_po_no').values_list('customer_po_no', flat=True).distinct()
    elif order_type == 'PO':
        order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                           order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                           order__document_number=doc_no) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('receive_quantity')) \
            .order_by('customer_po_no').values_list('customer_po_no', flat=True).distinct()

    data = list(order_item_list)
    json_content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def create_so_order(request, company_id, customer_id, document_date, customer_po, part_no, wanted_date, unit_price, quantity, order, row_count, exchange_rate, location):
    try:
        company = Company.objects.get(pk=company_id)
        menu_type = int(TRN_CODE_TYPE_DICT['Sales Number File'])
        mydict = dict(ORDER_TYPE)
        name = list(mydict.keys())[list(mydict.values()).index(int(dict(ORDER_TYPE)['SALES ORDER']))]
        transaction_code = TransactionCode.objects.get(is_hidden=False, company_id=company_id,
                                                    name=name, menu_type=menu_type).id

        item = Item.objects.filter(is_hidden=0, company_id=company_id, code=part_no)
        if item:
            item = item.first()
        else:
            messages.error(request, part_no + ' Part No. is invalid.')
            return None, True

        total_amount = 0
        price = 0
        supplier_item = None
        customer_item = CustomerItem.objects.filter(item=item, customer_id=customer_id)
        if customer_item:
            customer_item = customer_item.first()
            if unit_price and float(unit_price) > 0:
                price = float(unit_price)
                total_amount = float(quantity) * float(unit_price)
            else:
                try:
                    price = customer_item.new_price if customer_item.new_price else customer_item.sales_price
                    total_amount = float(quantity) * float(price)
                except:
                    total_amount = 0

            supplier_item = SupplierItem.objects.filter(item=item)
            if supplier_item:
                supplier_item = supplier_item.first()

        if total_amount and supplier_item:
            if not order:
                order = Order()
                order.customer_id = customer_item.customer_id
                order.reference_number = ''
                order.document_date = document_date
                order.document_number = generate_document_number(company_id,
                                                                order.document_date,
                                                                menu_type,
                                                                transaction_code)
                if order.document_number:
                    order.order_code = order.document_number
                try:
                    order.exchange_rate = exchange_rate.rate
                    order.exchange_rate_fk_id = exchange_rate.id
                except Exception as e:
                    print(e)
                    order.exchange_rate = 1.00

                order.currency_id = customer_item.customer.currency.id
                order.packing_number = 1
                order.order_type = dict(ORDER_TYPE)['SALES ORDER']
                order.create_date = datetime.datetime.today()
                order.update_date = datetime.datetime.today()
                order.is_hidden = False
                order.company_id = company_id
                order.status = dict(ORDER_STATUS)['Sent']
                order.subtotal = 0.0
                order.total = 0.0
                order.balance = 0.0
                order.tax_amount = 0.0
                order.save()

            if order:
                # order item
                order_item = OrderItem()
                order_item.item_id = item.id
                order_item.supplier_id = supplier_item.supplier_id
                order_item.customer_po_no = customer_po
                order_item.quantity = quantity
                order_item.last_quantity = quantity
                order_item.exchange_rate = order.exchange_rate
                order_item.wanted_date = wanted_date
                order_item.line_number = row_count
                order_item.from_currency_id = customer_item.customer.currency.id
                order_item.to_currency_id = company.currency.id
                order_item.delivery_quantity = 0
                order_item.receive_quantity = 0
                order_item.stock_quantity = 0
                order_item.bkord_quantity = quantity

                order_item.price = price
                order_item.amount = total_amount
                order_item.description = ''
                order_item.create_date = datetime.datetime.today()
                order_item.update_date = datetime.datetime.today()
                order_item.is_hidden = False
                order_item.order_id = order.id
                if company.is_inventory:
                    order_item.location_id = location
                order_item.save()

                order.subtotal += total_amount
                order.total += total_amount
                order.balance += total_amount
                order.save()

            return order, False
        else:
            messages.error(request, 'Supplier item not found')
            return None, True
    except Exception as e:
        print(e)
        return None, True


def create_po_order_csv(request, company_id, supplier_id, document_date, row, order, row_count, exchange_rate):
    try:
        company = Company.objects.get(pk=company_id)
        menu_type = int(TRN_CODE_TYPE_DICT['Purchase Number File'])
        mydict = dict(ORDER_TYPE)
        name = list(mydict.keys())[list(mydict.values()).index(int(dict(ORDER_TYPE)['PURCHASE ORDER']))]
        transaction_code = TransactionCode.objects.get(is_hidden=False, company_id=company_id,
                                                    name=name, menu_type=menu_type).id

        ref_number = row[1]
        ref_line = row[2]
        part_no = row[3]
        customer_po = row[4]
        quantity = str(row[5]).replace(',', '')
        unit_price = str(row[6]).replace(',', '')

        wantd_date = str(row[8])
        if len(wantd_date) == 7:
            wantd_date = '0' + wantd_date
        wanted_date = wantd_date[4:8] + '-' + wantd_date[2:4] + '-' + wantd_date[0:2]
        wanted_date = datetime.datetime.strptime(wanted_date, '%Y-%m-%d')

        schedl_date = str(row[9])
        if len(schedl_date) == 7:
            schedl_date = '0' + schedl_date
        try:
            schedule_date = schedl_date[4:8] + '-' + schedl_date[2:4] + '-' + schedl_date[0:2]
            if schedule_date:
                schedule_date = datetime.datetime.strptime(schedule_date, '%Y-%m-%d')
            else:
                schedule_date = wanted_date
        except:
            schedule_date = wanted_date

        description = row[10]

        item = Item.objects.filter(is_hidden=0, company_id=company_id, code=part_no)
        if item.exists():
            item = item.first()
        else:
            messages.error(request, part_no + ' Part No. is invalid.')
            return None, True

        location = ''
        if company.is_inventory:
            try:
                location = row[7]
            except Exception as e:
                print(e)
            if location == '':
                messages.error(request, 'Invalid location')
                return None, True
            else:
                location_code = Location.objects.filter(is_hidden=False, code=location)
                if location_code.exists():
                    location = location_code.first().id
                else:
                    messages.error(request, location + ' Location code not found')
                    return None, True

        total_amount = 0
        supplier_item = SupplierItem.objects.filter(item=item, supplier_id=supplier_id)
        if supplier_item.exists():
            supplier_item = supplier_item.first()
            try:
                if unit_price and float(unit_price) > 0:
                    price = float(unit_price)
                else:
                    price = supplier_item.new_price if supplier_item.new_price else supplier_item.purchase_price
                total_amount = float(quantity) * float(price)
            except:
                total_amount = 0

        if total_amount and supplier_item:
            
            if not order:
                order = Order()
                order.supplier_id = supplier_item.supplier_id
                order.reference_number = ''
                order.document_date = document_date
                order.document_number = generate_document_number(company_id,
                                                                order.document_date,
                                                                menu_type,
                                                                transaction_code)
                if order.document_number:
                    order.order_code = order.document_number
                try:
                    order.exchange_rate = exchange_rate.rate
                    order.exchange_rate_fk_id = exchange_rate.id
                except Exception as e:
                    print(e)
                    order.exchange_rate = 1.00

                order.currency_id = supplier_item.supplier.currency.id
                order.packing_number = 1
                order.order_type = dict(ORDER_TYPE)['PURCHASE ORDER']
                order.create_date = datetime.datetime.today()
                order.update_date = datetime.datetime.today()
                order.update_by_id = request.user.id
                order.is_hidden = False
                order.company_id = company_id
                order.status = dict(ORDER_STATUS)['Sent']
                order.subtotal = 0.0
                order.total = 0.0
                order.balance = 0.0
                order.tax_amount = 0.0
                order.save()

            if order:
                # order item
                order_item = OrderItem()
                if ref_number:
                    ref_order = Order.objects.filter(is_hidden=False, 
                                        order_type=dict(ORDER_TYPE)['SALES ORDER'], 
                                        document_number=ref_number)
                    if ref_order.exists() and ref_line:
                        ref_order = ref_order.last()
                        ref_item = OrderItem.objects.filter(is_hidden=False, order_id=ref_order.id, line_number=ref_line)
                        if ref_item.exists():
                            ref_item = ref_item.last()
                            if ref_item.item.id == item.id:
                                order_item.refer_number = ref_number
                                order_item.refer_code = 'S/O'
                                order_item.reference_id = ref_order.id
                                order_item.refer_line = ref_line
                            else:
                                messages.error(request, 'Refer Part no not found')
                                return None, True
                        else:
                            messages.error(request, 'Refer Line not found')
                            return None, True
                    else:
                        messages.error(request, 'Refer SO not found')
                        return None, True
                order_item.item_id = item.id
                order_item.supplier_id = supplier_item.supplier_id
                order_item.customer_po_no = customer_po
                order_item.quantity = quantity
                order_item.last_quantity = quantity
                order_item.exchange_rate = order.exchange_rate
                order_item.wanted_date = wanted_date
                order_item.schedule_date = schedule_date
                order_item.line_number = row_count
                order_item.from_currency_id = supplier_item.supplier.currency.id
                order_item.to_currency_id = company.currency.id
                order_item.delivery_quantity = 0
                order_item.receive_quantity = 0
                order_item.stock_quantity = 0
                order_item.bkord_quantity = quantity

                order_item.price = price
                order_item.amount = total_amount
                order_item.description = description
                order_item.create_date = datetime.datetime.today()
                order_item.update_date = datetime.datetime.today()
                order_item.is_hidden = False
                order_item.order_id = order.id

                if company.is_inventory:
                    order_item.location_id = location
                
                order_item.save()

                order.subtotal += total_amount
                order.total += total_amount
                order.balance += total_amount
                order.save()

            return order, False
        else:
            messages.error(request, 'Supplier item not found')
            return None, True
    except Exception as e:
        print(e)
        return None, True


def create_gr_order_csv(request, company_id, supplier_id, document_date, row, order, row_count, exchange_rate, newStockTrans):
    try:
        company = Company.objects.get(pk=company_id)
        menu_type = int(TRN_CODE_TYPE_DICT['Purchase Number File'])
        mydict = dict(ORDER_TYPE)
        name = list(mydict.keys())[list(mydict.values()).index(int(dict(ORDER_TYPE)['PURCHASE INVOICE']))]
        transaction_code = TransactionCode.objects.get(is_hidden=False, company_id=company_id,
                                                    name=name, menu_type=menu_type).id

        ref_number = row[1]
        ref_line = row[2]
        customer_po = row[3]
        # part_no = row[5]
        quantity = str(row[5]).replace(',', '')
        # unit_price = str(row[7]).replace(',', '')

        order_item = OrderItem()

        # item = Item.objects.filter(is_hidden=0, company_id=company_id, code=part_no)
        # if item.exists():
        #     item = item.first()

        ref_order = None
        item = None
        if ref_number:
            ref_order = Order.objects.filter(is_hidden=False, 
                                order_type=dict(ORDER_TYPE)['PURCHASE ORDER'], 
                                document_number=ref_number)
            if ref_order.exists() and ref_line:
                ref_order = ref_order.last()
                ref_item = OrderItem.objects.filter(is_hidden=False, order_id=ref_order.id, line_number=ref_line)
                if ref_item.exists():
                    ref_item = ref_item.last()
                    if str(ref_item.supplier.id) == str(supplier_id):
                        order_item.refer_number = ref_number
                        order_item.refer_code = 'P/O'
                        order_item.reference_id = ref_order.id
                        order_item.refer_line = ref_line
                        order_item.item_id = ref_item.item_id
                        order_item.price = ref_item.price

                        unit_price = ref_item.price
                        item = ref_item.item
                    else:
                        messages.error(request, 'Refer supplier does not match')
                        return None, None, True
                else:
                    messages.error(request, 'Refer Line not found')
                    return None, None, True
            else:
                messages.error(request, 'Refer PO not found')
                return None, None, True
        else:
            messages.error(request, 'Refer PO not found')
            return None, None, True

        location = ''
        if company.is_inventory:
            try:
                location = row[4]
            except Exception as e:
                print(e)
            if location == '':
                messages.error(request, 'Invalid location')
                return None, None, True
            else:
                location_code = Location.objects.filter(is_hidden=False, code=location)
                if location_code.exists():
                    location = location_code.first().id
                    try:
                        location_item = LocationItem.objects.get(is_hidden=False, location_id=location, item_id=item.id)
                    except:
                        part_no = 'Part item'
                        if item:
                            part_no = item.code
                        messages.error(request, part_no + ' does not belongs to ' + location_code.first().code + ' Location')
                        return None, None, True
                else:
                    messages.error(request, location + ' Location code not found')
                    return None, None, True

        total_amount = 0
        supplier_item = SupplierItem.objects.filter(item=item, supplier_id=supplier_id)
        if supplier_item.exists():
            supplier_item = supplier_item.first()
            try:
                if unit_price and float(unit_price) > 0:
                    price = float(unit_price)
                total_amount = float(quantity) * float(price)
            except:
                total_amount = 0

        if total_amount and supplier_item:
            if not order:
                order = Order()
                order.supplier_id = supplier_item.supplier_id
                order.reference_number = ''
                order.document_date = document_date
                if request.POST.get('document_no'):
                    order.document_number = request.POST.get('document_no')
                else:
                    order.document_number = generate_document_number(company_id,
                                                                    order.document_date,
                                                                    menu_type,
                                                                    transaction_code)
                if order.document_number:
                    order.order_code = order.document_number
                try:
                    order.exchange_rate = exchange_rate.rate
                    order.exchange_rate_fk_id = exchange_rate.id
                    order.supllier_exchange_rate = order.exchange_rate
                    order.tax_exchange_rate = order.exchange_rate
                except Exception as e:
                    print(e)
                    order.exchange_rate = 1.00
                    order.supllier_exchange_rate = 1.00
                    order.tax_exchange_rate = 1.00

                order.currency_id = supplier_item.supplier.currency.id
                if supplier_item.supplier.distribution_id:
                    order.distribution_code_id = supplier_item.supplier.distribution_id
                if supplier_item.supplier.tax:
                    order.tax_id = supplier_item.supplier.tax_id
                order.packing_number = 1
                order.order_type = dict(ORDER_TYPE)['PURCHASE INVOICE']
                order.create_date = datetime.datetime.today()
                order.update_date = datetime.datetime.today()
                order.update_by_id = request.user.id
                order.is_hidden = False
                order.company_id = company_id
                order.status = dict(ORDER_STATUS)['Sent']
                order.subtotal = 0.0
                order.total = 0.0
                order.balance = 0.0
                order.tax_amount = 0.0
                order.save()

                if company.is_inventory:
                    newStockTrans = create_stock_transaction(order, company_id,
                                                                 transaction_code)

            if order:
                # order item

                # order_item.item_id = item.id
                order_item.supplier_id = supplier_item.supplier_id
                order_item.customer_po_no = customer_po
                order_item.quantity = quantity
                order_item.last_quantity = quantity
                order_item.exchange_rate = order.exchange_rate
                order_item.line_number = row_count
                order_item.from_currency_id = supplier_item.supplier.currency.id
                order_item.to_currency_id = company.currency.id
                order_item.delivery_quantity = 0
                order_item.receive_quantity = quantity
                order_item.stock_quantity = quantity

                # order_item.price = price
                order_item.amount = total_amount
                order_item.description = ''
                order_item.create_date = datetime.datetime.today()
                order_item.update_date = datetime.datetime.today()
                order_item.is_hidden = False
                order_item.order_id = order.id
                if company.is_inventory:
                    order_item.location_id = location
                order_item.save()
                order_item = OrderItem.objects.get(pk=order_item.id)

                update_gr_reference = False
                if ref_order:
                    update_gr_reference, update_gr_reference_errs = order_vs_inventory(
                        request).set_reference_item(order_item.id)
                    if not update_gr_reference:
                        messages.error(request, create_error_string(update_gr_reference_errs))
                        return None, None, True

                if company.is_inventory and update_gr_reference:
                    newStockTrans.addItem(order_item)
                    # update item & locationitem qty
                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                        messages.error(request, create_error_string(update_inv_qty_log))
                        return None, None, True

                tax_amount = 0
                if order.tax_id:
                    tax = Tax.objects.filter(pk=order.tax_id)
                    if tax.exists():
                        tax_rate = tax.first().rate
                        tax_amount = (total_amount * float(tax_rate)) / 100;
                order.subtotal += total_amount
                order.tax_amount += tax_amount
                order.total += total_amount + tax_amount
                order.balance += total_amount + tax_amount
                order.save()

                if ref_order:
                    orderItems = OrderItem.objects.filter(order_id=ref_order.id, is_hidden=False)
                    orderStatus = 3
                    for item in orderItems:
                        if item.quantity > item.receive_quantity:
                            orderStatus = 6
                    
                    ref_order.status = orderStatus
                    ref_order.save()

            return order, newStockTrans, False
        else:
            messages.error(request, 'Supplier item not found')
            return None, None, True
    except Exception as e:
        print(e)
        return None, None, True


def create_do_order_csv(request, company_id, customer_id, document_date, row, order, row_count, exchange_rate, newStockTrans):
    try:
        company = Company.objects.get(pk=company_id)
        menu_type = int(TRN_CODE_TYPE_DICT['Sales Number File'])
        mydict = dict(ORDER_TYPE)
        name = list(mydict.keys())[list(mydict.values()).index(int(dict(ORDER_TYPE)['SALES INVOICE']))]
        transaction_code = TransactionCode.objects.get(is_hidden=False, company_id=company_id,
                                                    name=name, menu_type=menu_type).id

        ref_number = row[1]
        ref_line = row[2]
        customer_po = row[3]
        part_no = row[5]
        quantity = str(row[6]).replace(',', '')
        unit_price = str(row[7]).replace(',', '')

        carton_no = str(row[8])
        carton_total = str(row[9]).replace(',', '')
        if carton_total == "":
            carton_total = 0
        else:
            carton_total = float(carton_total)
        pallet_no = str(row[10])
        net_weight = str(row[11]).replace(',', '')
        if net_weight == "":
            net_weight = 0
        else:
            net_weight = float(net_weight)
        gross_weight = str(row[12]).replace(',', '')
        if gross_weight == "":
            gross_weight = 0
        else:
            gross_weight = float(gross_weight)
        

        item = Item.objects.filter(is_hidden=0, company_id=company_id, code=part_no)
        if item.exists():
            item = item.first()

        location = ''
        if company.is_inventory:
            try:
                location = row[4]
            except Exception as e:
                print(e)
            if location == '':
                messages.error(request, 'Invalid location')
                return None, None, True
            else:
                location_code = Location.objects.filter(is_hidden=False, code=location)
                if location_code.exists():
                    location = location_code.first().id
                    try:
                        loc_item = LocationItem.objects.get(is_hidden=False, location_id=location, item_id=item.id)
                    except:
                        messages.error(request, part_no + ' does not belongs to ' + location_code.first().code + ' Location')
                        return None, None, True
                else:
                    messages.error(request, location + ' Location code not found')
                    return None, None, True

        ref_order = None
        order_item = OrderItem()
        if ref_number:
            ref_order = Order.objects.filter(is_hidden=False, 
                                order_type=dict(ORDER_TYPE)['SALES ORDER'], 
                                document_number=ref_number)
            if ref_order.exists() and ref_line:
                ref_order = ref_order.last()
                ref_item = OrderItem.objects.filter(is_hidden=False, order_id=ref_order.id, line_number=ref_line)
                if ref_item.exists():
                    ref_item = ref_item.last()
                    if str(ref_item.order.customer.id) == str(customer_id):
                        order_item.refer_number = ref_number
                        order_item.refer_code = 'S/O'
                        order_item.reference_id = ref_order.id
                        order_item.refer_line = ref_line
                        order_item.item_id = ref_item.item_id
                        order_item.price = ref_item.price

                        unit_price = ref_item.price
                        item = ref_item.item

                        if company.is_inventory:
                            location_qty = 0
                            items = ref_item.item_id
                            loc_items = LocationItem.objects.filter(item_id=items,
                                                                    location__company_id=company.id,
                                                                    is_hidden=False,
                                                                    location__is_hidden=False)
                            if loc_item:
                                location_qty = loc_item.onhand_qty
                            if not loc_item or float(location_qty) <= 0:
                                location_qty = 0
                                po_list = order_vs_inventory(
                                    request).get_next_doc_detail(ref_item.id)
                                if po_list:
                                    for po in po_list:
                                        gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
                                        if gr_list:
                                            for gr in gr_list:
                                                location_qty += gr.quantity
                                                if gr.location_id:
                                                    location = gr.location_id
                                if location_qty == 0:
                                    loc_itms = loc_items. \
                                        filter(item_id=item.item_id).exclude(location_id=item.location_id).order_by('location_id')
                                    if loc_itms.exists():
                                        for loc_item in loc_itms:
                                            if loc_item.onhand_qty:
                                                location_qty = loc_item.onhand_qty
                                                location = loc_item.location_id
                                                break
                            if float(quantity) > float(location_qty):
                                messages.error(request, 'Insufficient location quantity')
                                return None, None, True
                    else:
                        messages.error(request, 'Refer Customer does not match')
                        return None, None, True
                else:
                    messages.error(request, 'Refer Line not found')
                    return None, None, True
            else:
                messages.error(request, 'Refer PO not found')
                return None, None, True
        else:
            messages.error(request, 'Refer PO not found')
            return None, None, True

        total_amount = 0
        customer_item = CustomerItem.objects.filter(item=item, customer_id=customer_id)
        if customer_item.exists():
            customer_item = customer_item.first()
            try:
                if unit_price and unit_price != "" and float(unit_price) > 0:
                    price = float(unit_price)
                total_amount = float(quantity) * float(price)
            except:
                total_amount = 0

        if total_amount and customer_item:
            if not order:
                order = Order()
                order.customer_id = customer_item.customer_id
                order.reference_number = ''
                order.document_date = document_date
                order.invoice_date = document_date
                order.delivery_date = document_date
                order.document_number = generate_document_number(company_id,
                                                                    order.document_date,
                                                                    menu_type,
                                                                    transaction_code)
                if order.document_number:
                    order.order_code = order.document_number
                try:
                    order.exchange_rate = exchange_rate.rate
                    order.exchange_rate_fk_id = exchange_rate.id
                    order.supllier_exchange_rate = order.exchange_rate
                    order.tax_exchange_rate = order.exchange_rate
                except Exception as e:
                    print(e)
                    order.exchange_rate = 1.00
                    order.supllier_exchange_rate = 1.00
                    order.tax_exchange_rate = 1.00

                order.currency_id = customer_item.customer.currency.id
                if customer_item.customer.tax:
                    order.tax_id = customer_item.customer.tax_id
                order.packing_number = 1
                order.order_type = dict(ORDER_TYPE)['SALES INVOICE']
                order.create_date = datetime.datetime.today()
                order.update_date = datetime.datetime.today()
                order.update_by_id = request.user.id
                order.is_hidden = False
                order.company_id = company_id
                order.status = dict(ORDER_STATUS)['Sent']
                order.subtotal = 0.0
                order.total = 0.0
                order.balance = 0.0
                order.tax_amount = 0.0
                order.save()

                if company.is_inventory:
                    newStockTrans = create_stock_transaction(order, company_id,
                                                                    transaction_code)

            if order:
                # order item
                
                # order_item.item_id = item.id
                if item.country_id:
                    order_item.origin_country_id = item.country_id
                order_item.customer_id = customer_item.customer_id
                order_item.customer_po_no = customer_po
                order_item.quantity = quantity
                order_item.last_quantity = quantity
                order_item.exchange_rate = order.exchange_rate
                order_item.line_number = row_count
                order_item.from_currency_id = customer_item.customer.currency.id
                order_item.to_currency_id = company.currency.id
                order_item.delivery_quantity = quantity
                order_item.receive_quantity = 0
                order_item.stock_quantity = 0

                order_item.carton_no = carton_no
                order_item.carton_total = carton_total
                order_item.pallet_no = pallet_no
                order_item.net_weight = net_weight
                order_item.gross_weight = gross_weight

                # order_item.price = price
                order_item.amount = total_amount
                order_item.description = ''
                order_item.create_date = datetime.datetime.today()
                order_item.update_date = datetime.datetime.today()
                order_item.is_hidden = False
                order_item.order_id = order.id
                if company.is_inventory:
                    order_item.location_id = location
                order_item.save()
                order_item = OrderItem.objects.get(pk=order_item.id)

                update_do_reference = False
                if ref_order:
                    update_do_reference, update_do_reference_errs = order_vs_inventory(
                        request).set_reference_item(order_item.id)
                    if not update_do_reference:
                        messages.error(request, create_error_string(update_do_reference_errs))
                        return None, None, True

                if company.is_inventory and update_do_reference:
                    newStockTrans.addItem(order_item)
                    # update item & locationitem qty
                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                        messages.error(request, create_error_string(update_inv_qty_log))
                        return None, None, True

                tax_amount = 0
                if order.tax_id:
                    tax = Tax.objects.filter(pk=order.tax_id)
                    if tax.exists():
                        tax_rate = tax.first().rate
                        tax_amount = (total_amount * float(tax_rate)) / 100;
                order.subtotal += total_amount
                order.tax_amount += tax_amount
                order.total += total_amount + tax_amount
                order.balance += total_amount + tax_amount
                order.save()

                if ref_order:
                    orderItems = OrderItem.objects.filter(order_id=ref_order.id, is_hidden=False)
                    orderStatus = 4
                    for item in orderItems:
                        if item.quantity > item.delivery_quantity:
                            orderStatus = 6
                    
                    ref_order.status = orderStatus
                    ref_order.save()

            return order, newStockTrans, False
        else:
            messages.error(request, 'Customer item not found')
            return None, None, True
    except Exception as e:
        print(e)
        return None, None, True


def save_order_item(request, order_id, order_status, formset_item, is_inventory, order_type, last_item_qty=None,
                    last_order_status=None):
    order = Order.objects.get(pk=order_id)
    fail = None
    if formset_item.is_valid():
        fail = False
        line = 1
        for form in formset_item:
            try:
                order_item = OrderItem()
                order_item.item_id = form.cleaned_data.get('item_id')
                if form.cleaned_data.get('supplier_code_id') != 'None' and form.cleaned_data.get(
                        'supplier_code_id'):
                    order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                order_item.quantity = form.cleaned_data.get('quantity')
                order_item.last_quantity = form.cleaned_data.get('quantity')
                if form.cleaned_data.get('exchange_rate') != '' and form.cleaned_data.get('exchange_rate') != None:
                    order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                else:
                    order_item.exchange_rate = request.POST.get('id_exchange_rate_value')
                if form.cleaned_data.get('wanted_date'):
                    order_item.wanted_date = form.cleaned_data.get('wanted_date')
                if form.cleaned_data.get('schedule_date'):
                    order_item.schedule_date = form.cleaned_data.get('schedule_date')
                if is_inventory and form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
                    order_item.location_id = form.cleaned_data.get('location').id
                order_item.refer_line = form.cleaned_data.get('refer_line')
                order_item.line_number = line
                if form.cleaned_data.get('currency_id') != '' and form.cleaned_data.get('currency_id') != None:
                    order_item.from_currency_id = form.cleaned_data.get('currency_id')
                else:
                    order_item.from_currency_id = order.currency_id
                order_item.to_currency_id = request.POST.get('currency')
                if form.cleaned_data.get('delivery_quantity') is not None:
                    order_item.delivery_quantity = form.cleaned_data.get('delivery_quantity')
                else:
                    order_item.delivery_quantity = 0
                if form.cleaned_data.get('receive_quantity') is not None:
                    order_item.receive_quantity = form.cleaned_data.get('receive_quantity')
                else:
                    order_item.receive_quantity = 0
                if form.cleaned_data.get('last_receive_date') and form.cleaned_data.get('last_receive_date') != '':
                    order_item.last_receive_date = form.cleaned_data.get('last_receive_date')
                if form.cleaned_data.get('last_delivery_date') and form.cleaned_data.get('last_delivery_date') != '':
                    order_item.last_delivery_date = form.cleaned_data.get('last_delivery_date')
                order_item.stock_quantity = 0

                if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
                    order_item.bkord_quantity = form.cleaned_data.get('bkord_quantity')
                elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
                    if form.cleaned_data.get('ref_number'):
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.refer_code = 'S/O'
                    if form.cleaned_data.get('reference_id'):
                        ref_id = form.cleaned_data.get('reference_id')
                        order_item.reference_id = ref_id if float(ref_id) > 0 else None

                order_item.price = form.cleaned_data.get('price')
                order_item.amount = form.cleaned_data.get('amount')
                order_item.description = form.cleaned_data.get('description')
                order_item.create_date = datetime.datetime.today()
                order_item.update_date = datetime.datetime.today()
                order_item.update_by_id = request.user.id
                order_item.is_hidden = False
                order_item.order_id = order_id
                order_item.save()
                line += 1

                if int(order_type) == dict(ORDER_TYPE)['SALES ORDER'] and \
                    int(order_status) >= dict(ORDER_STATUS)['Sent'] and is_inventory:
                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id, last_item_qty, last_order_status)
                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                        fail = True
                        for upd_inv_log in update_inv_qty_log:
                            messages.add_message(request, messages.ERROR, 'ERROR: ' + upd_inv_log['log'],
                                                extra_tags=upd_inv_log['tag'])
                        messages.add_message(request, messages.ERROR, SEND_DOC_FAILED + REFRESH_OR_GO_GET_SUPPORT,
                                            extra_tags='send_doc_failed')
            except Exception as e:
                print(e)
                fail = True
    else:
        print("save_order_item formset_item.errors: ", formset_item.errors)

    return fail


def save_order(request, company_id, order_type):
    # order process
    order = Order()

    dict_key = ''
    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        order.customer_id = request.POST.get('customer')
        order.reference_number = request.POST.get('reference_number')
        dict_key = 'Sales Number File'
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        order.supplier_id = request.POST.get('supplier')
        order.transport_responsibility = request.POST.get('transport_responsibility')
        dict_key = 'Purchase Number File'

    order.document_date = request.POST.get('document_date')
    if request.POST.get('document_number') and request.POST.get('document_number') != '':
        order.document_number = request.POST.get('document_number')
    elif request.POST.get('document_date'):
        trn_code_type = int(TRN_CODE_TYPE_DICT[dict_key])
        order.document_number = generate_document_number(company_id,
                                                         request.POST.get('document_date'),
                                                         trn_code_type,
                                                         request.POST.get('transaction_code'))
    if order.document_number:
        order.order_code = order.document_number
    if request.POST.get('exchange_rate_fk_id') != '' and request.POST.get('exchange_rate_fk_id') != 'None':
        order.exchange_rate_fk_id = request.POST.get('exchange_rate_fk_id')

    order.exchange_rate_date = request.POST.get('exchange_rate_date') if request.POST.get(
        'exchange_rate_date') else None
    if request.POST.get('id_exchange_rate_value'):
        order.exchange_rate = request.POST.get('id_exchange_rate_value')
    if request.POST.get('invoice_date') != '':
        order.invoice_date = request.POST.get('invoice_date')
    if request.POST.get('delivery_date'):
        order.delivery_date = request.POST.get('delivery_date')
    order.currency_id = request.POST.get('currency')
    if request.POST.get('tax'):
        order.tax_id = request.POST.get('tax')
    if request.POST.get('discount'):
        order.discount = Decimal(request.POST.get('discount'))
    order.subtotal = Decimal(request.POST.get('subtotal'))
    order.total = Decimal(request.POST.get('total'))
    order.tax_amount = Decimal(request.POST.get('tax_amount'))
    order.balance = order.total
    if request.POST.get('cost_center'):
        order.cost_center_id = request.POST.get('cost_center')
    if request.POST.get('note_customer'):
        order.note = request.POST.get('note_customer')
    if request.POST.get('remark'):
        order.remark = request.POST.get('remark')
    if request.POST.get('footer'):
        order.footer = request.POST.get('footer')
    order.packing_number = 1
    order.order_type = int(order_type)
    order.create_date = datetime.datetime.today()
    order.update_date = datetime.datetime.today()
    order.update_by_id = request.user.id
    order.is_hidden = False
    order.company_id = company_id
    order.status = dict(ORDER_STATUS)['Sent']
    order.save()

    return order


def so_po_error_render(request, company, form, form_info, items_list, order_type, formset_right,
                       formset_left, formset_item, customer, supplier, currency_symbol, order_status, form_delivery, doc_num_auto=True, style='N'):
    if style == 'old':
        template_name = 'order_new_foxpro.html' if int(order_type) == dict(ORDER_TYPE)['SALES ORDER'] else 'order_purchases_foxpro.html'
    else:
        template_name = 'order_new.html' if int(order_type) == dict(ORDER_TYPE)['SALES ORDER'] else 'order_purchases.html'

    return render(request, template_name,
                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                   'items_list': items_list, 'form_delivery': form_delivery,
                   'order_type': order_type, 'formset_right': formset_right, 'formset_left': formset_left,
                   'formset_item': formset_item, 'cus': customer,
                   'supplier': supplier, 'currency_symbol': currency_symbol,
                   'request_method': request.method, 'order_status': order_status, 'doc_num_auto': doc_num_auto})


def edit_so_po_error_render(request, order_type, company, form, form_info, items_list,
                            formset_right, copy_id, currency_symbol, order_status, formset_left, formset_item,
                            supplier, order, form_delivery, customer_delivery, decimal_place, msg, style):
    if style == 'old':
        template_name = 'order_purchases_foxpro.html' if int(order_type) == dict(ORDER_TYPE)[
            'PURCHASE ORDER'] else 'order_new_foxpro.html'
    else:
        template_name = 'order_purchases.html' if int(order_type) == dict(ORDER_TYPE)[
            'PURCHASE ORDER'] else 'order_new.html'

    kwarg = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
             'items_list': items_list, 'order_type': order_type, 'form_delivery': form_delivery,
             'formset_right': formset_right, 'copy_id': copy_id, 'currency_symbol': currency_symbol,
             'order_status': order_status, 'formset_left': formset_left, 'formset_item': formset_item,
             'supplier': supplier, 'order': order, 'request_method': request.method, 'customer_delivery': customer_delivery,
             'decimal_place': decimal_place, 'msg': msg
             }

    return render_to_response(template_name, RequestContext(request, kwarg))


def get_orders_object(order_type, order_id, company_id):
    order = Order.objects.get(pk=order_id)
    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)
    # get order header info
    try:
        order_header = order_header_list.filter(x_position=1, y_position=0).latest('update_date')
    except OrderHeader.DoesNotExist:
        order_header = None
    # get all items of Order by Order_ID
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id).values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier_id')) \
        .annotate(currency_id=F('to_currency')) \
        .annotate(original_currency=F('to_currency__code')) \
        .annotate(code=F('item__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(item_id=F('item_id')) \
        .annotate(amount=F('amount')) \
        .annotate(location=F('location_id')).order_by('line_number')

    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        order_item = order_item \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(bkord_quantity=Coalesce(F('bkord_quantity'), V(0)))

    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        order_item = order_item \
            .annotate(uom=F('item__purchase_measure__name')) \
            .annotate(ref_number=F('refer_number'))
    # if not order.currency.is_decimal:
    #     for item in order_item:
    #         item['amount'] = round_number(item['amount'], 0)


    return order, order_header_list, order_header, order_item


def get_company_currencysymbol(order):
    company = Company.objects.get(pk=order.company_id)

    try:
        currency_symbol = Currency.objects.get(pk=order.currency_id).symbol
    except Currency.DoesNotExist:
        currency_symbol = Currency.objects.none()

    return company, currency_symbol


def get_items_list(order_type, order, supplier, company_id):
    items_list = []
    # get list if items
    if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
        items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=order.customer_id).values() \
            .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
            .annotate(supplier_id=F('item__supplieritem__supplier')) \
            .annotate(location_code=F('customer__company__location__code')) \
            .annotate(location_id=F('customer__company__location__id')) \
            .annotate(custome_name=F('customer__name')) \
            .annotate(item_id=F('item_id')) \
            .annotate(item_name=F('item__name')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(currency=F('currency__code')) \
            .annotate(currency_id=F('currency_id')) \
            .annotate(line_id=Value(0, output_field=models.CharField()))
        for i, j in enumerate(items_list):
            if (i < items_list.__len__()):
                i += 1
                j['line_id'] = i
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
        items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              item__supplieritem__supplier=supplier.id,
                                              order__order_type=dict(ORDER_TYPE)['SALES ORDER']).values() \
            .annotate(item_name=F('item__name')) \
            .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
            .annotate(supplier_code_id=F('item__supplieritem__supplier')) \
            .annotate(order_type=F('order__order_type')) \
            .annotate(ref_number=F('order__document_number')) \
            .annotate(ref_line=F('refer_line')) \
            .annotate(currency_id=F('supplier__currency')) \
            .annotate(currency=F('supplier__currency__code')) \
            .annotate(location_code=F('item__locationitem__location__code')) \
            .annotate(location_id=F('item__locationitem__location_id')) \
            .annotate(purchase_price=F('item__purchase_price')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(uom=F('item__purchase_measure__name')) \
            .annotate(minimun_order=F('item__minimun_order')) \
            .annotate(line_id=Value(0, output_field=models.CharField()))
        if not items_list:
            items_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                     supplier_id=supplier.id).values() \
                .annotate(item_name=F('item__name')) \
                .annotate(supplier_code=F('supplier__code')) \
                .annotate(supplier_code_id=F('supplier_id')) \
                .annotate(order_type=Value('', output_field=models.CharField())) \
                .annotate(ref_number=Value('', output_field=models.CharField())) \
                .annotate(ref_line=Value(0, output_field=models.CharField())) \
                .annotate(currency_id=F('currency_id')) \
                .annotate(currency=F('currency__code')) \
                .annotate(location_code=F('item__locationitem__location__code')) \
                .annotate(location_id=F('item__locationitem__location_id')) \
                .annotate(purchase_price=F('item__purchase_price')) \
                .annotate(code=F('item__code')) \
                .annotate(category=F('item__category__code')) \
                .annotate(uom=F('item__purchase_measure__name')) \
                .annotate(minimun_order=F('item__minimun_order')) \
                .annotate(line_id=Value(0, output_field=models.CharField()))

        for i, j in enumerate(items_list):
            if (i < items_list.__len__()):
                i += 1
                j['line_id'] = i

    return items_list


def save_header_info(request, company_id, form_info, order_id, order_status, order_type):
    info = None

    if form_info.is_valid():
        info = form_info.save(commit=False)
        info.id = order_id
        if int(order_type) == dict(ORDER_TYPE)['SALES ORDER']:
            info.customer_id = request.POST.get('customer')
        if int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
            info.supplier_id = request.POST.get('supplier')
        if request.POST.get('cost_center'):
            info.cost_center_id = request.POST.get('cost_center')
        else:
            info.cost_center_id = None
        if request.POST.get('tax'):
            info.tax_id = request.POST.get('tax')
        else:
            info.tax_id = None
        if order_status < dict(ORDER_STATUS)['Sent']:
            info.status = dict(ORDER_STATUS)['Sent']
        if request.POST.get('id_exchange_rate_value'):
            info.exchange_rate = request.POST.get('id_exchange_rate_value')
        if request.POST.get('exchange_rate_fk_id') and request.POST.get('exchange_rate_fk_id') != 'None':
            info.exchange_rate_fk_id = request.POST.get('exchange_rate_fk_id')
        if request.POST.get('exchange_rate_date') and request.POST.get('exchange_rate_date') != 'None':
            info.exchange_rate_date = request.POST.get('exchange_rate_date')
        info.subtotal = Decimal(request.POST.get('subtotal'))
        info.total = Decimal(request.POST.get('total'))
        info.tax_amount = Decimal(request.POST.get('tax_amount'))
        info.balance = info.total
        info.update_date = datetime.datetime.today()
        info.update_by_id = request.user.id
        info.is_hidden = 0
        info.save()
    else:
        print("save_header_info form_info.errors: ", form_info.errors)
    return info


@login_required
@permission_required('orders.change_order', login_url='/alert/')
# @check_sp_closing
@csrf_exempt
def order_delete(request):
    if request.is_ajax():
        response_data = {}
        success = delete_order(request, request.POST.get('order_id'))

        if success:
            response_data['type'] = 'success'
            response_data['msg'] = 'Delete Order Successfully!!!'
        else:
            response_data['type'] = 'failed'
            response_data['msg'] = '"Delete Failed. You only have permission delete draft order!"'

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        pass


def gr_do_edit(request, order_id, order_type, style):
    if int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
        return HttpResponseRedirect('/orders/good_receive_edit/' + order_id + '/' + style + '/')
    if int(order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
        return HttpResponseRedirect('/orders/order_DO_edit/' + order_id + '/' + str(order_type) + '/0/' + style + '/')


@login_required
@permission_required('orders.change_order', login_url='/alert/')
# @check_sp_closing
def order_remove(request, order_id, order_type, style):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id, is_hidden=False)
    order = Order.objects.get(pk=order_id)
    if int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE'] or int(order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
        if order.document_date:
            document_date = order.document_date
            fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                            start_date__lte=document_date,
                                                            end_date__gte=document_date).first()

            if fiscal_period and fiscal_period.is_sp_locked:
                request.session['is_sp_locked'] = True
                messages.error(request, CHECK_SP_LOCKED % (
                    fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
        if 'is_sp_locked' in request.session and request.session['is_sp_locked']:
            return gr_do_edit(request, order_id, order_type, style)
        
        # check if Acc batch is alrady posted or not
        acc_entry_type = dict(TRANSACTION_TYPES)['AR Invoice']
        if order.order_type == dict(ORDER_TYPE)['PURCHASE INVOICE'] or \
                order.order_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'] or \
                order.order_type == dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']:
            acc_entry_type = dict(TRANSACTION_TYPES)['AP Invoice']
        
        sp_to_accounting = sp_to_acc(request)
        acc_batch_status = sp_to_accounting.check_batch_status(acc_entry_type, order)
        if acc_batch_status and acc_batch_status == int(STATUS_TYPE_DICT['Posted']):
            messages.error(request, 'Cannot delete ' + order.document_number + ', \
                as bacause the Accounting Batch is being already posted') 
            return gr_do_edit(request, order_id, order_type, style)

        # check if stock transaction is alrady posted or not
        if company.is_inventory:
            orderStockTransction = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                        document_number=order.document_number)
            if orderStockTransction.exists():
                orderStockTransction = orderStockTransction.last()
                if orderStockTransction.is_closed:
                    messages.error(request, 'Cannot delete ' + order.document_number + ', \
                        as bacause the Stock entry already been closed in Inventory Control System.') 
                    return gr_do_edit(request, order_id, order_type, style)
    
    result = validate_deleting(request, order_type, order_id)
    if result[0]:
        delete_order(request, order_id)
        return HttpResponseRedirect('/orders/list/' + str(order_type) + '/')
    else:
        if int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE'] or int(order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
            return gr_do_edit(request, order_id, order_type, style)
        else:
            messages.error(request, 'Cannot delete ' + order.document_number + ', \
                        Delete ' + result[1] + ' first')
            return HttpResponseRedirect('/orders/order_edit/' + order_id + '/' + str(order_type) + '/' + EDIT_TYPE['Edit'] + '/0/' + style + '/')
    

def delete_order(request, order_id):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id, is_hidden=False)
        with transaction.atomic():
            order = Order.objects.get(pk=order_id)
            order.update_date = datetime.datetime.today()
            order.update_by_id = request.user.id
            order.is_hidden = True
            order.save()

            order_header = OrderHeader.objects.filter(is_hidden=0, order__company_id=company_id, order_id=order_id)
            if order_header:
                for header in order_header:
                    header.is_hidden = True
                    header.save()

            order_item = OrderItem.objects.filter(is_hidden=0, order__company_id=company_id, order_id=order_id)
            for item in order_item:
                item.is_hidden = True
                item.save()

                if item.reference_id:
                    update_reference, update_reference_errs = order_vs_inventory(request).set_reference_item(item.id,
                                                                                                             None, None,
                                                                                                             True)
                    if not update_reference:
                        messages.add_message(request, messages.ERROR, create_error_string(update_reference_errs),
                                             extra_tags='update_ref_failed')

                if company.is_inventory and order.status > dict(ORDER_STATUS)['Draft']:
                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, item.id, None, None, True)
                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                        messages.add_message(request, messages.ERROR, create_error_string(update_inv_qty_log),
                                             extra_tags='update_inv_failed')

            if company.is_inventory:
                newStockTrans = create_stock_transaction(order, company_id, request.POST.get('transaction_code'))
                if newStockTrans.getStockTransaction():
                    if not newStockTrans.deleteStockTransaction():
                        messages.add_message(request, messages.ERROR, 'ERROR: Failed to delete stock transaction !',
                                             extra_tags='delete_stock_transaction_failed')

            if order.order_type == dict(ORDER_TYPE)['PURCHASE INVOICE'] or \
                    order.order_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'] or \
                    order.order_type == dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']:
                acc_entry_type = dict(TRANSACTION_TYPES)['AP Invoice']
            else:
                acc_entry_type = dict(TRANSACTION_TYPES)['AR Invoice']

            sp_to_accounting = sp_to_acc(request)
            new_batch = sp_to_accounting.delete_acc_entry(acc_entry_type, order)
            if not new_batch:
                print(generate_errors(sp_to_accounting.get_errors()))

            order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__company_id=company_id, order_id=order_id)
            for delivery in order_delivery:
                delivery.is_hidden = True
                delivery.save()
            messages.add_message(request, messages.SUCCESS, order.document_number + ' is deleted.', extra_tags='order_delete')
            return True

    except OSError as e:
        messages.add_message(request, messages.ERROR, e, extra_tags='order_delete')

    return False


@login_required
@permission_required('orders.change_order', login_url='/alert/')
@check_sp_closing
@csrf_exempt
def delete_order_single_row(request):
    if request.is_ajax():
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            company = Company.objects.get(pk=company_id, is_hidden=False)
            with transaction.atomic():
                sid = transaction.savepoint()
                fail = False
                row_id = request.POST.get('row_id')
                transaction_code = request.POST.get('transaction_code')
                order_item = OrderItem.objects.get(pk=row_id)
                order = Order.objects.get(pk=order_item.order_id)

                # check if Acc batch is alrady posted or not
                acc_entry_type = dict(TRANSACTION_TYPES)['AR Invoice']
                if order.order_type == dict(ORDER_TYPE)['PURCHASE INVOICE'] or \
                        order.order_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'] or \
                        order.order_type == dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']:
                    acc_entry_type = dict(TRANSACTION_TYPES)['AP Invoice']

                sp_to_accounting = sp_to_acc(request)
                acc_batch_status = sp_to_accounting.check_batch_status(acc_entry_type, order)
                if acc_batch_status and acc_batch_status == int(STATUS_TYPE_DICT['Posted']):
                    return HttpResponse(json.dumps({"message": 'Cannot edit ' + order.document_number + ', \
                        as bacause the Accounting Batch is being already posted'}), content_type="application/json")

                # check if stock transaction is alrady posted or not
                if company.is_inventory:
                    orderStockTransction = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                                document_number=order.document_number)
                    if orderStockTransction.exists():
                        orderStockTransction = orderStockTransction.last()
                        if orderStockTransction.is_closed:
                            return HttpResponse(json.dumps({"message": 'Cannot edit ' + order.document_number + ', \
                                as bacause the Stock entry already been closed in Inventory Control System.'}), content_type="application/json")

                # start deleting row
                order_item.is_hidden = True
                order_item.save()

                order.subtotal = float(order.subtotal) - float(order_item.amount)
                if order.tax_id:
                    tax_rate = Tax.objects.get(pk=order.tax_id).rate
                    order.tax_amount = float(order.subtotal) * float(tax_rate)
                else:
                    order.tax_amount = 0
                order.total = float(order.subtotal) + float(order.tax_amount)
                order.balance = order.total
                order.save()

                if order_item.reference_id:
                    update_reference, update_reference_errs = order_vs_inventory(request).set_reference_item(order_item.id,
                                                                                                            None, None,
                                                                                                            True)
                    if not update_reference:
                        print('update_reference_errs', update_reference_errs)
                        fail = True
                        transaction.savepoint_rollback(sid)

                if company.is_inventory and not fail and order_item.order.status > dict(ORDER_STATUS)['Draft']:
                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id, None, None, True)
                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                        print('update_inv_failed', update_inv_qty_log)
                        fail = True
                        transaction.savepoint_rollback(sid)

                if company.is_inventory and not fail:
                    newStockTrans = create_stock_transaction(order_item.order, company_id, transaction_code)
                    if newStockTrans.getStockTransaction():
                        if not newStockTrans.deleteStockTransaction():
                            print('ERROR: Failed to delete stock transaction !')
                            fail = True
                            transaction.savepoint_rollback(sid)
                        else:
                            new_order_items = OrderItem.objects.filter(is_hidden=0, order__company_id=company_id, order_id=order_item.order_id)
                            if new_order_items.exists():
                                for item in new_order_items:
                                    newStockTrans.addItem(item)
                                # generate new stock trans
                                newStockTrans.generate()

                if order_item.order.order_type == dict(ORDER_TYPE)['PURCHASE INVOICE'] or \
                        order_item.order.order_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'] or \
                        order_item.order.order_type == dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']:
                    acc_entry_type = dict(TRANSACTION_TYPES)['AP Invoice']
                else:
                    acc_entry_type = dict(TRANSACTION_TYPES)['AR Invoice']

                sp_to_accounting = sp_to_acc(request)
                new_batch = sp_to_accounting.update_acc_entry(acc_entry_type, order_item.order)
                if not new_batch:
                    print(generate_errors(sp_to_accounting.get_errors()))
                    # fail = True

                if not fail:
                    return HttpResponse(json.dumps({"message": "Success"}), content_type="application/json")
                else:
                    return HttpResponse(json.dumps({"message": "Reference error or Reference not found!"}), content_type="application/json")
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({"message": "Reference error or Reference not found!"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"message": "Reference error or Reference not found!"}), content_type="application/json")


@login_required
@csrf_exempt
def load_tax(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            tax_id = request.POST.get('tax_id')
            tax = Tax.objects.get(pk=tax_id)
            rate = decimal.Decimal(tax.rate)
            return HttpResponse(json.dumps(str(rate)), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='load_tax')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
@csrf_exempt
def load_currency(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        try:
            response_data = {}
            arrItems = json.loads(request.POST.get('arrItems'))
            currency_id = request.POST.get('currency_id')
            currency = Currency.objects.get(pk=currency_id)
            response_data['code'] = currency.code
            response_data['symbol'] = currency.symbol
            exchange_time = None
            if request.POST.get('doc_date'):
                exchange_time = datetime.datetime.strptime(request.POST.get('doc_date'), '%Y-%m-%d')

            for i in arrItems:
                if i['currency_id'] != '':
                    item_currency_rate = {}
                    item_currency = Currency.objects.filter(id=int(i['currency_id'])).first()
                    try:
                        if int(i['currency_id']) == int(currency_id):
                            rate = 1

                        else:
                            try:
                                if exchange_time:
                                    rate = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                                    from_currency_id=i['currency_id'],
                                                                    to_currency_id=currency_id,
                                                                    exchange_date__month=exchange_time.month,
                                                                    exchange_date__year=exchange_time.year,
                                                                    flag='ACCOUNTING').latest('exchange_date').rate
                                else:
                                    rate = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                                    from_currency_id=i['currency_id'],
                                                                    to_currency_id=currency_id,
                                                                    flag='ACCOUNTING').latest('exchange_date').rate

                            except:
                                rate = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                                from_currency_id=i['currency_id'],
                                                                to_currency_id=currency_id,
                                                                flag='ACCOUNTING').latest('exchange_date').rate
                        item_currency_rate['id'] = i['item_id']
                        item_currency_rate['currency'] = item_currency.code
                        item_currency_rate['rate'] = str(decimal.Decimal(rate))
                        response_data['item_rate_' + i['item_id']] = item_currency_rate
                    except Exception as e:
                        item_currency_rate['id'] = i['item_id']
                        item_currency_rate['currency'] = item_currency.code
                        item_currency_rate['rate'] = str(decimal.Decimal(0.000000))
                        response_data['item_rate_' + i['item_id']] = item_currency_rate
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
def load_price_product(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            response_data = {}
            product_id = request.POST.get('product_id')
            product = Item.objects.filter(id=product_id, company_id=company_id, is_hidden=0).values() \
                .annotate(supplier=F('supplieritem__supplier__name')) \
                .annotate(original_currency=F('purchase_currency__name')) \
                .annotate(original_price=F('purchase_price')).first()
            response_data['supplier'] = product['supplier']
            response_data['original_currency'] = product['original_currency']
            response_data['original_price'] = str(decimal.Decimal(product['original_price']))
            response_data['stock_quantity'] = str(get_item_onhandqty(product_id))
            response_data['price'] = str(decimal.Decimal(product['sale_price']))
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='load_price_product')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
def page_sp(request):
    try:
        return redirect('/orders/list/1/')
        # return render_to_response('page_sp.html', RequestContext(request))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@csrf_exempt
def change_company_inline(request, company_id):
    company = Company.objects.get(pk=company_id)
    if request.method == 'POST':
        try:
            if request.is_ajax():
                if request.POST.get('name') == 'company_name':
                    company.name = request.POST.get('value')
                    company.save()
                if request.POST.get('name') == 'company_address':
                    company.address = request.POST.get('value')
                    company.save()
                if request.POST.get('name') == 'company_email':
                    company.email = request.POST.get('value')
                    company.save()
            else:
                html = '<p>This is not ajax</p>'
                return HttpResponse(html)

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='change_company_inline')

        return HttpResponse("Successfully")


@login_required
@csrf_exempt
def change_customer_inline(request, customer_id):
    if request.method == 'POST':
        try:
            if request.is_ajax():
                customer = Customer.objects.get(pk=customer_id)
                if request.POST.get('name') == 'customer_name':
                    customer.name = request.POST.get('value')
                    customer.save()
                if request.POST.get('name') == 'customer_address':
                    customer.address = request.POST.get('value')
                    customer.save()
                if request.POST.get('name') == 'customer_email':
                    customer.email = request.POST.get('value')
                    customer.save()
        except OSError as e:
            error = messages.add_message(request, messages.ERROR, e, extra_tags='change_customer_inline')
            HttpResponse(error)
        return HttpResponse("Successfully")


@login_required
@csrf_exempt
def change_customer_delivery_address(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        response_data = {}
        try:
            delivery_id = request.POST.get('delivery_id')
            if not math.isnan(float(delivery_id)):
                customer_delivery = Delivery.objects.get(pk=delivery_id)
                contact = Contact.objects.filter(is_hidden=0, company_id=company_id, delivery_id=delivery_id).first()
                response_data['address'] = customer_delivery.address
                response_data['attention'] = customer_delivery.attention
                response_data['name'] = customer_delivery.name
                response_data['phone'] = customer_delivery.phone
                response_data['note_1'] = customer_delivery.note_1
                if contact is not None:
                    response_data['contact_name'] = contact.name
                    response_data['contact_company'] = contact.company_name
                    response_data['contact_attention'] = contact.attention
                    response_data['contact_designation'] = contact.designation
                    response_data['contact_phone'] = contact.phone
                    response_data['contact_fax'] = contact.fax
                    response_data['contact_email'] = contact.email
                    response_data['contact_web'] = contact.web
                    response_data['contact_address'] = contact.address
                    response_data['contact_remark'] = contact.note
            else:
                response_data['address'] = ''
                response_data['attention'] = ''
                response_data['name'] = ''
                response_data['phone'] = ''
                response_data['note_1'] = ''
        except OSError as e:
            error = messages.add_message(request, messages.ERROR, e, extra_tags='change_customer_delivery_address')
            HttpResponse(error)
        return HttpResponse(json.dumps(response_data), content_type='application/json')


@login_required
@csrf_exempt
def supplier_items_search(request):
    if request.method == 'POST':
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        if request.is_ajax():
            supplier_id = request.POST.get('supplier_id')
            search_condition = request.POST.get('search_condition')
            exclude_item_json = request.POST.get('exclude_item_list')
            if search_condition == '0':
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      supplier_id=supplier_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                    annotate(item_name=F('item__name')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_type=F('order__order_type')). \
                    annotate(ref_id=F('order_id')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(currency_id=F('supplier__currency')). \
                    annotate(currency=F('supplier__currency__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(purchase_price=F('item__purchase_price')). \
                    annotate(code=F('item__code')).annotate(category=F('item__category__code')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(minimun_order=F('item__minimun_order')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))
                if not items_list:
                    items_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                             supplier_id=supplier_id).values(). \
                        annotate(item_name=F('item__name')). \
                        annotate(supplier_code=F('supplier__code')). \
                        annotate(supplier_code_id=F('supplier_id')). \
                        annotate(order_type=Value('', output_field=models.CharField())). \
                        annotate(ref_number=Value('', output_field=models.CharField())). \
                        annotate(ref_line=Value(0, output_field=models.CharField())). \
                        annotate(currency_id=F('currency_id')). \
                        annotate(currency=F('currency__code')). \
                        annotate(location_code=F('item__locationitem__location__code')). \
                        annotate(location_id=F('item__locationitem__location_id')). \
                        annotate(purchase_price=F('item__purchase_price')). \
                        annotate(code=F('item__code')). \
                        annotate(category=F('item__category__code')). \
                        annotate(uom=F('item__purchase_measure__name')). \
                        annotate(minimun_order=F('item__minimun_order')). \
                        annotate(customer_po_no=Value('', output_field=models.CharField())). \
                        annotate(line_id=Value(0, output_field=models.CharField()))

                for i, j in enumerate(items_list):
                    if (i < items_list.__len__()):
                        i += 1
                        j['line_id'] = i
            else:
                if exclude_item_json:
                    exclude_item_list = json.loads(exclude_item_json)
                    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          supplier_id=supplier_id,
                                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
                        .filter(Q(item__name__contains=search_condition) |
                                Q(item__code__contains=search_condition) |
                                Q(order__document_number__contains=search_condition) |
                                Q(supplier__code__contains=search_condition) |
                                Q(location__code__contains=search_condition)) \
                        .exclude(item_id__in=exclude_item_list) \
                        .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
                        .values('item_id') \
                        .annotate(item_name=F('item__name')) \
                        .annotate(supplier_code=F('supplier__code')) \
                        .annotate(supplier_id=F('supplier_id')) \
                        .annotate(order_type=F('order__order_type')) \
                        .annotate(ref_id=F('order_id')) \
                        .annotate(ref_number=F('order__document_number')) \
                        .annotate(ref_line=F('line_number')) \
                        .annotate(currency_id=F('supplier__currency')) \
                        .annotate(currency=F('supplier__currency__code')) \
                        .annotate(location_code=F('location__code')) \
                        .annotate(location_id=F('location_id')) \
                        .annotate(purchase_price=F('item__purchase_price')) \
                        .annotate(code=F('item__code')) \
                        .annotate(category=F('item__category__code')) \
                        .annotate(uom=F('item__purchase_measure__name')) \
                        .annotate(minimun_order=F('item__minimun_order')) \
                        .annotate(customer_po_no=F('customer_po_no')) \
                        .annotate(line_id=Value(0, output_field=models.CharField()))
                else:
                    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          supplier_id=supplier_id,
                                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
                        .filter(Q(item__name__contains=search_condition) |
                                Q(item__code__contains=search_condition) |
                                Q(order__document_number__contains=search_condition) |
                                Q(supplier__code__contains=search_condition) |
                                Q(location__code__contains=search_condition)) \
                        .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
                        .values('item_id') \
                        .annotate(item_name=F('item__name')) \
                        .annotate(supplier_code=F('supplier__code')) \
                        .annotate(supplier_id=F('supplier_id')) \
                        .annotate(order_type=F('order__order_type')) \
                        .annotate(ref_id=F('order_id')) \
                        .annotate(ref_number=F('order__document_number')) \
                        .annotate(ref_line=F('line_number')) \
                        .annotate(currency_id=F('supplier__currency')) \
                        .annotate(currency=F('supplier__currency__code')) \
                        .annotate(location_code=F('location__code')) \
                        .annotate(location_id=F('location_id')) \
                        .annotate(purchase_price=F('item__purchase_price')) \
                        .annotate(code=F('item__code')) \
                        .annotate(category=F('item__category__code')) \
                        .annotate(uom=F('item__purchase_measure__name')) \
                        .annotate(minimun_order=F('item__minimun_order')) \
                        .annotate(customer_po_no=F('customer_po_no')) \
                        .annotate(line_id=Value(0, output_field=models.CharField()))

                for i, j in enumerate(items_list):
                    if (i < items_list.__len__()):
                        i += 1
                        j['line_id'] = i

            return render(request, 'supplier_items.html', {'items_list': items_list})


@login_required
@csrf_exempt
def customer_items_search(request):
    if request.method == 'POST':
        items_list = []
        if request.is_ajax():
            customer_id = request.POST.get('customer_id')
            search_condition = request.POST.get('search_condition')
            exclude_item_json = request.POST.get('exclude_item_list')
            if search_condition == '0':
                items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=customer_id).values() \
                    .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
                    .annotate(supplier_id=F('item__supplieritem__supplier')) \
                    .annotate(location_code=F('item__locationitem__location__code')) \
                    .annotate(location_id=F('item__locationitem__location')) \
                    .annotate(custome_name=F('customer__name')) \
                    .annotate(item_id=F('item_id')) \
                    .annotate(item_name=F('item__name')) \
                    .annotate(code=F('item__code')) \
                    .annotate(category=F('item__category__code')) \
                    .annotate(uom=F('item__sales_measure__name')) \
                    .annotate(currency=F('currency__code')) \
                    .annotate(currency_id=F('currency_id')) \
                    .annotate(line_id=Value(0, output_field=models.CharField()))
                for i, j in enumerate(items_list):
                    if (i < items_list.__len__()):
                        i += 1
                        j['line_id'] = i
            else:
                if exclude_item_json:
                    exclude_item_list = json.loads(exclude_item_json)
                    items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=customer_id) \
                        .filter(Q(item__name__contains=search_condition) |
                                Q(item__code__contains=search_condition) |
                                Q(item__supplieritem__supplier__code__contains=search_condition) |
                                Q(item__locationitem__location__code__contains=search_condition)) \
                        .exclude(item_id__in=exclude_item_list) \
                        .values('item_id') \
                        .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
                        .annotate(supplier_id=F('item__supplieritem__supplier')) \
                        .annotate(location_code=F('item__locationitem__location__code')) \
                        .annotate(location_id=F('item__locationitem__location__id')) \
                        .annotate(custome_name=F('customer__name')) \
                        .annotate(item_name=F('item__name')) \
                        .annotate(code=F('item__code')) \
                        .annotate(category=F('item__category__code')) \
                        .annotate(sales_price=F('sales_price')) \
                        .annotate(uom=F('item__sales_measure__name')) \
                        .annotate(currency=F('currency__code')) \
                        .annotate(currency_id=F('currency_id')) \
                        .annotate(line_id=Value(0, output_field=models.CharField()))
                else:
                    items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=customer_id) \
                        .filter(Q(item__name__contains=search_condition) |
                                Q(item__code__contains=search_condition) |
                                Q(item__supplieritem__supplier__code__contains=search_condition) |
                                Q(item__locationitem__location__code__contains=search_condition)) \
                        .values('item_id') \
                        .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
                        .annotate(supplier_id=F('item__supplieritem__supplier')) \
                        .annotate(location_code=F('item__locationitem__location__code')) \
                        .annotate(location_id=F('item__locationitem__location__id')) \
                        .annotate(custome_name=F('customer__name')) \
                        .annotate(item_name=F('item__name')) \
                        .annotate(code=F('item__code')) \
                        .annotate(category=F('item__category__code')) \
                        .annotate(sales_price=F('sales_price')) \
                        .annotate(uom=F('item__sales_measure__name')) \
                        .annotate(currency=F('currency__code')) \
                        .annotate(currency_id=F('currency_id')) \
                        .annotate(line_id=Value(0, output_field=models.CharField()))
                for i, j in enumerate(items_list):
                    if (i < items_list.__len__()):
                        i += 1
                        j['line_id'] = i
        return render(request, 'customer_items.html', {'items_list': items_list})


@login_required
@csrf_exempt
def change_customer_info(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            customer = Customer.objects.get(pk=customer_id)

            response_data = {'id': customer.id,
                             'name': customer.name,
                             'address': customer.address,
                             'email': customer.email,
                             'term': customer.payment_term,
                             'payment_mode': customer.payment_mode.name,
                             'credit_limit': str(customer.credit_limit)}

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='change_customer_info')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
@csrf_exempt
def change_supplier_inline(request, supplier_id):
    if request.method == 'POST':
        try:
            if request.is_ajax():
                supplier = Supplier.objects.get(pk=supplier_id)
                if request.POST.get('name') == 'supplier_name':
                    supplier.name = request.POST.get('value')
                    supplier.save()
                if request.POST.get('name') == 'supplier_address':
                    supplier.address = request.POST.get('value')
                    supplier.save()
                if request.POST.get('name') == 'supplier_email':
                    supplier.email = request.POST.get('value')
                    supplier.save()
        except OSError as e:
            error = messages.add_message(request, messages.ERROR, e, extra_tags='change_supplier_inline')
            HttpResponse(error)
        return HttpResponse("Successfully")


@login_required
@csrf_exempt
def change_supplier_info(request):
    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('supplier_id')
            supplier = Supplier.objects.get(pk=supplier_id)
            response_data = {'id': supplier.id,
                             'name': supplier.name,
                             'address': supplier.address,
                             'email': supplier.email,
                             'term': supplier.term_days,
                             'payment_mode': supplier.payment_mode.name,
                             'credit_limit': str(supplier.credit_limit)}
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='change_supplier_info')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
@permission_required('orders.add_order', login_url='/alert/')
def generate_purchase_load(request, sale_order_id):
    so_list = None
    array = []
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        so_items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                 order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            exclude(order__status=dict(ORDER_STATUS)['Delivered']). \
            exclude(quantity__lte=F('delivery_quantity')).values('order_id', 'line_number', 'quantity').distinct()

        exclude_so_list = []
        for so in so_items_list:
            po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                   reference_id=so['order_id'], refer_line=so['line_number'],
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                .aggregate(quantity=Sum('quantity'))['quantity']

            if po_item_qty and po_item_qty >= so['quantity']:
                if not so['order_id'] in exclude_so_list:
                    exclude_so_list.append(so['order_id'])
            else:
                if so['order_id'] in exclude_so_list:
                    exclude_so_list.remove(so['order_id'])

        so_list = OrderItem.objects. \
            filter(~Q(order_id__in=exclude_so_list),
                   is_hidden=0,
                   order__is_hidden=0,
                   order__company_id=company_id,
                   order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                   order__status=dict(ORDER_STATUS)['Sent']). \
            exclude(quantity__lte=F('delivery_quantity')). \
            values('order_id', 'order__document_number'). \
            order_by('-order__document_number').distinct()

        if sale_order_id != '0':
            sale_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=sale_order_id).order_by('line_number')
            supp_distinc = sale_item_list.values('order__document_number', 'supplier_id').order_by(
                'supplier_id').distinct()

            needToRemove = []
            messageStr = ''
            try:
                for so in supp_distinc:
                    po = Order.objects.filter(is_hidden=0, company_id=company_id,
                                              reference_number=so['order__document_number']).first()
                    if po:
                        needToRemove.append({'so': so, 'po': po})
                if needToRemove:
                    for i in needToRemove:
                        messageStr += '<li>- ' + i['po'].document_number + ' generated from ' + i[
                            'po'].reference_number + '</li>'
                        supp_distinc = supp_distinc.exclude(order__document_number=i['so']['order__document_number'])
            except Exception as e:
                print(e)

            if supp_distinc.__len__() == 0:
                messages.add_message(request, messages.ERROR,
                                     'Purchase Order has been generated from SO : <br/> ' +
                                     '<ul class="list-unstyled" style="margin-left:15px">' +
                                     messageStr + '</ul>',
                                     extra_tags='search_sale_order')

            od = Order.objects.get(pk=sale_order_id)

            for sup in supp_distinc:
                detail_sup = Supplier.objects.get(pk=sup['supplier_id'])
                loop_sup = {'supplier__name': detail_sup,
                            'order__document_number': od.document_number,
                            'order_id': sale_order_id,
                            'supplier_id': sup['supplier_id'],
                            'order__document_date': od.document_date.strftime("%d-%m-%Y")}
                items_sup = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                     order_id=sale_order_id, supplier_id=sup['supplier_id']).order_by('line_number')

                totalAmount_row = 0
                for itm in items_sup:
                    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                item_id=itm.item_id,
                                                                supplier_id=sup['supplier_id']).first()
                    if supplier_item:
                        if not supplier_item.effective_date:
                            totalAmount_row += itm.quantity * supplier_item.purchase_price
                        elif supplier_item.new_price and datetime.date.today() > supplier_item.effective_date:
                            totalAmount_row += itm.quantity * supplier_item.new_price
                        else:
                            totalAmount_row += itm.quantity * supplier_item.purchase_price
                    else:
                        messages.add_message(request, messages.ERROR, "Supplier Item doesn't have Purchase Price."
                                                                      "Please add the correct Purchase Price first.",
                                             extra_tags='bank_delete')
                        main_item = Item.objects.get(pk=itm.item_id)
                        if main_item and main_item.purchase_price:
                            totalAmount_row += itm.quantity * main_item.purchase_price
                        else:
                            totalAmount_row += itm.quantity * itm.price

                loop_sup['supplier_total'] = totalAmount_row
                array.append(loop_sup)
    except Exception as e:
        print(e)

    return render_to_response('generate_purchase_order.html', RequestContext(request, {'supplier_list': array,
                                                                                       'sale_order_id': sale_order_id,
                                                                                       'order_type': dict(ORDER_TYPE)[
                                                                                           'PURCHASE ORDER'],
                                                                                       'so_list': so_list}))


@login_required
@check_inventory_closing
@check_sp_closing
def generate_DO_load(request, good_receive_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    od = Order.objects.get(pk=good_receive_id)
    rate_order = 1
    if od.exchange_rate:
        rate_order = od.exchange_rate

    customer_list_all = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                 order_id=good_receive_id,
                                                 refer_line=F('reference__orderitem__line_number'),
                                                 reference__orderitem__refer_line=F(
                                                     'reference__orderitem__reference__orderitem__line_number'))

    customer_list = customer_list_all.values('order_id', 'reference_id', 'refer_number') \
        .annotate(customer_id=F('reference__orderitem__reference__customer_id')) \
        .annotate(customer_name=F('reference__orderitem__reference__customer__name')) \
        .annotate(so_id=F('reference__orderitem__reference')) \
        .annotate(so_no=F('reference__orderitem__reference__document_number')) \
        .annotate(quantity=F('quantity')) \
        .annotate(rest_quantity=Sum(F('reference__orderitem__reference__orderitem__quantity') - F(
            'reference__orderitem__reference__orderitem__delivery_quantity'))) \
        .annotate(quantity_to_delivery=Value(0, output_field=DecimalField())) \
        .annotate(price=F('reference__orderitem__reference__orderitem__price')) \
        .annotate(exchange_rate=F('exchange_rate')) \
        .annotate(amount=Value(0, output_field=DecimalField()))

    new_customer_list = customer_list_all.values('order_id', 'reference_id', 'refer_number') \
        .annotate(customer_id=F('reference__orderitem__reference__customer_id')) \
        .annotate(customer_name=F('reference__orderitem__reference__customer__name')) \
        .annotate(so_id=F('reference__orderitem__reference')) \
        .annotate(so_no=F('reference__orderitem__reference__document_number')) \
        .annotate(price=F('reference__orderitem__reference__orderitem__price')) \
        .annotate(total=Value(0, output_field=DecimalField())) \
        .distinct()

    for j in new_customer_list:
        total = 0
        for i in customer_list:
            if i['reference_id'] == j['reference_id']:
                if i['quantity'] >= i['rest_quantity']:
                    i['quantity_to_delivery'] = i['rest_quantity']
                elif i['quantity'] < i['rest_quantity']:
                    i['quantity_to_delivery'] = i['quantity']

                if not i['quantity_to_delivery']:
                    i['quantity_to_delivery'] = 0
                if not i['price']:
                    i['price'] = 0
                if not i['exchange_rate']:
                    i['exchange_rate'] = 0

                i['amount'] = float(i['quantity_to_delivery']) * float(i['price']) * float(rate_order)
                total += float(round_number(float(i['amount']), 6))
                j['total'] = total
    if 'is_inventory_locked' in request.session and request.session['is_inventory_locked']:
        is_locked = True
    else:
        is_locked = False
    return render_to_response('generate_DO_from_GR.html', RequestContext(request, {'customer_list': new_customer_list,
                                                                                   'good_receive_id': good_receive_id,
                                                                                   'is_locked': is_locked}))


@login_required
@csrf_exempt
def load_sales_items_by_customer(request, good_receive_id, reference_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            od = Order.objects.get(pk=good_receive_id)
            sale_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=good_receive_id, reference_id=reference_id,
                                                      refer_line=F('reference__orderitem__line_number'),
                                                      reference__orderitem__refer_line=F('reference__orderitem__reference__orderitem__line_number')) \
                .values('item_id', 'reference__orderitem__reference__orderitem__quantity',
                        'reference__orderitem__reference__orderitem__delivery_quantity',
                        'reference__orderitem__reference__document_number').annotate(item__name=F('item__name')) \
                .annotate(quantity=F('quantity')) \
                .annotate(rest_quantity=Sum(F('reference__orderitem__reference__orderitem__quantity') -
                                            F('reference__orderitem__reference__orderitem__delivery_quantity'))) \
                .annotate(quantity_to_delivery=Value(0, output_field=DecimalField())) \
                .annotate(price=F('reference__orderitem__reference__orderitem__price')) \
                .annotate(exchange_rate=F('exchange_rate')).annotate(amount=F('amount'))
            for i in sale_item_list:
                if i['quantity'] >= i['rest_quantity']:
                    i['quantity_to_delivery'] = i['rest_quantity']
                elif i['quantity'] < i['rest_quantity']:
                    i['quantity_to_delivery'] = i['quantity']
                i['exchange_rate'] = od.exchange_rate
                total_items_price = float(i['quantity_to_delivery']) * float(i['price']) * float(i['exchange_rate'])
                i['amount'] = float(round_number(float(total_items_price), 6))
            sale_item_list_json = json.dumps(list(sale_item_list), cls=DjangoJSONEncoder)
            return HttpResponse(sale_item_list_json, content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='except load_sales_items_by_customer')
    else:
        return HttpResponse(json.dumps({"status": "fail"}), content_type="application/json")


@login_required
@csrf_exempt
def generate_DO_from_GR(request, good_receive_id):
    if request.method == 'POST':
        sale_order_list = request.POST.getlist('sale_order_id')
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        new_sale_order_list = list(set(sale_order_list))

        for sale_order_id in new_sale_order_list:
            sale_order = Order.objects.get(pk=sale_order_id)
            good_receive = Order.objects.get(pk=good_receive_id)
            staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=sale_order.company_id).first()
            customer_id = sale_order.customer_id
            kwargs, contact = get_order_delivery_kwargs(company_id, customer_id, sale_order_id)
            # convert queryset to list
            with transaction.atomic():
                if customer_id != "":
                    account_list = Account.objects.filter(
                        company_id=company_id, is_hidden=0, is_active=True).order_by('account_segment', 'code')
                    account_sale = account_list.filter(code=s.ACCOUNT_SALES).first()
                    s.ACCOUNT_RECEIVABLE = account_list.filter(code=s.ACCOUNT_RECEIVABLE).first()
                    filter_transaction_code = TransactionCode.objects.filter(
                        is_hidden=False, company_id=company_id,
                        name="SALES INVOICE",
                        menu_type=int(TRN_CODE_TYPE_DICT['Sales Number File'])).last()
                    # order process
                    order = Order()
                    order.company_id = company_id
                    order.document_date = datetime.datetime.today()
                    order.document_number = generate_document_number(
                        company_id,
                        str(datetime.datetime.today().date()),
                        int(TRN_CODE_TYPE_DICT['Sales Number File']),
                        filter_transaction_code.id if filter_transaction_code else '',
                        filter_transaction_code.ics_prefix if filter_transaction_code else 'CW')
                    order.delivery_date = datetime.datetime.today()
                    order.invoice_date = datetime.datetime.today()
                    order.due_date = datetime.datetime.today()
                    order.customer_id = customer_id
                    order.currency_id = good_receive.currency_id
                    order.tax_id = sale_order.tax_id if sale_order else good_receive.tax_id
                    order.reference_number = good_receive.document_number
                    order.order_type = dict(ORDER_TYPE)['SALES INVOICE']
                    order.subtotal = 0
                    order.total = 0
                    order.balance = 0
                    order.tax_amount = 0
                    order.create_date = datetime.datetime.today()
                    order.update_date = datetime.datetime.today()
                    order.update_by_id = request.user.id
                    order.is_hidden = False
                    order.status = dict(ORDER_STATUS)['Sent']
                    order.exchange_rate = sale_order.exchange_rate
                    order.save()

                    # Save OrderItem
                    good_receive_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                      order__company_id=company_id,
                                                                      order_id=good_receive_id)
                    sum_amount = 0
                    stt = 0
                    delivery_status = 0
                    reference_order = None
                    for old_order_item in good_receive_item_list:
                        sales_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                    order__company_id=company_id,
                                                                    order_id=sale_order_id,
                                                                    item_id=old_order_item.item_id).first()
                        order_item = OrderItem()
                        order_item.order_id = order.id
                        order_item.customer_po_no = old_order_item.customer_po_no
                        order_item.supplier_id = old_order_item.supplier_id
                        order_item.reference_id = sale_order_id
                        order_item.item_id = old_order_item.item_id
                        order_item.location_id = old_order_item.location_id
                        order_item.from_currency_id = old_order_item.from_currency_id
                        order_item.to_currency_id = old_order_item.to_currency_id
                        order_item.exchange_rate = old_order_item.exchange_rate
                        order_item.quantity = old_order_item.quantity
                        order_item.stock_quantity = 0
                        order_item.delivery_quantity = 0
                        order_item.receive_quantity = 0
                        order_item.refer_line = old_order_item.line_number
                        stt += 1
                        order_item.line_number = stt
                        order_item.refer_number = sale_order.document_number
                        order_item.wanted_date = datetime.datetime.today()
                        order_item.schedule_date = datetime.datetime.today()
                        order_item.price = old_order_item.price
                        order_item.amount = old_order_item.amount
                        if sales_order_item:
                            order_item.price = sales_order_item.price
                            order_item.amount = order_item.price * order_item.quantity
                        sum_amount += order_item.amount
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.save()

                        # Update Delivery Quantity and Delivery Quantity
                        # of Reference Order ( Reference Order is Sales Order)
                        if sale_order.id:
                            refer_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                        order__company_id=company_id,
                                                                        order_id=sale_order_id,
                                                                        item_id=order_item.item_id,
                                                                        line_number=order_item.refer_line).first()
                            if refer_order_item:
                                refer_order_item.delivery_quantity = float(refer_order_item.delivery_quantity) + float(
                                    order_item.quantity)
                                refer_order_item.update_date = datetime.datetime.today()
                                refer_order_item.update_by_id = request.user.id
                                refer_order_item.last_delivery_date = datetime.datetime.today()
                                refer_order_item.save()

                                # Check delivery quantity
                                if refer_order_item.delivery_quantity < refer_order_item.quantity:
                                    delivery_status += 1

                    # save Total of Order
                    order = Order.objects.get(pk=order.id)
                    order.subtotal = sum_amount
                    order.tax_amount = (sum_amount * sale_order.tax.rate) / 100 if sale_order else good_receive.tax.rate
                    order.total = sum_amount + order.tax_amount
                    order.balance = sum_amount + order.tax_amount
                    order.save()

                    # Change order status base on delivery quantity
                    so_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                             order__company_id=company_id,
                                                             order_id=sale_order_id)
                    for i in so_order_item:
                        if i.delivery_quantity < i.quantity:
                            delivery_status += 1

                    sale_order.status = dict(ORDER_STATUS)['Partial'] \
                        if delivery_status > 0 else dict(ORDER_STATUS)['Delivered']
                    sale_order.save()

                    create_order_delivery(request, order, contact)

                    msg = 'Order Delivery  ' + str(
                        order.document_number) + ' was generated from ' + 'Good Receive ' + good_receive.document_number
                    messages.add_message(request, messages.INFO, msg)

    return HttpResponseRedirect(reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['SALES INVOICE']}))


def create_order_delivery(request, order, contact):
    order_delivery = OrderDelivery()
    order_delivery.order_id = order.id
    order_delivery.attention = contact.name if contact else ''
    order_delivery.phone = contact.phone if contact else ''
    order_delivery.note_1 = contact.note if contact else ''
    order_delivery.address = contact.address if contact else ''

    order_delivery.create_date = datetime.datetime.today()
    order_delivery.update_date = datetime.datetime.today()
    order_delivery.update_by_id = request.user.id
    order_delivery.is_hidden = 0
    order_delivery.save()

    return order_delivery


@login_required
def search_sale_order(request):
    sale_order_id = '0'
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    so_items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                             order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
        exclude(order__status=dict(ORDER_STATUS)['Draft']). \
        exclude(order__status=dict(ORDER_STATUS)['Delivered']). \
        exclude(quantity__lte=F('delivery_quantity')).values('order_id', 'line_number', 'quantity').distinct()

    exclude_so_list = []
    for so in so_items_list:
        po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                               reference_id=so['order_id'], refer_line=so['line_number'],
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .aggregate(quantity=Sum('quantity'))['quantity']

        if po_item_qty and po_item_qty >= so['quantity']:
            if not so['order_id'] in exclude_so_list:
                exclude_so_list.append(so['order_id'])
        else:
            if so['order_id'] in exclude_so_list:
                exclude_so_list.remove(so['order_id'])

    so_list = OrderItem.objects. \
        filter(~Q(order_id__in=exclude_so_list),
               is_hidden=0,
               order__is_hidden=0,
               order__company_id=company_id,
               order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
               order__status=dict(ORDER_STATUS)['Sent']). \
        exclude(quantity__lte=F('delivery_quantity')). \
        values('order_id', 'order__document_number'). \
        order_by('-order__document_number').distinct()

    if request.method == 'POST':
        supplier_list = OrderItem.objects.none()
        from_so = int(request.POST.get('from_so'))
        to_so = int(request.POST.get('to_so'))
        order_ids = get_order_filter_range(dict(ORDER_TYPE)['SALES ORDER'], company_id, from_so, to_so, 'id')
        sales_order = so_list. \
            filter(order_id__in=order_ids). \
            values('order_id', 'order__document_number')

        array = []
        for so in sales_order:
            od = Order.objects.get(pk=so['order_id'])
            sale_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=so['order_id'])
            supplier_list = sale_item_list.values('order__document_number', 'supplier_id').order_by(
                'supplier_id').distinct()

            for sup in supplier_list:
                detail_sup = Supplier.objects.get(pk=sup['supplier_id'])
                loop_sup = {'supplier__name': detail_sup,
                            'order__document_number': so['order__document_number'],
                            'order_id': so['order_id'],
                            'supplier_id': sup['supplier_id'],
                            'order__document_date': od.document_date.strftime("%d-%m-%Y")}
                items_sup = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                     order_id=so['order_id'], supplier_id=sup['supplier_id']).order_by('line_number')

                totalAmount_row = 0
                for itm in items_sup:
                    # check if there are po order item for this line
                    po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                           reference_id=itm.order_id, refer_line=itm.line_number,
                                                           order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                        .aggregate(quantity=Sum('quantity'))['quantity']

                    if po_item_qty and po_item_qty >= itm.quantity:
                        continue

                    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                item_id=itm.item_id,
                                                                supplier_id=sup['supplier_id']).first()
                    if supplier_item:
                        if not supplier_item.effective_date:
                            totalAmount_row += itm.quantity * supplier_item.purchase_price
                        elif datetime.date.today() >= supplier_item.effective_date:
                            totalAmount_row += itm.quantity * supplier_item.new_price
                        else:
                            totalAmount_row += itm.quantity * supplier_item.purchase_price
                    else:
                        messages.add_message(request, messages.ERROR, "Supplier Item doesn't have Purchase Price."
                                             "Please add the correct Purchase Price first.",
                                             extra_tags='bank_delete')
                        main_item = Item.objects.get(pk=itm.item_id)
                        if main_item and main_item.purchase_price:
                            totalAmount_row += itm.quantity * main_item.purchase_price
                        else:
                            totalAmount_row += itm.quantity * itm.price

                loop_sup['supplier_total'] = totalAmount_row
                array.append(loop_sup)

        return render_to_response('generate_purchase_order.html',
                                  RequestContext(request, {'supplier_list': array,
                                                           'sale_order_id': sale_order_id,
                                                           'order_type': dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                           'so_list': so_list, 'from_so': from_so, 'to_so': to_so}))
    else:
        supplier_list = None
    return render_to_response('generate_purchase_order.html', RequestContext(request, {'supplier_list': supplier_list,
                                                                                       'sale_order_id': sale_order_id,
                                                                                       'order_type': dict(ORDER_TYPE)[
                                                                                           'PURCHASE ORDER'],
                                                                                       'so_list': so_list}))


@login_required
@csrf_exempt
def generate_purchase_order(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if request.method == 'POST':
        sale_order_list = request.POST.get('so_list')
        sale_order_list = sale_order_list.split(',')
        new_sale_order_list = list(set(sale_order_list))
        sale_orders = Order.objects.filter(id__in=new_sale_order_list).order_by('document_number')

        for sale_order in sale_orders:
            # already_generate = Order.objects.filter(is_hidden=0, company_id=company_id,
            #                                         reference_number=sale_order.document_number).first()
            # if already_generate:
            #     messages.add_message(request, messages.ERROR,
            #                          'ERROR :: Purchase Order has been created from Sales Order ' +
            #                          already_generate.reference_number + ' with Document no ' +
            #                          str(already_generate.document_number))
            #     return HttpResponseRedirect(
            #         reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['SALES ORDER']}))
            try:
                sale_order_header = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order_id=sale_order.id, x_position=1, y_position=0).latest(
                    'update_date')
            except OrderHeader.DoesNotExist:
                sale_order_header = None
            supplier_selected_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                              order__company_id=company_id,
                                                              order_id=sale_order.id) \
                .exclude(quantity__lte=F('delivery_quantity')) \
                .values('supplier_id', 'line_number', 'quantity')
            # convert queryset to list
            # supplier_selected_list = list(supplier_selected_list)
            new_supplier_selected_list = []
            for i in supplier_selected_list:
                po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                       reference_id=sale_order.id, refer_line=i['line_number'],
                                                       order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                    .aggregate(quantity=Sum('quantity'))['quantity']

                if po_item_qty and po_item_qty >= i['quantity']:
                    continue
                new_supplier_selected_list.append(i['supplier_id'])
            new_supplier_selected_list = list(set(new_supplier_selected_list))
            if new_supplier_selected_list.__len__() > 0:
                filter_transaction_code = TransactionCode.objects.filter(
                    is_hidden=False, company_id=company_id,
                    name="PURCHASE ORDER",
                    menu_type=int(TRN_CODE_TYPE_DICT['Purchase Number File'])).last()
                with transaction.atomic():
                    for my_supplier_id in new_supplier_selected_list:
                        if my_supplier_id != "":
                            # order process
                            supplier = Supplier.objects.get(pk=my_supplier_id)
                            order = Order()
                            order.company_id = company_id
                            order.document_date = datetime.datetime.today()
                            order.document_number = generate_document_number(
                                company_id,
                                str(datetime.datetime.today().date()),
                                int(TRN_CODE_TYPE_DICT['Purchase Number File']),
                                filter_transaction_code.id if filter_transaction_code else '')
                            order.order_code = order.document_number
                            order.delivery_date = sale_order.delivery_date
                            order.invoice_date = sale_order.invoice_date
                            order.due_date = sale_order.due_date
                            exchange_rate = None
                            if supplier.currency_id is not sale_order.currency_id:
                                exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                            from_currency_id=supplier.currency_id,
                                                                            to_currency_id=company.currency_id,
                                                                            flag='ACCOUNTING').order_by('exchange_date').last()
                            if exchange_rate:
                                order.exchange_rate = exchange_rate.rate
                                order.exchange_rate_date = exchange_rate.exchange_date
                            else:
                                order.exchange_rate = sale_order.exchange_rate
                                order.exchange_rate_date = sale_order.exchange_rate_date if sale_order.exchange_rate_date else None
                            order.supplier_id = my_supplier_id
                            order.currency_id = supplier.currency_id
                            order.tax_id = supplier.tax_id if supplier else sale_order.tax_id
                            order.reference_number = sale_order.document_number
                            order.order_type = dict(ORDER_TYPE)['PURCHASE ORDER']
                            order.subtotal = 0
                            order.total = 0
                            order.balance = 0
                            order.tax_amount = 0
                            order.create_date = sale_order.create_date
                            order.update_date = sale_order.update_date
                            order.update_by_id = request.user.id
                            order.is_hidden = False
                            order.status = dict(ORDER_STATUS)['Sent']
                            order.exchange_rate_fk_id = sale_order.exchange_rate_fk_id if sale_order.exchange_rate_fk_id else None
                            order.remark = sale_order.remark
                            order.save()

                            order_header = OrderHeader()
                            order_header.order_id = order.id
                            if sale_order_header is not None:
                                order_header.label = sale_order_header.label
                                order_header.value = sale_order_header.value
                            else:
                                order_header.label = ""
                                order_header.value = ""
                            order_header.x_position = 1
                            order_header.y_position = 0
                            order_header.create_date = order.create_date
                            order_header.update_date = order.update_date
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.save()

                            # Save OrderItem
                            old_order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                           order__company_id=company_id,
                                                                           order_id=sale_order.id,
                                                                           supplier_id=my_supplier_id).order_by('line_number')
                            sum_amount = 0
                            line = 1
                            for old_order_item in old_order_item_list:
                                po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                       reference_id=sale_order.id, refer_line=old_order_item.line_number,
                                                                       order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                                    .aggregate(quantity=Sum('quantity'))['quantity']

                                if po_item_qty and po_item_qty >= old_order_item.quantity:
                                    continue
                                supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                            item_id=old_order_item.item_id,
                                                                            supplier_id=my_supplier_id).first()

                                if po_item_qty:
                                    quantity = old_order_item.quantity - po_item_qty
                                else:
                                    quantity = old_order_item.quantity
                                order_item = OrderItem()
                                order_item.order_id = order.id
                                order_item.customer_po_no = old_order_item.customer_po_no
                                order_item.supplier_id = old_order_item.supplier_id
                                order_item.reference_id = sale_order.id
                                order_item.item_id = old_order_item.item_id
                                order_item.location_id = old_order_item.location_id
                                order_item.from_currency_id = old_order_item.from_currency_id
                                order_item.to_currency_id = supplier.currency_id
                                order_item.exchange_rate = old_order_item.exchange_rate
                                order_item.quantity = quantity
                                order_item.stock_quantity = 0
                                order_item.delivery_quantity = 0
                                order_item.receive_quantity = 0
                                order_item.refer_line = old_order_item.line_number
                                order_item.line_number = line
                                order_item.refer_number = sale_order.document_number
                                order_item.wanted_date = old_order_item.wanted_date
                                order_item.schedule_date = old_order_item.schedule_date
                                order_item.price = old_order_item.item.purchase_price
                                if supplier_item:
                                    if not supplier_item.effective_date:
                                        order_item.price = supplier_item.purchase_price
                                    elif supplier_item.new_price and datetime.date.today() >= supplier_item.effective_date:
                                        order_item.price = supplier_item.new_price
                                    else:
                                        order_item.price = supplier_item.purchase_price
                                order_item.amount = order_item.price * quantity
                                sum_amount += order_item.amount
                                order_item.create_date = old_order_item.create_date
                                order_item.update_date = old_order_item.update_date
                                order_item.update_by_id = request.user.id
                                order_item.is_hidden = False
                                order_item.save()
                                line = line + 1

                                if company.is_inventory:
                                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                        fail = True
                                        for upd_inv_log in update_inv_qty_log:
                                            messages.add_message(request, messages.ERROR,
                                                                 'ERROR: ' + upd_inv_log['log'],
                                                                 extra_tags=upd_inv_log['tag'])
                                        messages.add_message(request, messages.ERROR,
                                                             SEND_DOC_FAILED + REFRESH_OR_GO_GET_SUPPORT,
                                                             extra_tags='send_doc_failed')

                            # save Total of Order
                            tax_rate = supplier.tax.rate if supplier.tax else sale_order.tax.rate if sale_order.tax else 0
                            order = Order.objects.get(pk=order.id)
                            order.subtotal = sum_amount
                            order.tax_amount = (sum_amount * tax_rate) / 100
                            order.total = sum_amount + order.tax_amount
                            order.balance = sum_amount
                            order.save()

                            msg = 'Order Purchase  ' + str(
                                order.document_number) + ' was generated from ' + 'Order Sale ' + sale_order.document_number
                            messages.add_message(request, messages.INFO, msg)

    return HttpResponseRedirect(reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE ORDER']}))


@login_required
def download_purchase_load(request):
    messageStr = ''
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    supplier_list = None
    so_list = OrderItem.objects. \
        filter(is_hidden=0,
               order__is_hidden=0,
               order__company_id=company_id,
               order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
               order__status__gte=dict(ORDER_STATUS)['Sent']). \
        exclude(quantity__lte=F('delivery_quantity')). \
        values('order_id', 'order__document_number'). \
        order_by('-order__document_number').distinct()
    if request.method == 'POST':
        supplier_list = OrderItem.objects.none()
        from_po = request.POST.get('from_po')
        to_po = request.POST.get('to_po')
        order_ids = get_order_filter_range(dict(ORDER_TYPE)['PURCHASE ORDER'], company_id, int(from_po), int(to_po), 'id')
        needToRemove = []
        purchase_order = so_list. \
            filter(order_id__in=order_ids). \
            values('order_id', 'supplier_id', 'supplier__name', 'order__document_date', 'order__document_number'). \
            annotate(supplier_total=Sum('amount'))
        supplier_list = list(chain(supplier_list, purchase_order))
        if purchase_order:
            for so in supplier_list:
                po = Order.objects.filter(is_hidden=0, company_id=company_id,
                                          reference_number=so['order__document_number']).first()
                if po:
                    needToRemove.append({'so': so, 'po': po})
            for i in needToRemove:
                messageStr += '<li>- ' + i['po'].document_number + ' generated from ' + i[
                    'po'].reference_number + '</li>'
                supplier_list.remove(i['so'])
            if supplier_list.__len__() == 0:
                messages.add_message(request, messages.ERROR,
                                     'Purchase Order has been generated from SO : <br/> <ul class="list-unstyled" style="margin-left:15px">' +
                                     messageStr + '</ul>',
                                     extra_tags='search_sale_order')
            return render_to_response('download_purchase_order.html',
                                      RequestContext(request, {'supplier_list': supplier_list,
                                                               'order_type': dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                               'so_list': so_list, 'from_po': from_po, 'to_po': to_po}))

        else:
            messages.add_message(request, messages.ERROR,
                                 'Document Number of the Order does not exist!',
                                 extra_tags='download_purchase_load')
        if supplier_list.__len__() == 0:
            supplier_list = None
    return render_to_response('download_purchase_order.html',
                              RequestContext(request, {'supplier_list': supplier_list,
                                                       'order_type': dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                       'so_list': so_list}))


@login_required
def download_purchase_order(request):
    response = HttpResponse(content_type='application/zip')
    if request.method == 'POST':
        list_po = request.POST.getlist('purchase_order_id')
        response['Content-Disposition'] = 'attachment; filename="PO_%s.zip' % datetime.datetime.now().strftime(
            '%Y%m%d_%H%M%S')
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        files = []
        for order_id in list_po:
            order = Order.objects.get(pk=order_id)
            report = Print_PO_Order(BytesIO(), 'Letter')
            pdf = report.print_report(order_id, '1', company_id, None)
            files.append(
                ("%s_%s.pdf" % (order.document_number, datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), pdf))
        buffer = BytesIO()
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        for name, f in files:
            zip.writestr(name, f)
        zip.close()
        buffer.flush()
        ret_zip = buffer.getvalue()
        buffer.close()
        response.write(ret_zip)
    return response


@login_required
def load_sales_items_by_supplier(request, sale_order_id, supplier_id):
    if request.method == 'POST':
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        try:
            od = Order.objects.get(pk=sale_order_id)
            supplier = Supplier.objects.get(pk=supplier_id)
            if od.currency_id is not supplier.currency_id:
                exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                            from_currency_id=supplier.currency_id,
                                                            to_currency_id=company.currency_id,
                                                            flag='ACCOUNTING').order_by('exchange_date').last()

                exchange_rate = exchange_rate.rate
            else:
                exchange_rate = od.exchange_rate
            sale_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=sale_order_id, supplier_id=supplier_id).order_by('line_number')
            i = 0
            list_data = []
            for d in range(0, len(sale_item_list)):
                if sale_item_list[i]:
                    pp = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                     supplier__company_id=company_id, supplier__is_hidden=0,
                                                     item=sale_item_list[i].item).first().purchase_price
                    am = sale_item_list[i].quantity * pp
                    list_data.append({'name': sale_item_list[i].item.name, 'quantity': str(sale_item_list[i].quantity),
                                      'purchase_price': str(pp), 'exchange_rate': str(exchange_rate),
                                      'amount': str(am)})
                i += 1
            sale_item_list_json = json.dumps(list_data)
            return HttpResponse(sale_item_list_json, content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='except load_sales_items_by_supplier')
    else:
        return HttpResponse(json.dumps({"status": "fail"}), content_type="application/json")


@login_required
def print_order(request, order_id):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        order = Order.objects.get(pk=order_id)
        return render_to_response('order_print.html',
                                  RequestContext(request, {'order_id': order_id, 'order_type': order.order_type}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def order_view(request, order_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order = Order.objects.get(pk=order_id)
    company = Company.objects.get(id=order.company_id)
    orderStatus = dict([element[::-1] for element in ORDER_STATUS])[order.status]
    information = Customer.objects.get(id=order.customer_id)
    supplier = Supplier.objects.get(id=order.supplier_id)
    orderItem = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                         order_id=order_id) \
        .values('order__currency__code', 'line_number', 'item_id', 'price', 'quantity') \
        .annotate(total=Sum(F('quantity')) * Sum(F('price'))) \
        .annotate(item_code=Value('0', output_field=models.CharField())) \
        .annotate(item_name=Value('0', output_field=models.CharField()))
    currency = Currency.objects.filter(id=order.currency_id)

    item_code_all = Item.objects.filter(id__in=[item.item_id for item in orderItem], company_id=company_id, is_hidden=0)

    for item in orderItem:
        item_code = item_code_all.filter(id=item.item_id).first()
        item['item_code'] = item_code.code if item_code else ''
        item['item_name'] = item_code.name if item_code else ''

    if (order.order_type == dict(ORDER_TYPE)['PURCHASE ORDER']) or (
            order.order_type == dict(ORDER_TYPE)['PURCHASE INVOICE']):
        information = supplier

    return render_to_response('order_view.html', RequestContext(request, {'order': order, 'company': company,
                                                                          'orderStatus': orderStatus,
                                                                          'information': information,
                                                                          'orderItem': orderItem, 'currency': currency,
                                                                          'media_url': s.MEDIA_URL}))


def create_stock_transaction(order, company_id, transaction_code):
    newStockTrans = __import__('utilities.common', globals(), locals(), ['UpdateStockTransaction'],
                               0).UpdateStockTransaction
    newStockTrans = newStockTrans(order, company_id, transaction_code)

    return newStockTrans


@login_required
@permission_required('orders.add_order', login_url='/alert/')
@check_inventory_closing
@check_sp_closing
def generate_good_receive(request, order_id, status):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    po_order = Order.objects.get(pk=order_id)
    company = Company.objects.get(pk=company_id)
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id).first()
    # get all items of Order by Order_ID
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id, supplier_id=po_order.supplier_id).values() \
        .exclude(quantity=F('receive_quantity')) \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier_id')) \
        .annotate(currency_id=F('from_currency')) \
        .annotate(original_currency=F('from_currency__code')) \
        .annotate(location=F('location_id')) \
        .annotate(uom=F('item__sales_measure__name')) \
        .annotate(ref_number=F('order__document_number')) \
        .annotate(code=F('item__code')) \
        .annotate(refer_line=F('line_number')) \
        .annotate(order_quantity=F('quantity')) \
        .annotate(quantity=F('quantity')) \
        .annotate(receive_quantity=F('receive_quantity')) \
        .annotate(customer_po_no=F('customer_po_no')) \
        .annotate(category=F('item__category__code'))
    # Define formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(GoodReceiveAddItemForm)(partial(GoodReceiveAddItemForm, company_id=company_id)))
    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)

    newStockTrans = None

    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = OrderHeaderForm(request.POST)
                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')

                form_info = OrderInfoForm(company_id, 5, instance=po_order)

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):

                    try:
                        currency_symbol = Currency.objects.get(pk=po_order.currency_id).symbol
                    except Currency.DoesNotExist:
                        currency_symbol = Currency.objects.none()

                    if po_order.supplier_id:
                        supplier = Supplier.objects.get(pk=po_order.supplier_id)
                    else:
                        supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
                    # get list if items
                    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order_id=order_id, supplier_id=supplier.id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
                        exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                        annotate(item_name=F('item__name')). \
                        annotate(supplier_code=F('supplier__code')). \
                        annotate(supplier_id=F('supplier_id')). \
                        annotate(order_type=F('order__order_type')). \
                        annotate(ref_id=F('order_id')). \
                        annotate(ref_number=F('order__document_number')). \
                        annotate(ref_line=F('line_number')). \
                        annotate(currency_id=F('from_currency')). \
                        annotate(currency=F('from_currency__code')). \
                        annotate(location_code=F('location__code')). \
                        annotate(location_id=F('location_id')). \
                        annotate(purchase_price=F('item__purchase_price')). \
                        annotate(code=F('item__code')). \
                        annotate(category=F('item__category__code')). \
                        annotate(uom=F('item__purchase_measure__name')). \
                        annotate(minimun_order=F('item__minimun_order')). \
                        annotate(quantity=F('quantity')). \
                        annotate(receive_quantity=F('receive_quantity')). \
                        annotate(customer_po_no=F('customer_po_no')). \
                        annotate(line_id=Value(0, output_field=models.CharField()))
                    statusid = po_order.status
                    context = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                               'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                               'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                               'request_method': request.method, 'currency_symbol': currency_symbol, 'order': po_order,
                               'statusid': statusid, 'is_generate': True}
                    return render_to_response('order_good_receive_copy.html', RequestContext(request, context))

                new_order = Order()
                new_order.debit_account_id = request.POST.get('debit_account')
                new_order.credit_account_id = request.POST.get('credit_account')
                new_order.reference_number = po_order.document_number
                new_order.invoice_date = request.POST.get('invoice_date')
                new_order.delivery_date = request.POST.get('delivery_date')
                new_order.currency_id = request.POST.get('currency')
                new_order.supplier_id = request.POST.get('hdSupplierId')
                # new_order.order_code = po_order.order_code
                new_order.tax_id = request.POST.get('tax')
                new_order.exchange_rate = po_order.exchange_rate
                if request.POST.get('discount'):
                    new_order.discount = Decimal(request.POST.get('discount'))
                if request.POST.get('subtotal'):
                    new_order.subtotal = Decimal(request.POST.get('subtotal'))
                if request.POST.get('total'):
                    new_order.total = Decimal(request.POST.get('total'))
                    new_order.balance = Decimal(request.POST.get('total'))
                if request.POST.get('tax_amount'):
                    new_order.tax_amount = Decimal(request.POST.get('tax_amount'))
                new_order.cost_center_id = request.POST.get('cost_center')
                new_order.note = request.POST.get('note')
                new_order.remark = request.POST.get('remark')
                new_order.footer = request.POST.get('footer')
                new_order.packing_number = 1
                new_order.order_type = dict(ORDER_TYPE)['PURCHASE INVOICE']
                new_order.create_date = datetime.datetime.today()
                new_order.update_date = datetime.datetime.today()
                new_order.update_by_id = request.user.id
                new_order.is_hidden = False
                new_order.company_id = company.id
                if request.POST.get('document_number'):
                    new_order.document_number = request.POST.get('document_number')
                if not request.POST.get('document_number'):
                    new_order.document_number = ''

                new_order.order_code = new_order.document_number
                new_order.document_date = request.POST.get('document_date')
                new_order.status = int(status)
                new_order.save()
                if int(status) >= dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                    newStockTrans = create_stock_transaction(new_order, company_id,
                                                             request.POST.get('transaction_code'))

                if form.is_valid():
                    header = form.save(commit=False)
                    header.order_id = new_order.id
                    header.x_position = 1
                    header.y_position = 0
                    header.create_date = datetime.datetime.today()
                    header.update_date = datetime.datetime.today()
                    header.update_by_id = request.user.id
                    header.is_hidden = 0
                    header.save()
                else:
                    print("generate_good_receive form.errors: ", form.errors)

                # order headers | formset_right
                if formset_right.is_valid():
                    for form in formset_right:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = new_order.id
                            order_header.save()
                else:
                    print("generate_good_receive formset_right.errors: ", formset_right.errors)

                # order headers | formset_left
                if formset_left.is_valid():
                    for form in formset_left:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 0
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = new_order.id
                            order_header.save()
                else:
                    print("generate_good_receive formset_left.errors: ", formset_left.errors)

                # order headers | formset_code
                if formset_code.is_valid():
                    for form in formset_code:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 2
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = new_order.id
                            order_header.save()
                else:
                    print("generate_good_receive formset_code.errors: ", formset_code.errors)

                # list of PO orders
                po_orders_list = []
                receive_status = 0
                # Order Item | formset_item
                if formset_item.is_valid():
                    stt = 0
                    for form in formset_item:
                        prev_order_item = OrderItem.objects.filter(item_id=form.cleaned_data.get('item_id'), reference_id=po_order.id).last()

                        if prev_order_item is None:
                            prev_stock_quantity = 0
                        else:
                            prev_stock_quantity = prev_order_item.stock_quantity

                        # process each OrderItem
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.reference_id = po_order.id
                        order_item.supplier_id = po_order.supplier_id
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        order_item.schedule_date = datetime.datetime.today()
                        if company.is_inventory:
                            order_item.location_id = form.cleaned_data.get('location').id
                        stt += 1
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = stt
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('currency')
                        order_item.stock_quantity = prev_stock_quantity + form.cleaned_data.get('quantity')
                        order_item.receive_quantity = form.cleaned_data.get('quantity')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = new_order.id
                        order_item.save()
                        if int(status) >= dict(ORDER_STATUS)['Sent']:
                            if company.is_inventory:
                                newStockTrans.addItem(order_item)

                            # update Order Item
                            if form.cleaned_data.get('reference_id'):
                                # Purchase Order
                                po_reference = Order.objects.get(pk=po_order.id)
                                # update this orderitem of this purchase order
                                item_po = OrderItem.objects.get(is_hidden=0, order__is_hidden=0,
                                                                order__company_id=company_id,
                                                                order_id=po_order.id,
                                                                item_id=form.cleaned_data.get('item_id'),
                                                                line_number=form.cleaned_data.get('refer_line'))
                                if po_reference and item_po:
                                    # Add this po to po_orders_list
                                    if po_reference.id not in po_orders_list:
                                        po_orders_list.append(po_reference)

                                    item_po.stock_quantity += form.cleaned_data.get('quantity')
                                    item_po.receive_quantity += form.cleaned_data.get('quantity')
                                    item_po.save()
                                    if item_po.reference_id:
                                        # Sales Order
                                        so_reference = Order.objects.get(pk=item_po.reference_id)
                                        # update this orderitem of this sales order
                                        item_so = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                           order__company_id=company_id,
                                                                           order_id=item_po.reference_id,
                                                                           item_id=form.cleaned_data.get(
                                                                               'item_id')).first()

                                        if so_reference and item_so:
                                            item_so.stock_quantity = 0 if item_so.stock_quantity == None else item_so.stock_quantity
                                            item_so.stock_quantity += form.cleaned_data.get('quantity')
                                            item_so.receive_quantity += form.cleaned_data.get('quantity')
                                            item_so.save()
                    if int(status) >= dict(ORDER_STATUS)['Sent']:
                        po_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                 order__company_id=company_id,
                                                                 order_id=po_order.id)
                        for i in po_order_item:
                            if i.receive_quantity < i.quantity:
                                receive_status += 1

                        po_order.status = dict(ORDER_STATUS)['Partial'] if receive_status > 0 else dict(ORDER_STATUS)[
                            'Received']
                        po_order.save()
                else:
                    print("generate_good_receive formset_item.errors: ", formset_item.errors)

                if int(status) >= dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                    newStockTrans.generate()

                # update status of po in po_orders_list
                if int(status) >= dict(ORDER_STATUS)['Sent'] and len(po_orders_list) > 0:
                    for po in po_orders_list:
                        orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                              order__company_id=company_id,
                                                              order_id=po.id,
                                                              order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])
                        flag = True
                        for item in orderitems:
                            if item.receive_quantity != item.quantity:
                                flag = False

                        po.status = dict(ORDER_STATUS)['Received'] if flag else dict(ORDER_STATUS)['Partial']
                        po.save()

            return HttpResponseRedirect(
                reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='generate_good_receive')
    else:
        try:
            order_header = order_header_list.filter(x_position=1, y_position=0).first()
        except OrderHeader.DoesNotExist:
            order_header = None
        try:
            currency_symbol = Currency.objects.get(pk=po_order.currency_id).symbol
        except Currency.DoesNotExist:
            currency_symbol = Currency.objects.none()
        # get label and value formset right
        extra_right = order_header_list.filter(x_position=1, y_position=1).values()
        # get label and value formset left
        extra_left = order_header_list.filter(x_position=0, y_position=1).values()
        # get label and value formset code
        extra_code = order_header_list.filter(x_position=1, y_position=2).values()

        if po_order.supplier_id:
            supplier = Supplier.objects.get(pk=po_order.supplier_id)
        else:
            supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
        # get list if items
        items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order_id=order_id, supplier_id=supplier.id,
                                              order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
            annotate(item_name=F('item__name')). \
            annotate(supplier_code=F('supplier__code')). \
            annotate(supplier_id=F('supplier_id')). \
            annotate(order_type=F('order__order_type')). \
            annotate(ref_id=F('order_id')). \
            annotate(ref_number=F('order__document_number')). \
            annotate(ref_line=F('line_number')). \
            annotate(currency_id=F('from_currency')). \
            annotate(currency=F('from_currency__code')). \
            annotate(location_code=F('location__code')). \
            annotate(location_id=F('location_id')). \
            annotate(purchase_price=F('item__purchase_price')). \
            annotate(code=F('item__code')). \
            annotate(category=F('item__category__code')). \
            annotate(uom=F('item__purchase_measure__name')). \
            annotate(minimun_order=F('item__minimun_order')). \
            annotate(quantity=F('quantity')). \
            annotate(receive_quantity=F('receive_quantity')). \
            annotate(customer_po_no=F('customer_po_no')). \
            annotate(line_id=Value(0, output_field=models.CharField()))

        form = OrderHeaderForm(instance=order_header)
        form_info = OrderInfoForm(company_id, 5, instance=po_order)
        formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
        formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
        formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
        formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)
        statusid = po_order.status
        context = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                   'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                   'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                   'request_method': request.method, 'currency_symbol': currency_symbol, 'order': po_order,
                   'statusid': statusid, 'is_generate': True}
        return render_to_response('order_good_receive_copy.html', RequestContext(request, context))


@login_required
def good_receive_list(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        gr_list = Order.objects.filter(is_hidden=0, company_id=company_id,
                                       order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'])
        if request.method == 'POST':
            doc_no = request.POST.get('doc_no')
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            if doc_no:
                gr_list = gr_list.filter(document_number__icontains=doc_no)
            if date_from:
                gr_list = gr_list.filter(document_date__gte=date_from)
            if date_to:
                gr_list = gr_list.filter(document_date__lte=date_to)
            form = GoodReceiveSearchForm(request.POST)
        else:
            form = GoodReceiveSearchForm()

        return render_to_response('order_good_receive_list.html',
                                  RequestContext(request, {'form': form, 'gr_list': gr_list, 'company_id': company_id}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


def get_distribution_code_list(company_id, dis_type):
    distribution_code_list_ar = []
    try:
        distribution_code_list = DistributionCode.objects. \
            filter(is_hidden=False,
                   is_active=True, company_id=company_id,
                   type=dis_type)
        if distribution_code_list:
            for dist_code_list in distribution_code_list:
                distribution_code_list_obj = {'id': dist_code_list.id,
                                              'code': dist_code_list.code,
                                              'name': dist_code_list.name,
                                              'gl_account_id': dist_code_list.gl_account_id,
                                              'tax_id': None}
                distribution_code_list_ar.append(distribution_code_list_obj)
    except Exception as e:
        print(e)
    return distribution_code_list_ar


@login_required
@permission_required('orders.add_order', login_url='/alert/')
@check_inventory_closing
@check_sp_closing
def good_receive_new(request, type='N'):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    distribution_code_list = get_distribution_code_list(company_id,
                                                        dict(DIS_CODE_TYPE_REVERSED)['AP Distribution Code'])
    company = Company.objects.get(pk=company_id)
    tax_authority = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id).first()
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()
    supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
    if not supplier:
        messages.add_message(request, messages.ERROR, "suppliers", extra_tags='order_new_empty_supplier')
        return HttpResponseRedirect(
            reverse('order_list', args=(), kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
    form = OrderHeaderForm(request.POST)
    form_info = GoodReceiveInfoForm(company_id, 5, request.POST, session_date=request.session['session_date'])
    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          supplier_id=supplier.id,
                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
        exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
        annotate(item_name=F('item__name')). \
        annotate(supplier_code=F('supplier__code')). \
        annotate(supplier_id=F('supplier_id')). \
        annotate(order_type=F('order__order_type')). \
        annotate(ref_id=F('order_id')). \
        annotate(ref_number=F('order__document_number')). \
        annotate(ref_line=F('line_number')). \
        annotate(currency_id=F('supplier__currency')). \
        annotate(currency=F('supplier__currency__code')). \
        annotate(location_code=F('location__code')). \
        annotate(location_id=F('location_id')). \
        annotate(purchase_price=F('item__purchase_price')). \
        annotate(code=F('item__code')). \
        annotate(category=F('item__category__code')). \
        annotate(uom=F('item__purchase_measure__name')). \
        annotate(minimun_order=F('item__minimun_order')). \
        annotate(quantity=F('quantity')). \
        annotate(receive_quantity=F('receive_quantity')). \
        annotate(customer_po_no=F('customer_po_no')). \
        annotate(line_id=Value(0, output_field=models.CharField()))
    # Define formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(GoodReceiveAddItemForm)(partial(GoodReceiveAddItemForm, company_id=company_id)))
    formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
    formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
    formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
    formset_item = ItemFormSet(request.POST, prefix='formset_item')

    newStockTrans = None

    if request.method == 'POST':
        try:
            with transaction.atomic():

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    if type == 'N':
                        template = 'order_good_receive_form.html'
                    else:
                        template = 'order_good_receive_foxpro.html'
                    return render(request, template,
                                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                                   'items_list': items_list, 'formset_right': formset_right,
                                   'formset_left': formset_left,
                                   'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                                   'request_method': request.method})
                # order process
                order = Order()
                order.document_date = request.POST.get('document_date')
                order.debit_account_id = request.POST.get('debit_account')
                order.credit_account_id = request.POST.get('credit_account')
                order.reference_number = request.POST.get('reference_number')
                # order.order_code = request.POST.get('order_code')
                order.exchange_rate_fk_id = request.POST.get('exchange_rate_fk_id') if request.POST.get(
                    'exchange_rate_fk_id') else None
                order.exchange_rate_date = request.POST.get('exchange_rate_date') if request.POST.get(
                    'exchange_rate_date') else None
                order.exchange_rate = request.POST.get('id_exchange_rate_value')
                if order.exchange_rate == '' or order.exchange_rate == None:
                    order.exchange_rate = 0
                if request.POST.get('invoice_date'):
                    order.invoice_date = request.POST.get('invoice_date')
                if request.POST.get('delivery_date'):
                    order.delivery_date = request.POST.get('delivery_date')
                order.currency_id = request.POST.get('currency')
                order.supplier_id = request.POST.get('hdSupplierId')
                if request.POST.get('tax'):
                    order.tax_id = request.POST.get('tax')
                if request.POST.get('discount'):
                    order.discount = Decimal(request.POST.get('discount'))
                order.subtotal = Decimal(request.POST.get('subtotal'))
                order.total = Decimal(request.POST.get('total'))
                order.tax_amount = Decimal(request.POST.get('tax_amount'))
                order.balance = order.total
                if request.POST.get('cost_center'):
                    order.cost_center_id = request.POST.get('cost_center')
                if request.POST.get('note'):
                    order.note = request.POST.get('note')
                if request.POST.get('remark'):
                    order.remark = request.POST.get('remark')
                if request.POST.get('footer'):
                    order.footer = request.POST.get('footer')
                order.packing_number = 1
                order.order_type = dict(ORDER_TYPE)['PURCHASE INVOICE']
                order.create_date = datetime.datetime.today()
                order.update_date = datetime.datetime.today()
                order.update_by_id = request.user.id
                order.is_hidden = False
                order.company_id = company.id
                if request.POST.get('document_number'):
                    order.document_number = request.POST.get('document_number')
                if not request.POST.get('document_number'):
                    order.document_number = ''
                order.order_code = order.document_number
                order.status = dict(ORDER_STATUS)['Sent']
                order.tax_exchange_rate = request.POST.get('tax_exchange_rate')
                if order.tax_exchange_rate == '' or order.tax_exchange_rate == None:
                    order.tax_exchange_rate = order.exchange_rate
                order.supllier_exchange_rate = request.POST.get('supllier_exchange_rate')
                if order.supllier_exchange_rate == '' or order.supllier_exchange_rate == None:
                    order.supllier_exchange_rate = order.exchange_rate

                order.distribution_code_id = request.POST.get('distribution_code')
                order.save()
                if order.status == dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                    newStockTrans = create_stock_transaction(order, company_id, request.POST.get('transaction_code'))

                if OrderHeaderForm(request.POST):
                    order_header = OrderHeader()
                    order_header.x_position = 1
                    order_header.y_position = 0
                    order_header.label = request.POST.get('label')
                    order_header.value = request.POST.get('value')
                    order_header.create_date = datetime.datetime.today()
                    order_header.update_date = datetime.datetime.today()
                    order_header.update_by_id = request.user.id
                    order_header.is_hidden = False
                    order_header.order_id = order.id
                    order_header.save()

                if formset_right.is_valid():
                    for form in formset_right:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                'value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("good_receive_new formset_right.errors: ", formset_right.errors)

                if formset_left.is_valid():
                    for form in formset_left:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                'value') is not None:
                            order_header.x_position = 0
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("good_receive_new formset_left.errors: ", formset_left.errors)

                # list of PO orders
                po_orders_list = []
                if formset_item.is_valid():
                    fail = False
                    for form in formset_item:
                        prev_order_item = OrderItem.objects.filter(item_id=form.cleaned_data.get(
                            'item_id'), reference_id=form.cleaned_data.get('reference_id')).last()

                        if prev_order_item is None:
                            prev_stock_quantity = 0
                        else:
                            prev_stock_quantity = prev_order_item.stock_quantity

                        # process each OrderItem
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.reference_id = form.cleaned_data.get('reference_id')
                        order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        order_item.schedule_date = datetime.datetime.today()
                        if company.is_inventory and form.cleaned_data.get('location') \
                            and form.cleaned_data.get('location') != 'None':
                            order_item.location_id = form.cleaned_data.get('location').id
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = form.cleaned_data.get('line_number')
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('currency')
                        order_item.stock_quantity = prev_stock_quantity + form.cleaned_data.get('quantity')
                        order_item.receive_quantity = form.cleaned_data.get('quantity')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = order.id
                        order_item.save()

                        if order.status == dict(ORDER_STATUS)['Sent']:
                            if form.cleaned_data.get('reference_id'):
                                po_reference = Order.objects.get(pk=form.cleaned_data.get('reference_id'))
                                if po_reference not in po_orders_list:
                                    po_orders_list.append(po_reference)

                                update_gr_reference, update_gr_reference_errs = order_vs_inventory(
                                    request).set_reference_item(order_item.id)
                                if not update_gr_reference:
                                    fail = True
                                    messages.add_message(request, messages.ERROR,
                                                         create_error_string(update_gr_reference_errs),
                                                         extra_tags='send_doc_failed')

                            if company.is_inventory and not fail:
                                newStockTrans.addItem(order_item)
                                # update item & locationitem qty
                                update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                                if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                    fail = True
                                    messages.add_message(request, messages.ERROR,
                                                         create_error_string(update_inv_qty_log),
                                                         extra_tags='send_doc_failed')

                    if fail:
                        order.status = dict(ORDER_STATUS)['Draft']
                        order.document_number = None
                        order.save()

                    if order.status == dict(ORDER_STATUS)['Sent'] and not fail:
                        sp_to_accounting = sp_to_acc(request)
                        new_batch = sp_to_accounting.generate_acc_entry(dict(TRANSACTION_TYPES)['AP Invoice'], order)
                        if not new_batch:
                            messages.add_message(request, messages.ERROR,
                                                 generate_errors(sp_to_accounting.get_errors()),
                                                 extra_tags='sp_to_acc_error')

                    if order.status == dict(ORDER_STATUS)['Sent'] and company.is_inventory and not fail:
                        newStockTrans.generate()

                    # update status of po in po_orders_list
                    if order.status == dict(ORDER_STATUS)['Sent'] and len(po_orders_list) > 0 and not fail:
                        for po in po_orders_list:
                            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                  order__company_id=company_id,
                                                                  order_id=po.id,
                                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])
                            flag = True
                            for item in orderitems:
                                if item.receive_quantity != item.quantity:
                                    flag = False

                            po.status = dict(ORDER_STATUS)['Received'] if flag else dict(ORDER_STATUS)['Partial']
                            po.save()
                else:
                    print("good_receive_new formset_item.errors: ", formset_item.errors)

                messages.success(request, "Document number " + order.document_number + " was successfully created")
                if type == 'N':
                    return HttpResponsePermanentRedirect(reverse('good_receive_new', kwargs={'type': 'N'}))
                else:
                    return HttpResponsePermanentRedirect(reverse('good_receive_new', kwargs={'type': 'old'}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='good_receive_new')

    else:
        tax_id = supplier.tax_id if supplier.tax_id else ''
        form_info = GoodReceiveInfoForm(company_id, 5, initial={'tax': tax_id,
                                                                'currency': supplier.currency_id if supplier.currency_id else ''},
                                        session_date=request.session['session_date'])
        form = OrderHeaderForm()
        formset_right = ExtraValueFormSetRight(prefix='formset_right')
        formset_left = ExtraValueFormSetLeft(prefix='formset_left')
        formset_item = ItemFormSet(prefix='formset_item')
        formset_code = ExtraValueFormSetCode(prefix='formset_code')

    if type == 'N':
        template = 'order_good_receive_form.html'
    else:
        template = 'order_good_receive_foxpro.html'
    return render(request, template,
                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                   'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                   'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                   'request_method': request.method,
                   'distribution_code_list': distribution_code_list, 'tax_authority': tax_authority})


@login_required
@csrf_exempt
def good_receive_search_item(request):
    if request.method == 'POST':
        if request.is_ajax():
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            supplier_id = request.POST.get('supplier_id')
            search_condition = request.POST.get('search_condition')
            exclude_item_json = request.POST.get('exclude_item_list')
            if search_condition == '0':
                items_list = Item.objects.none()
            else:
                if exclude_item_json:
                    exclude_item_list = json.loads(exclude_item_json)
                    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          supplier_id=supplier_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                        .filter(Q(item__name__icontains=search_condition) |
                                Q(item__code__icontains=search_condition) |
                                Q(order__document_number__icontains=search_condition) |
                                Q(supplier__code__icontains=search_condition) |
                                Q(item__category__code__icontains=search_condition) |
                                Q(location__code__icontains=search_condition), receive_quantity__lt=F('quantity')). \
                        exclude(item_id__in=exclude_item_list). \
                        exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                        annotate(item_name=F('item__name')). \
                        annotate(supplier_code=F('supplier__code')). \
                        annotate(supplier_id=F('supplier_id')). \
                        annotate(order_type=F('order__order_type')). \
                        annotate(ref_id=F('order_id')). \
                        annotate(ref_number=F('order__document_number')). \
                        annotate(ref_line=F('line_number')). \
                        annotate(currency_id=F('supplier__currency')). \
                        annotate(currency=F('supplier__currency__code')). \
                        annotate(location_code=F('location__code')). \
                        annotate(location_id=F('location_id')). \
                        annotate(purchase_price=F('item__purchase_price')). \
                        annotate(code=F('item__code')). \
                        annotate(category=F('item__category__code')). \
                        annotate(uom=F('item__purchase_measure__name')). \
                        annotate(minimun_order=F('item__minimun_order')). \
                        annotate(quantity=F('quantity')). \
                        annotate(receive_quantity=F('receive_quantity')). \
                        annotate(customer_po_no=F('customer_po_no')). \
                        annotate(line_id=Value(0, output_field=models.CharField()))

                else:
                    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          supplier_id=supplier_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                        .filter(Q(item__name__icontains=search_condition) |
                                Q(item__code__icontains=search_condition) |
                                Q(order__document_number__icontains=search_condition) |
                                Q(supplier__code__icontains=search_condition) |
                                Q(item__category__code__icontains=search_condition) |
                                Q(location__code__icontains=search_condition), receive_quantity__lt=F('quantity')). \
                        exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                        annotate(item_name=F('item__name')). \
                        annotate(supplier_code=F('supplier__code')). \
                        annotate(supplier_id=F('supplier_id')). \
                        annotate(order_type=F('order__order_type')). \
                        annotate(ref_id=F('order_id')). \
                        annotate(ref_number=F('order__document_number')). \
                        annotate(ref_line=F('line_number')). \
                        annotate(currency_id=F('supplier__currency')). \
                        annotate(currency=F('supplier__currency__code')). \
                        annotate(location_code=F('location__code')). \
                        annotate(location_id=F('location_id')). \
                        annotate(purchase_price=F('item__purchase_price')). \
                        annotate(code=F('item__code')). \
                        annotate(category=F('item__category__code')). \
                        annotate(uom=F('item__purchase_measure__name')). \
                        annotate(minimun_order=F('item__minimun_order')). \
                        annotate(quantity=F('quantity')). \
                        annotate(receive_quantity=F('receive_quantity')). \
                        annotate(customer_po_no=F('customer_po_no')). \
                        annotate(line_id=Value(0, output_field=models.CharField()))

                for i, j in enumerate(items_list):
                    if (i < items_list.__len__()):
                        i += 1
                        j['line_id'] = i

            return render(request, 'gr_items.html', {'items_list': items_list})


@login_required
def good_receive_po_as_json(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    exclude_po_list = json.loads(request.POST.get('exclude_list')) if request.POST.get('exclude_list') else []
    if supplier_id == '0':
        items_list = OrderItem.objects.none()
    else:
        items_list0 = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               supplier_id=supplier_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
            order_by('-id'). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            exclude(quantity__lte=F('receive_quantity')). \
            exclude(order__document_number__in=exclude_po_list). \
            values('order_id', 'order__document_number')
        items_list = items_list0.order_by('-order__document_number').distinct()

    array = []
    for field in items_list:
        order__document_number = str(field['order__document_number'])
        data = {"order_id": str(field['order_id']),
                "refer_number": order__document_number if order__document_number != 'None' and order__document_number else ''}

        array.append(data)

    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def good_receive_all_po_as_json(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    exclude_po_list = json.loads(request.POST.get('exclude_list')) if request.POST.get('exclude_list') else []
    if supplier_id == '0':
        items_list = OrderItem.objects.none()
    else:
        items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               supplier_id=supplier_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            exclude(quantity__lte=F('receive_quantity')). \
            exclude(order__document_number__in=exclude_po_list). \
            order_by('-order_id', 'line_number'). \
            values('order_id', 'order__document_number', 'line_number')

    array = []
    for item in items_list:
        data = {}
        data['ref_id'] = str(item['order_id'])
        data['refer_number'] = str(item['order__document_number'])
        data['refer_line'] = str(item['line_number'])
        array.append(data)

    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@permission_required('orders.change_order', login_url='/alert/')
@check_inventory_closing
@check_sp_closing
def good_receive_edit(request, order_id, type='N'):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    distribution_code_list = get_distribution_code_list(company_id,
                                                        dict(DIS_CODE_TYPE_REVERSED)['AP Distribution Code'])
    order = Order.objects.get(pk=order_id)
    decimal_place = order.currency.is_decimal
    initial_status = order.status
    company = Company.objects.get(pk=order.company_id)
    tax_authority = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id).first()
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id).first()
    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)
    try:
        order_header = order_header_list.filter(x_position=1, y_position=0).first()
    except OrderHeader.DoesNotExist:
        order_header = None
    # get all items of Order by Order_ID
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id,
                                          refer_line=F('reference__orderitem__line_number'),
                                          reference__orderitem__is_hidden=False) \
        .values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier_id')) \
        .annotate(currency_id=F('from_currency')) \
        .annotate(original_currency=F('from_currency__code')) \
        .annotate(location=F('location_id')) \
        .annotate(uom=F('item__purchase_measure__name')) \
        .annotate(ref_number=F('refer_number')) \
        .annotate(code=F('item__code')) \
        .annotate(order_quantity=F('reference__orderitem__quantity')) \
        .annotate(quantity=F('quantity')) \
        .annotate(receive_quantity=F('reference__orderitem__receive_quantity')) \
        .annotate(customer_po_no=F('customer_po_no')) \
        .annotate(category=F('item__category__code')).order_by('line_number')

    try:
        currency_symbol = Currency.objects.get(pk=order.currency_id).symbol
    except Currency.DoesNotExist:
        currency_symbol = Currency.objects.none()
    # get label and value formset right
    extra_right = order_header_list.filter(x_position=1, y_position=1).values()
    # get label and value formset left
    extra_left = order_header_list.filter(x_position=0, y_position=1).values()
    # get label and value formset code
    extra_code = order_header_list.filter(x_position=1, y_position=2).values()

    if order.supplier_id:
        supplier = Supplier.objects.get(pk=order.supplier_id)
    else:
        supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
    # get list if items
    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          supplier_id=supplier.id,
                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
        .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
        .values('item_id').annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_id=F('supplier_id')) \
        .annotate(order_type=F('order__order_type')) \
        .annotate(ref_id=F('order_id')) \
        .annotate(ref_number=F('order__document_number')) \
        .annotate(ref_line=F('line_number')) \
        .annotate(currency_id=F('supplier__currency')) \
        .annotate(currency=F('supplier__currency__code')) \
        .annotate(location_code=F('location__code')) \
        .annotate(location_id=F('location_id')) \
        .annotate(purchase_price=F('item__purchase_price')) \
        .annotate(code=F('item__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(uom=F('item__purchase_measure__name')) \
        .annotate(minimun_order=F('item__minimun_order')) \
        .annotate(quantity=F('quantity')) \
        .annotate(receive_quantity=F('receive_quantity')) \
        .annotate(customer_po_no=F('customer_po_no')) \
        .annotate(line_number=Value(0, output_field=models.CharField()))
    for i, j in enumerate(items_list):
        if (i < items_list.__len__()):
            i += 1
            j['line_number'] = i
    # Define formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(GoodReceiveAddItemForm)(partial(GoodReceiveAddItemForm, company_id=company_id)))

    newStockTrans = None

    if request.method == 'POST':
        # check if Acc batch is alrady posted or not
        sp_to_accounting = sp_to_acc(request)
        acc_batch_status = sp_to_accounting.check_batch_status(dict(TRANSACTION_TYPES)['AP Invoice'], order)
        if acc_batch_status and acc_batch_status == int(STATUS_TYPE_DICT['Posted']):
            messages.error(request, 'Cannot edit ' + order.document_number + ', as bacause the Accounting Batch is being already posted') 
            return HttpResponseRedirect(
                reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
        
        # check if stock transaction is alrady posted or not
        if company.is_inventory:
            orderStockTransction = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                        document_number=order.document_number)
            if orderStockTransction.exists():
                orderStockTransction = orderStockTransction.last()
                if orderStockTransction.is_closed:
                    messages.error(request, 'Cannot edit ' + order.document_number + ', as bacause the Stock entry already been closed in Inventory Control System.') 
                    return HttpResponseRedirect(
                        reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))

        fail = False
        try:
            last_item_qty = ast.literal_eval(request.POST['initial_item_qty_data'])
            order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0,
                                                           order__company_id=company_id,
                                                           order_id=order_id)
            with transaction.atomic():

                form = OrderHeaderForm(request.POST, instance=order_header)
                form_info = GoodReceiveInfoForm(company_id, 5, request.POST, instance=order)
                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    context = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                               'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                               'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                               'request_method': request.method, 'currency_symbol': currency_symbol, 'order': order, 'decimal_place': decimal_place}

                    if type == 'N':
                        template = 'order_good_receive_form.html'
                    else:
                        template = 'order_good_receive_foxpro.html'
                    return render(request, template, context)

                if company.is_inventory:
                    newStockTrans = create_stock_transaction(order, company_id, request.POST.get('transaction_code'))
                    if newStockTrans.getStockTransaction():
                        if not newStockTrans.deleteStockTransaction():
                            fail = True

                if not fail:
                    order.document_date = request.POST.get('document_date')
                    order.document_number = request.POST.get('document_number')
                    if initial_status < dict(ORDER_STATUS)['Sent']:
                        order.status = dict(ORDER_STATUS)['Sent']
                    order.exchange_rate = request.POST.get('id_exchange_rate_value')
                    order.tax_exchange_rate = request.POST.get('tax_exchange_rate')
                    order.supllier_exchange_rate = request.POST.get('supllier_exchange_rate')
                    order.distribution_code_id = request.POST.get('distribution_code')
                    order.tax_id = request.POST.get('tax')
                    order.save()

                    try:
                        old_trx = Transaction.objects.filter(order_id=order.id, is_hidden=0).last()
                    except:
                        pass

                # order process
                if form.is_valid() and not fail and order_header:
                    header = form.save(commit=False)
                    header.order_id = order_id
                    header.create_date = datetime.datetime.today()
                    header.update_date = datetime.datetime.today()
                    header.update_by_id = request.user.id
                    header.is_hidden = 0
                    header.save()
                else:
                    print("good_receive_edit form.errors, fail, order_header: ", form.errors, fail, order_header)

                if form_info.is_valid() and not fail:
                    info = form_info.save(commit=False)
                    info.supplier_id = request.POST.get('hdSupplierId')
                    info.id = order_id
                    if request.POST.get('cost_center'):
                        info.cost_center_id = request.POST.get('cost_center')
                    else:
                        info.cost_center_id = None
                    if request.POST.get('tax'):
                        info.tax_id = request.POST.get('tax')
                    else:
                        info.tax_id = None
                    if request.POST.get('id_exchange_rate_value'):
                        info.exchange_rate = request.POST.get('id_exchange_rate_value')
                    if request.POST.get('exchange_rate_fk_id') and request.POST.get('exchange_rate_fk_id') != 'None':
                        info.exchange_rate_fk_id = request.POST.get('exchange_rate_fk_id')
                    if request.POST.get('exchange_rate_date') and request.POST.get('exchange_rate_date') != 'None':
                        info.exchange_rate_date = request.POST.get('exchange_rate_date')
                    info.balance = info.total
                    info.update_date = datetime.datetime.today()
                    info.update_by_id = request.user.id
                    info.is_hidden = 0
                    info.remark = request.POST.get('remark')
                    info.save()
                else:
                    print("good_receive_edit form_info.errors, fail: ", form_info.errors, fail)

                if formset_right.is_valid() and not fail:
                    order_header_list.filter(x_position=1, y_position=1).delete()
                    for form in formset_right:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("good_receive_edit formset_right.errors, fail: ", formset_right.errors, fail)
                    order_header_list.filter(x_position=1, y_position=1).delete()

                if formset_left.is_valid() and not fail:
                    OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order_id=order_id, x_position=0, y_position=1).delete()
                    for form in formset_left:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 0
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("good_receive_edit formset_left.errors, fail: ", formset_left.errors, fail)
                    order_header_list.filter(x_position=0, y_position=1).delete()

                # list of PO orders
                po_orders_list = []

                if formset_item.is_valid() and not fail:
                    order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order_id=order_id)
                    # old_po_order_items = []
                    # new_po_order_items = []
                    for order_item in order_item_list:
                        # old_po_order_items.append({'reference_id': int(order_item.reference_id), 'id': order_item.id, 'line': order_item.line_number,
                        #                            'quantity': order_item.quantity, 'refer_line': int(order_item.refer_line)})
                        order_item.is_hidden = True
                        order_item.save()

                        # update refer item & inventory
                        if order_item.reference_id:
                            update_reference, update_reference_errs = order_vs_inventory(request)\
                                .set_reference_item(order_item.id, None, None, True)

                        if initial_status >= dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                            update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id, None, None, True)


                    line = 1
                    for form in formset_item:
                        # process each OrderItem
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.reference_id = form.cleaned_data.get('reference_id')
                        order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        order_item.schedule_date = datetime.date.today()
                        if company.is_inventory and form.cleaned_data.get('location') \
                            and form.cleaned_data.get('location') != 'None':
                            order_item.location_id = form.cleaned_data.get('location').id
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = line
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('currency')
                        order_item.stock_quantity = form.cleaned_data.get('quantity')
                        order_item.receive_quantity = form.cleaned_data.get('quantity')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        order_item.create_date = datetime.date.today()
                        order_item.update_date = datetime.date.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = order.id
                        order_item.save()
                        # new_po_order_items.append({'reference_id': int(form.cleaned_data.get('reference_id')),
                        #                            'refer_line': int(form.cleaned_data.get('refer_line')),
                        #                            'quantity': order_item.quantity, 'line': line})
                        line = line + 1

                        if initial_status >= dict(ORDER_STATUS)['Sent']:
                            if form.cleaned_data.get('reference_id'):
                                po_reference = Order.objects.get(pk=form.cleaned_data.get('reference_id'))
                                if po_reference not in po_orders_list:
                                    po_orders_list.append(po_reference)

                                # update_gr_reference, update_gr_reference_errs = order_vs_inventory(
                                    # request).set_reference_item(order_item.id, last_item_qty, initial_status)
                                update_gr_reference, update_gr_reference_errs = order_vs_inventory(
                                    request).set_reference_item(order_item.id)
                                if not update_gr_reference:
                                    print(order_item.id, 'ISSUE HERE: update_gr_reference')
                                    fail = True
                                    messages.add_message(request, messages.ERROR,
                                                         create_error_string(update_gr_reference_errs),
                                                         extra_tags='send_doc_failed')

                            if company.is_inventory and not fail:
                                newStockTrans.addItem(order_item)
                                # update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id, last_item_qty,
                                #                                              initial_status)
                                update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                                if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                    fail = True
                                    messages.add_message(request, messages.ERROR,
                                                         create_error_string(update_inv_qty_log),
                                                         extra_tags='send_doc_failed')

                    if initial_status >= dict(ORDER_STATUS)['Sent'] and company.is_inventory and not fail:
                        newStockTrans.generate()

                    if initial_status >= dict(ORDER_STATUS)['Sent'] and not fail:
                        sp_to_accounting = sp_to_acc(request)
                        new_batch = sp_to_accounting.update_acc_entry(dict(TRANSACTION_TYPES)['AP Invoice'], order)
                        if not new_batch:
                            messages.add_message(request, messages.ERROR,
                                                 generate_errors(sp_to_accounting.get_errors()),
                                                 extra_tags='sp_to_acc_error')

                    # update status of deleted po orders
                    # deleted_po_order_items = []
                    # for old_item in old_po_order_items:
                    #     found = False
                    #     for new_item in new_po_order_items:
                    #         if new_item['reference_id'] == old_item['reference_id'] and \
                    #                 new_item['refer_line'] == old_item['refer_line'] and \
                    #                 new_item['quantity'] == old_item['quantity'] and new_item['line'] == old_item['line']:
                    #             found = True
                    #             break
                    #     if not found:
                    #         deleted_po_order_items.append(old_item)
                    # if len(deleted_po_order_items):
                    #     for deleted_po in deleted_po_order_items:
                    #         if company.is_inventory:
                    #             update_inv_qty_log = push_doc_qty_to_inv_qty(request, deleted_po['id'], None,
                    #                                                             None, True)
                    #         po = Order.objects.get(pk=deleted_po['reference_id'])
                    #         order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                    #                                               order__company_id=company_id,
                    #                                               order_id=po.id, line_number=deleted_po['refer_line'],
                    #                                               order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']).first()
                    #         order_item.receive_quantity = order_item.receive_quantity - deleted_po['quantity']
                    #         order_item.stock_quantity = order_item.stock_quantity - deleted_po['quantity']
                    #         if order_item.receive_quantity < 0:
                    #             order_item.receive_quantity = 0
                    #         if order_item.stock_quantity < 0:
                    #             order_item.stock_quantity = 0
                    #         order_item.save()

                    #         all_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                    #                                              order__company_id=company_id,
                    #                                              order_id=po.id,
                    #                                              order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])
                    #         flag = True
                    #         total_qty = total_receive_qty = 0
                    #         for item in all_items:
                    #             total_qty += item.quantity
                    #             total_receive_qty += item.receive_quantity

                    #         if total_receive_qty > 0 and total_receive_qty < total_qty:
                    #             flag = False

                    #         po.status = dict(ORDER_STATUS)['Sent'] if flag else dict(ORDER_STATUS)['Partial']
                    #         po.save()
                    # update status of po in po_orders_list
                    if initial_status >= dict(ORDER_STATUS)['Sent'] and len(po_orders_list) > 0 and not fail:
                        for po in po_orders_list:
                            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                  order__company_id=company_id,
                                                                  order_id=po.id,
                                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])
                            flag = True
                            for item in orderitems:
                                if item.receive_quantity != item.quantity:
                                    flag = False

                            po.status = dict(ORDER_STATUS)['Received'] if flag else dict(ORDER_STATUS)['Partial']
                            po.save()
                else:
                    print("good_receive_edit formset_item.errors, fail: ", formset_item.errors, fail)

                if fail:
                    order.status = dict(ORDER_STATUS)['Draft']
                    # order.document_number = None
                    order.save()

            try:
                trx = Transaction.objects.filter(order_id=order.id, is_hidden=0).last()
                if trx:
                    if old_trx and int(old_trx.journal.flag) == FLAG_TYPE_DICT['CHECKED']:
                        trx.journal.flag = str(FLAG_TYPE_DICT['MODIFIED'])
                        trx.journal.save()

                        email_subject = str(trx.journal.batch.company.name) + ' Checked Journal in ' + \
                            str(trx.journal.batch.source_ledger) + ' Invoice was modified'

                        email_content = 'Details of the change\n'\
                            + '====================\n'\
                            + 'Time: ' + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + '\n'\
                            + 'Modified by: ' + str.strip(request.user.first_name + ' ' + request.user.last_name) + '\n'\
                            + 'Batch number: ' + str(trx.journal.batch.batch_no) + '\n'\
                            + 'Batch decription: ' + trx.journal.batch.description + '\n'\
                            + 'Entry Number: ' + str(trx.journal.batch.no_entries) + '\n'\
                            + 'Document number: ' + trx.journal.document_number + '\n'\
                            + 'Amount: ' + trx.journal.batch.currency.code + ' ' + str(trx.journal.batch.batch_amount) + '\n'

                        recepients = Staff.objects.filter(user__groups__name='Staff_Acc', notifyChangeSP=1)

                        for recepient in recepients:
                            try:
                                mail = EmailMessage(email_subject, email_content, request.user.email, [recepient.user.email])
                                mail.send()
                            except Exception as e:
                                print('Mail Error: ', e)

            except Exception as e:
                print('Error: ', e)
                pass

            return HttpResponseRedirect(
                reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='good_receive_edit')

    else:
        form = OrderHeaderForm(instance=order_header)
        form_info = GoodReceiveInfoForm(company_id, 5, instance=order)
        formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
        formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
        formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
        formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)
        context = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                   'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                   'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                   'request_method': request.method, 'currency_symbol': currency_symbol, 'order': order,
                   'distribution_code_list': distribution_code_list, 'decimal_place': decimal_place,
                   'tax_authority': tax_authority}
        if type == 'N':
            template = 'order_good_receive_form.html'
        else:
            template = 'order_good_receive_foxpro.html'
        return render(request, template, context)


def create_error_string(errors):
    error_strings = ''
    for err in errors:
        error_strings += err['log'] + '<br />'
    error_strings += SEND_DOC_FAILED + '<br />'
    error_strings += REFRESH_OR_GO_GET_SUPPORT
    return error_strings


@login_required
@permission_required('orders.add_order', login_url='/alert/')
@check_inventory_closing
@check_sp_closing
def good_receive_copy(request, order_id, status):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order = Order.objects.get(pk=order_id)
    company = Company.objects.get(pk=company_id)
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id).first()
    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)
    try:
        order_header = order_header_list.filter(x_position=1, y_position=0).first()
    except OrderHeader.DoesNotExist:
        order_header = None
    # get all items of Order by Order_ID
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id,
                                          refer_line=F('reference__orderitem__line_number')) \
        .values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier_id')) \
        .annotate(quantity=Sum(F('reference__orderitem__quantity') - F('reference__orderitem__receive_quantity'))) \
        .annotate(currency_id=F('from_currency')) \
        .annotate(original_currency=F('from_currency__code')) \
        .annotate(location=F('location_id')) \
        .annotate(uom=F('item__sales_measure__name')) \
        .annotate(ref_number=F('refer_number')) \
        .annotate(code=F('item__code')) \
        .annotate(order_quantity=F('reference__orderitem__quantity')) \
        .annotate(receive_quantity=F('reference__orderitem__receive_quantity')) \
        .annotate(customer_po_no=F('customer_po_no')) \
        .annotate(category=F('item__category__code'))
    try:
        currency_symbol = Currency.objects.get(pk=order.currency_id).symbol
    except Currency.DoesNotExist:
        currency_symbol = Currency.objects.none()
    # get label and value formset right
    extra_right = order_header_list.filter(x_position=1, y_position=1).values()
    # get label and value formset left
    extra_left = order_header_list.filter(x_position=0, y_position=1).values()
    # get label and value formset code
    extra_code = order_header_list.filter(x_position=1, y_position=2).values()

    if order.supplier_id:
        supplier = Supplier.objects.get(pk=order.supplier_id)
    else:
        supplier = Supplier.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()
    # Define formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(GoodReceiveAddItemForm)(partial(GoodReceiveAddItemForm, company_id=company_id)))

    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = OrderHeaderForm(request.POST)
                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          supplier_id=supplier.id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                        .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id').annotate(
                        item_name=F('item__name')) \
                        .annotate(supplier_code=F('supplier__code')) \
                        .annotate(supplier_id=F('supplier_id')) \
                        .annotate(order_type=F('order__order_type')) \
                        .annotate(ref_id=F('order_id')) \
                        .annotate(ref_number=F('order__document_number')) \
                        .annotate(ref_line=F('line_number')) \
                        .annotate(currency_id=F('supplier__currency')) \
                        .annotate(currency=F('supplier__currency__code')) \
                        .annotate(location_code=F('location__code')) \
                        .annotate(location_id=F('location_id')) \
                        .annotate(purchase_price=F('item__purchase_price')) \
                        .annotate(code=F('item__code')) \
                        .annotate(category=F('item__category__code')) \
                        .annotate(uom=F('item__purchase_measure__name')) \
                        .annotate(minimun_order=F('item__minimun_order')) \
                        .annotate(quantity=F('quantity')) \
                        .annotate(receive_quantity=F('receive_quantity')) \
                        .annotate(customer_po_no=F('customer_po_no')) \
                        .annotate(line_id=Value(0, output_field=models.CharField()))
                    form_info = GoodReceiveInfoForm(company_id, 5, instance=order)

                    context = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                               'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                               'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                               'request_method': request.method, 'currency_symbol': currency_symbol, 'order': order,
                               'status': status}
                    return render(request, 'order_good_receive_copy.html', context)

                new_order = Order()
                new_order.debit_account_id = request.POST.get('debit_account')
                new_order.credit_account_id = request.POST.get('credit_account')
                new_order.reference_number = request.POST.get('reference_number')
                # new_order.order_code = request.POST.get('order_code')

                if request.POST.get('invoice_date'):
                    new_order.invoice_date = request.POST.get('invoice_date')
                if request.POST.get('delivery_date'):
                    new_order.delivery_date = request.POST.get('delivery_date')
                new_order.currency_id = request.POST.get('currency')
                new_order.supplier_id = request.POST.get('hdSupplierId')
                if request.POST.get('tax'):
                    new_order.tax_id = request.POST.get('tax')
                if request.POST.get('discount'):
                    new_order.discount = Decimal(request.POST.get('discount'))
                new_order.subtotal = Decimal(request.POST.get('subtotal'))
                new_order.total = Decimal(request.POST.get('total'))
                new_order.balance = Decimal(request.POST.get('total'))
                new_order.tax_amount = Decimal(request.POST.get('tax_amount'))
                if request.POST.get('cost_center'):
                    new_order.cost_center_id = request.POST.get('cost_center')
                if request.POST.get('note'):
                    new_order.note = request.POST.get('note')
                if request.POST.get('remark'):
                    new_order.remark = request.POST.get('remark')
                if request.POST.get('footer'):
                    new_order.footer = request.POST.get('footer')
                new_order.packing_number = 1
                new_order.order_type = dict(ORDER_TYPE)['PURCHASE INVOICE']
                new_order.create_date = datetime.datetime.today()
                new_order.update_date = datetime.datetime.today()
                new_order.update_by_id = request.user.id
                new_order.is_hidden = False
                new_order.company_id = company.id
                new_order.document_date = request.POST.get('document_date')
                new_order.document_number = request.POST.get('document_number')
                new_order.order_code = new_order.document_number
                new_order.status = dict(ORDER_STATUS)['Draft']
                new_order.tax_exchange_rate = request.POST.get('tax_exchange_rate') if request.POST.get(
                    'tax_exchange_rate') else None
                new_order.supllier_exchange_rate = request.POST.get('supllier_exchange_rate') if request.POST.get(
                    'supllier_exchange_rate') else None
                new_order.distribution_code_id = request.POST.get('distribution_code') if request.POST.get(
                    'distribution_code') else None
                new_order.save()

                # order process
                if form.is_valid():
                    header = form.save(commit=False)
                    header.order_id = new_order.id
                    header.x_position = 1
                    header.y_position = 0
                    header.create_date = datetime.datetime.today()
                    header.update_date = datetime.datetime.today()
                    header.update_by_id = request.user.id
                    header.is_hidden = 0
                    header.save()
                else:
                    print("good_receive_copy form.errors: ", form.errors)

                if formset_right.is_valid():
                    for form in formset_right:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = new_order.id
                            order_header.save()
                else:
                    print("good_receive_copy formset_right.errors: ", formset_right.errors)

                if formset_left.is_valid():
                    for form in formset_left:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 0
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = new_order.id
                            order_header.save()
                else:
                    print("good_receive_copy formset_left.errors: ", formset_left.errors)

                if formset_code.is_valid():
                    for form in formset_code:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 2
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = new_order.id
                            order_header.save()
                else:
                    print("good_receive_copy formset_code.errors: ", formset_code.errors)

                if formset_item.is_valid():
                    for form in formset_item:
                        # process each OrderItem
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.reference_id = form.cleaned_data.get('reference_id')
                        order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        order_item.schedule_date = datetime.datetime.today()
                        if form.cleaned_data.get('location'):
                            order_item.location_id = form.cleaned_data.get('location').id
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = form.cleaned_data.get('line_number')
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('currency')
                        order_item.stock_quantity = form.cleaned_data.get('quantity')
                        order_item.receive_quantity = form.cleaned_data.get('quantity')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = new_order.id
                        order_item.save()
                else:
                    print("good_receive_copy formset_item.errors: ", formset_item.errors)

            return HttpResponseRedirect(
                reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='good_receive_copy')

    else:
        # get list if items
        items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              supplier_id=supplier.id,
                                              order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
            .values('item_id') \
            .annotate(item_name=F('item__name')) \
            .annotate(supplier_code=F('supplier__code')) \
            .annotate(supplier_id=F('supplier_id')) \
            .annotate(order_type=F('order__order_type')) \
            .annotate(ref_id=F('order_id')) \
            .annotate(ref_number=F('order__document_number')) \
            .annotate(ref_line=F('line_number')) \
            .annotate(currency_id=F('supplier__currency')) \
            .annotate(currency=F('supplier__currency__code')) \
            .annotate(location_code=F('location__code')) \
            .annotate(location_id=F('location_id')) \
            .annotate(purchase_price=F('item__purchase_price')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(uom=F('item__purchase_measure__name')) \
            .annotate(minimun_order=F('item__minimun_order')) \
            .annotate(quantity=F('quantity')) \
            .annotate(receive_quantity=F('receive_quantity')) \
            .annotate(customer_po_no=F('customer_po_no')) \
            .annotate(line_id=Value(0, output_field=models.CharField()))
        form = OrderHeaderForm(instance=order_header)
        form_info = GoodReceiveInfoForm(company_id, 5, instance=order)
        formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
        formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
        formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
        formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)

        context = {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                   'items_list': items_list, 'formset_right': formset_right, 'formset_left': formset_left,
                   'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                   'request_method': request.method, 'currency_symbol': currency_symbol, 'order': order,
                   'status': status}
        return render(request, 'order_good_receive_copy.html', context)


def create_order(company_id, request, form, order_id):
    order_item = OrderItem()
    order_item.item_id = form.cleaned_data.get('item_id')
    order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
    order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
    order_item.quantity = form.cleaned_data.get('quantity_do')
    order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
    if form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
        order_item.location_id = form.cleaned_data.get('location').id
    order_item.reference_id = form.cleaned_data.get('reference_id') if form.cleaned_data.get('reference_id') else None
    order_item.refer_number = form.cleaned_data.get('ref_number')
    order_item.refer_line = form.cleaned_data.get('refer_line')
    order_item.line_number = form.cleaned_data.get('line_number')
    order_item.from_currency_id = form.cleaned_data.get('currency_id')
    order_item.to_currency_id = request.POST.get('customer_currency_id')
    order_item.delivery_quantity = form.cleaned_data.get('quantity_do')
    order_item.price = form.cleaned_data.get('price')
    order_item.amount = form.cleaned_data.get('amount')
    order_item.origin_country_id = form.cleaned_data.get('origin_country_id')
    order_item.carton_no = form.cleaned_data.get('carton_no')
    order_item.carton_total = form.cleaned_data.get('carton_total')
    order_item.pallet_no = form.cleaned_data.get('pallet_no')
    order_item.net_weight = form.cleaned_data.get('net_weight')
    order_item.gross_weight = form.cleaned_data.get('gross_weight')
    order_item.m3_number = form.cleaned_data.get('m3_number')
    order_item.create_date = datetime.datetime.today()
    order_item.update_date = datetime.datetime.today()
    order_item.update_by_id = request.user.id
    order_item.is_hidden = False
    order_item.order_id = order_id
    order_item.save()

    return order_item


def check_item_location_qty(request, refer_item, items, company_id, item_qty_total, do_date):
    try:
        data = {}
        loc_items = LocationItem.objects.filter(item_id__in=items,
                        location__company_id=company_id,
                        is_hidden=False,
                        location__is_hidden=False)
        for item in refer_item:
            data["location_item_quantity"] = 0
            loc_item = loc_items. \
                filter(item_id=item.item_id, location_id=item.location_id)
            if loc_item.exists():
                loc_item = loc_item.aggregate(sum_onhand_qty=Coalesce(Sum('onhand_qty'), V(0)))
                data["location_item_quantity"] = str(loc_item.get('sum_onhand_qty'))
            if not len(loc_item) or float(data["location_item_quantity"]) <= 0:
                qty_gr = 0
                po_list = order_vs_inventory(request).get_next_doc_detail(item.id)
                if po_list:
                    for po in po_list:
                        gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
                        if gr_list:
                            for gr in gr_list:
                                qty_gr += gr.quantity
                if qty_gr == 0:
                    loc_itms = loc_items. \
                        filter(item_id=item.item_id).exclude(location_id=item.location_id).order_by('location_id')
                    if loc_itms.exists():
                        for loc_item in loc_itms:
                            if loc_item.onhand_qty:
                                qty_gr = loc_item.onhand_qty
                                break
                data["location_item_quantity"] = str(qty_gr)
            # cehck stock incoming date to get correct stock
            if data["location_item_quantity"]:
                stock_by_date_in = StockTransactionDetail.objects.filter(is_hidden=0, parent__is_closed=0, parent__company_id=company_id, in_location_id=item.location_id,
                                    item_id=item.item_id, parent__document_date__lte=do_date)\
                            .aggregate(current_onhand_qty=Coalesce(Sum('quantity'), V(0)))['current_onhand_qty']
                stock_by_date_out = StockTransactionDetail.objects.filter(is_hidden=0, parent__is_closed=0, parent__company_id=company_id, out_location_id=item.location_id,
                                                                          item_id=item.item_id, parent__document_date__lte=do_date)\
                            .aggregate(current_onhand_qty=Coalesce(Sum('quantity'), V(0)))['current_onhand_qty']
                print('stock_by_date_in', stock_by_date_in)
                print('stock_by_date_out', stock_by_date_out)
                print('(float(stock_by_date_in) - float(stock_by_date_out)', float(stock_by_date_in) - float(stock_by_date_out))
                if float(data["location_item_quantity"]) > (float(stock_by_date_in) - float(stock_by_date_out)) and\
                    (float(stock_by_date_in) - float(stock_by_date_out)) > 0:
                    data["location_item_quantity"] = str(float(stock_by_date_in) - float(stock_by_date_out))
                    print('data["location_item_quantity"]', data["location_item_quantity"])
            print(item.item_id,
                  item_qty_total[str(item.item_id)], data["location_item_quantity"])
            if (float(data["location_item_quantity"]) < float(item_qty_total[str(item.item_id)])):
                return [True, item.item.code]
                                
    except Exception as e:
        print(e)
    return [False, '']

@login_required
@permission_required('orders.add_order', login_url='/alert/')
@check_inventory_closing
@check_sp_closing
def order_DO_add(request, order_type, type='N'):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    tax_authority = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id).first()
    supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
    if not supplier:
        messages.add_message(request, messages.ERROR, "suppliers", extra_tags='order_new_empty_supplier')
        return HttpResponseRedirect(reverse('order_list', args=(), kwargs={'order_type': order_type}))
    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                supplier__company_id=company_id, supplier__is_hidden=0)
    countries_list = Country.objects.filter(is_hidden=0)
    distribution_code_list = get_distribution_code_list(company_id,
                                                        dict(DIS_CODE_TYPE_REVERSED)['AR Distribution Code'])

    form = OrderHeaderForm(request.POST)
    form_info = OrderInfoForm(company_id, order_type, request.POST, session_date=request.session['session_date'])
    form_delivery = OrderDeliveryForm(company_id, request.POST)
    # Define formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(DOInvoiceForm)(partial(DOInvoiceForm, company_id)))

    stock_transaction_code = TransactionCode.objects.filter(is_hidden=False, company_id=company_id, code='SIV',
                                                            menu_type='2').first()
    if stock_transaction_code:
        doc_num_auto = stock_transaction_code.auto_generate
    else:
        doc_num_auto = True

    newStockTrans = None

    if request.method == 'POST':
        try:
            with transaction.atomic():
                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')

                # location qty is valid
                if company.is_inventory:
                    item_list = []
                    refer_item = []
                    item_qty_total = {}
                    if formset_item.is_valid():
                        for form in formset_item:
                            item_id = form.cleaned_data.get('item_id')
                            reference_id = form.cleaned_data.get('reference_id') if form.cleaned_data.get('reference_id') else None
                            refer_line = form.cleaned_data.get('refer_line')
                            ref_item = None
                            if reference_id:
                                try:
                                    ref_item = OrderItem.objects.get(
                                        order_id=reference_id, line_number=refer_line, is_hidden=0)
                                except:
                                    pass
                            if ref_item:
                                refer_item.append(ref_item)
                            if item_id not in item_list:
                                item_list.append(item_id)
                                item_qty_total[item_id] = 0
                        for item_id in item_list:
                            for form in formset_item:
                                if (form.cleaned_data.get('item_id') == item_id):
                                    quantity = form.cleaned_data.get('quantity_do')
                                    item_qty_total[item_id] += int(quantity)
                        do_date = datetime.datetime.strptime(request.POST.get('document_date'), "%Y-%m-%d")
                        Fail = check_item_location_qty(
                            request, refer_item, item_list, company_id, item_qty_total, do_date)
                        if Fail[0]:
                            messages.error(request, Fail[1] + " Item has no sufficient stock")
                            if type == 'N':
                                template = 'order_DOInvoice.html'
                            else:
                                template = 'order_DOInvoice_foxpro.html'
                            return render(request, template,
                                            {'company': company, 'media_url': s.MEDIA_URL, 'form': form,
                                            'form_delivery': form_delivery,
                                            'form_info': form_info, 'countries_list': countries_list,
                                            'supplier_item': supplier_item,
                                            'order_type': order_type, 'formset_right': formset_right,
                                            'formset_left': formset_left,
                                            'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                                            'request_method': request.method})

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    if type == 'N':
                        template = 'order_DOInvoice.html'
                    else:
                        template = 'order_DOInvoice_foxpro.html'
                    return render(request, template,
                                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form,
                                   'form_delivery': form_delivery,
                                   'form_info': form_info, 'countries_list': countries_list,
                                   'supplier_item': supplier_item,
                                   'order_type': order_type, 'formset_right': formset_right,
                                   'formset_left': formset_left,
                                   'formset_item': formset_item, 'supplier': supplier, 'formset_code': formset_code,
                                   'request_method': request.method})

                # order process
                order = Order()
                if form.is_valid() and formset_item.is_valid():
                    order.customer_id = request.POST.get('hdCustomerId')
                    order.debit_account_id = request.POST.get('debit_account')
                    order.credit_account_id = request.POST.get('credit_account')
                    order.document_date = request.POST.get('document_date')
                    # order.order_code = request.POST.get('order_code')
                    order.currency_id = request.POST.get('customer_currency_id')
                    order.exchange_rate_fk_id = request.POST.get('exchange_rate_fk_id') if request.POST.get(
                        'exchange_rate_fk_id') else None
                    order.exchange_rate_date = request.POST.get('exchange_rate_date') if request.POST.get(
                        'exchange_rate_date') else None
                    order.exchange_rate = request.POST.get('id_exchange_rate_value')
                    order.tax_exchange_rate = request.POST.get('tax_exchange_rate')
                    if order.tax_exchange_rate == '' or order.tax_exchange_rate == None:
                        order.tax_exchange_rate = order.exchange_rate
                    order.order_type = order_type
                    order.status = dict(ORDER_STATUS)['Sent']
                    if request.POST.get('document_number') and request.POST.get('document_number') != '':
                        order.document_number = request.POST.get('document_number')
                    elif request.POST.get('document_date'):
                        order.document_number = generate_document_number(company_id,
                                                                         request.POST.get('document_date'),
                                                                         int(TRN_CODE_TYPE_DICT['Sales Number File']),
                                                                         request.POST.get('transaction_code'))
                        order.order_code = order.document_number
                    if request.POST.get('invoice_date'):
                        order.invoice_date = request.POST.get('invoice_date')
                    if request.POST.get('delivery_date'):
                        order.delivery_date = request.POST.get('delivery_date')
                    if request.POST.get('tax'):
                        order.tax_id = request.POST.get('tax')
                    if request.POST.get('discount'):
                        order.discount = Decimal(request.POST.get('discount'))
                    order.subtotal = Decimal(request.POST.get('subtotal'))
                    order.total = Decimal(request.POST.get('total'))
                    order.tax_amount = Decimal(request.POST.get('tax_amount'))
                    order.balance = order.total
                    if request.POST.get('cost_center'):
                        order.cost_center_id = request.POST.get('cost_center')
                    if request.POST.get('note_customer'):
                        order.note = request.POST.get('note_customer')
                    if request.POST.get('note_internal'):
                        order.remark = request.POST.get('note_internal')
                    if request.POST.get('footer'):
                        order.footer = request.POST.get('footer')
                    order.create_date = datetime.datetime.today()
                    order.update_date = datetime.datetime.today()
                    order.update_by_id = request.user.id
                    order.remark = request.POST.get('remark')
                    order.is_hidden = False
                    order.company_id = company_id
                    order = get_order_editable_data(order, request)

                    order.save()
                    if order.status == dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                        newStockTrans = create_stock_transaction(order, company_id,
                                                                 request.POST.get('transaction_code'))

                    if OrderHeaderForm(request.POST):
                        order_header = OrderHeader()
                        order_header.x_position = 1
                        order_header.y_position = 0
                        order_header.label = request.POST.get('label')
                        order_header.value = request.POST.get('value')
                        order_header.create_date = datetime.datetime.today()
                        order_header.update_date = datetime.datetime.today()
                        order_header.update_by_id = request.user.id
                        order_header.is_hidden = False
                        order_header.order_id = order.id
                        order_header.save()

                    if formset_right.is_valid():
                        for form in formset_right:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 1
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("order_DO_add formset_right.errors: ", formset_right.errors)

                    if formset_left.is_valid():
                        for form in formset_left:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 0
                                order_header.y_position = 1
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("order_DO_add formset_left.errors: ", formset_left.errors)

                    if formset_code.is_valid():
                        for form in formset_code:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 2
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("order_DO_add formset_code.errors: ", formset_code.errors)

                    fail = False
                    if formset_item.is_valid():
                        for form in formset_item:
                            fail = False
                            order_item = create_order(company_id, request, form, order.id)

                            if order.status == dict(ORDER_STATUS)['Sent']:
                                if form.cleaned_data.get('ref_number'):
                                    update_do_reference, update_do_reference_errs = order_vs_inventory(
                                        request).set_reference_item(order_item.id)
                                    if not update_do_reference:
                                        fail = True
                                        messages.add_message(request, messages.ERROR,
                                                             create_error_string(update_do_reference_errs),
                                                             extra_tags='update_reference_failed')

                                if company.is_inventory and not fail:
                                    newStockTrans.addItem(order_item)
                                    # update item & locationitem qty
                                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                        fail = True
                                        messages.add_message(request, messages.ERROR,
                                                             create_error_string(update_inv_qty_log),
                                                             extra_tags='send_doc_failed')
                    else:
                        print("order_DO_add formset_item.errors: ", formset_item.errors)

                    if fail:
                        order.status = dict(ORDER_STATUS)['Draft']
                        order.document_number = None
                        order.save()

                    # Order Delivery process
                    if form_delivery.is_valid() and not fail:
                        order_delivery = form_delivery.save(commit=False)
                        order_delivery.order_id = order.id
                        order_delivery.create_date = datetime.datetime.today()
                        order_delivery.update_date = datetime.datetime.today()
                        order_delivery.update_by_id = request.user.id
                        order_delivery.is_hidden = 0
                        if not request.POST.get('delivery'):
                            order_delivery.contact_id = request.POST.get('contact_id') if request.POST.get(
                                'contact_id') else None
                            order_delivery.delivery_id = None
                        else:
                            order_delivery.contact_id = None
                            order_delivery.delivery_id = request.POST.get('delivery') if request.POST.get(
                                'delivery') else None
                        order_delivery.save()
                    else:
                        print("order_DO_add form_delivery.errors, fail: ", form_delivery.errors, fail)

                    if order.status == dict(ORDER_STATUS)['Sent'] and company.is_inventory and not fail:
                        newStockTrans.generate()

                    if order.status == dict(ORDER_STATUS)['Sent'] and not fail:
                        cont = True
                        wish_doc_no = order.document_number
                        while cont:
                            # check one more time
                            check_order_count = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                                     document_number=wish_doc_no).count()
                            if check_order_count > 1:
                                doc_no = order.document_number.split('-')
                                postfix = int(doc_no[-1]) + 1
                                wish_doc_no = doc_no[0] + '-' + doc_no[1] + '-' + '{:05}'.format(postfix % 100000)
                                order.document_number = wish_doc_no
                                order.save()
                            else:
                                cont = False

                        sp_to_accounting = sp_to_acc(request)
                        new_batch = sp_to_accounting.generate_acc_entry(dict(TRANSACTION_TYPES)['AR Invoice'], order)
                        if not new_batch:
                            messages.add_message(request, messages.ERROR,
                                                 generate_errors(sp_to_accounting.get_errors()),
                                                 extra_tags='sp_to_acc_error')
                else:
                    print("order_DO_add form.errors, formset_item.errors: ", form.errors, formset_item.errors)

            messages.success(request, "Document number " + str(order.document_number) + " was successfully created")
            return HttpResponsePermanentRedirect(reverse('order_DO_add', args=[order_type, type]))

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='order_DO_add')

    # end if POST
    form_info = OrderInfoForm(company_id, order_type, initial={'tax': None, 'currency': None}, session_date=request.session['session_date'])
    form = OrderHeaderForm()
    form_delivery = OrderDeliveryForm(company_id)
    formset_right = ExtraValueFormSetRight(prefix='formset_right')
    formset_left = ExtraValueFormSetLeft(prefix='formset_left')
    formset_item = ItemFormSet(prefix='formset_item')
    formset_code = ExtraValueFormSetCode(prefix='formset_code')
    uom_list = ItemMeasure.objects.filter(is_active=True, is_hidden=False)
    if type == 'N':
        template = 'order_DOInvoice.html'
    else:
        template = 'order_DOInvoice_foxpro.html'

    return render(request, template,
                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_delivery': form_delivery,
                   'form_info': form_info,
                   'countries_list': countries_list, 'supplier_item': supplier_item, 'order_type': order_type,
                   'formset_right': formset_right, 'formset_left': formset_left, 'formset_item': formset_item,
                   'supplier': supplier, 'uom_list': uom_list,
                   'formset_code': formset_code, 'request_method': request.method,
                   'distribution_code_list': distribution_code_list, 'doc_num_auto': doc_num_auto,
                   'tax_authority': tax_authority})


def get_order_editable_data(order, request):
    order.via = request.POST.get('hdr_via') if request.POST.get('hdr_via') else None
    order.uom_id = request.POST.get('hdr_uom') if request.POST.get('hdr_uom') else None
    order.note = request.POST.get('hdr_delivery') if request.POST.get('hdr_delivery') else None
    order.distribution_code_id = request.POST.get('distribution_code')
    order.payment_term = request.POST.get('payment_term')
    order.payment_mode_id = request.POST.get('payment_mode') if request.POST.get('payment_mode') else None
    order.ship_from_id = request.POST.get('ship_from_code') if request.POST.get('ship_from_code') else None
    order.ship_to_id = request.POST.get('ship_to_code') if request.POST.get('ship_to_code') else None

    return order


def get_order_delivery_kwargs(company_id, customer_id, order_id):
    if customer_id is not 0:
        contact = Contact.objects.filter(is_hidden=0, company_id=company_id, customer_id=customer_id).first()
    else:
        contact = None
    order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order_id=order_id).first()
    kwargs = {"instance": order_delivery} if order_delivery else {"instance": contact}
    return kwargs, contact


@login_required
@permission_required('orders.change_order', login_url='/alert/')
@check_inventory_closing
@check_sp_closing
def order_DO_edit(request, order_id, order_type, copy_id, type='N'):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order = Order.objects.get(pk=order_id)
    decimal_place = order.currency.is_decimal
    initial_status = order.status
    order_status = order.status
    company = Company.objects.get(pk=order.company_id)
    tax_authority = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id).first()
    distribution_code_list = get_distribution_code_list(company_id,
                                                        dict(DIS_CODE_TYPE_REVERSED)['AR Distribution Code'])
    try:
        customer = Customer.objects.get(pk=order.customer_id)
    except Customer.DoesNotExist:
        customer = Customer.objects.none()
    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                supplier__company_id=company_id, supplier__is_hidden=0)
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id, reference__orderitem__is_hidden=0,
                                          refer_line=F('reference__orderitem__line_number')) \
        .select_related('item_id', 'supplier_id') \
        .values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier')) \
        .annotate(quantity_do=F('quantity')) \
        .annotate(currency_id=F('from_currency')) \
        .annotate(original_currency=F('to_currency__code')) \
        .annotate(location=F('location_id')) \
        .annotate(uom=F('item__sales_measure__name')) \
        .annotate(code=F('item__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(ref_number=F('refer_number')) \
        .annotate(order_quantity=F('reference__orderitem__quantity')) \
        .annotate(delivery_quantity=F('reference__orderitem__delivery_quantity')) \
        .annotate(origin_country_code=F('origin_country_id__code')).order_by('line_number')
    if not order_item:
        order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order_id=order_id) \
            .select_related('item_id', 'supplier_id') \
            .values() \
            .annotate(item_name=F('item__name')) \
            .annotate(supplier_code=F('supplier__code')) \
            .annotate(supplier_code_id=F('supplier')) \
            .annotate(quantity_do=F('quantity')) \
            .annotate(currency_id=F('from_currency')) \
            .annotate(original_currency=F('to_currency__code')) \
            .annotate(location_id=F('location_id')) \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(ref_number=F('refer_number')) \
            .annotate(order_quantity=Value(0, output_field=models.CharField())) \
            .annotate(delivery_quantity=Value(0, output_field=models.CharField())).order_by('line_number')
    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          item__customeritem__customer=customer.id,
                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
        .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
        .values('item_id') \
        .annotate(code=F('item__code')) \
        .annotate(item_name=F('item__name')) \
        .annotate(ref_number=F('order__document_number')) \
        .annotate(ref_line=F('line_number')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(location_code=F('location__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(sales_price=F('price')) \
        .annotate(currency=F('order__customer__currency__code')) \
        .annotate(location_id=F('location_id')) \
        .annotate(currency_id=F('order__customer__currency')) \
        .annotate(line_id=Value(0, output_field=models.CharField())) \
        .annotate(uom=F('item__purchase_measure__name')) \
        .annotate(supplier_code_id=F('supplier')) \
        .annotate(order_quantity=F('quantity')) \
        .annotate(delivery_quantity=F('delivery_quantity')) \
        .annotate(line_id=Value(0, output_field=models.CharField())).order_by('line_number')
    for i, j in enumerate(items_list):
        if i < items_list.__len__():
            i += 1
            j['line_id'] = i
    countries_list = Country.objects.filter(is_hidden=0)
    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)
    try:
        order_header = order_header_list.filter(x_position=1, y_position=0).first()
    except OrderHeader.DoesNotExist:
        order_header = None
        # get all items of Order by Order_ID
    try:
        currency_symbol = Currency.objects.get(pk=order.currency_id).symbol
    except Currency.DoesNotExist:
        currency_symbol = Currency.objects.none()

    # get label and value formset right
    extra_right = order_header_list.filter(x_position=1, y_position=1).values()
    # get label and value formset left
    extra_left = order_header_list.filter(x_position=0, y_position=1).values()
    # get label and value formset code
    extra_code = order_header_list.filter(x_position=1, y_position=2).values()
    # get order delivery info

    kwargs, contact = get_order_delivery_kwargs(company_id, customer.id, order_id)
    order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order_id=order_id).first()
    kwargs = {"instance": order_delivery} if order_delivery else {"instance": None}

    # formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(DOInvoiceForm)(partial(DOInvoiceForm, company.id)))

    newStockTrans = None
    info = None
    customer_delivery = None

    if request.method == 'POST':
        # check if Acc batch is alrady posted or not
        sp_to_accounting = sp_to_acc(request)
        acc_batch_status = sp_to_accounting.check_batch_status(dict(TRANSACTION_TYPES)['AR Invoice'], order)
        if acc_batch_status and acc_batch_status == int(STATUS_TYPE_DICT['Posted']):
            messages.error(request, 'Cannot edit ' + order.document_number + ', as bacause the Accounting Batch is being already posted') 
            return HttpResponseRedirect(
                    reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['SALES INVOICE']}))

        # check if stock transaction is alrady posted or not
        if company.is_inventory:
            orderStockTransction = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                        document_number=order.document_number)
            if orderStockTransction.exists():
                orderStockTransction = orderStockTransction.last()
                if orderStockTransction.is_closed:
                    messages.error(request, 'Cannot edit ' + order.document_number + ', as bacause the Stock entry already been closed in Inventory Control System.') 
                    return HttpResponseRedirect(
                        reverse('order_list', kwargs={'order_type': dict(ORDER_TYPE)['SALES INVOICE']}))

        fail = False
        last_item_qty = ast.literal_eval(request.POST['initial_item_qty_data'])
        order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order_id=order_id)
        try:
            with transaction.atomic():
                form = OrderHeaderForm(request.POST, instance=order_header)
                form_info = OrderInfoForm(company_id, order_type, request.POST, instance=order)
                form_delivery = OrderDeliveryForm(company_id, request.POST, **kwargs)
                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_item = ItemFormSet(request.POST, prefix='formset_item', initial=order_item)
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    context = {'company': company, 'cus': customer, 'media_url': s.MEDIA_URL, 'form': form,
                               'order': order, 'form_info': form_info, 'items_list': items_list,
                               'countries_list': countries_list, 'supplier_item': supplier_item,
                               'order_type': order_type, 'formset_right': formset_right,
                               'currency_symbol': currency_symbol, 'status': order_status, 'formset_left': formset_left,
                               'formset_item': formset_item, 'formset_code': formset_code,
                               'form_delivery': form_delivery, 'decimal_place': decimal_place,
                               'contact': contact, 'request_method': request.method, 'copy_id': copy_id}
                    if type == 'N':
                        template = 'order_DOInvoice.html'
                    else:
                        template = 'order_DOInvoice_foxpro.html'
                    return render_to_response(template, RequestContext(request, context))

                try:
                    old_trx = Transaction.objects.filter(order_id=order.id, is_hidden=0).last()
                except:
                    pass
                
                sid_one = transaction.savepoint()
                if form.is_valid():
                    header = form.save(commit=False)
                    header.order_id = order_id
                    header.x_position = 1
                    header.y_position = 0
                    header.create_date = datetime.datetime.today()
                    header.update_date = datetime.datetime.today()
                    header.update_by_id = request.user.id
                    header.is_hidden = 0
                    header.save()
                else:
                    print("order_DO_edit form.errors: ", form.errors)

                if form_info.is_valid():
                    info = form_info.save(commit=False)
                    info.id = order_id
                    info.customer_id = request.POST.get('hdCustomerId')
                    if request.POST.get('cost_center'):
                        info.cost_center_id = request.POST.get('cost_center')
                    else:
                        info.cost_center_id = None
                    if request.POST.get('tax'):
                        info.tax_id = request.POST.get('tax')
                    else:
                        info.tax_id = None
                    info.balance = info.total
                    info.update_date = datetime.datetime.today()
                    info.update_by_id = request.user.id
                    info.is_hidden = 0
                    info.remark = request.POST.get('remark')
                    if request.POST.get('id_exchange_rate_value'):
                        info.exchange_rate = request.POST.get('id_exchange_rate_value')
                    if request.POST.get('exchange_rate_fk_id') and request.POST.get('exchange_rate_fk_id') != 'None':
                        info.exchange_rate_fk_id = request.POST.get('exchange_rate_fk_id')
                    if request.POST.get('exchange_rate_date') and request.POST.get('exchange_rate_date') != 'None':
                        info.exchange_rate_date = request.POST.get('exchange_rate_date')
                    info.tax_exchange_rate = request.POST.get('tax_exchange_rate')
                    if info.tax_exchange_rate == '' or info.tax_exchange_rate == None:
                        info.tax_exchange_rate = info.exchange_rate
                    info.save()

                    order.document_date = request.POST.get('document_date')
                    if initial_status < dict(ORDER_STATUS)['Sent']:
                        order.status = dict(ORDER_STATUS)['Sent']
                    order = get_order_editable_data(order, request)
                    order.save()

                    if company.is_inventory:
                        newStockTrans = create_stock_transaction(info, company_id, request.POST.get('transaction_code'))
                        if newStockTrans.getStockTransaction():
                            if not newStockTrans.deleteStockTransaction():
                                fail = True
                else:
                    print("order_DO_edit form_info.errors: ", form_info.errors)

                if formset_right.is_valid() and not fail:
                    order_header_list.filter(x_position=1, y_position=1).delete()
                    for form in formset_right:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("order_DO_edit formset_right.errors, fail: ", formset_right.errors, fail)
                    order_header_list.filter(x_position=1, y_position=1).delete()

                if formset_left.is_valid() and not fail:
                    order_header_list.filter(x_position=0, y_position=1).delete()
                    for form in formset_left:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 0
                            order_header.y_position = 1
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("order_DO_edit formset_left.errors, fail: ", formset_left.errors, fail)
                    order_header_list.filter(x_position=0, y_position=1).delete()

                if formset_code.is_valid() and not fail:
                    order_header_list.filter(x_position=1, y_position=2).delete()
                    for form in formset_code:
                        order_header = OrderHeader()
                        if form.cleaned_data.get('label') is not None and form.cleaned_data.get('value') is not None:
                            order_header.x_position = 1
                            order_header.y_position = 2
                            order_header.label = form.cleaned_data.get('label')
                            order_header.value = form.cleaned_data.get('value')
                            order_header.create_date = datetime.datetime.today()
                            order_header.update_date = datetime.datetime.today()
                            order_header.update_by_id = request.user.id
                            order_header.is_hidden = False
                            order_header.order_id = order.id
                            order_header.save()
                else:
                    print("order_DO_edit formset_code.errors, fail: ", formset_code.errors, fail)
                    order_header_list.filter(x_position=1, y_position=2).delete()

                # old_so_order_items = []
                # new_so_order_items = []
                if formset_item.is_valid() and not fail:
                    order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order_id=order_id)
                    for order_item in order_item_list:
                        # old_so_order_items.append({'reference_id': int(order_item.reference_id), 'id': order_item.id, 'line': order_item.line_number,
                        #                            'quantity': order_item.quantity, 'refer_line': int(order_item.refer_line)})
                        order_item.is_hidden = True
                        order_item.save()

                        # update refer item & inventory
                        if order_item.reference_id:
                            update_reference, update_reference_errs = order_vs_inventory(request)\
                                .set_reference_item(order_item.id, None, None, True)

                        if initial_status >= dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                            update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id, None, None, True)
                            
                    # location qty is valid
                    # if company.is_inventory:
                    #     item_list = []
                    #     refer_item = []
                    #     item_qty_total = {}
                    #     if formset_item.is_valid():
                    #         for form in formset_item:
                    #             item_id = form.cleaned_data.get('item_id')
                    #             reference_id = form.cleaned_data.get('reference_id') if form.cleaned_data.get('reference_id') else None
                    #             refer_line = form.cleaned_data.get('refer_line')
                    #             ref_item = None
                    #             if reference_id:
                    #                 try:
                    #                     ref_item = OrderItem.objects.get(order_id=reference_id, line_number=refer_line, is_hidden=0)
                    #                 except:
                    #                     pass
                    #             if ref_item:
                    #                 refer_item.append(ref_item)
                    #             if item_id not in item_list:
                    #                 item_list.append(item_id)
                    #                 item_qty_total[item_id] = 0
                    #         for item_id in item_list:
                    #             for form in formset_item:
                    #                 if (form.cleaned_data.get('item_id') == item_id):
                    #                     quantity = form.cleaned_data.get('quantity_do')
                    #                     item_qty_total[item_id] += int(quantity)
                    #         Fail = check_item_location_qty(
                    #             request, refer_item, item_list, company_id, item_qty_total, info.document_date)
                    #         if Fail[0]:
                    #             transaction.savepoint_rollback(sid_one)
                    #             messages.error(request, Fail[1] + " Item has no sufficient stock")

                    #             context = {'company': company, 'cus': customer, 'media_url': s.MEDIA_URL, 'form': form,
                    #             'order': order, 'form_info': form_info, 'items_list': items_list,
                    #             'countries_list': countries_list, 'supplier_item': supplier_item,
                    #             'order_type': order_type, 'formset_right': formset_right,
                    #             'currency_symbol': currency_symbol, 'status': order_status, 'formset_left': formset_left,
                    #             'formset_item': formset_item, 'formset_code': formset_code,
                    #             'form_delivery': form_delivery, 'decimal_place': decimal_place,
                    #             'contact': contact, 'request_method': request.method, 'copy_id': copy_id}

                    #             if type == 'N':
                    #                 template = 'order_DOInvoice.html'
                    #             else:
                    #                 template = 'order_DOInvoice_foxpro.html'
                    #             return render_to_response(template, RequestContext(request, context))


                    line = 1
                    for form in formset_item:
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity_do')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        if form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
                            order_item.location_id = form.cleaned_data.get('location').id
                        order_item.reference_id = form.cleaned_data.get('reference_id') if form.cleaned_data.get(
                            'reference_id') else None
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = line
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('customer_currency_id')
                        order_item.stock_quantity = 0.0
                        order_item.delivery_quantity = form.cleaned_data.get('quantity_do')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        if form.cleaned_data.get('origin_country_id') and form.cleaned_data.get('origin_country_id') != 'undefined':
                            order_item.origin_country_id = form.cleaned_data.get('origin_country_id')
                        order_item.carton_no = form.cleaned_data.get('carton_no')
                        order_item.carton_total = form.cleaned_data.get('carton_total')
                        order_item.pallet_no = form.cleaned_data.get('pallet_no')
                        order_item.net_weight = form.cleaned_data.get('net_weight')
                        order_item.gross_weight = form.cleaned_data.get('gross_weight')
                        order_item.m3_number = form.cleaned_data.get('m3_number')
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = order.id
                        order_item.save()
                        # new_so_order_items.append({'reference_id': int(form.cleaned_data.get('reference_id')),
                        #                            'refer_line': int(form.cleaned_data.get('refer_line')),
                        #                            'quantity': order_item.quantity, 'line': line})
                        line = line + 1

                        if form.cleaned_data.get('ref_number'):
                            # update_do_reference, update_do_reference_errs = order_vs_inventory(
                                # request).set_reference_item(order_item.id, last_item_qty, initial_status)
                            update_do_reference, update_do_reference_errs = order_vs_inventory(
                                request).set_reference_item(order_item.id)
                            if not update_do_reference:
                                fail = True
                                messages.add_message(request, messages.ERROR,
                                                     create_error_string(update_do_reference_errs),
                                                     extra_tags='update_reference_failed')

                        if initial_status >= dict(ORDER_STATUS)['Sent'] and company.is_inventory:
                            newStockTrans.addItem(order_item)
                            # update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id, last_item_qty,
                            #                                              initial_status)
                            update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                            if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                fail = True
                                messages.add_message(request, messages.ERROR, create_error_string(update_inv_qty_log),
                                                     extra_tags='send_doc_failed')
                else:
                    print("order_DO_edit formset_item.errors, fail: ", formset_item.errors, fail)

                # Order Delivery process
                if form_delivery.is_valid() and not fail:
                    order_delivery = form_delivery.save(commit=False)
                    order_delivery.order_id = order_id
                    order_delivery.update_date = datetime.datetime.today()
                    order_delivery.update_by_id = request.user.id
                    if not request.POST.get('delivery'):
                        order_delivery.contact_id = request.POST.get('contact_id') if request.POST.get(
                            'contact_id') else None
                        order_delivery.delivery_id = None
                    else:
                        order_delivery.contact_id = None
                        order_delivery.delivery_id = request.POST.get('delivery') if request.POST.get(
                            'delivery') else None
                    order_delivery.save()
                else:
                    print("order_DO_edit form_delivery.errors, fail: ", form_delivery.errors, fail)

                # update status of deleted po orders
                # deleted_so_order_items = []
                # for old_item in old_so_order_items:
                #     found = False
                #     for new_item in new_so_order_items:
                #         if new_item['reference_id'] == old_item['reference_id'] and \
                #             new_item['refer_line'] == old_item['refer_line'] and \
                #             new_item['quantity'] == old_item['quantity'] and new_item['line'] == old_item['line']:
                #             found = True
                #             break
                #     if not found:
                #         deleted_so_order_items.append(old_item)
                # if len(deleted_so_order_items):
                #     for deleted_so in deleted_so_order_items:
                #         if company.is_inventory:
                #             update_inv_qty_log = push_doc_qty_to_inv_qty(request, deleted_so['id'], None,
                #                                                          None, True)
                #         so = Order.objects.get(pk=deleted_so['reference_id'])
                #         order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                #                                               order__company_id=company_id,
                #                                               order_id=so.id, line_number=deleted_so['refer_line'],
                #                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER']).first()
                #         if order_item:
                #             order_item.delivery_quantity = order_item.delivery_quantity - deleted_so['quantity']
                #             order_item.stock_quantity = order_item.stock_quantity - deleted_so['quantity']
                #             order_item.save()

                #         all_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                #                                              order__company_id=company_id,
                #                                              order_id=so.id,
                #                                              order__order_type=dict(ORDER_TYPE)['SALES ORDER'])
                #         flag = True
                #         total_qty = total_delivery_qty = 0
                #         for item in all_items:
                #             total_qty += item.quantity
                #             total_delivery_qty += item.delivery_quantity

                #         if total_delivery_qty > 0 and total_delivery_qty < total_qty:
                #             flag = False

                #         so.status = dict(ORDER_STATUS)['Sent'] if flag else dict(ORDER_STATUS)['Partial']
                #         so.save()

                if initial_status >= dict(ORDER_STATUS)['Sent'] and form_info.is_valid() and not fail:
                    if company.is_inventory:
                        newStockTrans.generate()
                    cont = True
                    wish_doc_no = info.document_number
                    while cont:
                        # check one more time
                        check_order_count = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                                 document_number=wish_doc_no).count()
                        if check_order_count > 1:
                            doc_no = order.document_number.split('-')
                            postfix = int(doc_no[-1]) + 1
                            wish_doc_no = doc_no[0] + '-' + doc_no[1] + '-' + '{:05}'.format(postfix % 100000)
                            info.document_number = wish_doc_no
                            info.save()
                        else:
                            cont = False

                    sp_to_accounting = sp_to_acc(request)
                    new_batch = sp_to_accounting.update_acc_entry(dict(TRANSACTION_TYPES)['AR Invoice'], order)
                    if not new_batch:
                        messages.add_message(request, messages.ERROR, generate_errors(sp_to_accounting.get_errors()),
                                             extra_tags='sp_to_acc_error')

                try:
                    trx = Transaction.objects.filter(order_id=order.id, is_hidden=0).last()
                    if trx:

                        if old_trx and int(old_trx.journal.flag) == FLAG_TYPE_DICT['CHECKED']:
                            trx.journal.flag = str(FLAG_TYPE_DICT['MODIFIED'])
                            trx.journal.save()

                            email_subject = str(trx.journal.batch.company.name) + ' Checked Journal in ' + \
                                str(trx.journal.batch.source_ledger) + ' Invoice was modified'

                            email_content = 'Details of the change\n'\
                                + '====================\n'\
                                + 'Time: ' + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + '\n'\
                                + 'Modified by: ' + str.strip(request.user.first_name + ' ' + request.user.last_name) + '\n'\
                                + 'Batch number: ' + str(trx.journal.batch.batch_no) + '\n'\
                                + 'Batch decription: ' + trx.journal.batch.description + '\n'\
                                + 'Entry Number: ' + str(trx.journal.batch.no_entries) + '\n'\
                                + 'Document number: ' + trx.journal.document_number + '\n'\
                                + 'Amount: ' + trx.journal.batch.currency.code + ' ' + str(trx.journal.batch.batch_amount) + '\n'

                            recepients = Staff.objects.filter(user__groups__name='Staff_Acc', notifyChangeSP=1)

                            for recepient in recepients:
                                try:
                                    mail = EmailMessage(email_subject, email_content, request.user.email, [recepient.user.email])
                                    mail.send()
                                except Exception as e:
                                    print('Mail Error: ', e)

                except Exception as e:
                    print('Error: ', e)
                    pass

            return HttpResponseRedirect('/orders/list/' + order_type + '/')
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='order_DO_edit')

    form = OrderHeaderForm(instance=order_header)
    form_info = OrderInfoForm(company_id, order_type, instance=order)

    form_delivery = OrderDeliveryForm(company_id, **kwargs)
    try:
        customer_delivery = Delivery.objects.get(pk=kwargs['instance'].delivery_id)
    except Exception as e:
        print(e)

    # load formset values
    formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
    formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
    formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
    formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)
    cust_info_obj = {'cust_name': None, 'info1': None, 'info2': None, 'info3': None, 'info4': None, 'info5': None}
    if order.note:
        cust_info = order.note.split(',')
        cust_info_obj['cust_name'] = cust_info[0] if len(cust_info) >= 1 else None
        cust_info_obj['info1'] = cust_info[1] if len(cust_info) >= 2 else None
        cust_info_obj['info2'] = cust_info[2] if len(cust_info) >= 3 else None
        cust_info_obj['info3'] = cust_info[3] if len(cust_info) >= 4 else None
        cust_info_obj['info4'] = cust_info[4] if len(cust_info) >= 5 else None
        cust_info_obj['info5'] = cust_info[5] if len(cust_info) >= 6 else None
    uom_list = ItemMeasure.objects.filter(is_active=True, is_hidden=False)

    context = {'company': company, 'cus': customer, 'media_url': s.MEDIA_URL, 'form': form,
               'order': order, 'form_info': form_info, 'items_list': items_list, 'countries_list': countries_list,
               'supplier_item': supplier_item, 'cust_info': cust_info_obj, 'order_type': order_type,
               'formset_right': formset_right, 'currency_symbol': currency_symbol, 'status': order_status,
               'formset_left': formset_left, 'formset_item': formset_item, 'formset_code': formset_code,
               'form_delivery': form_delivery, 'contact': contact, 'request_method': request.method,
               'copy_id': copy_id, 'uom_list': uom_list, 'customer_delivery': customer_delivery,
               'distribution_code_list': distribution_code_list, 'decimal_place': decimal_place,
               'tax_authority': tax_authority}
    if type == 'N':
        template = 'order_DOInvoice.html'
    else:
        template = 'order_DOInvoice_foxpro.html'
    return render_to_response(template, RequestContext(request, context))


@login_required
@check_inventory_closing
@check_sp_closing
def order_DO_copy(request, order_id, order_type, is_send):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order_DO = Order.objects.get(pk=order_id)
    order_status = order_DO.status

    company = Company.objects.get(pk=order_DO.company_id)
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id).first()
    distribution_code_list = get_distribution_code_list(company_id,
                                                        dict(DIS_CODE_TYPE_REVERSED)['AR Distribution Code'])
    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                supplier__company_id=company_id, supplier__is_hidden=0)
    try:
        customer = Customer.objects.get(pk=order_DO.customer_id)
    except Customer.DoesNotExist:
        messages.add_message(request, messages.ERROR, "suppliers", extra_tags='order_new_empty_supplier')
        return HttpResponseRedirect(reverse('order_list', args=(), kwargs={'order_type': order_type}))
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id,
                                          refer_line=F('reference__orderitem__line_number')) \
        .select_related('item_id', 'supplier_id').values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier')) \
        .annotate(quantity_do=Sum((F('reference__orderitem__quantity') - F('reference__orderitem__delivery_quantity')))) \
        .annotate(currency_id=F('to_currency')) \
        .annotate(original_currency=F('to_currency__code')) \
        .annotate(location_id=F('location_id')) \
        .annotate(uom=F('item__sales_measure__name')) \
        .annotate(code=F('item__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(ref_number=F('refer_number')) \
        .annotate(order_quantity=F('reference__orderitem__quantity')) \
        .annotate(delivery_quantity=F('reference__orderitem__delivery_quantity')) \
        .annotate(origin_country_code=F('origin_country_id__code'))
    if not order_item:
        order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order_id=order_id) \
            .select_related('item_id', 'supplier_id').values() \
            .annotate(item_name=F('item__name')) \
            .annotate(supplier_code=F('supplier__code')) \
            .annotate(supplier_code_id=F('supplier')) \
            .annotate(quantity_do=F('quantity')).annotate(currency_id=F('to_currency')) \
            .annotate(original_currency=F('to_currency__code')) \
            .annotate(location_code=F('location__code')) \
            .annotate(location_id=F('location__id')) \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(ref_number=F('refer_number')) \
            .annotate(order_quantity=Value(0, output_field=models.CharField())) \
            .annotate(delivery_quantity=Value(0, output_field=models.CharField()))
    items_list = items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       item__customeritem__customer=customer.id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
        .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
        .values('item_id') \
        .annotate(code=F('item__code')) \
        .annotate(item_name=F('item__name')) \
        .annotate(ref_number=F('order__document_number')) \
        .annotate(ref_line=F('line_number')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(location_code=F('location__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(sales_price=F('price')) \
        .annotate(currency=F('order__customer__customeritem__currency__code')) \
        .annotate(location_id=F('location_id')) \
        .annotate(currency_id=F('order__customer__customeritem__currency')) \
        .annotate(line_id=Value(0, output_field=models.CharField())) \
        .annotate(uom=F('item__purchase_measure__name')) \
        .annotate(supplier_code_id=F('supplier'))

    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)
    try:
        order_header = order_header_list.filter(x_position=1, y_position=0).first()
    except OrderHeader.DoesNotExist:
        order_header = None
        # get all items of Order by Order_ID
    try:
        currency_symbol = Currency.objects.get(pk=order_DO.currency_id).symbol
    except Currency.DoesNotExist:
        currency_symbol = Currency.objects.none()
    countries_list = Country.objects.filter(is_hidden=0)
    # get label and value formset right
    extra_right = order_header_list.filter(x_position=1, y_position=1).values()
    # get label and value formset left
    extra_left = order_header_list.filter(x_position=0, y_position=1).values()
    # get label and value formset code
    extra_code = order_header_list.filter(x_position=1, y_position=2).values()
    # get order delivery info

    kwargs, contact = get_order_delivery_kwargs(company_id, customer.id, order_id)
    form_delivery = OrderDeliveryForm(company_id, request.POST, **kwargs)
    # form
    form_info = OrderInfoForm(company_id, order_type, request.POST)
    # formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(DOInvoiceForm)(partial(DOInvoiceForm, company.id)))

    newStockTrans = None

    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = OrderHeaderForm(request.POST)
                form_info = OrderInfoForm(company.id, order_type, request.POST)
                form_delivery = OrderDeliveryForm(company.id, request.POST, **kwargs)

                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    return render_to_response('order_DOInvoice.html',
                                              RequestContext(request, {'company': company, 'cus': customer,
                                                                       'media_url': s.MEDIA_URL, 'form': form,
                                                                       'order': order_DO,
                                                                       'form_info': form_info,
                                                                       'items_list': items_list,
                                                                       'countries_list': countries_list,
                                                                       'supplier_item': supplier_item,
                                                                       'order_type': order_type,
                                                                       'formset_right': formset_right,
                                                                       'currency_symbol': currency_symbol,
                                                                       'order_status': order_status,
                                                                       'formset_left': formset_left,
                                                                       'formset_item': formset_item,
                                                                       'formset_code': formset_code,
                                                                       'form_delivery': form_delivery,
                                                                       'contact': contact, 'is_send': is_send,
                                                                       'copy_id': 1,
                                                                       'request_method': request.method}))

                # order process
                order = Order()
                if form.is_valid() and formset_item.is_valid():
                    order.customer_id = request.POST.get('hdCustomerId')
                    order.debit_account_id = request.POST.get('debit_account')
                    order.credit_account_id = request.POST.get('credit_account')
                    order.document_date = request.POST.get('document_date')
                    # order.order_code = request.POST.get('order_code')
                    order.currency_id = request.POST.get('currency')
                    order.reference_number = order_DO.reference_number
                    order.order_type = order_type
                    if int(is_send) == 1:
                        if request.POST.get('document_date'):
                            order.document_number = generate_document_number(company_id,
                                                                             request.POST.get('document_date'),
                                                                             int(TRN_CODE_TYPE_DICT[
                                                                                 'Sales Number File']),
                                                                             request.POST.get('transaction_code'))
                        order.status = dict(ORDER_STATUS)['Sent']
                    else:
                        order.document_number = None
                        order.status = dict(ORDER_STATUS)['Draft']
                    order.order_code = order.document_number
                    if request.POST.get('invoice_date'):
                        order.invoice_date = request.POST.get('invoice_date')
                    if request.POST.get('delivery_date'):
                        order.delivery_date = request.POST.get('delivery_date')
                    if request.POST.get('tax'):
                        order.tax_id = request.POST.get('tax')
                    if request.POST.get('discount'):
                        order.discount = Decimal(request.POST.get('discount'))
                    order.subtotal = Decimal(request.POST.get('subtotal'))
                    order.total = Decimal(request.POST.get('total'))
                    order.tax_amount = Decimal(request.POST.get('tax_amount'))
                    order.balance = order.total
                    if request.POST.get('cost_center'):
                        order.cost_center_id = request.POST.get('cost_center')
                    if request.POST.get('note_customer'):
                        order.note = request.POST.get('note_customer')
                    if request.POST.get('note_internal'):
                        order.remark = request.POST.get('note_internal')
                    if request.POST.get('footer'):
                        order.footer = request.POST.get('footer')
                    order.create_date = datetime.datetime.today()
                    order.update_date = datetime.datetime.today()
                    order.update_by_id = request.user.id
                    order.is_hidden = False
                    order.company_id = company.id
                    if int(is_send) == 1:
                        order.status = dict(ORDER_STATUS)['Sent']
                    else:
                        order.status = dict(ORDER_STATUS)['Draft']
                    order = get_order_editable_data(order, request)
                    order.save()

                    if is_send == '1':
                        newStockTrans = create_stock_transaction(order, company_id,
                                                                 request.POST.get('transaction_code'))

                    if OrderHeaderForm(request.POST):
                        order_header = OrderHeader()
                        order_header.x_position = 1
                        order_header.y_position = 0
                        order_header.label = request.POST.get('label')
                        order_header.value = request.POST.get('value')
                        order_header.create_date = datetime.datetime.today()
                        order_header.update_date = datetime.datetime.today()
                        order_header.update_by_id = request.user.id
                        order_header.is_hidden = False
                        order_header.order_id = order.id
                        order_header.save()

                    if formset_right.is_valid():
                        for form in formset_right:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 1
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("order_DO_copy formset_right.errors: ", formset_right.errors)

                    if formset_left.is_valid():
                        for form in formset_left:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 0
                                order_header.y_position = 1
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("order_DO_copy formset_left.errors: ", formset_left.errors)

                    if formset_code.is_valid():
                        for form in formset_code:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 2
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("order_DO_copy formset_code.errors: ", formset_code.errors)

                    delivery_status = 0
                    reference_order = None
                    if formset_item.is_valid():
                        for form in formset_item:
                            try:
                                reference_order = Order.objects.get(pk=form.cleaned_data.get('ref_number'))
                            except Exception as e:
                                print(e)
                            order_item = OrderItem()
                            order_item.item_id = form.cleaned_data.get('item_id')
                            order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                            order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                            order_item.quantity = form.cleaned_data.get('quantity_do')
                            order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                            if form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
                                order_item.location_id = form.cleaned_data.get('location').id
                            if reference_order:
                                order_item.reference_id = reference_order.id
                            order_item.refer_number = form.cleaned_data.get('ref_number')
                            order_item.refer_line = form.cleaned_data.get('refer_line')
                            order_item.line_number = form.cleaned_data.get('line_number')
                            order_item.from_currency_id = form.cleaned_data.get('currency_id')
                            order_item.to_currency_id = request.POST.get('currency')
                            order_item.stock_quantity = form.cleaned_data.get('quantity')
                            order_item.delivery_quantity = form.cleaned_data.get('quantity')
                            order_item.price = form.cleaned_data.get('price')
                            order_item.amount = form.cleaned_data.get('amount')
                            order_item.origin_country_id = form.cleaned_data.get('origin_country_id')
                            order_item.carton_no = form.cleaned_data.get('carton_no')
                            order_item.carton_total = form.cleaned_data.get('carton_total')
                            order_item.pallet_no = form.cleaned_data.get('pallet_no')
                            order_item.net_weight = form.cleaned_data.get('net_weight')
                            order_item.m3_number = form.cleaned_data.get('m3_number')
                            order_item.create_date = datetime.datetime.today()
                            order_item.update_date = datetime.datetime.today()
                            order_item.update_by_id = request.user.id
                            order_item.is_hidden = False
                            order_item.order_id = order.id
                            order_item.save()

                            # Update Stock
                            if int(is_send) == 1:
                                newStockTrans.addItem(order_item)

                                if company.is_inventory:
                                    # update item & locationitem qty
                                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                        fail = True
                                        for upd_inv_log in update_inv_qty_log:
                                            messages.add_message(request, messages.ERROR,
                                                                 'ERROR: ' + upd_inv_log['log'],
                                                                 extra_tags=upd_inv_log['tag'])
                                        messages.add_message(request, messages.ERROR,
                                                             SEND_DOC_FAILED + REFRESH_OR_GO_GET_SUPPORT,
                                                             extra_tags='send_doc_failed')

                                # Update Delivery Quantity and Delivery Quantity
                                # of Reference Order ( Reference Order is Sales Order)
                                if reference_order is not None:
                                    if reference_order.id:
                                        refer_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                                    order__company_id=company_id,
                                                                                    order_id=reference_order.id,
                                                                                    item_id=form.cleaned_data.get(
                                                                                        'item_id'),
                                                                                    line_number=form.cleaned_data.get(
                                                                                        'refer_line')).first()
                                        if refer_order_item:
                                            refer_order_item.stock_quantity = float(
                                                refer_order_item.stock_quantity) - float(order_item.quantity)
                                            refer_order_item.delivery_quantity = float(
                                                refer_order_item.delivery_quantity) + float(order_item.quantity)
                                            refer_order_item.update_date = datetime.datetime.today()
                                            refer_order_item.update_by_id = staff.id
                                            refer_order_item.save()

                        # Change order status base on delivery quantity
                        if int(is_send) == 1 and reference_order is not None:
                            if delivery_status > 0:
                                reference_order.status = dict(ORDER_STATUS)['Partial']
                            else:
                                reference_order.status = dict(ORDER_STATUS)['Delivered']
                            order.save()
                    else:
                        print("order_DO_copy formset_item.errors: ", formset_item.errors)

                    # Order Delivery process
                    if form_delivery.is_valid():
                        order_delivery = form_delivery.save(commit=False)
                        order_delivery.order_id = order.id
                        order_delivery.create_date = datetime.datetime.today()
                        order_delivery.update_date = datetime.datetime.today()
                        order_delivery.update_by_id = request.user.id
                        order_delivery.is_hidden = 0
                        if not request.POST.get('delivery'):
                            order_delivery.contact_id = request.POST.get('contact_id') if request.POST.get(
                                'contact_id') else None
                            order_delivery.delivery_id = None
                        else:
                            order_delivery.contact_id = None
                            order_delivery.delivery_id = request.POST.get('delivery') if request.POST.get(
                                'delivery') else None
                        order_delivery.save()
                    else:
                        print("order_DO_copy form_delivery.errors: ", form_delivery.errors)

                    if int(is_send) == 1:
                        newStockTrans.generate()
                else:
                    print("order_DO_copy form.errors, formset_item.errors: ", form.errors, formset_item.errors)

            if int(is_send) == 1:
                cont = True
                wish_doc_no = order.document_number
                while cont:
                    # check one more time
                    check_order_count = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                             document_number=wish_doc_no).count()
                    if check_order_count > 1:
                        doc_no = order.document_number.split('-')
                        postfix = int(doc_no[-1]) + 1
                        wish_doc_no = doc_no[0] + '-' + doc_no[1] + '-' + '{:05}'.format(postfix % 100000)
                        order.document_number = wish_doc_no
                        order.save()
                    else:
                        cont = False
            return HttpResponseRedirect('/orders/list/' + order_type + '/')
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='order_DO_copy')

    # end if POST

    form = OrderHeaderForm(instance=order_header)
    form_info = OrderInfoForm(company_id, order_type, instance=order_DO)
    form_delivery = OrderDeliveryForm(company_id, **kwargs)

    # load formset values
    formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
    formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
    formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
    formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)

    return render_to_response('order_DOInvoice.html', RequestContext(request, {'company': company, 'cus': customer,
                                                                               'media_url': s.MEDIA_URL, 'form': form,
                                                                               'order': order_DO,
                                                                               'form_info': form_info,
                                                                               'items_list': items_list,
                                                                               'countries_list': countries_list,
                                                                               'supplier_item': supplier_item,
                                                                               'order_type': order_type,
                                                                               'formset_right': formset_right,
                                                                               'currency_symbol': currency_symbol,
                                                                               'order_status': order_status,
                                                                               'formset_left': formset_left,
                                                                               'formset_item': formset_item,
                                                                               'formset_code': formset_code,
                                                                               'form_delivery': form_delivery,
                                                                               'contact': contact, 'is_send': is_send,
                                                                               'copy_id': 1,
                                                                               'request_method': request.method,
                                                                               'distribution_code_list': distribution_code_list}))


@login_required
@csrf_exempt
def DOInvoice_item_search(request, customer_id, search_condition):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        exclude_item_json = request.POST.get('exclude_item_list')
        if search_condition == '0':
            items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  item__customeritem__customer=customer_id,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                annotate(code=F('item__code')). \
                annotate(item_name=F('item__name')). \
                annotate(ref_number=F('order__document_number')). \
                annotate(ref_line=F('line_number')). \
                annotate(supplier_code=F('supplier__code')). \
                annotate(location_code=F('location__code')). \
                annotate(category=F('item__category__code')). \
                annotate(sales_price=F('price')). \
                annotate(currency=F('order__customer__currency__code')). \
                annotate(location_id=F('location_id')). \
                annotate(currency_id=F('order__customer__currency')). \
                annotate(uom=F('item__purchase_measure__name')). \
                annotate(supplier_code_id=F('supplier')). \
                annotate(order_quantity=F('quantity')). \
                annotate(delivery_quantity=F('delivery_quantity')). \
                annotate(customer_po_no=F('customer_po_no')). \
                annotate(line_id=Value(0, output_field=models.CharField()))
            for i, j in enumerate(items_list):
                if items_list.__len__() > i:
                    i += 1
                    j['line_id'] = i
        else:
            if exclude_item_json:
                exclude_item_list = json.loads(exclude_item_json)
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__customer_id=customer_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
                    .filter(Q(item__name__contains=search_condition) |
                            Q(item__code__contains=search_condition) |
                            Q(order__document_number__contains=search_condition) |
                            Q(supplier__code__contains=search_condition) |
                            Q(location__code__contains=search_condition)). \
                    exclude(item_id__in=exclude_item_list, order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                    annotate(code=F('item__code')). \
                    annotate(item_name=F('item__name')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(sales_price=F('price')). \
                    annotate(currency=F('order__customer__currency__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(currency_id=F('order__customer__currency')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(supplier_code_id=F('supplier')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(delivery_quantity=F('delivery_quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))
            else:
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      item__customeritem__customer=customer_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
                    .filter(Q(item__name__contains=search_condition) |
                            Q(item__code__contains=search_condition) |
                            Q(order__document_number__contains=search_condition) |
                            Q(supplier__code__contains=search_condition) |
                            Q(location__code__contains=search_condition)). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                    annotate(code=F('item__code')). \
                    annotate(item_name=F('item__name')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(sales_price=F('price')). \
                    annotate(currency=F('order__customer__currency__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(currency_id=F('order__customer__currency')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(supplier_code_id=F('supplier')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(delivery_quantity=F('delivery_quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))

            for i, j in enumerate(items_list):
                if items_list.__len__() > i:
                    i += 1
                    j['line_id'] = i

        item_list_json = json.dumps(list(items_list), cls=DjangoJSONEncoder)
        return HttpResponse(item_list_json, content_type="application/json")


@login_required
@check_inventory_closing
@check_sp_closing
def generate_DO_invoice(request, order_id, is_generate, is_send):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    order = Order.objects.get(pk=order_id)
    order_status = order.status

    order_type = dict(ORDER_TYPE)['SALES INVOICE']
    company = Company.objects.get(pk=order.company_id)
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id).first()
    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                supplier__company_id=company_id, supplier__is_hidden=0)
    try:
        customer = Customer.objects.get(pk=order.customer_id)
    except Customer.DoesNotExist:
        messages.add_message(request, messages.ERROR, "suppliers", extra_tags='order_new_empty_supplier')
        return HttpResponseRedirect(reverse('order_list', args=(), kwargs={'order_type': order_type}))
    order_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                           order_id=order_id).select_related('item_id', 'supplier_id') \
        .values(). \
        exclude(quantity=F('delivery_quantity')). \
        annotate(item_name=F('item__name')). \
        annotate(customer_po_no=F('customer_po_no')). \
        annotate(quantity_do=Sum((F('quantity') - F('delivery_quantity')))). \
        annotate(supplier_code=F('supplier__code')). \
        annotate(supplier_code_id=F('supplier')). \
        annotate(currency_id=F('to_currency')). \
        annotate(original_currency=F('to_currency__code')). \
        annotate(location=F('location_id')). \
        annotate(uom=F('item__sales_measure__name')). \
        annotate(code=F('item__code')). \
        annotate(category=F('item__category__code')). \
        annotate(ref_number=F('order__document_number')). \
        annotate(refer_line=F('line_number')). \
        annotate(order_quantity=F('quantity')). \
        annotate(delivery_quantity=F('delivery_quantity'))

    items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          item__customeritem__customer=customer.id,
                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
        exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
        annotate(code=F('item__code')).annotate(item_name=F('item__name')). \
        annotate(ref_number=F('order__document_number')). \
        annotate(ref_line=F('line_number')). \
        annotate(supplier_code=F('supplier__code')). \
        annotate(location_code=F('location__code')). \
        annotate(category=F('item__category__code')). \
        annotate(sales_price=F('price')). \
        annotate(currency=F('order__customer__customeritem__currency__code')). \
        annotate(location_id=F('location_id')). \
        annotate(currency_id=F('order__customer__customeritem__currency')). \
        annotate(line_id=Value(0, output_field=models.CharField())). \
        annotate(uom=F('item__purchase_measure__name')). \
        annotate(supplier_code_id=F('supplier')). \
        annotate(order_quantity=F('quantity')). \
        annotate(delivery_quantity=F('delivery_quantity')). \
        annotate(line_id=Value(0, output_field=models.CharField()))
    for i, j in enumerate(items_list):
        if (i < items_list.__len__()):
            i += 1
            j['line_id'] = i

    order_header_list = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)
    try:
        order_header = order_header_list.filter(x_position=1, y_position=0).first()
    except OrderHeader.DoesNotExist:
        order_header = None
        # get all items of Order by Order_ID
    try:
        currency_symbol = Currency.objects.get(pk=order.currency_id).symbol
    except Currency.DoesNotExist:
        currency_symbol = Currency.objects.none()
    countries_list = Country.objects.filter(is_hidden=0)
    # get label and value formset right
    extra_right = order_header_list.filter(x_position=1, y_position=1).values()
    # get label and value formset left
    extra_left = order_header_list.filter(x_position=0, y_position=1).values()
    # get label and value formset code
    extra_code = order_header_list.filter(x_position=1, y_position=2).values()
    # get order delivery info
    kwargs, contact = get_order_delivery_kwargs(company_id, customer.id, order_id)
    form_delivery = OrderDeliveryForm(company_id, request.POST, **kwargs)
    # form
    form_info = OrderInfoForm(company_id, order_type, request.POST)
    # formset
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    array_id_items = []

    for get_items in order_items:
        array_id_items.append(get_items['item_id'])
    array_loc = []
    for itm_id in array_id_items:
        get_location_id = LocationItem.objects.filter(is_hidden=0, item_id=itm_id) \
            .values_list('location_id', flat=True).distinct()
        array_loc.append(get_location_id)
    ItemFormSet = formset_factory(wraps(DOInvoiceForm)(partial(DOInvoiceForm, company.id)))

    newStockTrans = None

    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = OrderHeaderForm(request.POST)
                form_info = OrderInfoForm(company.id, order_type, request.POST)
                form_delivery = OrderDeliveryForm(company.id, request.POST, **kwargs)

                formset_right = ExtraValueFormSetRight(request.POST, prefix='formset_right')
                formset_left = ExtraValueFormSetLeft(request.POST, prefix='formset_left')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')

                if ('is_inventory_locked' in request.session and request.session['is_inventory_locked']) or \
                        ('is_sp_locked' in request.session and request.session['is_sp_locked']):
                    return render_to_response('generate_DO_invoice.html', RequestContext(request,
                                                                                         {'company': company,
                                                                                          'media_url': s.MEDIA_URL,
                                                                                          'form': form,
                                                                                          'form_info': form_info,
                                                                                          'items_list': items_list,
                                                                                          'countries_list': countries_list,
                                                                                          'supplier_item': supplier_item,
                                                                                          'order_type': order_type,
                                                                                          'formset_right': formset_right,
                                                                                          'contact': contact,
                                                                                          'currency_symbol': currency_symbol,
                                                                                          'is_generate': is_generate,
                                                                                          'order_status': order_status,
                                                                                          'formset_left': formset_left,
                                                                                          'formset_item': formset_item,
                                                                                          'form_delivery': form_delivery,
                                                                                          'cus': customer,
                                                                                          'order': order,
                                                                                          'formset_code': formset_code,
                                                                                          'request_method': request.method}))

                # order process
                order_DO_invoice = Order()
                if form.is_valid() and form_info.is_valid() and formset_item.is_valid():
                    order_DO_invoice.customer_id = request.POST.get('hdCustomerId')
                    order_DO_invoice.debit_account_id = request.POST.get('debit_account')
                    order_DO_invoice.credit_account_id = request.POST.get('credit_account')
                    order_DO_invoice.document_date = request.POST.get('document_date')
                    # order_DO_invoice.order_code = request.POST.get('order_code')
                    order_DO_invoice.currency_id = request.POST.get('currency')
                    order_DO_invoice.reference_number = order.document_number
                    if int(is_send) == 1:
                        if request.POST.get('document_date'):
                            order_DO_invoice.document_number = generate_document_number(
                                company_id,
                                request.POST.get('document_date'),
                                int(TRN_CODE_TYPE_DICT['Sales Number File']),
                                request.POST.get('transaction_code'))
                        order_DO_invoice.status = dict(ORDER_STATUS)['Sent']
                    else:
                        order_DO_invoice.document_number = None
                        order_DO_invoice.status = dict(ORDER_STATUS)['Draft']
                    order_DO_invoice.order_code = order_DO_invoice.document_number
                    if request.POST.get('invoice_date'):
                        order_DO_invoice.invoice_date = datetime.datetime.today()
                    if request.POST.get('delivery_date'):
                        order_DO_invoice.delivery_date = datetime.datetime.today()
                    if request.POST.get('tax'):
                        order_DO_invoice.tax_id = request.POST.get('tax')
                    if request.POST.get('discount'):
                        order_DO_invoice.discount = Decimal(request.POST.get('discount'))
                    order_DO_invoice.subtotal = Decimal(request.POST.get('subtotal'))
                    order_DO_invoice.total = Decimal(request.POST.get('total'))
                    order_DO_invoice.tax_amount = Decimal(request.POST.get('tax_amount'))
                    order_DO_invoice.balance = order.total
                    if request.POST.get('cost_center'):
                        order_DO_invoice.cost_center_id = request.POST.get('cost_center')
                    if request.POST.get('note_customer'):
                        order_DO_invoice.note = request.POST.get('note_customer')
                    if request.POST.get('note_internal'):
                        order_DO_invoice.remark = request.POST.get('note_internal')
                    if request.POST.get('footer'):
                        order_DO_invoice.footer = request.POST.get('footer')
                    order_DO_invoice.order_type = order_type
                    order_DO_invoice.create_date = datetime.datetime.today()
                    order_DO_invoice.update_date = datetime.datetime.today()
                    order_DO_invoice.update_by_id = request.user.id
                    order_DO_invoice.is_hidden = False
                    order_DO_invoice.company_id = company_id
                    if int(is_send) == 1:
                        order_DO_invoice.status = dict(ORDER_STATUS)['Sent']
                    else:
                        order_DO_invoice.status = dict(ORDER_STATUS)['Draft']
                    order_DO_invoice.save()

                    if int(is_send) == 1:
                        newStockTrans = create_stock_transaction(order_DO_invoice, company_id,
                                                                 request.POST.get('transaction_code'))

                    if OrderHeaderForm(request.POST):
                        order_header = OrderHeader()
                        order_header.x_position = 1
                        order_header.y_position = 0
                        order_header.label = request.POST.get('label')
                        order_header.value = request.POST.get('value')
                        order_header.create_date = datetime.datetime.today()
                        order_header.update_date = datetime.datetime.today()
                        order_header.update_by_id = request.user.id
                        order_header.is_hidden = False
                        order_header.order_id = order_DO_invoice.id
                        order_header.save()

                    if formset_right.is_valid():
                        for form in formset_right:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 1
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order_DO_invoice.id
                                order_header.save()
                    else:
                        print("DOInvoice_item_search formset_right.errors: ", formset_right.errors)

                    if formset_left.is_valid():
                        for form in formset_left:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 0
                                order_header.y_position = 1
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order_DO_invoice.id
                                order_header.save()
                    else:
                        print("DOInvoice_item_search formset_left.errors: ", formset_left.errors)

                    if formset_code.is_valid():
                        for form in formset_code:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 2
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order_DO_invoice.id
                                order_header.save()
                    else:
                        print("DOInvoice_item_search formset_code.errors: ", formset_code.errors)

                    delivery_status = 0
                    if formset_item.is_valid():
                        stt = 0
                        for form in formset_item:
                            order_item = OrderItem()
                            order_item.item_id = form.cleaned_data.get('item_id')
                            order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                            order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                            order_item.quantity = form.cleaned_data.get('quantity_do')
                            order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                            if form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
                                order_item.location_id = form.cleaned_data.get('location').id
                            order_item.reference_id = order.id
                            order_item.refer_number = form.cleaned_data.get('ref_number')
                            order_item.refer_line = form.cleaned_data.get('refer_line')
                            stt += 1
                            order_item.line_number = stt
                            order_item.from_currency_id = form.cleaned_data.get('currency_id')
                            order_item.to_currency_id = request.POST.get('currency')
                            order_item.stock_quantity = form.cleaned_data.get('order_quantity')
                            order_item.delivery_quantity = form.cleaned_data.get('delivery_quantity')
                            order_item.price = form.cleaned_data.get('price')
                            order_item.amount = form.cleaned_data.get('amount')
                            order_item.origin_country_id = form.cleaned_data.get('origin_country_id')
                            order_item.carton_no = form.cleaned_data.get('carton_no')
                            order_item.carton_total = form.cleaned_data.get('carton_total')
                            order_item.pallet_no = form.cleaned_data.get('pallet_no')
                            order_item.net_weight = form.cleaned_data.get('net_weight')
                            order_item.m3_number = form.cleaned_data.get('m3_number')
                            order_item.create_date = datetime.datetime.today()
                            order_item.update_date = datetime.datetime.today()
                            order_item.update_by_id = request.user.id
                            order_item.is_hidden = False
                            order_item.order_id = order_DO_invoice.id
                            order_item.save()

                            # Update Stock
                            if int(is_send) == 1:
                                newStockTrans.addItem(order_item)

                                if company.is_inventory:
                                    # update item & locationitem qty
                                    update_inv_qty_log = push_doc_qty_to_inv_qty(request, order_item.id)
                                    if update_inv_qty_log and len(update_inv_qty_log) > 0:
                                        fail = True
                                        for upd_inv_log in update_inv_qty_log:
                                            messages.add_message(request, messages.ERROR,
                                                                 'ERROR: ' + upd_inv_log['log'],
                                                                 extra_tags=upd_inv_log['tag'])
                                        messages.add_message(request, messages.ERROR,
                                                             SEND_DOC_FAILED + REFRESH_OR_GO_GET_SUPPORT,
                                                             extra_tags='send_doc_failed')

                                # Update Delivery Quantity and Delivery Quantity
                                # of Reference Order ( Reference Order is Sales Order)
                                if order.id:
                                    refer_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                                order__company_id=company_id,
                                                                                order_id=order.id,
                                                                                item_id=form.cleaned_data.get(
                                                                                    'item_id'),
                                                                                line_number=form.cleaned_data.get(
                                                                                    'refer_line')).first()
                                    if refer_order_item:
                                        refer_order_item.delivery_quantity = float(
                                            refer_order_item.delivery_quantity) + float(order_item.quantity)
                                        refer_order_item.update_date = datetime.datetime.today()
                                        refer_order_item.update_by_id = staff.id
                                        refer_order_item.last_delivery_date = datetime.datetime.today()
                                        refer_order_item.save()

                        # Change order status base on delivery quantity
                        if int(is_send) == 1:
                            so_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                     order__company_id=company_id,
                                                                     order_id=order.id)
                            for i in so_order_item:
                                if i.delivery_quantity < i.quantity:
                                    delivery_status += 1
                            if delivery_status > 0:
                                order.status = dict(ORDER_STATUS)['Partial']
                            else:
                                order.status = dict(ORDER_STATUS)['Delivered']
                            order.save()
                    else:
                        print("DOInvoice_item_search formset_item.errors: ", formset_item.errors)

                    # Order Delivery process
                    if form_delivery.is_valid():
                        order_delivery = form_delivery.save(commit=False)
                        order_delivery.order_id = order_DO_invoice.id
                        order_delivery.create_date = datetime.datetime.today()
                        order_delivery.update_date = datetime.datetime.today()
                        order_delivery.update_by_id = request.user.id
                        order_delivery.is_hidden = 0
                        order_delivery.save()
                    else:
                        print("DOInvoice_item_search form_delivery.errors: ", form_delivery.errors)

                    if int(is_send) == 1:
                        newStockTrans.generate()
                else:
                    print("generate_DO_invoice form.errors, form_info.errors, formset_item.errors: ", form.errors,
                          form_info.errors, formset_item.errors)

            if int(is_send) == 1:
                cont = True
                wish_doc_no = order_DO_invoice.document_number
                while cont:
                    # check one more time
                    check_order_count = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                             document_number=wish_doc_no).count()
                    if check_order_count > 1:
                        doc_no = order_DO_invoice.document_number.split('-')
                        postfix = int(doc_no[-1]) + 1
                        wish_doc_no = doc_no[0] + '-' + doc_no[1] + '-' + '{:05}'.format(postfix % 100000)
                        order_DO_invoice.document_number = wish_doc_no
                        order_DO_invoice.save()
                    else:
                        cont = False
            return HttpResponseRedirect('/orders/list/' + str(order_type) + '/')
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='generate_DO_invoice')

    # end if POST
    form = OrderHeaderForm(instance=order_header)
    form_info = OrderInfoForm(company_id, order_type, instance=order)
    form_info.initial['document_number'] = None
    form_delivery = OrderDeliveryForm(company_id, **kwargs)
    # load formset values
    formset_right = ExtraValueFormSetRight(prefix='formset_right', initial=extra_right)
    formset_left = ExtraValueFormSetLeft(prefix='formset_left', initial=extra_left)
    formset_item = ItemFormSet(prefix='formset_item', initial=order_items)
    formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)

    for i, itemForm in enumerate(formset_item.forms):
        for loc_id in array_loc:
            formset_item.forms[i].fields['location'].queryset = Location.objects.filter(is_hidden=0, is_active=1,
                                                                                        company_id=company_id,
                                                                                        id__in=loc_id)

    return render_to_response('generate_DO_invoice.html', RequestContext(request,
                                                                         {'company': company, 'media_url': s.MEDIA_URL,
                                                                          'form': form, 'form_info': form_info,
                                                                          'items_list': items_list,
                                                                          'countries_list': countries_list,
                                                                          'supplier_item': supplier_item,
                                                                          'order_type': order_type,
                                                                          'formset_right': formset_right,
                                                                          'contact': contact,
                                                                          'currency_symbol': currency_symbol,
                                                                          'is_generate': is_generate,
                                                                          'order_status': order_status,
                                                                          'formset_left': formset_left,
                                                                          'formset_item': formset_item,
                                                                          'form_delivery': form_delivery,
                                                                          'cus': customer, 'order': order,
                                                                          'formset_code': formset_code,
                                                                          'request_method': request.method}))


def get_cust_supp_name(order_type, field):
    if order_type in [dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['SALES INVOICE'],
                      dict(ORDER_TYPE)['SALES DEBIT NOTE'], dict(ORDER_TYPE)['SALES CREDIT NOTE']]:
        if field.customer and field.customer.name:
            return field.customer.name
    elif order_type in [dict(ORDER_TYPE)['PURCHASE ORDER'], dict(ORDER_TYPE)['PURCHASE INVOICE'],
                        dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'], dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']]:
        if field.supplier and field.supplier.name:
            return field.supplier.name
    else:
        return ''


def get_cust_supp_column_name(order_type):
    if order_type in [dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['SALES INVOICE'],
                      dict(ORDER_TYPE)['SALES DEBIT NOTE'], dict(ORDER_TYPE)['SALES CREDIT NOTE']]:
        return "customer__name"
    elif order_type in [dict(ORDER_TYPE)['PURCHASE ORDER'], dict(ORDER_TYPE)['PURCHASE INVOICE'],
                        dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'], dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']]:
        return "supplier__name"
    else:
        return ''


@login_required
def OrderList__asJson(request, order_type):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if int(order_type) in [dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'], dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']]:
        # purchase debit/credit note
        order_list = Order.objects.filter(is_hidden=0, company_id=company_id) \
            .filter(Q(order_type=dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']) |
                    Q(order_type=dict(ORDER_TYPE)['PURCHASE CREDIT NOTE'])).order_by('-document_number')
    elif int(order_type) in [dict(ORDER_TYPE)['SALES DEBIT NOTE'], dict(ORDER_TYPE)['SALES CREDIT NOTE']]:
        # sale credit/debit note
        order_list = Order.objects.filter(is_hidden=0, company_id=company_id) \
            .filter(Q(order_type=dict(ORDER_TYPE)['SALES DEBIT NOTE']) |
                    Q(order_type=dict(ORDER_TYPE)['SALES CREDIT NOTE'])).order_by('-document_number')
    elif int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
        order_list = Order.objects.filter(is_hidden=0, company_id=company_id, order_type=order_type).order_by('-document_date')
    else:
        order_list = Order.objects.filter(is_hidden=0, company_id=company_id, order_type=order_type).order_by('-document_number')

    records_total = order_list.count()

    if search:  # Filter data base on search
        if int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
            order_list = order_list.filter(Q(update_date__icontains=search) | Q(document_date__icontains=search) | Q(
                document_number__icontains=search) | Q(update_date__contains=search) | Q(
                customer__name__icontains=search) | Q(supplier__name__icontains=search) | Q(balance__icontains=search) | Q(
                reference_number__icontains=search) | Q(total__icontains=search)).order_by('-document_date')
        else:
            order_list = order_list.filter(Q(update_date__icontains=search) | Q(document_date__icontains=search) | Q(
                document_number__icontains=search) | Q(update_date__contains=search) | Q(
                customer__name__icontains=search) | Q(supplier__name__icontains=search) | Q(balance__icontains=search) | Q(
                reference_number__icontains=search) | Q(total__icontains=search)).order_by('-document_number')

    # All data
    records_filtered = order_list.count()
    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    column_name = ""
    if order_column == "1":
        column_name = "update_date"
    elif order_column == "2":
        column_name = "id"
    elif order_column == "3":
        column_name = "document_date"
    elif order_column == "4":
        column_name = "document_number"
    elif order_column == "5":
        column_name = "reference_number"
    elif order_column == "6":
        column_name = get_cust_supp_column_name(int(order_type))
    elif order_column == "7":
        column_name = "total"
    elif order_column == "8":
        column_name = "status"

    order_dir = request.GET['order[0][dir]']
    list = []
    if order_dir == "asc":
        if int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
            list = order_list.order_by('document_date', column_name)[int(start):(int(start) + int(length))]
        else:
            list = order_list.order_by('document_number', column_name)[int(start):(int(start) + int(length))]
    elif order_dir == "desc":
        if int(order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
            list = order_list.order_by('-document_date', '-' + column_name)[int(start):(int(start) + int(length))]
        else:
            list = order_list.order_by('-document_number', '-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        curr = field.currency.code if field.currency else ''
        money = field.total
        # money = round((field.total, field.subtotal)[int(order_type) == dict(ORDER_TYPE)['SALES ORDER'] or
        #                                             int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']], 6)
        if int(order_type) == dict(ORDER_TYPE)['SALES ORDER'] or int(order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
            money = OrderItem.objects.filter(is_hidden=0, order_id=field.id) \
                    .aggregate(total=Sum('amount'))['total']
        else:
            money = field.total
        if not money:
            money = 0.0
        if field.currency.is_decimal:
            separator = intcomma("%.2f" % money)
        else:
            separator = intcomma("%.0f" % money)
        format_money = str(curr + ' ' + separator)

        data = {"id": str(field.id),
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "document_date": field.document_date.strftime("%d-%m-%Y"),
                "document_number": field.document_number,
                "reference_number": field.reference_number,
                "cust_supp_name": get_cust_supp_name(int(order_type), field),
                "total": format_money,
                "status": str(field.status)}
        array.append(data)

    content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def do_by_so_as_json(request, customer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if customer_id == '0':
        items_list0 = OrderItem.objects.none()
    else:
        items_list0 = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__customer_id=customer_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            exclude(order__status=dict(ORDER_STATUS)['Delivered']). \
            exclude(quantity__lte=F('delivery_quantity')).values('order_id', 'item_id', 'location_id', 'order__document_number', 'quantity', 'delivery_quantity')

    items_list = items_list0.order_by('-order__document_number').distinct()
    records_total = items_list.count()
    array = []

    last_doc = ''
    for field in items_list:
        # if company.is_inventory:
        #     location_item_quantity = 0
        #     try:
        #         loc_item = LocationItem.objects. \
        #             filter(item_id=field['item_id'],
        #                     location__company_id=company_id,
        #                     location_id=field['location_id'],
        #                     is_hidden=False,
        #                     location__is_hidden=False)
        #         if loc_item:
        #             loc_item = loc_item.aggregate(sum_onhand_qty=Coalesce(Sum('onhand_qty'), V(0)))
        #             location_item_quantity = loc_item.get('sum_onhand_qty')
        #             if location_item_quantity <= 0:
        #                 loc_itms = LocationItem.objects. \
        #                                 filter(item_id=field['item_id'],
        #                                         is_hidden=False,
        #                                         location__is_hidden=False).exclude(location_id=field['location_id']).order_by('location_id')
        #                 if loc_itms.exists():
        #                     for loc_item in loc_itms:
        #                         if loc_item.onhand_qty:
        #                             location_item_quantity = loc_item.onhand_qty
        #                             break
        #         else:
        #             qty_gr = 0
        #             po_list = order_vs_inventory(request).get_next_doc_detail(field['item_id'])
        #             if po_list:
        #                 for po in po_list:
        #                     gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
        #                     if gr_list:
        #                         for gr in gr_list:
        #                             qty_gr += gr.quantity
        #             location_item_quantity = qty_gr

        #     except Exception as e:
        #         print(e)

        #     if location_item_quantity <= 0:
        #         continue

        if last_doc != str(field['order__document_number']):
            order__document_number = str(field['order__document_number'])
            data = {}
            data["order_id"] = str(field['order_id'])
            data["refer_number"] = order__document_number if order__document_number != 'None' and order__document_number else ''

            array.append(data)
        
        last_doc = str(field['order__document_number'])

    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def do_by_all_so_as_json(request, customer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if customer_id == '0':
        items_list = OrderItem.objects.none()
    else:
        items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__customer_id=customer_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            exclude(order__status=dict(ORDER_STATUS)['Delivered']). \
            exclude(quantity__lte=F('delivery_quantity')).order_by('-order_id', 'line_number'). \
            values('order_id', 'order__document_number', 'line_number')

    array = []
    for item in items_list:
        data = {}
        data['ref_id'] = str(item['order_id'])
        data['refer_number'] = str(item['order__document_number'])
        data['refer_line'] = str(item['line_number'])
        array.append(data)

    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def po_by_so_as_json(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    # company = Company.objects.get(pk=company_id)
    if supplier_id == '0':
        items_list0 = OrderItem.objects.none()
    else:
        # so_items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
        #                                          supplier_id=supplier_id,
        #                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
        #     exclude(order__status=dict(ORDER_STATUS)['Draft']). \
        #     exclude(order__status=dict(ORDER_STATUS)['Delivered']). \
        #     exclude(quantity__lte=F('delivery_quantity')). \
        #     order_by('order_id', 'line_number'). \
        #     values('order_id', 'line_number', 'quantity').distinct()

        exclude_so_list = []
        # po_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
        #                                            order__supplier_id=supplier_id,
        #                                            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])
        # for so in so_items_list:
        #     po_item_qty = po_items.filter(reference_id=so['order_id'], refer_line=so['line_number']) \
        #         .aggregate(quantity=Sum('quantity'))['quantity']
        #
        #     if po_item_qty and po_item_qty >= so['quantity']:
        #         if not so['order_id'] in exclude_so_list:
        #             exclude_so_list.append(so['order_id'])
        #     else:
        #         if so['order_id'] in exclude_so_list:
        #             exclude_so_list.remove(so['order_id'])

        items_list0 = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               supplier_id=supplier_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
            exclude(order_id__in=exclude_so_list). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            values('order_id', 'order__document_number')
            # exclude(order__status=dict(ORDER_STATUS)['Delivered']). \
            # exclude(quantity__lte=F('delivery_quantity'))\

    items_list = items_list0.order_by('-order__document_number').distinct()
    array = []

    for field in items_list:
        order__document_number = str(field['order__document_number'])
        data = {}
        data["order_id"] = str(field['order_id'])
        data["refer_number"] = order__document_number if order__document_number != 'None' and order__document_number else ''
        array.append(data)

    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')

@login_required
def po_by_so_all_data_json(request, supplier_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if supplier_id == '0':
        items_list = OrderItem.objects.none()
    else:
        exclude_so_list = []
        items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               supplier_id=supplier_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
            exclude(order_id__in=exclude_so_list). \
            exclude(order__status=dict(ORDER_STATUS)['Draft']). \
            order_by('-order_id', 'line_number'). \
            values('order_id', 'order__document_number', 'line_number')

    array = []
    for item in items_list:
        data = {}
        data['ref_id'] = str(item['order_id'])
        data['refer_number'] = str(item['order__document_number'])
        data['refer_line'] = str(item['line_number'])
        array.append(data)

    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def do_invoice_item_list_as_json(request):
    if request.is_ajax():
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        customer_id = request.GET['customer_id']

        if customer_id == '0':
            items_list = OrderItem.objects.none()
        else:
            if 'exclude_item_list' in request.GET:
                exclude_item_json = request.GET['exclude_item_list']
                exclude_item_list = json.loads(exclude_item_json)
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__customer_id=customer_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                    exclude(item_id__in=exclude_item_list).exclude(order__status=dict(ORDER_STATUS)['Draft']). \
                    exclude(quantity__lte=F('delivery_quantity')).values('item_id'). \
                    annotate(code=F('item__code')). \
                    annotate(item_name=F('item__name')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(sales_price=F('price')). \
                    annotate(currency_code=F('order__customer__currency__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(currency_id=F('order__customer__currency')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(delivery_quantity=F('delivery_quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(stock_quantity=F('item__quantity')). \
                    annotate(location_item_quantity=F('item__locationitem__onhand_qty')). \
                    annotate(country_origin_id=F('item__country_id')). \
                    annotate(country_origin_cd=F('item__country__code')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))
            else:
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__customer_id=customer_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']). \
                    exclude(quantity__lte=F('delivery_quantity')).values('item_id'). \
                    annotate(code=F('item__code')). \
                    annotate(item_name=F('item__name')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(sales_price=F('price')). \
                    annotate(currency_code=F('order__customer__currency__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(currency_id=F('order__customer__currency')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(delivery_quantity=F('delivery_quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(stock_quantity=F('item__quantity')). \
                    annotate(location_item_quantity=F('item__locationitem__onhand_qty')). \
                    annotate(country_origin_id=F('item__country_id')). \
                    annotate(country_origin_cd=F('item__country__code')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))

        records_total = items_list.count()

        if search:  # Filter data base on search
            items_list = items_list.filter(Q(item__name__icontains=search) | Q(item__code__icontains=search) | Q(
                order__document_number__icontains=search) | Q(supplier__code__icontains=search) | Q(
                location__code__icontains=search))

        # All data
        records_filtered = items_list.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "1":
            column_name = "item__code"
        elif order_column == "2":
            column_name = "item__name"
        elif order_column == "3":
            column_name = "order__document_number"
        elif order_column == "4":
            column_name = "line_number"
        elif order_column == "5":
            column_name = "supplier__code"
        elif order_column == "6":
            column_name = "location__code"
        elif order_column == "7":
            column_name = "item__category__code"
        elif order_column == "8":
            column_name = "price"
        elif order_column == "9":
            column_name = "order__customer__currency"
        elif order_column == "15":
            column_name = "quantity"
        elif order_column == "16":
            column_name = "delivery_quantity"
        elif order_column == "17":
            column_name = "customer_po_no"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = items_list.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = items_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        for i, j in enumerate(list):
            if (i < list.__len__()):
                i += 1
                j['line_id'] = i

        # Create data list
        array = []
        for field in list:
            data = {}
            data["item_id"] = str(field['item_id'])
            if str(field['item_name']) != 'None' and str(field['item_name']):
                data["item_name"] = str(field['item_name'])
            else:
                data["item_name"] = ''
            if str(field['supplier_code']) != 'None' and str(field['supplier_code']):
                data["supplier_code"] = str(field['supplier_code'])
            else:
                data["supplier_code"] = ''
            if str(field['ref_number']) != 'None' and str(field['ref_number']):
                data["refer_number"] = str(field['ref_number'])
            else:
                data["refer_number"] = ''
            data["refer_line"] = str(field['ref_line'])
            if str(field['location_code']) != 'None' and str(field['location_code']):
                data["location_code"] = str(field['location_code'])
            else:
                data["location_code"] = ''
            if str(field['code']) != 'None' and str(field['code']):
                data["code"] = str(field['code'])
            else:
                data["code"] = ''
            if str(field['category']) != 'None' and str(field['category']):
                data["category"] = str(field['category'])
            else:
                data["category"] = ''
            if str(field['sales_price']) != 'None' and str(field['sales_price']):
                data["sales_price"] = str(field['sales_price'])
            else:
                data["sales_price"] = ''
            if str(field['currency_code']) != 'None' and str(field['currency_code']):
                data["currency_code"] = str(field['currency_code'])
            else:
                data["currency_code"] = ''
            if str(field['currency_id']) != 'None' and str(field['currency_id']):
                data["currency_id"] = str(field['currency_id'])
            else:
                data["currency_id"] = ''
            if str(field["location_id"]) != 'None' and str(field['location_id']):
                data["location_id"] = str(field['location_id'])
            else:
                data["location_id"] = ''
            data["line_id"] = str(field['line_id'])
            if str(field["uom"]) != 'None' and str(field['uom']):
                data["unit"] = str(field['uom'])
            else:
                data["unit"] = ''
            if str(field["supplier_id"]) != 'None' and str(field['supplier_id']):
                data["supplier_id"] = str(field['supplier_id'])
            else:
                data["supplier_id"] = ''
            if str(field['customer_po_no']) != 'None' and str(field['customer_po_no']):
                data["customer_po_no"] = str(field['customer_po_no'])
            else:
                data["customer_po_no"] = ''
            if str(field['order_quantity']) != 'None' and str(field['order_quantity']):
                data["order_qty"] = str(field['order_quantity'])
            else:
                data["order_qty"] = ''
            if str(field['delivery_quantity']) != 'None' and str(field['delivery_quantity']):
                data["delivery_qty"] = str(field['delivery_quantity'])
            else:
                data["delivery_qty"] = ''
            if str(field['stock_quantity']) != 'None' and str(field['stock_quantity']):
                data["stock_quantity"] = str(field['stock_quantity'])
            else:
                data["stock_quantity"] = ''
            if str(field['location_item_quantity']) != 'None' and field['location_item_quantity']:
                data["location_item_quantity"] = str(field['location_item_quantity'])
            else:
                data["location_item_quantity"] = '0'
            if str(field['country_origin_id']) != 'None' and field['country_origin_id']:
                data["country_origin_id"] = str(field['country_origin_id'])
            else:
                data["country_origin_id"] = ''
            if str(field['country_origin_cd']) != 'None' and field['country_origin_cd']:
                data["country_origin_cd"] = str(field['country_origin_cd'])
            else:
                data["country_origin_cd"] = ''
            array.append(data)

        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@login_required
def soList_select__asJson(request, id_customers, item_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    if id_customers == '0':
        items_list = CustomerItem.objects.none()
    else:
        items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=id_customers, item_id=item_id) \
            .values('item_id').order_by('item__code', 'item__supplieritem__supplier__code', 'item__locationitem__location__id') \
            .annotate(new_price=F('new_price')) \
            .annotate(effective_date=F('effective_date')) \
            .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
            .annotate(supplier_id=F('item__supplieritem__supplier')) \
            .annotate(location_code=F('item__locationitem__location__code')) \
            .annotate(location_id=F('item__locationitem__location__id')) \
            .annotate(custome_name=F('customer__name')) \
            .annotate(item_name=F('item__name')) \
            .annotate(description=Value('', output_field=models.CharField())) \
            .annotate(item_short_description=F('item__short_description')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(minimun_order=F('item__minimun_order')) \
            .annotate(sales_price=F('sales_price')) \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(currency_code=F('currency__code')) \
            .annotate(currency_id=F('currency_id')) \
            .annotate(line_id=Value(0, output_field=models.CharField())).distinct()

    array = []
    draw = ''
    if company.is_inventory:
        for i, j in enumerate(items_list):
            if i < items_list.__len__():
                i += 1
                j['line_id'] = i
                if j['location_id'] is None:
                    get_default_location = Item.objects.get(pk=j['item_id'])
                    j['location_id'] = get_default_location.default_location_id \
                        if get_default_location.default_location_id is not None else None
                    j['location_code'] = get_default_location.default_location.code \
                        if get_default_location.default_location_id is not None else None

    # Create data list
    array = []
    identity = 1
    for field in items_list:
        if str(field["supplier_id"]) != 'None' and int(field['supplier_id']):
            data = {}
            data["identity"] = str(identity)
            identity += 1
            data["id"] = str(field['item_id'])
            data["name"] = str(field['item_name']) \
                if str(field['item_name']) != 'None' and str(field['item_name']) else ''
            data["supplier"] = str(field['supplier_code']) \
                if str(field['supplier_code']) != 'None' and str(field['supplier_code']) else ''
            data["location_code"] = str(field['location_code']) \
                if str(field['location_code']) != 'None' and str(field['location_code']) else ''
            data["code"] = str(field['code']) if str(field['code']) != 'None' and str(field['code']) else ''
            data["category"] = str(field['category']) if str(field['category']) != 'None' and str(field['category']) else ''
            data["minoq"] = str(field['minimun_order']) \
                if str(field['minimun_order']) != 'None' and str(field['minimun_order']) else '0'
            data["sales_price"] = str(field['sales_price']) \
                if str(field['sales_price']) != 'None' and str(field['sales_price']) else ''
            data["currency"] = str(field['currency_code']) \
                if str(field['currency_code']) != 'None' and str(field['currency_code']) else ''
            data["currency_id"] = str(field['currency_id']) \
                if str(field['currency_id']) != 'None' and str(field['currency_id']) else ''
            data["line_id"] = str(field['line_id'])
            data["uom"] = str(field['uom']) if str(field["uom"]) != 'None' and str(field['uom']) else ''
            data["supplier_id"] = str(field['supplier_id']) \
                if str(field["supplier_id"]) != 'None' and int(field['supplier_id']) else ''
            data["item_short_description"] = str(field['item_short_description']) \
                if str(field["item_short_description"]) != 'None' and str(field['item_short_description']) else ''
            data['description'] = str(field['description']) if field['description'] else ''

            if not field['effective_date']:
                data["unit_price"] = str(field['new_price'] if field['new_price'] else field['sales_price'])
            elif field['effective_date'].strftime('%Y-%m-%d') <= datetime.datetime.now().strftime('%Y-%m-%d'):
                data["unit_price"] = str(field['new_price'] if field['new_price'] else field['sales_price'])
            else:
                data["unit_price"] = str(field['sales_price'] if field['sales_price'] else 0.00000)

            data["qty_rfs"] = '0'
            if company.is_inventory:
                if str(field["location_id"]) != 'None' and str(field['location_id']):
                    data["location_id"] = str(field['location_id'])
                    try:
                        loc_item = LocationItem.objects.filter(is_hidden=0). \
                            filter(location_id=field['location_id'], item_id=field['item_id']). \
                            exclude(onhand_qty__isnull=True).exclude(onhand_qty__lte=0). \
                            aggregate(qty_rfs=Coalesce(Sum('onhand_qty'), V(0)) - Coalesce(Sum('booked_qty'), V(0)))
                        if loc_item:
                            data["qty_rfs"] = str(loc_item['qty_rfs'])
                    except Exception as e:
                        print(e)
                else:
                    data["location_id"] = ''

            array.append(data)

    content = {"draw": draw, "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def so_item_supp_info(request, id_customers, item_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    array = {'loc': [], 'sup': []}

    if id_customers == '0':
        items_list = CustomerItem.objects.none()
    else:
        items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=id_customers, 
                            item_id=item_id, customer__company_id=company_id) \
            .values('item_id').order_by('item__code', 'item__supplieritem__supplier__code') \
            .annotate(item_def_supp=F('item__default_supplier_id')) \
            .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
            .annotate(supplier_id=F('item__supplieritem__supplier')) .distinct()

    # Create data list
    for field in items_list:
        if str(field["supplier_id"]) != 'None' and int(field['supplier_id']):
            data = {}
            data["item_id"] = str(field['item_id'])
            data["supplier_code"] = str(field['supplier_code']) \
                if str(field['supplier_code']) != 'None' and str(field['supplier_code']) else ''
            data["item_def_supp"] = str(field['item_def_supp']) if str(
                field['item_def_supp']) != 'None' and str(field['item_def_supp']) else ''
            data["supplier_id"] = str(field['supplier_id']) \
                if str(field["supplier_id"]) != 'None' and int(field['supplier_id']) else ''

            array['sup'].append(data)

    
    if id_customers == '0':
        items_list = CustomerItem.objects.none()
    else:
        items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=id_customers, 
                            item_id=item_id, customer__company_id=company_id) \
            .values('item_id').order_by('item__code', 'item__locationitem__location__id') \
            .annotate(location_code=F('item__locationitem__location__code')) \
            .annotate(location_id=F('item__locationitem__location__id')).distinct()

    if company.is_inventory:
        for i, j in enumerate(items_list):
            if i < items_list.__len__():
                i += 1
                j['line_id'] = i
                if j['location_id'] is None:
                    get_default_location = Item.objects.get(pk=j['item_id'])
                    j['location_id'] = get_default_location.default_location_id \
                        if get_default_location.default_location_id is not None else None
                    j['location_code'] = get_default_location.default_location.code \
                        if get_default_location.default_location_id is not None else None
    for field in items_list:
        data = {}
        data["item_id"] = str(field['item_id'])
        data["location_code"] = str(field['location_code']) \
            if str(field['location_code']) != 'None' and str(field['location_code']) else ''
        data["rfs_qty"] = '0'
        if company.is_inventory and str(field["location_id"]) != 'None' and str(field['location_id']):
            data["location_id"] = str(field['location_id'])
            try:
                loc_item = LocationItem.objects.filter(is_hidden=0). \
                    filter(location_id=field['location_id'], item_id=field['item_id']). \
                    exclude(onhand_qty__isnull=True).exclude(onhand_qty__lte=0). \
                    aggregate(rfs_qty=Coalesce(Sum('onhand_qty'), V(0)) - Coalesce(Sum('booked_qty'), V(0)))
                if loc_item:
                    data["rfs_qty"] = str(loc_item['rfs_qty'])
            except Exception as e:
                print(e)
        else:
            data["location_id"] = ''

        array['loc'].append(data)

    content = {"data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def so_items_list(request, id_customers):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    # company = Company.objects.get(pk=company_id)

    if id_customers == '0':
        items_list = CustomerItem.objects.none()
    else:
        items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, 
                            customer_id=id_customers, customer__company_id=company_id) \
            .values('item_id').order_by('item__code') \
            .annotate(code=F('item__code')) \
            .annotate(item_name=F('item__name')) \
            .distinct()

    array = []
    # Create data list
    array = []
    for field in items_list:
        data = {}
        data["item_id"] = str(field['item_id'])
        data["code"] = str(field['code']) if str(field['code']) != 'None' and str(field['code']) else ''
        data["item_name"] = str(field['item_name']) \
                if str(field['item_name']) != 'None' and str(field['item_name']) else ''
        array.append(data)

    content = {"data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def so_invoice_item_list_as_json(request):
    if request.is_ajax():
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        customer_id = request.GET['customer_id']

        if customer_id == '0':
            items_list = CustomerItem.objects.none()
        else:
            items_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=customer_id) \
                .values('item_id') \
                .annotate(new_price=F('new_price')) \
                .annotate(effective_date=F('effective_date')) \
                .annotate(supplier_code=F('item__supplieritem__supplier__code')) \
                .annotate(supplier_id=F('item__supplieritem__supplier')) \
                .annotate(location_code=F('item__locationitem__location__code')) \
                .annotate(location_id=F('item__locationitem__location__id')) \
                .annotate(custome_name=F('customer__name')) \
                .annotate(item_name=F('item__name')) \
                .annotate(description=Value('', output_field=models.CharField())) \
                .annotate(code=F('item__code')) \
                .annotate(category=F('item__category__code')) \
                .annotate(minimun_order=F('item__minimun_order')) \
                .annotate(sales_price=F('sales_price')) \
                .annotate(uom=F('item__sales_measure__name')) \
                .annotate(currency_code=F('currency__code')) \
                .annotate(currency_id=F('currency_id')) \
                .annotate(line_id=Value(0, output_field=models.CharField())).distinct()

        records_total = items_list.count()

        if search:  # Filter data base on search
            items_list = items_list.filter(Q(item__name__icontains=search) | Q(item__code__icontains=search) | Q(
                item__supplieritem__supplier__code__icontains=search) | Q(
                item__locationitem__location__code__icontains=search))

        # All data
        records_filtered = items_list.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "1":
            column_name = "item__name"
        elif order_column == "2":
            column_name = "item__supplieritem__supplier__code"
        elif order_column == "3":
            column_name = "item__locationitem__location__code"
        elif order_column == "4":
            column_name = "item__code"
        elif order_column == "5":
            column_name = "item__category__code"
        elif order_column == "6":
            column_name = "sales_price"
        elif order_column == "7":
            column_name = "currency__code"
        order_dir = request.GET['order[0][dir]']

        list = []
        if order_dir == "asc":
            list = items_list.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = items_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        for i, j in enumerate(list):
            if i < list.__len__():
                i += 1
                j['line_id'] = i
                if j['location_id'] is None:
                    get_default_location = Item.objects.get(pk=j['item_id'])
                    j['location_id'] = get_default_location.default_location_id \
                        if get_default_location.default_location_id is not None else None
                    j['location_code'] = get_default_location.default_location.code \
                        if get_default_location.default_location_id is not None else None

        # Create data list
        array = []
        for field in list:
            data = {}
            data["item_id"] = str(field['item_id'])

            if not field['effective_date']:
                data["new_price"] = str(field['new_price'] if field['new_price'] else field['sales_price'])
            elif field['effective_date'].strftime('%Y-%m-%d') <= datetime.datetime.now().strftime('%Y-%m-%d'):
                data["new_price"] = str(field['new_price'] if field['new_price'] else field['sales_price'])
            else:
                data["new_price"] = str(field['sales_price'] if field['sales_price'] else 0.00000)

            data["item_name"] = str(field['item_name']) \
                if str(field['item_name']) != 'None' and str(field['item_name']) else ''
            data["supplier_code"] = str(field['supplier_code']) \
                if str(field['supplier_code']) != 'None' and str(field['supplier_code']) else ''
            data["location_code"] = str(field['location_code']) \
                if str(field['location_code']) != 'None' and str(field['location_code']) else ''
            data["code"] = str(field['code']) \
                if str(field['code']) != 'None' and str(field['code']) else ''
            data["category"] = str(field['category']) \
                if str(field['category']) != 'None' and str(field['category']) else ''
            data["sales_price"] = str(field['sales_price']) \
                if str(field['sales_price']) != 'None' and str(field['sales_price']) else ''
            data["minimun_order"] = str(field['minimun_order']) \
                if str(field['minimun_order']) != 'None' and str(field['minimun_order']) else ''
            data["currency_code"] = str(field['currency_code']) \
                if str(field['currency_code']) != 'None' and str(field['currency_code']) else ''
            data["currency_id"] = str(field['currency_id']) \
                if str(field['currency_id']) != 'None' and str(field['currency_id']) else ''
            data["line_id"] = str(field['line_id'])
            data["unit"] = str(field['uom']) if str(field["uom"]) != 'None' and str(field['uom']) else ''
            data["supplier_id"] = str(field['supplier_id']) \
                if str(field["supplier_id"]) != 'None' and str(field['supplier_id']) else ''
            data['description'] = str(field['description']) if field['description'] else ''

            data["rfs_qty"] = 0
            if str(field["location_id"]) != 'None' and str(field['location_id']):
                data["location_id"] = str(field['location_id'])
                try:
                    loc_item = LocationItem.objects.filter(is_hidden=0). \
                        filter(location_id=field['location_id'], item_id=field['item_id'], is_hidden=False). \
                        exclude(onhand_qty__isnull=True).exclude(onhand_qty__lte=0). \
                        aggregate(rfs_qty=Coalesce(Sum('onhand_qty'), V(0)) - Coalesce(Sum('booked_qty'), V(0)))
                    if loc_item:
                        data["rfs_qty"] = str(loc_item['rfs_qty'])
                except Exception as e:
                    print(e)
            else:
                data["location_id"] = ''

            array.append(data)

        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def apache_output_json(request):

    ip_address = get_client_ip(request)
    print("IP Address: ", ip_address)
    eprint("Out address: " + ip_address)

    content = {"Client IP Address": ip_address}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def po_select_as_json(request, id_supplier):

    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if id_supplier == '0':
        items_list = OrderItem.objects.none()
    else:
        items_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                 supplier_id=id_supplier) \
            .values('item_id') \
            .order_by('item__code') \
            .annotate(new_price=Coalesce(F('new_price'), V(0))) \
            .annotate(effective_date=F('effective_date')) \
            .annotate(item_name=F('item__name')) \
            .annotate(description=Value('', output_field=models.CharField())) \
            .annotate(amount=Value('', output_field=models.CharField())) \
            .annotate(supplier_code=F('supplier__code')) \
            .annotate(supplier_id=F('supplier_id')) \
            .annotate(ref_id=Value('', output_field=models.CharField())) \
            .annotate(ref_number=Value('', output_field=models.CharField())) \
            .annotate(ref_line=Value('', output_field=models.CharField())) \
            .annotate(currency_id=F('supplier__currency')) \
            .annotate(currency=F('supplier__currency__code')) \
            .annotate(default_location_id=F('item__default_location_id')) \
            .annotate(purchase_price=Coalesce(F('purchase_price'), V(0))) \
            .annotate(code=F('item__code')).annotate(category=F('item__category__code')) \
            .annotate(uom=F('item__purchase_measure__name')) \
            .annotate(minimun_order=F('item__minimun_order')) \
            .annotate(customer_po_no=Value('', output_field=models.CharField())) \
            .annotate(line_id=Value(0, output_field=models.CharField())) 
            # .annotate(location_code=F('item__locationitem__location__code')) \
            # .annotate(location_id=F('item__locationitem__location__id')) \
            # .annotate(location_id=Value(None, output_field=models.CharField())) \
            # .annotate(location_code=Value(None, output_field=models.CharField()))

        if company.is_inventory:
            # for i, j in enumerate(items_list):
            #     if i < items_list.__len__():
            #         i += 1
            #         j['line_id'] = i
            #         if j['location_id'] is None:
            #             get_default_location = Item.objects.get(pk=j['item_id'])
            #             j['location_id'] = get_default_location.default_location_id \
            #                 if get_default_location.default_location_id is not None else None
            #             j['location_code'] = get_default_location.default_location.code \
            #                 if get_default_location.default_location_id is not None else None
            item_ids = []

            for item_row in items_list:
                item_ids.append(item_row['item_id'])

            loc_item_list = LocationItem.objects.filter(is_hidden=0). \
                values('item_id'). \
                filter(item_id__in=item_ids). \
                exclude(onhand_qty__isnull=True).exclude(onhand_qty__lte=0). \
                annotate(rfs_qty=Coalesce(Sum('onhand_qty'), V(0)) - Coalesce(Sum('booked_qty'), V(0)))

            loc_items = {}

            for loc_item in loc_item_list:
                loc_items[loc_item['item_id']] = loc_item['rfs_qty']
        else:
            loc_items = {}

    array = []
    identity = 1
    for field in items_list:
        data = {}
        location_list = []
        data["identity"] = str(identity)
        identity += 1
        data["id"] = str(field['item_id'])
        if not field['effective_date']:
            data["purchase_price"] = str(field['new_price'] if field['new_price'] else field['purchase_price'])
        elif field['effective_date'].strftime('%Y-%m-%d') <= datetime.datetime.now().strftime('%Y-%m-%d'):
            data["purchase_price"] = str(field['new_price'] if field['new_price'] else field['purchase_price'])
        else:
            data["purchase_price"] = str(field['purchase_price'] if field['purchase_price'] else 0.00000)

        # data["location_code"] = str(field['location_code']) if field['location_code'] else ''
        # data["location_id"] = str(field['location_id']) if field['location_id'] else ''
        data["name"] = str(field['item_name']) if field['item_name'] else ''
        data["supplier"] = str(field['supplier_code']) if field['supplier_code'] else ''
        data["ref_no"] = str(field['ref_number']) 
        data["ref_line"] = str(field['ref_line']) 

        data["code"] = str(field['code']) if field['code'] else ''
        data["category"] = str(field['category']) if str(field['category']) != 'None' and str(field['category']) else ''
        data["currency"] = str(field['currency']) if field['currency'] else ''
        data["currency_id"] = str(field['currency_id']) if field['currency_id'] else ''
        data["line_id"] = str(field['line_id'])
        data["uom"] = str(field['uom']) if field['uom'] else ''
        data["supplier_id"] = str(field['supplier_id']) if field['supplier_id'] else ''
        data["minimun_order"] = str(field['minimun_order']) if field['minimun_order'] else ''
        data["backorder_qty"] = str(loc_items[field['item_id']]) if field['item_id'] in loc_items else ''
        data["ref_id"] = str(field['ref_id']) 
        data["customer_po_no"] = str(field['customer_po_no']) if field['customer_po_no'] else ''
        data['description'] = str(field['description']) if field['description'] else ''
        data['amount'] = str(field['amount']) if field['amount'] else ''
        data['location_list'] = []
        if not company.is_inventory:
            data['default_location_id'] = ''
        else:
            data['default_location_id'] = str(field['default_location_id']) if field['default_location_id'] else ''
            locations = LocationItem.objects.filter(is_hidden=0, item_id=field['item_id']).values('location_id', 'location__code')
            if locations.exists():
                for loc in locations:
                    location_list.append({
                        'id': loc['location_id'],
                        'code': loc['location__code']
                    })
                data['location_list'] = location_list

        # if data["location_id"] == '' and data['default_location_id'] != '':
        #     data["location_id"] = data['default_location_id']
        array.append(data)
    content = {"draw": '', "data": array}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')

@csrf_exempt
def po_invoice_item_list_as_json(request):
    if request.is_ajax():
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)

        supplier_id = request.GET['supplier_id']
        if supplier_id == '0':
            items_list = OrderItem.objects.none()
        else:
            items_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                     supplier_id=supplier_id) \
                .values('item_id') \
                .annotate(new_price=Coalesce(F('new_price'), V(0))) \
                .annotate(effective_date=F('effective_date')) \
                .annotate(item_name=F('item__name')) \
                .annotate(description=Value('', output_field=models.CharField())) \
                .annotate(amount=Value('', output_field=models.CharField())) \
                .annotate(supplier_code=F('supplier__code')).annotate(supplier_id=F('supplier_id')) \
                .annotate(ref_id=Value('', output_field=models.CharField())) \
                .annotate(ref_number=Value('', output_field=models.CharField())) \
                .annotate(ref_line=Value('', output_field=models.CharField())) \
                .annotate(currency_id=F('supplier__currency')) \
                .annotate(currency=F('supplier__currency__code')) \
                .annotate(location_code=F('item__locationitem__location__code')) \
                .annotate(location_id=F('item__locationitem__location_id')) \
                .annotate(default_location_id=F('item__default_location_id')) \
                .annotate(purchase_price=Coalesce(F('purchase_price'), V(0))) \
                .annotate(code=F('item__code')) \
                .annotate(category=F('item__category__code')) \
                .annotate(uom=F('item__purchase_measure__name')) \
                .annotate(minimun_order=F('item__minimun_order')) \
                .annotate(customer_po_no=Value('', output_field=models.CharField())) \
                .annotate(line_id=Value(0, output_field=models.CharField()))

        records_total = items_list.count()

        if search:  # Filter data base on search
            items_list = items_list.filter(Q(item__name__icontains=search) | Q(item__code__icontains=search) | Q(
                supplier__code__icontains=search) | Q(location_code__icontains=search))

        # All data
        records_filtered = items_list.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "1":
            column_name = "item__name"
        elif order_column == "2":
            column_name = "supplier__code"
        elif order_column == "3":
            column_name = "order__document_number"
        elif order_column == "4":
            column_name = "line_number"
        elif order_column == "5":
            column_name = "location_code"
        elif order_column == "6":
            column_name = "item__code"
        elif order_column == "7":
            column_name = "item__category__code"
        elif order_column == "8":
            column_name = "item__purchase_price"
        elif order_column == "9":
            column_name = "supplier__currency__code"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = items_list.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = items_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        for i, j in enumerate(list):
            if (i < list.__len__()):
                i += 1
                j['line_id'] = i

        # Create data list
        array = []
        for field in list:
            data = {}
            data["item_id"] = str(field['item_id'])
            if not field['effective_date']:
                data["new_price"] = str(field['new_price'] if field['new_price'] else field['purchase_price'])
            elif field['effective_date'].strftime('%Y-%m-%d') <= datetime.datetime.now().strftime('%Y-%m-%d'):
                data["new_price"] = str(field['new_price'] if field['new_price'] else field['purchase_price'])
            else:
                data["new_price"] = str(field['purchase_price'] if field['purchase_price'] else 0.00000)

            item_name = str(field['item_name'])
            supplier_code = str(field['supplier_code'])
            data["item_name"] = item_name if item_name != 'None' and item_name else ''
            data["supplier_code"] = supplier_code if supplier_code != 'None' and supplier_code else ''
            data["refer_number"] = str(field['ref_number']) \
                if str(field['ref_number']) != 'None' and str(field['ref_number']) else ''
            data["refer_line"] = str(field['ref_line'])
            data["location_code"] = str(field['location_code']) \
                if str(field['location_code']) != 'None' and str(field['location_code']) else ''
            data["code"] = str(field['code']) if str(field['code']) != 'None' and str(field['code']) else ''
            data["category"] = str(field['category']) \
                if str(field['category']) != 'None' and str(field['category']) else ''

            supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        item_id=field['item_id'],
                                                        supplier_id=field['supplier_id']).last()

            data["purchase_price"] = str(supplier_item.purchase_price) if supplier_item else '0'
            data["currency_code"] = str(field['currency']) \
                if str(field['currency']) != 'None' and str(field['currency']) else ''
            data["location_id"] = str(field['location_id']) \
                if str(field["location_id"]) != 'None' and str(field['location_id']) else ''
            data["currency_id"] = str(field['currency_id']) \
                if str(field["currency_id"]) != 'None' and str(field['currency_id']) else ''
            data["line_id"] = str(field['line_id'])
            data["unit"] = str(field['uom']) if str(field["uom"]) != 'None' and str(field['uom']) else ''
            data["supplier_id"] = str(field['supplier_id']) \
                if str(field["supplier_id"]) != 'None' and str(field['supplier_id']) else ''
            data["minimun_order"] = str(field['minimun_order']) \
                if str(field['minimun_order']) != 'None' and str(field['minimun_order']) else ''
            data["refer_id"] = str(field['ref_id']) if str(field['ref_id']) != 'None' and str(field['ref_id']) else ''
            data["customer_po_no"] = str(field['customer_po_no']) \
                if str(field['customer_po_no']) != 'None' and str(field['customer_po_no']) else ''
            data['description'] = str(field['description']) if field['description'] else ''
            data['amount'] = str(field['amount']) if field['amount'] else ''
            if not company.is_inventory:
                data['default_location_id'] = ''
            else:
                data['default_location_id'] = str(field['default_location_id']) if field['default_location_id'] else ''
            array.append(data)

        content = {"draw": '', "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@csrf_exempt
def customer_search_by_code(request):
    if request.method == 'POST' and request.is_ajax():
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            customer_code = request.POST.get('customer_code')
            if customer_code != '':
                customer = Customer.objects.filter(code__exact=customer_code, is_hidden=0, company_id=company_id,
                                                   is_active=1).first()
                contact = Contact.objects.filter(is_hidden=0, customer_id=customer.id,
                                                 contact_type=int(CONTACT_TYPES_DICT['Consignee']),
                                                 consignee_id=customer.id).first()
                if customer:
                    response_data = {}
                    response_data['id'] = customer.id
                    response_data['code'] = customer.code
                    response_data['name'] = customer.name
                    response_data['address'] = customer.address
                    response_data['email'] = customer.email
                    response_data['term'] = customer.payment_term if customer.payment_term is not None else ''
                    response_data['payment_mode'] = customer.payment_code.code if customer.payment_code_id else ''
                    response_data['credit_limit'] = str(customer.credit_limit) if customer.credit_limit else ''
                    response_data['tax_id'] = str(customer.tax_id) if customer.tax else '0'
                    response_data['currency_id'] = customer.currency_id
                    response_data['consignee'] = (contact.name if contact.consignee_id else '') \
                        if contact is not None else ''
                    response_data['consignee_addr'] = \
                        (contact.address if contact.consignee_id and contact.address else '') \
                        if contact is not None else ''
                    response_data['consignee_contact'] = \
                        (contact.name if contact.consignee_id and contact.name else '') \
                        if contact is not None else ''
                    response_data['consignee_phone'] = (contact.phone if contact.consignee_id else '') \
                        if contact is not None else ''

                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    messages.add_message(request, messages.ERROR, 'Cannot find customer',
                                         extra_tags='change_customer_info')
            else:
                response_data = {}
                response_data['id'] = 0
                response_data['code'] = ''
                response_data['name'] = ''
                response_data['address'] = ''
                response_data['email'] = ''
                response_data['term'] = ''
                response_data['payment_mode'] = ''
                response_data['credit_limit'] = ''
                response_data['tax_id'] = ''
                response_data['currency_id'] = ''
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='change_customer_info')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@csrf_exempt
def supplier_search_by_code(request):
    if request.method == 'POST' and request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        try:
            supplier_code = request.POST.get('supplier_code')
            response_data = {}
            if supplier_code != '':
                supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1,
                                                   code__exact=supplier_code).first()
                if supplier:
                    response_data['id'] = supplier.id
                    response_data['code'] = supplier.code
                    response_data['name'] = supplier.name
                    response_data['address'] = supplier.address
                    response_data['email'] = supplier.email
                    response_data['term'] = supplier.term_days if supplier.term_days is not None else ''
                    response_data['payment_mode'] = supplier.payment_code.code if supplier.payment_code_id else ''
                    response_data['credit_limit'] = str(supplier.credit_limit) if supplier.credit_limit else ''
                    response_data['tax_id'] = str(supplier.tax_id) if supplier.tax else '0'
                    response_data['currency_id'] = supplier.currency_id
                    response_data['currency_code'] = supplier.currency.code if supplier.currency.code else ''
                else:
                    messages.add_message(request, messages.ERROR, 'Cannot find supplier',
                                         extra_tags='change_supplier_info')
            else:
                response_data['id'] = 0
                response_data['code'] = ''
                response_data['name'] = ''
                response_data['address'] = ''
                response_data['email'] = ''
                response_data['term'] = ''
                response_data['payment_mode'] = ''
                response_data['credit_limit'] = ''
                response_data['tax_id'] = ''
                response_data['currency_id'] = ''
                response_data['currency_code'] = ''
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='change_supplier_info')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
@csrf_exempt
def suppliers_list_as_json(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        list_filter = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(
                Q(code__icontains=search) | Q(name__icontains=search) | Q(term_days=search) | Q(
                    credit_limit__icontains=search) | Q(payment_mode__name__icontains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "term_days"
        elif order_column == "3":
            column_name = "payment_mode__name"
        elif order_column == "4":
            column_name = "credit_limit"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {}
            data["id"] = field.id
            data["code"] = field.code if field.code else ''
            data["name"] = field.name if field.name else ''
            data["term_days"] = str(field.term_days if field.term_days else '')
            data["payment_mode"] = str(
                field.payment_mode.name if field.payment_mode and field.payment_mode.name else '')
            data["credit_limit"] = str(field.credit_limit if field.credit_limit else '0')
            data["currency_code"] = str(field.currency.code if field.currency and field.currency.code else '')
            array.append(data)
        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def customers_list_as_json(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        list_filter = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(
                Q(code__icontains=search) | Q(name__icontains=search) | Q(payment_term=search) | Q(
                    credit_limit__icontains=search) | Q(payment_mode__name__icontains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "payment_term"
        elif order_column == "3":
            column_name = "payment_mode__name"
        elif order_column == "4":
            column_name = "credit_limit"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {}
            data["id"] = field.id
            data["code"] = field.code if field.code else ''
            data["name"] = field.name if field.name else ''
            data["payment_term"] = str(field.payment_term if field.payment_term else '')
            data["payment_mode"] = str(
                field.payment_mode.name if field.payment_mode and field.payment_mode.name else '')
            data["credit_limit"] = str(field.credit_limit if field.credit_limit else '0')
            array.append(data)
        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def is_doc_no_exist(request):
    is_exist = False
    try:
        if request.is_ajax():
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            doc_no = request.POST.get('doc_no').upper()
            order = Order.objects.filter(is_hidden=0, company_id=company_id,
                                         document_number=doc_no).values('id')
            if order:
                is_exist = True
    except Exception as e:
        print(e)

    json_content = json.dumps(is_exist, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def get_orderitems_by_so_no(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        so_number = request.POST.get('so_number')
        do_date = request.POST.get('doc_date')
        customer_id = request.POST.get('customer_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        if customer_id == '':
            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__id=so_number,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=1).exclude(order__status=4).exclude(item_id__in=exclude_item_list). \
                exclude(delivery_quantity__gte=F('quantity')).order_by('line_number')
        else:
            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__id=so_number,
                                                  order__customer_id=customer_id,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=1).exclude(order__status=4).exclude(item_id__in=exclude_item_list). \
                exclude(delivery_quantity__gte=F('quantity')).order_by('line_number')
        
        if company.is_inventory:
            items = orderitems.values_list('item_id', flat=True)
            loc_items = LocationItem.objects.filter(item_id__in=items,
                        location__company_id=company_id,
                        is_hidden=False,
                        location__is_hidden=False)
        
        my_array = []
        for item in orderitems:
            if 0 > item.delivery_quantity:
                item.delivery_quantity = 0
                item.save()
            data = {}
            data['item_id'] = str(item.item_id)
            data['minimum_order'] = str(item.item.minimun_order) if item.item.minimun_order else 0
            data['sales_price'] = str(item.price)
            data['item_name'] = str(item.item.name)
            data['item_code'] = str(item.item.code)
            data['refer_id'] = str(item.order_id) if item.order_id else None
            data['refer_number'] = str(item.order.document_number)
            data['refer_line'] = str(item.line_number)
            data['description'] = str(item.description)
            data['schedule_date'] = item.schedule_date.strftime("%Y-%m-%d") if item.schedule_date else ''
            data['wanted_date'] = item.wanted_date.strftime("%Y-%m-%d") if item.wanted_date else ''
            data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
            data['location_code'] = str(item.location.code) if item.location else ''
            data['category'] = str(item.item.category.code) if item.item.category else ''
            data['currency_code'] = str(
                item.order.customer.currency.code) if item.order.customer and item.order.customer.currency else ''
            data['location_id'] = str(item.location_id) if item.location else ''
            data['currency_id'] = str(
                item.order.customer.currency_id) if item.order.customer and item.order.customer.currency else ''
            data['uom'] = str(item.item.sales_measure.name) if item.item.sales_measure else ''
            data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
            data['quantity'] = str(item.quantity)
            data['backorder_qty'] = str(item.bkord_quantity) if item.bkord_quantity else 0
            data['delivery_quantity'] = str(item.delivery_quantity) if item.delivery_quantity else 0
            data['customer_po_no'] = str(item.customer_po_no)
            data['customer_code'] = str(
                item.order.customer.code) if item.order.customer and item.order.customer.code else ''
            data['country_origin_id'] = str(item.item.country_id) if item.item.country_id else ''
            data['country_origin_cd'] = str(
                item.item.country.code) if item.item.country and item.item.country.code else ''
            if company.is_inventory:
                try:
                    loc_item = loc_items. \
                        filter(item_id=item.item_id, location_id=item.location_id)
                    if loc_item.exists():
                        loc_item = loc_item.aggregate(sum_onhand_qty=Coalesce(Sum('onhand_qty'), V(0)))
                        data["location_item_quantity"] = str(loc_item.get('sum_onhand_qty'))
                    if not len(loc_item) or float(data["location_item_quantity"]) <= 0:
                        qty_gr = 0
                        po_list = order_vs_inventory(request).get_next_doc_detail(item.id)
                        if po_list:
                            for po in po_list:
                                gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
                                if gr_list:
                                    for gr in gr_list:
                                        qty_gr += gr.quantity
                                        if gr.location_id:
                                            data['location_id'] = str(gr.location_id)
                                            data['location_code'] = str(gr.location.code)
                        if qty_gr == 0:
                            loc_itms = loc_items. \
                                filter(item_id=item.item_id).exclude(location_id=item.location_id).order_by('location_id')
                            if loc_itms.exists():
                                for loc_item in loc_itms:
                                    if loc_item.onhand_qty:
                                        qty_gr = loc_item.onhand_qty
                                        data['location_id'] = str(loc_item.location_id)
                                        data['location_code'] = str(loc_item.location.code) if loc_item.location.code else ''
                                        break
                        data["location_item_quantity"] = str(qty_gr)
                    # cehck stock incoming date to get correct stock
                    print('item', data['item_id'])
                    print('location_item_quantity', data['location_item_quantity'])
                    if data["location_item_quantity"]:
                        stock_by_date_in = StockTransactionDetail.objects.filter(is_hidden=0, parent__is_closed=0, parent__company_id=company_id, in_location_id=data['location_id'],
                                          item_id=data['item_id'], parent__document_date__lte=do_date)\
                                    .aggregate(current_onhand_qty=Coalesce(Sum('quantity'), V(0)))['current_onhand_qty']
                        stock_by_date_out = StockTransactionDetail.objects.filter(is_hidden=0, parent__is_closed=0, parent__company_id=company_id, out_location_id=data['location_id'],
                                          item_id=data['item_id'], parent__document_date__lte=do_date)\
                                    .aggregate(current_onhand_qty=Coalesce(Sum('quantity'), V(0)))['current_onhand_qty']
                        print('stock_by_date_in', stock_by_date_in)
                        print('stock_by_date_out', stock_by_date_out)
                        print('(float(stock_by_date_in) - float(stock_by_date_out)', float(stock_by_date_in) - float(stock_by_date_out))
                        if float(data["location_item_quantity"]) > (float(stock_by_date_in) - float(stock_by_date_out)) and\
                            (float(stock_by_date_in) - float(stock_by_date_out)) > 0:
                            data["location_item_quantity"] = str(float(stock_by_date_in) - float(stock_by_date_out))
                            print('data["location_item_quantity"]', data["location_item_quantity"])
                                          

                except Exception as e:
                    print(e)
                    data["location_item_quantity"] = '0'
            else:
                data["location_item_quantity"] = '0'

            my_array.append(data)
        if my_array:
            json_content = json.dumps(my_array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps("something went wrong", ensure_ascii=False), content_type='application/json')


@login_required
@csrf_exempt
def get_so_orderitems_for_po(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        so_number = request.POST.get('so_number')
        supplier_id = request.POST.get('supplier_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        if supplier_id:
            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__id=so_number,
                                                  supplier_id=supplier_id,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=1).exclude(item_id__in=exclude_item_list). \
                order_by('line_number')
            items = orderitems.values_list('item_id', flat=True)
            supplier_items = SupplierItem.objects.filter(is_hidden=0, is_active=1, supplier_id=supplier_id, item_id__in=items)
            if company.is_inventory:
                loc_items = LocationItem.objects.filter(item_id__in=items,
                            location__company_id=company_id,
                            is_hidden=False,
                            location__is_hidden=False)

            my_array = []
            for item in orderitems:
                # check if there are po order item for this line
                # po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                #                                        order__supplier_id=supplier_id,
                #                                        reference_id=so_number, refer_line=item.line_number,
                #                                        order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                #     .aggregate(quantity=Sum('quantity'))['quantity']
                
                # if po_item_qty and po_item_qty >= item.quantity:
                #     continue
                

                data = {}
                data['id'] = str(item.item_id)
                data['minimum_order'] = str(item.item.minimun_order) if item.item.minimun_order else 0
                data['price'] = str(item.price)
                supplier_item = supplier_items.filter(item_id=item.item_id).first()
                if not supplier_item.effective_date:
                    data['unit_price'] = str(supplier_item.purchase_price)
                elif supplier_item.new_price and datetime.date.today() >= supplier_item.effective_date:
                    data['unit_price'] = str(supplier_item.new_price)
                else:
                    data['unit_price'] = str(supplier_item.purchase_price)
                # data['unit_price'] = str(supplier_items.filter(item_id=item.item_id).first().purchase_price)
                data['name'] = str(item.item.name)
                data['item_code'] = str(item.item.code)
                data['ref_id'] = str(item.order_id) if item.order_id else None
                data['refer_number'] = str(item.order.document_number)
                data['refer_line'] = str(item.line_number)
                data['description'] = str(item.description)
                data['schedule_date'] = item.schedule_date.strftime("%Y-%m-%d") if item.schedule_date else ''
                data['wanted_date'] = item.wanted_date.strftime("%Y-%m-%d") if item.wanted_date else ''
                data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
                data['location_code'] = str(item.location.code) if item.location else ''
                data['category'] = str(item.item.category.code) if item.item.category else ''
                data['currency'] = str(
                    item.order.customer.currency.code) if item.order.customer and item.order.customer.currency else ''
                data['location_id'] = str(item.location_id) if item.location else ''
                data['currency_id'] = str(
                    item.order.customer.currency_id) if item.order.customer and item.order.customer.currency else ''
                data['uom'] = str(item.item.sales_measure.name) if item.item.sales_measure else ''
                data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
                data['order_quantity'] = str(item.quantity)
                data['backorder_qty'] = str(item.bkord_quantity) if item.bkord_quantity else 0
                data['delivery_quantity'] = str(item.delivery_quantity) if item.delivery_quantity else 0
                data['customer_po_no'] = str(item.customer_po_no)
                data['customer_code'] = str(
                    item.order.customer.code) if item.order.customer and item.order.customer.code else ''
                data['country_origin_id'] = str(item.item.country_id) if item.item.country_id else ''
                data['country_origin_cd'] = str(
                    item.item.country.code) if item.item.country and item.item.country.code else ''
                if company.is_inventory:
                    try:
                        loc_item = loc_items. \
                            filter(item_id=item.item_id, location_id=item.location_id)
                        if loc_item:
                            loc_item = loc_item.aggregate(sum_onhand_qty=Coalesce(Sum('onhand_qty'), V(0)))
                            data["location_item_quantity"] = str(loc_item.get('sum_onhand_qty'))
                        else:
                            qty_gr = 0
                            po_list = order_vs_inventory(request).get_next_doc_detail(item.id)
                            if po_list:
                                for po in po_list:
                                    gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
                                    if gr_list:
                                        for gr in gr_list:
                                            qty_gr += gr.quantity
                            data["location_item_quantity"] = str(qty_gr)

                    except Exception as e:
                        print(e)
                        data["location_item_quantity"] = '0'
                else:
                    data["location_item_quantity"] = '0'

                my_array.append(data)
            if my_array:
                json_content = json.dumps(my_array, ensure_ascii=False)
                return HttpResponse(json_content, content_type='application/json')
            else:
                print('EMPTY')
    return HttpResponse(json.dumps([], ensure_ascii=False), content_type='application/json')

@login_required
@csrf_exempt
def get_so_order_item_for_po(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        so_number = eval(request.POST.get('so_number'))
        supplier_id = request.POST.get('supplier_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        if supplier_id:
            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__id__in=so_number,
                                                  supplier_id=supplier_id,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=1).exclude(order__status=4).exclude(item_id__in=exclude_item_list). \
                order_by('order_id', 'line_number')
                # exclude(delivery_quantity__gte=F('quantity')). \
            items = orderitems.values_list('item_id', flat=True)
            supplier_items = SupplierItem.objects.filter(is_hidden=0, is_active=1, supplier_id=supplier_id, item_id__in=items)
            if company.is_inventory:
                loc_items = LocationItem.objects.filter(item_id__in=items,
                            location__company_id=company_id,
                            is_hidden=False,
                            location__is_hidden=False)

            my_array = []
            for item in orderitems:
                # check if there are po order item for this line
                # po_item_qty = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                #                                        order__supplier_id=supplier_id,
                #                                        reference_id=so_number, refer_line=item.line_number,
                #                                        order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                #     .aggregate(quantity=Sum('quantity'))['quantity']
                
                # if po_item_qty and po_item_qty >= item.quantity:
                #     continue
                

                data = {}
                data['item_id'] = str(item.item_id)
                data['minimum_order'] = str(item.item.minimun_order) if item.item.minimun_order else 0
                data['sales_price'] = str(item.price)
                supplier_item = supplier_items.filter(item_id=item.item_id).first()
                if not supplier_item.effective_date:
                    data['unit_price'] = str(supplier_item.purchase_price)
                elif supplier_item.new_price and datetime.date.today() >= supplier_item.effective_date:
                    data['unit_price'] = str(supplier_item.new_price)
                else:
                    data['unit_price'] = str(supplier_item.purchase_price)
                data['item_name'] = str(item.item.name)
                data['item_code'] = str(item.item.code)
                data['refer_id'] = str(item.order_id) if item.order_id else None
                data['refer_number'] = str(item.order.document_number)
                data['refer_line'] = str(item.line_number)
                data['description'] = str(item.description)
                data['schedule_date'] = item.schedule_date.strftime("%Y-%m-%d") if item.schedule_date else ''
                data['wanted_date'] = item.wanted_date.strftime("%Y-%m-%d") if item.wanted_date else ''
                data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
                data['location_code'] = str(item.location.code) if item.location else ''
                data['category'] = str(item.item.category.code) if item.item.category else ''
                data['currency_code'] = str(
                    item.order.customer.currency.code) if item.order.customer and item.order.customer.currency else ''
                data['location_id'] = str(item.location_id) if item.location else ''
                data['currency_id'] = str(
                    item.order.customer.currency_id) if item.order.customer and item.order.customer.currency else ''
                data['uom'] = str(item.item.sales_measure.name) if item.item.sales_measure else ''
                data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
                data['quantity'] = str(item.quantity)
                data['backorder_qty'] = str(item.bkord_quantity) if item.bkord_quantity else 0
                data['delivery_quantity'] = str(item.delivery_quantity) if item.delivery_quantity else 0
                data['customer_po_no'] = str(item.customer_po_no)
                data['customer_code'] = str(
                    item.order.customer.code) if item.order.customer and item.order.customer.code else ''
                data['country_origin_id'] = str(item.item.country_id) if item.item.country_id else ''
                data['country_origin_cd'] = str(
                    item.item.country.code) if item.item.country and item.item.country.code else ''
                if company.is_inventory:
                    try:
                        loc_item = loc_items. \
                            filter(item_id=item.item_id, location_id=item.location_id)
                        if loc_item:
                            loc_item = loc_item.aggregate(sum_onhand_qty=Coalesce(Sum('onhand_qty'), V(0)))
                            data["location_item_quantity"] = str(loc_item.get('sum_onhand_qty'))
                        else:
                            qty_gr = 0
                            po_list = order_vs_inventory(request).get_next_doc_detail(item.id)
                            if po_list:
                                for po in po_list:
                                    gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
                                    if gr_list:
                                        for gr in gr_list:
                                            qty_gr += gr.quantity
                            data["location_item_quantity"] = str(qty_gr)

                    except Exception as e:
                        print(e)
                        data["location_item_quantity"] = '0'
                else:
                    data["location_item_quantity"] = '0'

                my_array.append(data)
            if my_array:
                json_content = json.dumps(my_array, ensure_ascii=False)
                return HttpResponse(json_content, content_type='application/json')
            else:
                print('EMPTY')
    return HttpResponse(json.dumps("something went wrong", ensure_ascii=False), content_type='application/json')


@login_required
def get_item_backorder(request):
    json_data = []
    item_id = request.GET['item_id']

    try:
        loc_item = LocationItem.objects.filter(is_hidden=0). \
            values('item_id'). \
            filter(item_id=item_id). \
            exclude(onhand_qty__isnull=True).exclude(onhand_qty__lt=0). \
            annotate(rfs_qty=Coalesce(Sum('booked_qty'), V(0)) - Coalesce(Sum('onhand_qty'), V(0))). \
            first()

        data = {
            'item_id': item_id,
            'rfs_qty': str(loc_item['rfs_qty']),
        }

        json_data.append(data)

    except Exception as e:
        print(e)

    json_content = json.dumps(json_data, ensure_ascii=False)

    return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def get_orderitems_by_cust_po_no(request):
    my_array = []
    try:
        if request.is_ajax():
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            cust_po_no = request.POST.get('cust_po_no')
            item_id = request.POST.get('item_id')
            otype = request.POST.get('type')
            ref_number = ''
            try:
                ref_number = request.POST.get('ref_number')
            except:
                pass
            if request.POST.get('supplier_id'):
                item_id = request.POST.get('item_id')
                supplier_id = request.POST.get('supplier_id')
                orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      supplier_id=supplier_id, item_id=item_id,
                                                      customer_po_no=cust_po_no,
                                                      order__order_type=dict(ORDER_TYPE)['SALES ORDER']).exclude(order__document_number=ref_number). \
                    values('item_id', 'order_id', 'line_number', 'order__document_number', 'location_id', 'location__code')
                    #        'wanted_date', 'schedule_date'). \
                    # annotate(oqty=Coalesce(F('quantity'), V(0))). \
                    # annotate(dqty=Coalesce(F('delivery_quantity'), V(0))). \
                    # annotate(item__minimum_order=F('item'))
            else:
                orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                    customer_po_no=cust_po_no, item_id=item_id,
                                                    order__order_type=dict(ORDER_TYPE)['SALES ORDER']).exclude(order__document_number=ref_number). \
                    values('item_id', 'order_id', 'line_number', 'order__document_number', 'location_id', 'location__code')
                    #     'wanted_date', 'schedule_date'). \
                    # annotate(oqty=Coalesce(F('quantity'), V(0))). \
                    # annotate(dqty=Coalesce(F('delivery_quantity'), V(0))). \
                    # annotate(item__minimum_order=F('item'))

            item_ids = []

            for item_row in orderitems:
                item_ids.append(item_row['item_id'])

            loc_item_list = LocationItem.objects.filter(is_hidden=0). \
                values('item_id'). \
                filter(item_id__in=item_ids). \
                exclude(onhand_qty__isnull=True).exclude(onhand_qty__lt=0). \
                annotate(rfs_qty=Coalesce(Sum('booked_qty'), V(0)) - Coalesce(Sum('onhand_qty'), V(0)))

            loc_items = {}

            for loc_item in loc_item_list:
                loc_items[loc_item['item_id']] = loc_item['rfs_qty']

            for item in orderitems:
                data = {}
                data['doc_id'] = item['order_id']
                data['doc_no'] = item['order__document_number']
                data['ln_no'] = item['line_number']
                data['loc_id'] = item['location_id'] if item['location_id'] else ''
                data['loc_code'] = item['location__code'] if item['location__code'] else ''
                # data['backorder_qty'] = str(loc_items[item['item_id']]) if item['item_id'] in loc_items else '0'
                # order_qty = item['oqty'] if item['oqty'] else 0
                # delivery_qty = item['dqty'] if item['dqty'] else 0
                # data['qty'] = str(order_qty - delivery_qty)
                # data['wanted_date'] = item['wanted_date'].strftime("%Y-%m-%d") if item['wanted_date'] else ''
                # data['schedule_date'] = item['schedule_date'].strftime("%Y-%m-%d") if item['schedule_date'] else ''
                my_array.append(data)
    except Exception as e:
        print(e)
    
    json_content = json.dumps(my_array, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def get_orderitems_by_po_no(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        po_number = request.POST.get('po_number')
        supplier_id = request.POST.get('supplier_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order__id=po_number, supplier_id=int(supplier_id),
                                              order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                              receive_quantity__lt=F('quantity')) \
            .exclude(order__status=1).exclude(order__status=5).exclude(item_id__in=exclude_item_list)\
            .order_by('line_number')
        my_array = []
        for item in orderitems:
            if item.receive_quantity < 0:
                item.receive_quantity = 0
                item.save()
            data = {}
            data['item_id'] = str(item.item_id)
            data['purchase_price'] = str(item.price)
            data['item_name'] = str(item.item.name)
            data['code'] = str(item.item.code)
            data['refer_number'] = str(item.order.document_number)
            data['refer_line'] = str(item.line_number)
            data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
            data['location_code'] = str(item.location.code) if item.location else ''
            data['category'] = str(item.item.category.code) if item.item.category else ''
            data['currency_code'] = str(
                item.order.supplier.currency.code) if item.order.supplier and item.order.supplier.currency else ''
            data['location_id'] = str(item.location_id) if item.location else ''
            data['currency_id'] = str(
                item.order.supplier.currency_id) if item.order.supplier and item.order.supplier.currency else ''
            data['uom'] = str(item.item.purchase_measure.name) if item.item.purchase_measure else ''
            data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
            data['quantity'] = str(item.quantity) if item.quantity else '0'
            data['receive_quantity'] = str(item.receive_quantity) if item.receive_quantity else '0'
            data['minimun_order'] = str(item.item.minimun_order) if item.item.minimun_order else '0'
            data['customer_po_no'] = str(item.customer_po_no) if item.customer_po_no else ''
            data['refer_id'] = str(item.order_id) if item.order_id else None
            data['supplier_code'] = str(item.order.supplier.code) if item.order.supplier else ''
            data['outstanding_qty'] = float(data["quantity"]) - float(data["receive_quantity"])
            my_array.append(data)
        if my_array:
            json_content = json.dumps(my_array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps("something went wrong", ensure_ascii=False), content_type='application/json')


@login_required
def download_delivery_order(request, order_id):
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="DO_%s.zip' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order = Order.objects.get(pk=order_id)

    files = []
    # ================Print Print_Tax_Invoice=============
    report = Print_Tax_Invoice(BytesIO(), 'A4')
    pdf = report.print_report(order_id, '1', company_id, 0)
    files.append(
        ("TaxInvoice_%s_%s.pdf" % (order.document_number, datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), pdf))
    # ===============Print Print_Packing_List=============
    report = Print_Packing_List(BytesIO(), 'A4')
    pdf = report.print_report(order_id, '1', company_id, 0)
    files.append(
        ("PackingList_%s_%s.pdf" % (order.document_number, datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), pdf))
    # ===============Print Print_DO_Order==============
    report = Print_DO_Order(BytesIO(), 'A4')
    pdf = report.print_report(order_id, '1', company_id, 0)
    files.append(
        ("DeliveryOrder_%s_%s.pdf" % (order.document_number, datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), pdf))
    # =================End Print =======================
    buffer = BytesIO()
    zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    for name, f in files:
        zip.writestr(name, f)
    zip.close()
    buffer.flush()
    ret_zip = buffer.getvalue()
    buffer.close()
    response.write(ret_zip)
    return response


@login_required
@csrf_exempt
def customer_json_for_AR(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        list_filter = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(
                Q(code__icontains=search) | Q(name__icontains=search) | Q(payment_term__icontains=search) | Q(
                    credit_limit__icontains=search) | Q(payment_mode__name__icontains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "currency"
        elif order_column == "3":
            column_name = "payment_mode__name"
        elif order_column == "4":
            column_name = "credit_limit"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {}
            data["id"] = str(field.id)
            data["code"] = field.code if field.code else ''
            data["name"] = field.name if field.name else ''
            data["payment_term"] = str(field.payment_term) if field.payment_term else ''
            data["payment_mode"] = str(field.payment_mode.name) if field.payment_mode else ''
            data["credit_limit"] = str(field.credit_limit) if field.credit_limit else ''
            data['tax_id'] = str(field.tax_id) if field.tax else '0'
            data['currency_id'] = str(field.currency_id) if field.currency_id else '0'
            array.append(data)
        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
@csrf_exempt
def documents_list_as_json(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        try:
            draw = request.GET['draw']
            start = request.GET['start']
            length = request.GET['length']
            search = request.GET['search[value]']
            customer_id = request.GET['customer_id']
            do_orders = Order.objects.filter(company_id=company_id, is_hidden=0,
                                             order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                             customer_id=customer_id)
            if do_orders:
                records_total = do_orders.count()

                # Order by list_limit base on order_dir and order_column
                order_column = request.GET['order[0][column]']

                if search:  # Filter data base on search
                    do_orders = do_orders.filter(
                        Q(document_number=search) | Q(reference_number=search) | Q(customer__name=search))

                # All data
                records_filtered = do_orders.count()
                column_name = ""
                if order_column == "0":
                    column_name = "document_number"
                elif order_column == "1":
                    column_name = "invoice_date"
                elif order_column == "2":
                    column_name = "reference_number"
                elif order_column == "3":
                    column_name = "total"
                elif order_column == "4":
                    column_name = "customer__name"

                order_dir = request.GET['order[0][dir]']
                list = []
                if order_dir == "asc":
                    list = do_orders.order_by(column_name)[int(start):(int(start) + int(length))]
                elif order_dir == "desc":
                    list = do_orders.order_by('-' + column_name)[int(start):(int(start) + int(length))]

                # Create data list
                array = []
                for field in list:
                    data = {}
                    data["id"] = field.id if field.id else ''
                    data["code"] = str(field.document_number) if field.document_number else ''
                    data["date"] = str(field.invoice_date) if field.invoice_date else ''
                    data["reference"] = str(field.reference_number) if field.reference_number else ''
                    data["amount"] = str(field.total) if field.total else ''
                    data["customer_name"] = str(field.customer.name) if field.customer and field.customer.name else ''
                    array.append(data)

                content = {"draw": draw, "data": array, "recordsTotal": records_total,
                           "recordsFiltered": records_filtered}
                json_content = json.dumps(content, ensure_ascii=False)
                return HttpResponse(json_content, content_type='application/json')
            else:
                messages.add_message(request, messages.ERROR, 'Cannot find document', extra_tags='search_document')
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='search_document')
    return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
@csrf_exempt
def get_items_by_code(request):
    if request.is_ajax():
        part_id = request.POST.get('part_number')
        customer_id = request.POST.get('customer_id')
        supplier_id = request.POST.get('supplier_id')
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        item = Item.objects.get(pk=part_id)
        location_item = None
        customer_item = None
        if item:
            exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
                'exclude_item_list') else []

            supplieritems = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        supplier__company_id=company_id, supplier__is_hidden=0,
                                                        item_id=part_id)
            if supplier_id:
                supplieritems = supplieritems.filter(supplier_id=supplier_id).exclude(id__in=exclude_item_list)

            customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=part_id)
            if customer_id:
                customer_item = customer_item.filter(customer_id=customer_id).first()

            if item.default_location:
                location_item = LocationItem.objects.filter(is_hidden=0, item_id=item.id,
                                                            location_id=item.default_location_id).first()
            if not location_item:
                location_item = LocationItem.objects.filter(is_hidden=0, item_id=item.id).first()

            my_array = []
            for supplier_item in supplieritems:
                data = {}
                data['item_id'] = str(supplier_item.item.id)
                data['code'] = str(supplier_item.item.code) if supplier_item.item.code else ''
                data['item_name'] = str(supplier_item.item.name) if supplier_item.item.name else ''
                data['supplier_code'] = str(
                    supplier_item.supplier.code) if supplier_item.supplier and supplier_item.supplier.code else ''
                data['supplier_id'] = str(supplier_item.supplier_id) if supplier_item.supplier else ''
                if location_item:
                    data['location_code'] = str(
                        location_item.location.code) if location_item.location and location_item.location.code else ''
                    data['location_id'] = str(location_item.location.id) if location_item.location else ''
                else:
                    data['location_code'] = ''
                    data['location_id'] = ''
                data['category'] = str(supplier_item.item.category.code) if supplier_item.item.category else ''
                data['uom'] = str(supplier_item.item.sales_measure.name) if supplier_item.item.sales_measure else ''
                data['minimun_order'] = str(
                    supplier_item.item.minimun_order) if supplier_item.item.minimun_order else ''

                data['currency_id'] = str(
                    supplier_item.item.sale_currency_id) if supplier_item.item.sale_currency else ''
                data['currency_code'] = str(
                    supplier_item.item.sale_currency.code) if supplier_item.item.sale_currency and supplier_item.item.sale_currency.code else ''
                if supplier_id:
                    data['currency_id'] = str(supplier_item.currency_id) if supplier_item.currency else ''
                    data['currency_code'] = str(
                        supplier_item.currency.code) if supplier_item.currency and supplier_item.currency.code else ''
                    data['purchase_price'] = str(
                        supplier_item.purchase_price) if supplier_item.purchase_price else '0.00000'
                    try:
                        if (supplier_item.effective_date.strftime("%Y-%m-%d") <= datetime.datetime.now().strftime(
                                "%Y-%m-%d")):
                            data['purchase_price'] = str(
                                supplier_item.new_price) if supplier_item.new_price else supplier_item.purchase_price
                    except Exception as e:
                        print(e)

                if customer_id:
                    data['currency_id'] = str(customer_item.currency_id) if customer_item.currency else ''
                    data['currency_code'] = str(
                        customer_item.currency.code) if customer_item.currency and customer_item.currency.code else ''
                    data['sales_price'] = str(
                        customer_item.sales_price) if customer_item.sales_price else '0.00000'
                    try:
                        if (customer_item.effective_date.strftime("%Y-%m-%d") <= datetime.datetime.now().strftime(
                                "%Y-%m-%d")):
                            data['sales_price'] = str(
                                customer_item.new_price) if customer_item.new_price else customer_item.sales_price
                    except Exception as e:
                        print(e)

                my_array.append(data)
            if my_array:
                json_content = json.dumps(my_array, ensure_ascii=False)
                return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps("", ensure_ascii=False), content_type='application/json')


@login_required
@check_sp_closing
def sale_debit_credit_note_new(request, order_type, status):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()

    customer = Customer.objects.none()
    currency_symbol = Currency.objects.filter(is_hidden=0).first().symbol

    form_info = SaleCreditDebitNoteForm(company_id, order_type, request.POST)
    form_delivery = OrderDeliveryForm(company_id, request.POST)
    countries_list = Country.objects.filter(is_hidden=0)
    # Define formset
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(DOInvoiceForm)(partial(DOInvoiceForm, company_id)))

    if request.method == 'POST':
        try:
            with transaction.atomic():
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')
                order = Order()
                if 'is_sp_locked' in request.session and request.session['is_sp_locked']:
                    form_info = SaleCreditDebitNoteForm(company_id, order_type, initial={'tax': None, 'currency': None})
                    form_delivery = OrderDeliveryForm(company_id)
                    formset_item = ItemFormSet(prefix='formset_item')
                    formset_code = ExtraValueFormSetCode(prefix='formset_code')
                    return render(request, 'sale_debit_credit_note.html',
                                  {'form_info': form_info, 'order_type': order_type, 'formset_item': formset_item,
                                   'cus': customer,
                                   'countries_list': countries_list, 'form_delivery': form_delivery,
                                   'currency_symbol': currency_symbol, 'formset_code': formset_code,
                                   'request_method': request.method})

                if form_info.is_valid() and formset_item.is_valid() and form_delivery.is_valid():
                    order.customer_id = request.POST.get('hdCustomerId')
                    order.document_date = request.POST.get('document_date')
                    # order.order_code = request.POST.get('order_code')
                    order.currency_id = request.POST.get('currency')
                    if request.POST.get('transaction_code') == '9':
                        order.order_type = dict(ORDER_TYPE)['SALES DEBIT NOTE']
                    elif request.POST.get('transaction_code') == '8':
                        order.order_type = dict(ORDER_TYPE)['SALES CREDIT NOTE']
                    order.document_number = request.POST.get('document_number')
                    order.order_code = order.document_number
                    if request.POST.get('invoice_date'):
                        order.invoice_date = request.POST.get('invoice_date')
                    if request.POST.get('delivery_date'):
                        order.delivery_date = request.POST.get('delivery_date')
                    if request.POST.get('tax'):
                        order.tax_id = request.POST.get('tax')
                    if request.POST.get('discount'):
                        order.discount = Decimal(request.POST.get('discount'))
                    order.subtotal = Decimal(request.POST.get('subtotal'))
                    order.total = Decimal(request.POST.get('total'))
                    order.tax_amount = Decimal(request.POST.get('tax_amount'))
                    order.balance = order.total
                    if request.POST.get('cost_center'):
                        order.cost_center_id = request.POST.get('cost_center')
                    if request.POST.get('remark'):
                        order.remark = request.POST.get('remark')
                    order.create_date = datetime.datetime.today()
                    order.update_date = datetime.datetime.today()
                    order.update_by_id = request.user.id
                    order.is_hidden = False
                    order.company_id = company_id
                    try:
                        order.status = int(status)
                    except Exception as e:
                        print(e)
                        order.status = dict(ORDER_STATUS)['Draft']
                    order.save()

                    for form in formset_item:
                        reference_order = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                               document_number=form.cleaned_data.get(
                                                                   'ref_number')).first()
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity_do')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        if form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
                            order_item.location_id = form.cleaned_data.get('location').id
                        if reference_order:
                            order_item.reference_id = reference_order.id
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = form.cleaned_data.get('line_number')
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('currency')
                        order_item.stock_quantity = form.cleaned_data.get('quantity')
                        order_item.delivery_quantity = form.cleaned_data.get('quantity')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        order_item.origin_country_id = form.cleaned_data.get('origin_country_id')
                        order_item.description = form.cleaned_data.get('remark')
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = order.id
                        order_item.save()

                        # Update Stock
                        if int(status) >= dict(ORDER_STATUS)['Sent']:
                            # update item quantity
                            item_id = order_item.item_id
                            item = Item.objects.get(pk=item_id)
                            locationitem = LocationItem.objects.filter(is_hidden=0, item_id=item_id,
                                                                       location_id=order_item.location_id).last()
                            if locationitem:
                                locationitem.onhand_qty += order_item.quantity
                            item.last_purchase_price = order_item.price
                            item.last_purchase_date = datetime.datetime.today()
                            item.last_purchase_doc = order.document_number
                            if not item.cost_price or item.cost_price == 0:
                                item.cost_price = order_item.price
                            else:
                                item.cost_price = (order_item.price + item.cost_price) / 2
                            item.save()

                            # Update Return Quantity of Reference Order ( Reference Order is Delivery Order)
                            if reference_order.id:
                                refer_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                            order__company_id=company_id,
                                                                            order_id=reference_order.id,
                                                                            item_id=form.cleaned_data.get('item_id'),
                                                                            line_number=form.cleaned_data.get(
                                                                                'refer_line')).first()
                                if refer_order_item:
                                    refer_order_item.return_quantity = float(refer_order_item.return_quantity) + float(
                                        order_item.quantity)
                                    refer_order_item.update_date = datetime.datetime.today()
                                    refer_order_item.update_by_id = staff.id
                                    refer_order_item.save()

                    # Order Delivery process
                    order_delivery = form_delivery.save(commit=False)
                    order_delivery.order_id = order.id
                    order_delivery.create_date = datetime.datetime.today()
                    order_delivery.update_date = datetime.datetime.today()
                    order_delivery.update_by_id = request.user.id
                    order_delivery.is_hidden = 0
                    order_delivery.save()

                    return HttpResponseRedirect('/orders/list/' + str(order_type) + '/')
                else:
                    print("generate_DO_invoice form_info.errors, formset_item.errors, form_delivery.errors: ",
                          form_info.errors, formset_item.errors, form_delivery.errors)
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='sale_debit_credit_note_new')

    # end if POST
    form_info = SaleCreditDebitNoteForm(company_id, order_type, initial={'tax': None, 'currency': None})
    form_delivery = OrderDeliveryForm(company_id)
    formset_item = ItemFormSet(prefix='formset_item')
    formset_code = ExtraValueFormSetCode(prefix='formset_code')

    return render(request, 'sale_debit_credit_note.html',
                  {'form_info': form_info, 'order_type': order_type, 'formset_item': formset_item, 'cus': customer,
                   'countries_list': countries_list, 'form_delivery': form_delivery,
                   'currency_symbol': currency_symbol, 'formset_code': formset_code, 'request_method': request.method})


@login_required
@permission_required('orders.add_order', login_url='/alert/')
@check_sp_closing
def purchase_crdb_note_add(request, status):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)

    ItemFormSet = formset_factory(
        wraps(PurchaseCrDbNoteAddItem)(partial(PurchaseCrDbNoteAddItem, company_id=company_id)))
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()

    supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
    if not supplier:
        messages.add_message(request, messages.ERROR, "suppliers", extra_tags='order_new_empty_supplier')
        return HttpResponseRedirect(
            reverse('order_list', args=(), kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
    currency_symbol = Currency.objects.filter(is_hidden=0).first().symbol

    tax_id = supplier.tax_id if supplier.tax_id else ''

    if request.method == 'GET':
        form_info = PurchaseCrDbNoteInfoForm(
            company_id=request.session['login_company_id'] if request.session['login_company_id'] else 0,
            initial={'tax_id': tax_id, 'currency': supplier.currency if supplier.currency_id else ''})
        form = OrderHeaderForm()
        formset_right = ExtraValueFormSetRight(prefix='formset_right')
        formset_left = ExtraValueFormSetLeft(prefix='formset_left')
        formset_item = ItemFormSet(prefix='formset_item')
        formset_code = ExtraValueFormSetCode(prefix='formset_code')
        return render(request, 'purchase_crdb_note.html',
                      {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                       'formset_right': formset_right, 'formset_left': formset_left, 'formset_item': formset_item,
                       'supplier': supplier, 'formset_code': formset_code, 'request_method': request.method,
                       'currency_symbol': currency_symbol})
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form_info = PurchaseCrDbNoteInfoForm(request.POST, company_id=company_id)
                formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
                formset_item = ItemFormSet(request.POST, prefix='formset_item')

                if 'is_sp_locked' in request.session and request.session['is_sp_locked']:
                    form = OrderHeaderForm()
                    formset_right = ExtraValueFormSetRight(prefix='formset_right')
                    formset_left = ExtraValueFormSetLeft(prefix='formset_left')

                    return render(request, 'purchase_crdb_note.html',
                                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                                   'formset_right': formset_right, 'formset_left': formset_left,
                                   'formset_item': formset_item,
                                   'supplier': supplier, 'formset_code': formset_code, 'request_method': request.method,
                                   'currency_symbol': currency_symbol})
                if form_info.is_valid():
                    order = form_info.save(commit=False)
                    order.company_id = company_id
                    order.supplier_id = request.POST.get('hdSupplierId')
                    order.status = status
                    if request.POST.get('transaction_code') == '15':
                        order.order_type = dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']
                    elif request.POST.get('transaction_code') == '16':
                        order.order_type = dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']
                    if request.POST.get('document_date'):
                        doc_date = request.POST.get('document_date')
                    else:
                        doc_date = datetime.datetime.today()
                    order.document_date = doc_date
                    try:
                        order.status = int(status)
                    except Exception as e:
                        print(e)
                        order.status = dict(ORDER_STATUS)['Draft']
                    order.document_number = request.POST.get('document_number') if request.POST.get(
                        'document_number') else ''
                    order.create_date = datetime.datetime.today()
                    order.update_date = datetime.datetime.today()
                    order.update_by_id = request.user.id
                    order.is_hidden = 0
                    order.save()
                    if formset_item.is_valid():
                        for form_item in formset_item:
                            data = form_item.cleaned_data
                            orderitem = OrderItem()
                            orderitem.order_id = order.id
                            orderitem.reference_id = data.get('reference_id')
                            orderitem.refer_number = data.get('ref_number')
                            orderitem.refer_line = data.get('refer_line')
                            orderitem.item_id = data.get('item_id')
                            orderitem.quantity = data.get('quantity')
                            orderitem.customer_po_no = data.get('customer_po_no')
                            orderitem.price = Decimal(data.get('price'))
                            orderitem.amount = Decimal(data.get('amount'))
                            orderitem.description = data.get('description')
                            if form_item.cleaned_data.get('location'):
                                orderitem.location_id = data.get('location').id
                            orderitem.supplier_id = request.POST.get('hdSupplierId')
                            orderitem.from_currency_id = order.currency_id
                            orderitem.to_currency_id = order.currency_id
                            orderitem.line_number = data.get('line_number')
                            orderitem.create_date = datetime.datetime.today()
                            orderitem.update_date = datetime.datetime.today()
                            orderitem.update_by_id = request.user.id
                            orderitem.is_hidden = False
                            orderitem.save()
                            if int(status) >= dict(ORDER_STATUS)['Sent']:
                                # update item quantity
                                item_id = orderitem.item_id
                                item = Item.objects.get(pk=item_id)
                                locationitem = LocationItem.objects.filter(is_hidden=0, item_id=item_id,
                                                                           location_id=orderitem.location_id).last()
                                if locationitem:
                                    locationitem.onhand_qty -= orderitem.quantity
                                item.last_purchase_price = orderitem.price
                                item.last_purchase_date = datetime.datetime.today()
                                item.last_purchase_doc = order.document_number
                                if not item.cost_price or item.cost_price == 0:
                                    item.cost_price = orderitem.price
                                else:
                                    item.cost_price = (orderitem.price + item.cost_price) / 2
                                item.save()

                            # update Order Item
                            if form_item.cleaned_data.get('reference_id') and int(status) == dict(ORDER_STATUS)['Sent']:
                                # GR Order
                                gr_reference = Order.objects.get(pk=form_item.cleaned_data.get('reference_id'))
                                # update this orderitem of this purchase order
                                item_gr = OrderItem.objects.get(is_hidden=0, order__is_hidden=0,
                                                                order__company_id=company_id,
                                                                order_id=form_item.cleaned_data.get('reference_id'),
                                                                item_id=form_item.cleaned_data.get('item_id'),
                                                                line_number=form_item.cleaned_data.get('refer_line'))
                                if gr_reference and item_gr:
                                    item_gr.return_quantity += orderitem.quantity
                                    item_gr.update_date = datetime.datetime.today()
                                    item_gr.update_by_id = request.user.id
                                    item_gr.save()
                    else:
                        print("purchase_crdb_note_add formset_item.errors: ", formset_item.errors)

                    if formset_code.is_valid():
                        for form in formset_code:
                            if 'label' in form.cleaned_data and 'value' in form.cleaned_data:
                                order_header = form.save(commit=False)
                                order_header.x_position = 1
                                order_header.y_position = 2
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("purchase_crdb_note_add formset_code.errors: ", formset_code.errors)
                else:
                    print("purchase_crdb_note_edit form_info.errors: ", form_info.errors)
                return HttpResponsePermanentRedirect(
                    reverse('order_list', args=(), kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='pur_crdb_add')


@login_required
@permission_required('orders.change_order', login_url='/alert/')
@check_sp_closing
def purchase_crdb_note_edit(request, order_id, status):
    order = Order.objects.filter(id=order_id)
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if not order:
        return render_to_response('404.html',
                                  RequestContext(request, {'messages_error': 'No Order matches given queries'}))
    ExtraValueFormSetRight = formset_factory(ExtraValueFormRight)
    ExtraValueFormSetLeft = formset_factory(ExtraValueFormLeft)
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(
        wraps(PurchaseCrDbNoteAddItem)(partial(PurchaseCrDbNoteAddItem, company_id=company_id)))
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()
    supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).first()
    if not supplier:
        messages.add_message(request, messages.ERROR, "suppliers", extra_tags='order_new_empty_supplier')
        return HttpResponseRedirect(
            reverse('order_list', args=(), kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE INVOICE']}))
    tax_rate = Tax.objects.get(id=order.first().tax_id if order.first().tax_id else 0)
    if not tax_rate:
        tax_rate = 0
    else:
        tax_rate = tax_rate.rate / 100 if tax_rate.rate else 0
    currency_symbol = Currency.objects.filter(is_hidden=0).first().symbol

    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id,
                                          refer_line=F('reference__orderitem__line_number')) \
        .select_related('item_id', 'supplier_id').values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_id=F('supplier')) \
        .annotate(quantity_do=F('quantity')) \
        .annotate(currency_id=F('to_currency')) \
        .annotate(original_currency=F('to_currency__code')) \
        .annotate(location_id=F('location_id')) \
        .annotate(uom=F('item__sales_measure__name')) \
        .annotate(item_code=F('item__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(ref_number=F('refer_number')) \
        .annotate(order_quantity=F('reference__orderitem__quantity')) \
        .annotate(receive_quantity=F('reference__orderitem__return_quantity')) \
        .annotate(origin_country_code=F('origin_country__code')) \
        .annotate(remark=F('description'))
    if not order_item:
        order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order_id=order_id) \
            .select_related('item_id', 'supplier_id').values() \
            .annotate(item_name=F('item__name')) \
            .annotate(supplier_code=F('supplier__code')) \
            .annotate(supplier_id=F('supplier')) \
            .annotate(quantity_do=F('quantity')) \
            .annotate(currency_id=F('to_currency')) \
            .annotate(original_currency=F('to_currency__code')) \
            .annotate(location_code=F('location__code')) \
            .annotate(location_id=F('location__id')) \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(item_code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(ref_number=F('refer_number')) \
            .annotate(order_quantity=Value(0, output_field=models.CharField())) \
            .annotate(receive_quantity=Value(0, output_field=models.CharField())) \
            .annotate(remark=F('description'))
    trans_code = '1' if order.first().order_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE'] else '2'
    order_info = order.annotate(supplier_code=F('supplier__code')).annotate(
        transaction_code=Value(trans_code, output_field=models.CharField())).annotate(tax_code=F('tax__code'))

    if request.method == 'GET':
        form_info = PurchaseCrDbNoteInfoForm(company_id=company_id, instance=order_info.first(),
                                             initial={'transaction_code': trans_code})
        form = OrderHeaderForm()
        formset_right = ExtraValueFormSetRight(prefix='formset_right')
        formset_left = ExtraValueFormSetLeft(prefix='formset_left')
        formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
        formset_code = ExtraValueFormSetCode(prefix='formset_code')
        return render(request, 'purchase_crdb_note.html',
                      {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                       'tax_rate': tax_rate, 'formset_right': formset_right, 'formset_left': formset_left,
                       'order': order.first(), 'order_status': order.first().status, 'formset_item': formset_item,
                       'supplier': order.first().supplier, 'formset_code': formset_code,
                       'request_method': request.method, 'currency_symbol': currency_symbol})
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form_info = PurchaseCrDbNoteInfoForm(request.POST, company_id=company_id, instance=order_info.first())
                formset_code = ExtraValueFormSetCode(data=request.POST, prefix='formset_code')
                formset_item = ItemFormSet(data=request.POST, prefix='formset_item', initial=order_item)

                if 'is_sp_locked' in request.session and request.session['is_sp_locked']:
                    form = OrderHeaderForm()
                    formset_right = ExtraValueFormSetRight(prefix='formset_right')
                    formset_left = ExtraValueFormSetLeft(prefix='formset_left')

                    return render(request, 'purchase_crdb_note.html',
                                  {'company': company, 'media_url': s.MEDIA_URL, 'form': form, 'form_info': form_info,
                                   'formset_right': formset_right, 'formset_left': formset_left,
                                   'formset_item': formset_item,
                                   'supplier': supplier, 'formset_code': formset_code, 'request_method': request.method,
                                   'currency_symbol': currency_symbol})
                if form_info.is_valid():
                    order = form_info.save(commit=False)
                    order.company_id = company_id
                    order.supplier_id = request.POST.get('hdSupplierId')
                    order.status = status
                    if request.POST.get('transaction_code') == '5':
                        order.order_type = dict(ORDER_TYPE)['PURCHASE CREDIT NOTE']
                    elif request.POST.get('transaction_code') == '6':
                        order.order_type = dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']
                    if request.POST.get('document_date'):
                        doc_date = request.POST.get('document_date')
                    else:
                        doc_date = datetime.datetime.today()
                    order.document_date = doc_date

                    try:
                        order.status = int(status)
                    except Exception as e:
                        print(e)
                        order.status = dict(ORDER_STATUS)['Draft']
                    order.document_number = request.POST.get('document_number') if request.POST.get(
                        'document_number') else ''
                    order.create_date = datetime.datetime.today()
                    order.update_date = datetime.datetime.today()
                    order.update_by_id = request.user.id
                    order.is_hidden = 0
                    order.save()
                    if formset_item.is_valid():
                        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order_id=order_id).delete()
                        for form in formset_item:
                            data = form.cleaned_data
                            orderitem = OrderItem()
                            orderitem.order_id = order.id
                            orderitem.reference_id = data.get('reference_id')
                            orderitem.refer_line = data.get('refer_line')
                            orderitem.item_id = data.get('item_id')
                            orderitem.quantity = data.get('quantity')
                            orderitem.customer_po_no = data.get('customer_po_no')
                            orderitem.price = data.get('price')
                            orderitem.amount = data.get('amount')
                            orderitem.description = data.get('description')
                            if form.cleaned_data.get('location'):
                                orderitem.location_id = data.get('location').id
                            orderitem.supplier_id = request.POST.get('hdSupplierId')
                            orderitem.from_currency_id = order.currency_id
                            orderitem.to_currency_id = order.currency_id
                            orderitem.line_number = data.get('line_number')
                            orderitem.create_date = datetime.datetime.today()
                            orderitem.update_date = datetime.datetime.today()
                            orderitem.update_by_id = request.user.id
                            orderitem.is_hidden = False
                            orderitem.save()

                            if int(status) >= dict(ORDER_STATUS)['Sent']:
                                # update item quantity
                                item_id = order_item.item_id
                                item = Item.objects.get(pk=item_id)
                                locationitem = LocationItem.objects.filter(is_hidden=0, item_id=item_id,
                                                                           location_id=order_item.location_id).last()
                                if locationitem:
                                    locationitem.onhand_qty -= order_item.quantity
                                item.last_purchase_price = orderitem.price
                                item.last_purchase_date = datetime.datetime.today()
                                item.last_purchase_doc = order.document_number
                                if not item.cost_price or item.cost_price == 0:
                                    item.cost_price = orderitem.price
                                else:
                                    item.cost_price = (orderitem.price + item.cost_price) / 2
                                item.save()

                            # update Order Item
                            if form.cleaned_data.get('reference_id') and int(status) >= dict(ORDER_STATUS)['Sent']:
                                # GR Order
                                gr_reference = Order.objects.get(pk=form.cleaned_data.get('reference_id'))
                                # update this orderitem of this purchase order
                                item_gr = OrderItem.objects.get(is_hidden=0, order__is_hidden=0,
                                                                order__company_id=company_id,
                                                                order_id=form.cleaned_data.get('reference_id'),
                                                                item_id=form.cleaned_data.get('item_id'),
                                                                line_number=form.cleaned_data.get('refer_line'))
                                if gr_reference and item_gr:
                                    item_gr.return_quantity += form.cleaned_data.get('quantity')
                                    item_gr.update_date = datetime.datetime.today()
                                    item_gr.update_by_id = request.user.id
                                    item_gr.save()
                    else:
                        print("purchase_crdb_note_edit formset_item.errors: ", formset_item.errors)

                    if formset_code.is_valid():
                        for form in formset_code:
                            if 'label' in form.cleaned_data and 'value' in form.cleaned_data:
                                order_header = form.save(commit=False)
                                order_header.x_position = 1
                                order_header.y_position = 2
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("purchase_crdb_note_edit formset_code.errors: ", formset_code.errors)
                else:
                    print("purchase_crdb_note_edit form_info.errors: ", form_info.errors)

                return HttpResponsePermanentRedirect(
                    reverse('order_list', args=(), kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='pur_crdb_add')


@login_required
@csrf_exempt
def good_receive_item_list_as_json(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        supplier_id = request.GET['supplier_id']

        if supplier_id == '0':
            items_list = OrderItem.objects.none()
        else:
            items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  supplier_id=supplier_id,
                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
                exclude(order__status=dict(ORDER_STATUS)['Draft']). \
                exclude(quantity__lte=F('receive_quantity')).values('item_id'). \
                annotate(item_name=F('item__name')). \
                annotate(description=F('description')). \
                annotate(amount=F('amount')). \
                annotate(supplier_code=F('supplier__code')). \
                annotate(supplier_id=F('supplier_id')). \
                annotate(order_type=F('order__order_type')). \
                annotate(ref_id=F('order_id')).annotate(ref_number=F('order__document_number')). \
                annotate(ref_line=F('line_number')). \
                annotate(currency_id=F('supplier__currency')). \
                annotate(currency=F('supplier__currency__code')). \
                annotate(location_code=F('location__code')). \
                annotate(location_id=F('location_id')). \
                annotate(purchase_price=F('item__purchase_price')). \
                annotate(code=F('item__code')).annotate(category=F('item__category__code')). \
                annotate(uom=F('item__purchase_measure__name')). \
                annotate(minimun_order=F('quantity')). \
                annotate(customer_po_no=F('customer_po_no')). \
                annotate(order_quantity=F('quantity')). \
                annotate(receive_quantity=F('receive_quantity')). \
                annotate(line_id=Value(0, output_field=models.CharField())). \
                exclude(order_quantity=F('receive_quantity'))

        records_total = items_list.count()

        if search:  # Filter data base on search
            items_list = items_list.filter(Q(customer_po_no__icontains=search) | Q(item__code__icontains=search) | Q(
                item__category__code__icontains=search) | Q(location__code__icontains=search) | Q(
                order__document_number__icontains=search) | Q(item__code__icontains=search) | Q(
                order__supplier__code__icontains=search))

        # All data
        records_filtered = items_list.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "1":
            column_name = "item__name"
        elif order_column == "2":
            column_name = "suppier__code"
        elif order_column == "3":
            column_name = "order__document_number"
        elif order_column == "4":
            column_name = "line_number"
        elif order_column == "5":
            column_name = "location__code"
        elif order_column == "6":
            column_name = "item__code"
        elif order_column == "7":
            column_name = "item__category__code"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = items_list.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = items_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        for i, j in enumerate(list):
            if (i < list.__len__()):
                i += 1
                j['line_id'] = i

        # Create data list
        array = []
        for field in list:
            data = {}
            data["item_id"] = str(field['item_id'])
            if str(field['item_name']) != 'None' and str(field['item_name']):
                data["item_name"] = str(field['item_name'])
            else:
                data["item_name"] = ''
            if str(field['supplier_code']) != 'None' and str(field['supplier_code']):
                data["supplier_code"] = str(field['supplier_code'])
            else:
                data["supplier_code"] = ''
            if str(field['ref_number']) != 'None' and str(field['ref_number']):
                data["refer_number"] = str(field['ref_number'])
            else:
                data["refer_number"] = ''
            data["refer_line"] = str(field['ref_line'])
            if str(field['location_code']) != 'None' and str(field['location_code']):
                data["location_code"] = str(field['location_code'])
            else:
                data["location_code"] = ''
            if str(field['code']) != 'None' and str(field['code']):
                data["code"] = str(field['code'])
            else:
                data["code"] = ''
            if str(field['category']) != 'None' and str(field['category']):
                data["category"] = str(field['category'])
            else:
                data["category"] = ''
            supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        item_id=field['item_id'],
                                                        supplier_id=field['supplier_id']).last()
            if supplier_item:
                data["purchase_price"] = str(supplier_item.purchase_price)
            else:
                data["purchase_price"] = '0'
            if str(field['currency']) != 'None' and str(field['currency']):
                data["currency_code"] = str(field['currency'])
            else:
                data["currency_code"] = ''
            if str(field["location_id"]) != 'None' and str(field['location_id']):
                data["location_id"] = str(field['location_id'])
            else:
                data["location_id"] = ''
            if str(field["currency_id"]) != 'None' and str(field['currency_id']):
                data["currency_id"] = str(field['currency_id'])
            else:
                data["currency_id"] = ''
            data["line_id"] = str(field['line_id'])
            if str(field["uom"]) != 'None' and str(field['uom']):
                data["unit"] = str(field['uom'])
            else:
                data["unit"] = ''
            if str(field["supplier_id"]) != 'None' and str(field['supplier_id']):
                data["supplier_id"] = str(field['supplier_id'])
            else:
                data["supplier_id"] = ''
            if str(field['minimun_order']) != 'None' and str(field['minimun_order']):
                data["minimun_order"] = str(field['minimun_order'])
            else:
                data["minimun_order"] = ''
            if str(field['ref_id']) != 'None' and str(field['ref_id']):
                data["refer_id"] = str(field['ref_id'])
            else:
                data["refer_id"] = ''
            if str(field['customer_po_no']) != 'None' and str(field['customer_po_no']):
                data["customer_po_no"] = str(field['customer_po_no'])
            else:
                data["customer_po_no"] = ''
            data["order_qty"] = '0'
            data["receive_qty"] = '0'
            data['outstanding_qty'] = '0'
            if str(field['order_quantity']) != 'None' and str(field['order_quantity']):
                data["order_qty"] = str(field['order_quantity'])
                data["receive_qty"] = str(field['receive_quantity'])
                data["outstanding_qty"] = str(field['order_quantity'] - field['receive_quantity'])
            data['description'] = str(field['description']) if field['description'] else ''
            data['amount'] = str(field['amount']) if field['amount'] else ''

            array.append(data)

        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def load_doList__asJson(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        customer_id = request.GET['customer_id']

        if customer_id == '0':
            items_list = OrderItem.objects.none()
        else:
            if 'exclude_item_list' in request.GET:
                exclude_item_json = request.GET['exclude_item_list']
                exclude_item_list = json.loads(exclude_item_json)
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__customer_id=customer_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES INVOICE']). \
                    exclude(item_id__in=exclude_item_list). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']). \
                    exclude(quantity__lte=F('return_quantity')).values('item_id'). \
                    annotate(code=F('item__code')). \
                    annotate(item_name=F('item__name')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(reference_id=F('reference_id')). \
                    annotate(reference_line=F('refer_line')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(sales_price=F('price')). \
                    annotate(currency_code=F('order__customer__currency__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(currency_id=F('order__customer__currency')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(delivery_quantity=F('return_quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))
            else:
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__customer_id=customer_id,
                                                      order__order_type=dict(ORDER_TYPE)['SALES INVOICE']). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                    annotate(code=F('item__code')). \
                    annotate(item_name=F('item__name')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(reference_id=F('reference_id')). \
                    annotate(reference_line=F('refer_line')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(sales_price=F('price')). \
                    annotate(currency_code=F('order__customer__currency__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(currency_id=F('order__customer__currency')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(delivery_quantity=F('return_quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))

        records_total = items_list.count()
        if search:  # Filter data base on search
            items_list = items_list.filter(Q(item__name__contains=search) | Q(item__code__contains=search) | Q(
                order__document_number__contains=search) | Q(supplier__code__contains=search) | Q(
                location__code__contains=search))

        # All data
        records_filtered = items_list.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "1":
            column_name = "item__code"
        elif order_column == "2":
            column_name = "item__name"
        elif order_column == "3":
            column_name = "order__document_number"
        elif order_column == "4":
            column_name = "line_number"
        elif order_column == "5":
            column_name = "supplier__code"
        elif order_column == "6":
            column_name = "location__code"
        elif order_column == "7":
            column_name = "item__category__code"
        elif order_column == "8":
            column_name = "price"
        elif order_column == "9":
            column_name = "order__customer__currency"
        elif order_column == "15":
            column_name = "quantity"
        elif order_column == "16":
            column_name = "delivery_quantity"
        elif order_column == "17":
            column_name = "customer_po_no"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = items_list.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = items_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        for i, j in enumerate(list):
            if (i < list.__len__()):
                i += 1
                j['line_id'] = i

        # Create data list
        array = []
        for field in list:
            data = {}
            data["item_id"] = str(field['item_id'])
            if str(field['item_name']) != 'None' and str(field['item_name']):
                data["item_name"] = str(field['item_name'])
            else:
                data["item_name"] = ''
            if str(field['supplier_code']) != 'None' and str(field['supplier_code']):
                data["supplier_code"] = str(field['supplier_code'])
            else:
                data["supplier_code"] = ''
            if str(field['ref_number']) != 'None' and str(field['ref_number']):
                data["refer_number"] = str(field['ref_number'])
            else:
                data["refer_number"] = ''
            data["refer_line"] = str(field['ref_line'])
            if str(field['location_code']) != 'None' and str(field['location_code']):
                data["location_code"] = str(field['location_code'])
            else:
                data["location_code"] = ''
            if str(field['code']) != 'None' and str(field['code']):
                data["code"] = str(field['code'])
            else:
                data["code"] = ''
            if str(field['category']) != 'None' and str(field['category']):
                data["category"] = str(field['category'])
            else:
                data["category"] = ''
            if str(field['sales_price']) != 'None' and str(field['sales_price']):
                data["sales_price"] = str(field['sales_price'])
            else:
                data["sales_price"] = ''
            if str(field['currency_code']) != 'None' and str(field['currency_code']):
                data["currency_code"] = str(field['currency_code'])
            else:
                data["currency_code"] = ''
            if str(field['currency_id']) != 'None' and str(field['currency_id']):
                data["currency_id"] = str(field['currency_id'])
            else:
                data["currency_id"] = ''
            if str(field["location_id"]) != 'None' and str(field['location_id']):
                data["location_id"] = str(field['location_id'])
            else:
                data["location_id"] = ''
            data["line_id"] = str(field['line_id'])
            if str(field["uom"]) != 'None' and str(field['uom']):
                data["unit"] = str(field['uom'])
            else:
                data["unit"] = ''
            if str(field["supplier_id"]) != 'None' and str(field['supplier_id']):
                data["supplier_id"] = str(field['supplier_id'])
            else:
                data["supplier_id"] = ''
            if str(field['customer_po_no']) != 'None' and str(field['customer_po_no']):
                data["customer_po_no"] = str(field['customer_po_no'])
            else:
                data["customer_po_no"] = ''

            data["order_qty"] = str(field['order_quantity'] if field['order_quantity'] else '0')
            data["delivery_qty"] = str(field['delivery_quantity'] if field['delivery_quantity'] else '0')

            array.append(data)

        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@csrf_exempt
def load_grList__asJson(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        supplier_id = request.GET['supplier_id']

        if supplier_id == '0':
            items_list = OrderItem.objects.none()
        else:
            if 'exclude_item_list' in request.GET:
                exclude_item_json = request.GET['exclude_item_list']
                exclude_item_list = json.loads(exclude_item_json)
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      supplier_id=supplier_id,
                                                      order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']). \
                    exclude(item_id__in=exclude_item_list). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                    annotate(item_name=F('item__name')). \
                    annotate(description=F('description')). \
                    annotate(amount=F('amount')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_type=F('order__order_type')). \
                    annotate(ref_id=F('order_id')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(currency_id=F('supplier__currency')). \
                    annotate(currency=F('supplier__currency__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(purchase_price=F('item__purchase_price')). \
                    annotate(item_code=F('item__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(minimun_order=F('quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(receive_quantity=F('return_quantity')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))
            else:
                items_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      supplier_id=supplier_id,
                                                      order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']). \
                    exclude(order__status=dict(ORDER_STATUS)['Draft']).values('item_id'). \
                    annotate(item_name=F('item__name')). \
                    annotate(description=F('description')). \
                    annotate(amount=F('amount')). \
                    annotate(supplier_code=F('supplier__code')). \
                    annotate(supplier_id=F('supplier_id')). \
                    annotate(order_type=F('order__order_type')). \
                    annotate(ref_id=F('order_id')). \
                    annotate(ref_number=F('order__document_number')). \
                    annotate(ref_line=F('line_number')). \
                    annotate(currency_id=F('supplier__currency')). \
                    annotate(currency=F('supplier__currency__code')). \
                    annotate(location_code=F('location__code')). \
                    annotate(location_id=F('location_id')). \
                    annotate(purchase_price=F('item__purchase_price')). \
                    annotate(item_code=F('item__code')). \
                    annotate(category=F('item__category__code')). \
                    annotate(uom=F('item__purchase_measure__name')). \
                    annotate(minimun_order=F('quantity')). \
                    annotate(customer_po_no=F('customer_po_no')). \
                    annotate(order_quantity=F('quantity')). \
                    annotate(receive_quantity=F('return_quantity')). \
                    annotate(line_id=Value(0, output_field=models.CharField()))

        records_total = items_list.count()

        if search:  # Filter data base on search
            items_list = items_list.filter(Q(customer_po_no__icontains=search) | Q(item__code__icontains=search) | Q(
                item__category__code__icontains=search) | Q(location__code__icontains=search))

        # All data
        records_filtered = items_list.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "1":
            column_name = "item__code"
        elif order_column == "2":
            column_name = "item__name"
        elif order_column == "3":
            column_name = "item__purchase_measure__name"
        elif order_column == "4":
            column_name = "item__category__code"
        elif order_column == "5":
            column_name = "quantity"
        elif order_column == "6":
            column_name = "item__purchase_price"
        elif order_column == "7":
            column_name = "location__code"
        elif order_column == "8":
            column_name = "supplier_code"
        elif order_column == "9":
            column_name = "customer_po_no"
        elif order_column == "10":
            column_name = "ref_number"
        elif order_column == "11":
            column_name = "ref_line"
        elif order_column == "12":
            column_name = "order_quantity"
        elif order_column == "13":
            column_name = "receive_quantity"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = items_list.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = items_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        for i, j in enumerate(list):
            if (i < list.__len__()):
                i += 1
                j['line_id'] = i

        # Create data list
        array = []
        for field in list:
            data = {}
            data["item_id"] = str(field['item_id'])
            if str(field['item_name']) != 'None' and str(field['item_name']):
                data["item_name"] = str(field['item_name'])
            else:
                data["item_name"] = ''
            if str(field['supplier_code']) != 'None' and str(field['supplier_code']):
                data["supplier_code"] = str(field['supplier_code'])
                data["supplier_id"] = str(field['supplier_id'])
            else:
                data["supplier_code"] = ''
                data["supplier_id"] = ''
            if str(field['ref_number']) != 'None' and str(field['ref_number']):
                data["ref_number"] = str(field['ref_number'])
            else:
                data["ref_number"] = ''
            data["ref_line"] = str(field['ref_line'])
            if str(field['location_code']) != 'None' and str(field['location_code']):
                data["location_code"] = str(field['location_code'])
            else:
                data["location_code"] = ''
            if str(field['item_code']) != 'None' and str(field['item_code']):
                data["item_code"] = str(field['item_code'])
            else:
                data["item_code"] = ''
            if str(field['category']) != 'None' and str(field['category']):
                data["category"] = str(field['category'])
            else:
                data["category"] = ''
            supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        item_id=field['item_id'],
                                                        supplier_id=field['supplier_id']).last()
            if supplier_item:
                data["purchase_price"] = str(supplier_item.purchase_price)
            else:
                data["purchase_price"] = '0'
            if str(field['currency']) != 'None' and str(field['currency']):
                data["currency_code"] = str(field['currency'])
            else:
                data["currency_code"] = ''
            if str(field["location_id"]) != 'None' and str(field['location_id']):
                data["location_id"] = str(field['location_id'])
            else:
                data["location_id"] = ''
            if str(field["currency_id"]) != 'None' and str(field['currency_id']):
                data["currency_id"] = str(field['currency_id'])
            else:
                data["currency_id"] = ''
            data["line_id"] = str(field['line_id'])
            if str(field["uom"]) != 'None' and str(field['uom']):
                data["unit"] = str(field['uom'])
            else:
                data["unit"] = ''
            if str(field["supplier_id"]) != 'None' and str(field['supplier_id']):
                data["supplier_id"] = str(field['supplier_id'])
            else:
                data["supplier_id"] = ''
            if str(field['minimun_order']) != 'None' and str(field['minimun_order']):
                data["minimun_order"] = str(field['minimun_order'])
            else:
                data["minimun_order"] = ''
            if str(field['ref_id']) != 'None' and str(field['ref_id']):
                data["refer_id"] = str(field['ref_id'])
            else:
                data["refer_id"] = ''
            if str(field['customer_po_no']) != 'None' and str(field['customer_po_no']):
                data["customer_po_no"] = str(field['customer_po_no'])
            else:
                data["customer_po_no"] = ''
            if str(field['order_quantity']) != 'None' and str(field['order_quantity']):
                data["order_qty"] = str(field['order_quantity'])
                data["receive_qty"] = str(field['receive_quantity'])
            else:
                data["order_qty"] = ''
                data["receive_qty"] = ''
            data['description'] = str(field['description']) if field['description'] else ''
            data['amount'] = str(field['amount']) if field['amount'] else ''
            array.append(data)

        content = {"draw": draw, "data": array, "recordsTotal": records_total, "recordsFiltered": records_filtered}
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@login_required
@check_sp_closing
def sale_debit_credit_note_edit(request, order_id, order_type, copy_id, is_send):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    order = Order.objects.get(pk=order_id)
    order_status = order.status
    staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()
    customer = Customer.objects.get(pk=order.customer_id)
    if not customer:
        messages.add_message(request, messages.ERROR, "customers", extra_tags='order_new_empty_customer')
        return HttpResponseRedirect(
            reverse('order_list', args=(), kwargs={'order_type': dict(ORDER_TYPE)['PURCHASE SALES NOTE']}))

    currency_symbol = Currency.objects.filter(is_hidden=0).first().symbol
    order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=order_id,
                                          refer_line=F('reference__orderitem__line_number')) \
        .select_related('item_id', 'supplier_id').values() \
        .annotate(item_name=F('item__name')) \
        .annotate(supplier_code=F('supplier__code')) \
        .annotate(supplier_code_id=F('supplier')) \
        .annotate(quantity_do=F('quantity')) \
        .annotate(currency_id=F('to_currency')) \
        .annotate(original_currency=F('to_currency__code')) \
        .annotate(location=F('location_id')) \
        .annotate(uom=F('item__sales_measure__name')) \
        .annotate(code=F('item__code')) \
        .annotate(category=F('item__category__code')) \
        .annotate(ref_number=F('refer_number')) \
        .annotate(order_quantity=F('reference__orderitem__quantity')) \
        .annotate(delivery_quantity=F('reference__orderitem__return_quantity')) \
        .annotate(origin_country_code=F('origin_country__code')) \
        .annotate(remark=F('description'))
    if not order_item:
        order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order_id=order_id) \
            .select_related('item_id', 'supplier_id').values() \
            .annotate(item_name=F('item__name')) \
            .annotate(supplier_code=F('supplier__code')) \
            .annotate(supplier_code_id=F('supplier')) \
            .annotate(quantity_do=F('quantity')) \
            .annotate(currency_id=F('to_currency')) \
            .annotate(original_currency=F('to_currency__code')) \
            .annotate(location_id=F('location__id')) \
            .annotate(uom=F('item__sales_measure__name')) \
            .annotate(code=F('item__code')) \
            .annotate(category=F('item__category__code')) \
            .annotate(ref_number=F('refer_number')) \
            .annotate(order_quantity=Value(0, output_field=models.CharField())) \
            .annotate(delivery_quantity=Value(0, output_field=models.CharField())) \
            .annotate(remark=F('description'))

    kwargs, contact = get_order_delivery_kwargs(company_id, customer.id, order_id)

    extra_code = OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                            order_id=order_id, x_position=1, y_position=2).values()
    form_info = OrderInfoForm(company_id, order_type, request.POST)
    items_list = OrderItem.objects.none()
    form_delivery = OrderDeliveryForm(company_id, request.POST, **kwargs)
    countries_list = Country.objects.filter(is_hidden=0)
    tax_rate = Tax.objects.get(id=order.tax_id if order.tax_id else 0)
    if not tax_rate:
        tax_rate = 0
    else:
        tax_rate = tax_rate.rate / 100 if tax_rate.rate else 0
    # Define formset
    ExtraValueFormSetCode = formset_factory(ExtraValueFormCode)
    ItemFormSet = formset_factory(wraps(DOInvoiceForm)(partial(DOInvoiceForm, company_id)))

    formset_code = ExtraValueFormSetCode(request.POST, prefix='formset_code')
    formset_item = ItemFormSet(request.POST, prefix='formset_item')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                form_info = SaleCreditDebitNoteForm(company_id, order_type, request.POST, instance=order)
                form_delivery = OrderDeliveryForm(company_id, **kwargs)

                if 'is_sp_locked' in request.session and request.session['is_sp_locked']:
                    return render(request, 'sale_debit_credit_note.html',
                                  {'form_info': form_info, 'order': order,
                                   'order_type': order_type, 'formset_item': formset_item, 'cus': customer,
                                   'status': order_status,
                                   'countries_list': countries_list, 'form_delivery': form_delivery, 'contact': contact,
                                   'currency_symbol': currency_symbol, 'tax_rate': tax_rate,
                                   'formset_code': formset_code, 'request_method': request.method, 'copy_id': copy_id})

                if form_info.is_valid() and formset_item.is_valid():
                    info = form_info.save(commit=False)
                    info.id = order_id
                    info.company_id = company_id
                    info.customer_id = request.POST.get('hdCustomerId')
                    info.document_number = request.POST.get('document_number')
                    if request.POST.get('transaction_code') == '8':
                        info.order_type = dict(ORDER_TYPE)['SALES DEBIT NOTE']
                    elif request.POST.get('transaction_code') == '7':
                        info.order_type = dict(ORDER_TYPE)['SALES CREDIT NOTE']
                    if request.POST.get('cost_center'):
                        info.cost_center_id = request.POST.get('cost_center')
                    else:
                        info.cost_center_id = None
                    if request.POST.get('tax'):
                        info.tax_id = request.POST.get('tax')
                    else:
                        info.tax_id = None
                    if int(is_send) == 1:
                        info.status = dict(ORDER_STATUS)['Sent']
                    info.balance = info.total
                    info.create_date = datetime.datetime.today()
                    info.update_date = datetime.datetime.today()
                    info.update_by_id = request.user.id
                    info.is_hidden = 0
                    info.save()

                    if formset_code.is_valid():
                        OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id, x_position=1, y_position=2).delete()
                        for form in formset_code:
                            order_header = OrderHeader()
                            if form.cleaned_data.get('label') is not None and form.cleaned_data.get(
                                    'value') is not None:
                                order_header.x_position = 1
                                order_header.y_position = 2
                                order_header.label = form.cleaned_data.get('label')
                                order_header.value = form.cleaned_data.get('value')
                                order_header.create_date = datetime.datetime.today()
                                order_header.update_date = datetime.datetime.today()
                                order_header.update_by_id = request.user.id
                                order_header.is_hidden = False
                                order_header.order_id = order.id
                                order_header.save()
                    else:
                        print("sale_debit_credit_note_edit formset_code.errors: ", formset_code.errors)
                        OrderHeader.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id, x_position=1, y_position=2).delete()

                    order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order_id=order_id)
                    for order_item in order_item_list:
                        order_item.delete()
                    for form in formset_item:
                        reference_order = Order.objects.filter(is_hidden=0, company_id=company_id,
                                                               document_number=form.cleaned_data.get(
                                                                   'ref_number')).first()
                        order_item = OrderItem()
                        order_item.item_id = form.cleaned_data.get('item_id')
                        order_item.supplier_id = form.cleaned_data.get('supplier_code_id')
                        order_item.customer_po_no = form.cleaned_data.get('customer_po_no')
                        order_item.quantity = form.cleaned_data.get('quantity_do')
                        order_item.exchange_rate = form.cleaned_data.get('exchange_rate')
                        if form.cleaned_data.get('location') and form.cleaned_data.get('location') != 'None':
                            order_item.location_id = form.cleaned_data.get('location').id
                        if reference_order:
                            order_item.reference_id = reference_order.id
                        order_item.refer_number = form.cleaned_data.get('ref_number')
                        order_item.refer_line = form.cleaned_data.get('refer_line')
                        order_item.line_number = form.cleaned_data.get('line_number')
                        order_item.from_currency_id = form.cleaned_data.get('currency_id')
                        order_item.to_currency_id = request.POST.get('currency')
                        order_item.stock_quantity = form.cleaned_data.get('order_quantity')
                        order_item.delivery_quantity = form.cleaned_data.get('delivery_quantity')
                        order_item.price = form.cleaned_data.get('price')
                        order_item.amount = form.cleaned_data.get('amount')
                        order_item.origin_country_id = form.cleaned_data.get('origin_country_id')
                        order_item.description = form.cleaned_data.get('remark')
                        order_item.create_date = datetime.datetime.today()
                        order_item.update_date = datetime.datetime.today()
                        order_item.update_by_id = request.user.id
                        order_item.is_hidden = False
                        order_item.order_id = order.id
                        order_item.save()

                        # Update Stock
                        if int(is_send) == 1:
                            # update item quantity
                            item_id = order_item.item_id
                            item = Item.objects.get(pk=item_id)
                            locationitem = LocationItem.objects.filter(is_hidden=0, item_id=item_id,
                                                                       location_id=order_item.location_id).last()
                            if locationitem:
                                locationitem.onhand_qty += order_item.quantity
                            item.last_purchase_price = order_item.price
                            item.last_purchase_date = datetime.datetime.today()
                            item.last_purchase_doc = order.document_number
                            if not item.cost_price or item.cost_price == 0:
                                item.cost_price = order_item.price
                            else:
                                item.cost_price = (order_item.price + item.cost_price) / 2
                            item.save()

                            # Update Return Quantity of Reference Order ( Reference Order is Delivery Order)
                            if reference_order is not None:
                                refer_order_item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                            order__company_id=company_id,
                                                                            order_id=reference_order.id,
                                                                            item_id=form.cleaned_data.get('item_id'),
                                                                            line_number=form.cleaned_data.get(
                                                                                'refer_line')).first()
                                if refer_order_item:
                                    refer_order_item.return_quantity = float(refer_order_item.return_quantity) + float(
                                        order_item.quantity)
                                    refer_order_item.update_date = datetime.datetime.today()
                                    refer_order_item.update_by_id = staff.id
                                    refer_order_item.save()

                    # Order Delivery process
                    if form_delivery.is_valid():
                        order_delivery = form_delivery.save(commit=False)
                        order_delivery.order_id = order_id
                        order_delivery.create_date = datetime.datetime.today()
                        order_delivery.update_date = datetime.datetime.today()
                        order_delivery.update_by_id = request.user.id
                        order_delivery.is_hidden = 0
                        order_delivery.save()
                    else:
                        print("sale_debit_credit_note_edit form_delivery.errors: ", form_delivery.errors)

                    return HttpResponseRedirect('/orders/list/' + str(order_type) + '/')
                else:
                    print("sale_debit_credit_note_edit form_info.errors, formset_item.errors: ", form_info.errors,
                          formset_item.errors)
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='sale_debit_credit_note_new')
    else:
        form_info = SaleCreditDebitNoteForm(company_id, order_type, instance=order)
        form_info.initial.update({'document_type': order.order_type})
        form_delivery = OrderDeliveryForm(company_id, **kwargs)
        formset_item = ItemFormSet(prefix='formset_item', initial=order_item)
        formset_code = ExtraValueFormSetCode(prefix='formset_code', initial=extra_code)
    return render(request, 'sale_debit_credit_note.html',
                  {'form_info': form_info, 'order': order,
                   'order_type': order_type, 'formset_item': formset_item, 'cus': customer, 'status': order_status,
                   'countries_list': countries_list, 'form_delivery': form_delivery, 'contact': contact,
                   'currency_symbol': currency_symbol, 'tax_rate': tax_rate,
                   'formset_code': formset_code, 'request_method': request.method, 'copy_id': copy_id})


@login_required
@csrf_exempt
def get_orderitems_by_gr_no(request):
    if request.is_ajax() and request.POST.get('gr_number') and request.POST.get('supplier_id'):
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        gr_number = request.POST.get('gr_number')
        supplier_id = request.POST.get('supplier_id')
        if request.POST.get('exclude_item_list'):
            exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
                'exclude_item_list') != '[""]' else []
        orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order__document_number__exact=gr_number,
                                              supplier_id=int(supplier_id),
                                              order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                              return_quantity__lt=F('quantity')).exclude(order__status=1)

        my_array = []
        for item in orderitems:
            data = {}
            data['item_id'] = str(item.item_id)
            data['item_name'] = str(item.item.name)
            data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
            data['refer_number'] = gr_number
            data['refer_line'] = str(item.line_number)
            data['location_code'] = str(item.location.code) if item.location else ''
            data['item_code'] = str(item.item.code)
            data['category'] = str(item.item.category.code) if item.item.category else ''
            data['purchase_price'] = str(item.price)
            data['currency_code'] = str(
                item.order.supplier.currency.code) if item.order.supplier and item.order.supplier.currency else ''
            data['location_id'] = str(item.location_id) if item.location else ''
            data['currency_id'] = str(
                item.order.supplier.currency_id) if item.order.supplier and item.order.supplier.currency else ''
            data['uom'] = str(item.item.purchase_measure.name) if item.item.purchase_measure else ''
            data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
            data['minimun_order'] = str(item.quantity)
            data['order_qty'] = str(item.quantity)
            data['receive_qty'] = str(item.return_quantity)
            data['customer_po_no'] = str(item.customer_po_no)
            data['refer_id'] = str(item.order_id)
            data['description'] = str(item.description) if item.description else ''
            data['amount'] = str(item.amount) if item.amount else '0'
            my_array.append(data)
        if my_array:
            json_content = json.dumps(my_array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps("", ensure_ascii=False), content_type='application/json')


@login_required
@csrf_exempt
def get_orderitems_by_do_no(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        do_number = request.POST.get('do_number')
        customer_id = request.POST.get('customer_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order__document_number__exact=do_number,
                                              order__customer_id=int(customer_id),
                                              order__order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                              return_quantity__lt=F('quantity')).exclude(order__status=1)
        my_array = []
        for item in orderitems:
            data = {}
            data['item_id'] = str(item.item_id)
            data['sales_price'] = str(item.price)
            data['item_name'] = str(item.item.name)
            data['item_code'] = str(item.item.code)
            data['refer_number'] = do_number
            data['refer_line'] = str(item.line_number)
            data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
            data['location_code'] = str(item.location.code) if item.location else ''
            data['category'] = str(item.item.category.code) if item.item.category else ''
            data['currency_code'] = str(
                item.order.customer.currency.code) if item.order.customer and item.order.customer.currency else ''
            data['location_id'] = str(item.location_id) if item.location else ''
            data['currency_id'] = str(
                item.order.customer.currency_id) if item.order.customer and item.order.customer.currency else ''
            data['uom'] = str(item.item.sales_measure.name) if item.item.sales_measure else ''
            data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
            data['quantity'] = str(item.quantity)
            data['delivery_quantity'] = str(item.return_quantity)
            data['customer_po_no'] = str(item.customer_po_no)
            data['customer_code'] = str(item.order.customer.code) if item.order.customer else ''
            my_array.append(data)
        if my_array:
            json_content = json.dumps(my_array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')


def push_doc_qty_to_inv_qty(request, orderitem_id, last_qty=None, last_order_status=None, is_delete=False):
    result = []
    obj = {}
    update_location_item_log = order_vs_inventory(request).save_location_item(orderitem_id, last_qty, last_order_status,
                                                                              is_delete)
    if update_location_item_log and len(update_location_item_log) > 0:
        for log1 in update_location_item_log:
            obj['log'] = log1
            obj['tag'] = 'update_locationitem_failed'
            result.append(obj)

    save_item_file_log = order_vs_inventory(request).save_item_file_qty(orderitem_id, last_qty, last_order_status,
                                                                        is_delete)
    if save_item_file_log and len(save_item_file_log) > 0:
        for log2 in save_item_file_log:
            obj['log'] = log2
            obj['tag'] = 'update_itemfile_failed'
            result.append(obj)

    return result


def expanded_order(request, order_id, order_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                          order_id=int(order_id), order__order_type=order_type).order_by('line_number')
    my_array = []
    for item in orderitems:
        if item.to_currency:
            if item.to_currency.is_decimal:
                amount = round_number(item.amount)
            else:
                amount = round_number(item.amount, 0)
        else:
            amount = round_number(item.amount)

        data = {}
        data['item_id'] = str(item.item_id)
        data['sales_price'] = str(item.price)
        data['item_name'] = str(item.item.name)
        data['item_code'] = str(item.item.code)
        data['line_number'] = str(item.line_number)
        data['refer_line'] = str(item.refer_line)
        data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
        data['location_code'] = str(item.location.code) if item.location else ''
        data['category'] = str(item.item.category.code) if item.item.category else ''
        data['currency_code'] = str(
            item.order.customer.currency.code) if item.order.customer and item.order.customer.currency else ''
        data['location_id'] = str(item.location_id) if item.location else ''
        data['currency_id'] = str(
            item.order.customer.currency_id) if item.order.customer and item.order.customer.currency else ''
        data['uom'] = str(item.item.sales_measure.name) if item.item.sales_measure else ''
        data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
        data['quantity'] = intcomma("%.2f" % item.quantity)
        data['delivery_quantity'] = str(item.return_quantity)
        data['customer_po_no'] = str(item.customer_po_no)
        data['customer_code'] = str(item.order.customer.code) if item.order.customer else ''
        data['amount'] = str(amount)
        data['ref_number'] = item.reference.document_number if item.reference else ''
        my_array.append(data)
    json_content = json.dumps(my_array, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def location_code_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    locations = Location.objects.filter(is_hidden=False, company_id=company_id, is_active=1)

    my_array = []
    for item in locations:
        data = {}
        data['location_id'] = str(item.id)
        data['location_code'] = str(item.code)
        my_array.append(data)
    json_content = json.dumps(my_array, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def check_so_po_reference(request, reference_id, order_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if order_type == 'SO':
        refer_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                               order__company_id=company_id,
                                               reference_id=reference_id,
                                               order__order_type__in=[dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                      dict(ORDER_TYPE)['SALES INVOICE']])
    elif order_type == 'PO':
        refer_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                               order__company_id=company_id,
                                               reference_id=reference_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'])
    data = {}
    if len(refer_items):
        order_items = []
        for refer in refer_items:
            order_item = {
                'refer_id': refer.id,
                'refer_number': refer.refer_number,
                'refer_line': refer.refer_line,
                'new_refer_line': 0,
                'customer_po_no': refer.customer_po_no,
                'new_customer_po_no': '',
                'order_id': refer.order.id,
                'order_code': refer.order.order_code,
                'order_code_line': refer.line_number
            }
            order_items.append(order_item)
        data = {
            'reference_exists': True,
            'order_items': order_items
        }
    else:
        data = {
            'reference_exists': False,
            'order_items': []
        }
    json_content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def check_quantity_po_so_reference(request, reference_id, order_type, refer_line):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if order_type == 'SO':
        refer_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                               order__company_id=company_id,
                                               reference_id=reference_id,
                                               refer_line=refer_line,
                                               order__order_type=dict(ORDER_TYPE)['SALES INVOICE'])
    elif order_type == 'PO':
        refer_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                               order__company_id=company_id,
                                               reference_id=reference_id,
                                               refer_line=refer_line,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'])
    data = {}
    total_quantity = 0;
    if len(refer_items):
        order_items = []
        for refer in refer_items:
            order_item = {
                'refer_id': refer.id,
                'line_number': refer.line_number,
                'refer_number': refer.refer_number,
                'refer_line': refer.refer_line,
                'new_refer_line': 0,
                'customer_po_no': refer.customer_po_no,
                'new_customer_po_no': '',
                'order_id': refer.order.id,
                'document_number': refer.order.document_number,
                'order_code': refer.order.order_code,
                'quantity': intcomma("%.2f" % refer.quantity)
            }
            order_items.append(order_item)
        data = {
            'reference_exists': True,
            'total_quantity': intcomma("%.2f" % refer_items.aggregate(Sum('quantity')).get('quantity__sum', 0)),
            'order_items': order_items
        }
    else:
        data = {
            'reference_exists': False,
            'total_quantity': 0,
            'order_items': []
        }
    json_content = json.dumps(data, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@csrf_exempt
def get_order_item_by_po_no(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        po_numbers = eval(request.POST.get('po_number'))
        supplier_id = request.POST.get('supplier_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order__id__in=po_numbers, supplier_id=int(supplier_id),
                                              order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(order__status=1).exclude(order__status=5).exclude(item_id__in=exclude_item_list)\
            .order_by('line_number')
        
        my_array = []
        for item in orderitems:
            if item.receive_quantity < 0:
                item.receive_quantity = 0
                item.save()
            data = {}
            data['item_id'] = str(item.item_id)
            data['purchase_price'] = str(item.price)
            data['item_name'] = str(item.item.name)
            data['code'] = str(item.item.code)
            data['refer_number'] = str(item.order.document_number)
            data['refer_line'] = str(item.line_number)
            data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
            data['location_code'] = str(item.location.code) if item.location else ''
            data['category'] = str(item.item.category.code) if item.item.category else ''
            data['currency_code'] = str(
                item.order.supplier.currency.code) if item.order.supplier and item.order.supplier.currency else ''
            data['location_id'] = str(item.location_id) if item.location else ''
            data['currency_id'] = str(
                item.order.supplier.currency_id) if item.order.supplier and item.order.supplier.currency else ''
            data['uom'] = str(item.item.purchase_measure.name) if item.item.purchase_measure else ''
            data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
            data['quantity'] = str(item.quantity) if item.quantity else '0'
            data['receive_quantity'] = str(item.receive_quantity) if item.receive_quantity else '0'
            data['minimun_order'] = str(item.item.minimun_order) if item.item.minimun_order else '0'
            data['customer_po_no'] = str(item.customer_po_no) if item.customer_po_no else ''
            data['refer_id'] = str(item.order_id) if item.order_id else None
            data['supplier_code'] = str(item.order.supplier.code) if item.order.supplier else ''
            data['outstanding_qty'] = float(data["quantity"]) - float(data["receive_quantity"])
            my_array.append(data)
        if my_array:
            json_content = json.dumps(my_array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps("something went wrong", ensure_ascii=False), content_type='application/json')


@login_required
@csrf_exempt
def get_order_item_by_so_no(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        so_numbers = eval(request.POST.get('so_number'))
        customer_id = request.POST.get('customer_id')
        exclude_item_list = json.loads(request.POST.get('exclude_item_list')) if request.POST.get(
            'exclude_item_list') else []
        if customer_id == '':
            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__id__in=so_numbers,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=1).exclude(order__status=4).exclude(item_id__in=exclude_item_list).order_by('line_number')
        else:
            orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__id__in=so_numbers,
                                                  order__customer_id=customer_id,
                                                  order__order_type=dict(ORDER_TYPE)['SALES ORDER']). \
                exclude(order__status=1).exclude(order__status=4).exclude(item_id__in=exclude_item_list).order_by('line_number')

        my_array = []
        for item in orderitems:
            data = {}
            data['item_id'] = str(item.item_id)
            data['minimum_order'] = str(item.item.minimun_order) if item.item.minimun_order else 0
            data['sales_price'] = str(item.price)
            data['item_name'] = str(item.item.name)
            data['item_code'] = str(item.item.code)
            data['refer_id'] = str(item.order_id) if item.order_id else None
            data['refer_number'] = str(item.order.document_number)
            data['refer_line'] = str(item.line_number)
            data['description'] = str(item.description)
            data['schedule_date'] = item.schedule_date.strftime("%Y-%m-%d") if item.schedule_date else ''
            data['wanted_date'] = item.wanted_date.strftime("%Y-%m-%d") if item.wanted_date else ''
            data['supplier_code'] = str(item.supplier.code) if item.supplier else ''
            data['location_code'] = str(item.location.code) if item.location else ''
            data['category'] = str(item.item.category.code) if item.item.category else ''
            data['currency_code'] = str(
                item.order.customer.currency.code) if item.order.customer and item.order.customer.currency else ''
            data['location_id'] = str(item.location_id) if item.location else ''
            data['currency_id'] = str(
                item.order.customer.currency_id) if item.order.customer and item.order.customer.currency else ''
            data['uom'] = str(item.item.sales_measure.name) if item.item.sales_measure else ''
            data['supplier_id'] = str(item.supplier_id) if item.supplier else ''
            data['quantity'] = str(item.quantity)
            data['backorder_qty'] = str(item.bkord_quantity) if item.bkord_quantity else 0
            data['delivery_quantity'] = str(item.delivery_quantity) if item.delivery_quantity else 0
            data['customer_po_no'] = str(item.customer_po_no)
            data['customer_code'] = str(
                item.order.customer.code) if item.order.customer and item.order.customer.code else ''
            data['country_origin_id'] = str(item.item.country_id) if item.item.country_id else ''
            data['country_origin_cd'] = str(
                item.item.country.code) if item.item.country and item.item.country.code else ''
            try:
                loc_item = LocationItem.objects. \
                    filter(item_id=item.item_id,
                           location__company_id=company_id,
                           location_id=item.location_id,
                           is_hidden=False,
                           location__is_hidden=False)
                if loc_item:
                    loc_item = loc_item.aggregate(sum_onhand_qty=Coalesce(Sum('onhand_qty'), V(0)))
                    data["location_item_quantity"] = str(loc_item.get('sum_onhand_qty'))
                else:
                    qty_gr = 0
                    po_list = order_vs_inventory(request).get_next_doc_detail(item.id)
                    if po_list:
                        for po in po_list:
                            gr_list = order_vs_inventory(request).get_next_doc_detail(po.id)
                            if gr_list:
                                for gr in gr_list:
                                    qty_gr += gr.quantity
                    data["location_item_quantity"] = str(qty_gr)

            except Exception as e:
                print(e)
                data["location_item_quantity"] = '0'

            my_array.append(data)
        if my_array:
            json_content = json.dumps(my_array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
    return HttpResponse(json.dumps("something went wrong", ensure_ascii=False), content_type='application/json')


@login_required
def export_part_purchase_price_file(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    supplier_list = request.POST.get('param0')
    part_grp_list = request.POST.get('param1')
    part_no_list = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'Part_Purchase_Price_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = EXPORT_PURCHASE_PRICE_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, supplier_list, part_grp_list, part_no_list)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response

@login_required
def export_part_purchase_price(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    supp_ids = SupplierItem.objects.filter(is_hidden=0, is_active=1).order_by('supplier_id').values_list('supplier_id', flat=True).distinct()
    item_ids = SupplierItem.objects.filter(is_hidden=0, is_active=1).order_by('item_id').values_list('item_id', flat=True).distinct()
    supplier_list = Supplier.objects.filter(is_hidden=False, company_id=company_id, id__in=supp_ids).exclude(code=None).order_by('code').values_list('id', 'code').distinct()
    part_no_list = Item.objects.filter(is_hidden=False, company_id=company_id, id__in=item_ids).exclude(code=None).order_by('code').values_list('id', 'code').distinct()
    part_grp_list = ItemCategory.objects.filter(is_hidden=False, company_id=company_id).exclude(code=None).order_by('code').values_list('id', 'code').distinct()

    return render_to_response('export_part_purchase_price.html', RequestContext(request, {
                                'supplier_list': supplier_list, 
                                'part_no_list': part_no_list, 
                                'part_grp_list': part_grp_list}))


@login_required
def export_part_sales_price_file(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    customer_list = request.POST.get('param0')
    part_grp_list = request.POST.get('param1')
    part_no_list = request.POST.get('param2')
    include_supp = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'Part_Sales_Price_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = EXPORT_SALE_PRICE_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, customer_list, part_grp_list, part_no_list, include_supp)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response

@login_required
def export_part_sales_price(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    cust_ids = CustomerItem.objects.filter(is_hidden=0, is_active=1).order_by('customer_id').values_list('customer_id', flat=True).distinct()
    item_ids = CustomerItem.objects.filter(is_hidden=0, is_active=1).order_by('item_id').values_list('item_id', flat=True).distinct()
    customer_list = Customer.objects.filter(is_hidden=False, company_id=company_id, id__in=cust_ids).exclude(code=None).order_by('code').values_list('id', 'code').distinct()
    part_no_list = Item.objects.filter(is_hidden=False, company_id=company_id, id__in=item_ids).exclude(code=None).order_by('code').values_list('id', 'code').distinct()
    part_grp_list = ItemCategory.objects.filter(is_hidden=False, company_id=company_id).exclude(code=None).order_by('code').values_list('id', 'code').distinct()

    return render_to_response('export_part_sales_price.html', RequestContext(request, {
                                'customer_list': customer_list, 
                                'part_no_list': part_no_list, 
                                'part_grp_list': part_grp_list}))
