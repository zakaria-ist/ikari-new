import datetime
import os
from datetime import datetime
from functools import partial
from django.conf import settings as s
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from accounting.models import Journal
from companies.models import Company
from reports.numbered_page import NumberedPage
from suppliers.models import Supplier
from utilities.constants import TRANSACTION_TYPES, STATUS_TYPE_DICT, EMAIL_MSG_CONST, VENDOR_DEFAULT_MSG
from utilities.common import get_vendor_filter_range


class Print_AP_vendor_letter:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    def print_report(self, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        company = Company.objects.get(pk=company_id)
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=117, bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT))
        elements = []

        cust_id_from = int(cus_no) if cus_no else 0
        cust_id_to = int(curr_list) if curr_list else 0

        jounal_item_list = Journal.objects.filter(company_id=company_id, is_hidden=0, status=int(STATUS_TYPE_DICT['Posted']),
                                                  batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                  batch__batch_type=dict(TRANSACTION_TYPES)['AP Invoice'],
                                                  document_date__range=[age_from, cutoff_date])

        vendor_range = get_vendor_filter_range(company_id, int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                               int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')

        if cust_id_to > 0 and cust_id_from > 0:
            jounal_item_list = jounal_item_list.filter(
                supplier_id__in=vendor_range).values('supplier_id').distinct()
        else:
            jounal_item_list = jounal_item_list.values('supplier_id').distinct()

        if jounal_item_list:
            for exp in jounal_item_list:
                journal_trx = Supplier.objects.get(pk=exp['supplier_id'])
                email_msg = journal_trx.email_msg
                if email_msg is None:
                    email_msg = VENDOR_DEFAULT_MSG
                email_msg = email_msg.replace(EMAIL_MSG_CONST['company_name'], company.name)
                email_msg = email_msg.replace(EMAIL_MSG_CONST['date'], datetime.now().strftime('%d-%m-%Y'))
                if email_msg.find(EMAIL_MSG_CONST['vendor_name']):
                    email_msg = email_msg.replace(EMAIL_MSG_CONST['vendor_name'], journal_trx.name)
                if email_msg.find(EMAIL_MSG_CONST['company_phone']):
                    email_msg = email_msg.replace(EMAIL_MSG_CONST['company_phone'], company.phone)

                email_msg_array = email_msg.splitlines()
                table_data = []
                for i in range(len(email_msg_array)):
                    if i == 0:
                        table_data.append(['', '', '', '', '', '', email_msg_array[i], '', '', '', '', '', '', '', '', '', ''])
                    if i == 1 or i == 2:
                        table_data.append([email_msg_array[i], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 10),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
                     ]))
                elements.append(item_table)
                table_data = []
                for i in range(len(email_msg_array)):
                    if i >= 5:
                        table_data.append([email_msg_array[i], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 10),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
                     ]))
                elements.append(item_table)
                if elements.__len__() == 0:
                    table_data = [['']]
                    table_body = Table(table_data, colWidths=[795])
                    table_body.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 4.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 4.25, colors.transparent)
                         ]))
                    elements.append(table_body)
                elements.append(PageBreak())
        else:
            table_data = []
            table_data.append(['', 'NO DATA FOUND', ''])
            item_table = Table(table_data, colWidths=[270, 270, 270])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONT', (0, 0), (0, -1), s.REPORT_FONT_BOLD),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                                            ('ALIGN', (2, 0), (2, 0), 'CENTER'), ]))
            elements.append(item_table)

        doc.build(elements,
                  canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def print_report_email(self, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
        pdfmetrics.registerFont(
            TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(
            TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        company = Company.objects.get(pk=company_id)
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=117, bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT))
        elements = []

        cust_id_from = int(cus_no) if cus_no else 0
        cust_id_to = int(curr_list) if curr_list else 0

        jounal_item_list = Journal.objects.filter(company_id=company_id, is_hidden=0, status=int(STATUS_TYPE_DICT['Posted']),
                                                  batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                  batch__batch_type=dict(TRANSACTION_TYPES)['AP Invoice'],
                                                  document_date__range=[age_from, cutoff_date])

        vendor_range = get_vendor_filter_range(company_id, int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                               int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')

        jounal_item_list = jounal_item_list.filter(supplier_id__in=vendor_range).values('supplier_id').distinct()

        if jounal_item_list:
            for exp in jounal_item_list:
                journal_trx = Supplier.objects.get(pk=exp['supplier_id'])
                email_msg = journal_trx.email_msg
                if email_msg is None:
                    email_msg = VENDOR_DEFAULT_MSG
                email_msg = email_msg.replace(EMAIL_MSG_CONST['company_name'], company.name)
                email_msg = email_msg.replace(EMAIL_MSG_CONST['date'], datetime.now().strftime('%d-%m-%Y'))
                if email_msg.find(EMAIL_MSG_CONST['vendor_name']):
                    email_msg = email_msg.replace(EMAIL_MSG_CONST['vendor_name'], journal_trx.name)
                if email_msg.find(EMAIL_MSG_CONST['company_phone']):
                    email_msg = email_msg.replace(EMAIL_MSG_CONST['company_phone'], company.phone)

                email_msg_array = email_msg.splitlines()
                table_data = []
                for i in range(len(email_msg_array)):
                    if i == 0:
                        table_data.append(['', '', '', '', '', '', email_msg_array[i], '', '', '', '', '', '', '', '', '', ''])
                    if i == 1 or i == 2:
                        table_data.append([email_msg_array[i], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 10),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
                     ]))
                elements.append(item_table)
                table_data = []
                for i in range(len(email_msg_array)):
                    if i >= 5:
                        table_data.append([email_msg_array[i], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=[60, 5, 210, 5, 35, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75, 5, 75])

                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 10),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
                     ]))
                elements.append(item_table)
                if elements.__len__() == 0:
                    table_data = [['']]
                    table_body = Table(table_data, colWidths=[795])
                    table_body.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 4.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 4.25, colors.transparent)
                         ]))
                    elements.append(table_body)
                elements.append(PageBreak())

        doc.build(elements,
                  canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
