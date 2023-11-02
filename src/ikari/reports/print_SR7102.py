from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from items.models import ItemCategory
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from django.utils.dateparse import parse_date
import os
from companies.models import Company
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import validate_date_to_from, get_company_name_and_current_period, round_number, get_decimal_place
from functools import partial
from utilities.constants import ORDER_STATUS, ORDER_TYPE


colWidths = [85, 50, 60, 25, 80, 20, 65, 60, 80, 20]
rowHeights = 12


class Print_SR7102:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, pg_list, delivery_from, delivery_to, company_name):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT))

        # Draw header of PDF
        #  order = Order.objects.get(pk=customer_code)
        # if order:
        # 1st row
        header_data = []
        row1_info1 = "SR7102 Sales and Purchase System"
        row1_info2 = "SALES ANALYSIS REPORT BY PART GROUP"
        row1_info3 = ""
        header_data.append([row1_info1, row1_info2, row1_info3])

        # 2nd row
        row2_info1 = company_name
        row2_info2 = "Grouped by Part Group, Currency"
        row2_info3 = ""
        header_data.append([row2_info1, row2_info2, row2_info3])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        row3_info3 = ""

        header_data.append([row3_info1, row3_info2, row3_info3])
        # 4st row
        if len(pg_list):
            item0 = ItemCategory.objects.get(pk=pg_list[0]).code
            item1 = ItemCategory.objects.get(pk=pg_list[-1]).code
            row4_info1 = "Part Group: [ " + item0 + " ][ " + item1 + " ]"
        else:
            row4_info1 = "Part Group: [ ][ ]"

        row4_info2 = ""
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
        header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Part Group', '', 'Group Description', '', '', '', '', '', '', '']
        table_data.append(table_header)
        table_header = ['Document No.', 'Customer', 'Doc. Date', 'Curr', 'Exchange Rate', 'Ln', 'Delivery Qty',
                        'Unit Price', 'Amount (ORG)', 'Cfm']
        table_data.append(table_header)
        table_header = ['Customer PO No.', '', 'Part No.', '', '', '', '', '', '', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 3), (-1, 3), 0.25, colors.black),
             ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - h1 - 5)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, part_group):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=130, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
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
            .order_by('item__category__code', 'order__currency__code').distinct()

        pg_list = eval(part_group)
        if len(pg_list):
            stock_list = stock_list.filter(item__category_id__in=pg_list)

        sum_qty = sum_amount = sum_loc = 0
        sum_all_qty = sum_all_loc = 0
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if stock_list:
            part_code = ''
            m_currency = company.currency
            for i, item in enumerate(stock_list):
                if item.item.category and item.item.category.code != part_code:
                    part_code = item.item.category.code
                    if i != 0:
                        decimal_place = get_decimal_place(m_currency)
                        table_data = []
                        table_data.append(
                            ['', '', '', '', '', '', '', Paragraph('Total for ' + m_currency.code, styles['RightAlign']),
                             Paragraph(intcomma(decimal_place % round_number(sum_amount)), styles['RightAlign']),
                             Paragraph('&nbsp', styles['LeftAlign'])])
                        table_data.append(
                            ['', '', '', '', '', '',  '', Paragraph('Total for ' + company.currency.code, styles['RightAlign']),
                             Paragraph(intcomma(decimal_place_f % round_number(sum_loc)), styles['RightAlign']),
                             Paragraph('&nbsp', styles['LeftAlign'])])
                        table_data.append(['', '',  '', '', '', '', '', '', '', ''])
                        table_data.append(
                            ['', '', '', Paragraph('Group Total (Loc):', styles['RightAlignBold']), '', '',
                             Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']), '',
                             Paragraph(intcomma(decimal_place_f % round_number(sum_loc)), styles['RightAlignBold']), Paragraph('&nbsp', styles['LeftAlign'])])
                        table_data.append(['', '',  '', '', '', '', '', '', '', ''])

                        sum_qty = sum_amount = sum_loc = 0
                        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('SPAN', (3, 3), (5, 3)),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('TOPPADDING', (0, 0), (-1, -1), 0),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)

                    table_data = []
                    table_data.append(
                        [item.item.category.code, '', item.item.category.name, '', '', '', '', '', '', Paragraph('&nbsp', styles['LeftAlign'])])
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('SPAN', (2, 0), (4, 0)),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                m_currency = item.order.currency
                decimal_place = get_decimal_place(m_currency)
                table_data = []
                table_data.append(
                    [item.order.document_number,
                     item.order.customer.code,
                     item.order.document_date,
                     item.order.currency.code,
                     intcomma("%.8f" % item.order.exchange_rate),
                     item.line_number,
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
                     ('-' + str(item.refer_line)) if item.refer_line else '', '', item.item.code, '', '', '', '', '', '', ''])
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 5),
                     ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)

            if stock_list.__len__() - 1 == i:
                decimal_place = get_decimal_place(m_currency)
                table_data = []
                table_data.append(['', '', '', '', '', '', '', Paragraph('Total for ' + m_currency.code, styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place % round_number(sum_amount)), styles['RightAlign']),
                                   Paragraph('&nbsp', styles['LeftAlign'])])

                table_data.append(['', '', '', '', '', '', '', Paragraph('Total for ' + company.currency.code, styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place_f % round_number(sum_loc)), styles['RightAlign']),
                                   Paragraph('&nbsp', styles['LeftAlign'])])

                table_data.append(['', '',  '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', Paragraph('Group Total (Loc):', styles['RightAlignBold']), '', '',
                                   Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']), '',
                                   Paragraph(intcomma(decimal_place_f % round_number(sum_loc)), styles['RightAlignBold']),
                                   Paragraph('&nbsp', styles['LeftAlign'])])

                table_data.append(['', '',  '', '', '', '', '', '', '', ''])

                table_data.append(['', '', '', Paragraph('Grand Total (Loc):', styles['RightAlignBold']), '', '',
                                   Paragraph(intcomma("%.2f" % sum_all_qty), styles['RightAlignBold']), '',
                                   Paragraph(intcomma(decimal_place_f % round_number(sum_all_loc)), styles['RightAlignBold']),
                                   Paragraph('&nbsp', styles['LeftAlign'])])

                sum_qty = sum_amount = sum_loc = 0
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('SPAN', (3, 3), (5, 3)),
                     ('SPAN', (3, 5), (5, 5)),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
        else:
            table_data = []
            table_data.append(['', '',  '', '', '', '', '', '', '', ''])
            # Create the table
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
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
            elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, pg_list=pg_list, delivery_from=delivery_from_obj.strftime('%Y-%m-%d'),
                                      delivery_to=delivery_to_obj.strftime('%Y-%m-%d'), company_name=company_name),
                  onLaterPages=partial(self._header_footer, pg_list=pg_list, delivery_from=delivery_from_obj.strftime('%Y-%m-%d'),
                                       delivery_to=delivery_to_obj.strftime('%Y-%m-%d'), company_name=company_name),
                  canvasmaker=partial(NumberedPage, adjusted_height=95))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
