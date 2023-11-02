import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.db.models import F, Q
from django.db.models.functions import Value
from django.forms.formsets import formset_factory
from django.http import HttpResponsePermanentRedirect, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.template import RequestContext

from companies.models import Company
from countries.models import Country
from currencies.models import Currency
from customers.models import CustomerItem, Customer
from items.forms import ItemCategoryForm, PurchaseItemForm
from items.forms import ItemForm, CustomerItemForm, SupplierItemForm, PartSaleItemForm
from items.models import Item, ItemCategory, ItemMeasure
from locations.models import LocationItem, Location
from suppliers.models import Supplier
from suppliers.models import SupplierItem
from utilities.common import get_item_onhandqty
from utilities.constants import TYPE_ITEM_CATEGORY, TRN_CODE_TYPE_DICT, ITEM_TABS


# Create your views here.
@login_required
def load_list(request):
    try:
        return render(request, 'item-list.html')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('items.add_item', login_url='/alert/')
def item_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    form = ItemForm(company_id=company_id, type_flag=3, initial=request.GET)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Save into Item table
                item = Item()
                if request.POST.get('chkActive'):
                    item.is_active = True
                else:
                    item.is_active = False
                item.code = request.POST.get('code')
                if request.POST.get('category'):
                    item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                    item.category_id = item_cat.id
                if request.POST.get('category'):
                    item.category_id = request.POST.get('category')
                if request.POST.get('report_measure'):
                    item.report_measure = ItemMeasure.objects.get(id=int(request.POST.get('report_measure')))
                if request.POST.get('inv_measure'):
                    item.inv_measure = ItemMeasure.objects.get(id=int(request.POST.get('inv_measure')))
                if request.POST.get('sales_measure'):
                    item.sales_measure = ItemMeasure.objects.get(id=int(request.POST.get('sales_measure')))
                if request.POST.get('purchase_measure'):
                    item.purchase_measure = ItemMeasure.objects.get(id=int(request.POST.get('purchase_measure')))
                if request.POST.get('ratio'):
                    item.ratio = request.POST.get('ratio')
                if request.POST.get('person_incharge'):
                    item.person_incharge = request.POST.get('person_incharge')
                if request.POST.get('country'):
                    item.country = Country.objects.get(id=int(request.POST.get('country')))
                if request.POST.get('short_description'):
                    item.short_description = request.POST.get('short_description')
                item.name = request.POST.get('name') if request.POST.get(
                    'name') else ''
                if request.POST.get('model_qty'):
                    item.model_qty = request.POST.get('model_qty')
                if request.POST.get('minimun_order'):
                    item.minimun_order = request.POST.get('minimun_order')
                if request.POST.get('weight'):
                    item.weight = request.POST.get('weight')
                if request.POST.get('par_value'):
                    item.par_value = request.POST.get('par_value')
                if request.POST.get('book_value'):
                    item.book_value = request.POST.get('book_value')
                if request.POST.get('sale_price'):
                    item.sale_price = request.POST.get('sale_price')
                if request.POST.get('purchase_price'):
                    item.purchase_price = request.POST.get('purchase_price')
                if request.POST.get('stockist_price'):
                    item.stockist_price = request.POST.get('stockist_price')
                if request.POST.get('sale_currency'):
                    item.sale_currency = Currency.objects.get(id=int(request.POST.get('sale_currency')))
                else:
                    if request.POST.get('purchase_currency'):
                        item.sale_currency = Currency.objects.get(id=int(request.POST.get('purchase_currency')))
                if request.POST.get('purchase_currency'):
                    item.purchase_currency = Currency.objects.get(id=int(request.POST.get('purchase_currency')))

                if request.POST.get('default_location'):
                    item.default_location_id = request.POST.get('default_location')
                if request.POST.get('default_supplier'):
                    item.default_supplier_id = request.POST.get('default_supplier')
                item.company = Company.objects.get(id=company_id)
                item.create_date = datetime.datetime.today()
                item.update_date = datetime.datetime.today()
                item.update_by = request.user.id
                item.is_hidden = 0
                item.save()
                
                if item.default_location_id:
                    loc_item = LocationItem.objects.filter(location_id=item.default_location_id, item_id=item.id,
                                                            is_hidden=False, is_active=True)
                    if not loc_item:
                        loc_item = LocationItem()
                        loc_item.location_id = item.default_location_id
                        loc_item.item_id = item.id
                        loc_item.onhand_amount = 0
                        loc_item.cost_price = 0
                        loc_item.booked_amount = 0
                        loc_item.create_date = datetime.datetime.today()
                        loc_item.update_date = datetime.datetime.today()
                        loc_item.update_by = request.user.id
                        loc_item.is_hidden = 0
                        loc_item.is_active = 1
                        loc_item.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='item_add')
        return HttpResponsePermanentRedirect(reverse('item_list'))
    return render_to_response('inv-item-add.html',
                              RequestContext(request, {'form': form}))


@login_required
@permission_required('items.change_item', login_url='/alert/')
def item_edit(request, item_id, active_tab_index):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item = Item.objects.none()
    ics_flag = 3
    customeritem_list = CustomerItem.objects.filter(is_hidden=0, is_active=1,
                                                    customer__company_id=company_id, customer__is_hidden=0,
                                                    item_id=item_id)
    supplieritem_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                    supplier__company_id=company_id, supplier__is_hidden=0,
                                                    item_id=item_id)
    try:
        item = Item.objects.get(pk=item_id)
    except:
        messages_error = "Item does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    post = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ItemForm(company_id, ics_flag, request.POST, instance=post)
        try:
            with transaction.atomic():
                # Save changes into Item table
                if request.POST.get('chkActive'):
                    item.is_active = True
                else:
                    item.is_active = False
                item.code = request.POST.get('code')
                if request.POST.get('category'):
                    item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                    item.category_id = item_cat.id
                if request.POST.get('category'):
                    item.category_id = request.POST.get('category')
                if request.POST.get('report_measure'):
                    item.report_measure = ItemMeasure.objects.get(id=int(request.POST.get('report_measure')))
                if request.POST.get('inv_measure'):
                    item.inv_measure = ItemMeasure.objects.get(id=int(request.POST.get('inv_measure')))
                if request.POST.get('sales_measure'):
                    item.sales_measure = ItemMeasure.objects.get(id=int(request.POST.get('sales_measure')))
                if request.POST.get('purchase_measure'):
                    item.purchase_measure = ItemMeasure.objects.get(id=int(request.POST.get('purchase_measure')))
                if request.POST.get('ratio'):
                    item.ratio = request.POST.get('ratio')
                if request.POST.get('person_incharge'):
                    item.person_incharge = request.POST.get('person_incharge')
                if request.POST.get('country'):
                    item.country = Country.objects.get(id=int(request.POST.get('country')))
                if request.POST.get('short_description'):
                    item.short_description = request.POST.get('short_description')
                item.name = request.POST.get('name') if request.POST.get(
                    'name') else ''
                if request.POST.get('model_qty'):
                    item.model_qty = request.POST.get('model_qty')
                if request.POST.get('minimun_order'):
                    item.minimun_order = request.POST.get('minimun_order')
                if request.POST.get('weight'):
                    item.weight = request.POST.get('weight')
                if request.POST.get('par_value'):
                    item.par_value = request.POST.get('par_value')
                if request.POST.get('book_value'):
                    item.book_value = request.POST.get('book_value')
                if request.POST.get('sale_price'):
                    item.sale_price = request.POST.get('sale_price')
                if request.POST.get('purchase_price'):
                    item.purchase_price = request.POST.get('purchase_price')
                if request.POST.get('stockist_price'):
                    item.stockist_price = request.POST.get('stockist_price')
                if request.POST.get('sale_currency'):
                    item.sale_currency = Currency.objects.get(id=int(request.POST.get('sale_currency')))
                else:
                    if request.POST.get('purchase_currency'):
                        item.sale_currency = Currency.objects.get(id=int(request.POST.get('purchase_currency')))
                if request.POST.get('purchase_currency'):
                    item.purchase_currency = Currency.objects.get(id=int(request.POST.get('purchase_currency')))

                if request.POST.get('default_location'):
                    item.default_location_id = request.POST.get('default_location')

                if request.POST.get('default_supplier'):
                    item.default_supplier_id = request.POST.get('default_supplier')
                item.company = Company.objects.get(id=company_id)
                item.create_date = datetime.datetime.today()
                item.update_date = datetime.datetime.today()
                item.update_by = request.user.id
                item.is_hidden = 0
                item.save()
                
                if item.default_location_id:
                    loc_item = LocationItem.objects.filter(location_id=item.default_location_id, item_id=item.id,
                                                            is_hidden=False, is_active=True)
                    if not loc_item:
                        loc_item = LocationItem()
                        loc_item.location_id = item.default_location_id
                        loc_item.item_id = item.id
                        loc_item.onhand_amount = 0
                        loc_item.cost_price = 0
                        loc_item.booked_amount = 0
                        loc_item.create_date = datetime.datetime.today()
                        loc_item.update_date = datetime.datetime.today()
                        loc_item.update_by = request.user.id
                        loc_item.is_hidden = 0
                        loc_item.is_active = 1
                        loc_item.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='item_edit')
        return HttpResponsePermanentRedirect(reverse('item_list'))
    else:
        form = ItemForm(company_id, ics_flag, instance=post)
    if item.last_purchase_date:
        item.last_purchase_date = item.last_purchase_date.strftime("%d-%m-%Y")
    item.update_date = item.update_date.strftime("%d-%m-%Y")
    return render_to_response('inv-item-edit.html', RequestContext(request, {'item': item,
                                                                             'supplieritem_list': supplieritem_list,
                                                                             'customeritem_list': customeritem_list,
                                                                             'active_tab_index': active_tab_index,
                                                                             'form': form}))


