import calendar
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import xlsxwriter
from decimal import Decimal
from accounting.models import Journal
from transactions.models import Transaction
from inventory.models import TransactionCode
from companies.models import Company
from currencies.models import Currency, ExchangeRate
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, TRN_CODE_TYPE_DICT, TAX_TRACK_CLASS_DICT
from utilities.common import round_number


class Print_Tracking_item_XLS:
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
                                                                          perd_year=curr_year, perd_month=current_month,
                                                                          batch__batch_type__in=(
                                                                              dict(TRANSACTION_TYPES)['AR Invoice'],
                                                                              dict(TRANSACTION_TYPES)['AR Receipt']),
                                                                          transaction_type__in=('0', '', '2'),
                                                                          batch__status=int(STATUS_TYPE_DICT['Posted']))\
                                            .exclude(reverse_reconciliation=True)\
                                            .order_by('id').values_list('id', flat=True)
            else:
                journals = Journal.objects.select_related('batch').filter(is_hidden=0, company_id=company_id,
                                                                          perd_year=curr_year, perd_month=current_month,
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

        com_curr = ''
        str_tax_reporting = ''
        # decimal_place_f = get_decimal_place(company.currency)
        # decimal_place = "%.2f"
        is_decimal_f = company.currency.is_decimal
        is_decimal = True

        # Header
        if print_type == 'Source':
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Customer Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Exchange Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Sales', center_line)
            worksheet.write(11, 9, 'Tax Base', center_line)
            worksheet.write(11, 10, 'Tax Amount', center_line)

        elif print_type == 'Tax Reporting':
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Customer Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Sales', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Tax Base', center_line)
            worksheet.write(11, 11, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:L10', '------Tax Reporting-----', center_bold)

            com_curr = 'SGD'
            str_tax_reporting = "Tax Reporting Currency:"
        else:
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Customer Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Sales', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Sales', center_line)
            worksheet.write(11, 11, 'Tax Base', center_line)
            worksheet.write(11, 12, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:M10', '--------------Functional------------', center_bold)

        worksheet.set_column(0, 12, 18)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Source':
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.select_related('customer').filter(id__in=journal_ids).order_by('customer_id')
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
            tax_class = 0
            grand_total1 = grand_total2 = 0
            summaries = []
            for period in periods:
                period_counter += 1
                worksheet.write(printing_row, printing_col, 'Year-Period')
                worksheet.write(printing_row, printing_col + 1, ': ' + period)
                printing_row += 2

                year = period.split('-')[0]
                month = period.split('-')[1]
                if print_type == 'Source':
                    for currency in currencies:
                        subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                        currency_printed = False
                        worksheet.write(printing_row, printing_col, 'Source')
                        worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                        printing_row += 1
                        journal_by_curr = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)

                        all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                    journal__in=journal_by_curr
                                                                    ).order_by('tax__number', 'journal_id')\
                            .select_related('journal', 'journal__customer', 'tax')\
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
                                    column2 = trx.journal.customer.name[:15]
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = trx.exchange_rate
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                    tax_class = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)

                            if last_journal_id != trx.journal.id:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate if tax_rate else 0.0000000, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number(tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, round_number(tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

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
                                    column2 = trx.journal.customer.name[:15]
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = trx.exchange_rate
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                if tax_cl != tax_class and tax_class != 0:
                                    summery_obj = {'class': tax_class,
                                                'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)

                                    worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 8, round_number(tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    printing_row += 1

                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl
                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)
                            elif index > 0:
                                last_journal_id = trx.journal.id
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                if tax_cl != tax_class and tax_class != 0:
                                    worksheet.write(printing_row, printing_col, column1)
                                    worksheet.write(printing_row, printing_col + 1, column2)
                                    worksheet.write(printing_row, printing_col + 2, column3)
                                    worksheet.write(printing_row, printing_col + 3, column4)
                                    worksheet.write(printing_row, printing_col + 4, source_code)
                                    worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                    worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                    worksheet.write(printing_row, printing_col + 7, tax_rate if tax_rate else 0.0000000, rate_format)
                                    worksheet.write(printing_row, printing_col + 8, round_number(total_amount), dec_format if is_decimal else num_format)
                                    worksheet.write(printing_row, printing_col + 9, round_number(tax_base), dec_format if is_decimal else num_format)
                                    worksheet.write(printing_row, printing_col + 10, round_number(tax_amount), dec_format if is_decimal else num_format)
                                    printing_row += 1

                                    tax_cl_source_total += round_number(total_amount)
                                    tax_cl_base_total += round_number(tax_base)
                                    tax_cl_tax_total += round_number(tax_amount)
                                    
                                    if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                        total_amount = trx.journal.total_amount * -1
                                    else:
                                        total_amount = trx.journal.total_amount
                                    tax_base = 0
                                    tax_amount = 0
                                    tax_rate = int(trx.tax.rate)

                                    summery_obj = {'class': tax_class,
                                                   'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                   'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)

                                    worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 8, round_number(tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                    printing_row += 1

                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                    # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                    # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                                else:
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                    # tax_cl_base_total += round_number(trx.base_tax_amount)
                                    # tax_cl_tax_total += round_number(trx.tax_amount)
                            index += 1

                        if currency_printed:
                            if index != 0:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                            if tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                            worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                            worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1

                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total

                            worksheet.write(printing_row, printing_col + 7, 'Fiscal ' + period, border_top_bot)
                            worksheet.write(printing_row, printing_col + 8, 'Total ' + currency['code'] + ' :', border_top_bot)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1

                            tax_class = 0
                            grand_total1 += subtotal2
                            grand_total2 += subtotal3

                        currency['summary1'] = subtotal1
                        currency['summary2'] = subtotal2
                        currency['summary3'] = subtotal3

                else:  # Tax Reporting Currency & Functional Currency
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    journal_by_period = all_journals.filter(perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_period
                                                                ).order_by('tax__number', 'journal_id')\
                        .select_related('journal', 'journal__customer', 'tax')\
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
                                column2 = trx.journal.customer.name[:15]
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']
                            tax_rate = int(trx.tax.rate)

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if print_type == 'Tax Reporting':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = exchange_rate
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = (tax_amount * exchange_rate)
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = (tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                                total_amount = (total_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    s_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    total_amount), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_base), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_amount), dec_format if is_decimal_f else num_format)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_base), dec_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_amount), dec_format)
                                printing_row += 1

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

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
                                column2 = trx.journal.customer.name[:15]
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if print_type == 'Tax Reporting':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = exchange_rate
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = (tax_amount * exchange_rate)
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = (tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                                total_amount = (total_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class, 'code': 'SGD',
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                if print_type == 'Functional':
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1
                                else:
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_base_total), border_top_bot_dec)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_tax_total), border_top_bot_dec)
                                    printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                if print_type == 'Functional':
                                    worksheet.write(printing_row, printing_col, column1)
                                    worksheet.write(printing_row, printing_col + 1, column2)
                                    worksheet.write(printing_row, printing_col + 2, column3)
                                    worksheet.write(printing_row, printing_col + 3, column4)
                                    worksheet.write(printing_row, printing_col + 4, source_code)
                                    worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                    worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                    worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        s_amount), dec_format if is_decimal else num_format)
                                    worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        total_amount), dec_format if is_decimal_f else num_format)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_base), dec_format if is_decimal_f else num_format)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        tax_amount), dec_format if is_decimal_f else num_format)
                                    printing_row += 1
                                else:
                                    worksheet.write(printing_row, printing_col, column1)
                                    worksheet.write(printing_row, printing_col + 1, column2)
                                    worksheet.write(printing_row, printing_col + 2, column3)
                                    worksheet.write(printing_row, printing_col + 3, column4)
                                    worksheet.write(printing_row, printing_col + 4, source_code)
                                    worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                    worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                    worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        total_amount), dec_format)
                                    worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_base), dec_format)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_amount), dec_format)
                                    printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                total_amount = trx.journal.total_amount
                                if print_type == 'Functional' and com_curr != currency_code:
                                    total_amount = (total_amount * trx.exchange_rate)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class, 'code': 'SGD',
                                               'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                
                                if print_type == 'Functional':
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1
                                else:
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_base_total), border_top_bot_dec)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_tax_total), border_top_bot_dec)
                                    printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            t_base = 0
                            t_amount = 0
                            if print_type == 'Tax Reporting':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
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
                                    column6 = exchange_rate
                                    t_base = (trx.base_tax_amount * exchange_rate)
                                    t_amount = (trx.tax_amount * exchange_rate)
                                else:
                                    t_base = (trx.base_tax_amount * trx.exchange_rate)
                                    t_amount = (trx.tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional' and com_curr != currency_code:
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
                            # tax_cl_base_total += round_number(t_base)
                            # tax_cl_tax_total += round_number(t_amount)
                        index += 1

                    if index != 0:
                        if print_type == 'Functional':
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                s_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                total_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_base), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 12, round_number(
                                tax_amount), dec_format if is_decimal_f else num_format)
                            printing_row += 1
                        else:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_base), dec_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_amount), dec_format)
                            printing_row += 1

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

                    if tax_class != 0:
                        summery_obj = {'class': tax_class,
                                    'code': 'SGD',
                                    'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                        summaries.append(summery_obj)

                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1
                    else:
                        worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_cl_base_total), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_cl_tax_total), border_top_bot_dec)
                        printing_row += 1

                    subtotal1 += tax_cl_source_total
                    subtotal2 += tax_cl_base_total
                    subtotal3 += tax_cl_tax_total

                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col + 9, 'Fiscal ' + period, border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            subtotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            subtotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1
                    elif print_type == 'Tax Reporting':
                        worksheet.write(printing_row, printing_col + 8, 'Fiscal ' + period, border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            subtotal2), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            subtotal3), border_top_bot_dec)
                        printing_row += 1

                    tax_class = 0
                    grand_total1 += subtotal2
                    grand_total2 += subtotal3

            # Grand total:
            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 10, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
                worksheet.write(printing_row, printing_col + 11, 'TAX Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col + 9, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 10, round_number(
                    grand_total1), border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total2), border_top_bot_dec)
                printing_row += 1

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'E' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority And Tax Class', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Sales', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Sales', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1

            if print_type == 'Source':
                sortedsummaries = sorted(summaries, key=itemgetter('class', 'code'))
                l_class = 0
                l_code = ''
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']
                        l_code = summ['code']

                    if l_class == summ['class'] and l_code == summ['code']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        try:
                            curr = Currency.objects.get(code=l_code)
                            # decimal_place = get_decimal_place(curr)
                            is_decimal = curr.is_decimal
                        except:
                            is_decimal = True
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, l_class, num_format)
                        worksheet.write(printing_row, printing_col + 2, l_code)
                        worksheet.write(printing_row, printing_col + 3, round_number(
                            total1), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total2), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            total3), dec_format if is_decimal else num_format)
                        printing_row += 1
                        l_class = summ['class']
                        l_code = summ['code']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                try:
                    curr = Currency.objects.get(code=l_code)
                    # decimal_place = get_decimal_place(curr)
                    is_decimal = curr.is_decimal
                except:
                    is_decimal = True
                
                if len(sortedsummaries):
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, l_class, num_format)
                    worksheet.write(printing_row, printing_col + 2, l_code)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        total1), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total2), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        total3), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = 0
                total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                        worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                        worksheet.write(printing_row, printing_col + 3, summ['code'])
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total2), dec_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            total3), dec_format)
                        printing_row += 1
                        l_class = summ['class']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                    worksheet.write(printing_row, printing_col + 3, summ['code'])
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total2), dec_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        total3), dec_format)
                    printing_row += 1
            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = ''
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                        worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                        worksheet.write(printing_row, printing_col + 3, round_number(
                            total1), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total2), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            total3), dec_format if is_decimal_f else num_format)
                        printing_row += 1
                        l_class = summ['class']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        total1), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total2), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        total3), dec_format if is_decimal_f else num_format)
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

        com_curr = ''
        str_tax_reporting = ''
        # decimal_place_f = get_decimal_place(company.currency)
        # decimal_place = "%.2f"
        is_decimal_f = company.currency.is_decimal
        is_decimal = True

        # Header
        if print_type == 'Source':
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Vendor Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Exchange Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Purchase', center_line)
            worksheet.write(11, 9, 'Tax Base', center_line)
            worksheet.write(11, 10, 'Tax Amount', center_line)

        elif print_type == 'Tax Reporting':
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Vendor Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Purchase', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Tax Base', center_line)
            worksheet.write(11, 11, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:L10', '------Tax Reporting-----', center_bold)

            com_curr = 'SGD'
            str_tax_reporting = "Tax Reporting Currency:"
        else:
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Vendor Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Purchase', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Purchase', center_line)
            worksheet.write(11, 11, 'Tax Base', center_line)
            worksheet.write(11, 12, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:M10', '--------------Functional------------', center_bold)

        worksheet.set_column(0, 12, 18)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Source':
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.select_related('supplier').filter(id__in=journal_ids).order_by('supplier_id')

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
                    curr_obj = {'id': currency_id, 'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id
            period_counter = 0
            tax_class = 0
            summaries = []
            grand_total1 = grand_total2 = 0

            for period in periods:
                period_counter += 1
                worksheet.write(printing_row, printing_col, 'Year-Period')
                worksheet.write(printing_row, printing_col + 1, ': ' + period)
                printing_row += 2

                year = period.split('-')[0]
                month = period.split('-')[1]
                if print_type == 'Source':
                    for currency in currencies:
                        subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                        currency_printed = False
                        worksheet.write(printing_row, printing_col, 'Source Currency')
                        worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                        printing_row += 1

                        journal_by_curr = all_journals.filter(currency_id=currency['id'], perd_year=year, perd_month=month)
                        all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                    journal__in=journal_by_curr
                                                                    ).order_by('tax__number', 'journal__supplier_id', 'journal__document_date', 'journal_id')\
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
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                                else:
                                    source_code = 'AP-PY'
                                try:
                                    column1 = trx.journal.supplier.code
                                    column2 = trx.journal.supplier.name[:15] if trx.journal.supplier.name else ''
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = trx.exchange_rate
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                    tax_class = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)

                            if last_journal_id != trx.journal.id:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                last_journal_id = trx.journal.id
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                    source_code = 'AP-IN'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                    source_code = 'AP-DB'
                                elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    source_code = 'AP-CR'
                                else:
                                    source_code = 'AP-PY'
                                try:
                                    column1 = trx.journal.supplier.code
                                    column2 = trx.journal.supplier.name[:15] if trx.journal.supplier.name else ''
                                    column4 = trx.journal.document_number if trx.journal.document_number else ''
                                except:
                                    column1 = ''
                                    column2 = trx.journal.name
                                    column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                        else trx.journal.reference if trx.journal.reference else ''
                                column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                                column6 = trx.exchange_rate
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                tax_rate = int(trx.tax.rate)

                                total_amount = trx.journal.total_amount
                                tax_base = trx.base_tax_amount
                                tax_amount = trx.tax_amount

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                    tax_base = -1 * tax_base
                                    tax_amount = -1 * tax_amount

                                if tax_cl != tax_class and tax_class != 0:
                                    summery_obj = {'class': tax_class,
                                                'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)

                                    worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        tax_cl_source_total),  border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        tax_cl_base_total),  border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_tax_total),  border_top_bot_dec if is_decimal else border_top_bot_num)
                                    printing_row += 1

                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl
                                # tax_cl_source_total += round_number(total_amount)
                                # tax_cl_base_total += round_number(tax_base)
                                # tax_cl_tax_total += round_number(tax_amount)
                            elif index > 0:
                                last_journal_id = trx.journal.id
                                # decimal_place = get_decimal_place(trx.journal.currency)
                                is_decimal = trx.journal.currency.is_decimal
                                if trx.tax:
                                    tax_cl = trx.tax.number
                                else:
                                    tax_cl = 0
                                if tax_cl != tax_class and tax_class != 0:
                                    worksheet.write(printing_row, printing_col, column1)
                                    worksheet.write(printing_row, printing_col + 1, column2)
                                    worksheet.write(printing_row, printing_col + 2, column3)
                                    worksheet.write(printing_row, printing_col + 3, column4)
                                    worksheet.write(printing_row, printing_col + 4, source_code)
                                    worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                    worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                    worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        total_amount), dec_format if is_decimal else num_format)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        tax_base), dec_format if is_decimal else num_format)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_amount), dec_format if is_decimal else num_format)
                                    printing_row += 1

                                    tax_cl_source_total += round_number(total_amount)
                                    tax_cl_base_total += round_number(tax_base)
                                    tax_cl_tax_total += round_number(tax_amount)

                                    if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                        total_amount = trx.journal.total_amount * -1
                                    else:
                                        total_amount = trx.journal.total_amount
                                    tax_base = 0
                                    tax_amount = 0
                                    tax_rate = int(trx.tax.rate)

                                    summery_obj = {'class': tax_class,
                                                   'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                                   'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                    summaries.append(summery_obj)

                                    worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        tax_cl_source_total),  border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 9, round_number(
                                        tax_cl_base_total),  border_top_bot_dec if is_decimal else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_tax_total),  border_top_bot_dec if is_decimal else border_top_bot_num)
                                    printing_row += 1

                                    tax_class = tax_cl
                                    subtotal1 += tax_cl_source_total
                                    subtotal2 += tax_cl_base_total
                                    subtotal3 += tax_cl_tax_total
                                    tax_cl_source_total = 0
                                    tax_cl_base_total = 0
                                    tax_cl_tax_total = 0
                                else:
                                    tax_class = tax_cl

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    tax_base += trx.base_tax_amount * -1
                                    tax_amount += trx.tax_amount * -1
                                    # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                    # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                                else:
                                    tax_base += trx.base_tax_amount
                                    tax_amount += trx.tax_amount
                                    # tax_cl_base_total += round_number(trx.base_tax_amount)
                                    # tax_cl_tax_total += round_number(trx.tax_amount)
                            index += 1

                        if currency_printed:
                            if index != 0:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                            if tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                            worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                            worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1

                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total

                            worksheet.write(printing_row, printing_col + 7, 'Fiscal ' + period, border_top_bot)
                            worksheet.write(printing_row, printing_col + 8, 'Total ' + currency['code'] + ' :', border_top_bot)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                            printing_row += 1

                            tax_class = 0
                            grand_total1 += subtotal2
                            grand_total2 += subtotal3

                        currency['summary1'] = subtotal1
                        currency['summary2'] = subtotal2
                        currency['summary3'] = subtotal3

                else:  # Tax reporting currency & functional currency
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    journal_by_period = all_journals.filter(perd_year=year, perd_month=month)
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_period
                                                                ).order_by('tax__number', 'journal__supplier_id', 'journal_id')\
                        .select_related('journal', 'journal__supplier', 'tax')\
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
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name[:15] if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']
                            tax_rate = int(trx.tax.rate)

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            if print_type == 'Tax Reporting':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = exchange_rate
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = (tax_amount * exchange_rate)
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = (tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                                total_amount = (total_amount * trx.exchange_rate)

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    s_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    total_amount), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_base), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_amount), dec_format if is_decimal_f else num_format)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_base), dec_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_amount), dec_format)
                                printing_row += 1

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)
                            try:
                                currency_code = trx.currency.code  # currency['code']
                            except:
                                currency_code = trx.journal.currency.code  # currency['code']

                            s_amount = trx.journal.total_amount
                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if print_type == 'Tax Reporting':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = tax_amount * exchange_rate
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
                                    column6 = exchange_rate
                                    tax_base = (tax_base * exchange_rate)
                                    tax_amount = (tax_amount * exchange_rate)
                                else:
                                    tax_base = (tax_base * trx.exchange_rate)
                                    tax_amount = (tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional' and com_curr != currency_code:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                                total_amount = (total_amount * trx.exchange_rate)

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount
                                s_amount = -1 * s_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class, 'code': 'SGD',
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                if print_type == 'Functional':
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1
                                else:
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_base_total), border_top_bot_dec)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_tax_total), border_top_bot_dec)
                                    printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                if print_type == 'Functional':
                                    worksheet.write(printing_row, printing_col, column1)
                                    worksheet.write(printing_row, printing_col + 1, column2)
                                    worksheet.write(printing_row, printing_col + 2, column3)
                                    worksheet.write(printing_row, printing_col + 3, column4)
                                    worksheet.write(printing_row, printing_col + 4, source_code)
                                    worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                    worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                    worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        s_amount), dec_format if is_decimal else num_format)
                                    worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        total_amount), dec_format if is_decimal_f else num_format)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_base), dec_format if is_decimal_f else num_format)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        tax_amount), dec_format if is_decimal_f else num_format)
                                    printing_row += 1
                                else:
                                    worksheet.write(printing_row, printing_col, column1)
                                    worksheet.write(printing_row, printing_col + 1, column2)
                                    worksheet.write(printing_row, printing_col + 2, column3)
                                    worksheet.write(printing_row, printing_col + 3, column4)
                                    worksheet.write(printing_row, printing_col + 4, source_code)
                                    worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                    worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                    worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                    worksheet.write(printing_row, printing_col + 8, round_number(
                                        total_amount), dec_format)
                                    worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_base), dec_format)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_amount), dec_format)
                                    printing_row += 1
                                
                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                total_amount = trx.journal.total_amount
                                if print_type == 'Functional' and com_curr != currency_code:
                                    total_amount = (total_amount * trx.exchange_rate)
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = -1 * total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class, 'code': 'SGD',
                                               'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                if print_type == 'Functional':
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    worksheet.write(printing_row, printing_col + 12, round_number(
                                        tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                    printing_row += 1
                                else:
                                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                    worksheet.write(printing_row, printing_col + 10, round_number(
                                        tax_cl_base_total), border_top_bot_dec)
                                    worksheet.write(printing_row, printing_col + 11, round_number(
                                        tax_cl_tax_total), border_top_bot_dec)
                                    printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            t_base = 0
                            t_amount = 0
                            if print_type == 'Tax Reporting':
                                from_currency = trx.currency_id
                                to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                                if trx.journal.currency_id == to_currency:
                                    exchange_rate = Decimal('1.00000000')
                                    column6 = round_number(exchange_rate, 8)
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
                                    column6 = exchange_rate
                                    t_base = (trx.base_tax_amount * exchange_rate)
                                    t_amount = (trx.tax_amount * exchange_rate)
                                else:
                                    t_base = (trx.base_tax_amount * trx.exchange_rate)
                                    t_amount = (trx.tax_amount * trx.exchange_rate)
                            elif print_type == 'Functional' and com_curr != currency_code:
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
                            # tax_cl_base_total += round_number(t_base)
                            # tax_cl_tax_total += round_number(t_amount)
                        index += 1

                    if index != 0:
                        if print_type == 'Functional':
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                s_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                total_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_base), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 12, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1
                        else:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_base), dec_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_amount), dec_format)
                            printing_row += 1

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

                    if tax_class != 0:
                        summery_obj = {'class': tax_class, 'code': 'SGD',
                                    'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                        summaries.append(summery_obj)
                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1
                    else:
                        worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_cl_base_total), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_cl_tax_total), border_top_bot_dec)
                        printing_row += 1
                    subtotal1 += tax_cl_source_total
                    subtotal2 += tax_cl_base_total
                    subtotal3 += tax_cl_tax_total

                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col + 9, 'Fiscal ' + period, border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            subtotal2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            subtotal3), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                        printing_row += 1
                    elif print_type == 'Tax Reporting':
                        worksheet.write(printing_row, printing_col + 8, 'Fiscal ' + period, border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            subtotal2), border_top_bot_dec)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            subtotal3), border_top_bot_dec)
                        printing_row += 1
                    tax_class = 0
                    grand_total1 += subtotal2
                    grand_total2 += subtotal3

            # Grand total:
            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 10, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
                worksheet.write(printing_row, printing_col + 11, 'TAX Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col + 9, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 10, round_number(
                    grand_total1), border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total2), border_top_bot_dec)
                printing_row += 1

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'E' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority And Tax Class', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Purchase', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Purchase', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1

            if print_type == 'Source':
                sortedsummaries = sorted(summaries, key=itemgetter('class', 'code'))
                l_class = 0
                l_code = ''
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']
                        l_code = summ['code']

                    if l_class == summ['class'] and l_code == summ['code']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        try:
                            curr = Currency.objects.get(code=l_code)
                            # decimal_place = get_decimal_place(curr)
                            is_decimal = curr.is_decimal
                        except:
                            is_decimal = True
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, l_class, num_format)
                        worksheet.write(printing_row, printing_col + 2, l_code)
                        worksheet.write(printing_row, printing_col + 3, round_number(
                            total1), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total2), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            total3), dec_format if is_decimal else num_format)
                        printing_row += 1
                        l_class = summ['class']
                        l_code = summ['code']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                try:
                    curr = Currency.objects.get(code=l_code)
                    is_decimal = curr.is_decimal
                except:
                    is_decimal = True

                if len(sortedsummaries):
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, l_class, num_format)
                    worksheet.write(printing_row, printing_col + 2, l_code)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        total1), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total2), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        total3), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = 0
                total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                        worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                        worksheet.write(printing_row, printing_col + 3, summ['code'])
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total2), dec_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            total3), dec_format)
                        printing_row += 1
                        l_class = summ['class']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                    worksheet.write(printing_row, printing_col + 3, summ['code'])
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total2), dec_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        total3), dec_format)
                    printing_row += 1
            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                l_class = 0
                total1 = total2 = total3 = 0
                i = 0
                for summ in sortedsummaries:
                    if i == 0:
                        i += 1
                        l_class = summ['class']

                    if l_class == summ['class']:
                        total1 += summ['summary1']
                        total2 += summ['summary2']
                        total3 += summ['summary3']
                    else:
                        worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                        worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                        worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                        worksheet.write(printing_row, printing_col + 3, round_number(
                            total1), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 4, round_number(
                            total2), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 5, round_number(
                            total3), dec_format if is_decimal_f else num_format)
                        printing_row += 1
                        l_class = summ['class']
                        total1 = summ['summary1']
                        total2 = summ['summary2']
                        total3 = summ['summary3']
                if len(sortedsummaries):
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[l_class] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, l_class, num_format)
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        total1), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        total2), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        total3), dec_format if is_decimal_f else num_format)
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

        com_curr = ''
        str_tax_reporting = ''
        # decimal_place_f = get_decimal_place(company.currency)
        # decimal_place = "%.2f"
        is_decimal_f = company.currency.is_decimal
        is_decimal = True

        # Header
        if print_type == 'Source':
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Customer Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Exchange Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Sales', center_line)
            worksheet.write(11, 9, 'Tax Base', center_line)
            worksheet.write(11, 10, 'Tax Amount', center_line)

        elif print_type == 'Tax Reporting':
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Customer Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Sales', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Tax Base', center_line)
            worksheet.write(11, 11, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:L10', '------Tax Reporting-----', center_bold)

            com_curr = 'SGD'
            str_tax_reporting = "Tax Reporting Currency:"
        else:
            worksheet.write(11, 0, 'Customer No.', center_line)
            worksheet.write(11, 1, 'Customer Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Sales', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Sales', center_line)
            worksheet.write(11, 11, 'Tax Base', center_line)
            worksheet.write(11, 12, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:M10', '--------------Functional------------', center_bold)

        worksheet.set_column(0, 12, 18)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Source':
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.select_related('customer').filter(id__in=journal_ids).order_by('customer_id')

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

            tax_class = 0
            summaries = []
            grand_total1 = grand_total2 = 0

            if print_type == 'Source':
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    currency_printed = False
                    worksheet.write(printing_row, printing_col, 'Source Currency')
                    worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                    printing_row += 1

                    journal_by_curr = all_journals.filter(currency_id=currency['id'])
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_curr
                                                                ).order_by('tax__number', 'journal__document_date', 'journal_id')\
                        .select_related('journal', 'journal__customer', 'tax')\
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
                                column2 = trx.journal.customer.name[:15]
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

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
                                column2 = trx.journal.customer.name[:15]
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)
                                
                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = trx.journal.total_amount * -1
                                else:
                                    total_amount = trx.journal.total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class,
                                               'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                               'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                
                                worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                tax_base += trx.base_tax_amount * -1
                                tax_amount += trx.tax_amount * -1
                                # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                            else:
                                tax_base += trx.base_tax_amount
                                tax_amount += trx.tax_amount
                                # tax_cl_base_total += round_number(trx.base_tax_amount)
                                # tax_cl_tax_total += round_number(trx.tax_amount)
                        index += 1

                    if currency_printed:
                        if index != 0:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                        if tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)

                        worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                        worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 9, round_number(
                            tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

                        subtotal1 += tax_cl_source_total
                        subtotal2 += tax_cl_base_total
                        subtotal3 += tax_cl_tax_total

                        worksheet.write(printing_row, printing_col + 8, 'Total ' + currency['code'] + ' :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, round_number(
                            subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

                        tax_class = 0
                        grand_total1 += subtotal2
                        grand_total2 += subtotal3

                    currency['summary1'] = subtotal1
                    currency['summary2'] = subtotal2
                    currency['summary3'] = subtotal3

            else:  # Tax reporting currency
                subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                            journal__in=all_journals
                                                            ).order_by('tax__number', 'journal__document_date', 'journal_id')\
                    .select_related('journal', 'journal__customer', 'tax')\
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
                            column2 = trx.journal.customer.name[:15]
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = trx.exchange_rate
                        if trx.tax:
                            tax_cl = trx.tax.number
                            tax_class = trx.tax.number
                        else:
                            tax_cl = 0
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']
                        tax_rate = int(trx.tax.rate)

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
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
                                column6 = exchange_rate
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        if print_type == 'Functional':
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                s_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                total_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_base), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 12, round_number(
                                tax_amount), dec_format if is_decimal_f else num_format)
                            printing_row += 1
                        else:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_base), dec_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_amount), dec_format)
                            printing_row += 1

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

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
                            column2 = trx.journal.customer.name[:15]
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = trx.exchange_rate
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        tax_rate = int(trx.tax.rate)
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
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
                                column6 = exchange_rate
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if tax_cl != tax_class and tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': 'SGD',
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)

                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_base_total), border_top_bot_dec)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_tax_total), border_top_bot_dec)
                                printing_row += 1

                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)
                    elif index > 0:
                        last_journal_id = trx.journal.id
                        # decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        if tax_cl != tax_class and tax_class != 0:
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    s_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    total_amount), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_base), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_amount), dec_format if is_decimal_f else num_format)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_base), dec_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_amount), dec_format)
                                printing_row += 1
                            
                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            total_amount = trx.journal.total_amount
                            if print_type == 'Functional' and com_curr != currency_code:
                                total_amount = (total_amount * trx.exchange_rate)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                            tax_base = 0
                            tax_amount = 0
                            tax_rate = int(trx.tax.rate)

                            summery_obj = {'class': tax_class,
                                           'code': 'SGD',
                                           'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)
                            
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_base_total), border_top_bot_dec)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_tax_total), border_top_bot_dec)
                                printing_row += 1

                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        t_base = 0
                        t_amount = 0
                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
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
                                column6 = exchange_rate
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            else:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = (trx.tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional' and com_curr != currency_code:
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
                        # tax_cl_base_total += round_number(t_base)
                        # tax_cl_tax_total += round_number(t_amount)
                    index += 1

                if index != 0:
                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, column3)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, source_code)
                        worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                        worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                        worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            s_amount), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            total_amount), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_base), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            tax_amount), dec_format if is_decimal_f else num_format)
                        printing_row += 1
                    else:
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, column3)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, source_code)
                        worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                        worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                        worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            total_amount), dec_format)
                        worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_base), dec_format)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_amount), dec_format)
                        printing_row += 1

                    tax_cl_source_total += round_number(total_amount)
                    tax_cl_base_total += round_number(tax_base)
                    tax_cl_tax_total += round_number(tax_amount)

                if tax_class != 0:
                    summery_obj = {'class': tax_class, 'code': 'SGD',
                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                    summaries.append(summery_obj)

                if print_type == 'Functional':
                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                    worksheet.write(printing_row, printing_col + 10, round_number(
                        tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 11, round_number(
                        tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 12, round_number(
                        tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    printing_row += 1
                else:
                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                    worksheet.write(printing_row, printing_col + 10, round_number(
                        tax_cl_base_total), border_top_bot_dec)
                    worksheet.write(printing_row, printing_col + 11, round_number(
                        tax_cl_tax_total), border_top_bot_dec)
                    printing_row += 1
                subtotal1 += tax_cl_source_total
                subtotal2 += tax_cl_base_total
                subtotal3 += tax_cl_tax_total
                tax_class = 0
                grand_total1 += subtotal2
                grand_total2 += subtotal3

            # Grand total:
            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 10, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
                worksheet.write(printing_row, printing_col + 11, 'TAX Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col + 9, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 10, round_number(
                    grand_total1), border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total2), border_top_bot_dec)
                printing_row += 1

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'E' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority And Tax Class', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Sales', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Sales', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1

            if print_type == 'Source':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    try:
                        curr = Currency.objects.get(code=summ['code'])
                        # decimal_place = get_decimal_place(curr)
                        is_decimal = curr.is_decimal
                    except:
                        decimal_place = "%.2f"
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, str(summ['class']))
                    worksheet.write(printing_row, printing_col + 2, summ['code'])
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        summ['summary1']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        summ['summary2']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        summ['summary3']), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[summ['class']] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, str(summ['class']))
                    worksheet.write(printing_row, printing_col + 3, summ['code'], right_line)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        summ['summary2']), dec_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        summ['summary3']), dec_format)
                    printing_row += 1

            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[summ['class']] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, str(summ['class']))
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        summ['summary1']), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        summ['summary2']), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        summ['summary3']), dec_format if is_decimal_f else num_format)
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

        com_curr = ''
        str_tax_reporting = ''
        # decimal_place_f = get_decimal_place(company.currency)
        # decimal_place = "%.2f"
        is_decimal_f = company.currency.is_decimal
        is_decimal = True

        # Header
        if print_type == 'Source':
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Vendor Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Exchange Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Purchase', center_line)
            worksheet.write(11, 9, 'Tax Base', center_line)
            worksheet.write(11, 10, 'Tax Amount', center_line)

        elif print_type == 'Tax Reporting':
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Vendor Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Purchase', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Tax Base', center_line)
            worksheet.write(11, 11, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:L10', '------Tax Reporting-----', center_bold)

            com_curr = 'SGD'
            str_tax_reporting = "Tax Reporting Currency:"
        else:
            worksheet.write(11, 0, 'Vendor No.', center_line)
            worksheet.write(11, 1, 'Vendor Name', center_line)
            worksheet.write(11, 2, 'Document Date', center_line)
            worksheet.write(11, 3, 'Document Number', center_line)
            worksheet.write(11, 4, 'Source code', center_line)
            worksheet.write(11, 5, 'Tax Rept. Exch. Rate', center_line)
            worksheet.write(11, 6, 'Tax Class', center_line)
            worksheet.write(11, 7, 'Tax Rate', center_line)
            worksheet.write(11, 8, 'Purchase', center_line)
            worksheet.write(11, 9, 'Currency', center_line)
            worksheet.write(11, 10, 'Purchase', center_line)
            worksheet.write(11, 11, 'Tax Base', center_line)
            worksheet.write(11, 12, 'Tax Amount', center_line)
            worksheet.merge_range('I10:J10', '-------Source------', center_bold)
            worksheet.merge_range('K10:M10', '--------------Functional------------', center_bold)

        worksheet.set_column(0, 12, 18)

        if tax_authority == 'GSTDOS' or tax_authority == 'GSTSGD':
            worksheet.write(12, 0, 'Tax Authority')
            worksheet.write(12, 1, ': [GSTDOS] to [GSTDOS]')
            worksheet.write(12, 4, str_tax_reporting)
            worksheet.write(12, 5, com_curr)

            printing_row = 14
            printing_col = 0

            if print_type == 'Source':
                all_journals = Journal.objects.select_related('currency').filter(id__in=journal_ids).order_by('currency_id')
            else:
                all_journals = Journal.objects.select_related('supplier').filter(id__in=journal_ids).order_by('supplier_id')

            transaction_currency = all_journals.values('currency_id').distinct()
            currencies = []
            last_currency = None
            for trans_curr in transaction_currency:
                currency_id = trans_curr.get('currency_id')
                if currency_id != last_currency:
                    curr_obj = {'id': currency_id, 'code': Currency.objects.filter(pk=currency_id).values('code').first().get('code'),
                                'summary1': 0, 'summary2': 0, 'summary3': 0}
                    currencies.append(curr_obj)
                    last_currency = currency_id

            tax_class = 0
            summaries = []
            grand_total1 = grand_total2 = 0

            if print_type == 'Source':
                for currency in currencies:
                    subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0
                    currency_printed = False
                    worksheet.write(printing_row, printing_col, 'Source Currency')
                    worksheet.write(printing_row, printing_col + 1, ': ' + currency['code'])
                    printing_row += 1

                    journal_by_curr = all_journals.filter(currency_id=currency['id'])
                    all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                                journal__in=journal_by_curr
                                                                ).order_by('tax__number', 'journal__document_date', 'journal_id')\
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
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name[:15] if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                                tax_class = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)

                        if last_journal_id != trx.journal.id:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                                source_code = 'AP-IN'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                                source_code = 'AP-DB'
                            elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                source_code = 'AP-CR'
                            else:
                                source_code = 'AP-PY'
                            try:
                                column1 = trx.journal.supplier.code
                                column2 = trx.journal.supplier.name if trx.journal.supplier.name else ''
                                column4 = trx.journal.document_number if trx.journal.document_number else ''
                            except:
                                column1 = ''
                                column2 = trx.journal.name
                                column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                    else trx.journal.reference if trx.journal.reference else ''
                            column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                            column6 = trx.exchange_rate
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            tax_rate = int(trx.tax.rate)

                            total_amount = trx.journal.total_amount
                            tax_base = trx.base_tax_amount
                            tax_amount = trx.tax_amount

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                                tax_base = -1 * tax_base
                                tax_amount = -1 * tax_amount

                            if tax_cl != tax_class and tax_class != 0:
                                summery_obj = {'class': tax_class,
                                            'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                            'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)

                                worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl
                            # tax_cl_source_total += round_number(total_amount)
                            # tax_cl_base_total += round_number(tax_base)
                            # tax_cl_tax_total += round_number(tax_amount)
                        elif index > 0:
                            last_journal_id = trx.journal.id
                            # decimal_place = get_decimal_place(trx.journal.currency)
                            is_decimal = trx.journal.currency.is_decimal
                            if trx.tax:
                                tax_cl = trx.tax.number
                            else:
                                tax_cl = 0
                            if tax_cl != tax_class and tax_class != 0:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_base), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_amount), dec_format if is_decimal else num_format)
                                printing_row += 1

                                tax_cl_source_total += round_number(total_amount)
                                tax_cl_base_total += round_number(tax_base)
                                tax_cl_tax_total += round_number(tax_amount)

                                if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                    total_amount = trx.journal.total_amount * -1
                                else:
                                    total_amount = trx.journal.total_amount
                                tax_base = 0
                                tax_amount = 0
                                tax_rate = int(trx.tax.rate)

                                summery_obj = {'class': tax_class,
                                               'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                               'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                                summaries.append(summery_obj)
                                
                                worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 9, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                                printing_row += 1

                                tax_class = tax_cl
                                subtotal1 += tax_cl_source_total
                                subtotal2 += tax_cl_base_total
                                subtotal3 += tax_cl_tax_total
                                tax_cl_source_total = 0
                                tax_cl_base_total = 0
                                tax_cl_tax_total = 0
                            else:
                                tax_class = tax_cl

                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                tax_base += trx.base_tax_amount * -1
                                tax_amount += trx.tax_amount * -1
                                # tax_cl_base_total += round_number(trx.base_tax_amount * -1)
                                # tax_cl_tax_total += round_number(trx.tax_amount * -1)
                            else:
                                tax_base += trx.base_tax_amount
                                tax_amount += trx.tax_amount
                                # tax_cl_base_total += round_number(trx.base_tax_amount)
                                # tax_cl_tax_total += round_number(trx.tax_amount)
                        index += 1

                    if currency_printed:
                        if index != 0:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, round_number(
                                tax_base), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_amount), dec_format if is_decimal else num_format)
                            printing_row += 1

                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                        if tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': Currency.objects.filter(pk=currency['id']).values('code').first().get('code'),
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)

                        worksheet.write(printing_row, printing_col + 6, transaction_type + ' ' + str(tax_class), border_top_bot)
                        worksheet.write(printing_row, printing_col + 7, 'Total ' + currency['code'] + ' :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            tax_cl_source_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 9, round_number(
                            tax_cl_base_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_cl_tax_total), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

                        subtotal1 += tax_cl_source_total
                        subtotal2 += tax_cl_base_total
                        subtotal3 += tax_cl_tax_total

                        worksheet.write(printing_row, printing_col + 8, 'Total ' + currency['code'] + ' :', border_top_bot)
                        worksheet.write(printing_row, printing_col + 9, round_number(
                            subtotal2), border_top_bot_dec if is_decimal else border_top_bot_num)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            subtotal3), border_top_bot_dec if is_decimal else border_top_bot_num)
                        printing_row += 1

                        tax_class = 0
                        grand_total1 += subtotal2
                        grand_total2 += subtotal3

            else:  # Tax reporting currency & functional currency
                subtotal1 = subtotal2 = subtotal3 = tax_cl_source_total = tax_cl_base_total = tax_cl_tax_total = 0

                all_transactions = Transaction.objects.filter(company_id=company_id, is_hidden=0,
                                                            journal__in=all_journals
                                                            ).order_by('tax__number', 'journal__supplier_id', 'journal_id')\
                    .select_related('journal', 'journal__supplier', 'tax')\
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
                            source_code = 'AP-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AP-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AP-CR'
                        else:
                            source_code = 'AP-PY'
                        try:
                            column1 = trx.journal.supplier.code
                            column2 = trx.journal.supplier.name[:15] if trx.journal.supplier.name else ''
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = trx.exchange_rate
                        if trx.tax:
                            tax_cl = trx.tax.number
                            tax_class = trx.tax.number
                        else:
                            tax_cl = 0
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']
                        tax_rate = int(trx.tax.rate)

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
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
                                column6 = exchange_rate
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)

                    if last_journal_id != trx.journal.id:
                        if print_type == 'Functional':
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                s_amount), dec_format if is_decimal else num_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                total_amount), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_base), dec_format if is_decimal_f else num_format)
                            worksheet.write(printing_row, printing_col + 12, round_number(
                                tax_amount), dec_format if is_decimal_f else num_format)
                            printing_row += 1
                        else:
                            worksheet.write(printing_row, printing_col, column1)
                            worksheet.write(printing_row, printing_col + 1, column2)
                            worksheet.write(printing_row, printing_col + 2, column3)
                            worksheet.write(printing_row, printing_col + 3, column4)
                            worksheet.write(printing_row, printing_col + 4, source_code)
                            worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                            worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                            worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                            worksheet.write(printing_row, printing_col + 8, round_number(
                                total_amount), dec_format)
                            worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                            worksheet.write(printing_row, printing_col + 10, round_number(
                                tax_base), dec_format)
                            worksheet.write(printing_row, printing_col + 11, round_number(
                                tax_amount), dec_format)
                            printing_row += 1

                        tax_cl_source_total += round_number(total_amount)
                        tax_cl_base_total += round_number(tax_base)
                        tax_cl_tax_total += round_number(tax_amount)

                        last_journal_id = trx.journal.id
                        # decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Invoice']:
                            source_code = 'AP-IN'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                            source_code = 'AP-DB'
                        elif trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            source_code = 'AP-CR'
                        else:
                            source_code = 'AP-PY'
                        try:
                            column1 = trx.journal.supplier.code
                            column2 = trx.journal.supplier.name[:15] if trx.journal.supplier.name else ''
                            column4 = trx.journal.document_number if trx.journal.document_number else ''
                        except:
                            column1 = ''
                            column2 = trx.journal.name
                            column4 = trx.journal.invoice_number if trx.journal.invoice_number \
                                else trx.journal.reference if trx.journal.reference else ''
                        column3 = trx.journal.document_date.strftime('%d/%m/%Y')
                        column6 = trx.exchange_rate
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        tax_rate = int(trx.tax.rate)
                        try:
                            currency_code = trx.currency.code  # currency['code']
                        except:
                            currency_code = trx.journal.currency.code  # currency['code']

                        s_amount = trx.journal.total_amount
                        total_amount = trx.journal.total_amount
                        tax_base = trx.base_tax_amount
                        tax_amount = trx.tax_amount

                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = tax_amount * exchange_rate
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
                                column6 = exchange_rate
                                tax_base = (tax_base * exchange_rate)
                                tax_amount = (tax_amount * exchange_rate)
                            else:
                                tax_base = (tax_base * trx.exchange_rate)
                                tax_amount = (tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional' and com_curr != currency_code:
                            tax_base = (tax_base * trx.exchange_rate)
                            tax_amount = (tax_amount * trx.exchange_rate)
                            total_amount = (total_amount * trx.exchange_rate)

                        if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount = -1 * total_amount
                            tax_base = -1 * tax_base
                            tax_amount = -1 * tax_amount
                            s_amount = -1 * s_amount

                        if tax_cl != tax_class and tax_class != 0:
                            summery_obj = {'class': tax_class,
                                        'code': 'SGD',
                                        'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)

                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_base_total), border_top_bot_dec)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_tax_total), border_top_bot_dec)
                                printing_row += 1
                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        # tax_cl_source_total += round_number(total_amount)
                        # tax_cl_base_total += round_number(tax_base)
                        # tax_cl_tax_total += round_number(tax_amount)
                    elif index > 0:
                        last_journal_id = trx.journal.id
                        # decimal_place = get_decimal_place(trx.journal.currency)
                        is_decimal = trx.journal.currency.is_decimal
                        if trx.tax:
                            tax_cl = trx.tax.number
                        else:
                            tax_cl = 0
                        if tax_cl != tax_class and tax_class != 0:
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    s_amount), dec_format if is_decimal else num_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    total_amount), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_base), dec_format if is_decimal_f else num_format)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_amount), dec_format if is_decimal_f else num_format)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col, column1)
                                worksheet.write(printing_row, printing_col + 1, column2)
                                worksheet.write(printing_row, printing_col + 2, column3)
                                worksheet.write(printing_row, printing_col + 3, column4)
                                worksheet.write(printing_row, printing_col + 4, source_code)
                                worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                                worksheet.write(printing_row, printing_col + 6, int(tax_class), num_format)
                                worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                                worksheet.write(printing_row, printing_col + 8, round_number(
                                    total_amount), dec_format)
                                worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_base), dec_format)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_amount), dec_format)
                                printing_row += 1
                                
                            tax_cl_source_total += round_number(total_amount)
                            tax_cl_base_total += round_number(tax_base)
                            tax_cl_tax_total += round_number(tax_amount)

                            total_amount = trx.journal.total_amount
                            if print_type == 'Functional' and com_curr != currency_code:
                                total_amount = (total_amount * trx.exchange_rate)
                            if trx.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                total_amount = -1 * total_amount
                            tax_base = 0
                            tax_amount = 0
                            tax_rate = int(trx.tax.rate)

                            summery_obj = {'class': tax_class,
                                           'code': 'SGD',
                                           'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                            summaries.append(summery_obj)
                            
                            if print_type == 'Functional':
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                worksheet.write(printing_row, printing_col + 12, round_number(
                                    tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                                printing_row += 1
                            else:
                                worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                                worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                                worksheet.write(printing_row, printing_col + 10, round_number(
                                    tax_cl_base_total), border_top_bot_dec)
                                worksheet.write(printing_row, printing_col + 11, round_number(
                                    tax_cl_tax_total), border_top_bot_dec)
                                printing_row += 1
                            tax_class = tax_cl
                            subtotal1 += tax_cl_source_total
                            subtotal2 += tax_cl_base_total
                            subtotal3 += tax_cl_tax_total
                            tax_cl_source_total = 0
                            tax_cl_base_total = 0
                            tax_cl_tax_total = 0
                        else:
                            tax_class = tax_cl
                        t_base = 0
                        t_amount = 0
                        if print_type == 'Tax Reporting':
                            from_currency = trx.currency_id
                            to_currency = Currency.objects.get(is_hidden=False, code='SGD').id
                            if trx.journal.currency_id == to_currency:
                                exchange_rate = Decimal('1.00000000')
                                column6 = round_number(exchange_rate, 8)
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
                                column6 = exchange_rate
                                t_base = (trx.base_tax_amount * exchange_rate)
                                t_amount = (trx.tax_amount * exchange_rate)
                            else:
                                t_base = (trx.base_tax_amount * trx.exchange_rate)
                                t_amount = (trx.tax_amount * trx.exchange_rate)
                        elif print_type == 'Functional' and com_curr != currency_code:
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
                        # tax_cl_base_total += round_number(t_base)
                        # tax_cl_tax_total += round_number(t_amount)
                    index += 1

                if index != 0:
                    if print_type == 'Functional':
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, column3)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, source_code)
                        worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                        worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                        worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            s_amount), dec_format if is_decimal else num_format)
                        worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            total_amount), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_base), dec_format if is_decimal_f else num_format)
                        worksheet.write(printing_row, printing_col + 12, round_number(
                            tax_amount), dec_format if is_decimal_f else num_format)
                        printing_row += 1
                    else:
                        worksheet.write(printing_row, printing_col, column1)
                        worksheet.write(printing_row, printing_col + 1, column2)
                        worksheet.write(printing_row, printing_col + 2, column3)
                        worksheet.write(printing_row, printing_col + 3, column4)
                        worksheet.write(printing_row, printing_col + 4, source_code)
                        worksheet.write(printing_row, printing_col + 5, column6, rate_format)
                        worksheet.write(printing_row, printing_col + 6, int(tax_cl), num_format)
                        worksheet.write(printing_row, printing_col + 7, tax_rate, rate_format)
                        worksheet.write(printing_row, printing_col + 8, round_number(
                            total_amount), dec_format)
                        worksheet.write(printing_row, printing_col + 9, currency_code, right_line)
                        worksheet.write(printing_row, printing_col + 10, round_number(
                            tax_base), dec_format)
                        worksheet.write(printing_row, printing_col + 11, round_number(
                            tax_amount), dec_format)
                        printing_row += 1

                    tax_cl_source_total += round_number(total_amount)
                    tax_cl_base_total += round_number(tax_base)
                    tax_cl_tax_total += round_number(tax_amount)

                if tax_class != 0:
                    summery_obj = {'class': tax_class, 'code': 'SGD',
                                'summary1': tax_cl_source_total, 'summary2': tax_cl_base_total, 'summary3': tax_cl_tax_total}
                    summaries.append(summery_obj)

                if print_type == 'Functional':
                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                    worksheet.write(printing_row, printing_col + 10, round_number(
                        tax_cl_source_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 11, round_number(
                        tax_cl_base_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    worksheet.write(printing_row, printing_col + 12, round_number(
                        tax_cl_tax_total), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                    printing_row += 1
                else:
                    worksheet.write(printing_row, printing_col + 8, transaction_type + ' ' + str(tax_class), border_top_bot)
                    worksheet.write(printing_row, printing_col + 9, 'Total :', border_top_bot)
                    worksheet.write(printing_row, printing_col + 10, round_number(
                        tax_cl_base_total), border_top_bot_dec)
                    worksheet.write(printing_row, printing_col + 11, round_number(
                        tax_cl_tax_total), border_top_bot_dec)
                    printing_row += 1
                subtotal1 += tax_cl_source_total
                subtotal2 += tax_cl_base_total
                subtotal3 += tax_cl_tax_total
                tax_class = 0
                grand_total1 += subtotal2
                grand_total2 += subtotal3

            # Grand total:
            if print_type == 'Functional':
                worksheet.write(printing_row, printing_col + 10, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total1), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
                worksheet.write(printing_row, printing_col + 11, 'TAX Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 12, round_number(
                    grand_total2), border_top_bot_dec if is_decimal_f else border_top_bot_num)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col + 9, 'GSTDOS Total :', border_top_bot)
                worksheet.write(printing_row, printing_col + 10, round_number(
                    grand_total1), border_top_bot_dec)
                worksheet.write(printing_row, printing_col + 11, round_number(
                    grand_total2), border_top_bot_dec)
                printing_row += 1

            printing_row += 5
            m_range = 'A' + str(printing_row) + ':' + 'E' + str(printing_row)
            worksheet.merge_range(m_range, 'Summary By Tax Authority And Tax Class', merge_format)
            printing_row += 2

            if print_type == 'Source':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Purchase', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            elif print_type == 'Tax Reporting':
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Currency', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1
            else:
                worksheet.write(printing_row, printing_col, 'Tax Authority', center_line)
                worksheet.write(printing_row, printing_col + 1, 'Tax Class Name', center_line)
                worksheet.write(printing_row, printing_col + 2, 'Tax Class', center_line)
                worksheet.write(printing_row, printing_col + 3, 'Purchase', center_line)
                worksheet.write(printing_row, printing_col + 4, 'Tax Base', center_line)
                worksheet.write(printing_row, printing_col + 5, 'Tax Amount', center_line)
                printing_row += 1

            if print_type == 'Source':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    try:
                        curr = Currency.objects.get(code=summ['code'])
                        # decimal_place = get_decimal_place(curr)
                        is_decimal = curr.is_decimal
                    except:
                        decimal_place = "%.2f"
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, str(summ['class']))
                    worksheet.write(printing_row, printing_col + 2, summ['code'])
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        summ['summary1']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        summ['summary2']), dec_format if is_decimal else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        summ['summary3']), dec_format if is_decimal else num_format)
                    printing_row += 1
            elif print_type == 'Tax Reporting':
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[summ['class']] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, str(summ['class']))
                    worksheet.write(printing_row, printing_col + 3, summ['code'], right_line)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        summ['summary2']), dec_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        summ['summary3']), dec_format)
                    printing_row += 1

            else:
                sortedsummaries = sorted(summaries, key=itemgetter('class'))
                for summ in sortedsummaries:
                    worksheet.write(printing_row, printing_col, 'GSTDOS GSTDOS')
                    worksheet.write(printing_row, printing_col + 1, TAX_TRACK_CLASS_DICT[summ['class']] + '        Total')
                    worksheet.write(printing_row, printing_col + 2, str(summ['class']))
                    worksheet.write(printing_row, printing_col + 3, round_number(
                        summ['summary1']), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 4, round_number(
                        summ['summary2']), dec_format if is_decimal_f else num_format)
                    worksheet.write(printing_row, printing_col + 5, round_number(
                        summ['summary3']), dec_format if is_decimal_f else num_format)
                    printing_row += 1

            printing_row += 2
            worksheet.write(printing_row, printing_col, '1 authority printed')

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
