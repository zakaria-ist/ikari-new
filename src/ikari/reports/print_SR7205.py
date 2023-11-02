from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from items.models import Item
from orders.models import OrderItem
from suppliers.models import Supplier
from reports.numbered_page import NumberedPage
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from django.conf import settings as s
from django.db.models import F, Q, Value as V
from django.db.models.functions import Coalesce
import datetime
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from functools import partial
from utilities.common import validate_date_to_from, get_company_name_and_current_period


colWidths = [110, 110, 40, 40, 70, 130, 75]
rowHeights = 12


class Print_SR7205:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, delivery_from, delivery_to, part_list, supp_list, company_name, current_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # First row
        header_data = []
        row1_info1 = "SR7205 Sales and Purchase System"
        row1_info2 = "Outstanding P/O Balance Report By Delivery Date As At " + current_period
        header_data.append([row1_info1, row1_info2])

        # Second row
        row2_info1 = company_name
        row2_info2 = "Grouped by Delivery Date, Supplier Date"
        header_data.append([row2_info1, row2_info2])
        # Third row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])

        if len(supp_list):
            item1 = Supplier.objects.get(pk=supp_list[0]).code
            item2 = Supplier.objects.get(pk=supp_list[-1]).code
            row4_info1 = "Supplier No.: [" + item1 + "][" + item2 + "]"
        else:
            row4_info1 = "Supplier No.: [][]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        if len(part_list):
            item1 = Item.objects.get(pk=part_list[0]).code
            item2 = Item.objects.get(pk=part_list[-1]).code
            row5_info1 = "Part No.: [" + item1 + "][" + item2 + "]"
        else:
            row5_info1 = "Part No.: [][]"
        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])

        current_year = datetime.datetime.now().year
        delivery_from_year = datetime.datetime.strptime(delivery_from, '%d-%m-%Y').year
        delivery_to_year = datetime.datetime.strptime(delivery_to, '%d-%m-%Y').year
        if current_year - delivery_from_year <= 99 and delivery_to_year <= current_year:
            row6_info1 = "Delivery Date : [" + delivery_from + "]" + " - [" + delivery_to + "]"
        elif current_year - delivery_from_year <= 99:
            row6_info1 = "Delivery Date : [" + delivery_from + "]" + " - [_/_/_]"
        elif delivery_to_year <= current_year:
            row6_info1 = "Delivery Date : [_/_/_]" + " - [" + delivery_to + "]"
        else:
            row6_info1 = "Delivery Date : [_/_/_]" + " - [_/_/_]"

        header_data.append([row6_info1, row5_info2])

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
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Del. Date', 'SO No. & Line', 'Supp. Code', 'Curr', 'Doc. Date', 'Part No.', '']
        table_data.append(table_header)
        table_header = ['Customer PO No.', 'Document No. & Line', '', 'Unit Price', 'Order Qty', 'Rec\'d Qty', 'Balance  Qty']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 2), (-1, 2), 0.25, colors.black),
             ('ALIGN', (0, 0), (2, 0), 'LEFT'),
             ('ALIGN', (3, 0), (-1, 0), 'RIGHT'),
             ('ALIGN', (0, 1), (2, 1), 'LEFT'),
             ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 8, doc.height + doc.topMargin - h - h1 - 10)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, supplier_no, part_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=17, leftMargin=17, topMargin=160, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styleN = styles["Normal"]
        styleN.fontName = s.REPORT_FONT_BOLD
        styleN.alignment = TA_LEFT

        elements = []
        table_data = []

        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity__lte=F('receive_quantity')) \
            .annotate(balance_qty=Coalesce(F('quantity'), V(0)) - Coalesce(F('receive_quantity'), V(0))) \
            .order_by('wanted_date', 'customer_po_no', 'line_number')

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)
        order_item_list = order_item_list.filter(wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                     delivery_to_obj.strftime('%Y-%m-%d')))

        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(supplier_id__in=supp_list)

        part_list = eval(part_no)
        if len(part_list):
            order_item_list = order_item_list.filter(item__id__in=part_list)

        wanted_date = ''
        cust_po = ''
        sum_qty = sum_receive_qty = sum_balance_qty = 0
        grand_qty = grand_receive_qty = grand_balance_qty = 0

        for i, mItem in enumerate(order_item_list):
            if i == 0:
                # Start new Delivery Date Total
                wanted_date = mItem.wanted_date
                table_data = []
                table_data.append([mItem.wanted_date.strftime("%d/%m/%Y"), '', '', '', '', '', ''])
                # Create the table
                table_wanted_date = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                table_wanted_date.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (0, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(table_wanted_date)

            if wanted_date != mItem.wanted_date:
                table_data = []
                table_data.append(['', '', '', '', '', '', ''])
                table_data.append(['', '', Paragraph('Delivery Date Total:', styles['LeftAlignBold']), '',
                                   Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % sum_receive_qty), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % sum_balance_qty), styles['RightAlignBold'])])

                # Create the table
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (0, -1), 0),
                        ('SPAN', (2, 1), (3, 1)),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                sum_qty = sum_receive_qty = sum_balance_qty = 0
                wanted_date = mItem.wanted_date
                table_data = []
                table_data.append([mItem.wanted_date.strftime("%d/%m/%Y"), '', '', '', '', '', ''])
                # Create the table
                table_wanted_date = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                table_wanted_date.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (0, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(table_wanted_date)

            if wanted_date == mItem.wanted_date and float(mItem.balance_qty) > 0:
                item_price = mItem.price if mItem.price else 0
                item_quantity = float(mItem.quantity) if mItem.quantity else 0
                receive_quantity = float(mItem.receive_quantity) if mItem.receive_quantity else 0
                balance_qty = float(mItem.balance_qty) if mItem.balance_qty else 0

                sum_qty += item_quantity
                sum_receive_qty += receive_quantity
                sum_balance_qty += balance_qty

                grand_qty += item_quantity
                grand_receive_qty += receive_quantity
                grand_balance_qty += balance_qty

                table_data = []
                if cust_po == mItem.customer_po_no:
                    customer_po_no = ''
                else:
                    customer_po_no = mItem.customer_po_no
                    table_data.append(['', '', '', '', '', '', '', ])

                table_data.append(
                    [customer_po_no if cust_po != mItem.customer_po_no else '',
                     mItem.reference.document_number + '     ' + mItem.refer_line if mItem.reference else '                    ' + '0',
                     mItem.supplier.code if mItem.supplier else '',
                     mItem.order.currency.code,
                     mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else Paragraph(' / / ', styles['RightAlign']),
                     mItem.item.code, ''])
                table_data.append(['', mItem.order.document_number + '     ' + str(mItem.line_number), '',
                                   Paragraph(intcomma("%.5f" % item_price), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % item_quantity), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % receive_quantity), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % balance_qty), styles['RightAlign'])])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (0, -1), 0),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                cust_po = mItem.customer_po_no

                if i == order_item_list.__len__() - 1:
                    # Print Delivery Date Total
                    table_data = []
                    table_data.append(['', '', '', '', '', '', ''])
                    table_data.append(['', '', Paragraph('Delivery Date Total:', styles['LeftAlignBold']), '',
                                       Paragraph(intcomma("%.2f" % sum_qty), styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % sum_receive_qty), styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % sum_balance_qty), styles['RightAlignBold'])])
                    # Create the table
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (0, -1), 0),
                         ('SPAN', (2, 1), (3, 1)),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

        if table_data.__len__() == 0:
            table_data.append(['', '', '', '', '', '', '', ])
        else:
            table_data = []
            # Print Grant Total
            table_data.append(['', '', '', '', '', '', ''])
            table_data.append(['', '', Paragraph('Grand Total:', styles['LeftAlignBold']), '',
                               Paragraph(intcomma("%.2f" % grand_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_receive_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_balance_qty), styles['RightAlignBold'])])

        # Create the table
        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (2, 1), (3, 1)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), part_list=part_list,
                                      supp_list=supp_list,
                                      company_name=company_name, current_period=current_period),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), part_list=part_list,
                                       supp_list=supp_list,
                                       company_name=company_name, current_period=current_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=75))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
