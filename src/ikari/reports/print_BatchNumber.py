from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from companies.models import Company
from currencies.models import ExchangeRate, Currency
from accounting.models import Journal, Batch, DOCUMENT_TYPES, RevaluationLogs
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, STATUS_TYPE, DOCUMENT_TYPE_DICT, \
    PAYMENT_TRANSACTION_TYPES, PAYMENT_TYPE, RECEIPT_TRANSACTION_TYPES
from utilities.common import round_number
from datetime import datetime
from django.db.models import Sum
from django.db.models import Count
import os

COMMON_COLUMN = [70, 5, 130, 5, 80, 5, 80, 5, 65, 5, 115, 5, 110, 5, 110]
COMMON_COLUMN_2 = [90, 3, 107, 3, 207, 3, 183, 3, 100, 3, 100]
COMMON_COLUMN_3 = [80, 3, 176, 3, 80, 3, 80, 3, 80, 3, 80, 3, 100, 3, 100, 3]


class Print_BatchNumber:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, batch_type, ql_type_report=0):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', fontName=s.REPORT_FONT, alignment=TA_CENTER, fontSize=s.REPORT_FONT_SIZE))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "Date: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, Paragraph(row1_info2, styles['Center'])])

        if batch_type == '1':
            row2_info1 = 'A/R Batch Listing - Invoice'
        elif batch_type == '2':
            row2_info1 = 'A/P Batch Listing - Invoice'
        elif batch_type == '3':
            row2_info1 = 'A/R Batch Listing - Receipt'
        elif batch_type == '4':
            row2_info1 = 'A/P Batch Listing - Payment'
        elif ql_type_report == '2':
            row2_info1 = 'G/L Transactions Listing - In Source And Functional Currency'
        elif ql_type_report == '1':
            row2_info1 = 'G/L Transactions Listing - In Functional Currency'
        else:
            row2_info1 = ''

        row2_info2 = ''
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=[240, 300, 240])
        header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                          ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                          ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                          ('TOPPADDING', (0, 0), (-1, -1), 0),
                                          ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                          ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                          ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def format_decimal(is_decimal, amount):
        amount = amount if amount else 0
        return intcomma('%.2f' % round_number(amount)) if is_decimal else intcomma('%.0f' % round_number(amount, 0))

    @staticmethod
    def trancate_string(data, max_length):
        max_length = int(max_length)
        data = str(data)
        return (data[:max_length] + '..') if len(data) > max_length else data

    def print_report_ap_invoice(self, company_id, batch_type, batch_from, batch_to, entry_from, entry_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))

        if int(batch_from) > int(batch_to):
            batch_to = batch_from

        batch_list = Batch.objects.filter(is_hidden=0, status__in=[STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted']],
                                          company_id=company_id, batch_type=int(batch_type), id__gte=batch_from, id__lte=batch_to).order_by('id')

        elements = []
        table_data = []
        table_data.append(['From Batch Number:', '[' + str(batch_list.first().batch_no) + '] to [' + str(batch_list.last().batch_no) + ']'])
        table_data.append(['From Batch Date:', '[' + batch_list.first().batch_date.strftime('%d/%m/%Y') + '] to ['
                           + batch_list.last().batch_date.strftime('%d/%m/%Y') + ']'])
        table_data.append(['Status ', '[Open, Posted]'])
        table_data.append(['Reprint Previously Printed Batches', '[Yes]'])
        table_data.append(['Show Schedules', '[Yes]'])
        table_data.append(['Show Tax Details', '[Yes]'])
        table_data.append(['Show Comments', '[Yes]'])
        table_data.append([])

        item_table = Table(table_data, colWidths=[150, 660])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))

        elements.append(item_table)

        count_entry = 0

        for batch in batch_list:
            journal_list = Journal.objects.filter(batch__id=batch.id, is_hidden=0, company_id=company_id) \
                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']).exclude(is_auto_reversed_entry=True) \
                .exclude(status=int(STATUS_TYPE_DICT['Auto Reverse Entry'])).exclude(reference='REVERSING ENTRY') \
                .select_related('batch')
            
            if entry_from != 'null' and int(entry_from):
                entry_from = int(entry_from)
                journal_list = journal_list.filter(id__gte=entry_from)
            if entry_to != 'null' and int(entry_to):
                entry_to = int(entry_to)
                journal_list = journal_list.filter(id__lte=entry_to)

            count_entry += len(journal_list)
            journal_list_sort = sorted(journal_list, key=lambda Journal: int(Journal.code))

            table_data = []

            total_amount = intcomma('%.2f' % round_number(batch.batch_amount)) if batch.currency.is_decimal else intcomma('%.0f' % round_number(batch.batch_amount, 0))

            table_data.append(['Batch No:', batch.batch_no, '', 'Description:', batch.description, '', '', '',  '', 'Total amount:', total_amount])

            manual_doc = document_type(journal_list)
            table_data.append(['Batch Date:', batch.batch_date.strftime('%d/%m/%Y'), '', 'Type:', manual_doc, '',
                               'Source Application:', batch.source_ledger, '', 'No. of Entries:', batch.no_entries])

            table_data.append(['Last Edited:', batch.update_date.strftime('%d/%m/%Y'), '', 'Status:', STATUS_TYPE[batch.status - 1][1], '', '', '', ''])

            item_table = Table(table_data, colWidths=[80, 100, 15, 80, 100, 30, 100, 100, 5, 80, 120])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('ALIGN', (8, 0), (10, 1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))

            elements.append(item_table)
            batch_total_amount__sum = 0
            for journal in journal_list_sort:
                trx_list = Transaction.objects.filter(is_hidden=0, company_id=company_id, journal__id=journal.id).order_by('id')
                table_data = []
                table_data.append([])
                # row 1 of entry
                table_data.append(['Entry No.:', journal.code, journal.name, 'Vendor:',
                                   self.trancate_string(journal.supplier.code + ' ' + journal.supplier.name if journal.supplier and journal.supplier.name else '', 55)])

                item_table = Table(table_data, colWidths=[50, 40, 360, 50, 310])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                                                ('ALIGN', (4, 0), (4, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (0, -1), (5, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                # 800
                COMMON_COLUMN = [90, 70, 50, 50, 110, 110, 70, 70, 70, 60, 50, 10]
                table_data = []
                # row 2 of entry
                document_type_dict = dict(DOCUMENT_TYPES)
                table_data.append(['Document Number:', journal.document_number, '', '', 'Document Type:',
                                   document_type_dict.get(journal.document_type) if journal.document_type else '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                # row 2 of entry
                perd_month = str(journal.perd_month) if journal.perd_month > 9 else '0' + str(journal.perd_month)
                year_period = str(journal.perd_year) + ' - ' + perd_month
                table_data.append(['', '', '', '', 'Document Date:', journal.document_date.strftime('%d/%m/%Y'),
                                   'Posting Date:', journal.posting_date.strftime('%d/%m/%Y'), 'Year - Period:', year_period, '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('ALIGN', (8, 0), (11, 0), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                # row 3 of entry
                tax_group = journal.tax.tax_group.code if journal.tax else ''
                for trx in trx_list:
                    if trx.tax:
                        tax_group = trx.tax.tax_group.code
                table_data.append(['Account Set:', journal.account_set.code if journal.account_set else '', '', '', '', '',
                                   'Tax Group:' if tax_group != '' else '', tax_group if tax_group != '' else '', '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('ALIGN', (9, 0), (9, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                # if batch.currency != journal.currency:
                table_data = []
                # row 4 of entry
                # rate_date = trx_list[0].rate_date if trx_list else ''
                if len(str(journal.document_date.month)) == 1:
                    rate_date = '01/0' + \
                        str(journal.document_date.month) + \
                        '/' + str(journal.document_date.year)
                else:
                    rate_date = '01/' + \
                        str(journal.document_date.month) + \
                        '/' + str(journal.document_date.year)
                rate_type = 'SR'
                if rate_date != '':
                    rdate = rate_date.split('/')[::-1]
                    rdate = ('-').join(rdate)
                    revaluation_logs = RevaluationLogs.objects.filter(journal_type=journal.journal_type, currency=journal.currency,
                                                                      company_id=company_id, rate_date=rdate).order_by('id')
                    if revaluation_logs:
                        rate_type = revaluation_logs[0].rate_type if revaluation_logs else ''
                        rate_date = rate_date.strftime('%d/%m/%Y')
                table_data.append(['Currency:', journal.currency.code if journal.currency else '', 'Rate Type:', rate_type,
                                    'Rate Date:', rate_date, 'Exchange Rate:', str(journal.exchange_rate), '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                # row 5 of entry

                inv_name = ''
                if trx_list:
                    trx = trx_list[0]
                    inv_name = trx.related_invoice.document_number if trx.related_invoice else ''

                if inv_name != '':
                    table_data.append(['Apply To Doc:', inv_name, '', '', 'Apply To Exchange Rate:', str(journal.orig_exch_rate), '', '', '', '', '', ''])
                else:
                    table_data.append(['Terms:', journal.supplier.term_days + 'DAYS', 'Due Date:', journal.due_date.strftime('%d/%m/%Y'),
                                       '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                # row 5 of entry
                table_data.append([])
                table_data.append(['Distribution Code', '', 'G/L Account', '', 'Account Description', '',
                                   'Detail Description/Tax Authority', '', 'Net Dist. Amt', '', 'Allocated Tax'])

                COMMON_COLUMN_TRX = [90, 3, 77, 3, 210, 3, 210, 3, 105, 3, 105]
                item_table = Table(table_data, colWidths=COMMON_COLUMN_TRX)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                                                ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                                                ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                                ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                                ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                                ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                                                ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                                ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                                ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                for trx in trx_list:
                    table_data = []
                    # row 5 of entry

                    base_tax_amount = intcomma('%.2f' % round_number(trx.base_tax_amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.base_tax_amount, 0))
                    if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                        if float(str(base_tax_amount).replace(',', '')) > 0:
                            base_tax_amount = '-' + base_tax_amount
                    table_data.append([trx.distribution_code, '', trx.account.code if trx.account else '', '',
                                       self.trancate_string(trx.account.name, 34) if trx.account else '', '',
                                       self.trancate_string(trx.description if trx.description else '', 34), '', base_tax_amount, '', ''])

                    tax_amount = intcomma('%.2f' % round_number(trx.tax_amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.tax_amount, 0))

                    if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                        if float(str(tax_amount).replace(',', '')) > 0:
                            tax_amount = '-' + tax_amount

                    table_data.append(['', '', '', '', '', '', Paragraph(trx.tax.tax_group.code if trx.tax else '', styles['RightAlign']), '',
                                       tax_amount, '', ''])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN_TRX)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                    ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                                                    ('ALIGN', (8, 0), (8, -1), 'RIGHT'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ]))
                    elements.append(item_table)

                table_data = []
                # row 7 of entry
                total_amount__sum = trx_list.aggregate(Sum('total_amount'))['total_amount__sum']
                batch_total_amount__sum += float(round_number(total_amount__sum))
                total_amount__sum = intcomma('%.2f' % round_number(total_amount__sum)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(total_amount__sum, 0))
                if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                    if float(str(total_amount__sum).replace(',', '')) > 0:
                        total_amount__sum = '-' + total_amount__sum
                table_data.append(['', '', '', '', '', '', 'Total:', '', total_amount__sum, '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_TRX)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

            # --  Batch Summary By Currency --
            table_data = []
            table_data.append([])
            table_data.append(['-- Batch Summary By Currency --'])
            item_table = Table(table_data, colWidths=[800])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append([])
            table_data.append(['Currency', '', 'Description', '', 'Documents', '', '', ''])

            COMMON_COLUMN_3 = [70, 3, 200, 3, 150, 3, 100, 271]
            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('FONT', (0, 0), (6, -1), s.REPORT_FONT_BOLD),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                            ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                            ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            list_currency = journal_list.values('currency__code').order_by('currency__code').annotate(count=Count('currency__code'))

            for cur in list_currency:
                journal = journal_list.filter(currency__code=cur['currency__code']).first()
                total_credit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Credit Note']
                                                        ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                total_credit_note = float(round_number(total_credit_note)) if total_credit_note != None else 0

                total_debit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Debit Note']
                                                       ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                total_debit_note = float(round_number(total_debit_note)) if total_debit_note != None else 0

                batch_total_amount__sum = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Invoice']
                                                              ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                batch_total_amount__sum = float(round_number(batch_total_amount__sum)) if batch_total_amount__sum != None else 0
                journal_amount = batch_total_amount__sum - total_credit_note + total_debit_note

                total_credit_note = total_credit_note * -1 if total_credit_note > 0 else total_credit_note
                batch_total_amount__sum = self.format_decimal(journal.currency.is_decimal, batch_total_amount__sum)
                total_credit_note = self.format_decimal(journal.currency.is_decimal, total_credit_note)
                total_debit_note = self.format_decimal(journal.currency.is_decimal, total_debit_note)
                journal_amount = self.format_decimal(journal.currency.is_decimal, journal_amount)

                table_data = []
                table_data.append([cur['currency__code'], '', journal.currency.name, '', 'Total Invoice', '', batch_total_amount__sum, ''])
                table_data.append(['', '', '', '', 'Total Credit Notes', '', total_credit_note, ''])
                table_data.append(['', '', '', '', 'Total Debit Notes', '', total_debit_note, ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
                                                ('TOPPADDING', (0, 0), (-1, -1), -1),
                                                ('TOPPADDING', (0, 0), (-1, 0), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                table_data.append(['', '', '', '', 'Total for batch ' + batch.batch_no, '', journal_amount, ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
                                                ('TOPPADDING', (0, 0), (-1, -1), -1),
                                                ('TOPPADDING', (0, 0), (-1, 0), 0),
                                                ('LINEBELOW', (6, 0), (6, 0), 0.25, colors.black),
                                                ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black)
                                                ]))
                elements.append(item_table)

            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

        table_data = []
        table_data.append([str(count_entry) + ' entries printed'])
        table_data.append([str(len(batch_list)) + ' batches printed'])

        item_table = Table(table_data, colWidths=[800])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ]))
            elements.append(table_body)

        doc.build(elements, onFirstPage=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  onLaterPages=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def print_report_ap_payment(self, company_id, batch_type, batch_from, batch_to, entry_from, entry_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))

        if int(batch_from) > int(batch_to):
            batch_to = batch_from

        batch_list = Batch.objects.filter(is_hidden=0, status__in=[STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted']],
                                          company_id=company_id, batch_type=int(batch_type), id__gte=batch_from, id__lte=batch_to).order_by('id')

        elements = []
        table_data = []
        table_data.append(['From Batch Number:', '[' + str(batch_list.first().batch_no) + '] to [' + str(batch_list.last().batch_no) + ']'])

        table_data.append(['From Batch Date:', '[' + batch_list.first().batch_date.strftime('%d/%m/%Y') + '] to ['
                           + batch_list.last().batch_date.strftime('%d/%m/%Y') + ']'])

        table_data.append(['Status ', '[Open, Posted]'])
        table_data.append(['Show Tax Details', '[Yes]'])
        table_data.append(['Show Comments', '[Yes]'])
        table_data.append([])

        item_table = Table(table_data, colWidths=[150, 660])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)
        count_entry = 0
        for batch in batch_list:
            journal_list = Journal.objects.filter(batch__id=batch.id, is_hidden=0, company_id=company_id) \
                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']).exclude(is_auto_reversed_entry=True) \
                .exclude(status=int(STATUS_TYPE_DICT['Auto Reverse Entry'])).exclude(reference='REVERSING ENTRY').select_related('batch')

            if entry_from != 'null' and int(entry_from):
                entry_from = int(entry_from)
                journal_list = journal_list.filter(id__gte=entry_from)
            if entry_to != 'null' and  int(entry_to):
                entry_to = int(entry_to)
                journal_list = journal_list.filter(id__lte=entry_to)

            count_entry += len(journal_list)
            journal_list_sort = sorted(journal_list, key=lambda Journal: int(Journal.code))

            table_data = []
            batch_amount__sum = journal_list.aggregate(Sum('total_amount'))['total_amount__sum']
            batch_amount__sum = self.format_decimal(batch.currency.is_decimal, batch_amount__sum)
            # total_amount = intcomma('%.2f' % round_number(batch.batch_amount)) \
            #     if batch.currency.is_decimal else intcomma('%.0f' % round_number(batch.batch_amount, 0))

            table_data.append(['Batch No:', batch.batch_no, '', 'Description:', batch.description, '', 'Currency:',
                               batch.currency.code, '', Paragraph('Total amount:', styles['RightAlign']),
                               Paragraph(batch_amount__sum, styles['RightAlign'])])

            table_data.append(['Batch Date:', batch.batch_date.strftime('%d/%m/%Y'), '', 'Type:', document_type(journal_list), '',
                               'Source Application:', batch.source_ledger, '', Paragraph('No. of Entries:', styles['RightAlign']),
                               Paragraph(str(batch.no_entries), styles['RightAlign'])
                               ])

            bank_name = ''
            for journal in journal_list:
                bank_name = journal.bank.code if journal.bank else bank_name
            table_data.append(['Last Edited:', batch.update_date.strftime('%d/%m/%Y'), '', 'Status:', STATUS_TYPE[batch.status - 1][1], '',
                               'Bank:', bank_name, '', ''])

            item_table = Table(table_data, colWidths=[70, 50, 20, 70, 260, 10, 100, 70, 10, 70, 80])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                 ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ]))

            elements.append(item_table)

            batch_total_amount__sum = 0
            batch_invoice_amount__sum = 0
            batch_total_discount_amount = 0
            batch_currency_list = []
            for journal in journal_list_sort:
                i = 0
                index = -1
                currency_code = journal.currency.code
                currency_name = journal.currency.name
                currency_decimal = journal.currency.is_decimal
                if journal.supplier and journal.currency == journal.supplier.currency:
                    currency_code = journal.currency.code
                    currency_decimal = journal.currency.is_decimal
                    currency_name = journal.currency.name
                elif journal.supplier:
                    currency_code = journal.supplier.currency.code
                    currency_decimal = journal.supplier.currency.is_decimal
                    currency_name = journal.supplier.currency.name
                for curren in batch_currency_list:
                    if curren[0] == currency_code:
                        index = i
                        break;
                    i += 1
                if index > -1:
                    if journal.transaction_type == '2':
                        batch_currency_list[index][1] += journal.total_amount
                        batch_currency_list[index][4] += journal.original_amount
                        batch_currency_list[index][5] += journal.total_amount
                    else:
                        batch_currency_list[index][1] += 0
                        batch_currency_list[index][4] += journal.original_amount
                        batch_currency_list[index][5] += journal.total_amount
                else:
                    if journal.transaction_type == '2':
                        batch_currency_list.append([
                            currency_code, journal.total_amount, 0, 0, journal.original_amount, journal.total_amount, currency_decimal, currency_name])
                    else:
                        batch_currency_list.append([
                            currency_code, 0, 0, 0, journal.original_amount, journal.total_amount, currency_decimal, currency_name])
                batch_total_amount__sum += journal.total_amount
                trx_list = Transaction.objects.filter(is_hidden=0, company_id=company_id,
                                                      journal__id=journal.id).order_by('id')
                table_data = []
                # row 1 of entry
                table_data.append([])
                table_data.append(['Entry No.:', journal.code, '', journal.name, '', 'Document No.:', journal.document_number, '',
                                   Paragraph('Payment Amt. (' + journal.currency.code + '):', styles['RightAlignBold']),
                                   Paragraph(self.format_decimal(journal.currency.is_decimal, journal.total_amount), styles['RightAlign'])])

                item_table = Table(table_data, colWidths=[50, 30, 5, 270, 5, 90, 170, 5, 105, 80])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('LINEBELOW', (0, -1), (11, -1), 0.25, colors.black),
                     ]))
                elements.append(item_table)

                # 800
                COMMON_COLUMN = [85, 80, 5, 90, 95, 90, 90, 90, 5, 100, 80]
                # row 2 of entry
                table_data = []
                transaction_type_dict = dict(PAYMENT_TRANSACTION_TYPES)
                perd_month = str(journal.perd_month) if journal.perd_month > 9 else '0' + str(journal.perd_month)
                year_period = str(journal.perd_year) + ' - ' + perd_month
                table_data.append(['Transaction Type:', transaction_type_dict.get(journal.transaction_type), '',
                                   'Payment Date:', journal.document_date.strftime('%d/%m/%Y'), 'Posting Date:', journal.posting_date.strftime('%d/%m/%Y'),
                                   Paragraph('Year - Period:', styles['RightAlign']), '',  year_period])

                if journal.account_set_id:
                    supplier_currency = journal.supplier.currency
                    table_data.append(['Vendor:', self.trancate_string(journal.supplier.code, 14) if journal.supplier else '***Misc.***', '',
                                       self.trancate_string(journal.supplier.name if journal.supplier and journal.supplier.name else journal.name, 30),
                                       '', 'Account Set:', journal.account_set.code, '', '',
                                       Paragraph('Vendor Amt. (' + supplier_currency.code + '):', styles['RightAlign']),
                                       Paragraph(self.format_decimal(supplier_currency.is_decimal, journal.original_amount), styles['RightAlign'])])

                else:
                    table_data.append(['Vendor:', self.trancate_string(journal.supplier.code, 14) if journal.supplier else '***Misc.***', '',
                                       self.trancate_string(journal.supplier.name if journal.supplier and journal.supplier.name else journal.name,
                                                            30), '', '', '', '', ''])
                    tax_group = ''
                    for trx in trx_list:
                        if trx.tax:
                            tax_group = trx.tax.tax_group.code
                    if tax_group != '':
                        table_data.append(['Invoice Number:', journal.invoice_number, '', '', '', 'Tax Group:', tax_group, '', '',
                                           Paragraph('Total Tax Amt. (' + journal.currency.code + '):', styles['RightAlign']) if journal.tax_amount > 0 else '',
                                           Paragraph(self.format_decimal(journal.currency.is_decimal, journal.tax_amount),
                                                     styles['RightAlign']) if journal.tax_amount > 0 else ''])
                    else:
                        table_data.append(['Invoice Number:', journal.invoice_number, '', '', '', '', '', '', '',
                                           Paragraph('Total Tax Amt. (' + journal.currency.code + '):', styles['RightAlign']) if journal.tax_amount > 0 else '',
                                           Paragraph(self.format_decimal(journal.currency.is_decimal, journal.tax_amount),
                                                     styles['RightAlign']) if journal.tax_amount > 0 else ''])

                table_data.append(['Reference:', journal.reference, '', '', '', '', '', '', ''])

                if journal.supplier:
                    exchange_list = ExchangeRate.objects.filter(exchange_date__year=journal.document_date.year, exchange_date__month=journal.document_date.month,
                                                                company_id=journal.company_id, from_currency=journal.supplier.currency,
                                                                to_currency=batch.company.currency)

                    exc_rate = exchange_list[0].rate if exchange_list else 0
                    exc_rate_date = exchange_list[0].exchange_date.strftime('%d/%m/%Y') if exchange_list else ''

                    if journal.orig_exch_rate:
                        exc_rate = journal.orig_exch_rate
                    if journal.supplier.currency != batch.currency:
                        table_data.append(['Vendor Currency:', journal.supplier.currency.code, '', 'Vendor Rate Type:', 'SR', '',
                                           'Vendor Rate Date:', exc_rate_date, '', Paragraph('Vendor Rate:', styles['RightAlign']),
                                           Paragraph(str(exc_rate), styles['RightAlign'])])

                payment_type_dict = dict(PAYMENT_TYPE)
                table_data.append(['Bank Currency:', journal.bank.currency.code if journal.bank else '', '', 'Bank Rate Type:','SR', 
                                   'Bank Rate Date:', '1/' + str(journal.document_date.month) + '/' + str(journal.document_date.year), '', 
                                   '', 'Bank Rate:', journal.exchange_rate])
                
                print_check_no = True
                try:
                    if int(journal.payment_check_number) == 0:
                        print_check_no = False
                except Exception as e:
                    print(e)
                table_data.append(['Payment Code:', journal.payment_code.code if journal.payment_code else '', '', 'Payment Type:',
                                   payment_type_dict.get(journal.payment_code.payment_type) if journal.payment_code else '', 
                                   'Check No.:', journal.payment_check_number if print_check_no else '', '', '', '', ''])

                table_data.append([])
                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                     ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                     ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                     ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                     ('SPAN', (3, 1), (4, 1)),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ]))
                elements.append(item_table)

                # '2' -> 'Misc Payment'
                if journal.transaction_type == '2':
                    batch_invoice_amount__sum += journal.total_amount
                    table_data = []
                    # row 5 of entry
                    table_data.append(['', 'Dist. Code', '', 'G/L Account/ Reference', '', 'Account Description/ Detail Description', '',
                                       'Tax Authority', '', 'Net Dist. Amt', '', 'Allocated Tax'])

                    COMMON_COLUMN_2 = [20, 100, 3, 158, 3, 245, 3, 112, 3, 80, 3, 80]
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

                    for trx in trx_list:
                        table_data = []
                        amount = self.format_decimal(trx.currency.is_decimal, trx.base_tax_amount)
                        tax_amount = intcomma('%.2f' % round_number(trx.tax_amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.tax_amount, 0))

                        table_data.append(['', trx.distribution_code, '', trx.account.code if trx.account else '', '',
                                           trx.account.name if trx.account else '', '', '', '', amount, '', ''])

                        if trx.tax_amount != 0:
                            table_data.append(['', '', '', '', '', trx.description, '', trx.tax.tax_group.code if trx.tax else '', '', tax_amount])
                        elif trx.description != '':
                            table_data.append(['', '', '', '', '', trx.description, '', '', '', ''])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                             ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                             ('TOPPADDING', (0, 0), (-1, -1), 0),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ]))
                        elements.append(item_table)

                    table_data = []
                    # row 7 of entry
                    total_amount__sum = journal.total_amount
                    total_amount__sum = intcomma(
                        '%.2f' % round_number(total_amount__sum)) if journal.currency.is_decimal else intcomma(
                        '%.0f' % round_number(total_amount__sum, 0))
                    table_data.append(['', '', '', '', '', '', '', 'Total (' + journal.currency.code + '):', '', total_amount__sum, '', ''])
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEABOVE', (9, -1), (9, -1), 0.25, colors.black)
                                                    ]))
                    elements.append(item_table)
                else:
                    table_data = []
                    # row 5 of entry
                    table_data.append(['', 'Document No.:', '', 'Sched. No.', '', 'Adj. No.', '', 'Adj. Reference', '',
                                       'Adj. Description', '', 'Adjustment', '', 'Discount', '', 'Amount'])

                    COMMON_COLUMN_2 = [20, 100, 3, 90, 3, 119, 3, 110, 3, 110, 3, 80, 3, 80, 3, 80]
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (13, -1), (13, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (15, -1), (15, -1), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

                    total_amount__sum = 0
                    for trx in trx_list:
                        i = 0
                        index = -1
                        currency_code = journal.currency.code
                        currency_name = journal.currency.name
                        currency_decimal = journal.currency.is_decimal
                        if journal.supplier and journal.currency == journal.supplier.currency:
                            currency_code = journal.currency.code
                            currency_decimal = journal.currency.is_decimal
                            currency_name = journal.currency.name
                        elif journal.supplier:
                            currency_code = journal.supplier.currency.code
                            currency_decimal = journal.supplier.currency.is_decimal
                            currency_name = journal.supplier.currency.name
                        for curren in batch_currency_list:
                            if curren[0] == currency_code:
                                index = i
                                break
                            i += 1
                        if index > -1:
                            if journal.transaction_type == '2':
                                batch_currency_list[index][2] += trx.adjustment_amount
                                batch_currency_list[index][3] += trx.discount_amount
                            else:
                                batch_currency_list[index][2] += trx.adjustment_amount
                                batch_currency_list[index][3] += trx.discount_amount


                        table_data = []
                        # row 5 of entry

                        adjustment_amount = self.format_decimal(trx.currency.is_decimal, trx.adjustment_amount)
                        if trx.discount_amount != 0:
                            batch_total_discount_amount += trx.discount_amount
                        discount_amount = self.format_decimal(trx.currency.is_decimal, trx.discount_amount)
                        amount = trx.total_amount
                        if trx.related_invoice.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount__sum -= amount
                            amount = (-1) * amount
                        else:
                            total_amount__sum += amount
                        amount = self.format_decimal(trx.currency.is_decimal, amount)

                        table_data.append(['', trx.related_invoice.document_number if trx.related_invoice else '', '',
                                           '', '', '', '', '', '', '', '', adjustment_amount, '', discount_amount, '', amount])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                        ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ]))
                        elements.append(item_table)

                    table_data = []
                    # row 7 of entry
                    # total_amount__sum = trx_list.aggregate(Sum('total_amount'))['total_amount__sum']
                    total_amount__sum = self.format_decimal(trx.currency.is_decimal, total_amount__sum)

                    adjustment_amount__sum = trx_list.aggregate(Sum('adjustment_amount'))['adjustment_amount__sum']
                    adjustment_amount__sum = self.format_decimal(trx.currency.is_decimal, adjustment_amount__sum)

                    discount_amount__sum = trx_list.aggregate(Sum('discount_amount'))['discount_amount__sum']
                    discount_amount__sum = self.format_decimal(trx.currency.is_decimal, discount_amount__sum)

                    table_data.append(['', '', '', '', '', '', '', '', '', 'Total (' + trx.currency.code + '):', '', adjustment_amount__sum,
                                       '', discount_amount__sum, '', total_amount__sum])
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEABOVE', (11, 0), (11, 0), 0.25, colors.black),
                                                    ('LINEABOVE', (13, 0), (13, 0), 0.25, colors.black),
                                                    ('LINEABOVE', (15, 0), (15, 0), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

            # --  Batch Summary By Currency --
            table_data = []
            table_data.append([])
            table_data.append(['-- Batch Summary --'])
            item_table = Table(table_data, colWidths=[800])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                 ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ]))
            elements.append(item_table)

            table_data = []
            table_data.append([])
            table_data.append(['Currency', '', 'Description', '', 'Invoice', '', 'Adjustment', '',
                               'Discount', '', 'Payment', '', 'Advance Credit', '', 'Bank Amount', ''])

            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('ALIGN', (4, -1), (15, -1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONT', (0, 0), (15, -1), s.REPORT_FONT_BOLD),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                            ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                            ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                            ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                                            ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                            ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                            ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                                            ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
                                            ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            list_currency = journal_list.values('original_currency__code').order_by('original_currency__code').annotate(
                count=Count('original_currency__code'))

            is_exist_original_currency = False
            # for cur in list_currency:
            #     if cur['count'] > 0:
            #         is_exist_original_currency = True
            #         currency = Currency.objects.get(code=cur['original_currency__code'])

            #         table_data = []

            #         total_credit_note = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'],
            #                     document_type=DOCUMENT_TYPE_DICT['Credit Note'])\
            #             .aggregate(Sum('total_amount')).get('total_amount__sum', 0)
            #         total_credit_note = float(round_number(total_credit_note)) if total_credit_note != None else 0

            #         total_debit_note = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'],
            #                     document_type=DOCUMENT_TYPE_DICT['Debit Note'])\
            #             .aggregate(Sum('total_amount')).get('total_amount__sum', 0)
            #         total_debit_note = float(round_number(total_debit_note)) if total_debit_note != None else 0

            #         batch_total_amount__sum -= total_credit_note

            #         total_credit_note = intcomma(
            #             "%.2f" % total_credit_note) if currency.is_decimal else intcomma(
            #             "%.0f" % total_credit_note)

            #         adjustment_amount = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'])\
            #             .aggregate(Sum('adjustment_amount')).get('adjustment_amount__sum', 0)
            #         adjustment_amount = adjustment_amount if adjustment_amount != None else 0
            #         adjustment_amount = self.format_decimal(currency.is_decimal, adjustment_amount)

            #         discount_amount = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'])\
            #             .aggregate(Sum('discount_amount')).get('discount_amount__sum', 0)
            #         discount_amount = discount_amount if discount_amount != None else 0
            #         discount_amount = self.format_decimal(currency.is_decimal, discount_amount)

            #         invoice__sum = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'], invoice_number__isnull=False)\
            #             .aggregate(Sum('total_amount')).get('total_amount__sum', 0)
            #         invoice__sum = self.format_decimal(currency.is_decimal, invoice__sum)

            #         original_amount__sum = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'])\
            #             .aggregate(Sum('original_amount')).get('original_amount__sum', 0)
            #         original_amount__sum = self.format_decimal(currency.is_decimal, original_amount__sum)

            #         total_amount__sum = journal_list\
            #             .filter(original_currency__code=cur['original_currency__code'])\
            #             .aggregate(Sum('total_amount')).get('total_amount__sum', 0)
            #         total_amount__sum = self.format_decimal(batch.currency.is_decimal, total_amount__sum)

            #         table_data.append([currency.code, '', currency.name, '', invoice__sum, '', adjustment_amount, '',
            #                            discount_amount, '', original_amount__sum, '', total_credit_note, '', total_amount__sum, '', ])

            #         item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            #         item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
            #                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
            #                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
            #                                         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            #                                         ('ALIGN', (4, -1), (15, -1), 'RIGHT'),
            #                                         ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            #                                         ('FONT', (0, 0), (15, -1), s.REPORT_FONT),
            #                                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
            #                                         ('TOPPADDING', (0, 0), (-1, -1), 0),
            #                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            #                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
            #                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            #                                         ]))
            #         elements.append(item_table)

            if not is_exist_original_currency:
                list_currency = journal_list.values('currency__code').order_by('currency__code').annotate(count=Count('currency__code'))

                for cur in list_currency:
                    if cur['count'] > 0:
                        currency = Currency.objects.get(code=cur['currency__code'])
                        for currenc in batch_currency_list:
                            table_data = []

                            # total_credit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Credit Note']
                            #                                         ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                            # total_credit_note = float(round_number(total_credit_note)) if total_credit_note != None else 0

                            # total_debit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Debit Note']
                            #                                        ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                            # total_debit_note = float(round_number(total_debit_note)) if total_debit_note != None else 0

                            # batch_total_amount__sum -= total_credit_note

                            # total_credit_note = intcomma(
                            #     "%.2f" % total_credit_note) if currency.is_decimal else intcomma(
                            #     "%.0f" % total_credit_note)

                            # adjustment_amount = journal_list.filter(currency__code=cur['currency__code']) \
                            #     .aggregate(Sum('adjustment_amount')).get('adjustment_amount__sum', 0)
                            # adjustment_amount = adjustment_amount if adjustment_amount != None else 0
                            # adjustment_amount = self.format_decimal(currency.is_decimal, adjustment_amount)
                            adjustment_amount = self.format_decimal(currenc[6], currenc[2])

                            # discount_amount = journal_list.filter(currency__code=cur['currency__code']) \
                            #     .aggregate(Sum('discount_amount')).get('discount_amount__sum', 0)
                            # discount_amount = batch_total_discount_amount
                            # discount_amount = discount_amount if discount_amount != None else 0
                            # discount_amount = self.format_decimal(currency.is_decimal, discount_amount)
                            discount_amount = self.format_decimal(currenc[6], currenc[3])

                            # invoice__sum = journal_list.filter(currency__code=cur['currency__code'], invoice_number__isnull=False
                            #                                    ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                            # invoice__sum = self.format_decimal(currency.is_decimal, invoice__sum)
                            # invoice__sum = self.format_decimal(currency.is_decimal, batch_invoice_amount__sum)
                            invoice__sum = self.format_decimal(currenc[6], currenc[1])

                            # original_amount__sum = journal_list.filter(currency__code=cur['currency__code']
                            #                                            ).aggregate(Sum('original_amount')).get('original_amount__sum', 0)
                            # original_amount__sum = self.format_decimal(currency.is_decimal, original_amount__sum)
                            # original_amount__sum = self.format_decimal(currenc.is_decimal, batch_total_amount__sum)
                            original_amount__sum = self.format_decimal(currenc[6], currenc[4])
                            total_credit_note = self.format_decimal(currenc[6], 0)

                            # total_amount__sum = journal_list.filter(currency__code=cur['currency__code']
                            #                                         ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
                            # total_amount__sum = self.format_decimal(batch.currency.is_decimal, total_amount__sum)
                            # total_amount__sum = self.format_decimal(currency.is_decimal, batch_total_amount__sum)
                            total_amount__sum = self.format_decimal(currency.is_decimal, currenc[5])

                            table_data.append([currenc[0], '', currenc[7], '', invoice__sum, '',
                                            adjustment_amount, '', discount_amount, '', original_amount__sum, '',
                                            total_credit_note, '', total_amount__sum, '', ])

                            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                            ('ALIGN', (4, -1), (15, -1), 'RIGHT'),
                                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                            ('FONT', (0, 0), (15, -1), s.REPORT_FONT),
                                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                            ]))
                            elements.append(item_table)

            table_data = []
            original_amount__sum = self.format_decimal(currency.is_decimal, batch_total_amount__sum)
            table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', 'Total for batch ' + batch.batch_no + ':', '',
                               original_amount__sum, ''])

            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('ALIGN', (6, -1), (15, -1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEABOVE', (14, -1), (14, -1), 0.25, colors.black),
                                            ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

        table_data = []
        table_data.append([str(count_entry) + ' entries printed'])
        table_data.append([str(len(batch_list)) + ' batches printed'])
        item_table = Table(table_data, colWidths=[800])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  onLaterPages=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def print_report_ar_invoice(self, company_id, batch_type, batch_from, batch_to, entry_from, entry_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))

        if int(batch_from) > int(batch_to):
            batch_to = batch_from

        batch_list = Batch.objects.filter(is_hidden=0, status__in=[STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted'], STATUS_TYPE_DICT['Prov. Posted']],
                                          company_id=company_id, batch_type=int(batch_type), id__gte=batch_from, id__lte=batch_to).order_by('id')

        elements = []
        table_data = []
        table_data.append(['From Batch Number:', '[' + str(batch_list.first().batch_no) + '] to [' + str(batch_list.last().batch_no) + ']'])
        table_data.append(['From Batch Date:', '[' + batch_list.first().batch_date.strftime('%d/%m/%Y') +
                           '] to [' + batch_list.last().batch_date.strftime('%d/%m/%Y') + ']'])
        table_data.append(['Status ', '[Open, Posted]'])
        table_data.append(['Reprint Previously Printed batches', '[Yes]'])
        table_data.append(['Show Schedules', '[Yes]'])
        table_data.append(['Show Tax Details', '[Yes]'])
        table_data.append(['Show Comments', '[Yes]'])
        table_data.append([])
        item_table = Table(table_data, colWidths=[150, 660])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))

        elements.append(item_table)
        count_entry = 0
        for batch in batch_list:
            journal_list = Journal.objects.filter(batch__id=batch.id, is_hidden=0, company_id=company_id) \
                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']).exclude(is_auto_reversed_entry=True) \
                .exclude(status=int(STATUS_TYPE_DICT['Auto Reverse Entry'])).exclude(reference='REVERSING ENTRY') \
                .select_related('batch')

            if entry_from != 'null' and int(entry_from):
                entry_from = int(entry_from)
                journal_list = journal_list.filter(id__gte=entry_from)
            if entry_to != 'null' and  int(entry_to):
                entry_to = int(entry_to)
                journal_list = journal_list.filter(id__lte=entry_to)

            count_entry += len(journal_list)
            journal_list_sort = sorted(journal_list, key=lambda Journal: int(Journal.code))
            table_data = []

            total_amount = intcomma('%.2f' % round_number(batch.batch_amount)) if batch.currency.is_decimal else intcomma('%.0f' % round_number(batch.batch_amount, 0))

            manual_doc = document_type(journal_list)

            table_data.append(['Batch No:', batch.batch_no, 'Description:', batch.description, '', '', 'Total amount:', total_amount, ''])

            table_data.append(['Batch Date:', batch.batch_date.strftime('%d/%m/%Y'), 'Type:', manual_doc,
                               'Source Application:', batch.source_ledger, 'No. of Entries:', batch.no_entries, ''])

            table_data.append(['Last Edited:', batch.update_date.strftime('%d/%m/%Y'), 'Status:', STATUS_TYPE[batch.status - 1][1], '', '', '', ''])

            item_table = Table(table_data, colWidths=[100, 100, 100, 100, 100, 100, 100, 60, 50])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('ALIGN', (7, 0), (7, 1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))

            elements.append(item_table)

            batch_total_amount__sum = 0
            for journal in journal_list_sort:
                table_data = []
                # row 1 of entry
                table_data.append([])
                table_data.append(['Entry No.:', journal.code, journal.name, 'Customer', journal.customer.name if journal.customer else ''])

                item_table = Table(table_data, colWidths=[50, 40, 360, 100, 250])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                                                ('ALIGN', (4, 0), (4, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (0, -1), (5, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                # 800
                COMMON_COLUMN = [90, 70, 50, 50, 110, 110, 70, 70, 70, 110]
                table_data = []
                # row 2 of entry
                document_type_dict = dict(DOCUMENT_TYPES)
                table_data.append(['Document Number:', journal.document_number, '', '', 'Document Type:',
                                   document_type_dict.get(journal.document_type) if journal.document_type else '', '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                # row 2 of entry
                perd_month = str(journal.perd_month) if journal.perd_month > 9 else '0' + str(journal.perd_month)
                year_period = str(journal.perd_year) + ' - ' + perd_month
                table_data.append(['', '', '', '', 'Document Date:', journal.document_date.strftime('%d/%m/%Y'),
                                   'Posting Date:', journal.posting_date.strftime('%d/%m/%Y'), 'Year - Period:', year_period])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                # row 3 of entry
                table_data.append(['Account Set:', journal.account_set.code if journal.account_set else '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                trx_list = Transaction.objects.filter(is_hidden=0, company_id=company_id, journal__id=journal.id).order_by('id')

                table_data = []
                # row 5 of entry

                inv_name = ''
                if trx_list:
                    trx = trx_list[0]
                    inv_name = trx.related_invoice.document_number if trx.related_invoice else ''

                if inv_name != '':
                    table_data.append(['Apply To Doc:', inv_name, '', '', 'Apply To Exchange Rate:', str(journal.orig_exch_rate), '', '', '', ''])
                else:
                    table_data.append(['Terms:', journal.customer.payment_term + 'DAYS', 'Due Date:', journal.due_date.strftime('%d/%m/%Y'),
                                       '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                table_data.append([''])
                # row 5 of entry
                table_data.append(['Dist. Code', '', 'G/L Account/ Description', '', 'Detail Description', '', 'Tax Authority', '', 'Tax Base', '', 'Amount'])

                COMMON_COLUMN_2 = [70, 3, 257, 3, 214, 3, 86, 3, 80, 3, 80]
                item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                                                ('ALIGN', (8, 0), (10, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                                ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                                ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                                ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                                                ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                                ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                                ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                for trx in trx_list:
                    table_data = []
                    # row 5 of entry

                    total_amount = intcomma('%.2f' % round_number(trx.amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.amount, 0))
                    if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                        if float(str(total_amount).replace(',', '')) > 0:
                            total_amount = '-' + total_amount

                    table_data.append([trx.distribution_code, '', trx.account.code if trx.account else '', '',
                                       self.trancate_string(trx.description if trx.description else '', 31), '', '', '', '', '', total_amount])

                    table_data.append(['', '', self.trancate_string(trx.account.name if trx.account else '', 30), '', '', '', '', '', '', '', ''])

                    tax_amount = intcomma('%.2f' % round_number(trx.tax_amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.tax_amount, 0))

                    base_tax_amount = intcomma('%.2f' % round_number(trx.base_tax_amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.base_tax_amount, 0))
                    if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                        if float(str(base_tax_amount).replace(',', '')) > 0:
                            base_tax_amount = '-' + base_tax_amount
                        if float(str(tax_amount).replace(',', '')) > 0:
                            tax_amount = '-' + tax_amount

                    table_data.append(['', '', '', '', '', '', trx.tax.tax_group.code if trx.tax else '', '', base_tax_amount, '', tax_amount])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (8, 0), (10, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ]))
                    elements.append(item_table)

                table_data = []
                # row 7 of entry
                total_amount__sum = trx_list.aggregate(Sum('total_amount'))['total_amount__sum']
                total_amount__sum = float(round_number(total_amount__sum)) if total_amount__sum else 0
                batch_total_amount__sum += total_amount__sum
                total_amount__sum = intcomma('%.2f' % total_amount__sum) if trx.currency.is_decimal else intcomma('%.0f' % total_amount__sum)
                if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                    if float(str(total_amount__sum).replace(',', '')) > 0:
                        total_amount__sum = '-' + total_amount__sum
                table_data.append(['', '', '', '', '', '', 'Total Invoice:', '', '', '', total_amount__sum])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                table_data = []
                total_taxes__sum = trx_list.aggregate(Sum('tax_amount'))['tax_amount__sum']
                total_taxes__sum = float(round_number(total_taxes__sum)) if total_taxes__sum else 0
                total_taxes__sum = intcomma('%.2f' % total_taxes__sum) if trx.currency.is_decimal else intcomma('%.0f' % total_taxes__sum)
                if int(journal.document_type) == int(DOCUMENT_TYPE_DICT['Credit Note']):
                    if float(str(total_taxes__sum).replace(',', '')) > 0:
                        total_taxes__sum = '-' + total_taxes__sum

                table_data.append(['', '', '', '', '', '', 'Total Taxes:', '', '', '', total_taxes__sum])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

            # --  Batch Summary By Currency --
            table_data = []
            table_data.append([])
            table_data.append(['-- Batch Summary By Currency --'])
            item_table = Table(table_data, colWidths=[800])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append([])
            table_data.append(['Currency', '', 'Description', '', 'Documents', '', '', ''])

            COMMON_COLUMN_3 = [70, 3, 200, 3, 150, 3, 100, 271]
            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONT', (0, 0), (6, -1), s.REPORT_FONT_BOLD),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                            ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                            ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)
            list_currency = journal_list.values('currency__code').order_by('currency__code').annotate(count=Count('currency__code'))

            for cur in list_currency:
                journal = journal_list.filter(currency__code=cur['currency__code']).first()
                total_credit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Credit Note']).aggregate(
                    Sum('total_amount')).get('total_amount__sum', 0)
                total_credit_note = float(round_number(total_credit_note)) if total_credit_note != None else 0

                total_debit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Debit Note']).aggregate(
                    Sum('total_amount')).get('total_amount__sum', 0)
                total_debit_note = float(round_number(total_debit_note)) if total_debit_note != None else 0

                batch_total_amount__sum = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Invoice']
                                                              ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

                batch_total_amount__sum = float(round_number(batch_total_amount__sum)) if batch_total_amount__sum != None else 0
                journal_amount = batch_total_amount__sum - total_credit_note + total_debit_note
                journal_amount = self.format_decimal(journal.currency.is_decimal, journal_amount)

                total_credit_note = total_credit_note * -1 if total_credit_note > 0 else total_credit_note
                batch_total_amount__sum = self.format_decimal(batch.currency.is_decimal, batch_total_amount__sum)
                total_credit_note = self.format_decimal(journal.currency.is_decimal, total_credit_note)
                total_debit_note = self.format_decimal(journal.currency.is_decimal, total_debit_note)

                table_data = []
                table_data.append([cur['currency__code'], '', journal.currency.name, '', 'Total Invoices', '', batch_total_amount__sum, ''])
                table_data.append(['', '', '', '', 'Total Credit Notes', '', total_credit_note, ''])
                table_data.append(['', '', '', '', 'Total Debit Notes', '', total_debit_note, ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                table_data = []
                table_data.append(['', '', '', '', 'Total for batch ' + batch.batch_no, '', journal_amount, ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (6, 0), (6, 0), 0.25, colors.black),
                                                ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black)
                                                ]))
                elements.append(item_table)

            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

        table_data = []
        table_data.append([str(count_entry) + ' entries printed'])
        table_data.append([str(len(batch_list)) + ' batches printed'])
        item_table = Table(table_data, colWidths=[800])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  onLaterPages=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def print_report_ar_receipt(self, company_id, batch_type, batch_from, batch_to, entry_from, entry_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))

        if int(batch_from) > int(batch_to):
            batch_to = batch_from

        batch_list = Batch.objects.filter(is_hidden=0, status__in=[STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted']],
                                          company_id=company_id, batch_type=int(batch_type), id__gte=batch_from, id__lte=batch_to).order_by('id')

        elements = []
        table_data = []
        table_data.append(['From Batch Number:', '[' + str(batch_list.first().batch_no) + '] to [' + str(batch_list.last().batch_no) + ']'])
        table_data.append(['From Batch Date:', '[' + batch_list.first().batch_date.strftime('%d/%m/%Y') + '] to ['
                           + batch_list.last().batch_date.strftime('%d/%m/%Y') + ']'])
        table_data.append(['Status ', '[Open, Posted]'])
        table_data.append(['Reprint Previously Printed batches', '[Yes]'])
        table_data.append(['Show Schedules', '[Yes]'])
        table_data.append(['Show Tax Details', '[Yes]'])
        table_data.append(['Show Comments', '[Yes]'])
        table_data.append([])

        item_table = Table(table_data, colWidths=[150, 660])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))

        elements.append(item_table)
        count_entry = 0
        for batch in batch_list:
            journal_list = Journal.objects.filter(batch__id=batch.id, is_hidden=0, company_id=company_id) \
                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']).exclude(is_auto_reversed_entry=True) \
                .exclude(status=int(STATUS_TYPE_DICT['Auto Reverse Entry'])).exclude(reference='REVERSING ENTRY').select_related('batch')

            if entry_from != 'null' and int(entry_from):
                entry_from = int(entry_from)
                journal_list = journal_list.filter(id__gte=entry_from)
            if entry_to != 'null' and int(entry_to):
                entry_to = int(entry_to)
                journal_list = journal_list.filter(id__lte=entry_to)

            count_entry += len(journal_list)
            journal_list_sort = sorted(journal_list, key=lambda Journal: int(Journal.code))

            table_data = []
            batch_amount__sum = journal_list.aggregate(Sum('total_amount'))['total_amount__sum']
            batch_amount__sum = self.format_decimal(batch.currency.is_decimal, batch_amount__sum)

            # total_amount = intcomma('%.2f' % round_number(batch.batch_amount)) if batch.currency.is_decimal else intcomma('%.0f' % round_number(batch.batch_amount, 0))

            table_data.append(['Batch No:', batch.batch_no, 'Description:', batch.description, '', '', '', '', ''])
            table_data.append(['Batch Date:', batch.batch_date.strftime('%d/%m/%Y'), 'Type:', document_type(journal_list),
                               'Source Application:', batch.source_ledger, 'Total amount:', Paragraph(str(batch_amount__sum), styles['RightAlign']), ''])

            bank_name = ''
            for journal in journal_list:
                bank_name = journal.bank.code if journal.bank else bank_name

            table_data.append(['Last Edited:', batch.update_date.strftime('%d/%m/%Y'), 'Status:', STATUS_TYPE[batch.status - 1][1],
                               'Bank: ', bank_name, 'No. of Entries:', Paragraph(str(batch.no_entries), styles['RightAlign']), ''])

            item_table = Table(table_data, colWidths=[100, 100, 100, 100, 100, 100, 100, 60, 50])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))

            elements.append(item_table)

            batch_total_amount__sum = 0
            batch_invoice_amount__sum = 0
            batch_total_adjustment_amount = 0
            batch_total_discount_amount = 0
            batch_adj_transaction_list = []
            batch_currency_list = []
            for journal in journal_list_sort:
                i = 0
                # index = -1
                # currency_code = journal.currency.code
                # currency_name = journal.currency.name
                # currency_decimal = journal.currency.is_decimal
                # if journal.supplier and journal.currency == journal.supplier.currency:
                #     currency_code = journal.currency.code
                #     currency_decimal = journal.currency.is_decimal
                #     currency_name = journal.currency.name
                # elif journal.supplier:
                #     currency_code = journal.supplier.currency.code
                #     currency_decimal = journal.supplier.currency.is_decimal
                #     currency_name = journal.supplier.currency.name
                # for curren in batch_currency_list:
                #     if curren[0] == currency_code:
                #         index = i
                #         break;
                #     i += 1
                # if index > -1:
                #     if journal.transaction_type == '2':
                #         batch_currency_list[index][1] += journal.total_amount
                #         batch_currency_list[index][4] += journal.original_amount
                #         batch_currency_list[index][5] += journal.total_amount
                #     else:
                #         batch_currency_list[index][1] += 0
                #         batch_currency_list[index][4] += journal.original_amount
                #         batch_currency_list[index][5] += journal.total_amount
                # else:
                #     if journal.transaction_type == '2':
                #         batch_currency_list.append([
                #             currency_code, journal.total_amount, 0, 0, journal.original_amount, journal.total_amount, currency_decimal, currency_name])
                #     else:
                #         batch_currency_list.append([
                #             currency_code, 0, 0, 0, journal.original_amount, journal.total_amount, currency_decimal, currency_name])
                batch_total_amount__sum += journal.total_amount
                trx_list = Transaction.objects.filter(is_hidden=0, company_id=company_id,
                                                      journal__id=journal.id).order_by('id')
                table_data = []
                # row 1 of entry
                table_data.append([])
                table_data.append(['Entry No.:', journal.code, journal.name, 'Document No.:', journal.document_number,
                                   'Receipt Amt. (' + journal.currency.code + '):', self.format_decimal(journal.currency.is_decimal, journal.amount)])

                item_table = Table(table_data, colWidths=[50, 40, 280, 100, 150, 100, 80])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (0, -1), (6, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                # 800
                COMMON_COLUMN = [90, 90, 90, 90, 90, 80, 90, 60, 60, 60]
                # row 2 of entry
                table_data = []
                transaction_type_dict = dict(RECEIPT_TRANSACTION_TYPES)
                perd_month = str(journal.perd_month) if journal.perd_month > 9 else '0' + str(journal.perd_month)
                year_period = str(journal.perd_year) + ' - ' + perd_month
                table_data.append(['Transaction Type:', transaction_type_dict.get(journal.transaction_type),
                                   'Receipt Date:', journal.document_date.strftime('%d/%m/%Y'), 'Posting Date:', journal.posting_date.strftime('%d/%m/%Y'),
                                   'Year - Period:', year_period, '', ''])

                table_data.append(['Customer:', self.trancate_string(journal.customer.code, 14) if journal.customer else '***Misc.***',
                                   self.trancate_string(journal.customer.name if journal.customer else journal.name, 30), '',
                                   'Account Set: ' if journal.account_set else '', journal.account_set.code if journal.account_set else '', '', '', '', ''])

                tax_group = journal.tax.tax_group.code if journal.tax else ''
                for trx in trx_list:
                    if trx.tax:
                        tax_group = trx.tax.tax_group.code

                if tax_group != '':
                    table_data.append(['', '', '', '', 'Tax Group:',  tax_group, '', '', '', ''])

                if journal.invoice_number:
                    table_data.append(['Invoice Number:', journal.invoice_number, '', '', '', '', '', '', '', ''])

                table_data.append(['Reference:', journal.reference, '', '', '', '', '', '', '', ''])

                payment_type_dict = dict(PAYMENT_TYPE)
                table_data.append(['Payment Code:', journal.payment_code.code if journal.payment_code else '', 'Payment Type:', 
                                    payment_type_dict.get(journal.payment_code.payment_type) if journal.payment_code else '',
                                   'Check/Receipt No.:', journal.payment_check_number, '', '', '', ''])
                table_data.append([])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                                                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                # '2' -> 'Misc Receipt'
                if journal.transaction_type == '2':
                    batch_invoice_amount__sum += journal.total_amount
                    table_data = []
                    # row 5 of entry
                    table_data.append(['', 'Dist. Code', '', 'G/L Account/ Reference', '', 'Account Description/ Detail Description',
                                       '', 'Tax Authority', '', 'Tax Base', '', 'Amount'])

                    COMMON_COLUMN_2 = [20, 70, 3, 167, 3, 177, 3, 146, 3, 107, 3, 100]
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (13, -1), (13, -1), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

                    for trx in trx_list:
                        table_data = []
                        # row 5 of entry

                        amount = self.format_decimal(trx.currency.is_decimal, trx.base_tax_amount)
                        tax_amount = intcomma('%.2f' % round_number(trx.tax_amount)) if trx.currency.is_decimal else intcomma('%.0f' % round_number(trx.tax_amount, 0))

                        table_data.append(['', trx.distribution_code, '', trx.account.code if trx.account else '', '',
                                           trx.account.name if trx.account else '', '', trx.tax.tax_authority.code if trx.tax else '', '',
                                           tax_amount if trx.tax_amount != 0 else '', '', amount])

                        if trx.reference != '' or trx.description != '':
                            table_data.append(['', '', '', trx.reference, '', self.trancate_string(trx.description, 50), '', '', '', '', '', ''])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                        ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                                                        ('ALIGN', (9, 0), (8, -1), 'RIGHT'),
                                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ]))
                        elements.append(item_table)

                    table_data = []
                    # row 7 of entry
                    total_amount__sum = trx_list.aggregate(Sum('total_amount'))['total_amount__sum']
                    total_amount__sum = self.format_decimal(trx.currency.is_decimal, total_amount__sum)

                    table_data.append(['', '', '', '', '', '', '', '', '', 'Total Invoice (' + trx.currency.code + '):', '', total_amount__sum])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEABOVE', (11, -1), (11, -1), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

                    table_data = []
                    tax_amount__sum = trx_list.aggregate(Sum('tax_amount'))['tax_amount__sum']
                    tax_amount__sum = self.format_decimal(trx.currency.is_decimal, tax_amount__sum)
                    table_data.append(['', '', '', '', '', '', '', '', '', 'Total Taxes (' + trx.currency.code + '):', '', tax_amount__sum])
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ]))
                    elements.append(item_table)
                else:
                    table_data = []
                    # row 5 of entry
                    table_data.append(['', 'Document No.:.', '', 'Sched. No.', '', 'Adj. No.', '', 'Adj. Reference', '',
                                       'Adj. Description', '', 'Adjustment', '', 'Discount', '', 'Amount'])

                    COMMON_COLUMN_2 = [20, 70, 3, 90, 3, 90, 3, 110, 3, 110, 3, 90, 3, 90, 3, 111]
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (13, -1), (13, -1), 0.25, colors.black),
                                                    ('LINEBELOW', (15, -1), (15, -1), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

                    total_amount__sum = 0
                    adj_transaction_list = []
                    for trx in trx_list:
                        # i = 0
                        # index = -1
                        # currency_code = journal.currency.code
                        # currency_name = journal.currency.name
                        # currency_decimal = journal.currency.is_decimal
                        # if journal.supplier and journal.currency == journal.supplier.currency:
                        #     currency_code = journal.currency.code
                        #     currency_decimal = journal.currency.is_decimal
                        #     currency_name = journal.currency.name
                        # elif journal.supplier:
                        #     currency_code = journal.supplier.currency.code
                        #     currency_decimal = journal.supplier.currency.is_decimal
                        #     currency_name = journal.supplier.currency.name
                        # for curren in batch_currency_list:
                        #     if curren[0] == currency_code:
                        #         index = i
                        #         break
                        #     i += 1
                        # if index > -1:
                        #     if journal.transaction_type == '2':
                        #         batch_currency_list[index][2] += trx.adjustment_amount
                        #         batch_currency_list[index][3] += trx.discount_amount
                        #     else:
                        #         batch_currency_list[index][2] += trx.adjustment_amount
                        #         batch_currency_list[index][3] += trx.discount_amount
                        table_data = []
                        adj_no = ''
                        adj_ref = ''
                        adj_desc = ''
                        adj_transaction = None
                        adjustment_amount = self.format_decimal(trx.currency.is_decimal, trx.adjustment_amount)
                        if trx.adjustment_amount != 0:
                            batch_total_adjustment_amount += trx.adjustment_amount
                            try:
                                adj_journal = Journal.objects.get(transaction_id=trx.id, is_hidden=False)
                                if adj_journal:
                                    adj_no = str(adj_journal.code)
                                    adj_ref = adj_journal.reference
                                    adj_desc = adj_journal.name[:22]
                                    adj_transaction = Transaction.objects.get(journal_id=adj_journal.id, is_hidden=False)
                                    adj_transaction_list.append(adj_transaction)
                                    batch_adj_transaction_list.append(adj_transaction)
                            except Exception as e:
                                print(e)
                        discount_amount = self.format_decimal(trx.currency.is_decimal, trx.discount_amount)
                        if trx.discount_amount != 0:
                            batch_total_discount_amount += trx.discount_amount
                        amount = trx.total_amount
                        if trx.related_invoice.journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] or trx.related_invoice.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount__sum -= amount
                            amount = (-1) * amount
                        else:
                            total_amount__sum += amount

                        amount = self.format_decimal(trx.currency.is_decimal, amount)

                        table_data.append(['', trx.related_invoice.document_number, '', '', '', adj_no, '', adj_ref, '', adj_desc, '',
                                           adjustment_amount, '', discount_amount, '', amount])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                        ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                                        ('ALIGN', (10, 0), (13, -1), 'RIGHT'),
                                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ]))
                        elements.append(item_table)

                    table_data = []
                    # row 7 of entry
                    total_amount__sum = self.format_decimal(trx.currency.is_decimal, total_amount__sum)

                    adjustment_amount__sum = trx_list.aggregate(Sum('adjustment_amount'))['adjustment_amount__sum']
                    adjustment_amount__sum = self.format_decimal(trx.currency.is_decimal, adjustment_amount__sum)

                    discount_amount__sum = trx_list.aggregate(Sum('discount_amount'))['discount_amount__sum']
                    discount_amount__sum = self.format_decimal(trx.currency.is_decimal, discount_amount__sum)

                    table_data.append(['', '', '', '', '', '', '', '', '', 'Total (' + trx.currency.code + '):', '',
                                       adjustment_amount__sum, '', discount_amount__sum, '', total_amount__sum])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('LINEABOVE', (11, 0), (11, 0), 0.25, colors.black),
                                                    ('LINEABOVE', (13, 0), (13, 0), 0.25, colors.black),
                                                    ('LINEABOVE', (15, 0), (15, 0), 0.25, colors.black),
                                                    ]))
                    elements.append(item_table)

                    if adj_transaction_list:
                        total_debit = 0
                        total_credit = 0
                        for adj_transaction in adj_transaction_list:
                            try:
                                table_data = []
                                table_data.append(['', 'Adj. No.:.', '', 'Dist. Code/Detail Ref.', '', '', '', 'GL Account', '',
                                                'Account Description', '', '', '', 'Debit', '', 'Credit'])

                                COMMON_COLUMN_2 = [20, 70, 3, 90, 3, 90, 3, 110, 3, 110, 3, 90, 3, 90, 3, 111]
                                item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                                ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                                ('SAPN', (3, 0), (5, 0)),
                                                                ('SAPN', (9, 0), (12, 0)),
                                                                ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (13, -1), (13, -1), 0.25, colors.black),
                                                                ('LINEBELOW', (15, -1), (15, -1), 0.25, colors.black),
                                                                ]))
                                elements.append(item_table)

                                adj_transaction_amount = self.format_decimal(
                                    adj_transaction.currency.is_decimal, adj_transaction.total_amount)
                                if adj_transaction.is_debit_account:
                                    total_debit += adj_transaction.total_amount
                                else:
                                    total_credit += adj_transaction.total_amount
                                table_data = []
                                table_data.append(['', adj_transaction.journal.code, '', adj_transaction.distribution_code.code if adj_transaction.distribution_code else '', 
                                                    '', '', '', adj_transaction.account.code, '', adj_transaction.account.name, '', '', '', 
                                                    adj_transaction_amount if adj_transaction.is_debit_account else '0.00', '', 
                                                    adj_transaction_amount if adj_transaction.is_credit_account else '0.00'])

                                item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                                ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                                                ('ALIGN', (10, 0), (13, -1), 'RIGHT'),
                                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                                ('SAPN', (3, 0), (5, 0)),
                                                                ('SAPN', (9, 0), (12, 0)),
                                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                                ]))
                                elements.append(item_table)

                            except Exception as e:
                                print(e)
                        total_debit = self.format_decimal(
                            adj_transaction.currency.is_decimal, total_debit)
                        total_credit = self.format_decimal(
                            adj_transaction.currency.is_decimal, total_credit)
                        table_data = []
                        table_data.append(['', '', '', '', '', '', '', '', '', 'Total (' + adj_transaction.currency.code + '):', '',
                                        '', '', total_debit, '', total_credit])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_2)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                        ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ('LINEABOVE', (11, 0), (11, 0), 0.25, colors.black),
                                                        ('LINEABOVE', (13, 0), (13, 0), 0.25, colors.black),
                                                        ('LINEABOVE', (15, 0), (15, 0), 0.25, colors.black),
                                                        ]))
                        elements.append(item_table)

            # --  Batch Summary By Currency --
            table_data = []
            table_data.append([])
            table_data.append(['----- Batch Summary -----'])
            item_table = Table(table_data, colWidths=[800])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append([])
            table_data.append(['Currency', '', 'Description', '', 'Invoice', '', 'Adjustment', '', 'Discount', '', 'Receipt', '', 'Advance Credit', ''])

            COMMON_COLUMN_3 = [80, 3, 279, 3, 80, 3, 80, 3, 80, 3, 80, 3, 100, 3]
            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('ALIGN', (4, -1), (13, -1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONT', (0, 0), (13, -1), s.REPORT_FONT_BOLD),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                            ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                            ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                            ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                                            ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                            ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                            ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            list_currency = journal_list.values('original_currency__code').order_by('original_currency__code').annotate(
                count=Count('original_currency__code'))

            is_exist_original_currency = False
            # for cur in list_currency:
            #     if cur['count'] > 0:
            #         is_exist_original_currency = True
            #         currency = Currency.objects.get(code=cur['original_currency__code'])

            #         table_data = []

            #         total_credit_note = journal_list.filter(original_currency__code=cur['original_currency__code'],
            #                                                 document_type=DOCUMENT_TYPE_DICT['Credit Note']
            #                                                 ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

            #         total_credit_note = float(round_number(total_credit_note)) if total_credit_note != None else 0

            #         total_debit_note = journal_list.filter(original_currency__code=cur['original_currency__code'],
            #                                                document_type=DOCUMENT_TYPE_DICT['Debit Note']
            #                                                ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

            #         total_debit_note = float(round_number(total_debit_note)) if total_debit_note != None else 0

            #         batch_total_amount__sum -= total_credit_note

            #         total_credit_note = intcomma("%.2f" % total_credit_note) if currency.is_decimal else intcomma("%.0f" % total_credit_note)

            #         # adjustment_amount = journal_list.filter(original_currency__code=cur['original_currency__code']
            #         #                                         ).aggregate(Sum('adjustment_amount')).get('adjustment_amount__sum', 0)
            #         adjustment_amount = batch_total_adjustment_amount

            #         adjustment_amount = adjustment_amount if adjustment_amount != None else 0
            #         adjustment_amount = self.format_decimal(currency.is_decimal, adjustment_amount)

            #         # discount_amount = journal_list.filter(original_currency__code=cur['original_currency__code']
            #         #                                       ).aggregate(Sum('discount_amount')).get('discount_amount__sum', 0)
            #         discount_amount = batch_total_discount_amount

            #         discount_amount = discount_amount if discount_amount != None else 0
            #         discount_amount = self.format_decimal(currency.is_decimal, discount_amount)

            #         # invoice__sum = journal_list.filter(currency__code=cur['currency__code'], invoice_number__isnull=False
            #         #                                    ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

            #         # invoice__sum = float(invoice__sum)
            #         # invoice__sum = self.format_decimal(currency.is_decimal, invoice__sum)
            #         batch_invoice_amount__sum = self.format_decimal(currency.is_decimal, batch_invoice_amount__sum)

            #         # original_amount__sum = journal_list.filter(original_currency__code=cur['original_currency__code']
            #         #                                            ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

            #         # original_amount__sum = self.format_decimal(currency.is_decimal, original_amount__sum)

            #         batch_total_amount__sum = self.format_decimal(currency.is_decimal, batch_total_amount__sum)

            #         table_data.append([currency.code, '', currency.name, '', batch_invoice_amount__sum, '', adjustment_amount, '', discount_amount,
            #                            '', batch_total_amount__sum, '', total_credit_note, ])

            #         item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            #         item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
            #                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
            #                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
            #                                         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            #                                         ('ALIGN', (4, -1), (12, -1), 'RIGHT'),
            #                                         ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            #                                         ('FONT', (0, 0), (12, -1), s.REPORT_FONT),
            #                                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
            #                                         ('TOPPADDING', (0, 0), (-1, -1), 0),
            #                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            #                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
            #                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            #                                         ]))
            #         elements.append(item_table)

            if not is_exist_original_currency:
                list_currency = journal_list.values('currency__code').order_by(
                    'currency__code').annotate(
                    count=Count('currency__code'))
                for cur in list_currency:
                    if cur['count'] > 0:
                        currency = Currency.objects.get(code=cur['currency__code'])

                        table_data = []

                        total_credit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Credit Note']
                                                                ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

                        total_credit_note = float(round_number(total_credit_note)) if total_credit_note != None else 0

                        total_debit_note = journal_list.filter(currency__code=cur['currency__code'], document_type=DOCUMENT_TYPE_DICT['Debit Note']
                                                               ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

                        total_debit_note = float(round_number(total_debit_note)) if total_debit_note != None else 0

                        batch_total_amount__sum -= total_credit_note

                        total_credit_note = intcomma("%.2f" % total_credit_note) if currency.is_decimal else intcomma("%.0f" % total_credit_note)

                        adjustment_amount = batch_total_adjustment_amount

                        adjustment_amount = adjustment_amount if adjustment_amount != None else 0
                        adjustment_amount = self.format_decimal(currency.is_decimal, adjustment_amount)

                        # discount_amount = journal_list.filter(original_currency__code=cur['original_currency__code']
                        #                                       ).aggregate(Sum('discount_amount')).get('discount_amount__sum', 0)
                        discount_amount = batch_total_discount_amount

                        discount_amount = discount_amount if discount_amount != None else 0
                        discount_amount = self.format_decimal(currency.is_decimal, discount_amount)

                        # invoice__sum = journal_list.filter(currency__code=cur['currency__code'], invoice_number__isnull=False
                        #                                    ).aggregate(Sum('total_amount')).get('total_amount__sum', 0)

                        # invoice__sum = self.format_decimal(currency.is_decimal, invoice__sum)
                        batch_invoice_amount__sum = self.format_decimal(currency.is_decimal, batch_invoice_amount__sum)

                        # original_amount__sum = journal_list.filter(currency__code=cur['currency__code']
                        #                                            ).aggregate(Sum('original_amount')).get('original_amount__sum', 0)

                        # original_amount__sum = self.format_decimal(currency.is_decimal, original_amount__sum)

                        batch_total_amount__sum = self.format_decimal(currency.is_decimal, batch_total_amount__sum)

                        table_data.append([currency.code, '', currency.name, '', batch_invoice_amount__sum, '', adjustment_amount,
                                           '', discount_amount, '', batch_total_amount__sum, '', total_credit_note, ])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                        ('ALIGN', (4, -1), (12, -1), 'RIGHT'),
                                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                        ('FONT', (0, 0), (12, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ]))
                        elements.append(item_table)
            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

        table_data = []
        table_data.append([str(count_entry) + ' entries printed'])
        table_data.append([str(len(batch_list)) + ' batches printed'])
        item_table = Table(table_data, colWidths=[800])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)

        COMMON_COLUMN_3 = [100, 3, 100, 3, 100,
                           3, 200, 3, 80, 3, 100, 3, 100, 3]
        if batch_adj_transaction_list:
            elements.append(PageBreak())
            table_data = []
            table_data.append([''])
            table_data.append(['----- Adjustment Summary -----'])
            item_table = Table(table_data, colWidths=[800])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append(['Batch-Entry', '', 'Customer No.', '', 'GL Account', '', 'Account Description', '', '', '', 'Debit', '', 'Credit', ''])

            item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('ALIGN', (10, -1), (13, -1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONT', (0, 0), (13, -1), s.REPORT_FONT_BOLD),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('SAPN', (6, 0), (8, 0)),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                            ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                            ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                            ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                                            ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                            ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                            ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)
            last_entry = ''
            i = 0
            total_debit = 0
            total_credit = 0
            try:
                for adj_transaction in batch_adj_transaction_list:
                    batch_entry_trx = Transaction.objects.get(pk=adj_transaction.journal.transaction_id)
                    batch_entry = batch_entry_trx.journal.batch.batch_no + '-' + batch_entry_trx.journal.code
                    if i == 0:
                        last_entry = batch_entry
                        i += 1
                    if last_entry != batch_entry:
                        total_debit = self.format_decimal(
                            adj_transaction.currency.is_decimal, total_debit)
                        total_credit = self.format_decimal(
                            adj_transaction.currency.is_decimal, total_credit)
                        table_data = []
                        table_data.append(['', '', '', '', '', '', '', '', 'Total (' + adj_transaction.currency.code + '):',
                                        '', total_debit, '', total_credit, ''])

                        
                        item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                        ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ('LINEABOVE', (7, 0), (-1, -1), 0.25, colors.black),
                                                        ]))
                        elements.append(item_table)
                        total_debit = 0
                        total_credit = 0
                        last_entry = batch_entry
                    coustomer_no = batch_entry_trx.journal.customer.code
                    adj_transaction_amount = self.format_decimal(
                        adj_transaction.currency.is_decimal, adj_transaction.total_amount)
                    if adj_transaction.is_debit_account:
                        total_debit += adj_transaction.total_amount
                    else:
                        total_credit += adj_transaction.total_amount
                    table_data = []
                    table_data.append([batch_entry, '', coustomer_no, '', adj_transaction.account.code,
                                    '', adj_transaction.account.name, '', '', '', adj_transaction_amount if adj_transaction.is_debit_account else '0.00', 
                                    '', adj_transaction_amount if adj_transaction.is_credit_account else '0.00', ''])

                    
                    item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                    ('ALIGN', (10, -1), (13, -1), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('SAPN', (6, 0), (8, 0)),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ]))
                    elements.append(item_table)

                total_debit = self.format_decimal(
                    adj_transaction.currency.is_decimal, total_debit)
                total_credit = self.format_decimal(
                    adj_transaction.currency.is_decimal, total_credit)
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', 'Total (' + adj_transaction.currency.code + '):',
                                '', total_debit, '', total_credit, ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN_3)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEABOVE', (7, 0), (-1, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)
            except Exception as e:
                print(e)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  onLaterPages=partial(self._header_footer, company_id=company_id, batch_type=batch_type),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def print_report_gl_function(self, company_id, batch_type, batch_from, batch_to, entry_from, entry_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))

        if int(batch_from) > int(batch_to):
            batch_to = batch_from

        batch_list = Batch.objects.filter(is_hidden=0, status__in=[STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted']],
                                          company_id=company_id, id__gte=batch_from, id__lte=batch_to).order_by('id')

        elements = []
        table_data = []
        table_data.append(['From Batch Number:', '[' + str(batch_list.first().batch_no) + '] to [' + str(batch_list.last().batch_no) + ']'])
        table_data.append(['From Source ledger:', '[' + batch_list.first().source_ledger + '] to [GL]'])
        table_data.append(['From Batch Date:', '[' + batch_list.first().batch_date.strftime('%d/%m/%Y') + '] to ['
                           + batch_list.last().batch_date.strftime('%d/%m/%Y') + ']'])

        table_data.append(['Include Printed Batches', '[Yes]'])
        table_data.append(['Status ', '[Open, Posted]'])
        table_data.append(['Include Ref. and Desc', '[Yes]'])
        table_data.append(['Show Comments', '[Yes]'])
        table_data.append(['Date', 'Doc.Date'])
        table_data.append([])

        item_table = Table(table_data, colWidths=[150, 660])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)
        count_entry = 0
        for batch in batch_list:
            journal_list = Journal.objects.filter(batch__id=batch.id, is_hidden=0, company_id=company_id, journal_type=dict(TRANSACTION_TYPES)['GL']) \
                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                .exclude(is_auto_reversed_entry=True) \
                .exclude(status=int(STATUS_TYPE_DICT['Auto Reverse Entry'])) \
                .exclude(reference='REVERSING ENTRY').select_related('batch')

            if entry_from != 'null' and int(entry_from):
                entry_from = int(entry_from)
                journal_list = journal_list.filter(id__gte=entry_from)
            if entry_to != 'null' and int(entry_to):
                entry_to = int(entry_to)
                journal_list = journal_list.filter(id__lte=entry_to)

            count_entry += len(journal_list)

            journal_list_sort = sorted(journal_list, key=lambda Journal: int(Journal.code))

            table_data = []
            table_data.append(['Srce.', '', 'Doc. Date', '', 'Acount Number', '', 'Account Description', '',
                               Paragraph('Debits', styles['RightAlign']), '', Paragraph('Credits', styles['RightAlign'])])

            COMMON_COLUMN1 = [80, 3, 80, 3, 180, 3, 250, 3, 100, 3, 100]
            item_table = Table(table_data, colWidths=COMMON_COLUMN1)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('ALIGN', (8, 0), (10, 0), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
                                            ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
                                            ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
                                            ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
                                            ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                            ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append(['Batch Number:', batch.batch_no, batch.description, '', '', ''])

            status_type_dict = dict(STATUS_TYPE)
            table_data.append(['Creation Date:', batch.batch_date.strftime('%d/%m/%Y'), 'Status:', status_type_dict.get(str(batch.status)),
                               'Type:', document_type(journal_list)])

            table_data.append([])
            COMMON_COLUMN2 = [80, 100, 80, 100, 50, 390]

            item_table = Table(table_data, colWidths=COMMON_COLUMN2)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            total_jou_debits = 0
            total_jou_crebits = 0
            for journal in journal_list_sort:
                table_data = []
                # row 1 of entry
                table_data.append(['Entry Number:', journal.code, journal.name, '', '', ''])
                perd_month = str(journal.perd_month) if journal.perd_month > 9 else '0' + str(journal.perd_month)
                year_period = str(journal.perd_year) + ' - ' + perd_month
                table_data.append(['Entry date:', journal.document_date.strftime('%d/%m/%Y') if journal.document_date else '',
                                   'Year-Prd.:', year_period, '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN2)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                trx_list = Transaction.objects.filter(is_hidden=0, company_id=company_id, journal__id=journal.id).order_by('id')
                total_txr_debits = 0
                total_txr_crebits = 0

                for trx in trx_list:
                    total_txr_debits += (float(round_number(trx.functional_amount)) if trx.is_debit_account else 0)
                    total_txr_crebits += (float(round_number(trx.functional_amount)) if trx.is_credit_account else 0)
                    debits = self.format_decimal(trx.functional_currency.is_decimal, trx.functional_amount) if trx.is_debit_account else 0
                    credits = self.format_decimal(trx.functional_currency.is_decimal, trx.functional_amount) if trx.is_credit_account else 0

                    table_data = []
                    table_data.append([journal.source_type, '', journal.document_date.strftime('%d/%m/%Y'), '',
                                       trx.account.code, '', self.trancate_string(trx.account.name, 42), '', debits if trx.is_debit_account else '', '',
                                       credits if trx.is_credit_account else ''])

                    table_data.append(['', '', 'Ref.:', '', trx.reference, '', 'Desc.:' + trx.description, '', '', ''])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN1)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('ALIGN', (8, 0), (10, 0), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ]))
                    elements.append(item_table)

                table_data = []
                table_data.append(['', '', '', '', '', '', 'Entry Total:', '',
                                   self.format_decimal(trx.functional_currency.is_decimal, total_txr_debits) if total_txr_debits > 0 else '', '',
                                   self.format_decimal(trx.functional_currency.is_decimal, total_txr_crebits) if total_txr_crebits > 0 else ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN1)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('ALIGN', (6, 0), (10, 0), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                                ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                                ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                                ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                total_jou_debits += total_txr_debits
                total_jou_crebits += total_txr_crebits

            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

            table_data = []
            table_data.append(['', '', '', '', '', '', 'Batch Total:', '', self.format_decimal(trx.functional_currency.is_decimal, total_jou_debits), '',
                               self.format_decimal(trx.functional_currency.is_decimal, total_jou_crebits)])

            item_table = Table(table_data, colWidths=COMMON_COLUMN1)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (6, 0), (10, 0), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
                                            ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
                                            ('LINEABOVE', (8, -1), (8, -1), 0.25, colors.black),
                                            ('LINEABOVE', (10, -1), (10, -1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

        table_data = []
        table_data.append([str(count_entry) + ' entries printed'])
        table_data.append([str(len(batch_list)) + ' batches printed'])

        item_table = Table(table_data, colWidths=[800])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]

            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, batch_type=batch_type, ql_type_report='1'),
                  onLaterPages=partial(self._header_footer, company_id=company_id, batch_type=batch_type, ql_type_report='1'),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def print_report_gl_source_function(self, company_id, batch_type, batch_from, batch_to, entry_from, entry_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, 'static/fonts/arial.ttf')))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, 'static/fonts/arial-bold.ttf')))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))

        if int(batch_from) > int(batch_to):
            batch_to = batch_from

        batch_list = Batch.objects.filter(is_hidden=0, status__in=[STATUS_TYPE_DICT['Open'], STATUS_TYPE_DICT['Posted']],
                                          company_id=company_id, id__gte=batch_from, id__lte=batch_to).order_by('id')

        elements = []
        table_data = []
        table_data.append(['From Batch Number:', '[' + str(batch_list.first().batch_no) + '] to [' + str(batch_list.last().batch_no) + ']'])
        table_data.append(['From Source ledger:', '[' + batch_list.first().source_ledger + '] to [GL]'])
        table_data.append(['From Batch Date:', '[' + batch_list.first().batch_date.strftime('%d/%m/%Y') + '] to ['
                           + batch_list.last().batch_date.strftime('%d/%m/%Y') + ']'])
        table_data.append(['Include Printed Batches', '[Yes]'])
        table_data.append(['Status ', '[Open, Posted]'])
        table_data.append(['Include Ref. and Desc', '[Yes]'])
        table_data.append(['Show Comments', '[Yes]'])
        table_data.append(['Date', 'Doc.Date'])
        table_data.append([])

        item_table = Table(table_data, colWidths=[150, 660])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)
        count_entry = 0
        for batch in batch_list:
            journal_list = Journal.objects.filter(batch__id=batch.id, is_hidden=0, company_id=company_id, journal_type=dict(TRANSACTION_TYPES)['GL']) \
                .exclude(journal_type=dict(TRANSACTION_TYPES)['AD']) \
                .exclude(is_auto_reversed_entry=True) \
                .exclude(status=int(STATUS_TYPE_DICT['Auto Reverse Entry'])) \
                .exclude(reference='REVERSING ENTRY').select_related('batch')

            if entry_from != 'null' and int(entry_from):
                entry_from = int(entry_from)
                journal_list = journal_list.filter(id__gte=entry_from)
            if entry_to != 'null' and  int(entry_to):
                entry_to = int(entry_to)
                journal_list = journal_list.filter(id__lte=entry_to)

            count_entry += len(journal_list)
            journal_list_sort = sorted(journal_list, key=lambda Journal: int(Journal.code))

            COMMON_COLUMN1 = [30, 3, 40, 3, 140, 3, 140, 3, 20, 3, 50, 3, 70, 3, 20, 3, 133, 3, 133]

            table_data = []
            table_data.append(['', '', '', '', '', '', '', '', 'Rate', '', '', '', '', '', '', '',
                               '---------------Source---------------', '', '---------------Functional---------------'])

            item_table = Table(table_data, colWidths=COMMON_COLUMN1)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (16, 0), (18, 0), 'CENTER'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            COMMON_COLUMN2 = [30, 3, 50, 3, 100, 3, 170, 3, 20, 3, 50, 3, 70, 3, 20, 3, 65, 3, 65, 3, 65, 3, 65]
            table_data = []
            table_data.append(['Srce.', '', 'Doc. Date', '', 'Acount Number', '', 'Account Description', '', 'Type', '',
                               'Rate Date', '', 'Exch. Rate', '', 'Curr', '', 'Debits', '', 'Credits', '', 'Debits', '', 'Credits'])

            item_table = Table(table_data, colWidths=COMMON_COLUMN2)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (0, 0), (16, 0), 'LEFT'),
                                            ('ALIGN', (16, 0), (22, 0), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
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
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append(['Batch Number:', batch.batch_no, batch.description, '', '', ''])

            status_type_dict = dict(STATUS_TYPE)

            table_data.append(['Creation Date:', batch.batch_date.strftime('%d/%m/%Y'), 'Status:', status_type_dict.get(str(batch.status)),
                               'Type:', document_type(journal_list)])

            COMMON_COLUMN3 = [80, 70, 80, 130, 50, 390]

            item_table = Table(table_data, colWidths=COMMON_COLUMN3)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ]))
            elements.append(item_table)

            total_jou_src_debits = 0
            total_jou_src_crebits = 0

            total_jou_fun_debits = 0
            total_jou_fun_crebits = 0
            batch_src_currency_list = []
            for journal in journal_list_sort:
                table_data = []
                # row 1 of entry
                table_data.append([])
                table_data.append(['Entry Number:', journal.code, journal.name, '', '', ''])
                perd_month = str(journal.perd_month) if journal.perd_month > 9 else '0' + str(journal.perd_month)
                year_period = str(journal.perd_year) + ' - ' + perd_month
                table_data.append(['Entry date:', journal.document_date.strftime('%d/%m/%Y') if journal.document_date else '',
                                   'Year-Prd.:', year_period, '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN3)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)

                trx_list = Transaction.objects.filter(is_hidden=0, company_id=company_id,
                                                      journal__id=journal.id).order_by('id')

                total_txr_src_debits = 0
                total_txr_src_crebits = 0
                total_txr_fun_debits = 0
                total_txr_fun_crebits = 0
                src_currency_list = []
                for trx in trx_list:
                    total_txr_fun_debits += (float(round_number(trx.functional_amount)) if trx.is_debit_account else 0)
                    total_txr_fun_crebits += (float(round_number(trx.functional_amount)) if trx.is_credit_account else 0)

                    if trx.currency_id != trx.functional_currency_id:
                        # for journal
                        i = 0
                        index = -1
                        for curren in src_currency_list:
                            if curren[0] == trx.currency.code:
                                index = i
                                break;
                            i += 1
                        if index > -1:
                            src_currency_list[index][1] += (float(round_number(trx.amount)) if trx.is_debit_account else 0)
                            src_currency_list[index][2] += (float(round_number(trx.amount)) if trx.is_credit_account else 0)
                        else:
                            t_code = trx.currency.code
                            t_debit = (float(round_number(trx.amount)) if trx.is_debit_account else 0)
                            t_credit = (float(round_number(trx.amount)) if trx.is_credit_account else 0)
                            src_currency_list.append([t_code, t_debit, t_credit, trx.currency.is_decimal])
                        # for Batch
                        i = 0
                        index = -1
                        for curren in batch_src_currency_list:
                            if curren[0] == trx.currency.code:
                                index = i
                                break;
                            i += 1
                        if index > -1:
                            batch_src_currency_list[index][1] += (float(round_number(trx.amount)) if trx.is_debit_account else 0)
                            batch_src_currency_list[index][2] += (float(round_number(trx.amount)) if trx.is_credit_account else 0)
                        else:
                            t_code = trx.currency.code
                            t_debit = (float(round_number(trx.amount)) if trx.is_debit_account else 0)
                            t_credit = (float(round_number(trx.amount)) if trx.is_credit_account else 0)
                            batch_src_currency_list.append([t_code, t_debit, t_credit, trx.currency.is_decimal])
                    else:
                        total_txr_src_debits += (float(round_number(trx.amount)) if trx.is_debit_account else 0)
                        total_txr_src_crebits += (float(round_number(trx.amount)) if trx.is_credit_account else 0)

                    fun_debits = \
                        self.format_decimal(trx.functional_currency.is_decimal, trx.functional_amount) if trx.is_debit_account else 0
                    fun_credits = \
                        self.format_decimal(trx.functional_currency.is_decimal, trx.functional_amount) if trx.is_credit_account else 0
                    src_debits = \
                        self.format_decimal(trx.currency.is_decimal, trx.amount) if trx.is_debit_account else 0
                    src_credits = \
                        self.format_decimal(trx.currency.is_decimal, trx.amount) if trx.is_credit_account else 0
                    if trx.rate_date:
                        try:
                            if trx.rate_date.day != 1:
                                if len(str(trx.rate_date.month)) == 1:
                                    rate_date = '01/0' + str(trx.rate_date.month) + '/' + str(trx.rate_date.year)
                                else:
                                    rate_date = '01/' + str(trx.rate_date.month) + '/' + str(trx.rate_date.year)
                            else:
                                rate_date = trx.rate_date.strftime('%d/%m/%Y')
                        except:
                            rate_date = trx.rate_date.strftime('%d/%m/%Y')
                    else:
                        if 'RV' in trx.journal.source_type:
                            if trx.journal.document_date.month < 9:
                                rate_date = '01/0' + \
                                    str(trx.journal.document_date.month+1) + '/' + str(trx.journal.document_date.year)
                            elif trx.journal.document_date.month < 12:
                                rate_date = '01/' + \
                                    str(trx.journal.document_date.month+1) + '/' + str(trx.journal.document_date.year)
                            else:
                                rate_date = '01/01/' + str(trx.journal.document_date.year+1)
                        else:
                            if trx.journal.document_date.month < 10:
                                rate_date = '01/0' + \
                                    str(trx.journal.document_date.month) + '/' + str(trx.journal.document_date.year)
                            else:
                                rate_date = '01/' + \
                                    str(trx.journal.document_date.month) + '/' + str(trx.journal.document_date.year)
                        
                    table_data = []
                    table_data.append([trx.source_type, '', journal.document_date.strftime('%d/%m/%Y'), '',
                                       trx.account.code, '', self.trancate_string(trx.account.name, 30), '',
                                       'SR', '', rate_date if rate_date else '//', '',
                                       Paragraph(str(trx.exchange_rate), styles['RightAlign']), '',
                                       trx.currency.code, '', src_debits if src_debits != 0 and trx.amount > 0 else '', '',
                                       src_credits if src_credits != 0 and trx.amount > 0 else '', '',
                                       fun_debits if fun_debits != 0 and trx.functional_amount > 0 else '', '',
                                       fun_credits if fun_credits != 0 and trx.functional_amount > 0 else ''])

                    table_data.append(['', '', 'Ref.:', '', trx.reference, '', 'Desc.:' + trx.description,
                                       '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN2)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('ALIGN', (0, 0), (15, 0), 'LEFT'),
                                                    ('ALIGN', (16, 0), (22, 0), 'RIGHT'),
                                                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ]))
                    elements.append(item_table)

                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', '', '', '', 'Entry Total:', '', journal.currency.code, '', '',
                                   self.format_decimal(journal.currency.is_decimal, total_txr_src_debits)
                                   if total_txr_src_debits > 0 else '', '',
                                   self.format_decimal(journal.currency.is_decimal, total_txr_src_crebits)
                                   if total_txr_src_crebits > 0 else '', '',
                                   self.format_decimal(journal.company.currency.is_decimal, total_txr_fun_debits)
                                   if total_txr_fun_debits > 0 else '', '',
                                   self.format_decimal(journal.company.currency.is_decimal, total_txr_fun_crebits)
                                   if total_txr_fun_crebits > 0 else ''])
                for curren in src_currency_list:
                    table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', curren[0], '', '',
                                       self.format_decimal(curren[3], curren[1])if curren[1] > 0 else '', '',
                                       self.format_decimal(curren[3], curren[2])if curren[2] > 0 else '', '',
                                       '', '', ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN2)
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                                                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('LINEABOVE', (16, 0), (16, 0), 0.25, colors.black),
                                                ('LINEABOVE', (18, 0), (18, 0), 0.25, colors.black),
                                                ('LINEABOVE', (20, 0), (20, 0), 0.25, colors.black),
                                                ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                                                ]))
                elements.append(item_table)

                total_jou_src_debits += total_txr_src_debits
                total_jou_src_crebits += total_txr_src_crebits

                total_jou_fun_debits += total_txr_fun_debits
                total_jou_fun_crebits += total_txr_fun_crebits

            table_data = []
            table_data.append([''])
            table_data.append(['', '', '', '', '', '', '', '', '', '', '', 'Batch Total:', '', batch.currency.code, '', '',
                               self.format_decimal(batch.currency.is_decimal, total_jou_src_debits)
                               if total_jou_src_debits > 0 else '', '',
                               self.format_decimal(batch.currency.is_decimal, total_jou_src_crebits)
                               if total_jou_src_crebits > 0 else '', '',
                               self.format_decimal(batch.company.currency.is_decimal, total_jou_fun_debits)
                               if total_jou_fun_debits > 0 else '', '',
                               self.format_decimal(batch.company.currency.is_decimal, total_jou_fun_crebits)
                               if total_jou_fun_crebits > 0 else ''])
            for curren in batch_src_currency_list:
                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', curren[0], '', '',
                                    self.format_decimal(curren[3], curren[1])if curren[1] > 0 else '', '',
                                    self.format_decimal(curren[3], curren[2])if curren[2] > 0 else '', '',
                                    '', '', ''])

            item_table = Table(table_data, colWidths=COMMON_COLUMN2)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('ALIGN', (14, 1), (-1, -1), 'RIGHT'),
                                            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('LINEABOVE', (16, 1), (16, 1), 0.25, colors.black),
                                            ('LINEABOVE', (18, 1), (18, 1), 0.25, colors.black),
                                            ('LINEABOVE', (20, 1), (20, 1), 0.25, colors.black),
                                            ('LINEABOVE', (22, 1), (22, 1), 0.25, colors.black),
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append([''])
            item_table = Table(table_data, colWidths=[800])
            elements.append(item_table)

        table_data = []
        table_data.append([str(count_entry) + ' entries printed'])
        table_data.append([str(len(batch_list)) + ' batches printed'])
        item_table = Table(table_data, colWidths=[800])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]

            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, batch_type=batch_type, ql_type_report='2'),
                  onLaterPages=partial(self._header_footer, company_id=company_id, batch_type=batch_type, ql_type_report='2'),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


def document_type(journal_list):
    if journal_list:
        if journal_list[0].batch.input_type == '2':
            return 'Manual Entry'
        else:
            return 'Generated'
    else:
        return '-'
