from companies.models import Company
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES
from transactions.models import Transaction
from accounts.models import Account, AccountHistory
from django.contrib.humanize.templatetags.humanize import intcomma
import xlsxwriter
from utilities.common import round_number
from reports.print_GLSource import transaction_detail, get_posting_sequence
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q


class GLSource_Balance_Batch_XLS:
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

        center_bold = workbook.add_format({
            'bold': True,
            'align': 'center',
        })
        center_line = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bottom': 1,
            'top': 1
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

        is_decimal_f = company.currency.is_decimal

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
        worksheet.merge_range('D4:F4', 'G/L Transactions Listing - In Source and Functional Currency (GLPTLS3)', merge_format)
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

        worksheet.write(20, 0, 'Account Number/Desc.', center_bold)
        worksheet.merge_range('G20:J20', '--------------------------------- Source Currency ----------------------------------', center_bold)
        worksheet.merge_range('K20:N20', '--------------------------------- Functional Currency ----------------------------------', center_bold)
        # worksheet.write(21, 0, 'Year/Prd.', center_line)
        worksheet.write(21, 0, 'Prd.', center_line)
        worksheet.write(21, 1, 'Source', center_line)
        worksheet.write(21, 2, 'Doc. Date', center_line)
        worksheet.write(21, 3, 'Posting Seq.', center_line)
        worksheet.write(21, 4, 'Batch-Entry', center_line)
        worksheet.write(21, 5, 'Curr/Exchange rate', right_bold)
        worksheet.write(21, 6, 'Debits', right_bold)
        worksheet.write(21, 7, 'Credits', right_bold)
        worksheet.write(21, 8, 'Net Changes', right_bold)
        worksheet.write(21, 9, 'Balance', right_bold)
        worksheet.write(21, 10, 'Debits', right_bold)
        worksheet.write(21, 11, 'Credits', right_bold)
        worksheet.write(21, 12, 'Net Changes', right_bold)
        worksheet.write(21, 13, 'Balance', right_bold)

        worksheet.set_column(0, 13, 15)

        printing_row = 22
        printing_col = 0
        account_counter = 0
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
        # calculate_account_history(company_id, open_year, open_month)
        grand_total_cr = grand_total_db = 0
        account_counter = 0
        if account_item_list:
            for mAccount in account_item_list:
                open_account_history = full_account_history_list.filter(account_id=mAccount.id).order_by('source_currency_id')

                total_func_balance = 0
                remove_flag = False
                contain_trans = False
                remove_count = 0
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
                            worksheet.write(printing_row, printing_col, str(mAccount.code))
                            worksheet.write(printing_row, printing_col + 1, str(mAccount.name))
                            worksheet.write(printing_row, printing_col + 5, mAccount_History.source_currency.code if mAccount_History.source_currency else '')
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                begin_balance), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 13, round_number(
                                f_begin_balance), dec_format if is_decimal_f else num_format)
                            printing_row += 1
                            remove_count += 1
                        else:
                            worksheet.write(printing_row, printing_col + 5, mAccount_History.source_currency.code if mAccount_History.source_currency else '')
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                begin_balance), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 13, round_number(
                                f_begin_balance), dec_format if is_decimal_f else num_format)
                            printing_row += 1
                            remove_count += 1

                    if print_total_balance:
                        worksheet.write(printing_row, printing_col + 13, round_number(
                            total_func_balance), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1
                        remove_count += 1

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
                                    # worksheet.write(printing_row, printing_col, str(curr_year))
                                    printing_row += 1

                                    if mItem.currency_id:
                                        m_currency_month = mItem.currency.code
                                        m_currency = mItem.currency
                                    else:
                                        m_currency_month = ''

                                # get net balance every month,every currency
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

                                    is_decimal = m_currency.is_decimal if m_currency else True
                                    worksheet.write(printing_row, printing_col + 4, 'Net Change and Ending Balance for Fiscal Period ' +
                                                    str(current_month) + ': ', right_bold)
                                    worksheet.write(printing_row, printing_col + 5, m_currency_month, right_bold)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        net_change), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        balance), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        f_net_change), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 13, round_number(
                                        f_balance), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1

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

                                transaction_detail_list = transaction_detail(mItem)

                                is_decimal = mItem.currency.is_decimal if mItem.currency else True
                                total_amnt = round_number(mItem.total_amount)
                                total_f_amnt = round_number(mItem.functional_amount)

                                worksheet.write(printing_row, printing_col, str(current_month))
                                worksheet.write(printing_row, printing_col + 1, mItem.source_type)
                                worksheet.write(printing_row, printing_col + 2, mItem.journal.document_date.strftime("%d/%m/%Y")
                                                if mItem.journal.document_date else ' / / ')
                                worksheet.write(printing_row, printing_col + 3, posting_sequence)
                                worksheet.write(printing_row, printing_col + 4, batch_no)
                                worksheet.write(printing_row, printing_col + 5, mItem.currency.code if mItem.currency_id else '')
                                worksheet.write(printing_row, printing_col + 6, total_amnt if mItem.is_debit_account == 1 and total_amnt
                                                > 0 else total_amnt if mItem.account.balance_type == '1' and total_amnt == 0 else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 7, total_amnt if mItem.is_credit_account == 1 and total_amnt
                                                > 0 else total_amnt if mItem.account.balance_type == '2' and total_amnt == 0 else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, total_f_amnt if mItem.is_debit_account ==
                                                1 else None, dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 11, total_f_amnt if mItem.is_credit_account ==
                                                1 else None, dec_format if is_decimal_f else num_format)
                                printing_row += 1

                                worksheet.write(printing_row, printing_col + 1, transaction_detail_list[0])
                                worksheet.write(printing_row, printing_col + 5, mItem.exchange_rate, rate_format)
                                printing_row += 1
                                worksheet.write(printing_row, printing_col + 1, transaction_detail_list[1])
                                printing_row += 1

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

                                    is_decimal = m_currency.is_decimal if m_currency else True
                                    worksheet.write(printing_row, printing_col + 4, 'Net Change and Ending Balance for Fiscal Period ' +
                                                    str(current_month) + ': ', right_bold)
                                    worksheet.write(printing_row, printing_col + 5, m_currency_month, right_bold)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        net_change), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        balance), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        f_net_change), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 13, round_number(
                                        f_balance), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1

                                    for k in currency_total:
                                        is_decimal = k['curr'].is_decimal
                                        worksheet.write(printing_row, printing_col + 3, 'Account ' + mAccount.code, right_bold)
                                        worksheet.write(printing_row, printing_col + 4, 'Total: ', right_bold)
                                        worksheet.write(printing_row, printing_col + 5, k['curr'].code, right_bold)
                                        worksheet.write(printing_row, printing_col + 9, round_number(
                                            k['s_balance']), border_top_bot_dec if is_decimal else border_top_bot_num)
                                        worksheet.write(printing_row, printing_col + 13, round_number(
                                            k['f_balance']), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                        printing_row += 1

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

                                is_decimal = m_currency.is_decimal if m_currency else True
                                worksheet.write(printing_row, printing_col + 4, 'Net Change and Ending Balance for Fiscal Period ' +
                                                str(current_month) + ': ', right_bold)
                                worksheet.write(printing_row, printing_col + 5, m_currency_month, right_bold)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    net_change), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    balance), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    f_net_change), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 13, round_number(
                                    f_balance), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                printing_row += 1

                                for k in currency_total:
                                    is_decimal = k['curr'].is_decimal
                                    worksheet.write(printing_row, printing_col + 3, 'Account ' + mAccount.code, right_bold)
                                    worksheet.write(printing_row, printing_col + 4, 'Total: ', right_bold)
                                    worksheet.write(printing_row, printing_col + 5, k['curr'].code, right_bold)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        k['s_balance']), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 13, round_number(
                                        k['f_balance']), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1
                            if not contain_trans and printing_row > 0:
                                printing_row -= 1

                    if contain_trans:
                        if company.currency.is_decimal:
                            grand_total_db += round_number(total_amount_debit_function, 2)
                            grand_total_cr += round_number(total_amount_credit_function, 2)
                        else:
                            grand_total_db += round_number(total_amount_debit_function, 0)
                            grand_total_cr += round_number(total_amount_credit_function, 0)
                        worksheet.write(printing_row, printing_col + 9, 'Total: ' + str(mAccount.name) + ' ' + str(curr_year), right_bold)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            total_amount_debit_function), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            total_amount_credit_function), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            total_acc), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 13, round_number(
                            total_func_balance + total_acc), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1

                if open_account_history and remove_flag and not contain_trans and printing_row > 0:
                    while remove_count > 0:
                        printing_row -= 1
                        remove_count -= 1
                    account_counter -= 1

            # GRAND TOTAL
            printing_row += 4
            worksheet.write(printing_row, printing_col + 9, 'Report Total: ', right_bold)
            worksheet.write(printing_row, printing_col + 10, round_number(grand_total_db),
                            border_top_bot_dec if is_decimal_f else border_top_bot_num)
            worksheet.write(printing_row, printing_col + 11, round_number(grand_total_cr),
                            border_top_bot_dec if is_decimal_f else border_top_bot_num)
            worksheet.write(printing_row, printing_col + 12, round_number(grand_total_db -
                            grand_total_cr), border_top_bot_dec if is_decimal_f else border_top_bot_num)
            printing_row += 2

            worksheet.write(printing_row, printing_col, str(account_counter) + ' ' + 'accounts printed')
            printing_row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
