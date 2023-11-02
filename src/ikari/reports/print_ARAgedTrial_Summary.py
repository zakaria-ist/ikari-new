from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.helpers.aged_trial_report import get_due_period, get_ar_transactions, calculate_total_amount
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from django.utils.dateparse import parse_date
from accounting.models import DOCUMENT_TYPES, RevaluationDetails
from currencies.models import Currency, ExchangeRate
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import TRANSACTION_TYPES
from utilities.common import round_number


class Print_ARAgedTrialSummary:
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
        row2_info1 = "A/R Aged Trial Balance by Due Date (ARTBALSY)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Account Type "
        row3_info2 = "[All customers]"
        header_data.append([row3_info1, row3_info2])
        # 4st row
        row4_info1 = "Age Transaction Of As "
        row4_info2 = "[" + parse_date(age_from).strftime('%d/%m/%Y') + "]"
        header_data.append([row4_info1, row4_info2])
        # # 5st row
        if int(date_type) == 2:
            row5_info1 = "CutOff by Posting Date "
        else:
            row5_info1 = "CutOff by Document Date "
        row5_info2 = "[" + parse_date(cutoff_date).strftime('%d/%m/%Y') + "]"

        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[280, 200, 200])
        header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                          ('FONTSIZE', (0, 0), (-1, -1), 7),
                                          ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                                          ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                                          ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                          ('ALIGN', (1, 0), (1, 1), 'CENTER'),
                                          ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
                                          ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
                                          ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 8)
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
        row2_info1 = "A/R Aged Trial Balance by Due Date (ARTBALSY)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=[280, 200, 200])
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
        table_header = ['', '', '', '', '', '', '', '', first_p, '', second_p, '', third_p, '', over_p, '', '']
        table_data.append(table_header)
        # 2ND ROW
        table_header = ['Customer No.', '', 'Customer Name.', '', 'Cur.', '', 'Current', '', 'Days', '', 'Days', '', 'Days', '', 'Days', '', 'Total']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[60, 5, 170, 5, 30, 5, 90, 5, 80, 5, 80, 5, 80, 5, 80, 5, 85])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), 7),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
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
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN,
                                topMargin=s.REPORT_TOP_MARGIN, bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='normal', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=7))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=7))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=7))

        # Our container for 'Flowable' objects
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
                doc_select += dict(DOCUMENT_TYPES)[str(code)] + ', '
                doc_type_array.append(code)
            doc_select = doc_select[:-2]

        if curr_list == '1':
            print_amount = 'Customer Currency'
        else:
            print_amount = 'Functional Currency'

        table_data.append(['Print Transactions in', '[Summary]', ''])
        table_data.append(['Transaction Type', '[' + doc_select + ']', ''])
        # table_data.append(['Show Full Paid Transaction ', is_full_paid, ''])
        table_data.append(['Show Age Retainage', '[No] ', ''])
        table_data.append(['Print Amounts In', print_amount, ''])

        item_table = Table(table_data, colWidths=[280, 330, 200])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
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
        table_data.append(['', '', '', '', '', '', '', '', first_p, '', second_p, '', third_p, '', over_p, '', ''])
        table_data.append(['Customer No.', '', 'Customer Name.', '', 'Cur.', '', 'Current', '', 'Days', '', 'Days', '', 'Days', '', 'Days', '', 'Total'])

        item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
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
                                        ('LINEBELOW', (-1, -1), (-1, -1), 0.25, colors.black),
                                        ]))
        elements.append(item_table)

        journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
        ar_collections = get_ar_transactions(is_detail_report=False, company_id=company_id, cus_no=cus_no, cutoff_date=cutoff_date, date_type=date_type,
                                             paid_full=paid_full, doc_type_array=doc_type_array)

        journal_item_list = ar_collections.journal_item_list
        adjustment_journal_list = ar_collections.adjustment_journal_list
        journal_amount_list = ar_collections.journal_amount_list
        journal_item_vendor_count = 0

        m_currency = ''
        symbol_curr = ''
        if int(curr_list) == 1:
            symbol_curr = ''
        else:
            company = Company.objects.get(pk=company_id)
            curr = Currency.objects.get(pk=company.currency_id)
            symbol_curr = curr.code
        m_customer_code = ''
        sum_amount = 0
        total_current = total_1st = total_2nd = total_3rd = total_4th = 0
        table_data = []
        table_money = []
        exchange_rate = 1
        if journal_item_list:
            for i, journal in enumerate(journal_item_list):
                if i == 0:
                    m_customer_code = journal.customer.code
                    m_currency = journal.customer.currency.code
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                        m_currency = journal.customer.currency.code

                if (m_customer_code != journal.customer.code) | (
                        (journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']) & (m_customer_code == journal.customer.code) & (m_currency != journal.customer.currency.code)) | (
                        (journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']) & (m_customer_code == journal.customer.code) & (m_currency != journal.currency.code)):
                    table_data = []
                    m_customer_code = journal.customer.code
                    m_currency = journal.customer.currency.code
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                        m_currency = journal.customer.currency.code
                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th

                    if int(curr_list) == 1:
                        is_decimal = journal_item_list[i - 1].customer.currency.is_decimal if journal_item_list[i - 1].customer.currency else True
                    else:
                        is_decimal = company.currency.is_decimal if company else True
                    decimal_point = "%.2f"
                    if not is_decimal:
                        decimal_point = "%.0f"
                    if round_number(sum_amount) != 0:
                        table_data.append([Paragraph(journal_item_list[i - 1].customer.code if journal_item_list[i - 1].customer_id else '', styles['normal']), '',
                                        Paragraph(journal_item_list[i - 1].customer.name if journal_item_list[i - 1].customer_id else '', styles['normal']),
                                        '', symbol_curr if symbol_curr else journal_item_list[i - 1].customer.currency.code,
                                        '', intcomma(decimal_point % round_number(total_current)),
                                        '', intcomma(decimal_point % round_number(total_1st)),
                                        '', intcomma(decimal_point % round_number(total_2nd)),
                                        '', intcomma(decimal_point % round_number(total_3rd)),
                                        '', intcomma(decimal_point % round_number(total_4th)),
                                        '', intcomma(decimal_point % round_number(sum_amount))])

                        item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                                                        ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                                                        ]))
                        elements.append(item_table)
                        table_money.append([symbol_curr if symbol_curr else journal_item_list[i - 1].customer.currency.code, total_current, total_1st, total_2nd, total_3rd, total_4th])
                        journal_item_vendor_count += 1
                        
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    sum_amount = 0
                    total_current = total_1st = total_2nd = total_3rd = total_4th = 0
                if m_customer_code == journal.customer.code:
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    # if str(journal.id) not in adjustment_journal_list.keys():
                    curr_code = ''
                    day_due = journal.due_date
                    day_age = datetime.datetime.strptime(age_from, '%Y-%m-%d').date()

                    # total_amount = calculate_total_amount(journal, journal_type, cutoff_date)
                    try:
                        key = str(journal.id)
                        total_amount = journal_amount_list[key]
                    except:
                        total_amount = journal.has_outstanding(cutoff_date)[1]

                    if int(curr_list) == 1:
                        curr_code = journal.customer.currency.code
                        is_decimal = journal.customer.currency.is_decimal if journal.customer.currency else True
                    else:
                        total_amount = round_number(total_amount * exchange_rate)
                        curr_code = symbol_curr
                        is_decimal = company.currency.is_decimal if company else True
                    # sum_amount += total_amount
                    
                    decimal_point = "%.2f"
                    if not is_decimal:
                        decimal_point = "%.0f"

                    if total_amount != 0:
                        if not day_due:
                            diff_day = (day_age - journal.document_date).days
                        else:
                            diff_day = (day_age - day_due).days
                        due_period = get_due_period(diff_day=diff_day, period_current=age_period['current'], period_1st=age_period['1st'],
                                                    period_2nd=age_period['2nd'], period_3rd=age_period['3rd'], total=total_amount)

                        total_current += due_period['total_current']
                        total_1st += due_period['total_1st']
                        total_2nd += due_period['total_2nd']
                        total_3rd += due_period['total_3rd']
                        total_4th += due_period['total_4th']
                        # check_currency(table_money, curr_code, total_amount, due_period['due_day_calculate'])

                if i == journal_item_list.__len__() - 1:
                    table_data = []
                    m_customer_code = journal.customer.code
                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                    if int(curr_list) == 1:
                        is_decimal = journal.customer.currency.is_decimal if journal.customer.currency else True
                    else:
                        is_decimal = company.currency.is_decimal if company else True
                    if round_number(sum_amount) != 0:
                        table_data.append([Paragraph(journal_item_list[i].customer.code if journal_item_list[i].customer_id else '', styles['normal']), '',
                                        Paragraph(journal_item_list[i].customer.name if journal_item_list[i].customer_id else '', styles['normal']),
                                        '', symbol_curr if symbol_curr else journal_item_list[i].customer.currency.code,
                                        '', intcomma(decimal_point % round_number(total_current)),
                                        '', intcomma(decimal_point % round_number(total_1st)),
                                        '', intcomma(decimal_point % round_number(total_2nd)),
                                        '', intcomma(decimal_point % round_number(total_3rd)),
                                        '', intcomma(decimal_point % round_number(total_4th)),
                                        '', intcomma(decimal_point % round_number(sum_amount))])

                        item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                                                        ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                                                        ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                                                        ]))
                        elements.append(item_table)
                        table_money.append([symbol_curr if symbol_curr else journal_item_list[i].customer.currency.code, total_current, total_1st, total_2nd, total_3rd, total_4th])
                        journal_item_vendor_count += 1

            table_data = []
            table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

            sum_currency(table_money, table_data, curr_list)

            table_data.append([str(journal_item_vendor_count) + ' customer printed', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

            item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])
            if curr_list == '1':
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('FONTSIZE', (0, 0), (-1, -1), 7),
                                                ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                                                ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                                                ('LINEABOVE', (8, 1), (8, 1), 0.25, colors.black),
                                                ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
                                                ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                                                ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
                                                ('LINEABOVE', (-1, 1), (-1, 1), 0.25, colors.black),
                                                ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD)
                                                ]))
            else:
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                ('FONTSIZE', (0, 0), (-1, -1), 7),
                                                ('TOPPADDING', (0, 0), (-1, -1), -0.2),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                                                ('LINEABOVE', (8, 1), (8, 1), 0.25, colors.black),
                                                ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
                                                ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                                                ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
                                                ('LINEABOVE', (16, 1), (16, 1), 0.25, colors.black),
                                                ('LINEABOVE', (6, 2), (6, 2), 0.25, colors.black),
                                                ('LINEABOVE', (8, 2), (8, 2), 0.25, colors.black),
                                                ('LINEABOVE', (10, 2), (10, 2), 0.25, colors.black),
                                                ('LINEABOVE', (12, 2), (12, 2), 0.25, colors.black),
                                                ('LINEABOVE', (14, 2), (14, 2), 0.25, colors.black),
                                                ('LINEABOVE', (16, 2), (16, 2), 0.25, colors.black),
                                                ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD)
                                                ]))
            elements.append(item_table)

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75, 60, 85, 90, 130])

            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                                            ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, age_from=age_from, cutoff_date=cutoff_date,
                                      cus_no=cus_no, date_type=date_type, doc_type=doc_type),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, age_period=age_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


