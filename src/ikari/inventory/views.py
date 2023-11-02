import datetime
import calendar
import json
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import F, Q
from django.db.models.fields import DecimalField, CharField
from django.db.models.functions import Value
from django.forms.formsets import formset_factory
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext

from accounting.models import FiscalCalendar
from companies.models import Company
from currencies.models import Currency
from inventory.forms import TransCodeForm, StockTransForm, StockTransItemForm, file_control
from inventory.models import TransactionCode, StockTransactionDetail, StockTransaction, Incoming, Outgoing, History
from items.models import Item
from locations.models import Location, LocationItem
from utilities.common import check_inventory_closing, generate_document_number, Location_Item, \
    get_item_onhandqty, round_number
from utilities.constants import INV_IN_OUT_FLAG, INV_PRICE_FLAG, INV_DOC_TYPE, ST_REPORT_LIST, ORDER_STATUS, \
    TRN_CODE_TYPE_DICT


# Create your views here.
@login_required
def transaction_code_list(request):
    try:
        return render_to_response('transaction_code_list.html',
                                  RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Inventory Code']}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def load_file_control(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        currency_list = Currency.objects.filter(is_hidden=0)

        if request.method == 'POST':
            company.address = request.POST.get('address')
            if company.closing_date != request.POST.get('closing_date'):
                company.closing_date = request.POST.get('closing_date')
                company.update_date = datetime.datetime.now().strftime('%Y-%m-%d')
            company.currency_id = request.POST.get('currency')
            company.name = request.POST.get('name')
            company.current_period_month_ic = request.POST.get('current_period_month')
            company.current_period_year_ic = request.POST.get('current_period_year')
            company.costing_method = request.POST.get('costing_method')
            company.fiscal_period = request.POST.get('fiscal_period')
            for i in range(1, 13):
                try:
                    fiscal_data = FiscalCalendar.objects.get(fiscal_year=request.POST.get('fiscal_year'), company_id=company_id, period=i)
                    fiscal_data.start_date = request.POST.get('op_' + str(i)) if request.POST.get('op_' + str(i)) else datetime.datetime.now().date()
                    fiscal_data.end_date = request.POST.get('cl_' + str(i)) if request.POST.get('cl_' + str(i)) else datetime.datetime.now().date()
                    fiscal_data.save()
                except Exception as e:
                    print(e)
                    fiscal_data = FiscalCalendar()
                    fiscal_data.company_id = company_id
                    fiscal_data.fiscal_year = request.POST.get('fiscal_year')
                    fiscal_data.period = i
                    fiscal_data.start_date = request.POST.get('op_' + str(i)) if request.POST.get('op_' + str(i)) else datetime.datetime.now().date()
                    fiscal_data.end_date = request.POST.get('cl_' + str(i)) if request.POST.get('cl_' + str(i)) else datetime.datetime.now().date()
                    fiscal_data.save()

            company.lenght_item = request.POST.get('lenght_item')
            company.size_item = request.POST.get('size_item')
            company.extent_item = request.POST.get('extent_item')
            company.group_item = request.POST.get('group_item')
            company.uom_item = request.POST.get('uom_item')
            company.stock_take = request.POST.get('stock_take')
            company.price_decimal = request.POST.get('price_decimal')
            company.save()

        company = Company.objects.get(pk=company_id)
        if company.is_inventory:
            year = int(company.current_period_year_ic)
        else:
            year = int(company.current_period_year_sp)
        fiscal_calendar = FiscalCalendar.objects.filter(
            is_hidden=0, fiscal_year=year, company_id=company_id)
        if fiscal_calendar:
            fiscal_array = list(fiscal_calendar.values())
            try:
                for fiscal in fiscal_array:
                    fiscal['start_date'] = fiscal['start_date']
                    fiscal['end_date'] = fiscal['end_date'].strftime('%d-%m-%Y')
            except Exception as e:
                raise e
        else:
            fiscal_array = []
            yesr = datetime.datetime.now().year
            for i in range(1, 13):
                month = {}
                _, num_days = calendar.monthrange(year, i)
                first_day = datetime.date(year, i, 1)
                last_day = datetime.date(year, i, num_days).strftime('%d-%m-%Y')
                month['start_date'] = first_day
                month['end_date'] = last_day
                month['period'] = i
                fiscal_array.append(month)
        form = file_control(company_id=company_id, fiscal_array=fiscal_array)
        return render_to_response('control_file.html',
                                  RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Inventory Code'],
                                                           'form': form,
                                                           'company': company,
                                                           'currency_list': currency_list}))

    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def trans_code_list_by(request, menu_type):
    try:
        return render_to_response('transaction_code_list.html', RequestContext(request, {'menu_type': menu_type}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('inventory.add_transactioncode', login_url='/alert/')
def transaction_code_add(request, menu_type):
    if request.method == 'POST':
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        form = TransCodeForm(menu_type, request.POST)
        if form.is_valid():
            try:
                trans_code = form.save(commit=False)
                trans_code.company_id = company_id
                trans_code.create_date = datetime.datetime.today()
                trans_code.update_date = datetime.datetime.today()
                trans_code.update_by = request.user.id
                trans_code.is_hidden = 0
                trans_code.menu_type = menu_type
                trans_code.doc_type = request.POST.get('doc_type')
                trans_code.io_flag = request.POST.get('io_flag') if int(request.POST.get('io_flag')) > 0 else None
                trans_code.price_flag = request.POST.get('price_flag') if int(
                    request.POST.get('price_flag')) > 0 else None
                trans_code.last_no = 0
                trans_code.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='transaction_code_add')
            if int(menu_type) == int(TRN_CODE_TYPE_DICT['Inventory Code']):
                return HttpResponsePermanentRedirect(reverse('transaction_code_list'))
            else:
                return HttpResponsePermanentRedirect(reverse('trans_code_list_by', kwargs={'menu_type': menu_type}))
        else:
            form = TransCodeForm(menu_type, request.POST)
    else:
        form = TransCodeForm(menu_type)
    return render_to_response('transaction_code.html', RequestContext(request, {'form': form, 'menu_type': menu_type}))


@login_required
@permission_required('inventory.change_transactioncode', login_url='/alert/')
def transaction_code_edit(request, trans_code_id, menu_type):
    trans_code = get_object_or_404(TransactionCode, pk=trans_code_id)
    if request.method == 'POST':
        form = TransCodeForm(menu_type, request.POST, instance=trans_code)
        if form.is_valid():
            try:
                trans_code = form.save(commit=False)
                trans_code.id = trans_code_id
                trans_code.update_date = datetime.datetime.today()
                trans_code.update_by = request.user.id
                trans_code.is_hidden = 0
                trans_code.menu_type = menu_type
                trans_code.doc_type = request.POST.get('doc_type')
                trans_code.io_flag = request.POST.get('io_flag') if int(request.POST.get('io_flag')) > 0 else None
                trans_code.price_flag = request.POST.get('price_flag') if int(
                    request.POST.get('price_flag')) > 0 else None
                trans_code.last_no = request.POST.get('last_no')
                trans_code.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='transaction_code_edit')
            if int(menu_type) == int(TRN_CODE_TYPE_DICT['Inventory Code']):
                return HttpResponsePermanentRedirect(reverse('transaction_code_list'))
            else:
                return HttpResponsePermanentRedirect(reverse('trans_code_list_by', kwargs={'menu_type': menu_type}))

    trans_code.update_date = trans_code.update_date.strftime("%d-%m-%Y")
    form = TransCodeForm(menu_type, instance=trans_code)
    return render(request, 'transaction_code.html',
                  {'form': form, 'trans_code_id': trans_code_id, 'menu_type': menu_type})


