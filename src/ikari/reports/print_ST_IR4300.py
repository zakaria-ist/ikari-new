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
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import LOCATION_STOCK_CLASS, LOCATION_PRICE_TYPE
from locations.models import Location, LocationItem
from items.models import Item
from utilities.common import round_number, get_decimal_place


class print_ST_IR4300:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, issue_from, issue_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        canvas.saveState()

        header_data = []
        row1_info1 = "IR4300 Inventory Control System"
        row1_info2 = "Stock Value Report By Location & Item As " + issue_to.strftime('%d/%m/%Y')
        header_data.append([row1_info1, row1_info2])

        row2_info1 = Company.objects.get(pk=company_id).name
        row2_info2 = "Grouped by Location Code, Item code"
        header_data.append([row2_info1, row2_info2])

        row3_info1 = 'Date:' + str(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])

        header_table = Table(header_data, colWidths=[400, 410])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (1, -1), (1, -1), 'CENTER'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('FONTSIZE', (-1, 0), (-1, 0), 14),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin + 30)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin + 30 - h)

        header_data = []
        spaci = ''
        row2_info1 = "ITEM CODE"
        row2_info2 = ""
        row2_info3 = "OPENING"
        row2_info5 = "STOCK IN"
        row2_info6 = "STOCK OUT"
        row2_info7 = "CLOSING"
        row2_info8 = "(FIFO)"
        row2_info9 = "S$"

        header_data.append([row2_info1, spaci, row2_info2, spaci, row2_info3, spaci, row2_info5, spaci, row2_info6,
                            spaci, row2_info7, spaci, row2_info8, spaci, row2_info9])

        row3_info1 = "ITEM GROUP"
        row3_info2 = "DESCRIPTION"
        row3_info3 = "QTY"
        row3_info5 = "QTY"
        row3_info6 = "QTY"
        row3_info7 = "QTY"
        row3_info8 = "UNIT COST"
        row3_info9 = "CLOSING VALUE"

        header_data.append(
            [row3_info1, spaci, row3_info2, spaci, row3_info3, spaci, row3_info5, spaci, row3_info6, spaci, row3_info7, spaci, row3_info8, spaci, row3_info9])
        header_table = Table(header_data, colWidths=[80, 5, 180, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('LINEBELOW', (0, 1), (-1, 1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
             ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - 50)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=150, bottomMargin=42, pagesize=landscape(A4))

        style_normal = [('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (0, 0), 0)]

        style_subtotal = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                          ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                          ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                          ('LEFTPADDING', (0, 0), (-1, -1), 0),
                          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                          ('BOTTOMPADDING', (0, -1), (-1, -1), 10)]

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='BiggerFont', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=12))

        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        elements = []
        table_data = []
        isFirstLoc = True
        price_type_dict = dict(LOCATION_PRICE_TYPE)
        stock_class_dict = dict(LOCATION_STOCK_CLASS)
        array_data = str(issue_from).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        category_list = Item.objects.filter(company_id=company_id, is_hidden=0). \
            values_list('category', flat=True).distinct().order_by('-category__code')
        loc_list = Location.objects.filter(company_id=company_id, is_hidden=False, is_active=True).order_by('code')
        loc_itm_data = LocationItem.objects.filter(item__company_id=company_id, is_hidden=False).order_by('location__code')
        if loc_list:
            grandtotal1 = grandtotal2 = grandtotal3 = grandtotal4 = grandtotal6 = all_grandtot = 0
            for loc in loc_list:
                loc_total1 = loc_total2 = loc_total3 = loc_total4 = loc_total5 = loc_total6 = all_loc_total = 0
                itm_per_loc = loc_itm_data.filter(location_id=loc.id)
                if itm_per_loc:
                    address = loc.address.split(',')
                    if not isFirstLoc:
                        table_data.append(['', '', '', '', '', '', '', '', '', '', '', ''])
                    table_data.append([Paragraph('LOCATION CODE', styles['BiggerFont']), '',
                                       Paragraph(': ' + loc.code if loc.code else ':', styles['BiggerFont']), '',
                                       Paragraph('LOCATION NAME', styles['BiggerFont']), '',
                                       Paragraph(': ' + loc.name if loc.name else ':', styles['BiggerFont']), '',
                                       '', Paragraph('TEL. NO', styles['BiggerFont']), '',
                                       Paragraph(': ' + loc.phone if loc.phone else ':', styles['BiggerFont'])])

                    table_data.append([Paragraph('PRICE TYPE', styles['BiggerFont']), '',
                                       Paragraph(': ' + price_type_dict.get(str(loc.pricing_type)) if loc.pricing_type else ':', styles['BiggerFont']), '',
                                       Paragraph('ADDRESS', styles['BiggerFont']), '',
                                       Paragraph(': ' + address[0] if len(address) > 0 else ':', styles['BiggerFont']), '',
                                       '', Paragraph('FAX. NO', styles['BiggerFont']), '',
                                       Paragraph(': ' + loc.fax if loc.fax else ':', styles['BiggerFont'])])

                    table_body = Table(table_data, colWidths=[100, 5, 100, 25, 100, 5, 275, 5, 10, 50, 5, 110])
                    table_body.setStyle(TableStyle(style_normal))
                    elements.append(table_body)
                    table_data = [[Paragraph('STOCK CLASS', styles['BiggerFont']), '',
                                   Paragraph(': ' + stock_class_dict.get(str(loc.stock_class)) if loc.stock_class else ':', styles['BiggerFont']), '',
                                   '', '', Paragraph(address[1] if len(address) > 1 else '', styles['BiggerFont']), '', '', '', '', '']]

                    table_data.append(['', '', '', '', '', '', Paragraph(address[2] if len(address) > 2 else '', styles['BiggerFont']), '',
                                       '', '', '', ''])

                    table_body = Table(table_data, colWidths=[100, 5, 100, 25, 100, 12, 268, 5, 10, 50, 5, 110])
                    table_body.setStyle(TableStyle(style_normal))
                    elements.append(table_body)

                for category_item in category_list:
                    subtotal1 = subtotal2 = subtotal3 = subtotal4 = subtotal5 = subtotal6 = all_subtot = 0
                    itm_loc_per_partgp = itm_per_loc.filter(item__category__id=category_item).order_by('item__code')
                    for loc_itm in itm_loc_per_partgp:
                        if loc_itm.month_open_qty and loc_itm.month_open_qty != 0:
                            in_qty = loc_itm.in_qty if loc_itm.in_qty else 0
                            out_qty = loc_itm.out_qty if loc_itm.out_qty else 0
                            month_closing_qty = loc_itm.month_closing_qty if loc_itm.month_closing_qty else 0
                            cost_price = loc_itm.cost_price if loc_itm.cost_price else 0
                            onhand_amount = loc_itm.onhand_amount if loc_itm.onhand_amount else 0

                            table_data = [[Paragraph(loc_itm.item.code, styles['LeftAlign']), '', '', '',
                                           Paragraph(intcomma("%.2f" % loc_itm.month_open_qty), styles["RightAlign"]), '',
                                           Paragraph(intcomma("%.2f" % in_qty), styles["RightAlign"]), '',
                                           Paragraph(intcomma("%.2f" % out_qty), styles["RightAlign"]), '',
                                           Paragraph(intcomma("%.2f" % month_closing_qty), styles["RightAlign"]), '',
                                           Paragraph(intcomma("%.4f" % round_number(cost_price, 4)), styles["RightAlign"]), '',
                                           Paragraph(intcomma(decimal_place_f % round_number(onhand_amount)), styles["RightAlign"])]]
                            table_body = Table(table_data, colWidths=[245, 5, 5, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85])
                            table_body.setStyle(TableStyle(style_normal))
                            elements.append(table_body)

                            table_data = [[Paragraph(loc_itm.item.category.code if loc_itm.item.category else '', styles['LeftAlign']), '',
                                           Paragraph(loc_itm.item.name, styles['LeftAlign']), '', '', '', '', '', '', '', '', '', '', '', '', '']]

                            table_body = Table(table_data, colWidths=[80, 5, 645, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5])
                            table_body.setStyle(TableStyle(style_normal))
                            elements.append(table_body)
                            table_data = []

                            subtotal1 += loc_itm.month_open_qty
                            subtotal2 += in_qty
                            subtotal3 += out_qty
                            subtotal4 += month_closing_qty
                            subtotal5 += cost_price
                            subtotal6 += onhand_amount

                            loc_total1 += loc_itm.month_open_qty
                            loc_total2 += in_qty
                            loc_total3 += out_qty
                            loc_total4 += month_closing_qty
                            loc_total5 += cost_price
                            loc_total6 += onhand_amount

                            grandtotal1 += loc_itm.month_open_qty
                            grandtotal2 += in_qty
                            grandtotal3 += out_qty
                            grandtotal4 += month_closing_qty
                            grandtotal6 += onhand_amount

                    all_subtot = subtotal1 + subtotal2 + subtotal3 + subtotal4 + subtotal5 + subtotal6
                    if all_subtot:
                        table_data = [['', Paragraph('ITEM CATEGORY TOTAL', styles['BiggerFont']), '', '',
                                       Paragraph(intcomma("%.2f" % subtotal1), styles["RightAlign"]), '',
                                       Paragraph(intcomma("%.2f" % subtotal2), styles["RightAlign"]), '',
                                       Paragraph(intcomma("%.2f" % subtotal3), styles["RightAlign"]), '',
                                       Paragraph(intcomma("%.2f" % subtotal4), styles["RightAlign"]), '',
                                       Paragraph(intcomma("%.4f" % round_number(subtotal5, 4)), styles["RightAlign"]), '',
                                       Paragraph(intcomma(decimal_place_f % round_number(subtotal6)), styles["RightAlign"])]]

                        table_body = Table(table_data, colWidths=[20, 230, 5, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85])
                        table_body.setStyle(TableStyle(style_subtotal))
                        elements.append(table_body)
                    table_data = []

                all_loc_total = loc_total1 + loc_total2 + loc_total3 + loc_total4 + loc_total5 + loc_total6
                if all_loc_total:
                    table_data = [['', Paragraph('* LOCATION TOTAL *', styles['BiggerFont']), '', '',
                                   Paragraph(intcomma("%.2f" % loc_total1), styles["RightAlign"]), '',
                                   Paragraph(intcomma("%.2f" % loc_total2), styles["RightAlign"]), '',
                                   Paragraph(intcomma("%.2f" % loc_total3), styles["RightAlign"]), '',
                                   Paragraph(intcomma("%.2f" % loc_total4), styles["RightAlign"]), '',
                                   Paragraph(intcomma("%.4f" % round_number(loc_total5, 4)), styles["RightAlign"]), '',
                                   Paragraph(intcomma(decimal_place_f % round_number(loc_total6)), styles["RightAlign"])]]
                    table_body = Table(table_data, colWidths=[20, 230, 5, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85])
                    table_body.setStyle(TableStyle(style_subtotal))
                    elements.append(table_body)
                table_data = []
                isFirstLoc = False

            all_grandtot = grandtotal1 + grandtotal2 + grandtotal3 + grandtotal4 + grandtotal6
            if all_grandtot:
                table_data = [['', Paragraph('* GRAND TOTAL *', styles['BiggerFont']), '', '',
                               Paragraph(intcomma("%.2f" % grandtotal1), styles["RightAlign"]), '',
                               Paragraph(intcomma("%.2f" % grandtotal2), styles["RightAlign"]), '',
                               Paragraph(intcomma("%.2f" % grandtotal3), styles["RightAlign"]), '',
                               Paragraph(intcomma("%.2f" % grandtotal4), styles["RightAlign"]), '',
                               '', '', Paragraph(intcomma(decimal_place_f % round_number(grandtotal6)), styles["RightAlign"])]]

                table_body = Table(table_data, colWidths=[20, 230, 5, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85])
                table_body.setStyle(TableStyle(style_subtotal))
                elements.append(table_body)
            table_data = []

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[80, 5, 170, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85, 5, 85])
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
