import ast
import calendar
import datetime
import json
import logging
import traceback

import simplejson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.db.models.expressions import RawSQL
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from accounting.models import FiscalCalendar
from accounts.forms import AccountSetForm, RevaluationCodeForm
from accounts.models import Account, AccountType, DistributionCode, AccountHistory, AccountSet, AccountCurrency, \
    ReportGroup, RevaluationCode
from companies.models import Company, CostCenters
from currencies.models import Currency
from utilities.common import round_number, get_decimal_place
from transactions.models import Transaction
from utilities.constants import BALANCE_TYPE, ACCOUNT_TYPE, REPORT_CATEGORY, SOURCE_TYPES, ACCOUNT_SET_TYPE, \
    STATUS_TYPE_DICT, TRANSACTION_TYPES, REPORT_TEMPLATE_TYPES_DICT
from utilities.messages import MESSAGE_SUCCESS, MESSAGE_ERROR_2, REFRESH_OR_GO_GET_SUPPORT

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def load_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    session_date = request.session['session_date']
    fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, start_date__lte=session_date, end_date__gte=session_date).first()
    if fsc_calendar:
        fsc_year = fsc_calendar.fiscal_year
        fsc_month = fsc_calendar.period
        fsc_period = str(fsc_month) + '-' + str(fsc_year)
    return render_to_response('account-list.html', RequestContext(request, {'fsc_period': fsc_period}))


@login_required
def load_type_list(request):
    return render_to_response('account-type-list.html',
                              RequestContext(request))


@login_required
def load_dist_code_list(request, type):
    return render_to_response('distribution-code-list.html', RequestContext(request, {'type': type}))


@login_required
def load_account_set_list(request, account_set_type):
    return render_to_response('account-set-list.html', RequestContext(request,
                                                                      {'account_set_type': account_set_type}))


