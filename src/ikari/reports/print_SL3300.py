from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from django.db.models import Q
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
colWidths = [90, 150, 80, 50, 65, 55, 70]


class Print_SL3300:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, delivery_from, delivery_to, doc_list):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SL3300 Sales / Purchase System"
        row1_info2 = "Sales Order Check List"
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Transaction Code, Document No."
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4th row
        if len(doc_list):
            row4_info1 = "Document No. : [" + doc_list[0] + " ] - [ " + doc_list[-1] + " ] "
        else:
            row4_info1 = "Document No. : [ ] - [ ]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])
        # 5th row
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
        table_header.append(['Document No.', 'Customer Code & Name', '', 'Doc. Date', 'Term', 'Curr', 'Exchange Rate'])
        table_header.append(['Part No.', '', 'S.UOM   Part Grp.', 'Back Qty', 'Order Qty', 'Unit Price', 'Amount(ORG)'])
        table_header.append(['Customer PO No.', 'P/O No.', 'P/O Ln.', '', 'Due Date', 'Sup. Code', 'P/O Gen.'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('SPAN', (1, 0), (2, 0)),
             ('ALIGN', (4, 0), (6, 0), 'RIGHT'),
             ('ALIGN', (4, 1), (6, 1), 'RIGHT'),
             ('ALIGN', (4, 2), (6, 2), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 25, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, document_no, customer_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=160, bottomMargin=42, pagesize=self.pagesize)

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
            .order_by('order__document_number')

        po_refer_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                  order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                  order__document_date__gte=delivery_from_obj.strftime('%Y-%m-%d'))

        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)
        doc_list = eval(document_no)
        if len(doc_list):
            order_item_list = order_item_list.filter(order_id__in=doc_list)
            doc_list = [order_item_list.filter(order_id=doc_list[0]).first().order.document_number,
                        order_item_list.filter(order_id=doc_list[-1]).first().order.document_number]

        so_document_no = ''
        total_qty = total_amount = 0
        for i, mItem in enumerate(order_item_list):
            if so_document_no != mItem.order.document_number:
                so_document_no = mItem.order.document_number
                if total_qty > 0:
                    table_data = []
                    table_data.append(['', '', '', 'Total : ', intcomma("%.2f" % total_qty), '', intcomma("%.2f" % total_amount)])
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
                    total_qty = total_amount = 0

                table_data = []
                table_data.append([
                    mItem.order.document_number,
                    mItem.order.customer.code + '   ' + mItem.order.customer.name[:30], '',
                    mItem.order.document_date.strftime("%d/%m/%Y"),
                    mItem.order.customer.payment_term + ' Days',
                    mItem.order.customer.currency.code,
                    intcomma("%.8f" % mItem.order.exchange_rate)])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('SPAN', (1, 0), (2, 0)),
                     ('ALIGN', (3, 0), (6, 0), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
            if so_document_no == mItem.order.document_number:
                po_refer_item = po_refer_items.filter(reference_id=mItem.order_id, refer_line=mItem.line_number).first()
                table_data = []
                table_data.append([
                    mItem.item.code, '',
                    mItem.item.inv_measure.code if mItem.item.inv_measure else '' +\
                    '   ' + mItem.item.category.code if mItem.item.category else '',
                    intcomma("%.2f" % mItem.bkord_quantity) if mItem.bkord_quantity else intcomma("%.2f" % 0),
                    intcomma("%.2f" % mItem.quantity),
                    intcomma("%.5f" % mItem.price),
                    intcomma("%.2f" % mItem.amount)])
                table_data.append([
                    mItem.customer_po_no[:14],
                    po_refer_item.order.document_number if po_refer_item else '',
                    po_refer_item.line_number if po_refer_item else '', '',
                    po_refer_item.wanted_date.strftime("%d/%m/%Y") if po_refer_item else '',
                    po_refer_item.supplier.code if po_refer_item else '',
                    'Y' if po_refer_item else 'N'])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (3, 0), (6, 0), 'RIGHT'),
                     ('ALIGN', (3, 1), (6, 1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('LEFTPADDING', (0, 0), (0, 0), 5),
                     ('LEFTPADDING', (0, 1), (0, 1), 5),
                     ('LEFTPADDING', (2, 1), (2, 1), 5),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 5),
                     ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                total_qty += mItem.quantity
                total_amount += mItem.amount

            if i == len(order_item_list) - 1:
                table_data = []
                table_data.append(['', '', '', 'Total : ', intcomma("%.2f" % total_qty), '', intcomma("%.2f" % total_amount)])
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
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), doc_list=doc_list),
                  onLaterPages=partial(self._header_footer, company_id=company_id, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), doc_list=doc_list),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
