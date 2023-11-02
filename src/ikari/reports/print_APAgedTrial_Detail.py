from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models.fields import related
from accounting.models import Journal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.helpers.aged_trial_report import calculate_total_amount, get_ap_transactions, get_due_period
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.db.models import Q, Sum, Value, F
from django.db.models.functions import Coalesce
from django.conf import settings as s
from reports.print_APAgedTrial_Summary import get_exchange_rate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from django.utils.dateparse import parse_date
from accounting.models import DOCUMENT_TYPES
from transactions.models import Transaction
from utilities.constants import DOCUMENT_TYPES_IN_REPORT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, STATUS_TYPE_DICT
from utilities.common import round_number
from currencies.models import Currency
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from decimal import Decimal


class Print_APAgedTrialDetail:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, age_from, cutoff_date, cus_no, date_type, doc_type):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # # 2nd row
        row2_info1 = "A/P Aged Payables by Due Date (APAPAY11)"
        header_data.append([row2_info1])
        # 3rd row
        row3_info1 = " "
        header_data.append([row3_info1])
        # 4st row
        row4_info1 = "Age Transaction Of As "
        row4_info2 = "[" + parse_date(age_from).strftime('%d/%m/%Y') + "]"
        header_data.append([row4_info1, row4_info2])
        # 5st row
        if int(date_type) == 2:
            row5_info1 = "CutOff by Posting Date "
        else:
            row5_info1 = "CutOff by Document Date "
        row5_info2 = "[" + parse_date(cutoff_date).strftime('%d/%m/%Y') + "]"
        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[280, 100, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('TOPPADDING', (0, 0), (-1, -1), -0.2),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 18)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _header_last_footer(canvas, doc, company_id, age_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # # 2nd row
        row2_info1 = "A/P Aged Payables by Due Date (APAPAY11)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=[280, 5, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('TOPPADDING', (0, 0), (-1, -1), -0.2),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        first_p = str(age_period['current'] + 1) + ' To ' + str(age_period['1st'])
        second_p = str(age_period['1st'] + 1) + ' To ' + str(age_period['2nd'])
        third_p = str(age_period['2nd'] + 1) + ' To ' + str(age_period['3rd'])
        over_p = 'Over ' + str(age_period['3rd'])
        # # 1ST ROW
        table_header = ['Doc.Date', '', 'Doc.Type/Doc.Number', '', 'Due Date', '', '', '', first_p,
                        '', second_p, '', third_p, '', over_p, '', 'Total', '', 'Total']
        table_data.append(table_header)
        # 2ND ROW
        table_header = ['Appl.Date', '', 'Applied No.', '', 'App.Type', '', 'Current', '', 'Days',
                        '', 'Days', '', 'Days', '', 'Days', '', 'Overdue', '', 'Payables']

        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[60, 5, 130, 5, 80, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 6),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
             ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
             ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
             ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
             ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
             ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
             ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
             ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
             ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
             ('LINEBELOW', (-1, -1), (-1, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1 - 18)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
        company = Company.objects.get(pk=company_id)
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN,
                                topMargin=s.REPORT_TOP_MARGIN, bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE_2))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE_2))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        is_full_paid = '[No]'
        if int(paid_full):
            is_full_paid = '[Yes]'

        age_period = {'current': 0, '1st': 31, '2nd': 61, '3rd': 91}
        periods = periods.split(',')
        age_period['current'] = int(periods[0])
        age_period['1st'] = int(periods[1])
        age_period['2nd'] = int(periods[2])
        age_period['3rd'] = int(periods[3])

        doc_select = ''
        doc_type_array = []
        if doc_type:
            passing = doc_type.split(',')
            for code in passing:
                doc_select += dict(DOCUMENT_TYPES)[code] + ', '
                doc_type_array.append(code)
            doc_select = doc_select[:-2]

        if curr_list == '1':
            print_amount = 'Vendor Currency'
        else:
            print_amount = 'Functional Currency'

        table_data.append(['Print Transactions in', '[Detail by Document Date]', ''])
        table_data.append(['Transaction Type', '[' + doc_select + ']', ''])
        table_data.append(['Include Phone/Contact/Credit Limit', '[No]', ''])
        table_data.append(['Include Space For Comments', '[No]', ''])
        table_data.append(['Include Zero Balance Vendors', '[No]', ''])
        table_data.append(['Include Vendors/Transactions on Hold', '[No]', ''])
        table_data.append(['Show Applied Details', '[No] ', ''])
        table_data.append(['Show Full Paid Transactions', is_full_paid, ''])
        table_data.append(['Sort Transaction by Transcation Type', '[No] ', ''])
        table_data.append(['Print Amounts In', '[' + print_amount + ']', ''])
        table_data.append('')

        item_table = Table(table_data, colWidths=[280, 330, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.1, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, 0), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('TOPPADDING', (0, 0), (-1, -1), -0.2),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
             ]))
        elements.append(item_table)

        table_data = []
        first_p = str(age_period['current'] + 1) + ' To ' + str(age_period['1st'])
        second_p = str(age_period['1st'] + 1) + ' To ' + str(age_period['2nd'])
        third_p = str(age_period['2nd'] + 1) + ' To ' + str(age_period['3rd'])
        over_p = 'Over ' + str(age_period['3rd'])
        table_data.append(['Doc.Date', '', 'Doc.Type/Doc.Number', '', 'Due Date', '', '', '', first_p,
                           '', second_p, '', third_p, '', over_p, '', 'Total', '', 'Total'])

        table_data.append(['Appl.Date', '', 'Applied No.', '', 'App.Type', '', 'Current', '', 'Days',
                           '', 'Days', '', 'Days', '', 'Days', '', 'Overdue', '', 'Payables'])

        item_table = Table(table_data, colWidths=[60, 5, 130, 5, 80, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 6),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
             ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
             ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
             ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
             ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
             ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
             ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
             ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
             ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
             ('LINEBELOW', (-1, -1), (-1, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        # end design interface header

        # process table_data
        journal_type = dict(TRANSACTION_TYPES)['AP Payment']

        ap_collections = get_ap_transactions(company_id=company_id, cus_no=cus_no, cutoff_date=cutoff_date,
                                             date_type=date_type, paid_full=paid_full, doc_type_array=tuple(doc_type_array))

        journal_item_list = ap_collections.journal_item_list
        adjustment_journal_list = ap_collections.adjustment_journal_list
        journal_amount_list = ap_collections.journal_amount_list
        journal_item_vendor_count = 0

        m_supplier_code = ''
        m_currency = ''
        l_currency = None

        if int(curr_list) == 1:
            simbol_curr = ''
        else:
            curr = Currency.objects.get(pk=company.currency_id)
            simbol_curr = curr.code

        exchange_rate = 1
        sum_amount = 0
        table_money = []
        total_current = total_1st = total_2nd = total_3rd = total_4th = total_over = 0
        sum_cus_current = sum_cus_1st = sum_cus_2nd = sum_cus_3rd = sum_cus_4th = sum_all_cus = sum_over = 0
        v_elements = []
        colWidths=[60, 20, 115, 5, 80, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70]
        if journal_item_list:
            for i, journal in enumerate(journal_item_list):
                # check to print first row of supplier
                if (m_supplier_code != journal.supplier.code) | (
                        (m_supplier_code == journal.supplier.code) & (m_currency != journal.currency.code)):
                    if i != 0:
                        table_data = []
                        sum_all_cus = sum_cus_current + sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th
                        sum_over = sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th

                        if int(curr_list) == 1:
                            is_decimal = l_currency.is_decimal if l_currency else True
                        else:
                            is_decimal = company.currency.is_decimal if company else True
                        decimal_point = "%.2f"
                        if not is_decimal:
                            decimal_point = "%.0f"
                        table_data.append(['', '', Paragraph('Vendor Total:', styles['LeftAlignBold']), '', simbol_curr if simbol_curr else m_currency,
                                           '', intcomma(decimal_point % round_number(sum_cus_current)),
                                           '', intcomma(decimal_point % round_number(sum_cus_1st)),
                                           '', intcomma(decimal_point % round_number(sum_cus_2nd)),
                                           '', intcomma(decimal_point % round_number(sum_cus_3rd)),
                                           '', intcomma(decimal_point % round_number(sum_cus_4th)),
                                           '', intcomma(decimal_point % round_number(sum_over)),
                                           '', intcomma(decimal_point % round_number(sum_all_cus))])

                        item_table = Table(table_data, colWidths=[60, 5, 175, 10, 30, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('FONTSIZE', (0, 0), (-1, 0), s.REPORT_FONT_SIZE_2),
                             ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
                             ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
                             ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                             ('LINEABOVE', (12, 0), (12, 0), 0.25, colors.black),
                             ('LINEABOVE', (14, 0), (14, 0), 0.25, colors.black),
                             ('LINEABOVE', (16, 0), (16, 0), 0.25, colors.black),
                             ('LINEABOVE', (-1, 0), (-1, 0), 0.25, colors.black),
                             ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD),
                             ('TOPPADDING', (0, 0), (-1, -1), 0),
                             ('BOTTOMPADDING', (0, -1), (-1, -1), 7),
                             ]))
                        v_elements.append(item_table)
                        if int(paid_full) or round_number(sum_all_cus) != 0:
                            table_money.append([simbol_curr if simbol_curr else m_currency, sum_cus_current, sum_cus_1st, sum_cus_2nd, sum_cus_3rd, sum_cus_4th])
                            elements.extend(v_elements)
                            journal_item_vendor_count += 1
                        v_elements = []

                        sum_all_cus = sum_cus_current = sum_cus_1st = sum_cus_2nd = sum_cus_3rd = sum_cus_4th = sum_over = 0

                    table_data = []
                    m_supplier_code = journal.supplier.code
                    m_currency = journal.currency.code
                    l_currency = journal.currency
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    sum_amount = 0

                    table_data.append(['Vendor No.:', '', journal.supplier.code if journal.supplier_id else '', '', '',
                                       '', '', 'Vendor Name.:', '', journal.supplier.name if journal.supplier_id and journal.supplier.name else '',
                                       '', '', '', '', '', '', '', '', '', ])

                    item_table = Table(table_data, colWidths=[60, 15, 80, 10, 60, 5, 65, 5, 80, 65, 65, 5, 65, 5, 65, 5, 70, 5, 70])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, 0), s.REPORT_FONT_SIZE_2),
                         ('FONT', (0, 0), (0, -1), s.REPORT_FONT_BOLD),
                         ('FONT', (7, 0), (7, -1), s.REPORT_FONT_BOLD),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                         ]))
                    v_elements.append(item_table)

                if (m_supplier_code == journal.supplier.code) & (m_currency == journal.currency.code):
                    curr_code = ''
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    day_due = journal.due_date if journal.due_date else journal.document_date
                    day_age = datetime.datetime.strptime(age_from, '%Y-%m-%d').date()

                    # total_amount = calculate_total_amount(journal, journal_type, cutoff_date)
                    try:
                        key = str(journal.id)
                        total_amount = journal_amount_list[key]
                    except Exception as e:
                        total_amount = journal.has_outstanding(cutoff_date, True)[1]

                    if int(curr_list) == 1:
                        curr_code = journal.currency.code
                        is_decimal = journal.currency.is_decimal if journal.currency else True
                    else:
                        total_amount = round_number(total_amount * exchange_rate)
                        curr_code = simbol_curr
                        is_decimal = company.currency.is_decimal if company else True
                    sum_amount += total_amount
                    decimal_point = "%.2f"
                    if not is_decimal:
                        decimal_point = "%.0f"

                    adj_data = None
                    if str(journal.id) in adjustment_journal_list.keys():
                        adj_data = adjustment_journal_list[str(journal.id)]

                    if journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                        if day_due and day_age:
                            if day_age > day_due and journal.document_type not in [DOCUMENT_TYPE_DICT['Credit Note'], DOCUMENT_TYPE_DICT['Debit Note']]:
                                diff_day = (day_age - day_due).days
                                due_period = get_due_period(diff_day=diff_day, period_current=age_period['current'], period_1st=age_period['1st'],
                                                            period_2nd=age_period['2nd'], period_3rd=age_period['3rd'], total=total_amount)
                                total_current += due_period['total_current']
                                total_1st += due_period['total_1st']
                                total_2nd += due_period['total_2nd']
                                total_3rd += due_period['total_3rd']
                                total_4th += due_period['total_4th']
                            else:
                                total_current += total_amount
                        else:
                            total_current += total_amount

                        sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                        total_over = total_1st + total_2nd + total_3rd + total_4th
                        sum_cus_current += total_current
                        sum_cus_1st += total_1st
                        sum_cus_2nd += total_2nd
                        sum_cus_3rd += total_3rd
                        sum_cus_4th += total_4th
                        sum_over += total_over

                    document_type_dict = dict(DOCUMENT_TYPES_IN_REPORT)
                    table_data = []
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                        if round_number(sum_amount) != 0:
                            table_data.append([journal.document_date.strftime("%d/%m/%Y") if journal.document_date else '',
                                            document_type_dict.get(journal.document_type) if journal.document_type else '',
                                            journal.document_number[:20] if journal.document_number else '',
                                            '', journal.due_date.strftime("%d/%m/%Y") if journal.due_date else '',
                                            '', intcomma(decimal_point % round_number(total_current)) if Decimal(total_current) else '',
                                            '', intcomma(decimal_point % round_number(total_1st)) if Decimal(total_1st) else '',
                                            '', intcomma(decimal_point % round_number(total_2nd)) if Decimal(total_2nd) else '',
                                            '', intcomma(decimal_point % round_number(total_3rd)) if Decimal(total_3rd) else '',
                                            '', intcomma(decimal_point % round_number(total_4th)) if Decimal(total_4th) else '',
                                            '', intcomma(decimal_point % round_number(total_over)) if Decimal(total_over) else '',
                                            '', intcomma(decimal_point % round_number(sum_amount)) if Decimal(sum_amount) else ''])

                            item_table = Table(table_data, colWidths=colWidths)
                        else:
                            item_table = None
                    else:
                        table_data.append([journal.document_date.strftime("%d/%m/%Y") if journal.document_date else '',
                                           document_type_dict.get(journal.document_type) if journal.document_type else '',
                                           journal.document_number[:25] if journal.document_number else '',
                                           '', journal.due_date.strftime("%d/%m/%Y") if journal.due_date else journal.document_date,
                                           '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                        item_table = Table(table_data, colWidths=colWidths)
                    if int(paid_full):
                        paid_transactions = Transaction.objects.filter(related_invoice_id=journal.id,
                                                journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
                                            ).exclude(journal_id__isnull=True
                                            ).exclude(related_invoice_id__isnull=True
                                            ).exclude(journal__reverse_reconciliation=True
                                            ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']
                                            ).exclude(is_hidden=True
                                            ).order_by('journal__document_date', '-id')
                        try:
                            for paid_t in paid_transactions:
                                table_data.append([paid_t.journal.document_date.strftime("%d/%m/%Y") if paid_t.journal.document_date else '', '',
                                                paid_t.journal.document_number[:25] if paid_t.journal.document_number else '',
                                                '', document_type_dict.get(paid_t.journal.document_type) if paid_t.journal.document_type else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(total_current) else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(total_1st) else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(total_2nd) else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(total_3rd) else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(total_4th) else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(total_over) else '',
                                                '', intcomma(decimal_point % round_number((-1)*paid_t.total_amount)) if Decimal(sum_amount) else ''])
                            if len(paid_transactions):
                                table_data.append([])
                                item_table = Table(table_data, colWidths=colWidths)
                                
                                sum_cus_current -= total_current
                                sum_cus_1st -= total_1st
                                sum_cus_2nd -= total_2nd
                                sum_cus_3rd -= total_3rd
                                sum_cus_4th -= total_4th
                                sum_over -= total_over
                        except Exception as e:
                            print(e)
                    if adj_data:
                        table_data.append(['AD', 'AD0000000000000' + str(adj_data['doc']) if adj_data['doc'] else '', '',
                                           adj_data['doc_date'].strftime("%d/%m/%Y") if adj_data['doc_date'] else ' / / ',
                                           journal.document_number if journal.document_number else '',
                                           '', '', '', '', '', '', '', '', '', '', '', ''])
                        item_table = Table(table_data, colWidths=colWidths)

                    if item_table:
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                            ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                            ]))
                        v_elements.append(item_table)
                    sum_amount = total_current = total_1st = total_2nd = total_3rd = total_4th = total_over = 0
                if i == journal_item_list.__len__() - 1:
                    table_data = []
                    sum_all_cus = sum_cus_current + sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th
                    sum_over = sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th
                    table_data.append(['', '', Paragraph('Vendor Total:', styles['LeftAlignBold']),
                                       '', curr_code if curr_code else m_currency,
                                       '', intcomma(decimal_point % round_number(sum_cus_current)),
                                       '', intcomma(decimal_point % round_number(sum_cus_1st)),
                                       '', intcomma(decimal_point % round_number(sum_cus_2nd)),
                                       '', intcomma(decimal_point % round_number(sum_cus_3rd)),
                                       '', intcomma(decimal_point % round_number(sum_cus_4th)),
                                       '', intcomma(decimal_point % round_number(sum_over)),
                                       '', intcomma(decimal_point % round_number(sum_all_cus))])

                    item_table = Table(table_data, colWidths=[60, 5, 180, 5, 30, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                         ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
                         ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
                         ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                         ('LINEABOVE', (12, 0), (12, 0), 0.25, colors.black),
                         ('LINEABOVE', (14, 0), (14, 0), 0.25, colors.black),
                         ('LINEABOVE', (16, 0), (16, 0), 0.25, colors.black),
                         ('LINEABOVE', (-1, 0), (-1, 0), 0.25, colors.black),
                         ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, -1), (-1, -1), 7),
                         ]))
                    v_elements.append(item_table)
                    if int(paid_full) or round_number(sum_all_cus) != 0:
                        table_money.append([curr_code if curr_code else m_currency, sum_cus_current, sum_cus_1st, sum_cus_2nd, sum_cus_3rd, sum_cus_4th])
                        elements.extend(v_elements)
                        journal_item_vendor_count += 1
                    v_elements = []

            table_data = []
            if table_money:
                sum_currency(table_money, table_data, curr_list)
                item_table = Table(table_data, colWidths=[60, 5, 180, 5, 30, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
                if curr_list == '1':
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                         ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
                         ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
                         ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                         ('LINEABOVE', (12, 0), (12, 0), 0.25, colors.black),
                         ('LINEABOVE', (14, 0), (14, 0), 0.25, colors.black),
                         ('LINEABOVE', (16, 0), (16, 0), 0.25, colors.black),
                         ('LINEABOVE', (-1, 0), (-1, 0), 0.25, colors.black),
                         ('FONT', (2, 0), (-1, -1), s.REPORT_FONT_BOLD),
                         ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                         ]))
                else:
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                         ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                         ('LINEABOVE', (8, 1), (8, 1), 0.25, colors.black),
                         ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
                         ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                         ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
                         ('LINEABOVE', (16, 1), (16, 1), 0.25, colors.black),
                         ('LINEABOVE', (18, 1), (18, 1), 0.25, colors.black),
                         ('LINEABOVE', (6, 2), (6, 2), 0.25, colors.black),
                         ('LINEABOVE', (8, 2), (8, 2), 0.25, colors.black),
                         ('LINEABOVE', (10, 2), (10, 2), 0.25, colors.black),
                         ('LINEABOVE', (12, 2), (12, 2), 0.25, colors.black),
                         ('LINEABOVE', (14, 2), (14, 2), 0.25, colors.black),
                         ('LINEABOVE', (16, 2), (16, 2), 0.25, colors.black),
                         ('LINEABOVE', (18, 2), (18, 2), 0.25, colors.black),
                         ('FONT', (2, 0), (-1, -1), s.REPORT_FONT_BOLD),
                         ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP')
                         ]))
                elements.append(item_table)

            table_data = []
            table_data.append(['', '', '', '', '', '', ''])
            table_data.append(['CR:Credit Note', 'DB:Debit Note', 'IN:Invoice ', 'IT:Interest Charge', 'PI:Prepayment', '', 'MC:Miscellaneous Payment', ])

            table_data.append(['AD:Adjustment', 'CF:Applied Credit (from)', 'CT:Applied Credit (to)',
                               'DF:Applied Debit (from)', 'DT:Applied Debit (to)', '', '', ])

            table_data.append(['ED:Earned Discount Taken ', 'GL:Gain or Loss (multicurrency ledgers)', '', 'PY:Payment', 'RD:Rounding', '', '', ])

            table_data.append([str(journal_item_vendor_count) + ' vendors printed', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[150, 145, 120, 125, 120, 15, 120])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (-1, 0), s.REPORT_FONT_SIZE_2),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONT', (0, 0), (-1, 3), s.REPORT_FONT_ITALIC),
                 ('FONT', (0, -1), (0, -1), s.REPORT_FONT_BOLD),
                 ]))
            elements.append(item_table)

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[100, 130, 110, 105, 75, 60, 85, 10, 130])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, age_from=age_from,
                                      cutoff_date=cutoff_date, cus_no=cus_no, date_type=date_type, doc_type=doc_type),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, age_period=age_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


