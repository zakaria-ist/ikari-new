from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from accounts.models import Account, AccountHistory
from companies.models import Company
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, BALANCE_TYPE_DICT
from utilities.common import round_number
from reports.print_GLSource import transaction_detail, get_posting_sequence, get_broken_string
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from django.db.models import Q

HEADER_COLUMN = [280, 333, 188]
COMMON_COLUMN = [35, 5, 35, 5, 55, 5, 250, 5, 30, 5, 50, 5, 70, 5, 70, 5, 70, 5, 73, 5]


class Print_GLFunctionBalanceBatch:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
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
        row1_info1 = "Date: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # # 2nd row
        row2_info1 = "G/L Transactions Listing - In Functional Currency (GLPTLS1)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_data.append('')
        # # 3rd row
        row3_info1 = "Include Accounts With No Activity "
        row3_info2 = "[No]"
        header_data.append([row3_info1, row3_info2])
        # # 6st row
        row5_info1 = "Include Balances and Net Changes "
        row5_info2 = "[Yes]"
        header_data.append([row5_info1, row5_info2])

        # # 6st row
        row6_info1 = "Include Posting Seq. and Batch-Entry "
        row6_info2 = "[Yes]"
        header_data.append([row6_info1, row6_info2])

        # # 6st row
        row7_info1 = "Include Trans. Optional Fields"
        row7_info2 = "[No]"
        header_data.append([row7_info1, row7_info2])

        header_table = Table(header_data, colWidths=HEADER_COLUMN)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h + 8)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _header_last_footer(canvas, doc, company_id, issue_from, issue_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "Date: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # # 2nd row
        row2_info1 = "G/L Transactions Listing - In Functional Currency (GLPTLS1)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])

        header_table = Table(header_data, colWidths=HEADER_COLUMN)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 2, doc.height + doc.topMargin - h - 16)

        table_data = []
        # # 1ST ROW
        table_data.append([])
        table_data.append(['Account Number/', '', '', '', '', '', 'Description/', '', 'Posting'])
        table_data.append(['Prd.', '', 'Source', '', 'Doc.Date', '', 'Reference', '', 'Seq.', '',
                           'Batch-Entry', '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance', '', ''])

        item_header_table = Table(table_data, colWidths=COMMON_COLUMN)

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
             ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
             ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
             ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
             ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
             ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
             ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
             ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
             ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
             ('LINEBELOW', (18, -1), (18, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin + 2.5, doc.height + doc.topMargin - h - h1 - 16)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list, sp_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))

        company = Company.objects.get(pk=company_id)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        posting_sequence = get_posting_sequence(company.id)

        acc_list = eval(acc_list)
        if len(acc_list):
            account_list = Account.objects.filter(id__in=acc_list).order_by('code')
            acc_str = "[" + account_list[0].code + "] To [" + account_list[len(account_list)-1].code + "]"
        else:
            account_list = Account.objects.filter(is_hidden=False, company_id=company_id).order_by('code')
            acc_str = '[] To [ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ]'
            
        # Draw Content of PDF
        # design interface header
        issue_from = datetime.strptime(issue_from, '%Y-%m-%d')
        issue_to = datetime.strptime(issue_to, '%Y-%m-%d')
        last_year = issue_from - relativedelta(years=1)
        table_data.append(
            ['From Year - Period', "[" + str(issue_from.year) + '-' + str(issue_from.month) + "]"
             + " To [" + str(issue_to.year) + '-' + str(issue_to.month) + "]", ''])
        table_data.append(['Sort By', '[Account No.]', ''])
        table_data.append(['Sort Transactions By Date', '[No] ', ''])
        table_data.append(['From Account No.', acc_str, ''])
        table_data.append(['From Account Group', '[] To [ZZZZZZZZZZZZ]', ''])
        table_data.append(['Last Year Closed',  str(last_year.year), ''])
        table_data.append(['Last Posting Sequence', posting_sequence if posting_sequence else '-', ''])
        table_data.append(['Use Rolled Up Amounts ', '[No]', ''])
        table_data.append(['Date ', 'Doc. Date', ''])

        item_table = Table(table_data, colWidths=[280, 333, 186])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        elements.append(item_table)

        table_data = []
        table_data.append([])
        table_data.append(['Account Number/', '', '', '', '', '', 'Description/', '', 'Posting'])
        table_data.append(['Prd.', '', 'Source', '', 'Doc.Date', '', 'Reference', '', 'Seq.', '',
                           'Batch-Entry', '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance', '', ''])

        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
             ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
             ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
             ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
             ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
             ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
             ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
             ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
             ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
             ('LINEBELOW', (18, -1), (18, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        table_data = []
        account_counter = 0
        # end design interface header

        # get transaction
        if sp_period == 'CLS':
            transaction_item_list = Transaction.objects.select_related('journal__batch').select_related('journal').select_related('account').filter(
                company_id=company_id, is_hidden=0, journal_id__gt=0, journal__is_hidden=0,
                journal__perd_year__range=[issue_from.year, issue_to.year],
                journal__journal_type=dict(TRANSACTION_TYPES)['GL']
            ).exclude(journal__batch__posting_sequence='0') \
                .exclude(journal__batch__status__in=(int(STATUS_TYPE_DICT['Deleted']),
                                                    int(STATUS_TYPE_DICT['Open']),
                                                    int(STATUS_TYPE_DICT['ERROR']),
                                                    int(STATUS_TYPE_DICT['Prov. Posted']))
                        ).order_by('account__code', 'journal__document_date').distinct()
        else:
            transaction_item_list = Transaction.objects.select_related('journal__batch').select_related('journal').select_related('account').filter(
                company_id=company_id, is_hidden=0, journal_id__gt=0, journal__is_hidden=0,
                journal__perd_year__range=[issue_from.year, issue_to.year],
                journal__journal_type=dict(TRANSACTION_TYPES)['GL']
            ).exclude(source_type='GL-CL') \
                .exclude(reference='CLOSING ENTRY') \
                .exclude(description='CLOSING ENTRY') \
                .exclude(journal__batch__posting_sequence='0') \
                .exclude(journal__batch__status__in=(int(STATUS_TYPE_DICT['Deleted']),
                                                    int(STATUS_TYPE_DICT['Open']),
                                                    int(STATUS_TYPE_DICT['ERROR']),
                                                    int(STATUS_TYPE_DICT['Prov. Posted']))
                        ).order_by('account__code', 'journal__document_date').distinct()

        diff = relativedelta(issue_to, issue_from)
        number_of_month = (diff.years * 12) + diff.months

        if status_type != '0':
            transaction_item_list = transaction_item_list.filter(journal__batch__status=status_type)

        g_debit = g_credit = g_net = grandtotal = 0

        table_data = []
        
        account_item_list = account_list.exclude(deactivate_period__lte=issue_from).order_by('code').distinct()
        account_item_list = account_item_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        transaction_item_list = transaction_item_list.filter(account__in=account_item_list)

        open_year = issue_from.year if issue_from else 0
        open_month = issue_from.month if issue_from else 0
        # calculate_account_history(company_id, open_year, open_month)
        decimal_place = "%.2f"
        if not company.currency.is_decimal:
            decimal_place = "%.0f"
        if account_item_list:
            for i, mAccount in enumerate(account_item_list):
                if sp_period == 'CLS':
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id=company.currency_id,
                                                                                                period_month='CLS', period_year=open_year,
                                                                                                functional_currency_id=company.currency_id)\
                        .exclude(source_currency_id__isnull=True).first()
                else:
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id=company.currency_id,
                                                                                                period_month=open_month, period_year=open_year,
                                                                                                functional_currency_id=company.currency_id)\
                        .exclude(source_currency_id__isnull=True).first()
                table_data = []
                total_balance = 0
                print_account_checker = True
                if open_account_history:
                    total_balance = open_account_history.functional_begin_balance

                sum_amount_debit_acc = sum_amount_credit_acc = 0
                total_balance_acc = total_balance
                curr_year = ''
                for month in range(-1, number_of_month):
                    current_date = issue_from + relativedelta(months=month + 1)
                    curr_year = current_date.year
                    if sp_period == 'ADJ':
                        current_month = 14
                    elif sp_period == 'CLS':
                        current_month = 15
                    else:
                        current_month = current_date.month

                    transaction_item_list_account = transaction_item_list.filter(account_id=mAccount.id,
                                                                                 journal__perd_year=curr_year,
                                                                                 journal__perd_month=current_month) 
                        # .order_by('source_type', 'journal__batch__posting_sequence', 'journal__code')

                    error_batch_nos = transaction_item_list_account.filter(journal__batch__description__icontains='error')\
                        .values_list('journal__batch__batch_no', flat=True)\
                        .order_by('journal__batch__batch_no').distinct()
                    error_batch_desc = transaction_item_list_account.filter(journal__batch__description__icontains='error')\
                        .values_list('journal__batch__description', flat=True)\
                        .order_by('journal__batch__description').distinct()

                    for batch_no in error_batch_nos:
                        if len([i for i in error_batch_desc if batch_no in i]):
                            transaction_item_list_account = transaction_item_list_account.exclude(journal__batch__batch_no=batch_no)

                    transaction_item_list_account = sorted(
                        transaction_item_list_account, key=lambda Transaction: (
                            Transaction.source_type,
                            Transaction.journal.batch.posting_sequence,
                            int(Transaction.journal.code)))
                    if (len(transaction_item_list_account) or total_balance) and print_account_checker:
                        print_account_checker = False
                        account_counter += 1
                        table_data.append([Paragraph(str(mAccount.code), styles['LeftAlign']),
                                           '', '', '', '', '', Paragraph(str(mAccount.name), styles['LeftAlign']),
                                           '', '', '', '', '', '', '', '',   '', '', '', intcomma(decimal_place % round_number(total_balance)), '', ''])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN)

                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('ALIGN', (13, 0), (-1, -1), 'RIGHT'),
                             ('TOPPADDING', (0, 0), (-1, -1), 0),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('SPAN', (0, 0), (3, 0))
                             ]))
                        elements.append(item_table)
                    sum_amount_credit = sum_amount_debit = 0
                    trx_printed = False
                    if transaction_item_list_account:
                        for j, mItem in enumerate(transaction_item_list_account):
                            if j == 0:

                                table_data = []
                                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                     ]))
                                elements.append(item_table)

                            if mItem.journal:
                                if mItem.journal.batch:
                                    batch_no = str(int(mItem.journal.batch.batch_no)) + '-' + str(int(mItem.journal.code))
                                    posting_sequence = mItem.journal.batch.posting_sequence
                                else:
                                    batch_no = ''
                                    posting_sequence = ''
                            else:
                                batch_no = ''
                                posting_sequence = ''

                            table_data = []
                            transaction_detail_list = transaction_detail(mItem, 51)
                            table_data.append([
                                current_month, '', mItem.source_type, '', mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal else ' / / ', '',
                                transaction_detail_list[1], '', posting_sequence, '', batch_no, '',
                                intcomma(decimal_place % round_number(mItem.functional_amount)
                                         if mItem.functional_balance_type == BALANCE_TYPE_DICT['Debit'] else ''), '',
                                intcomma(decimal_place % round_number(mItem.functional_amount) if mItem.functional_balance_type ==
                                         BALANCE_TYPE_DICT['Credit'] else ''), '', '', '', '', '', ''])
                            try:
                                desc_list = get_broken_string(transaction_detail_list[2], 51)
                                for desc_str in desc_list:
                                    table_data.append(
                                        ['', '', '', '', '', '', desc_str, '', '', '', '', '', '', '', '', '', '', '', '', ''])
                            except:
                                pass
                            if len(transaction_detail_list[0]):
                                table_data.append(['', '', '', '', '', '', transaction_detail_list[0], '', '', '', '', '', '', '', '', '', '', '', '', ''])
                            if mItem.functional_balance_type == BALANCE_TYPE_DICT['Credit']:
                                sum_amount_credit += round_number(mItem.functional_amount)
                            else:
                                sum_amount_debit += round_number(mItem.functional_amount)

                            item_table = Table(table_data, colWidths=COMMON_COLUMN)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                 ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                 ('ALIGN', (8, 0), (10, 0), 'CENTER'),
                                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ]))
                            elements.append(item_table)
                            trx_printed = True
                        if (trx_printed and j == transaction_item_list_account.__len__() - 1):
                            table_data = []
                            total_balance += (sum_amount_debit - sum_amount_credit)
                            table_data.append([
                                '', '', '', '', '', '', 'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ', '',
                                '', '', '', '', '', '', '', '', intcomma(decimal_place % round_number(sum_amount_debit - sum_amount_credit)), '',
                                intcomma(decimal_place % round_number(total_balance)), '',  ''])
                            item_table = Table(table_data, colWidths=COMMON_COLUMN)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                                 ('SPAN', (6, 0), (9, 0)),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                 ]))
                            elements.append(item_table)
                            if company.currency.is_decimal:
                                sum_amount_credit_acc += round_number(sum_amount_credit, 2)
                                sum_amount_debit_acc += round_number(sum_amount_debit, 2)
                                total_balance_acc += round_number(sum_amount_debit, 2) - round_number(sum_amount_credit, 2)
                                g_credit += round_number(sum_amount_credit, 2)
                                g_debit += round_number(sum_amount_debit, 2)
                                g_net += round_number(sum_amount_debit, 2) - round_number(sum_amount_credit, 2)
                            else:
                                sum_amount_credit_acc += round_number(sum_amount_credit, 0)
                                sum_amount_debit_acc += round_number(sum_amount_debit, 0)
                                total_balance_acc += round_number(sum_amount_debit, 0) - round_number(sum_amount_credit, 0)
                                g_credit += round_number(sum_amount_credit, 0)
                                g_debit += round_number(sum_amount_debit, 0)
                                g_net += round_number(sum_amount_debit, 0) - round_number(sum_amount_credit, 0)

                        if(not trx_printed) and len(elements):
                            elements.pop()
                            if total_balance == 0 and len(elements):
                                elements.pop()
                                account_counter -= 1

                # Account Total
                if sum_amount_credit_acc != 0 or sum_amount_debit_acc != 0:
                    table_data = []
                    table_data.append([
                        '', '', '', '', '', '', 'Total: ' + str(mAccount.name) + ' ' + str(curr_year), '', '', '', '', '',
                        intcomma(decimal_place % round_number(sum_amount_debit_acc)), '', intcomma(decimal_place % round_number(sum_amount_credit_acc)), '',
                        intcomma(decimal_place % round_number(sum_amount_debit_acc - sum_amount_credit_acc)
                                 ), '', intcomma(decimal_place % round_number(total_balance_acc)), '', ''])
                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ('LINEABOVE', (-3, -1), (-3, -1), 0.25, colors.black),
                         ('LINEBELOW', (-3, -1), (-3, -1), 0.25, colors.black),
                         ('LINEABOVE', (-5, -1), (-5, -1), 0.25, colors.black),
                         ('LINEBELOW', (-5, -1), (-5, -1), 0.25, colors.black),
                         ('LINEABOVE', (-7, -1), (-7, -1), 0.25, colors.black),
                         ('LINEBELOW', (-7, -1), (-7, -1), 0.25, colors.black),
                         ('LINEABOVE', (-9, -1), (-9, -1), 0.25, colors.black),
                         ('LINEBELOW', (-9, -1), (-9, -1), 0.25, colors.black),
                         ]))
                    elements.append(item_table)
                if company.currency.is_decimal:
                    grandtotal += round_number(total_balance_acc, 2)
                else:
                    grandtotal += round_number(total_balance_acc, 0)

            # GRAND TOTAL
            table_data = []
            table_data.append([])
            table_data.append(['', '', '', '', '', '', 'Report Total: ', '', '', '', '', '',
                               intcomma(decimal_place % round_number(g_debit)), '', intcomma(decimal_place % round_number(g_credit)), '',
                               intcomma(decimal_place % round_number(g_net)), '', intcomma(decimal_place % round_number(grandtotal)), '', ''])
            table_data.append([
                str(account_counter) + ' ' + 'accounts printed', '', '', '', '', '', '', '', '', '', '', '',
                '', '',  '', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=COMMON_COLUMN)

            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('LINEABOVE', (-3, -2), (-3, -2), 0.25, colors.black),
                 ('LINEBELOW', (-3, -2), (-3, -2), 0.25, colors.black),
                 ('LINEABOVE', (-5, -2), (-5, -2), 0.25, colors.black),
                 ('LINEBELOW', (-5, -2), (-5, -2), 0.25, colors.black),
                 ('LINEABOVE', (-7, -2), (-7, -2), 0.25, colors.black),
                 ('LINEBELOW', (-7, -2), (-7, -2), 0.25, colors.black),
                 ('LINEABOVE', (-9, -2), (-9, -2), 0.25, colors.black),
                 ('LINEBELOW', (-9, -2), (-9, -2), 0.25, colors.black),
                 ]))
            elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=COMMON_COLUMN)
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                      issue_to=issue_to),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                       issue_to=issue_to),
                  # Get the value of the BytesIO buffer and write it to the response.
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
