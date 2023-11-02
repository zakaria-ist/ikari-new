from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from items.models import Item
from orders.models import OrderItem
from suppliers.models import Supplier
from reports.numbered_page import NumberedPage
from django.conf import settings as s
from django.db.models import Q, F, Value as V
from django.db.models.functions import Coalesce
from utilities.constants import ORDER_STATUS, ORDER_TYPE
import datetime
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from functools import partial
from utilities.common import validate_date_to_from, get_company_name_and_current_period

# Description = [Del.Date, Sch.Date, Cust PO No., Sup Code, Doc No., Ln. No., Doc Date, Curr, Unit Price, Order Qty, Rec'd Qty, Blc Qty]
colWidths = [50, 50, 105, 65, 90, 35, 50, 25, 70, 70, 70, 70]


class Print_SR7204:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'A4 & landscape':
            self.pagesize = landscape(A4)
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, delivery_from, delivery_to, part_list, company_name, current_period,
                       part_no_from='', part_no_to='', supp_list='', customer_code_from='', customer_code_to=''):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR7204 Sales & Purchase System"
        row1_info2 = "Outstanding P/O Balance Report By Part No As At " + current_period
        header_data.append([row1_info1, row1_info2, ''])

        # 2nd row
        row2_info1 = company_name
        row2_info2 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row2_info3 = "Grouped by Part No., Customer PO No."
        header_data.append([row2_info1, row2_info2, row2_info3])

        empty_data = '[] - []'
        general_data = ''
        # 3rd row
        if customer_code_to or customer_code_from:
            general_data = '[' + customer_code_from + '] - [' + customer_code_to + ']'
        else:
            general_data = empty_data

        row3_info1 = "Transaction Code : [PURCHASE ORDER]"
        row3_info2 = "Customer Code : " + general_data
        header_data.append([row3_info1, row3_info2, ])

        # 4th row
        if len(supp_list):
            item1 = Supplier.objects.get(pk=supp_list[0]).code
            item2 = Supplier.objects.get(pk=supp_list[-1]).code
            row4_info1 = "Supplier No.: [" + item1 + "][" + item2 + "]"
        else:
            row4_info1 = "Supplier No.: [][]"

        if delivery_from or delivery_to:
            general_data = "[" + delivery_from + ' ] - [' + delivery_to + ' ]'
        else:
            general_data = empty_data

        row4_info2 = "Delivery Date: " + general_data
        header_data.append([row4_info1, row4_info2, ''])

        if len(part_list):
            item1 = Item.objects.get(pk=part_list[0]).code
            item2 = Item.objects.get(pk=part_list[-1]).code
            row5_info1 = "Part No.: [" + item1 + "][" + item2 + "]"
        else:
            row5_info1 = "Part No.: [][]"

        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[243, 200, 317])
        header_table.setStyle(TableStyle(
            [('SPAN', (1, 0), (2, 0)),
             ('ALIGN', (1, 0), (-1, -4), 'RIGHT'),
             ('ALIGN', (2, 0), (-1, -3), 'RIGHT'),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('TOPPADDING', (0, 2), (-1, -2), 5),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin + 25, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Part No.', '', 'Part Description', '',  '', 'Part Group', '', 'Person In Charge', '', 'UOM', '']
        table_data.append(table_header)
        table_header = ['Del. Date', 'Sch. Date', 'Customer PO No.', 'Supplier Code', 'Document No', 'Ln. No.', 'Doc. Date', 'Curr', 'Unit Price',
                        'Order Qty', "Rec'd Qty", "Balance Qty"]
        table_data.append(table_header)

        global colWidths
        item_header_table = Table(table_data, colWidths=colWidths)

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('SPAN', (0, 0), (1, 0)),  # Part No.
             ('SPAN', (3, 0), (4, 0)),  # Part Description
             ('ALIGN', (2, 0), (-3, -3), 'CENTER'),  # Part Description
             ('SPAN', (2, 0), (3, 0)),
             ('SPAN', (5, 0), (6, 0)),
             ('SPAN', (7, 0), (8, 0)),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, -2), 0.25, colors.black),
             ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
             ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
             ('ALIGN', (7, 0), (8, 0), 'CENTER'),
             ('ALIGN', (9, 1), (9, 1), 'CENTER'),
             ('ALIGN', (9, 0), (-2, -2), 'RIGHT'),
             ('ALIGN', (7, 1), (8, 1), 'CENTER'),
             ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin + 30, doc.height + doc.topMargin - h - h1)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, supplier_no, part_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=15, leftMargin=15, topMargin=130, bottomMargin=30, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="Justify", fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_JUSTIFY))

        order_item_list = OrderItem.objects.select_related('order').select_related('item').filter(
            is_hidden=0, order__is_hidden=0, order__company_id=company_id,
            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('receive_quantity')) \
            .annotate(balance_qty=Coalesce(F('quantity'), V(0)) - Coalesce(F('receive_quantity'), V(0))) \
            .order_by('item__code', 'wanted_date', 'line_number')

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)
        order_item_list = order_item_list.filter(wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                     delivery_to_obj.strftime('%Y-%m-%d')))

        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(supplier_id__in=supp_list)

        part_list = eval(part_no)
        if len(part_list):
            order_item_list = order_item_list.filter(item__id__in=part_list)

        m_item_code = ''
        elements = []
        table_data = []
        acc_qty = acc_receive_qty = acc_balance_qty = 0  # sum qty of each part
        grand_total_qty = grand_total_receive_qty = grand_total_balance_qty = 0

        for i, mItem in enumerate(order_item_list):
            if m_item_code != mItem.item.code and float(mItem.balance_qty) > 0:
                m_item_code = mItem.item.code
                acc_qty = acc_receive_qty = acc_balance_qty = 0  # sum qty of each part
                part_info = []
                part_info.append([mItem.item.code, '', mItem.item.short_description if mItem.item.short_description else '', '', '',
                                  Paragraph(mItem.item.category.code[0:7] if mItem.item.category else '', styles['RightAlign']), '',
                                  mItem.item.person_incharge, '', Paragraph(mItem.item.inv_measure.code if mItem.item.inv_measure else '', styles['RightAlign']), '', ''])

                item_table = Table(part_info, colWidths=colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (7, 0), (7, -1), 'LEFT'),
                     ('ALIGN', (-2, 0), (-2, -1), 'LEFT'),
                     ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                     ('ALIGN', (7, 0), (-5, -1), 'CENTER'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 8),
                     ('SPAN', (0, 0), (1, 0)),
                     ('SPAN', (2, 0), (3, 0)),
                     ('SPAN', (5, 0), (6, 0)),
                     ('SPAN', (7, 0), (8, 0)),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ]))
                elements.append(item_table)
            #   check on next row data
            if m_item_code == mItem.item.code and mItem.order and float(mItem.balance_qty) > 0:
                table_data = []
                item_price = mItem.price if mItem.price else 0
                item_quantity = float(mItem.quantity) if mItem.quantity else 0
                receive_quantity = float(mItem.receive_quantity) if mItem.receive_quantity else 0
                grand_total_qty += item_quantity
                grand_total_receive_qty += receive_quantity
                grand_total_balance_qty += float(mItem.balance_qty)
                acc_qty += item_quantity
                acc_receive_qty += receive_quantity
                acc_balance_qty += float(mItem.balance_qty)

                table_data.append(
                    [mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else Paragraph(' / / ', styles['LeftAlign']),
                     mItem.schedule_date.strftime("%d/%m/%Y") if mItem.schedule_date else Paragraph(' / / ', styles['LeftAlign']),
                     Paragraph(mItem.customer_po_no, styles['LeftAlign']),
                     Paragraph(mItem.supplier.code, styles['CenterAlign']),
                     mItem.order.document_number, Paragraph(str(mItem.line_number), styles['CenterAlign']),
                     mItem.order.document_date.strftime("%d/%m/%Y"),
                     Paragraph(mItem.order.currency.code, styles['RightAlign']),
                     Paragraph(intcomma("%.5f" % item_price), styles['RightAlign']),
                     Paragraph(intcomma("%.2f" % item_quantity), styles['RightAlign']),
                     Paragraph(intcomma("%.2f" % receive_quantity), styles['RightAlign']),
                     Paragraph(intcomma("%.2f" % mItem.balance_qty), styles['RightAlign'])
                     ])

                item_table = Table(table_data, colWidths=colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('ALIGN', (7, 0), (7, -1), 'LEFT'),
                     ('ALIGN', (-2, 0), (-2, -1), 'LEFT'),
                     ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ]))
                elements.append(item_table)
                table_data = []

            # Detect if it is the last index
            if i + 1 < order_item_list.__len__():
                if order_item_list[i + 1].item.code != m_item_code and float(acc_balance_qty) > 0:
                    table_data = []
                    # Print Sub Total
                    table_data.append(['', '', '', '', '', Paragraph('Subtotal By Part No. :', styles['RightAlignBold']), '', '', '',
                                       Paragraph(intcomma("%.2f" % acc_qty), styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % acc_receive_qty), styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % acc_balance_qty), styles['RightAlignBold'])])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('SPAN', (5, 0), (7, 0)),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ]))

                    acc_qty = acc_receive_qty = acc_balance_qty = 0
                    elements.append(item_table)
        # Actions after the for loop
        if not float(acc_balance_qty) == 0:
            table_data = []
            # Print Sub Total
            table_data.append(['', '', '', '', '', Paragraph('Subtotal By Part No. :', styles['RightAlignBold']), '', '', '',
                               Paragraph(intcomma("%.2f" % acc_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % acc_receive_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % acc_balance_qty), styles['RightAlignBold'])])
            # Print Grand Total
            table_data.append(['', '', '', '', '', Paragraph('Grand Total :', styles['RightAlignBold']), '', '', '',
                               Paragraph(intcomma("%.2f" % grand_total_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_total_receive_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_total_balance_qty), styles['RightAlignBold'])])

        if table_data.__len__() == 0:
            table_data.append(['', '', '', '', '', '', '', '', ''])

        item_table = Table(table_data, colWidths=colWidths)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('SPAN', (5, 0), (7, 0)),
            ('SPAN', (5, 1), (7, 1)),
            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

        elements.append(item_table)
        acc_qty = acc_receive_qty = acc_balance_qty = 0

        company_name, current_period = get_company_name_and_current_period(company_id)

        if not delivery_from_obj:
            delivery_from_obj = ''
        else:
            delivery_from_obj = delivery_from_obj.strftime('%d-%m-%Y')

        if not delivery_to_obj:
            delivery_to_obj = ''
        else:
            delivery_to_obj = delivery_to_obj.strftime('%d-%m-%Y')

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from_obj,
                                      delivery_to=delivery_to_obj, part_list=part_list, supp_list=supp_list,
                                      company_name=company_name, current_period=current_period),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from_obj,
                                       delivery_to=delivery_to_obj, part_list=part_list, supp_list=supp_list,
                                       company_name=company_name, current_period=current_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=-150, adjusted_width=230))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
