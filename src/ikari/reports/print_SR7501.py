from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from django.db.models import Q
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import round_number, get_decimal_place
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

colWidths = [140, 140, 90, 90, 90]
rowHeights = 12


class Print_SR7501:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, issue_to, issue_from, supplier_list, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR7501 Sales and Purchase System"
        row1_info2 = "GOODS RECEIVE DETAIL REPORT BY Supplier"
        header_data.append([row1_info1, row1_info2])

        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Supplier"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if issue_from is not '0':
            current_period = datetime.datetime.strptime(issue_from, '%Y-%m-%d')
        row4_info1 = "Transaction Code : []"
        row4_info2 = "Current Period : [" + current_period.strftime("%B %Y") + "]" if issue_from is not '0' else ''
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[265, 270], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('ALIGN', (1, 3), (1, 3), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Supplier Code & Name', '', '', '', 'Supplier Currency']
        table_data.append(table_header)
        table_header = ['Part No.', 'Customer PO No.', 'Received Qty', 'Amount(ORG)', 'Amount(LOC)']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (4, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 1), (4, 1), 0.25, colors.black),
             ('ALIGN', (0, 0), (1, 0), 'LEFT'),
             ('ALIGN', (0, 1), (1, 1), 'LEFT'),
             ('ALIGN', (2, 0), (4, 0), 'RIGHT'),
             ('ALIGN', (2, 1), (4, 1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 5, doc.height + doc.topMargin - h - h1)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, supplier_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN + 15, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN,
                                pagesize=self.pagesize)

        elements = []

        if issue_from is not '0' and issue_to is not '0':
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(issue_from, issue_to)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')
        elif issue_from is not '0':
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(issue_from)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')
        elif issue_to is not '0':
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(issue_to)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')
        else:
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')

        supplier_list = eval(supplier_no)
        if len(supplier_list):
            supplier_item_list = supplier_item_list.filter(supplier_id__in=supplier_list)

        s_code = i_code = ''
        cust_po_no = ''
        item_quantity = item_amount = item_amount_loc = 0
        sup_quantity = sup_amount = sup_amount_loc = 0
        total_quantity = total_amount = total_amount_loc = 0
        decimal_place = "%.2f"
        for i, mItem in enumerate(supplier_item_list):
            # check to print first row of code
            if i == 0:
                s_code = mItem.supplier.code
                i_code = mItem.item.code
                cust_po_no = mItem.customer_po_no
                decimal_place = get_decimal_place(mItem.supplier.currency)
                table_data = []
                table_data.append([s_code, mItem.supplier.name if mItem.supplier.name else '', '', '', mItem.supplier.currency.code])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (4, 0), 'RIGHT'),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)

            if s_code != mItem.supplier.code:
                # Print part total
                if item_quantity > 0:
                    table_data = []
                    table_data.append([i_code, cust_po_no, intcomma("%.2f" % item_quantity),
                                       intcomma(decimal_place % round_number(item_amount)), intcomma(decimal_place % round_number(item_amount_loc))])

                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                item_quantity = item_amount = item_amount_loc = 0
                i_code = mItem.item.code

                table_data = []
                table_data.append(['', 'Supplier Total :', intcomma("%.2f" % sup_quantity),
                                   intcomma(decimal_place % round_number(sup_amount)), intcomma(decimal_place % round_number(sup_amount_loc))])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('LINEBELOW', (0, 0), (4, 0), 0.25, colors.black),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                sup_quantity = sup_amount = sup_amount_loc = 0
                s_code = mItem.supplier.code

                table_data = []
                table_data.append([s_code, mItem.supplier.name if mItem.supplier.name else '', '', '', mItem.supplier.currency.code])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (4, 0), 'RIGHT'),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)

            # check to print next row of code
            if s_code == mItem.supplier.code:
                if i_code != mItem.item.code:
                    if item_quantity > 0:
                        table_data = []
                        table_data.append([i_code, cust_po_no, intcomma("%.2f" % item_quantity),
                                           intcomma(decimal_place % round_number(item_amount)), intcomma(decimal_place % round_number(item_amount_loc))])
                        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                    item_quantity = item_amount = item_amount_loc = 0
                    i_code = mItem.item.code
                    cust_po_no = mItem.customer_po_no

                if i_code == mItem.item.code:
                    if cust_po_no != mItem.customer_po_no:
                        if item_quantity > 0:
                            table_data = []
                            table_data.append([i_code, cust_po_no, intcomma("%.2f" % item_quantity),
                                               intcomma(decimal_place % round_number(item_amount)), intcomma(decimal_place % round_number(item_amount_loc))])

                            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                    ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                    ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ]))
                            elements.append(item_table)
                        item_quantity = item_amount = item_amount_loc = 0
                        i_code = mItem.item.code
                        cust_po_no = mItem.customer_po_no

                    if cust_po_no == mItem.customer_po_no:
                        exchange_rate = mItem.order.exchange_rate if mItem.order else 1
                        cust_po_no = mItem.customer_po_no
                        item_quantity += mItem.quantity
                        item_amount += mItem.amount
                        item_amount_loc += round_number(mItem.amount * exchange_rate)
                        sup_quantity += mItem.quantity
                        sup_amount += mItem.amount
                        sup_amount_loc += round_number(mItem.amount * exchange_rate)
                        total_quantity += mItem.quantity
                        total_amount += mItem.amount
                        total_amount_loc += round_number(mItem.amount * exchange_rate)

                        decimal_place = get_decimal_place(mItem.supplier.currency)

            if i == supplier_item_list.__len__() - 1:
                # Print last row part No Total
                if item_quantity > 0:
                    table_data = []
                    table_data.append([i_code, cust_po_no, intcomma("%.2f" % item_quantity),
                                       intcomma(decimal_place % round_number(item_amount)), intcomma(decimal_place % round_number(item_amount_loc))])

                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                table_data = []
                table_data.append(['', 'Supplier Total :', intcomma("%.2f" % sup_quantity),
                                   intcomma(decimal_place % round_number(sup_amount)), intcomma(decimal_place % round_number(sup_amount_loc))])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('LINEBELOW', (0, 0), (4, 0), 0.25, colors.black),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)

        # Print Grand Total
        table_data = []
        table_data.append(['', '', '', '', ''])
        table_data.append(['', 'Grand Total :', intcomma("%.2f" % total_quantity),
                           intcomma(decimal_place % round_number(total_amount)), intcomma(decimal_place % round_number(total_amount_loc))])

        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '']]
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]))
            elements.append(item_table)

        doc.build(elements, onFirstPage=partial(self._header_footer, issue_to=str(issue_to), issue_from=str(issue_from),
                                                supplier_list=supplier_list, company_id=company_id),
                  onLaterPages=partial(self._header_footer, issue_to=str(issue_to), issue_from=str(issue_from),
                                       supplier_list=supplier_list, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=110))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