def get_exchange_rate(journal, company, age_from):
    exchange_rate = 1
    if journal.customer.currency.id != company.currency.id:
        revaluation_rates = RevaluationDetails.objects.filter(is_hidden=False, 
                                        document_no=journal.document_number, 
                                        document_date=journal.document_date,
                                        customer_id=journal.customer_id
                                    ).exclude(posting__posting_sequence=0)
        if not revaluation_rates.exists():
            if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] and journal.orig_exch_rate:
                exchange_rate = journal.orig_exch_rate
            elif journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice'] and journal.exchange_rate:
                exchange_rate = journal.exchange_rate
            else:
                exchange_rate_obj = ExchangeRate.objects.filter(is_hidden=False, company=company, 
                                            from_currency_id=journal.customer.currency.id,
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
                        if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] and journal.orig_exch_rate:
                            exchange_rate = journal.orig_exch_rate
                        elif journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice'] and journal.exchange_rate:
                            exchange_rate = journal.exchange_rate

    return exchange_rate


# def check_currency(table_money, code, amount, day):
#     isExit = False
#     for h in table_money:
#         if (table_money[0][2] == code) & (table_money[0][0] == day):
#             table_money[0][1] += amount
#             isExit = True
#             break

#     if not isExit:
#         table_money.append([day, amount, code])