@login_required
@permission_required('accounts.add_account', login_url='/alert/')
def account_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    account = Account()
    all_currency = Currency.objects.filter(is_hidden=False)

    revaluation_account = Account.objects.filter(
        is_hidden=False, is_active=True, company_id=company_id).order_by('account_segment', 'code')
    revaluation_codes = RevaluationCode.objects.filter(is_hidden=False, company_id=company_id)

    try:
        account_group = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])
    except ObjectDoesNotExist:
        account_group = AccountType.objects.filter(is_hidden=0, company_id=None)

    balance_sheet_group = account_group.filter(category=2)
    profit_loss_group = account_group.filter(category=3)

    if request.method == 'POST':
        try:
            if request.POST.get('multicurrency-checkbox'):
                account.is_multicurrency = True
            else:
                account.is_multicurrency = False
            if request.POST.get('active-checkbox'):
                account.is_active = True
            else:
                account.is_active = False
            if request.POST.get('editable-checkbox'):
                account.is_editable = True
            else:
                account.is_editable = False
            account.name = request.POST.get('name')
            account.description = request.POST.get('code')
            account.account_segment = request.POST.get('code')
            if company.use_segment:
                if request.POST.get('segm_code'):
                    account.segment_code_id = request.POST.get('segm_code')
                    account.code = request.POST.get('code') + '-' + account.segment_code.code
                else:
                    account.code = request.POST.get('code')
            else:
                account.code = request.POST.get('code')
            account.update_by = request.user.id
            account.create_date = datetime.datetime.today()
            account.is_hidden = False
            account.company_id = company_id
            # if request.POST.get('profit_loss_group') and request.POST.get('profit_loss_group') != '0':
            #     account.profit_loss_group_id = request.POST.get('profit_loss_group')
            # else:
            #     account.profit_loss_group_id = None
            account.account_group_id = request.POST.get('account_group')
            account.account_type = request.POST.get('account_type')
            account.balance_type = request.POST.get('balance_type_radio')
            account.save()

            if account.is_multicurrency:
                if request.POST.get('radioOptions') and int(request.POST.get('radioOptions')) == 1:
                    account.is_specific_currency = True
                else:
                    account.is_specific_currency = False
                if request.POST.get('default_curr') and int(request.POST.get('default_curr')) > 0:
                    account.default_currency_id = int(request.POST.get('default_curr'))
                else:
                    account.default_currency_id = company.currency_id
                account.save()

            # Create list of AccountHistory for newly created account
            session_date = request.session['session_date']
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, start_date__lte=session_date, end_date__gte=session_date).first()
            start_year = int(fsc_calendar.fiscal_year) if fsc_calendar else datetime.datetime.today().year
            this_year = start_year
            company = Company.objects.get(pk=company_id)
            if company.current_period_year and int(company.current_period_year) < start_year:
                start_year = int(company.current_period_year)
                this_year = start_year

            #     if account_history_list.count() < total_records:
            last_day = None
            # all_month_list = list(range(1, 13))
            # account_history_list = AccountHistory.objects.filter(company_id=company_id, is_hidden=False,
            #                                                      account_id=account.id)
            while start_year < this_year + 3:

                # account_history = account_history_list.filter(period_year=start_year)
                # month_list = [history.period_month for history in account_history]
                # month_not_in_list = set(all_month_list) - set(month_list)

                for i in range(12):
                    _, num_days = calendar.monthrange(start_year, i + 1)
                    last_day = datetime.date(start_year, i + 1, num_days)

                    account_history = AccountHistory()
                    account_history.period_year = start_year
                    account_history.period_month = i + 1
                    account_history.period_date = last_day
                    account_history.company_id = company_id
                    account_history.account_id = account.id
                    account_history.source_currency_id = company.currency_id
                    account_history.functional_currency_id = company.currency_id
                    account_history.save()

                account_history = AccountHistory()
                account_history.period_year = start_year
                account_history.period_month = 'ADJ'
                account_history.period_date = last_day
                account_history.company_id = company_id
                account_history.account_id = account.id
                account_history.source_currency_id = company.currency_id
                account_history.functional_currency_id = company.currency_id
                account_history.save()

                account_history = AccountHistory()
                account_history.period_year = start_year
                account_history.period_month = 'CLS'
                account_history.period_date = last_day
                account_history.company_id = company_id
                account_history.account_id = account.id
                account_history.source_currency_id = company.currency_id
                account_history.functional_currency_id = company.currency_id
                account_history.save()

                start_year += 1
            # End of creating AccountHistory

            if request.POST.get('multicurrency-checkbox'):
                currency_list_new = ast.literal_eval(request.POST['curr_list_data'])
                if len(currency_list_new) > 0:
                    for curr_list in currency_list_new:
                        if curr_list['curr_id'] and int(curr_list['curr_id']) > 0:
                            curr = AccountCurrency()
                            curr.create_date = datetime.datetime.today()
                            curr.name = account.code
                            curr.account_id = account.id
                            curr.currency_id = curr_list['curr_id']
                            if int(curr_list['revaluation_code_id']) == 0:
                                curr_list['revaluation_code_id'] = None
                            curr.revaluation_code_id = curr_list['revaluation_code_id']
                            if curr_list['revaluation_code_id']:
                                curr.is_active = True
                            else:
                                curr.is_active = False
                            curr.is_hidden = False
                            curr.update_date = datetime.datetime.today()
                            curr.update_by = request.user.id
                            curr.save()

                            # account history
                            start_year = int(fsc_calendar.fiscal_year) if fsc_calendar else datetime.datetime.today().year
                            this_year = start_year
                            while start_year < this_year + 3:
                                if int(curr_list['curr_id']) != company.currency_id:
                                    for i in range(12):
                                        _, num_days = calendar.monthrange(start_year, i + 1)
                                        last_day = datetime.date(start_year, i + 1, num_days)

                                        account_history = AccountHistory()
                                        account_history.period_year = start_year
                                        account_history.period_month = i + 1
                                        account_history.period_date = last_day
                                        account_history.company_id = company_id
                                        account_history.account_id = account.id
                                        account_history.source_currency_id = curr_list['curr_id']
                                        account_history.functional_currency_id = company.currency_id
                                        account_history.save()

                                    account_history = AccountHistory()
                                    account_history.period_year = start_year
                                    account_history.period_month = 'ADJ'
                                    account_history.period_date = last_day
                                    account_history.company_id = company_id
                                    account_history.account_id = account.id
                                    account_history.source_currency_id = curr_list['curr_id']
                                    account_history.functional_currency_id = company.currency_id
                                    account_history.save()

                                    account_history = AccountHistory()
                                    account_history.period_year = start_year
                                    account_history.period_month = 'CLS'
                                    account_history.period_date = last_day
                                    account_history.company_id = company_id
                                    account_history.account_id = account.id
                                    account_history.source_currency_id = curr_list['curr_id']
                                    account_history.functional_currency_id = company.currency_id
                                    account_history.save()
                                else:
                                    break

                                start_year += 1
                            # End of creating AccountHistory

            return HttpResponsePermanentRedirect(reverse('account_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_add')
            logger.error(traceback.format_exc())

    if company.use_segment:
        segment_list = CostCenters.objects.filter(company_id=company.id, is_active=True)
    else:
        segment_list = None
    context = {
        'account_group': account_group,
        'account_type': ACCOUNT_TYPE,
        'balance_type': BALANCE_TYPE,
        'account_set_type': ACCOUNT_SET_TYPE,
        'balance_sheet_group': balance_sheet_group,
        'profit_loss_group': profit_loss_group,
        'currency_list': all_currency,
        'revaluation_code_list': revaluation_codes,
        'company': company,
        'segment_list': segment_list,
    }
    return render(request, 'account-add.html', context)


def coverterDateTime(o):
    if isinstance(o, datetime.date):
        return o.__str__()


@login_required
@permission_required('accounts.change_account', login_url='/alert/')
def account_edit(request, account_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    account = Account.objects.get(pk=account_id)
    all_currency = Currency.objects.filter(is_hidden=False)
    revaluation_account = Account.objects.filter(
        is_hidden=False, is_active=True, company_id=company_id).order_by('account_segment', 'code')
    revaluation_codes = RevaluationCode.objects.filter(is_hidden=False, company_id=company_id)
    account_currency = AccountCurrency.objects.filter(account_id=account_id, is_hidden=False)

    try:
        account_group = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])
    except ObjectDoesNotExist:
        account_group = AccountType.objects.filter(is_hidden=0, company_id=None)

    balance_sheet_group = account_group.filter(category=2)
    profit_loss_group = account_group.filter(category=3)

    if request.method == 'POST':
        try:
            if company.use_segment:
                if request.POST.get('segm_code'):
                    account.segment_code_id = request.POST.get('segm_code')
                    account.code = account.account_segment + '-' + account.segment_code.code
                else:
                    account.segment_code_id = None
                    account.code = account.account_segment
            # else:
            #     account.code = request.POST.get('code')
            account.name = request.POST.get('name')
            if not account.is_multicurrency:
                if request.POST.get('multicurrency-checkbox'):
                    account.is_multicurrency = True
                else:
                    account.is_multicurrency = False
            if account.is_multicurrency:
                if request.POST.get('radioOptions') and int(request.POST.get('radioOptions')) == 1:
                    account.is_specific_currency = True
                else:
                    account.is_specific_currency = False
                if request.POST.get('default_curr') and int(request.POST.get('default_curr')) > 0:
                    account.default_currency_id = int(request.POST.get('default_curr'))
                else:
                    account.default_currency_id = company.currency_id
            if request.POST.get('active-checkbox'):
                account.is_active = True
            else:
                account.is_active = False
            if account.is_active == False:
                today = datetime.datetime.today()
                account.deactivate_date = today
                try:
                    fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
                    account.deactivate_period = datetime.date(int(fsc_calendar.fiscal_year), int(fsc_calendar.period), 1)
                except:
                    account.deactivate_period = today
            else:
                account.deactivate_date = None
                account.deactivate_period = None
            if request.POST.get('editable-checkbox'):
                account.is_editable = True
            else:
                account.is_editable = False
            # if request.POST.get('profit_loss_group') and request.POST.get('profit_loss_group') != '0':
            #     account.profit_loss_group_id = request.POST.get('profit_loss_group')
            # else:
            #     account.profit_loss_group_id = None
            account.update_by = request.user.id
            account.update_date = datetime.datetime.today()
            account.account_group_id = request.POST.get('account_group')
            account.account_type = request.POST.get('account_type')
            account.balance_type = request.POST.get('balance_type_radio')
            account.save()

            if account.is_multicurrency:
                currency_list_new = ast.literal_eval(request.POST['curr_list_data'])
                if len(currency_list_new) > 0:
                    if account_currency.count() > len(currency_list_new):
                        for acc_curr in account_currency:
                            acc_curr.is_hidden = True
                            acc_curr.save()

                    for curr_list in currency_list_new:
                        curr = None
                        if curr_list['curr_id'] and int(curr_list['curr_id']) > 0:
                            if curr_list['id']:
                                curr = AccountCurrency.objects.get(pk=curr_list['id'])
                            else:
                                curr = AccountCurrency()
                                curr.create_date = datetime.datetime.today()
                            if int(curr_list['revaluation_code_id']) == 0:
                                curr_list['revaluation_code_id'] = None
                            curr.name = account.code
                            curr.account_id = curr_list['account_id']
                            curr.currency_id = curr_list['curr_id']
                            curr.revaluation_code_id = curr_list['revaluation_code_id']
                            if curr_list['revaluation_code_id']:
                                curr.is_active = True
                            else:
                                curr.is_active = False
                            curr.is_hidden = False
                            curr.update_date = datetime.datetime.today()
                            curr.update_by = request.user.id
                            curr.save()
                        # else:
                        #     account2 = Account.objects.get(pk=account.id)
                        #     account2.is_multicurrency = False
                        #     account.update_by = request.user.id
                        #     account.update_date = datetime.datetime.today()
                        #     account2.save()

            return HttpResponsePermanentRedirect(reverse('account_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_edit')
            logger.error(traceback.format_exc())
    account.update_date = account.update_date.strftime("%d-%m-%Y")
    if company.use_segment:
        segment_list = CostCenters.objects.filter(company_id=company.id, is_active=True)
    else:
        segment_list = None
    context = {
        'account': account,
        'account_group': account_group,
        'account_type': ACCOUNT_TYPE,
        'balance_type': BALANCE_TYPE,
        'account_set_type': ACCOUNT_SET_TYPE,
        'balance_sheet_group': balance_sheet_group,
        'profit_loss_group': profit_loss_group,
        'currency_list': all_currency,
        'revaluation_code_list': revaluation_codes,
        'account_currency_list': account_currency,
        'company': company,
        'segment_list': segment_list,
    }
    return render(request, 'account-edit.html', context)


@login_required
def load_account_history_list(request, account_id=None):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    session_date = request.session['session_date']
    fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, start_date__lte=session_date, end_date__gte=session_date).first()
    if fsc_calendar:
        this_year = fsc_calendar.fiscal_year
    else:
        this_year = datetime.datetime.now().year

    account_list = Account.objects.filter(
        is_hidden=False, is_active=True, company_id=company.id).order_by('account_segment', 'code')
    # load default account
    if len(account_list):
        try:
            if account_id == None:
                account_id = account_list.last().id
            account = Account.objects.get(pk=account_id)
            year_list = AccountHistory.objects.filter(is_hidden=0, company_id__in=[company_id, None]).values(
                'period_year').order_by('period_year').distinct()
            max_year = 0
            for year in year_list:
                if int(year['period_year']) > int(max_year):
                    max_year = year['period_year']
                if int(year['period_year']) == int(this_year):
                    this_year = year['period_year']

            currency_list = Currency.objects.filter(is_hidden=0)

            context = {
                'account_list' : account_list,
                'account': account,
                'year_list': year_list,
                'currency_list': currency_list,
                'max_year': max_year,
                'this_year' : this_year,
                'company_currency': company.currency_id
            }
            return render(request, 'account-history.html', context)

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_delete')
            logger.error(traceback.format_exc())
    else:
        context = {}
        return render(request, 'account-history.html', context)