@login_required
@permission_required('inventory.delete_transactioncode', login_url='/alert/')
def transaction_code_delete(request, trans_code_id, menu_type):
    if request.method == 'POST':
        try:
            trans_code = TransactionCode.objects.get(pk=trans_code_id)
            trans_code.is_hidden = True
            trans_code.save()
            if int(menu_type) == int(TRN_CODE_TYPE_DICT['Inventory Code']):
                return HttpResponsePermanentRedirect(reverse('transaction_code_list'))
            else:
                return HttpResponsePermanentRedirect(reverse('trans_code_list_by', kwargs={'menu_type': menu_type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='transaction_code_delete')


@login_required
def load_location_list(request):
    if request.is_ajax():
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        exclude_location_id = request.GET['exclude_location_id']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        list_filter = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
        if exclude_location_id != '0':
            list_filter = list_filter.exclude(pk=exclude_location_id)

        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(Q(code__contains=search) | Q(name__contains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
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
                    "code": field.code,
                    "name": field.name,
                    "address": field.address}
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
def detail_item(request, item_id):
    list_filter = Item.objects.filter(pk=item_id) \
        .annotate(item_id=F('id')) \
        .annotate(item_name=F('name')) \
        .annotate(item_inv_measure=F('inv_measure__code')) \
        .annotate(item_onhand=Value(0, output_field=DecimalField())) \
        .annotate(item_code=F('code')) \
        .annotate(item_sale_price=F('sale_price')) \
        .annotate(item_purchase_price=F('purchase_price')) \
        .annotate(item_stockist_price=F('stockist_price')) \
        .annotate(stock_qty=Value('', output_field=CharField())) \
        .annotate(location_code=Value('', output_field=CharField()))
    array = []
    for field in list_filter:
        onhand_qty = get_item_onhandqty(field.item_id)
        if onhand_qty < 0:
            onhand_qty = 0
        data = {"item_name": field.item_name,
                "item_inv_measure": str(field.item_inv_measure),
                "item_onhand": intcomma("%.2f" % onhand_qty),
                "item_code": field.item_code,
                "item_remark": '',
                "stock_qty": str(field.stock_qty),
                "location_code": field.location_code,
                "item_id": str(field.item_id),
                "item_sale_price": str(field.sale_price),
                "item_purchase_price": str(field.purchase_price),
                "item_stockist_price": str(field.stockist_price),
                "id": str(field.item_id)}
        array.append(data)
    content = {
        "data": array
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def item_detail_loc(request):
    in_location_id = request.GET['in_location_id']
    out_location_id = request.GET['out_location_id']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    if in_location_id != '' and out_location_id != '':
        list_filter = LocationItem.objects.filter(is_hidden=0) \
            .filter(location_id=out_location_id) \
            .annotate(item_id=F('item__id')) \
            .annotate(item_name=F('item__name')) \
            .annotate(item_code=F('item__code')) \
            .annotate(location_code=F('location__code')).order_by('item__code')

    elif in_location_id != '':
        list_filter = Item.objects.filter(company_id=company_id, is_hidden=0) \
            .annotate(item_id=F('id')) \
            .annotate(item_name=F('name')) \
            .annotate(item_code=F('code')) \
            .annotate(stock_qty=Value('', output_field=CharField())) \
            .annotate(location_code=Value('', output_field=CharField())).order_by('code')
    elif out_location_id != '':
        list_filter = LocationItem.objects.filter(is_hidden=0) \
            .filter(location_id=out_location_id) \
            .annotate(item_id=F('item__id')) \
            .annotate(item_name=F('item__name')) \
            .annotate(item_code=F('item__code')) \
            .annotate(location_code=F('location__code')).order_by('item__code')
    else:
        list_filter = LocationItem.objects.none()

    # All data
    records_filtered = list_filter.count()

    # Create data list
    array = []
    data = {}
    for field in list_filter:
        data = {"item_id": field.item_id,
                "item_name": field.item_name,
                "item_code": field.item_code}
        array.append(data)

    content = {
        "data": array,
        "recordsFiltered": records_filtered
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def load_stock_transaction_items_list(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    in_location_id = request.GET['in_location_id']
    out_location_id = request.GET['out_location_id']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if in_location_id != '' and out_location_id != '':
        list_filter = LocationItem.objects.filter(is_hidden=0) \
            .filter(location_id=out_location_id) \
            .annotate(item_id=F('item__id')) \
            .annotate(item_name=F('item__name')) \
            .annotate(item_code=F('item__code')) \
            .annotate(location_code=F('location__code'))

    elif in_location_id != '':
        list_filter = Item.objects.filter(company_id=company_id, is_hidden=0) \
            .annotate(item_id=F('id')) \
            .annotate(item_name=F('name')) \
            .annotate(item_code=F('code')) \
            .annotate(stock_qty=Value('', output_field=CharField())) \
            .annotate(location_code=Value('', output_field=CharField()))
    elif out_location_id != '':
        list_filter = LocationItem.objects.filter(is_hidden=0) \
            .filter(location_id=out_location_id) \
            .annotate(item_id=F('item__id')) \
            .annotate(item_name=F('item__name')) \
            .annotate(item_code=F('item__code')) \
            .annotate(location_code=F('location__code'))
    else:
        list_filter = LocationItem.objects.none()

    records_total = list_filter.count()

    array = []
    data_len = 0

    if list_filter:
        if search:  # Filter data base on search
            list_filter = list_filter.filter(
                Q(item_code__icontains=search) | Q(item_name__icontains=search) |
                Q(location_code__icontains=search) | Q(stock_qty__icontains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "item_code"
        elif order_column == "1":
            column_name = "item_name"
        elif order_column == "2":
            column_name = "stock_qty"
        elif order_column == "3":
            column_name = "location_code"
        order_dir = request.GET['order[0][dir]']
        if order_dir == "asc":
            list_filter = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        if order_dir == "desc":
            list_filter = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        for field in list_filter:
            data = {"item_name": field.item_name,
                    "item_code": field.item_code,
                    "stock_qty": str(field.stock_qty),
                    "location_code": field.location_code,
                    "item_id": str(field.item_id),
                    "id": str(field.item_id)}
            array.append(data)
            data_len += 1

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def reset_transaction_code_list(request, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    trx_code_list = TransactionCode.objects.filter(is_hidden=0, company_id=company_id, menu_type=menu_type)
    if trx_code_list:
        for item in trx_code_list:
            item.last_no = 0
            item.update_date = datetime.datetime.today()
            item.save()
        if menu_type == '1':
            msg = 'All inventory code number reset is complete.'
        elif menu_type == '2':
            msg = 'All sales number reset is complete.'
        else:
            msg = 'All purchase code number reset is complete.'
        messages.add_message(request, messages.SUCCESS, msg, extra_tags='reset_transaction_code')

    return render_to_response('transaction_code_list.html', RequestContext(request, {'menu_type': menu_type}))


@login_required
def load_transaction_code_list(request, menu_type):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = TransactionCode.objects.filter(is_hidden=0, company_id=company_id, menu_type=menu_type)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) | Q(name__contains=search) |
            Q(io_flag__contains=search) | Q(price_flag__contains=search) |
            Q(doc_type__contains=search) |
            Q(ics_prefix__contains=search))

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
        column_name = "io_flag"
    elif order_column == "4":
        column_name = "price_flag"
    elif order_column == "5":
        column_name = "doc_type"
    elif order_column == "6":
        column_name = "auto_generate"
    elif order_column == "7":
        column_name = "ics_prefix"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    price_flag_dict = dict(INV_PRICE_FLAG)
    doc_type_dict = dict(INV_DOC_TYPE)
    io_flag_dict = dict([status[::-1] for status in INV_IN_OUT_FLAG])
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "code": field.code,
                "name": field.name,
                "io_flag": io_flag_dict.get(field.io_flag),
                "price_flag": price_flag_dict.get(field.price_flag),
                "doc_type": doc_type_dict.get(field.doc_type),
                "auto_generate": str(field.auto_generate),
                "ics_prefix": field.ics_prefix}
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
def stock_transaction_list(request):
    try:
        return render(request, 'stock_transaction_list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def load_stock_transaction_list(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    current_month = company.current_period_month_ic
    current_year = company.current_period_year_ic
    list_filter = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                  document_date__month__gte=current_month, document_date__year__gte=current_year).exclude(is_closed=True)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        if search.lower() in 'in':
            ioFlag = 1
        elif search.lower() in 'transfer':
            ioFlag = 2
        elif search.lower() in 'out':
            ioFlag = 3
        else:
            ioFlag = search

        if search.lower() in 'purchase':
            priceFlag = 1
        elif search.lower() in 'stocklist':
            priceFlag = 2
        elif search.lower() in 'retail':
            priceFlag = 3
        else:
            priceFlag = search
        upper_search = search.upper()
        list_filter = list_filter.filter(
            Q(document_number__contains=upper_search) |
            Q(transaction_code__code__contains=upper_search) |
            Q(document_date__contains=search) |
            Q(in_location__name__contains=upper_search) |
            Q(update_date__contains=search) |
            Q(out_location__name__contains=upper_search) |
            Q(io_flag__contains=ioFlag) |
            Q(price_flag__contains=priceFlag))

    # All data

    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "document_date"
    elif order_column == "2":
        column_name = "document_number"
    elif order_column == "3":
        column_name = "transaction_code"
    elif order_column == "4":
        column_name = "io_flag"
    elif order_column == "5":
        column_name = "price_flag"
    elif order_column == "6":
        column_name = "in_location"
    elif order_column == "7":
        column_name = "out_location"
    elif order_column == "8":
        column_name = "status"

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name, 'id')[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name, 'id')[int(start):(int(start) + int(length))]

    # Create data list
    price_flag_dict = dict(INV_PRICE_FLAG)
    io_flag_dict = dict([status[::-1] for status in INV_IN_OUT_FLAG])
    array = []
    for field in list:
        data = {}
        data["id"] = field.id
        data["order_id"] = field.order_id if field.order_id else ''
        data["update_date"] = field.update_date.strftime("%d-%m-%Y")
        data["document_date"] = field.document_date.strftime("%d-%m-%Y")
        data["transaction_code"] = field.transaction_code.code
        data["document_number"] = field.document_number
        data["io_flag"] = io_flag_dict.get(field.io_flag)
        data["price_flag"] = price_flag_dict.get(field.price_flag)
        data["in_location"] = field.in_location.code if field.in_location else None
        data["out_location"] = field.out_location.code if field.out_location else None
        data["status"] = field.status if field.status else ''
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
@check_inventory_closing
@permission_required('inventory.add_stocktransaction', login_url='/alert/')
def stock_transaction_add(request, is_send):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    ItemFormSet = formset_factory(StockTransItemForm)
    if request.method == 'POST':
        form = StockTransForm(company_id, request.POST, session_date=request.session['session_date'])
        formset_item = ItemFormSet(request.POST, prefix='formset_item')

        if 'is_inventory_locked' in request.session and request.session['is_inventory_locked']:
            form = StockTransForm(company_id, session_date=request.session['session_date'])
            formset_item = ItemFormSet(prefix='formset_item')
            return render_to_response('stock_transaction.html',
                                      RequestContext(request,
                                                     {'form': form, 'formset_item': formset_item,
                                                      'request_method': request.method}))
        if form.is_valid() and formset_item.is_valid():
            try:
                with transaction.atomic():
                    stock_trans = form.save(commit=False)
                    stock_trans.company_id = company_id
                    stock_trans.currency_id = form.cleaned_data['currency_id']
                    stock_trans.status = int(is_send)
                    stock_trans.create_date = datetime.datetime.today()
                    stock_trans.update_date = datetime.datetime.today()
                    stock_trans.update_by = request.user.id
                    stock_trans.is_hidden = 0
                    stock_trans.save()

                    if int(is_send) == 1:
                        if form.cleaned_data['document_number']:
                            stock_trans.document_number = form.cleaned_data['document_number']
                        else:
                            stock_trans.document_number = generate_document_number(
                                company_id,
                                request.POST.get('document_date'),
                                int(TRN_CODE_TYPE_DICT['Inventory Code']),
                                form.cleaned_data['transaction_code'].id)
                        stock_trans.save()

                    for form in formset_item:
                        stock_trans_item = StockTransactionDetail()
                        stock_trans_item.line_number = form.cleaned_data.get('line_number')
                        stock_trans_item.item_id = form.cleaned_data.get('item_id')
                        stock_trans_item.quantity = form.cleaned_data.get('quantity')
                        stock_trans_item.price = form.cleaned_data.get('price')
                        stock_trans_item.amount = form.cleaned_data.get('amount')
                        stock_trans_item.remark = form.cleaned_data.get('remark')
                        stock_trans_item.parent_id = stock_trans.id
                        stock_trans_item.in_location_id = stock_trans.in_location_id
                        stock_trans_item.out_location_id = stock_trans.out_location_id
                        stock_trans_item.create_date = datetime.datetime.today()
                        stock_trans_item.update_date = datetime.datetime.today()
                        stock_trans_item.update_by = request.user.id
                        stock_trans_item.is_hidden = False
                        stock_trans_item.save()
                        if int(is_send) == 1:
                            if stock_trans.io_flag == dict(INV_IN_OUT_FLAG)['IN']:
                                # Only i/o flag In, Transfer have outstanding_quantity
                                stock_trans_item.outstanding_quantity = form.cleaned_data.get('quantity')
                                # update_in_location(request, stock_trans.in_location_id,
                                #                    form.cleaned_data.get('item_id'), form.cleaned_data.get('quantity'))

                            elif stock_trans.io_flag == dict(INV_IN_OUT_FLAG)['OUT']:
                                # Subtract the item quantity based on FIFO flow
                                out_quantity = float(form.cleaned_data.get('quantity'))
                                related_stock_transactions = StockTransactionDetail.objects.filter(is_hidden=0) \
                                    .filter(Q(parent__io_flag=dict(INV_IN_OUT_FLAG)['IN']) | Q(
                                        parent__io_flag=dict(INV_IN_OUT_FLAG)['Transfer']))
                                related_stock_transactions = related_stock_transactions.filter(
                                    item_id=form.cleaned_data.get('item_id'),
                                    parent__in_location_id=stock_trans.out_location_id,
                                    parent__company_id=company_id,
                                    parent__is_hidden=False,
                                    is_hidden=False).order_by('parent__document_date')
                                for related_detail in related_stock_transactions:
                                    if out_quantity <= 0:
                                        continue

                                    if related_detail.outstanding_quantity < out_quantity:
                                        out_quantity = out_quantity - float(related_detail.outstanding_quantity)
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity == out_quantity:
                                        out_quantity = 0
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity > out_quantity:
                                        related_detail.outstanding_quantity = float(related_detail.outstanding_quantity) - out_quantity
                                        out_quantity = 0

                                    related_detail.save()

                                quantity = form.cleaned_data.get('quantity')
                                reversed_qty = quantity * -1
                                # update_out_location(request, stock_trans.out_location_id,
                                #                     form.cleaned_data.get('item_id'), quantity, reversed_qty)

                            elif stock_trans.io_flag == dict(INV_IN_OUT_FLAG)['Transfer']:
                                # Only i/o flag In, Transfer have outstanding_quantity
                                stock_trans_item.outstanding_quantity = form.cleaned_data.get('quantity')

                                # Subtract the item quantity based on FIFO flow
                                out_quantity = float(form.cleaned_data.get('quantity'))
                                related_stock_transactions = StockTransactionDetail.objects.filter(is_hidden=0) \
                                    .filter(Q(parent__io_flag=dict(INV_IN_OUT_FLAG)['IN']) | Q(
                                        parent__io_flag=dict(INV_IN_OUT_FLAG)['Transfer']))
                                related_stock_transactions = related_stock_transactions.filter(
                                    item_id=form.cleaned_data.get('item_id'),
                                    parent__in_location_id=stock_trans.out_location_id,
                                    parent__company_id=company_id, parent__is_hidden=False, is_hidden=False).order_by(
                                    'parent__document_date')
                                for related_detail in related_stock_transactions:
                                    if out_quantity <= 0:
                                        continue

                                    if related_detail.outstanding_quantity < out_quantity:
                                        out_quantity = out_quantity - float(related_detail.outstanding_quantity)
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity == out_quantity:
                                        out_quantity = 0
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity > out_quantity:
                                        related_detail.outstanding_quantity = float(related_detail.outstanding_quantity) - out_quantity
                                        out_quantity = 0

                                    related_detail.save()

                                quantity = form.cleaned_data.get('quantity')
                                reversed_qty = quantity * -1
                                # update_in_location(request, stock_trans.in_location_id,
                                #                    form.cleaned_data.get('item_id'), quantity)
                                # update_out_location(request, stock_trans.out_location_id,
                                # form.cleaned_data.get('item_id'), quantity, reversed_qty)

                            stock_trans_item.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='stock_transaction_add')

            messages.success(request, "Document number " + stock_trans.document_number + " was successfully created")
            return HttpResponsePermanentRedirect(reverse('stock_transaction_add', args=[0]))
        else:
            form = StockTransForm(company_id, request.POST, session_date=request.session['session_date'])
    else:
        form = StockTransForm(company_id, session_date=request.session['session_date'])
        formset_item = ItemFormSet(prefix='formset_item')
    return render_to_response('stock_transaction.html',
                              RequestContext(request, {'form': form, 'formset_item': formset_item,
                                                       'request_method': request.method,
                                                       'menu_type': TRN_CODE_TYPE_DICT['Inventory Code'],
                                                       "is_send": is_send}))


def add_outgoing_transaction(out_item, request, company_id):
    outgoing = Outgoing.objects.create(document_number=out_item.parent.document_number, line_number=out_item.line_number,
                                       sales_date=out_item.parent.document_date, out_qty=out_item.quantity, create_date=datetime.datetime.now().strftime('%Y-%m-%d'),
                                       update_by=request.user.id, update_date=datetime.datetime.now().strftime('%Y-%m-%d'), company_id=company_id,
                                       item_id=out_item.item_id, location_id=out_item.out_location_id, transaction_code_id=out_item.parent.transaction_code_id,
                                       document_line=out_item.line_number, ref_line=out_item.line_number, order_id=out_item.parent.order_id)
    return outgoing


def add_incoming_transaction(item, request, company_id):
    if item.parent.order and item.parent.order.exchange_rate:
        unit_price = float(item.price) * float(item.parent.order.exchange_rate)
    else:
        unit_price = float(item.price)
    Incoming.objects.create(document_number=item.parent.document_number, line_number=item.line_number, purchase_date=item.parent.document_date,
                            unit_price=unit_price, balance_qty=item.quantity, create_date=datetime.datetime.now().strftime('%Y-%m-%d'),
                            update_by=request.user.id, update_date=datetime.datetime.now().strftime('%Y-%m-%d'), company_id=company_id, item_id=item.item_id,
                            location_id=item.in_location_id, transaction_code_id=item.parent.transaction_code_id, order_id=item.parent.order_id)


def create_incoming(request, company_id, trx_code, daily_date):
    in_trans = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                               is_closed=0, document_date=daily_date,
                                               io_flag__in=(
                                                   dict(INV_IN_OUT_FLAG)['IN'], dict(INV_IN_OUT_FLAG)['Transfer']))
    if int(trx_code) > 0:
        in_trans = in_trans.filter(transaction_code_id=trx_code)
    in_trans_details = StockTransactionDetail.objects.filter(is_hidden=0, parent_id__in=in_trans).order_by('id')
    incoming_list = Incoming.objects.filter(is_hidden=0, company_id=company_id, is_history=0)

    for item in in_trans_details:
        in_list = incoming_list.filter(document_number=item.parent.document_number,
                                       location_id=item.in_location_id,
                                       line_number=item.line_number,
                                       out_qty=item.quantity,
                                       item_id=item.item_id).first()
        # We don't add repeated item
        if in_list:
            continue
        add_incoming_transaction(item, request, company_id)


def create_outgoing(request, company_id, trx_code, daily_date):
    out_trans = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                is_closed=0, document_date=daily_date,
                                                io_flag__in=(dict(INV_IN_OUT_FLAG)['OUT'], dict(INV_IN_OUT_FLAG)['Transfer']))
    if int(trx_code) > 0:
        out_trans = out_trans.filter(transaction_code_id=trx_code)
    out_trans_details = StockTransactionDetail.objects.filter(is_hidden=0, parent_id__in=out_trans).order_by('id')
    outgoing_list = Outgoing.objects.filter(is_hidden=0, company_id=company_id)

    for out_item in out_trans_details:
        out_list = outgoing_list.filter(item_id=out_item.item_id,
                                        location_id=out_item.out_location_id,
                                        document_number=out_item.parent.document_number,
                                        document_line=out_item.line_number,
                                        out_qty=out_item.quantity).first()
        # We don't add repeated item
        if out_list:
            continue

        outgoing = add_outgoing_transaction(out_item, request, company_id)

        # We try to get matching in-transaction now
        in_list = Incoming.objects.filter(is_hidden=0, company_id=company_id, location_id=outgoing.location_id,
                                          item_id=outgoing.item_id, balance_qty__gt=0, is_history=0).order_by('id')
        while len(in_list):
            incoming = in_list.first()

            out_qty = outgoing.out_qty
            if outgoing.in_qty > 0:  # That means, it has been done partially
                out_qty = outgoing.out_qty - outgoing.in_qty

            balance_qty = incoming.balance_qty

            if balance_qty >= out_qty:
                incoming.balance_qty = balance_qty - out_qty
                incoming.out_qty += out_qty
                outgoing.in_qty = out_qty
            else:  # Balance is lower than out_qty
                incoming.balance_qty = 0
                incoming.out_qty += out_qty
                outgoing.in_qty = balance_qty

            outgoing.unit_price = incoming.unit_price
            outgoing.ref_no = incoming.document_number
            outgoing.ref_code_id = incoming.transaction_code_id
            outgoing.ref_line = incoming.line_number
            outgoing.purchase_date = incoming.purchase_date

            # Save both incoming and outgoing
            incoming.save()
            outgoing.save()

            if balance_qty >= out_qty:
                # If there are more incoming balance, then we need to go through the next outgoing
                break

            # If incoming is not sufficient, we need to add the same outgoing
            outgoing = add_outgoing_transaction(out_item, request, company_id)

            out_list = Outgoing.objects.filter(is_hidden=0, company_id=company_id,
                                               item_id=outgoing.item_id,
                                               location_id=outgoing.location_id,
                                               document_number=outgoing.document_number,
                                               document_line=outgoing.line_number,
                                               out_qty=outgoing.out_qty).order_by('id')

            total_in_qty = 0
            for out in out_list:
                total_in_qty = total_in_qty + float(out.in_qty)
            outgoing.in_qty = Decimal(total_in_qty)
            outgoing.save()

            in_list = Incoming.objects.filter(is_hidden=0, company_id=company_id, location_id=outgoing.location_id,
                                              item_id=outgoing.item_id, balance_qty__gt=0, is_history=0).order_by('id')


def calculate_cost_FIFO(company_id, request, trx_code, daily_date):
    # First we want to add in-transaction into incoming
    create_incoming(request, company_id, trx_code, daily_date)

    # Now we get all the out-transaction details
    create_outgoing(request, company_id, trx_code, daily_date)
    return 1

def calculate_cost_FIFO_reverse(company_id, request, trx_code, daily_date):
    try:
        # Delete related outgoing
        out_trans = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                document_date=daily_date,
                                                io_flag__in=(dict(INV_IN_OUT_FLAG)['OUT'], dict(INV_IN_OUT_FLAG)['Transfer']))
        if int(trx_code) > 0:
            out_trans = out_trans.filter(transaction_code_id=trx_code)
        detail_items = StockTransactionDetail.objects.filter(is_hidden=0, parent_id__in=out_trans).values_list('item_id', flat=True)
        outgoing_list = Outgoing.objects.filter(is_hidden=0, company_id=company_id)

        for out_item in out_trans:
            out_lists = outgoing_list.filter(item_id__in=detail_items, location_id=out_item.out_location_id,
                                            document_number=out_item.document_number)
            # We don't add repeated item
            for out_list in out_lists:
                if out_list.ref_no:
                    incoming_list = Incoming.objects.filter(is_hidden=0, company_id=company_id, is_history=0,
                                                            document_number=out_list.ref_no, item_id=out_list.item_id,
                                                            line_number=out_list.ref_line, purchase_date__lte=out_list.sales_date,
                                                            location_id=out_list.location_id, balance_qty__gt=0)
                    for item in incoming_list:
                        item.balance_qty += out_list.out_qty
                        item.save()
                out_list.is_hidden = True
                out_list.save()
    except Exception as e:
        print(e)
        
    try:
        # Delete related incoming
        in_trans = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                               document_date=daily_date,
                                               io_flag__in=(
                                                   dict(INV_IN_OUT_FLAG)['IN'], dict(INV_IN_OUT_FLAG)['Transfer']))
        if int(trx_code) > 0:
            in_trans = in_trans.filter(transaction_code_id=trx_code)
        detail_items = StockTransactionDetail.objects.filter(is_hidden=0, parent_id__in=in_trans).values_list('item_id', flat=True)
        incoming_list = Incoming.objects.filter(is_hidden=0, company_id=company_id, is_history=0)

        for item in in_trans:
            in_lists = incoming_list.filter(document_number=item.document_number, item_id__in=detail_items,
                                            location_id=item.in_location_id)
            # We don't add repeated item
            for in_list in in_lists:
                in_list.is_hidden = True
                in_list.save()
    except Exception as e:
        print(e)

    return 1


