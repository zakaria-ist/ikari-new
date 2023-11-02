from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from taxes.models import Tax
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

rowHeights = 14
colWidths = [30, 60, 160, 30, 40, 50, 90, 90]


class Print_TL1200:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "TL1200 Sales / Purchase System"
        row1_info2 = "Tax Master File Listing"
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        row4_info1 = "Print Selection : [] - []"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[265, 273], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('FONTSIZE', (1, 0), (1, 0), 14),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_header = []
        table_header.append(['Tax', 'Shrot-Name', 'Description', 'Type', 'Rate(%)', 'Account', 'MTD-TAXL(G/L)', 'YTD-TAXL(G/L)'])
        table_header.append(['Code', '', '', '', '', 'Code', 'MTD-TAXE(Doc)', 'YTD-TAXE(Doc)'])
        table_header.append(['', '', '', '', '', '', 'MTD-TAXT(Tax)', 'YTD-TAXT(Tax)'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, tax_code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=140, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        tax_list = Tax.objects.filter(is_hidden=0, company_id=company_id).exclude(rate__isnull=True).order_by('code')

        t_list = eval(tax_code)
        if len(t_list):
            tax_list = tax_list.filter(id__in=t_list)

        for i, mItem in enumerate(tax_list):
            table_data = []
            table_data.append([mItem.code, mItem.shortname[0:10] if mItem.shortname else '',
                               mItem.name[0:25] if mItem.name else '', mItem.tax_type,
                               intcomma("%.2f" % mItem.rate), mItem.tax_account_code.code if mItem.tax_account_code else '',
                               intcomma("%.2f" % mItem.mtd) if mItem.mtd else intcomma("%.2f" % 0),
                               intcomma("%.2f" % mItem.ytd) if mItem.ytd else intcomma("%.2f" % 0)])

            table_data.append(['', '', '', '', '', '',
                               intcomma("%.2f" % mItem.mtdoc) if mItem.mtdoc else intcomma("%.2f" % 0),
                               intcomma("%.2f" % mItem.ytdoc) if mItem.ytdoc else intcomma("%.2f" % 0)])

            table_data.append(['', '', '', '', '', '',
                               intcomma("%.2f" % mItem.mtdoc) if mItem.mtdoc else intcomma("%.2f" % 0),
                               intcomma("%.2f" % mItem.ytdoc) if mItem.ytdoc else intcomma("%.2f" % 0)])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (4, 0), (7, 0), 'RIGHT'),
                 ('ALIGN', (4, 1), (7, 1), 'RIGHT'),
                 ('ALIGN', (4, 2), (7, 2), 'RIGHT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('TOPPADDING', (0, 0), (-1, 0), 10),
                 ('BOTTOMPADDING', (0, 2), (-1, -1), 10),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

        # Create the table
        if len(elements) == 0:
            table_data = []
            table_data.append(['', '', '', '', ''])
            item_table = Table(table_data, colWidths=[30, 65, 130, 155, 150], rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id),
                  onLaterPages=partial(self._header_footer, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
