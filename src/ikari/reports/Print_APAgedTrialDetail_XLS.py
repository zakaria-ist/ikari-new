import datetime
from decimal import Decimal
import xlsxwriter
from django.utils.dateparse import parse_date
from django.contrib.humanize.templatetags.humanize import intcomma
from companies.models import Company
from accounting.models import Journal
from transactions.models import Transaction
from reports.print_APAgedTrial_Summary import get_exchange_rate
from reports.helpers.aged_trial_report import calculate_total_amount, get_ap_transactions, get_due_period
from accounting.models import DOCUMENT_TYPES
from currencies.models import Currency
from utilities.common import round_number
from utilities.constants import DOCUMENT_TYPES_IN_REPORT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, STATUS_TYPE_DICT


class Print_APAgedTrialDetail_XLS:
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

        center = workbook.add_format({
            'align': 'center',
            'bold': True,
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
            print_amount = '[Vendor Currency]'
        else:
            print_amount = '[Functional Currency]'

        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'A/P Aged Payables by Due Date (APAPAYSY)', merge_format)
        worksheet.merge_range('A5:C5', 'Account Type:   [All Supplier]', merge_format)
        worksheet.merge_range('A6:C6', age_str, merge_format)
        worksheet.merge_range('A7:C7', cutoff_str, merge_format)
        if int(date_type) == 2:
            worksheet.merge_range('A8:C8', 'Print Transaction in   [Detail by Posting Date]', merge_format)
        else:
            worksheet.merge_range('A8:C8', 'Print Transaction in   [Detail by Document Date]', merge_format)
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

        worksheet.write(11, 0, 'Doc.Date', center)
        worksheet.write(12, 0, 'Appl.Date', center_line)
        worksheet.write(11, 1, 'Doc.Type/Doc.Number', center)
        worksheet.write(12, 1, 'Applied No.', center_line)
        worksheet.write(11, 2, 'Due Date', center)
        worksheet.write(12, 2, 'App.Type', center_line)
        worksheet.write(12, 3, 'Current', center_line)
        worksheet.write(11, 4, first_p, center)
        worksheet.write(12, 4, 'Days', center_line)
        worksheet.write(11, 5, second_p, center)
        worksheet.write(12, 5, 'Days', center_line)
        worksheet.write(11, 6, third_p, center)
        worksheet.write(12, 6, 'Days', center_line)
        worksheet.write(11, 7, over_p, center)
        worksheet.write(12, 7, 'Days', center_line)
        worksheet.write(11, 8, 'Total', center)
        worksheet.write(12, 8, 'Overdue', center_line)
        worksheet.write(11, 9, 'Total', center)
        worksheet.write(12, 9, 'Payables', center_line)
        worksheet.set_column(0, 9, 20)

        printing_row = 13
        printing_col = 0
        # process table_data
        journal_type = dict(TRANSACTION_TYPES)['AP Payment']

        ap_collections = get_ap_transactions(
            company_id=company_id,
            cus_no=cus_no,
            cutoff_date=cutoff_date, date_type=date_type,
            paid_full=paid_full, doc_type_array=tuple(doc_type_array)
        )

        journal_item_list = ap_collections.journal_item_list
        journal_amount_list = ap_collections.journal_amount_list
        journal_item_vendor_count = 0

        m_supplier_code = ''
        m_currency = ''
        l_currency = None

        if int(curr_list) == 1:
            simbol_curr = ''
        else:
            curr = Currency.objects.get(pk=company.currency_id)
            simbol_curr = curr.code

        exchange_rate = 1
        sum_amount = 0
        table_money = []
        total_current = total_1st = total_2nd = total_3rd = total_4th = total_over = 0
        sum_cus_current = sum_cus_1st = sum_cus_2nd = sum_cus_3rd = sum_cus_4th = sum_all_cus = sum_over = 0
        v_row_count = 0
        if journal_item_list:
            for i, journal in enumerate(journal_item_list):
                # check to print first row of supplier
                if (m_supplier_code != journal.supplier.code) | (
                        (m_supplier_code == journal.supplier.code) & (m_currency != journal.currency.code)):
                    if i != 0:
                        sum_all_cus = sum_cus_current + sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th
                        sum_over = sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th
                        if int(paid_full) or round_number(sum_all_cus) != 0:
                            if int(curr_list) == 1:
                                is_decimal = l_currency.is_decimal if l_currency else True
                            else:
                                is_decimal = company.currency.is_decimal if company else True
                            # decimal_point = "%.2f"
                            # if not is_decimal:
                            #     decimal_point = "%.0f"
                            worksheet.write(printing_row, printing_col + 1, 'Vendor Total:', border_top_bot)
                            worksheet.write(printing_row, printing_col + 2, simbol_curr if simbol_curr else m_currency, border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, round_number(sum_cus_current)
                                            , border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 4, round_number(sum_cus_1st)
                                            , border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 5, round_number(sum_cus_2nd)
                                            , border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 6, round_number(sum_cus_3rd)
                                            , border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 7, round_number(sum_cus_4th)
                                            , border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 8, round_number(sum_over)
                                            , border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 9, round_number(sum_all_cus)
                                            , border_top_bot_dec)
                            printing_row += 1
                            table_money.append([simbol_curr if simbol_curr else m_currency, sum_cus_current, sum_cus_1st, sum_cus_2nd, sum_cus_3rd, sum_cus_4th])
                            journal_item_vendor_count += 1
                        else:
                            printing_row -= v_row_count
                        
                        v_row_count = 0

                        sum_all_cus = sum_cus_current = sum_cus_1st = sum_cus_2nd = sum_cus_3rd = sum_cus_4th = sum_over = 0

                    m_supplier_code = journal.supplier.code
                    m_currency = journal.currency.code
                    l_currency = journal.currency
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    sum_amount = 0

                    worksheet.write(printing_row, printing_col, 'Vendor No.:')
                    worksheet.write(printing_row, printing_col + 1, journal.supplier.code if journal.supplier_id else '')
                    worksheet.write(printing_row, printing_col + 2, 'Vendor Name.:')
                    worksheet.write(printing_row, printing_col + 3, journal.supplier.name if journal.supplier_id and journal.supplier.name else '')
                    printing_row += 1
                    v_row_count += 1

                if (m_supplier_code == journal.supplier.code) & (m_currency == journal.currency.code):
                    exchange_rate = get_exchange_rate(journal, company, cutoff_date)
                    curr_code = ''
                    day_due = journal.due_date
                    day_age = datetime.datetime.strptime(age_from, '%Y-%m-%d').date()

                    # total_amount = calculate_total_amount(journal, journal_type, cutoff_date)
                    try:
                        key = str(journal.id)
                        total_amount = journal_amount_list[key]
                    except:
                        total_amount = journal.has_outstanding(cutoff_date, True)[1]

                    if int(curr_list) == 1:
                        curr_code = journal.currency.code
                        is_decimal = journal.currency.is_decimal if journal.currency else True
                    else:
                        total_amount = round_number(total_amount * exchange_rate)
                        curr_code = simbol_curr
                        is_decimal = company.currency.is_decimal if company else True
                    sum_amount += total_amount
                    # decimal_point = "%.2f"
                    # if not is_decimal:
                    #     decimal_point = "%.0f"

                    if journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                        if day_due and day_age:
                            if day_age > day_due and journal.document_type not in [DOCUMENT_TYPE_DICT['Credit Note'], DOCUMENT_TYPE_DICT['Debit Note']]:
                                diff_day = (day_age - day_due).days
                                due_period = get_due_period(diff_day=diff_day, period_current=age_period['current'], period_1st=age_period['1st'],
                                                            period_2nd=age_period['2nd'], period_3rd=age_period['3rd'], total=total_amount)
                                total_current += due_period['total_current']
                                total_1st += due_period['total_1st']
                                total_2nd += due_period['total_2nd']
                                total_3rd += due_period['total_3rd']
                                total_4th += due_period['total_4th']
                            else:
                                total_current += total_amount
                        else:
                            total_current += total_amount

                        sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                        total_over = total_1st + total_2nd + total_3rd + total_4th
                        sum_cus_current += total_current
                        sum_cus_1st += total_1st
                        sum_cus_2nd += total_2nd
                        sum_cus_3rd += total_3rd
                        sum_cus_4th += total_4th
                        sum_over += total_over

                    document_type_dict = dict(DOCUMENT_TYPES_IN_REPORT)
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                        if round_number(sum_amount) != 0:
                            doc_typ = document_type_dict.get(journal.document_type) if journal.document_type else ''
                            doc_num = journal.document_number if journal.document_number else ''
                            worksheet.write(printing_row, printing_col, journal.document_date.strftime("%d/%m/%Y") if journal.document_date else '')
                            worksheet.write(printing_row, printing_col + 1, doc_typ + '     ' + doc_num)
                            worksheet.write(printing_row, printing_col + 2, journal.due_date.strftime("%d/%m/%Y") if journal.due_date else '')
                            worksheet.write(printing_row, printing_col + 3, round_number(total_current)
                                                            if Decimal(total_current) else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 4, round_number(total_1st)
                                                            if Decimal(total_1st) else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, round_number(total_2nd)
                                                            if Decimal(total_2nd) else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 6, round_number(total_3rd)
                                                            if Decimal(total_3rd) else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 7, round_number(total_4th)
                                                            if Decimal(total_4th) else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(total_over)
                                                            if Decimal(total_over) else None, dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, round_number(sum_amount)
                                                            if Decimal(sum_amount) else None, dec_format if is_decimal else num_format)
                            printing_row += 1
                            v_row_count += 1
                        if int(paid_full):
                            paid_transactions = Transaction.objects.filter(related_invoice_id=journal.id,
                                                journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
                                            ).exclude(journal_id__isnull=True
                                            ).exclude(related_invoice_id__isnull=True
                                            ).exclude(journal__reverse_reconciliation=True
                                            ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']
                                            ).exclude(is_hidden=True
                                            ).order_by('journal__document_date', '-id')
                        try:
                            for paid_t in paid_transactions:
                                doc_tyyp = document_type_dict.get(paid_t.journal.document_type) if paid_t.journal.document_type else ''
                                doc_nuum = paid_t.journal.document_number if paid_t.journal.document_number else ''
                                worksheet.write(printing_row, printing_col, paid_t.journal.document_date.strftime(
                                    "%d/%m/%Y") if paid_t.journal.document_date else '')
                                worksheet.write(printing_row, printing_col + 1, '        ' + doc_nuum)
                                worksheet.write(printing_row, printing_col + 2, doc_tyyp)
                                worksheet.write(printing_row, printing_col + 3, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(total_current) else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 4, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(total_1st) else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(total_2nd) else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 6, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(total_3rd) else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 7, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(total_4th) else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 8, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(total_over) else None, dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number((-1)*paid_t.total_amount)
                                                                if Decimal(sum_amount) else None, dec_format if is_decimal else num_format)
                                printing_row += 1
                                v_row_count += 1
                            if len(paid_transactions):
                                printing_row += 1
                                v_row_count += 1

                                sum_cus_current -= total_current
                                sum_cus_1st -= total_1st
                                sum_cus_2nd -= total_2nd
                                sum_cus_3rd -= total_3rd
                                sum_cus_4th -= total_4th
                                sum_over -= total_over
                        except:
                            pass
                    else:
                        doc_typ = document_type_dict.get(journal.document_type) if journal.document_type else ''
                        doc_num = journal.document_number if journal.document_number else ''
                        worksheet.write(printing_row, printing_col, journal.document_date.strftime("%d/%m/%Y") if journal.document_date else '')
                        worksheet.write(printing_row, printing_col + 1, doc_typ + '     ' + doc_num)
                        worksheet.write(printing_row, printing_col + 2, journal.due_date.strftime("%d/%m/%Y") if journal.due_date else '')
                        printing_row += 1
                        v_row_count += 1
                    sum_amount = total_current = total_1st = total_2nd = total_3rd = total_4th = total_over = 0
                if i == journal_item_list.__len__() - 1:
                    sum_all_cus = sum_cus_current + sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th
                    sum_over = sum_cus_1st + sum_cus_2nd + sum_cus_3rd + sum_cus_4th

                    if int(paid_full) or round_number(sum_all_cus) != 0:
                        worksheet.write(printing_row, printing_col + 1, 'Vendor Total:', border_top_bot)
                        worksheet.write(printing_row, printing_col + 2, curr_code if curr_code else m_currency, border_top_bot)
                        worksheet.write(printing_row, printing_col + 3, round_number(sum_cus_current)
                                        , border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 4, round_number(sum_cus_1st)
                                        , border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 5, round_number(sum_cus_2nd)
                                        , border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 6, round_number(sum_cus_3rd)
                                        , border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 7, round_number(sum_cus_4th)
                                        , border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_over)
                                        , border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 9, round_number(sum_all_cus)
                                        , border_top_bot_dec)
                        printing_row += 1
                        table_money.append([curr_code if curr_code else m_currency, sum_cus_current, sum_cus_1st, sum_cus_2nd, sum_cus_3rd, sum_cus_4th])
                        journal_item_vendor_count += 1
                    else:
                        printing_row -= v_row_count
                    
                    v_row_count = 0

        if table_money:
            printing_row += 1
            table_money = sorted(table_money, key=lambda code: code[0])
            nline = 0
            sum_over = sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
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
                    sum_over = round_number(sum_1st) + round_number(sum_2nd) + round_number(sum_3rd) + round_number(sum_4th)
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
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_over), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 9, round_number(sum_all), border_top_bot_dec)
                        printing_row += 1
                        if curr_list != '1':
                            worksheet.write(printing_row, printing_col + 3, intcomma(decimal_point %
                                                                                        round_number(sum_current * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 4, intcomma(decimal_point % round_number(sum_1st * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 5, intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 6, intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 7, intcomma(decimal_point % round_number(sum_4th * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 8, intcomma(decimal_point % round_number(sum_over * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 9, intcomma(decimal_point % round_number(sum_all * 100 / sum_all) + '%'), border_top_bot)
                            printing_row += 1

                    else:
                        worksheet.write(printing_row, printing_col + 2, money, border_top_bot)
                        worksheet.write(printing_row, printing_col + 3, round_number(sum_current), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 4, round_number(sum_1st), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 5, round_number(sum_2nd), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 6, round_number(sum_3rd), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 7, round_number(sum_4th), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_over), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 9, round_number(sum_all), border_top_bot_dec)
                        printing_row += 1
                    
                    nline = 1

                    money = table_money[k][0]
                    sum_over = sum_all = sum_current = sum_1st = sum_2nd = sum_3rd = sum_4th = 0
                    sum_current += table_money[k][1]
                    sum_1st += table_money[k][2]
                    sum_2nd += table_money[k][3]
                    sum_3rd += table_money[k][4]
                    sum_4th += table_money[k][5]

                if k == len(table_money) - 1:
                    sum_over = sum_1st + sum_2nd + sum_3rd + sum_4th
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
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_over), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 9, round_number(sum_all), border_top_bot_dec)
                        printing_row += 1
                        if curr_list != '1':
                            worksheet.write(printing_row, printing_col + 3, intcomma(decimal_point %
                                                                                        round_number(sum_current * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 4, intcomma(decimal_point % round_number(sum_1st * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 5, intcomma(decimal_point % round_number(sum_2nd * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 6, intcomma(decimal_point % round_number(sum_3rd * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 7, intcomma(decimal_point % round_number(sum_4th * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 8, intcomma(decimal_point % round_number(sum_over * 100 / sum_all) + '%'), border_top_bot)
                            worksheet.write(printing_row, printing_col + 9, intcomma(decimal_point % round_number(sum_all * 100 / sum_all) + '%'), border_top_bot)
                            printing_row += 1

                    else:
                        worksheet.write(printing_row, printing_col + 2, money, border_top_bot)
                        worksheet.write(printing_row, printing_col + 3, round_number(sum_current), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 4, round_number(sum_1st), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 5, round_number(sum_2nd), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 6, round_number(sum_3rd), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 7, round_number(sum_4th), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 8, round_number(sum_over), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 9, round_number(sum_all), border_top_bot_dec)
                        printing_row += 1

        printing_row += 2
        worksheet.write(printing_row, printing_col, 'CR:Credit Note')
        worksheet.write(printing_row, printing_col + 1, 'DB:Dedit Note')
        worksheet.write(printing_row, printing_col + 2, 'IN:Invoice')
        worksheet.write(printing_row, printing_col + 3, 'IT:Interest Charge')
        worksheet.write(printing_row, printing_col + 4, 'PI:PrePayment')
        worksheet.write(printing_row, printing_col + 5, 'UC:Unapplied Cash')
        worksheet.write(printing_row, printing_col + 6, 'MC:Miscellaneous Receipt')
        worksheet.write(printing_row, printing_col + 7, 'AD:Adjustment')
        worksheet.write(printing_row, printing_col + 8, 'CF:Applied Credit (from)')
        printing_row += 1

        worksheet.write(printing_row, printing_col, 'CT:Applied Credit (to)')
        worksheet.write(printing_row, printing_col + 1, 'DF:Applied Dedit (from)')
        worksheet.write(printing_row, printing_col + 2, 'DT:Applied Dedit (to)')
        worksheet.write(printing_row, printing_col + 3, 'ED:Earned Discount Taken')
        worksheet.write(printing_row, printing_col + 4, 'GL:Gain or Loss (multicurrency ledgers)')
        worksheet.write(printing_row, printing_col + 5, 'PY:Receipt')
        worksheet.write(printing_row, printing_col + 6, 'WO:Write Off')
        worksheet.write(printing_row, printing_col + 7, 'RD:Rounding')
        worksheet.write(printing_row, printing_col + 8, 'RF:Refund')
        printing_row += 1

        printing_row += 1
        worksheet.write(printing_row, printing_col, str(journal_item_vendor_count) + ' vendors printed', border_top_bot)
        printing_row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