# @login_required
def update_balance_qty(request, company_id, trx_code, daily_date, reverse=False):
    # update items_item, locations_locationitem balances quantity for each transactions
    # URGENT is_closed
    closing_year = daily_date.year
    closing_month = daily_date.month
    closing_day = daily_date.day
    trans_list = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                 document_date=daily_date)
    if int(trx_code) > 0:
        trans_list = trans_list.filter(transaction_code_id=trx_code)
    # Put logic here!!!
    if trans_list:
        i = 1
        for trx_header in trans_list:
            adjustment = False
            if trx_header.order_id == None or trx_header.order_id == '':
                adjustment = True
            i += 1
            id_parent = trx_header.id
            trans_details_list = StockTransactionDetail.objects.filter(is_hidden=0, parent_id=id_parent).order_by('id')
            for trx_det in trans_details_list:
                costMethod = 2  # cost method ONLY THIS
                val_cost_price = cost_amount = stock_class = location_id = 0
                if int(trx_det.parent.io_flag) != 1 or (
                        int(trx_det.parent.io_flag) == 1 and int(trx_det.parent.price_flag) != 1):
                    val_cost_price = trx_det.item.cost_price
                    cost_amount = round_number(trx_det.quantity * val_cost_price, 2)

                elif int(trx_det.parent.io_flag) == 1 and int(trx_det.parent.price_flag) == 1:
                    val_cost_price = trx_det.price
                    cost_amount = trx_det.amount

                # CHECK IF CREDIT NOTE
                if trx_header.transaction_code.code == 'SCN' or trx_header.transaction_code.code == 'PCN':
                    val_cost_price = trx_det.cost_price
                    cost_amount = trx_det.amount

                # UPDATE ITEM
                itm = Item.objects.get(pk=trx_det.item_id)

                balance_amount = itm.balance_amount if itm.balance_amount else 0
                if int(trx_header.io_flag) == 1:
                    stock_class = trx_det.in_location.stock_class
                    location_id = trx_det.in_location_id
                elif int(trx_header.io_flag) == 3:
                    stock_class = trx_det.out_location.stock_class
                    location_id = trx_det.out_location_id
                if int(trx_header.io_flag) <= 2 and int(stock_class) == 1:  # sales/trasfer and Internal
                    if reverse:
                        itm.balance_qty = itm.balance_qty - trx_det.quantity
                        itm.balance_amount = balance_amount - cost_amount
                        itm.in_qty = itm.in_qty + trx_det.quantity
                    else:
                        itm.balance_qty = itm.balance_qty + trx_det.quantity
                        itm.balance_amount = balance_amount + cost_amount
                        itm.in_qty = itm.in_qty - trx_det.quantity
                    itm.move_date = trx_header.document_date
                    if float(itm.balance_qty) != 0 and int(costMethod) != 0:
                        itm.cost_price = balance_amount / itm.balance_qty  # count of COST-PRICE
                    if int(trx_header.price_flag) == 1:
                        itm.last_purchase_price = trx_det.price
                        itm.last_purchase_doc = trx_header.document_number
                        itm.last_purchase_date = trx_header.document_date

                elif int(trx_header.io_flag) >= 2 and int(stock_class) == 2:  # purchase/transfer and external
                    if reverse:
                        itm.balance_qty = itm.balance_qty + trx_det.quantity
                        itm.balance_amount = balance_amount + cost_amount
                        itm.out_qty = itm.out_qty + trx_det.quantity
                    else:
                        itm.balance_qty = itm.balance_qty - trx_det.quantity
                        itm.balance_amount = balance_amount - cost_amount
                        itm.out_qty = itm.out_qty - trx_det.quantity
                    itm.move_date = trx_header.document_date
                    if itm.balance_qty != 0 and int(costMethod) != 0:
                        itm.cost_price = balance_amount / itm.balance_qty
                itm.save()

                # UPDATE LOC ITEM
                itm_loc_code = LocationItem.objects.filter(is_hidden=0, item_id=trx_det.item_id,
                                                           location_id=location_id).last()
                
                if itm_loc_code:
                    if itm_loc_code.onhand_qty is None:
                        itm_loc_code.onhand_qty = 0
                    if itm_loc_code.onhand_amount is None:
                        itm_loc_code.onhand_amount = 0
                    if itm_loc_code.in_qty is None:
                        itm_loc_code.in_qty = 0
                    if itm_loc_code.out_qty is None:
                        itm_loc_code.out_qty = 0
                    if itm_loc_code.month_closing_qty is None:
                        itm_loc_code.month_closing_qty = 0
                    if itm_loc_code.month_open_qty is None:
                        itm_loc_code.month_open_qty = 0
                    if int(trx_header.io_flag) <= 2:
                        if reverse:
                            if adjustment:
                                itm_loc_code.onhand_qty = itm_loc_code.onhand_qty - trx_det.quantity
                                itm_loc_code.in_qty = itm_loc_code.in_qty + trx_det.quantity
                            itm_loc_code.onhand_amount = itm_loc_code.onhand_amount - cost_amount
                            itm_loc_code.month_closing_qty = itm_loc_code.month_closing_qty - trx_det.quantity
                        else:
                            if adjustment:
                                itm_loc_code.onhand_qty = itm_loc_code.onhand_qty + trx_det.quantity
                                itm_loc_code.in_qty = itm_loc_code.in_qty - trx_det.quantity
                            itm_loc_code.onhand_amount = itm_loc_code.onhand_amount + cost_amount
                            itm_loc_code.month_closing_qty = itm_loc_code.month_closing_qty + trx_det.quantity
                            if closing_day == calendar.monthrange(closing_year, closing_month)[1]:  # checking last day of month
                                itm_loc_code.month_open_qty = itm_loc_code.month_closing_qty
                                if closing_month == 12:  # closing year
                                    itm_loc_code.year_open_qty = itm_loc_code.month_closing_qty
                        if float(itm_loc_code.onhand_qty) != 0 and int(costMethod) != 0:
                            itm_loc_code.mv_cost_price = itm_loc_code.onhand_amount / itm_loc_code.onhand_qty
                        itm_loc_code.save()

                    if int(trx_header.io_flag) >= 2:
                        if reverse:
                            if adjustment:
                                itm_loc_code.onhand_qty = itm_loc_code.onhand_qty + trx_det.quantity
                                itm_loc_code.out_qty = itm_loc_code.out_qty + trx_det.quantity
                            itm_loc_code.onhand_amount = itm_loc_code.onhand_amount + cost_amount
                            itm_loc_code.month_closing_qty = itm_loc_code.month_closing_qty + trx_det.quantity
                        else:
                            if adjustment:
                                itm_loc_code.onhand_qty = itm_loc_code.onhand_qty - trx_det.quantity
                                itm_loc_code.out_qty = itm_loc_code.out_qty - trx_det.quantity
                            itm_loc_code.onhand_amount = itm_loc_code.onhand_amount - cost_amount
                            itm_loc_code.month_closing_qty = itm_loc_code.month_closing_qty - trx_det.quantity
                            if closing_day == calendar.monthrange(closing_year, closing_month)[1]:  # checking last day of month
                                itm_loc_code.month_open_qty = itm_loc_code.month_closing_qty
                                if closing_month == 12:  # closing year
                                    itm_loc_code.year_open_qty = itm_loc_code.month_closing_qty
                        if float(itm_loc_code.onhand_qty) != 0 and int(costMethod) != 0:
                            itm_loc_code.mv_cost_price = itm_loc_code.onhand_amount / itm_loc_code.onhand_qty
                        itm_loc_code.save()

                # UPDATE / CREATE HISTORY
                history_list = History.objects.filter(company_id=company_id, year=daily_date.year, month=daily_date.month,
                                                      io_flag=trx_header.io_flag, location_id=location_id,
                                                      item_code_id=trx_det.item_id, is_hidden=False,
                                                      transaction_code_id=trx_header.transaction_code_id).last()
                if reverse:
                    if history_list and int(trx_code) > 0:
                        history_list = history_list.filter(transaction_code_id=trx_code)
                        if history_list:
                            history_list.is_hidden = True
                            history_list.save()
                else:
                    if history_list and int(trx_code) > 0:
                        history_list = history_list.filter(transaction_code_id=trx_code)
                        if history_list:
                            history_list.quantity = history_list.quantity + trx_det.quantity
                            history_list.amount = history_list.amount + trx_det.amount
                            history_list.cost = cost_amount
                            history_list.save()
                    else:
                        if int(trx_header.io_flag) <= 2:
                            history_list = History()
                            history_list.year = int(daily_date.year)
                            history_list.month = int(daily_date.month)
                            history_list.location_id = location_id
                            history_list.item_code_id = trx_det.item_id

                            history_list.io_flag = 1

                            history_list.transaction_code_id = trx_header.transaction_code_id
                            history_list.quantity = trx_det.quantity
                            history_list.amount = trx_det.amount
                            history_list.cost = cost_amount
                            history_list.create_date = trx_header.document_date
                            history_list.update_date = trx_header.document_date
                            history_list.update_by = request.user.id
                            history_list.is_hidden = 0
                            history_list.company_id = company_id

                            history_list.save()

                        if int(trx_header.io_flag) >= 2:
                            history_list = History()
                            history_list.month = int(daily_date.month)
                            history_list.year = int(daily_date.year)
                            history_list.location_id = location_id
                            history_list.item_code_id = trx_det.item_id

                            history_list.io_flag = 3

                            history_list.transaction_code_id = trx_header.transaction_code_id
                            history_list.quantity = trx_det.quantity
                            history_list.amount = trx_det.amount
                            history_list.cost = cost_amount
                            history_list.create_date = trx_header.document_date
                            history_list.update_date = trx_header.document_date
                            history_list.update_by = request.user.id
                            history_list.is_hidden = 0
                            history_list.company_id = company_id
                            history_list.save()

                trx_det.amount = cost_amount
                trx_det.cost_price = val_cost_price
                trx_det.save()

                if int(costMethod) == 2:
                    if reverse:
                        trx_header.is_closed = 0
                    else:
                        trx_header.is_closed = 1
                    trx_header.update_date = daily_date
                    trx_header.save()

    elif closing_day == calendar.monthrange(closing_year, closing_month)[1]:  # checking last day of month
        loc_items = LocationItem.objects.filter(is_hidden=0).exclude(item_id__isnull=True, location_id__isnull=True)
        for loc_item in loc_items:
            loc_item.month_open_qty = loc_item.month_closing_qty
            if closing_month == 12:  # closing year
                loc_item.year_open_qty = loc_item.month_closing_qty
            loc_item.save()

    return 1
    # update location item


