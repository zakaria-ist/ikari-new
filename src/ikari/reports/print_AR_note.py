from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from accounting.models import Journal
from companies.models import Company
from contacts.models import Contact
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import round_number


class Print_AR_Note:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, journal_id, print_header, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Draw header of PDF
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomTitle', fontName=s.REPORT_FONT_BOLD, fontSize=16, leading=22,
                                  alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CustomHeader', fontName='Times-BoldItalic', fontSize=16, leading=18,
                                  alignment=TA_LEFT))
        journal = Journal.objects.get(pk=journal_id)
        # company = Company.objects.get(pk=company_id)

        # ===========================Header Image ===========================
        if print_header == '1':
            canvas.line(50, doc.height + doc.topMargin - 45, doc.width + doc.leftMargin + 10,
                        doc.height + doc.topMargin - 45)
            logo_exist = False
            if journal.company.header_logo:
                try:
                    path_header_logo = s.MEDIA_ROOT + str(journal.company.header_logo)
                    canvas.drawImage(path_header_logo, 65, doc.height + doc.topMargin - 35, 500, 60)
                except Exception as e:
                    print(e)
                    logo_exist = False
            if not logo_exist:
                header_data = []
                row1_info1 = Paragraph(journal.company.name.upper() if journal.company.name else '', styles['CustomHeader'])
                header_data.append([row1_info1])

                row2_info1 = Paragraph(journal.company.address if journal.company.address else '', styles['LeftAlign'])
                header_data.append([row2_info1])

                row3_info1 = "TEL: " + journal.company.phone if journal.company.phone else ''
                row3_info1 = row3_info1 + "        " + "FAX: " + journal.company.fax if journal.company.fax else ''
                header_data.append([row3_info1])

                row4_info1 = "GST Co Reg No : " + journal.company.company_number if journal.company.company_number else ''
                header_data.append([row4_info1])

                header_table = Table(header_data, colWidths=[430])
                header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                  ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                  ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                  ('BOTTOMPADDING', (0, -1), (-1, -1), 0),
                                                  ('TOPPADDING', (0, -1), (-1, -1), 0),
                                                  ]))

                w, h = header_table.wrap(doc.width, doc.topMargin)
                header_table.drawOn(canvas, doc.leftMargin + 60, doc.height + doc.topMargin - 40)
        # ===========================Header Title ===========================
        header_data = []
        if journal.document_type == '1':
            custom_title = 'Sale Invoice'
        if journal.document_type == '2':
            custom_title = 'Debit Note'
        if journal.document_type == '3':
            custom_title = 'Credit Note'

        row1_info1 = Paragraph(custom_title.upper(), styles['CustomTitle'])
        header_data.append([row1_info1])

        header_table = Table(header_data, colWidths=[530])
        header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                          ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 12, doc.height + doc.topMargin - h - 60)

        # ===========================Header Title Left===========================
        header_data = []

        if journal.customer:
            header_data.append(['', ''])
            header_data.append(['', journal.customer.name])
            address = journal.customer.address if journal.customer.address else journal.customer.note1
            row4_info1 = Paragraph(address.replace('\n', '<br />\n'), styles['LeftAlign'])
            header_data.append(['', row4_info1])
            row5_info1 = 'ATTN: '
            contact = Contact.objects.filter(is_hidden=0, company_id=company_id, customer_id=journal.customer.id).first()
            if contact:
                row5_info1 = row5_info1 + contact.name
            header_data.append(['', ''])
            header_data.append(['', row5_info1])

        header_table = Table(header_data, colWidths=[20, 330])
        header_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                          ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                          ('RIGHTPADDING', (-1, 0), (-1, -1), 17),
                                          ('BOTTOMPADDING', (0, -1), (-1, -1), 20),
                                          ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                          ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 12, doc.height + doc.topMargin - h - 80)

        # == == == == == == == == == == == == == =Header Title RIGHT== == == == == == == == == == == == == =
        header_data = []
        if journal:
            row3_info2 = custom_title + ' No.'
            row3_info3 = ': ' + journal.document_number
            header_data.append([row3_info2, row3_info3])

            row4_info2 = 'DATE'
            row4_info3 = ': ' + journal.document_date.strftime('%d %B %Y')
            header_data.append([row4_info2, row4_info3])

            header_data.append(['PAGE', ': '])

        header_table = Table(header_data, colWidths=[70, 140])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin + 340, doc.height + doc.topMargin - h - 100)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, journal_id, print_header, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=60, topMargin=250, bottomMargin=42, pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomHeaderStyle', fontName=s.REPORT_FONT_BOLD, fontSize=16, leading=22,
                                  alignment=TA_CENTER))
        # Our container for 'Flowable' objects
        elements = []
        journal = Journal.objects.get(pk=journal_id)
        if journal.currency.is_decimal:
            decimal_place = "%.2f"
        else:
            decimal_place = "%.0f"
        company = Company.objects.get(pk=company_id)

        # Draw Content of PDF
        item_list_data = []

        item_data = ['Description', '', '', '', '', 'Amount']
        item_list_data.append(item_data)
        item_data = ['', '', '', '', '', journal.currency.code + '  ']
        item_list_data.append(item_data)
        item_data = ['', '', '', '', '', '']
        item_list_data.append(item_data)
        item_data = ['Being charged for the following:', '', '', '', '', '']
        item_list_data.append(item_data)
        item_data = ['1', journal.name, '', '---', '', intcomma(decimal_place % round_number(journal.total_amount))]
        item_list_data.append(item_data)
        item_data = ['', '', '', '', '', '']
        item_list_data.append(item_data)
        item_list_data.append(item_data)
        item_data = ['', '', '', '', '', '']
        item_list_data.append(item_data)
        item_list_data.append(item_data)
        item_data = ['', '', '', '', '', '']
        item_list_data.append(item_data)
        item_list_data.append(item_data)
        item_data = ['', '', '', '', '', '']
        item_list_data.append(item_data)

        # Create the table
        item_table = Table(item_list_data, colWidths=[30, 190, 90, 75, 75, 75])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                        ('SPAN', (0, 1), (1, 1)),
                                        ('LINEBELOW', (0, 1), (5, 1), 0.25, colors.black),
                                        ('LINEABOVE', (0, 0), (5, 0), 0.25, colors.black),
                                        ]))
        elements.append(item_table)
        # ===========================Footer Data============================
        footer_data = []
        footer_data.append(['TOTAL:', '', '', '', '', intcomma(decimal_place % round_number(journal.total_amount))])

        footer_table = Table(footer_data, colWidths=[50, 170, 90, 75, 75, 75])
        footer_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ]))
        elements.append(footer_table)
        # ===========================Signature Data============================
        sign_data = []
        sign_data.append(['', '', '', ''])
        sign_data.append(['', '', '', ''])

        if journal.company.remit_remark:
            remit_remark = journal.company.remit_remark
        else:
            remit_remark = ''

        sign_data.append(['', '', '', company.name.upper()])
        sign_data.append(['', '', '', ''])

        if company.footer_logo:
            try:
                path_footer_logo = s.MEDIA_ROOT + str(company.footer_logo)
                sign_data.append([remit_remark, '', '', Image(path_footer_logo, 170, 50)])
            except Exception as e:
                sign_data.append(['', '', '', ''])
                sign_data.append(['', '', '', ''])
                sign_data.append(['', '', '', ''])
        else:
            sign_data.append([remit_remark, '', '', ''])

        sign_data.append(['', '', '', 'AUTHORISED SIGNATURE'])
        sign_table = Table(sign_data, colWidths=[180, 70, 30, 260])
        sign_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
             ('ALIGN', (-2, 3), (-2, -1), 'CENTER'),
             ('LINEABOVE', (3, -1), (3, -1), 0.25, colors.black),
             ('RIGHTPADDING', (0, 0), (-1, -1), 3),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('RIGHTPADDING', (-1, -1), (-1, -1), 20),
             ]))
        elements.append(sign_table)
        # ===========================End Coding============================
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, journal_id=journal_id, print_header=print_header, company_id=company.id),
                  onLaterPages=partial(self._header_footer, journal_id=journal_id, print_header=print_header, company_id=company.id),
                  canvasmaker=partial(NumberedPage, adjusted_height=-6, adjusted_width=-70, adjusted_caption=''))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
