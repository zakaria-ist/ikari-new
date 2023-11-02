import math
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from companies.models import Company
from locations.models import Location
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from inventory.models import Incoming
from orders.models import OrderItem
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import round_number, get_decimal_place

colWidths = [90, 120, 50, 70, 60, 60, 60, 60]
rowHeights = 10
titleRowHeights = 12
REPORT_FONT_SIZE = 7


class Print_ST_IL2601:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, issue_from):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))
        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "IL2601 Inventory Control System"
        row1_info2 = ""
        row1_info3 = "Stock Listing (FIFO) by Location & Item"
        header_data.append([row1_info1, row1_info2, row1_info3])

        # # 2nd row
        row2_info1 = company.name
        row2_info2 = ""
        row2_info3 = "Grouped by , Item code  "

        header_data.append([row2_info1, row2_info2, Paragraph(row2_info3, styles['RightAlign'])])
        issue_from = issue_from.split('-')
        # # 3rd row
        row3_info1 = 'Date:' + str(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        row3_info2 = "Report period:  " + str(issue_from[1]) + '/' + str(issue_from[0])
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])

        header_table = Table(header_data, colWidths=[220, 220, 130, 10], rowHeights=titleRowHeights)
        header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                          ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                                          ('ALIGN', (1, -1), (1, -1), 'CENTER'),
                                          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                          ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
                                          ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                          ('FONTSIZE', (-1, 0), (-1, 0), 9),
                                          ('TOPPADDING', (0, 0), (-1, -1), 0),
                                          ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                          ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                          ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 30, doc.height + doc.topMargin - h)

        header_data = []

        row2_info1 = "Item Code"
        row2_info2 = "Description"
        row2_info3 = "Item"
        row2_info4 = "Ref.Doc.No"
        row2_info5 = "Receipt Date"
        row2_info6 = "Price"
        row2_info7 = "Balance Qty"
        row2_info8 = "Amount"

        header_data.append([row2_info1, row2_info2, row2_info3, row2_info4, row2_info5, row2_info6, row2_info7, row2_info8])

        row3_info1 = ""
        row3_info2 = ""
        row3_info3 = "Group"
        row3_info4 = ""
        row3_info5 = ""
        row3_info6 = ""
        row3_info7 = ""
        row3_info8 = "Subtotal"

        header_data.append([row3_info1, row3_info2, row3_info3, row3_info4, row3_info5, row3_info6, row3_info7, row3_info8])

        header_table = Table(header_data, colWidths=colWidths, rowHeights=titleRowHeights)
        header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                          ('FONTSIZE', (0, 0), (-1, -1), REPORT_FONT_SIZE),
                                          ('ALIGN', (7, 1), (7, 1), 'LEFT'),
                                          ('ALIGN', (0, 0), (3, 0), 'LEFT'),
                                          ('ALIGN', (4, 0), (7, 0), 'RIGHT'),
                                          ('LINEBELOW', (0, 1), (-1, 1), 0.25, colors.black),
                                          ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                                          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                          ('TOPPADDING', (0, 0), (-1, -1), 0),
                                          ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                          ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                          ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 30, doc.height + doc.topMargin - h - 35)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, location):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=100, bottomMargin=42, pagesize=self.pagesize)
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=REPORT_FONT_SIZE))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        stock_locations = []
        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        if company.currency.is_decimal:
            decimal_place = 2
        else:
            decimal_place = 1

        stock_locs = Location.objects.filter(is_hidden=False, company_id=company_id).order_by('code')
        if location:
            stock_locations.append(int(location))
        else:
            stock_locations = stock_locs.values_list('id', flat=True)

        next_location = False
        total_balance = total_amount = 0
        old_system_date = datetime.datetime.strptime("2020-12-31", '%Y-%m-%d')
        for location_id in stock_locations:  # For every location
            if next_location:
                elements.append(PageBreak())
            table_data = []
            cur_location = Location.objects.get(pk=location_id)
            table_data.append(['LOCATION CODE', ':', Paragraph(str(cur_location.code if cur_location else ''), styles['LeftAlignBold']), 'LOCATION NAME', ':',
                               Paragraph(str(cur_location.name if cur_location else ''), styles['LeftAlign']), 'TEL. NO', ':',
                               Paragraph(str(cur_location.phone if cur_location else ''), styles['LeftAlign'])])

            table_data.append(['PRICE TYPE', ':', Paragraph(str(company.currency.code + '$'), styles['LeftAlign']),
                               'ADDRESS', ':', Paragraph(str(cur_location.address if cur_location else '')[:85], styles['LeftAlign']), 'FAX NO', ':',
                               Paragraph(str(cur_location.fax if cur_location else ''), styles['LeftAlign'])])

            class_code = ''
            if cur_location.stock_class:
                if cur_location.stock_class == 1:
                    class_code = 'INTERNAL'
                else:
                    class_code = 'EXTERNAL'
            table_data.append(['STOCK CLASS', ':', Paragraph(str(class_code), styles['LeftAlign']), '', '', '', '', '', ''])

            table_data.append(['', '', '', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[60, 3, 60, 70, 5, 274, 35, 3, 60], rowHeights=titleRowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('FONTSIZE', (0, 0), (-1, -1), REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                            ]))
            elements.append(item_table)

            total_loc_balance = total_loc_amount = 0
            part_list = Incoming.objects.select_related('item').filter(is_hidden=False, location_id=location_id,
                                                                       company_id=company_id, is_history=0) \
                .order_by('item__code').values('item_id').distinct()
            for item in part_list:  # For every item-code
                multiple_entry = multiple_entry_total = 0
                try:
                    loc_items = Incoming.objects.select_related('item').select_related('location')\
                        .filter(is_hidden=False, is_history=0, location_id=location_id, item_id=item['item_id'])\
                        .exclude(balance_qty=0) \
                        .order_by('purchase_date', '-balance_qty')
                except:
                    loc_items = None

                if loc_items:
                    for loc_item in loc_items:
                        order_price = 0
                        purchase_date = datetime.datetime.strptime(str(loc_item.purchase_date), '%Y-%m-%d')
                        if purchase_date <= old_system_date:
                            try:
                                order_item = OrderItem.objects.filter(order__is_hidden=0,is_hidden=0, 
                                                order__document_number=loc_item.document_number,
                                                line_number=loc_item.line_number).first()
                                if order_item:
                                    order_price = order_item.price
                            except Exception as e:
                                print(e)
                        group_code = ''
                        if loc_item.item.category_id:
                            group_code = loc_item.item.category.code if loc_item.item.category else ''

                        if multiple_entry:
                            item_code = ''
                            item_description = ''
                        else:
                            item_code = loc_item.item.code[:21]
                            item_description = loc_item.item.short_description if loc_item.item.short_description else ''

                        # calculation every Amount
                        # total_line = round_number(int(loc_item.balance_qty * loc_item.unit_price * 100) / 100)
                        if order_price:
                            total_line = loc_item.balance_qty * order_price
                        else:
                            total_line = loc_item.balance_qty * loc_item.unit_price
                        # calculation loc Balance,Amount
                        total_loc_balance += loc_item.balance_qty
                        # total_loc_amount += round_number(loc_item.balance_qty * loc_item.unit_price)
                        total_loc_amount += total_line
                        # calculation all Balance,Amount
                        total_balance += loc_item.balance_qty
                        # total_amount += round_number(loc_item.balance_qty * loc_item.unit_price)
                        total_amount += total_line
                        table_data = []
                        table_data.append([Paragraph(str(item_code), styles['LeftAlign']), Paragraph(str(item_description), styles['LeftAlign']),
                                           Paragraph(str(group_code), styles['LeftAlign']), Paragraph(str(loc_item.document_number), styles['LeftAlign']),
                                           Paragraph(str(loc_item.purchase_date.strftime("%d/%m/%Y") if loc_item.purchase_date else '//'),  styles['RightAlign']),
                                           intcomma("%.6f" % order_price if order_price else loc_item.unit_price),
                                           intcomma("%.2f" % loc_item.balance_qty),
                                           intcomma(decimal_place_f % (math.floor(total_line * 10 ** decimal_place) / 10 ** decimal_place))])

                        item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                        ('FONTSIZE', (0, 0), (-1, -1), REPORT_FONT_SIZE),
                                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                                        ]))
                        elements.append(item_table)
                        multiple_entry += 1
                        multiple_entry_total += loc_item.balance_qty

                if multiple_entry > 1:  # Subtotal for multiple entry
                    table_data = []
                    table_data.append(['',  intcomma("%.2f" % multiple_entry_total)])
                    item_table = Table(table_data, colWidths=[530, 70], rowHeights=rowHeights)
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                    ('FONTSIZE', (0, 0), (-1, -1), REPORT_FONT_SIZE),
                                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                                    ]))
                    elements.append(item_table)

            # Location total
            table_data = []
            table_data.append(['', '', '', '', '', '', '',  ''])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('FONTSIZE', (0, 0), (-1, -1), REPORT_FONT_SIZE),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                            ]))
            elements.append(item_table)

            table_data = []
            table_data.append(['', '', '', '', '* LOCATION TOTAL *', '', total_loc_balance,
                               intcomma("%.2f" % (math.floor(total_loc_amount * 10 ** decimal_place) / 10 ** decimal_place))])

            item_table = Table(table_data, colWidths=colWidths)
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                            ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                                            ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                                            ('FONTSIZE', (0, 0), (-1, -1), 9)
                                            ]))
            elements.append(item_table)
            total_loc_balance = total_loc_amount = 0
            next_location = True

        # Grand total
        table_data = []
        table_data.append(['', '', '', '', '* GRAND TOTAL *', '', total_balance,
                           intcomma("%.2f" % (math.floor(total_amount * 10 ** decimal_place) / 10 ** decimal_place))])
        item_table = Table(table_data, colWidths=colWidths)
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('FONTSIZE', (0, 0), (-1, -1), 9)
                                        ]))
        elements.append(item_table)

        doc.build(elements, onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from),
                  onLaterPages=partial(self._header_footer, company_id=company_id, issue_from=issue_from),
                  canvasmaker=partial(NumberedPage, adjusted_height=110))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