@login_required
def inv_daily_closing(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    closing_date = datetime.datetime.now().date()
    inv_trn_code = TransactionCode.objects.filter(company_id=company_id, is_hidden=False,
                                                  menu_type=int(TRN_CODE_TYPE_DICT['Inventory Code']))
    if company.closing_date:
        closing_date = company.closing_date + timedelta(days=1)
        closing_date = closing_date.strftime('%d-%m-%Y')
    else:
        closing_date = datetime.datetime.now().strftime('%d-%m-%Y')
    response = 1
    res = 1
    if request.method == 'POST':
        trx_code = request.POST['trn_code_opt']
        days = request.POST['day_to_close'].split('-')
        new_closing_date = datetime.datetime.now().date()
        new_closing_date = new_closing_date.replace(year=int(days[2]), month=int(days[1]), day=int(days[0]))
        # reverse to first of month
        if new_closing_date > company.closing_date:
            start_closing_date = new_closing_date.replace(year=int(days[2]), month=int(days[1]), day=int(1)) #first day of the month
            stock_trans = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                        document_date__range=(start_closing_date, company.closing_date),
                                        io_flag__in=(dict(INV_IN_OUT_FLAG)['IN'], dict(INV_IN_OUT_FLAG)['OUT'], 
                                                    dict(INV_IN_OUT_FLAG)['Transfer'])).order_by('-document_date')

            is_open = stock_trans.filter(is_closed=0)
            if is_open:
                stck_dates = stock_trans.values_list('document_date', flat=True).distinct()
                for stck_date in stck_dates:
                    res = update_balance_qty(request, company_id, trx_code, stck_date, True)
                    response = calculate_cost_FIFO_reverse(company_id, request, trx_code, stck_date)
            else:
                start_closing_date = company.closing_date + timedelta(days=1)

            stock_trans = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                        document_date__range=(start_closing_date, new_closing_date),
                                        io_flag__in=(dict(INV_IN_OUT_FLAG)['IN'], dict(INV_IN_OUT_FLAG)['OUT'], 
                                                    dict(INV_IN_OUT_FLAG)['Transfer'])).order_by('document_date')
            stck_dates = stock_trans.values_list('document_date', flat=True).distinct()

            for stck_date in stck_dates:
                response = calculate_cost_FIFO(company_id, request, trx_code, stck_date)
                res = update_balance_qty(request, company_id, trx_code, stck_date)

            company.closing_date = new_closing_date
            company.save()

            if res and response:
                messages.info(request, 'Closing Completed ...')
            else:
                messages.error(request, 'Errors while Closing ...')
        else:
            messages.error(request, 'Given date is back date than closing date ...')

        closing_date = company.closing_date + timedelta(days=1)
        closing_date = closing_date.strftime('%d-%m-%Y')

    return render_to_response('daily_closing.html', RequestContext(request, {"trn_code": inv_trn_code,
                                                                             'closing_date': closing_date}))


