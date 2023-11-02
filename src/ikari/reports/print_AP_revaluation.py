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
from accounting.models import Journal, RevaluationLogs, RevaluationDetails
from transactions.models import Transaction
from utilities.constants import TRANSACTION_TYPES
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.common import round_number


colWidths = [70, 5, 130, 5, 80, 5, 80, 5, 65, 5, 115, 5, 110, 5, 110]
MAX_LINE = 29


class Print_AP_revaluation:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, from_posting, to_posting):
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

        # # 2nd row
        row2_info1 = "A/P Revaluation Posting Journal (APRVPJ1Z)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_data.append('')
        # 3rd row
        row4_info1 = "From Posting Sequence "
        row4_info2 = "[" + from_posting + "]" + " To " + "[" + to_posting + "]"
        header_data.append([row4_info1, row4_info2])
        # 5st row

        row5_info1 = "Reprint Previously Printed Journal "
        row5_info2 = "[Yes]"

        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[280, 200, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
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

        # # 2nd row
        row2_info1 = "A/P Revaluation Posting Journal (APRVPJ1Z)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=[280, 100, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 10)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, from_posting, to_posting):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        table_header = ['Vendor No.', '', 'Document No.', '', 'Date', '', 'Source Amount', '', 'Prior Rate',
                        '', 'Prior Functionnal', '', 'Exchange Gain(Loss)', '', 'New Functional']

        table_data.append(table_header)
        table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

        item_header_table = Table(table_data, colWidths=colWidths)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
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
                ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
             ]))
        elements.append(item_header_table)

        posting_array = []
        from_p = int(from_posting)
        to_p = int(to_posting)
        while from_p <= to_p:
            posting_array.append(from_p)
            from_p += 1

        posting_number = RevaluationLogs.objects.filter(is_hidden=0, company_id=company_id, journal_type=dict(TRANSACTION_TYPES)['AP Invoice'],
                                                        posting_sequence__in=posting_array).exclude(posting_sequence='0'
                                                                                                    ).order_by('posting_sequence', 'currency__code')

        m_posting_seq = ''
        line_count = 0
        currency_array = []
        account_array = []
        decimal_place = "%.2f"
        company = Company.objects.get(pk=company_id)
        if company.currency.is_decimal:
            decimal_place_f = "%.2f"
        else:
            decimal_place_f = "%.0f"
        for posting in posting_number:
            curr_doc_total = curr_prior_total = curr_new_total = curr_gain_total = 0
            doc_total = prior_total = new_total = gain_total = 0
            if m_posting_seq != posting.posting_sequence:
                if line_count >= MAX_LINE - 4:
                    elements = go_next_page(elements)
                    line_count = 0
                table_data = []
                table_data.append(['Posting Sequence Number:', '', posting.posting_sequence, '', 'Posted On:',
                                   '', posting.revaluation_date.strftime('%d/%m/%Y'), '', ''])

                item_table = Table(table_data, colWidths=[160, 5, 60, 5, 80, 5, 80, 5, 395])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ]))
                elements.append(item_table)
                line_count += 1
                if line_count >= MAX_LINE:
                    elements = go_next_page(elements)
                    line_count = 0
                m_posting_seq = posting.posting_sequence

            if not posting.currency.is_decimal:
                decimal_place = "%.0f"
            else:
                decimal_place = "%.2f"
                
            if line_count >= MAX_LINE - 4:
                elements = go_next_page(elements)
                line_count = 0
            table_data = []
            table_data.append(['Revaluation Date:', '', posting.revaluation_date.strftime('%d/%m/%Y'), '', '', '', '', '', ''])

            table_data.append(['Revaluation Rate for:', '', posting.currency.code + '    ' + posting.rate_type, '', 'Rate Date',
                               '', posting.rate_date.strftime('%d/%m/%Y'), '', posting.exchange_rate])

            table_data.append(['', '', '', '', '', '', '', '', ''])

            item_table = Table(table_data, colWidths=[160, 5, 60, 5, 80, 5, 80, 5, 395])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('ALIGN', (5, 0), (-1, -1), 'LEFT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ]))
            elements.append(item_table)
            line_count += 3
            if line_count >= MAX_LINE:
                elements = go_next_page(elements)
                line_count = 0

            rv_journal_list = RevaluationDetails.objects.filter(posting_id=posting.id, is_hidden=0)
            m_cust = ''
            cust_count = 0
            for mItem in rv_journal_list:
                if m_cust == '':
                    # new cust
                    table_data = []
                    table_data.append([mItem.supplier.code if mItem.supplier else '', '', mItem.supplier.name if mItem.supplier else '', '', '', '', '', '', '', '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ]))
                    elements.append(item_table)
                    cust_count += 1
                    line_count += 1
                    if line_count >= MAX_LINE:
                        elements = go_next_page(elements)
                        line_count = 0
                    m_cust = mItem.supplier.code if mItem.supplier else ''
                if m_cust != '' and m_cust != mItem.supplier.code:
                    # prev vendor total
                    table_data = []
                    table_data.append(['', '', 'Document Total:', '', '', '', intcomma(decimal_place % round_number(doc_total)), '', '', '',
                                       intcomma(decimal_place_f % round_number(prior_total)), '', intcomma(decimal_place_f % round_number(gain_total)),
                                       '', intcomma(decimal_place_f % round_number(new_total))])

                    table_data.append(['', '', 'Vendor Total: (' + m_cust + ')', '', '', '', intcomma(decimal_place % round_number(doc_total)), '',
                                       posting.currency.code, '', intcomma(decimal_place_f % round_number(prior_total)), '',
                                       intcomma(decimal_place_f % round_number(gain_total)), '', intcomma(decimal_place_f % round_number(new_total))])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                         ('ALIGN', (8, 1), (8, 1), 'LEFT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
                         ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                         ('LINEABOVE', (12, 0), (12, 0), 0.25, colors.black),
                         ('LINEABOVE', (14, 0), (14, 0), 0.25, colors.black),
                         ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                         ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
                         ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                         ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
                         ]))
                    elements.append(item_table)
                    line_count += 2
                    if line_count >= MAX_LINE:
                        elements = go_next_page(elements)
                        line_count = 0
                    # new cust
                    table_data = []
                    table_data.append([mItem.supplier.code if mItem.supplier else '', '', mItem.supplier.name if mItem.supplier else '', '', '', '', '', '', '', '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ]))
                    elements.append(item_table)
                    cust_count += 1
                    line_count += 1
                    if line_count >= MAX_LINE:
                        elements = go_next_page(elements)
                        line_count = 0
                    m_cust = mItem.supplier.code if mItem.supplier else ''
                    doc_total = prior_total = new_total = gain_total = 0

                source_amount = mItem.source_amount
                prior_functional = mItem.prior_functional
                # new_functional = round_number(source_amount * posting.exchange_rate)
                new_functional = mItem.new_functional
                gain = mItem.gain_loss

                doc_total += source_amount
                prior_total += prior_functional
                new_total += new_functional
                gain_total += gain

                curr_doc_total += source_amount
                curr_prior_total += prior_functional
                curr_new_total += new_functional
                curr_gain_total += gain

                table_data = []
                table_data.append(['', '', mItem.document_no, '', posting.revaluation_date.strftime('%d/%m/%Y'),
                                   '', intcomma(decimal_place % round_number(source_amount)), '', mItem.prior_rate,
                                   '', intcomma(decimal_place_f % round_number(prior_functional)),
                                   '', intcomma(decimal_place_f % round_number(gain)),
                                   '', intcomma(decimal_place_f % round_number(new_functional))])

                item_table = Table(table_data, colWidths=colWidths)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, 0), 0),
                     ]))
                elements.append(item_table)
                line_count += 1
                if line_count >= MAX_LINE:
                    elements = go_next_page(elements)
                    line_count = 0

                # create account entry
                name = 'RV-' + posting.posting_sequence
                gl_journal = Journal.objects.filter(journal_type=dict(TRANSACTION_TYPES)['GL'],
                                                    is_hidden=0, company_id=company_id,
                                                    posting_date=posting.revaluation_date,
                                                    source_type='AP-GL', name=name,
                                                    reference=mItem.document_no).last()
                if gl_journal:
                    gl_trx = Transaction.objects.filter(journal_id=gl_journal.id)
                    for trx in gl_trx:
                        account_array.append({
                            'code': trx.account.code,
                            'desc': trx.account.name,
                            'curr': posting.currency.code,
                            'debits': trx.functional_amount if trx.is_debit_account else 0,
                            'credits': trx.functional_amount if trx.is_credit_account else 0,
                        })

            # Print last line
            table_data = []
            # if doc_total != 0 or gain_total != 0 or prior_total != 0:
            table_data.append(['', '', 'Document Total:', '', '', '', intcomma(decimal_place % round_number(doc_total)), '', '', '',
                                intcomma(decimal_place_f % round_number(prior_total)),  '', intcomma(decimal_place_f % round_number(gain_total)),
                                '', intcomma(decimal_place_f % round_number(new_total))])

            table_data.append(['', '', 'Vendor Total: (' + m_cust + ')', '', '', '', intcomma(decimal_place % round_number(doc_total)), '',
                                posting.currency.code, '', intcomma(decimal_place_f % round_number(prior_total)), '',
                                intcomma(decimal_place_f % round_number(gain_total)), '', intcomma(decimal_place_f % round_number(new_total))])

            table_data.append(['', '', posting.currency.code + '   ' + posting.currency.name, '', '', '',
                                intcomma(decimal_place % round_number(curr_doc_total)), '', '', '',
                                intcomma(decimal_place_f % round_number(curr_prior_total)), '',
                                intcomma(decimal_place_f % round_number(curr_gain_total)), '', intcomma(decimal_place_f % round_number(curr_new_total))])

            item_table = Table(table_data, colWidths=colWidths)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (8, 1), (8, 1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
                    ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
                    ('LINEABOVE', (12, 0), (12, 0), 0.25, colors.black),
                    ('LINEABOVE', (14, 0), (14, 0), 0.25, colors.black),
                    ('LINEABOVE', (6, 1), (6, 1), 0.25, colors.black),
                    ('LINEABOVE', (10, 1), (10, 1), 0.25, colors.black),
                    ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
                    ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
                    ('LINEABOVE', (6, 2), (6, 2), 0.25, colors.black),
                    ('LINEABOVE', (10, 2), (10, 2), 0.25, colors.black),
                    ('LINEABOVE', (12, 2), (12, 2), 0.25, colors.black),
                    ('LINEABOVE', (14, 2), (14, 2), 0.25, colors.black),
                    ]))
            elements.append(item_table)
            line_count += 3
            if line_count >= MAX_LINE:
                elements = go_next_page(elements)
                line_count = 0
            found = False
            for m_currency in currency_array:
                if m_currency['curr_code'] == posting.currency.code:
                    found = True
                    m_currency['curr_doc_total'] += curr_doc_total
                    m_currency['curr_prior_total'] += curr_prior_total
                    m_currency['curr_gain_total'] += curr_gain_total
                    m_currency['curr_new_total'] += curr_new_total
            if not found:
                currency_array.append({
                    'is_decimal': posting.currency.is_decimal,
                    'curr_code': posting.currency.code,
                    'curr_name': posting.currency.name,
                    'curr_doc_total': curr_doc_total,
                    'curr_prior_total': curr_prior_total,
                    'curr_gain_total': curr_gain_total,
                    'curr_new_total': curr_new_total
                })

            table_data = []
            table_data.append([str(cust_count) + ' vendors printed', '', '', '', '', '', ''])
            table_data.append(['', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[150, 145, 120, 125, 120, 15, 120])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_ITALIC),
                 ]))
            elements.append(item_table)
            line_count += 2
            if line_count > MAX_LINE:
                elements = go_next_page(elements)
                line_count = 0

        # Currency total
        elements.append(PageBreak())
        table_data = []
        table_data.append(['', '', '', '', '---  Currency Summary ---', '', '', '', '', '', ''])
        table_data.append(['', '', '', '', '', '', '', '', '', '', ''])
        table_data.append(['Currency', '', 'Currency Name', '', 'Source Amount', '', 'Prior Functional', '', 'Exchange Gain (Loss)', '', 'New Functional'])

        item_table = Table(table_data, colWidths=[70, 5, 210, 5, 120, 5, 120, 5, 120, 5, 120])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (4, 2), (-1, -1), 'RIGHT'),
             ('ALIGN', (0, 2), (2, 2), 'LEFT'),
             ('SPAN', (4, 0), (6, 0)),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (0, 2), (0, 2), 0.25, colors.black),
             ('LINEBELOW', (2, 2), (2, 2), 0.25, colors.black),
             ('LINEBELOW', (4, 2), (4, 2), 0.25, colors.black),
             ('LINEBELOW', (6, 2), (6, 2), 0.25, colors.black),
             ('LINEBELOW', (8, 2), (8, 2), 0.25, colors.black),
             ('LINEBELOW', (10, 2), (10, 2), 0.25, colors.black),
             ]))
        elements.append(item_table)
        prior_total = gain_total = new_total = 0     
        currency_array.sort(key=lambda r: (r['curr_code']))
        for m_currency in currency_array:
            if not m_currency['is_decimal']:
                decimal_place = "%.0f"
            else:
                decimal_place = "%.2f"
            table_data = []
            table_data.append([m_currency['curr_code'], '', m_currency['curr_name'], '',
                               intcomma(decimal_place % round_number(m_currency['curr_doc_total'])), '',
                               intcomma(decimal_place_f % round_number(m_currency['curr_prior_total'])),
                               '', intcomma(decimal_place_f % round_number(m_currency['curr_gain_total'])), '',
                               intcomma(decimal_place_f % round_number(m_currency['curr_new_total']))])

            item_table = Table(table_data, colWidths=[70, 5, 210, 5, 120, 5, 120, 5, 120, 5, 120])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (0, 0), (2, 0), 'LEFT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ]))
            elements.append(item_table)
            prior_total += m_currency['curr_prior_total']
            gain_total += m_currency['curr_gain_total']
            new_total += m_currency['curr_new_total']

        table_data = []
        table_data.append(['', '', '', '', 'Total:',
                           '', intcomma(decimal_place_f % round_number(prior_total)),
                           '', intcomma(decimal_place_f % round_number(gain_total)),
                           '', intcomma(decimal_place_f % round_number(new_total))])

        item_table = Table(table_data, colWidths=[70, 5, 210, 5, 120, 5, 120, 5, 120, 5, 120])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
             ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
             ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
             ('LINEBELOW', (6, 0), (6, 0), 0.25, colors.black),
             ('LINEBELOW', (8, 0), (8, 0), 0.25, colors.black),
             ('LINEBELOW', (10, 0), (10, 0), 0.25, colors.black),
             ]))
        elements.append(item_table)

        # Account total
        elements.append(PageBreak())
        table_data = []
        table_data.append(['', '', '---  General Ledger Summary  ---', '', '', '', '', '', ''])
        table_data.append(['', '', '', '', '', '', '---------------------  Functional -----------------------', '', '', ])
        table_data.append(['G/L Account', '', 'Account Description', '', 'Currency', '', 'Debits', '', 'Credits'])

        item_table = Table(table_data, colWidths=[195, 5, 210, 5, 120, 5, 120, 5, 120])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (4, 2), (-1, -1), 'RIGHT'),
             ('ALIGN', (0, 2), (2, 2), 'LEFT'),
             ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
             ('SPAN', (2, 0), (4, 0)),
             ('SPAN', (6, 1), (8, 1)),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (2, 0), (4, 0), 50),
             ('LINEBELOW', (0, 2), (0, 2), 0.25, colors.black),
             ('LINEBELOW', (2, 2), (2, 2), 0.25, colors.black),
             ('LINEBELOW', (4, 2), (4, 2), 0.25, colors.black),
             ('LINEBELOW', (6, 2), (6, 2), 0.25, colors.black),
             ('LINEBELOW', (8, 2), (8, 2), 0.25, colors.black),
             ]))
        elements.append(item_table)

        debit_total = credit_total = 0
        m_code = m_desc = m_curr = ''
        m_debit = m_credit = 0
        account_array.sort(key=lambda r: (r['code'], r['curr']))
        for m_acc in account_array:
            if m_code == '':
                m_code = m_acc['code']
            if m_desc == '':
                m_desc = m_acc['desc']
            if m_curr == '':
                m_curr = m_acc['curr']
            if m_code != m_acc['code'] or m_curr != m_acc['curr']:
                table_data = []
                table_data.append([m_code, '', m_desc, '', m_curr, '', intcomma(decimal_place_f % round_number(m_debit)) if m_debit else '',
                                   '', intcomma(decimal_place_f % round_number(m_credit)) if m_credit else ''])

                item_table = Table(table_data, colWidths=[195, 5, 210, 5, 120, 5, 120, 5, 120])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('ALIGN', (0, 0), (2, 0), 'LEFT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ]))
                elements.append(item_table)
                m_code = m_acc['code']
                m_curr = m_acc['curr']
                m_debit = m_acc['debits']
                m_credit = m_acc['credits']
                m_desc = m_acc['desc']
            else:
                m_desc = m_acc['desc']
                m_curr = m_acc['curr']
                m_debit += m_acc['debits']
                m_credit += m_acc['credits']

            debit_total += m_acc['debits']
            credit_total += m_acc['credits']
        table_data = []
        table_data.append([m_code, '', m_desc, '', m_curr, '', intcomma(decimal_place_f % round_number(m_debit)) if m_debit else '',
                           '', intcomma(decimal_place_f % round_number(m_credit)) if m_credit else ''])

        item_table = Table(table_data, colWidths=[195, 5, 210, 5, 120, 5, 120, 5, 120])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (0, 0), (2, 0), 'LEFT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        elements.append(item_table)

        # Total
        table_data = []
        table_data.append(['', '', '', '', 'Total:', '', intcomma(decimal_place_f % round_number(debit_total)),
                           '', intcomma(decimal_place_f % round_number(credit_total))])

        item_table = Table(table_data, colWidths=[195, 5, 210, 5, 120, 5, 120, 5, 120])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('LINEABOVE', (6, 0), (6, 0), 0.25, colors.black),
             ('LINEABOVE', (8, 0), (8, 0), 0.25, colors.black),
             ('LINEABOVE', (10, 0), (10, 0), 0.25, colors.black),
             ('LINEBELOW', (6, 0), (6, 0), 0.25, colors.black),
             ('LINEBELOW', (8, 0), (8, 0), 0.25, colors.black),
             ]))
        elements.append(item_table)

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
                  onFirstPage=partial(self._header_footer, company_id=company_id, from_posting=str(from_posting), to_posting=str(to_posting)),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


def go_next_page(elements):
    elements.append(PageBreak())
    table_data = []
    table_header = ['Vendor No.', '', 'Document No.', '', 'Date', '', 'Source Amount', '', 'Prior Rate',
                    '', 'Prior Functionnal', '', 'Exchange Gain(Loss)', '', 'New Functional']

    table_data.append(table_header)
    table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

    item_header_table = Table(table_data, colWidths=colWidths)
    item_header_table.setStyle(TableStyle(
        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
            ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
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
            ('LINEABOVE', (12, 1), (12, 1), 0.25, colors.black),
            ('LINEABOVE', (14, 1), (14, 1), 0.25, colors.black),
         ]))
    elements.append(item_header_table)

    return elements
