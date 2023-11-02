import calendar
import datetime
import json
import os
from decimal import Decimal
from io import BytesIO
from dateutil.relativedelta import relativedelta
from django.conf import settings as s
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q, F
from django.db.models import Sum, ExpressionWrapper
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from base64 import b64encode
from reportlab.pdfgen import canvas
from accounting.models import Journal
from companies.models import Company
from currencies.models import Currency, ExchangeRate
from customers.models import Customer, Delivery
from items.models import Item, ItemCategory
from orders.models import Order, OrderItem
from taxes.models import Tax
from locations.models import Location, LocationItem
from reports.Print_AP_vendor_Label import Print_AP_vendor_Label
from reports.Print_AP_vendor_letter import Print_AP_vendor_letter
from reports.Print_AR_customers import Print_AR_customers
from reports.Print_AR_customers_Label import Print_AR_customers_Label
from reports.Print_AR_customers_letter import Print_AR_customers_letter
from reports.Print_GLProfitLoss_XLS import Print_GLProfitLoss_XLS
from reports.Print_GLProfitLoss_XLS_new import Print_GLProfitLoss_XLS_new
from reports.Print_GLTrial_XLS import Print_GLTrial_XLS
from reports.Print_Tax_Auth import Print_Tax_Auth
from reports.Print_Tracking_item import Print_Tracking_item
from reports.Print_Tax_Auth_XLS import Print_Tax_Auth_XLS
from reports.Print_Tracking_item_XLS import Print_Tracking_item_XLS
from reports.Print_stock_value import Print_stock_value
from reports.Print_years_IR4900 import Print_years_IR4900
from reports.forms import ReportForm
from reports.models import Report
from reports.print_APAgedTrial_Detail import Print_APAgedTrialDetail
from reports.print_APAgedTrial_Summary import Print_APAgedTrialSummary
from reports.print_ARAgedTrial_Detail import Print_ARAgedTrialDetail
from reports.print_ARAgedTrial_Summary import Print_ARAgedTrialSummary
from reports.Print_ARAgedTrialDetail_XLS import Print_ARAgedTrialDetail_XLS
from reports.Print_ARAgedTrialSummary_XLS import Print_ARAgedTrialSummary_XLS
from reports.Print_APAgedTrialDetail_XLS import Print_APAgedTrialDetail_XLS
from reports.Print_APAgedTrialSummary_XLS import Print_APAgedTrialSummary_XLS
from reports.print_CL2100 import Print_CL2100
from reports.print_CL2400 import Print_CL2400
from reports.print_DL2400 import Print_DL2400
from reports.print_GL2200 import Print_GL2200
from reports.print_SL2100 import Print_SL2100
from reports.print_SL2100_XLS import Print_SL2100_XLS
from reports.print_SL2200 import Print_SL2200
from reports.print_SL2200_XLS import Print_SL2200_XLS
from reports.print_SL2201 import Print_SL2201
from reports.print_SL2201_XLS import Print_SL2201_XLS
from reports.print_SL3300 import Print_SL3300
from reports.print_SL3301 import Print_SL3301
from reports.print_SL3A00 import Print_SL3A00
from reports.print_SL3A01 import Print_SL3A01
from reports.print_TL1200 import Print_TL1200
from reports.print_GLBalance_Sheet import Print_GLBalanceSheet
from reports.print_GLBalance_Sheet_new import Print_GLBalanceSheet_new
from reports.print_GLBalance_Sheet_XLS import Print_GLBalanceSheet_XLS
from reports.print_GLBalance_Sheet_XLS_new import Print_GLBalanceSheet_XLS_new
from reports.print_GLFunction import Print_GLFunction
from reports.print_GLFunction_XLS import GLFunction_XLS
from reports.print_GLFunction_Balance import Print_GLFunctionBalance
from reports.print_GLFunction_Balance_XLS import GLFunction_Balance_XLS
from reports.print_GLFunction_Balance_Batch import Print_GLFunctionBalanceBatch
from reports.print_BatchNumber import Print_BatchNumber
from reports.print_GLFunction_Balance_Batch_XLS import GLFunction_Balance_Batch_XLS
from reports.print_GLFunction_Batch import Print_GLFunctionBatch
from reports.print_GLFunction_Batch_XLS import GLFunction_Batch_XLS
from reports.print_GLProfit_Loss import Print_GLProfitLoss
from reports.print_GLProfit_Loss_new import Print_GLProfitLoss_new
from reports.print_GLSource import Print_GLSource
from reports.print_GLSource_XLS import GLSource_XLS
from reports.print_GLSource_Balance import Print_GLSourceBalance
from reports.print_GLSource_Balance_XLS import GLSource_Balance_XLS
from reports.print_GLSource_Balance_Batch import Print_GLSourceBalanceBatch
from reports.print_GLSource_Balance_Batch_XLS import GLSource_Balance_Batch_XLS
from reports.print_GLSource_Batch import Print_GLSourceBatch
from reports.print_GLSource_Batch_XLS import GLSource_Batch_XLS
from reports.print_GLTrial_Balance_Sheet import Print_GLTrialBalanceSheet
from reports.print_GLTrial_Net_Sheet import Print_GLTrialNetSheet
from reports.print_Nothing import Print_Nothing
from reports.print_SR8800 import Print_SR8800
from reports.print_SR8801 import Print_SR8801
from reports.print_SR8400 import Print_SR8400
from reports.print_SR8300 import Print_SR8300
from reports.print_SR8301 import Print_SR8301
from reports.print_SR7101 import Print_SR7101
from reports.print_SR7101_XLS import Print_SR7101_XLS
from reports.print_SR7102 import Print_SR7102
from reports.print_SR7102_XLS import Print_SR7102_XLS
from reports.print_SR7103 import Print_SR7103
from reports.print_SR7103_XLS import Print_SR7103_XLS
from reports.print_SR7201 import Print_SR7201
from reports.print_SR7201_XLS import Print_SR7201_XLS
from reports.print_SR7202 import Print_SR7202
from reports.print_SR7202_XLS import Print_SR7202_XLS
from reports.print_SR7203 import Print_SR7203
from reports.print_SR7203_XLS import Print_SR7203_XLS
from reports.print_SR7204 import Print_SR7204
from reports.print_SR7204_XLS import Print_SR7204_XLS
from reports.print_SR7205 import Print_SR7205
from reports.print_SR7206 import Print_SR7206
from reports.print_SR7300 import Print_SR7300
from reports.print_SR7301 import Print_SR7301
from reports.print_SR7302 import Print_SR7302
from reports.print_SR7303 import Print_SR7303
from reports.print_SR7303_XLS import Print_SR7303_XLS
from reports.print_SR7401 import Print_SR7401
from reports.print_SR7402 import Print_SR7402
from reports.print_SR7402_XLS import Print_SR7402_XLS
from reports.print_SR7403 import Print_SR7403
from reports.print_SR7403_XLS import Print_SR7403_XLS
from reports.print_SR7404 import Print_SR7404
from reports.print_SR7404_XLS import Print_SR7404_XLS
from reports.print_SR7405 import Print_SR7405
from reports.print_SR7501 import Print_SR7501
from reports.print_SR7501_XLS import Print_SR7501_XLS
from reports.print_SR7502 import Print_SR7502
from reports.print_SR7502_XLS import Print_SR7502_XLS
from reports.print_SR7503 import Print_SR7503
from reports.print_SR7503_XLS import Print_SR7503_XLS
from reports.print_SR7504 import Print_SR7504
from reports.print_SR7504_XLS import Print_SR7504_XLS
from reports.print_SR7601 import Print_SR7601
from reports.print_SR7602 import Print_SR7602
from reports.print_SR7603 import Print_SR7603
from reports.print_SR7603_XLS import Print_SR7603_XLS
from reports.print_SR8500 import Print_SR8500
from reports.print_SR8500_XLS import Print_SR8500_XLS
from reports.print_SR8600 import Print_SR8600
from reports.print_SR8600_XLS import Print_SR8600_XLS
from reports.print_SR8601 import Print_SR8601
from reports.print_SR8601_XLS import Print_SR8601_XLS
from reports.print_SR8602 import Print_SR8602
from reports.print_SR8602_XLS import Print_SR8602_XLS
from reports.print_SR8603 import Print_SR8603
from reports.print_SR8603_XLS import Print_SR8603_XLS
from reports.print_SR8700 import Print_SR8700
from reports.print_SR8700_1 import Print_SR8700_1
from reports.print_SR8701 import Print_SR8701
from reports.print_ST_IL2601 import Print_ST_IL2601
from reports.print_STOutBalance import Print_STOutBalance
from reports.print_ST_IR4200 import print_ST_IR4200
from reports.print_ST_IR4300 import print_ST_IR4300
from reports.print_ST_IR4600 import print_ST_IR4600
from reports.print_Tax_Tracking import Print_Tax_Tracking
from reports.print_do_order import Print_DO_Order
from reports.print_order import Print_Order
from reports.print_packing_list import Print_Packing_List
from reports.print_po_order import Print_PO_Order
from reports.print_po_orders import Print_PO_Orders
from reports.print_AR_note import Print_AR_Note
from reports.print_tax_invoice import Print_Tax_Invoice
from reports.print_invoice import Print_Invoice
from reports.print_shipping_invoice import Print_Shipping_Invoice
from reports.print_shipping_invoice_2 import Print_Shipping_Invoice_2
from reports.print_AP_revaluation import Print_AP_revaluation
from reports.print_AR_revaluation import Print_AR_revaluation
from reports.print_GL_revaluation import Print_GL_revaluation
from staffs.models import Staff
from suppliers.models import Supplier
from utilities.common import send_email, get_orderitem_filter_range, get_vendor_filter_range, get_customer_filter_range
from utilities.constants import ORDER_TYPE, ORDER_STATUS, EMAIL_MSG_CONST, TRANSACTION_TYPES, STATUS_TYPE_DICT, \
    CUSTOMER_DEFAULT_MSG, VENDOR_DEFAULT_MSG
from django.contrib.humanize.templatetags.humanize import intcomma
from accounting.models import Batch
from reports.helpers.aged_trial_report import get_ar_transactions


