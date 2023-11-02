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
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
from reports.print_GLSource import transaction_detail
from reports.print_GLSource import value_checker, get_posting_sequence
from utilities.common import round_number
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q

HEADER_COLUMN = [280, 250, 250]
COMMON_COLUMN = [25, 2, 25, 2, 45, 2, 150, 2, 150, 2, 22, 2, 35, 2, 20, 2, 35, 2, 65, 2, 65, 2, 65, 2, 65, 3]


class Print_GLSourceBatch:
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
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 5)
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

        header_table = Table(header_data, colWidths=HEADER_COLUMN)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (1, 0), (1, 1), 'CENTER'),
             ('TOPPADDING', (0, 0), (-1, -1), -1),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h - 15)

        table_data = []
        table_data.append([])
        table_data.append(['Acc Number/', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ])
        table_data.append([
            # 'Year/', '', '', '', '', '', '', '', '', '', 'Post-', '', 'Batch-', '', '', '', 'Exch.', '',  '---------- Source Currency ----------',
            '', '', '', '', '', '', '', '', '', '', 'Post-', '', 'Batch-', '', '', '', 'Exch.', '',  '---------- Source Currency ----------',
            '', '', '', '--------- Function Currency --------', '', '', '', ''])
        table_data.append([
            'Prd.', '', 'Srce.', '', 'Doc. Date', '', 'Description', '', 'Reference', '', 'Seq', '', 'Entry', '', 'Curr', '', 'Rate', '',
            'Debits', '', 'Credits', '', 'Debits', '', 'Credits', '', '', ''])
        item_header_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
             ('SPAN', (-8, -2), (-10, -2)),
             ('SPAN', (-4, -2), (-6, -2)),
             ('ALIGN', (-8, -2), (-10, -2), 'CENTER'),
             ('ALIGN', (-4, -2), (-6, -2), 'CENTER'),
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
             ('LINEBELOW', (-4, -1), (-4, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1 - 15)
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

        item_table = Table(table_data, colWidths=[280, 332, 200])
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
        table_data.append(['Acc Number/', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ])
        table_data.append([
            # 'Year/', '', '', '', '', '', '', '', '', '', 'Post-', '', 'Batch-', '', '', '', 'Exch.', '',  '---------- Source Currency ----------',
            '', '', '', '', '', '', '', '', '', '', 'Post-', '', 'Batch-', '', '', '', 'Exch.', '',  '---------- Source Currency ----------',
            '', '', '', '--------- Function Currency --------', '', '', '', ''])
        table_data.append([
            'Prd.', '', 'Srce.', '', 'Doc. Date', '', 'Description', '', 'Reference', '', 'Seq', '', 'Entry', '', 'Curr', '', 'Rate', '',
            'Debits', '', 'Credits', '', 'Debits', '', 'Credits', '', '', ''])
        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('ALIGN', (18, 0), (-1, -1), 'RIGHT'),
             ('SPAN', (-8, -2), (-10, -2)),
             ('SPAN', (-4, -2), (-6, -2)),
             ('ALIGN', (-8, -2), (-10, -2), 'CENTER'),
             ('ALIGN', (-4, -2), (-6, -2), 'CENTER'),
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
             ('LINEBELOW', (-4, -1), (-4, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        table_data = []
        # end design interface header

        # get transaction
        company = Company.objects.get(pk=company_id)
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

        # get account
        account_item_list = account_list.exclude(deactivate_period__lte=issue_from).order_by('code').distinct()
        account_item_list = account_item_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        transaction_item_list = transaction_item_list.filter(account__in=account_item_list)

        account_counter = 0
        accumulate_credit_amount = accumulate_debit_amount = 0
        # process data
        if account_item_list:
            for i, mAccount in enumerate(account_item_list):
                table_data = []
                sum_amount_credit_change = sum_amount_debit_change = 0
                opening_balance = 0
                ending_balance = 0
                checker = False
                remove_flag = False
                trx_printed = False
                if sp_period == 'CLS':
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id__gt=0,
                                                                                                period_year=issue_from.year, period_month='CLS',
                                                                                                functional_currency_id=company.currency_id, source_currency_id=company.currency_id)\
                        .exclude(source_currency_id__isnull=True).first()
                else:
                    open_account_history = AccountHistory.objects.select_related('account').filter(company_id=company_id, is_hidden=0,
                                                                                                account_id=mAccount.id, source_currency_id__gt=0,
                                                                                                period_year=issue_from.year, period_month=issue_from.month,
                                                                                                functional_currency_id=company.currency_id, source_currency_id=company.currency_id)\
                        .exclude(source_currency_id__isnull=True).first()

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
                    account_counter += 1
                    db_balance, cr_balance = value_checker(mAccount, opening_balance)
                    table_data.append([
                        mAccount.code, '', '', '', '', mAccount.name, '',  '', '', '',
                        'Opening Balance: ', '', '', '', '', '', '', '', '', '', '', '', db_balance, '', cr_balance, '', '', ''])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                         ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                         ('SPAN', (5, 0), (8, 0)),
                         ('SPAN', (10, 0), (12, 0)),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('TOPPADDING', (0, 0), (-1, -1), -1),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                         ]))
                    elements.append(item_table)
                    if db_balance and float(db_balance.replace(',', '')) == 0:
                        if cr_balance and float(cr_balance.replace(',', '')) == 0:
                            remove_flag = True
                        else:
                            remove_flag = False
                    else:
                        remove_flag = False
                    # get data
                    sum_amount_credit = sum_amount_debit = 0
                    trx_printed = False
                    if transaction_item_list_account:
                        for j, mItem in enumerate(transaction_item_list_account):
                            if j == 0:
                                table_data = []
                                table_data.append([
                                    # curr_year, '', '', '', '', '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('TOPPADDING', (0, 0), (-1, -1), -1),
                                     ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
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
                            transaction_detail_list = transaction_detail(mItem, 30)
                            is_decimal = mItem.currency.is_decimal if mItem.currency else True
                            total_amnt = intcomma("%.2f" % round_number(mItem.total_amount)) if is_decimal else intcomma("%.0f" % mItem.total_amount)
                            total_f_amnt = intcomma("%.2f" % round_number(mItem.functional_amount)
                                                    ) if company.currency.is_decimal else intcomma("%.0f" % mItem.functional_amount)
                            table_data.append([
                                current_month, '', mItem.source_type, '', mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal else ' / / ',
                                '', transaction_detail_list[1], '', transaction_detail_list[0], '', posting_sequence, '', batch_no, '',
                                mItem.currency.code + " " if mItem.currency_id else '', '', intcomma("%.7f" % mItem.exchange_rate, 7), '',
                                total_amnt if mItem.is_debit_account == 1 and float(total_amnt.replace(
                                    ',', '')) > 0 else total_amnt if mItem.account.balance_type == '1' and float(total_amnt.replace(',', '')) == 0 else '', '',
                                total_amnt if mItem.is_credit_account == 1 and float(total_amnt.replace(
                                    ',', '')) > 0 else total_amnt if mItem.account.balance_type == '2' and float(total_amnt.replace(',', '')) == 0 else '', '',
                                total_f_amnt if mItem.is_debit_account == 1 else '', '',
                                total_f_amnt if mItem.is_credit_account == 1 else '', '', '', ''
                            ])
                            try:
                                table_data.append([
                                    '', '', '', '', '', '', transaction_detail_list[2][:30], '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '', '', '', '', '', '', ''
                                ])
                            except:
                                pass
                            trx_printed = True

                            item_table = Table(table_data, colWidths=COMMON_COLUMN)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                                 ('ALIGN', (14, 0), (-1, -1), 'RIGHT'),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('TOPPADDING', (0, 0), (-1, -1), -1),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ]))
                            elements.append(item_table)

                            if mItem.is_credit_account == 1:
                                sum_amount_credit += mItem.total_amount
                                sum_amount_credit_change += mItem.functional_amount
                            if mItem.is_debit_account == 1:
                                sum_amount_debit += mItem.total_amount
                                sum_amount_debit_change += mItem.functional_amount
                        if not trx_printed and len(elements):
                            elements.pop()
                if company.currency.is_decimal:
                    accumulate_credit_amount += round_number(sum_amount_credit_change, 2)
                    accumulate_debit_amount += round_number(sum_amount_debit_change, 2)
                else:
                    accumulate_credit_amount += round_number(sum_amount_credit_change, 0)
                    accumulate_debit_amount += round_number(sum_amount_debit_change, 0)
                if sum_amount_debit_change or sum_amount_credit_change:
                    checker = True
                    table_data = []
                    table_data.append(
                        ['', '', '', '', '', '', '',  '', 'Total: ' + str(mAccount.name) + ' ' + str(curr_year), '', '',
                         '', '', '', '', '', '', '', '', '', '', '',
                         intcomma("%.2f" % round_number(sum_amount_debit_change)), '',
                         intcomma("%.2f" % round_number(sum_amount_credit_change)), '', '', ''])

                    item_table = Table(table_data, colWidths=COMMON_COLUMN)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                         ('ALIGN', (8, 0), (-1, -1), 'RIGHT'),
                         ('SPAN', (8, 0), (16, 0)),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ('LINEABOVE', (-4, -1), (-4, -1), 0.25, colors.black),
                         ('LINEABOVE', (-6, -1), (-6, -1), 0.25, colors.black),
                         ('LINEBELOW', (-4, -1), (-4, -1), 0.25, colors.black),
                         ('LINEBELOW', (-6, -1), (-6, -1), 0.25, colors.black),
                         ]))
                    elements.append(item_table)

                table_data = []
                db_balance = intcomma("%.2f" % round_number(ending_balance) if ending_balance > 0 else '')
                cr_balance = intcomma("%.2f" % round_number(abs(ending_balance)) if ending_balance < 0 else '')
                if checker and not db_balance and not cr_balance:
                    db_balance = '0.00'

                table_data.append([
                    '', '', '', '', '', '', '',  '', '', '', 'Ending Balance: ', '', '', '', '', '', '', '',
                    '', '', '', '', db_balance, '', cr_balance, '', '', ''])
                table_data.append([])
                item_table = Table(table_data, colWidths=COMMON_COLUMN)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                        ('ALIGN', (13, 0), (-1, -1), 'RIGHT'),
                        ('SPAN', (10, 0), (12, 0)),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
                        ('TOPPADDING', (0, 0), (-1, -1), -1),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                     ]))
                elements.append(item_table)
                if remove_flag and not trx_printed:
                    if db_balance and float(db_balance.replace(',', '')) == 0:
                        if cr_balance and float(cr_balance.replace(',', '')) == 0:
                            remove_flag = True
                        else:
                            remove_flag = False
                    else:
                        remove_flag = False

                if remove_flag and len(elements) and not trx_printed:
                    account_counter -= 1
                    elements.pop()
                    if len(elements):
                        elements.pop()

        table_data = []
        table_data.append(['', '', '', '', '', '', '',  '', '', '', 'Report Total:',  '', '', '', '', '', '', '',
                           '', '', '', '',  intcomma("%.2f" % round_number(accumulate_debit_amount)
                                                     ) if company.currency.is_decimal else intcomma("%.0f" % accumulate_debit_amount), '',
                           intcomma("%.2f" % round_number(accumulate_credit_amount)) if company.currency.is_decimal else intcomma("%.0f" % accumulate_credit_amount), '', '', ''])
        table_data.append([str(account_counter) + ' accounts printed', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ])
        item_table = Table(table_data, colWidths=COMMON_COLUMN)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('ALIGN', (13, 0), (-1, -1), 'RIGHT'),
             ('SPAN', (10, 0), (12, 0)),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LINEABOVE', (-4, -2), (-4, -2), 0.25, colors.black),
             ('LINEBELOW', (-4, -2), (-4, -2), 0.25, colors.black),
             ('LINEABOVE', (-6, -2), (-6, -2), 0.25, colors.black),
             ('LINEBELOW', (-6, -2), (-6, -2), 0.25, colors.black)
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
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,  issue_to=issue_to),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
