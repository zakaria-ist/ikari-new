from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import OrderItem
from suppliers.models import Supplier
from reports.numbered_page import NumberedPage
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import round_number, get_decimal_place
import datetime
import calendar
from django.conf import settings as s
from django.utils.dateparse import parse_date
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

colWidths = [30, 40, 70, 60, 80, 60, 60, 60, 60]
rowHeights = 12


class Print_SR7300:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, first_day, last_day, sup_list, doc_list, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR7300 Sales and Purchase System"
        row1_info2 = "MONTHLY PURCHASE ORDER REGISTER BY SUPPLIER"
        header_data.append([row1_info1, row1_info2])

        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Supplier, Transaction Code, Document Number"
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        if len(sup_list):
            item1 = Supplier.objects.get(pk=sup_list[0]).code
            item2 = Supplier.objects.get(pk=sup_list[-1]).code
            row4_info1 = Paragraph("Supplier Code : [" + item1 + "][" + item2 + "]", styles['Normal'])
        else:
            row4_info1 = "Supplier Code : [][]"
        if len(doc_list):
            row4_info2 = Paragraph("Document No. : [" + doc_list[0] + "][" + doc_list[len(doc_list) - 1] + "]", styles['Normal'])
        else:
            row4_info2 = "Document No. : [] []"
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
        # 1st row
        table_header = ['Supplier Code & Name', '', '', '', '', '', '', '', '', '']
        table_data.append(table_header)
        # 2nd row
        table_header = ['Trn', 'Document No.', '', 'Doc. Date', '', 'Term', 'Curr', '', '', 'Exchange Rate']
        table_data.append(table_header)
        # 3rd row
        table_header = ['Ln', 'Reference No. & Line', '', '', 'Part No.', '', 'UOM   ', 'Order Qty', 'Unit Price', 'Amount']
        table_data.append(table_header)
        # 4st row
        table_header = ['', 'Customer PO No.', '', '', 'Del. Date', '', 'Part Gp', '', '', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[20, 10, 110, 22, 70, 45, 67, 60, 60, 60], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (4, 2), (4, 3), 'LEFT'),
             ('ALIGN', (5, 1), (7, 1), 'LEFT'),
             ('ALIGN', (6, 2), (6, 3), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 1), (-1, 1), 5),
             ('LEFTPADDING', (0, 2), (1, 2), 10),
             ('LEFTPADDING', (3, 1), (3, 1), 30),
             ('LEFTPADDING', (6, 1), (6, 1), 20),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, month, year, supplier_code, document_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=45, leftMargin=45, topMargin=155, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        elements = []
        first_day = datetime.date(int(year), int(month), 1)
        last_day = datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

        supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                                                      order__document_date__range=(first_day, last_day)) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .select_related('order', 'item', 'supplier')\
            .order_by('order__supplier__code')

        sup_list = eval(supplier_code)
        if len(sup_list):
            supplier_item_list = supplier_item_list.filter(supplier_id__in=sup_list)

        doc_list = eval(document_no)
        if len(doc_list):
            supplier_item_list = supplier_item_list.filter(order_id__in=doc_list)
            doc_list = supplier_item_list.values_list('order__document_number', flat=True)

        m_supplier_no = ''
        m_document_no = ''
        doc_qty = doc_amount = doc_loc_amount = 0  # sum qty of each Order
        sum_qty = sum_loc_amount = 0
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if supplier_item_list:
            sup_qty = sup_loc_amount = 0
            for i, mItem in enumerate(supplier_item_list):
                # check to print first row of supplier
                if (m_supplier_no != mItem.order.supplier.code) & (m_document_no != mItem.order.document_number):
                    # Start new Customer PO Total
                    table_data = []
                    m_supplier_no = mItem.order.supplier.code
                    doc_qty = doc_amount = 0
                    doc_loc_amount = 0
                    table_data.append(
                        [mItem.order.supplier.code, '', mItem.order.supplier.name if mItem.order.supplier.name else '', '', '', '', '', '', ''])
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                # check to print first row of Order
                if m_document_no != mItem.order.document_number:
                    m_document_no = mItem.order.document_number
                    doc_qty = doc_amount = 0
                    doc_loc_amount = 0
                    if m_document_no == mItem.order.document_number:
                        table_data = []
                        table_data.append(['P/O', mItem.order.document_number, '',
                                           mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ',
                                           mItem.supplier.term_days + 'days', mItem.order.currency.code, '', '',
                                           intcomma("%.8f" % mItem.order.exchange_rate)])  # rate

                        item_table = Table(table_data, colWidths=[30, 55, 80, 50, 55, 40, 90, 60, 60], rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                # check to print next row of Order
                if m_supplier_no == mItem.order.supplier.code \
                        and m_document_no == mItem.order.document_number:
                    doc_qty += mItem.quantity
                    sup_qty += mItem.quantity
                    sum_qty += mItem.quantity
                    doc_amount += mItem.amount
                    doc_loc_amount += round_number(mItem.amount * mItem.order.exchange_rate)
                    sup_loc_amount += round_number(mItem.amount * mItem.order.exchange_rate)
                    sum_loc_amount += round_number(mItem.amount * mItem.order.exchange_rate)
                    decimal_place = get_decimal_place(mItem.order.currency)
                    table_data = []
                    table_data.append([mItem.refer_line, mItem.refer_number, mItem.line_number, mItem.item.code, '',
                                       mItem.item.purchase_measure.code if mItem.item.purchase_measure else '',
                                       mItem.quantity, intcomma("%.5f" % mItem.price),
                                       intcomma(decimal_place % round_number(mItem.amount))
                                       ])

                    table_data.append(['', mItem.customer_po_no, '', mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ',
                                       '', mItem.item.category.code if mItem.item.category else '', '', '', ''])
                    # Create the table
                    item_table = Table(table_data, colWidths=[30, 70, 60, 60, 75, 55, 50, 60, 60], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
                         ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)
                    table_data = []

                if m_document_no == mItem.order.document_number and i + 1 < supplier_item_list.__len__():
                    if supplier_item_list[i + 1].order.document_number != mItem.order.document_number:
                        # Print PO Total
                        decimal_place = get_decimal_place(mItem.order.currency)
                        table_data = []
                        table_data.append(['', '', '', '', '', Paragraph('Total:', styles['RightAlignBold']),
                                           Paragraph(intcomma("%.2f" % float(doc_qty)), styles['RightAlignBold']),
                                           Paragraph('(ORG):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles['RightAlignBold']),
                                           ])

                        table_data.append(['', '', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])
                        table_data.append(['', '', '', '', '', '', '', '', ])

                        # Create the table
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
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                        table_data = []
                    if supplier_item_list[i + 1].order.supplier.code != mItem.order.supplier.code:
                        # Print Supplier total
                        table_data = []
                        table_data.append(['', '', '', Paragraph('Total for ' + mItem.order.supplier.code + ':', styles['RightAlignBold']), '', '',
                                           Paragraph(intcomma("%.2f" % float(sup_qty)), styles['RightAlignBold']),
                                           Paragraph('(ORG):', styles['RightAlignBold']),
                                           Paragraph(intcomma(decimal_place_f % round_number(sup_loc_amount)), styles['RightAlignBold'])])

                        table_data.append(['', '', '', '', '', '', '', '', ''])
                        sup_qty = sup_loc_amount = 0

                        # Create the table
                        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                             ('ALIGN', (7, 0), (8, -1), 'LEFT'),
                             ('ALIGN', (-2, 0), (-2, -1), 'LEFT'),
                             ('SPAN', (3, 0), (5, 0)),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ]))
                        elements.append(item_table)
                        table_data = []
                if i == supplier_item_list.__len__() - 1:
                    # Print PO Total
                    decimal_place = get_decimal_place(mItem.order.currency)
                    table_data = []
                    table_data.append(['', '', '', '', '', Paragraph('Total:', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % float(doc_qty)), styles['RightAlignBold']),
                                       Paragraph('(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place % round_number(doc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', '', Paragraph('(LOC):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(doc_loc_amount)), styles['RightAlignBold'])])

                    table_data.append(['', '', '', '', '', '', '', '', ''])

                    table_data.append(['', '', '', Paragraph('Total for ' + mItem.order.supplier.code + ':', styles['RightAlignBold']), '', '',
                                       Paragraph(intcomma("%.2f" % float(sup_qty)), styles['RightAlignBold']),
                                       Paragraph('(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(sup_loc_amount)), styles['RightAlignBold']),
                                       ])

                    sup_qty = sup_loc_amount = 0
                    table_data.append(['', '', '', '', '', '', '', '', ''])

                    table_data.append(['', '', '', '', '', Paragraph('Grand Total:', styles['RightAlignBold']),
                                       Paragraph(intcomma("%.2f" % float(sum_qty)), styles['RightAlignBold']),
                                       Paragraph('(ORG):', styles['RightAlignBold']),
                                       Paragraph(intcomma(decimal_place_f % round_number(sum_loc_amount)), styles['RightAlignBold']),
                                       ])

                    # Create the table
                    item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                         ('ALIGN', (7, 0), (8, -1), 'LEFT'),
                         ('ALIGN', (-2, 0), (-2, -1), 'LEFT'),
                         ('SPAN', (3, 3), (5, 3)),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT)]))
            elements.append(item_table)
        doc.build(elements, onFirstPage=partial(self._header_footer, first_day=str(first_day), last_day=str(last_day),
                                                sup_list=sup_list, doc_list=doc_list, company_id=company_id),
                  onLaterPages=partial(self._header_footer, first_day=str(first_day), last_day=str(last_day),
                                       sup_list=sup_list, doc_list=doc_list, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=85))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