@login_required
def get_account_code_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    try:
        account_list = Account.objects.filter(is_hidden=False, company_id=company.id)\
                        .order_by('account_segment', 'code')\
                        .values_list('id', 'code')
        content = {
            "account_list": list(account_list)
        }

    except:
        content = {
            "account_list": []
        }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')



@login_required
def AccountHistory__asJson(request):
    draw = request.POST['draw']

    search = request.POST['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_id = request.POST['account_id'] if 'account_id' in request.POST else 0
    if account_id == '':
        account_id = 0
    list_filter = AccountHistory.objects.filter(is_hidden=0, company_id=company_id, account_id=account_id)

    year = request.POST['year'] if 'year' in request.POST else 0
    currency = request.POST['currency'] if 'currency' in request.POST else 0
    currency_type = request.POST['currency_type'] if 'currency_type' in request.POST else ''

    if year:
        list_filter = list_filter.filter(period_year=year)

    if currency:
        # if currency_type == '2':
        list_filter = list_filter.filter(source_currency=currency)
        # else:
        #     list_filter = list_filter.filter(source_currency=currency) | list_filter.filter(source_currency=None)

        list_filter = list_filter.values( \
            'period_month', 'period_date', 'source_begin_balance', 'source_net_change', \
            'source_end_balance', 'functional_begin_balance', 'functional_net_change', \
            'functional_end_balance').distinct()

    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(period_month__contains=search)
                                         | Q(period_date__contains=search)
                                         | Q(source_net_change__contains=search)
                                         | Q(source_end_balance__contains=search)
                                         | Q(functional_net_change__contains=search)
                                         | Q(functional_end_balance__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.POST['order[0][column]']
    column_name = ""
    if order_column == "0":
        column_name = "period_month"
    elif order_column == "1":
        column_name = "period_date"
    elif order_column == "2":
        column_name = "source_net_change"
    elif order_column == "3":
        column_name = "source_end_balance"

    order_dir = request.POST['order[0][dir]']
    list  = []
    if order_dir == "asc":
        if column_name == "period_month":
            list = list_filter.annotate(int_period_month=RawSQL('CAST(period_month AS UNSIGNED)', params=[])).order_by('int_period_month')
        else:
            list = list_filter.order_by(column_name)
    elif order_dir == "desc":
        if column_name == "period_month":
            list = list_filter.annotate(int_period_month=RawSQL('CAST(period_month AS UNSIGNED)', params=[])).order_by('-int_period_month')
        else:
            list = list_filter.order_by('-' + column_name)

    # Create data list
    fsc_calendars = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, fiscal_year=year)
    array = []
    if currency_type == '1':
        for field in list:
            if fsc_calendars:
                perd = 12 if field['period_month'] in ['ADJ', 'CLS'] else int(field['period_month'])
                end_date = fsc_calendars.filter(period=perd).last().end_date
            else:
                end_date = field['period_date']
            source_net_change = field['source_net_change'] if field['source_net_change'] != 0 else 0
            source_end_balance = field['source_end_balance'] if field['source_end_balance'] != 0 else 0
            data = {"period_month": field['period_month'],
                    "period_date": end_date.strftime("%d-%m-%Y"),
                    "source_begin_balance": str(field['source_begin_balance']),
                    "source_net_change": intcomma("%.2f" % source_net_change),
                    "source_end_balance": intcomma("%.2f" % source_end_balance),
                    "account_id": str(account_id)}
            array.append(data)
    else:
        for field in list:
            if fsc_calendars:
                perd = 12 if field['period_month'] in ['ADJ', 'CLS'] else int(field['period_month'])
                end_date = fsc_calendars.filter(period=perd).last().end_date
            else:
                end_date = field['period_date']
            source_net_change = field['functional_net_change'] if field['functional_net_change'] != 0 else 0
            source_end_balance = field['functional_end_balance'] if field['functional_end_balance'] != 0 else 0
            data = {}
            data["period_month"] = str(field['period_month'])
            data["period_date"] = end_date.strftime("%d-%m-%Y")
            # Data will change follow functional
            data["source_begin_balance"] = str(field['functional_begin_balance']) if currency_type == '2' else 0
            data["source_net_change"] = intcomma("%.2f" % source_net_change)
            data["source_end_balance"] = intcomma("%.2f" % source_end_balance)
            data["account_id"] = str(account_id)
            array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
@permission_required('accounts.delete_account', login_url='/alert/')
def account_delete(request, account_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            account = Account.objects.get(pk=account_id)
            account.is_active = False
            transactions = Transaction.objects.filter(company_id=company_id, account=account, is_hidden=0)
            if not len(transactions):
                account.is_hidden = True
                messages.add_message(request, messages.INFO, 'Account is Deleted.', extra_tags='account_delete')
            else:
                messages.add_message(request, messages.ERROR, 'Account is Dactivated. To deleted account delete the transactions first.', extra_tags='account_delete')
            account.save()
            return HttpResponsePermanentRedirect(reverse('account_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_delete')
            logger.error(traceback.format_exc())


@login_required
@permission_required('accounts.add_accounttype', login_url='/alert/')
def account_type_add(request):
    account_type = AccountType()
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        company_list = Company.objects.filter(is_hidden=0, is_active=1, id=company_id)
    except ObjectDoesNotExist:
        company_list = None
    if request.method == 'POST':
        try:
            account_type.company_id = company_id
            account_type.name = request.POST.get('name')
            account_type.code = request.POST.get('code')
            account_type.category = request.POST.get('category')
            account_type.update_by = request.user.id
            account_type.is_hidden = False
            account_type.save()
            return HttpResponsePermanentRedirect(reverse('account_type_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_add')
            logger.error(traceback.format_exc())
    context = {
        'company_list': company_list,
        'category': REPORT_CATEGORY
    }

    return render(request, 'account-type-add.html', context)


@login_required
@permission_required('accounts.change_accounttype', login_url='/alert/')
def account_type_edit(request, account_type_id):
    account_type = AccountType.objects.get(pk=account_type_id)
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        company_list = Company.objects.filter(is_hidden=0, is_active=1,id=company_id)
    except ObjectDoesNotExist:
        company_list = None
    if request.method == 'POST':
        try:
            account_type.id = account_type_id
            account_type.name = request.POST.get('name')
            account_type.code = request.POST.get('code')
            account_type.company_id = company_id
            account_type.category = request.POST.get('category')
            account_type.update_by = request.user.id
            account_type.save()
            return HttpResponsePermanentRedirect(reverse('account_type_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_edit')
            logger.error(traceback.format_exc())
    account_type.update_date = account_type.update_date.strftime("%d-%m-%Y")
    context = {
        'account_type': account_type,
        'company_list': company_list,
        'category': REPORT_CATEGORY,
    }
    return render(request, 'account-type-edit.html', context)


@login_required
@permission_required('accounts.change_account', login_url='/alert/')
def account_type_delete(request, account_type_id):
    if request.method == 'POST':
        try:
            account_type = AccountType.objects.get(pk=account_type_id)
            account_type.is_hidden = True
            account_type.save()
            return HttpResponsePermanentRedirect(reverse('account_type_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_type_delete')
            logger.error(traceback.format_exc())


@login_required
def AccountType__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        category_dict = dict(REPORT_CATEGORY)
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = AccountType.objects.filter(is_hidden=0, company_id__in=[company_id, None])
        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(Q(name__icontains=search)
                                             | Q(code__icontains=search)
                                             | Q(company_id__name__icontains=search)
                                             | Q(update_date__contains=search))

        # All data
        records_filtered = list_filter.count()

        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "update_date"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "code"
        elif order_column == "3":
            column_name = "company_id__name"
        elif order_column == "4":
            column_name = "category"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": str(field.id),
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code,
                    "category": category_dict.get(field.category),
                    "company": field.company.name if field.company else ''}
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


@login_required
def bycode_account_json(request, acc_code, period, res):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        accounts = Account.objects.none()
        accounts_list = Account.objects.filter(
            company_id=company_id, is_active=True, is_hidden=False).order_by('account_segment', 'code')
        if int(res) == 2:
            accounts = accounts_list.filter(code__gt=acc_code).first()
        elif int(res) == 1:
            accounts = accounts_list.filter(code__gt=acc_code).last()

        if accounts:
            n_code = accounts.code
            acc_id_lt = accounts.id
        else:
            accounts_def = accounts_list.last()
            n_code = accounts_def.code
            acc_id_lt = accounts_def.id
        content = {
            "data": 0,
            "next_acc_code": n_code,
            "next_id_acc": acc_id_lt
        }
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')

    except:
        logger.error(traceback.format_exc())


@login_required
def detail_account_json(request, account_id, period, code):
    try:

        term = period.split('-')
        period_year = int(term[0])
        period_month = int(term[1])
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        accounts = Account.objects.filter(code=code, company_id=company_id, is_active=True, is_hidden=False).first()
        list_filter = AccountHistory.objects.filter(is_hidden=0, company_id=company_id,
                                                    account_id=accounts.id, period_month=period_month,
                                                    period_year=period_year)
        records_total = list_filter.count()

        records_filtered = list_filter.count()

        array = []
        for field in list_filter:
            data = {"code": field.source_currency.code,
                    "name": field.source_currency.name,
                    "account": field.account.id,
                    "account_code": field.account.code,
                    "source_end_balance": intcomma(field.source_end_balance),
                    "functional_end_balance": intcomma(field.functional_end_balance)}
            array.append(data)

        content = {
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')

    except:
        logger.error(traceback.format_exc())


@login_required
def Account__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Account.objects.filter(
            is_hidden=0, company_id=company_id).order_by('account_segment', 'code')

        balance_type_dict = dict(BALANCE_TYPE)
        account_type_dict = dict(ACCOUNT_TYPE)
        if search.lower() in "credit":
            stat = 2
        elif search.lower() in "debit":
            stat = 1
        else:
            stat = search

        if search.lower() in 'income statement':
            acco_type = 1
        elif search.lower() in 'balance sheet':
            acco_type = 2
        elif search.lower() in 'retained earning':
            acco_type = 3
        else:
            acco_type = search

        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(
                Q(name__icontains=search) | Q(code__icontains=search) | Q(account_group__name__icontains=search)
                | Q(company__name__icontains=search) | Q(update_date__icontains=search)
                | Q(balance_type__icontains=stat) | Q(account_type__icontains=acco_type)
            )

        # All data
        records_filtered = list_filter.count()
        order_column_dict = {'code': 1, 'name': 2, 'account_type': 3,
                         'balance_type': 4, 'account_group': 5}

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "update_date"
        elif order_column == str(order_column_dict['code']):
            column_name = "code"
        elif order_column == str(order_column_dict['name']):
            column_name = "name"
        elif order_column == str(order_column_dict['account_type']):
            column_name = "account_type"
        elif order_column == str(order_column_dict['balance_type']):
            column_name = "balance_type"
        elif order_column == str(order_column_dict['account_group']):
            column_name = "account_group"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
                list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
                list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        fsc_year = None
        fsc_month = None
        fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0,
                                start_date__lte=request.session['session_date'],
                                end_date__gte=request.session['session_date'])
        if fsc_calendar.exists():
            fsc_calendar = fsc_calendar.first()
            fsc_year = fsc_calendar.fiscal_year
            fsc_month = fsc_calendar.period

        array = []
        for field in list:
            current_balance = None
            revaluation_list = AccountCurrency.objects.filter(is_hidden=0, is_active=1, account_id=field.id)
            data = {}
            if fsc_month and fsc_year:
                this_account_history = AccountHistory.objects.filter(is_hidden=0, 
                                                                company_id=company_id, 
                                                                account_id=field.id,
                                                                period_year=fsc_year,
                                                                period_month=fsc_month,
                                                                source_currency_id=field.company.currency_id)
                if this_account_history.exists():
                    this_account_history = this_account_history.first()
                    current_balance = this_account_history.functional_end_balance
            data["id"] = field.id
            data["update_date"] = field.update_date.strftime(
                "%d-%m-%Y") if field.update_date else datetime.datetime.now().strftime("%d-%m-%Y")
            data["name"] = field.name
            data["code"] = str(field.code) if field.code is not None else ''
            data["account_type"] = account_type_dict.get(field.account_type)
            data["balance_type"] = balance_type_dict.get(field.balance_type)
            data["is_multicurrency"] = field.is_multicurrency
            if current_balance is not None:
                data["amount"] = intcomma("%.2f" % (current_balance))
            else:
                data["amount"] = intcomma("%.2f" % (field.debit_amount - field.credit_amount))
            data["account_group"] = field.account_group.name if field.account_group else ''
            data["Company_name"] = field.company.name if field.company else ''
            data["is_active"] = str(field.is_active)
            data["is_editable"] = str(field.is_editable)
            data["gl_revaluation"] = True if revaluation_list else False
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


@login_required
def DistributionCode__asJson(request, type):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = DistributionCode.objects.filter(is_hidden=False, is_active=1, company_id=company_id, type=type)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(company__name__icontains=search)
                | Q(gl_account__code__icontains=search)
                | Q(update_date__icontains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "update_date"
        elif order_column == "1":
            column_name = "code"
        elif order_column == "2":
            column_name = "name"
        elif order_column == "3":
            column_name = "gl_account"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code,
                    "company": field.company.name if field.company else '',
                    "gl_account": (str(field.gl_account.code) + " - " + str(
                        field.gl_account.name)) if field.gl_account else '',
                    "is_active": str(field.is_active), "account_id": field.gl_account_id if field.gl_account else '',
                    "account_name": field.gl_account.name if field.gl_account else '',
                    "account_code": field.gl_account.code if field.gl_account else ''}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,
            "BALANCE_TYPE": BALANCE_TYPE,
            "ACCOUNT_TYPE": ACCOUNT_TYPE
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except:
        logger.error(traceback.format_exc())


@login_required
@permission_required('accounts.add_account', login_url='/alert/')
def dist_code_add(request, type):
    distribution_code = DistributionCode()
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_list = Account.objects.filter(
        is_hidden=0, is_active=1, company_id=company_id).order_by('account_segment', 'code')
    if request.method == 'POST':
        try:
            if request.POST.get('sample-checkbox'):
                distribution_code.is_active = True
            else:
                distribution_code.is_active = False
            distribution_code.name = request.POST.get('name')
            distribution_code.code = request.POST.get('code')
            distribution_code.type = type
            distribution_code.company_id = company_id
            distribution_code.gl_account_id = request.POST.get('account')
            distribution_code.save()
            return HttpResponsePermanentRedirect(reverse('dist_code_list', kwargs={'type': type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_add')
            logger.error(traceback.format_exc())
    context = {
        "account_list": account_list,
        "type": type
    }
    return render(request, 'distribution-code-add.html', context)


@login_required
@permission_required('accounts.change_account', login_url='/alert/')
def dist_code_edit(request, dist_code_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    distribution_code = DistributionCode.objects.get(pk=dist_code_id)
    account_list = Account.objects.filter(
        is_hidden=0, is_active=1, company_id=company_id).order_by('account_segment', 'code')
    if request.method == 'POST':
        try:
            distribution_code.name = request.POST.get('name')
            distribution_code.code = request.POST.get('code')
            if request.POST.get('sample-checkbox'):
                distribution_code.is_active = True
            else:
                distribution_code.is_active = False
            distribution_code.company_id = company_id
            distribution_code.gl_account_id = request.POST.get('account')
            distribution_code.save()
            return HttpResponsePermanentRedirect(reverse('dist_code_list', kwargs={'type': distribution_code.type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_edit')
            logger.error(traceback.format_exc())
    distribution_code.update_date = distribution_code.update_date.strftime("%d-%m-%Y")
    context = {
        "distribution_code": distribution_code,
        "account_list": account_list,
        "type": distribution_code.type
    }
    return render(request, 'distribution-code-edit.html', context)


@login_required
@permission_required('accounts.delete_account', login_url='/alert/')
def dist_code_delete(request, dist_code_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            distribution_code = Account.objects.get(pk=dist_code_id)
            distribution_code.is_active = False
            distribution_code.is_hidden = True
            distribution_code.save()
            return HttpResponsePermanentRedirect(reverse('dist_code_list', kwargs={'type': type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_delete')
            logger.error(traceback.format_exc())


@login_required
def load_account_transaction_list(request, account_id=None, period=None):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_list = Account.objects.filter(
        is_hidden=False, company_id=company_id).order_by('account_segment', 'code')

    # load default account
    if len(account_list):
        if account_id == None:
            account_id = account_list.last().id

        if period:
            period = datetime.datetime.strptime(period, "%Y-%m-%d")
            period = period.strftime("%m-%Y")

        try:
            account = Account.objects.get(pk=account_id)
            currency_list = Currency.objects.filter(is_hidden=0)
            context = {
                'period': period,
                'account': account,
                'account_list': account_list,
                'source_code_list': SOURCE_TYPES,
                'source_currency_list': currency_list
            }
            return render(request, 'account-transaction.html', context)

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_delete')
            logger.error(traceback.format_exc())
    else:
        context = {}
        return render(request, 'account-transaction.html', context)


@login_required
def AccountTransaction__asJson(request):
    draw = request.POST['draw']
    start = request.POST['start']
    length = request.POST['length']
    search = request.POST['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_id = request.POST['account_id'] if 'account_id' in request.POST else 0
    if account_id == '':
        account_id = 0
    list_filter = Transaction.objects.filter(is_hidden=0, company_id=company_id,
                                             account_id=account_id,
                                             journal__journal_type=dict(TRANSACTION_TYPES)['GL'],
                                             journal__status__in=(int(STATUS_TYPE_DICT['Posted']),
                                                                  int(STATUS_TYPE_DICT['Reversed']),
                                                                  int(STATUS_TYPE_DICT['Auto Reverse Entry'])))

    # Exchange rate advance
    is_advance_filter = '0'
    if request.is_ajax():
        period_ending = request.POST['period_ending'] if 'period_ending' in request.POST else ''
        source_code = request.POST['source_code'] if 'source_code' in request.POST else '0'
        source_currency = request.POST['source_currency'] if 'source_currency' in request.POST else '0'
        is_advance_filter = request.POST['is_advance_filter'] if 'is_advance_filter' in request.POST else '0'
        if source_code != '0':
            list_filter = list_filter.filter(journal__source_type=source_code)
        if source_currency != '0':
            list_filter = list_filter.filter(currency_id=source_currency)
        if period_ending:
            array_period_ending = str(period_ending).split('-')
            last_day = datetime.date(int(array_period_ending[0]), int(array_period_ending[1]),
                                     calendar.monthrange(int(array_period_ending[0]), int(array_period_ending[1]))[1])
            if last_day:
                list_filter = list_filter.filter(journal__document_date__lte=last_day)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(journal__document_date__contains=search)
                                         | Q(journal__source_type__contains=search)
                                         | Q(reference__contains=search)
                                         | Q(description__contains=search)
                                         | Q(functional_amount__contains=search)
                                         | Q(total_amount__contains=search)
                                         | Q(functional_currency__code__contains=search)
                                         | Q(currency__code__contains=search)
                                         | Q(exchange_rate__contains=search)
                                         | Q(reference__contains=search)
                                         | Q(journal__batch__batch_no__contains=search)
                                         | Q(journal__code__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.POST['order[0][column]']
    column_name = ""
    if order_column == "0":
        column_name = "journal__document_date"
    if order_column == "1":
        column_name = "journal__document_date"
    if order_column == "2":
        column_name = "journal__document_date"
    elif order_column == "3":
        column_name = "journal__source_type"
    elif order_column == "4":
        column_name = "reference"
    elif order_column == "5":
        column_name = "description"
    elif order_column == "6":
        column_name = "functional_amount"
    elif order_column == "7":
        column_name = "total_amount"
    elif order_column == "8":
        column_name = "exchange_rate"
    elif order_column == "9":
        column_name = "journal__batch__batch_no"
    elif order_column == "10":
        column_name = "journal__code"

    order_dir = request.POST['order[0][dir]']
    list = []
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    elif order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    def check_decimal(number, currency_code):
        tmp = round_number(number, 2)
        return (get_decimal_place(currency_code) % tmp)

    # Create data list
    array = []
    for field in list:
        data = {}
        data["id"] = str(field.id)
        data["journal_id"] = str(field.journal_id)
        data["period_year"] = field.journal.document_date.strftime(
            "%Y") if field.journal and field.journal.document_date else ''
        data["period_month"] = field.journal.document_date.strftime(
            "%m") if field.journal and field.journal.document_date else ''
        data["document_date"] = field.journal.document_date.strftime(
            "%d-%m-%Y") if field.journal and field.journal.document_date else ''
        data["source_type"] = field.journal.source_type if field.journal else ''
        data["reference"] = field.reference if field.reference else ''
        data["description"] = str(field.description) if field.description else ''
        if field.is_credit_account:
            negative = '-'
        elif field.is_debit_account:
            negative = ' '
        data["functional_amount"] = negative + intcomma(check_decimal(field.functional_amount, field.functional_currency)) \
                                    + ' ' + intcomma(
            field.functional_currency.code) if field.functional_currency else ''
        data["source_amount"] = negative + intcomma(check_decimal(field.total_amount, field.currency)) \
                                + ' ' + intcomma(field.currency.code) if field.currency else ''
        data["exchange_rate"] = str(field.exchange_rate)
        data["batch_no"] = str(field.journal.batch.batch_no) if field.journal and field.journal.batch else ''
        data["entry_no"] = str(field.journal.code) if field.journal else ''
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
@permission_required('accounts.add_accountset', login_url='/alert/')
def account_set_add(request, account_set_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if request.method == 'POST':
        form = AccountSetForm(request, request.POST)
        try:
            if form.is_valid():
                account_set = form.save(commit=False)
                account_set.company_id = company_id
                account_set.type = account_set_type
                if int(company.currency_id) == int(request.POST.get('currency')):
                    account_set.revaluation_account_id = None
                    account_set.revaluation_unrealized_gain = None
                    account_set.revaluation_unrealized_loss = None
                    account_set.revaluation_realized_gain = None
                    account_set.revaluation_realized_loss = None
                    account_set.revaluation_rounding = None
                account_set.save()
                return HttpResponsePermanentRedirect(
                    reverse('account_set_list', kwargs={'account_set_type': account_set_type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_set_add')
            logger.error(traceback.format_exc())
    else:
        form = AccountSetForm(request)

    context = {
        'account_set_type': account_set_type,
        'company_currency_id': company.currency_id if company.currency else '',
        'form': form,
    }
    return render(request, 'account-set-form.html', context)


@login_required
@permission_required('accounts.change_accountset', login_url='/alert/')
def account_set_edit(request, account_set_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    account_set = AccountSet.objects.get(pk=account_set_id)
    company = Company.objects.get(pk=company_id)
    if request.method == 'POST':
        form = AccountSetForm(request, data=request.POST, instance=account_set)
        try:
            if form.is_valid():
                account_set = form.save(commit=False)
                if int(company.currency_id) == int(request.POST.get('currency')):
                    account_set.revaluation_account_id = None
                    account_set.revaluation_unrealized_gain = None
                    account_set.revaluation_unrealized_loss = None
                    account_set.revaluation_realized_gain = None
                    account_set.revaluation_realized_loss = None
                    account_set.revaluation_rounding = None
                account_set.save()
                return HttpResponsePermanentRedirect(
                    reverse('account_set_list', kwargs={'account_set_type': account_set.type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_set_edit')
            logger.error(traceback.format_exc())
    else:
        form = AccountSetForm(request, instance=account_set)
    account_set.update_date = account_set.update_date.strftime("%d-%m-%Y")
    context = {
        'account_set': account_set,
        'account_set_type': account_set.type,
        'company_currency_id': company.currency_id if company.currency else '',
        'form': form,
    }
    return render(request, 'account-set-form.html', context)


@login_required
@permission_required('accounts.delete_accountset', login_url='/alert/')
def account_set_delete(request, account_set_id):
    if request.method == 'POST':
        try:
            account_set = AccountSet.objects.get(pk=account_set_id)
            account_set.is_active = False
            account_set.is_hidden = True
            account_set.save()
            return HttpResponsePermanentRedirect(
                reverse('account_set_list', kwargs={'account_set_type': account_set.type}))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='account_set_delete')
            logger.error(traceback.format_exc())


@login_required
def AccountSet__asJson(request, account_set_type):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = AccountSet.objects.filter(is_hidden=0, company_id=company_id, is_active=True,
                                                type=account_set_type)

        company = Company.objects.get(pk=company_id)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(currency__code__icontains=search)
                | Q(control_account__code__icontains=search)
                | Q(revaluation_account__code__icontains=search)
                | Q(update_date__icontains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "update_date"
        elif order_column == "1":
            column_name = "code"
        elif order_column == "2":
            column_name = "name"
        elif order_column == "3":
            column_name = "control_account__code"
        elif order_column == "4":
            column_name = "currency__code"
        elif order_column == "5":
            column_name = "revaluation_account__code"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code,
                    "control_account": str(field.control_account.code) if field.control_account else '',
                    "revaluation_account": '<span class="label label-success label-mini" style="text-align:center">Yes</span>' if field.currency_id != company.currency_id else '',
                    "currency_code": str(field.currency.code) if field.currency else ''}
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
def load_account(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            if 'account_id' in request.POST and request.POST['account_id']:
                account_id = request.POST['account_id']
                account = Account.objects.get(pk=account_id)

                context = {
                    'name': account.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@login_required
@permission_required('accounts.add_account', login_url='/alert/')
def report_account_group(request, active_tab_index):
    success = 0
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        account = Account.objects.filter(
            is_hidden=False, is_active=True, company_id=company_id).order_by('account_segment', 'code')
        acct_grp_template = ReportGroup.objects.filter(company_id=company_id, is_hidden=False)
        acct_grp_list1 = acct_grp_template.filter(report_template_type='0')
        acct_grp_list2 = acct_grp_template.filter(report_template_type='1')

        if request.method == 'POST':
            try:
                redirect_url = None
                template_type = request.POST['template_type']
                filtered_acct_grp_template = acct_grp_template.filter(report_template_type=template_type)
                if filtered_acct_grp_template:
                    for acct_grp_item in filtered_acct_grp_template:
                        acct_grp_item.delete()

                if int(template_type) == 0:
                    acct_grp_template_new = ast.literal_eval(request.POST['template_pl'])
                    redirect_url = '/accounts/report_account_group/'+ REPORT_TEMPLATE_TYPES_DICT['Profit & Loss']+ '/'
                elif int(template_type) == 1:
                    acct_grp_template_new = ast.literal_eval(request.POST['template_bs'])
                    redirect_url = '/accounts/report_account_group/'+ REPORT_TEMPLATE_TYPES_DICT['Balance Sheet']+ '/'

                if len(acct_grp_template_new) > 0:
                    for acct_grp_list in acct_grp_template_new:
                        acct_grp_line = ReportGroup()
                        acct_grp_line.account_from_id = acct_grp_list['acc1']
                        acct_grp_line.account_to_id = acct_grp_list['acc2']
                        acct_grp_line.account_code_text = acct_grp_list['acc_code_text']
                        acct_grp_line.name = acct_grp_list['desc']
                        acct_grp_line.report_template_type = template_type
                        acct_grp_line.company_id = company_id
                        acct_grp_line.is_hidden = False
                        acct_grp_line.create_date = datetime.datetime.today()
                        acct_grp_line.save()
                        if acct_grp_line.id:
                            success += 1

                if success < len(acct_grp_template_new):
                    messages.error(request, MESSAGE_ERROR_2 + REFRESH_OR_GO_GET_SUPPORT)
                else:
                    messages.success(request, MESSAGE_SUCCESS)

                return redirect(redirect_url)

            except Exception as e:
                print(e)
                messages.add_message(request, messages.ERROR, e, extra_tags='report_account_group')
                logger.error(traceback.format_exc())

        context = {
            'account_list': account,
            'active_tab_index': active_tab_index,
            'acct_grp_list1': acct_grp_list1,
            'acct_grp_list2': acct_grp_list2
        }
        return render(request, 'report_acct_grp.html', context)

    except Exception as e:
        messages.add_message(request, messages.ERROR, e, extra_tags='report_account_group')
        logger.error(traceback.format_exc())

@login_required
def get_rpt_acc_grp(request):
    if request.method == 'POST':
        try:
            rpt_acc_grp_id = request.POST.get('rpt_acc_grp_id')
            rpt_acct_grp = ReportGroup.objects.get(pk=rpt_acc_grp_id)
            data = {"account_from_id": rpt_acct_grp.account_from.id,
                    "account_from_code": rpt_acct_grp.account_from.code,
                    "account_to_id": rpt_acct_grp.account_to.id if rpt_acct_grp.account_to else "",
                    "account_to_code": rpt_acct_grp.account_to.code if rpt_acct_grp.account_to else "",
                    "account_code_text": rpt_acct_grp.account_code_text,
                    "name": rpt_acct_grp.name}

            array = []
            array.append(data)
            json_content = json.dumps(array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
        except Exception as e:
            messages_error = "Load data failed"
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def del_rpt_acc_grp(request, rpt_acc_grp_id, template_type):
    try:
        rpt_acct_grp = ReportGroup.objects.get(pk=rpt_acc_grp_id)
        rpt_acct_grp.delete()
    except Exception as e:
        print(e)
        logging.error(traceback.format_exc())

    redirect_url = ''
    if int(template_type) == 0:
        redirect_url = '/accounts/report_account_group/'+ REPORT_TEMPLATE_TYPES_DICT['Profit & Loss']+ '/'
    elif int(template_type) == 1:
        redirect_url = '/accounts/report_account_group/'+ REPORT_TEMPLATE_TYPES_DICT['Balance Sheet']+ '/'

    return redirect(redirect_url)


@login_required
def revaluation_code_list(request):
    return render_to_response('revaluation-code-list.html', RequestContext(request))


@login_required
@permission_required('accounts.add_revaluationcode', login_url='/alert/')
def revaluation_code_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    if request.method == 'POST':
        form = RevaluationCodeForm(request, data=request.POST)

        try:
            if form.is_valid():
                revaluation_code = form.save(commit=False)
                revaluation_code.company_id = company_id
                revaluation_code.rate_type = 'SR'
                revaluation_code.save()

                return HttpResponsePermanentRedirect(reverse('revaluation_code_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='revaluation_code_add')
            logger.error(traceback.format_exc())

    else:
        form = RevaluationCodeForm(request)

    context = {
        'form_title': 'Add Revaluation Code',
        'form_action': reverse('revaluation_code_add'),
        'form': form,
        'account_list': Account.objects.filter(company_id=company_id, is_hidden=False).order_by('account_segment', 'code'),
    }
    return render(request, 'revaluation-code-form.html', context)


@login_required
@permission_required('accounts.change_revaluationcode', login_url='/alert/')
def revaluation_code_edit(request, revaluation_code_id):
    revaluation_code = RevaluationCode.objects.get(pk=revaluation_code_id)
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    if request.method == 'POST':
        form = RevaluationCodeForm(request, data=request.POST, instance=revaluation_code)

        try:
            if form.is_valid():
                revaluation_code = form.save(commit=False)
                revaluation_code.company_id = company_id
                revaluation_code.rate_type = 'SR'
                revaluation_code.save()

                return HttpResponseRedirect(reverse('revaluation_code_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='revaluation_code_edit')
            logger.error(traceback.format_exc())

    else:
        form = RevaluationCodeForm(request, instance=revaluation_code)

    context = {
        'form_title': 'Edit Revaluation Code',
        'form_action': reverse('revaluation_code_edit', kwargs={'revaluation_code_id':revaluation_code.id}),
        'form': form,
        'revaluation_code': revaluation_code,
        'user': request.user,
        'account_list': Account.objects.filter(company_id=company_id, is_hidden=False).order_by('account_segment', 'code'),
    }
    return render(request, 'revaluation-code-form.html', context)


@login_required
@permission_required('accounts.delete_revaluationcode', login_url='/alert/')
def revaluation_code_delete(request, revaluation_code_id):
    revaluation_code = RevaluationCode.objects.get(pk=revaluation_code_id)
    revaluation_code.is_hidden = 1
    revaluation_code.save()
    return HttpResponseRedirect(reverse('revaluation_code_list'))


@login_required
def RevaluationCode__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = RevaluationCode.objects.filter(is_hidden=False, company_id=company_id)
        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(Q(description__icontains=search)
                                             | Q(code__icontains=search)
                                             | Q(update_date__contains=search))

        # All data
        records_filtered = list_filter.count()

        # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        column_name = ""
        if order_column == "0":
            column_name = "update_date"
        elif order_column == "1":
            column_name = "code"
        elif order_column == "2":
            column_name = "description"
        elif order_column == "3":
            column_name = "rate_type"
        elif order_column == "4":
            column_name = "source_type"

        order_dir = request.GET['order[0][dir]']
        list = []
        if order_dir == "asc":
            list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
        elif order_dir == "desc":
            list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

        # Create data list
        array = []
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y") if field.update_date != None else field.create_date.strftime("%d-%m-%Y"),
                    "code": field.code,
                    "description": field.description,
                    "rate_type": field.rate_type,
                    "source_type": field.source_type}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception as e:
        print(e)
        logger.error(traceback.format_exc())
