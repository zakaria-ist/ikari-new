import json
import logging
import re
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN, InvalidOperation
from datetime import datetime, timedelta
from functools import wraps
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.mail import EmailMessage
from django.db.models import Q, Sum, Value as V
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from accounting.models import FiscalCalendar, Journal, Batch, APOptions, AROptions, RecurringBatch
from accounts.models import Account
from companies.models import Company, CostCenters
from currencies.models import ExchangeRate
from customers.models import Customer, Delivery
from accounting.models import RecurringEntry
from inventory.models import StockTransaction, StockTransactionDetail, TransactionCode
from items.models import Item, ItemCategory
from locations.models import LocationItem
from orders.models import Order, OrderItem, OrderDelivery
from suppliers.models import Supplier
from transactions.models import Transaction
from utilities.constants import AP_FUNCTION_LIST, AR_FUNCTION_LIST, GL_FUNCTION_LIST, BANK_FUNCTION_LIST, \
    SEND_FUNCTION_LIST, SOURCE_TYPE_APPLICATION, ORDER_STATUS, ORDER_TYPE, INV_IN_OUT_FLAG, TRN_CODE_TYPE_DICT, \
    INPUT_TYPE_DICT, STATUS_TYPE_DICT, TRANSACTION_TYPES_REVERSED, SOURCE_LEDGER_DICT, DOCUMENT_TYPE_DICT, \
    EXCHANGE_RATE_TYPE, BALANCE_TYPE_DICT, TRANSACTION_TYPES
from utilities.messages import FISCAL_LOCKED_ERROR, BANK_FISCAL_LOCKED_ERROR, SEND_FISCAL_LOCKED_ERROR, CHECK_IC_LOCKED, \
    CHECK_SP_LOCKED, UPDATE_LOCATION_ITEM_FAILED, UPDATE_ITEM_FILE_FAILED, UPDATE_REF_QTY_FAILED, MESSAGE_ERROR, \
    RV_ERR_CREATE_BATCH, DRAFT_BATCH_FAILED, BATCH_ERROR, CREATE_JOURNAL_FAILED, DRAFT_JOURNAL_FAILED, \
    REFRESH_OR_GO_GET_SUPPORT, DELETE_DRAFT_JOURNAL_FAILED, EXCEPTION_JOURNAL_ADD
from .constants import MSG_APPLY_CONTENT, MSG_APPLY_SUBJECT

logger = logging.getLogger(__name__)


def check_fiscal(func):
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        request.session['is_locked'] = False

        source_type = ""
        if func.__name__ in AP_FUNCTION_LIST:
            source_type = "1"
        elif func.__name__ in AR_FUNCTION_LIST:
            source_type = "2"
        elif func.__name__ in GL_FUNCTION_LIST:
            source_type = "3"
        elif func.__name__ in BANK_FUNCTION_LIST:
            source_type = "4"

        if request.method == 'POST':
            if 'document_date' in request.POST:
                document_date = request.POST['document_date']
                document_date = datetime.strptime(document_date, '%Y-%m-%d')
                if re.search('payment', func.__name__, re.IGNORECASE) or re.search('receipt', func.__name__,
                                                                                   re.IGNORECASE):
                    field_date = "Payment Date"
                else:
                    field_date = "Document Date"

                fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                              start_date__lte=document_date,
                                                              end_date__gte=document_date).first()
                if fiscal_period:
                    check_lock = get_check_lock(fiscal_period, source_type)

                    if check_lock:
                        messages.error(request, FISCAL_LOCKED_ERROR % (
                            field_date, document_date.date(), fiscal_period.period, fiscal_period.start_date,
                            fiscal_period.end_date, fiscal_period.fiscal_year,
                            SOURCE_TYPE_APPLICATION.get(source_type)))
                        request.session['is_locked'] = True

            if 'posting_date' in request.POST:
                posting_date = request.POST['posting_date']
                posting_date = datetime.strptime(posting_date, '%Y-%m-%d')
                fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                              start_date__lte=posting_date,
                                                              end_date__gte=posting_date).first()
                if fiscal_period:
                    check_lock = get_check_lock(fiscal_period, source_type)

                    if check_lock:
                        messages.error(request, FISCAL_LOCKED_ERROR % (
                            'Posting date', posting_date.date(), fiscal_period.period, fiscal_period.start_date,
                            fiscal_period.end_date, fiscal_period.fiscal_year,
                            SOURCE_TYPE_APPLICATION.get(source_type)))
                        request.session['is_locked'] = True

        elif request.method == 'GET':
            if func.__name__ in SEND_FUNCTION_LIST:
                if 'batch_id' in kwargs:
                    journal_list = Journal.objects.filter(is_hidden=False, batch_id=kwargs['batch_id'], company_id=company_id)
                    for journal in journal_list:
                        if journal.document_date:
                            document_date = datetime.strptime(str(journal.document_date), '%Y-%m-%d')
                            if re.search('payment', func.__name__, re.IGNORECASE) or re.search('receipt', func.__name__,
                                                                                               re.IGNORECASE):
                                field_date = "Payment Date"
                            else:
                                field_date = "Document Date"

                            fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                          start_date__lte=document_date,
                                                                          end_date__gte=document_date).first()
                            if fiscal_period:
                                check_lock = get_check_lock(fiscal_period, source_type)

                                if check_lock:
                                    messages.error(request, SEND_FISCAL_LOCKED_ERROR % (
                                        journal.code, field_date, document_date.date(), fiscal_period.period,
                                        fiscal_period.start_date, fiscal_period.end_date, fiscal_period.fiscal_year,
                                        SOURCE_TYPE_APPLICATION.get(source_type)))
                                    request.session['is_locked'] = True

                        if journal.posting_date:
                            posting_date = datetime.strptime(str(journal.posting_date), '%Y-%m-%d')
                            fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                          start_date__lte=posting_date,
                                                                          end_date__gte=posting_date).first()
                            if fiscal_period:
                                check_lock = get_check_lock(fiscal_period, source_type)

                                if check_lock:
                                    messages.error(request, SEND_FISCAL_LOCKED_ERROR % (
                                        journal.code, 'Posting date', posting_date.date(), fiscal_period.period,
                                        fiscal_period.start_date, fiscal_period.end_date, fiscal_period.fiscal_year,
                                        SOURCE_TYPE_APPLICATION.get(source_type)))
                                    request.session['is_locked'] = True
            else:
                if 'journal_id' in kwargs:
                    journal = Journal.objects.get(pk=kwargs['journal_id'])

                    if journal.document_date:
                        document_date = datetime.strptime(str(journal.document_date), '%Y-%m-%d')
                        if re.search('payment', func.__name__, re.IGNORECASE) or re.search('receipt', func.__name__,
                                                                                           re.IGNORECASE):
                            field_date = "Payment Date"
                        else:
                            field_date = "Document Date"

                        fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                      start_date__lte=document_date,
                                                                      end_date__gte=document_date).first()
                        if fiscal_period:
                            check_lock = get_check_lock(fiscal_period, source_type)

                            if check_lock:
                                messages.error(request, FISCAL_LOCKED_ERROR % (
                                    field_date, document_date.date(), fiscal_period.period, fiscal_period.start_date,
                                    fiscal_period.end_date, fiscal_period.fiscal_year,
                                    SOURCE_TYPE_APPLICATION.get(source_type)))

                    if journal.posting_date:
                        posting_date = datetime.strptime(str(journal.posting_date), '%Y-%m-%d')
                        fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                      start_date__lte=posting_date,
                                                                      end_date__gte=posting_date).first()
                        if fiscal_period:
                            check_lock = get_check_lock(fiscal_period, source_type)

                            if check_lock:
                                messages.error(request, FISCAL_LOCKED_ERROR % (
                                    'Posting date', posting_date.date(), fiscal_period.period, fiscal_period.start_date,
                                    fiscal_period.end_date, fiscal_period.fiscal_year,
                                    SOURCE_TYPE_APPLICATION.get(source_type)))
                else:
                    # today = datetime.today().date()
                    today = request.session['session_date']
                    if re.search('payment', func.__name__, re.IGNORECASE) or re.search('receipt', func.__name__,
                                                                                       re.IGNORECASE):
                        field_date = "Payment Date"
                    else:
                        field_date = "Document Date"

                    fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                  start_date__lte=today,
                                                                  end_date__gte=today).first()
                    if fiscal_period:
                        check_lock = get_check_lock(fiscal_period, source_type)

                        if check_lock and source_type != '4':
                            messages.error(request, FISCAL_LOCKED_ERROR % (
                                field_date, today, fiscal_period.period, fiscal_period.start_date,
                                fiscal_period.end_date,
                                fiscal_period.fiscal_year, SOURCE_TYPE_APPLICATION.get(source_type)))
                            messages.error(request, FISCAL_LOCKED_ERROR % (
                                'Posting date', today, fiscal_period.period, fiscal_period.start_date,
                                fiscal_period.end_date, fiscal_period.fiscal_year,
                                SOURCE_TYPE_APPLICATION.get(source_type)))
                        elif check_lock and source_type == '4':
                            messages.error(request, BANK_FISCAL_LOCKED_ERROR % (
                                'Reversal Date', today, fiscal_period.period, fiscal_period.start_date,
                                fiscal_period.end_date, fiscal_period.fiscal_year))
        return func(request, *args, **kwargs)

    def get_check_lock(fiscal_period, source_type):
        check_lock = False
        if source_type == '1':
            check_lock = fiscal_period.is_ap_locked
        elif source_type == '2':
            check_lock = fiscal_period.is_ar_locked
        elif source_type == '3':
            check_lock = fiscal_period.is_gl_locked
        elif source_type == '4':
            check_lock = fiscal_period.is_bank_locked
        return check_lock

    return wrapped