@login_required
@permission_required('items.delete_item', login_url='/alert/')
def item_delete(request, item_id):
    if request.method == 'POST':
        try:
            item = Item.objects.get(pk=item_id)
            item.is_active = False
            item.is_hidden = True
            item.save()
            return HttpResponsePermanentRedirect(reverse('item_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='item_delete')


@login_required
def load_category_list(request):

    return render_to_response('category-list.html',
                                RequestContext(request, {'menu_type': '1'}))



@login_required
def load_inv_category_list(request):

    return render_to_response('category-list.html',
                                RequestContext(request, {'menu_type': '3'}))
                                


@login_required
@permission_required('items.add_itemcategory', login_url='/alert/')
def category_add(request, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    is_inventory = company.is_inventory
    if request.method == 'POST':
        form = ItemCategoryForm(company_id, request.POST)
        if form.is_valid():
            try:
                my_category = form.save(commit=False)
                # if request.POST.get('tax') is None or request.POST.get('tax') == '':
                #     my_category.tax_id = None
                if request.POST.get('type') and request.POST.get('type') != '':
                    my_category.type = request.POST.get('type')
                my_category.company_id = company_id
                my_category.create_date = datetime.datetime.today()
                my_category.update_date = datetime.datetime.today()
                my_category.update_by = request.user.id
                my_category.is_hidden = 0
                my_category.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='category_add')
            return HttpResponsePermanentRedirect(reverse('category_list'))
        else:
            form = ItemCategoryForm(company_id, request.POST)
    else:
        form = ItemCategoryForm(company_id=company_id)
    return render(request, 'category-form.html', {'form': form, 'type_category': TYPE_ITEM_CATEGORY, 'is_inventory': is_inventory, 'menu_type': menu_type})


@login_required
@permission_required('items.change_itemcategory', login_url='/alert/')
def category_edit(request, category_id, menu_type):
    category = ItemCategory.objects.get(pk=category_id)
    post = get_object_or_404(ItemCategory, pk=category_id)
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    is_inventory = company.is_inventory
    if request.method == 'POST':
        form = ItemCategoryForm(company_id, request.POST, instance=post)
        if form.is_valid():
            try:
                my_category = form.save(commit=False)
                if request.POST.get('type') and request.POST.get('type') != '':
                    my_category.type = request.POST.get('type')
                my_category.update_date = datetime.datetime.today()
                my_category.update_by = request.user.id
                my_category.is_hidden = 0
                my_category.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='category_edit')
            return HttpResponsePermanentRedirect(reverse('category_list'))
    else:
        form = ItemCategoryForm(company_id, instance=category)
    category.update_date = category.update_date.strftime("%d-%m-%Y")
    return render(request, 'category-form.html',
                  {'form': form, 'category': category, 'is_inventory': is_inventory, 'type_category': TYPE_ITEM_CATEGORY, 'menu_type': menu_type})


@login_required
@permission_required('items.delete_itemcategory', login_url='/alert/')
def category_delete(request, category_id):
    if request.method == 'POST':
        try:
            my_category = ItemCategory.objects.get(pk=category_id)
            my_category.is_hidden = True
            my_category.save()
            return HttpResponsePermanentRedirect(reverse('category_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='category_delete')


def get_supplier_code_by_name(request, supplier_name):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1,
                                       name=supplier_name).first()
    json_supplier_code = ''
    if supplier:
        json_supplier_code = json.dumps(supplier.code, cls=DjangoJSONEncoder)
    return HttpResponse(json_supplier_code, content_type="application/json")


@login_required
def load_measure_list(request):
    return render(request, 'measure-list.html')


@login_required
@permission_required('items.add_itemmeasure', login_url='/alert/')
def measure_add(request):
    if request.method == 'POST':
        try:
            my_measure = ItemMeasure()
            my_measure.name = request.POST.get('name')
            my_measure.code = request.POST.get('code')
            my_measure.is_active = True
            my_measure.create_date = datetime.datetime.today()
            my_measure.update_date = datetime.datetime.today()
            my_measure.update_by = request.user.id
            my_measure.is_hidden = 0
            my_measure.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='measure_add')
        return HttpResponsePermanentRedirect(reverse('measure_list'))
    return render(request, 'measure-form.html')


@login_required
@permission_required('items.change_itemmeasure', login_url='/alert/')
def measure_edit(request, measure_id):
    my_measure = ItemMeasure.objects.get(pk=measure_id)
    if request.method == 'POST':
        try:
            my_measure.name = request.POST.get('name')
            my_measure.code = request.POST.get('code')
            my_measure.is_active = True
            my_measure.create_date = datetime.datetime.today()
            my_measure.update_date = datetime.datetime.today()
            my_measure.update_by = request.user.id
            my_measure.is_hidden = 0
            my_measure.save()
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='measure_edit')
        return HttpResponsePermanentRedirect(reverse('measure_list'))
    my_measure.update_date = my_measure.update_date.strftime("%d-%m-%Y")
    return render(request, 'measure-form.html', {'measure': my_measure})


@login_required
@permission_required('items.delete_itemmeasure', login_url='/alert/')
def measure_delete(request, measure_id):
    if request.method == 'POST':
        try:
            my_measure = ItemMeasure.objects.get(pk=measure_id)
            my_measure.is_hidden = True
            my_measure.is_active = False
            my_measure.save()
            return HttpResponsePermanentRedirect(reverse('measure_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='measure_delete')


@login_required
@permission_required('customers.add_customeritem', login_url='/alert/')
def customeritem_add(request, item_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':

        select_customer_id = request.POST.get('hdCustomerSelected')
        form = CustomerItemForm(company_id, request.POST)
        if select_customer_id == None or select_customer_id == '':
            messages_error = "Please select the correct customer!"
            return render_to_response('customer-item-form.html', RequestContext(request,
                                                                                {'form': form, 'item_id': item_id,
                                                                                 'messages_error': messages_error,
                                                                                 'item': item
                                                                                 }))
        else:
            all_customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id) \
                .values_list('customer_id', flat=True)
            if select_customer_id and int(select_customer_id) not in all_customer_item:
                customer_item = CustomerItem()
                customer_item.create_date = datetime.datetime.today()
            else:
                customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id,
                                                            customer_id=select_customer_id).first()
            if customer_item:
                try:
                    customer_item.customer_id = int(select_customer_id)
                    customer_item.item_id = item_id
                    customer_item.currency_id = request.POST.get('currency')
                    if request.POST.get('sales_price'):
                        customer_item.sales_price = request.POST.get('sales_price')
                        customer_item.new_price = request.POST.get('sales_price')
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
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='customeritem_add')
                return HttpResponsePermanentRedirect(reverse('item_edit', args=[item_id, int(ITEM_TABS['Load Stock'])]))
    else:
        form = CustomerItemForm(company_id)
    return render(request, 'customer-item-form.html',
                  {'form': form, 'item_id': item_id, 'item': item})


