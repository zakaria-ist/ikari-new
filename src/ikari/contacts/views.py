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

from companies.models import Company
from contacts.forms import ContactForm
from contacts.models import Contact
from utilities.constants import CONTACT_TYPES_DICT, LOCATION_TABS


# Create your views here.
@login_required
def load_list(request):
    try:
        return render(request, 'contact-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


def contact_change_check(user):
    if user.has_perm('contacts.change_contact') or user.has_perm('contacts.add_contact'):
        return True
    return False


@login_required
@permission_required('contacts.add_contact', login_url='/alert/')
def contact_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        form = ContactForm(company_id, request.POST)
        if form.is_valid():
            try:

                my_contact = form.save(commit=False)
                my_contact.company_id = company_id
                my_contact.create_date = datetime.datetime.today()
                my_contact.update_date = datetime.datetime.today()
                my_contact.update_by = request.user.id
                my_contact.is_hidden = 0
                my_contact.contact_type = request.POST.get('assignee')
                assignee = request.POST.get('assignee')
                if assignee == '1':
                    my_contact.customer_id = request.POST.get('customer')
                    my_contact.supplier_id = None
                    my_contact.location_id = None
                    my_contact.delivery_id = None
                    my_contact.consignee_id = None
                if assignee == '2':
                    my_contact.customer_id = None
                    my_contact.supplier_id = request.POST.get('supplier')
                    my_contact.location_id = None
                    my_contact.delivery_id = None
                    my_contact.consignee_id = None
                if assignee == '3':
                    my_contact.customer_id = None
                    my_contact.supplier_id = None
                    my_contact.location_id = request.POST.get('location')
                    my_contact.delivery_id = None
                    my_contact.consignee_id = None
                if assignee == '4':
                    my_contact.customer_id = None
                    my_contact.supplier_id = None
                    my_contact.location_id = None
                    my_contact.delivery_id = request.POST.get('delivery')
                    my_contact.consignee_id = None
                if assignee == '5':
                    my_contact.customer_id = None
                    my_contact.supplier_id = None
                    my_contact.location_id = None
                    my_contact.delivery_id = None
                    my_contact.consignee_id = request.POST.get('consignee')
                my_contact.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='contact_add')
            return HttpResponsePermanentRedirect(reverse('contact_list'))
        else:
            form = ContactForm(company_id, request.POST)
    else:
        form = ContactForm(company_id)
    return render(request, 'contact-form.html', {'form': form})


@login_required
@permission_required('contacts.change_contact', login_url='/alert/')
def contact_edit(request, contact_id=''):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    contact = Contact.objects.get(pk=contact_id)
    post = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        form = ContactForm(company_id, request.POST, instance=post)
        if form.is_valid():
            try:
                my_contact = form.save(commit=False)
                my_contact.update_date = datetime.datetime.today()
                my_contact.update_by = request.user.id
                my_contact.is_hidden = 0
                my_contact.contact_type = request.POST.get('assignee')
                assignee = request.POST.get('assignee')
                if assignee == '1':
                    my_contact.customer_id = request.POST.get('customer')
                    my_contact.supplier_id = None
                    my_contact.location_id = None
                    my_contact.delivery_id = None
                    my_contact.consignee_id = None
                if assignee == '2':
                    my_contact.customer_id = None
                    my_contact.supplier_id = request.POST.get('supplier')
                    my_contact.location_id = None
                    my_contact.delivery_id = None
                    my_contact.consignee_id = None
                if assignee == '3':
                    my_contact.customer_id = None
                    my_contact.supplier_id = None
                    my_contact.location_id = request.POST.get('location')
                    my_contact.delivery_id = None
                    my_contact.consignee_id = None
                if assignee == '4':
                    my_contact.customer_id = None
                    my_contact.supplier_id = None
                    my_contact.location_id = None
                    my_contact.delivery_id = request.POST.get('delivery')
                    my_contact.consignee_id = None
                if assignee == '5':
                    my_contact.customer_id = None
                    my_contact.supplier_id = None
                    my_contact.location_id = None
                    my_contact.delivery_id = None
                    my_contact.consignee_id = request.POST.get('consignee')

                my_contact.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='contact_edit')
            return HttpResponsePermanentRedirect(reverse('contact_list'))
    form = ContactForm(company_id, instance=post)
    return render(request, 'contact-form.html', {'form': form, 'contact': contact})


