from django.template import RequestContext
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from banks.models import Bank
from accounts.models import Account
from companies.models import Company
from accounting.models import Journal
from banks.forms import BankForm
from utilities.constants import BALANCE_TYPE, ACCOUNT_TYPE
import datetime
from django.db.models import Q
import json
import logging
import traceback
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def load_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    bank_list = Bank.objects.filter(is_hidden=0, company_id=company_id, is_active=True).order_by('-id')
    return render_to_response('bank-list.html', RequestContext(request, {'bank_list': bank_list}))


def bank_change_check(user):
    if user.has_perm('banks.change_bank') or user.has_perm('banks.add_bank'):
        return True
    return False


@login_required
@permission_required('banks.add_bank', login_url='/alert/')
def bank_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    company_currency_id = company.currency_id
    if request.method == 'POST':
        form = BankForm(company_id, request.POST)
        if form.is_valid():
            try:
                my_bank = form.save(commit=False)
                if request.POST.get('currency') is None or request.POST.get('currency') == '':
                    my_bank.currency_id = None
                if request.POST.get('gain_account') is None or request.POST.get('gain_account') == '':
                    my_bank.gain_account_id = None
                if request.POST.get('loss_account') is None or request.POST.get('loss_account') == '':
                    my_bank.loss_account_id = None
                if request.POST.get('round_account') is None or request.POST.get('round_account') == '':
                    my_bank.round_account_id = None
                my_bank.company_id = company_id
                my_bank.create_date = datetime.datetime.today()
                my_bank.update_date = datetime.datetime.today()
                my_bank.update_by = request.user.id
                my_bank.is_hidden = 0
                my_bank.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='bank_add')
            return HttpResponsePermanentRedirect(reverse('bank_list'))
        else:
            form = BankForm(company_id, request.POST)
    else:
        form = BankForm(company_id)
    return render(request, 'bank-form.html', {'form': form, 'company_currency_id': company_currency_id})


@login_required
@permission_required('banks.change_bank', login_url='/alert/')
def bank_edit(request, bank_id=''):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    company_currency_id = company.currency_id
    bank = Bank.objects.get(pk=bank_id)
    post = get_object_or_404(Bank, pk=bank_id)
    if request.method == 'POST':
        form = BankForm(company_id, request.POST, instance=post)
        if form.is_valid():
            try:
                my_bank = form.save(commit=False)
                if request.POST.get('currency') is None or request.POST.get('currency') == '':
                    my_bank.currency_id = None
                if request.POST.get('gain_account') is None or request.POST.get('gain_account') == '':
                    my_bank.gain_account_id = None
                if request.POST.get('loss_account') is None or request.POST.get('loss_account') == '':
                    my_bank.loss_account_id = None
                if request.POST.get('round_account') is None or request.POST.get('round_account') == '':
                    my_bank.round_account_id = None
                my_bank.update_date = datetime.datetime.today()
                my_bank.update_by = request.user.id
                my_bank.is_hidden = 0
                my_bank.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='bank_edit')
            return HttpResponsePermanentRedirect(reverse('bank_list'))
    post.update_date = post.update_date.strftime("%d-%m-%Y")
    form = BankForm(company_id, instance=post)
    return render(request, 'bank-form.html', {'form': form, 'bank': bank, 'company_currency_id': company_currency_id})


@login_required
@permission_required('banks.delete_bank', login_url='/alert/')
def bank_delete(request, bank_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            my_bank = Bank.objects.get(pk=bank_id)
            my_bank.is_active = False
            journals = Journal.objects.filter(company_id=company_id, bank_id=bank_id, is_hidden=0)
            if not len(journals):
                my_bank.is_hidden = True
                messages.add_message(request, messages.INFO, 'Bank is Deleted', extra_tags='bank_delete')
            else:
                messages.add_message(request, messages.WARNING, 'Bank is Deactivated but not deleted. As there are some dependencies', extra_tags='bank_delete')
            my_bank.save()
            return HttpResponsePermanentRedirect(reverse('bank_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='bank_delete')


@csrf_exempt
@login_required
def load_account(request):
    if request.method == 'POST':
        if 'account_id' in request.POST and request.POST['account_id']:
            account_id = request.POST['account_id']
            account = Account.objects.get(pk=account_id)
            context = {
                'name': account.name,
            }
            return HttpResponse(json.dumps(context), content_type="application/json")

    return HttpResponseNotFound


@login_required
def Bank__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = Bank.objects.filter(company_id=company_id, is_hidden=0).order_by('id')
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(update_date__contains=search)
                                         | Q(name__icontains=search)
                                         | Q(code__icontains=search)
                                         | Q(account__code__contains=search))

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
        column_name = "account__code"
    elif order_column == "5":
        column_name = "is_active"
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
                "bank_name": field.name,
                "bank_code": field.code,
                "account__code": field.account.code if field.account else '',
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
def AccountList__asJson(request):

    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    balance_type_dict = dict(BALANCE_TYPE)
    account_type_dict = dict(ACCOUNT_TYPE)

    list_filter = Account.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    records_total = list_filter.count()

    if search:
        if search.lower() in "income statement":
            cons = 1
        elif search[0].lower() in "balance sheet":
            cons = 2
        elif search[0].lower() in "retained earning":
            cons = 3
        else:
            cons = search

        if search.lower() in "credit":
            stat = 2
        elif search.lower() in "debit":
            stat = 1
        else:
            stat = search

        list_filter = list_filter.filter(
            Q(name__contains=search) | Q(code__contains=search)
            | Q(account_type__contains=cons)
            | Q(balance_type__contains=stat)
            | Q(company__name__contains=search)
            | Q(update_date__contains=search)
        )

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "code"
    elif order_column == "1":
        column_name = "name"
    elif order_column == "2":
        column_name = "account_type"
    elif order_column == "3":
        column_name = "balance_type"
    elif order_column == "4":
        column_name = "account_group"
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
                "account_type": account_type_dict.get(field.account_type),
                "balance_type": balance_type_dict.get(field.balance_type),
                "account_group": field.account_group.name if field.account_group else '',
                "company_name": field.company.name if field.company else ''}
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')

