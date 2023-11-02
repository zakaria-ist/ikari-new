from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
import datetime
import calendar
from django.conf import settings as s
from django.db.models import F, Sum
from customers.models import Customer
from items.models import Item
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from utilities.constants import ORDER_TYPE
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from currencies.models import Currency
from functools import partial
from utilities.common import get_company_name_and_current_period, get_customer_filter_range, round_number, get_decimal_place

colWidths = [60, 168, 70, 70, 70, 70, 70]
rowHeights = 12


def remove_none(param):
    if param is None or param == 'None' or param == 'none':
        param = ''
    return param


class Print_SR7602:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, month, year, cst_list, company_name):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1ST row
        header_data = []
        row1_info1 = "SR7602 Sales and Purchase System"
        row1_info2 = "MONTHLY SALES REPORT BY CUSTOMER"
        header_data.append([row1_info1, row1_info2])

        # 2ND row
        row2_info1 = company_name
        row2_info2 = "Group By Customer Code & Part Group, Part Number"
        header_data.append([row2_info1, row2_info2])
        # 3RD row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        try:
            row3_info2 = "Month: " + datetime.datetime.now().strftime(month + '/' + year)
        except:
            row3_info2 = "Month: " + datetime.datetime.now().strftime('%m/%Y')
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if len(cst_list):
            item0 = Customer.objects.get(pk=cst_list[0]).code
            item1 = Customer.objects.get(pk=cst_list[-1]).code
            row5_info1 = "Customer Code : [" + item0 + "] - [" + item1 + "]"
        else:
            row5_info1 = "Customer Code : [] - []"
        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[265, 313], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('ALIGN', (1, 2), (1, 2), 'CENTER'),
             ('LEFTPADDING', (1, 2), (1, 2), 80),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Customer Code / Name', '', '', '', '', '', '']
        table_data.append(table_header)
        table_header = ['Part Group / Description', '', '', '', '', 'Ratio', 'UOM']
        table_data.append(table_header)
        table_header = ['Part No.', '', 'Order Qty', 'Sales Qty', 'Return Qty', 'Net Qty', 'Total Qty']
        table_data.append(table_header)
        table_header = ['', 'Currency', 'Amount', 'Amount', 'Amount', 'Amount', 'Amount']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[70, 158, 70, 70, 70, 70, 70], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 1), (0, 1), 10),
             ('LEFTPADDING', (0, 2), (0, 2), 20),
             ('SPAN', (0, 0), (1, 0)),
             ('SPAN', (0, 1), (1, 1)),
             ('SPAN', (0, 2), (1, 2)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, month, year, print_selection, customer_code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=17, leftMargin=17, topMargin=140, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))

        elements = []
        style_custcode = [('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                          ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                          ('LEFTPADDING', (0, 0), (-1, -1), 0),
                          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                          ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]

        style_partgp = [('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('LEFTPADDING', (0, -1), (0, -1), 10),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]

        style_body = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                      ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                      ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                      ('LEFTPADDING', (0, 0), (-1, -1), 0),
                      ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                      ('LEFTPADDING', (0, 0), (0, 0), 20),
                      ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]

        style_subtotal = [('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                          ('LEFTPADDING', (0, 0), (-1, -1), 0),
                          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                          ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]

        style_grandtotal = [('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, 0), 10),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]

        # Draw Content of PDF
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        part_item = Item.objects.filter(company_id=company_id, is_hidden=0)
        category_list = part_item.values_list('category__code', flat=True).distinct().order_by('category')

        if print_selection == 'A':
            orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__document_date__range=(first_day, last_day),
                                                      order__order_type__in=(dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['SALES INVOICE']),
                                                      item__category__code__in=category_list)\
                .select_related('order', 'item', 'order__currency', 'order__customer')
        else:
            orderitem_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__document_date__range=(first_day, last_day), order__is_confirm=print_selection,
                                                      order__order_type__in=(dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['SALES INVOICE']),
                                                      item__category__code__in=category_list)\
                .select_related('order', 'item', 'order__currency', 'order__customer')

        cst_list = eval(customer_code)
        if len(cst_list):
            orderitem_list = orderitem_list.filter(order__customer_id__in=cst_list)

        # Get list of all customers
        cust_list = orderitem_list.values_list('order__customer__code', 'order__customer__name').order_by('order__customer__code').distinct()
        orderitem_list = orderitem_list.order_by('order__customer__code', 'order__customer__name',
                                                 'order__currency__code', 'item_id', 'item__category__code',
                                                 'item__code')

        company = Company.objects.get(id=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if orderitem_list:
            first_cust = True
            table_data = []
            gtc1 = gtc2 = gtc3 = gtc4 = gtc5 = 0
            for cust in cust_list:
                first_pg = True
                r6c1 = r6c2 = r6c3 = r6c4 = r6c5 = 0
                r7c1 = r7c2 = r7c3 = r7c4 = r7c5 = 0
                table_data = []
                if not first_cust:
                    table_data.append(['', '', '', '', '', '', ''])
                table_data.append([remove_none(cust[0]), remove_none(cust[1]), '', '', '', '', ''])
                item_table = Table(table_data, colWidths=[50, 230, 18, 70, 70, 70, 70], rowHeights=rowHeights)
                item_table.setStyle(TableStyle(style_custcode))
                elements.append(item_table)

                item_list = orderitem_list.filter(order__customer__code=cust[0], order__customer__name=cust[1]) \
                    .values_list('item__category__code', 'item__category__name', 'item__sales_measure__code',
                                 'item__code', 'order__currency__code', 'item__ratio',
                                 'order__currency_id', 'wanted_date', 'order__exchange_rate',
                                 'order__order_type', 'order_id', 'item_id', 'line_number') \
                    .annotate(order_qty=Sum(F('quantity'))) \
                    .annotate(order_amt=Sum(F('amount'))) \
                    .annotate(order_amt_delivery=Sum(F('delivery_quantity'))) \
                    .annotate(order_amt_price=F('price')) \
                    .annotate(order_amt_return=Sum(F('return_quantity'))) \
                    .order_by('item__category__code')

                category_list = item_list.values_list('item__category__code', 'item__category__name',
                                                      'item__sales_measure__code', 'item__ratio').distinct() \
                    .order_by('item__category__code')
                for cate in category_list:
                    table_data = []
                    if not first_pg:
                        table_data.append(['', '', '', '', '', '', ''])
                    table_data.append([remove_none(cate[0]), cate[1], '', '', '', remove_none(cate[3]),
                                       remove_none(cate[2])])
                    item_table = Table(table_data, colWidths=[70, 180, 60, 60, 68, 70, 70], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(style_partgp))
                    elements.append(item_table)

                    items_by_cate = item_list.filter(item__category__code=cate[0]).order_by('item__code', 'order__order_type', 'line_number')
                    prev_item_code = ''
                    for item in items_by_cate:
                        delivery_qty = 0
                        delivery_amount = 0
                        if item[9] == 1:
                            try:
                                do = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                              reference_id=item[10],
                                                              item_id=item[11],
                                                              order__order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                                              refer_line=item[12])

                                if do.__len__() > 0:
                                    for do_data in do:
                                        delivery_qty += do_data.delivery_quantity if do_data.delivery_quantity else 0
                                        delivery_amount += do_data.amount if do_data.amount else 0
                            except:
                                pass

                        table_data = []

                        line = 1 if item[3] != prev_item_code else line
                        code = '' if item[3] == prev_item_code else item[3]
                        price = item[15]
                        rate = item[8] if item[8] else 1
                        r1c1 = item[13] - delivery_qty if (item[13] and item[9] == 1) else 0
                        r1c2 = item[15] if (item[15] and item[9] == 6) else 0
                        r1c3 = item[17] if (item[17] and item[9] == 6) else 0
                        r1c4 = r1c2 - r1c3
                        r1c5 = r1c1 + r1c4
                        r2c1 = item[14] - delivery_amount if (r1c1 and item[14] and item[9] == 1) else 0
                        r2c2 = item[14] if (item[14] and item[9] == 6) else 0
                        if price is not None:
                            r2c3 = r1c3 * price
                        else:
                            r2c3 = r1c3
                        r2c4 = r2c2 - r2c3
                        r2c5 = r2c1 + r2c4
                        r3c1 = round_number(r2c1 / r1c1, 4) if r1c1 else 0
                        r3c2 = round_number(r2c2 / r1c2, 4) if r1c2 else 0
                        r3c3 = round_number(r2c3 / r1c3, 4) if r1c3 else 0
                        r3c4 = r3c2 - r3c3
                        r3c5 = r3c1 + r3c4
                        r6c1 += r2c1
                        r6c2 += r2c2
                        r6c3 += r2c3
                        r6c4 += r2c4
                        r6c5 += r2c5
                        r7c1 = round_number(r6c1 * rate)
                        r7c2 = round_number(r6c2 * rate)
                        r7c3 = round_number(r6c3 * rate)
                        r7c4 = round_number(r6c4 * rate)
                        r7c5 = round_number(r6c5 * rate)
                        try:
                            curr = Currency.objects.get(code=item[4])
                            decimal_place = get_decimal_place(curr)
                        except:
                            decimal_place = "%.2f"
                        if line == 1:
                            table_data.append(
                                [remove_none(code), '',
                                 Paragraph(intcomma("%.2f" % r1c1), styles['RightAlign']),
                                 Paragraph(intcomma("%.2f" % r1c2), styles['RightAlign']),
                                 Paragraph(intcomma("%.2f" % r1c3), styles['RightAlign']),
                                 Paragraph(intcomma("%.2f" % r1c4), styles['RightAlign']),
                                 Paragraph(intcomma("%.2f" % r1c5), styles['RightAlign'])])
                        # third row
                        table_data.append(['', remove_none(item[4]),
                                           Paragraph(intcomma(decimal_place % round_number(r2c1)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place % round_number(r2c2)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place % round_number(r2c3)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place % round_number(r2c4)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place % round_number(r2c5)), styles['RightAlign'])])

                        table_data.append(['', 'Average Unit Price:-',
                                           Paragraph(intcomma("%.4f" % round_number(r3c1, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r3c2, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r3c3, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r3c4, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r3c5, 4)), styles['RightAlign'])])
                        item_table = Table(table_data, colWidths=[60, 168, 70, 70, 70, 70, 70], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(style_body))
                        elements.append(item_table)
                        prev_item_code = item[3]
                        line += 1
                        first_pg = False

                first_cust = False
                table_data = []
                table_data.append(['', Paragraph('Total  ' + str(remove_none(item[4])), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % r6c1), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % r6c2), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % r6c3), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % r6c4), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % r6c5), styles['RightAlignBold'])])

                table_data.append(['', Paragraph('(Ex-Rate : ' + str(rate) + ') ' + 'Total  ' + remove_none(company.currency.code), styles['RightAlignBold']),
                                   Paragraph(intcomma(decimal_place_f % round_number(r7c1)), styles['RightAlignBold']),
                                   Paragraph(intcomma(decimal_place_f % round_number(r7c2)), styles['RightAlignBold']),
                                   Paragraph(intcomma(decimal_place_f % round_number(r7c3)), styles['RightAlignBold']),
                                   Paragraph(intcomma(decimal_place_f % round_number(r7c4)), styles['RightAlignBold']),
                                   Paragraph(intcomma(decimal_place_f % round_number(r7c5)), styles['RightAlignBold'])])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(style_subtotal))
                elements.append(item_table)

                gtc1 += r7c1
                gtc2 += r7c2
                gtc3 += r7c3
                gtc4 += r7c4
                gtc5 += r7c5

            table_data = []
            table_data.append(['', Paragraph('Grand Total For All Customer ' + remove_none(company.currency.code), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gtc1)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gtc2)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gtc3)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gtc4)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gtc5)), styles['RightAlignBold'])])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(style_grandtotal))
            elements.append(item_table)

        if len(elements) == 0:
            table_data = [['', '', '', '', '', '', '']]
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                                            ]))
            elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, month=month, year=year,
                                      cst_list=cst_list, company_name=company_name),
                  onLaterPages=partial(self._header_footer, month=month, year=year,
                                       cst_list=cst_list, company_name=company_name),
                  canvasmaker=partial(NumberedPage, adjusted_height=95, adjusted_width=15))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
