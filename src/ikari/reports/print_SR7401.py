from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.conf import settings as s
from django.db.models import F
import os
from companies.models import Company
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import validate_date_to_from, get_company_name_and_current_period, get_orderitem_filter_range, \
    round_number, get_decimal_place
from django.utils.dateparse import parse_date

rowHeights = 12


class Print_SR7401:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_name, current_period, doc_list, wanted_from, wanted_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # First row
        header_data = []
        row1_info1 = "SR7401 Sales and Purchase"
        row1_info2 = "Outstanding S/O Balance Report By Document Number As At " + current_period
        header_data.append([row1_info1, row1_info2])

        # Second row
        row2_info1 = company_name
        row2_info2 = "Grouped by Transaction Code, Document Number."
        header_data.append([row2_info1, row2_info2])
        # Third row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])

        # row4
        row4_info1 = "Transaction Code. : [SALE ORDER]"
        current_year = datetime.datetime.now().year
        wanted_from_year = datetime.datetime.strptime(wanted_from, '%d-%m-%Y').year
        wanted_to_year = datetime.datetime.strptime(wanted_to, '%d-%m-%Y').year
        if current_year - wanted_from_year <= 99 and wanted_to_year <= current_year:
            row4_info2 = "Wanted Date : [" + wanted_from + "]" + " - [" + wanted_to + "]"
        elif current_year - wanted_from_year <= 99:
            row4_info2 = "Wanted Date : [" + wanted_from + "]" + " - [_/_/_]"
        elif wanted_to_year <= current_year:
            row4_info2 = "Wanted Date : [_/_/_]" + " - [" + wanted_to + "]"
        else:
            row4_info2 = "Wanted Date : [_/_/_]" + " - [_/_/_]"
        header_data.append([row4_info1, row4_info2])
        if len(doc_list):
            header_data.append(["Document No. : [" + doc_list[0] + "] - [" + doc_list[-1] + "]", ""])
        else:
            header_data.append(["Document No. : [ ] - [ ]", ""])

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
        header_table.drawOn(canvas, doc.leftMargin - 5, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Document No.', '', 'Customer Code & Name', '', '', '', '', '', 'Doc. Date', 'Term', 'Curr', 'Exchg. Rate']
        table_data.append(table_header)
        table_header = ['Ln', 'Part No.', '', '', 'UOM', 'Part Gp.', '', 'Unit Price', '', 'Order Qty', 'Inv. Qty', 'Balance Qty']
        table_data.append(table_header)
        table_header = ['', 'Customer PO No.', '', 'P/O No. & Line', '', '', 'Due Date', '', 'Inv. Date', '', '', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[20, 80, 50, 50, 35, 60, 10, 45, 37, 55, 50, 70], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 3), (-1, 3), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 25, doc.height + doc.topMargin - h - h1 - 10)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, wanted_from, wanted_to, doc_no, cust_po):
        colWidths = [20, 80, 0, 60, 85, 45, 5, 58, 40, 55, 0, 50, 60]

        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=150, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, leading=12))

        elements = []
        order_type = dict(ORDER_TYPE)['SALES ORDER']
        wanted_from_obj, wanted_to_obj = validate_date_to_from(wanted_from, wanted_to)

        orderitems_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=order_type,
                                                   order__status__gte=dict(ORDER_STATUS)['Sent'],
                                                   wanted_date__range=(wanted_from_obj.strftime('%Y-%m-%d'),
                                                                       wanted_to_obj.strftime('%Y-%m-%d')))\
            .select_related('order', 'item', 'order__currency', 'order__customer')\
            .annotate(balance=F('quantity') - F('delivery_quantity'))\
            .exclude(quantity__lte=F('delivery_quantity'))\
            .order_by('order__document_number', 'line_number')

        doc_list = eval(doc_no)
        if len(doc_list):
            orderitems_list = orderitems_list.filter(order_id__in=doc_list)
            doc_list = [orderitems_list.filter(order_id=doc_list[0]).first().order.document_number,
                        orderitems_list.filter(order_id=doc_list[-1]).first().order.document_number]

        cust_po_list = eval(cust_po)
        if len(cust_po_list):
            orderitems_list = orderitems_list.filter(id__in=cust_po_list)

        grand_qty = grand_delivery_qty = grand_balance_qty = grandloc = 0
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        po_orderitems = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0,
                                                 order__company_id=company_id,
                                                 order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'])\
            .exclude(reference_id__isnull=True)\
            .select_related('order')
        m_document_no = ''
        order_qty = 0
        deli_qty = 0
        balance_amt = 0
        table_data = []
        rate = 1
        for i, mItem in enumerate(orderitems_list):
            if m_document_no != mItem.order.document_number:
                if i != 0:
                    grandloc += (balance_amt * rate)
                    minusin = float(order_qty) - float(deli_qty)
                    table_data.append(['', '', '', '', '', '', '', '', '', intcomma("%.2f" % order_qty), '',
                                    intcomma("%.2f" % deli_qty), intcomma("%.2f" % minusin)])

                    table_data.append(['', '', '', '', '', '', '', '', 'SO Total Bal Amt (ORG):', '', '', '',
                                    intcomma("%.2f" % round_number(balance_amt)) if mItem.order.currency.is_decimal
                                    else intcomma("%.0f" % round_number(balance_amt))])
                    if rate != 0:
                        balance_rate = round_number(float(balance_amt) * float(rate))
                        table_data.append(['', '', '', '', '', '', '', '', '', '', '', '(LOC):', intcomma(decimal_place_f % round_number(balance_rate))])
                    else:
                        table_data.append(['', 'Error Getting Exchange Rate !', '', '', '', '', '', '', '', '', '', '(LOC):',
                                        intcomma(decimal_place_f % round_number((balance_amt * rate)))])

                    table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', ''])
                    # Create the table
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                        ('SPAN', (3, 0), (6, 0)),
                        ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
                        ('TOPPADDING', (0, 0), (-1, 0), -2),
                        ('SPAN', (8, -2), (10, -2)),
                        ('SPAN', (8, -3), (11, -3)),
                        ('ALIGN', (8, -3), (11, -3), 'RIGHT'),
                        ('FONT', (8, -4), (-1, -1), s.REPORT_FONT_BOLD),
                        ('LEFTPADDING', (3, 0), (6, 0), 5),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                        ('FONTSIZE', (2, 0), (6, 0), 8),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                    elements.append(item_table)
                m_document_no = mItem.order.document_number
                order_qty = 0
                deli_qty = 0
                balance_amt = 0

                table_data = []
                rate = mItem.order.exchange_rate
                table_data = [[m_document_no, '', mItem.order.customer.code + ' ' + mItem.order.customer.name[:36], '',
                               '', '', '', '', mItem.order.document_date, mItem.order.customer.payment_term + ' Days', '',
                               mItem.order.currency.code, intcomma("%.8f" % rate)]]

                
            if m_document_no == mItem.order.document_number:
                po_orderitem = po_orderitems.filter(refer_number=mItem.order.document_number, item_id=mItem.item_id,
                                                    refer_line=mItem.line_number).first()
                po_doc = po_orderitem.order.document_number + ' ' + str(po_orderitem.line_number) if po_orderitem else ''
                due_date = parse_date(str(po_orderitem.wanted_date)).strftime('%d/%m/%Y') if po_orderitem else '//'
                inv_date = parse_date(str(po_orderitem.order.invoice_date)).strftime('%d/%m/%Y') if po_orderitem else '//'

                table_data.append([mItem.line_number, mItem.item.code, '', '', mItem.item.inv_measure.code if mItem.item.inv_measure else '',
                                    mItem.item.category.code[:8] if mItem.item.category else '', '', intcomma("%.5f" % mItem.price), '',
                                    intcomma("%.2f" % mItem.quantity), '', intcomma("%.2f" % mItem.delivery_quantity),
                                    intcomma("%.2f" % (mItem.quantity - mItem.delivery_quantity))])

                table_data.append(['', mItem.customer_po_no[:23], '', '', Paragraph(po_doc, styles['LeftAlign']), '',
                                    due_date, '', inv_date, '', '', '', ''])
                order_qty += mItem.quantity
                deli_qty += mItem.delivery_quantity
                balance_amt += (mItem.quantity - mItem.delivery_quantity) * mItem.price
                grand_qty += mItem.quantity
                grand_delivery_qty += mItem.delivery_quantity
                grand_balance_qty += mItem.balance
            if i == orderitems_list.__len__() - 1:
                grandloc += (balance_amt * rate)
                minusin = float(order_qty) - float(deli_qty)
                table_data.append(['', '', '', '', '', '', '', '', '', intcomma("%.2f" % order_qty), '',
                                   intcomma("%.2f" % deli_qty), intcomma("%.2f" % minusin)])

                table_data.append(['', '', '', '', '', '', '', '', 'SO Total Bal Amt (ORG):', '', '', '',
                                   intcomma("%.2f" % round_number(balance_amt)) if mItem.order.currency.is_decimal
                                   else intcomma("%.0f" % round_number(balance_amt))])
                if rate != 0:
                    balance_rate = round_number(float(balance_amt) * float(rate))
                    table_data.append(['', '', '', '', '', '', '', '', '', '', '', '(LOC):', intcomma(decimal_place_f % round_number(balance_rate))])
                else:
                    table_data.append(['', 'Error Getting Exchange Rate !', '', '', '', '', '', '', '', '', '', '(LOC):',
                                       intcomma(decimal_place_f % round_number((balance_amt * rate)))])

                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', ''])
                # Create the table
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('SPAN', (3, 0), (6, 0)),
                     ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
                     ('TOPPADDING', (0, 0), (-1, 0), -2),
                     ('SPAN', (8, -2), (10, -2)),
                     ('SPAN', (8, -3), (11, -3)),
                     ('ALIGN', (8, -3), (11, -3), 'RIGHT'),
                     ('FONT', (8, -4), (-1, -1), s.REPORT_FONT_BOLD),
                     ('LEFTPADDING', (3, 0), (6, 0), 5),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('FONTSIZE', (2, 0), (6, 0), 8),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                

        table_data = []
        table_data.append(['', '', '', '', '', 'Grand Total : ', '', '', '', intcomma("%.2f" % grand_qty), '',
                           intcomma("%.2f" % grand_delivery_qty), intcomma("%.2f" % grand_balance_qty)])

        table_data.append(['', '', '', '', '', '', '', '', '', '', '', '(LOC):',  intcomma(decimal_place_f % round_number(grandloc))])
        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('RIGHTPADDING', (11, -1), (12, -1), 0),
             ('SPAN', (5, -2), (6, -2)),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('RIGHTPADDING', (5, -2), (12, -2), 0),
             ('RIGHTPADDING', (9, -2), (9, -2), 5),
             ('RIGHTPADDING', (11, -2), (11, -2), 5),
             ('LEFTPADDING', (9, -2), (9, -2), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_name=company_name, current_period=current_period,
                                      doc_list=doc_list,
                                      wanted_from=wanted_from_obj.strftime('%d-%m-%Y'), wanted_to=wanted_to_obj.strftime('%d-%m-%Y')),
                  onLaterPages=partial(self._header_footer, company_name=company_name, current_period=current_period,
                                       doc_list=doc_list,
                                       wanted_from=wanted_from_obj.strftime('%d-%m-%Y'), wanted_to=wanted_to_obj.strftime('%d-%m-%Y')),
                  canvasmaker=partial(NumberedPage, adjusted_height=75))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
