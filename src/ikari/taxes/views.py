import datetime
import json
import logging
import traceback

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from accounts.models import Account, DistributionCode
from taxes.forms import TaxForm, TaxAuthorityForm, TaxGroupForm
from taxes.models import Tax, TaxAuthority, TaxGroup
from utilities.constants import TAX_TRX_TYPES, TAX_TYPE_DICT, PAGE_TYPE, TAX_CLASS
from utilities.messages import MESSAGE_ERROR, EXCEPTION_JOURNAL_ADD, EXCEPTION_JOURNAL_EDIT, EXCEPTION_JOURNAL_DELETE, \
    INVALID_FORM

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def load_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id)
    return render_to_response('tax-list.html', RequestContext(request, {'tax_list': tax_list}))


@login_required
def acc_tax_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id)
    return render_to_response('acc-tax-list.html', RequestContext(request, {'tax_list': tax_list}))


@login_required
@permission_required('taxes.add_tax', login_url='/alert/')
def tax_add(request, module_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    dis_code_list = DistributionCode.objects.filter(is_hidden=False, is_active=True, company_id=company_id)
    tax_group = []#TaxGroup.objects.filter(is_hidden=0, company_id=company_id)
    tax_authority = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id)
    if request.method == 'POST':
        form = TaxForm(company_id, request.POST)
        keys = ['name', 'rate', 'code', 'number', 'ytd', 'mtd', 'ytdoc', 'mtdoc', 'tax_type', 'shortname',
                'tax_group_id']
        tax = Tax()

        for key in keys:
            if request.POST.get(key):
                setattr(tax, key, request.POST.get(key))

        try:
            if request.POST.get('tax_account_code'):
                tax.tax_account_code_id = request.POST.get('tax_account_code')
            else:
                tax.tax_account_code_id = None
            if request.POST.get('distribution_code'):
                tax.distribution_code_id = request.POST.get('distribution_code')
            else:
                tax.distribution_code_id = None
            tax.create_date = datetime.datetime.today()
            tax.update_date = datetime.datetime.today()
            tax.update_by = request.user.id
            tax.is_hidden = 0
            tax.company_id = company_id
            tax.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='tax_add')

        if int(module_type) == int(PAGE_TYPE['S&P']):
            return HttpResponsePermanentRedirect(reverse('tax_list'))
        else:
            return HttpResponsePermanentRedirect(reverse('acc_tax_list'))

    else:
        form = TaxForm(company_id)
    return render(request, 'tax-form.html' if int(module_type) == int(PAGE_TYPE['S&P']) else 'acc-tax-form.html',
                  {'form': form, 'dis_code_list': dis_code_list, 'tax_group_list': tax_group,
                   'tax_authority_list': tax_authority})