@login_required
@permission_required('customers.change_customeritem', login_url='/alert/')
def customeritem_edit(request, customeritem_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        get = get_object_or_404(CustomerItem, pk=customeritem_id)
        customer_item = CustomerItem.objects.get(pk=customeritem_id)
        customer = Customer.objects.get(pk=customer_item.customer_id)
        item = Item.objects.get(id=customer_item.item_id)
    except:
        messages_error = "Customer Item does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        select_customer_id = request.POST.get('hdCustomerSelected')
        form = CustomerItemForm(company_id, request.POST, instance=get)
        if select_customer_id == None or select_customer_id == '':
            messages_error = "Please select the correct customer!"
            return render_to_response('customer-item-form.html', RequestContext(request,
                                                                                {'form': form,
                                                                                 'customeritem': customer_item,
                                                                                 'item_id': customer_item.item_id,
                                                                                 'messages_error': messages_error,
                                                                                 'item': item}))
        else:
            all_customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=customer_item.item_id) \
                .values_list('customer_id', flat=True)

            if select_customer_id and (int(select_customer_id) not in all_customer_item
                                       or int(select_customer_id) == customer_item.customer_id):
                customer_item = CustomerItem.objects.get(pk=customeritem_id)
            else:
                customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1,
                                                            customer__company_id=company_id,
                                                            item_id=customer_item.item_id,
                                                            customer_id=select_customer_id).first()
            if form.is_valid() and customer_item:
                try:
                    customer_item.customer_id = int(select_customer_id)
                    customer_item.currency_id = request.POST.get('currency')
                    if request.POST.get('sales_price'):
                        customer_item.sales_price = request.POST.get('sales_price')
                        customer_item.new_price = request.POST.get('sales_price')
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
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='customeritem_add')
                return HttpResponsePermanentRedirect(
                    reverse('item_edit', args=[customer_item.item_id, int(ITEM_TABS['Load Stock'])]))
    else:
        form = CustomerItemForm(company_id, instance=get)
    return render_to_response('customer-item-form.html', RequestContext(request, {'form': form,
                                                                                  'customeritem': customer_item,
                                                                                  'customer': customer, 'item': item}))


@login_required
@permission_required('customers.delete_customeritem', login_url='/alert/')
def customeritem_delete(request, customeritem_id):
    if request.method == 'POST':
        try:
            customeritem = CustomerItem.objects.get(pk=customeritem_id)
            customeritem.is_active = 0
            customeritem.is_hidden = 1
            customeritem.update_by = request.user.id
            customeritem.update_date = datetime.datetime.today()
            customeritem.save()
            return HttpResponsePermanentRedirect(
                reverse('item_edit', args=[customeritem.item_id, int(ITEM_TABS['Load Stock'])]))
        except:
            messages_error = "Customer Item does not exist."
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('suppliers.add_supplieritem', login_url='/alert/')
def supplieritem_add(request, item_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        form = SupplierItemForm(company_id, request.POST)
        select_supplier_id = request.POST.get('hdSupplierSelected')
        if select_supplier_id == None or select_supplier_id == '':
            messages_error = "Please select the correct supplier!"
            return render_to_response('supplier-item-form.html', RequestContext(request,
                                                                                {'form': form, 'item_id': item_id,
                                                                                 'messages_error': messages_error,
                                                                                 'item': item}))
        else:
            all_supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            supplier__company_id=company_id, supplier__is_hidden=0,
                                                            item_id=item_id). \
                values_list('supplier_id', flat=True)
            # add new supplier to this item
            if select_supplier_id and int(select_supplier_id) not in all_supplier_item:
                supplier_item = SupplierItem()
                supplier_item.create_date = datetime.datetime.today()
            # edit the existing supplier of this item
            else:
                supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            item_id=item_id, supplier_id=select_supplier_id).first()
            if supplier_item:
                try:
                    supplier_item.supplier_id = int(request.POST.get('hdSupplierSelected'))
                    supplier_item.item_id = item_id
                    supplier_item.currency_id = request.POST.get('currency')
                    if request.POST.get('purchase_price'):
                        supplier_item.purchase_price = request.POST.get('purchase_price')
                        supplier_item.new_price = request.POST.get('purchase_price')
                    if request.POST.get('leading_days'):
                        supplier_item.leading_days = request.POST.get('leading_days')
                    if request.POST.get('effective_date'):
                        supplier_item.effective_date = request.POST.get('effective_date')
                    if request.POST.get('is_active'):
                        supplier_item.is_active = 1
                    else:
                        supplier_item.is_active = 0
                    supplier_item.update_date = datetime.datetime.today()
                    supplier_item.update_by = request.user.id
                    supplier_item.is_hidden = 0
                    supplier_item.save()
                    # add default supplier to this item
                    if not item.default_supplier_id:
                        item.default_supplier_id = int(request.POST.get('hdSupplierSelected'))
                        item.save()
                    return HttpResponsePermanentRedirect(reverse('item_edit', args=[item_id, int(ITEM_TABS['Item'])]))
                except OSError as e:
                    print(e)
                    messages.add_message(request, messages.ERROR, e, extra_tags='supplier_item_add')

    else:
        form = SupplierItemForm(company_id)
    return render(request, 'supplier-item-form.html',
                  {'form': form, 'item_id': item_id, 'item': item})


@login_required
@permission_required('suppliers.change_supplieritem', login_url='/alert/')
def supplieritem_edit(request, supplieritem_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        post = get_object_or_404(SupplierItem, pk=supplieritem_id)
        supplier_item = SupplierItem.objects.get(pk=supplieritem_id)
        supplier = Supplier.objects.get(pk=supplier_item.supplier_id)
        item = Item.objects.get(id=supplier_item.item_id)
        all_supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        supplier__company_id=company_id, supplier__is_hidden=0,
                                                        item_id=supplier_item.item_id) \
            .values_list('supplier_id', flat=True)
    except ObjectDoesNotExist:
        messages_error = "Supplier Item does not exist."
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))
    if request.method == 'POST':
        form = SupplierItemForm(company_id, request.POST, instance=post)
        select_supplier_id = request.POST.get('hdSupplierSelected')
        if select_supplier_id == None or select_supplier_id == '':
            messages_error = "Please select the correct supplier!"
            return render_to_response('supplier-item-form.html', RequestContext(request,
                                                                                {'form': form,
                                                                                 'supplieritem': supplier_item,
                                                                                 'item_id': supplier_item.item_id,
                                                                                 'messages_error': messages_error,
                                                                                 'item': item}))
        else:
            if select_supplier_id and (int(select_supplier_id) not in all_supplier_item
                                       or int(select_supplier_id) == supplier_item.supplier_id):
                supplier_item = SupplierItem.objects.get(pk=supplieritem_id)
            else:
                supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                            item_id=supplier_item.item_id,
                                                            supplier_id=select_supplier_id).first()
            if supplier_item:
                try:
                    supplier_item.supplier_id = int(select_supplier_id)
                    supplier_item.currency_id = request.POST.get('currency')
                    if request.POST.get('purchase_price'):
                        supplier_item.purchase_price = request.POST.get('purchase_price')
                        supplier_item.new_price = request.POST.get('purchase_price')
                    if request.POST.get('leading_days'):
                        supplier_item.leading_days = request.POST.get('leading_days')
                    else:
                        supplier_item.leading_days = None
                    if request.POST.get('effective_date'):
                        supplier_item.effective_date = request.POST.get('effective_date')
                    else:
                        supplier_item.effective_date = None
                    if request.POST.get('is_active'):
                        supplier_item.is_active = 1
                    else:
                        supplier_item.is_active = 0
                    supplier_item.create_date = datetime.datetime.today()
                    supplier_item.update_date = datetime.datetime.today()
                    supplier_item.update_by = request.user.id
                    supplier_item.is_hidden = 0
                    supplier_item.save()
                    return HttpResponsePermanentRedirect(
                        reverse('item_edit', args=[supplier_item.item_id, int(ITEM_TABS['Item'])]))
                except OSError as e:
                    messages.add_message(request, messages.ERROR, e, extra_tags='supplier_item_edit')
    else:
        form = SupplierItemForm(company_id, instance=post)
    return render(request, 'supplier-item-form.html', {'form': form,
                                                       'supplier': supplier,
                                                       'supplieritem': supplier_item,
                                                       'item': item})


