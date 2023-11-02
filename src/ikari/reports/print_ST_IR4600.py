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
from inventory.models import History
from locations.models import Location, LocationItem
from items.models import Item, ItemMeasure
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import INV_IN_OUT_FLAG


class print_ST_IR4600:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
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
        row1_info1 = "IR4600 Inventory Control System"
        row1_info2 = ""
        row1_info3 = "Monthly Transaction Summary By Item & Location As At " + str(issue_to.strftime('%B %Y')).upper()
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

        header_data.append(
            [row1_info1, row1_info2, row1_info3, row1_info4, row1_info5, row1_info6, row1_info7, row1_info8])
        spaci = ''
        row2_info1 = "Item Code"
        row2_info2 = "Item"
        row2_info3 = "Location"
        row2_info4 = "Location Type"
        row2_info5 = "Stock"
        row2_info6 = "Opening"
        row2_info7 = "--------"
        row2_info8 = "Transaction Summary"
        row2_info9 = "--------"
        row2_info10 = "Closing"
        row2_info11 = "M'ment"

        header_data.append([row2_info1, spaci, row2_info2, spaci, row2_info3, spaci, row2_info4, spaci, row2_info5, spaci, row2_info6,
                            spaci, row2_info7, spaci, row2_info8, spaci, row2_info9, spaci, row2_info10, spaci, row2_info11])

        row3_info1 = ""
        row3_info2 = "Group"
        row3_info3 = "Code"
        row3_info4 = ""
        row3_info5 = "Class"
        row3_info6 = "Quantity"
        row3_info7 = "Code"
        row3_info8 = "In-Qty"
        row3_info9 = "Out-Qty"
        row3_info10 = "Qty"
        row3_info11 = ""

        header_data.append([row3_info1, spaci, row3_info2, spaci, row3_info3, spaci, row3_info4, spaci, row3_info5, spaci, row3_info6, spaci,
                            row3_info7, spaci, row3_info8, spaci, row3_info9, spaci, row3_info10, spaci, row3_info11])

        header_table = Table(header_data, colWidths=[90, 5, 65, 5, 60, 5, 65, 5, 65, 5, 85, 5, 45, 5, 85, 5, 68, 5, 65, 5, 65])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ('ALIGN', (12, 0), (12, -1), 'RIGHT'),
             ('ALIGN', (14, 0), (14, -1), 'CENTER'),
             ('ALIGN', (16, 0), (16, -1), 'LEFT'),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 50)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=150,
                                bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=11))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))
        company = Company.objects.get(pk=company_id)
        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        # process table_data
        array_data = str(issue_from).split('-')

        year = int(array_data[0])
        month = int(array_data[1])

        issue_from = datetime.date(year, month, 1)
        issue_to = datetime.date(year, month, calendar.monthrange(year, month)[1])

        history_list = History.objects.filter(company_id=company_id, is_hidden=0, year=year, month=month)
        lewatHIs = history_list.values("item_code_id", 'location_id').order_by('item_code__code').distinct()

        if lewatHIs:
            for item_stock in lewatHIs:
                here_Out = history_list.filter(item_code_id=item_stock['item_code_id'], io_flag=dict(INV_IN_OUT_FLAG)['OUT'])
                here_In = history_list.filter(item_code_id=item_stock['item_code_id'], io_flag=dict(INV_IN_OUT_FLAG)['IN'])

                itm = Item.objects.get(pk=item_stock['item_code_id'])
                msc = ItemMeasure.objects.get(pk=itm.inv_measure_id)
                inv_measure_id = msc.code

                if item_stock['location_id']:
                    loc = Location.objects.get(pk=item_stock['location_id'])
                    cek_stock = LocationItem.objects.filter(is_hidden=0,
                                                            location_id=item_stock['location_id'],
                                                            item_id=item_stock['item_code_id']).last()
                currency = company.currency.code
                sum_in_qty = 0
                if here_In:
                    for in_itm in here_In:
                        sum_in_qty += in_itm.quantity

                    trans_code_in = here_In.first().transaction_code.code
                    table_data = []
                    table_data.append([Paragraph(str(itm.code if item_stock['item_code_id'] else ''), styles['Normal']), '',
                                       Paragraph(str(itm.category.code if itm else ''), styles['Normal']), '',
                                       Paragraph(str(loc.code if loc else ''), styles['Normal']), '',
                                       Paragraph(str(currency if currency else ''), styles['Normal']), '',
                                       Paragraph(str('INTERNAL' if int(loc.stock_class) == 1 else 'EXTERNAL'), styles['Normal']), '',
                                       Paragraph(str(cek_stock.month_open_qty if cek_stock else 'month_open_qty'), styles['Normal']), '',
                                       Paragraph(str(trans_code_in), styles['Normal']), '', Paragraph(str(sum_in_qty), styles['Normal']), '',
                                       Paragraph(str(''), styles['Normal']), '',
                                       Paragraph(str(cek_stock.month_closing_qty if cek_stock else 'month_closing_qty'), styles['Normal']), '',
                                       Paragraph(str(inv_measure_id), styles['Normal'])])

                    item_table = Table(table_data, colWidths=[90, 5, 65, 5, 60, 5, 65, 5, 65, 5, 85, 5, 45, 5, 85, 5, 68, 5, 65, 5, 65])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (1, 0), (1, 0), 12),
                         ('LINEBELOW', (10, 2), (-1, 2), 0.25, colors.black),
                         ('ALIGN', (12, 0), (12, -1), 'RIGHT'),
                         ('ALIGN', (14, 0), (14, -1), 'CENTER'),
                         ('ALIGN', (16, 0), (16, -1), 'LEFT'),
                         ]))
                    elements.append(item_table)

                sum_out_qty = 0
                if here_Out:
                    for out_itm in here_Out:
                        sum_out_qty += out_itm.quantity

                    trans_code_out = here_Out.first().transaction_code.code
                    table_data = []
                    if not here_In:
                        table_data = []
                        table_data.append([Paragraph(str(itm.code if item_stock['item_code_id'] else ''), styles['Normal']), '',
                                           Paragraph(str(itm.category.code if itm else ''), styles['Normal']), '',
                                           Paragraph(str(loc.code if loc else ''), styles['Normal']), '',
                                           Paragraph(str(currency if currency else ''), styles['Normal']), '',
                                           Paragraph(str('INTERNAL' if int(loc.stock_class) == 1 else 'EXTERNAL'), styles['Normal']), '',
                                           Paragraph(str(cek_stock.month_open_qty if cek_stock else ''), styles['Normal']), '',
                                           Paragraph(str(trans_code_out if trans_code_out else ''), styles['Normal']), '',
                                           Paragraph(str(''), styles['Normal']), '', Paragraph(str(sum_out_qty), styles['Normal']), '',
                                           Paragraph(str(cek_stock.month_closing_qty if cek_stock else ''), styles['Normal']), '',
                                           Paragraph(str(inv_measure_id), styles['Normal'])])
                    else:
                        table_data.append([Paragraph(str(), styles['Normal']), '', Paragraph(str(), styles['Normal']), '',
                                           Paragraph(str(), styles['Normal']), '', Paragraph(str(), styles['Normal']), '',
                                           Paragraph(str(), styles['Normal']), '', Paragraph(str(''), styles['Normal']), '',
                                           Paragraph(str(trans_code_out if trans_code_in else ''), styles['Normal']), '',
                                           Paragraph(str(''), styles['Normal']), '', Paragraph(str(sum_out_qty), styles['Normal']), '',
                                           Paragraph(str(''), styles['Normal']), '', Paragraph(str(inv_measure_id), styles['Normal'])])

                    item_table = Table(table_data, colWidths=[90, 5, 65, 5, 60, 5, 65, 5, 65, 5, 85, 5, 45, 5, 85, 5, 68, 5, 65, 5, 65])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (1, 0), (1, 0), 12),
                         ('LINEABOVE', (10, 1), (-1, 1), 0.25, colors.black),
                         ('ALIGN', (12, 0), (1, 0), 'RIGHT'),
                         ('ALIGN', (14, 0), (1, 0), 'CENTER'),
                         ('ALIGN', (16, 0), (1, 0), 'LEFT'),
                         ]))
                    elements.append(item_table)
                if here_Out or here_In:
                    table_data = []
                    table_data.append([Paragraph(str(), styles['Normal']), '', Paragraph(str(), styles['Normal']), '',
                                       Paragraph(str(), styles['Normal']), '', Paragraph(str(), styles['Normal']), '',
                                       Paragraph(str(), styles['Normal']), '', Paragraph(str(''), styles['Normal']), '',
                                       Paragraph(str('* ITEM CODE TOTAL *'), styles['Normal']), '',
                                       Paragraph(str(sum_in_qty), styles['Normal']), '', Paragraph(str(sum_out_qty), styles['Normal']), '',
                                       Paragraph(str(''), styles['Normal']), '', Paragraph(str(''), styles['Normal'])])

                    item_table = Table(table_data, colWidths=[90, 5, 65, 5, 60, 5, 65, 5, 65, 5, 5, 5, 125, 5, 85, 5, 68, 5, 65, 5, 65])
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (1, 0), (1, 0), 12),
                         ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
                         ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
                         ('ALIGN', (12, 0), (12, -1), 'RIGHT'),
                         ('ALIGN', (14, 0), (14, -1), 'CENTER'),
                         ('ALIGN', (16, 0), (16, -1), 'LEFT'),
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
                  canvasmaker=partial(NumberedPage, adjusted_height=-145, adjusted_width=235))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
