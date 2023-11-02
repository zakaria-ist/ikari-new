import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
from countries.forms import CompanyForm
from countries.models import Country
from currencies.models import Currency
from taxes.models import Tax
from utilities.constants import TRN_CODE_TYPE_DICT


@login_required
def load_list(request):
    return render_to_response('country-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Global']}))


@login_required
def list_country(request):
    return render_to_response('country-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Sales Number File']}))


@login_required
@permission_required('countries.add_country', login_url='/alert/')
def country_add(request, menu_type):
    country = Country()
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id)
    currency_list = Currency.objects.filter(is_hidden=0)
    form = CompanyForm()
    if request.method == 'POST':
        try:
            country = Country()
            country.name = request.POST.get('name')
            country.code = request.POST.get('code')
            if request.POST.get('tax') != "0" and request.POST.get('tax'):
                country.tax_id = request.POST.get('tax')
            else:
                country.tax_id = None
            country.currency_id = request.POST.get('currency')
            country.create_date = datetime.datetime.today()
            country.update_date = datetime.datetime.today()
            country.update_by = request.user.id
            country.is_hidden = 0
            country.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='country_add')

        return HttpResponsePermanentRedirect(reverse('list_country'))
    context = {'tax_list': tax_list, 'currency_list': currency_list, 'form': form, 'menu_type': menu_type}
    return render_to_response('country-add.html',
                              RequestContext(request, context))


@login_required
@permission_required('countries.change_country', login_url='/alert/')
def country_edit(request, country_id, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    country = Country.objects.get(pk=country_id)
    tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id)
    currency_list = Currency.objects.filter(is_hidden=0)
    if request.method == 'POST':
        try:
            country.name = request.POST.get('name')
            country.code = request.POST.get('code')
            if request.POST.get('tax') != "0" and request.POST.get('tax'):
                country.tax_id = request.POST.get('tax')
            else:
                country.tax_id = None
            country.currency_id = request.POST.get('currency')
            country.create_date = datetime.datetime.today()
            country.update_date = datetime.datetime.today()
            country.update_by = request.user.id
            country.is_hidden = 0
            country.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='country_edit')
        return HttpResponsePermanentRedirect(reverse('list_country'))
    country.update_date = country.update_date.strftime("%d-%m-%Y")
    return render_to_response('country-edit.html', RequestContext(request, {'country': country, 'tax_list': tax_list,
                                                                            'currency_list': currency_list,
                                                                            'message': messages,
                                                                            'menu_type': menu_type}))


@login_required
@permission_required('countries.delete_country', login_url='/alert/')
def country_delete(request, country_id):
    if request.method == 'POST':
        try:
            country = Country.objects.get(pk=country_id)
            country.is_hidden = True
            country.save()
            return HttpResponsePermanentRedirect(reverse('list_country'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='country_delete')


@login_required
def country_list_asJson(request):
    country_list = Country.objects.filter(is_hidden=0)
    array = []

    for field in country_list:
        data = {"id": str(field.id),
                "name": str(field.name),
                "code": str(field.code)}
        array.append(data)

    json_content = json.dumps(array, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def Countries__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Country.objects.filter(is_hidden=0)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(name__icontains=search) | Q(code__icontains=search) |
            Q(currency__name__icontains=search)
        )

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "name"
    elif order_column == "2":
        column_name = "code"
    elif order_column == "3":
        column_name = "currency__name"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": str(field.id),
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "name": field.name,
                "code": field.code,
               }
        try:
            data["currency__name"] = field.currency.name
        except:
            data["currency__name"] = ""
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')