@login_required
@permission_required('suppliers.delete_supplieritem', login_url='/alert/')
def supplieritem_delete(request, supplieritem_id):
    if request.method == 'POST':
        try:
            supplier_item = SupplierItem.objects.get(pk=supplieritem_id)
            supplier_item.is_hidden = True
            supplier_item.is_active = False
            supplier_item.update_by = request.user.id
            supplier_item.update_date = datetime.datetime.today()
            supplier_item.save()
            return HttpResponsePermanentRedirect(
                reverse('item_edit', args=[supplier_item.item_id, int(ITEM_TABS['Item'])]))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='supplier_item_delete')
        except ObjectDoesNotExist:
            messages_error = "Supplier Item does not exist."
            return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def load_list_pagination(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    try:
        items_list = Item.objects.filter(is_hidden=0, company_id=company_id, code__icontains='') \
            .order_by('-update_date')
        paginator = Paginator(items_list, 10)  # Show 10 contacts per page

        page = request.GET.get('page')
        try:
            items_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            items_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            items_list = paginator.page(paginator.num_pages)
        return render_to_response('item-list.html', RequestContext(request, {'items_list': items_list}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


def load_list_condition(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    search_input = request.POST.get('search_input')
    if search_input is None:
        search_input = request.POST.get('search_input_get')
    if search_input is None:
        search_input = ''
    try:
        items_list_all = Item.objects.filter(is_hidden=0, company_id=company_id)
        items_list = items_list_all.filter(code__icontains=search_input) | \
                     items_list_all.filter(category__name__icontains=search_input) | \
                     items_list_all.filter(name__icontains=search_input)
        paginator = Paginator(items_list, 10)  # Show 10 contacts per page

        page = request.POST.get('prev_page')
        if page is None or page == '':
            page = request.POST.get('next_page')
        try:
            items_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            items_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            items_list = paginator.page(paginator.num_pages)
        return render_to_response('item-list.html', RequestContext(request, {'items_list': items_list,
                                                                             'search_input': search_input}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def ItemList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = Item.objects.filter(is_hidden=0, company_id=company_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search.upper()) | Q(name__contains=search.upper()) |
            Q(category__name__contains=search.upper()) | Q(update_date__contains=search.upper()) |
            Q(sale_currency__code__contains=search.upper()) |
            Q(purchase_currency__code__contains=search.upper()))

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
        column_name = "category__name"
    elif order_column == "4":
        column_name = "sale_price"
    elif order_column == "5":
        column_name = "purchase_price"
    elif order_column == "6":
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
                "item_code": field.code if field.code else '',
                "item_name": field.name if field.name else '',
                "category_name": field.category.name if field.category else '',
                "sale_price": (field.sale_currency.code if field.sale_currency else '') + ' ' + \
                              str(field.sale_price if field.sale_price else '0.00000'),
                "purchase_price": (field.purchase_currency.code if field.purchase_currency else '') + ' ' + \
                                  str(field.purchase_price if field.purchase_price else '0.00000'),
                # "quantity": str(get_item_onhandqty(field.id)), "is_active": str(field.is_active),
                "quantity": str(get_item_onhandqty(field.id)) if get_item_onhandqty(field.id) > 0 else '0.00',
                "minimun_order": str(field.minimun_order if field.minimun_order else '0.00'),
                "inv_measure": str(field.inv_measure.code if field.inv_measure else ''),
                "backorder_qty": str(field.backorder_qty if field.backorder_qty else '0.00'),
                "sales_measure": str(field.sales_measure.code if field.sales_measure else ''),
                "purchase_measure": str(field.purchase_measure.code if field.purchase_measure else ''),
                "model_qty": str(field.model_qty if field.model_qty else '0.00')}
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
def ItemList_by_location__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    id_loc = request.GET['id_loc']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = LocationItem.objects.filter(is_hidden=0, item__company_id=company_id)
    if int(id_loc) > 0:
        location = Location.objects.get(pk=id_loc)
        list_filter = list_filter.filter(location_id=location.id)
    records_total = list_filter.count()
    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(item__code__contains=search.upper()) |
            Q(item__category__name__contains=search.upper()) |
            Q(update_date__contains=search.upper()))
    # All data
    records_filtered = list_filter.count()
    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "item__code"
    elif order_column == "2":
        column_name = "min_qty"
    elif order_column == "3":
        column_name = "max_qty"
    elif order_column == "4":
        column_name = "reorder_qty"
    elif order_column == "5":
        column_name = "onhand_qty"
    elif order_column == "10":
        column_name = "sales_measure"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]
    # Create data list
    array = []
    for field in list:
        data = {"item_id": field.item.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "item_code": field.item.code,
                "item_name": field.item.name,
                "category_name": field.item.category.name if field.item.category else '',
                "sale_price": str(field.item.sale_price) + ' ' + \
                              field.item.sale_currency.code if field.item.sale_currency else '',
                "purchase_price": str(field.item.purchase_price) + ' ' + \
                                  field.item.purchase_currency.code if field.item.purchase_currency else '',
                "quantity": str(field.onhand_qty) if (field and field.onhand_qty != None) else '0.00',
                "minimun_qty": str(field.min_qty if (field and field.min_qty != None) else '0.00'),
                "maximum_qty": str(field.max_qty if (field and field.max_qty != None) else '0.00'),
                "reorder_qty": str(field.reorder_qty if (field and field.reorder_qty != None) else '0.00'),
                "inv_measure": str(field.item.inv_measure.code if field.item.inv_measure else ''),
                "backorder_qty": str(field.reorder_qty), "location": field.location.name if field.location else '',
                "location_id": field.location.id if field.location else ''}
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
def PartSaleItemList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    list_filter = Item.objects.filter(is_hidden=0, company_id=company_id).exclude(code__isnull=True).exclude(code='')
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__icontains=search) | Q(name__icontains=search) |
            Q(category__name__icontains=search) | Q(update_date__icontains=search) |
            Q(sale_currency__code__icontains=search) |
            Q(purchase_currency__code__icontains=search))

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
        column_name = "category__name"
    elif order_column == "4":
        column_name = "sale_price"
    elif order_column == "5":
        column_name = "purchase_price"
    elif order_column == "6":
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
                "item_code": field.code,
                "item_name": field.short_description,
                "category_name": field.category.name if field.category else '',
                "sale_price": intcomma("%.6f" % field.sale_price),
                "purchase_price": intcomma("%.6f" % field.purchase_price),
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
def MeasureList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    measure_list = ItemMeasure.objects.filter(is_hidden=0)
    records_total = measure_list.count()

    if search:  # Filter data base on search
        measure_list = measure_list.filter(
            Q(name__contains=search) |
            Q(code__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = measure_list.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "name"
    elif order_column == "2":
        column_name = "code"

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = measure_list.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = measure_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "name": field.name,
                "code": field.code, "is_active": str(field.is_active)}

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
def get_customer_info(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            customer_code = request.POST.get('customer_code')
            item_id = request.POST.get('item_id')
            customer = Customer.objects.filter(code__contains=customer_code, is_hidden=0, company_id=company_id,
                                               is_active=1).first()
            customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id,
                                                        customer_id=customer.id).first()

            response_data = {'id': customer.id,
                             'name': customer.name,
                             'code': customer.code,
                             'currency_id': customer.currency.id if customer.currency else 0,
                             'sale_price': '0'}
            if customer_item:
                response_data['sale_price'] = str(customer_item.sales_price if customer_item.sales_price else 0)

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_customer_info')
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")


@login_required
def get_supplier_info(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            supplier_code = request.POST.get('supplier_code')
            item_id = request.POST.get('item_id')
            supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1,
                                               code__contains=supplier_code).first()
            supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                        item_id=item_id, supplier_id=supplier.id).first()

            response_data = {'id': supplier.id,
                             'name': supplier.name,
                             'code': supplier.code,
                             'currency_id': supplier.currency.id if supplier.currency else 0,
                             'purchase_price': '0'}
            if supplier_item:
                response_data['purchase_price'] = str(
                    supplier_item.purchase_price if supplier_item.purchase_price else 0)

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_supplier_info')
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")


