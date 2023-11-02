from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import Order
from reports.numbered_page import NumberedPage
from utilities.constants import ORDER_TYPE
import datetime
import calendar
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial
from decimal import Decimal
from utilities.common import round_number, get_decimal_place

colWidths = [60, 98, 50, 210, 25, 75, 60]
rowHeights = 13
dataRowHeights = 18


class Print_SR8700:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, first_day, last_day, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1ST row
        header_data = []
        row1_info1 = "SR8700 Sales and Purchase System"
        row1_info2 = "MONTHLY SALES INVOICE SUMMARY REPORT AS AT " + last_day.strftime('%B %Y').upper()
        header_data.append([row1_info1, row1_info2])

        # 2ND row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Group By Currency & Customer"
        header_data.append([row2_info1, row2_info2])
        # 3RD row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])

        row4_info1 = "Issued Date : [" + first_day.strftime('%d/%m/%Y') + "] To [" + \
                     last_day.strftime('%d/%m/%Y') + "]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[265, 313], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Doc Date', 'Document No.', 'Customer Code & Name', '', 'Curr', 'Amount', 'Remark']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, 0), 10),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('ALIGN', (4, 0), (4, 0), 'CENTER'),
             ('ALIGN', (5, 0), (5, 0), 'RIGHT'),
             ('ALIGN', (6, 0), (6, 0), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (2, 0), (3, 0)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, month, year):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=17, leftMargin=17, topMargin=110, bottomMargin=42, pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE_2, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE_2, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE_2, alignment=TA_RIGHT))
        # Our container for 'Flowable' objects
        elements = []
        style = [('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]
        style_footer = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                        ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('SPAN', (2, 0), (3, 0)),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]

        # Draw Content of PDF
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        # filter orders by selected month (from first_day to last_day of the month)
        order_list = Order.objects.filter(company_id=company_id, is_hidden=0, customer__isnull=False,
                                          document_date__gte=first_day, document_date__lte=last_day,
                                          order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .select_related('customer', 'currency').order_by('currency', 'document_date', 'order_code', 'customer__name')
        length = len(order_list)

        if length:
            total = 0
            table_data = []
            i = 0
            m_curr_code = ''
            for order in order_list:
                if i == 0:
                    m_curr_code = order.currency.code
                    i+=1
                if m_curr_code != order.currency.code:
                    table_data = []
                    table_data.append(['', '', '', '',  Paragraph('Sub Total By: ' + m_curr_code, styles['RightAlignBold']),
                                    Paragraph(intcomma(decimal_place % round_number(total)), styles['RightAlignBold']), ''])

                    item_table = Table(table_data, colWidths=[60, 98, 50, 25, 210, 75, 60], rowHeights=dataRowHeights)
                    item_table.setStyle(TableStyle(style_footer))
                    elements.append(item_table)
                    total = 0
                    m_curr_code = order.currency.code
                total += Decimal(order.total)
                decimal_place = get_decimal_place(order.currency)
                table_data = []
                table_data.append([Paragraph(order.document_date.strftime("%d/%m/%Y"), styles['LeftAlign']),
                                   Paragraph(order.document_number, styles['LeftAlign']),
                                   Paragraph(order.customer.code, styles['LeftAlign']),
                                   Paragraph(order.customer.name[:42], styles['LeftAlign']),
                                   Paragraph(order.currency.code, styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place % round_number(order.total)), styles['RightAlign']), ''])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=dataRowHeights)
                item_table.setStyle(TableStyle(style))
                elements.append(item_table)
                m_curr_code = order.currency.code

            decimal_place = get_decimal_place(order.currency)
            table_data = []
            table_data.append(['', '', '', '',  Paragraph('Sub Total By: ' + order.currency.code, styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place % round_number(total)), styles['RightAlignBold']), ''])

            item_table = Table(table_data, colWidths=[60, 98, 50, 25, 210, 75, 60], rowHeights=dataRowHeights)
            item_table.setStyle(TableStyle(style_footer))
            elements.append(item_table)

        else:  # if there's no order in the selected month
            table_data = [['', '', '', '', '', '', '']]
            # Create the table
            item_table = Table(table_data, colWidths=colWidths, rowHeights=dataRowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ]))
            elements.append(item_table)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, first_day=first_day, last_day=last_day, company_id=company_id),
                  onLaterPages=partial(self._header_footer, first_day=first_day, last_day=last_day, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=97, adjusted_width=15))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
