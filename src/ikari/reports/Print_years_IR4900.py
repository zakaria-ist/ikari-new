from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
import calendar
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from inventory.models import History, TransactionCode
from items.models import Item
from locations.models import Location
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import round_number


class Print_years_IR4900:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, issue_from, issue_to, trx_code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        trans_code = TransactionCode.objects.get(pk=trx_code)
        # 1st row
        header_data = []
        row1_info1 = "IR4900_" + trans_code.code + " Inventory Control System"
        row1_info2 = ""
        row1_info3 = "Yearly Transaction Summary By Transaction Code As " + str(datetime.datetime.now().strftime('%B %Y'))
        header_data.append([row1_info1, row1_info2, row1_info3])

        # # 2nd row
        row2_info1 = company.name
        row2_info2 = ""
        row2_info3 = "Grouped by , Item code  "

        header_data.append([row2_info1, row2_info2, row2_info3])
        # # 3rd row
        row3_info1 = 'Date:' + str(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        row3_info2 = "Report period:" + issue_to.strftime('%B/%Y ')
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])
        # # 4rd row
        row4_info1 = "Item Code : [] - [y]"
        row4_info2 = ""
        row4_info3 = ""
        header_data.append([row4_info1, row4_info2, row4_info3])
        # # 5rd row
        row5_info1 = "Location Code : [] - [y]"
        row5_info2 = ""
        row5_info3 = ""
        header_data.append([row5_info1, row5_info2, row5_info3])

        row6_info1 = "Transaction Code : [" + trans_code.code + "]"
        row6_info2 = ""
        row6_info3 = ""
        header_data.append([row6_info1, row6_info2, row6_info3])
        header_data.append(['', '', ''])
        header_data.append(['', '', ''])

        header_table = Table(header_data, colWidths=[290, 280, 230, 10])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (1, -1), (1, -1), 'CENTER'),
             ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('FONTSIZE', (-1, 0), (-1, 0), 14),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin + 30)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin + 30 - h)
        # header_data = []
        # 1st row
        header_data = []
        row1_info1 = ""
        row1_info2 = ""
        row1_info3 = ""
        row1_info4 = ""
        row1_info5 = ""
        row1_info6 = ""
        row1_info7 = ""
        row1_info8 = ""

        header_data.append([row1_info1, row1_info2, row1_info3, row1_info4, row1_info5, row1_info6, row1_info7, row1_info8])
        spaci = ''
        row2_info1 = "Item Code"
        row2_info2 = "Item"
        row2_info3 = "Location"
        row2_info4 = "Price"
        row2_info5 = "Stock"
        row2_info6 = "Processing"
        row2_info7 = "Total-In"
        row2_info8 = "Total-In Amt"
        row2_info9 = "Total-Out"
        row2_info10 = "Total-Out Amt"

        header_data.append([row2_info1, spaci, row2_info2, spaci, row2_info3, spaci, row2_info4, spaci, row2_info5, spaci, row2_info6, spaci, row2_info7,
                            spaci, row2_info8, spaci, row2_info9, spaci, row2_info10])

        row3_info1 = ""
        row3_info2 = "Group"
        row3_info3 = "Code"
        row3_info4 = "Type"
        row3_info5 = "Class"
        row3_info6 = "Year-month"
        row3_info7 = "Qty"
        row3_info8 = "(S$)"
        row3_info9 = "Qty"
        row3_info10 = "(S$)"

        header_data.append([row3_info1, spaci, row3_info2, spaci, row3_info3, spaci, row3_info4, spaci, row3_info5, spaci, row3_info6, spaci,
                            row3_info7, spaci, row3_info8, spaci, row3_info9, spaci, row3_info10])

        header_table = Table(header_data, colWidths=[140, 5, 60, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 85])

        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 50)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, trx_code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        company = Company.objects.get(pk=company_id)
        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=150,
                                bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=11))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))

        # Our container for 'Flowable' objects
        elements = []
        # process table_data
        array_data = str(issue_from).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        trans_code = TransactionCode.objects.get(pk=trx_code)  # test 37
        total_amount_his_in = total_amount_his_out = sum_qty_out = sum_qty_in = 0
        lewatHIs = History.objects.filter(company_id=company_id, is_hidden=0,
                                          year=array_data[0], transaction_code_id=trans_code).order_by('item_code__code', 'month')
        if lewatHIs:
            for item_stock in lewatHIs:
                table_data = []
                qtyin = amount_in = qtyout = amount_out = 0
                itm = Item.objects.get(pk=item_stock.item_code_id)
                if int(item_stock.io_flag) == 1:
                    qtyin = item_stock.quantity
                    amount_in = intcomma("%.2f" % round_number(item_stock.amount))
                    total_amount_his_in += item_stock.amount
                    sum_qty_in += item_stock.quantity
                if int(item_stock.io_flag) == 3:
                    qtyout = item_stock.quantity
                    amount_out = intcomma("%.2f" % round_number(item_stock.amount))
                    total_amount_his_out += item_stock.amount
                    sum_qty_out += item_stock.quantity

                if item_stock.location_id:
                    loc = Location.objects.get(pk=item_stock.location_id)
                    if int(loc.stock_class) == 1:
                        class_code = 'INTERNAL'
                    else:
                        class_code = 'EXTERNAL'
                currency = company.currency.code
                table_data.append([Paragraph(str(item_stock.item_code.code if item_stock.item_code_id else ''), styles['Normal']), '',
                                   Paragraph(str(itm.category.code if itm else ''), styles['Normal']), '',
                                   Paragraph(str(loc.code if loc else ''), styles['Normal']), '',
                                   Paragraph(str(currency if currency else ''), styles['Normal']), '',
                                   Paragraph(str(class_code if class_code else ''), styles['Normal']), '',
                                   Paragraph(str(item_stock.year) + ' - ' + str(item_stock.month), styles['Normal']), '',
                                   Paragraph(str(qtyin), styles['Normal']), '', Paragraph(str(amount_in), styles['Normal']), '',
                                   Paragraph(str(qtyout), styles['Normal']), '', Paragraph(str(amount_out), styles['Normal'])])

                item_table = Table(table_data, colWidths=[140, 5, 60, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 85])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                     ]))
                elements.append(item_table)
            table_data = []
            table_data.append(['', '', '', '', '', '', '', '', "* GRAND TOTAL *", '', '', '', Paragraph(str(sum_qty_in), styles['Normal']), '',
                               Paragraph(intcomma("%.2f" % round_number(total_amount_his_in)), styles['Normal']), '',
                               Paragraph(str(sum_qty_out), styles['Normal']), '',
                               Paragraph(intcomma("%.2f" % round_number(total_amount_his_out)), styles['Normal'])])

            item_table = Table(table_data, colWidths=[140, 5, 60, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 65, 5, 85])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
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
                                      issue_to=issue_to, trx_code=trx_code
                                      ),
                  onLaterPages=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                       issue_to=issue_to, trx_code=trx_code),
                  canvasmaker=partial(NumberedPage, adjusted_height=-145, adjusted_width=235))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
