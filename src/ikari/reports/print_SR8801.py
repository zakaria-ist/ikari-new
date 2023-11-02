from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from orders.models import OrderItem
from suppliers.models import Supplier
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial
from utilities.common import validate_date_to_from

rowHeights = 14
colWidths = [70, 80, 150, 100, 70, 80, 100, 70, 90]


class Print_SR8801:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, delivery_from, delivery_to, supp_list):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR8801 Sales / Purchase System"
        row1_info2 = "Purchase Delivery Schedule Report"
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Group By Supplier Code, Part No. & Delivery Date"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if len(supp_list):
            item1 = Supplier.objects.get(pk=supp_list[0]).code
            item2 = Supplier.objects.get(pk=supp_list[-1]).code
            row4_info1 = "Supplier No.: [" + item1 + "][" + item2 + "]"
        else:
            row4_info1 = "Supplier No.: [][]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])
        # 5st row
        current_year = datetime.datetime.now().year
        delivery_from_year = datetime.datetime.strptime(delivery_from, '%d-%m-%Y').year
        delivery_to_year = datetime.datetime.strptime(delivery_to, '%d-%m-%Y').year
        if current_year - delivery_from_year <= 99 and delivery_to_year <= current_year:
            row5_info1 = "Receive Date : [" + delivery_from + "]" + " - [" + delivery_to + "]"
        elif current_year - delivery_from_year <= 99:
            row5_info1 = "Receive Date : [" + delivery_from + "]" + " - [_/_/_]"
        elif delivery_to_year <= current_year:
            row5_info1 = "Receive Date : [_/_/_]" + " - [" + delivery_to + "]"
        else:
            row5_info1 = "Receive Date : [_/_/_]" + " - [_/_/_]"
        row5_info2 = ""
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
             ('FONTSIZE', (1, 0), (1, 0), 14),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_header = []
        table_header.append(['Supp. Code', 'Customer PO No.', 'Part No.', 'P/O No.', 'Delivery Date', 'Order Qty', 'GR No.', 'Receive Date', 'Receive Qty'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('ALIGN', (5, 0), (5, 0), 'RIGHT'),
             ('ALIGN', (8, 0), (8, 0), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (5, 0), (5, 0), 20),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, supplier_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN,
                                topMargin=s.REPORT_TOP_MARGIN + 30, bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        # Draw Content of PDF
        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)
        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                   order__status__gte=dict(ORDER_STATUS)['Sent'],
                                                   order__document_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                                delivery_to_obj.strftime('%Y-%m-%d'))) \
            .select_related('order', 'supplier', 'item')\
            .order_by('supplier__code', 'item__code', 'order__document_date')

        po_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])\
            .select_related('order', 'supplier', 'item')

        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(order__supplier_id__in=supp_list)

        m_sup_code = ''
        sup_order_total = sup_receive_total = 0
        order_total = receive_total = 0
        for i, mItem in enumerate(order_item_list):
            if i == 0:
                m_sup_code = mItem.supplier.code

            if m_sup_code != mItem.supplier.code:
                table_data = []
                table_data.append(['', '', '', '', 'Sub Total : ', intcomma("%.2f" % sup_order_total), '', '', intcomma("%.2f" % sup_receive_total)])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('LINEABOVE', (4, 0), (-1, -1), 0.25, colors.black),
                     ('LINEBELOW', (4, 0), (-1, -1), 0.25, colors.black),
                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                     ('ALIGN', (5, 0), (5, 0), 'RIGHT'),
                     ('ALIGN', (8, 0), (8, 0), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (5, 0), (5, 0), 20),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                order_total += sup_order_total
                receive_total += sup_receive_total
                m_sup_code = mItem.supplier.code
                sup_order_total = sup_receive_total = 0

            if m_sup_code == mItem.supplier.code:
                refer_po_item = po_items.filter(order__id=mItem.reference_id, customer_po_no=mItem.customer_po_no,
                                                item_id=mItem.item_id, line_number=mItem.refer_line)

                for item in refer_po_item:
                    refer_po_item_document_number = item.order.document_number
                    refer_po_quantity = item.quantity
                    refer_po_wanted_date = item.wanted_date.strftime("%d/%m/%Y")

                    table_data = []
                    table_data.append([mItem.supplier.code if sup_order_total == 0 else '', mItem.customer_po_no, mItem.item.code,
                                       refer_po_item_document_number, refer_po_wanted_date, intcomma("%.2f" % refer_po_quantity),
                                       mItem.order.document_number, mItem.order.document_date.strftime("%d/%m/%Y"), intcomma("%.2f" % mItem.quantity)])

                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                         ('ALIGN', (5, 0), (5, 0), 'RIGHT'),
                         ('ALIGN', (8, 0), (8, 0), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (5, 0), (5, 0), 20),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                    sup_order_total += item.quantity
                    sup_receive_total += mItem.quantity

            if i == order_item_list.__len__() - 1:
                table_data = []
                table_data.append(['', '', '', '', 'Sub Total : ', intcomma("%.2f" % sup_order_total), '', '', intcomma("%.2f" % sup_receive_total)])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('LINEABOVE', (4, 0), (-1, -1), 0.25, colors.black),
                     ('LINEBELOW', (4, 0), (-1, -1), 0.25, colors.black),
                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                     ('ALIGN', (5, 0), (5, 0), 'RIGHT'),
                     ('ALIGN', (8, 0), (8, 0), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (5, 0), (5, 0), 20),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                order_total += sup_order_total
                receive_total += sup_receive_total
        # Grand Total:
        table_data = []
        table_data.append(['', '', '', '', 'Grand Total : ', intcomma("%.2f" % order_total), '', '', intcomma("%.2f" % receive_total)])

        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('ALIGN', (5, 0), (5, 0), 'RIGHT'),
             ('ALIGN', (8, 0), (8, 0), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (5, 0), (5, 0), 20),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)

        # Create the table
        if len(elements) == 0:
            table_data = []
            table_data.append(['', '', '', '', ''])
            item_table = Table(table_data, colWidths=[30, 65, 130, 155, 150], rowHeights=rowHeights)
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
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), supp_list=supp_list),
                  onLaterPages=partial(self._header_footer, company_id=company_id, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), supp_list=supp_list),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
