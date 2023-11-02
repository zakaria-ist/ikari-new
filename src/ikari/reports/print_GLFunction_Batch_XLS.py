from companies.models import Company
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
from transactions.models import Transaction
from accounts.models import Account, AccountHistory
from django.contrib.humanize.templatetags.humanize import intcomma
import xlsxwriter
from utilities.common import round_number
from reports.print_GLSource import transaction_detail, get_posting_sequence, value_checker
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q


class GLFunction_Batch_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def print_report(self, company_id, issue_from, issue_to, status_type, acc_list, sp_period):
        company = Company.objects.get(pk=company_id)
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("GL_Trx_Listing")

        merge_format = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            # 'bg_color': 'white'
        })
        right_line = workbook.add_format({
            'align': 'right'
        })

        center_line = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bottom': 1,
            'top': 1
        })
        center_bold = workbook.add_format({
            'bold': True,
            'align': 'center',
        })
        right_bold = workbook.add_format({
            'bold': True,
            'align': 'right',
            'bottom': 1,
            'top': 1
        })

        border_top_bot_num = workbook.add_format({
            'num_format': '#,##0',
            'bold': True,
            'align': 'right',
            'bottom': 1,
            'top': 1
        })
        border_top_bot_dec = workbook.add_format({
            'num_format': '#,##0.00',
            'bold': True,
            'align': 'right',
            'bottom': 1,
            'top': 1
        })

        dec_format = workbook.add_format({'num_format': '#,##0.00'})
        num_format = workbook.add_format({'num_format': '#,##0'})
        rate_format = workbook.add_format({'num_format': '#,##0.0000000'})

        is_decimal = company.currency.is_decimal

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

        worksheet.merge_range('D3:F3', company.name, merge_format)
        worksheet.merge_range('D4:F4', 'G/L Transactions Listing - In Functional Currency (GLPTLS1)', merge_format)
        worksheet.merge_range('D5:E5', 'Include Accounts With No Activity', merge_format)
        worksheet.write(4, 5, ': [No]', merge_format)
        worksheet.merge_range('D6:E6', 'Include Balances and Net Changes', merge_format)
        worksheet.write(5, 5, ': [Yes]', merge_format)
        worksheet.merge_range('D7:E7', 'Include Posting Seq. and Batch-Entry', merge_format)
        worksheet.write(6, 5, ': [Yes]', merge_format)
        worksheet.merge_range('D8:E8', 'Include Trans. Optional Fields', merge_format)
        worksheet.write(7, 5, ': [No]', merge_format)
        worksheet.merge_range('D9:E9', "Date", merge_format)
        worksheet.write(8, 5, ": " + datetime.now().strftime('%d-%m-%Y %H:%M:%S'), merge_format)
        worksheet.merge_range('D10:E10', 'From Year - Period', merge_format)
        worksheet.write(9, 5, ': ' + "[" + str(issue_from.month) + '-' + str(issue_from.year) + "]"
                              + " To: [" + str(issue_to.month) + '-' + str(issue_to.year) + "]", merge_format)
        worksheet.merge_range('D11:E11', 'Sort By', merge_format)
        worksheet.write(10, 5, ': [Account No.]', merge_format)
        worksheet.merge_range('D12:E12', 'Sort Transactions By Date', merge_format)
        worksheet.write(11, 5, ': [No]', merge_format)
        worksheet.merge_range('D13:E13', 'From Account No', merge_format)
        worksheet.write(12, 5, ': ' + acc_str, merge_format)
        worksheet.merge_range('D14:E14', 'From Account Group', merge_format)
        worksheet.write(13, 5, ': ' + '[] To [ZZZZZZZZZZZZ]', merge_format)
        worksheet.merge_range('D15:E15', 'Last Year Closed', merge_format)
        worksheet.write(14, 5, ': ' + str(last_year.year), merge_format)
        worksheet.merge_range('D16:E16', 'Last Posting Sequence', merge_format)
        worksheet.write(15, 5, ': ' + posting_sequence if posting_sequence else '-', merge_format)
        worksheet.merge_range('D17:E17', 'Use Rolled Up Amounts', merge_format)
        worksheet.write(16, 5, ': [No]', merge_format)
        worksheet.merge_range('D18:E18', 'Date Type', merge_format)
        worksheet.write(17, 5, ': Doc. Date', merge_format)

        worksheet.write(20, 0, 'Account Number/', center_bold)
        # worksheet.write(21, 0, 'Year/Prd.', center_line)
        worksheet.write(21, 0, 'Prd.', center_line)
        worksheet.write(21, 1, 'Source', center_line)
        worksheet.write(21, 2, 'Doc. Date', center_line)
        worksheet.write(21, 3, 'Description', center_line)
        worksheet.write(21, 4, 'Reference', center_line)
        worksheet.write(21, 5, 'Posting Seq.', center_line)
        worksheet.write(21, 6, 'Batch-Entry', center_line)
        worksheet.write(21, 7, 'Debits', right_bold)
        worksheet.write(21, 8, 'Credits', right_bold)

        worksheet.set_column(0, 8, 15)

        printing_row = 22
        printing_col = 0

        # decimal_place = "%.2f"
        # if not company.currency.is_decimal:
        #     decimal_place = "%.0f"

        account_counter = 0
        sum_amount_credit = sum_amount_debit = 0
        accumulate_credit_amount = accumulate_debit_amount = 0
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

        # get account
        account_item_list = account_list.exclude(deactivate_period__lte=issue_from).order_by('code').distinct()
        account_item_list = account_item_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        transaction_item_list = transaction_item_list.filter(account__in=account_item_list)

        open_year = issue_from.year if issue_from else 0
        open_month = issue_from.month if issue_from else 0
        # calculate_account_history(company_id, open_year, open_month)

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
                        worksheet.write(printing_row, printing_col, str(mAccount.code))
                        worksheet.write(printing_row, printing_col + 1, str(mAccount.name))
                        worksheet.write(printing_row, printing_col + 4, 'Opening Balance:', right_line)
                        worksheet.write(printing_row, printing_col + 7, float(
                            db_balance.replace(',', '')), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 8, float(
                            cr_balance.replace(',', '')), dec_format if is_decimal else num_format)
                        printing_row += 1

                    sum_amount_credit = sum_amount_debit = 0
                    trx_printed = False
                    if transaction_item_list_account:
                        for j, mItem in enumerate(transaction_item_list_account):
                            if j == 0:
                                # worksheet.write(printing_row, printing_col, curr_year)
                                printing_row += 1

                            batch_no = ''
                            posting_sequence = ''

                            if mItem.journal and mItem.journal.batch:
                                batch_no = str(int(mItem.journal.batch.batch_no)) + '-' + str(int(mItem.journal.code))
                                posting_sequence = mItem.journal.batch.posting_sequence

                            transaction_detail_list = transaction_detail(mItem)
                            worksheet.write(printing_row, printing_col, str(current_month))
                            worksheet.write(printing_row, printing_col + 1, mItem.source_type)
                            worksheet.write(printing_row, printing_col + 2, mItem.journal.document_date.strftime("%d/%m/%Y") if mItem.journal else ' / / ')
                            worksheet.write(printing_row, printing_col + 3, transaction_detail_list[1])
                            worksheet.write(printing_row, printing_col + 4, transaction_detail_list[0])
                            worksheet.write(printing_row, printing_col + 5, posting_sequence)
                            worksheet.write(printing_row, printing_col + 6, batch_no)
                            worksheet.write(printing_row, printing_col + 7, round_number(mItem.functional_amount)
                                            if mItem.is_debit_account == 1 else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(mItem.functional_amount)
                                            if mItem.is_credit_account == 1 else None, dec_format if is_decimal else num_format)
                            printing_row += 1

                            trx_printed = True
                            if mItem.is_credit_account == 1:
                                sum_amount_credit += round_number(mItem.functional_amount)
                            if mItem.is_debit_account == 1:
                                sum_amount_debit += round_number(mItem.functional_amount)
                        if(not trx_printed):
                            printing_row -= 1
                            # if total_balance == 0:
                            #     printing_row -= 1
                            #     account_counter -= 1

                    if company.currency.is_decimal:
                        accumulate_credit_amount += round_number(sum_amount_credit, 2)
                        accumulate_debit_amount += round_number(sum_amount_debit, 2)
                    else:
                        accumulate_credit_amount += round_number(sum_amount_credit, 0)
                        accumulate_debit_amount += round_number(sum_amount_debit, 0)
                    if sum_amount_debit or sum_amount_credit:
                        checker = True
                        worksheet.write(printing_row, printing_col + 6, 'Total: ' + str(mAccount.name) + ' ' + str(curr_year), right_bold)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            sum_amount_debit), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            sum_amount_credit), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

                    if print_ending_checker:
                        ending_balance = opening_balance + (sum_amount_debit - sum_amount_credit)
                        db_balance = round_number(ending_balance) if ending_balance > 0 else None
                        cr_balance = round_number(abs(ending_balance)) if ending_balance < 0 else None
                        if checker and not db_balance and not cr_balance:
                            db_balance = 0.00

                        worksheet.write(printing_row, printing_col + 4, 'Ending Balance:', right_line)
                        worksheet.write(
                            printing_row, printing_col + 7, db_balance, dec_format if is_decimal else num_format)
                        worksheet.write(
                            printing_row, printing_col + 8, cr_balance, dec_format if is_decimal else num_format)
                        printing_row += 2

                        if not db_balance and not cr_balance and printing_row > 0:
                            printing_row -= 1

        worksheet.write(printing_row, printing_col + 6, 'Report Total:', right_bold)
        worksheet.write(printing_row, printing_col + 7, round_number(accumulate_debit_amount),
                        border_top_bot_dec if is_decimal else border_top_bot_num)
        worksheet.write(printing_row, printing_col + 8, round_number(accumulate_credit_amount),
                        border_top_bot_dec if is_decimal else border_top_bot_num)
        printing_row += 2
        worksheet.write(printing_row, printing_col, str(account_counter) + ' ' + 'accounts printed')
        printing_row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