@login_required
@permission_required('contacts.delete_contact', login_url='/alert/')
def contact_delete(request, contact_id):
    if request.method == 'POST':
        try:
            my_contact = Contact.objects.get(pk=contact_id)
            my_contact.is_active = False
            my_contact.is_hidden = True
            my_contact.save()
            return HttpResponsePermanentRedirect(reverse('contact_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='contact_delete')


@login_required
@permission_required('contacts.add_contact', login_url='/alert/')
def contact_refer_add(request, contact_type, refer_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            # if request.POST.get('contact_name'):
            contact = Contact()
            if request.POST.get('contact_name'):
                contact.name = request.POST.get('contact_name')
            else:
                contact.name = ''
            contact.contact_type = contact_type
            if request.POST.get('checkbox'):
                contact.is_active = True
            else:
                contact.is_active = False
            if contact_type == CONTACT_TYPES_DICT['Customer']:  # customer
                contact.customer_id = refer_id
            elif contact_type == CONTACT_TYPES_DICT['Supplier']:  # supplier
                contact.supplier_id = refer_id
            elif contact_type == CONTACT_TYPES_DICT['Location']:  # location
                contact.location_id = refer_id
            elif contact_type == CONTACT_TYPES_DICT['Delivery']:  # delivery
                contact.delivery_id = refer_id
            elif contact_type == CONTACT_TYPES_DICT['Consignee']:  # consignee
                contact.consignee_id = contact.id
                if request.session['consignee_type'] == 1:
                    contact.customer_id = refer_id
                elif request.session['consignee_type'] == 2:
                    contact.supplier_id = refer_id

            contact.company = Company.objects.get(pk=company_id)
            if request.POST.get('attention'):
                contact.attention = request.POST.get('attention')
            if request.POST.get('phone'):
                contact.phone = request.POST.get('phone')
            if request.POST.get('company_name'):
                contact.company_name = request.POST.get('company_name')
            if request.POST.get('designation'):
                contact.designation = request.POST.get('designation')
            if request.POST.get('fax'):
                contact.fax = request.POST.get('fax')
            if request.POST.get('email'):
                contact.email = request.POST.get('email')
            if request.POST.get('web'):
                contact.web = request.POST.get('web')
            if request.POST.get('contact_address'):
                contact.address = request.POST.get('contact_address')
            if request.POST.get('remark'):
                contact.note = request.POST.get('remark')
            contact.create_date = datetime.datetime.today()
            contact.update_date = datetime.datetime.today()
            contact.update_by = request.user.id
            contact.is_hidden = 0
            contact.save()
            if contact_type == CONTACT_TYPES_DICT['Customer']:  # customer tab contact
                return HttpResponsePermanentRedirect(reverse('customer_edit', args=[refer_id]))
            elif contact_type == CONTACT_TYPES_DICT['Supplier']:  # supplier tab contact
                return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[refer_id]))
            elif contact_type == CONTACT_TYPES_DICT['Location']:  # location
                return HttpResponsePermanentRedirect(reverse('location_edit', args=[refer_id, int(LOCATION_TABS['Contact'])]))
            elif contact_type == CONTACT_TYPES_DICT['Delivery']:  # delivery
                return HttpResponsePermanentRedirect(reverse('delivery_edit', args=[refer_id]))
            elif contact_type == CONTACT_TYPES_DICT['Consignee']:
                if request.session['consignee_type'] == 1:  # customer tab consignee
                    del request.session['consignee_type']
                    return HttpResponsePermanentRedirect(reverse('customer_edit', args=[refer_id]))
                if request.session['consignee_type'] == 2:  # supplier tab consignee
                    del request.session['consignee_type']
                    return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[refer_id]))

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='contact_refer_add')
    elif contact_type == CONTACT_TYPES_DICT['Customer'] \
            or contact_type == CONTACT_TYPES_DICT['Supplier'] \
            or contact_type == CONTACT_TYPES_DICT['Location'] \
            or contact_type == CONTACT_TYPES_DICT['Delivery'] \
            or contact_type == CONTACT_TYPES_DICT['Consignee']:
        if contact_type == CONTACT_TYPES_DICT['Consignee']:
            if request.META['HTTP_REFERER'] and ('customer' in request.META['HTTP_REFERER']):
                request.session['consignee_type'] = 1
            elif request.META['HTTP_REFERER'] and ('supplier' in request.META['HTTP_REFERER']):
                request.session['consignee_type'] = 2
            else:
                request.session['consignee_type'] = 0
        return render_to_response('contact-refer.html',
                                  RequestContext(request, {'refer_id': refer_id, 'contact_type': contact_type}))
    else:
        form = ContactForm(company_id)
        return render(request, 'contact-form.html', {'form': form})