@login_required
def inv_monthly_closing(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    inv_trn_code = TransactionCode.objects.filter(company_id=company_id, is_hidden=False,
                                                  menu_type=int(TRN_CODE_TYPE_DICT['Inventory Code']))

    # Call daily closing to be sure
    inv_daily_closing(request)
    yy = request.POST['years_period']
    mm = request.POST['month_period']
    # Make sure we set the is_closed flag in StockTransaction
    trans_list = StockTransaction.objects.filter(is_hidden=0, company_id=company_id,
                                                 is_closed=0, document_date__year=yy, document_date__month=mm)
    for trans in trans_list:
        trans.is_closed = 1
        trans.closing_date = datetime.datetime.now().strftime('%Y-%m-%d')
        trans.save()

    incoming_list = Incoming.objects.filter(is_hidden=0, company_id=company_id, balance_qty=0, is_history=0)
    for incoming in incoming_list:
        incoming.is_history = 1
        incoming.save()

    outgoing_list = Outgoing.objects.filter(is_hidden=0, company_id=company_id, ref_no__isnull=False, is_history=0)
    for outgoing in outgoing_list:
        outgoing.is_history = 1
        outgoing.save()

    return render_to_response('daily_closing.html', RequestContext(request, {"trn_code": inv_trn_code}))


def add_or_adjust_history_transaction(item, location_id, request, company_id, closing_year, closing_month):
    history = History.objects.filter(is_hidden=0, company_id=company_id,
                                     year=closing_year, month=closing_month,
                                     location_id=location_id, item_code_id=item.item_id,
                                     io_flag=item.parent.io_flag).first()
    if history:
        history.quantity += item.quantity
        history.amount += item.amount
        history.cost += item.cost
        history.save()
    else:
        history = add_history_transaction(item, request, company_id, closing_year, closing_month,
                                          location_id)
    return history


def add_history_transaction(item, request, company_id, closing_year, closing_month, location_id):
    history = History()
    history.year = closing_year
    history.month = closing_month
    history.io_flag = item.parent.io_flag

    history.quantity = item.quantity
    history.amount = item.amount
    history.cost = item.cost

    history.item_code_id = item.item_id
    history.transaction_code_id = item.parent.transaction_code_id
    history.location_id = location_id
    history.create_date = datetime.datetime.now().strftime('%Y-%m-%d')
    history.update_by = request.user.id
    history.update_date = datetime.datetime.now().strftime('%Y-%m-%d')
    history.company_id = company_id
    history.save()

    return history


@login_required
@check_inventory_closing
@permission_required('inventory.change_stocktransaction', login_url='/alert/')
def stock_transaction_edit(request, stock_trans_id, is_send):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    stock_trans = get_object_or_404(StockTransaction, pk=stock_trans_id)
    trans_items = StockTransactionDetail.objects.filter(is_hidden=0, parent_id=stock_trans_id).values() \
        .annotate(item_code=F('item__code')) \
        .annotate(item_id=F('item_id')) \
        .annotate(item_name=F('item__name')) \
        .annotate(item_inv_measure=F('item__inv_measure__code')) \
        .annotate(item_onhand=Value(0, output_field=DecimalField())) \
        .annotate(stock_qty=Value(0, output_field=DecimalField()))

    for trans_item in trans_items:
        onhand_qty = get_item_onhandqty(trans_item['item_id'])
        trans_item['item_onhand'] = onhand_qty  # if onhand_qty >= 0 else  0

    ItemFormSet = formset_factory(StockTransItemForm)
    if request.method == 'POST':
        form = StockTransForm(company_id, data=request.POST, instance=stock_trans)
        formset_item = ItemFormSet(request.POST, prefix='formset_item')
        if 'is_inventory_locked' in request.session and request.session['is_inventory_locked']:
            form = StockTransForm(company_id, instance=stock_trans)
            formset_item = ItemFormSet(prefix='formset_item', initial=trans_items)
            return render_to_response('stock_transaction.html',
                                      RequestContext(request, {'form': form, 'stock_trans_id': stock_trans_id,
                                                               'formset_item': formset_item,
                                                               'request_method': request.method,
                                                               'status': stock_trans.status}))

        if form.is_valid() and formset_item.is_valid():
            try:
                with transaction.atomic():
                    stock_trans = form.save(commit=False)
                    stock_trans.company_id = company_id
                    stock_trans.currency_id = form.cleaned_data['currency_id']
                    stock_trans.in_location = form.cleaned_data['in_location'] if form.cleaned_data[
                        'in_location'] else None
                    stock_trans.out_location = form.cleaned_data['out_location'] if form.cleaned_data[
                        'out_location'] else None
                    # stock_trans.status = dict(ORDER_STATUS)['Posted'] if int(is_send) == 1 else dict(ORDER_STATUS)[
                    #     'Draft']
                    stock_trans.status = int(is_send)
                    stock_trans.id = stock_trans_id
                    stock_trans.update_date = datetime.datetime.today()
                    stock_trans.update_by = request.user.id
                    stock_trans.is_hidden = 0
                    stock_trans.save()

                    if int(is_send) == 1:
                        if form.cleaned_data['document_number']:
                            stock_trans.document_number = form.cleaned_data['document_number']
                        else:
                            stock_trans.document_number = generate_document_number(
                                company_id,
                                request.POST.get('document_date'),
                                int(TRN_CODE_TYPE_DICT['Inventory Code']),
                                form.cleaned_data['transaction_code'].id)
                        stock_trans.save()
                    stock_trans_item_list = StockTransactionDetail.objects.filter(parent_id=stock_trans_id)
                    for stock_trans_item in stock_trans_item_list:
                        stock_trans_item.delete()
                    for form in formset_item:
                        stock_trans_item = StockTransactionDetail()
                        stock_trans_item.line_number = form.cleaned_data.get('line_number')
                        stock_trans_item.item_id = form.cleaned_data.get('item_id')
                        stock_trans_item.quantity = form.cleaned_data.get('quantity')
                        stock_trans_item.price = form.cleaned_data.get('price')
                        stock_trans_item.amount = form.cleaned_data.get('amount')
                        stock_trans_item.remark = form.cleaned_data.get('remark')
                        stock_trans_item.parent_id = stock_trans.id
                        stock_trans_item.in_location_id = stock_trans.in_location_id
                        stock_trans_item.out_location_id = stock_trans.out_location_id
                        stock_trans_item.create_date = datetime.datetime.today()
                        stock_trans_item.update_date = datetime.datetime.today()
                        stock_trans_item.update_by_id = request.user.id
                        stock_trans_item.is_hidden = False
                        stock_trans_item.save()

                        if int(is_send) == 1:
                            if stock_trans.io_flag == dict(INV_IN_OUT_FLAG)['IN']:
                                # Only i/o flag In, Transfer have outstanding_quantity
                                stock_trans_item.outstanding_quantity = form.cleaned_data.get('quantity')
                                # update_in_location(request, stock_trans.in_location_id,
                                #                    form.cleaned_data.get('item_id'), form.cleaned_data.get('quantity'))

                            elif stock_trans.io_flag == dict(INV_IN_OUT_FLAG)['OUT']:
                                # Subtract the item quantity based on FIFO flow
                                out_quantity = float(form.cleaned_data.get('quantity'))
                                related_stock_transactions = StockTransactionDetail.objects.filter(
                                    Q(parent__io_flag=dict(INV_IN_OUT_FLAG)['IN']) | Q(
                                        parent__io_flag=dict(INV_IN_OUT_FLAG)['Transfer']))
                                related_stock_transactions = related_stock_transactions.filter(
                                    item_id=form.cleaned_data.get('item_id'),
                                    parent__in_location_id=stock_trans.out_location_id,
                                    parent__company_id=company_id, parent__is_hidden=False, is_hidden=False).order_by(
                                    'parent__document_date')
                                for related_detail in related_stock_transactions:
                                    if out_quantity <= 0:
                                        continue

                                    if related_detail.outstanding_quantity < out_quantity:
                                        out_quantity = out_quantity - float(related_detail.outstanding_quantity)
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity == out_quantity:
                                        out_quantity = 0
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity > out_quantity:
                                        related_detail.outstanding_quantity = float(related_detail.outstanding_quantity) - out_quantity
                                        out_quantity = 0

                                    related_detail.save()

                                quantity = form.cleaned_data.get('quantity')
                                reversed_qty = quantity * -1
                                # update_out_location(request, stock_trans.out_location_id,
                                #                     form.cleaned_data.get('item_id'), quantity, reversed_qty)

                            elif stock_trans.io_flag == dict(INV_IN_OUT_FLAG)['Transfer']:
                                # Only i/o flag In, Transfer have outstanding_quantity
                                stock_trans_item.outstanding_quantity = form.cleaned_data.get('quantity')

                                # Subtract the item quantity based on FIFO flow
                                out_quantity = float(form.cleaned_data.get('quantity'))
                                related_stock_transactions = StockTransactionDetail.objects.filter(
                                    Q(parent__io_flag=dict(INV_IN_OUT_FLAG)['IN']) | Q(
                                        parent__io_flag=dict(INV_IN_OUT_FLAG)['Transfer']))
                                related_stock_transactions = related_stock_transactions.filter(
                                    item_id=form.cleaned_data.get('item_id'),
                                    parent__in_location_id=stock_trans.out_location_id,
                                    parent__company_id=company_id, parent__is_hidden=False, is_hidden=False).order_by(
                                    'parent__document_date')
                                for related_detail in related_stock_transactions:
                                    if out_quantity <= 0:
                                        continue

                                    if related_detail.outstanding_quantity < out_quantity:
                                        out_quantity = out_quantity - float(related_detail.outstanding_quantity)
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity == out_quantity:
                                        out_quantity = 0
                                        related_detail.outstanding_quantity = 0
                                    elif related_detail.outstanding_quantity > out_quantity:
                                        related_detail.outstanding_quantity = float(related_detail.outstanding_quantity) - out_quantity
                                        out_quantity = 0

                                    related_detail.save()

                                quantity = form.cleaned_data.get('quantity')
                                reversed_qty = quantity * -1
                                # update_in_location(request, stock_trans.in_location_id,
                                #                    form.cleaned_data.get('item_id'), quantity)
                                # update_out_location(request, stock_trans.out_location_id,
                                #                     form.cleaned_data.get('item_id'), quantity, reversed_qty)

                            stock_trans_item.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='stock_transaction_edit')
            return HttpResponsePermanentRedirect(reverse('stock_transaction_list'))
    else:
        form = StockTransForm(company_id, instance=stock_trans)
        formset_item = ItemFormSet(prefix='formset_item', initial=trans_items)
        # print(formset_item)
    return render_to_response('stock_transaction.html',
                              RequestContext(request, {'form': form, 'stock_trans_id': stock_trans_id,
                                                       'formset_item': formset_item,
                                                       'request_method': request.method,
                                                       'status': stock_trans.status,
                                                       'menu_type': TRN_CODE_TYPE_DICT['Inventory Code'],
                                                       'io_flag': stock_trans.io_flag}))


