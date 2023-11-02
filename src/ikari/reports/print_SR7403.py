from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from orders.models import OrderItem
from customers.models import Customer
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from reports.numbered_page import NumberedPage
from django.db.models import F
import datetime
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from functools import partial
from companies.models import Company
from utilities.common import validate_date_to_from, get_company_name_and_current_period, get_decimal_place


colWidths = [25, 115, 50, 135, 90, 50, 70, 40, 80, 80, 80]
rowHeights = 12


class Print_SR7403:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, delivery_from, delivery_to, cust_list, company_name, current_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # First row
        header_data = []
        row1_info1 = "SR7403 Sales and Purchase System"
        row1_info2 = "Outstanding S/O Balance Report By Wanted Date As At " + current_period
        header_data.append([row1_info1, row1_info2])
        # Second row
        row2_info1 = company_name
        row2_info2 = "Grouped by Wanted Date, Customer PO"
        header_data.append([row2_info1, row2_info2])
        # Third row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # row4
        row4_info1 = "Transaction Code. : [SALES ORDER]"
        current_year = datetime.datetime.now().year
        delivery_from_year = datetime.datetime.strptime(delivery_from, '%d-%m-%Y').year
        delivery_to_year = datetime.datetime.strptime(delivery_to, '%d-%m-%Y').year
        if current_year - delivery_from_year <= 99 and delivery_to_year <= current_year:
            row4_info2 = "Delivery Date : [" + delivery_from + "]" + " - [" + delivery_to + "]"
        elif current_year - delivery_from_year <= 99:
            row4_info2 = "Delivery Date : [" + delivery_from + "]" + " - [_/_/_]"
        elif delivery_to_year <= current_year:
            row4_info2 = "Delivery Date : [_/_/_]" + " - [" + delivery_to + "]"
        else:
            row4_info2 = "Delivery Date : [_/_/_]" + " - [_/_/_]"
        header_data.append([row4_info1, row4_info2])
        if len(cust_list):
            item1 = Customer.objects.get(pk=cust_list[0]).code
            item2 = Customer.objects.get(pk=cust_list[-1]).code
            header_data.append(["Customer Code: [" + item1 + "][" + item2 + "]", ""])
        else:
            header_data.append(["Customer Code: [][]", ""])

        header_table = Table(header_data, colWidths=[365, 370], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 5, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Wanted Date', '', '', '', '', '', '', '', '', '', '']
        table_data.append(table_header)
        table_header = ['Ln.', 'Part No./', 'Part', 'Customer PO No.', '-----------Document------------',
                        '', 'Unit Price', 'UOM', 'Order Qty', 'Inv Qty', 'Balance Qty']
        table_data.append(table_header)
        table_header = ['No.', 'Part Description', 'Group', 'Supplier Code', 'No.', 'Date', '', '', '', '', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (10, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 2), (10, 2), 0.25, colors.black),
             ('ALIGN', (0, 0), (3, 0), 'LEFT'),
             ('ALIGN', (0, 1), (3, 1), 'LEFT'),
             ('ALIGN', (0, 2), (3, 2), 'LEFT'),
             ('ALIGN', (6, 0), (10, 0), 'RIGHT'),
             ('ALIGN', (6, 1), (10, 1), 'RIGHT'),
             ('ALIGN', (6, 2), (10, 2), 'RIGHT'),
             ('ALIGN', (4, 1), (5, 1), 'CENTER'),
             ('ALIGN', (4, 2), (5, 2), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (0, 0), (1, 0)),
             ('SPAN', (4, 1), (5, 1)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 10)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, customer_no, supplier_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN + 30,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=8, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        elements = []
        table_data = []

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)
        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                   order__status__gte=dict(ORDER_STATUS)['Sent'],
                                                   wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                       delivery_to_obj.strftime('%Y-%m-%d'))) \
            .select_related('order', 'item', 'order__currency', 'order__customer')\
            .exclude(quantity__lte=F('delivery_quantity')) \
            .annotate(balance_qty=F('quantity') - F('delivery_quantity')) \
            .order_by('wanted_date', 'item__code', 'line_number')

        po_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(reference_id__isnull=True)\
            .select_related('order')

        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)
        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(supplier_id__in=supp_list)

        sum_balance_qty = 0
        grand_balance_qty = 0
        wanted_date = ''
        company = Company.objects.get(pk=company_id)

        for i, mItem in enumerate(order_item_list):
            if i == 0:
                # Start new Delivery Date Total
                wanted_date = mItem.wanted_date
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])
                table_data.append([mItem.wanted_date.strftime("%d/%m/%Y"), '', '', '', '', '', '', '', '', '', ''])
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
                table_data.append(['', '', '', '', '', '', '', '', Paragraph('Subtotal by Wanted Date:', styles['RightAlignBold']), '',
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
                        ('SPAN', (8, 0), (9, 0)),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                sum_balance_qty = 0
                wanted_date = mItem.wanted_date
                table_data = []
                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])
                table_data.append([mItem.wanted_date.strftime("%d/%m/%Y"), '', '', '', '', '', '', '', '', '', ''])
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
                delivery_quantity = float(mItem.delivery_quantity) if mItem.delivery_quantity else 0
                balance_qty = float(mItem.balance_qty) if mItem.balance_qty else 0

                sum_balance_qty += balance_qty
                grand_balance_qty += balance_qty

                po_item = po_items.filter(reference_id=mItem.order.id, refer_line=mItem.line_number).last()

                table_data = []
                table_data.append([str(mItem.line_number),  mItem.item.code,  mItem.item.category.code[:8] if mItem.item.category else '',
                                   mItem.customer_po_no,  mItem.order.document_number,
                                   mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else Paragraph(' / / ', styles['RightAlign']),
                                   Paragraph(intcomma("%.5f" % item_price), styles['RightAlign']),
                                   mItem.item.purchase_measure.code if mItem.item.purchase_measure else '',
                                   Paragraph(intcomma("%.2f" % item_quantity), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % delivery_quantity), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % balance_qty), styles['RightAlign'])])

                table_data.append(['', mItem.item.short_description if mItem.item.short_description else '', '', mItem.supplier.code if mItem.supplier else '',
                                   po_item.order.document_number if po_item else '',
                                   po_item.refer_line if po_item else '0', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('ALIGN', (0, 0), (3, 0), 'LEFT'),
                        ('ALIGN', (6, 0), (10, 0), 'RIGHT'),
                        ('ALIGN', (0, 1), (3, 1), 'LEFT'),
                        ('ALIGN', (6, 1), (10, 1), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (0, -1), 0),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)

                if i == order_item_list.__len__() - 1:
                    # Print Delivery Date Total
                    table_data = []
                    table_data.append(['', '', '', '', '', '', '', '', Paragraph('Subtotal by Wanted Date:', styles['RightAlignBold']), '',
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
                            ('SPAN', (8, 0), (9, 0)),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

        if table_data.__len__() == 0:
            table_data.append(['', '', '', '', '', '', '', '', '', '', ''])
        else:
            table_data = []
            table_data.append(['', '', '', '', '', '', '', '', Paragraph('Grand Total:', styles['RightAlignBold']), '',
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
                ('TOPPADDING', (0, 0), (0, -1), 0),
                ('SPAN', (8, 0), (9, 0)),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), cust_list=cust_list,
                                      company_name=company_name, current_period=current_period),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), cust_list=cust_list,
                                       company_name=company_name, current_period=current_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
