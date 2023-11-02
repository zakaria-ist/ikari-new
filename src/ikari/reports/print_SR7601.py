import calendar
import datetime
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from utilities.constants import ORDER_TYPE
from django.conf import settings as s
from items.models import ItemCategory
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial
from decimal import Decimal
from utilities.common import get_company_name_and_current_period, get_category_filter_range, round_number, get_decimal_place

colWidths = [70, 158, 70, 70, 70, 70, 70]
rowHeights = 12


class Print_SR7601:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, month, year, cat_list, company_name):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1ST row
        header_data = []
        row1_info1 = "SR7601 Sales and Purchase System"
        row1_info2 = "MONTHLY SALES REPORT BY PART GROUP"
        header_data.append([row1_info1, row1_info2])

        # 2ND row
        row2_info1 = company_name
        row2_info2 = "Group By Part Group, Part Number"
        header_data.append([row2_info1, row2_info2])
        # 3RD row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        try:
            row4_info1 = "Month: " + datetime.datetime.now().strftime(month + '/' + year)
        except:
            row4_info1 = "Month: " + datetime.datetime.now().strftime('%m/%Y')
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])
        # 5st row
        if len(cat_list):
            item0 = ItemCategory.objects.get(pk=cat_list[0]).code
            item1 = ItemCategory.objects.get(pk=cat_list[-1]).code
            row5_info1 = "Part Group : [ " + item0 + " ]-[ " + item1 + " ]"
        else:
            row5_info1 = "Part Group : [ ] - [ ]"
        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])

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
        table_header = ['Part Group / Description', '', '', '', '', '', '']
        table_data.append(table_header)
        table_header = ['Part No.', 'Part Description', '', '', '', 'Ratio', 'UOM']
        table_data.append(table_header)
        table_header = ['Customer Code / Name', '', 'Order Qty', 'Sales Qty', 'Return Qty', 'Net Qty', 'Total Qty']
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
             ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 1), (0, 1), 10),
             ('LEFTPADDING', (0, 2), (0, 2), 10),
             ('SPAN', (0, 0), (1, 0)),
             ('SPAN', (1, 1), (2, 1)),
             ('SPAN', (0, 2), (1, 2)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, month, year, category, print_selection):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=17, leftMargin=17, topMargin=150, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        style_normal = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]
        style_code = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                      ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                      ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                      ('LEFTPADDING', (0, 0), (-1, -1), 0),
                      ('LEFTPADDING', (0, 0), (0, 0), 10),
                      ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                      ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
                      ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                      ]
        style_body = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                      ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                      ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                      ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                      ('LEFTPADDING', (0, 0), (-1, -1), 0),
                      ('LEFTPADDING', (0, 0), (0, 0), 10),
                      ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                      ]
        style_foot = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                      ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                      ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                      ('LEFTPADDING', (0, 0), (-1, -1), 0),
                      ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                      ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                      ]
        style_totalgroup = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))

        # Draw Content of PDF
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        # Get all orderitem in the time range
        orderitem_list_all = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id)
        if print_selection == 'A':
            orderitem_list = orderitem_list_all.filter(order__document_date__range=(first_day, last_day),
                                                       order__order_type__in=(dict(ORDER_TYPE)['SALES ORDER'],
                                                                              dict(ORDER_TYPE)['SALES INVOICE']))\
                .select_related('order', 'item', 'order__currency', 'order__customer')\
                .exclude(item__category__isnull=True)
        else:
            orderitem_list = orderitem_list_all.filter(order__document_date__range=(first_day, last_day), order__is_confirm=print_selection,
                                                       order__order_type__in=(dict(ORDER_TYPE)['SALES ORDER'],
                                                                              dict(ORDER_TYPE)['SALES INVOICE']))\
                .select_related('order', 'item', 'order__currency', 'order__customer')\
                .exclude(item__category__isnull=True)

        cat_list = eval(category)
        if len(cat_list):
            orderitem_list = orderitem_list.filter(item__category_id__in=cat_list)

        category_list = orderitem_list.values('item__category__code', 'item__category__name').distinct().order_by('item__category__code')

        code_list = orderitem_list.values('item__code', 'item__short_description', 'item__ratio').distinct().order_by('item__code')
        curr_list = orderitem_list.values_list('order__currency__code', flat=True).distinct().order_by('order__currency__code')

        orderitem_list = list(orderitem_list.order_by('item__category__code'))
        company = Company.objects.get(pk=company_id)
        company_curr_code = company.currency.code
        decimal_place_f = get_decimal_place(company.currency)

        len1 = len(orderitem_list)
        if len1:
            gt_r1c1 = gt_r1c2 = gt_r1c3 = gt_r1c4 = gt_r1c5 = 0
            gt_r2c1 = gt_r2c2 = gt_r2c3 = gt_r2c4 = gt_r2c5 = 0
            # Grouped by part group
            for category_item in category_list:

                orderitem_partgp = [orderitem for orderitem in orderitem_list if orderitem.item.category and orderitem.item.category.code == category_item['item__category__code']]

                table_data = [[Paragraph(category_item['item__category__code'], styles['LeftAlign']),
                               Paragraph(category_item['item__category__name'], styles['LeftAlign']), '', '', '', '', '']]
                item_table = Table(table_data, colWidths=[50, 178, 70, 70, 70, 70, 70], rowHeights=rowHeights)
                item_table.setStyle(TableStyle(style_normal))
                elements.append(item_table)
                table_data = []
                # Grouped by part no
                st_r1c1 = st_r1c2 = st_r1c3 = st_r1c4 = st_r1c5 = 0
                st_r2c1 = st_r2c2 = st_r2c3 = st_r2c4 = st_r2c5 = 0
                for code in code_list:
                    orderitem_partno = [orderitem for orderitem in orderitem_partgp if orderitem.item.code == code['item__code']]

                    if len(orderitem_partno) == 0:
                        continue

                    table_data.append([
                        Paragraph(str(code['item__code']), styles['LeftAlign']),
                        Paragraph(str(code['item__short_description']), styles['LeftAlign']), '', '', '',
                        Paragraph(str(code['item__ratio']), styles['RightAlign']),
                        Paragraph(str(orderitem_partno[0].item.inv_measure.code if orderitem_partno[0].item.inv_measure else ''), styles['RightAlign'])])
                    item_table = Table(table_data, colWidths=[280, 158, 0, 0, 0, 70, 70], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(style_code))
                    elements.append(item_table)
                    table_data = []

                    # Grouped by currency
                    for curr in curr_list:
                        orderitems = [orderitem for orderitem in orderitem_partno if orderitem.order.currency.code == curr]
                        orderitems.sort(key=lambda orderitem: (orderitem.order.customer.code, orderitem.order.customer.name))

                        r6c1 = r6c2 = r6c3 = r6c4 = r6c5 = 0
                        r7c1 = r7c2 = r7c3 = r7c4 = r7c5 = 0
                        r8c1 = r8c2 = r8c3 = r8c4 = r8c5 = 0
                        for orderitem in orderitems:
                            delivery_qty = 0
                            delivery_amount = 0
                            if orderitem.order.order_type == dict(ORDER_TYPE)['SALES ORDER']:
                                try:
                                    do = [orderitem for orderitem in orderitem_list
                                          if orderitem.reference_id == orderitem.order.id and
                                          orderitem.item_id == orderitem.item_id and
                                          orderitem.order.order_type == dict(ORDER_TYPE)['SALES INVOICE'] and
                                          orderitem.refer_line == orderitem.line_number]

                                    if do.__len__() > 0:
                                        for do_data in do:
                                            delivery_qty += do_data.delivery_quantity if do_data.delivery_quantity else 0
                                            delivery_amount += do_data.amount if do_data.amount else 0
                                except:
                                    pass

                            price = orderitem.price
                            rate = Decimal(orderitem.order.exchange_rate) if orderitem.order.exchange_rate else 1

                            # r1c1 = orderitem.quantity - delivery_qty if (orderitem.quantity and orderitem.order.order_type ==
                            #                                              dict(ORDER_TYPE)['SALES ORDER']) else 0
                            r1c1 = orderitem.quantity - orderitem.delivery_quantity
                            r1c2 = orderitem.delivery_quantity if (
                                orderitem.delivery_quantity and orderitem.order.order_type == dict(ORDER_TYPE)['SALES INVOICE']) else 0
                            r1c3 = orderitem.return_quantity if (orderitem.return_quantity and orderitem.order.order_type ==
                                                                 dict(ORDER_TYPE)['SALES INVOICE']) else 0
                            r1c4 = r1c2 - r1c3
                            r1c5 = r1c1 + r1c4
                            r2c1 = orderitem.amount - \
                                delivery_amount if (r1c1 and orderitem.amount and orderitem.order.order_type == dict(ORDER_TYPE)['SALES ORDER']) else 0
                            r2c2 = orderitem.amount if (orderitem.amount and orderitem.order.order_type == dict(ORDER_TYPE)['SALES INVOICE']) else 0
                            r2c3 = round_number(r1c3 * price)
                            r2c4 = r2c2 - r2c3
                            r2c5 = r2c1 + r2c4
                            r3c1 = round_number(r2c1 / r1c1, 4) if r1c1 else 0
                            r3c2 = round_number(r2c2 / r1c2, 4) if r1c2 else 0
                            r3c3 = round_number(r2c3 / r1c3, 4) if r1c3 else 0
                            r3c4 = r3c2 - r3c3
                            r3c5 = r3c1 + r3c4
                            r4c1 = round_number(r2c1 * rate) if r1c1 else 0
                            r4c2 = round_number(r2c2 * rate)
                            r4c3 = round_number(r2c3 * rate)
                            r4c4 = r4c2 - r4c3
                            r4c5 = r4c1 + r4c4
                            r5c1 = round_number(r2c1 * rate / r1c1, 4) if r1c1 else 0
                            r5c2 = round_number(r2c2 * rate / r1c2, 4)if r1c2 else 0
                            r5c3 = round_number(r2c3 * rate / r1c3, 4) if r1c3 else 0
                            r5c4 = r5c2 - r5c3
                            r5c5 = r5c1 + r5c4
                            r6c1 += r1c1
                            r6c2 += r1c2
                            r6c3 += r1c3
                            r6c4 += r1c4
                            r6c5 += r1c5
                            r7c1 += r4c1
                            r7c2 += r4c2
                            r7c3 += r4c3
                            r7c4 += r4c4
                            r7c5 += r4c5
                            r8c1 += r5c1
                            r8c2 += r5c2
                            r8c3 += r5c3
                            r8c4 += r5c4
                            r8c5 += r5c5
                            decimal_place = get_decimal_place(orderitem.order.currency)
                            table_data.append([Paragraph(orderitem.order.customer.code[:8], styles['LeftAlign']),
                                               Paragraph(orderitem.order.customer.name[0:27], styles['LeftAlign']),
                                               Paragraph(intcomma("%.2f" % r1c1), styles['RightAlign']),
                                               Paragraph(intcomma("%.2f" % r1c2), styles['RightAlign']),
                                               Paragraph(intcomma("%.2f" % r1c3), styles['RightAlign']),
                                               Paragraph(intcomma("%.2f" % r1c4), styles['RightAlign']),
                                               Paragraph(intcomma("%.2f" % r1c5), styles['RightAlign'])])

                            table_data.append(['', Paragraph(orderitem.order.currency.code, styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place % round_number(r2c1)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place % round_number(r2c2)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place % round_number(r2c3)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place % round_number(r2c4)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place % round_number(r2c5)), styles['RightAlign'])])

                            table_data.append(['', Paragraph('Average Unit Price :-', styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r3c1, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r3c2, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r3c3, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r3c4, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r3c5, 4)), styles['RightAlign'])])

                            table_data.append(['', Paragraph('(Ex-Rate: ' + intcomma("%.8f" % rate) + ' ' + company_curr_code + ' )', styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place_f % round_number(r4c1)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place_f % round_number(r4c2)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place_f % round_number(r4c3)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place_f % round_number(r4c4)), styles['RightAlign']),
                                               Paragraph(intcomma(decimal_place_f % round_number(r4c5)), styles['RightAlign'])])

                            table_data.append(['', Paragraph('Average Unit Price :- ', styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r5c1, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r5c2, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r5c3, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r5c4, 4)), styles['RightAlign']),
                                               Paragraph(intcomma("%.4f" % round_number(r5c5, 4)), styles['RightAlign'])])
                            item_table = Table(table_data, colWidths=[60, 168, 70, 70, 70, 70, 70], rowHeights=rowHeights)
                            item_table.setStyle(TableStyle(style_body))
                            elements.append(item_table)
                            table_data = []

                        st_r1c1 += r6c1
                        st_r1c2 += r6c2
                        st_r1c3 += r6c3
                        st_r1c4 += r6c4
                        st_r1c5 += r6c5
                        st_r2c1 += r7c1
                        st_r2c2 += r7c2
                        st_r2c3 += r7c3
                        st_r2c4 += r7c4
                        st_r2c5 += r7c5

                        table_data.append(['', Paragraph('Total Qty (Part)', styles['RightAlign']),
                                           Paragraph(intcomma("%.2f" % r6c1), styles['RightAlign']),
                                           Paragraph(intcomma("%.2f" % r6c2), styles['RightAlign']),
                                           Paragraph(intcomma("%.2f" % r6c3), styles['RightAlign']),
                                           Paragraph(intcomma("%.2f" % r6c4), styles['RightAlign']),
                                           Paragraph(intcomma("%.2f" % r6c5), styles['RightAlign'])])

                        table_data.append(['',
                                           Paragraph(company_curr_code, styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place_f % round_number(r7c1)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place_f % round_number(r7c2)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place_f % round_number(r7c3)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place_f % round_number(r7c4)), styles['RightAlign']),
                                           Paragraph(intcomma(decimal_place_f % round_number(r7c5)), styles['RightAlign'])])

                        table_data.append(['', Paragraph('Average Unit Price :- ', styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r8c1, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r8c2, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r8c3, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r8c4, 4)), styles['RightAlign']),
                                           Paragraph(intcomma("%.4f" % round_number(r8c5, 4)), styles['RightAlign'])])
                        table_data.append(['', '', '', '', '', '', ''])
                        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(style_foot))
                        elements.append(item_table)
                        table_data = []

                gt_r1c1 += st_r1c1
                gt_r1c2 += st_r1c2
                gt_r1c3 += st_r1c3
                gt_r1c4 += st_r1c4
                gt_r1c5 += st_r1c5
                gt_r2c1 += st_r2c1
                gt_r2c2 += st_r2c2
                gt_r2c3 += st_r2c3
                gt_r2c4 += st_r2c4
                gt_r2c5 += st_r2c5

                table_data.append(['', Paragraph('Total Qty (Group)', styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % st_r1c1), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % st_r1c2), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % st_r1c3), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % st_r1c4), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % st_r1c5), styles['RightAlign'])])

                table_data.append(['', Paragraph(company_curr_code, styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place_f % round_number(st_r2c1)), styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place_f % round_number(st_r2c2)), styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place_f % round_number(st_r2c3)), styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place_f % round_number(st_r2c4)), styles['RightAlign']),
                                   Paragraph(intcomma(decimal_place_f % round_number(st_r2c5)), styles['RightAlign'])])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(style_totalgroup))
                elements.append(item_table)
                table_data = []

            # Grand Total
            table_data.append(['', Paragraph('Grand Total For All Group Qty', styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % gt_r1c1), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % gt_r1c2), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % gt_r1c3), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % gt_r1c4), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % gt_r1c5), styles['RightAlignBold'])])

            table_data.append(['', Paragraph(company_curr_code, styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gt_r2c1)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gt_r2c2)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gt_r2c3)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gt_r2c4)), styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(gt_r2c5)), styles['RightAlignBold'])])
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(style_normal))
            elements.append(item_table)
            table_data = []

        else:
            table_data.append(['', '', '', '', '', '', ''])
            # Create the table
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(style_normal))
            elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, month=month, year=year, cat_list=cat_list, company_name=company_name),
                  onLaterPages=partial(self._header_footer, month=month, year=year, cat_list=cat_list, company_name=company_name),
                  canvasmaker=partial(NumberedPage, adjusted_width=20, adjusted_height=95))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