def transaction_processing(cleaned_journal_list, journal_list, Journal_type, cutoff_date, credit_note_list, debit_note_list, adjustment_journal_list):
    for journal in journal_list:
        full_transaction_list = Transaction.objects.filter(related_invoice=journal, journal__document_date__lte=cutoff_date
                                                           ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True)
        payment_total = full_transaction_list.aggregate(total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))

        if journal.total_amount > payment_total['total']:
            cleaned_journal_list.append(journal.id)
            credit_note = full_transaction_list.filter(journal__document_type=DOCUMENT_TYPE_DICT['Credit Note'])
            debit_note = full_transaction_list.filter(journal__document_type=DOCUMENT_TYPE_DICT['Debit Note'])
            adjustment_trx = full_transaction_list.filter(journal__document_type=DOCUMENT_TYPE_DICT['Adjustment'])
            adjustment = full_transaction_list.filter(journal__document_type=DOCUMENT_TYPE_DICT['Adjustment']).aggregate(
                total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))

            if len(adjustment_trx):
                adjustment_trx = adjustment_trx.last()
                adjustment_journal_list.update(
                    {
                        str(journal.id): {
                            'doc': adjustment_trx.journal.document_number,
                            'amount': adjustment['total'],
                            'doc_date': adjustment_trx.transaction_date
                        }
                    }
                )

            if credit_note:
                credit_note = credit_note.values_list('journal_id', flat=True)
                credit_note_list = credit_note_list.filter(~Q(pk__in=credit_note))

            if debit_note:
                debit_note = debit_note.values_list('journal_id', flat=True)
                debit_note_list = debit_note_list.filter(~Q(pk__in=debit_note))

    return cleaned_journal_list, credit_note_list, debit_note_list, adjustment_journal_list


