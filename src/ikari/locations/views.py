import ast
import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from companies.models import Company
from contacts.models import Contact
from items.models import Item
from locations.models import Location, LocationItem
from utilities.common import get_item_onhandqty
from utilities.constants import LOCATION_TABS


# Create your views here.
@login_required
def load_list(request):
    try:
        return render(request, 'location-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def load_stock_list(request, loc_id):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        loc = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id).order_by('name')
        if int(loc_id) == 0:
            loc_def = loc.filter().first()
            loc_id = loc_def.id
        return render_to_response('stock_loc.html',
                                  RequestContext(request, {'location': loc, 'location_id': loc_id}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('locations.add_location', login_url='/alert/')
def location_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    currency = company.currency
    if request.method == 'POST':
        if request.POST.get('name'):
            try:
                with transaction.atomic():
                    location = Location()
                    location.name = request.POST.get('name')
                    location.is_active = True
                    if request.POST.get('code'):
                        location.code = request.POST.get('code')
                    if request.POST.get('address'):
                        location.address = request.POST.get('address')
                    if request.POST.get('attention'):
                        location.attention = request.POST.get('attention')
                    if request.POST.get('phone'):
                        location.phone = request.POST.get('phone')
                    if request.POST.get('fax'):
                        location.fax = request.POST.get('fax')
                    if request.POST.get('pricing_type'):
                        location.pricing_type = int(request.POST.get('pricing_type'))
                    if request.POST.get('stock_class'):
                        location.stock_class = int(request.POST.get('stock_class'))
                    if request.POST.get('stock_limit'):
                        location.stock_limit = request.POST.get('stock_limit')
                    if request.POST.get('stock_take_flag'):
                        location.stock_take_flag = request.POST.get('stock_take_flag')
                    if request.POST.get('stock_take_date'):
                        location.stock_take_date = request.POST.get('stock_take_date')
                    location.company_id = company_id
                    location.create_date = datetime.datetime.today()
                    location.update_date = datetime.datetime.today()
                    location.update_by = request.user.id
                    location.is_hidden = 0
                    location.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='location_add')
        else:
            messages_error = "Name field is required"
            return render_to_response('location-add.html',
                                      RequestContext(request, {'messages_error': messages_error,
                                                               'currency': currency}))
        return HttpResponsePermanentRedirect(reverse('location_list'))
    return render_to_response('location-add.html', RequestContext(request, {'currency': currency}))


@login_required
@permission_required('locations.change_location', login_url='/alert/')
def location_edit(request, location_id, active_tab_index):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        location = Location.objects.get(pk=location_id)
    except:
        messages_error = "Location does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    currency = Company.objects.get(pk=company_id).currency
    loc_item_list = LocationItem.objects.filter(is_hidden=0, location_id=location_id)
    loc_item_id = [loc_item.item_id for loc_item in loc_item_list] if loc_item_list else []
    item_list = Item.objects.filter(id__in=loc_item_id, is_hidden=0, company_id=company_id)

    if request.method == 'POST':
        if request.POST.get('name'):
            try:
                location.name = request.POST.get('name')
                if request.POST.get('code'):
                    location.code = request.POST.get('code')
                if request.POST.get('address'):
                    location.address = request.POST.get('address')
                if request.POST.get('attention'):
                    location.attention = request.POST.get('attention')
                if request.POST.get('phone'):
                    location.phone = request.POST.get('phone')
                if request.POST.get('fax'):
                    location.fax = request.POST.get('fax')
                if request.POST.get('pricing_type'):
                    location.pricing_type = int(request.POST.get('pricing_type'))
                if request.POST.get('stock_class'):
                    location.stock_class = int(request.POST.get('stock_class'))
                if request.POST.get('stock_limit'):
                    location.stock_limit = request.POST.get('stock_limit')
                if request.POST.get('stock_take_flag'):
                    location.stock_take_flag = request.POST.get('stock_take_flag')
                if request.POST.get('stock_take_date'):
                    location.stock_take_date = request.POST.get('stock_take_date')
                else:
                    location.stock_take_date = None
                location.company_id = company_id
                location.create_date = datetime.datetime.today()
                location.update_date = datetime.datetime.today()
                location.update_by = request.user.id
                location.is_hidden = 0
                location.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='location_edit')
            return HttpResponsePermanentRedirect(reverse('location_list'))
        else:
            messages_error = "Name field is required"
            location.update_date = location.update_date.strftime("%d-%m-%Y")
            return render_to_response('location-edit.html',
                                      RequestContext(request, {'location': location,
                                                               'currency': currency,
                                                               'loc_item_list': loc_item_list,
                                                               'item_list': item_list,
                                                               'active_tab_index': active_tab_index,
                                                               'messages_error': messages_error}))
    location.update_date = location.update_date.strftime("%d-%m-%Y")
    return render_to_response('location-edit.html',
                              RequestContext(request, {'location': location,
                                                       'currency': currency,
                                                       'active_tab_index': active_tab_index,
                                                       'loc_item_list': loc_item_list,
                                                       'item_list': item_list}))


@login_required
@permission_required('locations.delete_location', login_url='/alert/')
def location_delete(request, location_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        location = Location.objects.get(pk=location_id)
    except:
        messages_error = "Location does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        try:
            location.is_hidden = True
            location.save()
            return HttpResponsePermanentRedirect(reverse('location_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='location_delete')


@login_required
def location_item_search(request, location_id, search_condition):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        loc_item_values = LocationItem.objects.filter(is_hidden=0, location_id=location_id).values_list('item_id',
                                                                                                        flat=True)

        item_list_all = Item.objects.filter(company_id=company_id, is_hidden=0) \
            .exclude(id__in=loc_item_values) \
            .values_list('code', 'name', 'category__name', 'id')

        if search_condition == '0':
            item_list = item_list_all.filter(Q(code__contains=search_condition) |
                                             Q(name__contains=search_condition))
        else:
            item_list = item_list_all.filter(Q(code__contains=search_condition) |
                                             Q(name__contains=search_condition) |
                                             Q(category__name__contains=search_condition))

        item_list_json = json.dumps(list(item_list), cls=DjangoJSONEncoder)
        return HttpResponse(item_list_json, content_type="application/json")


def location_item_condition(request, location_id, active_tab_index):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    search_input = '' if request.POST.get('search_input') is None else request.POST.get('search_input')

    try:
        location = Location.objects.get(pk=location_id)
        company_list = Company.objects.get(id=company_id)
        currency = company_list.first().currency
        contact_list = Contact.objects.filter(is_hidden=0, company_id=company_id, location_id=location_id)
        loc_item_list = LocationItem.objects.filter(is_hidden=0, location_id=location_id)

        loc_item_values = LocationItem.objects.filter(is_hidden=0, location_id=location_id).values_list('item_id',
                                                                                                        flat=True)
        item_list_all = Item.objects.filter(company_id=company_id, is_hidden=0).exclude(id__in=loc_item_values)
        item_list = item_list_all.filter(code__contains=search_input) | \
                    item_list_all.filter(name__contains=search_input) | \
                    item_list_all.filter(category__name__contains=search_input)

        return render_to_response('location-edit.html', RequestContext(request, {'location': location,
                                                                                 'currency': currency,
                                                                                 'active_tab_index': active_tab_index,
                                                                                 'company_list': company_list,
                                                                                 'contact_list': contact_list,
                                                                                 'loc_item_list': loc_item_list,
                                                                                 'item_list': item_list,
                                                                                 'search_input': search_input,
                                                                                 'open_item_search_dialog': 'true'}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('locations.add_location', login_url='/alert/')
def location_category_add(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        location_id = request.POST.get('hdLocationID')
        item_id = ast.literal_eval(request.POST['hdCategory'])
        kk = []
        for id_item in item_id:
            kk.append(int(id_item['item']))
        location = Location.objects.get(pk=location_id)
    except:
        messages_error = "Location does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        try:
            item = Item.objects.filter(category__in=kk, is_hidden=0, company_id=company_id)
            if item:
                for itm in item:
                    loc_item = LocationItem.objects.filter(is_hidden=0, location_id=location.id, item_id=itm.id)
                    if not loc_item:
                        location_item = LocationItem()
                        location_item.location_id = location_id
                        location_item.item_id = itm.id

                        location_item.company_id = company_id
                        location_item.create_date = datetime.datetime.today()
                        location_item.update_date = datetime.datetime.today()
                        location_item.update_by = request.user.id
                        location_item.is_hidden = 0
                        location_item.is_active = 1
                        location_item.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='location_add')
    return HttpResponsePermanentRedirect(reverse('location_edit', args=[location_id, int(LOCATION_TABS['Item'])]))


@login_required
@permission_required('locations.add_location', login_url='/alert/')
def location_item_add(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        location_id = request.POST.get('hdLocationID')
        list_array = ()
        ini_item_list = ast.literal_eval(request.POST['hdItemSelected'])
        item_id = request.POST.get('hdItemSelected')
        kk = []
        for id_item in ini_item_list:
            kk.append(int(id_item['item']))
        location = Location.objects.get(pk=location_id)
    except:
        messages_error = "Location does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        try:
            item = Item.objects.filter(pk__in=kk, is_hidden=0, company_id=company_id)
            for itm in item:
                loc_item = LocationItem.objects.filter(is_hidden=0, location_id=location.id, item_id=itm.id)
                if not loc_item:
                    location_item = LocationItem()
                    location_item.location_id = location_id
                    location_item.item_id = itm.id

                    location_item.company_id = company_id
                    location_item.create_date = datetime.datetime.today()
                    location_item.update_date = datetime.datetime.today()
                    location_item.update_by = request.user.id
                    location_item.is_hidden = 0
                    location_item.is_active = 1
                    location_item.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='location_add')
    return HttpResponsePermanentRedirect(reverse('location_edit', args=[location_id, int(LOCATION_TABS['Item'])]))
    

@login_required
@permission_required('locations.add_location', login_url='/alert/')
def add_loc_item(request, item_id):
    exclude_loc_ids = []
    loc_item_values = LocationItem.objects.filter(is_hidden=0, item_id=item_id)
    if loc_item_values:
        exclude_loc_ids = loc_item_values.values_list('location_id', flat=True)

    locations = Location.objects.exclude(id__in=exclude_loc_ids).values_list('id', 'code')
    item = Item.objects.filter(pk=item_id).first()

    if request.method == 'POST':
        loc_item = LocationItem()
        loc_item.location_id = request.POST.get('location')
        loc_item.item_id = item.id
        loc_item.min_qty = request.POST.get('min_qty')
        loc_item.max_qty = request.POST.get('max_qty')
        loc_item.reorder_qty = request.POST.get('reorder_qty')
        loc_item.onhand_qty = request.POST.get('onhand_qty')
        loc_item.create_date = datetime.datetime.today()
        loc_item.update_date = datetime.datetime.today()
        loc_item.update_by = request.user.id
        loc_item.is_hidden = 0
        loc_item.is_active = 1
        loc_item.onhand_amount = 0
        loc_item.cost_price = 0
        loc_item.booked_amount = 0
        loc_item.save()
    
        return HttpResponsePermanentRedirect(reverse('item_edit', kwargs={'item_id': item_id, 'active_tab_index': '3'}))
    if len(locations):
        return render_to_response('location_items-add.html', 
                    RequestContext(request, {'locations': locations, 'item': item}))
    else:
        messages.add_message(request, messages.ERROR, "No more new Locations.", extra_tags='location_item_add')
        return HttpResponsePermanentRedirect(reverse('item_edit', kwargs={'item_id': item_id, 'active_tab_index': '3'}))


@login_required
@permission_required('locations.delete_location', login_url='/alert/')
def location_item_delete(request):
    try:
        location_id = request.POST.get('hdDelteLocationID')
        item_id = request.POST.get('hdDeleteItemSelected')
        location_item_list = LocationItem.objects.filter(is_hidden=0, location_id=location_id, item_id=item_id)
    except:
        messages_error = "Location does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        try:
            for location_item in location_item_list:
                location_item.delete()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='location_delete')
    return HttpResponsePermanentRedirect(reverse('location_edit', args=[location_id, int(LOCATION_TABS['Item'])]))


@login_required
def LocationList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = Location.objects.filter(is_hidden=0, is_active=1, company_id=company_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) |
            Q(name__contains=search) |
            Q(address__contains=search) |
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
        column_name = "address"
    elif order_column == "4":
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
                "location_code": field.code,
                "location_name": field.name,
                "location_address": field.address,
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


@login_required
def LocationItemList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    location_id = request.GET['location_id']
    list_filter = LocationItem.objects.filter(is_hidden=0, location_id=location_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(item__code__contains=search) |
            Q(item__name__contains=search) |
            Q(item__category__name__contains=search) |
            Q(stock_qty__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = list_filter.count()

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
        column_name = "stock_qty"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "item_id": str(field.item_id),
                "update_date": field.update_date.strftime("%Y-%m-%d"),
                "item_code": field.item.code,
                "item_name": field.item.name,
                "item_description": field.item.name,
                "category": field.item.category.name if field.item.category else '',
                "stock_qty": str(get_item_onhandqty(field.item_id))}
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
def ItemSearch_asJson(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    location_id = request.GET['location_id']

    loc_item_values = LocationItem.objects.filter(is_hidden=0, location_id=location_id).values_list('item_id',
                                                                                                    flat=True)
    list_filter = Item.objects.filter(company_id=company_id, is_hidden=0).exclude(id__in=loc_item_values)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(code__contains=search) |
                                         Q(name__contains=search) |
                                         Q(category__name__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "code"
    elif order_column == "1":
        column_name = "name"
    elif order_column == "2":
        column_name = "category__name"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "item_id": str(field.id),
                "item_code": field.code,
                "item_name": field.name,
                "category": field.category.name if field.category else ''}
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
def location_item_edit(request, location_id, item_id, next=''):
    loc_item_values = LocationItem.objects.filter(is_hidden=0, item_id=item_id)
    if int(location_id) > 0:
        loc_item_values = loc_item_values.filter(location_id=location_id)
    loc_item_values = loc_item_values.first()
    if request.method == 'POST':
        loc_item_values.min_qty = request.POST.get('min_qty')
        loc_item_values.max_qty = request.POST.get('max_qty')
        loc_item_values.reorder_qty = request.POST.get('reorder_qty')
        loc_item_values.update_date = datetime.datetime.today()
        loc_item_values.save()
        if next == '':
            return HttpResponsePermanentRedirect(reverse('load_stock_list', kwargs={'loc_id': location_id}))
        else:
            return HttpResponsePermanentRedirect(reverse('item_edit', kwargs={'item_id': item_id, 'active_tab_index': '3'}))

    return render_to_response('location_items-edit.html', RequestContext(request, {'loc_item_values': loc_item_values, 'next': next}))


@login_required
def delete_loc_item(request, location_id, item_id, next=''):
    loc_item_values = LocationItem.objects.filter(is_hidden=0, item_id=item_id, location_id=location_id).first()
    if request.method == 'POST' and loc_item_values:
        loc_item_values.is_hidden = True
        loc_item_values.update_date = datetime.datetime.today()
        loc_item_values.save()
        messages.add_message(request, messages.ERROR, 'Location item is deleted', extra_tags='location_item_delete')
        if next == '':
            return HttpResponsePermanentRedirect(reverse('load_stock_list', kwargs={'loc_id': location_id}))
        else:
            return HttpResponsePermanentRedirect(reverse('item_edit', kwargs={'item_id': item_id, 'active_tab_index': '3'}))

    return render_to_response('location_items-edit.html', RequestContext(request, {'loc_item_values': loc_item_values, 'next': next}))