@login_required
@permission_required('taxes.change_tax', login_url='/alert/')
def tax_edit(request, tax_id, module_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax = Tax.objects.get(pk=tax_id)
    dis_code_list = DistributionCode.objects.filter(is_hidden=False, is_active=True, company_id=company_id)
    tax_group = []#TaxGroup.objects.filter(is_hidden=0, company_id=company_id)
    tax_authority = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id)
    if request.method == 'POST':
        try:
            if request.POST.get('number'):
                tax.number = request.POST.get('number')
            else:
                tax.number = None
            if request.POST.get('code'):
                tax.code = request.POST.get('code')
            else:
                tax.code = None
            if request.POST.get('name'):
                tax.name = request.POST.get('name')
            else:
                tax.name = None
            if request.POST.get('rate'):
                tax.rate = request.POST.get('rate')
            else:
                tax.rate = None
            if request.POST.get('shortname'):
                tax.shortname = request.POST.get('shortname')
            else:
                tax.shortname = None

            # additional fields from the old system
            if request.POST.get('tax_type'):
                tax.tax_type = request.POST.get('tax_type')
            else:
                tax.tax_type = None

            if request.POST.get('tax_group'):
                tax.tax_group_id = int(request.POST.get('tax_group'))
            else:
                tax.tax_group_id = None

            if request.POST.get('tax_account_code'):
                tax.tax_account_code_id = request.POST.get('tax_account_code')
            else:
                tax.tax_account_code_id = None
            if request.POST.get('distribution_code'):
                tax.distribution_code_id = request.POST.get('distribution_code')
            else:
                tax.distribution_code_id = None

            if request.POST.get('mtd'):
                tax.mtd = request.POST.get('mtd')
            else:
                tax.mtd = None
            if request.POST.get('ytd'):
                tax.ytd = request.POST.get('ytd')
            else:
                tax.ytd = None
            if request.POST.get('mtdoc'):
                tax.mtdoc = request.POST.get('mtdoc')
            else:
                tax.mtdoc = None
            if request.POST.get('ytdoc'):
                tax.ytdoc = request.POST.get('ytdoc')
            else:
                tax.ytdoc = None
            # end of additional fields

            tax.update_date = datetime.datetime.today()
            tax.update_by = request.user.id
            tax.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='tax_edit')
        if int(module_type) == int(PAGE_TYPE['S&P']):
            return HttpResponsePermanentRedirect(reverse('tax_list'))
        else:
            return HttpResponsePermanentRedirect(reverse('acc_tax_list'))

    tax.update_date = tax.update_date.strftime("%d-%m-%Y")
    form = TaxForm(company_id, instance=tax)
    if int(module_type) == int(PAGE_TYPE['S&P']):
        return render(request, 'tax-form.html',
                      {'form': form, 'tax': tax, 'dis_code_list': dis_code_list, 'tax_group_list': tax_group,
                       'tax_authority_list': tax_authority})
    else:
        return render(request, 'acc-tax-form.html',
                      {'form': form, 'tax': tax, 'dis_code_list': dis_code_list, 'tax_group_list': tax_group,
                       'tax_authority_list': tax_authority})


@login_required
@permission_required('taxes.delete_tax', login_url='/alert/')
def tax_delete(request, tax_id, module_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            tax = Tax.objects.get(pk=tax_id)
            tax.is_hidden = True
            tax.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='tax_delete')
        if int(module_type) == int(PAGE_TYPE['S&P']):
            return HttpResponsePermanentRedirect(reverse('tax_list'))
        else:
            return HttpResponsePermanentRedirect(reverse('acc_tax_list'))


