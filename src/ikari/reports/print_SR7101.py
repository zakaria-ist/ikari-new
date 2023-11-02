from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from items.models import Item
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
import os
from companies.models import Company
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import validate_date_to_from, get_company_name_and_current_period, round_number, get_decimal_place
from functools import partial
from utilities.constants import ORDER_STATUS, ORDER_TYPE

rowHeights = 12


class Print_SR7101:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, part_no, cust_po_list, delivery_from, delivery_to, company_name):
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
        row1_info1 = "SR7101 Sales and Purchase System"
        row1_info2 = "SALES ANALYSIS REPORT BY PART NUMBER"
        row1_info3 = ""
        header_data.append([row1_info1, row1_info2, row1_info3])

        # 2nd row
        row2_info1 = company_name
        row2_info2 = "Grouped by Part No., Currency"
        row2_info3 = ""
        header_data.append([row2_info1, row2_info2, row2_info3])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        row3_info3 = ""

        header_data.append([row3_info1, row3_info2, row3_info3])
        # 4st row
        if len(part_no):
            item1 = Item.objects.get(pk=part_no[0])
            item2 = Item.objects.get(pk=part_no[-1])
            row4_info1 = "Part No.: [" + item1.code + "][" + item2.code + "]"
        else:
            row4_info1 = "Part No.: [][]"
        if len(cust_po_list):
            row4_info2 = "Cust. PO.: [" + cust_po_list[0] + "][" + cust_po_list[-1] + "]"
        else:
            row4_info2 = "Cust. PO.: [][]"
        row4_info3 = ""
        header_data.append([row4_info1, row4_info2, row4_info3])

        header_table = Table(header_data, colWidths=[265, 280, 100], rowHeights=rowHeights)
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
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Part No.', '', '', '', 'Part Descr.', '', '', 'UOM', 'Part Group']
        table_data.append(table_header)
        table_header = ['Document No.', 'Customer', 'Doc. Date', 'Curr', 'Exch. Rate', 'Ln', 'Delivery Qty', 'Unit Price', 'Amount (ORG) Cfm']
        table_data.append(table_header)
        table_header = ['Customer PO No.', '', '', '', '', '', '', '', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[100, 60, 60, 25, 60, 20, 60, 55, 95], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 3), (-1, 3), 0.25, colors.black),
             ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin + 5, doc.height + doc.topMargin - h - h1 - 5)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, cust_po, part_no, is_confirm):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=130, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT, leading=20))

        elements = []
        table_data = []

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)

        stock_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order__order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                              order__document_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                           delivery_to_obj.strftime('%Y-%m-%d'))) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
            .select_related('item', 'order', 'order__customer')\
            .order_by('item__code', 'order__currency', 'order__document_date').distinct()

        cust_po_list = eval(cust_po)
        if len(cust_po_list):
            stock_list = stock_list.filter(customer_po_no__in=cust_po_list)
        part_list = eval(part_no)
        if len(part_list):
            stock_list = stock_list.filter(item_id__in=part_list)

        sum_qty = sum_amount = sum_loc = 0
        sum_all_qty = sum_all_loc = 0
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if stock_list:
            part_num = ''
            for i, item in enumerate(stock_list):
                if item.item.code != '':
                    if part_num != item.item.code and i != 0:
                        decimal_place = get_decimal_place(item.order.currency)
                        table_data.append(
                            ['', '', '',
                             '', '', '', 'Total:' + item.order.currency.code, '',
                             Paragraph(intcomma(decimal_place % round_number(sum_amount)), styles['RightAlignBold']),
                             Paragraph('&nbsp', styles['LeftAlign'])])
                        table_data.append(
                            ['', '', '',
                             '', '', '', 'Total:SGD', '',
                             Paragraph(intcomma(decimal_place_f % round_number(sum_loc)), styles['RightAlignBold']),
                             Paragraph('&nbsp', styles['LeftAlign'])])
                        table_data.append(
                            ['', Paragraph('Part Total', styles['LeftAlignBold']),
                             Paragraph('for Local', styles['LeftAlignBold']), '',
                             '(QTY):', '', Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']), '',
                             Paragraph(intcomma(decimal_place_f % sum_loc), styles['RightAlignBold']),
                             Paragraph('&nbsp', styles['LeftAlign'])])

                        sum_qty = sum_amount = sum_loc = 0

                    if part_num != item.item.code:
                        table_data.append(['', '',  '', '', '', '', '', '', '', ''])
                        table_data.append(
                            [Paragraph(item.item.code, styles['LeftAlignBold']), '', '', '',
                             Paragraph(item.item.short_description if item.item.short_description else '', styles['LeftAlignBold']), '', '',
                             Paragraph(item.item.inv_measure.name if item.item.inv_measure else '', styles['RightAlignBold']),
                             Paragraph(item.item.category.code if item.item.category else '', styles['RightAlignBold']),
                             Paragraph('&nbsp', styles['LeftAlign'])])
                        table_data.append(['', '',  '', '', '', '', '', '', '', ''])

                    part_num = item.item.code
                    decimal_place = get_decimal_place(item.order.currency)
                    table_data.append(
                        [item.order.document_number,
                         item.order.customer.code,
                         item.order.document_date.strftime('%d-%m-%Y'),
                         item.order.currency.code,
                         intcomma("%.8f" % item.order.exchange_rate),
                         Paragraph(str(item.line_number), styles['LeftAlign']),
                         intcomma("%.2f" % item.quantity),
                         intcomma("%.5f" % round_number(item.price, 5)),
                         intcomma(decimal_place % round_number(item.amount)), 'N'])

                    sum_qty += item.quantity
                    sum_amount += item.amount
                    sum_loc += round_number(item.amount * item.order.exchange_rate)
                    sum_all_qty += item.quantity
                    sum_all_loc += round_number(item.amount * item.order.exchange_rate)

                    table_data.append(
                        [item.customer_po_no if item.customer_po_no else '' +
                         ('-' + str(
                             item.refer_line)) if item.refer_line else '', '',
                         '', '', '', '', '', '', ''])

            if stock_list.__len__() - 1 == i:
                decimal_place = get_decimal_place(item.order.currency)
                table_data.append(
                    ['', '', '',
                        '', '', '', 'Total:' + item.order.currency.code, '',
                        Paragraph(intcomma(decimal_place % round_number(sum_amount)), styles['RightAlignBold']),
                        Paragraph('&nbsp', styles['LeftAlign'])])
                table_data.append(
                    ['', '', '',
                        '', '', '', 'Total:SGD', '',
                        Paragraph(intcomma(decimal_place_f % round_number(sum_loc)), styles['RightAlignBold']),
                        Paragraph('&nbsp', styles['LeftAlign'])])
                table_data.append(
                    ['', Paragraph('Part Total', styles['LeftAlignBold']),
                        Paragraph('for Local', styles['LeftAlignBold']), '',
                        '(QTY):', '', Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']), '',
                        Paragraph(intcomma(decimal_place_f % sum_loc), styles['RightAlignBold']),
                        Paragraph('&nbsp', styles['LeftAlign'])])

                table_data.append(['', '',  '', '', '', '', '', '', '', ''])

                table_data.append(
                    ['', Paragraph('Grand Total', styles['LeftAlignBold']),
                        Paragraph('for Local', styles['LeftAlignBold']), '',
                        '(QTY):', '', Paragraph(intcomma("%.2f" % sum_all_qty), styles['RightAlignBold']), '',
                        Paragraph(intcomma(decimal_place_f % sum_all_loc), styles['RightAlignBold']),
                        Paragraph('&nbsp', styles['LeftAlign'])])
        else:
            table_data.append(['', '',  '', '', '', '', '', '', '', ''])
        # Create the table
        item_table = Table(table_data, colWidths=[100, 60, 60, 25, 60, 20, 60, 55, 80, 15], rowHeights=rowHeights)
        if table_data.__len__() > 1:
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
        else:
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ]))
        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, part_no=part_list, cust_po_list=cust_po_list, delivery_from=delivery_from_obj.strftime('%Y-%m-%d'),
                                      delivery_to=delivery_to_obj.strftime('%Y-%m-%d'), company_name=company_name),
                  onLaterPages=partial(self._header_footer, part_no=part_list, cust_po_list=cust_po_list, delivery_from=delivery_from_obj.strftime('%Y-%m-%d'),
                                       delivery_to=delivery_to_obj.strftime('%Y-%m-%d'), company_name=company_name),
                  canvasmaker=partial(NumberedPage, adjusted_height=95))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