@login_required
def print_order(request, order_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_Order(buffer, 'A4')
    pdf = report.print_report(order_id, company_id)

    response.write(pdf)
    return response


@login_required
def print_po_order(request, order_id, print_header, remove_address, address=0, signature=1, part_group=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_PO_Order(buffer, 'A4')
    pdf = report.print_report(order_id, print_header, company_id, address, remove_address, signature, part_group)

    response.write(pdf)
    return response


@login_required
def print_po_orders(request, from_order_id, to_order_id, print_header, remove_address, address=0, signature=1, part_group=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_PO_Orders(buffer, 'A4')
    pdf = report.print_report(from_order_id, to_order_id, print_header, address, company_id, remove_address, signature, part_group)

    response.write(pdf)
    return response


@login_required
def print_packing_list(request, order_id, print_header, part_group=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_Packing_List(buffer, 'A4')
    if part_group is None or part_group is '':
        part_group = 0
    pdf = report.print_report(order_id, print_header, company_id, part_group)

    response.write(pdf)
    return response


@login_required
def print_po_order_pdf(request, order_id, print_header):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order = Order.objects.get(pk=order_id)
    response = HttpResponse(content_type='application/pdf')
    if order:
        response['Content-Disposition'] = 'attachment; filename="%s_%s.pdf' % \
                                          (order.document_number, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    else:
        response['Content-Disposition'] = 'attachment; filename="PO_%s.pdf' % \
                                          datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_PO_Order(buffer, 'A4')
    pdf = report.print_report(order_id, print_header, company_id, 0, 0, 1, 0)

    response.write(pdf)
    return response


@login_required
def print_tax_invoice(request, order_id, print_header, part_group=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_Tax_Invoice(buffer, 'A4')
    if part_group is None or part_group is '':
        part_group = 0
    pdf = report.print_report(order_id, print_header, company_id, part_group)

    response.write(pdf)
    return response


@login_required
def print_invoice(request, order_id, print_header, part_group=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_Invoice(buffer, 'A4')
    if part_group is None or part_group is '':
        part_group = 0
    pdf = report.print_report(order_id, print_header, company_id, part_group)

    response.write(pdf)
    return response


@login_required
def print_shipping_invoice(request, order_id, print_header, part_group=0, address=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_Shipping_Invoice(buffer, 'A4')
    if part_group is None or part_group is '':
        part_group = 0
    pdf = report.print_report(order_id, print_header, company_id, part_group, address)

    response.write(pdf)
    return response


@login_required
def print_shipping_invoice_2(request, order_id, print_header, part_group=0, address=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_Shipping_Invoice_2(buffer, 'A4')
    if part_group is None or part_group is '':
        part_group = 0
    pdf = report.print_report(order_id, print_header, company_id, part_group, address)

    response.write(pdf)
    return response


@login_required
def print_do_order(request, order_id, print_header, part_group=0):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_DO_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_DO_Order(buffer, 'A4')
    if part_group is None or part_group is '':
        part_group = 0
    pdf = report.print_report(order_id, print_header, company_id, part_group)

    response.write(pdf)
    return response


@login_required
@csrf_exempt
def print_SR7102(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    part_group = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7102_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7102(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, part_group)

    response.write(b64encode(pdf))
    return response


@login_required
def print_SR7102_excel(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    part_group = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7102_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7102_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, part_group)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7101(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    cust_po = request.POST.get('param2')
    part_no = request.POST.get('param3')
    is_confirm = request.POST.get('param4')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7101_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7101(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, cust_po, part_no, is_confirm)

    response.write(b64encode(pdf))
    return response


@login_required
def print_SR7101_excel(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    cust_po = request.POST.get('param2')
    part_no = request.POST.get('param3')
    is_confirm = request.POST.get('param4')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7101_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7101_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, cust_po, part_no, is_confirm)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_SR7103_excel(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    cust_po = request.POST.get('param2')
    part_no = request.POST.get('param3')
    customer_code = request.POST.get('param4')
    is_confirm = request.POST.get('param5')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7103_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7103_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, cust_po, part_no, customer_code, is_confirm)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7103(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    cust_po = request.POST.get('param2')
    part_no = request.POST.get('param3')
    customer_code = request.POST.get('param4')
    is_confirm = request.POST.get('param5')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7103_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7103(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, cust_po, part_no, customer_code, is_confirm)

    response.write(b64encode(pdf))
    return response


@login_required
def print_SR7206(request, date_from, date_to, supplier_no):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7206_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7206(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no)

    response.write(pdf)
    return response


@login_required
def print_SR7405(request, date_from, date_to, customer_code):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7405_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7405(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, customer_code)

    response.write(pdf)
    return response


@login_required
def print_SR8600(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8600_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')

    buffer = BytesIO()
    report = Print_SR8600(buffer, 'A4')
    pdf = report.print_report(company_id, from_data[1], from_data[0], to_data[1], to_data[0])

    response.write(pdf)
    return response


@login_required
def print_xls_SR8600(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR8600_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR8600_XLS(output)

    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')

    xlsx_report = xls.WriteToExcel(company_id, from_data[1], from_data[0], to_data[1], to_data[0])

    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_xls_SR8601(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR8601_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR8601_XLS(output)
    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')
    try:
        xlsx_report = xls.WriteToExcel(company_id, from_data[1], from_data[0], to_data[1], to_data[0])
    except Exception as e:
        print(e)
        xlsx_report = xls.WriteToExcel(company_id, datetime.datetime.today().month, datetime.datetime.today().year,
                        datetime.datetime.today().month, datetime.datetime.today().year)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_SR8601(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8601_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    # if array_data.__len__() >= 2:
    buffer = BytesIO()
    report = Print_SR8601(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, from_data[1], from_data[0], to_data[1], to_data[0])
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year, 
                    datetime.datetime.today().month, datetime.datetime.today().year)

    response.write(pdf)
    return response


@login_required
def print_xls_SR8602(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR8602_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR8602_XLS(output)
    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')
    try:
        xlsx_report = xls.WriteToExcel(company_id, from_data[1], from_data[0], to_data[1], to_data[0])
    except Exception as e:
        print(e)
        xlsx_report = xls.WriteToExcel(company_id, datetime.datetime.today().month, datetime.datetime.today().year,
                        datetime.datetime.today().month, datetime.datetime.today().year)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_SR8602(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8602_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8602(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, from_data[1], from_data[0], to_data[1], to_data[0])
    except Exception as e:
        print(e)
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year,
                    datetime.datetime.today().month, datetime.datetime.today().year)

    response.write(pdf)
    return response


@login_required
def print_xls_SR8603(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR8603_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR8603_XLS(output)
    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')
    try:
        xlsx_report = xls.WriteToExcel(company_id, from_data[1], from_data[0], to_data[1], to_data[0])
    except Exception as e:
        print(e)
        xlsx_report = xls.WriteToExcel(company_id, datetime.datetime.today().month, datetime.datetime.today().year,
                        datetime.datetime.today().month, datetime.datetime.today().year)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_SR8603(request, from_month, to_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    from_data = str(from_month).split('-')
    to_data = str(to_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8603_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8603(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, from_data[1], from_data[0], to_data[1], to_data[0])
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year,
                datetime.datetime.today().month, datetime.datetime.today().year)

    response.write(pdf)
    return response


@login_required
def print_SR8700(request, select_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8700_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8700(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, array_data[1], array_data[0])
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year)

    response.write(pdf)
    return response


@login_required
def print_SR8700_1(request, select_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8700_1_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8700_1(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, array_data[1], array_data[0])
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year)

    response.write(pdf)
    return response


@login_required
def print_SR8701(request, select_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8701_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8701(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, array_data[1], array_data[0])
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year)

    response.write(pdf)
    return response


@login_required
@csrf_exempt
def print_SR7601(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    select_month = request.POST.get('param0')
    category = request.POST.get('param1')
    print_selection = request.POST.get('param2')
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7601_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7601(buffer, 'A4')
    try:
        pdf = report.print_report(company_id, array_data[1], array_data[0], category, print_selection)
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year, category, print_selection)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7602(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    select_month = request.POST.get('param0')
    customer_code = request.POST.get('param1')
    print_selection = request.POST.get('param2')
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7602_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7602(buffer, 'A4')
    try:
        pdf = report.print_report(
            company_id, array_data[1], array_data[0], print_selection, customer_code)
    except:
        pdf = report.print_report(company_id, datetime.datetime.today().month, datetime.datetime.today().year,
                                  print_selection, customer_code)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7303(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    wanted_from = request.POST.get('param2')
    wanted_to = request.POST.get('param3')
    supplier_code = request.POST.get('param4')
    document_no = request.POST.get('param5')
    customer_po = request.POST.get('param6')
    part_no = request.POST.get('param7')
    sort_by = request.POST.get('param8')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7303_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7303(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to, wanted_from, wanted_to, supplier_code, document_no, customer_po, part_no, sort_by)
    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7303(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    wanted_from = request.POST.get('param2')
    wanted_to = request.POST.get('param3')
    supplier_code = request.POST.get('param4')
    document_no = request.POST.get('param5')
    customer_po = request.POST.get('param6')
    part_no = request.POST.get('param7')
    sort_by = request.POST.get('param8')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7303_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7303_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, issue_from, issue_to, wanted_from, wanted_to, supplier_code, document_no, customer_po, part_no, sort_by)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7603(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    wanted_from = request.POST.get('param2')
    wanted_to = request.POST.get('param3')
    customer_code = request.POST.get('param4')
    document_no = request.POST.get('param5')
    customer_po = request.POST.get('param6')
    part_no = request.POST.get('param7')
    sort_by = request.POST.get('param8')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7603_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7603(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to, wanted_from, wanted_to, customer_code, document_no, customer_po, part_no, sort_by)
    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7603(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    wanted_from = request.POST.get('param2')
    wanted_to = request.POST.get('param3')
    customer_code = request.POST.get('param4')
    document_no = request.POST.get('param5')
    customer_po = request.POST.get('param6')
    part_no = request.POST.get('param7')
    sort_by = request.POST.get('param8')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7603_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7603_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, issue_from, issue_to, wanted_from, wanted_to, customer_code, document_no, customer_po, part_no, sort_by)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_xls_SR7201(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    document_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7201_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7201_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, document_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7201(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    document_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7201_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7201(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, document_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7205(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7205_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7205_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, supplier_no, part_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_xls_SR7203(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    customer_po = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7203_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7203_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, supplier_no, customer_po)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7205(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7205_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7205(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no, part_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7203(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    customer_po = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7203_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7203(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no, customer_po)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7300(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    select_month = request.POST.get('param0')
    supplier_code = request.POST.get('param1')
    document_no = request.POST.get('param2')
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7300_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7300(buffer, 'A4')
    pdf = report.print_report(company_id, array_data[1], array_data[0], supplier_code, document_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7301(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    select_month = request.POST.get('param0')
    supplier_code = request.POST.get('param1')
    document_no = request.POST.get('param2')
    customer_po = request.POST.get('param3')
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7301_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7301(buffer, 'A4')
    pdf = report.print_report(company_id, array_data[1], array_data[0], supplier_code, document_no, customer_po)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7302(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    select_month = request.POST.get('param0')
    supplier_code = request.POST.get('param1')
    document_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    array_data = str(select_month).split('-')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7302_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7302(buffer, 'A4')
    pdf = report.print_report(company_id, array_data[1], array_data[0], supplier_code, document_no, part_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_GL2200(request, selected_month):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_GL2200_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_GL2200(buffer, 'A4')
    pdf = report.print_report(company_id, selected_month)

    response.write(pdf)
    return response


@login_required
def print_CL2400(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    supplier_code = request.POST.get('param0')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_CL2400_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_CL2400(buffer, 'A4')
    pdf = report.print_report(company_id, supplier_code)

    response.write(b64encode(pdf))
    return response


@login_required
def print_DL2400(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    customer_code = request.POST.get('param0')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_DL2400_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_DL2400(buffer, 'A4')
    pdf = report.print_report(company_id, customer_code)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_TL1200(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    tax_code = request.POST.get('param0')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_TL1200_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_TL1200(buffer, 'A4')
    pdf = report.print_report(company_id, tax_code)

    response.write(b64encode(pdf))
    return response


@login_required
def print_CL2100(request, code):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_CL2100_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_CL2100(buffer, 'A4')
    pdf = report.print_report(company_id, code)

    response.write(pdf)
    return response


@login_required
@csrf_exempt
def print_SL2100(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    part_code = request.POST.get('param0')
    part_group = request.POST.get('param1') 
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL2100_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL2100(buffer, 'A4')
    pdf = report.print_report(company_id, part_code, part_group, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SL2100(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    part_code = request.POST.get('param0')
    part_group = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SL2100_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SL2100_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, part_code, part_group, supplier_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SL2200(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    part_code = request.POST.get('param0')
    part_group = request.POST.get('param1') 
    customer_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL2200_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL2200(buffer, 'A4')
    pdf = report.print_report(company_id, part_code, part_group, customer_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SL2200(request):
    part_code = request.POST.get('param0')
    part_group = request.POST.get('param1') 
    customer_no = request.POST.get('param2')
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SL2200_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SL2200_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, part_code, part_group, customer_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SL2201(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    part_code = request.POST.get('param0')
    part_group = request.POST.get('param1') 
    customer_no = request.POST.get('param2') 
    supplier_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL2201_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL2201(buffer, 'A4')
    pdf = report.print_report(company_id, part_code, part_group,  customer_no, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SL2201(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    part_code = request.POST.get('param0')
    part_group = request.POST.get('param1') 
    customer_no = request.POST.get('param2') 
    supplier_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SL2201_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SL2201_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, part_code, part_group, customer_no, supplier_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SL3300(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1') 
    document_no = request.POST.get('param2') 
    customer_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL3300_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL3300(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, document_no, customer_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SL3301(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1') 
    document_no = request.POST.get('param2') 
    customer_no = request.POST.get('param3')
    customer_po_no = request.POST.get('param4')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL3301_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL3301(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, document_no, customer_no, customer_po_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SL3A00(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1') 
    document_no = request.POST.get('param2') 
    supplier_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL3A00_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL3A00(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, document_no, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SL3A01(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1') 
    document_no = request.POST.get('param2') 
    supplier_no = request.POST.get('param3')
    customer_po_no = request.POST.get('param4')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SL3A01_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SL3A01(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, document_no, supplier_no, customer_po_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR8300(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    document_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8300_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8300(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no, document_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR8400(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    document_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8400_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8400(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, customer_no, document_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR8301(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    customer_po = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8301_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8301(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no, customer_po)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR8800(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8800_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8800(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, customer_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR8801(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8801_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8801(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7202(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7202_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7202(buffer, 'A4')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7202(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7202_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7202_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, supplier_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_xls_SR7204(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7204_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7204_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, supplier_no, part_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7204(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7204_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7204(buffer, 'A4 & landscape')
    pdf = report.print_report(company_id, date_from, date_to, supplier_no, part_no)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7401(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    doc_no = request.POST.get('param2')
    cust_po = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7401_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7401(buffer, 'A4')
    pdf = report.print_report(company_id, wanted_from, wanted_to, doc_no, cust_po)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7402(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7402_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7402(buffer, 'A4')
    pdf = report.print_report(company_id, wanted_from, wanted_to, customer_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7402(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7402_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7402_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, wanted_from, wanted_to, customer_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7403(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    supplier_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7403_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7403(buffer, 'A4')
    pdf = report.print_report(company_id, wanted_from, wanted_to, customer_no, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7403(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    supplier_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7403_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7403_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, wanted_from, wanted_to, customer_no, supplier_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_xls_SR7404(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    part_group = request.POST.get('param4')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7404_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7404_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, wanted_from, wanted_to, customer_no, part_no, part_group)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7404(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    wanted_from = request.POST.get('param0')
    wanted_to = request.POST.get('param1')
    customer_no = request.POST.get('param2')
    part_no = request.POST.get('param3')
    part_group = request.POST.get('param4')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7402_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7404(buffer, 'A4 & landscape')
    pdf = report.print_report(company_id, wanted_from, wanted_to, customer_no, part_no, part_group)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR8500(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    location = request.POST.get('param2')
    part_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR8500_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR8500(buffer, 'A4')
    if location is '0':
        location = None
    pdf = report.print_report(company_id, date_from, date_to, part_no, location)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR8500(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    date_from = request.POST.get('param0')
    date_to = request.POST.get('param1')
    location = request.POST.get('param2')
    part_no = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR8500_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR8500_XLS(output)
    if location is '0':
        location = None
    xlsx_report = xls.WriteToExcel(company_id, date_from, date_to, part_no, location)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_blank(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="blank_report_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


@login_required
def view_report(request, order_type, order_id, print_type, category_id=None):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(id=company_id)

    current_period_from = company.current_period_year_sp + '-' + company.current_period_month_sp + '-01'
    current_period_from = datetime.datetime.strptime(current_period_from, "%Y-%m-%d").date()
    current_period_to = current_period_from + relativedelta(months=1) - relativedelta(days=1)

    # date_to_cur_1m = date_from_cur + relativedelta(months=1) - relativedelta(days=1)
    # date_to_cur1m_1m = date_to_cur_1m - relativedelta(months=1)
    # date_to_cur_24m = date_from_cur + relativedelta(months=24) - relativedelta(days=1)
    if category_id:
        report_name = Report.objects.filter(is_category=True, id=category_id, is_hidden=0).first().name
        report_list = Report.objects.filter(is_category=False, category_id=category_id, is_hidden=0).order_by('code')
    else:
        report_name = ''
        report_list = []
    if category_id and report_name == 'Listing':
        part_list = Item.objects.filter(is_hidden=0, is_active=1, company_id=company_id).order_by('code').values_list('id', 'code')
        part_group_list = ItemCategory.objects.filter(is_hidden=0, company_id=company_id).order_by('code').values_list('id', 'code')
        customer_list = Customer.objects.filter(is_hidden=0, is_active=1, company_id=company_id).order_by('code').values_list('id', 'code')
        supplier_list = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id).order_by('code').values_list('id', 'code')
        tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id).exclude(code__isnull=True).order_by('code').values_list('id', 'code')
    else:
        part_list = []
        part_group_list = []
        customer_list = []
        supplier_list = []
        tax_list = []

    form = ReportForm(company_id)
    if not category_id:
        category_id = ''

    return render(request, 'view-reports.html', {'form': form,
                                                 'part_list': part_list,
                                                 'part_group_list': part_group_list,
                                                 'tax_list': tax_list,
                                                 'report_list': report_list,
                                                 'report_name': report_name,
                                                 'customer_list': customer_list,
                                                 'supplier_list': supplier_list,
                                                 'order_type': order_type,
                                                 'order_id': order_id,
                                                 'category_id': category_id,
                                                 'current_period_from': current_period_from.strftime("%d-%m-%Y"),
                                                 'current_period_to': current_period_to.strftime("%d-%m-%Y"),
                                                 'print_type': print_type})


@login_required
def get_reports_by_category(request, cat_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(id=company_id)
    if request.is_ajax():
        if 'MUTO' in company.name:
            exclude_list = ['SR7502']
            report_list = Report.objects.filter(is_category=False, category_id=cat_id, is_hidden=0)\
                .exclude(code__in=exclude_list)\
                .order_by('code') \
                .values_list('code', 'name')
        else:
            report_list = Report.objects.filter(is_category=False, category_id=cat_id, is_hidden=0).order_by('code') \
                .values_list('code', 'name')
        report_list_json = json.dumps(list(report_list), cls=DjangoJSONEncoder)
        return HttpResponse(report_list_json, content_type="application/json")


def Http_as_json(select2_list=None, order_by='code', index_by='id'):
    if select2_list:
        select2_list = select2_list.order_by(order_by).values_list(index_by, order_by)
    select2_list_json = json.dumps(list(select2_list), cls=DjangoJSONEncoder)

    return HttpResponse(select2_list_json, content_type="application/json")


@login_required
def get_sales_info(request, year_month, data_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        year = year_month.split('-')[0]
        month = year_month.split('-')[1]

        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__document_date__range=(first_day, last_day),
                                                  order__order_type__in=(dict(ORDER_TYPE)['SALES ORDER'],
                                                                         dict(ORDER_TYPE)['SALES INVOICE']))

        select2_list = []
        if data_type == 'category':
            part_category = list(set([orderitem.item.category_id for orderitem in orderitem_list]))
            select2_list = ItemCategory.objects.filter(is_hidden=0, company_id=company_id,
                                                       id__in=part_category)
        elif data_type == 'customer':
            customers = list(set([orderitem.order.customer_id for orderitem in orderitem_list]))
            select2_list = Customer.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                                   id__in=customers)

        return Http_as_json(select2_list)


@login_required
def get_part_group(request, date_from, date_to, order_code):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        if date_from != '0' and date_to != '0':
            category_ids = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                    order__document_date__range=(date_from, date_to),
                                                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']).values_list('item__category_id', flat=True)
        if date_from != '0':
            category_ids = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                    order__document_date__gte=date_from,
                                                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']).values_list('item__category_id', flat=True)
        if date_to != '0':
            category_ids = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                    order__document_date__lte=date_to,
                                                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']).values_list('item__category_id', flat=True)
        else:
            category_ids = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']).values_list('item__category_id', flat=True)

        select2_list = []
        # part_category = list(set([orderitem.item.category_id for orderitem in orderitem_list]))
        select2_list = ItemCategory.objects.filter(is_hidden=0, company_id=company_id,
                                                   id__in=category_ids)

        return Http_as_json(select2_list)


@login_required
def get_supplier_list(request, date_from, date_to, data_type=None):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        supplier_list = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id)

        if data_type == 'outstanding_po':
            if date_from != '0' and date_to != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                          wanted_date__range=(date_from, date_to)). \
                    exclude(quantity__lte=F('receive_quantity'))
            elif date_from != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                          wanted_date__gte=(date_from)). \
                    exclude(quantity__lte=F('receive_quantity'))
            elif date_to != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                          wanted_date__lte=(date_to)). \
                    exclude(quantity__lte=F('receive_quantity'))
            else:
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
                    exclude(quantity__lte=F('receive_quantity'))

            outstanding_po_supplier = list(set([po.order.supplier_id for po in outstanding_po]))
            supplier_list = supplier_list.filter(id__in=outstanding_po_supplier)
        elif data_type == 'SR8801':
            if date_from != '0' and date_to != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(date_from, date_to))
            elif date_from != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(date_from))
            elif date_to != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(date_to))
            else:
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'])

            outstanding_po_supplier = list(set([po.order.supplier_id for po in outstanding_po]))
            supplier_list = supplier_list.filter(id__in=outstanding_po_supplier)
        elif data_type == 'SR7403':
            order_type = 'SALES INVOICE'
            if date_from != '0' and date_to != '0':
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type],
                                                          order__document_date__range=(date_from, date_to)) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft'])
            elif date_from != '0':
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type],
                                                          order__document_date__gte=(date_from)) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft'])
            elif date_to != '0':
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type],
                                                          order__document_date__lte=(date_to)) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft'])
            else:
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type]) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft'])

            suppliers = list(set([so.supplier_id for so in salesitem_list]))
            supplier_list = supplier_list.filter(id__in=suppliers)
        else:
            if date_from != '0' and date_to != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                          order__document_date__range=(date_from, date_to))
            elif date_from != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                          order__document_date__gte=(date_from))
            elif date_to != '0':
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                          order__document_date__lte=(date_to))
            else:
                outstanding_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])

            outstanding_po_supplier = list(set([po.order.supplier_id for po in outstanding_po]))
            supplier_list = supplier_list.filter(id__in=outstanding_po_supplier)

        return Http_as_json(supplier_list)


@login_required
def get_sales_analysis_data(request, date_from, date_to):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    order_type = 'SALES INVOICE'
    if date_from != '0' and date_to != '0':
        salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)[order_type],
                                                  order__document_date__range=(date_from, date_to)) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id', 'customer_po_no', 'item__id').distinct()
    elif date_from != '0':
        salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)[order_type],
                                                  order__document_date__gte=(date_from)) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id', 'customer_po_no', 'item__id').distinct()
    elif date_to != '0':
        salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)[order_type],
                                                  order__document_date__lte=(date_to)) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id', 'customer_po_no', 'item__id').distinct()
    else:
        salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)[order_type]) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id', 'customer_po_no', 'item__id').distinct()

    customers = list(set([so['order__customer__id'] for so in salesitem_list]))
    customer_po_list = list(set([so['customer_po_no'] for so in salesitem_list]))
    parts = list(set([so['item__id'] for so in salesitem_list]))

    customer_list = Customer.objects.filter(is_hidden=0, is_active=1, company_id=company_id, id__in=customers).order_by('code').values_list('id', 'code')
    part_list = Item.objects.filter(is_hidden=0, company_id=company_id, id__in=parts).order_by('code').values_list('id', 'code')
    customer_po_list.sort()

    context = {
        'customer_list': list(customer_list),
        'part_list': list(part_list),
        'customer_po_list': customer_po_list
    }

    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required
def get_customer_list(request, date_from, date_to, data_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if data_type == 'outstanding_so':
            if date_from != '0' and date_to != '0':
                outstanding_so = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                          wanted_date__range=(date_from, date_to)) \
                    .exclude(quantity__lte=F('delivery_quantity')).values('order__customer__id').distinct()
            elif date_from != '0':
                outstanding_so = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                          wanted_date__gte=(date_from)) \
                    .exclude(quantity__lte=F('delivery_quantity')).values('order__customer__id').distinct()
            elif date_to != '0':
                outstanding_so = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                          wanted_date__lte=(date_to)) \
                    .exclude(quantity__lte=F('delivery_quantity')).values('order__customer__id').distinct()
            else:
                outstanding_so = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                          order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
                    .exclude(quantity__lte=F('delivery_quantity')).values('order__customer__id').distinct()

            customers = list(set([so['order__customer__id'] for so in outstanding_so]))

        else:
            if data_type == 'sales invoice':
                order_type = 'SALES INVOICE'
            else:
                order_type = 'SALES ORDER'
            if date_from != '0' and date_to != '0':
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type],
                                                          order__document_date__range=(date_from, date_to)) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id').distinct()
            elif date_from != '0':
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type],
                                                          order__document_date__gte=(date_from)) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id').distinct()
            elif date_to != '0':
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type],
                                                          order__document_date__lte=(date_to)) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id').distinct()
            else:
                salesitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)[order_type]) \
                    .exclude(order__status=dict(ORDER_STATUS)['Draft']).values('order__customer__id').distinct()

            customers = list(set([so['order__customer__id'] for so in salesitem_list]))

        customer_list = Customer.objects.filter(is_hidden=0, is_active=1, company_id=company_id, id__in=customers)

        return Http_as_json(customer_list)


@login_required
def get_oustanding_sales(request, date_from, date_to, doc_from, doc_to, cus_po_from, cus_po_to, data_type):
    if request.is_ajax():

        order_type = dict(ORDER_TYPE)['SALES ORDER']
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if date_from != '0' and date_to != '0':
            orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                      order__company_id=company_id,
                                                      order__order_type=order_type,
                                                      wanted_date__range=(date_from, date_to)) \
                .exclude(quantity__lte=F('delivery_quantity'))
        elif date_from != '0':
            orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                      order__company_id=company_id,
                                                      order__order_type=order_type,
                                                      wanted_date__gte=(date_from)) \
                .exclude(quantity__lte=F('delivery_quantity'))
        elif date_to != '0':
            orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                      order__company_id=company_id,
                                                      order__order_type=order_type,
                                                      wanted_date__lte=(date_to)) \
                .exclude(quantity__lte=F('delivery_quantity'))
        else:
            orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                      order__company_id=company_id,
                                                      order__order_type=order_type) \
                .exclude(quantity__lte=F('delivery_quantity'))

        if "document_no" in data_type:
            item_key = 'order__document_number'

            doc_no_from = ''
            if doc_from and not doc_from == '0':
                doc_no_from = orderitem_list.filter(order_id=doc_from).first()
                doc_no_from = doc_no_from.order.document_number

            doc_no_to = ''
            if doc_to and not doc_to == '0':
                doc_no_to = orderitem_list.filter(order_id=doc_to).first()
                doc_no_to = doc_no_to.order.document_number

            doc_numbers = get_orderitem_filter_range(order_type, company_id, doc_no_from, doc_no_to, item_key)
            orderitem_list = orderitem_list.filter(order__document_number__in=doc_numbers)

            seen = set()
            seen_add = seen.add
            orderitems = [orderitem.id for orderitem in orderitem_list if
                          not (orderitem.order.document_number in seen or seen_add(orderitem.order.document_number))]

            orderitem_list = orderitem_list.filter(id__in=orderitems)

            return Http_as_json(orderitem_list, 'order__document_number', 'order_id')

        elif 'customer_po' in data_type:
            item_key = 'order__document_number'
            doc_no_from = ''
            if doc_from and not doc_from == '0':
                doc_no_from = orderitem_list.filter(order_id=doc_from).first()
                doc_no_from = doc_no_from.order.document_number

            doc_no_to = ''
            if doc_to and not doc_to == '0':
                doc_no_to = orderitem_list.filter(order_id=doc_to).first()
                doc_no_to = doc_no_to.order.document_number

            doc_numbers = get_orderitem_filter_range(order_type, company_id, doc_no_from, doc_no_to, item_key)

            item_key = 'customer_po_no'
            customer_no_from = ''
            if cus_po_from and not cus_po_from == '0':
                customer_no_from = orderitem_list.filter(id=cus_po_from).first()
                customer_no_from = customer_no_from.customer_po_no

            customer_no_to = ''
            if cus_po_to and not cus_po_to == '0':
                customer_no_to = orderitem_list.filter(id=cus_po_to).first()
                customer_no_to = customer_no_to.customer_po_no

            customer_pos = get_orderitem_filter_range(order_type, company_id, customer_no_from, customer_no_to,
                                                      item_key)

            orderitem_list = orderitem_list.filter(customer_po_no__in=customer_pos,
                                                   order__document_number__in=doc_numbers)

            seen = set()
            seen_add = seen.add
            cus_po = [cus_po.id for cus_po in orderitem_list if
                      not (cus_po.customer_po_no in seen or seen_add(cus_po.customer_po_no))]

            cus_po_list = orderitem_list.filter(id__in=cus_po)

            return Http_as_json(cus_po_list, 'customer_po_no')


def get_gr_data(request, date_from, date_to, data_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    select2_list = []
    if data_type == 'SR7503':
        if date_from != '0' and date_to != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__range=(date_from, date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item_id', 'customer_po_no').distinct()
        elif date_from != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__gte=(date_from)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item_id', 'customer_po_no').distinct()
        elif date_to != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__lte=(date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item_id', 'customer_po_no').distinct()
        else:
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item_id', 'customer_po_no').distinct()

        customer_po_list = list(set([gr['customer_po_no'] for gr in gr_list]))
        parts = list(set([gr['item_id'] for gr in gr_list]))

        part_list = Item.objects.filter(is_hidden=0, company_id=company_id, id__in=parts).order_by('code').values_list('id', 'code')
        cat_list = Item.objects.filter(is_hidden=0, company_id=company_id, id__in=parts).order_by(
            'category_id').values_list('category_id', 'category__code').distinct()
        customer_po_list.sort()

        context = {
            'cat_list': list(cat_list),
            'part_list': list(part_list),
            'customer_po_list': customer_po_list
        }

        return HttpResponse(json.dumps(context), content_type="application/json")

    elif data_type == 'part_no':
        if date_from != '0' and date_to != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__range=(date_from, date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item__code').distinct()
        elif date_from != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__gte=(date_from)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item__code').distinct()
        elif date_to != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__lte=(date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item__code').distinct()
        else:
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code').values('item__code').distinct()

        part_no = list(set([gr['item__code'] for gr in gr_list]))
        select2_list = Item.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                           code__in=part_no)

    elif data_type == 'supplier':
        if date_from != '0' and date_to != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__range=(date_from, date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier_id').values('supplier_id').distinct()
        elif date_from != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__gte=(date_from)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier_id').values('supplier_id').distinct()
        elif date_to != '0':
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                               order__document_date__lte=(date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier_id').values('supplier_id').distinct()
        else:
            gr_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier_id').values('supplier_id').distinct()

        suppliers = list(set([gr['supplier_id'] for gr in gr_list]))
        select2_list = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                               id__in=suppliers)

    return Http_as_json(select2_list)


def get_delivery_addr(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        addr_list = Delivery.objects.filter(is_hidden=0, is_active=1, company_id=company_id).values_list('id', 'code')

        dump_data = json.dumps(list(addr_list), cls=DjangoJSONEncoder)
        return HttpResponse(dump_data, content_type="application/json")


def get_inv_location(request):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        location_data = Location.objects.filter(is_hidden=False, company_id=company_id)
        location_list = []

        for loc in location_data:
            location_list.append(
                {
                    'id': loc.id,
                    'code': loc.code
                }
            )

        dump_data = json.dumps(location_list, cls=DjangoJSONEncoder)
        return HttpResponse(dump_data, content_type="application/json")


def get_SR8500_data(request, location_id):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        com_location_ids = Location.objects.filter(is_hidden=False, company_id=company_id).values_list('id', flat=True)

        if int(location_id):
            part_list = LocationItem.objects.filter(is_hidden=False, location_id=int(location_id)).values('item_id').distinct()
        else:
            part_list = LocationItem.objects.filter(is_hidden=False, location_id__in=com_location_ids).values('item_id').distinct()

        if part_list:
            part_ids = list(set([part['item_id'] for part in part_list]))
            part_list = Item.objects.filter(id__in=part_ids)
            part_list = part_list.order_by('code').values_list('id', 'code')
            part_data = json.dumps(list(part_list), cls=DjangoJSONEncoder)

            return HttpResponse(part_data, content_type="application/json")


def get_po_data(request, date_from, date_to, data_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if data_type == 'po':
            if date_from != '0' and date_to != '0':
                po_list = Order.objects.filter(is_hidden=0, company_id=company_id,
                                               order_type=dict(ORDER_TYPE)['PURCHASE ORDER'], document_date__range=(date_from, date_to)) \
                    .exclude(Q(status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('document_number')
            elif date_from != '0':
                po_list = Order.objects.filter(is_hidden=0, company_id=company_id,
                                               order_type=dict(ORDER_TYPE)['PURCHASE ORDER'], document_date__gte=(date_from)) \
                    .exclude(Q(status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('document_number')
            elif date_to != '0':
                po_list = Order.objects.filter(is_hidden=0, company_id=company_id,
                                               order_type=dict(ORDER_TYPE)['PURCHASE ORDER'], document_date__lte=(date_to)) \
                    .exclude(Q(status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('document_number')
            else:
                po_list = Order.objects.filter(is_hidden=0, company_id=company_id,
                                               order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                    .exclude(Q(status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('document_number')
            select2_list = []

            for po in po_list:
                select2_list.append(
                    {'id': po.id, 'doc_num': po.document_number}
                )
            dump_data = json.dumps(select2_list, cls=DjangoJSONEncoder)
            return HttpResponse(dump_data, content_type="application/json")
        else:
            if date_from != '0' and date_to != '0':
                po_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                   wanted_date__range=(date_from, date_to)) \
                    .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('item__code').values('item__code').distinct()
            elif date_from != '0':
                po_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                   wanted_date__gte=(date_from)) \
                    .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('item__code').values('item__code').distinct()
            elif date_to != '0':
                po_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                   wanted_date__lte=(date_to)) \
                    .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('item__code').values('item__code').distinct()
            else:
                po_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
                    .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                    .order_by('item__code').values('item__code').distinct()

            select2_list = []
            if data_type == 'part_no':
                part_no = list(set([po['item__code'] for po in po_list]))
                select2_list = Item.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                                   code__in=part_no)

            return Http_as_json(select2_list)


def get_so_data(request, date_from, date_to, data_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if date_from != '0' and date_to != '0':
            so_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                               wanted_date__range=(date_from, date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item_id').values('item_id').distinct()
        elif date_from != '0':
            so_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                               wanted_date__gte=(date_from)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item_id').values('item_id').distinct()
        elif date_to != '0':
            so_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                               wanted_date__lte=(date_to)) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item_id').values('item_id').distinct()
        else:
            so_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                               order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item_id').values('item_id').distinct()

        select2_list = []
        if data_type == 'part_no':
            part_no = list(set([so['item_id'] for so in so_list]))
            select2_list = Item.objects.filter(id__in=part_no)
            item_list = select2_list.values_list('id', 'code')
            grp_list = select2_list.values_list('category__id', 'category__code').order_by('category__code').distinct()

        json_data = {}
        if select2_list:
            json_data = {
                "grp_list": list(grp_list),
                "part_list": list(item_list)
            }

        json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data_dumps, content_type="application/json")


@login_required
def get_customer_po(request, date_from, date_to, supplier_id, order_code):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        if order_code == 'SR7203':
            if date_from != '0' and date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                   wanted_date__range=(date_from, date_to)). \
                    exclude(quantity__lte=F('receive_quantity'))
            elif date_from != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                   wanted_date__gte=(date_from)). \
                    exclude(quantity__lte=F('receive_quantity'))
            elif date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                   wanted_date__lte=(date_to)). \
                    exclude(quantity__lte=F('receive_quantity'))
            else:
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
                    exclude(quantity__lte=F('receive_quantity'))
        else:
            if order_code == 'SL3301':
                order_type = 'SALES ORDER'
            else:
                order_type = 'PURCHASE ORDER'
            if date_from != '0' and date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type],
                                                                   order__document_date__range=(date_from, date_to))
            elif date_from != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type],
                                                                   order__document_date__gte=(date_from))
            elif date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type],
                                                                   order__document_date__lte=(date_to))
            else:
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type])

        if supplier_id != '0':
            outstanding_customer_po = outstanding_customer_po.filter(supplier_id=supplier_id)

        seen = set()
        seen_add = seen.add
        outstanding_cus_po = [cus_po.id for cus_po in outstanding_customer_po if
                              not (cus_po.customer_po_no in seen or seen_add(cus_po.customer_po_no))]

        cus_po_list = outstanding_customer_po.filter(id__in=outstanding_cus_po)

        return Http_as_json(cus_po_list, 'customer_po_no')


@login_required
def get_document_no(request, date_from, date_to, order_code):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        if order_code != 'SR7201':
            if order_code == 'SL3300' or order_code == 'SL3301':
                order_type = 'SALES ORDER'
            else:
                order_type = 'PURCHASE ORDER'
            if date_from != '0' and date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type],
                                                                   order__document_date__range=(date_from, date_to))
            elif date_from != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type],
                                                                   order__document_date__gte=(date_from))
            elif date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type],
                                                                   order__document_date__lte=(date_to))
            else:
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)[order_type])
        else:
            if date_from != '0' and date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                   wanted_date__range=(date_from, date_to)). \
                    exclude(quantity__lte=F('receive_quantity'))
            elif date_from != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                   wanted_date__gte=(date_from)). \
                    exclude(quantity__lte=F('receive_quantity'))
            elif date_to != '0':
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                                   wanted_date__lte=(date_to)). \
                    exclude(quantity__lte=F('receive_quantity'))
            else:
                outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                                   order__company_id=company_id,
                                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']). \
                    exclude(quantity__lte=F('receive_quantity'))

        seen = set()
        seen_add = seen.add
        outstanding_cus_po = [cus_po.id for cus_po in outstanding_customer_po if
                              not (cus_po.order.document_number in seen or seen_add(cus_po.order.document_number))]

        cus_po_list = outstanding_customer_po.filter(id__in=outstanding_cus_po)

        return Http_as_json(cus_po_list, 'order__document_number', 'order_id')


@login_required
def get_SL3_data(request, date_from, date_to, order_code):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        if order_code == 'SL3300' or order_code == 'SL3301':
            order_type = 'SALES ORDER'
        elif order_code == 'SL3A00' or order_code == 'SL3A01':
            order_type = 'PURCHASE ORDER'
        if date_from != '0' and date_to != '0':
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type],
                                                               order__document_date__range=(date_from, date_to))
        elif date_from != '0':
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type],
                                                               order__document_date__gte=(date_from))
        elif date_to != '0':
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type],
                                                               order__document_date__lte=(date_to))
        else:
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type])

        if order_code == 'SL3300' or order_code == 'SL3301':
            cust_list = outstanding_customer_po.values_list('order__customer_id', 'order__customer__code')\
                .order_by('order__customer_id').distinct()
            cust_data = json.dumps(list(cust_list), cls=DjangoJSONEncoder)

            return HttpResponse(cust_data, content_type="application/json")
        elif order_code == 'SL3A00' or order_code == 'SL3A01':
            cust_list = outstanding_customer_po.values_list('supplier_id', 'supplier__code')\
                .order_by('supplier_id').distinct()
            cust_data = json.dumps(list(cust_list), cls=DjangoJSONEncoder)

            return HttpResponse(cust_data, content_type="application/json")


@login_required
def get_document_numbers(request, date_from, date_to, order_code, customer_id):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        if order_code == 'SR8400':
            order_type = 'SALES ORDER'
        else:
            order_type = 'PURCHASE ORDER'
        if date_from != '0' and date_to != '0':
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type],
                                                               order__document_date__range=(date_from, date_to))
        elif date_from != '0':
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type],
                                                               order__document_date__gte=(date_from))
        elif date_to != '0':
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type],
                                                               order__document_date__lte=(date_to))
        else:
            outstanding_customer_po = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                               order__company_id=company_id,
                                                               order__order_type=dict(ORDER_TYPE)[order_type])
        if customer_id != '0':
            if order_code == 'SR8400':
                outstanding_customer_po = outstanding_customer_po.filter(order__customer_id=customer_id)
            else:
                outstanding_customer_po = outstanding_customer_po.filter(supplier_id=customer_id)
        seen = set()
        seen_add = seen.add
        outstanding_cus_po = [cus_po.id for cus_po in outstanding_customer_po if
                              not (cus_po.order.document_number in seen or seen_add(cus_po.order.document_number))]

        cus_po_list = outstanding_customer_po.filter(id__in=outstanding_cus_po)

        return Http_as_json(cus_po_list, 'order__document_number', 'order_id')


@login_required
def get_report_filters(request, date_from, date_to, order_code, date_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        if order_code == 'SR7603':
            order_type = 'SALES ORDER'
        else:
            order_type = 'PURCHASE ORDER'

        item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                             order__company_id=company_id,
                                             order__order_type=dict(ORDER_TYPE)[order_type])
        if date_type == 'issue':
            if date_from != '0' and date_to != '0':
                item_list = item_list.filter(order__document_date__range=(date_from, date_to))
            elif date_from != '0':
                item_list = item_list.filter(order__document_date__gte=(date_from))
            elif date_to != '0':
                item_list = item_list.filter(order__document_date__lte=(date_to))
        else:
            if date_from != '0' and date_to != '0':
                item_list = item_list.filter(wanted_date__range=(date_from, date_to))
            elif date_from != '0':
                item_list = item_list.filter(wanted_date__gte=(date_from))
            elif date_to != '0':
                item_list = item_list.filter(wanted_date__lte=(date_to))
        if item_list:
            if order_type == 'SALES ORDER':
                customer_list = list(item_list.values_list('order__customer_id', 'order__customer__code').order_by('order__customer__code').distinct())
            else:
                customer_list = list(item_list.values_list('supplier_id', 'supplier__code').order_by('supplier__code').distinct())
            document_list = list(item_list.values_list('order_id', 'order__document_number').order_by('order__document_number').distinct())
            customer_po_list = list(item_list.values_list('id', 'customer_po_no').order_by('customer_po_no').distinct())
            part_list = list(item_list.values_list('item_id', 'item__code').order_by('item__code').distinct())

        json_data = {}
        if item_list:
            json_data = {
                "customer_list": customer_list,
                "document_list": document_list,
                "customer_po_list": customer_po_list,
                "part_list": part_list
            }

        json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data_dumps, content_type="application/json")


def get_monthly_purchase(request, year_month, parameter_id, data_type):
    if request.is_ajax():
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

        year = year_month.split('-')[0]
        month = year_month.split('-')[1]

        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                  order__document_date__range=(first_day, last_day)) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .order_by('order__supplier__code')

        # if data_type == "document_no":
        #     supplier_id = parameter_id

        #     if supplier_id and not supplier_id == '0':
        #         orderitem_list = orderitem_list.filter(supplier_id=supplier_id)

        #     seen = set()
        #     seen_add = seen.add
        #     orderitems = [orderitem.id for orderitem in orderitem_list if
        #                   not (orderitem.order.document_number in seen or seen_add(orderitem.order.document_number))]

        #     orderitem_list = orderitem_list.filter(id__in=orderitems)

        #     return Http_as_json(orderitem_list, 'order__document_number', 'order_id')
        # elif data_type == 'supplier':

        #     suppliers = list(set([po.supplier_id for po in orderitem_list]))
        #     supplier_list = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id, id__in=suppliers)
        #     return Http_as_json(supplier_list)
        # elif data_type == 'customer_po':
        #     seen = set()
        #     seen_add = seen.add
        #     cus_po = [cus_po.id for cus_po in orderitem_list if
        #               not (cus_po.customer_po_no in seen or seen_add(cus_po.customer_po_no))]

        #     cus_po_list = orderitem_list.filter(id__in=cus_po)

        #     return Http_as_json(cus_po_list, 'customer_po_no')
        # elif data_type == 'part_no_cus_po':
        #     customer_po = parameter_id

        #     if customer_po and not customer_po == '0':
        #         customer_po = orderitem_list.get(id=customer_po).customer_po_no
        #         orderitem_list = orderitem_list.filter(customer_po_no__contains=customer_po)

        #     part_no = list(set([gr.item.code for gr in orderitem_list]))
        #     select2_list = Item.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
        #                                        code__in=part_no)
        #     return Http_as_json(select2_list)
        # elif data_type == 'part_no_doc_no':
        #     document_no = parameter_id

        #     if document_no and not document_no == '0':
        #         orderitem_list = orderitem_list.filter(order_id=document_no)

        #     part_no = list(set([gr.item.code for gr in orderitem_list]))
        #     select2_list = Item.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
        #                                        code__in=part_no)
        #     return Http_as_json(select2_list)
        seen = set()
        seen_add = seen.add
        orderitems = [orderitem.id for orderitem in orderitem_list if
                        not (orderitem.order.document_number in seen or seen_add(orderitem.order.document_number))]

        orderitems = orderitem_list.filter(id__in=orderitems)
        doc_list = orderitems.order_by('order__document_number').values_list('order_id', 'order__document_number')

        suppliers = list(set([po.supplier_id for po in orderitem_list]))
        supplier_list = Supplier.objects.filter(is_hidden=0, is_active=1, company_id=company_id, id__in=suppliers)\
                            .order_by('code').values_list('id', 'code')
        
        cus_po_list = []
        if data_type == 'customer_po':
            seen = set()
            seen_add = seen.add
            cus_po = [cus_po.id for cus_po in orderitem_list if
                      not (cus_po.customer_po_no in seen or seen_add(cus_po.customer_po_no))]

            cus_pos = orderitem_list.filter(id__in=cus_po)
            cus_po_list = cus_pos.order_by('customer_po_no').values_list('id', 'customer_po_no')
        
        part_list = []
        if data_type == 'part_no':
            part_no = list(set([gr.item.code for gr in orderitem_list]))
            parts = Item.objects.filter(is_hidden=0, is_active=1, company_id=company_id,
                                               code__in=part_no)
            part_list = parts.order_by('code').values_list('id', 'code')
        json_data = {
            "doc_list": list(doc_list), 
            "supplier_list": list(supplier_list),
            "cus_po_list": list(cus_po_list),
            "part_list": list(part_list)
        }
        json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data_dumps, content_type="application/json")

@login_required
def get_current_month_amount(request, order_type, month, year):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
        order_list = Order.objects.filter(is_hidden=0, company_id=company_id, order_type=order_type)
        if first_day:
            order_list = order_list.filter(document_date__gte=first_day)
        if last_day:
            order_list = order_list.filter(document_date__lte=last_day)
        company = Company.objects.get(pk=company_id)
        company_currency = Currency.objects.get(pk=company.currency_id)
        default_currency = Currency.objects.filter(code__contains=s.DEFAULT_CURRENCY_CODE).first()
        company_currency_id = 0
        if company_currency:
            company_currency_id = company_currency.id
        elif default_currency:
            company_currency_id = default_currency.id

        for i, my_order in enumerate(order_list):
            if int(my_order.currency.id) != int(company_currency_id):
                order_exchange = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                             from_currency__id=my_order.currency.id,
                                                             to_currency__id=company_currency_id,
                                                             flag='ACCOUNTING').first()
                my_order.total = Decimal(my_order.total) * Decimal(order_exchange.rate)
        order_list = order_list.values('order_type') \
            .annotate(sum_amount=ExpressionWrapper(Sum('total'), output_field=models.FloatField(default=0.0)))

        if order_list:
            json_data = {"month": month, "month_amount": order_list[0]['sum_amount']}
            json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        else:
            json_data = {"month": month, "month_amount": 0}
            json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data_dumps, content_type="application/json")


@login_required
def get_current_month_profit(request, month, year):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
        item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                             order__order_type=dict(ORDER_TYPE)['SALES ORDER'])
        item_list = item_list.exclude(order__customer__isnull=True)
        if first_day:
            item_list = item_list.filter(order__document_date__gte=first_day)
        if last_day:
            item_list = item_list.filter(order__document_date__lte=last_day)
        item_list = item_list.values('item__supplieritem__supplier__code', 'item__supplieritem__supplier__name',
                                     'order__customer__code', 'order__customer__name',
                                     'item__name', 'item__purchase_code', 'item__category__name',
                                     'item__purchase_currency__id', 'item__purchase_currency__code',
                                     'item__purchase_price',
                                     'item__sale_currency__id', 'item__sale_currency__code', 'price') \
            .annotate(sum_quantity=ExpressionWrapper(Sum('quantity'), output_field=models.FloatField(default=0.0))) \
            .annotate(profit=ExpressionWrapper(F('price') - F('item__purchase_price'),
                                               output_field=models.FloatField(default=0.0))) \
            .order_by('order__customer__code', 'item__supplieritem__supplier__code', 'item__purchase_code')

        company = Company.objects.get(pk=company_id)
        company_currency = Currency.objects.get(pk=company.currency_id)
        default_currency = Currency.objects.filter(code__contains=s.DEFAULT_CURRENCY_CODE).first()
        company_currency_id = 0
        if company_currency:
            company_currency_id = company_currency.id
        elif default_currency:
            company_currency_id = default_currency.id

        total_profit = 0
        total_quantity = 0
        purchase_exchange_rate = 1
        sale_exchange_rate = 1

        exchange_rate_list = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                         to_currency__id=company_currency_id,
                                                         flag='ACCOUNTING')

        for i, my_item in enumerate(item_list):
            purchase_exchange = exchange_rate_list.filter(
                from_currency__id=my_item['item__purchase_currency__id']).first()
            if purchase_exchange:
                purchase_exchange_rate = purchase_exchange.rate

            sale_exchange = exchange_rate_list.filter(from_currency__id=my_item['item__sale_currency__id']).first()
            if sale_exchange:
                sale_exchange_rate = sale_exchange.rate

            local_purchase_price = Decimal(my_item['item__purchase_price']) * purchase_exchange_rate
            local_sale_price = Decimal(my_item['price']) * sale_exchange_rate
            my_item['profit'] = "%.2f" % (local_sale_price - local_purchase_price)
            total_quantity += my_item['sum_quantity']
            total_profit += Decimal(my_item['profit']) * Decimal(my_item['sum_quantity'])

        if item_list:
            json_data = {"month": month, "total_profit": total_profit}
            json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        else:
            json_data = {"month": month, "total_profit": 0}
            json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)
        return HttpResponse(json_data_dumps, content_type="application/json")