@login_required
def CustomerList__asJson(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']

    # if request.GET['filter'] and request.GET['filter'] != '':
    if request.POST.get('filter') and request.POST.get('filter') != '':
        # customer_code = request.GET['filter']
        customer_code = request.POST.get('filter')
        list_filter = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1, code=customer_code)
    else:
        list_filter = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

    if 'exclude_customer_list' in request.GET:
        exclude_customer_list = request.GET['exclude_customer_list']
        exclude_customer_list = json.loads(exclude_customer_list)
        list_filter.exclude(id__in=exclude_customer_list)

    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__icontains=search) | Q(name__icontains=search) |
            Q(country__code__icontains=search) |
            Q(location__code__icontains=search) |
            Q(currency__code__icontains=search) |
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
                "code": field.code,
                "name": field.name,
                "country_code": field.country.code if field.country else '',
                "location_code": field.location.code if field.location else '',
                "currency_code": field.currency.code if field.currency else '',
                "currency_id": str(field.currency.id if field.currency else 0)}
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
def SupplierList__asJson(request):
    draw = request.POST['draw']
    start = request.POST['start']
    length = request.POST['length']
    search = request.POST['search[value]']

    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.POST.get('filter') and request.POST.get('filter') != '':
        supplier_code = request.POST.get('filter')
        list_filter = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1, code=supplier_code)
    else:
        list_filter = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)

    if request.POST.get('exclude_item_list'):
        exclude_item_json = request.POST.get('exclude_item_list')
        exclude_item_list = json.loads(exclude_item_json)
        list_filter = list_filter.exclude(id__in=exclude_item_list)

    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) | Q(name__contains=search) |
            Q(country__code__contains=search) |
            Q(currency__code__contains=search) |
            Q(update_date__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.POST['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "code"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "3":
        column_name = "country__code"
    elif order_column == "4":
        column_name = "currency__code"

    order_dir = request.POST['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%Y-%m-%d"),
                "code": field.code,
                "name": field.name if field.name else '',
                "country_code": field.country.code if field.country else '',
                "currency_code": field.currency.code if field.currency else '',
                "currency_id": str(field.currency.id if field.currency else 0)}
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
def CustomerEditItemList__asJson(request, item_id):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    customeritem_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id)
    records_total = customeritem_list.count()

    if search:  # Filter data base on search
        customeritem_list = customeritem_list.filter(
            Q(customer__name__contains=search.upper()) | Q(sales_price__contains=search.upper()) | Q(
                leading_days__contains=search.upper()) |
            Q(customer__code__contains=search.upper()) | Q(currency__code__contains=search.upper())
            | Q(effective_date__contains=search.upper()) |
            Q(update_date__contains=search.upper()))

    # All data
    records_filtered = customeritem_list.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "customer__code"
    elif order_column == "2":
        column_name = "customer__name"
    elif order_column == "3":
        column_name = "sales_price"
    elif order_column == "4":
        column_name = "effective_date"
    elif order_column == "5":
        column_name = "leading_days"

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = customeritem_list.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = customeritem_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "name": field.customer.name,
                "code": field.customer.code,
                "sale_price": str(field.sales_price) + ' ' + str(field.currency.code),
                "effective_date": field.effective_date.strftime("%d-%m-%Y") if field.effective_date else '',
                "leading_days": str(field.leading_days) if field.leading_days else '',
                "is_active": str(field.is_active)
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
def SupplierEditItemList__asJson(request, item_id):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    supplier_list = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                supplier__company_id=company_id, supplier__is_hidden=0,
                                                item_id=item_id)
    records_total = supplier_list.count()

    if search:  # Filter data base on search
        supplier_list = supplier_list.filter(
            Q(supplier__name__contains=search.upper()) | Q(purchase_price__contains=search.upper()) |
            Q(leading_days__contains=search.upper()) | Q(supplier__code__contains=search.upper()) |
            Q(currency__code__contains=search.upper()) | Q(effective_date__contains=search.upper()) |
            Q(update_date__contains=search.upper()))

    # All data
    records_filtered = supplier_list.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "supplier__code"
    elif order_column == "2":
        column_name = "supplier__name"
    elif order_column == "3":
        column_name = "purchase_price"
    elif order_column == "4":
        column_name = "effective_date"
    elif order_column == "5":
        column_name = "leading_days"

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = supplier_list.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = supplier_list.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "supplier_name": field.supplier.name,
                "supplier_code": field.supplier.code,
                "purchase_price": str(field.purchase_price) + ' ' + str(field.currency.code),
                "effective_date": field.effective_date.strftime("%d-%m-%Y") if field.effective_date else '',
                "leading_days": str(field.leading_days) if field.leading_days else '',
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
def Loc_ItemList__asJson(request, item_id):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']

    locationitem = LocationItem.objects.filter(item_id=item_id, is_hidden=0)
    records_total = locationitem.count()

    if search:
        locationitem = locationitem.filter(
            Q(location__name__icontains=search) |
            Q(location__code__icontains=search) |
            Q(onhand_qty__contains=search) |
            Q(booked_qty__contains=search) |
            Q(min_qty__contains=search) |
            Q(max_qty__contains=search) |
            Q(last_open_qty__contains=search)
        )
    # All data
    records_filtered = locationitem.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "location__name"
    elif order_column == "1":
        column_name = "location__code"
    elif order_column == "2":
        column_name = "onhand_qty"
    elif order_column == "3":
        column_name = "booked_qty"
    elif order_column == "4":
        column_name = "min_qty"
    elif order_column == "5":
        column_name = "max_qty"

    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = locationitem.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = locationitem.order_by('-' + column_name)[int(start):(int(start) + int(length))]
    # Create data list
    array = []
    for field in list:
        onhand_qty = str(field.onhand_qty if field.onhand_qty else 0)
        booked_qty = str(field.booked_qty if field.booked_qty else 0)
        ready_for_sales_qty = str(float(onhand_qty) - float(booked_qty)) if onhand_qty and float(onhand_qty) > 0 else 0
        data = {"id": field.id,
                "item_id": field.item_id,
                "location_id": field.location_id,
                "location_name": field.location.name if field.location.name else '',
                "location_code": field.location.code if field.location.code else '',
                "onhand_qty": onhand_qty,
                "booked_qty": booked_qty,
                "ready_for_sales_qty": ready_for_sales_qty,
                "min_qty": str(field.min_qty if field.min_qty else 0),
                "max_qty": str(field.max_qty if field.max_qty else 0)}
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
def purchase_item_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    inventory = {
        'item': Item.objects.filter(is_hidden=0, company_id=company_id).count(),
        'using_inventory': Company.objects.get(pk=company_id).is_inventory
    }
    return render(request, 'purchase-item-list.html', inventory)