def sum_currency(table_money, table_data, curr_list):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE_2))
    table_money = sorted(table_money, key=lambda code: code[0])
    nline = 0
    sum_over = sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
    for k, j in enumerate(table_money):
        if k == 0:
            money = table_money[k][0]
        if (table_money[k][0] == money):
            money = table_money[k][0]
            sum_current += table_money[k][1]
            sum_1st += table_money[k][2]
            sum_2nd += table_money[k][3]
            sum_3rd += table_money[k][4]
            sum_4th += table_money[k][5]
        else:
            sum_over = round_number(sum_1st) + round_number(sum_2nd) + round_number(sum_3rd) + round_number(sum_4th)
            sum_all = round_number(sum_current) + round_number(sum_1st) + round_number(sum_2nd) + round_number(sum_3rd) + round_number(sum_4th)
            try:
                is_decimal = Currency.objects.get(code=money).is_decimal
            except:
                is_decimal = True
            decimal_point = "%.2f"
            if not is_decimal:
                decimal_point = "%.0f"
            if nline == 0:
                table_data.append(['', '', Paragraph('Report Total:', styles['LeftAlignBold']), '', money, '',
                                   intcomma(decimal_point % round_number(sum_current)),
                                   '', intcomma(decimal_point % round_number(sum_1st)),
                                   '', intcomma(decimal_point % round_number(sum_2nd)),
                                   '', intcomma(decimal_point % round_number(sum_3rd)),
                                   '', intcomma(decimal_point % round_number(sum_4th)),
                                   '', intcomma(decimal_point % round_number(sum_over)),
                                   '', intcomma(decimal_point % round_number(sum_all))])
                if curr_list != '1':
                    table_data.append(['', '', '', '', '', '', intcomma(decimal_point % round_number(sum_current * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_1st * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_4th * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_over * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_all * 100 / sum_all)) + '%'])
            else:
                table_data.append(['', '', '', '', money, '', intcomma(decimal_point % round_number(sum_current)),
                                   '', intcomma(decimal_point % round_number(sum_1st)),
                                   '', intcomma(decimal_point % round_number(sum_2nd)),
                                   '', intcomma(decimal_point % round_number(sum_3rd)),
                                   '', intcomma(decimal_point % round_number(sum_4th)),
                                   '', intcomma(decimal_point % round_number(sum_over)),
                                   '', intcomma(decimal_point % round_number(sum_all))])
            nline = 1

            money = table_money[k][0]
            sum_over = sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
            sum_current += table_money[k][1]
            sum_1st += table_money[k][2]
            sum_2nd += table_money[k][3]
            sum_3rd += table_money[k][4]
            sum_4th += table_money[k][5]

        if k == len(table_money) - 1:
            sum_over = round_number(sum_1st) + round_number(sum_2nd) + round_number(sum_3rd) + round_number(sum_4th)
            sum_all = round_number(sum_current) + round_number(sum_1st) + round_number(sum_2nd) + round_number(sum_3rd) + round_number(sum_4th)
            try:
                is_decimal = Currency.objects.get(code=money).is_decimal
            except:
                is_decimal = True
            decimal_point = "%.2f"
            if not is_decimal:
                decimal_point = "%.0f"
            if nline == 0:
                table_data.append(['', '', Paragraph('Report Total:', styles['LeftAlignBold']), '', money, '',
                                   intcomma(decimal_point % round_number(sum_current)),
                                   '', intcomma(decimal_point % round_number(sum_1st)),
                                   '', intcomma(decimal_point % round_number(sum_2nd)),
                                   '', intcomma(decimal_point % round_number(sum_3rd)),
                                   '', intcomma(decimal_point % round_number(sum_4th)),
                                   '', intcomma(decimal_point % round_number(sum_over)),
                                   '', intcomma(decimal_point % round_number(sum_all))])
                if curr_list != '1':
                    table_data.append(['', '', '', '', '', '', intcomma(decimal_point % round_number(sum_current * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_1st * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_4th * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_over * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_all * 100 / sum_all)) + '%'])
            else:
                table_data.append(['', '', '', '', money, '',
                                   intcomma(decimal_point % round_number(sum_current)),
                                   '', intcomma(decimal_point % round_number(sum_1st)),
                                   '', intcomma(decimal_point % round_number(sum_2nd)),
                                   '', intcomma(decimal_point % round_number(sum_3rd)),
                                   '', intcomma(decimal_point % round_number(sum_4th)),
                                   '', intcomma(decimal_point % round_number(sum_over)),
                                   '', intcomma(decimal_point % round_number(sum_all))])