@login_required
def get_current_month_profit_percent(request, month, year):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.is_ajax():
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
        item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                             order__order_type=dict(ORDER_TYPE)['SALES ORDER'])
        item_list = item_list.exclude(order__customer__isnull=True)
        if first_day:
            item_list = item_list.filter(order__document_date__gte=first_day)
        if last_day:
            item_list = item_list.filter(order__document_date__lte=last_day)
        item_list = item_list.values('item__supplieritem__supplier__code', 'item__supplieritem__supplier__name',
                                     'order__customer__code', 'order__customer__name',
                                     'item__name', 'item__purchase_code', 'item__category__name',
                                     'item__purchase_currency__id', 'item__purchase_currency__code',
                                     'item__purchase_price',
                                     'item__sale_currency__id', 'item__sale_currency__code', 'price') \
            .annotate(sum_quantity=ExpressionWrapper(Sum('quantity'), output_field=models.FloatField(default=0.0))) \
            .annotate(profit=ExpressionWrapper(F('price') - F('item__purchase_price'),
                                               output_field=models.FloatField(default=0.0))) \
            .order_by('order__customer__code', 'item__supplieritem__supplier__code', 'item__purchase_code')

        company = Company.objects.get(pk=company_id)
        company_currency = Currency.objects.get(pk=company.currency_id)
        default_currency = Currency.objects.filter(code__contains=s.DEFAULT_CURRENCY_CODE).first()
        company_currency_id = 0
        if company_currency:
            company_currency_id = company_currency.id
        elif default_currency:
            company_currency_id = default_currency.id

        total_profit = 0
        total_quantity = 0
        total_sales = 0
        total_sales_local = 0
        percent_profit = 0
        purchase_exchange_rate = 1
        sale_exchange_rate = 1

        exchange_rate_list = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                         to_currency__id=company_currency_id,
                                                         flag='ACCOUNTING')

        for i, my_item in enumerate(item_list):
            purchase_exchange = exchange_rate_list.filter(
                from_currency__id=my_item['item__purchase_currency__id']).first()
            if purchase_exchange:
                purchase_exchange_rate = purchase_exchange.rate

            sale_exchange = exchange_rate_list.filter(from_currency__id=my_item['item__sale_currency__id']).first()
            if sale_exchange:
                sale_exchange_rate = sale_exchange.rate

            local_purchase_price = Decimal(my_item['item__purchase_price']) * purchase_exchange_rate
            local_sale_price = Decimal(my_item['price']) * sale_exchange_rate
            my_item['profit'] = "%.2f" % (local_sale_price - local_purchase_price)
            total_quantity += my_item['sum_quantity']
            total_profit += Decimal(my_item['profit']) * Decimal(my_item['sum_quantity'])
            total_sales += Decimal(my_item['price']) * Decimal(my_item['sum_quantity'])
            total_sales_local += Decimal(local_sale_price) * Decimal(my_item['sum_quantity'])
        if total_sales > 0 and total_sales_local > 0:
            percent_profit = "%.2f" % (total_sales / total_sales_local)

        json_data = {"month": month, "percent_profit": percent_profit}
        json_data_dumps = json.dumps(json_data, cls=DjangoJSONEncoder)

        return HttpResponse(json_data_dumps, content_type="application/json")