def sum_currency(table_money, table_data, curr_list):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=7))
    table_money = sorted(table_money, key=lambda code: code[0])
    nline = 0
    sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
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
                                   '', intcomma(decimal_point % round_number(sum_all))])
                if curr_list != '1':
                    table_data.append(['', '', '', '', '', '', intcomma(decimal_point % round_number(sum_current * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_1st * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_4th * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_all * 100 / sum_all)) + '%'])
            else:
                table_data.append(['', '', '', '', money, '', intcomma(decimal_point % round_number(sum_current)),
                                   '', intcomma(decimal_point % round_number(sum_1st)),
                                   '', intcomma(decimal_point % round_number(sum_2nd)),
                                   '', intcomma(decimal_point % round_number(sum_3rd)),
                                   '', intcomma(decimal_point % round_number(sum_4th)),
                                   '', intcomma(decimal_point % round_number(sum_all))])
            nline = 1

            money = table_money[k][0]
            sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
            sum_current += table_money[k][1]
            sum_1st += table_money[k][2]
            sum_2nd += table_money[k][3]
            sum_3rd += table_money[k][4]
            sum_4th += table_money[k][5]

        if k == len(table_money) - 1:
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
                                   '', intcomma(decimal_point % round_number(sum_all))])
                if curr_list != '1':
                    table_data.append(['', '', '', '', '', '', intcomma(decimal_point % round_number(sum_current * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_1st * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_4th * 100 / sum_all)) + '%',
                                       '', intcomma(decimal_point % round_number(sum_all * 100 / sum_all)) + '%'])
            else:
                table_data.append(['', '', '', '', money, '',
                                   intcomma(decimal_point % round_number(sum_current)),
                                   '', intcomma(decimal_point % round_number(sum_1st)),
                                   '', intcomma(decimal_point % round_number(sum_2nd)),
                                   '', intcomma(decimal_point % round_number(sum_3rd)),
                                   '', intcomma(decimal_point % round_number(sum_4th)),
                                   '', intcomma(decimal_point % round_number(sum_all))])