def check_inventory_closing(func):
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        request.session['is_inventory_locked'] = False
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if request.method == 'POST':
            if 'document_date' in request.POST and request.POST['document_date']:
                document_date = request.POST['document_date']
                document_date = datetime.strptime(document_date, '%Y-%m-%d')
                fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0,
                                                              start_date__lte=document_date,
                                                              end_date__gte=document_date).first()
                if fiscal_period and fiscal_period.is_ic_locked:
                    request.session['is_inventory_locked'] = True
                    messages.error(request, CHECK_IC_LOCKED % (
                        fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
        elif request.method == 'GET':
            if 'stock_trans_id' in kwargs and kwargs['stock_trans_id']:
                stock_trans = StockTransaction.objects.get(pk=kwargs['stock_trans_id'])

                if stock_trans.document_date:
                    document_date = datetime.strptime(str(stock_trans.document_date), '%Y-%m-%d')
                    fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                  start_date__lte=document_date,
                                                                  end_date__gte=document_date).first()

                    if fiscal_period and fiscal_period.is_ic_locked:
                        request.session['is_inventory_locked'] = True
                        messages.error(request, CHECK_IC_LOCKED % (
                            fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
            elif 'order_id' in kwargs and kwargs['order_id']:
                order = Order.objects.get(pk=kwargs['order_id'])

                if order.document_date:
                    document_date = datetime.strptime(str(order.document_date), '%Y-%m-%d')
                    fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                  start_date__lte=document_date,
                                                                  end_date__gte=document_date).first()

                    if fiscal_period and fiscal_period.is_ic_locked:
                        request.session['is_inventory_locked'] = True
                        messages.error(request, CHECK_IC_LOCKED % (
                            fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
            else:
                today = datetime.today().date()
                fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                              start_date__lte=today,
                                                              end_date__gte=today).first()

                if fiscal_period and fiscal_period.is_ic_locked:
                    request.session['is_inventory_locked'] = True
                    messages.error(request, CHECK_IC_LOCKED % (
                        fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
        return func(request, *args, **kwargs)

    return wrapped


def check_sp_closing(func):
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        request.session['is_sp_locked'] = False
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if request.method == 'POST':
            if 'document_date' in request.POST and request.POST['document_date']:
                document_date = request.POST['document_date']
                document_date = datetime.strptime(document_date, '%Y-%m-%d')
                fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                              start_date__lte=document_date,
                                                              end_date__gte=document_date).first()

                if fiscal_period and fiscal_period.is_sp_locked:
                    request.session['is_sp_locked'] = True
                    messages.error(request, CHECK_SP_LOCKED % (
                        fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
        elif request.method == 'GET':
            if 'order_id' in kwargs and kwargs['order_id']:
                order = Order.objects.get(pk=kwargs['order_id'])

                if order.document_date:
                    document_date = datetime.strptime(str(order.document_date), '%Y-%m-%d')
                    fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                                  start_date__lte=document_date,
                                                                  end_date__gte=document_date).first()

                    if fiscal_period and fiscal_period.is_sp_locked:
                        request.session['is_sp_locked'] = True
                        messages.error(request, CHECK_SP_LOCKED % (
                            fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))
            else:
                today = datetime.today().date()
                fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                              start_date__lte=today,
                                                              end_date__gte=today).first()

                if fiscal_period and fiscal_period.is_sp_locked:
                    request.session['is_sp_locked'] = True
                    messages.error(request, CHECK_SP_LOCKED % (
                        fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date))

        return func(request, *args, **kwargs)

    return wrapped


@csrf_exempt
def load_fiscal_period(request):
    if request.is_ajax():
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            today = datetime.today().date()
            last_month = datetime.today().month - 1
            fiscal_period = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=False,
                                                          fiscal_year=today.year, period=last_month).first()
            response_data = {}
            if fiscal_period:
                response_data['period'] = fiscal_period.period if fiscal_period.period else ''
                response_data['start_date'] = fiscal_period.start_date if fiscal_period.start_date else ''
                response_data['end_date'] = fiscal_period.end_date if fiscal_period.end_date else ''
                response_data['msg'] = None

                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='search_location_code')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


def to_string(s):
    if s is None:
        return ''
    else:
        return str(s)


def validate_date_to_from(delivery_from, delivery_to):
    delivery_to_obj = delivery_from_obj = None
    try:
        if delivery_from != '0':
            delivery_from_obj = datetime.strptime(delivery_from, '%Y-%m-%d')
    except Exception as e:
        print(e)

    try:
        if delivery_to != '0':
            delivery_to_obj = datetime.strptime(delivery_to, '%Y-%m-%d')
    except Exception as e:
        print(e)

    if not delivery_to_obj:
        delivery_to_obj = datetime.now() + relativedelta(years=1)

    if not delivery_from_obj:
        delivery_from_obj = datetime.now() - relativedelta(years=100)

    return delivery_from_obj, delivery_to_obj


def get_index_of_value(list_evaluated, list, item_key):
    index = []

    try:
        list = list[::-1]
        value = list.pop()
    except Exception as e:
        return index

    for i, item in enumerate(list_evaluated):
        if item[item_key] == value:
            index.append(i)
            try:
                value = list.pop()
            except Exception as e:
                print(e)

    return index


def update_po_address(order_id, address_id=None):
    try:
        order = Order.objects.get(pk=int(order_id))
        order_delivery = OrderDelivery.objects.filter(order_id=order.id, is_hidden=0).first()
        if address_id:
            address = Delivery.objects.get(pk=address_id)
        else:
            address = None
        if address:
            if order_delivery:
                order_delivery.delivery_id = address_id
                order_delivery.name = address.name
                order_delivery.address = address.address
                order_delivery.phone = address.phone
                order_delivery.note_1 = address.note_1
                order_delivery.update_date = datetime.today()
                order_delivery.save()
            else:
                order_delivery = OrderDelivery()
                order_delivery.order_id = order.id
                order_delivery.delivery_id = address_id
                order_delivery.name = address.name
                order_delivery.address = address.address
                order_delivery.phone = address.phone
                order_delivery.note_1 = address.note_1
                order_delivery.save()
        else:
            if order_delivery:
                order_delivery.delivery_id = None
                order_delivery.name = ''
                order_delivery.address = ''
                order_delivery.phone = ''
                order_delivery.note_1 = ''
                order_delivery.is_hidden = 1
                order_delivery.update_date = datetime.today()
                order_delivery.save()

    except Exception as e:
        print(e)


def get_order_filter_range(order_type, company_id, doc_no_from, doc_no_to, item_key):
    order_list = Order.objects.filter(is_hidden=0, company_id=company_id, order_type=order_type)

    filter_key = item_key + '__in'
    filters = {filter_key: (doc_no_from, doc_no_to)}
    order_list = order_list.order_by(item_key)

    order_docno_list = order_list.filter(**filters).values(item_key).distinct()

    if not order_docno_list:
        order_docno_list = order_list.values(item_key).distinct()
    elif len(order_docno_list) == 1:
        order_docno_alllist = order_list.values(item_key).distinct()

        try:
            if order_docno_list.first()[item_key] == doc_no_to:
                index = get_index_of_value(order_docno_alllist, [doc_no_to], item_key) + 1
                order_docno_list = order_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(order_docno_alllist, [doc_no_from], item_key)
                order_docno_list = order_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        order_docno_alllist = order_list.values(item_key).distinct()
        index = get_index_of_value(order_docno_alllist, [doc_no_from, doc_no_to], item_key)
        order_docno_list = order_docno_alllist[index[0]:index[1] + 1]

    return [order[item_key] for order in order_docno_list]


def get_orderitem_filter_range(order_type, company_id, doc_no_from, doc_no_to, item_key):
    order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=order_type)

    filter_key = item_key + '__in'
    filters = {filter_key: (doc_no_from, doc_no_to)}
    order_item_list = order_item_list.order_by(item_key)

    orderitem_docno_list = order_item_list.filter(**filters).values(item_key).distinct()

    if not orderitem_docno_list:
        orderitem_docno_list = order_item_list.values(item_key).distinct()
    elif len(orderitem_docno_list) == 1:
        orderitem_docno_alllist = order_item_list.values(item_key).distinct()

        try:
            if orderitem_docno_list.first()[item_key] == doc_no_to:
                index = get_index_of_value(orderitem_docno_alllist, [doc_no_to], item_key) + 1
                orderitem_docno_list = orderitem_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(orderitem_docno_alllist, [doc_no_from], item_key)
                orderitem_docno_list = orderitem_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        orderitem_docno_alllist = order_item_list.values(item_key).distinct()
        index = get_index_of_value(orderitem_docno_alllist, [doc_no_from, doc_no_to], item_key)
        orderitem_docno_list = orderitem_docno_alllist[index[0]:index[1] + 1]

    return [orderitem[item_key] for orderitem in orderitem_docno_list]


def get_vendor_filter_range(company_id, vendor_from, vendor_to, item_key):
    vendor_list = Supplier.objects.filter(is_hidden=0, company_id=company_id)

    filter_key = item_key + '__in'
    filters = {filter_key: (vendor_from, vendor_to)}
    vendor_list = vendor_list.order_by(item_key)

    vendor_docno_list = vendor_list.filter(**filters).values(item_key).distinct()

    if not vendor_docno_list:
        vendor_docno_list = vendor_list.values(item_key).distinct()
    elif len(vendor_docno_list) == 1:
        vendor_docno_alllist = vendor_list.values(item_key).distinct()

        try:
            if vendor_docno_list.first()[item_key] == vendor_to:
                index = get_index_of_value(vendor_docno_alllist, [vendor_to], item_key) + 1
                vendor_docno_list = vendor_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(vendor_docno_alllist, [vendor_from], item_key)
                vendor_docno_list = vendor_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        vendor_docno_alllist = vendor_list.values(item_key).distinct()
        index = get_index_of_value(vendor_docno_alllist, [vendor_from, vendor_to], item_key)
        vendor_docno_list = vendor_docno_alllist[index[0]:index[1] + 1]

    return [vendor[item_key] for vendor in vendor_docno_list]


def get_account_filter_range(company_id, val_from, val_to, item_key):
    account_list = Account.objects.filter(
        is_hidden=0, company_id=company_id).order_by('account_segment', 'code')

    filter_key = item_key + '__in'
    filters = {filter_key: (val_from, val_to)}
    account_list = account_list.order_by(item_key)

    account_docno_list = account_list.filter(**filters).values(item_key).distinct()

    if not account_docno_list:
        account_docno_list = account_list.values(item_key).distinct()
    elif len(account_docno_list) == 1:
        account_docno_alllist = account_list.values(item_key).distinct()

        try:
            if account_docno_list.first()[item_key] == val_to:
                index = get_index_of_value(account_docno_alllist, [val_to], item_key) + 1
                account_docno_list = account_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(account_docno_alllist, [val_from], item_key)
                account_docno_list = account_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        account_docno_alllist = account_list.values(item_key).distinct()
        index = get_index_of_value(account_docno_alllist, [val_from, val_to], item_key)
        account_docno_list = account_docno_alllist[index[0]:index[1] + 1]

    return [account[item_key] for account in account_docno_list]


def get_segment_filter_range(company_id, val_from, val_to, item_key):
    segment_list = CostCenters.objects.filter(is_hidden=0, company_id=company_id)

    filter_key = item_key + '__in'
    filters = {filter_key: (val_from, val_to)}
    segment_list = segment_list.order_by(item_key)

    segment_docno_list = segment_list.filter(**filters).values(item_key).distinct()

    if not segment_docno_list:
        segment_docno_list = segment_list.values(item_key).distinct()
    elif len(segment_docno_list) == 1:
        segment_docno_alllist = segment_list.values(item_key).distinct()

        try:
            if segment_docno_list.first()[item_key] == val_to:
                index = get_index_of_value(segment_docno_alllist, [val_to], item_key) + 1
                segment_docno_list = segment_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(segment_docno_alllist, [val_from], item_key)
                segment_docno_list = segment_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        segment_docno_alllist = segment_list.values(item_key).distinct()
        index = get_index_of_value(segment_docno_alllist, [val_from, val_to], item_key)
        segment_docno_list = segment_docno_alllist[index[0]:index[1] + 1]

    return [segment[item_key] for segment in segment_docno_list]


def get_customer_filter_range(company_id, val_from, val_to, item_key):
    customer_list = Customer.objects.filter(is_hidden=0, company_id=company_id)

    filter_key = item_key + '__in'
    filters = {filter_key: (val_from, val_to)}
    customer_list = customer_list.order_by(item_key)

    customer_docno_list = customer_list.filter(**filters).values(item_key).distinct()

    if not customer_docno_list:
        customer_docno_list = customer_list.values(item_key).distinct()
    elif len(customer_docno_list) == 1:
        customer_docno_alllist = customer_list.values(item_key).distinct()

        try:
            if customer_docno_list.first()[item_key] == val_to:
                index = get_index_of_value(customer_docno_alllist, [val_to], item_key) + 1
                customer_docno_list = customer_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(customer_docno_alllist, [val_from], item_key)
                customer_docno_list = customer_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        customer_docno_alllist = customer_list.values(item_key).distinct()
        index = get_index_of_value(customer_docno_alllist, [val_from, val_to], item_key)
        customer_docno_list = customer_docno_alllist[index[0]:index[1] + 1]

    return [customer[item_key] for customer in customer_docno_list]


def get_category_filter_range(company_id, val_from, val_to, item_key):
    category_list = ItemCategory.objects.filter(is_hidden=0, company_id=company_id)

    filter_key = item_key + '__in'
    filters = {filter_key: (val_from, val_to)}
    category_list = category_list.order_by(item_key)

    category_docno_list = category_list.filter(**filters).values(item_key).distinct()

    if not category_docno_list:
        category_docno_list = category_list.values(item_key).distinct()
    elif len(category_docno_list) == 1:
        category_docno_alllist = category_list.values(item_key).distinct()

        try:
            if category_docno_list.first()[item_key] == val_to:
                index = get_index_of_value(category_docno_alllist, [val_to], item_key) + 1
                category_docno_list = category_docno_alllist[:index[0]]
            else:
                index = get_index_of_value(category_docno_alllist, [val_from], item_key)
                category_docno_list = category_docno_alllist[index[0]:]
        except Exception as e:
            print(e)
    else:
        category_docno_alllist = category_list.values(item_key).distinct()
        index = get_index_of_value(category_docno_alllist, [val_from, val_to], item_key)
        category_docno_list = category_docno_alllist[index[0]:index[1] + 1]

    return [category[item_key] for category in category_docno_list]


def get_company_name_and_current_period(company_id):
    try:
        company = Company.objects.get(pk=company_id)
        curr_year = company.current_period_year_sp if company.current_period_year_sp else company.current_period_year
        curr_month = company.current_period_month_sp if company.current_period_month_sp else company.current_period_month
        current_period = datetime.strptime(curr_year + '-' + curr_month, '%Y-%m')
    except Exception as e:
        print(e)
        return '', ''

    return company.name, current_period.strftime('%B %Y')


def wrap_text(value, mFilter=None, decimal_place="%.2f"):
    str_value = intcomma(decimal_place % round_number(value)).replace("-", "")
    if mFilter and mFilter in ('PL-NETSALE', 'PL-REVENUE', 'PL-EXC'):
        if value > 0:
            style = 'RightAlignRed'
            str_value = '(' + str_value + ')'
        else:
            style = 'RightAlignBlack'
    else:
        if value < 0:
            style = 'RightAlignRed'
            str_value = '(' + str_value + ')'
        else:
            style = 'RightAlignBlack'

    return str_value, style


def wrap_text_xls(value, mFilter=None, decimal_place="%.2f"):
    str_value = intcomma(decimal_place % round_number(value)).replace("-", "")
    if mFilter and mFilter in ('PL-NETSALE', 'PL-REVENUE', 'PL-EXC'):
        if value > 0:
            str_value = '(' + str_value + ')'
    else:
        if value < 0:
            str_value = '(' + str_value + ')'

    return str_value


def wrap_separator(value, m_account_group=None, decimal_place="%.2f"):
    str_value = intcomma(decimal_place % round_number(value)).replace("-", "")
    if m_account_group and m_account_group in ('BS-CL', 'BS-SE'):
        if value > 0:
            str_value = '(' + str_value + ')'
    else:
        if value < 0:
            str_value = '(' + str_value + ')'

    return str_value


def separator(value, decimal_place="%.2f"):
    str_value = intcomma(decimal_place % round_number(value))
    return str_value


def get_number(value):
    num = str(value).replace(',', '').replace('-', '').replace('(', '').replace(')', '')
    return float(num)


def send_email(sender, recipient_name, email_msg, balance_date, company_name, email, attachment_path):
    subject = MSG_APPLY_SUBJECT % (company_name)
    if None == email_msg:
        msg_content_to_client = MSG_APPLY_CONTENT % (recipient_name, balance_date)
    else:
        msg_content_to_client = email_msg

    try:
        mail = EmailMessage(subject, msg_content_to_client, to=[email])
        if None != attachment_path:
            mail.attach_file(attachment_path)
        mail.send()
    except Exception as e:
        error_msg = "MAIL ERROR: " + str(e)
        logger.error(error_msg)


def get_form_field_attr(element, placeholder="", required=False, autofocus=False, readonly=False):
    element = element.copy()
    element['placeholder'] = placeholder
    element['required'] = required
    element['autofocus'] = autofocus
    element['readonly'] = readonly
    return element


def get_item_onhandqty(item_id):
    onhand_qty = 0
    loc_items = LocationItem.objects.filter(is_hidden=0, item_id=item_id).values('item_id'). \
        annotate(sum_onhand=Coalesce(Sum('onhand_qty'), V(0)))
    if loc_items:
        for loc_item in loc_items:
            onhand_qty += loc_item['sum_onhand']
    return onhand_qty


def generate_batch_number(company_id, batch_type):
    batchs = Batch.objects.filter(company_id=company_id, batch_type=batch_type, is_hidden=False).order_by('-batch_no')
    cnt = 0
    batch_last = 0
    if batchs:
        cnt = batchs.count()
        if batchs.first().batch_no:
            batch_last = int(batchs.first().batch_no)
    batch_number = cnt + 1 if cnt > batch_last else batch_last + 1
    str_length = len(str(batch_number))
    if str_length < 6:
        while str_length < 6:
            batch_number = '0' + str(batch_number)
            str_length += 1
    else:
        batch_number = '0' + str(batch_number)

    return batch_number

def generate_recurring_batch_number(company_id, batch_type):
    batchs = RecurringBatch.objects.filter(company_id=company_id, batch_type=batch_type, is_hidden=False).order_by('-batch_no')
    cnt = 0
    batch_last = 0
    if batchs:
        cnt = batchs.count()
        if batchs.first().batch_no:
            batch_last = int(batchs.first().batch_no)
    batch_number = cnt + 1 if cnt > batch_last else batch_last + 1
    str_length = len(str(batch_number))
    if str_length < 6:
        while str_length < 6:
            batch_number = '0' + str(batch_number)
            str_length += 1
    else:
        batch_number = '0' + str(batch_number)

    return batch_number


def search(request):
    obj = objSearch(request.GET['search'], request)

    return HttpResponse(obj.getResponse(), content_type='application/json')


def get_largest_document_number(prefix, month, year, filter_transaction_code, is_inventory):
    try:
        regex = re.escape(prefix) + re.escape('-') + re.escape(year) + r'[0-9]{2}' + re.escape('-') + r'[0-9]{5}'
        filters = {"document_number__iregex": regex, "is_hidden": 0}
        exclude_filters = {"status": dict(ORDER_STATUS)['Draft']}

        if is_inventory:
            last_order_doc = StockTransaction.objects.order_by('-document_number').filter(**filters).exclude(
                **exclude_filters).first()
        else:
            last_order_doc = Order.objects.order_by('-document_number').filter(**filters).exclude(
                **exclude_filters).first()

        postfix = int(str(last_order_doc.document_number)[-5:]) + 1
    except Exception as e:
        print(e)
        postfix = 1
    document_number = prefix + '-' + year + month + '-' + '{:05}'.format(postfix % 100000)

    filter_transaction_code.last_no = postfix
    filter_transaction_code.save()

    return document_number


def AR_AP_generate_document_number(company_id, journal_type):
    prefix = 'PY'
    next_number = '1'
    length = 22
    if journal_type == dict(TRANSACTION_TYPES)['AP Payment']:
        ap_options = APOptions.objects.filter(company_id=company_id)
        if ap_options:
            ap_options = ap_options.last()
            prefix = ap_options.payment_prefix
            next_number = str(ap_options.payment_next_number)
            length = ap_options.payment_length
    elif journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
        ar_options = AROptions.objects.filter(company_id=company_id)
        if ar_options:
            ar_options = ar_options.last()
            prefix = ar_options.receipt_prefix
            next_number = str(ar_options.receipt_next_number)
            length = ar_options.receipt_length

    temp_length = len(prefix) + len(next_number)
    in_length = length - temp_length
    document_number = prefix
    i = 0
    while i < in_length:
        document_number += '0'
        i += 1
    document_number += next_number
    return document_number


def update_next_doc_number(company_id, doc_number, journal_type):
    try:
        doc_number = int(doc_number[-8::])
        next_number = doc_number + 1
        if journal_type == dict(TRANSACTION_TYPES)['AP Payment']:
            ap_options = APOptions.objects.filter(company_id=company_id)
            if ap_options:
                ap_options = ap_options.last()
                ap_options.payment_next_number = next_number
                ap_options.save()
        elif journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
            ar_options = AROptions.objects.filter(company_id=company_id)
            if ar_options:
                ar_options = ar_options.last()
                ar_options.receipt_next_number = next_number
                ar_options.save()
        return True
    except Exception as e:
        print(e)
        return False

def update_next_adj_number(company_id, doc_number):
    try:
        next_number = doc_number + 1
        ar_options = AROptions.objects.filter(company_id=company_id)
        if ar_options:
            ar_options = ar_options.last()
            ar_options.adjustment_next_number = next_number
            ar_options.save()
        return True
    except Exception as e:
        print(e)
        return False


def generate_document_number(company_id, document_date, trn_code_type, transaction_code, prefix=''):
    # Document number is generated based on current period, not document_date
    try:
        company = Company.objects.get(pk=company_id)
        year = company.current_period_year_sp
        month = "%02d" % int(company.current_period_month_sp)
    except Exception as e:
        print(e)
        year = document_date.split('-')[0]
        month = document_date.split('-')[1]

    stock_transaction_code_list = TransactionCode.objects.filter(is_hidden=False, company_id=company_id,
                                                                 menu_type=trn_code_type).values("ics_prefix")
    stock_code_list = []
    for code in stock_transaction_code_list:
        stock_code_list.append(code['ics_prefix'])

    if prefix != '' and prefix in stock_code_list:  # Inventory
        year = company.current_period_year_ic
        month = "%02d" % int(company.current_period_month_ic)
    filter_transaction_code = TransactionCode.objects.get(pk=transaction_code)
    try:
        # We try to see if transaction code maintain "Last No"
        prefix = filter_transaction_code.ics_prefix
        postfix = int(filter_transaction_code.last_no) + 1
        if postfix < 0:
            return get_largest_document_number(prefix, month, year, filter_transaction_code, prefix in stock_code_list)

        document_number = prefix + '-' + year + month + '-' + '{:05}'.format(postfix % 100000)
        filter_transaction_code.last_no = postfix

        filters = {"document_number": document_number, "is_hidden": 0, "company_id": company_id}
        exclude_filters = {"status": dict(ORDER_STATUS)['Draft']}
        # Check if there's duplicate
        if prefix != '' and prefix in stock_code_list:  # Inventory
            exclude_filters = {"status": dict(ORDER_STATUS)['Sent']}
            last_order = StockTransaction.objects.filter(**filters).exclude(**exclude_filters).first()
        else:  # Sales & Purchase
            last_order = Order.objects.filter(**filters).exclude(**exclude_filters).first()

        if last_order:
            return get_largest_document_number(prefix, month, year, filter_transaction_code, prefix in stock_code_list)
        filter_transaction_code.save()

    except Exception as e:
        print(e)
        document_number = get_largest_document_number(prefix, month, year, filter_transaction_code,
                                                      prefix in stock_code_list)

    return document_number


class objSearch():
    """docstring for objSearch"""
    init = [
        {
            'keywords': 'transactioncode',
            'app': 'inventory.models',
            'target_model': 'TransactionCode',
            'reverse': False
        },
        {
            'keywords': 'location',
            'app': 'locations.models',
            'target_model': 'Location',
            'reverse': False
        },
        {
            'keywords': 'item',
            'app': 'items.models',
            'target_model': 'Item',
            'reverse': False
        },
        {
            'keywords': 'partgroup',
            'app': 'items.models',
            'target_model': 'ItemCategory',
            'reverse': False
        },
        {
            'keywords': 'tax',
            'app': 'taxes.models',
            'target_model': 'Tax',
            'reverse': False
        },
        {
            'keywords': 'deliveryinfo',
            'app': 'customers.models',
            'target_model': 'Delivery',
            'reverse': False
        },
        {
            'keywords': 'customerinfo',
            'app': 'customers.models',
            'target_model': 'Customer',
            'reverse': False
        },
        {
            'keywords': 'supplierinfo',
            'app': 'suppliers.models',
            'target_model': 'Supplier',
            'reverse': False
        },
        {
            'keywords': 'accountgroup',
            'app': 'accounts.models',
            'target_model': 'AccountType',
            'reverse': False
        },
        {
            'keywords': 'account',
            'app': 'accounts.models',
            'target_model': 'Account',
            'reverse': False
        },
        {
            'keywords': 'distributioncode',
            'app': 'accounts.models',
            'target_model': 'DistributionCode',
            'reverse': False
        },
        {
            'keywords': 'paymentcode',
            'app': 'accounting.models',
            'target_model': 'PaymentCode',
            'reverse': False
        },
        {
            'keywords': 'currency',
            'app': 'currencies.models',
            'target_model': 'Currency',
            'reverse': False
        },
        {
            'keywords': 'country',
            'app': 'countries.models',
            'target_model': 'Country',
            'reverse': False
        },
        {
            'keywords': 'country',
            'app': 'countries.models',
            'target_model': 'Country',
            'reverse': False
        },
        {
            'keywords': 'paymentmode',
            'app': 'accounting.models',
            'target_model': 'PaymentCode',
            'reverse': False
        },
        {
            'keywords': 'costcenters',
            'app': 'companies.models',
            'target_model': 'CostCenters',
            'reverse': False
        },
        {
            'keywords': 'uom',
            'app': 'items.models',
            'target_model': 'ItemMeasure',
            'reverse': False
        },
        {
            'keywords': 'partsaleprice',
            'app': 'items.models',
            'target_model': 'Item',
            'reverse': True
        },
        {
            'keywords': 'purchaseitem',
            'app': 'items.models',
            'target_model': 'Item',
            'reverse': True
        },
        {
            'keywords': 'accountset',
            'app': 'accounts.models',
            'target_model': 'AccountSet',
            'reverse': True
        },
        {
            'keywords': 'stocktransaction',
            'app': 'inventory.models',
            'target_model': 'StockTransaction',
            'reverse': True
        },
        {
            'keywords': 'supplier info',
            'app': 'suppliers.models',
            'target_model': 'Supplier',
            'reverse': True
        }

    ]

    keyword = None
    model = None
    response = None
    is_reverse = 0
    use_inventory = 0
    company = 0

    def __init__(self, string, request):
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.company = Company.objects.get(pk=company_id)
        if self.escapeString(string):
            if self.importModel():
                self.response = self.generateResponse(self.getData())
            else:
                self.response = json.dumps(
                    {'status': 300, 'message': 'search code for "' + self.keyword + '" not yet supported'})
        else:
            self.response = json.dumps({'status': 200, 'object': 'null'})

    def escapeString(self, string):
        string = string.replace(" ", "")
        if string.isalpha():
            self.keyword = string
            return True
        return False

    def importModel(self):
        for d in self.init:
            if d['keywords'] == self.keyword:
                appModel = __import__(d['app'], globals(), locals(), [d['target_model']])
                self.model = getattr(appModel, d['target_model'])
                self.is_reverse = d['reverse']
                return True
        return 0

    def getData(self):

        filters = {'is_hidden': 0}

        if hasattr(self.model, 'company_id'):
            filters['company_id'] = self.company.id
        elif hasattr(self.model, 'company'):
            filters['company'] = self.company.id

        if hasattr(self.model, 'transaction_code'):
            code = 'transaction_code'
        elif hasattr(self.model, 'code'):
            code = 'code'
        else:
            return 0

        d = self.model.objects.filter(**filters).values(code)
        return d

    def generateResponse(self, d):
        if d and d.count():
            d = list(d)
        else:
            d = 'null'

        return json.dumps({'status': 200, 'object': {'data': d, 'is_reverse': self.is_reverse,
                                                     'use_inventory': self.company.is_inventory}})

    def getResponse(self):
        return self.response


class UpdateStockTransaction():
    """docstring for updateStockTransaction """

    def __init__(self, order, company_id, trxCode):
        self.order = order
        self.db = __import__('django.db', globals(), locals(), ['transaction', 'IntegrityError'], 0)
        self.inventory = __import__('inventory.models', globals(), locals(),
                                    ['StockTransaction', 'StockTransactionDetail', 'TransactionCode'], 0)
        self.company_id = company_id
        self.trxCode = trxCode
        self.items = []
        self.stock_transaction = None

    def getStockTransaction(self):
        try:
            stockTrans = StockTransaction.objects.filter(company_id=self.company_id, order_id=self.order.id,
                                                         is_hidden=False)
            if stockTrans:
                self.stock_transaction = stockTrans
                return stockTrans
        except Exception as e:
            print(e)
            return StockTransaction.objects.none()

    def deleteStockTransaction(self):
        try:
            StockTransHeader = self.stock_transaction
            if not StockTransHeader:
                StockTransHeader = self.getStockTransaction()

            if StockTransHeader:
                for hdr in StockTransHeader:
                    hdr.is_hidden = True
                    StockTransDetail = StockTransactionDetail.objects.filter(parent_id=hdr.id, is_hidden=False)
                    if StockTransDetail:
                        for dtl in StockTransDetail:
                            dtl.is_hidden = True
                            try:
                                dtl.save()
                            except Exception as e:
                                print(e)
                                return False
                    try:
                        hdr.save()
                    except Exception as e:
                        print(e)
                        return False
        except Exception as e:
            print(e)
            return False
        return True

    def addItem(self, item):
        if item.location:
            if self.items.__len__():
                isLocationExist = False
                for tmpItem in self.items:
                    if tmpItem['location'] == item.location.id:  # isLocationExist = True
                        isLocationExist = True
                        tmpItem['data'].append(item)
                        break

                if not isLocationExist:
                    self.items.append({'location': item.location.id, 'data': [item]})
            else:
                self.items.append({'location': item.location.id, 'data': [item]})

    def generate(self):
        code = self.inventory.TransactionCode.objects.get(pk=self.trxCode)
        for order in self.items:
            if order['location']:
                try:
                    with self.db.transaction.atomic():
                        newStockOrder = self.saveOrder(order, code)
                        if newStockOrder:
                            self.saveItems(newStockOrder, order)
                except OSError as e:
                    return 0

    def saveOrder(self, order, code):
        stockTrans = self.inventory.StockTransaction()
        stockTrans.document_date = self.order.document_date
        stockTrans.transaction_code_id = code.id
        stockTrans.document_number = self.order.document_number
        stockTrans.remark = self.order.remark
        stockTrans.io_flag = code.io_flag
        stockTrans.price_flag = code.price_flag
        stockTrans.remark = self.order.remark
        stockTrans.update_by = self.order.update_by
        stockTrans.company_id = self.order.company_id
        stockTrans.currency_id = self.order.currency_id
        stockTrans.status = dict(ORDER_STATUS)['Draft']
        stockTrans.is_from_sp = 1
        stockTrans.order_id = self.order.id
        if stockTrans.io_flag == dict(INV_IN_OUT_FLAG)['IN']:
            stockTrans.in_location_id = order['location']
        elif stockTrans.io_flag == dict(INV_IN_OUT_FLAG)['OUT']:
            stockTrans.out_location_id = order['location']
        stockTrans.save()

        return stockTrans

    def saveItems(self, newStockOrder, order):
        for item in order['data']:
            dbItem = self.inventory.StockTransactionDetail()
            dbItem.parent_id = newStockOrder.id
            if newStockOrder.io_flag == dict(INV_IN_OUT_FLAG)['IN']:
                dbItem.in_location_id = order['location']
                dbItem.outstanding_quantity = item.quantity
            elif newStockOrder.io_flag == dict(INV_IN_OUT_FLAG)['OUT']:
                dbItem.out_location_id = order['location']
                out_quantity = item.quantity
                related_stock_transactions = StockTransactionDetail.objects.filter(is_hidden=0) \
                    .filter(Q(parent__io_flag=1) | Q(parent__io_flag=2))
                related_stock_transactions = related_stock_transactions.filter(item_id=item.item_id,
                                                                               parent__in_location_id=newStockOrder.out_location_id,
                                                                               parent__company_id=newStockOrder.company_id,
                                                                               parent__is_hidden=False,
                                                                               is_hidden=False).order_by(
                    'parent__document_date')
                for related_detail in related_stock_transactions:
                    if out_quantity <= 0:
                        continue

                    if related_detail.outstanding_quantity < out_quantity:
                        out_quantity -= related_detail.outstanding_quantity
                        related_detail.outstanding_quantity = 0
                    elif related_detail.outstanding_quantity == out_quantity:
                        out_quantity = 0
                        related_detail.outstanding_quantity = 0
                    elif related_detail.outstanding_quantity > out_quantity:
                        related_detail.outstanding_quantity = related_detail.outstanding_quantity - out_quantity
                        out_quantity = 0

                    related_detail.save()
            dbItem.line_number = item.line_number
            dbItem.quantity = item.quantity
            dbItem.item_id = item.item_id
            dbItem.price = item.price
            dbItem.amount = item.amount
            dbItem.save()

    def getItems(self):
        return self.items

    def getOrder(self):
        return self.order

    def generate_document_number(self, document_date, inv_prefix):
        return generate_document_number(self.company_id, document_date, int(TRN_CODE_TYPE_DICT['Inventory Code']),
                                        inv_prefix)


class Location_Item(object):
    def __init__(self, request, location_id=None, item_id=None):
        self.request = request
        self.company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.location_id = location_id
        self.item_id = item_id
        self.item_location = None
        self.errors = []

    def get_item_location(self, location_id=None, item_id=None):
        result = False
        if not location_id:
            location_id = self.location_id
        if not item_id:
            item_id = self.item_id

        try:
            item_location = LocationItem.objects.filter(is_hidden=0, location_id=location_id,
                                                        item_id=item_id, location__company_id=self.company_id).first()
            if item_location:
                self.item_location = item_location
                result = True
            else:
                self.new_location_item()
                result = True
        except Exception as e:
            print(e)
            self._set_errors('Failed to get item location')
        return result

    def new_location_item(self):
        try:
            item_location = LocationItem()
            item_location.location_id = self.location_id
            item_location.item_id = self.item_id
            item_location.onhand_qty = 0
            item_location.booked_qty = 0
            item_location.in_qty = 0
            item_location.out_qty = 0
            item_location.create_date = datetime.today()
            item_location.update_by_id = self.request.user.id
            item_location.save()

            self.item_location = item_location
        except Exception as e:
            print(e)
            self._set_errors('Failed to create new item location')

    def _set_errors(self, error_msg):
        self.errors.append(error_msg)

    def get_errors(self):
        return self.errors

    def set_onhand(self, qty):
        result = False
        try:
            if self.item_location.onhand_qty:
                self.item_location.onhand_qty += qty
            else:
                self.item_location.onhand_qty = qty
            self.item_location.save()
            result = True
        except Exception as e:
            print(e)
            self._set_errors('Failed to update onhand qty')
        return result

    def set_booked(self, qty):
        result = False
        try:
            if self.item_location.booked_qty:
                self.item_location.booked_qty += qty
            else:
                self.item_location.booked_qty = qty
            self.item_location.save()
            result = True
        except Exception as e:
            print(e)
            self._set_errors('Failed to update booked qty')
        return result

    def set_in_qty(self, qty):
        result = False
        try:
            if self.item_location.in_qty:
                self.item_location.in_qty += qty
            else:
                self.item_location.in_qty = qty
            self.item_location.save()
            result = True
        except Exception as e:
            print(e)
            self._set_errors('Failed to update in qty')
        return result

    def set_out_qty(self, qty):
        result = False
        try:
            if self.item_location.out_qty:
                self.item_location.out_qty += qty
            else:
                self.item_location.out_qty = qty
            self.item_location.save()
            result = True
        except Exception as e:
            print(e)
            self._set_errors('Failed to update out qty')
        return result

    def get_quantity(self):
        location_data = None
        try:
            if self.item_location:
                location_data = {'onhand_qty': self.item_location.onhand_qty,
                                 'booked_qty': self.item_location.booked_qty,
                                 'in_qty': self.item_location.in_qty,
                                 'out_qty': self.item_location.out_qty,
                                 'back_order_qty': self.item_location.back_order_qty,
                                 'stock_qty': self.item_location.stock_qty,
                                 'last_open_qty': self.item_location.last_open_qty,
                                 'last_closing_qty': self.item_location.last_closing_qty,
                                 'month_open_qty': self.item_location.month_open_qty,
                                 'month_closing_qty': self.item_location.month_closing_qty,
                                 'year_open_qty': self.item_location.year_open_qty}
        except Exception as e:
            print(e)

        return location_data


class order_vs_inventory(Location_Item):
    request = None
    company_id = 0

    def __init__(self, request):
        self.request = request
        self.company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.company = Company.objects.get(pk=self.company_id, is_hidden=False)
        self.order_details = None
        super(order_vs_inventory, self).__init__(request)

    def get_order_item(self, orderitem_id):
        order_line = None
        try:
            order_line = OrderItem.objects.get(pk=orderitem_id)
        except Exception as e:
            print(e)

        return order_line

    def get_order_detail(self, orderitem_id):
        order_detail_data = None
        try:
            order_item = self.get_order_item(orderitem_id)
            if order_item:
                order_detail_data = {'order': order_item.order,
                                     'order_type': order_item.order.order_type,
                                     'order_item_id': order_item.id,
                                     'qty': order_item.quantity,
                                     'last_qty': order_item.last_quantity,
                                     'backorder_qty': order_item.bkord_quantity,
                                     'item_id': order_item.item_id,
                                     'item_code': order_item.item.code,
                                     'price': order_item.price,
                                     'document_number': order_item.order.document_number,
                                     'line_number': order_item.line_number,
                                     'refer_doc_id': order_item.reference_id,
                                     'refer_doc_no': order_item.refer_number,
                                     'refer_doc_ln': order_item.refer_line,
                                     'location_detail': {}}
                if self.company.is_inventory:
                    order_detail_data['location_id'] = order_item.location_id if order_item.location else None
                    order_detail_data['location_code'] = order_item.location.code if order_item.location else None
                    if order_item.location_id:
                        self.location_id = order_item.location_id
                        self.item_id = order_item.item_id
                        if self.get_item_location(order_item.location_id, order_item.item_id):
                            order_detail_data['location_detail'] = self.get_quantity()
        except Exception as e:
            print(e)
        self.order_details = order_detail_data
        return order_detail_data

    def get_reference_item(self, orderitem_id):
        reference_item = None
        try:
            source_doc = self.get_order_detail(orderitem_id)
            try:
                reference_item = OrderItem.objects. \
                    filter(order_id=source_doc['refer_doc_id'],
                        line_number=source_doc['refer_doc_ln'],
                        item_id=source_doc['item_id'],
                        is_hidden=False)
                if reference_item.exists():
                    reference_item = reference_item.last()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
        return reference_item

    def resetOrderStatus(self, order_id, qty1, qty2, order_type, ref_item_id=None):
        result = False
        try:
            order = Order.objects.get(pk=order_id, is_hidden=False)
            other_order_items = None
            if ref_item_id:
                other_order_items = OrderItem.objects.filter(
                    order_id=order_id, is_hidden=False).exclude(id=ref_item_id)

            if qty1 <= 0:
                order.status = dict(ORDER_STATUS)['Sent']
            elif qty1 and qty1 < qty2:
                order.status = dict(ORDER_STATUS)['Partial']
            elif qty1 and qty1 >= qty2:
                if order_type == dict(ORDER_TYPE)['SALES INVOICE']:
                    delivered = True
                    if other_order_items:
                        for item in other_order_items:
                            if item.delivery_quantity >= item.quantity:
                                delivered = True
                            else:
                                delivered = False
                                break
                    if delivered:
                        order.status = dict(ORDER_STATUS)['Delivered']
                    else:
                        order.status = dict(ORDER_STATUS)['Partial']
                elif order_type == dict(ORDER_TYPE)['PURCHASE INVOICE']:
                    received = True
                    if other_order_items:
                        for item in other_order_items:
                            if item.receive_quantity >= item.quantity:
                                received = True
                            else:
                                received = False
                                break
                    if received:
                        order.status = dict(ORDER_STATUS)['Received']
                    else:
                        order.status = dict(ORDER_STATUS)['Partial']
                else:
                    pass
            else:
                return False
            order.save()
            result = True
        except Exception as e:
            print(e)
        return result

    def set_reference_item(self, orderitem_id, last_qty=None, last_order_status=None, is_delete=False):
        result = False
        errors = []
        order_data = self.get_order_detail(orderitem_id)
        qty = self.enhanced_qty(order_data, last_qty, last_order_status, is_delete)
        try:
            reference_lvl1 = self.get_reference_item(orderitem_id)
            if reference_lvl1:
                try:
                    result = True
                    order_type = order_data['order_type']
                    if reference_lvl1.order.order_type == dict(ORDER_TYPE)['SALES ORDER'] and order_type != dict(ORDER_TYPE)['PURCHASE ORDER']:
                        reference_lvl1.delivery_quantity += qty
                        if 0 > reference_lvl1.delivery_quantity:
                            reference_lvl1.delivery_quantity = 0
                        reference_lvl1.last_delivery_date = datetime.today()
                        self.resetOrderStatus(reference_lvl1.order_id, reference_lvl1.delivery_quantity,
                                              reference_lvl1.quantity, order_type, reference_lvl1.id)
                    elif reference_lvl1.order.order_type == dict(ORDER_TYPE)['PURCHASE ORDER']:
                        reference_lvl1.stock_quantity += qty
                        reference_lvl1.receive_quantity += qty
                        if 0 > reference_lvl1.stock_quantity:
                            reference_lvl1.stock_quantity = 0
                        if 0 > reference_lvl1.receive_quantity :
                            reference_lvl1.receive_quantity = 0
                        self.resetOrderStatus(reference_lvl1.order_id, reference_lvl1.receive_quantity,
                                              reference_lvl1.quantity, order_type, reference_lvl1.id)
                    reference_lvl1.update_date = datetime.today()
                    reference_lvl1.update_by_id = self.request.user.id

                    # Do not proceed if it comes from DO or GR, otherwise SO/PO related to the PO/SO will go wrong!!
                    if order_type == dict(ORDER_TYPE)['SALES INVOICE'] or dict(ORDER_TYPE)['PURCHASE INVOICE']:
                        reference_lvl1.save()
                        return result, errors

                    if reference_lvl1.reference_id:
                        reference_lvl2 = self.get_reference_item(reference_lvl1.id)
                        if reference_lvl2:
                            try:
                                if reference_lvl2.order.order_type == dict(ORDER_TYPE)['SALES ORDER']:
                                    reference_lvl2.delivery_quantity += qty
                                    if 0 > reference_lvl2.delivery_quantity:
                                        reference_lvl2.delivery_quantity = 0
                                    reference_lvl2.last_delivery_date = datetime.today()
                                    self.resetOrderStatus(reference_lvl2.order_id, reference_lvl2.delivery_quantity,
                                                          reference_lvl2.quantity, order_type, reference_lvl2.id)
                                elif reference_lvl2.order.order_type == dict(ORDER_TYPE)['PURCHASE ORDER']:
                                    reference_lvl2.stock_quantity += qty
                                    reference_lvl2.receive_quantity += qty
                                    if 0 > reference_lvl2.stock_quantity:
                                        reference_lvl2.stock_quantity = 0
                                    if 0 > reference_lvl2.receive_quantity :
                                        reference_lvl2.receive_quantity = 0
                                    self.resetOrderStatus(reference_lvl2.order_id, reference_lvl2.receive_quantity,
                                                          reference_lvl2.quantity, order_type, reference_lvl2.id)
                                reference_lvl2.update_date = datetime.today()
                                reference_lvl2.update_by_id = self.request.user.id
                                reference_lvl2.save()
                            except Exception as e:
                                print(e)
                                result = False
                                errors.append(UPDATE_REF_QTY_FAILED % (reference_lvl2.order.document_number))
                    if result:
                        reference_lvl1.save()
                except Exception as e:
                    print(e)
                    errors.append(UPDATE_REF_QTY_FAILED % (reference_lvl1.order.document_number))
        except Exception as e:
            print(EXCEPTION_JOURNAL_ADD % 'Set Reference', e)
            errors.append(EXCEPTION_JOURNAL_ADD % 'Set Reference')
        return result, errors

    def get_next_doc_detail(self, orderitem_id):
        next_doc_detail_data = None
        try:
            source_doc = self.get_order_detail(orderitem_id)
            try:
                next_doc_detail_data = OrderItem.objects. \
                    filter(reference_id=source_doc['order'].id,
                           refer_line=source_doc['line_number'],
                           item_id=source_doc['item_id'],
                           is_hidden=False)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
        return next_doc_detail_data

    def isFulfilled(self, orderitem_id):
        result = False
        outstanding_quantity = 0
        try:
            current_doc = self.order_details if self.order_details else self.get_order_detail(orderitem_id)
            next_docs = self.get_next_doc_detail(orderitem_id)
            if current_doc and next_docs:
                current_doc_qty = current_doc['qty']
                next_doc_qty = 0
                for next_doc in next_docs:
                    next_doc_qty += next_doc['order_detail'].quantity
                outstanding_quantity = current_doc_qty - next_doc_qty
                if outstanding_quantity <= 0:
                    result = True
        except Exception as e:
            print(e)
        return result, outstanding_quantity

    def delete_order_detail(self, orderitem_id):
        result = False
        try:
            order_item = OrderItem.objects.get(pk=orderitem_id)
            order_item.is_hidden = True
            order_item.update_date = datetime.today()
            order_item.update_by = self.request.user
            order_item.save()
            result = order_item.is_hidden
        except Exception as e:
            print(e)
        return result

    def save_order_qty(self, trx_data, last_qty=None, last_order_status=None, is_delete=False):
        result = False
        status = UPDATE_LOCATION_ITEM_FAILED % (trx_data['item_code'], trx_data['location_code'])
        try:
            location_item = self.item_location
            if not location_item:
                if self.get_item_location(trx_data['location_id'], trx_data['item_id']):
                    location_item = self.item_location

            if location_item:
                current_qty = self.enhanced_qty(trx_data, last_qty, last_order_status, is_delete)
                oh_qty = location_item.onhand_qty if location_item.onhand_qty else 0
                bo_qty = location_item.booked_qty if location_item.booked_qty else 0
                in_qty = location_item.in_qty if location_item.in_qty else 0
                out_qty = location_item.out_qty if location_item.out_qty else 0

                if trx_data['order_type'] == dict(ORDER_TYPE)['SALES ORDER']:
                    location_item.booked_qty = bo_qty + current_qty
                elif trx_data['order_type'] == dict(ORDER_TYPE)['PURCHASE INVOICE']:
                    location_item.onhand_qty = oh_qty + current_qty
                    location_item.in_qty = in_qty + current_qty
                elif trx_data['order_type'] == dict(ORDER_TYPE)['SALES INVOICE']:
                    location_item.onhand_qty = oh_qty - current_qty
                    if location_item.booked_qty:
                        location_item.booked_qty = bo_qty - current_qty
                    location_item.out_qty = out_qty + current_qty
                location_item.update_by = self.request.user.id
                location_item.update_date = datetime.today()
                location_item.save()
                result = True
                status = None
        except Exception as e:
            print(e)
            
        return result, status

    def save_location_item(self, orderitem_id, last_qty=None, last_order_status=None, is_delete=False):
        result = []
        try:
            order_detail = self.order_details
            if not order_detail:
                order_detail = self.get_order_detail(orderitem_id)

            if order_detail and order_detail['location_detail']:
                try:
                    is_updated, update_status = self.save_order_qty(order_detail, last_qty, last_order_status,
                                                                    is_delete)
                    if not is_updated:
                        result.append(update_status)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        return result

    def enhanced_qty(self, item, last_qty=None, last_order_status=None, is_delete=False):
        if is_delete:
            enhanced_qty = item['qty'] * -1
        else:
            enhanced_qty = item['qty']
            if last_order_status and int(last_order_status) != int(dict(ORDER_STATUS)['Draft']):
                if last_qty:
                    for lst_qty in last_qty:
                        if int(item['order_type']) == dict(ORDER_TYPE)['SALES ORDER']:
                            if lst_qty['item_id'] and lst_qty['item_id'] != '' and \
                                    int(item['item_id']) == int(lst_qty['item_id']):
                                enhanced_qty = Decimal(item['qty']) - Decimal(lst_qty['qty'])
                                break
                        else:
                            if lst_qty['item_id'] and lst_qty['item_id'] != '' and \
                                int(item['item_id']) == int(lst_qty['item_id']) and \
                                    item['refer_doc_no'] == lst_qty['refer_doc'] and \
                                    item['refer_doc_ln'] == lst_qty['refer_line'] and \
                                    int(item['line_number']) == int(lst_qty['ln']):
                                enhanced_qty = Decimal(item['qty']) - Decimal(lst_qty['qty'])
                                break
        return enhanced_qty

    # note for later = backorder qty di locationitem nggak ada kalo datanya hasil migrasi, bahaya
    def save_item_file_qty(self, orderitem_id, last_qty=None, last_order_status=None, is_delete=False):
        result = []
        try:
            order_detail = self.order_details
            if not order_detail:
                order_detail = self.get_order_detail(orderitem_id)
            try:
                item = Item.objects.get(pk=order_detail['item_id'])
                if item:
                    current_qty = Decimal(
                        self.enhanced_qty(order_detail, last_qty, last_order_status, is_delete))
                    so_qty0 = item.so_qty if item.so_qty else 0
                    po_qty0 = item.po_qty if item.po_qty else 0
                    bo_qty = item.backorder_qty if item.backorder_qty else 0
                    in_qty = item.in_qty if item.in_qty else 0
                    out_qty = item.out_qty if item.out_qty else 0
                    
                    if order_detail['order_type'] == dict(ORDER_TYPE)['SALES ORDER']:
                        item.backorder_qty = bo_qty + current_qty
                        item.so_qty = so_qty0 + current_qty
                    elif order_detail['order_type'] == dict(ORDER_TYPE)['PURCHASE ORDER']:
                        item.po_qty = po_qty0 + current_qty
                    elif order_detail['order_type'] == dict(ORDER_TYPE)['PURCHASE INVOICE']:
                        item.in_qty = in_qty + current_qty
                        if bo_qty:
                            item.backorder_qty = bo_qty - current_qty
                        item.last_purchase_price = order_detail['price']
                        item.last_purchase_date = datetime.today()
                        item.last_purchase_doc = order_detail['document_number']
                        if not item.cost_price or item.cost_price == 0:
                            item.cost_price = order_detail['price']
                        else:
                            item.cost_price = (order_detail['price'] + item.cost_price) / 2
                        item.update_date = datetime.today()
                        item.update_by = self.request.user.id
                        item.move_date = datetime.today()
                    elif order_detail['order_type'] == dict(ORDER_TYPE)['SALES INVOICE']:
                        item.out_qty = out_qty + current_qty
                        item.update_date = datetime.today()
                        item.update_by = self.request.user.id
                    item.save()
            except Exception as e:
                print(e)
                result.append(UPDATE_ITEM_FILE_FAILED)
                pass
        except Exception as e:
            print(e)
            result.append(UPDATE_ITEM_FILE_FAILED)
            pass
        return result


class my_error():
    errors = None

    def __init__(self):
        self.clear_errors()

    def set_errors(self, error_msg):
        self.errors.append(error_msg)

    def get_errors(self):
        return self.errors

    def clear_errors(self):
        self.errors = []


class accounting_entry(my_error):
    request = None
    batch = None
    batch_status = None
    journal = None
    transaction = None
    transaction_types = None
    company = None
    order = None

    def __init__(self, request):
        super(accounting_entry, self).__init__()
        self.request = request
        self.batch = None
        self.transaction_types = dict(TRANSACTION_TYPES_REVERSED)
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            self.company = Company.objects.get(pk=company_id, is_hidden=False)
        except Exception as e:
            print(e)
            self.company = None

    def new_batch(self, batch_type, currency=None):
        try:
            batch = Batch()
            batch.company_id = self.company.id
            batch.batch_no = generate_batch_number(self.company.id, batch_type)
            batch.batch_date = self.order.document_date
            batch.batch_type = batch_type
            batch.currency_id = currency.id if currency else None
            batch.status = int(STATUS_TYPE_DICT['Open'])
            batch.source_ledger = self.get_source_ledger(batch_type)
            batch.create_date = self.order.create_date
            batch.update_date = self.order.update_date
            batch.update_by = self.request.user.id
            batch.save()
            if batch.id:
                self.batch = batch
        except Exception as e:
            print(e)
            self.set_errors(RV_ERR_CREATE_BATCH)
        return self.batch

    def set_batch_as_deleted(self, batch_id):
        result = False
        try:
            batch = self.batch if self.is_batch_exist(batch_id) else None
            if batch:
                journals = Journal.objects.filter(batch_id=batch.id, is_hidden=False, company_id=self.company.id)
                if journals:
                    for journal in journals:
                        self.delete_journal(journal.id)
                batch.status = int(STATUS_TYPE_DICT['Deleted'])
                batch.save()
                self.batch = None
                result = True
        except Exception as e:
            print(e)
        return result

    def delete_batch(self, batch_id):
        result = False
        try:
            batch = self.batch if self.is_batch_exist(batch_id) else None
            if batch:
                journals = Journal.objects.filter(batch_id=batch.id, is_hidden=False, company_id=self.company.id)
                if journals:
                    for journal in journals:
                        self.delete_journal(journal.id)
                batch.delete()
                self.batch = None
                result = True
        except Exception as e:
            print(e)
        return result

    def hide_batch(self, batch_id):
        result = False
        try:
            batch = self.batch if self.is_batch_exist(batch_id) else None
            if batch:
                journals = Journal.objects.filter(batch_id=batch.id, is_hidden=False, company_id=self.company.id)
                if journals:
                    for journal in journals:
                        self.hide_journal(journal.id)
                batch.is_hidden = True
                batch.save()
                self.batch = None
                result = True
        except Exception as e:
            print(e)
        return result

    def set_batch_as_error(self, batch_id):
        result = False
        try:
            batch = self.batch
            if not batch:
                batch = self.batch if self.is_batch_exist(batch_id) else None
            if batch:
                batch.status = STATUS_TYPE_DICT['ERROR']
                batch.save()
                self.batch = None
                result = True
                self.set_errors(BATCH_ERROR)
        except Exception as e:
            print(e)
        return result

    def is_batch_exist(self, batch_id):
        result = False
        try:
            batch = Batch.objects.get(pk=batch_id, is_hidden=False, company_id=self.company.id)
            if batch:
                self.batch = batch
                result = True
        except Exception as e:
            print(e)
        return result

    def get_source_ledger(self, transaction_type):
        if self.transaction_types.get(int(transaction_type)) == 'AR Invoice':
            source_ledger = SOURCE_LEDGER_DICT['Account Receivable']
        elif self.transaction_types.get(int(transaction_type)) == 'AP Invoice':
            source_ledger = SOURCE_LEDGER_DICT['Account Payable']
        else:
            source_ledger = SOURCE_LEDGER_DICT['General Ledger']
        return source_ledger

    def new_journal(self, batch):
        self.journal = None
        try:
            journal = Journal()
            journal.journal_type = batch.batch_type
            journal.document_date = self.order.document_date
            journal.company_id = self.company.id
            journal.status = int(STATUS_TYPE_DICT['Open'])
            journal.batch_id = batch.id
            journal.create_date = self.order.create_date
            journal.update_date = self.order.update_date
            journal.update_by = self.request.user.id
            journal.save()
            if journal.id:
                self.journal = journal
        except Exception as e:
            print(e)
            self.set_errors(CREATE_JOURNAL_FAILED)
        return self.journal

    def delete_journal(self, journal_id):
        result = False
        try:
            journal = Journal.objects.get(pk=journal_id, is_hidden=False, company_id=self.company.id)
            if journal:
                transactions = Transaction.objects.filter(journal_id=journal.id, is_hidden=False,
                                                          company_id=self.company.id)
                if transactions:
                    for transaction in transactions:
                        transaction.delete()
                journal.delete()
                self.journal = None
                result = True
        except Exception as e:
            print(e)
        return result

    def hide_journal(self, journal_id):
        result = False
        try:
            journal = Journal.objects.get(pk=journal_id, is_hidden=False, company_id=self.company.id)
            if journal:
                transactions = Transaction.objects.filter(journal_id=journal.id, is_hidden=False,
                                                          company_id=self.company.id)
                if transactions:
                    for transaction in transactions:
                        transaction.is_hidden = True
                        transaction.save()
                journal.is_hidden = True
                journal.save()
                self.journal = None
                result = True
        except Exception as e:
            print(e)
        return result

    def new_transaction(self, journal_id):
        self.transaction = None
        try:
            transaction = Transaction()
            transaction.company_id = self.company.id
            transaction.journal_id = journal_id
            transaction.transaction_date = self.order.document_date
            transaction.create_date = self.order.create_date
            transaction.update_date = self.order.update_date
            transaction.update_by = self.request.user.id
            transaction.save()
            if transaction:
                self.transaction = transaction
        except Exception as e:
            print(e)
            self.set_errors(CREATE_JOURNAL_FAILED)
        return self.transaction

    def delete_transaction(self, transaction_id):
        result = False
        try:
            transaction = Transaction.objects.filter(pk=transaction_id, is_hidden=False, company_id=self.company.id)
            transaction.delete()
            result = True
        except Exception as e:
            print(e)
        return result

    def hide_transaction(self, transaction_id):
        result = False
        try:
            transaction = Transaction.objects.filter(pk=transaction_id, is_hidden=False, company_id=self.company.id)
            transaction.is_hidden = True
            transaction.save()
            result = True
        except Exception as e:
            print(e)
        return result


class sp_to_acc(accounting_entry):
    def __init__(self, request):
        super(sp_to_acc, self).__init__(request)

    def generate_acc_entry(self, batch_type, order, CN_DN_type=None):
        result = False
        oorder = Order.objects.get(pk=order.id)
        if oorder:
            self.order = oorder
        batch = self.get_or_create_batch(batch_type, order, CN_DN_type)
        if batch:
            entries = self.create_entries(batch, order)
            if entries:
                if len(self.get_errors()) > 0:
                    if not self.delete_journal(entries.id):
                        self.hide_journal(entries.id)
                else:
                    result = True
        return result

    def create_entries(self, batch, order, CN_DN_type=None):
        self.journal = None
        journal = self.new_draft_journal(batch, order, CN_DN_type)
        if journal:
            transaction = self.new_draft_transaction(journal, order)
            if transaction:
                self.journal = journal
        return self.journal

    def check_batch_status(self, batch_type, order, CN_DN_type=None):
        batch_status = None
        self.company_id = order.company_id
        oorder = Order.objects.get(pk=order.id)
        if oorder:
            self.order = oorder
            batch_status = self.get_batch_status(batch_type, oorder.currency)

        return batch_status

    def update_acc_entry(self, batch_type, order, CN_DN_type=None):
        result = False
        oorder = Order.objects.get(pk=order.id)
        if oorder:
            self.order = oorder
        batch = self.get_or_create_batch(batch_type, order, CN_DN_type)
        if batch:
            old_draft_journal = self.journal if self.get_draft_journal(batch, order.id) else None
            if old_draft_journal:
                if self.hide_journal(old_draft_journal.id):
                    batch.status = int(STATUS_TYPE_DICT['Open'])
                    batch.no_entries -= 1
                    batch.batch_amount -= old_draft_journal.total_amount
                    batch.save()
                    return self.generate_acc_entry(batch_type, order)
            else:
                result = self.create_entries(batch, order)
        return result

    def delete_acc_entry(self, batch_type, order, CN_DN_type=None):
        result = False
        oorder = Order.objects.get(pk=order.id)
        if oorder:
            self.order = oorder
        batch = self.get_or_create_batch(batch_type, order, CN_DN_type)
        if batch:
            journal = self.journal if self.get_draft_journal(batch, order.id) else None
            if journal:
                if self.hide_journal(journal.id):
                    batch.status = int(STATUS_TYPE_DICT['Open'])
                    batch.no_entries -= 1
                    batch.batch_amount -= journal.total_amount
                    batch.save()
                    result = True
                    if not batch.no_entries:
                        if not self._set_draft_batch_as_deleted(batch.id):
                            if not self._delete_draft_batch(batch.id):
                                return False
        if not result:
            self.clear_errors()
            self.set_errors('Warning: ' + DELETE_DRAFT_JOURNAL_FAILED)
        return result

    def get_or_create_batch(self, batch_type, order, CN_DN_type=None):
        self.company_id = order.company_id
        draft_batch = self.get_draft_batch(batch_type, order.currency)
        if not draft_batch:
            draft_batch = self.new_batch(batch_type)
            if draft_batch:
                if not self._set_draft_batch(draft_batch, order.currency, CN_DN_type):
                    if not self._delete_draft_batch(draft_batch.id):
                        return None
        return draft_batch

    def get_draft_batch(self, batch_type, currency):
        try:
            draft_batch = Batch.objects. \
                filter(batch_date__month=self.order.document_date.month,
                       batch_date__year=self.order.document_date.year,
                       batch_type=batch_type, company_id=self.company_id,
                       status=int(STATUS_TYPE_DICT['Open']),
                       currency_id=currency.id, is_hidden=False). \
                first()

            if draft_batch:
                self.batch = draft_batch

        except Exception as e:
            print(e)
        return self.batch

    def get_batch_status(self, batch_type, currency):
        try:
            draft_batch = Batch.objects. \
                filter(batch_date__month=self.order.document_date.month,
                       batch_date__year=self.order.document_date.year,
                       batch_type=batch_type, company_id=self.company_id,
                       currency_id=currency.id, is_hidden=False). \
                first()

            if draft_batch:
                self.batch_status = draft_batch.status

        except Exception as e:
            print(e)
        return self.batch_status

    def _set_draft_batch(self, batch, currency, CN_DN_type=None):
        result = False
        try:
            batch.description = self._generate_draft_batch_desc(batch.batch_type, CN_DN_type) + str(
                self.order.document_date.month) + '/' + str(
                self.order.document_date.year) + ' (' + currency.code + ')'
            batch.currency_id = currency.id
            batch.input_type = int(INPUT_TYPE_DICT['Generated'])
            batch.status = int(STATUS_TYPE_DICT['Open'])
            batch.save()
            result = True
            self.batch = batch
        except Exception as e:
            print(e)
            self.clear_errors()
            self.set_errors(DRAFT_BATCH_FAILED)
        return result

    def _delete_draft_batch(self, batch_id):
        if not self.delete_batch(batch_id):
            if not self.hide_batch(batch_id):
                if not self.set_batch_as_error(batch_id):
                    return False
        return True

    def _set_draft_batch_as_deleted(self, batch_id):
        if not self.set_batch_as_deleted(batch_id):
            if not self.hide_batch(batch_id):
                if not self.set_batch_as_error(batch_id):
                    if not self.delete_batch(batch_id):
                        return False
        return True

    def new_draft_journal(self, batch, order, CN_DN_type=None):
        journal = self.new_journal(batch)
        if journal:
            try:
                # journal.name = self._generate_draft_journal_desc(batch.batch_type, CN_DN_type) + order.document_number
                journal.document_type = self.get_document_type(CN_DN_type)
                journal.order_id = order.id

                if self.transaction_types.get(int(batch.batch_type)) == 'AR Invoice':
                    journal.customer_id = order.customer_id
                    journal.name = order.customer.name
                    acc_set = Customer.objects.get(pk=order.customer_id, is_hidden=False)
                    journal.account_set_id = acc_set.account_set_id
                    journal.due_date = self.order.document_date + timedelta(
                        days=int(order.customer.payment_term)) if order.customer.payment_term else None
                    exchange_rate = self.get_exchange_rate(order.customer.currency_id, self.company.currency_id)
                else:
                    journal.supplier_id = order.supplier_id
                    journal.name = order.supplier.name if order.supplier.name else ''
                    acc_set = Supplier.objects.get(pk=order.supplier_id, is_hidden=False)
                    journal.account_set_id = acc_set.account_set_id
                    journal.due_date = self.order.document_date + timedelta(
                        days=int(order.supplier.term_days)) if order.supplier.term_days else None
                    exchange_rate = self.get_exchange_rate(order.supplier.currency_id, self.company.currency_id)

                journal.currency_id = order.currency_id
                journal.tax_id = order.tax_id
                journal.document_number = order.document_number
                journal.amount = order.subtotal
                journal.tax_amount = order.tax_amount
                journal.total_amount = order.total
                journal.outstanding_amount = order.total
                journal.document_amount = order.total
                journal.posting_date = self.order.document_date
                fsc_calendar = FiscalCalendar.objects.filter(company_id=self.company.id, is_hidden=0,
                                                                start_date__lte=self.order.document_date, end_date__gte=self.order.document_date).first()
                if fsc_calendar:
                    year = fsc_calendar.fiscal_year
                    month = fsc_calendar.period
                else:
                    year = self.order.document_date.year
                    month = self.order.document_date.month
                journal.perd_month = month
                journal.perd_year = year
                if not order.exchange_rate_fk_id:
                    if exchange_rate:
                        journal.exchange_rate = exchange_rate.rate
                        journal.exchange_rate_fk_id = exchange_rate.id
                    else:
                        journal.exchange_rate = order.exchange_rate
                else:
                    journal.exchange_rate = order.exchange_rate
                    journal.exchange_rate_fk_id = order.exchange_rate_fk_id

                batch.batch_amount += journal.total_amount
                batch.no_entries += 1
                batch.save()

                journals = Journal.objects.filter(
                    batch_id=batch.id, is_hidden=False).exclude(
                    code__isnull=True).order_by('id')
                if journals:
                    new_code = int(journals.last().code) + 1
                    journal.code = new_code
                else:
                    journal.code = 1
                
                journal.status = int(STATUS_TYPE_DICT['Open'])
                journal.save()
                self.journal = journal
            except Exception as e:
                print(e)
                self.clear_errors()
                self.set_errors(DRAFT_JOURNAL_FAILED)
        return self.journal

    def get_draft_journal(self, batch, order_id):
        self.journal = None
        try:
            draft_journal = Journal.objects. \
                filter(batch_id=batch.id,
                       batch__status=int(STATUS_TYPE_DICT['Open']),
                       batch__is_hidden=False,
                       batch__company_id=self.company.id,
                       is_hidden=False,
                       company_id=self.company.id,
                       order_id=order_id).first()
            if draft_journal:
                self.journal = draft_journal
        except Exception as e:
            print(e)
        return self.journal

    def new_draft_transaction(self, journal, order, CN_DN_type=None):
        transaction = self.new_transaction(journal.id)
        if transaction:
            try:
                transaction.number = 1
                transaction.order_id = journal.order_id
                transaction.currency_id = order.currency_id
                transaction.is_debit_account = self.is_debit_account(journal, CN_DN_type)
                transaction.is_credit_account = not transaction.is_debit_account
                transaction.account_id = self.get_gl_account(order, journal.journal_type)
                transaction.amount = order.subtotal
                transaction.tax_id = order.tax_id
                transaction.tax_amount = order.tax_amount
                transaction.total_amount = order.total
                transaction.remark = order.remark
                transaction.distribution_code_id = order.distribution_code_id
                if not order.exchange_rate_fk_id:
                    if self.transaction_types.get(int(journal.batch.batch_type)) == 'AR Invoice':
                        exchange_rate = self.exchange_rate if self.exchange_rate else self.get_exchange_rate(
                            order.customer.currency_id, self.company.currency_id)
                    else:
                        exchange_rate = self.exchange_rate if self.exchange_rate else self.get_exchange_rate(
                            order.supplier.currency_id, self.company.currency_id)
                    if exchange_rate:
                        transaction.exchange_rate = exchange_rate.rate
                        transaction.rate_date = exchange_rate.exchange_date
                    else:
                        transaction.exchange_rate = order.exchange_rate
                        transaction.rate_date = order.exchange_rate_date
                else:
                    transaction.exchange_rate = order.exchange_rate
                    transaction.rate_date = order.exchange_rate_date
                transaction.functional_currency_id = self.company.currency_id
                transaction.functional_amount = float(transaction.total_amount) * float(transaction.exchange_rate)
                transaction.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                        BALANCE_TYPE_DICT['Debit'])[transaction.is_debit_account]
                transaction.save()
                self.transaction = transaction
            except Exception as e:
                print(e)
                self.clear_errors()
                self.set_errors(DRAFT_JOURNAL_FAILED)
        return self.transaction

    def get_draft_transaction(self, journal):
        self.transaction = None
        try:
            draft_transaction = Transaction.objects. \
                filter(journal_id=journal.id,
                       journal__is_hidden=False,
                       journal__company_id=self.company.id,
                       is_hidden=False,
                       company_id=self.company.id)
            if draft_transaction:
                self.transaction = draft_transaction
        except Exception as e:
            print(e)
        return self.transaction

    def get_exchange_rate(self, from_currency, to_currency):
        self.exchange_rate = None
        try:
            exchange_rate = ExchangeRate.objects. \
                filter(is_hidden=False,
                       company_id=self.company.id,
                       from_currency_id=from_currency,
                       to_currency_id=to_currency,
                       exchange_date__month=self.order.document_date.month,
                       exchange_date__year=self.order.document_date.year,
                       flag=EXCHANGE_RATE_TYPE['3']). \
                order_by('exchange_date').last()
            if exchange_rate:
                self.exchange_rate = exchange_rate
        except Exception as e:
            print(e)
        return self.exchange_rate

    def _generate_draft_batch_desc(self, batch_type, CN_DN_type=None):
        if self.transaction_types.get(int(batch_type)) == 'AR Invoice':
            if not CN_DN_type:
                batch_desc = 'SALES INVOICE '
            else:
                batch_desc = 'SALES DEBIT & CREDIT NOTE '
        else:
            if not CN_DN_type:
                batch_desc = 'PURCHASE INVOICE '
            else:
                batch_desc = 'PURCHASES DEBIT & CREDIT NOTE '
        return batch_desc

    def _generate_draft_journal_desc(self, journal_type, CN_DN_type=None):
        journal_desc = ""
        if self.transaction_types.get(int(journal_type)) == 'AR Invoice':
            if not CN_DN_type:
                journal_desc = 'Generate from Sales '
            elif CN_DN_type == dict(ORDER_TYPE)['SALES DEBIT NOTE']:
                journal_desc = 'Generate from Sales Debit Note '
            else:
                journal_desc = 'Generate from Sales Credit Note '
        elif self.transaction_types.get(int(journal_type)) == 'AP Invoice':
            if not CN_DN_type:
                journal_desc = 'Generate from Purchase '
            elif CN_DN_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']:
                journal_desc = 'Generate from Purchase Debit Note '
            else:
                journal_desc = 'Generate from Purchase Credit Note '
        return journal_desc

    def get_document_type(self, CN_DN_type=None):
        document_type = DOCUMENT_TYPE_DICT['Invoice']
        if CN_DN_type:
            if CN_DN_type == dict(ORDER_TYPE)['PURCHASE DEBIT NOTE']:
                document_type = DOCUMENT_TYPE_DICT['Debit Note']
            else:
                document_type = DOCUMENT_TYPE_DICT['Credit Note']
        return document_type

    def is_debit_account(self, journal, CN_DN_type=None):
        is_debit_account = False
        if self.transaction_types.get(int(journal.journal_type)) == 'AR Invoice':
            if not CN_DN_type:
                is_debit_account = (False, True)[journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
            else:
                is_debit_account = (True, False)[journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
        elif self.transaction_types.get(int(journal.journal_type)) == 'AP Invoice':
            if not CN_DN_type:
                is_debit_account = (True, False)[journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
            else:
                is_debit_account = (False, True)[journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
        return is_debit_account

    def get_gl_account(self, order, journal_type):
        gl_account = None
        try:
            if order.distribution_code_id:
                gl_account = Account.objects.get(id=order.distribution_code.gl_account_id)
            if not gl_account:
                if self.transaction_types.get(int(journal_type)) == 'AR Invoice':
                    if order.customer.account_receivable_id:
                        gl_account = Account.objects.get(id=order.customer.account_receivable_id).id
                    elif order.customer.tax.distribution_code_id:
                        gl_account = Account.objects.get(id=order.customer.tax.distribution_code.gl_account_id).id
                    elif order.customer.account_set:
                        gl_account = Account.objects.get(id=order.customer.account_set.control_account_id).id
                    else:
                        gl_account = Account.objects.get(id=order.customer.distribution_code.gl_account_id).id
                elif self.transaction_types.get(int(journal_type)) == 'AP Invoice':
                    if order.supplier.account_payable_id:
                        gl_account = Account.objects.get(id=order.supplier.account_payable_id).id
                    elif order.supplier.tax.distribution_code_id:
                        gl_account = Account.objects.get(id=order.supplier.tax.distribution_code.gl_account_id).id
                    elif order.supplier.account_set:
                        gl_account = Account.objects.get(id=order.supplier.account_set.control_account_id).id
                    else:
                        gl_account = Account.objects.get(id=order.supplier.distribution.gl_account_id).id
        except Exception as e:
            print(e)
        return gl_account


def generate_errors(errors):
    error_strings = ''
    for err in errors:
        error_strings += err + '<br />'
    if not error_strings:
        error_strings = MESSAGE_ERROR
    else:
        error_strings += REFRESH_OR_GO_GET_SUPPORT
    return error_strings


def add_one_month(t):
    """Return a `datetime.date` or `datetime.datetime` (as given) that is
    one month earlier.

    Note that the resultant day of the month might change if the following
    month has fewer days:

        >>> add_one_month(datetime.date(2010, 1, 31))
        datetime.date(2010, 2, 28)
    """
    import datetime
    one_day = datetime.timedelta(days=1)
    one_month_later = t + one_day
    while one_month_later.month == t.month:  # advance to start of next month
        one_month_later += one_day
    target_month = one_month_later.month
    while one_month_later.day < t.day:  # advance to appropriate day
        one_month_later += one_day
        if one_month_later.month != target_month:  # gone too far
            one_month_later -= one_day
            break
    return one_month_later


def subtract_one_month(t):
    """Return a `datetime.date` or `datetime.datetime` (as given) that is
    one month later.

    Note that the resultant day of the month might change if the following
    month has fewer days:

        >>> subtract_one_month(datetime.date(2010, 3, 31))
        datetime.date(2010, 2, 28)
    """
    import datetime
    one_day = datetime.timedelta(days=1)
    one_month_earlier = t - one_day
    while one_month_earlier.month == t.month or one_month_earlier.day > t.day:
        one_month_earlier -= one_day
    return one_month_earlier


def round_number(number, decimal_num=None, direction=None):
    # number = Decimal("{:.12f}".format(float(number)))
    try:
        str_number = str(number)
        if len(str_number.split('.')[1]) > 2:
            number = Decimal(str_number + '1111111')
    except:
        pass
    getcontext().prec = 20
    decimal_place = '1.'
    if decimal_num == None:
        decimal_num = 2
    while decimal_num > 0:
        decimal_place += '0'
        decimal_num -= 1

    value = 0
    if direction == None:
        direction == 'up'
    try:
        if direction == 'up':
            value = Decimal(number).quantize(Decimal(decimal_place), rounding=ROUND_HALF_UP)
        elif direction == 'even':
            value = Decimal(number).quantize(Decimal(decimal_place), rounding=ROUND_HALF_EVEN)
        elif direction == 'down':
            value = Decimal(number).quantize(Decimal(decimal_place), rounding=ROUND_HALF_DOWN)
        else:
            value = Decimal(number).quantize(Decimal(decimal_place), rounding=ROUND_HALF_UP)
    except InvalidOperation as e:
        print(number, decimal_place, getcontext().prec)
        print("Error:", str(e))
        value = Decimal(number).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
    return value


def get_decimal_place(currency):
    try:
        if currency.is_decimal:
            decimal_place = "%.2f"
        else:
            decimal_place = "%.0f"
    except:
        decimal_place = "%.2f"

    return decimal_place


def get_recurring_nearest_batches(company_id, batch_type, batch_no):
    prev_batch = 0
    next_batch = 0
    try:
        batches = RecurringBatch.objects.filter(is_hidden=0, company_id=company_id, batch_type=batch_type) \
            .exclude(status=int(STATUS_TYPE_DICT['Deleted'])) \
            .values('id', 'batch_no')
        batch_list = sorted(batches, key=lambda B: int(B['batch_no']))

        if batch_list:
            if batch_no:
                i = 0
                while i < len(batch_list):
                    if i != 0 and int(batch_no) == int(batch_list[i]['batch_no']):
                        p_journals = RecurringEntry.objects.filter(is_hidden=0, batch_id=int(batch_list[i - 1]['id'])) \
                            .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                            .exclude(document_type=DOCUMENT_TYPE_DICT['Adjustment']) \
                            .values('id', 'code')
                        if p_journals:
                            p_journals = sorted(p_journals, key=lambda J: int(J['code']))
                            prev_batch = p_journals[0]['id']

                        if i < len(batch_list) - 1:
                            n_journals = RecurringEntry.objects.filter(is_hidden=0, batch_id=int(batch_list[i + 1]['id'])) \
                                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                                .exclude(document_type=DOCUMENT_TYPE_DICT['Adjustment']) \
                                .values('id', 'code')
                            if n_journals:
                                n_journals = sorted(n_journals, key=lambda J: int(J['code']))
                                next_batch = n_journals[0]['id']

                        break

                    i += 1

            else:
                p_batch = int(batch_list[-1]['id'])
                p_journals = RecurringEntry.objects.filter(is_hidden=0, batch_id=p_batch) \
                    .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                    .exclude(document_type=DOCUMENT_TYPE_DICT['Adjustment']) \
                    .values('id', 'code')
                if p_journals:
                    p_journals = sorted(p_journals, key=lambda J: int(J['code']))
                    prev_batch = p_journals[0]['id']
    except Exception as e:
        print('get_nearest_batches', e)

    return prev_batch, next_batch


def get_related_batches(company_id, batch_type, batch_no):
    first_batch = 0
    last_batch = 0
    prev_batch = 0
    next_batch = 0
    try:
        batches = Batch.objects.filter(is_hidden=0, company_id=company_id, batch_type=batch_type) \
            .exclude(status=int(STATUS_TYPE_DICT['Deleted'])) \
            .values('id', 'batch_no')
        batch_list = sorted(batches, key=lambda B: int(B['batch_no']))

        if batch_list:
            first_batch = batch_list[0]['id']
            last_batch = batch_list[len(batch_list) - 1]['id']
            if batch_no:
                i = 0
                while i < len(batch_list):
                    if i != 0 and int(batch_no) == int(batch_list[i]['batch_no']):
                        prev_batch = int(batch_list[i - 1]['id'])
                        if i < len(batch_list) - 1:
                            next_batch = int(batch_list[i + 1]['id'])
                        
                        break
                    i += 1

    except Exception as e:
        print('get_related_batches', e)

    return first_batch, prev_batch, next_batch, last_batch


def get_nearest_batches(company_id, batch_type, batch_no):
    prev_batch = 0
    next_batch = 0
    try:
        batches = Batch.objects.filter(is_hidden=0, company_id=company_id, batch_type=batch_type) \
            .exclude(status=int(STATUS_TYPE_DICT['Deleted'])) \
            .values('id', 'batch_no')
        batch_list = sorted(batches, key=lambda B: int(B['batch_no']))

        if batch_list:
            if batch_no:
                i = 0
                while i < len(batch_list):
                    if i != 0 and int(batch_no) == int(batch_list[i]['batch_no']):
                        p_journals = Journal.objects.filter(is_hidden=0, batch_id=int(batch_list[i - 1]['id'])) \
                            .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                            .exclude(document_type=DOCUMENT_TYPE_DICT['Adjustment']) \
                            .values('id', 'code')
                        if p_journals:
                            p_journals = sorted(p_journals, key=lambda J: int(J['code']))
                            prev_batch = p_journals[0]['id']

                        if i < len(batch_list) - 1:
                            n_journals = Journal.objects.filter(is_hidden=0, batch_id=int(batch_list[i + 1]['id'])) \
                                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                                .exclude(document_type=DOCUMENT_TYPE_DICT['Adjustment']) \
                                .values('id', 'code')
                            if n_journals:
                                n_journals = sorted(n_journals, key=lambda J: int(J['code']))
                                next_batch = n_journals[0]['id']

                        break

                    i += 1

            else:
                p_batch = int(batch_list[-1]['id'])
                p_journals = Journal.objects.filter(is_hidden=0, batch_id=p_batch) \
                    .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                    .exclude(document_type=DOCUMENT_TYPE_DICT['Adjustment']) \
                    .values('id', 'code')
                if p_journals:
                    p_journals = sorted(p_journals, key=lambda J: int(J['code']))
                    prev_batch = p_journals[0]['id']
    except Exception as e:
        print('get_nearest_batches', e)

    return prev_batch, next_batch


def get_batch_journals(batch_id, journal, is_recurring=False):
    prev_journal = 0
    next_journal = 0
    first_journal = 0
    last_journal = 0
    cur_entry = 0

    try:
        if is_recurring:
            journal_list = RecurringEntry.objects.filter(is_hidden=0, batch_id=batch_id) \
                .exclude(journal_type=11) \
                .exclude(document_type='10') \
                .values('id', 'code')
        else:
            journal_list = Journal.objects.filter(is_hidden=0, batch_id=batch_id) \
                .exclude(journal_type=11) \
                .exclude(document_type='10') \
                .exclude(reference='REVERSING ENTRY') \
                .values('id', 'code')

        if journal_list:
            journals_list = sorted(journal_list, key=lambda J: int(J['code']))
            if not journal:
                first_journal = journals_list[0]['id']
            elif journal.id != journals_list[0]['id']:
                first_journal = journals_list[0]['id']

            if journal and journal.id != journals_list[-1]['id']:
                last_journal = journals_list[-1]['id']
            else:
                prev_journal = journals_list[-1]['id']

            if journal and int(journal.code) >= 1:
                for i, j in enumerate(journals_list):
                    if j['code'] == journal.code and j['id'] == journal.id:
                        prev_journal = journals_list[i - 1]['id'] if i != 0 else 0
                        next_journal = journals_list[i + 1]['id'] if i < len(journals_list) - 1 else 0
                        break
    except Exception as e:
        print('get_batch_journals', e)

    return prev_journal, next_journal, first_journal, last_journal


def check_leap_year(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        False
