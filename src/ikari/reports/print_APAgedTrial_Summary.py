from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from django.utils.dateparse import parse_date
from accounting.models import DOCUMENT_TYPES, RevaluationDetails
from currencies.models import Currency, ExchangeRate
from reports.helpers.aged_trial_report import calculate_total_amount, get_ap_transactions
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import TRANSACTION_TYPES, DOCUMENT_TYPE_DICT
from utilities.common import round_number


class Print_APAgedTrialSummary:
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
        row2_info1 = "A/P Aged Payables by Due Date (APAPAYSY)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_data.append('')
        # # 3rd row
        row3_info1 = "Age Transaction Of As "
        row3_info2 = "[" + parse_date(age_from).strftime('%d/%m/%Y') + "]"
        header_data.append([row3_info1, row3_info2])
        # # 5st row
        if int(date_type) == 2:
            row4_info1 = "CutOff by Posting Date "
        else:
            row4_info1 = "CutOff by Document Date "
        row4_info2 = "[" + parse_date(cutoff_date).strftime('%d/%m/%Y') + "]"
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[280, 200, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONTSIZE', (0, 0), (-1, -1), 7),
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
        row2_info1 = "A/P Aged Trial Balance by Due Date (ARTBALSY)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=[280, 330, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), 7),
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
        table_header = ['Vendor No.', '', 'Vendor Name.', '', 'Cur.', '', 'Current', '', 'Days',
                        '', 'Days', '', 'Days', '', 'Days', '', 'Overdue', '', 'Payables', ]

        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[60, 5, 170, 5, 30, 5, 90, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), 7),
             ('TOPPADDING', (0, 0), (-1, -1), -0.2),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LINEABOVE', (0, 2), (0, 2), 0.25, colors.black),
             ('LINEABOVE', (2, 2), (2, 2), 0.25, colors.black),
             ('LINEABOVE', (4, 2), (4, 2), 0.25, colors.black),
             ('LINEABOVE', (6, 2), (6, 2), 0.25, colors.black),
             ('LINEABOVE', (8, 2), (8, 2), 0.25, colors.black),
             ('LINEABOVE', (10, 2), (10, 2), 0.25, colors.black),
             ('LINEABOVE', (12, 2), (12, 2), 0.25, colors.black),
             ('LINEABOVE', (14, 2), (14, 2), 0.25, colors.black),
             ('LINEABOVE', (-1, 2), (-1, 2), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
        company = Company.objects.get(pk=company_id)
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='normal', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=7))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=7))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=7))
        elements = []
        table_data = []

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

        table_data.append(['Print Transactions in', '[Summary]', ''])
        table_data.append(['Transaction Type', '[' + doc_select + ']', ''])
        table_data.append(['Include Phone/Contact/Credit Limit', '[No]', ''])
        table_data.append(['Include Space For Comments', '[No]', ''])
        table_data.append(['Include Zero Balance Vendors', '[No]', ''])
        table_data.append(['Include Vendors/Transactions on Hold', '[No]', ''])
        table_data.append(['Print Amounts In', print_amount, ''])

        item_table = Table(table_data, colWidths=[280, 330, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), 7),
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

        table_data.append(['Vendor No.', '', 'Vendor Name.', '', 'Cur.', '', 'Current', '', 'Days',
                           '', 'Days', '', 'Days', '', 'Days', '', 'Overdue', '', 'Payables'])

        item_table = Table(table_data, colWidths=[60, 5, 170, 5, 30, 5, 90, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), 7),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
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
        journal_type = dict(TRANSACTION_TYPES)['AP Payment']
        ap_collections = get_ap_transactions(
            company_id=company_id,
            cus_no=cus_no,
            cutoff_date=cutoff_date, date_type=date_type,
            paid_full=paid_full, doc_type_array=tuple(doc_type_array)
        )

        journal_item_list = ap_collections.journal_item_list
        journal_amount_list = ap_collections.journal_amount_list
        journal_item_vendor_count = 0
        journal_item_list_currency = journal_item_list.values_list('currency__code') \
                                                      .annotate(amount_sum=Sum('total_amount')) \
                                                      .order_by('currency__code').distinct()

        if int(curr_list) == 1:
            simbol_curr = ''
        else:
            company = Company.objects.get(pk=company_id)
            curr = Currency.objects.get(pk=company.currency_id)
            simbol_curr = curr.code

        table_money = []
        m_supplier_code = ''
        m_currency = 0
        sum_amount = 0
        exchange_rate = 1
        total_current = total_1st = total_2nd = total_3rd = total_4th = 0

        if journal_item_list:
            for i, journal in enumerate(journal_item_list):
                if i == 0:
                    m_supplier_code = journal.supplier.code
                    m_currency = journal.currency.code

                if (m_supplier_code != journal.supplier.code) \
                        | ((m_currency != journal.currency.code) & (
                            m_supplier_code == journal.supplier.code)):
                    table_data = []
                    m_supplier_code = journal.supplier.code
                    m_currency = journal.currency.code
                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                    sum_over = total_1st + total_2nd + total_3rd + total_4th
                    if int(curr_list) == 1:
                        is_decimal = journal_item_list[i - 1].currency.is_decimal if journal_item_list[i - 1].currency else True
                    else:
                        is_decimal = company.currency.is_decimal if company else True
                    decimal_point = "%.2f"
                    if not is_decimal:
                        decimal_point = "%.0f"
                    if round_number(sum_amount) != 0:
                        table_data.append([Paragraph(journal_item_list[i - 1].supplier.code if journal_item_list[i - 1].supplier_id else '', styles['normal']), '',
                                        Paragraph(journal_item_list[i - 1].supplier.name if journal_item_list[i - 1].supplier_id and journal_item_list[i - 1].supplier.name else '',
                                                    styles['normal']),
                                        '', simbol_curr if simbol_curr else journal_item_list[i - 1].currency.code,
                                        '', intcomma(decimal_point % round_number(total_current)),
                                        '', intcomma(decimal_point % round_number(total_1st)),
                                        '', intcomma(decimal_point % round_number(total_2nd)),
                                        '', intcomma(decimal_point % round_number(total_3rd)),
                                        '', intcomma(decimal_point % round_number(total_4th)),
                                        '', intcomma(decimal_point % round_number(sum_over)),
                                        '', intcomma(decimal_point % round_number(sum_amount))])

                        item_table = Table(table_data, colWidths=[60, 5, 180, 5, 30, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('FONTSIZE', (0, 0), (-1, -1), 7),
                            ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                            ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP')
                            ]))
                        elements.append(item_table)
                        table_money.append([simbol_curr if simbol_curr else journal_item_list[i - 1].currency.code, total_current, total_1st, total_2nd, total_3rd, total_4th])
                        journal_item_vendor_count += 1

                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)

                    sum_amount = sum_over = 0
                    total_current = total_1st = total_2nd = total_3rd = total_4th = 0
                if m_supplier_code == journal.supplier.code:
                    curr_code = ''
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    day_due = journal.due_date
                    day_age = datetime.datetime.strptime(age_from, '%Y-%m-%d').date()

                    # total_amount = calculate_total_amount(journal, journal_type, cutoff_date)
                    try:
                        key = str(journal.id)
                        total_amount = journal_amount_list[key]
                    except:
                        total_amount = journal.has_outstanding(cutoff_date)[1]

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

                    if day_due and day_age:
                        if day_age > day_due and journal.document_type not in [DOCUMENT_TYPE_DICT['Credit Note'], DOCUMENT_TYPE_DICT['Debit Note']]:
                            check_day = (day_age - day_due)
                            if int(check_day.days) <= age_period['1st'] and int(check_day.days) > age_period['current']:
                                total_1st += total_amount
                            else:
                                if int(check_day.days) <= age_period['2nd']:
                                    total_2nd += total_amount
                                else:
                                    if int(check_day.days) <= age_period['3rd']:
                                        total_3rd += total_amount
                                    else:
                                        total_4th += total_amount
                        else:
                            total_current += total_amount
                    else:
                        total_current += journal.total_amount

                if i == journal_item_list.__len__() - 1:
                    table_data = []
                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                    sum_over = total_1st + total_2nd + total_3rd + total_4th
                    if int(curr_list) == 1:
                        is_decimal = journal.currency.is_decimal if journal.currency else True
                    else:
                        is_decimal = company.currency.is_decimal if company else True
                    decimal_point = "%.2f"
                    if not is_decimal:
                        decimal_point = "%.0f"
                    if round_number(sum_amount) != 0:
                        table_data.append([Paragraph(journal.supplier.code if journal.supplier_id else '', styles['normal']), '',
                                        Paragraph(journal.supplier.name if journal.supplier_id and journal.supplier.name else '', styles['normal']),
                                        '', simbol_curr if simbol_curr else journal.currency.code,
                                        '', intcomma(decimal_point % round_number(total_current)),
                                        '', intcomma(decimal_point % round_number(total_1st)),
                                        '', intcomma(decimal_point % round_number(total_2nd)),
                                        '', intcomma(decimal_point % round_number(total_3rd)),
                                        '', intcomma(decimal_point % round_number(total_4th)),
                                        '', intcomma(decimal_point % round_number(sum_over)),
                                        '', intcomma(decimal_point % round_number(sum_amount))])

                        item_table = Table(table_data, colWidths=[60, 5, 180, 5, 30, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('FONTSIZE', (0, 0), (-1, -1), 7),
                            ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                            ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP')
                            ]))
                        elements.append(item_table)
                        table_money.append([simbol_curr if simbol_curr else journal.currency.code, total_current, total_1st, total_2nd, total_3rd, total_4th])
                        journal_item_vendor_count += 1

        if journal_item_list_currency:
            table_data = []
            table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

            sum_currency(table_money, table_data, curr_list)

            table_data.append([str(journal_item_vendor_count) + ' vendors printed', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[60, 5, 180, 5, 30, 5, 80, 5, 65, 5, 65, 5, 65, 5, 65, 5, 70, 5, 70])
            if curr_list == '1':
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONTSIZE', (0, 0), (-1, -1), 7),
                     ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                     ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                     ('LINEABOVE', (8, 1), (8, 1), 0.25, colors.black),
                     ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
                     ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                     ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
                     ('LINEABOVE', (16, 1), (16, 1), 0.25, colors.black),
                     ('LINEABOVE', (-1, 1), (-1, 1), 0.25, colors.black),
                     ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD),
                     ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                     ]))
            else:
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONTSIZE', (0, 0), (-1, -1), 7),
                     ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
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
                     ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD),
                     ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                     ]))
            elements.append(item_table)

        # end process data

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75, 60, 85, 90, 130])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, age_from=age_from,
                                      cutoff_date=cutoff_date, cus_no=cus_no, date_type=date_type, doc_type=doc_type
                                      ),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, age_period=age_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


