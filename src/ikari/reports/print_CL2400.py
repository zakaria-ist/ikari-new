from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from suppliers.models import Supplier
from contacts.models import Contact
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

rowHeights = 12
topRowHeights = 45
bottomRowHeights = 25


class Print_CL2400:
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
        row1_info1 = "CL2400 AP Listing From SP System"
        row1_info2 = "Supplier File Listing (Summary) "
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
        row4_info1 = "Print Selection : [Supplier Code]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])
        # 5st row
        row5_info1 = "Supplier : [] To []"
        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])

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

        table_data = []
        table_header = ['Line', 'Supplier Code/Name', '', 'Address', '']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[30, 65, 130, 155, 150], rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (1, 0), (2, 0)),
             ('SPAN', (4, 0), (-1, 0)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, supplier_code):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=115, bottomMargin=42, pagesize=self.pagesize)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        sup_item_all = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1).order_by('code')
        supp_list = eval(supplier_code)
        if len(supp_list):
            sup_item_all = sup_item_all.filter(id__in=supp_list)

        count = 0
        for i, my_item in enumerate(sup_item_all):
            if my_item.name != None:
                count += 1
                address = 'NULL'
                if my_item.address != None:
                    address = my_item.address
                table_data = []
                table_data.append(
                    [count, my_item.code.replace('\r', ''),
                     Paragraph(my_item.name, styles['LeftAlign']),
                     address.replace('\n\n', '\n'), ''])
                item_table = Table(table_data, colWidths=[30, 70, 170, 140, 120], rowHeights=topRowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (0, 0), (4, -1), 'LEFT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('SPAN', (3, 0), (4, 0)),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                     ]))
                elements.append(item_table)

                contact_list = Contact.objects.filter(is_hidden=0, company_id=company_id, supplier_id=my_item.id)
                for my_contact in contact_list:
                    table_data = []
                    table_data.append(
                        ['', Paragraph('Attention : ' + my_contact.name, styles['LeftAlign']),
                         'Tel No : ' + my_contact.phone if my_contact.phone else '',
                         'Fax No : ' + my_contact.fax if my_contact.fax else '',
                         'Designation : ' + my_contact.designation if my_contact.designation else ''])
                    item_table = Table(table_data, colWidths=[30, 140, 105, 105, 140], rowHeights=bottomRowHeights)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (0, 0), (4, -1), 'LEFT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                         ]))
                    elements.append(item_table)

        # Create the table
        if len(table_data) == 0:
            table_data.append(['', '', '', '', ''])
            item_table = Table(table_data, colWidths=[30, 65, 130, 155, 150], rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (0, 0), (4, -1), 'LEFT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
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
