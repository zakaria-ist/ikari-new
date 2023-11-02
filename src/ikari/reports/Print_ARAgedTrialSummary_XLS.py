import datetime
import xlsxwriter
from django.utils.dateparse import parse_date
from django.contrib.humanize.templatetags.humanize import intcomma
from companies.models import Company
from reports.helpers.aged_trial_report import calculate_total_amount, get_ar_transactions, get_due_period
from reports.print_ARAgedTrial_Summary import get_exchange_rate
from accounting.models import DOCUMENT_TYPES
from currencies.models import Currency
from utilities.common import round_number
from utilities.constants import TRANSACTION_TYPES


class Print_ARAgedTrialSummary_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full, periods, appl_detail):
        company = Company.objects.get(pk=company_id)

        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Profit_Loss")

        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'white'})

        right_line = workbook.add_format({
            'align': 'right'
        })

        center_line = workbook.add_format({
            'align': 'center',
            'bottom': 1,
            'bold': True,
        })

        border_top_bot = workbook.add_format({
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

        age_str = "Age Transaction Of As  " + "[" + parse_date(age_from).strftime('%d/%m/%Y') + "]"
        cutoff_str = ''
        if int(date_type) == 2:
            cutoff_str = "CutOff by Posting Date   " + "[" + parse_date(cutoff_date).strftime('%d/%m/%Y') + "]"
        else:
            cutoff_str = "CutOff by Document Date   " + "[" + parse_date(cutoff_date).strftime('%d/%m/%Y') + "]"

        if curr_list == '1':
            print_amount = '[Customer Currency]'
        else:
            print_amount = '[Functional Currency]'

        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'A/R Aged Trial Balance by Due Date (ARTBALSY)', merge_format)
        worksheet.merge_range('A5:C5', 'Account Type:   [All customers]', merge_format)
        worksheet.merge_range('A6:C6', age_str, merge_format)
        worksheet.merge_range('A7:C7', cutoff_str, merge_format)
        worksheet.merge_range('A8:C8', 'Print Transaction in   [Summary]', merge_format)
        worksheet.merge_range('A9:C9', 'Print Amounts in   ' + print_amount, merge_format)

        age_period = {'current': 0, '1st': 31, '2nd': 61, '3rd': 91}
        periods = periods.split(',')
        age_period['current'] = int(periods[0])
        age_period['1st'] = int(periods[1])
        age_period['2nd'] = int(periods[2])
        age_period['3rd'] = int(periods[3])

        doc_select = ''
        doc_type_array = []
        if doc_type:
            passing = doc_type.split(',')
            for code in passing:
                doc_select += dict(DOCUMENT_TYPES)[str(code)] + ', '
                doc_type_array.append(code)
            doc_select = doc_select[:-2]

        first_p = str(age_period['current'] + 1) + ' To ' + str(age_period['1st'])
        second_p = str(age_period['1st'] + 1) + ' To ' + str(age_period['2nd'])
        third_p = str(age_period['2nd'] + 1) + ' To ' + str(age_period['3rd'])
        over_p = 'Over ' + str(age_period['3rd'])

        worksheet.write(11, 0, 'Customer No.', center_line)
        worksheet.write(11, 1, 'Customer Name', center_line)
        worksheet.write(11, 2, 'Cur.', center_line)
        worksheet.write(11, 3, 'Current', center_line)
        worksheet.write(11, 4, first_p + '  Days', center_line)
        worksheet.write(11, 5, second_p + '  Days', center_line)
        worksheet.write(11, 6, third_p + '  Days', center_line)
        worksheet.write(11, 7, over_p + '  Days', center_line)
        worksheet.write(11, 8, 'Total', center_line)
        worksheet.set_column(0, 8, 20)
        worksheet.set_column(1, 1, 30)

        printing_row = 12
        printing_col = 0

        journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
        ar_collections = get_ar_transactions(is_detail_report=True, company_id=company_id, cus_no=cus_no, cutoff_date=cutoff_date,
                                             date_type=date_type, paid_full=paid_full, doc_type_array=doc_type_array)

        journal_item_list = ar_collections.journal_item_list
        adjustment_journal_list = ar_collections.adjustment_journal_list
        journal_amount_list = ar_collections.journal_amount_list
        journal_item_vendor_count = 0

        if int(curr_list) == 1:
            simbol_curr = ''
        else:
            company = Company.objects.get(pk=company_id)
            curr = Currency.objects.get(pk=company.currency_id)
            simbol_curr = curr.code
        m_customer_code = ''
        sum_amount = 0
        total_current = total_1st = total_2nd = total_3rd = total_4th = 0
        table_money = []
        exchange_rate = 1
        if journal_item_list:
            for i, journal in enumerate(journal_item_list):
                if i == 0:
                    m_customer_code = journal.customer.code
                    m_currency = journal.customer.currency.code
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                        m_currency = journal.customer.currency.code

                if (m_customer_code != journal.customer.code) | (
                        (journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']) & (m_customer_code == journal.customer.code) & (m_currency != journal.customer.currency.code)) | (
                        (journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']) & (m_customer_code == journal.customer.code) & (m_currency != journal.currency.code)):
                    m_customer_code = journal.customer.code
                    m_currency = journal.customer.currency.code
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                        m_currency = journal.customer.currency.code
                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                    if int(curr_list) == 1:
                        is_decimal = journal_item_list[i - 1].customer.currency.is_decimal if journal_item_list[i - 1].customer.currency else True
                    else:
                        is_decimal = company.currency.is_decimal if company else True
                    # decimal_point = "%.2f"
                    # if not is_decimal:
                    #     decimal_point = "%.0f"

                    if round_number(sum_amount) != 0:
                        worksheet.write(printing_row, printing_col, journal_item_list[i - 1].customer.code if journal_item_list[i - 1].customer_id else '')
                        worksheet.write(printing_row, printing_col + 1, journal_item_list[i - 1].customer.name if journal_item_list[i - 1].customer_id else '')
                        worksheet.write(printing_row, printing_col + 2, simbol_curr if simbol_curr else journal_item_list[i - 1].customer.currency.code)
                        worksheet.write(printing_row, printing_col + 3, round_number(total_current)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(total_1st)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(total_2nd)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 6, round_number(total_3rd)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 7, round_number(total_4th)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_amount)
                                        , dec_format if is_decimal else num_format)
                        printing_row += 1
                        table_money.append([simbol_curr if simbol_curr else journal_item_list[i - 1].customer.currency.code, total_current, total_1st, total_2nd, total_3rd, total_4th])
                        journal_item_vendor_count += 1

                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    sum_amount = 0
                    total_current = total_1st = total_2nd = total_3rd = total_4th = 0
                if m_customer_code == journal.customer.code:
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    # if str(journal.id) not in adjustment_journal_list.keys():
                    curr_code = ''
                    day_due = journal.due_date
                    day_age = datetime.datetime.strptime(age_from, '%Y-%m-%d').date()

                    # total_amount = calculate_total_amount(journal, journal_type, cutoff_date)
                    try:
                        key = str(journal.id)
                        total_amount = journal_amount_list[key]
                    except:
                        total_amount = journal.has_outstanding(cutoff_date)[1]

                    if int(curr_list) == 1:
                        curr_code = journal.customer.currency.code
                        is_decimal = journal.customer.currency.is_decimal if journal.customer.currency else True
                    else:
                        total_amount = round_number(total_amount * exchange_rate)
                        curr_code = simbol_curr
                        is_decimal = company.currency.is_decimal if company else True
                    # sum_amount += total_amount
                    decimal_point = "%.2f"
                    if not is_decimal:
                        decimal_point = "%.0f"

                    if total_amount != 0:
                        if not day_due:
                            diff_day = (day_age - journal.document_date).days
                        else:
                            diff_day = (day_age - day_due).days
                        due_period = get_due_period(diff_day=diff_day, period_current=age_period['current'], period_1st=age_period['1st'],
                                                    period_2nd=age_period['2nd'], period_3rd=age_period['3rd'], total=total_amount)

                        total_current += due_period['total_current']
                        total_1st += due_period['total_1st']
                        total_2nd += due_period['total_2nd']
                        total_3rd += due_period['total_3rd']
                        total_4th += due_period['total_4th']

                if i == journal_item_list.__len__() - 1:
                    m_customer_code = journal.customer.code
                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                    if int(curr_list) == 1:
                        is_decimal = journal.customer.currency.is_decimal if journal.customer.currency else True
                    else:
                        is_decimal = company.currency.is_decimal if company else True
                    if round_number(sum_amount) != 0:
                        worksheet.write(printing_row, printing_col, journal_item_list[i].customer.code if journal_item_list[i].customer_id else '')
                        worksheet.write(printing_row, printing_col + 1, journal_item_list[i].customer.name if journal_item_list[i].customer_id else '')
                        worksheet.write(printing_row, printing_col + 2, simbol_curr if simbol_curr else journal_item_list[i].customer.currency.code)
                        worksheet.write(printing_row, printing_col + 3, round_number(total_current)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(total_1st)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(total_2nd)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 6, round_number(total_3rd)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 7, round_number(total_4th)
                                        , dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_amount)
                                        , dec_format if is_decimal else num_format)
                        printing_row += 1
                        table_money.append([simbol_curr if simbol_curr else journal_item_list[i].customer.currency.code, total_current, total_1st, total_2nd, total_3rd, total_4th])
                        journal_item_vendor_count += 1

            printing_row += 1

            if table_money:
                table_money = sorted(table_money, key=lambda code: code[0])
                nline = 0
                sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
                for k, j in enumerate(table_money):
                    if k == 0:
                        money = table_money[k][0]
                    if (table_money[k][0] == money):
                        money = table_money[k][0]
                        sum_current += table_money[k][1]
                        sum_1st += table_money[k][2]
                        sum_2nd += table_money[k][3]
                        sum_3rd += table_money[k][4]
                        sum_4th += table_money[k][5]
                    else:
                        sum_all = round_number(sum_current) + round_number(sum_1st) + round_number(sum_2nd) + round_number(sum_3rd) + round_number(sum_4th)
                        try:
                            is_decimal = Currency.objects.get(code=money).is_decimal
                        except:
                            is_decimal = True

                        decimal_point = "%.2f"
                        if not is_decimal:
                            decimal_point = "%.0f"
                        if nline == 0:
                            worksheet.write(printing_row, printing_col + 1, 'Report Total:', border_top_bot)
                            worksheet.write(printing_row, printing_col + 2, money, border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, round_number(sum_current), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 4, round_number(sum_1st), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 5, round_number(sum_2nd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 6, round_number(sum_3rd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 7, round_number(sum_4th), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 8, round_number(sum_all), border_top_bot_dec)
                            printing_row += 1
                            if curr_list != '1':
                                worksheet.write(printing_row, printing_col + 3, intcomma(decimal_point %
                                                                                         round_number(sum_current * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 4, intcomma(decimal_point % round_number(sum_1st * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 5, intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 6, intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 7, intcomma(decimal_point % round_number(sum_4th * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 8, intcomma(decimal_point % round_number(sum_all * 100 / sum_all) + '%'), border_top_bot)
                                printing_row += 1

                        else:
                            worksheet.write(printing_row, printing_col + 2, money, border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, round_number(sum_current), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 4, round_number(sum_1st), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 5, round_number(sum_2nd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 6, round_number(sum_3rd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 7, round_number(sum_4th), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 8, round_number(sum_all), border_top_bot_dec)
                            printing_row += 1
                        
                        nline = 1

                        money = table_money[k][0]
                        sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
                        sum_current += table_money[k][1]
                        sum_1st += table_money[k][2]
                        sum_2nd += table_money[k][3]
                        sum_3rd += table_money[k][4]
                        sum_4th += table_money[k][5]

                    if k == len(table_money) - 1:
                        sum_all = sum_current + sum_1st + sum_2nd + sum_3rd + sum_4th
                        try:
                            is_decimal = Currency.objects.get(code=money).is_decimal
                        except:
                            is_decimal = True
                        decimal_point = "%.2f"
                        if not is_decimal:
                            decimal_point = "%.0f"
                        if nline == 0:
                            worksheet.write(printing_row, printing_col + 1, 'Report Total:', border_top_bot)
                            worksheet.write(printing_row, printing_col + 2, money, border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, round_number(sum_current), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 4, round_number(sum_1st), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 5, round_number(sum_2nd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 6, round_number(sum_3rd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 7, round_number(sum_4th), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 8, round_number(sum_all), border_top_bot_dec)
                            printing_row += 1
                            if curr_list != '1':
                                worksheet.write(printing_row, printing_col + 3, intcomma(decimal_point %
                                                                                         round_number(sum_current * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 4, intcomma(decimal_point % round_number(sum_1st * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 5, intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 6, intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 7, intcomma(decimal_point % round_number(sum_4th * 100 / sum_all) + '%'), border_top_bot)
                                worksheet.write(printing_row, printing_col + 8, intcomma(decimal_point % round_number(sum_all * 100 / sum_all) + '%'), border_top_bot)
                                printing_row += 1

                        else:
                            worksheet.write(printing_row, printing_col + 2, money, border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, round_number(sum_current), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 4, round_number(sum_1st), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 5, round_number(sum_2nd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 6, round_number(sum_3rd), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 7, round_number(sum_4th), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 8, round_number(sum_all), border_top_bot_dec)
                            printing_row += 1

            worksheet.write(printing_row, printing_col, str(journal_item_vendor_count) + ' customer printed')
            printing_row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data


# def check_currency(table_money, code, amount, day):
#     isExit = False
#     for h in table_money:
#         if (table_money[0][2] == code) & (table_money[0][0] == day):
#             table_money[0][1] += amount
#             isExit = True
#             break

#     if not isExit:
#         table_money.append([day, amount, code])
