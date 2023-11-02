from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
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
from utilities.common import validate_date_to_from, get_company_name_and_current_period, round_number, get_decimal_place


colWidths = [20, 120, 85, 30, 60, 60, 60, 55, 55]
rowHeights = 12


class Print_SR7402:
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
        row1_info1 = "SR7402 Sales and Purchase System"
        row1_info2 = "Outstanding S/O Balance Report By Customer As At " + current_period
        header_data.append([row1_info1, row1_info2])

        # Second row
        row2_info1 = company_name
        row2_info2 = "Grouped by Customer, Document Number."
        header_data.append([row2_info1, row2_info2])
        # Third row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # Empty row
        # header_data.append(['', ''])
        # row4
        row4_info1 = "Transaction Code. : [SALE ORDER]"
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
            row5_info1 = "Customer Code: [" + item1 + "][" + item2 + "]"
        else:
            row5_info1 = "Customer Code: [][]"
        header_data.append([row5_info1, ""])
        # Empty row
        # header_data.append(['', ''])

        header_table = Table(header_data, colWidths=[265, 270], rowHeights=rowHeights)
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
        table_header = ['Customer Code & Name']
        table_data.append(table_header)
        table_header = ['Document No.', '', 'Doc. Date', '', 'Term', 'Curr', 'Exchange Rate', '', '', '', '']
        table_data.append(table_header)
        table_header = ['Ln', 'Part No.', '', '', 'UOM', 'Part Gp.', '', 'Unit Price', 'Order Qty', 'Inv Qty ', 'Balance Qty']
        table_data.append(table_header)
        table_header = ['Customer PO No.', '', '', 'P/O No. & Line', '', 'Due Date', 'Sch Date', '', 'Last Inv. Date', 'Remark', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[25, 65, 60, 30, 50, 50, 40, 40, 80, 55, 55], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 4), (-1, 4), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (2, 1), (3, 1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (3, 3), (4, 3)),
             ('SPAN', (6, 1), (7, 1)),
             ('SPAN', (6, -1), (7, -1)),
             ('SPAN', (2, 1), (3, 1)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 18, doc.height + doc.topMargin - h - h1 - 10)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, customer_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=160, bottomMargin=42, pagesize=self.pagesize)

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
            .annotate(balance=F('quantity') - F('delivery_quantity')) \
            .order_by('order__customer__code', 'order__document_number', 'line_number')

        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)

        m_customer_no = ''
        m_document_no = ''
        doc_qty = doc_delivery_qty = doc_balance_qty = 0  # sum qty of each Order
        cus_qty = cus_delivery_qty = cus_balance_qty = cus_loc_amount = 0  # sum qty of each supplier
        grand_qty = grand_delivery_qty = grand_balance_qty = 0  # total sum
        doc_org_amount = doc_loc_amount = 0
        cus_org_amount = grand_loc = 0
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        po_orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                 order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])\
            .exclude(reference_id__isnull=True)\
            .select_related('order')
        for i, mItem in enumerate(order_item_list):
            exchange_rate = mItem.order.exchange_rate
            grand_loc += round_number((mItem.quantity - mItem.delivery_quantity) * mItem.price * exchange_rate)  # mItem.amount * exchange_rate

            if float(mItem.balance) > 0:
                grand_qty += mItem.quantity
                grand_delivery_qty += mItem.delivery_quantity
                grand_balance_qty += mItem.balance

            # check to print first row of supplier
            if m_customer_no != mItem.order.customer.code and float(mItem.balance) > 0:
                # Start new Customer PO Total
                table_customer_no_data = []
                cus_qty = cus_delivery_qty = cus_balance_qty = cus_org_amount = cus_loc_amount = 0
                m_customer_no = mItem.order.customer.code
                table_customer_no_data.append([mItem.order.customer.code, mItem.order.customer.name, '', '', '', ''])
                # Create the table
                table_customer_no = Table(table_customer_no_data, colWidths=[60, 250, 62, 55, 55, 65], rowHeights=rowHeights)
                table_customer_no.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (0, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(table_customer_no)

            # check to print first row of Order
            if m_document_no != mItem.order.document_number and float(mItem.balance) > 0:
                m_document_no = mItem.order.document_number
                doc_qty = doc_delivery_qty = doc_balance_qty = 0
                doc_org_amount = doc_loc_amount = 0

                if m_document_no == mItem.order.document_number and float(mItem.balance) > 0:
                    table_data = []
                    table_data.append(
                        [mItem.order.document_number,
                         mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ',
                         mItem.order.customer.payment_term + 'days',
                         mItem.order.currency.code,
                         intcomma("%.8f" % exchange_rate),
                         '', '', ''])  # rate
                    item_table = Table(table_data, colWidths=[120, 55, 50, 50, 80, 80, 50, 60], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                    table_data = []

            # check to print next row of Order
            if m_customer_no == mItem.order.customer.code \
                    and m_document_no == mItem.order.document_number \
                    and float(mItem.balance) > 0:
                doc_qty += mItem.quantity
                doc_delivery_qty += mItem.delivery_quantity
                doc_balance_qty += float(mItem.balance)

                doc_org_amount += round_number(mItem.balance * mItem.price)
                doc_loc_amount = round_number(doc_org_amount * exchange_rate)

                cus_qty += mItem.quantity
                cus_delivery_qty += mItem.delivery_quantity
                cus_balance_qty += mItem.balance

                cus_org_amount += mItem.amount
                cus_loc_amount += round_number(mItem.balance * mItem.price * exchange_rate)

                table_data = []
                table_data.append([mItem.line_number, mItem.item.code,
                                   Paragraph(mItem.item.purchase_measure.code if mItem.item.purchase_measure else '', styles['RightAlign']), '',
                                   Paragraph(mItem.item.category.code[:8] if mItem.item.category else '', styles['LeftAlign']),
                                   Paragraph(intcomma("%.5f" % mItem.price), styles['LeftAlign']), intcomma("%.2f" % mItem.quantity),
                                   intcomma("%.2f" % mItem.delivery_quantity), intcomma("%.2f" % mItem.balance)])

                po_orderitem = po_orderitems.filter(refer_line=mItem.line_number, item_id=mItem.item_id,
                                                    customer_po_no=mItem.customer_po_no, refer_number=mItem.order.document_number).first()

                po_doc = po_orderitem.order.document_number + ' ' + str(
                    po_orderitem.line_number) if po_orderitem else ''

                table_data.append([Paragraph(mItem.customer_po_no[:24], styles['LeftAlign']), '', po_doc, '',
                                   mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ',
                                   mItem.schedule_date.strftime("%d/%m/%Y") if mItem.schedule_date else ' / / ',
                                   mItem.last_delivery_date.strftime("%d/%m/%Y") if mItem.last_delivery_date else ' / / ',
                                   '', ''])
                # Create the table
                global colWidths
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('SPAN', (0, -1), (1, -1)),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                table_data = []

            if i + 1 < order_item_list.__len__():
                if m_document_no == mItem.order.document_number and float(mItem.balance) > 0 and  \
                        order_item_list[i + 1].order.document_number != mItem.order.document_number:

                    decimal_place = get_decimal_place(mItem.order.currency)
                    item_table = self.print_SO_Total(doc_balance_qty, doc_delivery_qty, doc_loc_amount,
                                                     doc_org_amount, doc_qty, styles, decimal_place, decimal_place_f)
                    elements.append(item_table)
                    table_data = []
                    doc_qty = doc_balance_qty = 0

                if order_item_list[i + 1].order.customer.code != mItem.order.customer.code and float(cus_balance_qty) > 0:
                    decimal_place = get_decimal_place(mItem.order.currency)
                    item_table = self.print_cust_total(cus_balance_qty, cus_delivery_qty, cus_qty, cus_loc_amount,
                                                       mItem, styles, decimal_place_f)
                    elements.append(item_table)
                    table_data = []
                    cus_qty = cus_delivery_qty = cus_balance_qty = cus_loc_amount = 0

            if i == order_item_list.__len__() - 1:
                # Print PO Total
                decimal_place = get_decimal_place(mItem.order.currency)
                item_table = self.print_SO_Total(doc_balance_qty, doc_delivery_qty, doc_loc_amount, doc_org_amount,
                                                 doc_qty, styles, decimal_place, decimal_place_f)
                elements.append(item_table)

                item_table = self.print_cust_total(cus_balance_qty, cus_delivery_qty, cus_qty, cus_loc_amount,
                                                   mItem, styles, decimal_place_f)
                elements.append(item_table)
                cus_qty = cus_delivery_qty = cus_balance_qty = cus_loc_amount = 0

        item_table = self.print_grand_total(grand_balance_qty, grand_delivery_qty, grand_loc, grand_qty,
                                            styles, table_data, decimal_place_f)
        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), cust_list=cust_list,
                                      company_name=company_name, current_period=current_period),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), cust_list=cust_list,
                                       company_name=company_name, current_period=current_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=75))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def print_grand_total(self, grand_balance_qty, grand_delivery_qty, grand_loc, grand_qty, styles,
                          table_data, decimal_place_f):
        if float(grand_balance_qty) == 0:
            table_data.append(['', '', '', '', '', '', '', '', ''])
        else:
            table_data = []
            # Print Grant Total
            table_data.append(['', '', '', '', '', '', '', '', ''])

            table_data.append(['', '', '', '', '', Paragraph('Grand Total:', styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_delivery_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_balance_qty), styles['RightAlignBold'])])

            table_data.append(['', '', '', '', '', '', '', Paragraph('(LOC) :', styles['RightAlignBold']),
                               Paragraph(intcomma(decimal_place_f % round_number(grand_loc)), styles['RightAlignBold'])])

        # Create the table
        global colWidths
        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), 8),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        return item_table

    def print_cust_total(self, cus_balance_qty, cus_delivery_qty, cus_qty, cus_loc_amount, mItem, styles, decimal_place):
        table_data = []
        # Print CUSTOMER Total
        table_data.append(['', Paragraph('Total For ' + mItem.order.customer.code + ' : ', styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % cus_qty), styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % cus_delivery_qty), styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % cus_balance_qty), styles['RightAlignBold'])])

        table_data.append(['', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                           Paragraph(intcomma(decimal_place % cus_loc_amount), styles['RightAlignBold'])])
        # Create the table
        item_table = Table(table_data, colWidths=[282, 100, 50, 55, 55], rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        return item_table

    def print_SO_Total(self, doc_balance_qty, doc_delivery_qty, doc_loc_amount, doc_org_amount, doc_qty, styles, decimal_place, decimal_place_f):
        # Print PO Total
        table_data = []
        table_data.append(['', '', '', '', '', '', Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % doc_delivery_qty), styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % doc_balance_qty), styles['RightAlignBold'])])

        table_data.append(['', '', '', '', '', Paragraph('SO Total:', styles['RightAlignBold']),
                           Paragraph('Bal Amt (ORG):', styles['RightAlignBold']), '',
                           Paragraph(intcomma(decimal_place % round_number(doc_org_amount)), styles['RightAlignBold'])])

        table_data.append(['', '', '', '', '', '', '',  Paragraph('(LOC):', styles['RightAlignBold']),
                           Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])
        # Create the table
        global colWidths
        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (7, 0), (8, -1), 'LEFT'),
             ('ALIGN', (-2, 0), (-2, -1), 'LEFT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (-2, 1), (-3, 1)),
             ('FONTSIZE', (0, 0), (-1, -1), 8),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        return item_table
