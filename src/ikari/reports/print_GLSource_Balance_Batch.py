import os
from functools import partial
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from accounts.models import Account, AccountHistory
from companies.models import Company
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
from utilities.common import round_number
from reports.print_GLSource import transaction_detail
from reports.print_GLSource import get_posting_sequence

HEADER_COLUMN = [280, 250, 250]
COMMON_COLUMN = [30, 5, 30, 5, 45, 5, 30, 5, 50, 5, 40, 5, 64, 5, 64, 5, 64, 5, 64, 5, 64, 5, 64, 5, 64, 5, 64, 1]


class Print_GLSourceBalanceBatch:
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
        header_data.append([row3_info1, row3_info2, ''])

        # # 6st row
        row5_info1 = "Include Balances and Net Changes "
        row5_info2 = "[Yes]"
        header_data.append([row5_info1, row5_info2, ''])

        # # 6st row
        row6_info1 = "Include Posting Seq. and Batch-Entry "
        row6_info2 = "[Yes]"
        header_data.append([row6_info1, row6_info2, ''])

        # # 6st row
        row7_info1 = "Include Trans. Optional Fields"
        row7_info2 = "[No]"
        header_data.append([row7_info1, row7_info2, ''])

        header_table = Table(header_data, colWidths=HEADER_COLUMN)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1)
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
        header_data.append([row1_info1, row1_info2, ''])

        # # 2nd row
        row2_info1 = "G/L Transactions Listing - In Source and Functional Currency (GLPTLS3)"
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2, ''])

        header_table = Table(header_data, colWidths=HEADER_COLUMN)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 20)

        table_data = []
        table_data.append('')
        table_data.append([
            # 'Acc. No./Des./Year/', '', '', '', '', '', 'Post', '', '', '', 'Curr/', '',
            'Acc. No./Des.', '', '', '', '', '', 'Post', '', '', '', 'Curr/', '',
            '--------------------------------- Source Currency ----------------------------------', '', '', '', '', '', '', '',
            '------------------------------- Functional Currency -------------------------------', '',  '', '', '', ''])
        table_data.append(['Pd.', '', 'Source', '', 'Doc. Date', '', 'Seq-', '', 'Batch-Entry', '', 'Ex. Rate',
                           '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance', '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance'])
        item_header_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('SPAN', (12, -2), (18, -2)),
             ('SPAN', (20, -2), (26, -2)),
             ('ALIGN', (12, -2), (18, -2), 'CENTER'),
             ('ALIGN', (20, -2), (26, -2), 'CENTER'),
             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
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
             ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
             ('LINEBELOW', (18, -1), (18, -1), 0.25, colors.black),
             ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
             ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
             ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
             ('LINEBELOW', (26, -1), (26, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1 - 20)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, status_type, line_1, line_2, line_3, acc_list, sp_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        company = Company.objects.get(pk=company_id)
        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN - 6,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))

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
        table_data.append(['From Account No.', acc_str, ''])
        table_data.append(['From Account Group', '[] To [ZZZZZZZZZZZZ]', ''])
        table_data.append(['Last Year Closed',  str(last_year.year), ''])
        table_data.append(['Last Posting Sequence', posting_sequence if posting_sequence else '-', ''])
        table_data.append(['Use Rolled Up Amounts ', '[No]', ''])
        table_data.append(['Date ', 'Doc. Date', ''])

        item_table = Table(table_data, colWidths=[280, 202, 330])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ]))
        elements.append(item_table)

        table_data = []
        table_data.append([])
        table_data.append([
            # 'Acc. No./Des./Year/', '', '', '', '', '', 'Post', '', '', '', 'Curr/', '',
            'Acc. No./Des.', '', '', '', '', '', 'Post', '', '', '', 'Curr/', '',
            '--------------------------------- Source Currency ----------------------------------', '', '', '', '', '', '', '',
            '------------------------------- Functional Currency -------------------------------', '',  '', '', '', '', '', ])
        table_data.append(['Pd.', '', 'Source', '', 'Doc. Date', '', 'Seq-', '', 'Batch-Entry', '', 'Ex. Rate',
                           '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance', '', 'Debits', '', 'Credits', '', 'Net Change', '', 'Balance'])
        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('SPAN', (12, -2), (18, -2)),
             ('SPAN', (20, -2), (26, -2)),
             ('ALIGN', (12, -2), (18, -2), 'CENTER'),
             ('ALIGN', (20, -2), (26, -2), 'CENTER'),
             ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
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
             ('LINEBELOW', (16, -1), (16, -1), 0.25, colors.black),
             ('LINEBELOW', (18, -1), (18, -1), 0.25, colors.black),
             ('LINEBELOW', (20, -1), (20, -1), 0.25, colors.black),
             ('LINEBELOW', (22, -1), (22, -1), 0.25, colors.black),
             ('LINEBELOW', (24, -1), (24, -1), 0.25, colors.black),
             ('LINEBELOW', (26, -1), (26, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        # end design interface header

        # get transaction
        if sp_period == 'CLS':
            transaction_item_list = Transaction.objects.select_related('journal__batch').select_related('journal').select_related('account').filter(
                company=company, is_hidden=0, journal_id__gt=0, journal__is_hidden=0,
                journal__perd_year__range=[issue_from.year, issue_to.year],
                journal__journal_type=dict(TRANSACTION_TYPES)['GL']
            ).exclude(journal__batch__posting_sequence='0') \
                .exclude(journal__batch__status__in=(int(STATUS_TYPE_DICT['Deleted']),
                                                    int(STATUS_TYPE_DICT['Open']),
                                                    int(STATUS_TYPE_DICT['ERROR']),
                                                    int(STATUS_TYPE_DICT['Prov. Posted']))
                        ).order_by('account__code', 'journal__document_date')\
                        .only('id', 'is_credit_account', 'is_debit_account', 'amount', 
                            'transaction_date', 'is_hidden', 'account_id', 'company_id',
                            'currency_id', 'journal_id', 'total_amount', 'exchange_rate',
                            'functional_amount', 'description', 'reference', 'source_type')\
                        .distinct()
        else:
            transaction_item_list = Transaction.objects.select_related('journal__batch').select_related('journal').select_related('account').filter(
                company=company, is_hidden=0, journal_id__gt=0, journal__is_hidden=0,
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
                        ).order_by('account__code', 'journal__document_date')\
                        .only('id', 'is_credit_account', 'is_debit_account', 'amount', 
                            'transaction_date', 'is_hidden', 'account_id', 'company_id',
                            'currency_id', 'journal_id', 'total_amount', 'exchange_rate',
                            'functional_amount', 'description', 'reference', 'source_type')\
                        .distinct()

        diff = relativedelta(issue_to, issue_from)
        number_of_month = (diff.years * 12) + diff.months

        if status_type != '0':
            transaction_item_list = transaction_item_list.filter(journal__batch__status=status_type)

        # get account
        account_item_list = account_list.exclude(deactivate_period__lte=issue_from).order_by('code').distinct()
        account_item_list = account_item_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        transaction_item_list = transaction_item_list.filter(account__in=account_item_list)

        if sp_period == 'CLS':
            full_account_history_list = AccountHistory.objects.select_related('account').filter(company=company, is_hidden=0, source_currency_id__gt=0,
                                                                                                period_year=issue_from.year, period_month='CLS')\
                .exclude(source_currency_id__isnull=True)
        else:
            full_account_history_list = AccountHistory.objects.select_related('account').filter(company=company, is_hidden=0, source_currency_id__gt=0,
                                                                                                period_year=issue_from.year, period_month=issue_from.month)\
                .exclude(source_currency_id__isnull=True)
        m_currency_month = ''
        m_currency = None
        grand_total_cr = grand_total_db = 0
        account_counter = 0
        if account_item_list:
            for mAccount in account_item_list:
                open_account_history = full_account_history_list.filter(account_id=mAccount.id).order_by('source_currency_id')

                table_data = []
                total_func_balance = 0
                remove_flag = False
                contain_trans = False
                currency_total = []
                if open_account_history:
                    if mAccount.is_multicurrency:
                        print_total_balance = True
                    else:
                        print_total_balance = False
                    # rendering account with multi-currencies
                    for k, mAccount_History in enumerate(open_account_history):
                        if mAccount_History.source_currency == company.currency:
                            if mAccount.is_multicurrency:
                                begin_balance = mAccount_History.source_begin_balance
                                f_begin_balance = mAccount_History.source_begin_balance
                            else:
                                begin_balance = mAccount_History.functional_begin_balance
                                f_begin_balance = mAccount_History.functional_begin_balance
                        else:
                            begin_balance = mAccount_History.source_begin_balance
                            f_begin_balance = mAccount_History.functional_begin_balance

                        total_func_balance += f_begin_balance
                        is_decimal = mAccount_History.source_currency.is_decimal if mAccount_History.source_currency else True
                        currency_total.append({
                            'curr': mAccount_History.source_currency,
                            's_balance': begin_balance,
                            'f_balance': f_begin_balance
                        })
                        if k == 0:
                            table_data.append([
                                mAccount.code, '', '', '', mAccount.name[:28], '', '', '', '', '',
                                mAccount_History.source_currency.code, '', '', '', '', '', '', '',
                                intcomma("%.2f" % round_number(begin_balance)) if is_decimal else intcomma("%.0f" % begin_balance), '', '', '', '', '', '', '',
                                intcomma("%.2f" % round_number(f_begin_balance)) if company.currency.is_decimal else intcomma("%.0f" % f_begin_balance)])
                        else:
                            table_data.append([
                                '', '', '', '', '', '', '', '', '', '',
                                mAccount_History.source_currency.code if mAccount_History.source_currency else '', '', '', '', '', '', '', '',
                                intcomma("%.2f" % round_number(begin_balance)) if is_decimal else intcomma("%.0f" % begin_balance), '', '', '', '', '', '', '',
                                intcomma("%.2f" % round_number(f_begin_balance)) if company.currency.is_decimal else intcomma("%.0f" % f_begin_balance)])
                    if print_total_balance:
                        table_data.append([
                            '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', intcomma("%.2f" % round_number(total_func_balance)) if company.currency.is_decimal else intcomma("%.0f" % total_func_balance)])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN)

                    if print_total_balance:
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('TOPPADDING', (0, 0), (-1, -1), -1),
                             ('TOPPADDING', (0, 0), (26, 0), 3),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('SPAN', (4, 0), (8, 0)),
                             ('LINEABOVE', (-1, -1), (-1, -1), 0.25, colors.black)
                             ]))
                    else:
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('TOPPADDING', (0, 0), (-1, -1), -1),
                             ('TOPPADDING', (0, 0), (26, 0), 3),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('SPAN', (6, 0), (8, 0))
                             ]))
                    elements.append(item_table)
                    account_counter += 1
                    if total_func_balance == 0:
                        remove_flag = True
                    # get filter every item
                    total_amount_credit_function = total_amount_debit_function = total_acc = 0
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
                            # .order_by('currency__code', 'source_type', 'journal__batch__posting_sequence', 'journal__code')
                        

                        error_batch_nos = transaction_item_list_account.filter(journal__batch__description__icontains='error')\
                            .values_list('journal__batch__batch_no', flat=True)\
                            .order_by('journal__batch__batch_no').distinct()
                        error_batch_desc = transaction_item_list_account.filter(journal__batch__description__icontains='error')\
                            .values_list('journal__batch__description', flat=True)\
                            .order_by('journal__batch__description').distinct()

                        for batch_no in error_batch_nos:
                            if len([i for i in error_batch_desc if batch_no in i]):
                                transaction_item_list_account = transaction_item_list_account.exclude(journal__batch__batch_no=batch_no)

                        sum_amount_debit_change_month = sum_amount_credit_change_month = 0
                        sum_amount_credit_month_function = sum_amount_debit_month_function = 0
                        transaction_item_list_account = sorted(
                            transaction_item_list_account, key=lambda Transaction: (
                                Transaction.currency.code, 
                                Transaction.source_type, 
                                Transaction.journal.batch.posting_sequence, 
                                int(Transaction.journal.code)))
                        if transaction_item_list_account:
                            account_total_printed = False
                            for index, mItem in enumerate(transaction_item_list_account):
                                if index == 0:
                                    table_data = []
                                    table_data.append([
                                        # curr_year, '', ' ', '', ' ', '', '', '', '', '', '', '', '', '',
                                        '', '', ' ', '', ' ', '', '', '', '', '', '', '', '', '',
                                        ' ', '', '', '', '', '', '', '', '', '', '', '', ''])
                                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('BOTTOMPADDING', (0, -1), (-1, -1), 0),
                                            ('TOPPADDING', (0, -1), (-1, -1), 0),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
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
                                    net_change = sum_amount_debit_change_month - sum_amount_credit_change_month
                                    f_net_change = sum_amount_debit_month_function - sum_amount_credit_month_function
                                    total_acc += f_net_change
                                    is_decimal = True
                                    balance = f_balance = 0

                                    for k in currency_total:
                                        if k['curr'] == m_currency:
                                            is_decimal = k['curr'].is_decimal
                                            balance = k['s_balance'] + net_change
                                            k['s_balance'] = balance
                                            f_balance = k['f_balance'] + f_net_change
                                            k['f_balance'] = f_balance

                                    table_data = []
                                    table_data.append([
                                        'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ', '', '', '', '', '', '',
                                        '', '', '', m_currency_month, '', '', '', '', '',
                                        intcomma("%.2f" % round_number(net_change)) if is_decimal else intcomma("%.0f" % net_change), '',
                                        intcomma("%.2f" % round_number(balance)) if is_decimal else intcomma("%.0f" % balance), '', '', '', '', '',
                                        intcomma("%.2f" % round_number(f_net_change)) if company.currency.is_decimal else intcomma("%.0f" % f_net_change), '',
                                        intcomma("%.2f" % round_number(f_balance)) if company.currency.is_decimal else intcomma("%.0f" % f_balance)])

                                    table_data.append([])
                                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                                            ('ALIGN', (10, 0), (10, -1), 'CENTER'),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('TOPPADDING', (0, 0), (-1, -1), -1),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                                            ('SPAN', (0, 0), (9, 0)),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
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

                                batch_no = ''
                                posting_sequence = ''

                                if mItem.journal and mItem.journal.batch:
                                    batch_no = str(int(mItem.journal.batch.batch_no)) + '-' + str(int(mItem.journal.code))
                                    posting_sequence = mItem.journal.batch.posting_sequence

                                table_data = []

                                transaction_detail_list = transaction_detail(mItem, 30)

                                is_decimal = mItem.currency.is_decimal if mItem.currency else True
                                total_amnt = intcomma("%.2f" % round_number(mItem.total_amount)) if is_decimal else intcomma("%.0f" % mItem.total_amount)
                                total_f_amnt = intcomma("%.2f" % round_number(mItem.functional_amount)
                                                        ) if company.currency.is_decimal else intcomma("%.0f" % mItem.functional_amount)

                                table_data.append([
                                    current_month, '', mItem.source_type, '',
                                    mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal.document_date else ' / / ',
                                    '', posting_sequence, '',  batch_no,  '', mItem.currency.code if mItem.currency_id else '', '',
                                    total_amnt if mItem.is_debit_account == 1 and float(total_amnt.replace(
                                        ',', '')) > 0 else total_amnt if mItem.account.balance_type == '1' and float(total_amnt.replace(',', '')) == 0 else '', '',
                                    total_amnt if mItem.is_credit_account == 1 and float(total_amnt.replace(',', '')) > 0 else total_amnt if mItem.account.balance_type == '2' and float(
                                        total_amnt.replace(',', '')) == 0 else '', '', '', '', '', '',
                                    total_f_amnt if mItem.is_debit_account == 1 else '', '',
                                    total_f_amnt if mItem.is_credit_account == 1 else ''])

                                table_data.append([
                                    '', '', 'Ref.: ' + transaction_detail_list[0][:30], '', '', '', '', '', '', '',
                                    intcomma("%.7f" % mItem.exchange_rate), '', '', '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', ''])
                                table_data.append([
                                    '', '', 'Desc.: ' + transaction_detail_list[1], '', '', '', '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '', '', '', '', '', ''])
                                try:
                                    table_data.append([
                                        '', '', transaction_detail_list[2][:36], '', '', '', '', '', '', '', '', '', '', '',
                                        '', '', '', '', '', '', '', '', '', '', '', '', ''])
                                except:
                                    pass

                                contain_trans = True
                                # sum data month,total amount for every account code
                                if mItem.is_credit_account:
                                    total_amount_credit_function += round_number(mItem.functional_amount)
                                    sum_amount_credit_month_function += round_number(mItem.functional_amount)
                                    sum_amount_credit_change_month += mItem.total_amount
                                elif mItem.is_debit_account:
                                    total_amount_debit_function += round_number(mItem.functional_amount)
                                    sum_amount_debit_month_function += round_number(mItem.functional_amount)
                                    sum_amount_debit_change_month += mItem.total_amount

                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                        ('ALIGN', (10, 0), (-1, -1), 'RIGHT'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), -0.5),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), -0.5),
                                        ('SPAN', (2, 1), (8, 1)),
                                        ('SPAN', (2, 2), (12, 2))
                                     ]))
                                elements.append(item_table)

                                if (index == transaction_item_list_account.__len__() - 1):
                                    account_total_printed = True
                                    # get month
                                    net_change = sum_amount_debit_change_month - sum_amount_credit_change_month
                                    f_net_change = sum_amount_debit_month_function - sum_amount_credit_month_function
                                    total_acc += f_net_change
                                    is_decimal = True
                                    balance = f_balance = 0
                                    for k in currency_total:
                                        if k['curr'] == m_currency:
                                            is_decimal = k['curr'].is_decimal
                                            balance = k['s_balance'] + net_change
                                            k['s_balance'] = balance
                                            f_balance = k['f_balance'] + f_net_change
                                            k['f_balance'] = f_balance
                                    table_data = []
                                    table_data.append([
                                        'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ', '', '', '', '', '', '',
                                        '', '', '', m_currency_month, '', '', '', '', '',
                                        intcomma("%.2f" % round_number(net_change)) if is_decimal else intcomma("%.0f" % net_change), '',
                                        intcomma("%.2f" % round_number(balance)) if is_decimal else intcomma("%.0f" % balance), '', '', '', '', '',
                                        intcomma("%.2f" % round_number(f_net_change)) if company.currency.is_decimal else intcomma("%.0f" % f_net_change), '',
                                        intcomma("%.2f" % round_number(f_balance)) if company.currency.is_decimal else intcomma("%.0f" % f_balance)])

                                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                                            ('ALIGN', (10, 0), (10, 0), 'CENTER'),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('SPAN', (0, 0), (9, 0)),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                         ]))
                                    elements.append(item_table)

                                    table_data = []
                                    for k in currency_total:
                                        is_decimal = k['curr'].is_decimal
                                        table_data.append([
                                            '', '', '', '', '', 'Account ' + mAccount.code, '', '', '', 'Total: ',
                                            k['curr'].code, '', '', '', '', '', '', '',
                                            intcomma("%.2f" % round_number(k['s_balance'])) if is_decimal else intcomma("%.0f" % k['s_balance']), '', '', '',
                                            '', '', '', '', intcomma("%.2f" % round_number(k['f_balance'])) if company.currency.is_decimal else intcomma("%.0f" % k['f_balance'])])

                                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                                            ('ALIGN', (10, 0), (10, -1), 'CENTER'),
                                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                            ('TOPPADDING', (0, 0), (-1, -1), -1),
                                            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                         ]))
                                    elements.append(item_table)
                            if not account_total_printed:
                                net_change = sum_amount_debit_change_month - sum_amount_credit_change_month
                                f_net_change = sum_amount_debit_month_function - sum_amount_credit_month_function
                                total_acc += f_net_change
                                is_decimal = True
                                balance = f_balance = 0
                                for k in currency_total:
                                    if k['curr'] == m_currency:
                                        is_decimal = k['curr'].is_decimal
                                        balance = k['s_balance'] + net_change
                                        k['s_balance'] = balance
                                        f_balance = k['f_balance'] + f_net_change
                                        k['f_balance'] = f_balance
                                table_data = []
                                table_data.append([
                                    'Net Change and Ending Balance for Fiscal Period ' + str(current_month) + ': ', '', '', '', '', '', '',
                                    '', '', '', m_currency_month, '', '', '', '', '',
                                    intcomma("%.2f" % round_number(net_change)) if is_decimal else intcomma("%.0f" % net_change), '',
                                    intcomma("%.2f" % round_number(balance)) if is_decimal else intcomma("%.0f" % balance), '', '', '', '', '',
                                    intcomma("%.2f" % round_number(f_net_change)) if company.currency.is_decimal else intcomma("%.0f" % f_net_change), '',
                                    intcomma("%.2f" % round_number(f_balance)) if company.currency.is_decimal else intcomma("%.0f" % f_balance)])

                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                                        ('ALIGN', (10, 0), (10, 0), 'CENTER'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('SPAN', (0, 0), (9, 0)),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                     ]))
                                elements.append(item_table)

                                table_data = []
                                for k in currency_total:
                                    is_decimal = k['curr'].is_decimal
                                    table_data.append([
                                        '', '', '', '', '', 'Account ' + mAccount.code, '', '', '', 'Total: ',
                                        k['curr'].code, '', '', '', '', '', '', '',
                                        intcomma("%.2f" % round_number(k['s_balance'])) if is_decimal else intcomma("%.0f" % k['s_balance']), '', '', '',
                                        '', '', '', '', intcomma("%.2f" % round_number(k['f_balance'])) if company.currency.is_decimal else intcomma("%.0f" % k['f_balance'])])

                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                                        ('ALIGN', (10, 0), (10, -1), 'CENTER'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), -1),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                     ]))
                                elements.append(item_table)

                            if not contain_trans and len(elements):
                                elements.pop()

                    if contain_trans:
                        if company.currency.is_decimal:
                            grand_total_db += round_number(total_amount_debit_function, 2)
                            grand_total_cr += round_number(total_amount_credit_function, 2)
                        else:
                            grand_total_db += round_number(total_amount_debit_function, 0)
                            grand_total_cr += round_number(total_amount_credit_function, 0)

                        table_data = []
                        table_data.append([
                            '', '', '', '', '', '', '', '', '', '', '', '', 'Total: ', '', str(mAccount.name) + ' ' + str(curr_year),
                            '', '', '', '', '', intcomma("%.2f" % round_number(total_amount_debit_function)
                                                         ) if company.currency.is_decimal else intcomma("%.0f" % total_amount_debit_function), '',
                            intcomma("%.2f" % round_number(total_amount_credit_function)
                                     ) if company.currency.is_decimal else intcomma("%.0f" % total_amount_credit_function), '',
                            intcomma("%.2f" % round_number(total_acc)) if company.currency.is_decimal else intcomma("%.0f" % total_acc), '',
                            intcomma("%.2f" % round_number(total_func_balance + total_acc)) if company.currency.is_decimal else intcomma("%.0f" % float(total_func_balance + total_acc))])

                        COMMON_COLUMN_TOTAL = [30, 5, 30, 5, 45, 5, 30, 5, 50, 5, 40, 5, 35, 5, 93, 5, 64, 5, 64, 5, 64, 5, 64, 5, 64, 5, 64, 1]

                        item_table = Table(table_data, colWidths=COMMON_COLUMN_TOTAL)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                             ('ALIGN', (0, 0), (16, -1), 'LEFT'),
                             ('ALIGN', (17, 0), (-1, -1), 'RIGHT'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('LINEABOVE', (20, 0), (20, 0), 0.25, colors.black),
                             ('LINEABOVE', (22, 0), (22, 0), 0.25, colors.black),
                             ('LINEABOVE', (24, 0), (24, 0), 0.25, colors.black),
                             ('LINEABOVE', (26, 0), (26, 0), 0.25, colors.black),
                             ('LINEABOVE', (-1, 0), (-1, 0), 0.25, colors.black),
                             ('LINEABOVE', (20, 1), (20, 1), 0.25, colors.black),
                             ('LINEABOVE', (22, 1), (22, 1), 0.25, colors.black),
                             ('LINEABOVE', (24, 1), (24, 1), 0.25, colors.black),
                             ('LINEABOVE', (26, 1), (26, 1), 0.25, colors.black),
                             ('LINEABOVE', (-1, 1), (-1, 1), 0.25, colors.black),
                             ]))
                        elements.append(item_table)
                        # # end process data

                if open_account_history and remove_flag and not contain_trans and len(elements):
                    elements.pop()
                    account_counter -= 1

            # GRAND TOTAL
            table_data = []
            table_data.append([
                '', '', '', '', '', str('Report Total: '),  '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                intcomma("%.2f" % round_number(grand_total_db)) if company.currency.is_decimal else intcomma("%.0f" % grand_total_db), '',
                intcomma("%.2f" % round_number(grand_total_cr)) if company.currency.is_decimal else intcomma("%.0f" % grand_total_cr), '',
                intcomma("%.2f" % round_number(grand_total_db - grand_total_cr)) if company.currency.is_decimal else intcomma("%.0f" % float(grand_total_db - grand_total_cr)), '', ''])
            table_data.append([])
            table_data.append([
                str(account_counter) + ' accounts printed', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=COMMON_COLUMN)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('LINEABOVE', (-4, -3), (-4, -3), 0.25, colors.black),
                 ('LINEBELOW', (-4, -3), (-4, -3), 0.25, colors.black),
                 ('LINEABOVE', (-6, -3), (-6, -3), 0.25, colors.black),
                 ('LINEBELOW', (-6, -3), (-6, -3), 0.25, colors.black),
                 ('LINEABOVE', (-8, -3), (-8, -3), 0.25, colors.black),
                 ('LINEBELOW', (-8, -3), (-8, -3), 0.25, colors.black),
                 ('SPAN', (5, 0), (8, 0)),
                 ('SPAN', (0, -1), (4, -1)),
                 ]))
            elements.append(item_table)
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
                      canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
            # Get the value of the BytesIO buffer and write it to the response.
            pdf = buffer.getvalue()
            buffer.close()
            return pdf
