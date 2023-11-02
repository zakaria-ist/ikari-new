import calendar
import datetime
import xlsxwriter
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import intcomma
from accounts.models import Account, AccountHistory
from accounting.models import FiscalCalendar
from transactions.models import Transaction
from companies.models import Company
from utilities.common import wrap_separator, separator, round_number
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, ACCOUNT_TYPE_DICT, BALANCE_TYPE_DICT


class Print_GLTrial_XLS(object):
    """docstring for Print_GLTrial_XLS"""

    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, gl_type, issue_from, issue_end, acc_list, is_activity):
        if gl_type == '1':
            xlsx_data = trial_balance(self, company_id, gl_type, issue_from, issue_end, acc_list, is_activity)
        elif gl_type == '2':
            xlsx_data = trial_netChanges(self, company_id, gl_type, issue_from, issue_end, acc_list,
                                         is_activity)
        return xlsx_data


def trial_balance(self, company_id, gl_type, issue_from, issue_end, acc_list, is_activity):
    company = Company.objects.get(pk=company_id)
    output = self.buffer
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Trial Balance")

    worksheet.set_column(0, 0, 14)
    worksheet.set_column(1, 1, 25)
    worksheet.set_column(2, 2, 15)
    worksheet.set_column(3, 3, 15)

    merge_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': 'white'
    })
    merge_left = workbook.add_format({
        'bold': True,
        'align': 'left',
        'valign': 'vcenter',
        'bg_color': 'white'
    })
    center = workbook.add_format({
        'align': 'center',
        'bold': True
    })
    right_line = workbook.add_format({
        'align': 'right'
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

    array_data = str(issue_from).split('-')
    if array_data[1] in ['ADJ', 'CLS']:
        issue_from = datetime.date(int(array_data[0]), 12, 1)
        issue_to = datetime.date(int(array_data[0]), 12,
                                 calendar.monthrange(int(array_data[0]), 12)[1])
    else:
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])

    fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, period=issue_to.month, fiscal_year=issue_to.year).last()
    if fsc_calendar:
        end_date = fsc_calendar.end_date.strftime('%d/%m/%Y')
    else:
        end_date = issue_to.strftime('%d/%m/%Y')

    acc_list = eval(acc_list)
    if len(acc_list):
        account_list = Account.objects.filter(id__in=acc_list).order_by('code')
    else:
        account_list = Account.objects.filter(is_hidden=False, company_id=company_id).order_by('code')

    is_activity_str = '[No]'
    if is_activity == '1':
        is_activity_str = '[Yes]'

    worksheet.merge_range('A1:D1', "", merge_format)
    worksheet.merge_range('A2:D2', company.name, merge_format)
    worksheet.merge_range('A3:D3', "Trial Balance as of  " + end_date, merge_format)
    worksheet.merge_range('A4:D4', "", merge_format)
    worksheet.merge_range('A5:D5', "Report (GLTRLR1)", merge_left)
    worksheet.merge_range('A6:D6', datetime.datetime.now().strftime('%d/%m/%Y %r'), merge_left)
    worksheet.merge_range('A7:D7', "In Functional Currency:     " + str(company.currency.code), merge_left)
    worksheet.merge_range('A8:D8', "", merge_format)
    worksheet.merge_range('A9:D9', "Sort By:     [Account No.]", merge_left)
    worksheet.merge_range('A10:D10', "Include Accounts With No Activity:     " + is_activity_str, merge_left)
    worksheet.merge_range('A11:D11', "For Year-Period:     " + "[" + '-'.join(array_data) + "]", merge_left)
    worksheet.merge_range('A12:D12', "From Account No.:     " + "[" + account_list[0].code + "] To [" + account_list[len(account_list)-1].code + "]", merge_left)
    worksheet.merge_range('A13:D13', "Use Rolled Up Amounts:     [No]", merge_left)
    worksheet.write(14, 0, 'Account Number', center)
    worksheet.write(14, 1, 'Description', center)
    worksheet.write(14, 2, 'Debit', center)
    worksheet.write(14, 3, 'Credit', center)
    row = 15
    col = 0

    account_item_list = account_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
    account_item_list = account_item_list.exclude(deactivate_period__lte=issue_from).values('id').order_by('code').distinct()

    total_debit = total_credit = 0
    total_income = total_income_debit = total_income_credit = 0
    sum_debit = sum_credit = 0
    mCode = ''
    mCountCode = 0
    if company.currency.is_decimal:
        is_decimal = True
    else:
        is_decimal = False
    if account_item_list:
        for acct in account_item_list:
            mAccount = account_list.filter(id=acct['id']).first()
            if array_data[1] == 'ADJ':
                item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                             source_currency__code=company.currency.code,
                                                             account_id=mAccount.id,
                                                             period_month__exact='CLS',
                                                             period_year__exact=int(array_data[0]))\
                    .exclude(source_currency_id__isnull=True).first()
            elif array_data[1] == 'CLS':
                item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                             source_currency__code=company.currency.code,
                                                             account_id=mAccount.id,
                                                             period_month__exact='CLS',
                                                             period_year__exact=int(array_data[0]))\
                    .exclude(source_currency_id__isnull=True).first()
            else:
                item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                             source_currency__code=company.currency.code,
                                                             account_id=mAccount.id,
                                                             period_month__exact=int(array_data[1]),
                                                             period_year__exact=int(array_data[0]))\
                    .exclude(source_currency_id__isnull=True).first()
            if mCode != mAccount.code:
                mCode = mAccount.code
                sum_debit = sum_credit = 0

            if item_account:
                if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                    sum_credit += item_account.functional_end_balance
                if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                    sum_debit += item_account.functional_end_balance

            if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                if sum_credit < 0:
                    mCountCode += 1
                    worksheet.write(row, col, mAccount.code)
                    worksheet.write(row, col + 1, mAccount.name)
                    worksheet.write(row, col + 2, None, num_format)
                    worksheet.write(row, col + 3, round_number(float(sum_credit) * -1), dec_format if is_decimal else num_format)
                    row += 1
                    total_credit += sum_credit
                elif sum_credit > 0:
                    mCountCode += 1
                    worksheet.write(row, col, mAccount.code)
                    worksheet.write(row, col + 1, mAccount.name)
                    worksheet.write(row, col + 2, round_number(sum_credit),
                                    dec_format if is_decimal else num_format)
                    worksheet.write(row, col + 3, None, num_format)
                    row += 1
                    total_debit += sum_credit
                if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                    total_income_credit += sum_credit

            if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                if sum_debit > 0:
                    mCountCode += 1
                    worksheet.write(row, col, mAccount.code)
                    worksheet.write(row, col + 1, mAccount.name)
                    worksheet.write(row, col + 2, round_number(sum_debit),
                                    dec_format if is_decimal else num_format)
                    worksheet.write(row, col + 3, None, num_format)
                    row += 1
                    total_debit += sum_debit
                elif sum_debit < 0:
                    mCountCode += 1
                    worksheet.write(row, col, mAccount.code)
                    worksheet.write(row, col + 1, mAccount.name)
                    worksheet.write(row, col + 2, None, num_format)
                    worksheet.write(row, col + 3, round_number(float(sum_debit)
                                    * -1), dec_format if is_decimal else num_format)
                    row += 1
                    total_credit += sum_debit
                if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                    total_income_debit += sum_debit
        if total_credit < 0:
            total_credit = total_credit * -1
        if total_debit < 0:
            total_debit = total_debit * -1
        worksheet.write(row, col + 1, 'Total : ', right_line)
        worksheet.write(row, col + 2, round_number(total_debit),
                        border_top_bot_dec if is_decimal else border_top_bot_num)
        worksheet.write(row, col + 3, round_number(total_credit),
                        border_top_bot_dec if is_decimal else border_top_bot_num)
        row += 1
        total_income = total_income_debit + total_income_credit
        if total_income >= 0:
            worksheet.write(row, col + 1, 'Net Income (Loss) for Accounts Listed: ', right_line)
            worksheet.write(row, col + 2, round_number(total_income) if total_income else '',
                            border_top_bot_dec if is_decimal else border_top_bot_num)
            row += 1
        else:
            total_income = total_income * -1
            worksheet.write(row, col + 1, 'Net Income (Loss) for Accounts Listed: ', right_line)
            worksheet.write(row, col + 3, round_number(total_income) if total_income else '',
                            border_top_bot_dec if is_decimal else border_top_bot_num)
            row += 1
        worksheet.write(row, col, str(mCountCode) + ' accounts printed ')

    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data


