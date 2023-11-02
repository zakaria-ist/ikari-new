from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from accounting.models import Batch, Journal
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import round_number


colWidths = [75, 5, 75, 5, 190, 5, 190, 5, 120, 5, 120]
MAX_LINE = 20


class Print_GL_revaluation:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, from_posting, to_posting, from_batch_date, to_batch_date):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])
        row2_info1 = "G/L Batch Listing - In Functional Currency (GLBCHL01)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        row5_info1 = "From Creation Date "
        row5_info2 = "[" + from_batch_date + "]" + " To " + "[" + to_batch_date + "]"
        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[180, 330, 300])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (1, 0), (1, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _header_last_footer(canvas, doc, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])
        row2_info1 = "G/L Batch Listing - In Functional Currency (GLBCHL01)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_table = Table(header_data, colWidths=[280, 330, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONT', (1, 0), (1, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, from_posting, to_posting):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22,
                                topMargin=80, bottomMargin=32, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT))

        # Our container for 'Flowable' objects
        elements = []
        header_data = []
        row4_info1 = "From Batch Number "
        row4_info2 = "[" + from_posting + "]" + " To " + "[" + to_posting + "]"
        header_data.append([row4_info1, row4_info2])
        row4_info3 = "From Source Ledger "
        row4_info4 = "[GL] To [GL]"
        header_data.append([row4_info3, row4_info4])

        row5_info3 = "Include Printed Batches"
        row5_info4 = "Yes"
        header_data.append([row5_info3, row5_info4])

        row6_info1 = "Status"
        row6_info2 = "[Open, Posted, Readt to Post]"
        header_data.append([row6_info1, row6_info2])
        row6_info3 = "Type"
        row6_info4 = "[Entered, Subledger, Imported, Generated, Recurring]"
        header_data.append([row6_info3, row6_info4])

        row7_info1 = "Include Trans. Optional Field"
        row7_info2 = "[No]"
        header_data.append([row7_info1, row7_info2])
        row7_info3 = "Include Ref. & Desc."
        row7_info4 = "[Yes]"
        header_data.append([row7_info3, row7_info4])

        row8_info1 = "Include Comments"
        row8_info2 = "[Yes]"
        header_data.append([row8_info1, row8_info2])
        row8_info3 = "Date"
        row8_info4 = "[Doc. Date]"
        header_data.append([row8_info3, row8_info4])
        header_data.append(['', ''])

        header_table = Table(header_data, colWidths=[180, 630])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ]))
        elements.append(header_table)

        table_data = []
        table_header = ['Source', '', 'Doc. date', '', 'Account Number', '', 'Account Description', '', 'Debits',
                        '', 'Credits']
        table_data.append(table_header)
        table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

        item_header_table = Table(table_data, colWidths=colWidths)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('LINEABOVE', (0, 1), (0, 1), 0.25, colors.black),
                ('LINEABOVE', (2, 1), (2, 1), 0.25, colors.black),
                ('LINEABOVE', (4, 1), (4, 1), 0.25, colors.black),
                ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                ('LINEABOVE', (8, 1), (8, 1), 0.25, colors.black),
                ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
             ]))
        elements.append(item_header_table)

        posting_array = []
        from_p = int(from_posting)
        to_p = int(to_posting)
        while from_p <= to_p:
            posting_array.append(str(from_p))
            from_p += 1

        from_batch = Batch.objects.filter(company_id=company_id, batch_no__contains=from_posting).last()
        posting_batches = Batch.objects.filter(is_hidden=0, company_id=company_id,
                                               batch_type=dict(TRANSACTION_TYPES)['GL'],
                                               status=STATUS_TYPE_DICT['Posted'],
                                               description__startswith="GL REVALUATION",
                                               id__gte=from_batch.id) \
            .order_by('id')

        m_batch_no = ''
        from_batch_date = to_batch_date = ''
        line_count = 0
        batch_count = 0

        company = Company.objects.get(pk=company_id)
        if company.currency.is_decimal:
            decimal_place = "%.2f"
        else:
            decimal_place = "%.0f"
        for posting in posting_batches:
            batch_credit_total = batch_debit_total = 0

            batch_count += 1
            if batch_count == 1:
                from_batch_date = posting.batch_date.strftime('%d/%m/%Y')
            to_batch_date = posting.batch_date.strftime('%d/%m/%Y')

            if m_batch_no != posting.batch_no:
                table_data = []
                table_data.append(['Batch Number:', '', posting.batch_no, '', posting.description, '', '', '', '', '', ''])
                table_data.append(['Creation Date:', '', posting.batch_date.strftime('%d/%m/%Y'), '', 'Status:', '', 'Posted', '', 'Type:', '', 'Generated'])
                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=[80, 5, 80, 5, 80, 5, 80, 5, 80, 5, 370])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('SPAN', (4, 0), (10, 0)),
                     ]))
                elements.append(item_table)
                line_count += 3
                if line_count > MAX_LINE:
                    elements = go_next_page(elements)
                    line_count = 0
                m_batch_no = posting.batch_no

            gl_journal_list = Journal.objects.filter(journal_type=dict(TRANSACTION_TYPES)['GL'], is_hidden=0, company_id=company_id,
                                                     status=STATUS_TYPE_DICT['Posted'], source_type='GL-RV', batch__batch_no=posting.batch_no)
            entry_count = 0
            for journal in gl_journal_list:
                entry_count += 1
                entry_debit_total = entry_credit_total = 0
                table_data = []
                table_data.append(['Entry Number:', '', journal.code, '', journal.name, '', '', '', '', '', ''])
                table_data.append(['Post Date:', '', journal.posting_date.strftime('%d/%m/%Y'), '', 'Year-Prd:',
                                   '', journal.posting_date.strftime('%m-%Y'), '', 'Auto Reverse:', '', 'Next Period'])
                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=[80, 5, 80, 5, 80, 5, 80, 5, 80, 5, 370])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('SPAN', (4, 0), (10, 0)),
                     ]))
                elements.append(item_table)
                line_count += 3
                if line_count > MAX_LINE:
                    elements = go_next_page(elements)
                    line_count = 0

                gl_trx = Transaction.objects.filter(is_hidden=0, company_id=company_id,
                                                    journal_id=journal.id)
                for trx in gl_trx:
                    entry_debit_total += trx.functional_amount if trx.is_debit_account else 0
                    entry_credit_total += trx.functional_amount if trx.is_credit_account else 0
                    batch_debit_total += trx.functional_amount if trx.is_debit_account else 0
                    batch_credit_total += trx.functional_amount if trx.is_credit_account else 0
                    table_data = []
                    table_data.append([trx.source_type, '', trx.transaction_date.strftime('%d/%m/%Y'), '', trx.account.code, '', trx.account.name,
                                       '', intcomma(decimal_place % round_number(trx.functional_amount)) if trx.is_debit_account else '',
                                       '', intcomma(decimal_place % round_number(trx.functional_amount)) if trx.is_credit_account else ''
                                       ])
                    ref = 'Ref.: ' + trx.reference if trx.reference else 'Ref.: '
                    desc = 'Desc.: ' + trx.description if trx.description else 'Desc.: '
                    table_data.append(['', '', '', '', ref, '', desc, '', '', '', ''])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ]))
                    elements.append(item_table)
                    line_count += 2
                    if line_count > MAX_LINE:
                        elements = go_next_page(elements)
                        line_count = 0

                table_data = []
                table_data.append(['', '', '', '', '', '', 'Entry Total:', '', intcomma(decimal_place % round_number(entry_debit_total)),
                                   '', intcomma(decimal_place % round_number(entry_credit_total))])
                table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

                item_table = Table(table_data, colWidths=colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
                     ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                     ('LINEBELOW', (8, 0), (8, 0), 0.25, colors.black),
                     ('LINEBELOW', (10, 0), (10, 0), 0.25, colors.black),
                     ]))
                elements.append(item_table)
                line_count += 2
                if line_count > MAX_LINE:
                    elements = go_next_page(elements)
                    line_count = 0

            table_data = []
            table_data.append(['', '', '', '', '', '', 'Batch Total:', '', intcomma(decimal_place % round_number(batch_debit_total)),
                               '', intcomma(decimal_place % round_number(batch_credit_total))])

            item_table = Table(table_data, colWidths=colWidths)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
                 ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                 ('LINEBELOW', (8, 0), (8, 0), 0.25, colors.black),
                 ('LINEBELOW', (10, 0), (10, 0), 0.25, colors.black),
                 ]))
            elements.append(item_table)
            line_count += 1
            if line_count > MAX_LINE:
                elements = go_next_page(elements)
                line_count = 0
            # Print last line
            table_data = []
            table_data.append([str(entry_count) + ' Entries printed', '', '', '', '', '', ''])
            table_data.append(['', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[150, 145, 120, 125, 120, 15, 120])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_ITALIC),
                 ]))
            elements.append(item_table)
            line_count += 2
            if line_count > MAX_LINE:
                elements = go_next_page(elements)
                line_count = 0

        table_data = []
        table_data.append([str(batch_count) + ' Batches printed', '', '', '', '', '', ''])
        table_data.append(['', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=[150, 145, 120, 125, 120, 15, 120])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_ITALIC),
             ]))
        elements.append(item_table)
        line_count += 1
        if line_count > MAX_LINE:
            elements = go_next_page(elements)
            line_count = 0

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[100, 130, 110, 105, 75, 60, 85, 10, 130])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, from_posting=str(from_posting), to_posting=str(to_posting),
                                      from_batch_date=str(from_batch_date), to_batch_date=str(to_batch_date)),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


def go_next_page(elements):
    elements.append(PageBreak())
    table_data = []
    table_header = ['Source', '', 'Doc. date', '', 'Account Number', '', 'Account Description', '', 'Debits', '', 'Credits']
    table_data.append(table_header)
    table_data.append(['', '', '', '', '', '', '', '', '', '', ''])

    item_header_table = Table(table_data, colWidths=colWidths)
    item_header_table.setStyle(TableStyle(
        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
            ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (0, 1), 0.25, colors.black),
            ('LINEABOVE', (2, 1), (2, 1), 0.25, colors.black),
            ('LINEABOVE', (4, 1), (4, 1), 0.25, colors.black),
            ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
            ('LINEABOVE', (8, 1), (8, 1), 0.25, colors.black),
            ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
         ]))
    elements.append(item_header_table)

    return elements
