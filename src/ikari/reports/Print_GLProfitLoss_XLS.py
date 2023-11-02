import calendar
import datetime
from decimal import Decimal
import xlsxwriter
from django.db.models import Q
from accounts.models import Account, AccountHistory, ReportGroup
from companies.models import Company, CostCenters
from transactions.models import Transaction
from utilities.common import wrap_text_xls, get_segment_filter_range
from utilities.constants import STATUS_TYPE_DICT, BALANCE_TYPE_DICT, REPORT_TYPE, ACCOUNT_TYPE_DICT, SEGMENT_FILTER_DICT


class Print_GLProfitLoss_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        company = Company.objects.get(pk=company_id)
        if SEGMENT_FILTER_DICT['Account'] == filter_type and company.use_segment:  # account
            return self.WriteToExcelbyAccount(company_id, issue_date, report_type, filter_type, from_val, to_val)
        elif company.use_segment:
            return self.WriteToExcelbySegment(company_id, issue_date, report_type, filter_type, from_val, to_val)
        else:
            return self.WriteToExcelForAccount(company_id, issue_date, report_type, filter_type, from_val, to_val)

    def WriteToExcelbyAccount(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Profit_Loss")
        row = 10
        col = 0
        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'white'})
        right_line = workbook.add_format({
            'align': 'right'
        })
        center = workbook.add_format({
            'align': 'center'
        })
        center_line = workbook.add_format({
            'align': 'center',
            'bottom': 1
        })
        border_top_bot = workbook.add_format({
            'align': 'right',
            'bottom': 1,
            'top': 1
        })

        border_bot = workbook.add_format({
            'align': 'right',
            'top': 1
        })
        array_data = str(issue_date).split('-')
        month = int(array_data[1])
        year = int(array_data[0])
        issue_to = datetime.date(year, month,
                                 calendar.monthrange(year, month)[1])
        company = Company.objects.get(pk=company_id)
        format_date_report = str(issue_to.month) + '/' + str(issue_to.day) + '/' + str(issue_to.year)
        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'TRADING AND PROFIT AND LOSS ACCOUNT', merge_format)
        worksheet.merge_range('A5:C5', 'FOR THE MONTH OF ' + format_date_report, merge_format)
        worksheet.write(6, 2, 'CURRENT', center)
        worksheet.write(6, 3, 'YEAR TO', center)
        worksheet.write(7, 2, 'MONTH', center)
        worksheet.write(7, 3, 'DATE', center)
        worksheet.write(8, 2, company.currency.code, center_line)
        worksheet.write(8, 3, company.currency.code, center_line)
        worksheet.set_column(0, 0, 50)
        worksheet.set_column(1, 0, 20)
        filter_array = []
        filter_array.append('PL-NETSALE')
        filter_array.append('PL-PURCH')
        filter_array.append('PL-COGS')
        filter_array.append('PL-REVENUE')
        filter_array.append('PL-EXPENSE')
        filter_array.append('PL-EXC')
        total_good_sold_change = total_good_sold_balance = 0
        total_profit_change = total_profit_balance = 0
        total_revenue_change = total_revenue_balance = 0
        total_net_profit_change = total_net_profit_balance = 0
        total_net_profit_tax_change = total_net_profit_tax_balance = 0
        prov_posted_amount = 0
        FlagReport = 1
        test = 1
        is_stock_closing = 0
        acc_stock = ''
        name_stock = ''
        sum_net_stock = 0
        sum_balance_stock = 0
        is_4550_grouped = False
        custom_acc_grp = createCustomAccGroupList(company_id)

        for j, mFilter in enumerate(filter_array):
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Income Statement']),
                                                       profit_loss_group__code=mFilter).order_by('account_segment').distinct()
            if account_item_list:
                if mFilter == 'PL-COGS':
                    worksheet.write(row, col, 'LESS : COST OF GOODS SOLD')
                    row += 1
                elif mFilter == 'PL-EXPENSE':
                    row += 1
                    worksheet.write(row, col, 'LESS : EXPENDITURE')
                    row += 1
                elif mFilter == 'PL-REVENUE':
                    row -= 1
                    worksheet.write(row, col, 'ADD: OTHER INCOME')
                    row += 1
            total_change = total_balance = 0
            sum_change = sum_balance = 0
            total_sum_change = total_sum_balance = 0
            custom_acc_code = None
            last_seg_acc = last_seg_name = ''
            seg_change_total = 0
            seg_balance_total = 0
            pl_seg_change_total = 0
            pl_seg_balance_total = 0
            skip_count = 0
            last_segment = CostCenters.objects.filter(company_id=company_id).last()
            segment_code = last_segment.code if last_segment else ''
            segment_count = CostCenters.objects.filter(company_id=company_id).count()
            count = len(account_item_list)
            account_counter = 0
            if account_item_list:
                for i, mAccount in enumerate(account_item_list):
                    account_counter += 1
                    item_account_q = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                   account_id=mAccount.id, period_month__exact=int(array_data[1]),
                                                                   period_year__exact=array_data[0])
                    item_account = item_account_q.filter(Q(source_currency_id=company.currency_id) | Q(source_currency_id__isnull=True))
                    sum_change = sum_balance = 0
                    if item_account:
                        prov_posted_amount_per_account = 0
                        for j, iAccount in enumerate(item_account):
                            if report_type == dict(REPORT_TYPE)['Provisional']:
                                prov_posted_amount_per_account = getProvisionalPostedAmount(company_id, array_data[0],
                                                                                            array_data[1], mFilter,
                                                                                            mAccount.id,
                                                                                            iAccount.source_currency_id)
                            sum_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                            sum_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)
                            total_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                            total_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)

                        if FlagReport == 1:
                            if mFilter == 'PL-EXC':
                                if skip_count == 0:
                                    last_seg_acc = mAccount.account_segment
                                    last_seg_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    pl_seg_change_total = 0
                                    pl_seg_balance_total = 0
                                if last_seg_acc == mAccount.account_segment:
                                    pl_seg_change_total += sum_change
                                    pl_seg_balance_total += sum_balance
                                    skip_count += 1
                                    if skip_count == segment_count or account_counter == count - 1:  # print last item
                                        last_seg_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                                        worksheet.write(row, col + 2, wrap_text_xls(pl_seg_change_total, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(pl_seg_balance_total, mFilter), right_line)
                                        skip_count = 0
                                else:
                                    worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                                    worksheet.write(row, col + 2, wrap_text_xls(pl_seg_change_total, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(pl_seg_balance_total, mFilter), right_line)
                                    last_seg_acc = mAccount.account_segment
                                    last_seg_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    pl_seg_change_total = sum_change
                                    pl_seg_balance_total = sum_balance
                                    if account_counter == count - 1:
                                        row += 1
                                        worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                                        worksheet.write(row, col + 2, wrap_text_xls(pl_seg_change_total, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(pl_seg_balance_total, mFilter), right_line)
                                if len(custom_acc_grp) > 0:
                                    custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        total_sum_change = sum_change
                                        total_sum_balance = sum_balance
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        total_sum_change += sum_change
                                        total_sum_balance += sum_balance
                                        row -= 1
                                    worksheet.write(row, col, custom_acc_code + '    ' + custom_acc['custom_acc_name'])
                                    worksheet.write(row, col + 2, wrap_text_xls(total_sum_change, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_sum_balance, mFilter), right_line)

                            else:
                                if skip_count == 0:
                                    last_seg_acc = mAccount.account_segment
                                    last_seg_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_change_total = 0
                                    seg_balance_total = 0
                                if last_seg_acc == mAccount.account_segment:
                                    seg_change_total += sum_change
                                    seg_balance_total += sum_balance
                                    skip_count += 1
                                    if skip_count == segment_count or account_counter == count - 1:  # print last item
                                        last_seg_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                                        worksheet.write(row, col + 2, wrap_text_xls(seg_change_total, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(seg_balance_total, mFilter), right_line)
                                        skip_count = 0
                                    else:
                                        row -= 1
                                else:
                                    worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                                    worksheet.write(row, col + 2, wrap_text_xls(seg_change_total, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(seg_balance_total, mFilter), right_line)
                                    last_seg_acc = mAccount.account_segment
                                    last_seg_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_change_total = sum_change
                                    seg_balance_total = sum_balance
                                    if account_counter == count - 1 and mFilter != 'PL-EXPENSE':
                                        row += 1
                                        worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                                        worksheet.write(row, col + 2, wrap_text_xls(seg_change_total, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(seg_balance_total, mFilter), right_line)
                                if len(custom_acc_grp) > 0:
                                    custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        total_sum_change = sum_change
                                        total_sum_balance = sum_balance
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        total_sum_change += sum_change
                                        total_sum_balance += sum_balance
                                        row -= 1
                                    worksheet.write(row, col, custom_acc_code + '    ' + custom_acc['custom_acc_name'])
                                    worksheet.write(row, col + 2, wrap_text_xls(total_sum_change, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_sum_balance, mFilter), right_line)
                                if mAccount.code == '4550':
                                    is_stock_closing = 1
                                    acc_stock = mAccount.code
                                    name_stock = mAccount.name
                                    sum_net_stock = sum_change
                                    sum_balance_stock = sum_balance
                            row += 1
                    else:
                        if account_counter == count - 1 and mFilter != 'PL-EXPENSE':
                            # row += 1
                            worksheet.write(row, col, last_seg_acc + '    ' + last_seg_name)
                            worksheet.write(row, col + 2, wrap_text_xls(seg_change_total, mFilter), right_line)
                            worksheet.write(row, col + 3, wrap_text_xls(seg_balance_total, mFilter), right_line)
                            row += 1

            if (mFilter == 'PL-PURCH') | (mFilter == 'PL-COGS'):
                total_good_sold_change += total_change
                total_good_sold_balance += total_balance
            if (mFilter == 'PL-NETSALE'):
                total_profit_change += total_change
                total_profit_balance += total_balance
            if (mFilter == 'PL-COGS'):
                total_profit_change += total_good_sold_change
                total_profit_balance += total_good_sold_balance
            if mFilter == 'PL-REVENUE':
                total_revenue_change = total_profit_change + total_change
                total_revenue_balance = total_profit_balance + total_balance
            if mFilter == 'PL-EXPENSE':
                total_net_profit_change = total_revenue_change + total_change
                total_net_profit_balance = total_revenue_balance + total_balance
            if mFilter == 'PL-EXC':
                total_net_profit_tax_change = total_net_profit_change + total_change
                total_net_profit_tax_balance = total_net_profit_balance + total_balance + Decimal(prov_posted_amount)
            # sum_profit_finish.append(total_net_profit_tax_balance)
            if FlagReport == 1:
                if mFilter == 'PL-PURCH':
                    row = row
                else:
                    if mFilter == 'PL-REVENUE':
                        worksheet.write(row, col, ' OTHER REVENUE  ')
                        worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                        worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                        row += 2
                        worksheet.write(row, col, ' TOTAL REVENUE  ')
                        worksheet.write(row, col + 2, wrap_text_xls(total_revenue_change, mFilter), border_bot)
                        worksheet.write(row, col + 3, wrap_text_xls(total_revenue_balance, mFilter), border_bot)
                    else:
                        if mFilter == 'PL-COGS':
                            if is_stock_closing:
                                if not is_4550_grouped:
                                    row -= 1
                                    worksheet.write(row, col, ' ')
                                    worksheet.write(row, col + 2,
                                                    wrap_text_xls(total_good_sold_change - Decimal(sum_net_stock), mFilter),
                                                    border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(
                                        total_good_sold_balance - Decimal(sum_balance_stock), mFilter), border_bot)
                                    row += 1
                                    worksheet.write(row, col, acc_stock + '    ' + name_stock)
                                    worksheet.write(row, col + 2, wrap_text_xls(sum_net_stock, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(sum_balance_stock, mFilter), right_line)
                                    row += 1

                            worksheet.write(row, col, ' COST OF GOODS SOLD ')
                            worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                            worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                            row += 2
                            worksheet.write(row, col, 'GROSS PROFIT ')
                            worksheet.write(row, col + 2, wrap_text_xls(total_profit_change, 'PL-EXC'), border_bot)
                            worksheet.write(row, col + 3, wrap_text_xls(total_profit_balance, 'PL-EXC'), border_bot)
                            row += 2
                        else:
                            if mFilter == 'PL-EXPENSE':
                                worksheet.write(row, col, 'TOTAL EXPENDITURE        ')
                                worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_top_bot)
                                worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_top_bot)
                                row += 2
                                worksheet.write(row, col, 'NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ')
                                worksheet.write(row, col + 2, wrap_text_xls(total_net_profit_change, 'PL-EXC'), border_bot)
                                worksheet.write(row, col + 3, wrap_text_xls(total_net_profit_balance, 'PL-EXC'), border_bot)
                                row += 1
                            else:
                                if mFilter == 'PL-EXC':
                                    worksheet.write(row, col, 'TOTAL EXCH GAIN/(LOSS) ')
                                    worksheet.write(
                                        row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                                    row += 2

                                    worksheet.write(row, col, 'NET PROFIT/(LOSS) AFTER INCOME TAXES ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_net_profit_tax_change, mFilter),
                                                    border_top_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_net_profit_tax_balance, mFilter),
                                                    border_top_bot)
                                else:
                                    row -= 1
                                    worksheet.write(row, col, 'NET SALES  ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                row += 1
                test += 1
        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def WriteToExcelbySegment(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Profit_Loss")
        row = 3
        col = 0
        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'white'})
        right_line = workbook.add_format({
            'align': 'right'
        })
        center = workbook.add_format({
            'align': 'center'
        })
        center_line = workbook.add_format({
            'align': 'center',
            'bottom': 1
        })
        border_top_bot = workbook.add_format({
            'align': 'right',
            'bottom': 1,
            'top': 1
        })

        border_bot = workbook.add_format({
            'align': 'right',
            'top': 1
        })
        array_data = str(issue_date).split('-')
        month = int(array_data[1])
        year = int(array_data[0])
        issue_to = datetime.date(year, month,
                                 calendar.monthrange(year, month)[1])
        company = Company.objects.get(pk=company_id)
        format_date_report = str(issue_to.month) + '/' + str(issue_to.day) + '/' + str(issue_to.year)
        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'TRADING AND PROFIT AND LOSS ACCOUNT', merge_format)
        worksheet.merge_range('A5:C5', 'FOR THE MONTH OF ' + format_date_report, merge_format)
        worksheet.set_column(0, 0, 50)
        worksheet.set_column(1, 0, 20)
        filter_array = []
        filter_array.append('PL-NETSALE')
        filter_array.append('PL-PURCH')
        filter_array.append('PL-COGS')
        filter_array.append('PL-REVENUE')
        filter_array.append('PL-EXPENSE')
        filter_array.append('PL-EXC')
        total_revenue_change = total_revenue_balance = 0
        total_net_profit_change = total_net_profit_balance = 0
        total_net_profit_tax_change = total_net_profit_tax_balance = 0
        prov_posted_amount = 0
        FlagReport = 1
        test = 1
        is_stock_closing = 0
        acc_stock = ''
        name_stock = ''
        sum_net_stock = 0
        sum_balance_stock = 0
        is_4550_grouped = False
        custom_acc_grp = createCustomAccGroupList(company_id)

        segment_code_range = get_segment_filter_range(company_id, int(from_val), int(to_val), 'id')
        for segment_code in segment_code_range:
            segment = CostCenters.objects.get(pk=segment_code)
            row += 3
            worksheet.write(row, col + 1, segment.name)
            row += 2
            worksheet.write(row, 2, 'CURRENT', center)
            worksheet.write(row, 3, 'YEAR TO', center)
            row += 1
            worksheet.write(row, 2, 'MONTH', center)
            worksheet.write(row, 3, 'DATE', center)
            row += 1
            worksheet.write(row, 2, company.currency.code, center_line)
            worksheet.write(row, 3, company.currency.code, center_line)
            row += 2
            total_profit_change = total_profit_balance = 0
            total_good_sold_change = total_good_sold_balance = 0
            for j, mFilter in enumerate(filter_array):
                account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                           segment_code_id=segment_code,
                                                           account_type=int(ACCOUNT_TYPE_DICT['Income Statement']),
                                                           profit_loss_group__code=mFilter).order_by('code').distinct()
                if account_item_list:
                    if mFilter == 'PL-COGS':
                        worksheet.write(row, col, 'LESS : COST OF GOODS SOLD')
                        row += 2
                    elif mFilter == 'PL-EXPENSE':
                        row += 1
                        worksheet.write(row, col, 'LESS : EXPENDITURE')
                        row += 1
                    elif mFilter == 'PL-REVENUE':
                        row -= 1
                        worksheet.write(row, col, 'ADD: OTHER INCOME')
                        row += 1
                total_change = total_balance = 0
                sum_change = sum_balance = 0
                total_sum_change = total_sum_balance = 0
                custom_acc_code = None
                if account_item_list:
                    for i, mAccount in enumerate(account_item_list):
                        item_account_q = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                       account_id=mAccount.id, period_month__exact=int(array_data[1]),
                                                                       period_year__exact=array_data[0])
                        item_account = item_account_q.filter(Q(source_currency_id=company.currency_id) | Q(source_currency_id__isnull=True))
                        sum_change = sum_balance = 0
                        if item_account:
                            prov_posted_amount_per_account = 0
                            for j, iAccount in enumerate(item_account):
                                if report_type == dict(REPORT_TYPE)['Provisional']:
                                    prov_posted_amount_per_account = getProvisionalPostedAmount(company_id, array_data[0],
                                                                                                array_data[1], mFilter,
                                                                                                mAccount.id,
                                                                                                iAccount.source_currency_id)
                                sum_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                                sum_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)
                                total_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                                total_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)

                            if FlagReport == 1:
                                if mFilter == 'PL-EXC':
                                    worksheet.write(row, col, mAccount.code + '    ' + mAccount.name)
                                    worksheet.write(row, col + 2, wrap_text_xls(sum_change, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(sum_balance, mFilter), right_line)
                                    if len(custom_acc_grp) > 0:
                                        custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                        if custom_acc['custom_acc_code'] != custom_acc_code:
                                            total_sum_change = sum_change
                                            total_sum_balance = sum_balance
                                            custom_acc_code = custom_acc['custom_acc_code']
                                        else:
                                            total_sum_change += sum_change
                                            total_sum_balance += sum_balance
                                            row -= 1
                                        worksheet.write(row, col, custom_acc_code + '    ' + custom_acc['custom_acc_name'])
                                        worksheet.write(row, col + 2, wrap_text_xls(total_sum_change, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(total_sum_balance, mFilter), right_line)

                                else:
                                    worksheet.write(row, col, mAccount.code + '    ' + mAccount.name)
                                    worksheet.write(row, col + 2, wrap_text_xls(sum_change, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(sum_balance, mFilter), right_line)
                                    if len(custom_acc_grp) > 0:
                                        custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                        if custom_acc['custom_acc_code'] != custom_acc_code:
                                            total_sum_change = sum_change
                                            total_sum_balance = sum_balance
                                            custom_acc_code = custom_acc['custom_acc_code']
                                        else:
                                            total_sum_change += sum_change
                                            total_sum_balance += sum_balance
                                            row -= 1
                                        worksheet.write(row, col, custom_acc_code + '    ' + custom_acc['custom_acc_name'])
                                        worksheet.write(row, col + 2, wrap_text_xls(total_sum_change, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(total_sum_balance, mFilter), right_line)
                                    if mAccount.code == '4550':
                                        is_stock_closing = 1
                                        acc_stock = mAccount.code
                                        name_stock = mAccount.name
                                        sum_net_stock = sum_change
                                        sum_balance_stock = sum_balance
                                row += 1

                if (mFilter == 'PL-PURCH') | (mFilter == 'PL-COGS'):
                    total_good_sold_change += total_change
                    total_good_sold_balance += total_balance
                if (mFilter == 'PL-NETSALE'):
                    total_profit_change += total_change
                    total_profit_balance += total_balance
                if (mFilter == 'PL-COGS'):
                    total_profit_change += total_good_sold_change
                    total_profit_balance += total_good_sold_balance
                if mFilter == 'PL-REVENUE':
                    total_revenue_change = total_profit_change + total_change
                    total_revenue_balance = total_profit_balance + total_balance
                if mFilter == 'PL-EXPENSE':
                    total_net_profit_change = total_revenue_change + total_change
                    total_net_profit_balance = total_revenue_balance + total_balance
                if mFilter == 'PL-EXC':
                    total_net_profit_tax_change = total_net_profit_change + total_change
                    total_net_profit_tax_balance = total_net_profit_balance + total_balance + Decimal(prov_posted_amount)
                # sum_profit_finish.append(total_net_profit_tax_balance)
                if FlagReport == 1:
                    if mFilter == 'PL-PURCH':
                        row = row
                    else:
                        if mFilter == 'PL-REVENUE':
                            worksheet.write(row, col, ' OTHER REVENUE  ')
                            worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                            worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                            row += 2
                            worksheet.write(row, col, ' TOTAL REVENUE  ')
                            worksheet.write(row, col + 2, wrap_text_xls(total_revenue_change, mFilter), border_bot)
                            worksheet.write(row, col + 3, wrap_text_xls(total_revenue_balance, mFilter), border_bot)
                        else:
                            if mFilter == 'PL-COGS':
                                if is_stock_closing:
                                    if not is_4550_grouped:
                                        row -= 1
                                        worksheet.write(row, col, ' ')
                                        worksheet.write(row, col + 2,
                                                        wrap_text_xls(total_good_sold_change - Decimal(sum_net_stock), mFilter),
                                                        border_bot)
                                        worksheet.write(row, col + 3, wrap_text_xls(
                                            total_good_sold_balance - Decimal(sum_balance_stock), mFilter), border_bot)
                                        row += 1
                                        worksheet.write(row, col, acc_stock + '    ' + name_stock)
                                        worksheet.write(row, col + 2, wrap_text_xls(sum_net_stock, mFilter), right_line)
                                        worksheet.write(row, col + 3, wrap_text_xls(sum_balance_stock, mFilter), right_line)
                                        row += 1

                                worksheet.write(row, col, ' COST OF GOODS SOLD ')
                                worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                                row += 2
                                worksheet.write(row, col, 'GROSS PROFIT ')
                                worksheet.write(row, col + 2, wrap_text_xls(total_profit_change, 'PL-EXC'), border_bot)
                                worksheet.write(row, col + 3, wrap_text_xls(total_profit_balance, 'PL-EXC'), border_bot)
                                row += 2
                            else:
                                if mFilter == 'PL-EXPENSE':
                                    worksheet.write(row, col, 'TOTAL EXPENDITURE        ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_top_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_top_bot)
                                    row += 2
                                    worksheet.write(row, col, 'NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_net_profit_change, 'PL-EXC'), border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_net_profit_balance, 'PL-EXC'), border_bot)
                                    row += 1
                                else:
                                    if mFilter == 'PL-EXC':
                                        worksheet.write(row, col, 'TOTAL EXCH GAIN/(LOSS) ')
                                        worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                        worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                                        row += 2

                                        worksheet.write(row, col, 'NET PROFIT/(LOSS) AFTER INCOME TAXES ')
                                        worksheet.write(row, col + 2, wrap_text_xls(total_net_profit_tax_change, mFilter),
                                                        border_top_bot)
                                        worksheet.write(row, col + 3, wrap_text_xls(total_net_profit_tax_balance, mFilter),
                                                        border_top_bot)
                                    else:
                                        worksheet.write(row, col, 'NET SALES  ')
                                        worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                        worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                    row += 1
                    test += 1
        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def WriteToExcelForAccount(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Profit_Loss")
        row = 10
        col = 0
        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'white'})
        right_line = workbook.add_format({
            'align': 'right'
        })
        center = workbook.add_format({
            'align': 'center'
        })
        center_line = workbook.add_format({
            'align': 'center',
            'bottom': 1
        })
        border_top_bot = workbook.add_format({
            'align': 'right',
            'bottom': 1,
            'top': 1
        })

        border_bot = workbook.add_format({
            'align': 'right',
            'top': 1
        })
        array_data = str(issue_date).split('-')
        month = int(array_data[1])
        year = int(array_data[0])
        issue_to = datetime.date(year, month,
                                 calendar.monthrange(year, month)[1])
        company = Company.objects.get(pk=company_id)
        format_date_report = str(issue_to.month) + '/' + str(issue_to.day) + '/' + str(issue_to.year)
        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'TRADING AND PROFIT AND LOSS ACCOUNT', merge_format)
        worksheet.merge_range('A5:C5', 'FOR THE MONTH OF ' + format_date_report, merge_format)
        worksheet.write(6, 2, 'CURRENT', center)
        worksheet.write(6, 3, 'YEAR TO', center)
        worksheet.write(7, 2, 'MONTH', center)
        worksheet.write(7, 3, 'DATE', center)
        worksheet.write(8, 2, company.currency.code, center_line)
        worksheet.write(8, 3, company.currency.code, center_line)
        worksheet.set_column(0, 0, 50)
        worksheet.set_column(1, 0, 20)
        filter_array = []
        filter_array.append('PL-NETSALE')
        filter_array.append('PL-PURCH')
        filter_array.append('PL-COGS')
        filter_array.append('PL-REVENUE')
        filter_array.append('PL-EXPENSE')
        filter_array.append('PL-EXC')
        total_good_sold_change = total_good_sold_balance = 0
        total_profit_change = total_profit_balance = 0
        total_revenue_change = total_revenue_balance = 0
        total_net_profit_change = total_net_profit_balance = 0
        total_net_profit_tax_change = total_net_profit_tax_balance = 0
        prov_posted_amount = 0
        FlagReport = 1
        test = 1
        is_stock_closing = 0
        acc_stock = ''
        name_stock = ''
        sum_net_stock = 0
        sum_balance_stock = 0
        is_4550_grouped = False
        custom_acc_grp = createCustomAccGroupList(company_id)

        for j, mFilter in enumerate(filter_array):
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Income Statement']),
                                                       profit_loss_group__code=mFilter).order_by('code').distinct()
            if account_item_list:
                if mFilter == 'PL-COGS':
                    worksheet.write(row, col, 'LESS : COST OF GOODS SOLD')
                    row += 2
                elif mFilter == 'PL-EXPENSE':
                    row += 1
                    worksheet.write(row, col, 'LESS : EXPENDITURE')
                    row += 1
                elif mFilter == 'PL-REVENUE':
                    row -= 1
                    worksheet.write(row, col, 'ADD: OTHER INCOME')
                    row += 1
            total_change = total_balance = 0
            sum_change = sum_balance = 0
            total_sum_change = total_sum_balance = 0
            custom_acc_code = None
            if account_item_list:
                for i, mAccount in enumerate(account_item_list):
                    item_account_q = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                   account_id=mAccount.id, period_month__exact=int(array_data[1]),
                                                                   period_year__exact=array_data[0])
                    item_account = item_account_q.filter(Q(source_currency_id=company.currency_id) | Q(source_currency_id__isnull=True))
                    sum_change = sum_balance = 0
                    if item_account:
                        prov_posted_amount_per_account = 0
                        for j, iAccount in enumerate(item_account):
                            if report_type == dict(REPORT_TYPE)['Provisional']:
                                prov_posted_amount_per_account = getProvisionalPostedAmount(company_id, array_data[0],
                                                                                            array_data[1], mFilter,
                                                                                            mAccount.id,
                                                                                            iAccount.source_currency_id)
                            sum_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                            sum_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)
                            total_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                            total_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)

                        if FlagReport == 1:
                            if mFilter == 'PL-EXC':
                                worksheet.write(row, col, mAccount.code + '    ' + mAccount.name)
                                worksheet.write(row, col + 2, wrap_text_xls(sum_change, mFilter), right_line)
                                worksheet.write(row, col + 3, wrap_text_xls(sum_balance, mFilter), right_line)
                                if len(custom_acc_grp) > 0:
                                    custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        total_sum_change = sum_change
                                        total_sum_balance = sum_balance
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        total_sum_change += sum_change
                                        total_sum_balance += sum_balance
                                        row -= 1
                                    worksheet.write(row, col, custom_acc_code + '    ' + custom_acc['custom_acc_name'])
                                    worksheet.write(row, col + 2, wrap_text_xls(total_sum_change, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_sum_balance, mFilter), right_line)

                            else:
                                worksheet.write(row, col, mAccount.code + '    ' + mAccount.name)
                                worksheet.write(row, col + 2, wrap_text_xls(sum_change, mFilter), right_line)
                                worksheet.write(row, col + 3, wrap_text_xls(sum_balance, mFilter), right_line)
                                if len(custom_acc_grp) > 0:
                                    custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        total_sum_change = sum_change
                                        total_sum_balance = sum_balance
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        total_sum_change += sum_change
                                        total_sum_balance += sum_balance
                                        row -= 1
                                    worksheet.write(row, col, custom_acc_code + '    ' + custom_acc['custom_acc_name'])
                                    worksheet.write(row, col + 2, wrap_text_xls(total_sum_change, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_sum_balance, mFilter), right_line)
                                if mAccount.code == '4550':
                                    is_stock_closing = 1
                                    acc_stock = mAccount.code
                                    name_stock = mAccount.name
                                    sum_net_stock = sum_change
                                    sum_balance_stock = sum_balance
                            row += 1

            if (mFilter == 'PL-PURCH') | (mFilter == 'PL-COGS'):
                total_good_sold_change += total_change
                total_good_sold_balance += total_balance
            if (mFilter == 'PL-NETSALE'):
                total_profit_change += total_change
                total_profit_balance += total_balance
            if (mFilter == 'PL-COGS'):
                total_profit_change += total_good_sold_change
                total_profit_balance += total_good_sold_balance
            if mFilter == 'PL-REVENUE':
                total_revenue_change = total_profit_change + total_change
                total_revenue_balance = total_profit_balance + total_balance
            if mFilter == 'PL-EXPENSE':
                total_net_profit_change = total_revenue_change + total_change
                total_net_profit_balance = total_revenue_balance + total_balance
            if mFilter == 'PL-EXC':
                total_net_profit_tax_change = total_net_profit_change + total_change
                total_net_profit_tax_balance = total_net_profit_balance + total_balance + Decimal(prov_posted_amount)
            # sum_profit_finish.append(total_net_profit_tax_balance)
            if FlagReport == 1:
                if mFilter == 'PL-PURCH':
                    row = row
                else:
                    if mFilter == 'PL-REVENUE':
                        worksheet.write(row, col, ' OTHER REVENUE  ')
                        worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                        worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                        row += 2
                        worksheet.write(row, col, ' TOTAL REVENUE  ')
                        worksheet.write(row, col + 2, wrap_text_xls(total_revenue_change, mFilter), border_bot)
                        worksheet.write(row, col + 3, wrap_text_xls(total_revenue_balance, mFilter), border_bot)
                    else:
                        if mFilter == 'PL-COGS':
                            if is_stock_closing:
                                if not is_4550_grouped:
                                    row -= 1
                                    worksheet.write(row, col, ' ')
                                    worksheet.write(row, col + 2,
                                                    wrap_text_xls(total_good_sold_change - Decimal(sum_net_stock), mFilter),
                                                    border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(
                                        total_good_sold_balance - Decimal(sum_balance_stock), mFilter), border_bot)
                                    row += 1
                                    worksheet.write(row, col, acc_stock + '    ' + name_stock)
                                    worksheet.write(row, col + 2, wrap_text_xls(sum_net_stock, mFilter), right_line)
                                    worksheet.write(row, col + 3, wrap_text_xls(sum_balance_stock, mFilter), right_line)
                                    row += 1

                            worksheet.write(row, col, ' COST OF GOODS SOLD ')
                            worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                            worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                            row += 2
                            worksheet.write(row, col, 'GROSS PROFIT ')
                            worksheet.write(row, col + 2, wrap_text_xls(total_profit_change, 'PL-EXC'), border_bot)
                            worksheet.write(row, col + 3, wrap_text_xls(total_profit_balance, 'PL-EXC'), border_bot)
                            row += 2
                        else:
                            if mFilter == 'PL-EXPENSE':
                                worksheet.write(row, col, 'TOTAL EXPENDITURE        ')
                                worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_top_bot)
                                worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_top_bot)
                                row += 2
                                worksheet.write(row, col, 'NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ')
                                worksheet.write(row, col + 2, wrap_text_xls(total_net_profit_change, 'PL-EXC'), border_bot)
                                worksheet.write(row, col + 3, wrap_text_xls(total_net_profit_balance, 'PL-EXC'), border_bot)
                                row += 1
                            else:
                                if mFilter == 'PL-EXC':
                                    worksheet.write(row, col, 'TOTAL EXCH GAIN/(LOSS) ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                                    row += 2

                                    worksheet.write(row, col, 'NET PROFIT/(LOSS) AFTER INCOME TAXES ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_net_profit_tax_change, mFilter),
                                                    border_top_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_net_profit_tax_balance, mFilter),
                                                    border_top_bot)
                                else:
                                    worksheet.write(row, col, 'NET SALES  ')
                                    worksheet.write(row, col + 2, wrap_text_xls(total_change, mFilter), border_bot)
                                    worksheet.write(row, col + 3, wrap_text_xls(total_balance, mFilter), border_bot)
                row += 1
                test += 1
        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data


