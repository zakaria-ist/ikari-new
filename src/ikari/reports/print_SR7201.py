from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import Order, OrderItem
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import validate_date_to_from, get_company_name_and_current_period, round_number
from django.db.models import Q, F, Value as V
from django.db.models.functions import Coalesce
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from functools import partial
from decimal import Decimal

colWidths = [20, 90, 45, 105, 60, 65, 45, 62, 75]
rowHeights = 12


class Print_SR7201:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, delivery_from, delivery_to, doc_list, company_name, current_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        header_data = []
        row1_info1 = "SR7201 Sales and Purchase System"
        row1_info2 = "Outstanding P/O Balance Report By Document No. As At " + current_period
        header_data.append([row1_info1, row1_info2])

        # Second row
        row2_info1 = company_name
        row2_info2 = "Grouped by Transaction Code, Document Number"
        header_data.append([row2_info1, row2_info2])
        # Third row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # row4
        row4_info1 = "Transaction Code. : [PURCHASE ORDER]"
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
        if len(doc_list):
            item1 = Order.objects.get(pk=doc_list[0]).document_number
            item2 = Order.objects.get(pk=doc_list[-1]).document_number
            row5_info1 = "Document No: [" + item1 + "][" + item2 + "]"
        else:
            row5_info1 = "Document No: [][]"
        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])
        # Empty row

        header_table = Table(header_data, colWidths=[265, 307], rowHeights=rowHeights)
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
        table_header = ['Trn', 'Document No.', 'Supplier Code & Name', '', '', 'Doc. Date', 'Term', 'Curr', 'Exchange Rate']
        table_data.append(table_header)
        table_header = ['Ln', 'Reference No.&Line', '', 'Part No.', '', 'UOM', 'Part Gp.', 'Del. Date', "Last Rcv.Date"]
        table_data.append(table_header)
        table_header = ['', 'Customer PO No.', '', '', 'Unit Price', 'Order Qty', '', "Rec'd Qty", 'Balance Qty']
        table_data.append(table_header)

        global colWidths
        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 3), (-1, 3), 0.25, colors.black),
             ('ALIGN', (3, 0), (3, -1), 'LEFT'),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (-2, -1), (-2, -1), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1 - 10)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, document_no):
        global colWidths

        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=17, leftMargin=17, topMargin=150, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        elements = []
        table_data = []
        exchange_rate = 0

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)

        order_item_list = OrderItem.objects.select_related('order').select_related('item').filter(
            is_hidden=0, order__is_hidden=0, order__company_id=company_id,
            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
            wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                delivery_to_obj.strftime('%Y-%m-%d'))) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('receive_quantity')) \
            .annotate(balance_qty=Coalesce(F('quantity'), V(0)) - Coalesce(F('receive_quantity'), V(0))) \
            .order_by('order__document_number', 'line_number')

        doc_list = eval(document_no)
        if len(doc_list):
            order_item_list = order_item_list.filter(order_id__in=doc_list)

        m_document_no = ''
        doc_qty = doc_receive_qty = doc_balance_qty = 0  # sum qty of each Order
        grand_qty = grand_receive_qty = grand_balance_qty = gt_loc = 0  # total sum
        doc_org_amount = doc_loc_amount = 0

        for i, mItem in enumerate(order_item_list):
            if float(mItem.balance_qty) > 0:
                grand_qty += float(mItem.quantity) if mItem.quantity else 0
                grand_receive_qty += float(mItem.receive_quantity) if mItem.receive_quantity else 0
                grand_balance_qty += float(mItem.balance_qty)

            # check to print first row of Order
            if m_document_no != mItem.order.document_number and float(mItem.balance_qty) > 0:
                m_document_no = mItem.order.document_number
                doc_qty = doc_receive_qty = doc_balance_qty = 0
                doc_org_amount = doc_loc_amount = 0
                exchange_rate = Decimal(mItem.order.exchange_rate) if mItem.order.exchange_rate else 1

                # Create the table
                table_doc_data = []
                table_doc_data.append(['P/O', Paragraph(mItem.order.document_number if mItem.order.document_number else '', styles['LeftAlign']),
                                       mItem.order.supplier.code if mItem.order.supplier else '',
                                       mItem.order.supplier.name if mItem.order.supplier and mItem.order.supplier.name else '', '',
                                       mItem.order.document_date.strftime(
                                           "%d/%m/%Y") if mItem.order.document_date else Paragraph(' / / ', styles['RightAlign']),
                                       Paragraph(str(mItem.supplier.term_days) + ' Days', styles['RightAlign']),
                                       mItem.order.currency.code, intcomma("%.8f" % exchange_rate)])  # rate

                table_doc = Table(table_doc_data, colWidths=colWidths, rowHeights=rowHeights)
                table_doc.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('SPAN', (3, 0), (4, 0)),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('FONTSIZE', (2, 0), (4, 0), 7),
                     ('FONT', (2, 0), (4, 0), s.REPORT_FONT_BOLD),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(table_doc)

            # check to print next row of Order
            if m_document_no == mItem.order.document_number and float(mItem.balance_qty) > 0:
                item_price = mItem.price if mItem.price else 0
                item_quantity = float(mItem.quantity) if mItem.quantity else 0
                receive_quantity = float(mItem.receive_quantity) if mItem.receive_quantity else 0

                doc_qty += float(mItem.quantity) if mItem.quantity else 0
                doc_receive_qty += float(mItem.receive_quantity) if mItem.receive_quantity else 0
                doc_balance_qty += float(mItem.balance_qty)

                doc_org_amount += round_number(mItem.balance_qty * mItem.price)
                doc_loc_amount += round_number(mItem.balance_qty * mItem.price * exchange_rate)
                gt_loc += round_number(mItem.balance_qty * mItem.price * exchange_rate)

                table_data.append([Paragraph(str(mItem.line_number), styles['CenterAlign']), mItem.refer_number, mItem.refer_line,
                                   Paragraph(mItem.item.code if mItem.item.code else '', styles['LeftAlign']), '',
                                   mItem.item.purchase_measure.code if mItem.item.purchase_measure else '',
                                   Paragraph(mItem.item.category.code[0:7] if mItem.item.category else '', styles['RightAlign']),
                                   mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else Paragraph(' / / ', styles['RightAlign']),
                                   mItem.last_receive_date.strftime("%d/%m/%Y") if mItem.last_receive_date else Paragraph(' / / ', styles['RightAlign'])])

                table_data.append(['', mItem.customer_po_no[:25], '', '', Paragraph(intcomma("%.5f" % item_price), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % item_quantity), styles['RightAlign']), '',
                                   Paragraph(intcomma("%.2f" % receive_quantity), styles['RightAlign']),
                                   Paragraph(intcomma("%.2f" % mItem.balance_qty), styles['RightAlign'])])

            if m_document_no == mItem.order.document_number and i + 1 < order_item_list.__len__():
                if order_item_list[i + 1].order.document_number != mItem.order.document_number:
                    # Print PO Total
                    table_data.append(['', '', '', Paragraph('PO Total :', styles['RightAlignBold']),
                                       Paragraph('Quantity :', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']), '',
                                       Paragraph(intcomma("%.2f" % doc_receive_qty), styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % doc_balance_qty), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', Paragraph('Bal ', styles['RightAlignBold']),
                                       Paragraph('Amt(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % round_number(doc_org_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', '', '', ''])
                    # Create the table
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                         ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                         ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                         ('ALIGN', (0, -4), (-1, -4), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                    table_data = []

            if m_document_no == mItem.order.document_number and i == order_item_list.__len__() - 1:
                # Print PO Total
                table_data.append(['', '', '', Paragraph('PO Total :', styles['RightAlignBold']),
                                   Paragraph('Quantity :', styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']), '',
                                   Paragraph(intcomma("%.2f" % doc_receive_qty), styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % doc_balance_qty), styles['RightAlignBold'])])

                table_data.append(['', '', '', '', '', '', Paragraph('Bal ', styles['RightAlignBold']),
                                   Paragraph('Amt(ORG):', styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % round_number(doc_org_amount)), styles['RightAlignBold'])])

                table_data.append(['', '', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                                   Paragraph(intcomma("%.2f" % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                table_data.append(['', '', '', '', '', '', '', '', ''])
                # Create the table
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                     ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                     ('ALIGN', (0, -4), (-1, -4), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                table_data = []

        if float(grand_balance_qty) == 0:
            table_data.append(['', '', '', '', '', '', '', '', ''])
        else:
            table_data = []
            # Print Grant Total
            table_data.append(['', '', '', Paragraph('Grand Total :', styles['LeftAlignBold']), '',
                               Paragraph(intcomma("%.2f" % grand_qty), styles['RightAlignBold']), '',
                               Paragraph(intcomma("%.2f" % grand_receive_qty), styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % grand_balance_qty), styles['RightAlignBold'])])

            table_data.append(['', '', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                               Paragraph(intcomma("%.2f" % round_number(gt_loc)), styles['RightAlignBold'])])

        # Create the table
        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (3, 0), (4, 0)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                      delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), doc_list=doc_list,
                                      company_name=company_name, current_period=current_period),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from_obj.strftime('%d-%m-%Y'),
                                       delivery_to=delivery_to_obj.strftime('%d-%m-%Y'), doc_list=doc_list,
                                       company_name=company_name, current_period=current_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=76))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
