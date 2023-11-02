import os
from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from accounts.models import Account, AccountHistory
from companies.models import Company
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, BALANCE_TYPE_DICT
from reports.print_GLSource import get_posting_sequence
from utilities.common import round_number
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q

HEADER_COLUMN = [280, 250, 250]
COMMON_COLUMN = [30, 5, 30, 5, 50, 5, 135, 5, 25, 5, 50, 5, 25, 5, 55, 5, 55, 5, 55, 5, 55, 5, 55, 5, 55, 5, 55, 5, 55]


class Print_GLSourceBalance:
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
        row2_info1 = "G/L Transactions Listing - In Source and Functional Currency (GLPTLS3)"
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
             ('FONTSIZE', (1, 0), (1, 0), s.REPORT_FONT_SIZE),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)
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
        row2_info1 = "G/L Transactions Listing - In Source and Functional Currency (GLPTLS3)"
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
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_data.append(['Acc No/', '', 'Desc/', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '',
                           '----------------------- Source Currency --------------------- ', '', '', '', '', '', '', '',
                           '----------------------- Function Currency ---------------------'
                           ])
        table_data.append(['Prd.', '', 'Source', '', '', '', 'Date', '', 'Exch.Rate', '', 'Curr',
                           '', 'Debits', '', 'Credits', '', 'Net Change', '',
                           'Balance', '', 'Credits', '', 'Debits', '', 'Net Change', '', 'Balance'
                           ])

        item_header_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (12, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
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
             ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
             ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
             ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
             ('LINEBELOW', (-1, -1), (-1, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list, sp_period):
        company = Company.objects.get(pk=company_id)
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN,
                                topMargin=s.REPORT_TOP_MARGIN, bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))

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
        table_data.append(['Sort Transactions By Transaction Date', '[No] ', ''])
        table_data.append(['From Account No.', acc_str, ''])
        table_data.append(['From Account Group', '[] To [ZZZZZZZZZZZZ]', ''])
        table_data.append(['Last Year Closed',  str(last_year.year), ''])
        table_data.append(['Last Posting Sequence', posting_sequence if posting_sequence else '-', ''])
        table_data.append(['Use Rolled Up Amounts ', '[No]', ''])
        table_data.append(['Date ', 'Doc. Date', ''])

        item_table = Table(table_data, colWidths=[280, 330, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), s.REPORT_FONT_SIZE),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        elements.append(item_table)

        table_data = []

        table_data.append(['Acc No/', '', 'Desc/', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           '----------------------- Source Currency --------------------- ', '', '', '', '', '', '', '',
                           '----------------------- Function Currency ---------------------'
                           ])
        table_data.append(['Prd.', '', 'Source', '', '', '', 'Date', '', 'Exch.Rate', '', 'Curr',
                           '', 'Debits', '', 'Credits', '', 'Net Change', '',
                           'Balance', '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance'
                           ])
        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
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
             ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
             ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
             ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
             ('LINEBELOW', (-1, -1), (-1, -1), 0.25, colors.black),
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

        transaction_item_list = transaction_item_list.filter(journal__document_date__lte=issue_to)

        if status_type != '0':
            transaction_item_list = transaction_item_list.filter(journal__batch__status=status_type)

        # get account
        account_item_list = account_list.exclude(deactivate_period__lte=issue_from).order_by('code').distinct()
        account_item_list = account_item_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        transaction_item_list = transaction_item_list.filter(account__in=account_item_list)

        m_currency_month = ''
        m_currency = None
        open_year = issue_from.year if issue_from else 0
        open_month = issue_from.month if issue_from else 0
        if account_item_list:
            for i, mAccount in enumerate(account_item_list):
                table_data = []
                if sp_period == 'CLS':
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id__gt=0,
                                                                                                period_month='CLS', period_year=open_year)\
                        .exclude(source_currency_id__isnull=True)
                else:
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id__gt=0,
                                                                                                period_month=open_month, period_year=open_year)\
                        .exclude(source_currency_id__isnull=True)
                if open_account_history:
                    for k, mAccount_History in enumerate(open_account_history):
                        opening_balance = mAccount_History.functional_begin_balance
                        is_decimal = mAccount_History.source_currency.is_decimal if mAccount_History.source_currency else True
                        if k == 0:
                            table_data.append([
                                mAccount.code, '', mAccount.name, '', ' ', '', '', '', '', '',
                                mAccount_History.source_currency.code if mAccount_History.source_currency else '', '', ' ', '', '', '', '', '',
                                intcomma("%.2f" % round_number(opening_balance)) if is_decimal else intcomma("%.0f" % opening_balance),
                                '', '', '', '', '', '', '', intcomma("%.2f" % round_number(opening_balance)) if is_decimal else intcomma("%.0f" % opening_balance)])
                        else:
                            table_data.append([
                                '', '', ' ', '', ' ', '', '', '', '', '',  mAccount_History.source_currency.code if mAccount_History.source_currency else '',
                                '', ' ', '', '', '', '', '', intcomma("%.2f" % round_number(
                                    opening_balance)) if is_decimal else intcomma("%.0f" % opening_balance),
                                '', '', '', '', '', '', '', intcomma("%.2f" % round_number(opening_balance)) if is_decimal else intcomma("%.0f" % opening_balance)])
                else:
                    table_data.append([
                        mAccount.code, '', mAccount.name, '', ' ', '', '', '', '', '', '', '', ' ', '', '', '', '', '',
                        intcomma("%.2f" % 0) if int(mAccount.balance_type) == int(BALANCE_TYPE_DICT['Debit']) else '',
                        '', '', '', '', '', '', '', intcomma("%.2f" % 0) if int(mAccount.balance_type) == int(BALANCE_TYPE_DICT['Credit']) else ''])

                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                     ('ALIGN', (17, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('SPAN', (2, 0), (8, 0)),
                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                     ]))
                elements.append(item_table)

                total_amount_credit_function = total_amount_debit_function = total_acc = 0
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
                    # get filter every item
                    sum_amount_credit_month_function = sum_amount_debit_month_function = 0
                    sum_amount_debit_change_month = sum_amount_credit_change_month = 0
                    # get data to calculation balance
                    total_month = 0  # mAccount.debit_amount - mAccount.credit_amount
                    total_month_function = 0  # mAccount.debit_amount - mAccount.credit_amount
                    if transaction_item_list_account:
                        for j, mItem in enumerate(transaction_item_list_account):
                            if j == 0:
                                table_data = []
                                table_data.append(['', '', ' ', '', ' ', '', '', '', '', '', '', '', '', '',
                                                   ' ', '', '', '', '', '', '', '', '', '', '', '', ''])
                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                     ]))
                                elements.append(item_table)

                                if mItem.currency_id:
                                    m_currency_month = mItem.currency.code
                                    m_currency = mItem.currency
                                else:
                                    m_currency_month = ''

                            if mItem.currency_id:
                                code_currency = mItem.currency.code
                            else:
                                code_currency = ''
                            # output data if difference month or the same month but difference currency
                            if m_currency_month != code_currency:
                                total_month = 0  # mAccount.debit_amount - mAccount.credit_amount
                                total_month_function = 0  # mAccount.debit_amount - mAccount.credit_amount
                                net_change = sum_amount_debit_change_month - sum_amount_credit_change_month
                                f_net_change = sum_amount_debit_month_function - sum_amount_credit_month_function
                                total_month += (sum_amount_debit_change_month - sum_amount_credit_change_month)
                                total_month_function += (sum_amount_debit_month_function - sum_amount_credit_month_function)
                                total_acc += total_month_function

                                is_decimal = m_currency.is_decimal if m_currency else True
                                table_data = []
                                table_data.append([
                                    'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ',
                                    '', '', '', '', '', '', '', '', '', m_currency_month, '', '', '', '', '',
                                    intcomma("%.2f" % round_number(net_change)) if is_decimal else intcomma("%.0f" % net_change),
                                    '', intcomma("%.2f" % round_number(total_month)) if is_decimal else intcomma("%.0f" % total_month), '', '', '', '', '',
                                    intcomma("%.2f" % round_number(f_net_change)) if company.currency.is_decimal else intcomma("%.0f" % f_net_change),
                                    '', intcomma("%.2f" % round_number(total_month_function)) if company.currency.is_decimal else intcomma("%.0f" % total_month_function)])

                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
                                     ('FONT', (0, 0), (14, 0), s.REPORT_FONT_BOLD),
                                     ('FONT', (0, 1), (-1, -1), s.REPORT_FONT_BOLD),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                     ('SPAN', (0, 0), (9, 0)),
                                     ]))
                                elements.append(item_table)
                                sum_amount_credit_change_month = sum_amount_debit_change_month = 0
                                sum_amount_credit_month_function = sum_amount_debit_month_function = 0
                                if mItem.currency_id:
                                    m_currency_month = mItem.currency.code
                                    m_currency = mItem.currency
                                else:
                                    m_currency_month = ''
                                    m_currency = None

                            table_data = []

                            is_decimal = mItem.currency.is_decimal if mItem.currency else True
                            total_amnt = intcomma("%.2f" % round_number(mItem.total_amount)) if is_decimal else intcomma("%.0f" % mItem.total_amount)
                            total_f_amnt = intcomma("%.2f" % round_number(mItem.functional_amount)
                                                    ) if company.currency.is_decimal else intcomma("%.0f" % mItem.functional_amount)
                            table_data.append([
                                current_month, '', mItem.source_type, '', '', '',
                                mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal.document_date else ' / / ', '',
                                intcomma("%.7f" % mItem.exchange_rate), '', mItem.currency.code if mItem.currency_id else '', '',
                                total_amnt if mItem.is_debit_account == 1 else '', '',
                                total_amnt if mItem.is_credit_account == 1 else '',
                                '', '', '', '', '', total_f_amnt if mItem.is_debit_account == 1 else '', '',
                                total_f_amnt if mItem.is_credit_account == 1 else '', '', '', '', '', ])

                            # sum data month,total amount for every account code
                            if mItem.is_credit_account == 1:
                                total_amount_credit_function += mItem.functional_amount
                                sum_amount_credit_month_function += mItem.functional_amount
                                sum_amount_credit_change_month += mItem.total_amount
                            elif mItem.is_debit_account == 1:
                                total_amount_debit_function += mItem.functional_amount
                                sum_amount_debit_month_function += mItem.functional_amount
                                sum_amount_debit_change_month += mItem.total_amount

                            item_table = Table(table_data, colWidths=COMMON_COLUMN)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                 ('ALIGN', (11, 0), (-1, -1), 'RIGHT'),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                 ]))
                            elements.append(item_table)
                            if (j == transaction_item_list_account.__len__() - 1):
                                # get month
                                table_data = []
                                # total source
                                total_month = 0  # mAccount.debit_amount - mAccount.credit_amount
                                total_month_function = 0  # mAccount.debit_amount - mAccount.credit_amount
                                net_change = sum_amount_debit_change_month - sum_amount_credit_change_month
                                f_net_change = sum_amount_debit_month_function - sum_amount_credit_month_function
                                total_month += (sum_amount_debit_change_month - sum_amount_credit_change_month)
                                # total for function
                                total_month_function += (sum_amount_debit_month_function - sum_amount_credit_month_function)
                                total_acc += total_month_function

                                is_decimal = m_currency.is_decimal if m_currency else True
                                table_data.append([
                                    'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ',
                                    '', '', '', '', '', '', '', '', '', m_currency_month, '', '', '', '', '',
                                    intcomma("%.2f" % round_number(net_change)) if is_decimal else intcomma("%.0f" % net_change),
                                    '', intcomma("%.2f" % round_number(total_month)) if is_decimal else intcomma("%.0f" % total_month), '', '', '', '',
                                    '', intcomma("%.2f" % round_number(f_net_change)) if company.currency.is_decimal else intcomma("%.0f" % f_net_change),
                                    '', intcomma("%.2f" % round_number(total_month_function)) if company.currency.is_decimal else intcomma("%.0f" % total_month_function)])
                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('ALIGN', (16, 0), (-1, -1), 'RIGHT'),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                     ('SPAN', (0, 0), (9, 0)),
                                     ]))
                                elements.append(item_table)
                if total_acc:
                    table_data = []
                    table_data.append(
                        ['', '', '', '', '', '', '', '', '', '',
                         'Totals: ' + str(mAccount.name) + curr_year, '', '', '', '', '', '', '', '', '',
                         intcomma("%.2f" % round_number(total_amount_debit_function)), '',
                         intcomma("%.2f" % round_number(total_amount_credit_function)), '',
                         intcomma("%.2f" % round_number(total_amount_debit_function - total_amount_credit_function)), '',
                         intcomma("%.2f" % round_number(total_acc))
                         ])
                    table_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                                       '', '', '', '', '', '', '', '', '', '', '', ''])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                         ('ALIGN', (0, 0), (16, -1), 'LEFT'),
                         ('ALIGN', (17, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                         ('LINEABOVE', (20, 0), (20, 0), 0.25, colors.black),
                         ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                         ('LINEABOVE', (24, 0), (24, 0), 0.25, colors.black),
                         ('LINEABOVE', (-1, 0), (-1, 0), 0.25, colors.black),
                         ('LINEABOVE', (20, 1), (20, 1), 0.25, colors.black),
                         ('LINEABOVE', (22, 1), (22, 1), 0.25, colors.black),
                         ('LINEABOVE', (24, 1), (24, 1), 0.25, colors.black),
                         ('LINEABOVE', (-1, 1), (-1, 1), 0.25, colors.black),
                         ]))
                    elements.append(item_table)
                    # # end process data

        # else:  # if there's no order in the selected month
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
                  canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
