import os
import calendar
import datetime
import json
import logging
import traceback
import mysql.connector
from mysql.connector import Error
from copy import deepcopy
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Value
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext
from django.conf import settings
import threading

from orders.models import Order
from companies.models import Company
from currencies.forms import ExchangeRateForm
from currencies.models import Currency, ExchangeRate
from utilities.constants import TRN_CODE_TYPE_DICT
from utilities.messages import UPDATE_EXCHANGE_RATE_FAILED, UPDATE_EXCHANGE_RATE_SUCCESS


# Create your views here.
@login_required
def load_list(request):
    return render_to_response('currency-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Global']}))


@login_required
def curr_list(request):
    return render_to_response('currency-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Sales Number File']}))


@login_required
@permission_required('currencies.add_currency', login_url='/alert/')
def currency_add(request, menu_type):
    currency = Currency()
    if request.method == 'POST':
        try:
            if request.POST.get('chkDecimal'):
                currency.is_decimal = True
            else:
                currency.is_decimal = False
            currency = Currency(
                name=request.POST.get('name'),
                code=request.POST.get('code'),
                symbol=request.POST.get('symbol'),
                is_decimal=currency.is_decimal,
                format=request.POST.get('format'),
                create_date=datetime.datetime.today(),
                update_date=datetime.datetime.today(),
                update_by=request.user.id,
                is_hidden=0,
            )
            currency.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='currency_add')

        return HttpResponsePermanentRedirect(reverse('curr_list'))
    return render_to_response('currency-add.html', RequestContext(request, {'menu_type': menu_type}))


@login_required
@permission_required('currencies.change_currency', login_url='/alert/')
def currency_edit(request, currency_id, menu_type):
    currency = Currency.objects.get(pk=currency_id)
    if request.method == 'POST':
        try:
            if request.POST.get('chkDecimal'):
                currency.is_decimal = True
            else:
                currency.is_decimal = False
            currency = Currency(
                id=currency_id,
                name=request.POST.get('name'),
                code=request.POST.get('code'),
                symbol=request.POST.get('symbol'),
                is_decimal=currency.is_decimal,
                format=request.POST.get('format'),
                update_date=datetime.datetime.today(),
                update_by=request.user.id,
                is_hidden=0,
            )
            currency.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='currency_edit')
        return HttpResponsePermanentRedirect(reverse('curr_list'))

    currency.update_date = currency.update_date.strftime("%d-%m-%Y")
    return render_to_response('currency-edit.html',
                              RequestContext(request, {'currency': currency, 'menu_type': menu_type}))