def trial_netChanges(self, company_id, gl_type, issue_from, issue_to, acc_list, is_activity):
    output = self.buffer
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("testSheet")

    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 0, 17)

    right = workbook.add_format({
        'align': 'right'
    })
    right_dec = workbook.add_format({
        'num_format': '#,##0.00',
        'align': 'right'
    })
    right_num = workbook.add_format({
        'num_format': '#,##0',
        'align': 'right'
    })
    center = workbook.add_format({
        'align': 'center'
    })
    worksheet.write(0, 0, 'Account Number', center)
    worksheet.write(0, 1, 'Description', center)
    worksheet.write(0, 2, 'Debit', center)
    worksheet.write(0, 3, 'Credit', center)
    worksheet.write(0, 4, 'Net Changes', center)
    worksheet.write(0, 5, 'Debit', center)
    worksheet.write(0, 6, 'Credit', center)
    worksheet.set_column(0, 6, 20)
    row = 1
    col = 0
    
    array_data = str(issue_from).split('-')
    array_data_to = str(issue_to).split('-')
    if array_data[1] in ['ADJ', 'CLS']:
        issue_from = datetime.date(int(array_data[0]), 12, 1)
    else:
        issue_from = datetime.date(
            int(array_data[0]), int(array_data[1]), 1)
    if array_data_to[1] in ['ADJ', 'CLS']:
        issue_to = datetime.date(int(array_data_to[0]), 12,
                                    calendar.monthrange(int(array_data_to[0]), 12)[1])
    else:
        issue_to = datetime.date(int(array_data_to[0]), int(array_data_to[1]),
                                    calendar.monthrange(int(array_data_to[0]), int(array_data_to[1]))[1])
                                    
    acc_list = eval(acc_list)
    if len(acc_list):
        account_list = Account.objects.filter(id__in=acc_list).order_by('code')
    else:
        account_list = Account.objects.filter(is_hidden=False, company_id=company_id).order_by('code')

    account_item_list = account_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
    account_item_list = account_item_list.exclude(deactivate_period__lte=issue_from).values('id').order_by('code').distinct()

    total_debit = total_credit = total_debit_to = total_credit_to = total_net = sum_net = 0
    sum_debit = sum_credit = 0
    mFinalDebit = mFinalCredit = mFinalDebit_to = mFinalCredit_to = 0
    open_total_income = open_total_income_debit = open_total_income_credit = 0
    end_total_income = end_total_income_debit = end_total_income_credit = 0
    mCode = ''
    mCountCode = 0
    company = Company.objects.get(pk=company_id)
    if company.currency.is_decimal:
        is_decimal = True
        decimal_place = "%.2f"
    else:
        is_decimal = False
        decimal_place = "%.0f"
    if account_item_list:
        for acct in account_item_list:
            mAccount = account_list.filter(id=acct['id']).first()
            item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0, source_currency_id__gt=0,
                                                         account_id=mAccount.id).exclude(source_currency_id__isnull=True)
            if mCode != mAccount.code:
                mCountCode += 1
                mCode = mAccount.code
                sum_debit = []
                sum_credit = []
            get_data(item_account, sum_credit, sum_debit, mAccount.balance_type, array_data[0], array_data[1], 1)
            mFinalDebit = sum_debit[0]
            total_debit += mFinalDebit
            mFinalCredit = sum_credit[0]
            total_credit += mFinalCredit
            sum_debit_to = []
            sum_credit_to = []
            get_data(item_account, sum_credit_to, sum_debit_to, mAccount.balance_type, array_data_to[0],
                     array_data_to[1],
                     2)
            mFinalDebit_to = sum_debit_to[0]
            total_debit_to += mFinalDebit_to
            mFinalCredit_to = sum_credit_to[0]
            total_credit_to += mFinalCredit_to
            total_net_change = []
            get_net(item_account, total_net_change, issue_from, issue_to)
            sum_net = total_net_change[0]
            total_net += sum_net
            a = str(mAccount.code)
            if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                open_credit_balance = ''
                end_credit_balance = ''
                if sum_debit[0] >= 0:
                    open_debit_balance = separator(
                        sum_debit[0], decimal_place).replace("-", "").replace(",", "")
                else:
                    open_debit_balance = str(separator(
                        sum_debit[0], decimal_place).replace("-", "").replace(",", ""))
                if sum_debit_to[0] >= 0:
                    end_debit_balance = separator(
                        sum_debit_to[0], decimal_place).replace("-", "").replace(",", "")
                else:
                    end_debit_balance = str(
                        separator(sum_debit_to[0], decimal_place).replace("-", "").replace(",", ""))

                if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                    open_total_income_debit += sum_debit[0]
                    end_total_income_debit += sum_debit_to[0]
            elif mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                open_debit_balance = ''
                end_debit_balance = ''
                if sum_credit[0] <= 0:
                    open_credit_balance = separator(
                        sum_credit[0], decimal_place).replace("-", "").replace(",", "")
                else:
                    open_credit_balance = str(
                        separator(sum_credit[0], decimal_place).replace("-", "").replace(",", ""))
                if sum_credit_to[0] <= 0:
                    end_credit_balance = separator(
                        sum_credit_to[0], decimal_place).replace("-", "").replace(",", "")
                else:
                    end_credit_balance = str(separator(sum_credit_to[0], decimal_place)).replace(
                        "-", "").replace(",", "")

                if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                    open_total_income_credit += sum_credit[0]
                    end_total_income_credit += sum_credit_to[0]

            worksheet.write(row, col, a)
            worksheet.write(row, col + 1, str(mAccount.name), right)
            worksheet.write(row, col + 2, float(open_debit_balance) if open_debit_balance else 0.00, 
                            right_dec if is_decimal else right_num)
            worksheet.write(row, col + 3, float(open_credit_balance) if open_credit_balance else 0.00,
                            right_dec if is_decimal else right_num)

            worksheet.write(row, col + 4, float(separator(
                total_net_change[0], decimal_place).replace(",", "")) if total_net_change else 0.00, right_dec if is_decimal else right_num)

            worksheet.write(row, col + 5, float(end_debit_balance.replace(",", "")) if end_debit_balance else 0.00,
                            right_dec if is_decimal else right_num)
            worksheet.write(row, col + 6, float(end_credit_balance.replace(",", "")) if end_credit_balance else 0.00,
                            right_dec if is_decimal else right_num)
            sum_debit = sum_credit = 0
            mFinalDebit = mFinalCredit = 0
            row += 1
        worksheet.write(row, col, 'Total: ')
        worksheet.write(row, col + 1, float(separator(total_debit,
                        decimal_place).replace(",", "")),  right_dec if is_decimal else right_num)
        worksheet.write(row, col + 2, float(separator(total_credit,
                        decimal_place).replace(",", "")),  right_dec if is_decimal else right_num)
        worksheet.write(row, col + 3, float(separator(total_net,
                        decimal_place).replace(",", "")),  right_dec if is_decimal else right_num)
        worksheet.write(row, col + 4, float(separator(total_debit_to,
                        decimal_place).replace(",", "")),  right_dec if is_decimal else right_num)
        worksheet.write(row, col + 5, float(separator(total_credit_to,
                        decimal_place).replace(",", "")),  right_dec if is_decimal else right_num)
        row += 1
        open_total_income = open_total_income_debit + open_total_income_credit
        end_total_income = end_total_income_debit + end_total_income_credit
        total_income = end_total_income - open_total_income
        worksheet.write(row, col, 'Net Income (Loss) for Accounts Listed:')
        worksheet.write(row, col + 1, float(separator(total_income, decimal_place).replace(",", ""))
                        if total_income > 0 else 0.00,  right_dec if is_decimal else right_num)
        worksheet.write(row, col + 2, float(separator(total_income, decimal_place).replace(",", ""))
                        if total_income < 0 else 0.00,  right_dec if is_decimal else right_num)
        row += 1
        worksheet.write(row, col, str(mCountCode) + ' accounts printed ', right)

    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data


