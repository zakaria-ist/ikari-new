from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from items.models import Item
from reports.numbered_page import NumberedPage
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import round_number, get_decimal_place
import datetime
import calendar
from django.conf import settings as s
from django.db.models import Q
from django.utils.dateparse import parse_date
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

rowHeights = 12


class Print_SR7302:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, first_day, last_day, part_list, company_id):
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
        row1_info1 = "SR7302 Sales and Purchase System"
        row1_info2 = "MONTHLY PURCHASE ORDER REGISTER BY PART NUMBER"
        header_data.append([row1_info1, row1_info2])

        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Part No., Customer PO No"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        row4_info1 = "Printed Section : [PART NUMBER]"
        if len(part_list):
            item1 = Item.objects.get(pk=part_list[0]).code
            item2 = Item.objects.get(pk=part_list[-1]).code
            row4_info2 = "Part No.: [" + item1 + "][" + item2 + "]"
        else:
            row4_info2 = "Part No. : [] []"
        header_data.append([row4_info1, row4_info2])
        # 5st row
        row5_info1 = "Transaction Code : [PURCHASE ORDER]"
        row5_info2 = "Issued Date : [" + parse_date(first_day).strftime('%d/%m/%Y') + "] [" + \
                     parse_date(last_day).strftime('%d/%m/%Y') + "]"
        header_data.append([row5_info1, row5_info2])

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
        table_header = ['Part No. ', '', '', 'Part Description', '', '', 'UOM', 'Part Gp.']
        table_data.append(table_header)
        table_header = ['Trn', '', 'Customer PO No.', 'Document No.', 'Doc Date', 'Term', 'Curr', 'Exchange Rate']
        table_data.append(table_header)
        table_header = ['Ln', '', 'Reference No. & Line', 'Supplier Code', 'Del. Date', 'Order Qty', 'Unit Price', 'Amount']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[35, 20, 100, 80, 70, 70, 70, 80], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 3), (-1, 3), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, month, year, supplier_code, document_no, part_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=140, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        elements = []
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                      order__document_date__range=(first_day, last_day)) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .select_related('order', 'item', 'supplier')\
            .order_by('item__code', 'customer_po_no')

        sup_list = eval(supplier_code)
        if len(sup_list):
            customer_item_list = customer_item_list.filter(supplier_id__in=sup_list)

        doc_list = eval(document_no)
        if len(doc_list):
            customer_item_list = customer_item_list.filter(order_id__in=doc_list)

        part_list = eval(part_no)
        if len(part_list):
            customer_item_list = customer_item_list.filter(item_id__in=part_list)

        m_customer_po_no = ''
        m_code = ''
        m_document_number = ''
        doc_qty = doc_amount = doc_loc_amount = 0  # sum qty of each Order
        all_doc_qty_grand = all_doc_loc_amount_grand = 0
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if customer_item_list:
            for i, mItem in enumerate(customer_item_list):
                # check to print first row of code
                if (m_code != mItem.item.code):
                    # Start new part no Total
                    table_data = []
                    m_code = mItem.item.code
                    doc_qty = doc_amount = 0
                    doc_loc_amount = 0
                    all_doc_qty = all_doc_loc_amount = 0
                    m_document_number = ''
                    m_customer_po_no = ''
                    table_data.append([Paragraph(mItem.item.code if mItem.item.code else '', styles['LeftAlignBold']), '', '',
                                       Paragraph(mItem.item.short_description if mItem.item.short_description else '', styles["LeftAlign"]),
                                       '', '', mItem.item.purchase_measure.code if mItem.item.purchase_measure else '',  
                                       mItem.item.category.code if mItem.item.category else ''])

                    item_table = Table(table_data, colWidths=[115, 20, 20, 135, 50, 60, 45, 80], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                # check to print first row of cuatomer_po_no
                if (m_customer_po_no != mItem.customer_po_no) | (m_document_number != mItem.order.document_number):
                    m_document_number = mItem.order.document_number
                    if m_customer_po_no != mItem.customer_po_no:
                        doc_qty = doc_amount = 0
                        doc_loc_amount = 0
                    m_customer_po_no = mItem.customer_po_no
                    if m_customer_po_no == mItem.customer_po_no:
                        table_data = []
                        table_data.append(['P/O', Paragraph(mItem.customer_po_no, styles["LeftAlign"]), '', mItem.order.document_number,
                                           mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ',
                                           mItem.supplier.term_days + 'days', mItem.order.currency.code,
                                           intcomma("%.8f" % mItem.order.exchange_rate)])  # rate'

                        item_table = Table(table_data, colWidths=[55, 70, 30, 110, 70, 40, 70, 80], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                # check to print next row of customer_po_no
                if m_customer_po_no == mItem.customer_po_no \
                        and m_code == mItem.item.code:
                    doc_qty += mItem.quantity
                    doc_amount += mItem.amount
                    doc_loc_amount += round_number(mItem.amount * mItem.order.exchange_rate)

                    all_doc_qty += mItem.quantity
                    all_doc_loc_amount += round_number(mItem.amount * mItem.order.exchange_rate)
                    all_doc_qty_grand += mItem.quantity
                    all_doc_loc_amount_grand += round_number(mItem.amount * mItem.order.exchange_rate)
                    table_data = []
                    decimal_place = get_decimal_place(mItem.order.currency)
                    table_data.append([mItem.refer_line, mItem.refer_number, mItem.line_number, mItem.supplier.code,
                                       mItem.order.delivery_date,  mItem.quantity, intcomma("%.5f" % mItem.price),
                                       intcomma(decimal_place % round_number(mItem.amount))])
                    # Create the table
                    item_table = Table(table_data, colWidths=[55, 70, 30, 110, 70, 40, 70, 80], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                         ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                if m_code == mItem.item.code and i + 1 < customer_item_list.__len__():
                    if (customer_item_list[i + 1].customer_po_no != mItem.customer_po_no) | \
                            (customer_item_list[i + 1].item.code != mItem.item.code):
                        # Print CUSTOMER PO Total
                        decimal_place = get_decimal_place(mItem.order.currency)
                        table_data = []
                        table_data.append(['', '', '', '', Paragraph('Customer PO Total:', styles['RightAlignBold']),
                                           Paragraph(intcomma("%.2f" % float(doc_qty)), styles['RightAlignBold']),
                                           Paragraph('(ORG):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                        # Create the table
                        item_table = Table(table_data, colWidths=[55, 70, 30, 70, 90, 60, 70, 80], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)

                    if customer_item_list[i + 1].item.code != mItem.item.code:
                        # Print Part No Total
                        table_data = []
                        table_data.append(['', '', '', '', Paragraph('Part Total:', styles['RightAlignBold']),
                                           Paragraph(intcomma("%.2f" % all_doc_qty), styles['RightAlignBold']),
                                           Paragraph('(LOC):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place_f % round_number(all_doc_loc_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', '', ''])

                        # Create the table
                        item_table = Table(table_data, colWidths=[55, 70, 30, 70, 90, 60, 70, 80], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
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
                    table_data.append(['', '', '', '', Paragraph('Customer PO Total:', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % doc_qty), styles['RightAlignBold']),
                                       Paragraph('(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', Paragraph('Part Total:', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % all_doc_qty), styles['RightAlignBold']),
                                       Paragraph('(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(all_doc_loc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', '', ''])

                    table_data.append(['', '', '', '', Paragraph('Grand Total:', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % all_doc_qty_grand), styles['RightAlignBold']),
                                       Paragraph('(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(all_doc_loc_amount_grand)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', '', ''])

                    # Create the table
                    item_table = Table(table_data, colWidths=[55, 70, 30, 70, 90, 60, 70, 80], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
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
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT)]))
            elements.append(item_table)

        doc.build(elements, onFirstPage=partial(self._header_footer, first_day=str(first_day), last_day=str(last_day),
                                                part_list=part_list, company_id=company_id),
                  onLaterPages=partial(self._header_footer, first_day=str(first_day), last_day=str(last_day),
                                       part_list=part_list, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=85))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