@login_required
def TaxList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id)
    records_total = tax_list.count()

    if search:  # Filter data base on search
        tax_list = tax_list.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(rate__contains=search) |
            Q(tax_account_code__name__icontains=search) |
            Q(distribution_code__name__icontains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = tax_list.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "code"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "3":
        column_name = "rate"
    elif order_column == "4":
        column_name = "tax_account_code__name"
    elif order_column == "5":
        column_name = "distribution_code__name"

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = tax_list.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = tax_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "shortname": field.shortname,
                "name": field.name, "code": field.code, "rate": str(field.rate),
                "number": dict(TAX_CLASS)[str(field.number)] if field.number else '',
                "tax_type": "Customer/Vendor" if field.tax_type == TAX_TYPE_DICT['Customer/Vendor'] else "Item",
                "tax_account_code": field.tax_account_code.name if field.tax_account_code else '',
                "distribution_code": field.distribution_code.name if field.distribution_code else '',
                "mtd": str(field.mtd) if field.mtd != None else '', 
                "ytd": str(field.ytd) if field.ytd != None else '',
                "mtdoc": str(field.mtdoc) if field.mtdoc != None else '', 
                "ytdoc": str(field.ytdoc) if field.ytdoc != None else ''
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


@login_required
def tax_authority_list(request):
    return render(request, 'tax-authority-list.html')


@login_required
def TaxAuthorityList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax_auth_list = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id)
    records_total = tax_auth_list.count()

    if search:  # Filter data base on search
        tax_auth_list = tax_auth_list.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = tax_auth_list.count()

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = tax_auth_list.order_by('update_date')[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = tax_auth_list.order_by('-update_date')[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "code": field.code,
                "name": field.name,
                "currency": field.currency.code,
                "is_recoverable": field.is_recoverable,
                "recoverable_rate": str(field.recoverable_rate),
                "recoverable_account": field.recoverable_account.code if field.recoverable_account else None}
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
@permission_required('taxes.add_tax', login_url='/alert/')
def tax_authority_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_list = Account.objects.filter(
        company_id=company_id, is_hidden=False, is_active=True).order_by('account_segment', 'code')
    form = TaxAuthorityForm()
    if request.method == 'POST':
        form = TaxAuthorityForm(request.POST)
        if form.is_valid():
            try:
                tax_authority_entry = form.save(commit=False)
                tax_authority_entry.liability_account_id = request.POST.get('liability_account')
                tax_authority_entry.is_recoverable = True if request.POST.get('is_recoverable') else False
                tax_authority_entry.recoverable_account_id = request.POST.get('recoverable_account')
                tax_authority_entry.is_expense_separately = True if request.POST.get('is_expense_separately') else False
                tax_authority_entry.expense_account_id = request.POST.get('expense_account')
                tax_authority_entry.company_id = company_id
                tax_authority_entry.create_date = datetime.datetime.today()
                tax_authority_entry.update_date = datetime.datetime.today()
                tax_authority_entry.update_by = request.user.id
                tax_authority_entry.is_hidden = False
                tax_authority_entry.save()
            except Exception as e:
                print(EXCEPTION_JOURNAL_ADD % 'Tax Authority', e)
                logging.error(traceback.format_exc())
                messages.error(request, EXCEPTION_JOURNAL_ADD % 'Tax Authority')
        return HttpResponsePermanentRedirect(reverse('tax_authority_list'))

    return render(request, 'tax-authority-form.html', {'form': form, 'account_list': account_list})


@login_required
@permission_required('taxes.add_tax', login_url='/alert/')
def tax_authority_edit(request, tax_authority_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_list = Account.objects.filter(
        company_id=company_id, is_hidden=False, is_active=True).order_by('account_segment', 'code')
    try:
        tax_authority = TaxAuthority.objects.get(pk=tax_authority_id)
        form = TaxAuthorityForm(instance=tax_authority)
        if request.method == 'POST':
            form = TaxAuthorityForm(data=request.POST, instance=tax_authority)
            if form.is_valid():

                tax_authority_entry = form.save(commit=False)
                tax_authority_entry.liability_account_id = request.POST.get('liability_account')
                tax_authority_entry.is_recoverable = True if request.POST.get('is_recoverable') else False
                tax_authority_entry.recoverable_account_id = request.POST.get('recoverable_account')
                tax_authority_entry.is_expense_separately = True if request.POST.get(
                    'is_expense_separately') else False
                tax_authority_entry.expense_account_id = request.POST.get('expense_account')
                tax_authority_entry.update_date = datetime.datetime.today()
                tax_authority_entry.update_by = request.user.id
                tax_authority_entry.save()
            else:
                print(INVALID_FORM, ' Form error: ', form.errors)
                messages.error(request, INVALID_FORM)

            return HttpResponsePermanentRedirect(reverse('tax_authority_list'))
    except Exception as e:
        print(EXCEPTION_JOURNAL_EDIT % 'Tax Authority', e)
        logging.error(traceback.format_exc())
        messages.error(request, EXCEPTION_JOURNAL_EDIT % 'Tax Authority')

    return render(request, 'tax-authority-form.html',
                  {'form': form, 'account_list': account_list, 'tax_authority': tax_authority})


@login_required
@permission_required('taxes.delete_tax', login_url='/alert/')
def tax_authority_delete(request, tax_authority_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            tax_authority = TaxAuthority.objects.get(pk=tax_authority_id)
            tax_authority.is_hidden = True
            tax_authority.save()
        except Exception as e:
            print(EXCEPTION_JOURNAL_DELETE % 'Tax Authority', e)
            logging.error(traceback.format_exc())
            messages.add_message(request, EXCEPTION_JOURNAL_DELETE % 'Tax Authority', e,
                                 extra_tags='tax_authority_delete')
    return HttpResponsePermanentRedirect(reverse('tax_authority_list'))


@login_required
def tax_group_list(request):
    return render(request, 'tax-group-list.html')


@login_required
def TaxGroupList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    transaction_type_dict = dict(TAX_TRX_TYPES)

    tax_group_list = TaxGroup.objects.filter(is_hidden=0, company_id=company_id)
    records_total = tax_group_list.count()

    if search:  # Filter data base on search
        tax_group_list = tax_group_list.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = tax_group_list.count()

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = tax_group_list.order_by('update_date')[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = tax_group_list.order_by('-update_date')[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "code": field.code,
                "name": field.name,
                "transaction_type": transaction_type_dict.get(str(field.transaction_type)),
                "currency": field.currency.code,
                "calculation_method": field.calculation_method,
                "tax_authority": field.tax_authority.code if field.tax_authority else None}
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
@permission_required('taxes.add_tax', login_url='/alert/')
def tax_group_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_list = Account.objects.filter(
        company_id=company_id, is_hidden=False, is_active=True).order_by('account_segment', 'code')
    tax_authority_list = TaxAuthority.objects.filter(is_hidden=0, company_id=company_id)
    form = TaxGroupForm()
    if request.method == 'POST':
        form = TaxGroupForm(request.POST)
        if form.is_valid():
            try:
                tax_group_entry = form.save(commit=False)
                tax_group_entry.tax_authority_id = request.POST.get('tax_authority')
                tax_group_entry.is_taxable = True if request.POST.get('is_taxable') else False
                tax_group_entry.is_surtax = True if request.POST.get('is_surtax') else False
                tax_group_entry.surtax_authority_id = request.POST.get('surtax_on_authority')
                tax_group_entry.surtax_authority_account_id = request.POST.get('surtax_account')
                tax_group_entry.company_id = company_id
                tax_group_entry.create_date = datetime.datetime.today()
                tax_group_entry.update_date = datetime.datetime.today()
                tax_group_entry.update_by = request.user.id
                tax_group_entry.is_hidden = False
                tax_group_entry.save()
            except Exception as e:
                print(EXCEPTION_JOURNAL_ADD % 'Tax Group', e)
                logging.error(traceback.format_exc())
                messages.error(request, EXCEPTION_JOURNAL_ADD % 'Tax Group')
        return HttpResponsePermanentRedirect(reverse('tax_group_list'))

    return render(request, 'tax-group-form.html',
                  {'form': form, 'account_list': account_list, 'tax_authority_list': tax_authority_list})


@login_required
@permission_required('taxes.add_tax', login_url='/alert/')
def tax_group_edit(request, tax_group_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_list = Account.objects.filter(
        company_id=company_id, is_hidden=False, is_active=True).order_by('account_segment', 'code')
    tax_authority_list = TaxAuthority.objects.filter(company_id=company_id, is_hidden=False)
    try:
        tax_group = TaxGroup.objects.get(pk=tax_group_id)
        form = TaxGroupForm(instance=tax_group)
        if request.method == 'POST':
            form = TaxGroupForm(data=request.POST, instance=tax_group)
            if form.is_valid():
                tax_group_entry = form.save(commit=False)
                tax_group_entry.tax_authority_id = request.POST.get('tax_authority')
                tax_group_entry.is_taxable = True if request.POST.get('is_taxable') else False
                tax_group_entry.is_surtax = True if request.POST.get('is_surtax') else False
                tax_group_entry.surtax_authority_id = request.POST.get('surtax_on_authority')
                tax_group_entry.surtax_authority_account_id = request.POST.get('surtax_account')
                tax_group_entry.update_date = datetime.datetime.today()
                tax_group_entry.update_by = request.user.id
                tax_group_entry.save()
            else:
                print(INVALID_FORM, ' Form error: ', form.errors)
                messages.error(request, INVALID_FORM)

            return HttpResponsePermanentRedirect(reverse('tax_group_list'))
    except Exception as e:
        print(EXCEPTION_JOURNAL_EDIT % 'Tax Group', e)
        logging.error(traceback.format_exc())
        messages.error(request, EXCEPTION_JOURNAL_EDIT % 'Tax Group')

    return render(request, 'tax-group-form.html', {'form': form, 'account_list': account_list, 'tax_group': tax_group,
                                                   'tax_authority_list': tax_authority_list})


@login_required
@permission_required('taxes.delete_tax', login_url='/alert/')
def tax_group_delete(request, tax_group_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            tax_group = TaxGroup.objects.get(pk=tax_group_id)
            tax_group.is_hidden = True
            tax_group.save()
        except Exception as e:
            print(EXCEPTION_JOURNAL_DELETE % 'Tax Group', e)
            logging.error(traceback.format_exc())
            messages.add_message(request, EXCEPTION_JOURNAL_DELETE % 'Tax Group', e, extra_tags='tax_group_delete')
    return HttpResponsePermanentRedirect(reverse('tax_group_list'))