@login_required
def print_xls_SR7504(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    is_confirm = request.POST.get('param3')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7504_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7504_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, issue_from, issue_to, supplier_no, is_confirm)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7504(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    is_confirm = request.POST.get('param3')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7504_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7504(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to, supplier_no, is_confirm)

    response.write(b64encode(pdf))
    return response


@login_required
@csrf_exempt
def print_SR7503(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    customer_po = request.POST.get('param2')
    part_group = request.POST.get('param3')
    part_no = request.POST.get('param4')
    is_confirm = request.POST.get('param5')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7503_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7503(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to, customer_po, part_group, part_no, is_confirm)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7503(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    customer_po = request.POST.get('param2')
    part_group = request.POST.get('param3')
    part_no = request.POST.get('param4')
    is_confirm = request.POST.get('param5')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7503_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7503_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, issue_from, issue_to, customer_po, part_group, part_no, is_confirm)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7501(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7501_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7501(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to, supplier_no)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7501(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    supplier_no = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7501_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7501_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, issue_from, issue_to, supplier_no)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
@csrf_exempt
def print_SR7502(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    code = request.POST.get('param2')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_SR7502_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_SR7502(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to, code)

    response.write(b64encode(pdf))
    return response


@login_required
def print_xls_SR7502(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    issue_from = request.POST.get('param0')
    issue_to = request.POST.get('param1')
    code = request.POST.get('param2')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()

    file_name = 'report_SR7502_XLS_%s.xlsx' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    xls = Print_SR7502_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, issue_from, issue_to, code)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_APvendor_Label(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                         paid_full):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_APvendorLabel_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    buffer = BytesIO()
    report = Print_AP_vendor_Label(buffer, 'A4')
    pdf = report.print_report(company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                              paid_full)

    response.write(pdf)
    return response


@login_required
def print_APvendor_letter(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                          paid_full):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_APvendorA4_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    if report_type == 'email':
        buffer = BytesIO()
        company = Company.objects.get(pk=company_id)
        company_name = company.name
        cust_id_from = int(cus_no) if cus_no else 0
        cust_id_to = int(curr_list) if curr_list else 0

        jounal_item_list = Journal.objects.filter(
            company_id=company_id, is_hidden=0,
            status=int(STATUS_TYPE_DICT['Posted']),
            batch__status=int(STATUS_TYPE_DICT['Posted']),
            batch__batch_type=dict(TRANSACTION_TYPES)['AP Invoice'],
            document_date__range=[age_from, cutoff_date])

        vendor_range = get_vendor_filter_range(company_id, cust_id_from, cust_id_to, 'id')

        if cust_id_to > cust_id_from and cust_id_from > 0:
            jounal_item_list = jounal_item_list.filter(supplier_id__in=vendor_range).values('supplier_id').distinct()
        else:
            jounal_item_list = jounal_item_list.values('supplier_id').distinct()

        # get_user_login = Staff.objects.get(pk=request.session['staff_admin'])
        # user_login = User.objects.get(pk=get_user_login.user_id)
        user_login = User.objects.get(pk=request.user.id)
        if jounal_item_list:
            for exp in jounal_item_list:
                vendor = Supplier.objects.get(pk=exp['supplier_id'])

                send_email_to = vendor.email
                receipient_name = vendor.name
                sender = user_login.email

                now = datetime.datetime.now()
                month = str(now.month)
                if len(month) == 1:
                    month = '0' + month
                day = str(now.day)
                if len(day) == 1:
                    day = '0' + day
                email_msg = vendor.email_msg
                if email_msg is None:
                    email_msg = VENDOR_DEFAULT_MSG
                email_msg = email_msg.replace(EMAIL_MSG_CONST['company_name'], company_name)
                email_msg = email_msg.replace(EMAIL_MSG_CONST['date'], datetime.datetime.now().strftime('%d-%m-%Y'))
                if email_msg.find(EMAIL_MSG_CONST['vendor_name']):
                    email_msg = email_msg.replace(EMAIL_MSG_CONST['vendor_name'], receipient_name)
                if email_msg.find(EMAIL_MSG_CONST['company_phone']):
                    email_msg = email_msg.replace(EMAIL_MSG_CONST['company_phone'], company.phone)
                attachment = None
                if ('' != send_email_to and None != send_email_to):
                    send_email(sender, receipient_name, email_msg, str(now.year) + '/' + month + '/' + day, company_name,
                               send_email_to, attachment)

        buffer = BytesIO()
        report = Print_AP_vendor_letter(buffer, 'A4')
        pdf = report.print_report(company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                                  paid_full)
        response.write(pdf)
    else:
        buffer = BytesIO()
        report = Print_AP_vendor_letter(buffer, 'A4')
        pdf = report.print_report(company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                                  paid_full)
        response.write(pdf)
    return response


@login_required
def print_ARCustomers_Label(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                            paid_full):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_ARCustomerLabel_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    buffer = BytesIO()
    report = Print_AR_customers_Label(buffer, 'A4')
    pdf = report.print_report(company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                              paid_full)

    response.write(pdf)
    return response


@login_required
def print_ARCustomers_letter(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                             paid_full):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_ARCustomerA4_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    buffer = BytesIO()
    report = Print_AR_customers_letter(buffer, 'A4')
    pdf = report.print_report(company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                              paid_full)

    response.write(pdf)
    return response


def export_ARCustomers(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    buffer = BytesIO()
    report = Print_AR_customers(buffer, 'A4')
    pdf = report.print_report(company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list,
                              paid_full)
    return pdf


@login_required
def print_AR_note(request, journal_id, print_header):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_order_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    buffer = BytesIO()
    report = Print_AR_Note(buffer, 'A4')
    pdf = report.print_report(journal_id, print_header, company_id)

    response.write(pdf)
    return response


def prepareMessage(customer, company, age_from, cutoff_date, doc_type):
    open_doc = 1 if int(doc_type) == 1 else 2
    cus_no = str(customer.id) + ',' + str(customer.id)
    # jounal_item_list = Journal.objects.filter(company_id=company.id, is_hidden=0, customer_id=customer.id,
    #                                           batch__batch_type=dict(TRANSACTION_TYPES)['AR Invoice'],
    #                                           batch__status=open_doc, document_date__range=[age_from, cutoff_date])
    ar_collections = get_ar_transactions(is_detail_report=True, company_id=company.id, cus_no=cus_no, cutoff_date=cutoff_date, date_type='1',
                                                 paid_full=0, doc_type_array=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
    journal_item_list = ar_collections.journal_item_list
    # journal_item_list = journal_item_list.filter(customer_id=id_customers)
    adjustment_journal_list = ar_collections.adjustment_journal_list
    journal_amount_list = ar_collections.journal_amount_list
    grand_total = 0
    due_days = ''
    payment_term = ''

    for journal in journal_item_list:
        # grand_total += journal.outstanding_amount
        key = str(journal.id)
        if key in journal_amount_list:
            grand_total += journal_amount_list[key]
        else:
            grand_total += journal.has_outstanding(cutoff_date, False)[1]

    try:
        journal = journal_item_list[0]
        document_dt = journal.due_date
        datetime_object = datetime.datetime.strptime(cutoff_date, '%Y-%m-%d')
        d0 = datetime.date(datetime_object.year, datetime_object.month, datetime_object.day)
        d1 = datetime.date(document_dt.year, document_dt.month, document_dt.day)
        delta = d0 - d1
        to_tsr = str(delta)
        day_str = to_tsr.split(' ')
        if int(day_str[0]) > 122:
            time_tagih = 121
        elif int(day_str[0]) > 92 and int(day_str[0]) < 121:
            time_tagih = 91
        elif int(day_str[0]) > 62 and int(day_str[0]) < 91:
            time_tagih = 61
        elif int(day_str[0]) > 32 and int(day_str[0]) < 61:
            time_tagih = 31
        else:
            time_tagih = ' <30'

        due_days = str(time_tagih)
        payment_term = str(journal.customer.payment_term)

    except Exception as e:
        print(e)
        due_days = ''
        payment_term = ''

    # email_msg = customer.email_msg
    email_msg = None
    if email_msg is None:
        email_msg = CUSTOMER_DEFAULT_MSG
    email_msg = email_msg.replace(EMAIL_MSG_CONST['company_name'], company.name)
    email_msg = email_msg.replace(EMAIL_MSG_CONST['date'], datetime.datetime.now().strftime('%d-%m-%Y'))
    if email_msg.find(EMAIL_MSG_CONST['customer_name']):
        email_msg = email_msg.replace(EMAIL_MSG_CONST['customer_name'], customer.name)
    if email_msg.find(EMAIL_MSG_CONST['currency']):
        email_msg = email_msg.replace(EMAIL_MSG_CONST['currency'], company.currency.code)
    if email_msg.find(EMAIL_MSG_CONST['amount']):
        email_msg = email_msg.replace(EMAIL_MSG_CONST['amount'], intcomma("%.2f" % grand_total))
    if email_msg.find(EMAIL_MSG_CONST['due_days']):
        email_msg = email_msg.replace(EMAIL_MSG_CONST['due_days'], due_days)
    if email_msg.find(EMAIL_MSG_CONST['pay_term']):
        email_msg = email_msg.replace(EMAIL_MSG_CONST['pay_term'], payment_term)

    return email_msg


@login_required
def print_ARCustomers(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_ARAllCustomer_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    if report_type == 'email':
        buffer = BytesIO()
        company = Company.objects.get(pk=company_id)
        company_name = company.name
        if cus_no != '0':
            id_cus_range = cus_no.split(',')
            cust_id_from = int(id_cus_range[0])
            cust_id_to = int(id_cus_range[1])
            if cust_id_from > 0 and cust_id_to > 0:
                customer_code_range = get_customer_filter_range(company_id,
                                                                int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                                                int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')
                cus_email = Customer.objects.filter(id__in=customer_code_range).exclude(email='').exclude(email=None)
            else:
                cus_email = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1).exclude(email='').exclude(email=None)
        else:
            cus_email = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1).exclude(email='').exclude(email=None)
        # get_user_login = Staff.objects.get(pk=request.session['staff_admin'])
        # user_login = User.objects.get(pk=get_user_login.user_id)
        user_login = User.objects.get(pk=request.user.id)
        last_pdf = None
        for e_cus in cus_email:
            send_email_to = e_cus.email

            sender = user_login.email
            receipient_name = e_cus.name

            now = datetime.datetime.now()
            report = Report()

            month = str(now.month)
            if len(month) == 1:
                month = '0' + month
            day = str(now.day)
            if len(day) == 1:
                day = '0' + day
            filename = 'Customer' + str(e_cus.id) + '_' + str(now.year) + '_' + month + '_' + day
            report_arcus = Print_AR_customers(buffer, 'A4')
            pdf, is_sending = report_arcus.print_report_email(company_id, report_type, age_from, cutoff_date, cus_no,
                                                              date_type, doc_type, curr_list, e_cus.id, paid_full)

            report.report_pdf.save(filename + '.pdf', ContentFile(pdf))
            report.save()
            if int(is_sending) > 0:
                email_msg = prepareMessage(e_cus, company, age_from, cutoff_date, doc_type)
                send_email(sender, receipient_name, email_msg, str(now.year) + '/' + month + '/' + day, company_name,
                           send_email_to, os.path.join(s.BASE_DIR, 'media/') + filename + '.pdf')
            report.delete()
            last_pdf = pdf
        response.write(last_pdf)
    else:

        pdf = export_ARCustomers(request, report_type, age_from, cutoff_date, cus_no, date_type, doc_type,
                                 curr_list, paid_full)

        response.write(pdf)
    return response


@login_required
def print_ARAgedTrialSummary(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="AR Aged Summary(%s)%s.pdf' % (company.name, datetime.datetime.now().strftime(
            '%Y%m%d'))

    buffer = BytesIO()
    report = Print_ARAgedTrialSummary(buffer, 'A4')
    pdf = report.print_report(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)

    response.write(pdf)
    return response


@login_required
def print_ARAgedTrialDetail(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="AR Aged Detail(%s)%s.pdf' % (company.name, datetime.datetime.now().strftime(
            '%Y%m%d'))

    buffer = BytesIO()
    report = Print_ARAgedTrialDetail(buffer, 'A4')
    pdf = report.print_report(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)

    response.write(pdf)
    return response


@login_required
def print_APAgedTrialSummary(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="AP Aged Summary(%s)%s.pdf' % (company.name, datetime.datetime.now().strftime(
            '%Y%m%d'))

    buffer = BytesIO()
    report = Print_APAgedTrialSummary(buffer, 'A4')
    pdf = report.print_report(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)

    response.write(pdf)
    return response


@login_required
def print_APAgedTrialDetail(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="AP Aged Detail(%s)%s.pdf' % (company.name, datetime.datetime.now().strftime(
            '%Y%m%d'))

    buffer = BytesIO()
    report = Print_APAgedTrialDetail(buffer, 'A4')
    pdf = report.print_report(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)

    response.write(pdf)
    return response


@login_required
def print_APAgedTrialSummary_XLS(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    file_name = 'report_APAgedTrialSummary_XLS%s.xlsx' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    xls = Print_APAgedTrialSummary_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_APAgedTrialDetail_XLS(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    file_name = 'report_APAgedTrialDetail_XLS%s.xlsx' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    xls = Print_APAgedTrialDetail_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_ARAgedTrialDetail_XLS(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    file_name = 'report_ARAgedTrialDetail_XLS%s.xlsx' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    xls = Print_ARAgedTrialDetail_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_ARAgedTrialSummary_XLS(request, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    file_name = 'report_ARAgedTrialSummary_XLS%s.xlsx' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')
    xls = Print_ARAgedTrialSummary_XLS(output)
    xlsx_report = xls.WriteToExcel(company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


@login_required
def print_GLSourceBalance(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                     calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                     calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_blc_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLSourceBalance(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLSourceBalance_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_blc_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLSource_Balance_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLSourceBalanceBatch_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_blc_batch_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLSource_Balance_Batch_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLSourceBatch_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_batch_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLSource_Batch_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLSource_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLSource_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLSourceBalanceBatch(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_blc_batch_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLSourceBalanceBatch(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLSource(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLSource(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLSourceBatch(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_src_batch_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLSourceBatch(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLFunction_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLFunction_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLFunctionBatch_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_batch_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLFunction_Batch_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLFunctionBalanceBatch_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_blc_batch_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLFunction_Balance_Batch_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLFunctionBalance_XLS(request, issue_from, issue_to, status_type, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_blc_' + 'period_[' + dt + '_' + dt1 + '].xlsx'
        xls = GLFunction_Balance_XLS(output)
        xlsx_report = xls.print_report(company_id, str(first_day), str(
            last_day), status_type, acc_list, array_from[1])

        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLFunction(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLFunction(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLFunctionBatch(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_batch_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLFunctionBatch(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLFunctionBalance(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_blc_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLFunctionBalance(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLFunctionBalanceBatch(request, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0' and issue_to != '0':
        array_from = str(issue_from).split('-')
        array_to = str(issue_to).split('-')
        if array_from[1] in ['ADJ', 'CLS']:
            first_day = datetime.date(int(array_from[0]), 12, 1)
        else:
            first_day = datetime.date(int(array_from[0]), int(array_from[1]), 1)
        if array_to[1] in ['ADJ', 'CLS']:
            last_day = datetime.date(int(array_to[0]), 12,
                                    calendar.monthrange(int(array_to[0]), 12)[1])
        else:
            last_day = datetime.date(int(array_to[0]), int(array_to[1]),
                                    calendar.monthrange(int(array_to[0]), int(array_to[1]))[1])
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name = 'TL_func_blc_batch_' + 'period_[' + dt + '_' + dt1 + '].pdf'
        report = Print_GLFunctionBalanceBatch(buffer, 'A4')
        pdf = report.print_report(company_id, str(first_day), str(
            last_day), status_type, line_1, line_2, line_3, acc_list, array_from[1])
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLBalanceSheet(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0':
        file_name = 'report_GLBalanceSheet_%s.pdf' % datetime.datetime.now().strftime(
            '%Y%m%d_%H%M%S')
        report = Print_GLBalanceSheet(buffer, 'A4')
        pdf = report.print_report(company_id, issue_from, report_type, filter_type, from_val, to_val)
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLBalanceSheet_new(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        file_name = 'BS_prd_%s.pdf' % dt
        report = Print_GLBalanceSheet_new(buffer, 'A4', report_type)
        pdf = report.print_report(company_id, issue_from, filter_type, from_val, to_val)
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_GLBalanceSheetXLS(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0':
        file_name = 'report_GLBalanceSheet_XLS%s.xlsx' % datetime.datetime.now().strftime(
            '%Y%m%d_%H%M%S')
        xls = Print_GLBalanceSheet_XLS(output)
        xlsx_report = xls.WriteToExcel(company_id, issue_from, report_type, filter_type, from_val, to_val)
        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print_GLBalanceSheetXLS_new(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        file_name = 'BS_prd_%s.xlsx' % dt
        xls = Print_GLBalanceSheet_XLS_new(output)
        xlsx_report = xls.WriteToExcel(company_id, issue_from, report_type, filter_type, from_val, to_val)
        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print__GLProfitLoss(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0':
        file_name = 'report_GLProfitLoss_%s.pdf' % datetime.datetime.now().strftime(
            '%Y%m%d_%H%M%S')
        report = Print_GLProfitLoss(buffer, 'A4', report_type)
        pdf = report.print_report(company_id, issue_from, filter_type, from_val, to_val)
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print__GLProfitLoss_new(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        file_name = 'PL_prd_%s.pdf' % dt
        report = Print_GLProfitLoss_new(buffer, 'A4', report_type)
        pdf = report.print_report(company_id, issue_from, filter_type, from_val, to_val)
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print__GLProfitLoss_excel(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0':
        file_name = 'report_GLProfit_loss_XLS%s.xlsx' % datetime.datetime.now().strftime(
            '%Y%m%d_%H%M%S')
        xls = Print_GLProfitLoss_XLS(output)
        xlsx_report = xls.WriteToExcel(company_id, issue_from, report_type, filter_type, from_val, to_val)
        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print__GLProfitLoss_excel_new(request, issue_from, report_type, filter_type, from_val, to_val):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        file_name = 'PL_prd_%s.xlsx' % dt
        xls = Print_GLProfitLoss_XLS_new(output)
        xlsx_report = xls.WriteToExcel(company_id, issue_from, report_type, filter_type, from_val, to_val)
        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print__GLTrial_excel(request, gl_type, issue_from, issue_end, acc_list, is_activity):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        file_name = 'TB_prd_%s.xlsx' % dt
        xls = Print_GLTrial_XLS(output)
        xlsx_report = xls.WriteToExcel(company_id, gl_type, issue_from, issue_end, acc_list,
                                       is_activity)
        response['Content-Disposition'] = 'attachment; filename="' + file_name
        response.write(xlsx_report)
    return response


@login_required
def print__GLTrialBalanceSheet(request, issue_from, issue_to, acc_list, is_activity):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        file_name = 'TB_prd_%s.pdf' % dt
        report = Print_GLTrialBalanceSheet(buffer, 'A4')
        pdf = report.print_report(company_id, issue_from, issue_to, acc_list, is_activity)
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print__GLTrialNetSheet(request, issue_from, issue_to, acc_list, is_activity):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if issue_from != '0':
        dt = issue_from.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = issue_to.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        dtstr = dt + '_' + dt1
        file_name = 'TNS_prdt_%s.pdf' % dtstr
        report = Print_GLTrialNetSheet(buffer, 'A4')
        pdf = report.print_report(company_id, issue_from, issue_to, acc_list, is_activity)
    else:
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_ST_report_IR4200(request, issue_from):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="print_ST_IR4200%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = print_ST_IR4200(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from)

    response.write(pdf)
    return response


@login_required
def print_ST_report_IR4300(request, issue_from):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="print_ST_IR4600%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = print_ST_IR4300(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from)

    response.write(pdf)
    return response


@login_required
def print_ST_report_IR4600(request, issue_from):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="print_ST_IR4600%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = print_ST_IR4600(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from)

    response.write(pdf)
    return response


@login_required
def print_ST_years_trx(request, issue_from, trx_code):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="Print_years_IR4900%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_years_IR4900(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, trx_code)

    response.write(pdf)
    return response


@login_required
def print_ST_stock_value(request, sort_order, print_selection):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="print_ST_stock_value%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_stock_value(buffer, 'A4')
    pdf = report.print_report(company_id, sort_order, print_selection)

    response.write(pdf)
    return response


@login_required
def print_ST_report_IL2601(request, issue_from, location):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_STListFiFoSheet_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    if location is '0':
        location = None
    buffer = BytesIO()
    report = Print_ST_IL2601(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, location)

    response.write(pdf)
    return response


@login_required
def print_STOutBalance(request, issue_from, issue_to):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = 'inline; filename="report_STListFiFoSheet_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_STOutBalance(buffer, 'A4')
    pdf = report.print_report(company_id, issue_from, issue_to)

    response.write(pdf)
    return response


@login_required
def print_tax_tracking(request, tax_authority, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if tax_authority == '0' or tax_authority == '':
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found('Tax Authority')
    else:
        name = tax_report_file_name(from_period_year, to_period_year, print_type, report_by, print_by, transaction_type)
        file_name = '%s.pdf' % name
        report = Print_Tax_Tracking(buffer, 'A4', company_id)
        pdf = report.print_report(company_id, from_period_year, to_period_year, print_type, report_by, print_by,
                                  transaction_type, is_history, tax_authority)
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_tax_item(request, tax_authority, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if tax_authority == '0' or tax_authority == '':
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found('Tax Authority')
    else:
        name = tax_report_file_name(from_period_year, to_period_year, print_type, report_by, print_by, transaction_type)
        file_name = '%s.pdf' % name
        report = Print_Tracking_item(buffer, 'A4', company_id)
        pdf = report.print_report(company_id, from_period_year, to_period_year, print_type, report_by, print_by,
                                  transaction_type, is_history, tax_authority)
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_tax_auth(request, tax_authority, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    if tax_authority == '0' or tax_authority == '':
        file_name = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found('Tax Authority')
    else:
        name = tax_report_file_name(from_period_year, to_period_year, print_type, report_by, print_by, transaction_type)
        file_name = '%s.pdf' % name
        report = Print_Tax_Auth(buffer, 'A4', company_id)
        pdf = report.print_report(company_id, from_period_year, to_period_year, print_type, report_by, print_by,
                                  transaction_type, is_history, tax_authority)
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


def print_tax_auth_XLS(request, tax_authority, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    name = tax_report_file_name(from_period_year, to_period_year, print_type, report_by, print_by, transaction_type)
    file_name = '%s.xlsx' % name
    xls = Print_Tax_Auth_XLS(output, company_id)
    xlsx_report = xls.WriteToExcel(company_id, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history, tax_authority)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


def print_item_tax_XLS(request, tax_authority, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/vnd.ms-excel')
    output = BytesIO()
    name = tax_report_file_name(from_period_year, to_period_year, print_type, report_by, print_by, transaction_type)
    file_name = '%s.xlsx' % name
    xls = Print_Tracking_item_XLS(output, company_id)
    xlsx_report = xls.WriteToExcel(company_id, from_period_year, to_period_year, print_type, report_by, print_by, transaction_type, is_history, tax_authority)
    response['Content-Disposition'] = 'attachment; filename="' + file_name
    response.write(xlsx_report)
    return response


def tax_report_file_name(from_period_year, to_period_year, print_type, report_by, print_by, transaction_type):
    file_name = 'TT_'
    try:
        if 'Functional' in print_type:
            file_name += "func_"
        elif 'Source' in print_type:
            file_name += "src_"
        elif 'Tax' in print_type:
            file_name += "tax_reporting_"

        if 'Fiscal' in report_by:
            file_name += "fiscal_"
        elif 'Document' in report_by:
            file_name += "doc_date_"

        if 'Authority' in transaction_type:
            file_name += "tax_auth_"
        elif 'Item' in transaction_type:
            file_name += "item_tax_"

        if 'Sales' in print_by:
            file_name += "sales_"
        elif 'Purchase' in print_by:
            file_name += "purchase_"

        dt = from_period_year.split('-')
        dt = dt[1] + '-' + dt[0]
        dt1 = to_period_year.split('-')
        dt1 = dt1[1] + '-' + dt1[0]
        file_name += 'period_[' + dt + '_' + dt1 + ']'

    except Exception as e:
        print(e)

    return file_name


@login_required
def print_no_data_found(request):
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    file_name = 'no_data_found.pdf'
    report = Print_Nothing(buffer, 'A4')
    pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + file_name
    response.write(pdf)
    return response


@login_required
def print_AP_revaluation(request, from_posting, to_posting):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_AP_revaluation_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_AP_revaluation(buffer, 'A4')
    pdf = report.print_report(company_id, from_posting, to_posting)
    response.write(pdf)
    return response


@login_required
def print_AR_revaluation(request, from_posting, to_posting):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_AR_revaluation_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_AR_revaluation(buffer, 'A4')
    pdf = report.print_report(company_id, from_posting, to_posting)
    response.write(pdf)
    return response


@login_required
def print_GL_revaluation(request, from_posting, to_posting):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report_GL_revaluation_%s.pdf' % datetime.datetime.now().strftime(
        '%Y%m%d_%H%M%S')

    buffer = BytesIO()
    report = Print_GL_revaluation(buffer, 'A4')
    pdf = report.print_report(company_id, from_posting, to_posting)
    response.write(pdf)
    return response


@login_required
def print_BatchNumber(request, batch_type, batch_from, batch_to, currency, entry_from, entry_to):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()

    if batch_from != '0':
        if int(batch_to) < 0:
            company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
            status_list = [STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted']]
            order_list = Batch.objects.filter(is_hidden=0, company_id=company_id, batch_type=int(batch_type),
                                              status__in=status_list).order_by('-id')
            if order_list:
                batch_to = order_list[0].id

        report = Print_BatchNumber(buffer, 'A4')

        if int(batch_to) > 0 and int(batch_from) != int(batch_to):
            name_file_format = str(Batch.objects.get(pk=int(batch_from)).batch_no) + '_' + str(Batch.objects.get(pk=int(batch_to)).batch_no) + '.pdf'
        else:
            name_file_format = str(Batch.objects.get(pk=int(batch_from)).batch_no) + '.pdf'

        if batch_type == '1':
            name_file_format = "AR_Invoice_" + name_file_format
            pdf = report.print_report_ar_invoice(company_id, batch_type, batch_from, batch_to, entry_from, entry_to)
        elif batch_type == '2':
            name_file_format = "AP_Invoice_" + name_file_format
            pdf = report.print_report_ap_invoice(company_id, batch_type, batch_from, batch_to, entry_from, entry_to)
        elif batch_type == '3':
            name_file_format = "AR_Receipt_" + name_file_format
            pdf = report.print_report_ar_receipt(company_id, batch_type, batch_from, batch_to, entry_from, entry_to)
        elif batch_type == '4':
            name_file_format = "AP_Payment_" + name_file_format
            pdf = report.print_report_ap_payment(company_id, batch_type, batch_from, batch_to, entry_from, entry_to)
        elif currency == '2':
            name_file_format = "GL_Source_function_" + name_file_format
            pdf = report.print_report_gl_source_function(company_id, batch_type, batch_from, batch_to, entry_from, entry_to)
        elif currency == '1':
            name_file_format = "GL_function_" + name_file_format
            pdf = report.print_report_gl_function(company_id, batch_type, batch_from, batch_to, entry_from, entry_to)
        else:
            name_file_format = 'no_data_found.pdf'
    else:
        name_file_format = 'no_data_found.pdf'
        report = Print_Nothing(buffer, 'A4')
        pdf = report.print_not_found()
    response['Content-Disposition'] = 'inline; filename="' + name_file_format
    response.write(pdf)
    return response
