from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from items.models import ItemCategory, ItemMeasure
from taxes.models import Tax
from accounts.models import Account
from countries.models import Country
from currencies.models import Currency
from accounting.models import PaymentCode
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company, CostCenters
from functools import partial

rowHeights = 14
colWidths = [50, 100, 300, 90]


class Print_CL2100:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, code_type):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "CL2100 AP Listing From S&P System"
        row1_info2 = "Code File Listing"
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
        row4_info1 = "Code Type : [" + code_type + "]"
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
        table_header.append(['Line', 'Code', 'Description', 'Last Update'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 15, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=120, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        item_list = []
        if code == 'account':
            item_list = Account.objects.filter(
                is_hidden=0, company_id=company_id).order_by('account_segment')
            code_type = 'Account'
        elif code == 'tax':
            item_list = Tax.objects.filter(is_hidden=0, company_id=company_id).order_by('code')
            code_type = 'Tax'
        elif code == 'country':
            item_list = Country.objects.filter(is_hidden=0).order_by('code')
            code_type = 'Country'
        elif code == 'currency':
            item_list = Currency.objects.filter(is_hidden=0).order_by('code')
            code_type = 'Currency'
        elif code == 'payment':
            item_list = PaymentCode.objects.filter(is_hidden=0, is_active=1).exclude(source_type__isnull=True).order_by('code')
            code_type = 'Payment Mode'
        elif code == 'part_group':
            item_list = ItemCategory.objects.filter(is_hidden=0).order_by('code')
            code_type = 'Part Group'
        elif code == 'measurement':
            item_list = ItemMeasure.objects.filter(is_hidden=0, is_active=1).order_by('code')
            code_type = 'Measurement'
        elif code == 'cost':
            code_type = 'Cost Center'
            company = Company.objects.get(pk=company_id)
            if company.use_segment:
                item_list = CostCenters.objects.filter(is_hidden=0, company_id=company_id).order_by('code')

        for i, mItem in enumerate(item_list):
            table_data = []
            table_data.append([
                i + 1,
                mItem.code,
                mItem.name[0:30] if mItem.name else '',
                mItem.update_date.strftime("%d/%m/%Y")
            ])

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
                  onFirstPage=partial(self._header_footer, company_id=company_id, code_type=code_type),
                  onLaterPages=partial(self._header_footer, company_id=company_id, code_type=code_type),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
