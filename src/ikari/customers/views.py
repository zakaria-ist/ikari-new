import datetime
import json
import logging
import traceback
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from companies.models import Company
from accounts.models import Account, AccountSet
from contacts.models import Contact
from taxes.models import Tax
from orders.models import Order
from accounting.models import PaymentCode, Journal
from currencies.models import Currency
from customers.forms import CustomerOldSystemColumn, CustomerForm, AccCustomerForm, DeliveryForm
from customers.models import Customer, Delivery, CustomerItem
from items.models import Item
from locations.models import Location
from utilities.constants import BALANCE_TYPE, ACCOUNT_TYPE, TERMS_CODE, ACCOUNT_SET_TYPE_DICT, TAX_TRX_TYPES_DICT, \
    CONTACT_TYPES_DICT, PAYMENT_CODE_TYPE_DICT

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def load_list(request):
    try:
        return render(request, 'customer-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


# Create your views here.
@login_required
def acc_customer_list(request):
    try:
        return render(request, 'acc-customer-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('customers.change_customer', login_url='/alert/')
def customer_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST' and request.POST.get('name') and request.POST.get('code'):
        try:
            with transaction.atomic():
                customer = Customer()
                customer.name = request.POST.get('name')
                customer.code = request.POST.get('code')
                if request.POST.get('type'):
                    customer.customer_type = request.POST.get('type')
                else:
                    customer.customer_type = None
                if request.POST.get('address'):
                    customer.address = request.POST.get('address')
                else:
                    customer.address = None
                if request.POST.get('note1'):
                    customer.note1 = request.POST.get('note1')
                else:
                    customer.note1 = None
                customer.company_id = company_id
                if request.POST.get('tax') != "0" and request.POST.get('tax'):
                    customer.tax_id = request.POST.get('tax')
                else:
                    customer.tax_id = None
                if request.POST.get('country') != "0" and request.POST.get('country'):
                    customer.country_id = request.POST.get('country')
                else:
                    customer.country_id = None
                if request.POST.get('currency') != "0" and request.POST.get('currency'):
                    customer.currency_id = request.POST.get('currency')
                else:
                    customer.currency_id = None
                if request.POST.get('payment_term') != "-1" and request.POST.get('payment_term'):
                    customer.payment_term = request.POST.get('payment_term')
                else:
                    customer.payment_term = None
                if request.POST.get('location') != "0" and request.POST.get('location'):
                    customer.location_id = request.POST.get('location')
                else:
                    customer.location_id = None
                if request.POST.get('payment_code') != "0" and request.POST.get('payment_code'):
                    customer.payment_code_id = request.POST.get('payment_code')
                else:
                    customer.payment_code_id = None
                if request.POST.get('credit_limit') != "0" and request.POST.get('credit_limit'):
                    customer.credit_limit = request.POST.get('credit_limit')
                else:
                    customer.credit_limit = None
                if request.POST.get('pricing_type') != "0" and request.POST.get('pricing_type'):
                    customer.pricing_type = request.POST.get('pricing_type')
                else:
                    customer.pricing_type = None
                if request.POST.get('statement') != "0" and request.POST.get('statement'):
                    customer.statement = request.POST.get('statement')
                else:
                    customer.statement = None
                if request.POST.get('interest_flag') != "0" and request.POST.get('interest_flag'):
                    customer.interest_flag = request.POST.get('interest_flag')
                else:
                    customer.interest_flag = None

                customer.is_active = True
                customer.is_hidden = False
                customer.create_date = datetime.datetime.today()
                customer.update_by = request.user.id
                customer.update_date = datetime.datetime.today()
                OldSystemColumn = CustomerOldSystemColumn(data=request.POST, instance=customer)
                if OldSystemColumn.is_valid():
                    OldSystemColumn.save()
                customer.distribution_code_id = request.POST.get('distribution_code') if request.POST.get(
                    'distribution_code') else None
                customer.save()

                try:
                    contact_list = Contact()
                    contact_list.contact_type = int(CONTACT_TYPES_DICT['Customer'])
                    contact_list.customer_id = customer.id
                    contact_list.company_id = company_id
                    contact_list.is_active = True
                    contact_list.create_date = datetime.datetime.today()
                    contact_list.is_hidden = 0
                    if request.POST.get('consignee_contact_person'):
                        contact_list.name = request.POST.get('consignee_contact_person')
                    if request.POST.get('consignee_address'):
                        contact_list.address = request.POST.get('consignee_address')
                    if request.POST.get('contact_attention'):
                        contact_list.attention = request.POST.get('contact_attention')
                    if request.POST.get('consignee_name'):
                        contact_list.company_name = request.POST.get('consignee_name')
                    if request.POST.get('contact_designation'):
                        contact_list.designation = request.POST.get('contact_designation')
                    if request.POST.get('consignee_phone'):
                        contact_list.phone = request.POST.get('consignee_phone')
                    if request.POST.get('note1'):
                        contact_list.note = request.POST.get('note1')
                    contact_list.update_date = datetime.datetime.today()
                    contact_list.update_by = request.user.id
                    contact_list.save()
                except Exception:
                    pass

            return HttpResponsePermanentRedirect(reverse('customer_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_add')
    # save referer from order add new
    else:
        request.session['url_referer'] = request.META.get('HTTP_REFERER')
        form = CustomerForm(initial={'payment_term': '30'}, company_id=company_id)
        OldSystemColumn = CustomerOldSystemColumn()
    return render_to_response('customer-form.html',
                              RequestContext(request, {'form': form, 'OldSystemColumn': OldSystemColumn,
                                                       'term_list': TERMS_CODE
                                                       }))


@login_required
def customer_By_pk(request, customer_id, rate_date):
    try:

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        list_filter = Customer.objects.filter(pk=customer_id, is_hidden=False, company=company)
        array = []
        for field in list_filter:
            data = {"id": field.id,
                    "payment_code_id": field.payment_code.id if field.payment_code else '',
                    "payment_code": field.payment_code.code if field.payment_code else '',
                    "payment_term": field.payment_term,
                    "currency_id": field.currency.id,
                    "currency_name": field.currency.name,
                    "is_decimal": 1 if field.currency.is_decimal else 0,
                    "credit_limit": str(field.credit_limit),
                    "address": field.address,
                    "email": field.email,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "customer_code": field.code,
                    "customer_name": field.name,
                    "country_code": field.country.code if field.country else '',
                    "location_code": field.location.code if field.location else '',
                    "currency_code": field.currency.code if field.currency else '',
                    "currency_symbol": field.currency.symbol if field.currency else '',
                    "tax_name": field.tax.name if field.tax else '',
                    "is_active": str(field.is_active),
                    "tax_id": field.tax.id if field.tax else '',
                    "distribution_code_id": field.distribution_code_id if field.distribution_code_id else '',
                    "consignee_name": None,
                    "consignee_company_name": None,
                    "consignee_address": None,
                    "consignee_phone": None}
            try:
                contact = Contact.objects.filter(customer_id=field.id, company_id=company_id, is_hidden=0).first()
                if contact:
                    data["contact_id"] = contact.id
                    data["consignee_name"] = contact.name
                    data["attention"] = contact.attention
                    data["consignee_company_name"] = contact.company_name
                    data["consignee_address"] = contact.address
                    data["consignee_phone"] = contact.phone
            except Exception:
                pass
            array.append(data)

        content = {
            "data": array,
        }
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def customer_By_code(request, customer_code):
    try:

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        list_filter = Customer.objects.filter(code=customer_code, is_hidden=False, company=company)
        array = []
        for field in list_filter:
            data = {
                "id": field.id,
                "customer_code": field.code,
                "customer_name": field.name
            }
            array.append(data)

        content = {
            "data": array,
        }
        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
@permission_required('customers.change_customer', login_url='/alert/')
def customer_edit(request, customer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    post = get_object_or_404(Customer, pk=customer_id)
    customer = Customer.objects.get(pk=customer_id)
    contact_list = Contact.objects.filter(is_hidden=0, contact_type__in=(1, 5), customer_id=customer_id, company_id=company_id).first()

    OldSystemColumn = CustomerOldSystemColumn(instance=customer)
    if request.method == 'POST':
        try:
            customer.id = customer_id
            customer.name = request.POST.get('name')
            customer.code = request.POST.get('code')
            if request.POST.get('type'):
                customer.customer_type = request.POST.get('type')
            else:
                customer.customer_type = None
            if request.POST.get('address'):
                customer.address = request.POST.get('address')
            else:
                customer.address = None
            if request.POST.get('note1'):
                customer.note1 = request.POST.get('note1')
            else:
                customer.note1 = None
            customer.create_date = datetime.datetime.today()
            customer.update_date = datetime.datetime.today()
            customer.update_by = request.user.id
            customer.is_hidden = False
            customer.company_id = company_id
            if request.POST.get('tax') != "0" and request.POST.get('tax'):
                customer.tax_id = request.POST.get('tax')
            else:
                customer.tax_id = None
            if request.POST.get('country') != "0" and request.POST.get('country'):
                customer.country_id = request.POST.get('country')
            else:
                customer.country_id = None
            if request.POST.get('currency') != "0" and request.POST.get('currency'):
                customer.currency_id = request.POST.get('currency')
            else:
                customer.currency_id = None
            if request.POST.get('payment_term') != "-1" and request.POST.get('payment_term'):
                customer.payment_term = request.POST.get('payment_term')
            else:
                customer.payment_term = None
            if request.POST.get('location') != "0" and request.POST.get('location'):
                customer.location_id = request.POST.get('location')
            else:
                customer.location_id = None
            if request.POST.get('payment_code') != "0" and request.POST.get('payment_code'):
                customer.payment_code_id = request.POST.get('payment_code')
            else:
                customer.payment_code_id = None
            if request.POST.get('credit_limit') != "0" and request.POST.get('credit_limit'):
                customer.credit_limit = request.POST.get('credit_limit')
            else:
                customer.credit_limit = None
            if request.POST.get('pricing_type') != "0" and request.POST.get('pricing_type'):
                customer.pricing_type = request.POST.get('pricing_type')
            else:
                customer.pricing_type = None
            if request.POST.get('statement') != "0" and request.POST.get('statement'):
                customer.statement = request.POST.get('statement')
            else:
                customer.statement = None
            if request.POST.get('interest_flag') != "0" and request.POST.get('interest_flag'):
                customer.interest_flag = request.POST.get('interest_flag')
            else:
                customer.interest_flag = None

            OldSystemColumn = CustomerOldSystemColumn(data=request.POST, instance=customer)
            if OldSystemColumn.is_valid():
                OldSystemColumn.save()
            customer.distribution_code_id = request.POST.get('distribution_code') if request.POST.get(
                'distribution_code') else None
            customer.save()

            if not contact_list:
                contact_list = Contact()
                contact_list.contact_type = int(CONTACT_TYPES_DICT['Customer'])
                contact_list.customer_id = customer.id
                contact_list.company_id = company_id
                contact_list.is_active = True
                contact_list.create_date = datetime.datetime.today()
                contact_list.is_hidden = 0
            contact_list.name = request.POST.get('consignee_contact_person')
            contact_list.address = request.POST.get('consignee_address')
            contact_list.attention = request.POST.get('contact_attention')
            contact_list.company_name = request.POST.get('consignee_name')
            contact_list.designation = request.POST.get('contact_designation')
            contact_list.phone = request.POST.get('consignee_phone')
            contact_list.note = request.POST.get('note1')
            contact_list.update_date = datetime.datetime.today()
            contact_list.update_by = request.user.id
            contact_list.save()

            return HttpResponsePermanentRedirect(reverse('customer_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_edit')
    else:
        customer.update_date = customer.update_date.strftime("%d-%m-%Y")
        form = CustomerForm(instance=post, company_id=company_id)
    return render_to_response('customer-form.html', RequestContext(request, {'customer': customer,
                                                                             'contact_list': contact_list,
                                                                             'term_list': TERMS_CODE,
                                                                             'form': form,
                                                                             'OldSystemColumn': OldSystemColumn
                                                                             }))


@login_required
@permission_required('customers.change_customer', login_url='/alert/')
def acc_customer_add(request):
    # customer = Customer()
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    payment_code_list = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                        company_id=company_id, 
                                                        source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
    tax_code_list = Tax.objects.filter(is_hidden=False,
                                       company_id=company_id,
                                       tax_group__company_id=company_id,
                                       tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Sales']))
    currency_code_list = Currency.objects.filter(is_hidden=False)
    if request.method == 'POST':
        form = AccCustomerForm(request, request.POST)
        try:
            with transaction.atomic():
                customer = Customer()
                customer.company_id = company_id
                customer.name = request.POST.get('name')
                customer.email = request.POST.get('email')
                customer.code = request.POST.get('code')
                if request.POST.get('account_receivable'):
                    customer.account_receivable_id = request.POST.get('account_receivable')
                else:
                    customer.account_receivable_id = None
                if request.POST.get('currency'):
                    customer.currency_id = request.POST.get('currency')
                else:
                    customer.currency_id = None
                if request.POST.get('account_set'):
                    customer.account_set_id = request.POST.get('account_set')
                else:
                    customer.account_set_id = None
                if request.POST.get('payment_term'):
                    customer.payment_term = request.POST.get('payment_term')
                else:
                    customer.payment_term = None
                if request.POST.get('interest_profile'):
                    customer.interest_profile_id = request.POST.get('interest_profile')
                else:
                    customer.interest_profile_id = None
                if request.POST.get('payment_code'):
                    customer.payment_code_id = request.POST.get('payment_code')
                else:
                    customer.payment_code_id = None
                if request.POST.get('tax'):
                    customer.tax_id = request.POST.get('tax')
                else:
                    customer.tax_id = None
                if request.POST.get('credit_limit'):
                    customer.credit_limit = request.POST.get('credit_limit')
                else:
                    customer.credit_limit = None
                if request.POST.get('email_msg'):
                    customer.email_msg = request.POST.get('email_msg')
                else:
                    customer.email_msg = None
                if request.POST.get('address'):
                    customer.address = request.POST.get('address')
                else:
                    customer.address = None
                if request.POST.get('phone'):
                    customer.phone = request.POST.get('phone')
                else:
                    customer.phone = None
                if request.POST.get('postal_code'):
                    customer.postal_code = request.POST.get('postal_code')
                else:
                    customer.postal_code = None
                if request.POST.get('country'):
                    customer.country_id = request.POST.get('country')
                else:
                    customer.country_id = None

                customer.is_active = True
                customer.is_hidden = False
                customer.create_date = datetime.datetime.today()
                customer.update_by = request.user.id
                customer.update_date = datetime.datetime.today()
                customer.save()
                return HttpResponsePermanentRedirect(reverse('acc_customer_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_add')
            return HttpResponsePermanentRedirect(reverse('acc_customer_list'))
    else:
        form = AccCustomerForm(request)

    return render_to_response('acc-customer-form.html',
                              RequestContext(request, {'form': form, 'terms_code_list': TERMS_CODE,
                                                       'payment_code_list': payment_code_list,
                                                       'tax_code_list': tax_code_list,
                                                       'currency_code_list': currency_code_list}))


@login_required
@permission_required('customers.change_customer', login_url='/alert/')
def acc_customer_edit(request, customer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    customer = Customer.objects.get(pk=customer_id)
    post = get_object_or_404(Customer, pk=customer_id)  # get this 'post' instance to the form
    payment_code_list = PaymentCode.objects.filter(is_hidden=False, is_active=True, 
                                                        company_id=company_id, 
                                                        source_type=PAYMENT_CODE_TYPE_DICT['AR Payment Code']).order_by('code')
    tax_code_list = Tax.objects.filter(is_hidden=False,
                                       company_id=company_id,
                                       tax_group__company_id=company_id,
                                       tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Sales']))
    currency_code_list = Currency.objects.filter(is_hidden=False)
    if request.method == 'POST':
        form = AccCustomerForm(request, request.POST, instance=post)
        try:
            customer.id = customer_id
            customer.name = request.POST.get('name')
            customer.email = request.POST.get('email')
            customer.code = request.POST.get('code')
            if request.POST.get('account_receivable'):
                customer.account_receivable_id = request.POST.get('account_receivable')
            else:
                customer.account_receivable_id = None
            if request.POST.get('currency'):
                customer.currency_id = request.POST.get('currency')
            else:
                customer.currency_id = None
            if request.POST.get('account_set'):
                customer.account_set_id = request.POST.get('account_set')
            else:
                customer.account_set_id = None
            if request.POST.get('payment_term'):
                customer.payment_term = request.POST.get('payment_term')
            else:
                customer.payment_term = None
            if request.POST.get('interest_profile'):
                customer.interest_profile_id = request.POST.get('interest_profile')
            else:
                customer.interest_profile_id = None
            if request.POST.get('payment_code'):
                customer.payment_code_id = request.POST.get('payment_code')
            else:
                customer.payment_code_id = None
            if request.POST.get('tax'):
                customer.tax_id = request.POST.get('tax')
            else:
                customer.tax_id = None
            if request.POST.get('credit_limit'):
                customer.credit_limit = request.POST.get('credit_limit')
            else:
                customer.credit_limit = None
            if request.POST.get('email_msg'):
                customer.email_msg = request.POST.get('email_msg')
            else:
                customer.email_msg = None
            if request.POST.get('address'):
                customer.address = request.POST.get('address')
            else:
                customer.address = None
            if request.POST.get('phone'):
                customer.phone = request.POST.get('phone')
            else:
                customer.phone = None
            if request.POST.get('postal_code'):
                customer.postal_code = request.POST.get('postal_code')
            else:
                customer.postal_code = None
            if request.POST.get('country'):
                customer.country_id = request.POST.get('country')
            else:
                customer.country_id = None
                
            customer.update_by = request.user.id
            customer.update_date = datetime.datetime.today()
            customer.save()

            return HttpResponsePermanentRedirect(reverse('acc_customer_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_edit')
            return HttpResponsePermanentRedirect(reverse('acc_customer_list'))
    else:
        form = AccCustomerForm(request, instance=post)
        customer.update_date = customer.update_date.strftime("%d-%m-%Y")
    return render_to_response('acc-customer-form.html',
                              RequestContext(request, {'form': form, 'terms_code_list': TERMS_CODE,
                                                       'payment_code_list': payment_code_list,
                                                       'tax_code_list': tax_code_list,
                                                       'currency_code_list': currency_code_list,
                                                       'customer': customer}))


@login_required
@permission_required('customers.delete_customer', login_url='/alert/')
def customer_delete(request, customer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(pk=customer_id)
            customer.is_active = False
            journals = Journal.objects.filter(company_id=company_id, customer_id=customer_id, is_hidden=0)
            orders = Order.objects.filter(company_id=company_id, customer_id=customer_id, is_hidden=0)
            if not len(journals) and not len(orders):
                customer.is_hidden = True
                messages.add_message(request, messages.INFO, 'Customer is Deleted', extra_tags='customer_delete')
            else:
                messages.add_message(request, messages.WARNING, 'Customer is Deactivated but not deleted. As there are some dependencies', extra_tags='customer_delete')
            customer.save()
            return HttpResponsePermanentRedirect(reverse('acc_customer_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_delete')


@login_required
@permission_required('customers.add_delivery', login_url='/alert/')
def delivery_add(request):
    if request.method == 'POST':
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        form = DeliveryForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    delivery = Delivery()
                    delivery.code = request.POST.get('code')
                    delivery.name = request.POST.get('name')
                    delivery.attention = request.POST.get('attention')
                    delivery.phone = request.POST.get('phone')
                    delivery.email = request.POST.get('email')
                    delivery.fax = request.POST.get('fax')
                    delivery.note_1 = request.POST.get('note_1')
                    delivery.address = request.POST.get('address')
                    delivery.is_active = 1
                    delivery.company_id = company_id
                    delivery.create_date = datetime.datetime.today()
                    delivery.update_date = datetime.datetime.today()
                    delivery.update_by = request.user.id
                    delivery.is_hidden = 0
                    delivery.save()

                    contact = Contact()
                    if request.POST.get('name'):
                        contact.name = request.POST.get('name')
                    contact.contact_type = int(CONTACT_TYPES_DICT['Delivery'])
                    contact.delivery_id = delivery.id
                    contact.company_id = company_id
                    if request.POST.get('attention'):
                        contact.attention = request.POST.get('attention')
                    if request.POST.get('phone'):
                        contact.phone = request.POST.get('phone')
                    if request.POST.get('fax'):
                        contact.fax = request.POST.get('fax')
                    if request.POST.get('email'):
                        contact.email = request.POST.get('email')
                    if request.POST.get('web'):
                        contact.web = request.POST.get('web')
                    if request.POST.get('address'):
                        contact.address = request.POST.get('address')
                    if request.POST.get('remark'):
                        contact.note = request.POST.get('remark')
                    if request.POST.get('company_name'):
                        contact.company_name = request.POST.get('company_name')
                    if request.POST.get('designation'):
                        contact.designation = request.POST.get('designation')
                    contact.create_date = datetime.datetime.today()
                    contact.update_date = datetime.datetime.today()
                    contact.update_by = request.user.id
                    contact.is_hidden = 0
                    contact.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='delivery_add')
            return HttpResponsePermanentRedirect(reverse('delivery_list'))
    else:
        form = DeliveryForm()
    return render(request, 'delivery-form.html', {'form': form})


@login_required
@permission_required('customers.change_delivery', login_url='/alert/')
def delivery_edit(request, delivery_id):
    delivery = Delivery.objects.get(pk=delivery_id)
    post = get_object_or_404(Delivery, pk=delivery_id)  # get this 'post' instance to the form

    last_update = delivery.update_date.strftime("%Y-%m-%d")
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=post)
        if form.is_valid():
            try:
                delivery.code = request.POST.get('code')
                delivery.name = request.POST.get('name')
                delivery.attention = request.POST.get('attention')
                delivery.phone = request.POST.get('phone')
                delivery.email = request.POST.get('email')
                delivery.fax = request.POST.get('fax')
                delivery.note_1 = request.POST.get('note_1')
                delivery.address = request.POST.get('address')
                delivery.update_by = request.user.id
                delivery.update_date = datetime.datetime.today()
                delivery.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='delivery_edit')
            return HttpResponsePermanentRedirect(reverse('delivery_list'))
    else:
        form = DeliveryForm(instance=post)

    return render(request, 'delivery-form.html', {'form': form, 'delivery': delivery, 'last_update': last_update})


@login_required
@permission_required('customers.delete_delivery', login_url='/alert/')
def delivery_delete(request, delivery_id):
    if request.method == 'POST':
        try:
            delivery = Delivery.objects.get(pk=delivery_id)
            delivery.is_active = 0
            delivery.is_hidden = 1
            delivery.update_by = request.user.id
            delivery.update_date = datetime.datetime.today()
            delivery.save()
            return HttpResponsePermanentRedirect(reverse('delivery_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='delivery_delete')


@login_required
def delivery_list(request):
    try:
        return render(request, 'delivery-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('customers.add_customeritem', login_url='/alert/')
def item_add(request, customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
        item_list = Item.objects.none()
        currency_list = Currency.objects.filter(is_hidden=0)
        select_item_id = request.POST.get('hdItemSelected')
    except ObjectDoesNotExist:
        messages_error = "Permission Denied."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        if select_item_id == None or select_item_id == '':
            messages_error = "Please select the an Item!"
            return render_to_response('customer-item.html', RequestContext(request,
                                                                           {'customer': customer,
                                                                            'item_list': item_list,
                                                                            'currency_list': currency_list,
                                                                            'messages_error': messages_error}))
        else:
            all_customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=customer_id) \
                .values_list('item_id', flat=True)
            if select_item_id and int(select_item_id) not in all_customer_item:
                customer_item = CustomerItem()
                customer_item.create_date = datetime.datetime.today()
            else:
                customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=select_item_id,
                                                            customer_id=customer_id).first()
            if customer_item:
                try:
                    customer_item.item_id = int(select_item_id)
                    customer_item.customer_id = customer_id
                    customer_item.currency_id = request.POST.get('currency')
                    if request.POST.get('sales_price'):
                        customer_item.sales_price = request.POST.get('sales_price')
                    if request.POST.get('leading_days'):
                        customer_item.leading_days = request.POST.get('leading_days')
                    if request.POST.get('effective_date'):
                        customer_item.effective_date = request.POST.get('effective_date')
                    if request.POST.get('is_active'):
                        customer_item.is_active = 1
                    else:
                        customer_item.is_active = 0

                    customer_item.update_date = datetime.datetime.today()
                    customer_item.update_by = request.user.id
                    customer_item.is_hidden = 0
                    customer_item.save()
                    return HttpResponsePermanentRedirect(reverse('customer_edit', args=[customer_id]))
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='customer_add_item')

    else:
        return render(request, 'customer-item.html', {'customer': customer,
                                                      # 'form': form,
                                                      'currency_list': currency_list,
                                                      'item_list': item_list})


@login_required
@permission_required('customers.change_customeritem', login_url='/alert/')
def item_edit(request, custitem_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item_list = Item.objects.none()
    currency_list = Currency.objects.filter(is_hidden=0)
    select_item_id = request.POST.get('hdItemSelected')
    try:
        customer_item = CustomerItem.objects.get(pk=custitem_id)
        customer = Customer.objects.get(pk=customer_item.customer_id)
    except ObjectDoesNotExist:
        messages_error = "Customer Item does not exist | Permission Denied."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        if select_item_id == None or select_item_id == '':
            messages_error = "Please select the an Item!"
            return render_to_response('customer-item.html', RequestContext(request,
                                                                           {'customer': customer,
                                                                            'currency_list': currency_list,
                                                                            'item_list': item_list,
                                                                            'customeritem': customer_item,
                                                                            'messages_error': messages_error}))
        else:
            all_customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1,
                                                            customer_id=customer_item.customer_id) \
                .values_list('item_id', flat=True)
            if select_item_id and (int(select_item_id) not in all_customer_item
                                   or int(select_item_id) == customer_item.item_id):
                customer_item = CustomerItem.objects.get(pk=custitem_id)
            else:
                customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1,
                                                            customer__company_id=company_id,
                                                            item_id=select_item_id,
                                                            customer_id=customer_item.customer_id).first()
            if customer_item:
                try:
                    customer_item.item_id = int(request.POST.get('hdItemSelected'))
                    customer_item.currency_id = request.POST.get('currency')
                    if request.POST.get('sales_price'):
                        customer_item.sales_price = request.POST.get('sales_price')
                    if request.POST.get('leading_days'):
                        customer_item.leading_days = request.POST.get('leading_days')
                    else:
                        customer_item.leading_days = None
                    if request.POST.get('effective_date'):
                        customer_item.effective_date = request.POST.get('effective_date')
                    else:
                        customer_item.effective_date = None
                    if request.POST.get('is_active'):
                        customer_item.is_active = 1
                    else:
                        customer_item.is_active = 0
                    customer_item.update_date = datetime.datetime.today()
                    customer_item.update_by = request.user.id
                    customer_item.is_hidden = 0
                    customer_item.save()
                    return HttpResponsePermanentRedirect(reverse('customer_edit', args=[customer.id]))
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='customer_add_item')

    else:
        return render(request, 'customer-item.html', {'customer': customer, 'item_list': item_list,
                                                      'currency_list': currency_list,
                                                      'customeritem': customer_item})


@login_required
@permission_required('customers.delete_customeritem', login_url='/alert/')
def item_delete(request, custitem_id):
    if request.method == 'POST':
        try:
            customeritem = CustomerItem.objects.get(pk=custitem_id)
            customeritem.is_hidden = True
            customeritem.is_active = False
            customeritem.update_by = request.user.id
            customeritem.update_date = datetime.datetime.today()
            customeritem.save()
            return HttpResponsePermanentRedirect(reverse('customer_edit', args=[customeritem.customer_id]))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='customer_delete_item')
        except ObjectDoesNotExist:
            messages_error = "Customer Item does not exist."
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def CustomerList__asJson(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Customer.objects.filter(is_hidden=0, company_id=company_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(country__code__icontains=search) |
            Q(location__code__icontains=search) |
            Q(currency__code__icontains=search) |
            Q(tax__name__icontains=search) |
            Q(update_date__icontains=search))

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
        column_name = "country__code"
    elif order_column == "4":
        column_name = "location__code"
    elif order_column == "5":
        column_name = "currency__code"
    elif order_column == "6":
        column_name = "tax__name"
    elif order_column == "7":
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
                "customer_code": field.code,
                "customer_name": field.name,
                "country_code": field.country.code if field.country else '',
                "location_code": field.location.code if field.location else '',
                "currency_code": field.currency.code if field.currency else '',
                "is_active": str(field.is_active)}
        try:
            data['tax_name'] = field.tax.name if field.tax else '',
        except:
            data['tax_name'] = '',
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
def CustomerItemList__asJson(request, customer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    customer = Customer.objects.get(pk=customer_id)
    customer_item_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=customer_id) \
        .values_list('item_id', flat=True)
    list_filter = Item.objects.filter(company_id=company_id, is_hidden=0, sale_currency_id=customer.currency_id) \
        .exclude(id__in=customer_item_list)

    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) |
            Q(name__contains=search) |
            Q(category__code__contains=search) |
            Q(country__name__contains=search) |
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
        column_name = "category__code"
    elif order_column == "4":
        column_name = "country__name"
    elif order_column == "5":
        column_name = "sales_price"
    elif order_column == "6":
        column_name = "sale_currency__code"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        sales_price = field.sale_price if field.sale_price else 0
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "item_code": field.code,
                "item_name": field.name,
                "category_code": field.category.code if field.category else '',
                "country_name": field.country.name if field.country else '',
                "sales_price": intcomma("%.2f" % sales_price),
                "sale_currency": field.sale_currency.code if field.sale_currency else 0,
                "sale_currency_id": field.sale_currency_id if field.sale_currency else 0}

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
def DeliveryList__asJson(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Delivery.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) |
            Q(name__contains=search) |
            Q(address__contains=search) |
            Q(phone__contains=search) |
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
        column_name = "phone"
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
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "delivery_code": field.code,
                "delivery_name": field.name,
                "delivery_address": field.address,
                "delivery_phone": field.phone,
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
def CustomerEditItemList__asJson(request, custitem_id):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']

    customer_item_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer_id=custitem_id)
    records_total = customer_item_list.count()

    if search:  # Filter data base on search
        customer_item_list = customer_item_list.filter(
            Q(item__code__contains=search) |
            Q(item__name__contains=search) |
            Q(item__category__name__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = customer_item_list.count()

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
        column_name = "sales_price"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = customer_item_list.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = customer_item_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        sales_price = field.sales_price if field.sales_price else 0
        currency = field.currency.code if field.currency else ''
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "item_code": field.item.code,
                "item_name": field.item.name,
                "category_name": field.item.category.name if field.item.category else '',
                "sales_price": intcomma("%.2f" % sales_price) + ' ' + currency,
                "is_active": str(field.item.is_active)}
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
def get_item_info(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            item_code = request.POST.get('item_code')
            customer_id = request.POST.get('customer_id')
            customer = Customer.objects.get(pk=customer_id)
            item = Item.objects.filter(code__contains=item_code, company_id=company_id, is_hidden=0).first()
            customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1,
                                                        customer_id=customer_id, item__code__contains=item_code).first()

            response_data = {}
            response_data['id'] = item.id
            response_data['name'] = item.name
            response_data['code'] = item.code
            response_data['currency_id'] = str(item.sale_currency.id if item.sale_currency else 0)
            response_data['sale_price'] = str(item.sale_price if item.sale_price else 0)
            if customer_item:
                response_data['currency_id'] = str(customer_item.currency.id if customer_item.currency else
                                                   item.sale_currency.id if item.sale_currency else 0)
                response_data['sale_price'] = str(customer_item.sales_price if customer_item.sales_price else
                                                  item.sale_price if item.sale_price else 0)
            if int(customer.currency_id) != int(response_data['currency_id']):
                messages.add_message(request, messages.ERROR,
                                     "Currency of item is different with currency of customer.",
                                     extra_tags='get_item_info')
                return HttpResponse(json.dumps({"Fail": "Currency of item is different with currency of customer."}),
                                    content_type="application/json")

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_item_info')
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")


@login_required
def DeliveryContact__asJson(request, delivery_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']

    list_filter = Contact.objects.filter(is_hidden=0, company_id=company_id, delivery_id=delivery_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(attention__contains=search) |
            Q(name__contains=search) |
            Q(location__name__contains=search) |
            Q(phone__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "name"
    elif order_column == "2":
        column_name = "attention"
    elif order_column == "3":
        column_name = "location__name"
    elif order_column == "4":
        column_name = "phone"
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
        data = {}
        data["id"] = field.id
        data["update_date"] = field.update_date.strftime("%d-%m-%Y")
        data["name"] = field.name
        data["attention"] = field.attention if field.attention else ''
        data["location"] = field.location.name if field.location else ""
        data["phone"] = field.phone
        data["is_active"] = str(field.is_active)
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@csrf_exempt
@login_required
def load_account_set(request):
    if request.method == 'POST':
        try:
            if 'account_set_id' in request.POST and request.POST['account_set_id']:
                account_set_id = request.POST['account_set_id']
                account = AccountSet.objects.get(pk=account_set_id)

                context = {
                    'name': account.name,
                    'currency_id': account.currency_id if account.currency else ''
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@csrf_exempt
@login_required
def load_payment_code(request):
    if request.method == 'POST':
        try:
            if 'payment_code_id' in request.POST and request.POST['payment_code_id']:
                payment_code_id = request.POST['payment_code_id']
                payment_code = PaymentCode.objects.get(pk=payment_code_id)

                context = {
                    'name': payment_code.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@csrf_exempt
@login_required
def load_tax_code(request):
    if request.method == 'POST':
        try:
            if 'tax_id' in request.POST and request.POST['tax_id']:
                tax_id = request.POST['tax_id']
                tax = Tax.objects.get(pk=tax_id)

                context = {
                    'name': tax.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@csrf_exempt
@login_required
def load_currency_code(request):
    if request.method == 'POST':
        try:
            if 'currency_id' in request.POST and request.POST['currency_id']:
                currency_id = request.POST['currency_id']
                currency = Currency.objects.get(pk=currency_id)

                context = {
                    'name': currency.name,
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponseNotFound
    else:
        return HttpResponseNotFound


@login_required
def AccountList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']

        balance_type_dict = dict(BALANCE_TYPE)
        account_type_dict = dict(ACCOUNT_TYPE)

        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Account.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(
                Q(name__contains=search) | Q(code__contains=search)
                | Q(account_type__contains=search)
                | Q(company__name__contains=search) | Q(update_date__contains=search)
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
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def AccCustomerList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    list_filter = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(account_set__code__icontains=search) |
            Q(payment_code__code__icontains=search) |
            Q(currency__code__icontains=search) |
            Q(tax__code__contains=search) |
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
        column_name = "account_set__code"
    elif order_column == "4":
        column_name = "payment_code__code"
    elif order_column == "5":
        column_name = "currency__code"
    elif order_column == "6":
        column_name = "tax__code"
    elif order_column == "7":
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
                "customer_code": field.code,
                "customer_name": field.name,
                "account_set": field.account_set.code if field.account_set else '',
                "payment_code": field.payment_code.code if field.payment_code else '',
                "currency_code": field.currency.code if field.currency else '',
                "is_active": str(field.is_active)}

        try:
            data['tax_code'] = field.tax.code if field.tax else '',
        except:
            data['tax_code'] = '',
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
def AR_AccountSetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = AccountSet.objects.filter(is_hidden=0, company_id=company_id, is_active=True,
                                                type=ACCOUNT_SET_TYPE_DICT['AR Account Set'])
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__contains=search)
                                             | Q(code__contains=search)
                                             | Q(control_account__code__contains=search)
                                             | Q(control_account__name__contains=search)
                                             | Q(revaluation_account__code__contains=search)
                                             | Q(revaluation_account__name__contains=search)
                                             | Q(currency__code__contains=search)
                                             | Q(currency__name__contains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "control_account__code"
        elif order_column == "3":
            column_name = "currency__code"
        elif order_column == "4":
            column_name = "revaluation_account__code"
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
                    "control_account": (field.control_account.code + '-' + field.control_account.name)
                    if field.control_account else '',
                    "currency_code": (field.currency.code + '-' + field.currency.name) if field.currency else '',
                    "currency_id": str(field.currency_id) if field.currency else '',
                    "revaluation_account": (field.revaluation_account.code + '-' + field.revaluation_account.name)
                    if field.revaluation_account else ''}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')

    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def CurrencySetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        list_filter = Currency.objects.filter(is_hidden=0)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__contains=search)
                                             | Q(code__contains=search)
                                             | Q(update_date__contains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
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
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def PaymentModeSetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        list_filter = PaymentCode.objects.filter(is_hidden=0)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__contains=search)
                                             | Q(code__contains=search)
                                             | Q(update_date__contains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
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
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def TaxSetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Tax.objects.filter(is_hidden=0,
                                         company_id=company_id,
                                         tax_group__company_id=company_id,
                                         tax_group__transaction_type=int(TAX_TRX_TYPES_DICT['Sales']))
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__icontains=search)
                                             | Q(code__icontains=search)
                                             | Q(rate__icontains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
        order_column = request.GET['order[0][column]']
        if order_column == "0":
            column_name = "code"
        elif order_column == "1":
            column_name = "name"
        elif order_column == "2":
            column_name = "rate"
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
                    "rate": str(field.rate)
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
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def LocationSetList__asJson(request):
    try:
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        list_filter = Location.objects.filter(company_id=company_id, is_active=1, is_hidden=0)
        records_total = list_filter.count()

        if search:
            list_filter = list_filter.filter(Q(name__contains=search)
                                             | Q(code__contains=search)
                                             | Q(update_date__contains=search))

            # All data
        records_filtered = list_filter.count()  # Order by list_limit base on order_dir and order_column
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
        for field in list:
            data = {"id": field.id,
                    "update_date": field.update_date.strftime("%d-%m-%Y"),
                    "name": field.name,
                    "code": field.code}
            array.append(data)

        content = {
            "draw": draw,
            "data": array,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered
        }

        json_content = json.dumps(content, ensure_ascii=False)
        return HttpResponse(json_content, content_type='application/json')
    except Exception:
        logger.error(traceback.format_exc())
        return HttpResponseNotFound


@login_required
def get_customer_code_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)

    try:
        customer_list = Customer.objects.filter(is_hidden=False, is_active=True, company_id=company.id)\
                        .order_by('code')\
                        .values_list('id', 'code')
        content = {
            "customer_list": list(customer_list)
        }

    except:
        content = {
            "customer_list": []
        }
    
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')
