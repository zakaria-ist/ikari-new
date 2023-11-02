from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from customers.models import Customer
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from django.db.models import Q
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial
from utilities.common import validate_date_to_from

rowHeights = 14
colWidths = [70, 120, 30, 70, 90, 90, 80]


class Print_SR8400:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, delivery_from, delivery_to, cust_list):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SL8400 Sales / Purchase System"
        row1_info2 = "S/O and Sales Invoice Matching Report By Customer"
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Customer, Document Number"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if len(cust_list):
            item1 = Customer.objects.get(pk=cust_list[0]).code
            item2 = Customer.objects.get(pk=cust_list[-1]).code
            row4_info1 = "Customer No.: [" + item1 + "][" + item2 + "]"
        else:
            row4_info1 = "Customer No.: [][]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])
        # 5st row
        current_year = datetime.datetime.now().year
        delivery_from_year = datetime.datetime.strptime(delivery_from, '%d-%m-%Y').year
        delivery_to_year = datetime.datetime.strptime(delivery_to, '%d-%m-%Y').year
        if current_year - delivery_from_year <= 99 and delivery_to_year <= current_year:
            row5_info1 = "Issue Date : [" + delivery_from + "]" + " - [" + delivery_to + "]"
        elif current_year - delivery_from_year <= 99:
            row5_info1 = "Issue Date : [" + delivery_from + "]" + " - [_/_/_]"
        elif delivery_to_year <= current_year:
            row5_info1 = "Issue Date : [_/_/_]" + " - [" + delivery_to + "]"
        else:
            row5_info1 = "Issue Date : [_/_/_]" + " - [_/_/_]"
        row5_info2 = "Transaction Code : [SALES ORDER]"
        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[265, 273], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('FONTSIZE', (1, 0), (1, 0), 11),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_header = []
        table_header.append(['Customer Code & Name', '', '', '', '', '', ''])
        table_header.append(['Trn code', 'Document No.', 'Line', 'Doc. Date', 'Part No.', '', 'Order Qty'])
        table_header.append(['', 'Customer PO No.', '', '', '', '', ''])
        table_header.append(['', 'Sales Invoice No', 'Line', 'Invoice Date', '', '', 'Invoice Qty'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 3), (-1, 3), 0.25, colors.black),
             ('ALIGN', (0, 0), (0, 0), 'LEFT'),
             ('ALIGN', (0, 1), (0, 1), 'CENTER'),
             ('ALIGN', (0, 3), (0, 3), 'CENTER'),
             ('ALIGN', (6, 1), (6, 1), 'RIGHT'),
             ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, customer_no, document_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=180, bottomMargin=42, pagesize=self.pagesize)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)
        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__document_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                                delivery_to_obj.strftime('%Y-%m-%d')),
                                                   order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .order_by('order__customer__code', 'order__document_number')

        do_refer_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                                  order__document_date__gte=delivery_from_obj.strftime('%Y-%m-%d'))

        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)

        doc_list = eval(document_no)
        if len(doc_list):
            order_item_list = order_item_list.filter(order_id__in=doc_list)

        customer_code = ''
        do_exists = False
        for i, mItem in enumerate(order_item_list):
            if customer_code != mItem.order.customer.code:
                do_exists = False
                customer_code = mItem.order.customer.code
                table_data = []
                table_data.append([mItem.order.customer.code, mItem.order.customer.name, '', '', '', '', ''])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('SPAN', (1, 0), (4, 0)),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
            if customer_code == mItem.order.customer.code:
                do_refer_item = do_refer_items.filter(reference_id=mItem.order.id, refer_line=mItem.line_number)
                if do_refer_item:
                    do_exists = True
                    table_data = []
                    table_data.append(['S/O', mItem.order.document_number, mItem.line_number,
                                       mItem.order.document_date.strftime("%d/%m/%Y"), mItem.item.code, '', intcomma("%.2f" % mItem.quantity)])

                    table_data.append(['', mItem.customer_po_no, '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONT', (1, 1), (1, 1), s.REPORT_FONT_BOLD),
                         ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                         ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                         ('ALIGN', (6, 0), (6, 0), 'RIGHT'),
                         ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (2, 0), (2, 0), 10),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                    do_total = 0
                    for refer_item in do_refer_item:
                        table_data = []
                        table_data.append(['D/O', refer_item.order.document_number, refer_item.line_number,
                                           refer_item.order.document_date.strftime("%d/%m/%Y"), refer_item.item.code, '',
                                           intcomma("%.2f" % refer_item.quantity)])

                        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                             ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                             ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (2, 0), (2, 0), 10),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                        do_total += refer_item.quantity
                    # GR total
                    table_data = []
                    table_data.append(['', '', '', '', '', 'Invoice Total :', intcomma("%.2f" % do_total)])
                    table_data.append(['', '', '', '', '', '', ''])
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                         ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                if not do_exists:
                    elements.pop()
                    customer_code = ''

        # Create the table
        if len(elements) == 0:
            table_data = []
            table_data.append(['', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), cust_list=cust_list),
                  onLaterPages=partial(self._header_footer, company_id=company_id, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), cust_list=cust_list),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