@login_required
@permission_required('inventory.delete_stocktransaction', login_url='/alert/')
def stock_transaction_delete(request, stock_trans_id):
    try:
        stock_trans = get_object_or_404(StockTransaction, pk=stock_trans_id)
        stock_trans.is_hidden = True
        stock_trans.update_date = datetime.datetime.today()
        stock_trans.update_by_id = request.user.id
        stock_trans.save()
        stock_trans_item_list = StockTransactionDetail.objects.filter(parent_id=stock_trans_id)
        for stock_trans_item in stock_trans_item_list:
            stock_trans_item.is_hidden = True
            stock_trans_item.update_date = datetime.datetime.today()
            stock_trans_item.update_by_id = request.user.id
            stock_trans_item.save()

        return HttpResponsePermanentRedirect(reverse('stock_transaction_list'))
    except OSError as e:
        messages.add_message(request, messages.ERROR, 'Error happened while deleting.', extra_tags='category_delete')
        return HttpResponsePermanentRedirect(reverse('stock_transaction_list'))


@login_required
def search_transaction_code(request):
    if request.is_ajax():
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            transaction_code = request.POST.get('transaction_code')
            response_data = {}
            if transaction_code != '':
                trans_code = TransactionCode.objects.get(id=transaction_code)
                if trans_code:
                    price_flag_dict = dict(INV_PRICE_FLAG)
                    reversedDict = dict([status[::-1] for status in INV_IN_OUT_FLAG])
                    response_data['io_flag'] = reversedDict[str(trans_code.io_flag)]
                    response_data['io_flag_id'] = trans_code.io_flag
                    response_data['price_flag'] = price_flag_dict.get(trans_code.price_flag)
                    response_data['price_flag_id'] = trans_code.price_flag
                    response_data['auto_generate'] = trans_code.auto_generate
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='search_transaction_code')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
def is_trn_code_exist(request):
    response_data = []
    try:
        if request.is_ajax():
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            tcode = request.POST.get('transaction_code').upper()
            transaction_code = TransactionCode.objects.filter(is_hidden=0, company_id=company_id, code=tcode). \
                values('pk', 'menu_type', 'io_flag', 'price_flag')

            for trn_code in transaction_code:
                obj = {'id': str(trn_code['pk']),
                       'menu_type': trn_code['menu_type'],
                       'io_flag': trn_code['io_flag'],
                       'price_flag': trn_code['price_flag']}
                response_data.append(obj)
    except:
        pass
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def search_location_code(request):
    if request.is_ajax():
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            flag = request.POST.get('flag')
            in_location_code = request.POST.get('in_location_code')
            out_location_code = request.POST.get('out_location_code')
            response_data = {}
            if in_location_code != '' and flag == 'id_in_location':
                location = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                                   code__contains=in_location_code).first()
                if location != None:
                    response_data['flag'] = flag
                    response_data['id'] = location.id
                    response_data['code'] = in_location_code
                    response_data['msg'] = None
                else:
                    response_data['msg'] = 'In Location is not valid'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            elif out_location_code != '' and flag == 'id_out_location':
                location = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                                   code__contains=out_location_code).first()
                if location != None:
                    response_data['flag'] = flag
                    response_data['id'] = location.id
                    response_data['code'] = out_location_code
                    response_data['msg'] = None
                else:
                    response_data['msg'] = 'Out Location is not valid'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='search_location_code')
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}), content_type="application/json")


