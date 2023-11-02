import datetime
import calendar
from dateutil.relativedelta import relativedelta
import os
from functools import partial
from operator import itemgetter
from django.conf import settings as s
from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
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
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, TRN_CODE_TYPE_DICT, TAX_TRACK_CLASS_DICT
from utilities.common import round_number, get_decimal_place

src_col_width = [90, 3, 130, 3, 50, 3, 130, 3, 35, 3, 60, 3, 25, 3, 25, 3, 75, 3, 75, 3, 75]
fun_col_width = [65, 3, 125, 3, 50, 3, 82, 3, 35, 3, 56, 3, 25, 3, 25, 3, 70, 3, 20, 3, 70, 3, 70, 3, 70]
tax_col_width = [70, 3, 145, 3, 50, 3, 100, 3, 35, 3, 56, 3, 25, 3, 25, 3, 80, 3, 20, 3, 80, 3, 80]


class Print_Tracking_item:
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
        row1_info2 = ""
        row1_info3 = company.name
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

        header_table = Table(header_data, colWidths=[100, 250, 330])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'LEFT'),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONT', (2, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - 70)
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
             ('FONT', (1, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 15)

        table_data = []
        if print_by == 'Sales':
            if print_type == 'Source Currency':
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Source', '', 'Exchange', '', 'Tax', '', 'Tax', '', '', '', '', '', ''])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Rate', '', 'Class', '',
                                   'Rate', '', 'Sales', '', 'Tax Base', '', 'Tax Amount'])
                item_header_table = Table(table_data, colWidths=src_col_width)
            elif print_type == 'Functional Currency':
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                   '----------Source---------', '', '--------------Functional------------', '', '', '', ''])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                   'Rate', '', 'Sales', '', 'Curr', '', 'Sales', '', 'Tax Base', '', 'Tax Amount'])
                item_header_table = Table(table_data, colWidths=fun_col_width)
            else:
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                   '------------Source-----------', '', '', '', '-----------------Tax Reporting-----------------'])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                   'Rate', '', 'Sales', '', 'Curr', '', 'Tax Base', '', 'Tax Amount'])
                item_header_table = Table(table_data, colWidths=tax_col_width)
        else:
            if print_type == 'Source Currency':
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Source', '', 'Exchange', '', 'Tax', '', 'Tax', '', '', '', '', '', ''])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Rate', '', 'Class', '',
                                   'Rate', '', 'Purchases', '', 'Tax Base', '', 'Tax Amount'])
                item_header_table = Table(table_data, colWidths=src_col_width)
            elif print_type == 'Functional Currency':
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                   '----------Source-----------', '', '----------------Functional----------------', '', '', '', ''])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                   'Rate', '', 'Purchase', '', 'Curr', '', 'Purchase', '', 'Tax Base', '', 'Tax Amount'])
                item_header_table = Table(table_data, colWidths=fun_col_width)
            else:
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                   '-------------Source-----------', '', '', '', '------------------Tax Reporting----------------'])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                   'Rate', '', 'Purchases', '', 'Curr', '', 'Tax Base', '', 'Tax Amount'])
                item_header_table = Table(table_data, colWidths=tax_col_width)

        if print_type == 'Source Currency':
            item_header_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                 ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                 ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
        elif print_type == 'Functional Currency':
            item_header_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                 ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                 ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                 ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
                 ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (24, 0), (-1, -1), 'RIGHT'),
                 ('SPAN', (20, 0), (24, 0),),
                 ('ALIGN', (20, 0), (24, 0), 'CENTER'),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
        else:
            item_header_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                 ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                 ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                 ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1 - 30)
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, print_type, report_by, print_by, transaction_type,
                     is_history, tax_authority):

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
                                                          ).order_by('journal__perd_year', 'journal__perd_month')
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
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id, perd_year=curr_year,
                                                  perd_month=current_month, batch__batch_type__in=(
                                                      dict(TRANSACTION_TYPES)['AR Invoice'],
                                                      dict(TRANSACTION_TYPES)['AR Receipt']),
                                                  transaction_type__in=('0', '', '2'),
                                                  batch__status=int(STATUS_TYPE_DICT['Posted']))\
                                        .exclude(reverse_reconciliation=True)\
                                        .order_by('id').values_list('id', flat=True)
            else:
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id, perd_year=curr_year,
                                                  perd_month=current_month, batch__batch_type__in=(
                                                      dict(TRANSACTION_TYPES)['AP Invoice'],
                                                      dict(TRANSACTION_TYPES)['AP Payment']),
                                                  transaction_type__in=('0', '', '2'),
                                                  batch__status=int(STATUS_TYPE_DICT['Posted']))\
                                        .exclude(reverse_reconciliation=True)\
                                        .order_by('id').values_list('id', flat=True)
            journal_ids = journal_ids + list(journals)

        if print_by == 'Sales':
            pdf = self.print_reportSales(company_id, journal_ids, issue_from, issue_to, print_type, report_by, transaction_type,
                                    is_history, tax_authority)
        else:  # print_by=='Purchase':
            pdf = self.print_reportPurchase(company_id, journal_ids, issue_from, issue_to, print_type, report_by, transaction_type,
                                       is_history, tax_authority)

        return pdf


    def print_reportSales(self, company_id, journal_ids, issue_from, issue_to, print_type, report_by, transaction_type, is_history, tax_authority):
        if report_by == 'Fiscal Period':
            pdf = self.print_reportSalesFiscalPeriod(company_id, journal_ids, issue_from, issue_to, print_type, transaction_type,
                                                is_history, tax_authority)
        else:
            pdf = self.print_reportSalesDocumentDate(company_id, journal_ids, issue_from, issue_to, print_type, transaction_type,
                                                is_history, tax_authority)

        return pdf


    def print_reportSalesFiscalPeriod(self, company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=115, bottomMargin=42,
                                pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        elements = []
        table_data = []
        table_data.append(['', '', '', '', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=[60, 3, 55, 3, 35, 3, 100, 3, 250, 275])

        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('TOPPADDING', (0, 0), (-1, 0), 10),
                                        ('LINEBELOW', (8, 0), (8, 0), 0.5, colors.transparent),
                                        ('ALIGN', (8, 0), (8, 0), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)
        table_data = []
        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            company = Company.objects.get(pk=company_id)
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            str_tax_reporting = com_curr = ''

            if print_type == 'Source Currency':
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Source', '', 'Exchange', '', 'Tax', '', 'Tax', '', '', '', '', '', ''])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Rate', '', 'Class', '',
                                'Rate', '', 'Sales', '', 'Tax Base', '', 'Tax Amount'])

                item_table = Table(table_data, colWidths=src_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            elif print_type == 'Functional Currency':
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '-----------Source---------', '', '---------------Functional----------------', '', '',  '', ''])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Sales', '', 'Curr', '', 'Sales', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = company.currency.code
                str_tax_reporting = "Functional Currency"

                item_table = Table(table_data, colWidths=fun_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (24, 0), (-1, -1), 'RIGHT'),
                    ('SPAN', (20, 0), (24, 0)),
                    ('ALIGN', (20, 0), (24, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            else:
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '------------Source-----------', '', '', '', '-----------------Tax Reporting-----------------'])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Sales', '', 'Curr', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"

                item_table = Table(table_data, colWidths=tax_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))

            elements.append(item_table)
            table_data = []

            if print_type == 'Source Currency' or print_type == 'Functional Currency':
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', '', '', ''])
            else:
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', str_tax_reporting, com_curr, ''])

            item_table = Table(table_data, colWidths=[88, 430, 153, 30, 100])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))

            elements.append(item_table)
            if print_type == 'Source Currency':
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('customer_id')
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
            tax_class = 0
            grand_total1 = grand_total2 = 0
            if print_type == 'Source Currency':
                colWidths = src_col_width
            elif print_type == 'Functional Currency':
                colWidths = fun_col_width
            else:
                colWidths = tax_col_width
            summaries = []
            decimal_place = "%.2f"
            for period in periods:
                period_counter += 1
                table_data = []
                table_data.append(['Year-Period', ': ' + period])
                item_table = Table(table_data, colWidths=[88, 712])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)

                year = period.split('-')[0]
                month = period.split('-')[1]
                if print_type == 'Source Currency':
                    for currency in currencies:
                        subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                        currency_printed = False
                        table_data = []
                        table_data.append(['Source Currency', ': ' + currency['code']])
                        item_table = Table(table_data, colWidths=[88, 712])
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                        journal_by_curr = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)
                        all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                    journal__in=journal_by_curr
                                                                    ).order_by('tax__number', 'journal__customer_id')\
                            .exclude(tax_id__isnull=True)\
                            .select_related('tax', 'journal')
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
                                    column2 = trx.journal.customer.name
                                    column4 = trx.journal.document_number
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = round_number(trx.exchange_rate, 8)
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                    tax_class = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)

                            if last_journal_id != trx.journal.id:
                                decimal_place = get_decimal_place(trx.journal.currency)
                                table_data = []
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

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
                                    column2 = trx.journal.customer.name
                                    column4 = trx.journal.document_number
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = round_number(trx.exchange_rate, 8)
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                if tax_cl != tax_class and tax_class != 0:
                                    summery_obj = {'class': tax_class,
                                                'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)
                                    table_data = []
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '',
                                                    Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                        ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl
                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)
                            elif index > 0:
                                last_journal_id = trx.journal.id
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                if tax_cl != tax_class and tax_class != 0:
                                    table_data = []
                                    table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                    Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                    Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)

                                    tax_cl_source_total += round_number(total_amount)
                                    tax_cl_base_total += round_number(tax_base)
                                    tax_cl_tax_total += round_number(tax_amount)

                                    if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                        total_amount = trx.journal.total_amount * -1
                                    else:
                                        total_amount = trx.journal.total_amount
                                    tax_base = 0
                                    tax_amount = 0
                                    tax_rate = int(trx.tax.rate)

                                    summery_obj = {'class': tax_class,
                                                   'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                   'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)
                                    
                                    table_data = []
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '',
                                                    Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                        ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                    # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                    # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                                else:
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                    # tax_cl_base_total += round_number(trx.base_tax_amount)
                                    # tax_cl_tax_total += round_number(trx.tax_amount)
                            index += 1

                        if currency_printed:
                            if index != 0:
                                table_data = []
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                            if tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                            table_data = []
                            table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                            Paragraph(' Total ', styles['LeftAlignBold']), '',
                                            Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            table_data = []
                            table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period, styles['LeftAlignBold']), '',
                                            Paragraph(' Total ', styles['LeftAlignBold']), '',
                                            Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '', '', '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal2)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal3)), styles['RightAlignBold']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)
                            tax_class = 0
                            grand_total1 += subtotal2
                            grand_total2 += subtotal3

                        currency['summary1'] = subtotal1
                        currency['summary2'] = subtotal2
                        currency['summary3'] = subtotal3

                else:  # Tax Reporting Currency & Functional Currency
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    journal_by_period = all_journals.filter(perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_period
                                                                ).order_by('tax__number', 'journal__customer_id')\
                        .exclude(tax_id__isnull=True)\
                        .select_related('tax', 'journal')

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
                                column2 = trx.journal.customer.name
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']
                            tax_rate = int(trx.tax.rate)

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if print_type == 'Tax Reporting Currency':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = (tax_amount * exchange_rate)
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = (tax_amount * trx.exchange_rate)
                            if print_type == 'Functional Currency' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                                total_amount = (total_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                            else:
                                table_data.append([Paragraph(str(column1)[:17], styles['LeftAlign']), '', Paragraph(str(column2)[:25], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:21], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

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
                                column2 = trx.journal.customer.name
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if print_type == 'Tax Reporting Currency':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = (tax_amount * exchange_rate)
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = (tax_amount * trx.exchange_rate)
                            if print_type == 'Functional Currency' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                                total_amount = (total_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class, 'code': 'SGD',
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                table_data = []
                                if print_type == 'Functional Currency':
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                else:
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))

                                elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                table_data = []
                                if print_type == 'Functional Currency':
                                    table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                    Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                    Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                                    Paragraph(currency_code, styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                else:
                                    table_data.append([Paragraph(str(column1)[:17], styles['LeftAlign']), '', Paragraph(str(column2)[:25], styles['LeftAlign']), '',
                                                    Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:21], styles['LeftAlign']), '',
                                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                    Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                    Paragraph(currency_code, styles['RightAlign']), '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                total_amount = trx.journal.total_amount
                                if print_type == 'Functional Currency' and com_curr != currency_code:
                                    total_amount = (total_amount * trx.exchange_rate)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class, 'code': 'SGD',
                                               'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                table_data = []
                                if print_type == 'Functional Currency':
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                else:
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))

                                elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            t_base = 0
                            t_amount = 0

                            if print_type == 'Tax Reporting Currency':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    t_base = (trx.base_tax_amount * exchange_rate)
                                    t_amount = (trx.tax_amount * exchange_rate)
                                elif trx.journal.currency_id != to_currency:
                                    if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                        exchange_rate = trx.journal.tax_exchange_rate
                                    else:
                                        try:
                                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                        from_currency_id=from_currency, to_currency_id=to_currency,
                                                                                        exchange_date__lte=trx.journal.document_date,
                                                                                        flag='ACCOUNTING').order_by('exchange_date').last().rate
                                        except:
                                            exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    t_base = (trx.base_tax_amount * exchange_rate)
                                    t_amount = (trx.tax_amount * exchange_rate)
                                else:
                                    t_base = (trx.base_tax_amount * trx.exchange_rate)
                                    t_amount = (trx.tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional Currency' and com_curr != currency_code:
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
                            # tax_cl_base_total += round_number(t_base)
                            # tax_cl_tax_total += round_number(t_amount)
                        index += 1

                    if index != 0:
                        table_data = []
                        if print_type == 'Functional Currency':
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                        else:
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

                    if tax_class != 0:
                        summery_obj = {'class': tax_class, 'code': 'SGD',
                                    'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                        summaries.append(summery_obj)
                    table_data = []
                    if print_type == 'Functional Currency':
                        table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    else:
                        table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    subtotal1 += tax_cl_source_total
                    subtotal2 += tax_cl_base_total
                    subtotal3 += tax_cl_tax_total
                    table_data = []
                    if print_type == 'Functional Currency':
                        table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period, styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma(decimal_place_f % round_number(subtotal2)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(subtotal3)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    elif print_type == 'Tax Reporting Currency':
                        table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period, styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma("%.2f" % round_number(subtotal2)), styles['RightAlignBold']), '',
                                           Paragraph(intcomma("%.2f" % round_number(subtotal3)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    tax_class = 0
                    grand_total1 += subtotal2
                    grand_total2 += subtotal3
            # Grand total:
            table_data = []
            if print_type == 'Functional Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                table_data.append(['', '', '', '', '', '', Paragraph('TAX', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 0), (24, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 1), (24, 1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)
            elif print_type == 'Tax Reporting Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)
            elements.append(PageBreak())
            table_data = []
            table_data.append(['', Paragraph('Summary By Tax Authority And Tax Class', styles['RightAlignBold']), ''])
            item_table = Table(table_data, colWidths=[160, 240, 295])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            curr_code = 'Currency'
            str_1 = "Sales"
            line_1 = 120
            line_2 = 60
            if print_type == 'Source Currency':
                src = 'Source'
            elif print_type == 'Tax Reporting Currency':
                src = 'Tax Reporting'
                str_1 = ''
                line_1 = 0
            else:
                src = ''
                curr_code = ''
                line_2 = 0
            table_data = []
            table_data.append(['', '', '', '', '', '', '', Paragraph(src, styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            table_data.append([Paragraph('Tax Authority', styles['LeftAlignBold']), '', '', '', '',
                            Paragraph('Tax Class', styles['LeftAlignBold']), '', Paragraph(curr_code, styles['LeftAlignBold']), '',
                            Paragraph(str_1, styles['RightAlignBold']), '', Paragraph('Tax Base', styles['RightAlignBold']), '',
                            Paragraph('Tax Amounts', styles['RightAlignBold']), '', '', ''])

            if print_type == 'Source Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class', 'code'))
                l_class = 0
                l_code = ''
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']
                        l_code = summ['code']

                    if l_class == summ['class'] and l_code == summ['code']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        try:
                            curr = Currency.objects.get(code=l_code)
                            decimal_place = get_decimal_place(curr)
                        except:
                            decimal_place = "%.2f"
                        table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph('GSTDOS ', styles['LeftAlign']), '', '',
                                        Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(l_code, styles['LeftAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total1)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total2)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total3)), styles['RightAlign']), '', '', ''])

                        l_class = summ['class']
                        l_code = summ['code']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                try:
                    curr = Currency.objects.get(code=l_code)
                    decimal_place = get_decimal_place(curr)
                except:
                    decimal_place = "%.2f"
                if len(sortedsummaries):
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph('GSTDOS ', styles['LeftAlign']), '', '',
                                    Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(l_code, styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total1)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total2)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total3)), styles['RightAlign']), '', '', ''])

            elif print_type == 'Tax Reporting Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = 0
                total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                        Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                        Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(summ['code'], styles['LeftAlign']), '', '', '',
                                        Paragraph(intcomma("%.2f" % round_number(total2)), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(total3)), styles['RightAlign']), '', '', ''])

                        l_class = summ['class']
                        total2 = summ['summary2']
                        total3 = summ['summary3']

                if len(sortedsummaries):
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                    Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                    Paragraph(str(l_class), styles['LeftAlign']), '',
                                    Paragraph(summ['code'], styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma("%.2f" % round_number(total2)), styles['RightAlign']), '',
                                    Paragraph(intcomma("%.2f" % round_number(total3)), styles['RightAlign']), '', '', ''])
            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = 0
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                        Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                        Paragraph(str(l_class), styles['LeftAlign']), '', '', '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total1)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total2)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total3)), styles['RightAlign']), '', '', ''])

                        l_class = summ['class']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                    Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                    Paragraph(str(l_class), styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total1)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total2)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total3)), styles['RightAlign']), '', '', ''])

            table_data.append([Paragraph('1 authority printed', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', ''])

            item_table = Table(table_data,
                            colWidths=[90, 3, 165, 30, 3, 50, 3, line_2, 3, line_1, 5,
                                        90, 3, 95, 3, 25, 20])

            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 1), (0, 1), 0.25, colors.black),
                ('LINEBELOW', (2, 1), (3, 1), 0.25, colors.black),
                ('LINEBELOW', (5, 1), (5, 1), 0.25, colors.black),
                ('LINEBELOW', (7, 1), (7, 1), 0.25, colors.black),
                ('LINEBELOW', (9, 1), (9, 1), 0.25, colors.black),
                ('LINEBELOW', (11, 1), (11, 1), 0.25, colors.black),
                ('LINEBELOW', (13, 1), (13, 1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))

            elements.append(item_table)

        # if there's no order in the selected month
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
                                    issue_to=issue_to, print_type=print_type, report_by="Fiscal Period", print_by='Sales',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code, tax_authority=tax_authority),
                onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Fiscal Period",
                                    print_by='Sales',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code),
                canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


    def print_reportSalesDocumentDate(self, company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=115, bottomMargin=42,
                                pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))

        elements = []
        table_data = []
        table_data.append(['', '', '', '', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=[60, 3, 55, 3, 35, 3, 100, 3, 250, 275])

        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('TOPPADDING', (0, 0), (-1, 0), 10),
                                        ('LINEBELOW', (8, 0), (8, 0), 0.5, colors.transparent),
                                        ('ALIGN', (8, 0), (8, 0), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
        elements.append(item_table)
        table_data = []
        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            company = Company.objects.get(pk=company_id)
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            str_tax_reporting = com_curr = ''

            if print_type == 'Source Currency':
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Source', '', 'Exchange', '', 'Tax', '', 'Tax', '', '', '', '', '', ''])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Rate', '', 'Class', '',
                                'Rate', '', 'Sales', '', 'Tax Base', '', 'Tax Amount'])

                item_table = Table(table_data, colWidths=src_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            elif print_type == 'Functional Currency':
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '-----------Source---------', '', '---------------Functional----------------', '', '',  '', ''])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Sales', '', 'Curr', '', 'Sales', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = company.currency.code
                str_tax_reporting = "Functional Currency"

                item_table = Table(table_data, colWidths=fun_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (24, 0), (-1, -1), 'RIGHT'),
                    ('SPAN', (20, 0), (24, 0),),
                    ('ALIGN', (20, 0), (24, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            else:
                table_data.append(['Customer', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '------------Source-----------', '', '', '', '-----------------Tax Reporting-----------------'])

                table_data.append(['No.', '', 'Customer Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Sales', '', 'Curr', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"

                item_table = Table(table_data, colWidths=tax_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))

            elements.append(item_table)
            table_data = []

            if print_type == 'Source Currency' or print_type == 'Functional Currency':
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', '', '', ''])
            else:
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', str_tax_reporting, com_curr, ''])

            item_table = Table(table_data, colWidths=[88, 430, 153, 30, 100])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            if print_type == 'Source Currency':
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('customer_id')

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

            tax_class = 0
            summaries = []
            grand_total1 = grand_total2 = 0
            if print_type == 'Source Currency':
                colWidths = src_col_width
            elif print_type == 'Functional Currency':
                colWidths = fun_col_width
            else:
                colWidths = tax_col_width

            if print_type == 'Source Currency':
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    currency_printed = False
                    table_data = []
                    table_data.append(['Source Currency', ': ' + currency['code']])
                    item_table = Table(table_data, colWidths=[88, 712])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                    journal_by_curr = all_journals.filter(currency_id=currency['id'])
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_curr
                                                                ).order_by('tax__number', 'journal__document_date', 'journal_id')\
                        .exclude(tax_id__isnull=True)\
                        .select_related('tax', 'journal')
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
                                column2 = trx.journal.customer.name
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            table_data = []
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '',  Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

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
                                column2 = trx.journal.customer.name
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '',
                                                Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                    ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                table_data = []
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '',  Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = trx.journal.total_amount * -1
                                else:
                                    total_amount = trx.journal.total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class,
                                               'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                               'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '',
                                                Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                    ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                tax_base += trx.base_tax_amount * -1
                                tax_amount += trx.tax_amount * -1
                                # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                            else:
                                tax_base += trx.base_tax_amount
                                tax_amount += trx.tax_amount
                                # tax_cl_base_total += round_number(trx.base_tax_amount)
                                # tax_cl_tax_total += round_number(trx.tax_amount)
                        index += 1

                    if currency_printed:
                        if index != 0:
                            table_data = []
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                        if tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)
                        table_data = []
                        table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '',
                                        '', '', '', Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                            ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                        subtotal1 += tax_cl_source_total
                        subtotal2 += tax_cl_base_total
                        subtotal3 += tax_cl_tax_total
                        table_data = []
                        table_data.append(['', '', '', '', '', '', '', '', Paragraph(' Total ', styles['LeftAlignBold']), '',
                                        Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '', '', '',
                                        Paragraph(intcomma(decimal_place % round_number(subtotal2)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place % round_number(subtotal3)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                        tax_class = 0
                        grand_total1 += subtotal2
                        grand_total2 += subtotal3

                    currency['summary1'] = subtotal1
                    currency['summary2'] = subtotal2
                    currency['summary3'] = subtotal3

            else:  # Tax reporting currency
                subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                            journal__in=all_journals
                                                            ).order_by('tax__number', 'journal__document_date', 'journal_id')\
                    .exclude(tax_id__isnull=True)\
                    .select_related('tax', 'journal')

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
                            column2 = trx.journal.customer.name
                            column4 = trx.journal.document_number
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = round_number(trx.exchange_rate, 8)
                        if trx.tax:
                            tax_cl = trx.tax.number
                            tax_class = trx.tax.number
                        else:
                            tax_cl = 0
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']
                        tax_rate = int(trx.tax.rate)

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting Currency':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
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
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        if print_type == 'Functional Currency' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        table_data = []
                        if print_type == 'Functional Currency':
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(column2[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                        else:
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(column2[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

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
                            column2 = trx.journal.customer.name
                            column4 = trx.journal.document_number
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = round_number(trx.exchange_rate, 8)
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        tax_rate = int(trx.tax.rate)
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        if print_type == 'Tax Reporting Currency':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency, to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        if print_type == 'Functional Currency' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if tax_cl != tax_class and tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': 'SGD',
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            else:
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)
                    elif index > 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        if tax_cl != tax_class and tax_class != 0:
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(column2[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                            else:
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(column2[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            total_amount = trx.journal.total_amount
                            if print_type == 'Functional Currency' and com_curr != currency_code:
                                total_amount = (total_amount * trx.exchange_rate)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                            tax_base = 0
                            tax_amount = 0
                            tax_rate = int(trx.tax.rate)

                            summery_obj = {'class': tax_class,
                                           'code': 'SGD',
                                           'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            else:
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        t_base = 0
                        t_amount = 0
                        if print_type == 'Tax Reporting Currency':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency, to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            else:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = (trx.tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional Currency' and com_curr != currency_code:
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
                        # tax_cl_base_total += round_number(t_base)
                        # tax_cl_tax_total += round_number(t_amount)
                    index += 1

                if index != 0:
                    table_data = []
                    if print_type == 'Functional Currency':
                        table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                        Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                        Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                        Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                        Paragraph(currency_code, styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                    else:
                        table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                        Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                        Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                        Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                        Paragraph(currency_code, styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)

                    tax_cl_source_total += round_number(total_amount)
                    tax_cl_base_total += round_number(tax_base)
                    tax_cl_tax_total += round_number(tax_amount)

                if tax_class != 0:
                    summery_obj = {'class': tax_class, 'code': 'SGD',
                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                    summaries.append(summery_obj)
                table_data = []
                if print_type == 'Functional Currency':
                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                    item_table = Table(table_data, colWidths=colWidths)

                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                        ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                else:
                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                    item_table = Table(table_data, colWidths=colWidths)

                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                subtotal1 += tax_cl_source_total
                subtotal2 += tax_cl_base_total
                subtotal3 += tax_cl_tax_total
                tax_class = 0
                grand_total1 += subtotal2
                grand_total2 += subtotal3

            # Grand total:
            table_data = []
            if print_type == 'Functional Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                table_data.append(['', '', '', '', '', '', Paragraph('TAX', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                '', '', Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 0), (24, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 1), (24, 1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)
            if print_type == 'Tax Reporting Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)

            elements.append(PageBreak())
            table_data = []
            table_data.append(['', Paragraph('Summary By Tax Authority And Tax Class', styles['RightAlignBold']), ''])

            item_table = Table(table_data, colWidths=[160, 240, 295])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            curr_code = 'Currency'
            str_1 = "Sales"
            line_1 = 120
            line_2 = 60
            if print_type == 'Source Currency':
                src = 'Source'
            elif print_type == 'Tax Reporting Currency':
                src = 'Tax Reporting'
                str_1 = ''
                line_1 = 0
            else:
                src = ''
                curr_code = ''
                line_2 = 0
            table_data = []
            table_data.append(['', '', '', '', '', '', '', Paragraph(src, styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            table_data.append([Paragraph('Tax Authority', styles['LeftAlignBold']), '', '', '', '',
                            Paragraph('Tax Class', styles['LeftAlignBold']), '', Paragraph(curr_code, styles['LeftAlignBold']), '',
                            Paragraph(str_1, styles['RightAlignBold']), '', Paragraph('Tax Base', styles['RightAlignBold']), '',
                            Paragraph('Tax Amounts', styles['RightAlignBold']), '', '', ''])

            if print_type == 'Source Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    try:
                        curr = Currency.objects.get(code=summ['code'])
                        decimal_place = get_decimal_place(curr)
                    except:
                        decimal_place = "%.2f"
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph('GSTDOS ', styles['LeftAlign']), '', '',
                                    Paragraph(str(summ['class']), styles['LeftAlign']), '', Paragraph(summ['code'], styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(summ['summary1'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(summ['summary2'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(summ['summary3'])), styles['RightAlign']), '', '', ''])

            elif print_type == 'Tax Reporting Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                    Paragraph(TAX_TRACK_CLASS_DICT[summ['class']], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                    Paragraph(str(summ['class']), styles['LeftAlign']), '', Paragraph(summ['code'], styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma("%.2f" % round_number(summ['summary2'])), styles['RightAlign']), '',
                                       Paragraph(intcomma("%.2f" % round_number(summ['summary3'])), styles['RightAlign']), '', '', ''])
            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                    Paragraph(TAX_TRACK_CLASS_DICT[summ['class']], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                    Paragraph(str(summ['class']), styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma(decimal_place_f % round_number(summ['summary1'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(summ['summary2'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(summ['summary3'])), styles['RightAlign']), '', '', ''])

            table_data.append([Paragraph('1 authority printed', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            item_table = Table(table_data,
                            colWidths=[90, 3, 165, 30, 3, 50, 3, line_2, 3, line_1, 5,
                                        90, 3, 95, 3, 25, 20])

            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 1), (0, 1), 0.25, colors.black),
                ('LINEBELOW', (2, 1), (3, 1), 0.25, colors.black),
                ('LINEBELOW', (5, 1), (5, 1), 0.25, colors.black),
                ('LINEBELOW', (7, 1), (7, 1), 0.25, colors.black),
                ('LINEBELOW', (11, 1), (11, 1), 0.25, colors.black),
                ('LINEBELOW', (13, 1), (13, 1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))

            elements.append(item_table)

        # if there's no order in the selected month
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
                                    issue_to=issue_to, print_type=print_type, report_by="Document Date", print_by='Sales',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code, tax_authority=tax_authority),
                onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Document Date",
                                    print_by='Sales',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code),
                canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


    def print_reportPurchase(self, company_id, journal_ids, issue_from, issue_to, print_type, report_by, transaction_type, is_history, tax_authority):
        if report_by == 'Fiscal Period':
            pdf = self.print_reportPurchaseFiscalPeriod(company_id, journal_ids, issue_from, issue_to, print_type, transaction_type,
                                                is_history, tax_authority)
        else:
            pdf = self.print_reportPurchaseDocumentDate(company_id, journal_ids, issue_from, issue_to, print_type, transaction_type,
                                                is_history, tax_authority)

        return pdf


    def print_reportPurchaseFiscalPeriod(self, company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=115, bottomMargin=42,
                                pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        elements = []
        table_data = []
        table_data.append(['', '', '', '', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=[60, 3, 55, 3, 35, 3, 100, 3, 250, 275])

        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('TOPPADDING', (0, 0), (-1, 0), 10),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LINEBELOW', (8, 0), (8, 0), 0.5, colors.transparent),
                                        ('ALIGN', (8, 0), (8, 0), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
        elements.append(item_table)
        table_data = []
        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            company = Company.objects.get(pk=company_id)
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            str_tax_reporting = com_curr = ''

            if print_type == 'Source Currency':
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Source', '', 'Exchange', '', 'Tax', '', 'Tax', '', '', '', '', '', ''])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Rate', '', 'Class', '',
                                'Rate', '', 'Purchases', '', 'Tax Base', '', 'Tax Amount'])

                item_table = Table(table_data, colWidths=src_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            elif print_type == 'Functional Currency':
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '----------Source-----------', '', '---------------Functional---------------', '', '', '', ''])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Purchase', '', 'Curr', '', 'Purchase', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = company.currency.code
                str_tax_reporting = "Functional Currency"

                item_table = Table(table_data, colWidths=fun_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (24, 0), (-1, -1), 'RIGHT'),
                    ('SPAN', (20, 0), (24, 0),),
                    ('ALIGN', (20, 0), (24, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            else:
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '-------------Source-----------', '', '', '', '------------------Tax Reporting----------------'])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Purchases', '', 'Curr', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"

                item_table = Table(table_data, colWidths=tax_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))

            elements.append(item_table)
            table_data = []
            if print_type == 'Source Currency' or print_type == 'Functional Currency':
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', '', '', ''])
            else:
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', str_tax_reporting, com_curr, ''])

            item_table = Table(table_data, colWidths=[88, 430, 153, 30, 100])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            if print_type == 'Source Currency':
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('supplier_id')
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
            tax_class = 0
            summaries = []
            grand_total1 = grand_total2 = 0
            if print_type == 'Source Currency':
                colWidths = src_col_width
            elif print_type == 'Functional Currency':
                colWidths = fun_col_width
            else:
                colWidths = tax_col_width

            for period in periods:
                period_counter += 1
                table_data = []
                table_data.append(['Year-Period', ': ' + period])
                item_table = Table(table_data, colWidths=[88, 712])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)

                year = period.split('-')[0]
                month = period.split('-')[1]
                if print_type == 'Source Currency':
                    for currency in currencies:
                        subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                        currency_printed = False
                        table_data = []
                        table_data.append(['Source Currency', ': ' + currency['code']])
                        item_table = Table(table_data, colWidths=[88, 712])
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                        journal_by_curr = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)
                        all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                    journal__in=journal_by_curr
                                                                    ).order_by('tax__number', 'journal__supplier_id', 'journal__document_date', 'journal_id')\
                            .exclude(tax_id__isnull=True)\
                            .select_related('tax', 'journal')
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
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                                else:
                                    source_code = 'AP-PY'
                                try:
                                    column1 = trx.journal.supplier.code
                                    column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                    column4 = trx.journal.document_number
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = round_number(trx.exchange_rate, 8)
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                    tax_class = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)
                            
                            if last_journal_id != trx.journal.id:
                                table_data = []
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                last_journal_id = trx.journal.id
                                decimal_place = get_decimal_place(trx.journal.currency)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                                else:
                                    source_code = 'AP-PY'
                                try:
                                    column1 = trx.journal.supplier.code
                                    column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                    column4 = trx.journal.document_number
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = round_number(trx.exchange_rate, 8)
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                if tax_cl != tax_class and tax_class != 0:
                                    summery_obj = {'class': tax_class,
                                                'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)
                                    table_data = []
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '',
                                                    Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                        ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl
                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)
                            elif index > 0:
                                last_journal_id = trx.journal.id
                                decimal_place = get_decimal_place(trx.journal.currency)
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0

                                if tax_cl != tax_class and tax_class != 0:
                                    table_data = []
                                    table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                    Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                    Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(
                                                           str(tax_rate), styles['CenterAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)

                                    tax_cl_source_total += round_number(total_amount)
                                    tax_cl_base_total += round_number(tax_base)
                                    tax_cl_tax_total += round_number(tax_amount)

                                    if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                        total_amount = trx.journal.total_amount * -1
                                    else:
                                        total_amount = trx.journal.total_amount
                                    tax_base = 0
                                    tax_amount = 0
                                    tax_rate = int(trx.tax.rate)

                                    summery_obj = {'class': tax_class,
                                                'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)

                                    table_data = []
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '',
                                                    Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                        ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                    tax_cl_source_total = 0
                                else:
                                    tax_class = tax_cl

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                    # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                    # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                                else:
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                    # tax_cl_base_total += round_number(trx.base_tax_amount)
                                    # tax_cl_tax_total += round_number(trx.tax_amount)
                            index += 1

                        if currency_printed:
                            if index != 0:
                                table_data = []
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                            if tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}

                                summaries.append(summery_obj)
                            table_data = []
                            table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                            Paragraph(' Total ', styles['LeftAlignBold']), '',
                                            Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            table_data = []
                            table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period, styles['LeftAlignBold']), '',
                                            Paragraph(' Total ', styles['LeftAlignBold']), '',
                                            Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '', '', '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal2)), styles['RightAlignBold']), '',
                                            Paragraph(intcomma(decimal_place % round_number(subtotal3)), styles['RightAlignBold']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)
                            tax_class = 0
                            grand_total1 += subtotal2
                            grand_total2 += subtotal3

                        currency['summary1'] = subtotal1
                        currency['summary2'] = subtotal2
                        currency['summary3'] = subtotal3

                else:  # Tax reporting currency & functional currency
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    journal_by_period = all_journals.filter(perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_period
                                                                ).order_by('tax__number', 'journal__supplier_id', 'journal_id')\
                        .exclude(tax_id__isnull=True)\
                        .select_related('tax', 'journal')

                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    for trx in all_transactions:
                        if index == 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']
                            tax_rate = int(trx.tax.rate)

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            if print_type == 'Tax Reporting Currency':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
                                elif trx.journal.currency_id != to_currency:
                                    if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                        exchange_rate = trx.journal.tax_exchange_rate
                                    else:
                                        try:
                                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                        from_currency_id=from_currency, to_currency_id=to_currency,
                                                                                        exchange_date__lte=trx.journal.document_date,
                                                                                        flag='ACCOUNTING').order_by('exchange_date').last().rate
                                        except:
                                            exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = tax_amount * trx.exchange_rate
                            if print_type == 'Functional Currency' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = tax_amount * trx.exchange_rate
                                total_amount = (total_amount * trx.exchange_rate)

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                            

                        if last_journal_id != trx.journal.id:
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])
                            else:
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if print_type == 'Tax Reporting Currency':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = tax_amount * trx.exchange_rate
                            if print_type == 'Functional Currency' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = tax_amount * trx.exchange_rate
                                total_amount = (total_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': 'SGD',
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                table_data = []
                                if print_type == 'Functional Currency':
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                else:
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                            
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                table_data = []
                                if print_type == 'Functional Currency':
                                    table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                    Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                    Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                                    Paragraph(currency_code, styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])
                                else:
                                    table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                    Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                    Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                    Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                    Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                    Paragraph(currency_code, styles['RightAlign']), '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                                       Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                total_amount = trx.journal.total_amount
                                if print_type == 'Functional Currency' and com_curr != currency_code:
                                    total_amount = (total_amount * trx.exchange_rate)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class,
                                                'code': 'SGD',
                                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                table_data = []
                                if print_type == 'Functional Currency':
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                else:
                                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                       Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
                                    elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            t_base = 0
                            t_amount = 0
                            if print_type == 'Tax Reporting Currency':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
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
                                    column6 = round_number(exchange_rate, 8)
                                    t_base = (trx.base_tax_amount * exchange_rate)
                                    t_amount = trx.tax_amount * exchange_rate
                                else:
                                    t_base = (trx.base_tax_amount * trx.exchange_rate)
                                    t_amount = (trx.tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional Currency' and com_curr != currency_code:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = trx.tax_amount * trx.exchange_rate
                            else:
                                t_base = trx.base_tax_amount
                                t_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                t_base = -1 * t_base
                                t_amount = -1 * t_amount

                            tax_base += t_base
                            tax_amount += t_amount
                            # tax_cl_base_total += t_base
                            # tax_cl_tax_total += t_amount
                            
                        index += 1

                    if index != 0:
                        table_data = []
                        if print_type == 'Functional Currency':
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])
                        else:
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

                    if tax_class != 0:
                        summery_obj = {'class': tax_class, 'code': 'SGD',
                                    'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}

                        summaries.append(summery_obj)
                    table_data = []
                    if print_type == 'Functional Currency':
                        table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    else:
                        table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    subtotal1 += tax_cl_source_total
                    subtotal2 += tax_cl_base_total
                    subtotal3 += tax_cl_tax_total
                    table_data = []
                    if print_type == 'Functional Currency':
                        table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period, styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma(decimal_place_f % round_number(subtotal2)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(subtotal3)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    else:
                        table_data.append(['', '', '', '', '', '', Paragraph('Fiscal ' + period, styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                        Paragraph(intcomma("%.2f" % round_number(subtotal2)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma("%.2f" % round_number(subtotal3)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                    tax_class = 0
                    grand_total1 += subtotal2
                    grand_total2 += subtotal3

            # Grand total:
            table_data = []
            if print_type == 'Functional Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                table_data.append(['', '', '', '', '', '', Paragraph('Tax', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                '', '', Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 0), (24, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 1), (24, 1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)
            elif print_type == 'Tax Reporting Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)

            elements.append(PageBreak())
            table_data = []
            table_data.append(['', Paragraph('Summary By Tax Authority And Tax Class', styles['RightAlignBold']), ''])

            item_table = Table(table_data, colWidths=[160, 240, 295])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            curr_code = 'Currency'
            str_1 = "Purchases"
            line_1 = 120
            line_2 = 60
            if print_type == 'Source Currency':
                src = 'Source'
            elif print_type == 'Tax Reporting Currency':
                src = 'Tax Reporting'
                str_1 = ''
                line_1 = 0
            else:
                src = ''
                curr_code = ''
                line_2 = 0
            table_data = []
            table_data.append(['', '', '', '', '', '', '', Paragraph(src, styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            table_data.append([Paragraph('Tax Authority', styles['LeftAlignBold']), '', '', '', '',
                            Paragraph('Tax Class', styles['LeftAlignBold']), '', Paragraph(curr_code, styles['LeftAlignBold']), '',
                            Paragraph(str_1, styles['RightAlignBold']), '', Paragraph('Tax Base', styles['RightAlignBold']), '',
                            Paragraph('Tax Amounts', styles['RightAlignBold']), '', '', ''])

            total_tax_amu = 0

            if print_type == 'Source Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class', 'code'))
                l_class = 0
                l_code = ''
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']
                        l_code = summ['code']

                    if l_class == summ['class'] and l_code == summ['code']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        try:
                            curr = Currency.objects.get(code=l_code)
                            decimal_place = get_decimal_place(curr)
                        except:
                            decimal_place = "%.2f"
                        table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph('GSTDOS ', styles['LeftAlign']), '', '',
                                        Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(l_code, styles['LeftAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total1)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total2)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total3)), styles['RightAlign']), '', '', ''])

                        l_class = summ['class']
                        l_code = summ['code']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                try:
                    curr = Currency.objects.get(code=l_code)
                    decimal_place = get_decimal_place(curr)
                except:
                    decimal_place = "%.2f"

                if len(sortedsummaries):
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph('GSTDOS ', styles['LeftAlign']), '', '',
                                    Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(l_code, styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total1)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total2)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(total3)), styles['RightAlign']), '', '', ''])

            elif print_type == 'Tax Reporting Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = 0
                total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                        Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                        Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(summ['code'], styles['LeftAlign']), '', '', '',
                                        Paragraph(intcomma("%.2f" % round_number(total2)), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(total3)), styles['RightAlign']), '', '', ''])

                        l_class = summ['class']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '',
                                    Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']), Paragraph('Total ', styles['LeftAlign']), '',
                                    Paragraph(str(l_class), styles['LeftAlign']), '', Paragraph(summ['code'], styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma("%.2f" % round_number(total2)), styles['RightAlign']), '',
                                       Paragraph(intcomma("%.2f" % round_number(total3)), styles['RightAlign']), '', '', ''])

            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = ''
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    total_tax_amu += summ['summary3']
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']),
                                        Paragraph('Total ', styles['LeftAlign']), '', Paragraph(str(l_class), styles['LeftAlign']), '',
                                        '', '', Paragraph(intcomma(decimal_place_f % round_number(total1)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total2)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total3)), styles['RightAlign']), '', '', ''])

                        l_class = summ['class']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph(TAX_TRACK_CLASS_DICT[l_class], styles['LeftAlign']),
                                    Paragraph('Total ', styles['LeftAlign']), '', Paragraph(str(l_class), styles['LeftAlign']), '',
                                    '', '', Paragraph(intcomma(decimal_place_f % round_number(total1)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total2)), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(total3)), styles['RightAlign']), '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', 'Total Tax :', '',
                                Paragraph(intcomma(decimal_place_f % round_number(total_tax_amu)), styles['RightAlign']), ''])

            table_data.append([Paragraph('1 authority printed', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            item_table = Table(table_data, colWidths=[90, 3, 165, 30, 3, 50, 3, line_2, 3, line_1, 5, 90, 3, 95, 3, 25, 20])

            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 1), (0, 1), 0.25, colors.black),
                ('LINEBELOW', (2, 1), (3, 1), 0.25, colors.black),
                ('LINEBELOW', (5, 1), (5, 1), 0.25, colors.black),
                ('LINEBELOW', (7, 1), (7, 1), 0.25, colors.black),
                ('LINEBELOW', (9, 1), (9, 1), 0.25, colors.black),
                ('LINEBELOW', (11, 1), (11, 1), 0.25, colors.black),
                ('LINEBELOW', (13, 1), (13, 1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))

            elements.append(item_table)

        # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['']]
            table_body = Table(table_data, colWidths=[795])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(table_body)

        doc.build(elements,
                onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Fiscal Period", print_by='Purchase',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code, tax_authority=tax_authority),
                onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Fiscal Period",
                                    print_by='Purchase',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code),
                canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


    def print_reportPurchaseDocumentDate(self, company_id, journal_ids, issue_from, issue_to, print_type, transaction_type, is_history, tax_authority):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=115, bottomMargin=42,
                                pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        elements = []
        table_data = []
        table_data.append(['', '', '', '', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=[60, 3, 55, 3, 35, 3, 100, 3, 250, 275])

        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('TOPPADDING', (0, 0), (-1, 0), 10),
                                        ('LINEBELOW', (8, 0), (8, 0), 0.5, colors.transparent),
                                        ('ALIGN', (8, 0), (8, 0), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                        ]))
        elements.append(item_table)
        table_data = []
        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            company = Company.objects.get(pk=company_id)
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            str_tax_reporting = com_curr = ''

            if print_type == 'Source Currency':
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Source', '', 'Exchange', '', 'Tax', '', 'Tax', '', '', '', '', '', ''])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Rate', '', 'Class', '',
                                'Rate', '', 'Purchases', '', 'Tax Base', '', 'Tax Amount'])

                item_table = Table(table_data, colWidths=src_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            elif print_type == 'Functional Currency':
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '----------Source-----------', '', '---------------Functional---------------', '', '', '', ''])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Purchase', '', 'Curr', '', 'Purchase', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = company.currency.code
                str_tax_reporting = "Functional Currency"

                item_table = Table(table_data, colWidths=fun_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (24, 0), (-1, -1), 'RIGHT'),
                    ('SPAN', (20, 0), (24, 0),),
                    ('ALIGN', (20, 0), (24, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
            else:
                table_data.append(['Vendor', '', '', '', '', '', '', '', 'Srce.', '', 'Tax Rpt.', '', 'Tax', '', 'Tax', '', '', '',
                                '-------------Source-----------', '', '', '', '------------------Tax Reporting----------------'])

                table_data.append(['No.', '', 'Vendor Name', '', 'Doc. Date', '', 'Document No.', '', 'Code', '', 'Exch. Rate', '', 'Class', '',
                                'Rate', '', 'Purchases', '', 'Curr', '', 'Tax Base', '', 'Tax Amount'])

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"

                item_table = Table(table_data, colWidths=tax_col_width)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
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
                    ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
                    ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (20, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (22, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))

            elements.append(item_table)
            table_data = []

            if print_type == 'Source Currency':
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', '', '', ''])
            else:
                table_data.append(['Tax Authority', ': [GSTDOS] to [GSTDOS]', str_tax_reporting, com_curr, ''])

            item_table = Table(table_data, colWidths=[88, 430, 153, 30, 100])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            if print_type == 'Source Currency':
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('supplier_id')

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id, 'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}

                    currencies.append(curr_obj)
                    last_currency = currency_id

            tax_class = 0
            summaries = []
            grand_total1 = grand_total2 = 0
            if print_type == 'Source Currency':
                colWidths = src_col_width
            elif print_type == 'Functional Currency':
                colWidths = fun_col_width
            else:
                colWidths = tax_col_width

            if print_type == 'Source Currency':
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    currency_printed = False
                    table_data = []
                    table_data.append(['Source Currency', ': ' + currency['code']])
                    item_table = Table(table_data, colWidths=[88, 712])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                    journal_by_curr = all_journals.filter(currency_id=currency['id'])
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0, journal__in=journal_by_curr
                                                                ).order_by('tax__number', 'journal__document_date', 'journal_id')\
                        .exclude(tax_id__isnull=True).select_related('tax', 'journal')

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
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            table_data = []
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = round_number(trx.exchange_rate, 8)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}

                                summaries.append(summery_obj)
                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '',
                                                '', '', '', '', Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                    ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                table_data = []
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = trx.journal.total_amount * -1
                                else:
                                    total_amount = trx.journal.total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                
                                table_data = []
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '',
                                                '', '', '', '', Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                                    ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                tax_base += trx.base_tax_amount * -1
                                tax_amount += trx.tax_amount * -1
                                # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                            else:
                                tax_base += trx.base_tax_amount
                                tax_amount += trx.tax_amount
                                # tax_cl_base_total += round_number(trx.base_tax_amount)
                                # tax_cl_tax_total += round_number(trx.tax_amount)
                        index += 1

                    if currency_printed:
                        if index != 0:
                            table_data = []
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                        if tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}

                            summaries.append(summery_obj)
                        table_data = []
                        table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                        Paragraph(' Total ', styles['LeftAlignBold']), '', Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '',
                                        '', '', '', Paragraph(intcomma(decimal_place % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (16, -1), (16, -1), 0.25, colors.black),
                            ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                        subtotal1 += tax_cl_source_total
                        subtotal2 += tax_cl_base_total
                        subtotal3 += tax_cl_tax_total
                        table_data = []
                        table_data.append(['', '', '', '', '', '', '', '', Paragraph(' Total ', styles['LeftAlignBold']), '',
                                        Paragraph(currency['code'] + ' :', styles['LeftAlignBold']), '', '', '', '', '', '', '',
                                        Paragraph(intcomma(decimal_place % round_number(subtotal2)), styles['RightAlignBold']), '',
                                        Paragraph(intcomma(decimal_place % round_number(subtotal3)), styles['RightAlignBold']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('LINEABOVE', (18, -1), (18, -1), 0.25, colors.black),
                            ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)
                        tax_class = 0
                        grand_total1 += subtotal2
                        grand_total2 += subtotal3

            else:  # Tax reporting currency & functional currency
                subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0, journal__in=all_journals
                                                            ).order_by('tax__number', 'journal__supplier_id', 'journal_id')\
                    .exclude(tax_id__isnull=True).select_related('tax', 'journal')

                if not int(is_history):
                    all_transactions = all_transactions.filter(is_clear_tax=False)
                last_journal_id = 0
                index = 0
                for trx in all_transactions:
                    if index == 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AP-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AP-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AP-CR'
                        else:
                            source_code = 'AP-PY'
                        try:
                            column1 = trx.journal.supplier.code
                            column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                            column4 = trx.journal.document_number
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = round_number(trx.exchange_rate, 8)
                        if trx.tax:
                            tax_cl = trx.tax.number
                            tax_class = trx.tax.number
                        else:
                            tax_cl = 0
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']
                        tax_rate = int(trx.tax.rate)

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting Currency':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
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
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        if print_type == 'Functional Currency' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        table_data = []
                        if print_type == 'Functional Currency':
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '',  Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])
                        else:
                            table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                            Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                            Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                            Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                            Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                            Paragraph(currency_code, styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                            Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                        elements.append(item_table)

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AP-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AP-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AP-CR'
                        else:
                            source_code = 'AP-PY'
                        try:
                            column1 = trx.journal.supplier.code
                            column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                            column4 = trx.journal.document_number
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = round_number(trx.exchange_rate, 8)
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        tax_rate = int(trx.tax.rate)
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting Currency':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency, to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        if print_type == 'Functional Currency' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        if tax_cl != tax_class and tax_class != 0:
                            summery_obj = {'class': tax_class, 'code': 'SGD',
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            else:
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)
                    elif index > 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        if tax_cl != tax_class and tax_class != 0:
                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '',  Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])
                            else:
                                table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                                Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:18], styles['LeftAlign']), '',
                                                Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                                Paragraph(intcomma(tax_class), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                                Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                                Paragraph(currency_code, styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                            elements.append(item_table)

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            total_amount = trx.journal.total_amount
                            if print_type == 'Functional Currency' and com_curr != currency_code:
                                total_amount = (total_amount * trx.exchange_rate)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                            tax_base = 0
                            tax_amount = 0
                            tax_rate = int(trx.tax.rate)

                            summery_obj = {'class': tax_class, 'code': 'SGD',
                                           'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)

                            table_data = []
                            if print_type == 'Functional Currency':
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            else:
                                table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                                Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                elements.append(item_table)
                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        t_base = 0
                        t_amount = 0
                        if print_type == 'Tax Reporting Currency':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
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
                                column6 = round_number(exchange_rate, 8)
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            else:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = (trx.tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional Currency' and com_curr != currency_code:
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
                        # tax_cl_base_total += round_number(t_base)
                        # tax_cl_tax_total += round_number(t_amount)
                    index += 1

                if index != 0:
                    table_data = []
                    if print_type == 'Functional Currency':
                        table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                        Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                        Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                        Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(s_amount)), styles['RightAlign']), '',
                                        Paragraph(currency_code, styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(total_amount)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_base)), styles['RightAlign']), '',
                                        Paragraph(intcomma(decimal_place_f % round_number(tax_amount)), styles['RightAlign']), ])
                    else:
                        table_data.append([Paragraph(str(column1)[:11], styles['LeftAlign']), '', Paragraph(str(column2)[:21], styles['LeftAlign']), '',
                                        Paragraph(column3, styles['LeftAlign']), '', Paragraph(str(column4)[:20], styles['LeftAlign']), '',
                                        Paragraph(source_code, styles['LeftAlign']), '', Paragraph(str(column6)[:11], styles['RightAlign']), '',
                                        Paragraph(intcomma(tax_cl), styles['CenterAlign']), '', Paragraph(str(tax_rate), styles['CenterAlign']), '',
                                        Paragraph(intcomma(decimal_place % round_number(total_amount)), styles['RightAlign']), '',
                                        Paragraph(currency_code, styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_base)), styles['RightAlign']), '',
                                        Paragraph(intcomma("%.2f" % round_number(tax_amount)), styles['RightAlign']), ])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)

                    tax_cl_source_total += round_number(total_amount)
                    tax_cl_base_total += round_number(tax_base)
                    tax_cl_tax_total += round_number(tax_amount)

                if tax_class != 0:
                    summery_obj = {'class': tax_class, 'code': 'SGD',
                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}

                    summaries.append(summery_obj)
                table_data = []
                if print_type == 'Functional Currency':
                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_source_total)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                        ('LINEABOVE', (24, -1), (24, -1), 0.25, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                else:
                    table_data.append(['', '', '', '', '', '', Paragraph(transaction_type + ' ' + str(tax_class), styles['LeftAlignBold']), '',
                                    Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_base_total)), styles['RightAlignBold']), '',
                                    Paragraph(intcomma("%.2f" % round_number(tax_cl_tax_total)), styles['RightAlignBold']), ])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                        ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                subtotal1 += tax_cl_source_total
                subtotal2 += tax_cl_base_total
                subtotal3 += tax_cl_tax_total
                tax_class = 0
                grand_total1 += subtotal2
                grand_total2 += subtotal3

            # Grand total:
            table_data = []
            if print_type == 'Functional Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                table_data.append(['', '', '', '', '', '', Paragraph('TAX', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma(decimal_place_f % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (24, 0), (24, 0), 0.25, colors.black),
                    ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                    ('LINEABOVE', (24, 1), (24, 1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)
            elif print_type == 'Tax Reporting Currency':
                table_data.append(['', '', '', '', '', '', Paragraph('GSTDOS', styles['LeftAlignBold']), '',
                                Paragraph(' Total ', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', '', '', '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total1)), styles['RightAlignBold']), '',
                                Paragraph(intcomma("%.2f" % round_number(grand_total2)), styles['RightAlignBold']), ])

                item_table = Table(table_data, colWidths=colWidths)

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LINEABOVE', (20, -1), (20, -1), 0.25, colors.black),
                    ('LINEABOVE', (22, -1), (22, -1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)

            elements.append(PageBreak())
            table_data = []
            table_data.append(['', Paragraph('Summary By Tax Authority And Tax Class', styles['RightAlignBold']), ''])

            item_table = Table(table_data, colWidths=[160, 240, 295])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            elements.append(item_table)
            curr_code = 'Currency'
            str_1 = "Purchases"
            line_1 = 120
            line_2 = 60
            if print_type == 'Source Currency':
                src = 'Source'
            elif print_type == 'Tax Reporting Currency':
                src = 'Tax Reporting'
                str_1 = ''
                line_1 = 0
            else:
                src = ''
                curr_code = ''
                line_2 = 0
            table_data = []
            table_data.append(['', '', '', '', '', '', '', Paragraph(src, styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            table_data.append([Paragraph('Tax Authority', styles['LeftAlignBold']), '', '', '', '', Paragraph('Tax Class', styles['LeftAlignBold']), '',
                            Paragraph(curr_code, styles['LeftAlignBold']), '', Paragraph(str_1, styles['RightAlignBold']), '',
                            Paragraph('Tax Base', styles['RightAlignBold']), '', Paragraph('Tax Amounts', styles['RightAlignBold']), '', '', ''])

            total_tax_amu = 0

            if print_type == 'Source Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    try:
                        curr = Currency.objects.get(code=summ['code'])
                        decimal_place = get_decimal_place(curr)
                    except:
                        decimal_place = "%.2f"
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph('GSTDOS ', styles['LeftAlign']), '', '',
                                    Paragraph(str(summ['class']), styles['LeftAlign']), '', Paragraph(summ['code'], styles['LeftAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(summ['summary1'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(summ['summary2'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place % round_number(summ['summary3'])), styles['RightAlign']), '', '', ''])

            elif print_type == 'Tax Reporting Currency':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph(TAX_TRACK_CLASS_DICT[summ['class']], styles['LeftAlign']),
                                    Paragraph('Total ', styles['LeftAlign']), '', Paragraph(str(summ['class']), styles['LeftAlign']), '',
                                    Paragraph(summ['code'], styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma("%.2f" % round_number(summ['summary2'])), styles['RightAlign']), '',
                                    Paragraph(intcomma("%.2f" % round_number(summ['summary3'])), styles['RightAlign']), '', '', ''])

            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    total_tax_amu += summ['summary3']
                    table_data.append([Paragraph('GSTDOS ', styles['LeftAlign']), '', Paragraph(TAX_TRACK_CLASS_DICT[summ['class']], styles['LeftAlign']),
                                    Paragraph('Total ', styles['LeftAlign']), '', Paragraph(str(summ['class']), styles['LeftAlign']), '', '', '',
                                    Paragraph(intcomma(decimal_place_f % round_number(summ['summary1'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(summ['summary2'])), styles['RightAlign']), '',
                                    Paragraph(intcomma(decimal_place_f % round_number(summ['summary3'])), styles['RightAlign']), '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', 'Report Tax :', '',
                                Paragraph(intcomma(decimal_place_f % round_number(total_tax_amu)), styles['RightAlign']), ''])

            table_data.append([Paragraph('1 authority printed', styles['LeftAlignBold']), '', '', '', '', '', '', '', '', ''])

            item_table = Table(table_data,
                            colWidths=[90, 3, 165, 30, 3, 50, 3, line_2, 3, line_1, 5,
                                        90, 3, 95, 3, 25, 20])

            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 1), (0, 1), 0.25, colors.black),
                ('LINEBELOW', (2, 1), (3, 1), 0.25, colors.black),
                ('LINEBELOW', (5, 1), (5, 1), 0.25, colors.black),
                ('LINEBELOW', (7, 1), (7, 1), 0.25, colors.black),
                ('LINEBELOW', (9, 1), (9, 1), 0.25, colors.black),
                ('LINEBELOW', (11, 1), (11, 1), 0.25, colors.black),
                ('LINEBELOW', (13, 1), (13, 1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))

            elements.append(item_table)

        # if there's no order in the selected month
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
                                    issue_to=issue_to, print_type=print_type, report_by="Document Date", print_by='Purchase',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code, tax_authority=tax_authority),
                onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                    issue_to=issue_to, print_type=print_type, report_by="Document Date",
                                    print_by='Purchase',
                                    transaction_type=transaction_type, tx_rpt_code=self.tax_rpt_code),
                canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