@login_required
def load_list_purchase_item_as_json(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        draw = request.GET['draw']
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        list_filter = Item.objects.filter(is_hidden=0, company_id=company_id).exclude(code__isnull=True).exclude(code='')
        records_total = list_filter.count()

        if search:  # Filter data base on search
            list_filter = list_filter.filter(
                Q(code__icontains=search) | Q(name__icontains=search) |
                Q(category__name__icontains=search) | Q(update_date__icontains=search) |
                Q(purchase_currency__code__icontains=search))

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
            column_name = "category__name"
        elif order_column == "4":
            column_name = "purchase_price"
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
                    "item_code": field.code,
                    "item_name": field.short_description,
                    "category_name": field.category.name if field.category else '',
                    "purchase_price": intcomma("%.6f" % field.purchase_price),
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
    return HttpResponse(json.dumps("", ensure_ascii=False), content_type='application/json')


@login_required
@permission_required('items.add_item', login_url='/alert/')
def purchase_item_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    all_part_number = Item.objects.filter(is_hidden=0, company_id=company_id).order_by('name')
    supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1, )
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, company_id=company_id)
        try:
            with transaction.atomic():
                if request.POST.get('new_part') == 'on':
                    if form.is_valid():
                        item = form.save(commit=False)
                        if request.POST.get('code'):
                            item.code = request.POST.get('code')
                        if request.POST.get('category'):
                            item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                            item.category_id = item_cat.id
                        item.company_id = company_id
                        item.is_hidden = 0
                        item.create_date = datetime.datetime.today()
                        item.update_date = datetime.datetime.today()
                        item.update_by = request.user.id
                        item.save()

                        suppliers = json.loads(request.POST.get('suppliers_json'))
                        for suppItem in suppliers:
                            supplier = Supplier.objects.get(pk=suppItem[0])
                            s_item = SupplierItem()
                            s_item.supplier_id = int(suppItem[0])
                            s_item.item_id = item.id
                            s_item.is_active = 1
                            s_item.create_date = datetime.datetime.today()
                            s_item.update_date = datetime.datetime.today()
                            s_item.update_by = request.user.id
                            s_item.is_hidden = 0
                            s_item.purchase_price = suppItem[1].replace(',', '') if suppItem[1] else 0
                            s_item.leading_days = suppItem[2] if suppItem[2] else None
                            s_item.effective_date = suppItem[3].split('-')[2] + '-' + suppItem[3].split('-')[1] + '-' + suppItem[3].split('-')[0] if suppItem[3] else None
                            s_item.new_price = suppItem[4].replace(',', '') if suppItem[4] else None
                            s_item.currency_id = supplier.currency_id if supplier.currency else 0
                            s_item.save()

                        # Update default Supplier of Item
                        if item and not item.default_supplier:
                            item.default_supplier_id = int(suppliers[0][0])
                            item.save()
                else:
                    item_id = request.POST.get('part_number_axis')
                    item = Item.objects.get(pk=item_id, is_hidden=0, company_id=company_id)
                    supplieritems = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                supplier__company_id=company_id, supplier__is_hidden=0,
                                                                item_id=item.id)
                    form = PurchaseItemForm(request.POST, instance=item, company_id=company_id)
                    supplieritems_ids = supplieritems.values_list('supplier_id', flat=True)
                    suppliers_remain = []
                    if form.is_valid():
                        item = form.save(commit=False)
                        item.company_id = company_id
                        if request.POST.get('code'):
                            item.code = request.POST.get('code')
                        if request.POST.get('category'):
                            item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                            item.category_id = item_cat.id
                        item.is_hidden = 0
                        item.update_date = datetime.datetime.today()
                        item.update_by = request.user.id
                        item.save()

                        suppliers = json.loads(request.POST.get('suppliers_json'))
                        for suppItem in suppliers:
                            supplier = Supplier.objects.get(pk=suppItem[0])
                            s_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                 supplier_id=supplier.id, item_id=item.id).first()
                            if not s_item:
                                s_item = SupplierItem()
                                s_item.supplier_id = int(suppItem[0])
                                s_item.item_id = item.id
                                s_item.is_active = 1
                                s_item.is_hidden = 0
                            s_item.update_date = datetime.datetime.today()
                            s_item.update_by = request.user.id

                            s_item.purchase_price = suppItem[1].replace(',', '') if suppItem[1] else 0
                            s_item.leading_days = round(float(suppItem[2]), 2) if suppItem[2] else None
                            if suppItem[3]:
                                date_array = suppItem[3].split('-')
                                effective_date = date_array[2] + '-' + date_array[1] + '-' + date_array[0]
                                s_item.effective_date = effective_date
                            else:
                                s_item.effective_date = None

                            s_item.new_price = suppItem[4].replace(',', '') if suppItem[4] else None
                            s_item.currency_id = supplier.currency_id if supplier.currency else 0
                            s_item.save()

                            suppliers_remain.append(s_item.supplier_id)
                        # remove suppliers
                        remove_suppliers = list(set(supplieritems_ids) - set(suppliers_remain))
                        for rm_supp in remove_suppliers:
                            supplier = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                   supplier_id=rm_supp, item_id=item.id)
                            for supp in supplier:
                                supp.is_hidden = 1
                                supp.update_date = datetime.datetime.today()
                                supp.update_by = request.user.id
                                supp.save()

                        # Update default Supplier of Item
                        if item and not item.default_supplier:
                            item.default_supplier_id = int(suppliers[0][0])
                            item.save()

                    messages.add_message(request, messages.SUCCESS, 'Purchase Item is successfully created. Now edit Sales Item', extra_tags='part_sale_add')
                    return redirect('/items/part_sale_edit/' + str(item.id) + '/')

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='purchase_item_add')
            return render(request, 'purchase-item-form.html', context={'form': form})
        return HttpResponsePermanentRedirect(reverse('purchase_item_list'))
    form = PurchaseItemForm(request.GET, company_id=company_id)
    return render_to_response('purchase-item-form.html', RequestContext(request,
                                                                        {'form': form, 'supplier_list': supplier_list,
                                                                         'all_part_number': all_part_number, 'isnew': 0,
                                                                         'company': company}))


@permission_required('items.change_item', login_url='/alert/')
def purchase_item_edit(request, item_id):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        item = Item.objects.get(pk=item_id, is_hidden=0, company_id=company_id)
        supplieritems = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                    supplier__company_id=company_id, supplier__is_hidden=0,
                                                    item_id=item.id)
        supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
        if request.method == 'POST':
            form = PurchaseItemForm(request.POST, instance=item, company_id=company_id)
            supplieritems_ids = supplieritems.values_list('supplier_id', flat=True)
            suppliers_remain = []
            try:
                with transaction.atomic():
                    if form.is_valid():
                        item = form.save(commit=False)
                        item.company_id = company_id
                        if request.POST.get('code'):
                            item.code = request.POST.get('code')
                        if request.POST.get('category'):
                            item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                            item.category_id = item_cat.id
                        item.is_hidden = 0
                        item.update_date = datetime.datetime.today()
                        item.update_by = request.user.id
                        item.save()

                        suppliers = json.loads(request.POST.get('suppliers_json'))
                        for suppItem in suppliers:
                            supplier = Supplier.objects.get(pk=suppItem[0])
                            s_item = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                 supplier_id=supplier.id, item_id=item.id).first()
                            if not s_item:
                                s_item = SupplierItem()
                                s_item.supplier_id = int(suppItem[0])
                                s_item.item_id = item.id
                                s_item.is_active = 1
                                s_item.is_hidden = 0
                            s_item.update_date = datetime.datetime.today()
                            s_item.update_by = request.user.id

                            s_item.purchase_price = suppItem[1].replace(',', '') if suppItem[1] else 0
                            s_item.leading_days = round(float(suppItem[2]), 2) if suppItem[2] else None
                            if suppItem[3]:
                                date_array = suppItem[3].split('-')
                                effective_date = date_array[2] + '-' + date_array[1] + '-' + date_array[0]
                                s_item.effective_date = effective_date
                            else:
                                s_item.effective_date = None

                            s_item.new_price = suppItem[4].replace(',', '') if suppItem[4] else None
                            s_item.currency_id = supplier.currency_id if supplier.currency else 0
                            s_item.save()

                            suppliers_remain.append(s_item.supplier_id)
                        # remove suppliers
                        remove_suppliers = list(set(supplieritems_ids) - set(suppliers_remain))
                        for rm_supp in remove_suppliers:
                            supplier = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                                   supplier_id=rm_supp, item_id=item.id)
                            for supp in supplier:
                                supp.is_hidden = 1
                                supp.update_date = datetime.datetime.today()
                                supp.update_by = request.user.id
                                supp.save()

                        # Update default Supplier of Item
                        if item and not item.default_supplier:
                            item.default_supplier_id = int(suppliers[0][0])
                            item.save()

            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='purchase_item_add')
                return render(request, 'purchase-item-form.html', context={'form': form})
            return HttpResponsePermanentRedirect(reverse('purchase_item_list'))

        form = PurchaseItemForm(instance=item, company_id=company_id)
        existing_suppliers = '['
        for supplier_item in supplieritems:
            existing_suppliers = \
                existing_suppliers + '["' + str(supplier_item.supplier.code) + '", "' + str(
                    supplier_item.supplier.name if supplier_item.supplier.name else '') + \
                '", "' + str(supplier_item.currency.code if supplier_item.currency else \
                    supplier_item.supplier.currency.code if supplier_item.supplier.currency else '') + '", "' + \
                str(supplier_item.purchase_price) + '", "' + str(supplier_item.leading_days) + '", "' + \
                str(supplier_item.effective_date.strftime("%d-%m-%Y") if supplier_item.effective_date else '') + '", "' + str(
                    supplier_item.new_price) + '", "' + \
                str(supplier_item.update_date.strftime("%d-%m-%Y")) + '", "' + str(supplier_item.supplier_id) + '", ],'
        existing_suppliers += ']'
        return render_to_response('purchase-item-form.html',
                                  RequestContext(request,
                                                 {'form': form, 'existing_suppliers': existing_suppliers, 'isnew': 1,
                                                  'item_id': item_id, 'supplier_list': supplier_list}))
    except Exception as e:
        print(e)
        return render_to_response('404.html',
                                  RequestContext(request, {'messages_error': "Oops, you've found a glitch!\n"
                                                                             "Please contact your Administrators!"}))


