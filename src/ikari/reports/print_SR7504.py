from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from suppliers.models import Supplier
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from django.db.models import Q
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import round_number, get_decimal_place
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

rowHeights = 12


class Print_SR7504:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, issue_to, issue_from, supplier_list, company_id):
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
        row1_info1 = "SR7504 Sales and Purchase System"
        row1_info2 = "GOODS RECEIVE DETAIL REPORT BY SUPPLIER"
        header_data.append([row1_info1, row1_info2])

        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Supplier"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if len(supplier_list):
            item1 = Supplier.objects.get(pk=supplier_list[0])
            item2 = Supplier.objects.get(pk=supplier_list[-1])
            row4_info1 = "Supplier Code: [" + item1.code + "][" + item2.code + "]"
        else:
            row4_info1 = "Supplier Code: [][]"

        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

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
        header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Supplier Code & Name ', '', '', '', '', '', 'Curr', '  Tx Curr', '', '']
        table_data.append(table_header)
        table_header = ['S.No', 'Document No', 'Doc.Date', 'Tx Exchange Rate', 'Exchange Rate', 'Ln', 'Received Qty', 'Unit Price', 'Amount(ORG)', 'Cfm']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[20, 93, 63, 84, 70, 20, 60, 48, 65, 20], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (1, -1), (2, -1), 'CENTER'),
             ('ALIGN', (6, 0), (6, 0), 'RIGHT'),
             ('ALIGN', (7, 0), (7, 0), 'LEFT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1)

        table_data = []
        table_header1 = ['', 'Customer PO No.', 'Part No.', '', '', '', '', '', '', '']
        table_data.append(table_header1)

        item_header_table = Table(table_data, colWidths=[25, 95, 110, 40, 70, 20, 60, 50, 40, 30], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
             ('ALIGN', (2, -1), (2, -1), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - 90)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, supplier_no, is_confirm):

        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=130, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        elements = []

        # Get list of supplier no
        company = Company.objects.get(id=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if issue_from is not '0' and issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(issue_from, issue_to)) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .exclude(Q(supplier__isnull=True)) \
                .order_by('supplier__code', 'order__document_number', 'line_number')
        elif issue_from is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(issue_from)) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .exclude(Q(supplier__isnull=True)) \
                .order_by('supplier__code', 'order__document_number', 'line_number')
        elif issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(issue_to)) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .exclude(Q(supplier__isnull=True)) \
                .order_by('supplier__code', 'order__document_number', 'line_number')
        else:
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .exclude(Q(supplier__isnull=True)) \
                .order_by('supplier__code', 'order__document_number', 'line_number')

        supplier_list = eval(supplier_no)
        if len(supplier_list):
            customer_item_list = customer_item_list.filter(supplier_id__in=supplier_list)

        if is_confirm == 'Y':  # pgrh_updfg
            customer_item_list = customer_item_list.filter(order__is_confirm=is_confirm)

        m_document_number = ''
        m_supplier_code = ''
        doc_qty = doc_amount = doc_loc_amount = no = 0  # sum qty of each Order
        all_doc_qty = all_doc_loc_amount = all_amount = all_grand_qty = all_grand_amount = 0
        if customer_item_list:
            for i, mItem in enumerate(customer_item_list):
                exchange_rate = mItem.order.exchange_rate

                # check to print first row of code
                if m_supplier_code != mItem.order.supplier.code:
                    # Start new part no Total
                    table_data = []
                    m_supplier_code = mItem.order.supplier.code
                    doc_qty = doc_amount = 0
                    doc_loc_amount = 0
                    all_doc_qty = all_doc_loc_amount = all_amount = 0
                    m_document_number = ''
                    no = 0
                    table_data.append([Paragraph(mItem.order.supplier.code if mItem.order.supplier.code else '', styles["LeftAlign"]), 
                                       Paragraph(mItem.order.supplier.name if mItem.order.supplier.name else '', styles["LeftAlign"]),
                                       '', '', '', Paragraph(mItem.order.currency.code if mItem.order.currency.code else '', styles["LeftAlign"]),
                                       Paragraph(company.currency.code if company.currency.id else '', styles["LeftAlign"]), ''])

                    item_table = Table(table_data, colWidths=[90, 220, 20, 20, 40, 41, 25, 69], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('SPAN', (1, 0), (4, 0)),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                # check to print first row of cuatomer_po_no
                if m_document_number != mItem.order.document_number:
                    m_document_number = mItem.order.document_number
                    doc_qty = doc_amount = 0
                    doc_loc_amount = 0
                if m_document_number == mItem.order.document_number:
                    decimal_place = get_decimal_place(mItem.order.currency)
                    table_data = []
                    if not mItem.price:
                        mItem.price = 0
                    no += 1
                    table_data.append([no, Paragraph(mItem.order.document_number if mItem.order.document_number else '', styles["LeftAlign"]),
                                       mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ',
                                       intcomma("%.8f" % exchange_rate), intcomma("%.8f" % exchange_rate),
                                       mItem.line_number, intcomma("%.2f" % mItem.quantity),
                                       intcomma("%.5f" % mItem.price), intcomma(decimal_place % round_number(mItem.amount)), 'N'])  # rate

                    item_table = Table(table_data, colWidths=[35, 90, 55, 70, 70, 20, 60, 50, 60, 15], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (3, 0), (-1, 0), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                    table_data = []
                    table_data.append(['', mItem.customer_po_no, '', mItem.item.code,  '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=[30, 85, 25, 70, 70, 20, 20, 50, 70, 50], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                # check to print next row of customer_po_no
                if m_document_number == mItem.order.document_number \
                        and m_supplier_code == mItem.order.supplier.code:
                    doc_qty += mItem.quantity
                    doc_amount += mItem.amount
                    doc_loc_amount += round_number(mItem.amount * exchange_rate)

                    all_amount += mItem.amount
                    all_doc_qty += mItem.quantity
                    all_doc_loc_amount += round_number(mItem.amount * exchange_rate)
                    all_grand_qty += mItem.quantity
                    all_grand_amount += round_number(mItem.amount * exchange_rate)

                if m_supplier_code == mItem.order.supplier.code and i + 1 < customer_item_list.__len__():
                    if (customer_item_list[i + 1].order.supplier.code != mItem.order.supplier.code) | \
                            (customer_item_list[i + 1].order.document_number != mItem.order.document_number):
                        # Print CUSTOMER PO Total
                        decimal_place = get_decimal_place(mItem.order.currency)
                        table_data = []
                        table_data.append(['', '', '', Paragraph('Document Total:', styles['RightAlignBold']),
                                           Paragraph('(QTY):', styles['RightAlignBold']),
                                           Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']),
                                           Paragraph('Amt(ORG):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', Paragraph('Amt(LOC):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', '', ''])

                        # Create the table
                        item_table = Table(table_data, colWidths=[55, 60, 30, 100, 50, 70, 65, 65], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('FONTSIZE', (0, 0), (-1, 0), 8),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)

                    if customer_item_list[i + 1].order.supplier.code != mItem.order.supplier.code:
                        # Print Part No Total
                        decimal_place = get_decimal_place(mItem.order.currency)
                        table_data = []
                        table_data.append(['', '', '', Paragraph('Supplier:', styles['RightAlignBold']),
                                           Paragraph('(QTY):', styles['RightAlignBold']),
                                           Paragraph(intcomma("%.2f" % all_doc_qty), styles['RightAlignBold']),
                                           Paragraph('Amt(ORG):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place % round_number(all_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', Paragraph('Amt(LOC):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place_f % round_number(all_doc_loc_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', '', ''])

                        # Create the table
                        item_table = Table(table_data, colWidths=[55, 60, 30, 100, 50, 70, 65, 65], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('FONTSIZE', (0, 0), (-1, 0), 8),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                        all_doc_qty = all_doc_loc_amount = 0
                        table_data = []
                if i == customer_item_list.__len__() - 1:
                    # Print last row customer and part No Total
                    decimal_place = get_decimal_place(mItem.order.currency)
                    table_data = []
                    table_data.append([Paragraph('Document Total:', styles['RightAlignBold']),
                                       Paragraph('(QTY):', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']),
                                       Paragraph('Amt(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', Paragraph('Amt(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', ''])
                    table_data.append([Paragraph('Supplier Total:', styles['RightAlignBold']),
                                       Paragraph('(QTY):', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % all_doc_qty), styles['RightAlignBold']),
                                       Paragraph('Amt(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place % round_number(all_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', Paragraph('Amt(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place % round_number(all_doc_loc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', ''])
                    table_data.append([Paragraph('Grand Total For Local:', styles['RightAlignBold']),
                                       Paragraph('(QTY):', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % all_grand_qty), styles['RightAlignBold']),
                                       Paragraph('(Amt):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(all_grand_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', ''])

                    # Create the table
                    item_table = Table(table_data, colWidths=[245, 50, 70, 65, 65], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, 0), 8),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '']]
            item_table = Table(table_data, colWidths=[30, 70, 25, 70, 60, 50, 45, 50, 60, 65], rowHeights=rowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ]))
            elements.append(item_table)

        doc.build(elements, onFirstPage=partial(self._header_footer, issue_to=str(issue_to), issue_from=str(issue_from),
                                                supplier_list=supplier_list, company_id=company_id),
                  onLaterPages=partial(self._header_footer, issue_to=str(issue_to), issue_from=str(issue_from),
                                       supplier_list=supplier_list, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