def get_exchange_rate(journal, company, age_from):
    exchange_rate = 1
    if journal.supplier.currency.id != company.currency.id:
        revaluation_rates = RevaluationDetails.objects.filter(is_hidden=False,
                                        document_no=journal.document_number,
                                        document_date=journal.document_date,
                                        supplier_id=journal.supplier_id
                                        ).exclude(posting__posting_sequence=0)
        if not revaluation_rates.exists():
            if journal.exchange_rate:
                exchange_rate = journal.exchange_rate
            else:
                exchange_rate_obj = ExchangeRate.objects.filter(is_hidden=False, company=company,
                                                                from_currency_id=journal.supplier.currency.id,
                                                                to_currency_id=company.currency.id,
                                                                exchange_date__lte=journal.document_date).order_by('-exchange_date', '-id').first()
                if exchange_rate_obj:
                    exchange_rate = exchange_rate_obj.rate
                else:
                    exchange_rate = 1.00
        else:
            # exchange_rate = revaluation_rates.last().rev_rate
            revaluation_rate = revaluation_rates.filter(
                posting__rate_date__month=journal.document_date.month,
                posting__rate_date__year=journal.document_date.year,
                posting__revaluation_date__gte=age_from)
            if revaluation_rate.exists():
                revaluation_rate = revaluation_rate.last()
                exchange_rate = revaluation_rate.rev_rate
            else:
                next_period = journal.document_date + relativedelta(months=1)
                revaluation_rate = revaluation_rates.filter(
                    posting__rate_date__month=next_period.month,
                    posting__rate_date__year=next_period.year,
                    posting__revaluation_date__gte=age_from)
                if revaluation_rate.exists():
                    revaluation_rate = revaluation_rate.last()
                    exchange_rate = revaluation_rate.rev_rate
                else:
                    revaluation_rate = revaluation_rates.filter(
                        posting__revaluation_date__gte=age_from)
                    if revaluation_rate.exists():
                        revaluation_rate = revaluation_rate.last()
                        exchange_rate = revaluation_rate.rev_rate
                    else:
                        if journal.exchange_rate:
                            exchange_rate = journal.exchange_rate

    return exchange_rate


def sum_currency(table_money, table_data, curr_list):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=7))
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
