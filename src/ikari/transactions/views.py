import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext

from accounting.forms import PaymentCodeForm
from accounting.models import PaymentCode
from transactions.models import Transaction
from utilities.constants import TRN_CODE_TYPE_DICT


# Create your views here.@login_required
def trans_method_list(request):
    return render_to_response('trans-method-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Global']}))


@login_required
def trans_mode(request):
    return render_to_response('trans-method-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Sales Number File']}))


@login_required
@permission_required('transactions.add_transactionmethod', login_url='/alert/')
def trans_method_add(request, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        form = PaymentCodeForm(request.POST)
        if form.is_valid():
            try:
                my_trans_method = form.save(commit=False)
                my_trans_method.company_id = company_id
                my_trans_method.create_date = datetime.datetime.today()
                my_trans_method.update_date = datetime.datetime.today()
                my_trans_method.update_by = request.user.id
                my_trans_method.is_hidden = 0
                my_trans_method.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='trans_method_add')
            return HttpResponsePermanentRedirect(reverse('trans_method_list'))
        else:
            form = PaymentCodeForm(request.POST)
    else:
        form = PaymentCodeForm()
    return render(request, 'trans-method-form.html', {'form': form, 'menu_type': menu_type})


@login_required
@permission_required('transactions.change_transactionmethod', login_url='/alert/')
def trans_method_edit(request, trans_method_id, menu_type):
    my_trans_method = get_object_or_404(PaymentCode, pk=trans_method_id)
    if request.method == 'POST':
        form = PaymentCodeForm(request.POST, instance=my_trans_method)
        if form.is_valid():
            try:
                my_trans_method = form.save(commit=False)
                my_trans_method.update_date = datetime.datetime.today()
                my_trans_method.update_by = request.user.id
                my_trans_method.is_hidden = 0
                my_trans_method.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='trans_method_edit')
            return HttpResponsePermanentRedirect(reverse('trans_method_list'))
    my_trans_method.update_date = my_trans_method.update_date.strftime("%d-%m-%Y")    
    form = PaymentCodeForm(instance=my_trans_method)
    return render(request, 'trans-method-form.html',
                  {'form': form, 'trans_method': my_trans_method, 'menu_type': menu_type})


@login_required
@permission_required('transactions.delete_transactionmethod', login_url='/alert/')
def trans_method_delete(request, trans_method_id):
    if request.method == 'POST':
        try:
            my_trans_method = PaymentCode.objects.get(pk=trans_method_id)
            my_trans_method.is_hidden = True
            my_trans_method.save()
            return HttpResponsePermanentRedirect(reverse('trans_method_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='trans_method_delete')


@login_required
def TransMethod__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = PaymentCode.objects.filter(is_hidden=0)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(name__contains=search) | Q(code__contains=search) | Q(update_date__contains=search)
        )

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
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for j, field in enumerate(list):
        # for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "code": field.code,
                "name": field.name}
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
def get_info_transaction(request):
    if request.method == 'POST':
        try:
            transaction_id = request.POST.get('transaction_id')
            transaction = Transaction.objects.get(id=transaction_id)
            data = {}
            if transaction.distribution_code_id:
                data["distribution_id"] = transaction.distribution_code_id
                data["distribution_code"] = transaction.distribution_code.code
                data["distribution_desc"] = transaction.distribution_code.name
            else:
                data["distribution_id"] = ""
                data["distribution_code"] = ""
                data["distribution_desc"] = ""
            data["account_id_trs"] = transaction.account_id
            data["account_code"] = transaction.account.code
            data["account_desc"] = transaction.account.name
            data["description"] = transaction.description
            data["amount"] = str(transaction.amount)
            data["base_tax_amount"] = str(transaction.base_tax_amount)
            data["tax_amount"] = str(transaction.tax_amount)
            data["total_amount"] = str(transaction.total_amount)
            data["is_tax_include"] = str(int(transaction.is_tax_include))
            data["tax_id"] = str(transaction.tax_id)
            data["is_tax_transaction"] = transaction.is_tax_transaction
            data["is_manual_tax_input"] = transaction.is_manual_tax_input

            array = []
            array.append(data)
            json_content = json.dumps(array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
        except ObjectDoesNotExist:
            messages_error = "Can't load transaction"
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def get_gl_info_transaction(request):
    if request.method == 'POST':
        try:
            transaction_id = request.POST.get('transaction_id')
            transaction = Transaction.objects.get(id=transaction_id)
            data = {"reference": transaction.reference,
                    "description": transaction.description,
                    "account_id": transaction.account_id,
                    "account_code": transaction.account.code,
                    "account_name": transaction.account.name,
                    "currency_id": transaction.currency_id,
                    "currency_code": transaction.currency.code,
                    "currency_name": transaction.currency.name,
                    "is_decimal": transaction.currency.is_decimal,
                    "amount": str(transaction.amount),
                    "exchange_rate": str(transaction.exchange_rate),
                    "rate_date": transaction.rate_date.strftime("%d-%m-%Y") if transaction.rate_date else '',
                    "functional_amount": str(transaction.functional_amount),
                    "remark": transaction.remark,
                    "is_debit_account": transaction.is_debit_account,
                    "functional_balance_type": transaction.functional_balance_type,
                    "is_auto_exch": transaction.is_auto_exch}
            array = []
            array.append(data)
            json_content = json.dumps(array, ensure_ascii=False)
            return HttpResponse(json_content, content_type='application/json')
        except ObjectDoesNotExist:
            messages_error = "Can't load transaction"
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