@login_required
@permission_required('items.delete_item', login_url='/alert/')
def purchase_item_delete(request, item_id):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        item = Item.objects.get(pk=item_id, is_hidden=0, company_id=company_id)
        supplieritems = SupplierItem.objects.filter(is_hidden=0, is_active=1,
                                                    item_id=item.id,
                                                    supplier__company_id=company_id, supplier__is_hidden=0)
        with transaction.atomic():
            item.is_hidden = 1
            item.update_date = datetime.datetime.today()
            item.update_by = request.user.id
            item.save()
            # bulk update supplier item
            supplieritems.update(is_hidden=1, update_date=datetime.datetime.today(), update_by=request.user.id)

            return HttpResponsePermanentRedirect(reverse('purchase_item_list'))
    except OSError as e:
        messages.add_message(request, messages.ERROR, e, extra_tags='purchase_item_add')
        return render(request, '404.html', context={'messages_error': "Oops, you've found a glitch!\n"
                                                                      "Please contact your Administrators!"})


@login_required
def part_sale_list(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        inventory = {
            'item': Item.objects.filter(is_hidden=0, company_id=company_id).count(),
            'using_inventory': Company.objects.get(pk=company_id).is_inventory
        }
        return render(request, 'part_sale_price_list.html', inventory)
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist." \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def part_sale_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    customer_list = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    CustomerItemFormSet = formset_factory(PartSaleItemForm)
    all_part_number = Item.objects.filter(is_hidden=0, company_id=company_id).order_by('name')
    type_flag = 2
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Save into Item table
                if request.POST.get('new_part') == 'on':
                    formset_customer_item = CustomerItemFormSet(request.POST, prefix='formset_customer_item')
                    form = ItemForm(company_id, type_flag, request.POST)
                    if form.is_valid():
                        item = form.save(commit=False)
                        if request.POST.get('code'):
                            item.code = request.POST.get('code')
                        if request.POST.get('category'):
                            item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                            item.category_id = item_cat.id
                        item.company_id = company_id
                        item.create_date = datetime.datetime.today()
                        item.update_date = datetime.datetime.today()
                        item.update_by = request.user.id
                        item.is_hidden = 0
                        item.save()
                        if formset_customer_item.is_valid():
                            for form in formset_customer_item:
                                customer_item = CustomerItem()
                                customer_item.customer_id = form.cleaned_data.get('customer_id')
                                customer_item.item_id = item.id
                                customer_item.currency_id = form.cleaned_data.get('currency_id')
                                customer_item.sales_price = form.cleaned_data.get('sales_price').replace(',', '')
                                customer_item.new_price = form.cleaned_data.get('new_price').replace(',', '')
                                customer_item.leading_days = form.cleaned_data.get('leading_days')
                                if form.cleaned_data.get('effective_date') != None and form.cleaned_data.get(
                                        'effective_date') != '':
                                    customer_item.effective_date = form.cleaned_data.get('effective_date')
                                else:
                                    customer_item.effective_date = None
                                customer_item.update_date = form.cleaned_data.get('update_date')
                                customer_item.update_by = request.user.id
                                customer_item.is_hidden = 0
                                customer_item.save()

                            messages.add_message(request, messages.SUCCESS, 'Sales Item is successfully created. Now edit Puchase Item', extra_tags='part_sale_add')
                            return redirect('/items/purchase-item/edit/' + str(item.id) + '/')

                        else:
                            print(formset_customer_item.errors)
                    else:
                        print(form.errors)
                else:
                    item_id = request.POST.get('part_number_axis')
                    item = get_object_or_404(Item, pk=item_id)
                    customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item.id)
                    formset_customer_item = CustomerItemFormSet(request.POST, prefix='formset_customer_item')
                    form = ItemForm(company_id, type_flag, request.POST, instance=item)
                    if form.is_valid():
                        item = form.save(commit=False)
                        if request.POST.get('code'):
                            item.code = request.POST.get('code')
                        if request.POST.get('category'):
                            item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                            item.category_id = item_cat.id
                        item.company_id = company_id
                        item.update_date = datetime.datetime.today()
                        item.update_by = request.user.id
                        item.is_hidden = 0
                        item.save()
                        if formset_customer_item.is_valid():
                            customer_item.update(is_hidden=True)
                            for formset in formset_customer_item:
                                customerItem = CustomerItem()
                                customerItem.customer_id = formset.cleaned_data.get('customer_id')
                                customerItem.item_id = item.id
                                customerItem.currency_id = formset.cleaned_data.get('currency_id')
                                customerItem.sales_price = (formset.cleaned_data.get('sales_price')).replace(',', '')
                                customerItem.new_price = (formset.cleaned_data.get('new_price')).replace(',', '')
                                customerItem.leading_days = formset.cleaned_data.get('leading_days')
                                if formset.cleaned_data.get('effective_date') != None and formset.cleaned_data.get(
                                        'effective_date') != '':
                                    customerItem.effective_date = formset.cleaned_data.get('effective_date')
                                else:
                                    customerItem.effective_date = None
                                customerItem.update_date = datetime.datetime.now()
                                customerItem.update_by = request.user.id
                                customerItem.is_hidden = 0
                                customerItem.save()

                            messages.add_message(request, messages.SUCCESS, 'Sales Item is successfully Updated. Now edit Puchase Item', extra_tags='part_sale_add')
                            return redirect('/items/purchase-item/edit/' + str(item.id) + '/')

                        else:
                            print(formset_customer_item.errors)
                
                    else:
                        print(form.errors)

        except Exception as e:
            print(e)
            messages.add_message(request, messages.ERROR, e, extra_tags='part_sale_add')
        return HttpResponsePermanentRedirect(reverse('part_sale_list'))
    else:
        form = ItemForm(company_id=company_id, type_flag=type_flag)
        initial = [{'line_number': 1, 'update_date': datetime.date.today().strftime('%d-%m-%Y')}]
        formset_customer_item = CustomerItemFormSet(initial=initial, prefix='formset_customer_item')
        # formset_customer_item = CustomerItemFormSet(prefix='formset_customer_item')
    return render_to_response('part_sale_price.html',
                              RequestContext(request, {'form': form, 'formset_customer_item': formset_customer_item,
                                                       'all_part_number': all_part_number, 'isnew': 0,
                                                       'company': company, 'request_method': request.method,
                                                       'customer_list': customer_list}))