# column=1:functional_net_change,column=2:functional_net_change
def get_data(item_account, sum_credit, sum_debit, balance_type, year, month, column):
    # get year
    if year:
        item_account = item_account.filter(period_year=int(year))
    if month:
        if month in ['ADJ', 'CLS']:
            item_account = item_account.filter(period_month=month)
        else:
            item_account = item_account.filter(period_month=int(month))
    total_sum_credit = total_sum_debit = 0
    # sum debit,sum credit for open Balanca
    if item_account:
        for j, iAccount in enumerate(item_account):
            if balance_type == BALANCE_TYPE_DICT['Credit']:
                if column == 1:
                    total_sum_credit += iAccount.functional_begin_balance
                else:
                    total_sum_credit += iAccount.functional_end_balance

            if balance_type == BALANCE_TYPE_DICT['Debit']:
                if column == 1:
                    total_sum_debit += iAccount.functional_begin_balance
                else:
                    total_sum_debit += iAccount.functional_end_balance
    sum_credit.append(total_sum_credit)
    sum_debit.append(total_sum_debit)


def get_net(item_account, total_net_change, issue_from, issue_to):
    # get year
    if issue_from:
        item_account = item_account.filter(period_date__gte=issue_from)
    if issue_to:
        item_account = item_account.filter(period_date__lte=issue_to)
    sum = 0
    # sum net change
    if item_account:
        for j, iAccount in enumerate(item_account):
            sum += iAccount.functional_net_change
    total_net_change.append(sum)
    return total_net_change
