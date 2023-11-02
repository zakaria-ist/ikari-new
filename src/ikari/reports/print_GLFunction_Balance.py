from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
from datetime import datetime
from django.conf import settings as s
from transactions.models import Transaction
from accounts.models import Account, AccountHistory
import os
from django.db.models import Q
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reports.print_GLSource import transaction_detail, get_broken_string
from reports.print_GLSource import get_posting_sequence
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
from utilities.common import round_number
from dateutil.relativedelta import relativedelta

HEADER_COLUMN = [280, 330, 150]
COMMON_COLUMN = [30, 3, 30, 3, 45, 3, 210, 3, 190, 3, 65, 3, 65, 3, 65, 3, 65, 3]


class Print_GLFunctionBalance:
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
        header_data.append([])
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
        row6_info2 = "[No]"
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
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
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
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - 20)

        table_data = []
        table_data.append([])
        table_data.append(['Account Number/', '', '', '', '', '', '', '', ''])
        table_data.append(['Prd.', '', 'Source', '', 'Doc.Date', '', 'Description', '', 'Reference',
                           '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance', ''])

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
             ('LINEBELOW', (-2, -1), (-2, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 1, doc.height + doc.topMargin - h - h1 - 15)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list, sp_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN,
                                topMargin=s.REPORT_TOP_MARGIN, bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))

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
        table_data.append(['From Account  No.', acc_str, ''])
        table_data.append(['From Account Group', '[] To [ZZZZZZZZZZZZ]', ''])
        table_data.append(['Last Year Closed',  str(last_year.year), ''])
        table_data.append(['Last Posting Sequence', posting_sequence if posting_sequence else '-', ''])
        table_data.append(['Use Rolled Up Amounts ', '[No]', ''])
        table_data.append(['Date ', 'Doc. Date', ''])

        item_table = Table(table_data, colWidths=[280, 332, 186])
        item_table.setStyle(TableStyle(
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
        elements.append(item_table)

        table_data = []
        table_data.append([])
        table_data.append(['Account Number/', '', '', '', '', '', '', '', ''])
        table_data.append(['Prd.', '', 'Source', '', 'Doc.Date', '', 'Description', '', 'Reference',
                           '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance', ''])

        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
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
             ('LINEBELOW', (-2, -1), (-2, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        table_data = []
        # end design interface header

        # get transaction
        if sp_period == 'CLS':
            transaction_item_list = Transaction.objects.select_related('journal__batch').select_related('journal').select_related('account').filter(
                company_id=company_id, is_hidden=0, journal_id__gt=0,
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
                company_id=company_id, is_hidden=0, journal_id__gt=0,
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


        table_data = []
        account_counter = 0
        accumulate_debit_amount = 0
        accumulate_credit_amount = 0
        # get account
        account_item_list = account_list.exclude(deactivate_period__lte=issue_from).order_by('code').distinct()
        account_item_list = account_item_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        transaction_item_list = transaction_item_list.filter(account__in=account_item_list)

        open_year = issue_from.year if issue_from else 0
        open_month = issue_from.month if issue_from else 0
        # calculate_account_history(company_id, open_year, open_month)
        grandtotal = 0
        decimal_place = "%.2f"
        if not company.currency.is_decimal:
            decimal_place = "%.0f"
        if account_item_list:
            for i, mAccount in enumerate(account_item_list):
                if sp_period == 'CLS':
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id=company.currency_id,
                                                                                                period_month='CLS', period_year=str(open_year),
                                                                                                functional_currency_id=company.currency_id)\
                        .exclude(source_currency_id__isnull=True).first()
                else:
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id=company.currency_id,
                                                                                                period_month=str(open_month), period_year=str(open_year),
                                                                                                functional_currency_id=company.currency_id)\
                        .exclude(source_currency_id__isnull=True).first()
                table_data = []
                total_balance = 0
                print_account_checker = True
                if open_account_history:
                    total_balance = open_account_history.functional_begin_balance

                    # get data
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
                        transaction_item_list_account = transaction_item_list.filter(account_id=mAccount.id, journal__perd_year=curr_year,
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
                            table_data.append([
                                mAccount.code, '', '', '', '', '', mAccount.name,  '', '', '', '', '', '', '', '', '',
                                intcomma(decimal_place % round_number(total_balance)), '', '', ''])

                            item_table = Table(table_data, colWidths=COMMON_COLUMN)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                 ('ALIGN', (13, 0), (-1, -1), 'RIGHT'),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('SPAN', (0, 0), (3, 0))
                                 ]))
                            elements.append(item_table)

                        sum_amount_credit = sum_amount_debit = 0
                        trx_printed = False
                        if transaction_item_list_account:
                            for j, mItem in enumerate(transaction_item_list_account):
                                if j == 0:
                                    table_data = []
                                    table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                                         ]))
                                    elements.append(item_table)

                                table_data = []

                                transaction_detail_list = transaction_detail(mItem, 38)

                                table_data.append([
                                    current_month, '', mItem.source_type, '', mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal else ' / / ',
                                    '', transaction_detail_list[1], '', transaction_detail_list[0], '',
                                    intcomma(decimal_place % round_number(mItem.functional_amount) if mItem.is_debit_account == 1 else ''), '',
                                    intcomma(decimal_place % round_number(mItem.functional_amount) if mItem.is_credit_account == 1 else ''),
                                    '', '', '', '', '', '', ''])
                                try:
                                    desc_list = get_broken_string(transaction_detail_list[2], 38)
                                    for desc_str in desc_list:
                                        table_data.append(
                                            ['', '', '', '', '', '', desc_str, '', '', '', '', '', '', '', '', '', '', '', '', ''])
                                except:
                                    pass

                                if mItem.is_credit_account == 1:
                                    sum_amount_credit += round_number(mItem.functional_amount)
                                if mItem.is_debit_account == 1:
                                    sum_amount_debit += round_number(mItem.functional_amount)

                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                     ('ALIGN', (9, 0), (-1, -1), 'RIGHT'),
                                     ('ALIGN', (1, 0), (8, 0), 'LEFT'),
                                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ]))
                                elements.append(item_table)
                                trx_printed = True
                                if (trx_printed and j == transaction_item_list_account.__len__() - 1):
                                    # get month
                                    table_data = []
                                    # total source
                                    total_balance += (sum_amount_debit - sum_amount_credit)
                                    table_data.append([
                                        '', '', '', '', '', '', 'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ', '', '', '',
                                        '', '', '', '', intcomma(decimal_place % round_number(sum_amount_debit - sum_amount_credit)),
                                        '', intcomma(decimal_place % round_number(total_balance)), '', '', ''])
                                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                         ('ALIGN', (6, 0), (8, 0), 'LEFT'),
                                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                         ('SPAN', (6, 0), (8, 0)),
                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2)
                                         ]))
                                    elements.append(item_table)
                                    if company.currency.is_decimal:
                                        sum_amount_credit_acc += round_number(sum_amount_credit, 2)
                                        sum_amount_debit_acc += round_number(sum_amount_debit, 2)
                                        total_balance_acc += round_number(sum_amount_debit, 2) - round_number(sum_amount_credit, 2)
                                    else:
                                        sum_amount_credit_acc += round_number(sum_amount_credit, 0)
                                        sum_amount_debit_acc += round_number(sum_amount_debit, 0)
                                        total_balance_acc += round_number(sum_amount_debit, 0) - round_number(sum_amount_credit, 0)
                            if(not trx_printed) and len(elements):
                                elements.pop()
                                if total_balance == 0 and len(elements):
                                    elements.pop()
                                    account_counter -= 1

                    if company.currency.is_decimal:
                        accumulate_credit_amount += round_number(sum_amount_credit_acc, 2)
                        accumulate_debit_amount += round_number(sum_amount_debit_acc, 2)
                    else:
                        accumulate_credit_amount += round_number(sum_amount_credit_acc, 0)
                        accumulate_debit_amount += round_number(sum_amount_debit_acc, 0)
                    # Account Total
                    if sum_amount_credit_acc or sum_amount_debit_acc:
                        table_data = []
                        table_data.append([
                            '', '', '', '', '', '', 'Total: ' + str(mAccount.name) + ' ' + str(curr_year),
                            '', '', '',
                            intcomma(decimal_place % round_number(sum_amount_debit_acc)), '',
                            intcomma(decimal_place % round_number(sum_amount_credit_acc)), '',
                            intcomma(decimal_place % round_number(sum_amount_debit_acc - sum_amount_credit_acc)), '',
                            intcomma(decimal_place % round_number(total_balance_acc)), '', '', ''])
                        table_data.append([])
                        item_table = Table(table_data, colWidths=COMMON_COLUMN)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                             ('ALIGN', (6, 0), (8, 0), 'LEFT'),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('TOPPADDING', (0, 0), (-1, -1), 0),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('SPAN', (6, 0), (8, 0)),
                             ('LINEABOVE', (10, -2), (10, -2), 0.25, colors.black),
                             ('LINEABOVE', (12, -2), (12, -2), 0.25, colors.black),
                             ('LINEABOVE', (14, -2), (14, -2), 0.25, colors.black),
                             ('LINEABOVE', (16, -2), (16, -2), 0.25, colors.black),
                             ('LINEBELOW', (10, -2), (10, -2), 0.25, colors.black),
                             ('LINEBELOW', (12, -2), (12, -2), 0.25, colors.black),
                             ('LINEBELOW', (14, -2), (14, -2), 0.25, colors.black),
                             ('LINEBELOW', (16, -2), (16, -2), 0.25, colors.black),
                             ]))
                        elements.append(item_table)

                    if company.currency.is_decimal:
                        grandtotal += round_number(total_balance_acc, 2)
                    else:
                        grandtotal += round_number(total_balance_acc, 0)
        # Report Final Total Row
        if company.currency.is_decimal:
            g_net = round_number(accumulate_debit_amount, 2) - round_number(accumulate_credit_amount, 2)
        else:
            g_net = round_number(accumulate_debit_amount, 0) - round_number(accumulate_credit_amount, 0)
        table_data = []
        table_data.append([
            '', '', '', '', '', '', 'Report Total:', '', '', '', intcomma(decimal_place % round_number(accumulate_debit_amount)), '',
            intcomma(decimal_place % round_number(accumulate_credit_amount)), '', intcomma(decimal_place % round_number(g_net)), '',
            intcomma(decimal_place % round_number(grandtotal)), '', '', ''])
        table_data.append([str(account_counter) + ' accounts printed', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
             ('ALIGN', (6, 0), (8, 0), 'LEFT'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('SPAN', (6, 0), (8, 0)),
             ('LINEABOVE', (10, -2), (10, -2), 0.25, colors.black),
             ('LINEABOVE', (12, -2), (12, -2), 0.25, colors.black),
             ('LINEABOVE', (14, -2), (14, -2), 0.25, colors.black),
             ('LINEABOVE', (16, -2), (16, -2), 0.25, colors.black),
             ('LINEBELOW', (10, -2), (10, -2), 0.25, colors.black),
             ('LINEBELOW', (12, -2), (12, -2), 0.25, colors.black),
             ('LINEBELOW', (14, -2), (14, -2), 0.25, colors.black),
             ('LINEBELOW', (16, -2), (16, -2), 0.25, colors.black),
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
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT,  adjusted_width=255))  # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
