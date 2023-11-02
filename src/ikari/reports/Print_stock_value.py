from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
import calendar
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from locations.models import Location, LocationItem
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import LOCATION_PRICE_TYPE, LOCATION_STOCK_CLASS
from utilities.common import round_number, get_decimal_place


class Print_stock_value:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, sort_order, print_selection):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        canvas.saveState()

        TblStyle1 = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                     ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
                     ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('FONTSIZE', (1, 0), (1, 0), 12)]

        TblStyle2 = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                     ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
                     ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 3), (-1, 3), 5),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('FONTSIZE', (1, 0), (1, 0), 12)]

        header_data = []
        company = Company.objects.get(pk=company_id)
        current_yrprd = int(company.current_period_year_ic) if company.current_period_year_ic else int(datetime.datetime.now().strftime('%Y'))
        current_yrmth = int(company.current_period_month_ic) if company.current_period_month_ic else int(datetime.datetime.now().strftime('%m'))
        if int(current_yrmth) == 1:
            current_yrprd = int(current_yrprd) - 1
            current_yrmth = 12
        else:
            current_yrmth -= 1
        last_month_end = datetime.date(current_yrprd, current_yrmth, calendar.monthrange(current_yrprd, current_yrmth)[1])
        header_data.append(['IR4C00 Inventory Control System',
                            'Stock Value Report By Location As at ' + last_month_end.strftime('%B %Y')])
        header_data.append([company.name, ''])
        header_data.append(['Date: ' + str(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')), 'Page :        '])
        if int(print_selection) > 0:
            header_data.append(['', '<------------- AMOUNT BASED ON STOCKIST PRICE ------------->'])
        header_table = Table(header_data, colWidths=[235, 343])
        if int(print_selection) > 0:
            header_table.setStyle(TableStyle(TblStyle2))
        else:
            header_table.setStyle(TableStyle(TblStyle1))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        header_data = []
        row2_info1 = "LOCATION CODE & NAME"
        row2_info2 = "PRICE TYPE"
        row2_info3 = "OPENING AMT"
        row2_info4 = "STOCK IN AMT"
        row2_info5 = "STOCK OUT AMT"
        row2_info6 = "CLOSING AMT"
        header_data.append([row2_info1, '', row2_info2, '', row2_info3, '', row2_info4, '', row2_info5, '', row2_info6])
        header_table = Table(header_data, colWidths=[178, 5, 65, 5, 75, 5, 75, 5, 85, 5, 75])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - 65)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, sort_order, print_selection):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=17, leftMargin=17, topMargin=123, bottomMargin=42, pagesize=self.pagesize)

        style_normal = [('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (0, 0), 0),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)]

        style_grandtotal = [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                            ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)]

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='BiggerFont', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=12))

        company = Company.objects.get(pk=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        elements = []
        table_data = []
        price_type_dict = dict(LOCATION_PRICE_TYPE)
        record_count = 0
        # VERSI LAMA PERNAH MATCH SAMA GOOGLE DRIVE

        stock_class_dict = dict([stock_class[::-1] for stock_class in LOCATION_STOCK_CLASS])
        loc_list = Location.objects.filter(company_id=company_id, is_hidden=False, is_active=True,
                                           stock_class=stock_class_dict['Internal Stock']).order_by('code')
        loc_itm_data = LocationItem.objects.filter(item__company_id=company_id, is_hidden=False).order_by('location__code')

        grand_total1 = grand_total2 = grand_total3 = grand_total4 = 0
        for loc in loc_list:
            loc_total1 = loc_total2 = loc_total3 = loc_total4 = 0
            itm_per_loc = loc_itm_data.filter(location_id=loc.id)\
                .exclude(month_open_qty=0)\
                .exclude(month_open_qty__isnull=True).order_by('item__category__code', 'item__code')

            for loc_itm in itm_per_loc:
                price = (self.nvl(loc_itm.item.cost_price), self.nvl(loc_itm.item.stockist_price))[int(print_selection) > 0]
                opening_amt = self.nvl(loc_itm.month_open_qty) * price if int(print_selection) else self.nvl(loc_itm.onhand_amount)
                in_amt = self.validate_qty(loc_itm.onhand_qty, loc_itm.in_qty) * price
                out_amt = self.nvl(loc_itm.out_qty) * price
                closing_amt = opening_amt + in_amt - out_amt

                loc_total1 += opening_amt
                loc_total2 += in_amt
                loc_total3 += out_amt
                loc_total4 += closing_amt

            grand_total1 += loc_total1
            grand_total2 += loc_total2
            grand_total3 += loc_total3
            grand_total4 += loc_total4
            all_loc_total = loc_total1 + loc_total2 + loc_total3 + loc_total4
            if all_loc_total:
                record_count += 1
                table_data = [[Paragraph(loc.code + ' ' + loc.name, styles['LeftAlign']), '',
                               Paragraph(price_type_dict.get(str(loc.pricing_type)), styles['LeftAlign']), '',
                               Paragraph(intcomma(decimal_place_f % round_number(loc_total1)) if loc_total1 else '0.00', styles["RightAlign"]), '',
                               Paragraph(intcomma(decimal_place_f % round_number(loc_total2)) if loc_total2 else '0.00', styles["RightAlign"]), '',
                               Paragraph(intcomma(decimal_place_f % round_number(loc_total3)) if loc_total3 else '0.00', styles["RightAlign"]), '',
                               Paragraph(intcomma(decimal_place_f % round_number(loc_total4)) if loc_total4 else '0.00', styles["RightAlign"])]]

                table_body = Table(table_data, colWidths=[178, 5, 65, 5, 75, 5, 75, 5, 85, 5, 75])
                table_body.setStyle(TableStyle(style_normal))
                elements.append(table_body)

        all_grandtot = grand_total1 + grand_total2 + grand_total3 + grand_total4
        if all_grandtot:
            table_data = [[Paragraph('NO. OF RECORDS LISTED = ' + str(record_count), styles['LeftAlign']), '', '', '',
                           Paragraph(intcomma(decimal_place_f % round_number(grand_total1)) if grand_total1 else '0.00', styles["RightAlign"]), '',
                           Paragraph(intcomma(decimal_place_f % round_number(grand_total2)) if grand_total2 else '0.00', styles["RightAlign"]), '',
                           Paragraph(intcomma(decimal_place_f % round_number(grand_total3)) if grand_total3 else '0.00', styles["RightAlign"]), '',
                           Paragraph(intcomma(decimal_place_f % round_number(grand_total4)) if grand_total4 else '0.00', styles["RightAlign"])]]

            table_body = Table(table_data, colWidths=[178, 5, 65, 5, 75, 5, 75, 5, 85, 5, 75])
            table_body.setStyle(TableStyle(style_grandtotal))
            elements.append(table_body)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[178, 5, 65, 5, 75, 5, 75, 5, 85, 5, 75])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, sort_order=sort_order,
                                      print_selection=print_selection),
                  onLaterPages=partial(self._header_footer, company_id=company_id, sort_order=sort_order,
                                       print_selection=print_selection),
                  canvasmaker=partial(NumberedPage, adjusted_height=103, adjusted_width=15))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def nvl(self, param):
        return param if param else 0

    def validate_qty(self, oh_qty, in_qty):
        result = 0
        if self.nvl(in_qty) > 0:
            calculate = self.nvl(oh_qty) + self.nvl(in_qty)
            if calculate > 0:
                result = calculate
        return result