def getProvisionalPostedAmount(company_id, p_perd_year, p_perd_month, pl_group_code, acc_id, curr):
    prov_posted_amount = 0
    provisional_transaction = Transaction.objects.filter(company_id=company_id, is_hidden=False,
                                                         account__profit_loss_group__code=pl_group_code,
                                                         journal__status=int(STATUS_TYPE_DICT['Prov. Posted']),
                                                         journal__perd_year__lte=p_perd_year,
                                                         journal__perd_month__lte=p_perd_month,
                                                         journal__is_hidden=False,
                                                         account_id=acc_id,
                                                         currency_id=curr)
    if provisional_transaction:
        for prov_trx in provisional_transaction:
            prov_posted_amount += (float(prov_trx.functional_amount) * -1, float(prov_trx.functional_amount))[
                prov_trx.functional_balance_type == BALANCE_TYPE_DICT['Debit']]
    return prov_posted_amount


def createCustomAccGroupList(company_id):
    rpt_acc_grp_list = []
    rpt_acct_grp = ReportGroup.objects.filter(company_id=company_id, is_hidden=False, report_template_type='0')
    for rpt_acc_grp in rpt_acct_grp:
        rpt_acc_grp_obj = {'acc1_id': rpt_acc_grp.account_from.id,
                           'acc2_id': rpt_acc_grp.account_to.id if rpt_acc_grp.account_to else rpt_acc_grp.account_from.id,
                           'acc_code': rpt_acc_grp.account_code_text,
                           'acc_name': rpt_acc_grp.name}
        rpt_acc_grp_list.append(rpt_acc_grp_obj)
    return rpt_acc_grp_list


def getCustomAccGroup(rpt_acc_grp_list, mAccount):
    is_4550_exist = False
    custom_acc = {"custom_acc_code": None, "custom_acc_name": None}
    for custom_acc in rpt_acc_grp_list:
        if mAccount.id >= custom_acc['acc1_id'] and mAccount.id <= custom_acc['acc2_id']:
            custom_acc['custom_acc_code'] = custom_acc['acc_code']
            custom_acc['custom_acc_name'] = str(custom_acc['acc_name'])
            if mAccount.code == '4550':
                is_4550_exist = True
            break
        else:
            custom_acc['custom_acc_code'] = mAccount.code
            custom_acc['custom_acc_name'] = str(mAccount.name)
    return custom_acc, is_4550_exist
