from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from inventory.models import StockTransaction, StockTransactionDetail
from django.utils.dateparse import parse_date
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import INV_IN_OUT_FLAG
from utilities.common import round_number


class Print_STOutBalance:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, issue_from, issue_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "SR8500 Sales & Purchase System "
        row1_info2 = ""
        row1_info3 = "OUTSTANDING BALANCE & STOCK STATUS REPORT"
        header_data.append([row1_info1, row1_info2, row1_info3])

        # # 2nd row
        row2_info1 = company.name
        row2_info2 = ""
        row2_info3 = "AS AT " + str(datetime.datetime.now().strftime('%B %Y '))

        header_data.append([row2_info1, row2_info2, row2_info3])
        # # 3rd row
        row3_info1 = 'Date:' + str(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        row3_info2 = ""
        row3_info3 = "Grouped by Part No"
        header_data.append([row3_info1, row3_info2, row3_info3])
        # # 4rd row
        row4_info1 = ""
        row4_info2 = ""
        row4_info3 = ""
        header_data.append([row4_info1, row4_info2, row4_info3])
        # # 5rd row
        row5_info1 = "Part No.          :" + "[] - [y]"
        row5_info2 = ""
        row5_info3 = ""
        header_data.append([row5_info1, row5_info2, row5_info3])

        # # 6rd row
        to_date = from_date = ''
        if issue_to:
            if issue_to != '0':
                to_date = parse_date(issue_to).strftime('%d/%m/%Y')
        else:
            to_date = ''
        if issue_from:
            if issue_from != '0':
                from_date = parse_date(issue_from).strftime('%d/%m/%Y')
        else:
            from_date = ''
        row6_info1 = "Wanted Date:" + "[" + from_date + "] [" + to_date + "]"
        row6_info2 = ""
        row6_info3 = ""
        header_data.append([row6_info1, row6_info2, row6_info3])

        header_table = Table(header_data, colWidths=[290, 280, 230, 10])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (1, -1), (1, -1), 'CENTER'),
             ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('FONTSIZE', (-1, 0), (-1, 0), 14),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        # header_data = []
        # 1st row
        header_data = []
        row1_info1 = ""
        row1_info2 = ""
        row1_info3 = ""
        row1_info4 = ""
        row1_info5 = ""

        header_data.append([row1_info1, row1_info2, row1_info3, row1_info4, row1_info5])

        row2_info1 = "Part No."
        row2_info2 = "On Hand Qty"
        row2_info3 = "Outstanding"
        row2_info4 = "Outstanding"
        row2_info5 = ""

        header_data.append([row2_info1, row2_info2, row2_info3, row2_info4, row2_info5])

        row3_info1 = ""
        row3_info2 = ""
        row3_info3 = "S/O Qty   "
        row3_info4 = "P/O Qty   "
        row3_info5 = ""

        header_data.append([row3_info1, row3_info2, row3_info3, row3_info4, row3_info5])

        header_table = Table(header_data, colWidths=[240, 140, 140, 140, 140])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ('TOPPADDING', (-1, -1), (-1, -1), -50),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 70)

        # header_data = []
        # 1st row
        header_data = []
        row1_info1 = ""
        row1_info2 = ""
        row1_info3 = ""
        row1_info4 = ""
        row1_info5 = "Balance Qty"
        header_data.append(
            [row1_info1, row1_info2, row1_info3, row1_info4, row1_info5])
        header_table = Table(header_data, colWidths=[240, 140, 140, 140, 140])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('ALIGN', (1, 0), (-1, -1), 'RIGHT')
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 103)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=30, topMargin=165,
                                bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=11))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        # process table_data
        stock_item_list = StockTransaction.objects.filter(company_id=company_id, is_hidden=0)\
            .exclude(io_flag=dict(INV_IN_OUT_FLAG)['Transfer'])
        # ckeck case only input  Date To
        if issue_from == '0':
            if issue_to:
                stock_item_list = stock_item_list.filter(document_date__lte=issue_to)
        # ckeck case only input  Date From
        if issue_to == '0':
            if issue_from:
                stock_item_list = stock_item_list.filter(document_date__gte=issue_from)

        # ckeck case input both Date From, To
        if (issue_from != '0') & (issue_to != '0'):
            if issue_from:
                stock_item_list = stock_item_list.filter(document_date__gte=issue_from)
            if issue_to:
                stock_item_list = stock_item_list.filter(document_date__lte=issue_to)

        stock_item_list = stock_item_list.values('id').order_by('id')

        total_po = total_so = 0
        # total_bl = 0
        table_data = []
        mCode = ''
        item_stock = StockTransactionDetail.objects.filter(is_hidden=0,
                                                           parent_id__in=stock_item_list).order_by('item_id')

        if item_stock:
            for i, mStock in enumerate(item_stock):
                if i == 0:
                    mCode = mStock.item_id

                if mCode != mStock.item_id:
                    # output total location if move another item
                    table_data = []
                    table_data.append([Paragraph(str(item_stock[i - 1].item.code if item_stock[i - 1].item_id else ''), styles['Normal']),
                                       intcomma("%.2f" % 0), intcomma("%.2f" % round_number(total_so)),
                                       intcomma("%.2f" % round_number(total_po)), intcomma("%.2f" % round_number(total_po - total_so))])

                    item_table = Table(table_data, colWidths=[230, 140, 140, 140, 140])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                         ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                         ]))
                    elements.append(item_table)
                    mCode = mStock.item_id
                    total_po = total_so = 0
                if mCode == mStock.item_id:
                    if mStock.parent.io_flag == dict(INV_IN_OUT_FLAG)['IN']:
                        total_po += mStock.quantity
                    if mStock.parent.io_flag == dict(INV_IN_OUT_FLAG)['OUT']:
                        total_so += mStock.quantity
                if i == item_stock.__len__() - 1:
                    table_data = []
                    table_data.append([Paragraph(str(mStock.item.code if mStock.item_id else ''), styles['Normal']),
                                       intcomma("%.2f" % 0), intcomma("%.2f" % round_number(total_so)),
                                       intcomma("%.2f" % round_number(total_po)), intcomma("%.2f" % round_number(total_po - total_so))])

                    item_table = Table(table_data, colWidths=[230, 140, 140, 140, 140])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                         ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                         ]))
                    elements.append(item_table)

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[90, 155, 5, 190, 5, 150, 5, 150, 50])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                      issue_to=issue_to
                                      ),
                  onLaterPages=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                       issue_to=issue_to),
                  canvasmaker=partial(NumberedPage, adjusted_height=-190, adjusted_width=235))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