@login_required
@permission_required('contacts.change_contact', login_url='/alert/')
def contact_refer_edit(request, contact_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        contact = Contact.objects.get(pk=contact_id)
        post = get_object_or_404(Contact, pk=contact_id)
    except:
        messages_error = "Contact does not exist."
        return render_to_response('404.html',
                                  RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        try:
            # if request.POST.get('contact_name'):
            contact.name = request.POST.get('contact_name')
            if request.POST.get('checkbox'):
                contact.is_active = True
            else:
                contact.is_active = False
            if request.POST.get('attention'):
                contact.attention = request.POST.get('attention')
            if request.POST.get('company_name'):
                contact.company_name = request.POST.get('company_name')
            if request.POST.get('designation'):
                contact.designation = request.POST.get('designation')
            if request.POST.get('phone'):
                contact.phone = request.POST.get('phone')
            if request.POST.get('fax'):
                contact.fax = request.POST.get('fax')
            if request.POST.get('email'):
                contact.email = request.POST.get('email')
            if request.POST.get('web'):
                contact.web = request.POST.get('web')
            if request.POST.get('contact_address'):
                contact.address = request.POST.get('contact_address')
            if request.POST.get('remark'):
                contact.note = request.POST.get('remark')
            contact.create_date = datetime.datetime.today()
            contact.update_date = datetime.datetime.today()
            contact.update_by = request.user.id
            contact.is_hidden = 0
            contact.save()
            # return HttpResponsePermanentRedirect(reverse('location_edit', args=[contact.location_id]))
            if contact.contact_type == int(CONTACT_TYPES_DICT['Customer']):  # customer tab contact
                return HttpResponsePermanentRedirect(reverse('customer_edit', args=[contact.customer_id]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Supplier']):  # supplier tab contact
                return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[contact.supplier_id]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Location']):  # location
                return HttpResponsePermanentRedirect(reverse('location_edit', args=[contact.location_id, int(LOCATION_TABS['Contact'])]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Delivery']):  # delivery
                return HttpResponsePermanentRedirect(reverse('delivery_edit', args=[contact.delivery_id]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Consignee']):
                if request.session['consignee_type'] == 1:  # customer tab consignee
                    return HttpResponsePermanentRedirect(reverse('customer_edit', args=[contact.customer_id]))
                if request.session['consignee_type'] == 2:  # supplier tab consignee
                    return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[contact.supplier_id]))

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='contact_refer_edit')
    elif contact.contact_type == int(CONTACT_TYPES_DICT['Customer']):  # customer tab contact
        return render_to_response('contact-refer.html',
                                  RequestContext(request, {'refer_id': contact.customer_id, 'contact': contact}))
    elif contact.contact_type == int(CONTACT_TYPES_DICT['Supplier']):  # supplier
        return render_to_response('contact-refer.html',
                                  RequestContext(request, {'refer_id': contact.supplier_id, 'contact': contact}))
    elif contact.contact_type == int(CONTACT_TYPES_DICT['Location']):  # location
        return render_to_response('contact-refer.html',
                                  RequestContext(request, {'refer_id': contact.location_id, 'contact': contact}))
    elif contact.contact_type == int(CONTACT_TYPES_DICT['Delivery']):  # delivery
        return render_to_response('contact-refer.html',
                                  RequestContext(request, {'refer_id': contact.delivery_id, 'contact': contact}))
    elif contact.contact_type == int(CONTACT_TYPES_DICT['Consignee']):
        if request.session['url_referer'] and ('customer' in request.session['url_referer']):
            request.session['consignee_type'] = 1
            return render_to_response('contact-refer.html',
                                      RequestContext(request, {'refer_id': contact.customer_id, 'contact': contact}))
        elif request.session['url_referer'] and ('supplier' in request.session['url_referer']):
            request.session['consignee_type'] = 2
            return render_to_response('contact-refer.html',
                                      RequestContext(request, {'refer_id': contact.supplier_id, 'contact': contact}))
        else:
            request.session['consignee_type'] = 0
            del request.session['url_referer']
    else:
        request.session['url_referer'] = request.META['HTTP_REFERER']
        form = ContactForm(company_id, instance=post)
        return render(request, 'contact-form.html', {'form': form, 'contact': contact})


@login_required
@permission_required('contacts.delete_contact', login_url='/alert/')
def contact_refer_delete(request, contact_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        contact = Contact.objects.get(pk=contact_id)
    except:
        messages_error = "Contact does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        try:
            contact.is_hidden = True
            contact.save()
            if contact.contact_type == int(CONTACT_TYPES_DICT['Customer']):  # customer tab contact
                return HttpResponsePermanentRedirect(reverse('customer_edit', args=[contact.customer_id]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Supplier']):  # supplier tab contact
                return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[contact.supplier_id]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Location']):  # location
                return HttpResponsePermanentRedirect(reverse('location_edit', args=[contact.location_id, int(LOCATION_TABS['Contact'])]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Delivery']):  # delivery
                return HttpResponsePermanentRedirect(reverse('delivery_edit', args=[contact.delivery_id]))
            elif contact.contact_type == int(CONTACT_TYPES_DICT['Consignee']):
                if request.session['consignee_type'] == 1:  # customer tab consignee
                    return HttpResponsePermanentRedirect(reverse('customer_edit', args=[contact.customer_id]))
                if request.session['consignee_type'] == 2:  # supplier tab consignee
                    return HttpResponsePermanentRedirect(reverse('supplier_edit', args=[contact.supplier_id]))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='contact_refer_delete')


def str_contact_type(contact_type):
    dict = {'Customer': 1, 'Supplier': 2, 'Location': 3, 'Delivery': 4, 'Consignee': 5}

    for contact_type_str, contact_type_int in dict.items():
        if contact_type == contact_type_int:
            return contact_type_str

    return 'Undefined'


def int_contact_type(contact_type):
    dict = {'Customer': 1, 'Supplier': 2, 'Location': 3, 'Delivery': 4, 'Consignee': 5}

    for contact_type_str, contact_type_int in dict.items():
        if contact_type == contact_type_str:
            return contact_type_int

    return contact_type


def str_contact_owner(field):
    contact_type = field.contact_type

    if contact_type == int(CONTACT_TYPES_DICT['Customer']):
        if field.customer:
            return field.customer.name
    elif contact_type == int(CONTACT_TYPES_DICT['Supplier']):
        if field.supplier:
            return field.supplier.name
    elif contact_type == int(CONTACT_TYPES_DICT['Location']):
        if field.location:
            return field.location.name
    elif contact_type == int(CONTACT_TYPES_DICT['Delivery']):
        if field.delivery:
            return field.delivery.name
    elif contact_type == int(CONTACT_TYPES_DICT['Consignee']):
        if field.consignee:
            return field.consignee.name

    return ''


@login_required
def ContactList__asJson(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Contact.objects.filter(is_hidden=0, company_id=company_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(name__contains=search) |
            Q(fax__contains=search) |
            Q(contact_type__contains=int_contact_type(search)) |
            Q(customer__name__contains=search) |
            Q(supplier__name__contains=search) |
            Q(location__name__contains=search) |
            Q(delivery__name__contains=search) |
            Q(consignee__name__contains=search) |
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
        column_name = "contact_type"
    elif order_column == "3":
        column_name = "consignee__name"
    elif order_column == "4":
        column_name = "phone"
    elif order_column == "5":
        column_name = "fax"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%Y-%m-%d"),
                "contact_name": field.name,
                "contact_type": str_contact_type(field.contact_type),
                "contact_owner": str_contact_owner(field),
                "phone": field.phone,
                "fax": field.fax,
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