@login_required
def part_json_item(request, item_id):
    all_part_number = Item.objects.get(pk=item_id)
    array = []
    data = {"code": all_part_number.code,
            "name": all_part_number.name,
            "short_description": all_part_number.short_description,
            "quantity": intcomma("%.2f" % get_item_onhandqty(item_id)),
            "category": all_part_number.category_id,
            "sale_currency": all_part_number.sale_currency_id,
            "purchase_currency": all_part_number.purchase_currency_id,
            "sale_price": intcomma("%.6f" % all_part_number.sale_price),
            "purchase_price": intcomma("%.6f" % all_part_number.purchase_price),
            "stockist_price": intcomma("%.6f" % all_part_number.stockist_price),
            'cost_price': intcomma("%.6f" % all_part_number.cost_price),
            "retail_price": intcomma("%.6f" % all_part_number.retail_price),
            'last_purchase_price': intcomma("%.6f" % all_part_number.last_purchase_price),
            "last_purchase_doc": all_part_number.last_purchase_doc,
            "minimun_order": intcomma("%.2f" % all_part_number.minimun_order), "size": all_part_number.size,
            "weight": all_part_number.weight, "po_qty": intcomma("%.2f" % all_part_number.po_qty),
            "so_qty": intcomma("%.2f" % all_part_number.so_qty),
            "backorder_qty": intcomma("%.2f" % all_part_number.backorder_qty),
            "in_qty": intcomma("%.2f" % all_part_number.in_qty),
            "out_qty": intcomma("%.2f" % all_part_number.out_qty),
            "balance_qty": intcomma("%.2f" % all_part_number.balance_qty),
            "balance_amount": intcomma("%.2f" % all_part_number.balance_amount) if all_part_number.balance_amount else '0.00',
            "par_value": all_part_number.par_value,
            "book_value": all_part_number.book_value,
            "is_active": all_part_number.is_active,
            "update_by": all_part_number.update_by,
            "country": all_part_number.country_id,
            "inv_measure": all_part_number.inv_measure_id,
            "sales_measure": all_part_number.sales_measure_id,
            "purchase_measure": all_part_number.purchase_measure_id,
            "report_measure": all_part_number.report_measure_id,
            "model_qty": all_part_number.model_qty,
            "person_incharge": all_part_number.person_incharge,
            "ratio": intcomma("%.2f" % all_part_number.ratio),
            'default_supplier': all_part_number.default_supplier.id if all_part_number.default_supplier else None,
            'default_location': all_part_number.default_location.id if all_part_number.default_location else None}
    array.append(data)
    customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id)
    customers = []
    for cust_item in customer_item:
        data = {}
        data['customer_code'] = cust_item.customer.code
        data['sales_price'] = intcomma("%.6f" % cust_item.sales_price) if cust_item.sales_price else '0.0'
        data['new_price'] = intcomma("%.6f" % cust_item.new_price) if cust_item.new_price else '0.0'
        data['leads'] = str(cust_item.leading_days) if cust_item.leading_days else '0'
        data['effective_date'] = cust_item.effective_date.strftime("%d-%m-%Y") if cust_item.effective_date else ''
        data['update_date'] = cust_item.update_date.strftime("%d-%m-%Y") if cust_item.update_date else ''

        customers.append(data)

    supplier_item = SupplierItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id)
    suppliers = []
    for cust_item in supplier_item:
        data = {}
        data['customer_code'] = cust_item.supplier.code
        data['sales_price'] = intcomma("%.6f" % cust_item.purchase_price) if cust_item.purchase_price else '0.0'
        data['new_price'] = intcomma("%.6f" % cust_item.new_price) if cust_item.new_price else '0.0'
        data['leads'] = str(cust_item.leading_days) if cust_item.leading_days else '0'
        data['effective_date'] = cust_item.effective_date.strftime("%d-%m-%Y") if cust_item.effective_date else ''
        data['update_date'] = cust_item.update_date.strftime("%d-%m-%Y") if cust_item.update_date else ''

        suppliers.append(data)

    content = {"data": array, 'customers': customers, 'suppliers': suppliers}
    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def part_sale_edit(request, item_id):
    type_flag = 2
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    item = get_object_or_404(Item, pk=item_id)
    customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id).values() \
        .annotate(customer_code=F('customer__code')) \
        .annotate(customer_name=F('customer__name')) \
        .annotate(currency_code=F('currency__code')) \
        .annotate(line_number=Value(0, output_field=models.CharField()))
    for i, j in enumerate(customer_item):
        if i < customer_item.__len__():
            i += 1
            j['line_number'] = i
            j['update_date'] = j['update_date'].strftime("%d-%m-%Y")
            j['effective_date'] = j['effective_date'].strftime("%d-%m-%Y") if j['effective_date'] else ''
    customer_list = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    CustomerItemFormSet = formset_factory(PartSaleItemForm)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Save into Item table
                formset_customer_item = CustomerItemFormSet(request.POST, prefix='formset_customer_item',
                                                            initial=customer_item)
                form = ItemForm(company_id, type_flag, request.POST, instance=item)
                if form.is_valid():
                    item = form.save(commit=False)
                    if request.POST.get('code'):
                        item.code = request.POST.get('code')
                    if request.POST.get('category'):
                        item_cat = ItemCategory.objects.get(id=int(request.POST.get('category')))
                        item.category_id = item_cat.id
                    item.company_id = company_id
                    item.create_date = datetime.datetime.today()
                    item.update_date = datetime.datetime.today()
                    item.update_by = request.user.id
                    item.is_hidden = 0
                    item.save()
                    if formset_customer_item.is_valid():
                        CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id).delete()
                        for formset in formset_customer_item:
                            customerItem = CustomerItem()
                            customerItem.customer_id = formset.cleaned_data.get('customer_id')
                            customerItem.item_id = item.id
                            customerItem.currency_id = formset.cleaned_data.get('currency_id')
                            customerItem.sales_price = formset.cleaned_data.get('sales_price').replace(',', '')
                            customerItem.new_price = formset.cleaned_data.get('new_price').replace(',', '')
                            customerItem.leading_days = formset.cleaned_data.get('leading_days')
                            if formset.cleaned_data.get('effective_date') != None and formset.cleaned_data.get(
                                    'effective_date') != '':
                                customerItem.effective_date = formset.cleaned_data.get('effective_date')
                            else:
                                customerItem.effective_date = None
                            customerItem.update_date = datetime.datetime.now()
                            customerItem.update_by = request.user.id
                            customerItem.is_hidden = 0
                            customerItem.save()
                    else:
                        print(formset_customer_item.errors)
            
                else:
                    print(form.errors)

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='part_sale_edit')
        return HttpResponsePermanentRedirect(reverse('part_sale_list'))
    else:
        type_flag = 2
        form = ItemForm(company_id=company_id, type_flag=type_flag, instance=item)
        if len(customer_item):
            formset_customer_item = CustomerItemFormSet(prefix='formset_customer_item', initial=customer_item)
        else:
            initial = [{'line_number': 1, 'update_date': datetime.date.today().strftime('%d-%m-%Y')}]
            formset_customer_item = CustomerItemFormSet(initial=initial, prefix='formset_customer_item')
    return render_to_response('part_sale_price.html',
                              RequestContext(request,
                                             {'form': form, 'formset_customer_item': formset_customer_item, 'isnew': 1,
                                              'request_method': request.method, 'item_id': item_id,
                                              'customer_list': customer_list}))


@login_required
def part_sale_delete(request, item_id):
    if request.method == 'POST':
        try:
            item = Item.objects.get(pk=item_id)
            item.is_active = False
            item.is_hidden = True
            item.save()
            customer_item = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id=item_id)
            for customer in customer_item:
                customer.is_active = False
                customer.is_hidden = True
                customer.save()
            return HttpResponsePermanentRedirect(reverse('part_sale_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='part_sale_delete')


@login_required
def CategoryList__asJson(request, menu_type):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    item_category = ItemCategory.objects.filter(is_hidden=0, company_id=company_id)
    if int(menu_type) < 2:
        list_filter = item_category.filter(type__lte=2) | item_category.filter(type=None)
    else:
        list_filter = item_category.filter(type__gte=2) | item_category.filter(type=None)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(
            Q(code__contains=search) |
            Q(name__contains=search) |
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
def get_customer_info1(request):
    if request.method == 'POST':
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            customer_code = request.POST.get('customer_code')
            customer = Customer.objects.filter(code=customer_code, is_hidden=0, company_id=company_id,
                                               is_active=1).first()
            if customer:
                response_data = {'id': customer.id,
                                 'name': customer.name,
                                 'code': customer.code,
                                 'currency_id': customer.currency.id if customer.currency else 0,
                                 'currency_code': customer.currency.code if customer.currency else 0}
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"Fail": "Can not find Customer"}), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_customer_info1')
            return HttpResponse(json.dumps({"Fail": e}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")


@login_required
def get_supplier_info1(request):
    if request.method == 'POST':
        try:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            supplier_code = request.POST.get('supplier_code')

            supplier = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1,
                                               code=supplier_code).first()
            if supplier:
                response_data = {'id': supplier.id,
                                 'name': supplier.name,
                                 'code': supplier.code,
                                 'currency_id': supplier.currency.id if supplier.currency else 0,
                                 'currency_code': supplier.currency.code if supplier.currency else 0}
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"Fail": "Can not find Supplier"}), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_supplier_info1')
            return HttpResponse(json.dumps({"Fail": e}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")


@login_required
def get_item_info(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            item_code = request.POST.get('item_code')
            item_type = request.POST.get('item_type')

            item = Item.objects.filter(is_hidden=0, code__contains=item_code, company_id=company_id).first()
            if item:
                response_data = {'id': item.id,
                                 'name': item.name,
                                 'code': item.code}
                # return HttpResponse(json.dumps(response_data), content_type="application/json")
                if int(item_type) == 1:
                    return HttpResponseRedirect(reverse('part_sale_edit', kwargs={'item_id': item.id}))
                else:
                    return HttpResponseRedirect(reverse('purchase_item_edit', kwargs={'item_id': item.id}))
            else:
                return HttpResponse(json.dumps({"Fail": "Can not find Item"}), content_type="application/json")
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='get_item_info')
            return HttpResponse(json.dumps({"Fail": e}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"Fail": "this isn't happening"}), content_type="application/json")