@login_required
def print_stock_reports(request, report_code):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    inv_trn_code = TransactionCode.objects.filter(company_id=company_id, is_hidden=False,
                                                  menu_type=int(TRN_CODE_TYPE_DICT['Inventory Code']))

    return render_to_response('stock-reports.html', RequestContext(request, {'st_report_list': ST_REPORT_LIST,
                                                                             "report_code": report_code,
                                                                             "trn_code": inv_trn_code,
                                                                             'company': company}))


def reset_in_out_loc_item(trans_list, stock_trans_item_list):
    for trans_d in stock_trans_item_list:
        itm = Item.objects.get(pk=trans_d.item_id)
        itm.in_qty = 0
        itm.out_qty = 0
        itm.save()
        if int(trans_d.parent.io_flag) <= int(dict(INV_IN_OUT_FLAG)['Transfer']):
            loc = trans_d.in_location_id if trans_d.in_location_id else trans_d.parent.in_location_id
            reset_loc_item(loc, trans_d.item_id)
        if int(trans_d.parent.io_flag) >= int(dict(INV_IN_OUT_FLAG)['Transfer']):
            loc = trans_d.out_location_id if trans_d.out_location_id else trans_d.parent.out_location_id
            reset_loc_item(loc, trans_d.item_id)


def reset_loc_item(loc, item_id):
    loc_itm = LocationItem.objects.filter(is_hidden=0, location_id=loc, item_id=item_id).last()
    if loc_itm:
        loc_itm.out_qty = 0
        loc_itm.in_qty = 0
        loc_itm.save()


