from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from django.utils.dateparse import parse_date
from accounting.models import Journal
from customers.models import Customer
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import TRANSACTION_TYPES
from utilities.common import get_customer_filter_range


class Print_AR_customers_Label:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
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

        header_table = Table(header_data, colWidths=[280, 330, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
             ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _header_last_footer(canvas, doc, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
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

        header_table = Table(header_data, colWidths=[280, 330, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_header = ['', '', '', '', '', '', '', '', '1 To 30', '', '31 To 60', '', '61 To 90', '', 'Over 90', '', '']

        table_data.append(table_header)
        # 2ND ROW
        table_header = ['Customer No.', '', 'Customer Name.', '', 'Cur.', '', 'Current', '', 'Days',
                        '', 'Days', '', 'Days', '', 'Days', '', 'Total']

        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[60, 5, 170, 5, 30, 5, 90, 5, 80, 5, 80, 5, 80, 5, 80, 5, 85])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
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

    def print_report(self, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=117, bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT))

        # Our container for 'Flowable' objects
        cust_id_from = 0
        cust_id_to = 0
        if cus_no != '0':
            id_cus_range = cus_no.split(',')
            cust_id_from = int(id_cus_range[0])
            cust_id_to = int(id_cus_range[1])
        # cust_id_from = int(cus_no) if cus_no else 0
        # cust_id_to = int(curr_list) if curr_list else 0
        open_doc = 1 if int(doc_type) == 1 else 2

        jounal_item_list = Journal.objects.filter(company_id=company_id, is_hidden=0, batch__batch_type=dict(TRANSACTION_TYPES)['AR Invoice'],
                                                  batch__status=open_doc, is_fully_paid=0, document_date__lte=cutoff_date)
        if cust_id_from > 0 and cust_id_to > 0:
            customer_code_range = get_customer_filter_range(company_id, int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                                            int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')

            jounal_item_list = jounal_item_list.filter(customer_id__in=customer_code_range).values('customer_id').distinct()
        else:
            jounal_item_list = jounal_item_list.values('customer_id').distinct()

        elements = []
        for exp in jounal_item_list:
            if exp['customer_id']:
                journal_trx = Customer.objects.get(pk=exp['customer_id'])
                table_data = []
                table_data.append([journal_trx.name, '', ''])
                table_data.append(['', '', ''])
                table_data.append(['', '', ''])
                table_data.append(['', '', ''])
                table_data.append(['', '', ''])

                item_table = Table(table_data, colWidths=[280, 330, 200])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONT', (0, 0), (0, -1), s.REPORT_FONT_BOLD),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ]))
                elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75, 60, 85, 90, 130])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)
        doc.build(elements,
                  canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