@login_required
@permission_required('currencies.delete_currency', login_url='/alert/')
def currency_delete(request, currency_id):
    if request.method == 'POST':
        try:
            currency = Currency.objects.get(pk=currency_id)
            currency.is_hidden = True
            currency.save()
            return HttpResponsePermanentRedirect(reverse('curr_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='currency_delete')


def update_order_exchangerate(exchangerate, company_id):
    try:
        order_list = Order.objects.filter(is_hidden=False, company_id=company_id, currency_id=exchangerate.from_currency_id,
                                          document_date__year=exchangerate.exchange_date.year, document_date__month=exchangerate.exchange_date.month)
        for order in order_list:
            if order.exchange_rate:
                order.exchange_rate = exchangerate.rate
            if order.supllier_exchange_rate:
                order.supllier_exchange_rate = exchangerate.rate
            if order.tax_exchange_rate:
                order.tax_exchange_rate = exchangerate.rate
            order.save()
    except Exception as e:
        print(e)


@login_required
@permission_required('currencies.add_exchangerate', login_url='/alert/')
def exchange_rate_add(request, menu_type):
    company__id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    companies = Company.objects.filter(is_hidden=False)
    curr_company = companies.get(pk=company__id)
    company_list = list(companies.exclude(id=company__id).values_list('id', flat=True))
    company_list.append(int(company__id))
    company_list.reverse()

    form = ExchangeRateForm(request.POST)

    if menu_type == TRN_CODE_TYPE_DICT['Sales Number File']:
        flag_string = 'SALES'
    elif menu_type == TRN_CODE_TYPE_DICT['Purchase Number File']:
        flag_string = 'PURCHASE'
    else:
        flag_string = 'ACCOUNTING'

    if request.method == 'POST':
        for company_id in company_list:
            company = companies.get(pk=company_id)
            is_exist = request.POST.get("is_exist")
            hdReplaceIsExist = request.POST.get("hdReplaceIsExist")
            hdNoReplace = request.POST.get("hdNoReplace")

            if is_exist == '0':
                from_currency = request.POST.get("from_currency")
                to_currency = request.POST.get("to_currency")
                date_ex = request.POST.get("exchange_date")
            else:
                from_currency = request.POST.get("hdReplaceFromCurrency")
                to_currency = request.POST.get("hdReplaceToCurrency")
                date_ex = request.POST.get("hdReplaceExchangeDate")

            array_data = str(date_ex).split('-')
            check_month = ExchangeRate.objects.filter(company_id=company_id, is_hidden=False,
                                                      from_currency_id=from_currency, to_currency_id=to_currency,
                                                      exchange_date__month=array_data[1], exchange_date__year=array_data[0],
                                                      flag=flag_string)
            # return for event blur
            if (check_month.__len__() == 0) and (is_exist == '0') and (hdNoReplace != '1'):
                if company_id == curr_company.id:
                    return HttpResponse(json.dumps(is_exist), content_type='application/json')
                else:
                    continue
            # check data exist or not
            if (check_month.__len__() > 0) and (is_exist == '0'):
                if company_id == curr_company.id:
                    messages.add_message(request, messages.ERROR, 'Rate already exist in month  ' + array_data[1],
                                         extra_tags='exchange_rate_add')
                    if is_exist == '0' and hdNoReplace == '0':
                        is_exist = '1'
                        return HttpResponse(json.dumps(is_exist), content_type='application/json')
                    else:
                        return render(request, 'exchange-rates.html',
                                      RequestContext(request, {'form': form, 'menu_type': menu_type}))
                else:
                    continue
            else:
                if hdReplaceIsExist == '1':
                    rate = request.POST.get("hdIsRate")
                    description = request.POST.get("hdIDescription")
                    for from_ex in check_month:
                        data_exchangerate = ExchangeRate()
                        data_exchangerate.id = from_ex.id
                        data_exchangerate.exchange_date = date_ex
                        data_exchangerate.from_currency_id = from_currency
                        data_exchangerate.company_id = company.id
                        data_exchangerate.to_currency_id = to_currency
                        data_exchangerate.description = description
                        data_exchangerate.rate = rate
                        data_exchangerate.update_by = request.user.id
                        data_exchangerate.is_hidden = 0
                        data_exchangerate.flag = flag_string
                        data_exchangerate.save()
                        # Update other companies
                        reflect_to_other_companies(data_exchangerate, company_id, 'add')
                        # Update order table
                        data_exchangerate = ExchangeRate.objects.get(pk=from_ex.id)
                        if data_exchangerate.to_currency.code == company.currency.code:
                            update_order_exchangerate(data_exchangerate, company_id)
                else:
                    try:
                        if company_id == curr_company.id:
                            exchangerate = form.save(commit=False)
                            exchangerate.company_id = company.id
                            exchangerate.create_date = datetime.datetime.today()
                            exchangerate.update_date = datetime.datetime.today()
                            exchangerate.update_by = request.user.id
                            exchangerate.is_hidden = 0
                            exchangerate.flag = flag_string
                            exchangerate.save()
                            new_exch_id = exchangerate.id
                        else:
                            if new_exch_id:
                                new_rate_entry = ExchangeRate.objects.get(pk=new_exch_id)
                                nexchangerate = deepcopy(new_rate_entry)
                                exchangerate.pk = None
                                exchangerate.company_id = company.id
                                exchangerate.save()

                        # Update other companies
                        reflect_to_other_companies(exchangerate, company_id, 'add')
                        # Update order table
                        if exchangerate.to_currency.code == company.currency.code:
                            update_order_exchangerate(exchangerate, company_id)
                    except ObjectDoesNotExist:
                        if company_id == curr_company.id:
                            messages_error = "Company and Staff information of Current User does not exist. " \
                                "\nPlease input Company and Staff of Current User!"
                            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
                        else:
                            continue
        return HttpResponsePermanentRedirect(reverse('exchange_rate_list', args=[menu_type]))
    else:
        form = ExchangeRateForm()
    return render(request, 'exchange-rates.html', {'form': form, 'menu_type': menu_type})


@login_required
@permission_required('currencies.change_exchangerate', login_url='/alert/')
def exchange_rate_edit(request, exchange_rate_id, menu_type):
    global from_currency_old
    global to_currency_old
    global rate_old
    global description_old
    global id_old
    global date_old

    company__id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    companies = Company.objects.filter(is_hidden=False)
    curr_company = companies.get(pk=company__id)
    company_list = list(companies.exclude(id=company__id).values_list('id', flat=True))
    company_list.append(int(company__id))
    company_list.reverse()

    if menu_type == TRN_CODE_TYPE_DICT['Sales Number File']:
        flag_string = 'SALES'
    elif menu_type == TRN_CODE_TYPE_DICT['Purchase Number File']:
        flag_string = 'PURCHASE'
    else:
        flag_string = 'ACCOUNTING'

    exchangerate = ExchangeRate.objects.get(pk=exchange_rate_id)
    # if request.method == 'GET':
    from_currency_old = exchangerate.from_currency_id
    to_currency_old = exchangerate.to_currency_id
    rate_old = exchangerate.rate
    description_old = exchangerate.description
    id_old = exchangerate.id
    date_old = exchangerate.exchange_date
    post = get_object_or_404(ExchangeRate, pk=exchange_rate_id)
    if request.method == 'POST':
        for company_id in company_list:
            company = Company.objects.get(pk=company_id)
            if company_id == curr_company.id:
                e_post = get_object_or_404(ExchangeRate, pk=exchange_rate_id)
            else:
                e_post = ExchangeRate.objects.filter(company_id=company_id, is_hidden=False, exchange_date=exchangerate.exchange_date,
                                                     rate=exchangerate.rate, from_currency_id=exchangerate.from_currency_id,
                                                     to_currency_id=exchangerate.to_currency_id).first()

            if e_post:
                id_old = e_post.id
                form = ExchangeRateForm(request.POST, instance=e_post)
                hdNoReplace = request.POST.get("hdNoReplace")
                is_exist = request.POST.get("is_exist")
                hdReplaceIsExist = request.POST.get("hdReplaceIsExist")

                if hdReplaceIsExist == '1':
                    from_currency_new = request.POST.get("hdReplaceFromCurrency")
                    to_currency_new = request.POST.get("hdReplaceToCurrency")
                    date_ex = request.POST.get("hdReplaceExchangeDate")
                    rate_new = request.POST.get("hdIsRate")
                    description_new = request.POST.get("hdIDescription")
                else:
                    from_currency_new = request.POST.get("from_currency")
                    to_currency_new = request.POST.get("to_currency")
                    date_ex = request.POST.get("exchange_date")
                    rate_new = request.POST.get("rate")
                    description_new = request.POST.get("description")
                id_old_after = exchange_rate_id

                if description_new is None:
                    description_new = ''
                if rate_new is None:
                    rate_new = ''

                array_data = str(date_ex).split('-')
                check_month = ExchangeRate.objects.filter(company_id=company_id, is_hidden=False,
                                                          exchange_date__month=array_data[1], exchange_date__year=array_data[0],
                                                          from_currency_id=from_currency_new, to_currency_id=to_currency_new,
                                                          flag=flag_string)
                if check_month:
                    id_new = check_month.last().id
                # check exist data or not data
                change = 1
                if (check_month.__len__() > 0) & (hdReplaceIsExist != '1'):
                    if ((from_currency_old != int(from_currency_new)) | (to_currency_old != int(to_currency_new))) \
                            & (id_old != id_new):
                        change = 1
                        is_exist = '1'
                    else:
                        if ((from_currency_old == int(from_currency_new))
                                & (to_currency_old == int(to_currency_new))
                                & (rate_old == Decimal(rate_new))
                                & (description_old == description_new)
                                & (id_old == id_new)
                                & (date_old == datetime.datetime.strptime(date_ex, "%Y-%m-%d").date())):
                            change = 1
                        else:
                            if (from_currency_old == int(from_currency_new)) \
                                    & (to_currency_old == int(to_currency_new)) \
                                    & (rate_old != Decimal(rate_new)) & (id_old == id_new) \
                                    & (date_old != datetime.datetime.strptime(date_ex, "%Y-%m-%d").date()):
                                change = 1
                            else:
                                if (from_currency_old == int(from_currency_new)) \
                                        & (to_currency_old == int(to_currency_new)) \
                                        & (description_old != description_new) \
                                        & (id_old == id_new):
                                    change = 1
                                else:
                                    if ((from_currency_old == int(from_currency_new))
                                            & (to_currency_old == int(to_currency_new))
                                            & (id_old != id_new)):
                                        change = 1
                                        is_exist = '1'
                                    else:
                                        if (from_currency_old == int(from_currency_new)) \
                                                & (to_currency_old == int(to_currency_new)) \
                                                & (date_old != datetime.datetime.strptime(date_ex, "%Y-%m-%d").date()) \
                                                & (id_old == id_new):
                                            change = 1
                                        else:
                                            if (from_currency_old == int(from_currency_new)) \
                                                    & (to_currency_old == int(to_currency_new)) \
                                                    & (date_old == datetime.datetime.strptime(date_ex, "%Y-%m-%d").date()) \
                                                    & (id_old == id_new):
                                                change = 1
                else:
                    change = 1

                if ((from_currency_old == int(from_currency_new)) & (to_currency_old == int(to_currency_new))
                        & (id_old == int(id_old_after))
                        & (date_old == datetime.datetime.strptime(date_ex, "%Y-%m-%d").date())
                        & (rate_old == Decimal(rate_new))
                        & (description_old == description_new)):
                    change = 1

                if ((from_currency_old == int(from_currency_new))
                        & (to_currency_old == int(to_currency_new))
                        & (id_old == int(id_old_after))
                        & (date_old == datetime.datetime.strptime(date_ex, "%Y-%m-%d").date())):
                    if (rate_old != Decimal(rate_new)) | (description_old == description_new):
                        change = 1

                # return for event blur
                if (hdReplaceIsExist != '1') & (hdNoReplace != '1'):
                    if company_id == curr_company.id:
                        return HttpResponse(json.dumps(is_exist), content_type='application/json')
                    else:
                        continue

                if change == 0:
                    # return for event blur
                    if (is_exist == '1') & (hdNoReplace == '0'):
                        return HttpResponse(json.dumps(is_exist), content_type='application/json')

                    if ((from_currency_old != int(from_currency_new))
                            | (to_currency_old != int(to_currency_new))
                            | (date_old != datetime.datetime.strptime(date_ex, "%Y-%m-%d").date())
                            | (description_old != description_new)):
                        messages.add_message(request, messages.ERROR,
                                             'Exchange Rate already exist in month  ' + array_data[1],
                                             extra_tags='exchange_rate_edit')
                    menu_type = str(menu_type)
                    if company_id == curr_company.id:
                        return render(request, 'exchange-rates.html',
                                      RequestContext(request, {'form': form, 'exchangerate': exchangerate, 'menu_type': menu_type}))
                    else:
                        continue
                if change == 1:
                    if hdReplaceIsExist == '1':
                        # update id_old
                        data_exchangerate = ExchangeRate()
                        data_exchangerate.id = id_old
                        data_exchangerate.exchange_date = date_ex
                        data_exchangerate.from_currency_id = from_currency_new
                        data_exchangerate.company_id = company.id
                        data_exchangerate.to_currency_id = to_currency_new
                        data_exchangerate.description = description_new
                        data_exchangerate.rate = rate_new
                        data_exchangerate.update_by = request.user.id
                        data_exchangerate.create_date = datetime.datetime.today()
                        data_exchangerate.update_date = datetime.datetime.today()
                        data_exchangerate.is_hidden = 0
                        data_exchangerate.flag = flag_string
                        data_exchangerate.save()
                        # Update other companies
                        reflect_to_other_companies(data_exchangerate, company_id, 'edit')
                        # Update order table
                        data_exchangerate = ExchangeRate.objects.get(pk=id_old)
                        if data_exchangerate.to_currency.code == company.currency.code:
                            update_order_exchangerate(data_exchangerate, company_id)
                        # delete new_id
                        exchangerate = ExchangeRate.objects.get(pk=id_new)
                        exchangerate.is_hidden = True
                        exchangerate.save()
                    else:
                        try:
                            # update id_old
                            data_exchangerate = ExchangeRate()
                            data_exchangerate.id = id_old
                            data_exchangerate.exchange_date = date_ex
                            data_exchangerate.from_currency_id = from_currency_new
                            data_exchangerate.company_id = company.id
                            data_exchangerate.to_currency_id = to_currency_new
                            data_exchangerate.description = description_new
                            data_exchangerate.rate = rate_new
                            data_exchangerate.update_by = request.user.id
                            data_exchangerate.create_date = datetime.datetime.today()
                            data_exchangerate.update_date = datetime.datetime.today()
                            data_exchangerate.is_hidden = 0
                            data_exchangerate.flag = flag_string
                            data_exchangerate.save()
                            # Update other companies
                            reflect_to_other_companies(data_exchangerate, company_id, 'edit')
                            # Update order table
                            data_exchangerate = ExchangeRate.objects.get(pk=id_old)
                            if data_exchangerate.to_currency.code == company.currency.code:
                                update_order_exchangerate(data_exchangerate, company_id)
                        except ObjectDoesNotExist:
                            if company_id == curr_company.id:
                                messages_error = "Company and Staff information of Current User does not exist. " \
                                    "\nPlease input Company and Staff of Current User!"
                                return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
                            else:
                                continue

        return HttpResponsePermanentRedirect(reverse('exchange_rate_list', args=[menu_type]))

    form = ExchangeRateForm(instance=post)

    exchangerate.update_date = exchangerate.update_date.strftime("%d-%m-%Y")

    return render(request, 'exchange-rates.html', {'form': form,
                                                   'exchangerate': exchangerate,
                                                   'menu_type': menu_type})


@login_required
@permission_required('currencies.delete_exchangerate', login_url='/alert/')
def exchange_rate_delete(request, exchange_rate_id, menu_type):
    if request.method == 'POST':
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            companies = Company.objects.filter(is_hidden=False)
            curr_company = companies.get(pk=company_id)
            company_list = list(companies.exclude(id=company_id).values_list('id', flat=True))
            exchangerate = ExchangeRate.objects.get(pk=exchange_rate_id)
            exchangerate.is_hidden = True
            exchangerate.save()
            # Update other companies
            reflect_to_other_companies(exchangerate, company_id, 'delete')
            for company__id in company_list:
                try:
                    exchangerate = ExchangeRate.objects.filter(company_id=company__id, exchange_date=exchangerate.exchange_date,
                                                               rate=exchangerate.rate, from_currency_id=exchangerate.from_currency_id,
                                                               to_currency_id=exchangerate.to_currency_id).first()
                    exchangerate.is_hidden = True
                    exchangerate.save()
                except:
                    continue
            return HttpResponsePermanentRedirect(reverse('exchange_rate_list', args=[menu_type]))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='exchange_rate_delete')


@login_required
def generate_exchange_copy(request, overwrite, menu_type):
    company__id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    companies = Company.objects.filter(is_hidden=False)
    curr_company = companies.get(pk=company__id)
    company_list = list(companies.exclude(id=company__id).values_list('id', flat=True))
    company_list.append(int(company__id))
    company_list.reverse()

    from_exchange_rate_list = []
    from_month = ''
    to_month = ''
    if menu_type == TRN_CODE_TYPE_DICT['Sales Number File']:
        flag_string = 'SALES'
    elif menu_type == TRN_CODE_TYPE_DICT['Purchase Number File']:
        flag_string = 'PURCHASE'
    else:
        flag_string = 'ACCOUNTING'
    if request.method == 'POST':
        for company_id in company_list:
            company = Company.objects.get(pk=company_id)
            if overwrite == '1':
                if request.POST.get('hdReplaceFromMonth'):
                    from_month = request.POST.get('hdReplaceFromMonth')
                else:
                    if company_id == curr_company.id:
                        messages.add_message(request, messages.ERROR,
                                             'Please select From Month that you want copy',
                                             extra_tags='exchange_copy')
                if request.POST.get('hdReplaceToMonth'):
                    to_month = request.POST.get('hdReplaceToMonth')
                else:
                    if company_id == curr_company.id:
                        messages.add_message(request, messages.ERROR,
                                             'Please select To Month that you want copy',
                                             extra_tags='exchange_copy')
                if request.POST.get('hdReplaceExchangeList'):
                    hdExchangeList = request.POST.get('hdReplaceExchangeList')
            if overwrite == '0':
                if request.POST.get('hdFromMonth'):
                    from_month = request.POST.get('hdFromMonth')
                else:
                    if company_id == curr_company.id:
                        messages.add_message(request, messages.ERROR,
                                             'Please select From Month that you want copy',
                                             extra_tags='exchange_copy')
                if request.POST.get('hdToMonth'):
                    to_month = request.POST.get('hdToMonth')
                else:
                    if company_id == curr_company.id:
                        messages.add_message(request, messages.ERROR,
                                             'Please select To Month that you want copy',
                                             extra_tags='exchange_copy')
                if request.POST.get('hdExchangeList'):
                    hdExchangeList = request.POST.get('hdExchangeList')

            if hdExchangeList:
                hdExchangeList = hdExchangeList.split(',')
                if from_month and to_month:
                    array_to_month = str(to_month).split('-')
                    first_day = datetime.date(int(array_to_month[1]), int(array_to_month[0]), 1)
                    from_exchange_rate_list = ExchangeRate.objects.filter(is_hidden=0, company_id=curr_company.id,
                                                                          id__in=hdExchangeList, flag=flag_string)
                    if len(from_exchange_rate_list) == 0:
                        if company_id == curr_company.id:
                            messages.add_message(request, messages.ERROR,
                                                 'Exchange Rate is no exist in month ' + from_month + ". Please select other month",
                                                 extra_tags='exchange_copy')
                    else:
                        to_exchange_rate_list = ExchangeRate.objects.filter(is_hidden=0, company_id=company_id,
                                                                            exchange_date__month=array_to_month[0],
                                                                            exchange_date__year=array_to_month[1],
                                                                            flag=flag_string)
                        exist_flag = False
                        if overwrite == '0':
                            for from_ex in from_exchange_rate_list:
                                for to_ex in to_exchange_rate_list:
                                    if (from_ex.from_currency_id == to_ex.from_currency_id and
                                            from_ex.to_currency_id == to_ex.to_currency_id):
                                        from_ex.is_exist = '1'
                                        exist_flag = True
                                        break
                            if exist_flag:
                                if company_id == curr_company.id:
                                    messages.add_message(request, messages.ERROR,
                                                         'Exchange Rate is exist in month of ' + to_month +
                                                         '. Please confirm if you want to overwrite the data.',
                                                         extra_tags='exchange_copy')
                        if not exist_flag:
                            # check overwrite data
                            if overwrite == '1':
                                for from_ex in from_exchange_rate_list:
                                    for to_ex in to_exchange_rate_list:
                                        if (from_ex.from_currency_id == to_ex.from_currency_id and
                                                from_ex.to_currency_id == to_ex.to_currency_id):
                                            exist_flag = True
                                            break

                                    if exist_flag:
                                        data_exchangerate = ExchangeRate()
                                        data_exchangerate.id = to_ex.id
                                        data_exchangerate.exchange_date = first_day
                                        data_exchangerate.from_currency_id = from_ex.from_currency_id
                                        data_exchangerate.company_id = company_id
                                        data_exchangerate.to_currency_id = from_ex.to_currency_id
                                        data_exchangerate.rate = from_ex.rate
                                        data_exchangerate.is_hidden = 0
                                        data_exchangerate.flag = flag_string
                                        data_exchangerate.save()
                                        exist_flag = False
                                        # Update other companies
                                        reflect_to_other_companies(data_exchangerate, company_id, 'edit')
                                        # Update order table
                                        data_exchangerate = ExchangeRate.objects.get(pk=to_ex.id)
                                        if data_exchangerate.to_currency.code == company.currency.code:
                                            update_order_exchangerate(data_exchangerate, company_id)
                                    else:
                                        data_exchangerate = ExchangeRate()
                                        data_exchangerate.exchange_date = first_day
                                        data_exchangerate.from_currency_id = from_ex.from_currency_id
                                        data_exchangerate.company_id = company_id
                                        data_exchangerate.to_currency_id = from_ex.to_currency_id
                                        data_exchangerate.rate = from_ex.rate
                                        data_exchangerate.is_hidden = 0
                                        data_exchangerate.flag = flag_string
                                        data_exchangerate.save()
                                        # Update other companies
                                        reflect_to_other_companies(data_exchangerate, company_id, 'add')
                                        # Update order table
                                        if data_exchangerate.to_currency.code == company.currency.code:
                                            update_order_exchangerate(data_exchangerate, company_id)
                                # return HttpResponsePermanentRedirect(reverse('exchange_rate_list', args=[int(menu_type)]))
                            else:
                                with transaction.atomic():
                                    for from_ex in from_exchange_rate_list:
                                        data_exchangerate = ExchangeRate()
                                        data_exchangerate.exchange_date = first_day
                                        data_exchangerate.from_currency_id = from_ex.from_currency_id
                                        data_exchangerate.company_id = company_id
                                        data_exchangerate.to_currency_id = from_ex.to_currency_id
                                        data_exchangerate.rate = from_ex.rate
                                        data_exchangerate.is_hidden = 0
                                        data_exchangerate.flag = flag_string
                                        data_exchangerate.save()
                                        # Update other companies
                                        reflect_to_other_companies(data_exchangerate, company_id, 'add')
                                        # Update order table
                                        if data_exchangerate.to_currency.code == company.currency.code:
                                            update_order_exchangerate(data_exchangerate, company_id)
            else:
                if company_id == curr_company.id:
                    messages.add_message(request, messages.ERROR,
                                         'Exchange Rate is no exist in month ' + from_month + ". Please select other month",
                                         extra_tags='exchange_copy')
        return HttpResponsePermanentRedirect(reverse('exchange_rate_list', args=[int(menu_type)]))

    return render_to_response('exchange_copy.html',
                              RequestContext(request, {'exchangerate_list': from_exchange_rate_list,
                                                       'from_month': from_month,
                                                       'to_month': to_month
                                                       }))


@login_required
def load_exchange_copy(request, overwrite, menu_type):
    try:
        exchangerate_list = []
        from_month = datetime.date.today().strftime("%m-%Y")
        to_month = datetime.date.today().strftime("%m-%Y")
        return render_to_response('exchange_copy.html',
                                  RequestContext(request, {'exchangerate_list': exchangerate_list,
                                                           'from_month': from_month,
                                                           'to_month': to_month,
                                                           'menu_type': menu_type}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def search_exchange_copy(request, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    from_exchange_rate_list = []
    from_month = ''
    to_month = ''
    if menu_type == TRN_CODE_TYPE_DICT['Sales Number File']:
        flag_string = 'SALES'
    elif menu_type == TRN_CODE_TYPE_DICT['Purchase Number File']:
        flag_string = 'PURCHASE'
    else:
        flag_string = 'ACCOUNTING'
    if request.method == 'POST':
        if request.POST.get('from_month'):
            from_month = request.POST.get('from_month')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Please select From Month that you want copy',
                                 extra_tags='exchange_copy')
        if request.POST.get('to_month'):
            to_month = request.POST.get('to_month')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Please select To Month that you want copy',
                                 extra_tags='exchange_copy')
        if from_month and to_month:
            array_from_month = str(from_month).split('-')
            array_to_month = str(to_month).split('-')

            from_exchange_rate_list = ExchangeRate.objects.filter(is_hidden=0, company_id=company_id,
                                                                  exchange_date__month=array_from_month[0],
                                                                  exchange_date__year=array_from_month[1],
                                                                  flag=flag_string) \
                .annotate(ex_rate_date=Value(str('{:02}'.format(1) + '-' + to_month.strip()),
                                             output_field=models.CharField())) \
                .annotate(is_exist=Value('0', output_field=models.CharField())) \
                .annotate(line_number=Value('0', output_field=models.CharField()))
            if len(from_exchange_rate_list) == 0:
                messages.add_message(request, messages.ERROR,
                                     'Exchange Rate is not exist in month ' + from_month + ". Please select other month",
                                     extra_tags='exchange_copy')
            else:
                to_exchange_rate_list = ExchangeRate.objects.filter(is_hidden=0, company_id=company_id,
                                                                    exchange_date__month=array_to_month[0],
                                                                    exchange_date__year=array_to_month[1],
                                                                    flag=flag_string)
                exist_flag = False
                for from_ex in from_exchange_rate_list:
                    for to_ex in to_exchange_rate_list:
                        if (from_ex.from_currency_id == to_ex.from_currency_id and
                                from_ex.to_currency_id == to_ex.to_currency_id):
                            from_ex.is_exist = '1'
                            exist_flag = True
                            break
                if exist_flag:
                    messages.add_message(request, messages.ERROR,
                                         'Exchange Rate is exist in month of ' + to_month +
                                         '. Please confirm if you want to overwrite the data.',
                                         extra_tags='exchange_copy')

    return render_to_response('exchange_copy.html',
                              RequestContext(request, {'exchangerate_list': from_exchange_rate_list,
                                                       'from_month': from_month,
                                                       'to_month': to_month,
                                                       'menu_type': menu_type}))


@login_required
def exchange_rate_list(request, menu_type):
    session_date = request.session['session_date']
    session_date = session_date.strftime("%m-%Y")
    currency_list = Currency.objects.filter(is_hidden=0).order_by('code').values_list('code', 'name')
    return render_to_response('exchange-rates-list.html', RequestContext(request,
                                                                         {'menu_type': menu_type,
                                                                          'session_date': session_date,
                                                                          'currency_list': currency_list}))


@login_required
def get_exchange_by_rate_date(request, is_req, id_req, rate_date, exchrate_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    from_curr_id = int(id_req)
    if is_req == '1':
        to_curr = company.currency.id
    else:
        to_curr = int(is_req)
    try:
        from_code = Currency.objects.get(pk=from_curr_id).code
        from_curr = Currency.objects.get(pk=from_curr_id)
        to_code = Currency.objects.get(pk=to_curr).code
    except:
        from_code = ''
        to_code = ''
        from_curr = None
    array = []
    if from_curr_id == to_curr:
        curr_obj = {
            "id": '',
            "rate": '1.0000000',
            "exchange_date": rate_date,
            "company_currency": company.currency.code,
            'is_decimal': 1 if from_curr and from_curr.is_decimal else 0,
            'from_code': from_code,
            'to_code': to_code
        }
    elif from_curr and from_curr == company.currency:
        curr_obj = {
            "id": '',
            "rate": '1.0000000',
            "exchange_date": rate_date,
            "company_currency": company.currency.code,
            'is_decimal': 1 if from_curr and from_curr.is_decimal else 0,
            'from_code': from_code,
            'to_code': to_code
        }
    else:
        curr_obj = {
            "id": '',
            "rate": '0000000',
            "exchange_date": rate_date,
            "company_currency": company.currency.code,
            'is_decimal': 1,
            'from_code': from_code,
            'to_code': to_code
        }
    if exchrate_type == '1':
        flag_string = 'SALES'
    elif exchrate_type == '2':
        flag_string = 'PURCHASE'
    else:
        flag_string = 'ACCOUNTING'
    try:
        month = rate_date.split('-')[1]
        year = rate_date.split('-')[0]
        
        Exchange = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                            from_currency_id=from_curr_id, to_currency_id=to_curr,
                                            exchange_date__year=year, exchange_date__month=month,
                                            flag=flag_string).first()
        if Exchange:
            curr_obj["id"] = str(Exchange.id)
            curr_obj["rate"] = str(Exchange.rate)
            curr_obj["exchange_date"] = Exchange.exchange_date.strftime("%Y-%m-%d")
            curr_obj["is_decimal"] = 1 if Exchange.from_currency.is_decimal else 0
        # else:
        #     Exchange_last = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
        #                                                 from_currency_id=from_curr_id, to_currency_id=to_curr,
        #                                                 exchange_date__lte=rate_date,
        #                                                 flag=flag_string).last()
        #     if Exchange_last:
        #         curr_obj["id"] = str(Exchange_last.id)
        #         curr_obj["rate"] = str(Exchange_last.rate)
        #         curr_obj["exchange_date"] = Exchange_last.exchange_date.strftime("%Y-%m-%d")
        #         curr_obj["is_decimal"] = 1 if Exchange_last.from_currency.is_decimal else 0

    except ObjectDoesNotExist:
        pass

    array.append(curr_obj)
    json_content = json.dumps(array, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def get_exchange_rate(request, exchrate_type):
    session_date = request.session['session_date']
    array = []
    if exchrate_type == '1':
        flag_string = 'SALES'
    elif exchrate_type == '2':
        flag_string = 'PURCHASE'
    else:
        flag_string = 'ACCOUNTING'
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        doc_date = None
        if request.POST.get('doc_date'):
            doc_date = datetime.datetime.strptime(request.POST.get('doc_date'), "%Y-%m-%d")
        from_curr_id = int(request.POST.get('from_currency_id'))
        to_curr_id = int(request.POST.get('to_currency_id'))
        curr_obj = {
            "id": None,
            "rate": 1,
            "exchange_date": doc_date.strftime("%d-%m-%Y") if doc_date else \
                session_date.strftime("%d-%m-%Y") if session_date else datetime.datetime.now().strftime("%d-%m-%Y")
        }
        split_date = curr_obj["exchange_date"].split('-')
        curr_obj["exchange_date"] = '01-' + split_date[1] + '-' + split_date[2]
        if from_curr_id != to_curr_id:
            if doc_date:
                Exchange = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                       from_currency_id=from_curr_id, to_currency_id=to_curr_id,
                                                       exchange_date__month=doc_date.month, exchange_date__year=doc_date.year,
                                                       flag=flag_string).order_by('-exchange_date').first()
            elif session_date:
                Exchange = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                       from_currency_id=from_curr_id, to_currency_id=to_curr_id,
                                                       exchange_date__month=session_date.month, exchange_date__year=session_date.year,
                                                       flag=flag_string).order_by('-exchange_date').first()
                if not Exchange:
                    Exchange = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                           from_currency_id=from_curr_id, to_currency_id=to_curr_id,
                                                           flag=flag_string).order_by('-exchange_date').first()
            else:
                Exchange = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                       from_currency_id=from_curr_id, to_currency_id=to_curr_id,
                                                       flag=flag_string).order_by('-exchange_date').first()
            if Exchange:
                curr_obj["id"] = str(Exchange.id)
                curr_obj["rate"] = str(Exchange.rate)
                curr_obj["exchange_date"] = Exchange.exchange_date.strftime("%d-%m-%Y")
                split_date = curr_obj["exchange_date"].split('-')
                curr_obj["exchange_date"] = '01-' + split_date[1] + '-' + split_date[2]
        array.append(curr_obj)
        json_content = json.dumps(array, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except ObjectDoesNotExist:
        array.append(curr_obj)
        json_content = json.dumps(array, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')


@login_required
def ExchangeRate__asJson(request):
    draw = request.POST['draw']
    start = request.POST['start']
    length = request.POST['length']
    search = request.POST['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = ExchangeRate.objects.filter(is_hidden=0, company_id=company_id)

    # Exchange rate advance
    is_advance_filter = '0'
    if request.is_ajax():
        from_currency = request.POST['from_currency'] if 'from_currency' in request.POST else ''
        to_currency = request.POST['to_currency'] if 'to_currency' in request.POST else ''
        exchange_date = request.POST['exchange_date'] if 'exchange_date' in request.POST else ''
        is_advance_filter = request.POST['is_advance_filter'] if 'is_advance_filter' in request.POST else '0'
        exch_rate_type = request.POST['exch_rate_type'] if 'exch_rate_type' in request.POST else ''
        if exch_rate_type == '1':
            flag_string = 'SALES'
        elif exch_rate_type == '2':
            flag_string = 'PURCHASE'
        else:
            flag_string = 'ACCOUNTING'
        list_filter = list_filter.filter(flag=flag_string)

    # records_total = list_filter.count()

    # if is_advance_filter == '1':
    if from_currency:
        list_filter = list_filter.filter(from_currency__code=from_currency)
    if to_currency:
        list_filter = list_filter.filter(to_currency__code=to_currency)
    # if exchange_date:
    #     # Filter data from first date to last date of the month
    #     array_exchange_date = str(exchange_date).split('-')
    #     first_day = datetime.date(int(array_exchange_date[0]), int(array_exchange_date[1]), 1)
    #     last_day = datetime.date(int(array_exchange_date[0]), int(array_exchange_date[1]),
    #                                 calendar.monthrange(int(array_exchange_date[0]), int(array_exchange_date[1]))[1])
    #     if first_day:
    #         list_filter = list_filter.filter(exchange_date__gte=first_day)
    #     if last_day:
    #         list_filter = list_filter.filter(exchange_date__lte=last_day)

    records_total = list_filter.count()
    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(from_currency__name__icontains=search) | Q(to_currency__name__icontains=search) | Q(
                exchange_date__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.POST['order[0][column]']
    if order_column == "0":
        column_name = "from_currency"
    elif order_column == "1":
        column_name = "to_currency"
    elif order_column == "2":
        column_name = "rate"
    elif order_column == "3":
        column_name = "exchange_date"
    order_dir = request.POST['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "from_currency": field.from_currency.name,
                "to_currency": field.to_currency.name,
                "rate": str(field.rate),
                "exchange_date": field.exchange_date.strftime("%d-%m-%Y")}
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
def Currencies__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Currency.objects.filter(is_hidden=0)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(name__icontains=search) | Q(code__icontains=search) | Q(
                symbol__icontains=search) | Q(format__icontains=search) | Q(update_date__icontains=search)
        )

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "1":
        column_name = "code"
    elif order_column == "3":
        column_name = "symbol"
    elif order_column == "4":
        column_name = "format"
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
                "symbol": field.symbol}
        if (field.format == 'None') | (field.format is None):
            field.format = ""
        # data["format"] = field.format
        # data["is_decimal"] = str(field.is_decimal)
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


def send_to_sp(request, exchrate_id, exchrate_type):
    try:
        flag_string = ('PURCHASE', 'SALES')[exchrate_type == '1']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        ExchRate = ExchangeRate.objects.get(pk=exchrate_id)
        rate_date_arr = str(ExchRate.exchange_date).split('-')
        existing_exchange_rate = ExchangeRate.objects.filter(is_hidden=0, company_id=company_id,
                                                             exchange_date__month=rate_date_arr[1],
                                                             exchange_date__year=rate_date_arr[0],
                                                             from_currency_id=ExchRate.from_currency_id,
                                                             to_currency_id=ExchRate.to_currency_id,
                                                             flag=flag_string).first()

        if existing_exchange_rate:
            existing_exchange_rate.rate = ExchRate.rate
            existing_exchange_rate.exchange_date = ExchRate.exchange_date
            existing_exchange_rate.update_by = request.user.id
            existing_exchange_rate.save()
        else:
            new_exchange_rate = deepcopy(ExchRate)
            new_exchange_rate.pk = None
            new_exchange_rate.description = 'Copied from Accounting at ' + datetime.datetime.now().strftime("%Y-%m-%d")
            new_exchange_rate.create_date = datetime.datetime.now()
            new_exchange_rate.flag = flag_string
            new_exchange_rate.save()

        messages.info(request, UPDATE_EXCHANGE_RATE_SUCCESS)

    except Exception:
        logging.error(traceback.format_exc())
        messages.error(request, UPDATE_EXCHANGE_RATE_FAILED)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def start_copying(data, login_company_id, operation):
    db_list = read_settings()
    for setting in db_list:
        db = setting[0]
        user = setting[1]
        password = setting[2]
        host = setting[3]
        company_id = None
        company_name = None
        try:
            connection = mysql.connector.connect(host=host,
                                                 database=db,
                                                 user=user,
                                                 password=password)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT * FROM companies_company WHERE is_hidden=0 LIMIT 1"
                cursor.execute(sql)
                result = cursor.fetchall()
                for x in result:
                    company_id = x[0]
                    company_name = x[1]

                if company_id:
                    # print(company_id, company_name, setting)
                    # if operation == 'add':
                    #     sql = select_sql(company_id, data)
                    #     cursor.execute(sql)
                    #     result = cursor.fetchall()
                    #     if cursor.rowcount > 0: # if exist then update
                    #         sql = update_sql(company_id, data)
                    #         cursor.execute(sql)
                    #         connection.commit()
                    #         print(cursor.rowcount, "record updated.")
                    #     else: # else insert
                    #         sql, val = insert_sql(company_id, data)
                    #         cursor.execute(sql, val)
                    #         connection.commit()
                    #     print(cursor.rowcount, "record inserted.")
                    if operation == 'add' or operation == 'edit':
                        sql, val = update_sql(company_id, data)
                        cursor.execute(sql, val)
                        connection.commit()
                        if cursor.rowcount == 0:  # if not exist then insert
                            sql, val = insert_sql(company_id, data)
                            cursor.execute(sql, val)
                            connection.commit()
                            # print(cursor.rowcount, "record inserted.")
                        # else:
                            # print(cursor.rowcount, "record updated.")
                            
                    elif operation == 'delete':
                        sql, val = delete_sql(company_id, data)
                        cursor.execute(sql, val)
                        connection.commit()
                        # print(cursor.rowcount, "record deleted.")

        except mysql.connector.Error as error:
            print(error)
            connection = None
        except Exception as e:
            print(e)
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    return True


def reflect_to_other_companies(data, login_company_id, operation):
    start_copying_t = threading.Thread(name='start_copying', target=start_copying, args=(data, login_company_id, operation, ), daemon=True)
    start_copying_t.start()

    return True


def select_sql(company_id, data):
    sql = "SELECT * FROM currencies_exchangerate WHERE \
                company_id=" + str(company_id) + " AND \
                exchange_date='" + str(data.exchange_date) + "' AND \
                from_currency_id=" + str(data.from_currency_id) + " AND \
                to_currency_id=" + str(data.to_currency_id)
    return sql


def insert_sql(company_id, data):
    sql = "INSERT INTO currencies_exchangerate \
            (company_id, exchange_date, from_currency_id, to_currency_id, rate, is_hidden, flag, \
                create_date, update_date, description, apply_flag) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (company_id, data.exchange_date, data.from_currency_id, data.to_currency_id, data.rate, 0, data.flag,
           datetime.datetime.now(), datetime.datetime.now(), data.description, 0)

    return sql, val


def update_sql(company_id, data):
    sql = """ UPDATE currencies_exchangerate SET rate = %s, update_date = %s, apply_flag = %s WHERE
                company_id = %s AND
                exchange_date = %s AND
                from_currency_id= %s AND
                to_currency_id= %s """
    val = (float(data.rate), datetime.datetime.now().strftime("%Y-%m-%d"), 0, company_id,
           data.exchange_date, int(data.from_currency_id), int(data.to_currency_id))
    return sql, val


def delete_sql(company_id, data):
    sql = """ UPDATE currencies_exchangerate SET is_hidden = %s, update_date = %s WHERE
                company_id = %s AND
                exchange_date = %s AND
                from_currency_id= %s AND
                to_currency_id= %s """
    val = (1, datetime.datetime.now().strftime("%Y-%m-%d"), company_id, data.exchange_date, int(data.from_currency_id), int(data.to_currency_id))
    return sql, val


def read_settings():
    db_list = []
    own_setting_file = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[1]
    split_arr = own_setting_file.split('_')
    setting_pattern = split_arr[0] + '_' + split_arr[1] + '_'

    path = os.path.join(settings.BASE_DIR, 'ikari/')

    for f_name in os.listdir(path):
        if f_name.startswith(setting_pattern) and f_name.endswith('.py'):
            with open(os.path.join(path, f_name), 'r') as f:
                db = user = password = host = ''
                for num, line in enumerate(f, 1):
                    if "        'NAME':" in line:
                        db = line.split("'")[3]
                    if "        'USER':" in line:
                        user = line.split("'")[3]
                    if "        'PASSWORD':" in line:
                        password = line.split("'")[3]
                    if "        'HOST':" in line:
                        host = line.split("'")[3]
                        break
                db_list.append([db, user, password, host])

    return db_list


def tax_reporting_exch_rate(request, from_currency, doc_date):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    from_currency = int(from_currency)
    to_currency = 9
    try:
        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                    from_currency_id=from_currency,
                                                    to_currency_id=to_currency,
                                                    exchange_date__lte=doc_date,
                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
    except:
        exchange_rate = Decimal('1.0000000')

    content = {
        "exchange_rate": float(exchange_rate)
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')