def recalculate_in_out_item(stock_trans_item_list):
    for trans_d in stock_trans_item_list:
        itm = Item.objects.get(pk=trans_d.item_id)
        itm_in_qty = itm.in_qty if itm.in_qty > 0 else 0
        itm_out_qty = itm.out_qty if itm.out_qty > 0 else 0

        if int(trans_d.parent.io_flag) <= int(dict(INV_IN_OUT_FLAG)['Transfer']):
            loc = trans_d.in_location_id if trans_d.in_location_id else trans_d.parent.in_location_id
            loc_itm = LocationItem.objects.filter(is_hidden=0, location_id=loc, item_id=trans_d.item_id).last()

            if loc_itm:
                in_qty = 0 if loc_itm.in_qty == None else loc_itm.in_qty
                loc_itm.in_qty = in_qty + trans_d.quantity

                itm.in_qty = itm_in_qty + trans_d.quantity

        if int(trans_d.parent.io_flag) >= int(dict(INV_IN_OUT_FLAG)['Transfer']):
            loc = trans_d.out_location_id if trans_d.out_location_id else trans_d.parent.out_location_id
            loc_itm = LocationItem.objects.filter(is_hidden=0, location_id=loc, item_id=trans_d.item_id).last()

            if loc_itm:
                out_qty = 0 if loc_itm.out_qty == None else loc_itm.out_qty
                loc_itm.out_qty = out_qty + trans_d.quantity

                itm.out_qty = itm_out_qty + trans_d.quantity

        if loc_itm:
            loc_itm.save()
        itm.save()


@login_required
def repost_stock(request):
    response_data = {'res_code': '1'}
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    if request.method == 'POST':
        trans_list = StockTransaction.objects.filter(is_hidden=0, company_id=company_id, is_closed=0)
        trans_list_id = [trans.id for trans in trans_list]
        stock_trans_item_list = StockTransactionDetail.objects.filter(parent_id__in=trans_list_id)
        item_list_id = [stock_trans_item.item_id for stock_trans_item in stock_trans_item_list]

        if not trans_list:
            return render_to_response('repost_stock.html', RequestContext(request, {'response_data': response_data}))

        reset_in_out_loc_item(trans_list, stock_trans_item_list)
        recalculate_in_out_item(stock_trans_item_list)

        balance_item = Item.objects.filter(company_id=company_id, is_hidden=0, pk__in=item_list_id)
        for all_item in balance_item:
            all_item.balance_qty = 0
            all_item.save()

        loc_onhand_qty = LocationItem.objects.filter(is_hidden=0, item__company_id=company_id, item_id__in=item_list_id)
        for oh_itm in loc_onhand_qty:
            item_balance_qty = Item.objects.get(pk=oh_itm.item_id)

            balance_qty = 0 if item_balance_qty.balance_qty == None else item_balance_qty.balance_qty
            onhand_qty = 0 if oh_itm.onhand_qty == None else oh_itm.onhand_qty
            item_balance_qty.balance_qty = balance_qty + onhand_qty
            item_balance_qty.save()

        balance_amount_item = Item.objects.filter(company_id=company_id, is_hidden=0, pk__in=item_list_id)
        for b_amount in balance_amount_item:
            b_amount.balance_amount = b_amount.balance_qty * b_amount.cost_price
            b_amount.save()

        response_data['res_code'] = '0'
        response_data['msg'] = 'Re-post stock completed ... !!'
    return render_to_response('repost_stock.html', RequestContext(request, {'response_data': response_data}))


def update_in_location(request, location_id, item_id, qty):
    loc_item = Location_Item(request, location_id, item_id)
    if not loc_item.get_item_location():
        loc_item.new_location_item()
    loc_item.set_in_qty(qty)
    loc_item.set_onhand(qty)


def update_out_location(request, location_id, item_id, qty, reversed_qty):
    loc_item = Location_Item(request, location_id, item_id)
    if not loc_item.get_item_location():
        loc_item.new_location_item()
    loc_item.set_out_qty(qty)
    loc_item.set_onhand(reversed_qty)


def detailStock(request, stock_trans_id, loc_id):
    trans_items = StockTransactionDetail.objects.filter(parent_id=stock_trans_id, is_hidden=0)
    array = []
    for field in trans_items:
        data = {"id": field.id,
                "quantity": intcomma("%.2f" % field.quantity),
                "item_code": field.item.code,
                "unit_price": intcomma("%.6f" % field.price),
                "amount": intcomma("%.2f" % field.amount),
                "remark": field.remark}
        array.append(data)
    content = {
        "data": array
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')
