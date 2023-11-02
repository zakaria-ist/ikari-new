import calendar
import datetime
from dateutil.relativedelta import relativedelta
import xlsxwriter
from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
from accounting.models import Journal
from transactions.models import Transaction
from inventory.models import TransactionCode
from companies.models import Company
from currencies.models import Currency, ExchangeRate
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, TRN_CODE_TYPE_DICT
from utilities.common import round_number, get_decimal_place


class Print_Tax_Auth_XLS:
    def __init__(self, buffer, company_id):
        self.buffer = buffer

        # Get Tax_Report_Running_Number
        tx_rpt_rnum = TransactionCode.objects.filter(is_hidden=0, company_id=company_id,
                                                     code='TX', menu_type=TRN_CODE_TYPE_DICT['Global']).first()
        if not tx_rpt_rnum:
            tx_rpt_rnum = TransactionCode()
            tx_rpt_rnum.code = 'TX'
            tx_rpt_rnum.name = 'Running number for tax tracking report'
            tx_rpt_rnum.company_id = company_id
            tx_rpt_rnum.menu_type = TRN_CODE_TYPE_DICT['Global']
            tx_rpt_rnum.auto_generate = True
            tx_rpt_rnum.is_hidden = False
            tx_rpt_rnum.save()
        tax_running_number = tx_rpt_rnum.last_no + 10
        tx_rpt_rnum.last_no += 10
        tx_rpt_rnum.save()
        self.tx_rpt_code = tx_rpt_rnum.code + str(tax_running_number)

    def WriteToExcel(self, company_id, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority):
        company = Company.objects.get(pk=company_id)

        if issue_from != '0' and issue_to != '0':
            array_from_year = str(issue_from).split('-')
            array_to_year = str(issue_to).split('-')
            issue_from = datetime.date(int(array_from_year[0]), int(array_from_year[1]), 1)
            issue_to = datetime.date(int(array_to_year[0]), int(array_to_year[1]),
                                     calendar.monthrange(int(array_to_year[0]), int(array_to_year[1]))[1])
        else:
            all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0, journal__is_hidden=0,
                                                          journal__batch__batch_type__in=(
                                                              dict(TRANSACTION_TYPES)['AP Invoice'],
                                                              dict(TRANSACTION_TYPES)['AP Payment'],
                                                              dict(TRANSACTION_TYPES)['AR Invoice'],
                                                              dict(TRANSACTION_TYPES)['AR Receipt']),
                                                          journal__transaction_type__in=('0', '', '2'),
                                                          journal__batch__status=int(STATUS_TYPE_DICT['Posted'])
                                                          ).order_by('journal__perd_year', 'journal__perd_month')\
                .select_related('journal', 'journal__batch')
            if not int(is_history):
                all_transactions = all_transactions.filter(is_clear_tax=False)

            from_year = all_transactions.first().journal.perd_year
            from_month = all_transactions.first().journal.perd_month
            to_year = all_transactions.last().journal.perd_year
            to_month = all_transactions.last().journal.perd_month

            issue_from = datetime.date(int(from_year), int(from_month), 1)
            issue_to = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])

        number_of_month = relativedelta(issue_to, issue_from)
        number_of_month = (number_of_month.years * 12) + number_of_month.months
        journal_ids = []
        for month in range(-1, number_of_month):
            current_date = issue_from + relativedelta(months=month + 1)
            curr_year = current_date.year
            current_month = current_date.month
            if print_by == 'Sales':
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id,
                                                                          perd_year=curr_year,
                                                                          perd_month=current_month,
                                                                          batch__batch_type__in=(
                                                                              dict(TRANSACTION_TYPES)['AR Invoice'],
                                                                              dict(TRANSACTION_TYPES)['AR Receipt']),
                                                                          transaction_type__in=('0', '', '2'),
                                                                          batch__status=int(STATUS_TYPE_DICT['Posted'])).order_by('id')\
                                            .exclude(reverse_reconciliation=True)\
                                            .order_by('id').values_list('id', flat=True)
            else:
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id,
                                                                          perd_year=curr_year,
                                                                          perd_month=current_month,
                                                                          batch__batch_type__in=(
                                                                              dict(TRANSACTION_TYPES)['AP Invoice'],
                                                                              dict(TRANSACTION_TYPES)['AP Payment']),
                                                                          transaction_type__in=('0', '', '2'),
                                                                          batch__status=int(STATUS_TYPE_DICT['Posted'])).order_by('id')\
                                            .exclude(reverse_reconciliation=True)\
                                            .order_by('id').values_list('id', flat=True)
            journal_ids = journal_ids + list(journals)

        if print_type == 'Functional Currency':
            print_type = 'Functional'
        elif print_type == 'Source Currency':
            print_type = 'Source'
        elif print_type == 'Tax Reporting Currency':
            print_type = 'Tax Reporting'
        else:
            print_type = ''

        if report_by == 'Fiscal Period':
            if print_by == 'Sales':
                return self.FiscalPeriodSales(company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority)
            else:
                return self.FiscalPeriodPurchase(company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority)
        else:
            if print_by == 'Sales':
                return self.DocumentDateSales(company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority)
            else:
                return self.DocumentDatePurchase(company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority)

    def FiscalPeriodSales(self, company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority):
        company_id = company.id
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Tax Report")

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
            'align': 'center',
            'bottom': 1,
            'bold': True,
        })
        center_bold = workbook.add_format({
            'align': 'center',
            'bold': True,
        })

        border_top_bot = workbook.add_format({
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

        auth_str = ':   [ ' + tax_authority + ' ] to [ ' + tax_authority + ' ]'
        worksheet.merge_range('C3:E3', company.name, merge_format)
        worksheet.merge_range('C4:E4', print_by + " " + transaction_type + " Tracking (" + self.tx_rpt_code + ")", merge_format)
        worksheet.merge_range('C5:D5', 'From Tax Authority', merge_format)
        worksheet.write(4, 4, auth_str, merge_format)
        worksheet.merge_range('C6:D6', "Print Amounts in", merge_format)
        worksheet.write(5, 4, ":  " + "[" + print_type + "]", merge_format)
        worksheet.merge_range('C7:D7', "Report by", merge_format)
        worksheet.write(6, 4, ":   " + "[" + report_by + "]", merge_format)
        worksheet.merge_range('C8:D8', "As of Fiscal Year", merge_format)
        worksheet.write(7, 4, ":   " + "[" + str(issue_from.month) + '-' + str(issue_from.year) +
                              "] TO [" + str(issue_to.month) + '-' + str(issue_to.year) + "]", merge_format)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            com_curr = ''
            str_tax_reporting = ''
            # decimal_place_f = get_decimal_place(company.currency)
            # decimal_place = "%.2f"
            is_decimal_f = company.currency.is_decimal
            is_decimal = True

            # Header
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Document Date', center_line)
            worksheet.write(11, 2, 'Source code', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Invoice Amount', center_line)
            if print_type == 'Tax Reporting':
                worksheet.write(11, 5, 'Currency', center_line)
                worksheet.write(11, 6, 'Tax Base', center_line)
                worksheet.write(11, 7, 'Tax Amount', center_line)

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"
            else:
                worksheet.write(11, 5, 'Tax Base', center_line)
                worksheet.write(11, 6, 'Tax Amount', center_line)
                worksheet.merge_range('E10:G10', print_type, center_bold)

            worksheet.set_column(0, 7, 18)

            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Tax Reporting':
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('customer_id').select_related('currency')
            else:
                all_journals = Journal.objects.filter(id__in=journal_ids).order_by('currency_id').select_related('currency')

            journal_doc_dates = all_journals.values('perd_month', 'perd_year').order_by('perd_year', 'perd_month').distinct()
            periods = []
            periods_count = 0
            last_period = None
            for doc_date in journal_doc_dates:
                period_str = str(doc_date.get('perd_year')) + '-' + str(doc_date.get('perd_month'))
                if period_str != last_period:
                    periods.append(period_str)
                    periods_count += 1
                    last_period = period_str

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id,
                                'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0,
                                'summary2': 0,
                                'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id

            period_counter = 0
            summary_total_amount = summary_tax_base = summary_tax_amount = 0
            func_summary1 = func_summary2 = func_summary3 = 0
            for period in periods:
                period_counter += 1
                worksheet.write(printing_row, printing_col, 'Year-Period')
                worksheet.write(printing_row, printing_col + 1, ': ' + period)
                printing_row += 2
                year = period.split('-')[0]
                month = period.split('-')[1]
                func_subtotal1 = func_subtotal2 = func_subtotal3 = 0
                if print_type == 'Source' or print_type == 'Functional':
                    for currency in currencies:
                        subtotal1 = subtotal2 = subtotal3 = 0
                        currency_printed = False

                        if print_type == 'Source':
                            worksheet.write(printing_row, printing_col, 'Source Currency')
                            worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                            printing_row += 1

                        journal_by_curr = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)
                        all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                    journal__in=journal_by_curr
                                                                    ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                            .select_related('journal', 'journal__customer')\
                            .exclude(tax_id__isnull=True)
                        if not int(is_history):
                            all_transactions = all_transactions.filter(is_clear_tax=False)
                        last_journal_id = 0
                        index = 0
                        for trx in all_transactions:
                            currency_printed = True
                            if index == 0:
                                last_journal_id = trx.journal.id
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AR-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AR-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AR-CR'
                                else:
                                    source_code = 'AR-PY'
                                try:
                                    column1 = trx.journal.customer.code
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = trx.journal.name[:15]
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                                if print_type == 'Functional':
                                    total_amount = trx.journal.total_amount * trx.exchange_rate
                                    tax_base = trx.base_tax_amount * trx.exchange_rate
                                    tax_amount = trx.tax_amount * trx.exchange_rate
                                else:
                                    total_amount = trx.journal.total_amount
                                    tax_base = trx.base_tax_amount
                                    tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # subtotal1 += round_number(total_amount)
                                # subtotal2 += round_number(tax_base)
                                # subtotal3 += round_number(tax_amount)
                                # func_subtotal1 += round_number(total_amount)
                                # func_subtotal2 += round_number(tax_base)
                                # func_subtotal3 += round_number(tax_amount)

                            if last_journal_id != trx.journal.id:
                                if print_type == 'Functional':
                                    # decimal_place = decimal_place_f
                                    is_decimal = is_decimal_f
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, source_code)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                subtotal1 += round_number(total_amount)
                                subtotal2 += round_number(tax_base)
                                subtotal3 += round_number(tax_amount)
                                func_subtotal1 += round_number(total_amount)
                                func_subtotal2 += round_number(tax_base)
                                func_subtotal3 += round_number(tax_amount)

                                last_journal_id = trx.journal.id
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AR-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AR-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AR-CR'
                                else:
                                    source_code = 'AR-PY'
                                try:
                                    column1 = trx.journal.customer.code
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = trx.journal.name[:15]
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                                if print_type == 'Functional':
                                    total_amount = trx.journal.total_amount * trx.exchange_rate
                                    tax_base = trx.base_tax_amount * trx.exchange_rate
                                    tax_amount = trx.tax_amount * trx.exchange_rate
                                else:
                                    total_amount = trx.journal.total_amount
                                    tax_base = trx.base_tax_amount
                                    tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # subtotal1 += round_number(total_amount)
                                # subtotal2 += round_number(tax_base)
                                # subtotal3 += round_number(tax_amount)
                                # func_subtotal1 += round_number(total_amount)
                                # func_subtotal2 += round_number(tax_base)
                                # func_subtotal3 += round_number(tax_amount)
                            elif index > 0:
                                last_journal_id = trx.journal.id
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    if print_type == 'Functional':
                                        tax_base += trx.base_tax_amount * trx.exchange_rate * -1
                                        tax_amount += trx.tax_amount * trx.exchange_rate * -1
                                    else:
                                        tax_base += trx.base_tax_amount * -1
                                        tax_amount += trx.tax_amount * -1
                                else:
                                    if print_type == 'Functional':
                                        tax_base += trx.base_tax_amount * trx.exchange_rate
                                        tax_amount += trx.tax_amount * trx.exchange_rate
                                    else:
                                        tax_base += trx.base_tax_amount
                                        tax_amount += trx.tax_amount

                                # subtotal2 += round_number(trx.base_tax_amount)
                                # subtotal3 += round_number(trx.tax_amount)
                                # func_subtotal2 += round_number(trx.base_tax_amount)
                                # func_subtotal3 += round_number(trx.tax_amount)
                            index += 1

                        currency['summary1'] += subtotal1
                        currency['summary2'] += subtotal2
                        currency['summary3'] += subtotal3

                        if currency_printed:
                            if index != 0:
                                subtotal1 += round_number(total_amount)
                                subtotal2 += round_number(tax_base)
                                subtotal3 += round_number(tax_amount)
                                func_subtotal1 += round_number(total_amount)
                                func_subtotal2 += round_number(tax_base)
                                func_subtotal3 += round_number(tax_amount)
                                currency['summary1'] += round_number(total_amount)
                                currency['summary2'] += round_number(tax_base)
                                currency['summary3'] += round_number(tax_amount)
                                if print_type == 'Functional':
                                    # decimal_place = decimal_place_f
                                    is_decimal - is_decimal_f
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, source_code)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1
                            if print_type == 'Source':
                                worksheet.write(printing_row, printing_col + 2, 'Fiscal ' + period, border_top_bot)
                                worksheet.write(printing_row, printing_col + 3, ' Total ' + currency['code'] + ' :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    subtotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col + 2, 'Fiscal ' + period, border_top_bot)
                        worksheet.write(printing_row, printing_col + 3, ' Total:', border_top_bot)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            func_subtotal1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            func_subtotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            func_subtotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1

                        func_summary1 += func_subtotal1
                        func_summary2 += func_subtotal2
                        func_summary3 += func_subtotal3
                else:
                    subtotal1 = subtotal2 = subtotal3 = 0
                    journal_by_period = all_journals.filter(perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_period
                                                                ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                        .select_related('journal', 'journal__customer')\
                        .exclude(tax_id__isnull=True)

                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    for trx in all_transactions:
                        if index == 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, currency_code)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_base), dec_format)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                tax_amount), dec_format)
                            printing_row += 1

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal=trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)

                        elif index > 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            t_base = 0
                            t_amount = 0
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            elif com_curr != currency_code:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = (trx.tax_amount * trx.exchange_rate)
                            else:
                                t_base = trx.base_tax_amount
                                t_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                t_base = -1 * t_base
                                t_amount = -1 * t_amount

                            tax_base += t_base
                            tax_amount += t_amount
                            # subtotal2 += round_number(t_base)
                            # subtotal3 += round_number(t_amount)
                        index += 1

                    if index != 0:
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, source_code)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total_amount), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, currency_code)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            tax_base), dec_format)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            tax_amount), dec_format)
                        printing_row += 1

                        subtotal1 += round_number(total_amount)
                        subtotal2 += round_number(tax_base)
                        subtotal3 += round_number(tax_amount)

                    worksheet.write(printing_row, printing_col + 4, 'Fiscal ' + period, border_top_bot)
                    worksheet.write(printing_row, printing_col + 5, ' Total:', border_top_bot)
                    worksheet.write(printing_row, printing_col + 6, round_number(
                        subtotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 7, round_number(
                        subtotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    printing_row += 1

                    summary_total_amount += subtotal1
                    summary_tax_base += subtotal2
                    summary_tax_amount += subtotal3

            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 2, company.currency.code, border_top_bot)
                worksheet.write(printing_row, printing_col + 3, ' Total:', border_top_bot)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    func_summary1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 5, round_number(
                    func_summary2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 6, round_number(
                    func_summary3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1

            if period_counter == periods_count:
                printing_row += 5
                m_range = 'A' + str(printing_row) + ':' + 'D' + str(printing_row)
                worksheet.merge_range(m_range, 'Summary By Tax Authority', merge_format)
                printing_row += 2

                if print_type == 'Source':
                    worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                    worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                    worksheet.write(printing_row, printing_col + 2, 'Invoice Amount', center_line)
                    worksheet.write(printing_row, printing_col + 3, 'Tax Base', center_line)
                    worksheet.write(printing_row, printing_col + 4, 'Tax Amount', center_line)
                    printing_row += 1
                elif print_type == 'Tax Reporting':
                    worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                    worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                    worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                    worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                    printing_row += 1
                else:
                    worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                    worksheet.write(printing_row, printing_col + 1, 'Invoice Amount', center_line)
                    worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                    worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                    printing_row += 1

                total_tax_base = total_tax_amu = tot_inv = 0
                if print_type == 'Source':
                    for curr in currencies:
                        curr_code = curr['code']
                        try:
                            cur = Currency.objects.get(code=curr['code'])
                            # decimal_place = get_decimal_place(cur)
                            is_decimal = cur.is_decimal
                        except:
                            # decimal_place = "%.2f"
                            is_decimal = True
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, curr_code)
                        worksheet.write(printing_row, printing_col + 2, round_number(
                            curr['summary1']), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 3, round_number(
                            curr['summary2']), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            curr['summary3']), dec_format if is_decimal else num_format)
                        printing_row += 1
                elif print_type == 'Tax Reporting':
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, "SGD")
                    worksheet.write(printing_row, printing_col + 2, round_number(
                        summary_tax_base), dec_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        summary_tax_amount), dec_format)
                    printing_row += 1
                else:
                    for curr in currencies:
                        tot_inv += curr['summary1']
                        total_tax_base += curr['summary2']
                        total_tax_amu += curr['summary3']

                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, round_number(
                        tot_inv), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 2, round_number(
                        total_tax_base), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        total_tax_amu), dec_format if is_decimal_f else num_format)
                    printing_row += 2
                    worksheet.write(printing_row, printing_col + 1, 'Report Total :', right_line)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        total_tax_amu), dec_format if is_decimal_f else num_format)
                    printing_row += 1

                printing_row += 2
                worksheet.write(printing_row, printing_col, '1 authority printed')

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def FiscalPeriodPurchase(self, company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority):
        company_id = company.id
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Tax Report")

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
            'align': 'center',
            'bottom': 1,
            'bold': True,
        })
        center_bold = workbook.add_format({
            'align': 'center',
            'bold': True,
        })

        border_top_bot = workbook.add_format({
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

        auth_str = ':   [ ' + tax_authority + ' ] to [ ' + tax_authority + ' ]'
        worksheet.merge_range('C3:E3', company.name, merge_format)
        worksheet.merge_range('C4:E4', print_by + " " + transaction_type + " Tracking (" + self.tx_rpt_code + ")", merge_format)
        worksheet.merge_range('C5:D5', 'From Tax Authority', merge_format)
        worksheet.write(4, 4, auth_str, merge_format)
        worksheet.merge_range('C6:D6', "Print Amounts in", merge_format)
        worksheet.write(5, 4, ":  " + "[" + print_type + "]", merge_format)
        worksheet.merge_range('C7:D7', "Report by", merge_format)
        worksheet.write(6, 4, ":   " + "[" + report_by + "]", merge_format)
        worksheet.merge_range('C8:D8', "As of Fiscal Year", merge_format)
        worksheet.write(7, 4, ":   " + "[" + str(issue_from.month) + '-' + str(issue_from.year) +
                              "] TO [" + str(issue_to.month) + '-' + str(issue_to.year) + "]", merge_format)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            com_curr = ''
            str_tax_reporting = ''
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            is_decimal_f = company.currency.is_decimal
            is_decimal = True

            # Header
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Document Date', center_line)
            worksheet.write(11, 2, 'Source code', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Invoice Amount', center_line)
            if print_type == 'Tax Reporting':
                worksheet.write(11, 5, 'Currency', center_line)
                worksheet.write(11, 6, 'Tax Base', center_line)
                worksheet.write(11, 7, 'Tax Amount', center_line)
                worksheet.write(11, 8, 'Recoverable Tax', center_line)
                worksheet.write(11, 9, 'Recoverable Rate', center_line)
                worksheet.write(11, 10, 'Expense Separately', center_line)
                worksheet.merge_range('E10:F10', 'Source', center_bold)
                worksheet.merge_range('G10:I10', print_type, center_bold)

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"
            else:
                worksheet.write(11, 5, 'Tax Base', center_line)
                worksheet.write(11, 6, 'Tax Amount', center_line)
                worksheet.write(11, 7, 'Recoverable Tax', center_line)
                worksheet.write(11, 8, 'Recoverable Rate', center_line)
                worksheet.write(11, 9, 'Expense Separately', center_line)
                worksheet.merge_range('E10:G10', print_type, center_bold)

            worksheet.set_column(0, 10, 18)

            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id')
            journal_doc_dates = all_journals.values('perd_month', 'perd_year').order_by('perd_year', 'perd_month').distinct()
            periods = []
            periods_count = 0
            last_period = None
            for doc_date in journal_doc_dates:
                period_str = str(doc_date.get('perd_year')) + '-' + str(doc_date.get('perd_month'))
                if period_str != last_period:
                    periods.append(period_str)
                    periods_count += 1
                    last_period = period_str

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id,
                                'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id

            period_counter = 0
            grand_total1 = grand_total2 = grand_total3 = 0
            for period in periods:
                period_counter += 1
                worksheet.write(printing_row, printing_col, 'Year-Period')
                worksheet.write(printing_row, printing_col + 1, ': ' + period)
                printing_row += 2

                year = period.split('-')[0]
                month = period.split('-')[1]
                period_total1 = period_total2 = period_total3 = 0
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = 0
                    currency_printed = False
                    if print_type == 'Source' or print_type == 'Functional':
                        if print_type == 'Source':
                            worksheet.write(printing_row, printing_col, 'Source Currency')
                            worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                            printing_row += 1

                    journals = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journals
                                                                ).order_by('journal__supplier_id', 'journal__document_date', 'journal_id')\
                        .select_related('journal', 'journal__supplier', 'tax')\
                        .exclude(tax_id__isnull=True)

                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    for trx in all_transactions:
                        currency_printed = True
                        if index == 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'

                            is_expense_separately = 'No'
                            recoverable_rate = 0.00
                            if trx.tax:
                                if trx.tax.tax_authority:
                                    recoverable_rate = trx.tax.tax_authority.recoverable_rate
                                    if trx.tax.tax_authority.is_expense_separately:
                                        is_expense_separately = 'Yes'
                            try:
                                column1 = trx.journal.supplier.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')
                            if print_type == 'Source':
                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                            elif print_type == 'Functional':
                                total_amount = (trx.journal.total_amount * trx.exchange_rate)
                                tax_base = (trx.base_tax_amount * trx.exchange_rate)
                                tax_amount = (trx.tax_amount * trx.exchange_rate)
                            else:
                                total_amount = trx.journal.total_amount
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    tax_base = (trx.base_tax_amount * exchange_rate)
                                    tax_amount = (trx.tax_amount * exchange_rate)
                                elif trx.journal.currency_id != to_currency:
                                    if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                        exchange_rate = trx.journal.tax_exchange_rate
                                    else:
                                        try:
                                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                        from_currency_id=from_currency,
                                                                                        to_currency_id=to_currency,
                                                                                        exchange_date__lte=trx.journal.document_date,
                                                                                        flag='ACCOUNTING').order_by('exchange_date').last().rate
                                        except:
                                            exchange_rate = Decimal('1.00000000')
                                    tax_base = (trx.base_tax_amount * exchange_rate)
                                    tax_amount = (trx.tax_amount * exchange_rate)
                                else:
                                    tax_base = (trx.base_tax_amount * trx.exchange_rate)
                                    tax_amount = (trx.tax_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # period_total1 += round_number(total_amount)
                            # period_total2 += round_number(tax_base)
                            # period_total3 += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            if print_type == 'Tax Reporting':
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, source_code)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, trx.journal.currency.code, right_line)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    tax_base), dec_format)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    tax_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    tax_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 9, str(intcomma(decimal_place_f %
                                                                                            recoverable_rate)) + '%' if tax_amount else '', right_line)
                                worksheet.write(printing_row, printing_col + 10, str(is_expense_separately), right_line)
                                printing_row += 1
                            else:
                                if print_type == 'Functional':
                                    # decimal_place = decimal_place_f
                                    is_decimal - is_decimal_f
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, source_code)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 8, str(intcomma(decimal_place %
                                                                                            recoverable_rate)) + '%' if tax_amount else '', right_line)
                                worksheet.write(printing_row, printing_col + 9, str(is_expense_separately), right_line)
                                printing_row += 1

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            period_total1 += round_number(total_amount)
                            period_total2 += round_number(tax_base)
                            period_total3 += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'

                            is_expense_separately = 'No'
                            recoverable_rate = 0.00
                            if trx.tax:
                                if trx.tax.tax_authority:
                                    recoverable_rate = trx.tax.tax_authority.recoverable_rate
                                    if trx.tax.tax_authority.is_expense_separately:
                                        is_expense_separately = 'Yes'
                            try:
                                column1 = trx.journal.supplier.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')
                            if print_type == 'Source':
                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                            elif print_type == 'Functional':
                                total_amount = (trx.journal.total_amount * trx.exchange_rate)
                                tax_base = (trx.base_tax_amount * trx.exchange_rate)
                                tax_amount = (trx.tax_amount * trx.exchange_rate)
                            else:
                                total_amount = trx.journal.total_amount
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    tax_base = (trx.base_tax_amount * exchange_rate)
                                    tax_amount = (trx.tax_amount * exchange_rate)
                                elif trx.journal.currency_id != to_currency:
                                    if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                        exchange_rate = trx.journal.tax_exchange_rate
                                    else:
                                        try:
                                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                        from_currency_id=from_currency,
                                                                                        to_currency_id=to_currency,
                                                                                        exchange_date__lte=trx.journal.document_date,
                                                                                        flag='ACCOUNTING').order_by('exchange_date').last().rate
                                        except:
                                            exchange_rate = Decimal('1.00000000')
                                    tax_base = (trx.base_tax_amount * exchange_rate)
                                    tax_amount = (trx.tax_amount * exchange_rate)
                                else:
                                    tax_base = (trx.base_tax_amount * trx.exchange_rate)
                                    tax_amount = (trx.tax_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # period_total1 += round_number(total_amount)
                            # period_total2 += round_number(tax_base)
                            # period_total3 += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                if print_type == 'Source':
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                    # subtotal2 += round_number(trx.base_tax_amount * -1)
                                    # subtotal3 += round_number(trx.tax_amount * -1)
                                    # period_total2 += round_number(trx.base_tax_amount * -1)
                                    # period_total3 += round_number(trx.tax_amount * -1)
                                elif print_type == 'Tax Reporting':
                                    from_currency = trx.currency_id
                                    to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                    if trx.journal.currency_id == to_currency:
                                        exchange_rate = Decimal('1.00000000')
                                        tax_base += (trx.base_tax_amount * exchange_rate * -1)
                                        tax_amount += (trx.tax_amount * exchange_rate * -1)
                                    elif trx.journal.currency_id != to_currency:
                                        if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                            exchange_rate = trx.journal.tax_exchange_rate
                                        else:
                                            try:
                                                exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                            from_currency_id=from_currency,
                                                                                            to_currency_id=to_currency,
                                                                                            exchange_date__lte=trx.journal.document_date,
                                                                                            flag='ACCOUNTING').order_by('exchange_date').last().rate
                                            except:
                                                exchange_rate = Decimal('1.00000000')
                                        tax_base += (trx.base_tax_amount * exchange_rate * -1)
                                        tax_amount += (trx.tax_amount * exchange_rate * -1)
                                        # subtotal2 += round_number(trx.base_tax_amount * exchange_rate * -1)
                                        # subtotal3 += round_number(trx.tax_amount * exchange_rate * -1)
                                        # period_total2 += round_number(trx.base_tax_amount * exchange_rate * -1)
                                        # period_total3 += round_number(trx.tax_amount * exchange_rate * -1)
                                    else:
                                        tax_base += (trx.base_tax_amount * trx.exchange_rate * -1)
                                        tax_amount += (trx.tax_amount * trx.exchange_rate * -1)
                                        # subtotal2 += round_number(trx.base_tax_amount * trx.exchange_rate * -1)
                                        # subtotal3 += round_number(trx.tax_amount * trx.exchange_rate * -1)
                                        # period_total2 += round_number(trx.base_tax_amount * trx.exchange_rate * -1)
                                        # period_total3 += round_number(trx.tax_amount * trx.exchange_rate * -1)
                                else:
                                    tax_base += (trx.base_tax_amount * trx.exchange_rate * -1)
                                    tax_amount += (trx.tax_amount * trx.exchange_rate * -1)
                                    # subtotal2 += round_number(trx.base_tax_amount * trx.exchange_rate * -1)
                                    # subtotal3 += round_number(trx.tax_amount * trx.exchange_rate * -1)
                                    # period_total2 += round_number(trx.base_tax_amount * trx.exchange_rate * -1)
                                    # period_total3 += round_number(trx.tax_amount * trx.exchange_rate * -1)
                            else:
                                if print_type == 'Source':
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                    # subtotal2 += round_number(trx.base_tax_amount)
                                    # subtotal3 += round_number(trx.tax_amount)
                                    # period_total2 += round_number(trx.base_tax_amount)
                                    # period_total3 += round_number(trx.tax_amount)
                                elif print_type == 'Tax Reporting':
                                    from_currency = trx.currency_id
                                    to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                    if trx.journal.currency_id == to_currency:
                                        exchange_rate = Decimal('1.00000000')
                                        tax_base += (trx.base_tax_amount * exchange_rate)
                                        tax_amount += (trx.tax_amount * exchange_rate)
                                    elif trx.journal.currency_id != to_currency:
                                        if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                            exchange_rate = trx.journal.tax_exchange_rate
                                        else:
                                            try:
                                                exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                            from_currency_id=from_currency,
                                                                                            to_currency_id=to_currency,
                                                                                            exchange_date__lte=trx.journal.document_date,
                                                                                            flag='ACCOUNTING').order_by('exchange_date').last().rate
                                            except:
                                                exchange_rate = Decimal('1.00000000')

                                        tax_base += (trx.base_tax_amount * exchange_rate)
                                        tax_amount += (trx.tax_amount * exchange_rate)
                                        # subtotal2 += round_number(trx.base_tax_amount * exchange_rate)
                                        # subtotal3 += round_number(trx.tax_amount * exchange_rate)
                                        # period_total2 += round_number(trx.base_tax_amount * exchange_rate)
                                        # period_total3 += round_number(trx.tax_amount * exchange_rate)
                                    else:
                                        tax_base += (trx.base_tax_amount * trx.exchange_rate)
                                        tax_amount += (trx.tax_amount * trx.exchange_rate)
                                        # subtotal2 += round_number(trx.base_tax_amount * trx.exchange_rate)
                                        # subtotal3 += round_number(trx.tax_amount * trx.exchange_rate)
                                        # period_total2 += round_number(trx.base_tax_amount * trx.exchange_rate)
                                        # period_total3 += round_number(trx.tax_amount * trx.exchange_rate)
                                else:
                                    tax_base += (trx.base_tax_amount * trx.exchange_rate)
                                    tax_amount += (trx.tax_amount * trx.exchange_rate)
                                    # subtotal2 += round_number(trx.base_tax_amount * trx.exchange_rate)
                                    # subtotal3 += round_number(trx.tax_amount * trx.exchange_rate)
                                    # period_total2 += round_number(trx.base_tax_amount * trx.exchange_rate)
                                    # period_total3 += round_number(trx.tax_amount * trx.exchange_rate)
                        index += 1

                    currency['summary1'] += subtotal1
                    currency['summary2'] += subtotal2
                    currency['summary3'] += subtotal3

                    if currency_printed:
                        if index != 0:
                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            period_total1 += round_number(total_amount)
                            period_total2 += round_number(tax_base)
                            period_total3 += round_number(tax_amount)
                            currency['summary1'] += round_number(total_amount)
                            currency['summary2'] += round_number(tax_base)
                            currency['summary3'] += round_number(tax_amount)
                            
                            if print_type == 'Tax Reporting':
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, source_code)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, trx.journal.currency.code, right_line)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    tax_base), dec_format)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    tax_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    tax_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 9, str(intcomma(decimal_place_f %
                                                                                            recoverable_rate)) + '%' if tax_amount else '', right_line)
                                worksheet.write(printing_row, printing_col + 10, str(is_expense_separately), right_line)
                                printing_row += 1
                            else:
                                if print_type == 'Functional':
                                    decimal_place = decimal_place_f
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, source_code)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 8, str(intcomma(decimal_place %
                                                                                            recoverable_rate)) + '%' if tax_amount else '', right_line)
                                worksheet.write(printing_row, printing_col + 9, str(is_expense_separately), right_line)
                                printing_row += 1

                        if print_type == 'Source':
                            worksheet.write(printing_row, printing_col + 2, 'Fiscal ' + period, border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, ' Total ' + currency['code'] + ' :', border_top_bot)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                subtotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1
                if print_type == 'Functional':
                    worksheet.write(printing_row, printing_col + 3, 'Fiscal ' + period + ' Total:', border_top_bot)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        period_total1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        period_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 6, round_number(
                        period_total3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 7, round_number(
                        period_total3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    printing_row += 1

                    grand_total1 += period_total1
                    grand_total2 += period_total2
                    grand_total3 += period_total3
                elif print_type == 'Tax Reporting':
                    worksheet.write(printing_row, printing_col + 5, 'Fiscal ' + period + ' Total:', border_top_bot)
                    worksheet.write(printing_row, printing_col + 6, round_number(
                        period_total2), border_top_bot_dec)
                    worksheet.write(printing_row, printing_col + 7, round_number(
                        period_total3), border_top_bot_dec)
                    worksheet.write(printing_row, printing_col + 8, round_number(
                        period_total3), border_top_bot_dec)
                    printing_row += 1

                    grand_total1 += period_total1
                    grand_total2 += period_total2
                    grand_total3 += period_total3
            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 3, 'GSTDOS Total:', border_top_bot)
                worksheet.write(printing_row, printing_col + 4, round_number(grand_total1),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 5, round_number(grand_total2),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 6, round_number(grand_total3),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 7, round_number(grand_total3),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col + 5, 'GSTDOS Total:', border_top_bot)
                worksheet.write(printing_row, printing_col + 6, round_number(grand_total2),
                                border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 7, round_number(grand_total3),
                                border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 8, round_number(grand_total3),
                                border_top_bot_dec)
                printing_row += 1

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'D' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Invoice Amount', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Amount', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Recoverable Tax', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Recoverable Tax', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Invoice Amount', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Recoverable Tax', center_line)
                printing_row += 1

            total_tax_base = total_tax_amu = tot_inv = 0
            if print_type == 'Source':
                for curr in currencies:
                    curr_code = curr['code']
                    try:
                        cur = Currency.objects.get(code=curr['code'])
                        # decimal_place = get_decimal_place(cur)
                        is_decimal = cur.is_decimal
                    except:
                        # decimal_place = "%.2f"
                        is_decimal = True
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, curr_code)
                    worksheet.write(printing_row, printing_col + 2, round_number(
                        curr['summary1']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        curr['summary2']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        curr['summary3']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        curr['summary3']), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                for curr in currencies:
                    total_tax_base += curr['summary2']
                    total_tax_amu += curr['summary3']
                worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                worksheet.write(printing_row, printing_col + 1, "SGD")
                worksheet.write(printing_row, printing_col + 2, round_number(
                    total_tax_base), dec_format)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    total_tax_amu), dec_format)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    total_tax_amu), dec_format)
                printing_row += 1
            else:
                for curr in currencies:
                    tot_inv += curr['summary1']
                    total_tax_base += curr['summary2']
                    total_tax_amu += curr['summary3']
                worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                worksheet.write(printing_row, printing_col + 1,
                                round_number(tot_inv), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 2, round_number(
                    total_tax_base), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    total_tax_amu), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    total_tax_amu), dec_format if is_decimal_f else num_format)
                printing_row += 2
                worksheet.write(printing_row, printing_col + 1, 'Report Total :', right_line)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    total_tax_amu), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    total_tax_amu), dec_format if is_decimal_f else num_format)
                printing_row += 1

            printing_row += 2
            worksheet.write(printing_row, printing_col, '1 authority printed')

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def DocumentDateSales(self, company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority):
        company_id = company.id
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Tax Report")

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
            'align': 'center',
            'bottom': 1,
            'bold': True,
        })
        center_bold = workbook.add_format({
            'align': 'center',
            'bold': True,
        })

        border_top_bot = workbook.add_format({
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

        auth_str = ':   [ ' + tax_authority + ' ] to [ ' + tax_authority + ' ]'
        worksheet.merge_range('C3:E3', company.name, merge_format)
        worksheet.merge_range('C4:E4', print_by + " " + transaction_type + " Tracking (" + self.tx_rpt_code + ")", merge_format)
        worksheet.merge_range('C5:D5', 'From Tax Authority', merge_format)
        worksheet.write(4, 4, auth_str, merge_format)
        worksheet.merge_range('C6:D6', "Print Amounts in", merge_format)
        worksheet.write(5, 4, ":  " + "[" + print_type + "]", merge_format)
        worksheet.merge_range('C7:D7', "Report by", merge_format)
        worksheet.write(6, 4, ":   " + "[" + report_by + "]", merge_format)
        worksheet.merge_range('C8:D8', "As of Fiscal Year", merge_format)
        worksheet.write(7, 4, ":   " + "[" + str(issue_from.month) + '-' + str(issue_from.year) +
                              "] TO [" + str(issue_to.month) + '-' + str(issue_to.year) + "]", merge_format)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            com_curr = ''
            str_tax_reporting = ''
            # decimal_place_f = get_decimal_place(company.currency)
            # decimal_place = "%.2f"
            is_decimal_f = company.currency.is_decimal
            is_decimal = True

            # Header
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Document Date', center_line)
            worksheet.write(11, 2, 'Source code', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Invoice Amount', center_line)
            if print_type == 'Tax Reporting':
                worksheet.write(11, 5, 'Currency', center_line)
                worksheet.write(11, 6, 'Tax Base', center_line)
                worksheet.write(11, 7, 'Tax Amount', center_line)

                com_curr = company.currency.code
                str_tax_reporting = "Tax Reporting Currency:"
            else:
                worksheet.write(11, 5, 'Tax Base', center_line)
                worksheet.write(11, 6, 'Tax Amount', center_line)
                worksheet.merge_range('E10:G10', print_type, center_bold)

            worksheet.set_column(0, 7, 18)

            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Source' or print_type == 'Functional':
                all_journals = Journal.objects.select_related('currency', 'customer').filter(id__in=journal_ids).order_by('currency_id', 'customer_id')
            else:
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('document_date')

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            func_summary1 = func_summary2 = func_summary3 = 0
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id,
                                'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0,
                                'summary2': 0,
                                'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id

            summary_total_amount = summary_tax_base = summary_tax_amount = 0
            if print_type == 'Source' or print_type == 'Functional':
                func_subtotal1 = func_subtotal2 = func_subtotal3 = 0
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = 0
                    custotal1 = custotal2 = custotal3 = 0
                    currency_printed = False
                    if print_type == 'Source':
                        worksheet.write(printing_row, printing_col, 'Source Currency')
                        worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                        printing_row += 1

                    journals = all_journals.filter(currency_id=currency['id']).order_by('document_date')
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journals
                                                                ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                        .select_related('journal', 'journal__customer')\
                        .exclude(tax_id__isnull=True)

                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    customer_code = ''
                    for trx in all_transactions:
                        if last_journal_id == 0:
                            try:
                                customer_code = trx.journal.customer.code
                            except:
                                customer_code = ''
                        currency_printed = True
                        if index == 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')
                            if print_type == 'Source':
                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                            else:
                                total_amount = trx.journal.total_amount * trx.exchange_rate
                                tax_base = trx.base_tax_amount * trx.exchange_rate
                                tax_amount = trx.tax_amount * trx.exchange_rate

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # custotal1 += round_number(total_amount)
                            # custotal2 += round_number(tax_base)
                            # custotal3 += round_number(tax_amount)
                            # func_subtotal1 += round_number(total_amount)
                            # func_subtotal2 += round_number(tax_base)
                            # func_subtotal3 += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            if print_type == 'Functional':
                                # decimal_place = decimal_place_f
                                is_decimal - is_decimal_f
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            func_subtotal1 += round_number(total_amount)
                            func_subtotal2 += round_number(tax_base)
                            func_subtotal3 += round_number(tax_amount)
                            if trx.journal.customer and customer_code == trx.journal.customer.code:
                                custotal1 += round_number(total_amount)
                                custotal2 += round_number(tax_base)
                                custotal3 += round_number(tax_amount)
                            elif customer_code == '':
                                custotal1 += round_number(total_amount)
                                custotal2 += round_number(tax_base)
                                custotal3 += round_number(tax_amount)
                            if trx.journal.customer and customer_code != trx.journal.customer.code:
                                if customer_code != '':
                                    custotal1 += round_number(total_amount)
                                    custotal2 += round_number(tax_base)
                                    custotal3 += round_number(tax_amount)
                                
                                if print_type == 'Functional':
                                    # decimal_place = decimal_place_f
                                    is_decimal - is_decimal_f
                                worksheet.write(
                                    printing_row, printing_col + 2, 'Customer TAX Auth. Total ', border_top_bot)
                                worksheet.write(
                                    printing_row, printing_col + 3, currency['code'] + ':', border_top_bot)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    custotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    custotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    custotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                                try:
                                    customer_code = trx.journal.customer.code
                                except:
                                    customer_code = ''

                                custotal1 = 0
                                custotal2 = 0
                                custotal3 = 0

                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AR-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AR-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AR-CR'
                            else:
                                source_code = 'AR-PY'
                            try:
                                column1 = trx.journal.customer.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            if print_type == 'Source':
                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                            else:
                                total_amount = trx.journal.total_amount * trx.exchange_rate
                                tax_base = trx.base_tax_amount * trx.exchange_rate
                                tax_amount = trx.tax_amount * trx.exchange_rate

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # func_subtotal1 += round_number(total_amount)
                            # func_subtotal2 += round_number(tax_base)
                            # func_subtotal3 += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                if print_type == 'Source':
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                else:
                                    tax_base += trx.base_tax_amount * trx.exchange_rate * -1
                                    tax_amount += trx.tax_amount * trx.exchange_rate * -1
                            else:
                                if print_type == 'Source':
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                else:
                                    tax_base += trx.base_tax_amount * trx.exchange_rate
                                    tax_amount += trx.tax_amount * trx.exchange_rate

                            # subtotal2 += round_number(trx.base_tax_amount)
                            # subtotal3 += round_number(trx.tax_amount)
                            # func_subtotal2 += round_number(trx.base_tax_amount)
                            # func_subtotal3 += round_number(trx.tax_amount)
                        index += 1

                    currency['summary1'] += subtotal1
                    currency['summary2'] += subtotal2
                    currency['summary3'] += subtotal3

                    if currency_printed:
                        if index != 0:
                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            func_subtotal1 += round_number(total_amount)
                            func_subtotal2 += round_number(tax_base)
                            func_subtotal3 += round_number(tax_amount)
                            custotal1 += round_number(total_amount)
                            custotal2 += round_number(tax_base)
                            custotal3 += round_number(tax_amount)
                            currency['summary1'] += round_number(total_amount)
                            currency['summary2'] += round_number(tax_base)
                            currency['summary3'] += round_number(tax_amount)
                            if print_type == 'Functional':
                                # decimal_place = decimal_place_f
                                is_decimal - is_decimal_f
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1

                            worksheet.write(printing_row, printing_col + 2, 'Customer TAX Auth. Total ', border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, currency['code'] + ':', border_top_bot)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                custotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                custotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                custotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1
                        if print_type == 'Source':
                            worksheet.write(printing_row, printing_col + 2, 'GSTDOS Total ', border_top_bot)
                            worksheet.write(printing_row, printing_col + 3, currency['code'] + ':', border_top_bot)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                subtotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1
                if print_type == 'Functional':
                    worksheet.write(printing_row, printing_col + 3, 'GSTDOS Total ', border_top_bot)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        func_subtotal1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        func_subtotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 6, round_number(
                        func_subtotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    printing_row += 1

                    func_summary1 += func_subtotal1
                    func_summary2 += func_subtotal2
                    func_summary3 += func_subtotal3
            else:
                subtotal1 = subtotal2 = subtotal3 = 0
                custotal1 = custotal2 = custotal3 = 0
                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                            journal__in=all_journals
                                                            ).order_by('journal__customer__code', '-journal__document_type', 'journal_id')\
                    .select_related('journal', 'journal__customer')\
                    .exclude(tax_id__isnull=True)

                if not int(is_history):
                    all_transactions = all_transactions.filter(is_clear_tax=False)
                last_journal_id = 0
                index = 0
                customer_code = ''
                for trx in all_transactions:
                    if last_journal_id == 0:
                        try:
                            customer_code = trx.journal.customer.code
                        except:
                            customer_code = ''
                    if index == 0:
                        last_journal_id = trx.journal.id
                        # decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AR-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AR-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AR-CR'
                        else:
                            source_code = 'AR-PY'
                        try:
                            column1 = trx.journal.customer.code
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = trx.journal.name[:15]
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount

                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        else:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)

                        # subtotal1 += round_number(total_amount)
                        # subtotal2 += round_number(tax_base)
                        # subtotal3 += round_number(tax_amount)
                        # custotal1 += round_number(total_amount)
                        # custotal2 += round_number(tax_base)
                        # custotal3 += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, source_code)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total_amount), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, currency_code)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            tax_base), dec_format)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            tax_amount), dec_format)
                        printing_row += 1

                        subtotal1 += round_number(total_amount)
                        subtotal2 += round_number(tax_base)
                        subtotal3 += round_number(tax_amount)
                        if trx.journal.customer and customer_code == trx.journal.customer.code:
                            custotal1 += round_number(total_amount)
                            custotal2 += round_number(tax_base)
                            custotal3 += round_number(tax_amount)
                        elif customer_code == '':
                            custotal1 += round_number(total_amount)
                            custotal2 += round_number(tax_base)
                            custotal3 += round_number(tax_amount)
                        if trx.journal.customer and customer_code != trx.journal.customer.code:
                            if customer_code != '':
                                custotal1 += round_number(total_amount)
                                custotal2 += round_number(tax_base)
                                custotal3 += round_number(tax_amount)

                            worksheet.write(printing_row, printing_col + 4, 'Customer TAX Auth. ', border_top_bot)
                            worksheet.write(printing_row, printing_col + 5, 'Total :', border_top_bot)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                custotal2), border_top_bot_dec)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                custotal3), border_top_bot_dec)
                            printing_row += 1

                            try:
                                customer_code = trx.journal.customer.code
                            except:
                                customer_code = ''

                            custotal1 = 0
                            custotal2 = 0
                            custotal3 = 0

                        last_journal_id = trx.journal.id
                        # decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AR-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AR-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AR-CR'
                        else:
                            source_code = 'AR-PY'
                        try:
                            column1 = trx.journal.customer.code
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = trx.journal.name[:15]
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount

                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            tax_base = (tax_base * exchange_rate)
                            tax_amount = (tax_amount * exchange_rate)
                        else:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)

                        # subtotal1 += round_number(total_amount)
                        # subtotal2 += round_number(tax_base)
                        # subtotal3 += round_number(tax_amount)

                    elif index > 0:
                        last_journal_id = trx.journal.id
                        # decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        t_base = 0
                        t_amount = 0
                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            t_base = (trx.base_tax_amount * exchange_rate)
                            t_amount = (trx.tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            t_base = (trx.base_tax_amount * exchange_rate)
                            t_amount = (trx.tax_amount * exchange_rate)
                        elif com_curr != currency_code:
                            t_base = (trx.base_tax_amount * trx.exchange_rate)
                            t_amount = (trx.tax_amount * trx.exchange_rate)
                        else:
                            t_base = trx.base_tax_amount
                            t_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            t_base = -1 * t_base
                            t_amount = -1 * t_amount

                        tax_base += t_base
                        tax_amount += t_amount
                        # subtotal2 += round_number(t_base)
                        # subtotal3 += round_number(t_amount)
                    index += 1

                if index != 0:
                    worksheet.write(printing_row, printing_col, column1)
                    worksheet.write(printing_row, printing_col + 1, column2)
                    worksheet.write(printing_row, printing_col + 2, source_code)
                    worksheet.write(printing_row, printing_col + 3, column4)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total_amount), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, currency_code)
                    worksheet.write(printing_row, printing_col + 6, round_number(
                        tax_base), dec_format)
                    worksheet.write(printing_row, printing_col + 7, round_number(
                        tax_amount), dec_format)
                    printing_row += 1

                    subtotal1 += round_number(total_amount)
                    subtotal2 += round_number(tax_base)
                    subtotal3 += round_number(tax_amount)
                    custotal1 += round_number(total_amount)
                    custotal2 += round_number(tax_base)
                    custotal3 += round_number(tax_amount)

                    worksheet.write(printing_row, printing_col + 4, 'Customer TAX Auth. ', border_top_bot)
                    worksheet.write(printing_row, printing_col + 5, 'Total :', border_top_bot)
                    worksheet.write(printing_row, printing_col + 6, round_number(
                        custotal2), border_top_bot_dec)
                    worksheet.write(printing_row, printing_col + 7, round_number(
                        custotal3), border_top_bot_dec)
                    printing_row += 1

                worksheet.write(printing_row, printing_col + 4, 'GSTDOS ', border_top_bot)
                worksheet.write(printing_row, printing_col + 5, 'Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 6, round_number(custotal2),
                                border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 7, round_number(custotal3),
                                border_top_bot_dec)
                printing_row += 1

                summary_total_amount += subtotal1
                summary_tax_base += subtotal2
                summary_tax_amount += subtotal3

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'D' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Invoice Amount', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Amount', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Invoice Amount', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                printing_row += 1

            total_tax_base = total_tax_amu = tot_inv = 0
            if print_type == 'Source':
                for curr in currencies:
                    curr_code = curr['code']
                    try:
                        cur = Currency.objects.get(code=curr['code'])
                        # decimal_place = get_decimal_place(cur)
                        is_decimal = cur.is_decimal
                    except:
                        # decimal_place = "%.2f"
                        is_decimal = True
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, curr_code)
                    worksheet.write(printing_row, printing_col + 2, round_number(
                        curr['summary1']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        curr['summary2']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        curr['summary3']), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                worksheet.write(printing_row, printing_col + 1, "SGD")
                worksheet.write(printing_row, printing_col + 2, round_number(
                    summary_tax_base), dec_format)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    summary_tax_amount), dec_format)
                printing_row += 1
            else:
                for curr in currencies:
                    tot_inv += curr['summary1']
                    total_tax_base += curr['summary2']
                    total_tax_amu += curr['summary3']

                worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                worksheet.write(printing_row, printing_col + 1,
                                round_number(tot_inv), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 2, round_number(
                    total_tax_base), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    total_tax_amu), dec_format if is_decimal_f else num_format)
                printing_row += 2
                worksheet.write(printing_row, printing_col + 1, 'Report Total :', right_line)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    total_tax_amu), dec_format if is_decimal_f else num_format)
                printing_row += 1

            printing_row += 2
            worksheet.write(printing_row, printing_col, '1 authority printed')

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def DocumentDatePurchase(self, company, journal_ids, issue_from, issue_to, print_type, report_by, print_by, transaction_type, is_history, tax_authority):
        company_id = company.id
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Tax Report")

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
            'align': 'center',
            'bottom': 1,
            'bold': True,
        })
        center_bold = workbook.add_format({
            'align': 'center',
            'bold': True,
        })

        border_top_bot = workbook.add_format({
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

        auth_str = ':   [ ' + tax_authority + ' ] to [ ' + tax_authority + ' ]'
        worksheet.merge_range('C3:E3', company.name, merge_format)
        worksheet.merge_range('C4:E4', print_by + " " + transaction_type + " Tracking (" + self.tx_rpt_code + ")", merge_format)
        worksheet.merge_range('C5:D5', 'From Tax Authority', merge_format)
        worksheet.write(4, 4, auth_str, merge_format)
        worksheet.merge_range('C6:D6', "Print Amounts in", merge_format)
        worksheet.write(5, 4, ":  " + "[" + print_type + "]", merge_format)
        worksheet.merge_range('C7:D7', "Report by", merge_format)
        worksheet.write(6, 4, ":   " + "[" + report_by + "]", merge_format)
        worksheet.merge_range('C8:D8', "As of Fiscal Year", merge_format)
        worksheet.write(7, 4, ":   " + "[" + str(issue_from.month) + '-' + str(issue_from.year) +
                              "] TO [" + str(issue_to.month) + '-' + str(issue_to.year) + "]", merge_format)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            com_curr = ''
            str_tax_reporting = ''
            decimal_place_f = get_decimal_place(company.currency)
            decimal_place = "%.2f"
            is_decimal_f = company.currency.is_decimal
            is_decimal = True

            # Header
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Document Date', center_line)
            worksheet.write(11, 2, 'Source code', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Invoice Amount', center_line)
            if print_type == 'Tax Reporting':
                worksheet.write(11, 5, 'Currency', center_line)
                worksheet.write(11, 6, 'Tax Base', center_line)
                worksheet.write(11, 7, 'Tax Amount', center_line)
                worksheet.write(11, 8, 'Recoverable Tax', center_line)
                worksheet.write(11, 9, 'Recoverable Rate', center_line)
                worksheet.write(11, 10, 'Expense Separately', center_line)
                worksheet.merge_range('E10:F10', 'Source', center_bold)
                worksheet.merge_range('G10:I10', print_type, center_bold)

                com_curr = 'SGD'
                str_tax_reporting = "Tax Reporting Currency:"
            else:
                worksheet.write(11, 5, 'Tax Base', center_line)
                worksheet.write(11, 6, 'Tax Amount', center_line)
                worksheet.write(11, 7, 'Recoverable Tax', center_line)
                worksheet.write(11, 8, 'Recoverable Rate', center_line)
                worksheet.write(11, 9, 'Expense Separately', center_line)
                worksheet.merge_range('E10:G10', print_type, center_bold)

            worksheet.set_column(0, 10, 18)

            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Tax Reporting' or print_type == 'Functional':
                all_journals = Journal.objects.select_related('supplier').filter(id__in=journal_ids).order_by('supplier__code', 'document_date')
            else:
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id', 'document_date')
            journal_doc_dates = all_journals.values('perd_month', 'perd_year').order_by('perd_year', 'perd_month').distinct()
            periods = []
            periods_count = 0
            last_period = None
            for doc_date in journal_doc_dates:
                period_str = str(doc_date.get('perd_year')) + '-' + str(doc_date.get('perd_month'))
                if period_str != last_period:
                    periods.append(period_str)
                    periods_count += 1
                    last_period = period_str

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            summary_total_amount = summary_tax_base = summary_tax_amount = 0
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id,
                                'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id
            grandtotal1 = grandtotal2 = grandtotal3 = 0
            if print_type == 'Source':
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = 0
                    ventotal1 = ventotal2 = ventotal3 = 0
                    currency_printed = False

                    worksheet.write(printing_row, printing_col, 'Source Currency')
                    worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                    printing_row += 1

                    journals = all_journals.filter(currency_id=currency['id']).order_by('document_date')
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journals
                                                                ).order_by('journal__supplier__code', 'journal__document_date', 'journal_id')\
                        .select_related('journal', 'journal__supplier', 'tax')\
                        .exclude(tax_id__isnull=True)
                    if not int(is_history):
                        all_transactions = all_transactions.filter(is_clear_tax=False)
                    last_journal_id = 0
                    index = 0
                    vendor_code = ''
                    for trx in all_transactions:
                        if last_journal_id == 0:
                            try:
                                vendor_code = trx.journal.supplier.code
                            except:
                                vendor_code = ''
                        currency_printed = True
                        if index == 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'

                            is_expense_separately = 'No'
                            recoverable_rate = 0.00
                            if trx.tax:
                                if trx.tax.tax_authority:
                                    recoverable_rate = trx.tax.tax_authority.recoverable_rate
                                    if trx.tax.tax_authority.is_expense_separately:
                                        is_expense_separately = 'Yes'
                            try:
                                column1 = trx.journal.supplier.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # ventotal1 += round_number(total_amount)
                            # ventotal2 += round_number(tax_base)
                            # ventotal3 += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 8, str(intcomma(decimal_place % recoverable_rate)) + '%' if tax_amount else '', right_line)
                            worksheet.write(printing_row, printing_col + 9, str(is_expense_separately), right_line)
                            printing_row += 1

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            grandtotal1 += round_number(total_amount)
                            grandtotal2 += round_number(tax_base)
                            grandtotal3 += round_number(tax_amount)
                            if trx.journal.supplier and vendor_code == trx.journal.supplier.code:
                                ventotal1 += round_number(total_amount)
                                ventotal2 += round_number(tax_base)
                                ventotal3 += round_number(tax_amount)
                            elif vendor_code == '':
                                ventotal1 += round_number(total_amount)
                                ventotal2 += round_number(tax_base)
                                ventotal3 += round_number(tax_amount)
                            if trx.journal.supplier and vendor_code != trx.journal.supplier.code:
                                if vendor_code != '':
                                    ventotal1 += round_number(total_amount)
                                    ventotal2 += round_number(tax_base)
                                    ventotal3 += round_number(tax_amount)
                                worksheet.write(printing_row, printing_col + 2, 'Vendor TAX Auth.', border_top_bot)
                                worksheet.write(printing_row, printing_col + 3, 'Total ' + currency['code'] + ' :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    ventotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    ventotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    ventotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    ventotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                                try:
                                    vendor_code = trx.journal.supplier.code
                                except:
                                    vendor_code = ''

                                ventotal1 = 0
                                ventotal2 = 0
                                ventotal3 = 0

                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'

                            is_expense_separately = 'No'
                            recoverable_rate = 0.00
                            if trx.tax:
                                if trx.tax.tax_authority:
                                    recoverable_rate = trx.tax.tax_authority.recoverable_rate
                                    if trx.tax.tax_authority.is_expense_separately:
                                        is_expense_separately = 'Yes'
                            try:
                                column1 = trx.journal.supplier.code
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = trx.journal.name[:15]
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # subtotal1 += round_number(total_amount)
                            # subtotal2 += round_number(tax_base)
                            # subtotal3 += round_number(tax_amount)
                            # grandtotal1 += round_number(total_amount)
                            # grandtotal2 += round_number(tax_base)
                            # grandtotal3 += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                tax_base += trx.base_tax_amount * -1
                                tax_amount += trx.tax_amount * -1
                                # subtotal2 += round_number(trx.base_tax_amount * -1)
                                # subtotal3 += round_number(trx.tax_amount * -1)
                            else:
                                tax_base += trx.base_tax_amount
                                tax_amount += trx.tax_amount
                                # subtotal2 += round_number(trx.base_tax_amount)
                                # subtotal3 += round_number(trx.tax_amount)
                        index += 1

                    currency['summary1'] += subtotal1
                    currency['summary2'] += subtotal2
                    currency['summary3'] += subtotal3

                    if currency_printed:
                        if index != 0:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 8, str(intcomma(decimal_place % recoverable_rate)) + '%' if tax_amount else '', right_line)
                            worksheet.write(printing_row, printing_col + 9, str(is_expense_separately), right_line)
                            printing_row += 1

                            subtotal1 += round_number(total_amount)
                            subtotal2 += round_number(tax_base)
                            subtotal3 += round_number(tax_amount)
                            grandtotal1 += round_number(total_amount)
                            grandtotal2 += round_number(tax_base)
                            grandtotal3 += round_number(tax_amount)
                            ventotal1 += round_number(total_amount)
                            ventotal2 += round_number(tax_base)
                            ventotal3 += round_number(tax_amount)
                            currency['summary1'] += round_number(total_amount)
                            currency['summary2'] += round_number(tax_base)
                            currency['summary3'] += round_number(tax_amount)

                        worksheet.write(printing_row, printing_col + 2, 'Vendor TAX Auth.', border_top_bot)
                        worksheet.write(printing_row, printing_col + 3, 'Total ' + currency['code'] + ' :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                                    ventotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            ventotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            ventotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            ventotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

                        worksheet.write(printing_row, printing_col + 2, 'GSTDOS Total ', border_top_bot)
                        worksheet.write(printing_row, printing_col + 3, currency['code'] + ' :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            subtotal1), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

            else:
                subtotal1 = subtotal2 = subtotal3 = 0
                ventotal1 = ventotal2 = ventotal3 = 0
                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                            journal__in=all_journals
                                                            ).order_by('journal__supplier__code', 'journal__document_date', 'journal_id')\
                    .select_related('journal', 'journal__supplier', 'tax')\
                    .exclude(tax_id__isnull=True)
                if not int(is_history):
                    all_transactions = all_transactions.filter(is_clear_tax=False)
                last_journal_id = 0
                index = 0
                vendor_code = ''
                for trx in all_transactions:
                    if last_journal_id == 0:
                        try:
                            vendor_code = trx.journal.supplier.code
                        except:
                            vendor_code = ''
                    if index == 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                        else:
                            source_code = 'AP-PY'

                        is_expense_separately = 'No'
                        recoverable_rate = 0.00
                        if trx.tax:
                            if trx.tax.tax_authority:
                                recoverable_rate = trx.tax.tax_authority.recoverable_rate
                                if trx.tax.tax_authority.is_expense_separately:
                                    is_expense_separately = 'Yes'
                        try:
                            column1 = trx.journal.supplier.code
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = trx.journal.name[:15]
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        if print_type == 'Functional' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (trx.journal.total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount

                        # subtotal1 += round_number(total_amount)
                        # subtotal2 += round_number(tax_base)
                        # subtotal3 += round_number(tax_amount)
                        # ventotal1 += round_number(total_amount)
                        # ventotal2 += round_number(tax_base)
                        # ventotal3 += round_number(tax_amount)
                        # grandtotal1 += round_number(total_amount)
                        # grandtotal2 += round_number(tax_base)
                        # grandtotal3 += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        if print_type == 'Functional':
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 5, round_number(
                                tax_base), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                tax_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 8, str(intcomma(decimal_place_f %
                                                                                        recoverable_rate)) + '%' if tax_amount else '', right_line)
                            worksheet.write(printing_row, printing_col + 9, str(is_expense_separately), right_line)
                            printing_row += 1
                        else:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, source_code)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 5, currency_code)
                            worksheet.write(printing_row, printing_col + 6, round_number(
                                tax_base), dec_format)
                            worksheet.write(printing_row, printing_col + 7, round_number(
                                tax_amount), dec_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                tax_amount), dec_format)
                            worksheet.write(printing_row, printing_col + 9, str(intcomma("%.2f" %
                                                                                        recoverable_rate)) + '%' if tax_amount else '', right_line)
                            worksheet.write(printing_row, printing_col + 10, str(is_expense_separately), right_line)
                            printing_row += 1

                        subtotal1 += round_number(total_amount)
                        subtotal2 += round_number(tax_base)
                        subtotal3 += round_number(tax_amount)
                        grandtotal1 += round_number(total_amount)
                        grandtotal2 += round_number(tax_base)
                        grandtotal3 += round_number(tax_amount)
                        if trx.journal.supplier and vendor_code == trx.journal.supplier.code:
                            ventotal1 += round_number(total_amount)
                            ventotal2 += round_number(tax_base)
                            ventotal3 += round_number(tax_amount)
                        elif vendor_code == '':
                            ventotal1 += round_number(total_amount)
                            ventotal2 += round_number(tax_base)
                            ventotal3 += round_number(tax_amount)
                        if trx.journal.supplier and vendor_code != trx.journal.supplier.code:
                            if vendor_code != '':
                                ventotal1 += round_number(total_amount)
                                ventotal2 += round_number(tax_base)
                                ventotal3 += round_number(tax_amount)
                            total_str = 'Vendor TAX Auth. Total :'
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col + 3, 'Vendor TAX Auth. Total:', border_top_bot)
                                worksheet.write(printing_row, printing_col + 4, round_number(
                                    ventotal1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 5, round_number(
                                    ventotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    ventotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    ventotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col + 5, 'Vendor TAX Auth. Total:', border_top_bot)
                                worksheet.write(printing_row, printing_col + 6, round_number(
                                    ventotal2), border_top_bot_dec)
                                worksheet.write(printing_row, printing_col + 7, round_number(
                                    ventotal3), border_top_bot_dec)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    ventotal3), border_top_bot_dec)
                                printing_row += 1

                            try:
                                vendor_code = trx.journal.supplier.code
                            except:
                                vendor_code = ''

                            ventotal1 = 0
                            ventotal2 = 0
                            ventotal3 = 0

                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.journal.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                        else:
                            source_code = 'AP-PY'

                        is_expense_separately = 'No'
                        recoverable_rate = 0.00
                        if trx.tax:
                            if trx.tax.tax_authority:
                                recoverable_rate = trx.tax.tax_authority.recoverable_rate
                                if trx.tax.tax_authority.is_expense_separately:
                                    is_expense_separately = 'Yes'
                        try:
                            column1 = trx.journal.supplier.code
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = trx.journal.name[:15]
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column2 = trx.journal.document_date.strftime('%d/%m/%Y')

                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            elif trx.journal.currency_id != to_currency:
                                if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                    exchange_rate = trx.journal.tax_exchange_rate
                                else:
                                    try:
                                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                    from_currency_id=from_currency,
                                                                                    to_currency_id=to_currency,
                                                                                    exchange_date__lte=trx.journal.document_date,
                                                                                    flag='ACCOUNTING').order_by('exchange_date').last().rate
                                    except:
                                        exchange_rate = Decimal('1.00000000')
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        if print_type == 'Functional' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (trx.journal.total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount

                        # subtotal1 += round_number(total_amount)
                        # subtotal2 += round_number(tax_base)
                        # subtotal3 += round_number(tax_amount)
                        # ventotal1 += round_number(total_amount)
                        # ventotal2 += round_number(tax_base)
                        # ventotal3 += round_number(tax_amount)
                        # grandtotal1 += round_number(total_amount)
                        # grandtotal2 += round_number(tax_base)
                        # grandtotal3 += round_number(tax_amount)

                    elif index > 0:
                        last_journal_id = trx.journal.id
                        decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        t_base = 0
                        t_amount = 0
                        from_currency = trx.currency_id
                        to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                        if trx.journal.currency_id == to_currency:
                            exchange_rate = Decimal('1.00000000')
                            t_base = (trx.base_tax_amount * exchange_rate)
                            t_amount = (trx.tax_amount * exchange_rate)
                        elif trx.journal.currency_id != to_currency:
                            if trx.journal.tax_exchange_rate and trx.journal.tax_exchange_rate > 0:
                                exchange_rate = trx.journal.tax_exchange_rate
                            else:
                                try:
                                    exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company_id,
                                                                                from_currency_id=from_currency,
                                                                                to_currency_id=to_currency,
                                                                                exchange_date__lte=trx.journal.document_date,
                                                                                flag='ACCOUNTING').order_by('exchange_date').last().rate
                                except:
                                    exchange_rate = Decimal('1.00000000')
                            t_base = (trx.base_tax_amount * exchange_rate)
                            t_amount = (trx.tax_amount * exchange_rate)
                        elif com_curr != currency_code:
                            t_base = (trx.base_tax_amount * trx.exchange_rate)
                            t_amount = (trx.tax_amount * trx.exchange_rate)
                        else:
                            t_base = trx.base_tax_amount
                            t_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            t_base = -1 * t_base
                            t_amount = -1 * t_amount

                        tax_base += t_base
                        tax_amount += t_amount
                        # subtotal2 += round_number(t_base)
                        # subtotal3 += round_number(t_amount)
                        # ventotal2 += round_number(t_base)
                        # ventotal3 += round_number(t_amount)
                        # grandtotal2 += round_number(t_base)
                        # grandtotal3 += round_number(t_amount)
                    index += 1

                if index != 0:
                    subtotal1 += round_number(total_amount)
                    subtotal2 += round_number(tax_base)
                    subtotal3 += round_number(tax_amount)
                    grandtotal1 += round_number(total_amount)
                    grandtotal2 += round_number(tax_base)
                    grandtotal3 += round_number(tax_amount)
                    ventotal1 += round_number(total_amount)
                    ventotal2 += round_number(tax_base)
                    ventotal3 += round_number(tax_amount)
                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, source_code)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total_amount), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            tax_base), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            tax_amount), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            tax_amount), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 8, str(intcomma(decimal_place_f % recoverable_rate)) + '%' if tax_amount else '', right_line)
                        worksheet.write(printing_row, printing_col + 9, str(is_expense_separately), right_line)
                        printing_row += 1
                    else:
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, source_code)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total_amount), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, currency_code)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            tax_base), dec_format)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            tax_amount), dec_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            tax_amount), dec_format)
                        worksheet.write(printing_row, printing_col + 9, str(intcomma("%.2f" % recoverable_rate)) + '%' if tax_amount else '', right_line)
                        worksheet.write(printing_row, printing_col + 10, str(is_expense_separately), right_line)
                        printing_row += 1

                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col + 3, 'Vendor TAX Auth. Total:', border_top_bot)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            ventotal1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            ventotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            ventotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            ventotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1
                    else:
                        worksheet.write(printing_row, printing_col + 5, 'Vendor TAX Auth. Total:', border_top_bot)
                        worksheet.write(printing_row, printing_col + 6, round_number(
                            ventotal2), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 7, round_number(
                            ventotal3), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            ventotal3), border_top_bot_dec)
                        printing_row += 1

                summary_total_amount += subtotal1
                summary_tax_base += subtotal2
                summary_tax_amount += subtotal3

            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 3, 'GSTDOS Total:', border_top_bot)
                worksheet.write(printing_row, printing_col + 4, round_number(grandtotal1),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 5, round_number(grandtotal2),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 6, round_number(grandtotal3),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 7, round_number(grandtotal3),
                                border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col + 5, 'GSTDOS Total:', border_top_bot)
                worksheet.write(printing_row, printing_col + 6, round_number(grandtotal2),
                                border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 7, round_number(grandtotal3),
                                border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 8, round_number(grandtotal3),
                                border_top_bot_dec)
                printing_row += 1

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'D' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Invoice Amount', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Amount', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Recoverable Tax', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Recoverable Tax', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Invoice Amount', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Tax Amount', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Recoverable Tax', center_line)
                printing_row += 1

            total_tax_base = total_tax_amu = tot_inv = 0
            if print_type == 'Source':
                for curr in currencies:
                    curr_code = curr['code']
                    try:
                        cur = Currency.objects.get(code=curr['code'])
                        # decimal_place = get_decimal_place(cur)
                        is_decimal = cur.is_decimal
                    except:
                        # decimal_place = "%.2f"
                        is_decimal = True
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, curr_code)
                    worksheet.write(printing_row, printing_col + 2, round_number(
                        curr['summary1']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        curr['summary2']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        curr['summary3']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        curr['summary3']), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                worksheet.write(printing_row, printing_col + 1, "SGD")
                worksheet.write(printing_row, printing_col + 2, round_number(
                    summary_tax_base), dec_format)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    summary_tax_amount), dec_format)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    summary_tax_amount), dec_format)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                worksheet.write(printing_row, printing_col + 1, round_number(
                    grandtotal1), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 2, round_number(
                    grandtotal2), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    grandtotal3), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    grandtotal3), dec_format if is_decimal_f else num_format)
                printing_row += 2
                worksheet.write(printing_row, printing_col + 1, 'Report Total :', right_line)
                worksheet.write(printing_row, printing_col + 3, round_number(
                    grandtotal3), dec_format if is_decimal_f else num_format)
                worksheet.write(printing_row, printing_col + 4, round_number(
                    grandtotal3), dec_format if is_decimal_f else num_format)
                printing_row += 1

            printing_row += 2
            worksheet.write(printing_row, printing_col, '1 authority printed')

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
