from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from reportlab.lib.pagesizes import A4, landscape
from django.db.models import Q
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial
from utilities.common import round_number, get_decimal_place

rowHeights = 20
colWidths = [95, 30, 80, 70, 25, 105, 130, 60, 70, 70, 70]


class Print_SR7603:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, wanted_from, wanted_to, issue_from, issue_to, pt_list, doc_list, cust_list, po_list, company_id, sort_by):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR7603 Sales and Purchase System"
        row1_info2 = ""
        row1_info3 = ""
        row1_info4 = "SALES ORDER ISSUED REPORT"
        header_data.append([row1_info1, row1_info2, row1_info3, row1_info4])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = ""
        row2_info3 = ""
        if sort_by == 'customer':
            row2_info4 = "Sorting Order: [CUSTOMER CODE]"
        elif sort_by == 'document':
            row2_info4 = "Sorting Order: [DOCUMENT NUMBER]"
        elif sort_by == 'customer_po':
            row2_info4 = "Sorting Order: [CUSTOMER PO NO]"
        elif sort_by == 'part_no':
            row2_info4 = "Sorting Order: [PART NO]"
        elif sort_by == 'wanted_date':
            row2_info4 = "Sorting Order: [WANTED DATE]"
        header_data.append([row2_info1, row2_info2, row2_info3, row2_info4])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        row3_info3 = ""
        row3_info4 = ""
        header_data.append([row3_info1, row3_info2, row3_info3, row3_info4])

        row4_info1 = "Transaction Code : [SALES ORDER]"
        if len(doc_list):
            row4_info2 = "Document No: [ " + doc_list[0] + " ] - [ " + doc_list[-1] + " ]"
        else:
            row4_info2 = "Document No: [] - []"

        row4_info3 = "Issued Date : [" + issue_from + "] - [" + issue_to + "]"

        row4_info4 = ''
        header_data.append([row4_info1, row4_info2, row4_info3, row4_info4])

        if len(cust_list):
            row5_info1 = "Customer Code : [ " + cust_list[0] + " ] - [ " + cust_list[-1] + " ]"
        else:
            row5_info1 = "Customer Code : [] - []"
        if len(po_list):
            row5_info2 = "Cus PO No : [ " + po_list[0] + " ] - [ " + po_list[-1] + " ]"
        else:
            row5_info2 = "Cus PO No : [] - []"

        row5_info3 = "Delivery Date : [" + wanted_from + "] - [" + wanted_to + "]"

        row5_info4 = ''
        header_data.append([row5_info1, row5_info2, row5_info3, row5_info4])

        header_table = Table(header_data, colWidths=[290, 270, 150, 100])

        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (-1, 0), (-1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (3, 0), (3, 0), s.REPORT_FONT_BOLD),
             ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
             ('BOTTOMPADDING', (0, 2), (-1, 2), 10),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_header = ['Customer Code', 'Curr', 'Exch. Rate', 'Doc.Date', 'Trn', 'Document No./Ln', 'Part No.',
                        'Del. Date', 'Order Qty', 'Unit Price', 'Amount']
        table_data.append(table_header)
        # 2ND ROW
        table_header = ['Customer Name', '', '', '', '', 'Customer PO No.', 'Part Description', '', '', '', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (8, 0), (-1, 0), 'RIGHT'),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (1, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 5, doc.height + doc.topMargin - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, wanted_from, wanted_to, customer_code, document_no, customer_po, part_no, sort_by):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=185, bottomMargin=42, pagesize=landscape(A4))

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        elements = []
        table_data = []

        order_by = "order__customer__code"
        if sort_by == 'customer':
            order_by = "order__customer__code"
        elif sort_by == 'document':
            order_by = "order__document_number"
        elif sort_by == 'customer_po':
            order_by = "customer_po_no"
        elif sort_by == 'part_no':
            order_by = "item__code"
        elif sort_by == 'wanted_date':
            order_by = "wanted_date"
        # get delivery date
        if issue_from is not '0' and issue_to is not '0':
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                       order__document_date__range=(issue_from, issue_to)
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)
        elif issue_from is not '0':
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                       order__document_date__gte=(issue_from)
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)
        elif issue_to is not '0':
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                       order__document_date__lte=(issue_to)
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)
        else:
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER']
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)

        if wanted_from is not '0' and wanted_to is not '0':
            order_item_list = order_item_list.filter(wanted_date__range=(wanted_from, wanted_to))
        if wanted_from is not '0':
            order_item_list = order_item_list.filter(wanted_date__gte=wanted_from)
        if wanted_to is not '0':
            order_item_list = order_item_list.filter(wanted_date__lte=wanted_to)

        cust_list = eval(customer_code)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)
            cust_list = [order_item_list.filter(order__customer_id=cust_list[0]).first().order.customer.code, 
                        order_item_list.filter(order__customer_id=cust_list[-1]).first().order.customer.code]
        doc_list = eval(document_no)
        if len(doc_list):
            order_item_list = order_item_list.filter(order_id__in=doc_list)
            doc_list = [order_item_list.filter(order_id=doc_list[0]).first().order.document_number, 
                        order_item_list.filter(order_id=doc_list[-1]).first().order.document_number]
        pt_list = eval(part_no)
        if len(pt_list):
            order_item_list = order_item_list.filter(item_id__in=pt_list)
            pt_list = [order_item_list.filter(item_id=pt_list[0]).first().item.code, 
                        order_item_list.filter(item_id=pt_list[-1]).first().item.code]
        po_list = eval(customer_po)
        if len(po_list):
            order_item_list = order_item_list.filter(id__in=po_list)
            po_list = [order_item_list.get(id=po_list[0]).customer_po_no, 
                        order_item_list.get(id=po_list[-1]).customer_po_no]

        sum_qty = 0
        for i, mItem in enumerate(order_item_list):
            decimal_place = get_decimal_place(mItem.order.currency)
            table_data = []
            table_data.append([mItem.order.customer.code if mItem.order.customer_id else '',
                               mItem.order.currency.code if mItem.order.currency_id else '',
                               intcomma("%.8f" % mItem.order.exchange_rate),
                               mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ',
                               'S/O', mItem.order.document_number + '   ' + str(mItem.line_number),
                               mItem.item.code if mItem.item_id else '', mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ',
                               intcomma("%.2f" % mItem.quantity) if mItem.quantity else '',
                               intcomma("%.5f" % mItem.price) if mItem.price else '',
                               intcomma(decimal_place % round_number(mItem.amount)) if mItem.amount else ''])

            sum_qty += mItem.quantity

            table_data.append([mItem.order.customer.name if mItem.order.customer_id else '', '', '', '', '',
                               mItem.customer_po_no, mItem.item.short_description if mItem.item.short_description else '', '', '', '', ''])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                    ('SPAN', (0, 1), (4, 1)),
                    ('ALIGN', (8, 0), (-1, 0), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (1, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ]))
            elements.append(item_table)

        table_data = []
        table_data.append(['', '', '', '', '', '', Paragraph('Grand Total:', styles['RightAlignBold']), '',
                           Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']), '', ''])

        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('TOPPADDING', (1, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ]))
        elements.append(item_table)
        if table_data.__len__() == 0:
            table_data = []
            table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

            # Create the table
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ('TOPPADDING', (1, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ]))
            elements.append(item_table)

        issue_from = formate_date(issue_from)
        issue_to = formate_date(issue_to)
        wanted_from = formate_date(wanted_from)
        wanted_to = formate_date(wanted_to)

        doc.build(elements, onFirstPage=partial(self._header_footer, wanted_from=wanted_from,
                                                wanted_to=wanted_to, issue_from=issue_from,
                                                issue_to=issue_to, pt_list=pt_list,
                                                doc_list=doc_list,
                                                cust_list=cust_list, po_list=po_list, company_id=company_id, sort_by=sort_by),
                  onLaterPages=partial(self._header_footer, wanted_from=wanted_from,
                                       wanted_to=wanted_to, issue_from=issue_from,
                                       issue_to=issue_to, pt_list=pt_list,
                                                doc_list=doc_list,
                                                cust_list=cust_list, po_list=po_list, company_id=company_id, sort_by=sort_by),
                  canvasmaker=partial(NumberedPage, adjusted_height=-155, adjusted_width=255))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


def formate_date(date_obj):
    if date_obj != '0':
        date_obj = date_obj.split('-')
        date_obj.reverse()
        date_obj = '/'.join(date_obj)
    else:
        date_obj = ' / / '

    return date_obj
