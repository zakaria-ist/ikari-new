import datetime
import calendar
from dateutil.relativedelta import relativedelta
import os
from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from accounting.models import Journal
from inventory.models import TransactionCode
from companies.models import Company
from currencies.models import Currency, ExchangeRate
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, TRN_CODE_TYPE_DICT
from utilities.common import round_number, get_decimal_place

colWidths = [140, 3, 55, 3, 40, 3, 220, 3, 105, 3, 105, 3, 105, 0, 0, 0, 0, 0, 0, 0]
tax_colWidths = [140, 3, 75, 3, 55, 3, 170, 3, 100, 3, 30, 3, 100, 3, 100, 0, 0, 0, 0, 0, 0, 0]


class Print_Tax_Tracking:
    tax_rpt_code = None

    def __init__(self, buffer, pagesize, company_id):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

        # Get Tax_Report_Running_Number
        tx_rpt_rnum = TransactionCode.objects.filter(is_hidden=0, company_id=company_id,
                                                     code='TX', menu_type=TRN_CODE_TYPE_DICT['Global']).first()
        if not tx_rpt_rnum:
            tx_rpt_rnum = TransactionCode()
            tx_rpt_rnum.code = 'TX'
            tx_rpt_rnum.name = 'Running number for tax tracking report'
            tx_rpt_rnum.company_id = company_id
            tx_rpt_rnum.menu_type = TRN_CODE_TYPE_DICT['Global']
            tx_rpt_rnum.auto_generate = True
            tx_rpt_rnum.is_hidden = False
            tx_rpt_rnum.save()
        tax_running_number = tx_rpt_rnum.last_no + 10
        tx_rpt_rnum.last_no += 10
        tx_rpt_rnum.save()
        self.tax_rpt_code = tx_rpt_rnum.code + str(tax_running_number)

    @staticmethod
    def _header_footer(canvas, doc, company_id, issue_from, issue_to, print_type, report_by, print_by, transaction_type,
                       tx_rpt_code, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)

        # 1st row
        header_data = []
        row1_info1 = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        row1_info2 = company.name
        row1_info3 = ''
        header_data.append([row1_info1, row1_info2, row1_info3])

        # # 2nd row
        row2_info1 = print_by + " " + transaction_type + " Tracking (" + tx_rpt_code + ")"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_data.append([])
        # # 3rd row
        row3_info1 = "From Tax Authority"
        row3_info2 = "[" + tax_authority + "] to [" + tax_authority + "]"
        header_data.append([row3_info1, row3_info2])
        # # 5st row
        row4_info1 = "Print Amounts in"
        row4_info2 = "[" + print_type + "]"
        header_data.append([row4_info1, row4_info2])

        # # 6st row
        row5_info1 = "Report by"
        row5_info2 = "[" + report_by + "]"
        header_data.append([row5_info1, row5_info2])

        # # 6st row
        row6_info1 = "As of Fiscal Year"
        row6_info2 = "[" + str(issue_from.month) + '-' + str(issue_from.year) + \
                     "] TO [" + str(issue_to.month) + '-' + str(issue_to.year) + "]"
        header_data.append([row6_info1, row6_info2])
        header_table = Table(header_data, colWidths=[280, 250, 330])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'LEFT'),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONT', (2, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 3, doc.height + doc.topMargin - 70)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _header_last_footer(canvas, doc, company_id, issue_from, issue_to, print_type, report_by, print_by,
                            transaction_type, tx_rpt_code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # 2nd row
        row2_info1 = print_by + " " + transaction_type + " Tracking (" + tx_rpt_code + ")"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=[280, 330, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 4, doc.height + doc.topMargin - h - 15)

        table_data = []
        if print_by == 'Sales':
            if print_type == 'Tax Reporting':
                table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', '', '', 'Tax', '', 'Tax', '',
                                '', '', '', '', '', ''])

                table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Curr', '', 'Base', '',
                                'Amount', '', '', '', '', '', '', ''])

                item_header_table = Table(table_data, colWidths=tax_colWidths)

            else:
                table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', 'Tax', '', 'Tax', '', '', '',
                                '', '', '', ''])

                table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Base', '', 'Amount', '',
                                '', '', '', '', '', ''])

                item_header_table = Table(table_data, colWidths=colWidths)

        else:
            table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', 'Tax', '', 'Tax', '',
                            'Recoverable', '', 'Recoverable', '', 'Expense', ''])

            table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Base', '', 'Amount', '',
                            'Tax', '', 'Rate', '', 'Separately', ''])

            item_header_table = Table(table_data, colWidths=[60, 3, 55, 3, 35, 3, 100, 3, 80, 3, 80, 3, 80, 3, 80, 3, 55, 3, 45, 80])
        if print_by == 'Sales':
            if print_type == 'Tax Reporting':
                item_header_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                    ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                    ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                    ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                    ]))

            else:
                item_header_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                    ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                    ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                    ]))
        else:
            item_header_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
                ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
                ('LINEBELOW', (18, -1), (18, -1), 0.25, colors.black),
                ('ALIGN', (8, 0), (16, -1), 'RIGHT'),
                ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        if print_by == 'Sales':
            if print_type == 'Tax Reporting':
                item_header_table.drawOn(canvas, doc.leftMargin + 2, doc.height + doc.topMargin - h - h1 - 27)
            else:
                item_header_table.drawOn(canvas, doc.leftMargin + 5, doc.height + doc.topMargin - h - h1 - 30)
        else:
            item_header_table.drawOn(canvas, doc.leftMargin + 3, doc.height + doc.topMargin - h - h1 - 10)
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        if issue_from != '0' and issue_to != '0':
            array_from_year = str(issue_from).split('-')
            array_to_year = str(issue_to).split('-')
            issue_from = datetime.date(int(array_from_year[0]), int(array_from_year[1]), 1)
            issue_to = datetime.date(int(array_to_year[0]), int(array_to_year[1]),
                                     calendar.monthrange(int(array_to_year[0]), int(array_to_year[1]))[1])
        else:
            all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0, journal__is_hidden=0,
                                                          journal__batch__batch_type__in=(
                                                              dict(TRANSACTION_TYPES)['AP Invoice'],
                                                              dict(TRANSACTION_TYPES)['AP Payment'],
                                                              dict(TRANSACTION_TYPES)['AR Invoice'],
                                                              dict(TRANSACTION_TYPES)['AR Receipt']),
                                                          journal__transaction_type__in=('0', '', '2'),
                                                          journal__batch__status=int(STATUS_TYPE_DICT['Posted'])
                                                          ).order_by('journal__perd_year', 'journal__perd_month')\
                .select_related('journal', 'journal__batch')
            if not int(is_history):
                all_transactions = all_transactions.filter(is_clear_tax=False)

            from_year = all_transactions.first().journal.perd_year
            from_month = all_transactions.first().journal.perd_month
            to_year = all_transactions.last().journal.perd_year
            to_month = all_transactions.last().journal.perd_month

            issue_from = datetime.date(int(from_year), int(from_month), 1)
            issue_to = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])

        number_of_month = relativedelta(issue_to, issue_from)
        number_of_month = (number_of_month.years * 12) + number_of_month.months
        journal_ids = []
        for month in range(-1, number_of_month):
            current_date = issue_from + relativedelta(months=month + 1)
            curr_year = current_date.year
            current_month = current_date.month
            if print_by == 'Sales':
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id, perd_year=curr_year, perd_month=current_month,
                                                                          batch__batch_type__in=(
                                                                              dict(TRANSACTION_TYPES)['AR Invoice'],
                                                                              dict(TRANSACTION_TYPES)['AR Receipt']),
                                                                          transaction_type__in=('0', '', '2'), batch__status=int(STATUS_TYPE_DICT['Posted'])
                                                                          ).exclude(reverse_reconciliation=True)\
                                            .order_by('id').values_list('id', flat=True)
            else:
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id, perd_year=curr_year, perd_month=current_month,
                                                                          batch__batch_type__in=(
                                                                              dict(TRANSACTION_TYPES)['AP Invoice'],
                                                                              dict(TRANSACTION_TYPES)['AP Payment']),
                                                                          transaction_type__in=('0', '', '2'), batch__status=int(STATUS_TYPE_DICT['Posted'])
                                                                          ).exclude(reverse_reconciliation=True)\
                                            .order_by('id').values_list('id', flat=True)
            journal_ids = journal_ids + list(journals)

        if print_type == 'Functional Currency':
            print_type = 'Functional'
        elif print_type == 'Source Currency':
            print_type = 'Source'
        elif print_type == 'Tax Reporting Currency':
            print_type = 'Tax Reporting'
        else:
            print_type = ''
        if print_by == 'Sales':
            pdf = self.print_reportSales(company_id, journal_ids, issue_from, issue_to, print_type, report_by, transaction_type,
                                    is_history, tax_authority)
        return pdf


    def print_reportSales(self, company_id, journal_ids, issue_from, issue_to, print_type, report_by, transaction_type, is_history, tax_authority):
        if report_by == 'Fiscal Period':
            pdf = self.print_reportSalesFiscalPeriod(company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority)
        else:
            pdf = self.print_reportSalesDocumentDate(company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority)

        return pdf


    def print_reportSalesFiscalPeriod(self, company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer

        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))

        elements = []
        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            com_curr = ''
            str_tax_reporting = ''
            company = Company.objects.get(pk=company_id)
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            if print_type == 'Tax Reporting':
                com_curr = 'SGD'
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', 'Source', '', '', '', print_type, '', '', '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=tax_colWidths)

                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, 0), 10),
                                                ('LINEBELOW', (8, 0), (10, 0), 0.5, colors.black),
                                                ('LINEBELOW', (12, 0), (15, 0), 0.5, colors.black),
                                                ('SPAN', (8, 0), (10, 0)),
                                                ('SPAN', (12, 0), (15, 0)),
                                                ('ALIGN', (12, 0), (15, 0), 'CENTER'),
                                                ('ALIGN', (8, 0), (10, 0), 'CENTER'), ]))
                elements.append(item_table)

                table_data = []
                str_tax_reporting = "Tax Reporting Currency:"
                table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', '', '', 'Tax', '', 'Tax', '', '', '',
                                '', '', '', ''])

                table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Curr', '', 'Base', '', 'Amount',
                                '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=tax_colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                    ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                    ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                    ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                    ]))
                elements.append(item_table)
            else:
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', print_type, '', '', '', '', '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, 0), 10),
                                                ('LINEBELOW', (8, 0), (13, 0), 0.5, colors.black),
                                                ('SPAN', (8, 0), (13, 0)),
                                                ('ALIGN', (8, 0), (13, 0), 'CENTER'), ]))
                elements.append(item_table)
                table_data = []
                table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', 'Tax', '', 'Tax', '', '', '', '', '',
                                '', ''])

                table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Base', '', 'Amount', '', '', '',
                                '', '', '', ''])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                    ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                    ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                    ]))

                elements.append(item_table)

            table_data = []
            table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', str_tax_reporting, '', com_curr, ''])
            if print_type == 'Tax Reporting':
                item_table = Table(table_data, colWidths=[105, 265, 120, 3, 25, 275])
            else:
                item_table = Table(table_data, colWidths=[120, 295, 120, 3, 25, 225])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
                ]))
            elements.append(item_table)
            if print_type == 'Tax Reporting':
                all_journals = Journal.objects.select_related('customer').filter(id__in=journal_ids).order_by('customer_id')
            else:
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id')

            journal_doc_dates = all_journals.values('perd_month', 'perd_year').order_by('perd_year', 'perd_month').distinct()
            periods = []
            periods_count = 0
            last_period = None
            for doc_date in journal_doc_dates:
                period_str = str(doc_date.get('perd_year')) + '-' + str(doc_date.get('perd_month'))
                if period_str != last_period:
                    periods.append(period_str)
                    periods_count += 1
                    last_period = period_str

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id,
                                'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}

                    currencies.append(curr_obj)
                    last_currency = currency_id

            period_counter = 0
            summary_total_amount = summary_tax_base = summary_tax_amount = 0
            func_summary1 = func_summary2 = func_summary3 = 0
            for period in periods:
                period_counter += 1
                table_data = []
                table_data.append(['Year-Period', ': ' + period])
                if print_type == 'Tax Reporting':
                    item_table = Table(table_data, colWidths=[105, 688])
                else:
                    item_table = Table(table_data, colWidths=[120, 668])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ]))
                elements.append(item_table)

                year = period.split('-')[0]
                month = period.split('-')[1]
                func_subtotal1 = func_subtotal2 = func_subtotal3 = 0
                if print_type == 'Source' or print_type == 'Functional':
                    for currency in currencies:
                        subtotal1 = subtotal2 = subtotal3 = 0
                        currency_printed = False

                        if print_type == 'Source':
                            table_data = []
                            table_data.append(['Source Currency', ': ' + currency['code']])
                            item_table = Table(table_data, colWidths=[120, 668])
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                                ]))
                            elements.append(item_table)

                        journal_by_curr = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)
                        all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                    journal__in=journal_by_curr
                                                                    ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                            .select_related('journal', 'journal__customer', 'tax')\
                            .exclude(tax_id__isnull=True)

                        if not int(is_history):
                            all_transactions = all_transactions.filter(is_clear_tax=False)
                        last_journal_id = 0
                        index = 0
                        for trx in all_transactions:
                            currency_printed = True
                            if index == 0:
                                last_journal_id = trx.journal.id
                                decimal_place = get_decimal_place(trx.journal.currency)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AR-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AR-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AR-CR'
                                else:
                                    source_code = 'AR-PY'
                                try:
                                    column1 = trx.journal.customer.code
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                                if print_type == 'Functional':
                                    total_amount = trx.journal.total_amount * trx.exchange_rate
                                    tax_base = trx.base_tax_amount * trx.exchange_rate
                                    tax_amount = trx.tax_amount * trx.exchange_rate
                                else:
                                    total_amount = trx.journal.total_amount
                                    tax_base = trx.base_tax_amount
                                    tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # subtotal1 += round_number(total_amount)
                                # subtotal2 += round_number(tax_base)
                                # subtotal3 += round_number(tax_amount)
                                # func_subtotal1 += round_number(total_amount)
                                # func_subtotal2 += round_number(tax_base)
                                # func_subtotal3 += round_number(tax_amount)

                            if last_journal_id != trx.journal.id:
                                if print_type == 'Functional':
                                    decimal_place = decimal_place_f
                                table_data = []
                                table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), '',
                                                '', '', '', '', '', ''])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ]))
                                elements.append(item_table)

                                subtotal1 += round_number(total_amount)
                                subtotal2 += round_number(tax_base)
                                subtotal3 += round_number(tax_amount)
                                func_subtotal1 += round_number(total_amount)
                                func_subtotal2 += round_number(tax_base)
                                func_subtotal3 += round_number(tax_amount)

                                last_journal_id = trx.journal.id
                                decimal_place = get_decimal_place(trx.journal.currency)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AR-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AR-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AR-CR'
                                else:
                                    source_code = 'AR-PY'
                                try:
                                    column1 = trx.journal.customer.code
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                                if print_type == 'Functional':
                                    total_amount = trx.journal.total_amount * trx.exchange_rate
                                    tax_base = trx.base_tax_amount * trx.exchange_rate
                                    tax_amount = trx.tax_amount * trx.exchange_rate
                                else:
                                    total_amount = trx.journal.total_amount
                                    tax_base = trx.base_tax_amount
                                    tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # subtotal1 += round_number(total_amount)
                                # subtotal2 += round_number(tax_base)
                                # subtotal3 += round_number(tax_amount)
                                # func_subtotal1 += round_number(total_amount)
                                # func_subtotal2 += round_number(tax_base)
                                # func_subtotal3 += round_number(tax_amount)
                            elif index > 0:
                                last_journal_id = trx.journal.id
                                decimal_place = get_decimal_place(trx.journal.currency)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    if print_type == 'Functional':
                                        tax_base += trx.base_tax_amount * trx.exchange_rate * -1
                                        tax_amount += trx.tax_amount * trx.exchange_rate * -1
                                    else:
                                        tax_base += trx.base_tax_amount * -1
                                        tax_amount += trx.tax_amount * -1
                                else:
                                    if print_type == 'Functional':
                                        tax_base += trx.base_tax_amount * trx.exchange_rate
                                        tax_amount += trx.tax_amount * trx.exchange_rate
                                    else:
                                        tax_base += trx.base_tax_amount
                                        tax_amount += trx.tax_amount

                                # subtotal2 += round_number(trx.base_tax_amount)
                                # subtotal3 += round_number(trx.tax_amount)
                                # func_subtotal2 += round_number(trx.base_tax_amount)
                                # func_subtotal3 += round_number(trx.tax_amount)
                            index += 1

                        currency['summary1'] += subtotal1
                        currency['summary2'] += subtotal2
                        currency['summary3'] += subtotal3

                        if currency_printed:
                            if index != 0:
                                subtotal1 += round_number(total_amount)
                                subtotal2 += round_number(tax_base)
                                subtotal3 += round_number(tax_amount)
                                func_subtotal1 += round_number(total_amount)
                                func_subtotal2 += round_number(tax_base)
                                func_subtotal3 += round_number(tax_amount)
                                currency['summary1'] += round_number(total_amount)
                                currency['summary2'] += round_number(tax_base)
                                currency['summary3'] += round_number(tax_amount)

                                if print_type == 'Functional':
                                    decimal_place = decimal_place_f
                                table_data = []
                                table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), '',
                                                '', '', '', '', '', ''])

                                item_table = Table(table_data, colWidths=colWidths)

                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ]))
                                elements.append(item_table)
                            if print_type == 'Source':
                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period + ' Total ' + currency['code'] + ' :', styles['LeftAlignBold']),
                                                '', Paragraph(intcomma(decimal_place % round_number(subtotal1)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(subtotal2)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(subtotal3)), styles['RightAlignBold']), '',
                                                '', '', '', '', '', '', ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                    ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                                    ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                    ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                                    ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                                    ]))
                                elements.append(item_table)
                    if print_type == 'Functional':
                        table_data = []
                        table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period + ' Total :', styles['LeftAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(func_subtotal1)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(func_subtotal2)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(func_subtotal3)), styles['RightAlignBold']), '',
                                        '', '', '', '', '', '', ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                            ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                            ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                            ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                            ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                            ]))
                        elements.append(item_table)

                        func_summary1 += func_subtotal1
                        func_summary2 += func_subtotal2
                        func_summary3 += func_subtotal3
                else:
                    subtotal1 = subtotal2 = subtotal3 = 0
                    journal_by_period = all_journals.filter(perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_period
                                                                ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                        .select_related('journal', 'journal__customer', 'tax')\
                        .exclude(tax_id__isnull=True)

                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    for trx in all_transactions:
                        if index == 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            table_data = []
                            table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(str(currency_code), styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                               Paragraph(intcomma("%.2f" % round_number(
                                                   tax_amount)), styles['RightAlign']), '',
                                            '', '', '', '', '', ''])

                            item_table = Table(table_data, colWidths=tax_colWidths)

                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ]))
                            elements.append(item_table)

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)

                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            t_base = 0
                            t_amount = 0
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            elif com_curr != currency_code:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = (trx.tax_amount * trx.exchange_rate)
                            else:
                                t_base = trx.base_tax_amount
                                t_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                t_base = -1 * t_base
                                t_amount = -1 * t_amount

                            tax_base += t_base
                            tax_amount += t_amount
                            # subtotal2 += round_number(t_base)
                            # subtotal3 += round_number(t_amount)
                        index += 1

                    if index != 0:
                        table_data = []
                        table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                        Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                        Paragraph(str(currency_code), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), '',
                                        '', '', '', '', '', ''])

                        item_table = Table(table_data, colWidths=tax_colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ]))
                        elements.append(item_table)

                        subtotal1 += round_number(total_amount)
                        subtotal2 += round_number(tax_base)
                        subtotal3 += round_number(tax_amount)

                    table_data = []
                    table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period + ' Total :', styles['LeftAlignBold']),
                                    '', '', '', '', '', Paragraph(intcomma("%.2f" % round_number(subtotal2)), styles['RightAlignBold']), '',
                                       Paragraph(intcomma("%.2f" % round_number(subtotal3)), styles['RightAlignBold']), '', '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=tax_colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                        ('LINEABOVE', (14, -1), (14, -1), 0.25, colors.black),
                        ]))
                    elements.append(item_table)
                    summary_total_amount += subtotal1
                    summary_tax_base += subtotal2
                    summary_tax_amount += subtotal3

            if print_type == 'Functional':
                table_data = []
                table_data.append(['', '', '', '', '', '', Paragraph(company.currency.code + ' Total ' + ' :', styles['LeftAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(func_summary1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(func_summary2)), styles['RightAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(func_summary3)), styles['RightAlignBold']), '', '', '', '', '', '', '', ])

                item_table = Table(table_data, colWidths=colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                    ]))
                elements.append(item_table)
            elements.append(PageBreak())
            if period_counter == periods_count:
                table_data = []
                table_data.append(['', Paragraph('Summary By Tax Authority', styles['LeftAlignBold']), ''])
                item_table = Table(table_data, colWidths=[160, 140, 495])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 20),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ]))
                elements.append(item_table)

                table_data = []
                curr_code = Source = ''
                footer1 = 'Invoice'
                footer2 = 'Amounts'
                line_2 = (0, 1)

                if print_type == 'Source':
                    curr_code = 'Currency'
                    Source = 'Source'
                elif print_type == 'Tax Reporting':
                    footer1 = print_type
                    footer2 = 'Currency'
                else:
                    line_2 = (8, 3)

                table_data.append(['', '', Paragraph(Source, styles['LeftAlignBold']), '', Paragraph(footer1, styles['RightAlignBold']), '',
                                Paragraph('Tax', styles['RightAlignBold']), '', Paragraph('Tax', styles['RightAlignBold']), '', '', ''])

                table_data.append([Paragraph('Tax Authority', styles['LeftAlignBold']), '', Paragraph(curr_code, styles['LeftAlignBold']), '',
                                Paragraph(footer2, styles['RightAlignBold']), '', Paragraph('Base', styles['RightAlignBold']), '',
                                Paragraph('Amounts', styles['RightAlignBold']), '', '', ''])

                total_tax_base = total_tax_amu = tot_inv = 0
                if print_type == 'Source':
                    for curr in currencies:
                        curr_code = curr['code']
                        try:
                            cur = Currency.objects.get(code=curr['code'])
                            decimal_place = get_decimal_place(cur)
                        except:
                            decimal_place = "%.2f"
                        table_data.append([Paragraph('GSTDOS GSTDOS', styles['LeftAlign']), '', Paragraph(curr_code, styles['LeftAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(curr['summary1'])), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(curr['summary2'])), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(curr['summary3'])), styles['RightAlign']), '', '', ''])

                elif print_type == 'Tax Reporting':
                    table_data.append([Paragraph('GSTDOS GSTDOS', styles['LeftAlign']), '', '', '',
                                    Paragraph(str('SGD'), styles['RightAlign']), '',
                                    Paragraph(intcomma("%.2f" % round_number(summary_tax_base)), styles['RightAlign']), '',
                                    Paragraph(intcomma("%.2f" % round_number(summary_tax_amount)), styles['RightAlign']), '', '', ''])
                else:
                    for curr in currencies:
                        tot_inv += curr['summary1']
                        total_tax_base += curr['summary2']
                        total_tax_amu += curr['summary3']

                    table_data.append([Paragraph('GSTDOS GSTDOS', styles['LeftAlign']), '', Paragraph(curr_code, styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tot_inv)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total_tax_base)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total_tax_amu)), styles['RightAlign']), '', '', ''])

                    table_data.append(['', '', '', '', '', '', '', '', '', '', '', ''])

                    table_data.append(['', '', '', '', '', 'Report Total :', '', '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total_tax_amu)), styles['RightAlign']), '', '', ''])

                table_data.append([Paragraph('1 authority printed', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=[125, 3, 100, 3, 80, 3, 80, 3, 80, 3, 80, 195])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, 1), (0, 1), 0.25, colors.black),
                    ('LINEBELOW', (2, 1), (2, 1), 0.25, colors.black),
                    ('LINEBELOW', (4, 1), (4, 1), 0.25, colors.black),
                    ('LINEBELOW', (6, 1), (6, 1), 0.25, colors.black),
                    ('LINEBELOW', (8, 1), (8, 1), 0.25, colors.black),
                    ('LINEBELOW', line_2, line_2, 0.25, colors.black),
                    ]))

                elements.append(item_table)

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['']]
            table_body = Table(table_data, colWidths=[795])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                ]))
            elements.append(table_body)

        doc.build(elements,
                onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Fiscal Period", print_by="Sales",
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code, tax_authority=tax_authority),
                onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Fiscal Period",
                                    print_by="Sales",
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code),
                canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


    def print_reportSalesDocumentDate(self, company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer

        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))

        elements = []
        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            com_curr = ''
            str_tax_reporting = ''
            company = Company.objects.get(pk=company_id)
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            if print_type == 'Tax Reporting':
                com_curr = 'SGD'
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', 'Source', '', '', '', print_type, '', '', '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=tax_colWidths)

                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, 0), 10),
                                                ('LINEBELOW', (8, 0), (10, 0), 0.5, colors.black),
                                                ('LINEBELOW', (12, 0), (15, 0), 0.5, colors.black),
                                                ('SPAN', (8, 0), (10, 0)),
                                                ('SPAN', (12, 0), (15, 0)),
                                                ('ALIGN', (12, 0), (15, 0), 'CENTER'),
                                                ('ALIGN', (8, 0), (10, 0), 'CENTER'), ]))

                elements.append(item_table)

                table_data = []
                str_tax_reporting = "Tax Reporting Currency:"
                table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', '', '', 'Tax', '', 'Tax', '', '', '',
                                '', '', '', ''])

                table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Curr', '', 'Base', '', 'Amount',
                                '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=tax_colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                    ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                    ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                    ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                    ]))
                elements.append(item_table)
            else:
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', print_type, '', '', '', '', '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, 0), 10),
                                                ('LINEBELOW', (8, 0), (13, 0), 0.5, colors.black),
                                                ('SPAN', (8, 0), (13, 0)),
                                                ('ALIGN', (8, 0), (13, 0), 'CENTER'),
                                                ]))

                elements.append(item_table)
                table_data = []
                table_data.append(['', '', 'Document', '', 'Source', '', 'Document', '', 'Invoice', '', 'Tax', '', 'Tax', '', '', '', '', '',
                                '', ''])

                table_data.append(['Customer No.', '', 'Date', '', 'Code', '', 'Number', '', 'Amount', '', 'Base', '', 'Amount', '', '', '',
                                '', '', '', ''])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                    ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                    ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                    ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                    ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                    ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                    ]))

                elements.append(item_table)

            table_data = []
            table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', str_tax_reporting, '', com_curr, ''])
            if print_type == 'Tax Reporting':
                item_table = Table(table_data, colWidths=[105, 265, 120, 3, 25, 275])
            else:
                item_table = Table(table_data, colWidths=[120, 295, 120, 3, 25, 225])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
                ]))
            elements.append(item_table)
            if print_type == 'Source' or print_type == 'Functional':
                all_journals = Journal.objects.select_related('currency', 'customer').filter(id__in=journal_ids).order_by('currency_id', 'customer_id')
            else:
                all_journals = Journal.objects.select_related('customer').filter(id__in=journal_ids).order_by('document_date')

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            func_summary1 = func_summary2 = func_summary3 = 0
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id,
                                'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id

            summary_total_amount = summary_tax_base = summary_tax_amount = 0
            if print_type == 'Source' or print_type == 'Functional':
                func_subtotal1 = func_subtotal2 = func_subtotal3 = 0
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = 0
                    custotal1 = custotal2 = custotal3 = 0
                    currency_printed = False
                    if print_type == 'Source':
                        table_data = []
                        table_data.append(['Source Currency', ': ' + currency['code']])
                        item_table = Table(table_data, colWidths=[120, 668])
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                            ]))
                        elements.append(item_table)

                    journals = all_journals.filter(currency_id=currency['id']).order_by('document_date')
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journals
                                                                ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                        .select_related('journal', 'journal__customer', 'tax')\
                        .exclude(tax_id__isnull=True)

                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    customer_code = ''
                    for trx in all_transactions:
                        if last_journal_id == 0:
                            try:
                                customer_code = trx.journal.customer.code
                            except:
                                customer_code = ''
                        currency_printed = True
                        if index == 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')
                            if print_type == 'Source':
                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                            else:
                                total_amount = trx.journal.total_amount * trx.exchange_rate
                                tax_base = trx.base_tax_amount * trx.exchange_rate
                                tax_amount = trx.tax_amount * trx.exchange_rate

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # custotal1 += round_number(total_amount)
                            # custotal2 += round_number(tax_base)
                            # custotal3 += round_number(tax_amount)
                            # func_subtotal1 += round_number(total_amount)
                            # func_subtotal2 += round_number(tax_base)
                            # func_subtotal3 += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            if print_type == 'Functional':
                                decimal_place = decimal_place_f
                            table_data = []
                            table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), '',
                                            '', '', '', '', '', ''])

                            item_table = Table(table_data, colWidths=colWidths)

                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ]))
                            elements.append(item_table)

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            func_subtotal1 += round_number(total_amount)
                            func_subtotal2 += round_number(tax_base)
                            func_subtotal3 += round_number(tax_amount)
                            if trx.journal.customer and customer_code == trx.journal.customer.code:
                                custotal1 += round_number(total_amount)
                                custotal2 += round_number(tax_base)
                                custotal3 += round_number(tax_amount)
                            elif customer_code == '':
                                custotal1 += round_number(total_amount)
                                custotal2 += round_number(tax_base)
                                custotal3 += round_number(tax_amount)
                            if trx.journal.customer and customer_code != trx.journal.customer.code:
                                if customer_code != '':
                                    custotal1 += round_number(total_amount)
                                    custotal2 += round_number(tax_base)
                                    custotal3 += round_number(tax_amount)
                                if print_type == 'Functional':
                                    decimal_place = decimal_place_f
                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph('Customer TAX Auth. Total ' + currency['code'] + ':', styles['LeftAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(custotal1)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(custotal2)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(custotal3)), styles['RightAlignBold']), '', '', '', '', '', '', ''])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                    ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                                    ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                    ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                                    ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                                    ]))
                                elements.append(item_table)

                                try:
                                    customer_code = trx.journal.customer.code
                                except:
                                    customer_code = ''

                                custotal1 = 0
                                custotal2 = 0
                                custotal3 = 0

                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            if print_type == 'Source':
                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                            else:
                                total_amount = trx.journal.total_amount * trx.exchange_rate
                                tax_base = trx.base_tax_amount * trx.exchange_rate
                                tax_amount = trx.tax_amount * trx.exchange_rate

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # func_subtotal1 += round_number(total_amount)
                            # func_subtotal2 += round_number(tax_base)
                            # func_subtotal3 += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                if print_type == 'Source':
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                else:
                                    tax_base += trx.base_tax_amount * trx.exchange_rate * -1
                                    tax_amount += trx.tax_amount * trx.exchange_rate * -1
                            else:
                                if print_type == 'Source':
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                else:
                                    tax_base += trx.base_tax_amount * trx.exchange_rate
                                    tax_amount += trx.tax_amount * trx.exchange_rate

                            # subtotal2 += round_number(trx.base_tax_amount)
                            # subtotal3 += round_number(trx.tax_amount)
                            # func_subtotal2 += round_number(trx.base_tax_amount)
                            # func_subtotal3 += round_number(trx.tax_amount)
                        index += 1

                    currency['summary1'] += subtotal1
                    currency['summary2'] += subtotal2
                    currency['summary3'] += subtotal3

                    if currency_printed:
                        if index != 0:
                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            func_subtotal1 += round_number(total_amount)
                            func_subtotal2 += round_number(tax_base)
                            func_subtotal3 += round_number(tax_amount)
                            custotal1 += round_number(total_amount)
                            custotal2 += round_number(tax_base)
                            custotal3 += round_number(tax_amount)
                            currency['summary1'] += round_number(total_amount)
                            currency['summary2'] += round_number(tax_base)
                            currency['summary3'] += round_number(tax_amount)

                            if print_type == 'Functional':
                                decimal_place = decimal_place_f
                            table_data = []
                            table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), '',
                                            '', '', '', '', '', ''])

                            item_table = Table(table_data, colWidths=colWidths)

                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ]))
                            elements.append(item_table)
                            table_data = []
                            table_data.append(['', '', '', '', '', '', Paragraph('Customer TAX Auth. Total ' + currency['code'] + ':', styles['LeftAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(custotal1)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(custotal2)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(custotal3)), styles['RightAlignBold']), '', '', '', '', '', '', ''])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                                ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                                ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                                ]))
                            elements.append(item_table)
                        if print_type == 'Source':
                            table_data = []
                            table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS Total ' + currency['code'] + ' :', styles['LeftAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal1)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal2)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal3)), styles['RightAlignBold']), '', '', '', '', '', '', ''])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                                ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                                ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                                ]))
                            elements.append(item_table)
                if print_type == 'Functional':

                    table_data = []
                    table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS Total :', styles['LeftAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(func_subtotal1)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(func_subtotal2)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(func_subtotal3)), styles['RightAlignBold']), '', '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('LINEABOVE', (6, -1), (6, -1), 0.25, colors.black),
                        ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                        ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                        ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                        ]))
                    elements.append(item_table)
                    func_summary1 += func_subtotal1
                    func_summary2 += func_subtotal2
                    func_summary3 += func_subtotal3
            else:
                subtotal1 = subtotal2 = subtotal3 = 0
                custotal1 = custotal2 = custotal3 = 0
                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                            journal__in=all_journals
                                                            ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                    .select_related('journal', 'journal__customer', 'tax')\
                    .exclude(tax_id__isnull=True)

                if not int(is_history):
                    all_transactions = all_transactions.filter(is_clear_tax=False)
                last_journal_id = 0
                index = 0
                customer_code = ''
                for trx in all_transactions:
                    if last_journal_id == 0:
                        try:
                            customer_code = trx.journal.customer.code
                        except:
                            customer_code = ''
                    if index == 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AR-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AR-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AR-CR'
                        else:
                            source_code = 'AR-PY'
                        try:
                            column1 = trx.journal.customer.code
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount

                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        else:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)

                        # subtotal1 += round_number(total_amount)
                        # subtotal2 += round_number(tax_base)
                        # subtotal3 += round_number(tax_amount)
                        # custotal1 += round_number(total_amount)
                        # custotal2 += round_number(tax_base)
                        # custotal3 += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        table_data = []
                        table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                        Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                        Paragraph(str(currency_code), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), '',
                                        '', '', '', '', '', ''])

                        item_table = Table(table_data, colWidths=tax_colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ]))
                        elements.append(item_table)

                        subtotal1 += round_number(total_amount)
                        subtotal2 += round_number(tax_base)
                        subtotal3 += round_number(tax_amount)
                        if trx.journal.customer and customer_code == trx.journal.customer.code:
                            custotal1 += round_number(total_amount)
                            custotal2 += round_number(tax_base)
                            custotal3 += round_number(tax_amount)
                        elif customer_code == '':
                            custotal1 += round_number(total_amount)
                            custotal2 += round_number(tax_base)
                            custotal3 += round_number(tax_amount)
                        if trx.journal.customer and customer_code != trx.journal.customer.code:
                            if customer_code != '':
                                custotal1 += round_number(total_amount)
                                custotal2 += round_number(tax_base)
                                custotal3 += round_number(tax_amount)
                            if trx.journal.customer and customer_code != trx.journal.customer.code:
                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph('Customer TAX Auth. Total :', styles['LeftAlignBold']),
                                                '', '', '', '', '', Paragraph(intcomma("%.2f" % round_number(custotal2)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma("%.2f" % round_number(custotal3)), styles['RightAlignBold']), '',
                                                '', '', '', '', '', ''])

                                item_table = Table(table_data, colWidths=tax_colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                                    ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                                    ('LINEABOVE', (14, -1), (14, -1), 0.25, colors.black),
                                    ]))
                                elements.append(item_table)

                                try:
                                    customer_code = trx.journal.customer.code
                                except:
                                    customer_code = ''

                                custotal1 = 0
                                custotal2 = 0
                                custotal3 = 0

                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AR-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AR-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AR-CR'
                        else:
                            source_code = 'AR-PY'
                        try:
                            column1 = trx.journal.customer.code
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount

                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        else:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)

                        # subtotal1 += round_number(total_amount)
                        # subtotal2 += round_number(tax_base)
                        # subtotal3 += round_number(tax_amount)

                    elif index > 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        t_base = 0
                        t_amount = 0
                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            t_base = (trx.base_tax_amount * exchange_rate)
                            t_amount = (trx.tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            t_base = (trx.base_tax_amount * exchange_rate)
                            t_amount = (trx.tax_amount * exchange_rate)
                        elif com_curr != currency_code:
                            t_base = (trx.base_tax_amount * trx.exchange_rate)
                            t_amount = (trx.tax_amount * trx.exchange_rate)
                        else:
                            t_base = trx.base_tax_amount
                            t_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            t_base = -1 * t_base
                            t_amount = -1 * t_amount

                        tax_base += t_base
                        tax_amount += t_amount
                        # subtotal2 += round_number(t_base)
                        # subtotal3 += round_number(t_amount)
                    index += 1

                if index != 0:
                    table_data = []
                    table_data.append([Paragraph(column1, styles['LeftAlign']), '', Paragraph(column2, styles['LeftAlign']), '',
                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(column4, styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                    Paragraph(str(currency_code), styles['RightAlign']), '',
                                    Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                    Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), '',
                                    '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=tax_colWidths)
                    table_data = []
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ]))
                    elements.append(item_table)

                    subtotal1 += round_number(total_amount)
                    subtotal2 += round_number(tax_base)
                    subtotal3 += round_number(tax_amount)
                    custotal1 += round_number(total_amount)
                    custotal2 += round_number(tax_base)
                    custotal3 += round_number(tax_amount)

                    table_data = []
                    table_data.append(['', '', '', '', '', '', Paragraph('Customer TAX Auth. Total :', styles['LeftAlignBold']),
                                    '', '', '', '', '', Paragraph(intcomma("%.2f" % round_number(custotal2)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma("%.2f" % round_number(custotal3)), styles['RightAlignBold']), '',
                                    '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=tax_colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                        ('LINEABOVE', (14, -1), (14, -1), 0.25, colors.black),
                        ]))
                    elements.append(item_table)

                table_data = []
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS Total :', styles['LeftAlignBold']),
                                '', '', '', '', '', Paragraph(intcomma("%.2f" % round_number(subtotal2)), styles['RightAlignBold']), '',
                                Paragraph(intcomma("%.2f" % round_number(subtotal3)), styles['RightAlignBold']), '',
                                '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=tax_colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('LINEABOVE', (12, -1), (12, -1), 0.25, colors.black),
                    ('LINEABOVE', (14, -1), (14, -1), 0.25, colors.black),
                    ]))
                elements.append(item_table)
                summary_total_amount += subtotal1
                summary_tax_base += subtotal2
                summary_tax_amount += subtotal3

            elements.append(PageBreak())
            table_data = []
            table_data.append(['', Paragraph('Summary By Tax Authority', styles['LeftAlignBold']), ''])
            item_table = Table(table_data, colWidths=[160, 140, 495])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
            elements.append(item_table)

            table_data = []
            curr_code = Source = ''
            footer1 = 'Invoice'
            footer2 = 'Amounts'
            line_2 = (0, 1)

            if print_type == 'Source':
                curr_code = 'Currency'
                Source = 'Source'
            elif print_type == 'Tax Reporting':
                footer1 = print_type
                footer2 = 'Currency'
            else:
                line_2 = (8, 3)

            table_data.append(['', '', Paragraph(Source, styles['LeftAlignBold']), '', Paragraph(footer1, styles['RightAlignBold']), '',
                            Paragraph('Tax', styles['RightAlignBold']), '', Paragraph('Tax', styles['RightAlignBold']), '', '', ''])

            table_data.append([Paragraph('Tax Authority', styles['LeftAlignBold']), '', Paragraph(curr_code, styles['LeftAlignBold']), '',
                            Paragraph(footer2, styles['RightAlignBold']), '', Paragraph('Base', styles['RightAlignBold']), '',
                            Paragraph('Amounts', styles['RightAlignBold']), '', '', ''])

            total_tax_base = total_tax_amu = tot_inv = 0
            if print_type == 'Source':
                for curr in currencies:
                    curr_code = curr['code']
                    try:
                        cur = Currency.objects.get(code=curr['code'])
                        decimal_place = get_decimal_place(cur)
                    except:
                        decimal_place = "%.2f"
                    table_data.append([Paragraph('GSTDOS GSTDOS', styles['LeftAlign']), '', Paragraph(curr_code, styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(curr['summary1'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(curr['summary2'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(curr['summary3'])), styles['RightAlign']), '', '', ''])

            elif print_type == 'Tax Reporting':
                table_data.append([Paragraph('GSTDOS GSTDOS', styles['LeftAlign']), '', '', '',
                                Paragraph(str('SGD'), styles['RightAlign']), '',
                                Paragraph(intcomma("%.2f" % round_number(summary_tax_base)), styles['RightAlign']), '',
                                Paragraph(intcomma("%.2f" % round_number(summary_tax_amount)), styles['RightAlign']), '', '', ''])
            else:
                for curr in currencies:
                    tot_inv += curr['summary1']
                    total_tax_base += curr['summary2']
                    total_tax_amu += curr['summary3']

                table_data.append([Paragraph('GSTDOS GSTDOS', styles['LeftAlign']), '', Paragraph(curr_code, styles['LeftAlign']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(tot_inv)), styles['RightAlign']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(total_tax_base)), styles['RightAlign']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(total_tax_amu)), styles['RightAlign']), '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', 'Report Total :', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(total_tax_amu)), styles['RightAlign']), '', '', ''])

            table_data.append([Paragraph('1 authority printed', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[155, 3, 100, 3, 80, 3, 80, 3, 80, 3, 80, 195])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 1), (0, 1), 0.25, colors.black),
                ('LINEBELOW', (2, 1), (2, 1), 0.25, colors.black),
                ('LINEBELOW', (4, 1), (4, 1), 0.25, colors.black),
                ('LINEBELOW', (6, 1), (6, 1), 0.25, colors.black),
                ('LINEBELOW', (8, 1), (8, 1), 0.25, colors.black),
                ('LINEBELOW', line_2, line_2, 0.25, colors.black),
                ]))

            elements.append(item_table)

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['']]
            table_body = Table(table_data, colWidths=[795])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                ]))
            elements.append(table_body)

        doc.build(elements,
                onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Document Date", print_by="Sales",
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code, tax_authority=tax_authority),
                onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Document Date",
                                    print_by="Sales",
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code),
                canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
