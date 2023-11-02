from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from django.db.models import Q
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import round_number, get_decimal_place
from items.models import Item
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

rowHeights = 12


class Print_SR7503:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, issue_to, issue_from, part_list, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT))
        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR7503 Sales and Purchase System"
        row1_info2 = "GOODS RECEIVE DETAIL REPORT BY PART NUMBER"
        header_data.append([row1_info1, row1_info2])

        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Part No., Currency"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if len(part_list):
            item1 = Item.objects.get(pk=part_list[0])
            item2 = Item.objects.get(pk=part_list[-1])
            row4_info1 = "Part No: [" + item1.code + "][" + item2.code + "]"
        else:
            row4_info1 = "Part No: [][]"

        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[265, 270], rowHeights=rowHeights)
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
        header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Part No.', '', '', '', '', 'Part Description  ', '', '', '', 'UOM', 'Part Group', '', '']
        table_data.append(table_header)
        table_header = ['S.No', 'Document No', 'Supplier', 'Doc.Date', 'Curr', 'Exchange Rate', '', 'Ln',
                        'Received Qty', 'Unit Price', 'Amount(ORG)', '  Cfm']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[25, 80, 45, 50, 35, 65, 5, 22, 73, 60, 60, 10], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (9, 0), (9, 0), 'CENTER'),
             ('ALIGN', (4, -1), (5, -1), 'RIGHT'),
             ('ALIGN', (3, 1), (3, 1), 'RIGHT'),
             ('ALIGN', (4, 0), (5, 0), 'CENTER'),
             ('ALIGN', (10, 0), (-1, 0), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 15, doc.height + doc.topMargin - h - h1)

        table_data = []
        table_header1 = ['', 'Customer PO No.', '', 'Tx Curr', 'Tx Exchange Rate', '', '', '', '', '']
        table_data.append(table_header1)

        item_header_table = Table(table_data, colWidths=[25, 95, 85, 40, 70, 20, 60, 50, 40, 55], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
             ('ALIGN', (2, -1), (2, -1), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 15, doc.height + doc.topMargin - 90)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, customer_po, part_group, part_no, is_confirm):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=130, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        elements = []

        company = Company.objects.get(id=company_id)
        if issue_from is not '0' and issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(issue_from, issue_to)
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')
        elif issue_from is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(issue_from)
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')
        elif issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(issue_to)
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')
        else:
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')

        cust_po_list = eval(customer_po)
        if len(cust_po_list):
            customer_item_list = customer_item_list.filter(customer_po_no__in=cust_po_list)
        group_list = eval(part_group)
        if len(group_list):
            customer_item_list = customer_item_list.filter(item__category__id__in=group_list)
        part_list = eval(part_no)
        if len(part_list):
            customer_item_list = customer_item_list.filter(item_id__in=part_list)

        m_code = ''
        seq = 0
        doc_qty = doc_amount = doc_tax_amount = 0  # sum qty of each Order
        sum_qty = sum_amount = 0

        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)

        if is_confirm == 'Y':  # pgrh_updfg
            customer_item_list = customer_item_list.filter(order__is_confirm=is_confirm)
        if customer_item_list:
            for i, mItem in enumerate(customer_item_list):
                # check to print first row of code
                if m_code != mItem.item.code:
                    # Start new part no Total
                    table_data = []
                    m_code = mItem.item.code
                    doc_qty = doc_amount = 0
                    doc_tax_amount = 0
                    seq = 0

                    table_data.append([Paragraph(mItem.item.code if mItem.item.code else '', styles["LeftAlign"]),
                                       Paragraph(mItem.item.short_description if mItem.item.short_description else '', styles["LeftAlign"]),
                                       Paragraph(mItem.item.purchase_measure.code if mItem.item.purchase_measure else '', styles["LeftAlign"]),
                                       Paragraph(mItem.item.category.code if mItem.item.category else '', styles["LeftAlign"])])

                    item_table = Table(table_data, colWidths=[220, 200, 60, 70], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                # check to print next row of code
                if m_code == mItem.item.code:
                    exchange_rate = mItem.order.exchange_rate if mItem.order else 1

                    doc_qty += mItem.quantity
                    sum_qty += mItem.quantity
                    doc_amount += mItem.amount
                    sum_amount += round_number(mItem.amount * exchange_rate)
                    doc_tax_amount += round_number(mItem.amount * exchange_rate)
                    seq += 1
                    decimal_place = get_decimal_place(mItem.order.currency)
                    table_data = []
                    if not mItem.price:
                        mItem.price = 0
                    table_data.append([seq, Paragraph(mItem.order.document_number if mItem.order.document_number else '', styles["LeftAlign"]),
                                       mItem.supplier.code if mItem.supplier_id else ' / / ',
                                       mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ',
                                       Paragraph(mItem.order.currency.code if mItem.order.currency_id else ' / / ', styles["RightAlign"]),
                                       Paragraph(intcomma("%.8f" % exchange_rate), styles["RightAlign"]),
                                       mItem.line_number, intcomma("%.2f" % mItem.quantity),
                                       intcomma("%.5f" % mItem.price), intcomma(decimal_place % round_number(mItem.amount)), '  N'])  # rate

                    item_table = Table(table_data, colWidths=[25, 80, 55, 50, 25, 60, 20, 65, 65, 75, 20], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (6, 0), (-1, 0), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                    table_data = []
                    table_data.append(['', mItem.customer_po_no, '',
                                       Paragraph(company.currency.code if company.currency.id else '', styles["LeftAlign"]),
                                       Paragraph(intcomma("%.8f" % exchange_rate), styles["LeftAlign"]), '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=[60, 95, 65, 33, 78, 20, 60, 50, 40, 50], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                if m_code == mItem.item.code and i + 1 < customer_item_list.__len__():
                    if (customer_item_list[i + 1].item.code != mItem.item.code):
                        decimal_place = get_decimal_place(mItem.order.currency)
                        item_table = self.print_Total_For(company, doc_amount, doc_tax_amount, item_table, mItem,
                                                          styles)
                        elements.append(item_table)

                        item_table = self.print_PartTotal(doc_qty, doc_tax_amount, styles, decimal_place)
                        elements.append(item_table)

                if i == customer_item_list.__len__() - 1:
                    # Print last row customer and part No Total
                    item_table = self.print_Total_For(company, doc_amount, doc_tax_amount, item_table, mItem,
                                                      styles)
                    elements.append(item_table)
                    decimal_place = get_decimal_place(mItem.order.currency)
                    item_table = self.print_PartTotal(doc_qty, doc_tax_amount, styles, decimal_place)
                    elements.append(item_table)

                    item_table = self.print_GrandTotal(doc_qty, doc_tax_amount, item_table, styles, sum_amount, sum_qty, decimal_place_f)
                    elements.append(item_table)
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '']]
            item_table = Table(table_data, colWidths=[30, 70, 25, 70, 60, 50, 45, 50, 60, 65], rowHeights=rowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]))
            elements.append(item_table)

        doc.build(elements, onFirstPage=partial(self._header_footer, issue_to=str(issue_to), issue_from=str(issue_from),
                                                part_list=part_list, company_id=company_id),
                  onLaterPages=partial(self._header_footer, issue_to=str(issue_to), issue_from=str(issue_from),
                                       part_list=part_list, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def print_GrandTotal(self, doc_qty, doc_tax_amount, item_table, styles, sum_amount, sum_qty, decimal_place):
        table_data = []
        table_data.append([Paragraph('Grand Total For Local: (QTY):', styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']),
                           Paragraph(intcomma(decimal_place % round_number(sum_amount)), styles['RightAlignBold'])])

        table_data.append(['', '', ''])
        # Create the table
        item_table = Table(table_data, colWidths=[295, 140, 70], rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('FONTSIZE', (0, -1), (-1, -1), 3),
             ]))
        return item_table

    def print_PartTotal(self, doc_qty, doc_tax_amount, styles, decimal_place):
        # Print CUSTOMER PO Total
        table_data = []
        table_data.append(
            [Paragraph('Part Total For Local: (QTY):', styles['RightAlignBold']),
             Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']),
             Paragraph(intcomma(decimal_place % round_number(doc_tax_amount)), styles['RightAlignBold']),
             ])
        table_data.append(['', '', ''])
        # Create the table
        item_table = Table(table_data, colWidths=[290, 140, 70], rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (-1, 1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        return item_table

    def print_Total_For(self, company, doc_amount, doc_tax_amount, item_table, mItem, styles):
        decimal_place = get_decimal_place(mItem.order.currency)
        decimal_place_f = get_decimal_place(company.currency)
        table_data = []
        table_data.append(['', Paragraph('Total For:', styles["LeftAlign"]), Paragraph(mItem.order.currency.code, styles["LeftAlign"]),
                           Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles["RightAlign"])])

        table_data.append(['', Paragraph('Total For:', styles["LeftAlign"]),
                           Paragraph(company.currency.code if company.currency.id else '', styles["LeftAlign"]),
                           Paragraph(intcomma(decimal_place_f % round_number(doc_tax_amount)), styles["RightAlign"])])

        item_table = Table(table_data, colWidths=[310, 50, 50, 90], rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (-1, 1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        return item_table
