from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from transactions.models import Transaction
from accounts.models import Account, AccountHistory
import os
from django.db.models import Q
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reports.print_GLSource import transaction_detail, get_broken_string
from reports.print_GLSource import get_posting_sequence, value_checker
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
from utilities.common import round_number

HEADER_COLUMN = [280, 330, 200]
COMMON_COLUMN = [35, 3, 35, 3, 55, 3, 218, 3, 200, 3, 50, 3, 50, 3, 55, 3, 55, 12]


class Print_GLFunctionBatch:
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
        row1_info1 = "Date:  " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # # 2nd row
        row2_info1 = "G/L Transactions Listing - In Functional Currency (GLPTLS1)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_data.append([])
        # # 3rd row
        row3_info1 = "Include Accounts With No Activity "
        row3_info2 = "[No]"
        header_data.append([row3_info1, row3_info2])

        # # 6st row
        row5_info1 = "Include Balances and Net Changes "
        row5_info2 = "[No]"
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
        header_table.drawOn(canvas, doc.leftMargin - 2, doc.height + doc.topMargin - h + 8)
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
        row1_info1 = "Date:  " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row1_info2 = company.name
        header_data.append([row1_info1, row1_info2])

        # # 2nd row
        row2_info1 = "G/L Transactions Listing - In Functional Currency (GLPTLS1)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        header_data.append([])
        header_table = Table(header_data, colWidths=HEADER_COLUMN)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 2, doc.height + doc.topMargin - h - 14)

        table_data = []
        table_data.append(['Account Number/', '', '', '', '', '', '', '', '', '', 'Posting'])
        table_data.append(['Prd.', '', 'Source', '', 'Doc.Date', '', 'Description', '', 'Reference',
                           '', 'Seq.', '', 'Batch-Entry',  '', 'Debits', '', 'Credits', ''])

        item_header_table = Table(table_data, colWidths=COMMON_COLUMN)

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
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
             ('LINEBELOW', (-2, -1), (-2, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 2, doc.height + doc.topMargin - h - h1 - 14)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list, sp_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN,
                                topMargin=s.REPORT_TOP_MARGIN, bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))

        company = Company.objects.get(pk=company_id)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        posting_sequence = get_posting_sequence(company_id)
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
        table_data.append(['Sort Transactions By Transaction Date', '[No] ', ''])
        table_data.append(['From Account no.', acc_str, ''])
        table_data.append(['From Account Group', '[] To [ZZZZZZZZZZZZ]', ''])
        table_data.append(['Last Year Closed',  str(last_year.year), ''])
        table_data.append(['Last Posting Sequence', posting_sequence if posting_sequence else '-', ''])
        table_data.append(['Use Rolled Up Amounts ', '[No]', ''])
        table_data.append(['Date ', 'Doc. Date', ''])

        item_table = Table(table_data, colWidths=[280, 330, 192])
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
        table_data.append(['Account Number/', '', '', '', '', '', '', '', '', '', 'Posting'])
        table_data.append(['Prd.', '', 'Source', '', 'Doc.Date', '', 'Description', '', 'Reference',
                           '', 'Seq.', '', 'Batch-Entry',  '', 'Debits', '', 'Credits', '', ''])

        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        # 6column
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ('LINEBELOW', (0, -1), (0, -1), 0.25, colors.black),
             ('LINEBELOW', (2, -1), (2, -1), 0.25, colors.black),
             ('LINEBELOW', (4, -1), (4, -1), 0.25, colors.black),
             ('LINEBELOW', (6, -1), (6, -1), 0.25, colors.black),
             ('LINEBELOW', (8, -1), (8, -1), 0.25, colors.black),
             ('LINEBELOW', (10, -1), (10, -1), 0.25, colors.black),
             ('LINEBELOW', (12, -1), (12, -1), 0.25, colors.black),
             ('LINEBELOW', (14, -1), (14, -1), 0.25, colors.black),
             ('LINEBELOW', (-3, -1), (-3, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        table_data = []
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

        sum_amount_credit = sum_amount_debit = 0
        accumulate_credit_amount = accumulate_debit_amount = 0
        table_data = []
        account_counter = 0
        # process data
        # get account
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
                opening_balance = 0
                ending_balance = 0
                checker = False
                print_opening_checker = True
                print_ending_checker = False
                if open_account_history:
                    opening_balance = open_account_history.functional_begin_balance
                    ending_balance = open_account_history.functional_end_balance
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
                                                                                 journal__perd_month=current_month
                                                                                 )
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
                    if (len(transaction_item_list_account) or opening_balance) and print_opening_checker:
                        print_opening_checker = False
                        print_ending_checker = True
                        account_counter += 1
                        db_balance, cr_balance = value_checker(mAccount, opening_balance)
                        table_data.append([
                            mAccount.code, '', '', '', '', '', mAccount.name,  '', 'Opening Balance:', '', '', '', '', '', db_balance, '', cr_balance, '', ''])
                        item_table = Table(table_data, colWidths=COMMON_COLUMN)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('TOPPADDING', (0, 0), (-1, -1), 3),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
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
                                table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                     ('ALIGN', (9, 0), (-1, -1), 'RIGHT'),
                                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                     ]))
                                elements.append(item_table)

                            batch_no = ''
                            posting_sequence = ''

                            if mItem.journal and mItem.journal.batch:
                                batch_no = str(int(mItem.journal.batch.batch_no)) + '-' + str(int(mItem.journal.code))
                                posting_sequence = mItem.journal.batch.posting_sequence

                            table_data = []
                            transaction_detail_list = transaction_detail(mItem, 42)
                            table_data.append([
                                current_month, '', mItem.source_type, '',
                                mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal else ' / / ', '', transaction_detail_list[1],
                                '', transaction_detail_list[0], '', posting_sequence, '', batch_no, '',
                                intcomma(decimal_place % round_number(mItem.functional_amount) if mItem.is_debit_account == 1 else ''), '',
                                intcomma(decimal_place % round_number(mItem.functional_amount) if mItem.is_credit_account == 1 else ''), '', ''])
                            try:
                                desc_list = get_broken_string(transaction_detail_list[2], 42)
                                for desc_str in desc_list:
                                    table_data.append(
                                        ['', '', '', '', '', '', desc_str, '', '', '', '', '', '', '', '', '', ''])
                            except:
                                pass

                            item_table = Table(table_data, colWidths=COMMON_COLUMN)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                 ('ALIGN', (9, 0), (-1, -1), 'RIGHT'),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('TOPPADDING', (0, 0), (-1, -1), -1),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ]))
                            elements.append(item_table)
                            trx_printed = True
                            if mItem.is_credit_account == 1:
                                sum_amount_credit += round_number(mItem.functional_amount)
                            if mItem.is_debit_account == 1:
                                sum_amount_debit += round_number(mItem.functional_amount)
                        if(not trx_printed) and len(elements):
                            elements.pop()
                            if opening_balance == 0 and len(elements):
                                elements.pop()
                                account_counter -= 1

                    if company.currency.is_decimal:
                        accumulate_credit_amount += round_number(sum_amount_credit, 2)
                        accumulate_debit_amount += round_number(sum_amount_debit, 2)
                    else:
                        accumulate_credit_amount += round_number(sum_amount_credit, 0)
                        accumulate_debit_amount += round_number(sum_amount_debit, 0)
                    if sum_amount_debit or sum_amount_credit:
                        checker = True
                        table_data = []
                        table_data.append(['', '', '', '', '', '', '', '', 'Total: ' + str(mAccount.name) + ' ' + str(curr_year), '', '', '', '', '',
                                           intcomma(decimal_place % round_number(sum_amount_debit)), '',
                                           intcomma(decimal_place % round_number(sum_amount_credit)), '', ''])

                        item_table = Table(table_data, colWidths=COMMON_COLUMN)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('LINEABOVE', (-5, -1), (-5, -1), 0.25, colors.black),
                             ('LINEBELOW', (-5, -1), (-5, -1), 0.25, colors.black),
                             ('LINEABOVE', (-3, -1), (-3, -1), 0.25, colors.black),
                             ('LINEBELOW', (-3, -1), (-3, -1), 0.25, colors.black),
                             ]))
                        elements.append(item_table)

                if print_ending_checker:
                    table_data = []
                    db_balance = intcomma(decimal_place % round_number(ending_balance) if ending_balance > 0 else '')
                    cr_balance = intcomma(decimal_place % round_number(abs(ending_balance)) if ending_balance < 0 else '')
                    if checker and not db_balance and not cr_balance:
                        db_balance = '0.00'

                    table_data.append([
                        '', '', '', '', '', '', '', '', Paragraph(str('Ending Balance:'), styles['LeftAlignBold']), '', '', '', '', '',
                        db_balance, '', cr_balance, '', ''])
                    table_data.append([])
                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                         ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ]))
                    elements.append(item_table)

                    if not db_balance and not cr_balance and len(elements):
                        elements.pop()

        table_data = []
        table_data.append(['', '', '', '', '', '', '', '', 'Report Total:', '', '', '', '', '',
                           intcomma(decimal_place % round_number(accumulate_debit_amount)), '',
                           intcomma(decimal_place % round_number(accumulate_credit_amount)), '', ''])
        table_data.append([str(account_counter) + ' accounts printed', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LINEABOVE', (-3, -2), (-3, -2), 0.25, colors.black),
             ('LINEBELOW', (-3, -2), (-3, -2), 0.25, colors.black),
             ('LINEABOVE', (-5, -2), (-5, -2), 0.25, colors.black),
             ('LINEBELOW', (-5, -2), (-5, -2), 0.25, colors.black)
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
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
