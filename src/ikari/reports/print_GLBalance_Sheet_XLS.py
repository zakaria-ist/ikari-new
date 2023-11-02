import calendar
import datetime
from decimal import Decimal
import xlsxwriter
from accounts.models import Account, AccountHistory, ReportGroup
from companies.models import Company, CostCenters
from reports.print_GLProfit_Loss import NetPurchase_account_history
from transactions.models import Transaction
from utilities.common import wrap_separator, get_segment_filter_range
from utilities.constants import STATUS_TYPE_DICT, BALANCE_TYPE_DICT, REPORT_TYPE, ACCOUNT_TYPE_DICT, SEGMENT_FILTER_DICT


class Print_GLBalanceSheet_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def getProvisionalPosted(self, acc_id, company_id, p_perd_year, p_perd_month):
        prov_posted = {'account_id': 0, 'source': 0, 'functional': 0}
        provisional_transaction = Transaction.objects.filter(company_id=company_id, is_hidden=False,
                                                             journal__status=int(STATUS_TYPE_DICT['Prov. Posted']),
                                                             account_id=acc_id, journal__perd_year__lte=p_perd_year,
                                                             journal__perd_month__lte=p_perd_month)
        if provisional_transaction:
            for prov_trx in provisional_transaction:
                prov_posted['account_id'] = prov_trx.account_id
                prov_posted['source'] += (float(prov_trx.total_amount) * -1,
                                          float(prov_trx.total_amount))[
                    prov_trx.functional_balance_type == BALANCE_TYPE_DICT['Debit']]
                prov_posted['functional'] += (float(prov_trx.functional_amount) * -1,
                                              float(prov_trx.functional_amount))[
                    prov_trx.functional_balance_type == BALANCE_TYPE_DICT['Debit']]
        return prov_posted

    def createCustomAccGroupList(self, company_id):
        rpt_acc_grp_list = []
        rpt_acct_grp = ReportGroup.objects.filter(company_id=company_id, is_hidden=False, report_template_type='1')
        for rpt_acc_grp in rpt_acct_grp:
            rpt_acc_grp_obj = {'acc1_id': rpt_acc_grp.account_from.id,
                               'acc2_id': rpt_acc_grp.account_to.id if rpt_acc_grp.account_to else rpt_acc_grp.account_from.id,
                               'acc_code': rpt_acc_grp.account_code_text,
                               'acc_name': rpt_acc_grp.name}
            rpt_acc_grp_list.append(rpt_acc_grp_obj)
        return rpt_acc_grp_list

    def getCustomAccGroup(self, rpt_acc_grp_list, mAccount):
        custom_acc = {"custom_acc_code": None, "custom_acc_name": None}
        for custom_acc in rpt_acc_grp_list:
            if mAccount.id >= custom_acc['acc1_id'] and mAccount.id <= custom_acc['acc2_id']:
                custom_acc['custom_acc_code'] = custom_acc['acc_code']
                custom_acc['custom_acc_name'] = str(custom_acc['acc_name'])
                break
            else:
                custom_acc['custom_acc_code'] = mAccount.code
                custom_acc['custom_acc_name'] = str(mAccount.name)
        return custom_acc

    def WriteToExcel(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        company = Company.objects.get(pk=company_id)
        if SEGMENT_FILTER_DICT['Segment'] == filter_type:
            return self.WriteToExcelforSegment(company_id, issue_date, report_type, filter_type, from_val, to_val)
        elif company.use_segment:
            return self.WriteToExcelforAccount(company_id, issue_date, report_type, filter_type, from_val, to_val)
        else:
            return self.WriteToExcelOnlyForAccount(company_id, issue_date, report_type, filter_type, from_val, to_val)

    def WriteToExcelforAccount(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Balance Sheet")
        row = 7
        col = 0
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
            'bottom': 1
        })
        border_top_bot = workbook.add_format({
            'align': 'right',
            'bottom': 1,
            'top': 1
        })
        array_data = str(issue_date).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        company = Company.objects.get(pk=company_id)
        format_date_report = str(issue_to.day) + '/' + str(issue_to.month) + '/' + str(issue_to.year)
        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'BALANCE SHEET', merge_format)
        worksheet.merge_range('A5:C5', 'AS AT ' + format_date_report, merge_format)
        worksheet.write(6, 2, company.currency.code, center_line)
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(2, 0, 17)

        filter_array = []
        filter_array.append('BS-FA')
        filter_array.append('BS-NA')
        filter_array.append('BS-CA')
        filter_array.append('BS-CL')
        filter_array.append('BS-LL')
        filter_array.append('BS-SE')

        total = total_long_term = 0
        sum_credit = sum_debit = total_account = 0
        rpt_acc_grp_list = self.createCustomAccGroupList(company_id)
        last_segment = CostCenters.objects.filter(company_id=company_id).last()
        segment_code = last_segment.code if last_segment else ''
        segment_count = CostCenters.objects.filter(company_id=company_id).count()
        for j, mFilter in enumerate(filter_array):
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Balance Sheet']),
                                                       profit_loss_group__code=mFilter).order_by('account_segment').distinct()
            m_account_group = m_name_group = ''
            sum_total_account = 0
            custom_acc_code = None
            custom_acc_code2 = None
            if account_item_list:
                total = 0
                if (j != 0):
                    if mFilter == 'BS-FA':
                        m_name_group = ' FIXED ASSETS'
                    total = total_account = 0
                if mFilter == 'BS-FA':
                    m_name_group = 'FIXED ASSETS, AT COST LESS DEPRECIATION'
                    m_total = 'FIXED ASSETS'
                elif mFilter == 'BS-NA':
                    m_name_group = ' NON ASSETS '
                    m_total = ' NON ASSETS '
                elif mFilter == 'BS-CA':
                    m_name_group = 'CURRENT ASSETS:'
                    m_total = 'CURRENT ASSETS:'
                elif mFilter == 'BS-CL':
                    m_name_group = 'CURRENT LIABILITIES:'
                    m_total = 'CURRENT LIABILITIES:'
                elif mFilter == 'BS-LL':
                    m_name_group = 'LONG-TERM LIABILITY :'
                    m_total = 'LONG-TERM LIABILITY :'
                elif mFilter == 'BS-SE':
                    m_name_group = "SHAREHOLDERS' EQUITY:"
                    m_total = "SHAREHOLDERS' EQUITY:"
                    worksheet.write(row, col, 'REPRESENTED BY:-         ')
                    row += 2
                worksheet.write(row, col, m_name_group)
                row += 1

                last_seg_account = last_seg_account_name = ''
                seg_total = 0
                skip_count = 0
                count = len(account_item_list)
                for i, mAccount in enumerate(account_item_list):
                    mAccount_disctinct_list = []
                    mAccount_disctinct_obj = {}
                    if (m_account_group != mAccount.profit_loss_group.code):
                        if (i != 0):
                            if mAccount.profit_loss_group.code == 'BS-FA':
                                m_name_group = ' FIXED ASSETS'

                        m_account_group = mAccount.profit_loss_group.code
                    if m_account_group == mAccount.profit_loss_group.code:
                        # process new data
                        item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                     account_id=mAccount.id, source_currency_id=company.currency_id)
                        if issue_from:
                            item_account = item_account.filter(period_month__exact=int(array_data[1]))
                        if issue_to:
                            item_account = item_account.filter(period_year__exact=int(array_data[0]))
                        # sum debit,sum credit
                        if item_account:
                            for j, iAccount in enumerate(item_account):
                                if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                                    sum_credit += iAccount.functional_end_balance
                                if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                                    sum_debit += iAccount.functional_end_balance
                            total_account = sum_debit + sum_credit
                            if report_type == dict(REPORT_TYPE)['Provisional']:
                                prov_posted = self.getProvisionalPosted(mAccount.id, company_id, int(array_data[0]),
                                                                        int(array_data[1]))
                                if mAccount.id == prov_posted['account_id']:
                                    total_account += Decimal(prov_posted['functional'])
                            total += total_account
                        if mAccount.profit_loss_group.code == 'BS-FA':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(mAccount_disctinct_obj)
                            else:
                                if skip_count == 0:
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = 0
                                if last_seg_account == mAccount.account_segment:
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total += total_account
                                    skip_count += 1
                                    if skip_count == segment_count:  # print last item
                                        last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                        skip_count = 0
                                    else:
                                        row -= 1
                                else:
                                    worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = total_account
                                    if i == count - 1:
                                        row += 1
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-NA':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(mAccount_disctinct_obj)
                            else:
                                if skip_count == 0:
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = 0
                                if last_seg_account == mAccount.account_segment:
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total += total_account
                                    skip_count += 1
                                    if skip_count == segment_count:  # print last item
                                        last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                        skip_count = 0
                                    else:
                                        row -= 1
                                else:
                                    worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = total_account
                                    if i == count - 1:
                                        row += 1
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-CA':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(mAccount_disctinct_obj)
                            else:
                                if skip_count == 0:
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = 0
                                if last_seg_account == mAccount.account_segment:
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total += total_account
                                    skip_count += 1
                                    if skip_count == segment_count:  # print last item
                                        last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                        skip_count = 0
                                    else:
                                        row -= 1
                                else:
                                    worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = total_account
                                    if i == count - 1:
                                        row += 1
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-CL' or mAccount.profit_loss_group.code == 'BS-LL':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(mAccount_disctinct_obj)
                            else:
                                if skip_count == 0:
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = 0
                                if last_seg_account == mAccount.account_segment:
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total += total_account
                                    skip_count += 1
                                    if skip_count == segment_count:  # print last item
                                        last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                                        skip_count = 0
                                    else:
                                        row -= 1
                                else:
                                    worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = total_account
                                    if i == count - 1:
                                        row += 1
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-SE':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(mAccount_disctinct_obj)
                            else:
                                if skip_count == 0:
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = 0
                                if last_seg_account == mAccount.account_segment:
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total += total_account
                                    skip_count += 1
                                    if skip_count == segment_count:  # print last item
                                        last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                        skip_count = 0
                                    else:
                                        row -= 1
                                else:
                                    worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)
                                    last_seg_account = mAccount.account_segment
                                    last_seg_account_name = mAccount.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    seg_total = total_account
                                    if i == count - 1:
                                        row += 1
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total), right_line)

                        # call PROFIT(LOSS)FOR PERIOD: only in 1 month
                        if m_account_group == 'BS-SE':
                            FlagReport = 0
                            sum_profit_finish = []
                            total_retained = retained_sum_credit = retained_sum_debit = 0
                            # Get amount of Retained Earnings Accounts
                            retained_accounts = Account.objects.filter(company_id=company_id, is_active=True,
                                                                       is_hidden=0,
                                                                       account_type=int(
                                                                           ACCOUNT_TYPE_DICT['Retained Earning']))

                            for r_account in retained_accounts:
                                item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                             account_id=r_account.id, source_currency_id=company.currency_id)
                                if issue_from:
                                    item_account = item_account.filter(period_month__exact=int(array_data[1]))
                                if issue_to:
                                    item_account = item_account.filter(period_year__exact=int(array_data[0]))

                                # sum debit,sum credit
                                retained_amount = 0
                                if item_account:
                                    for j, iAccount in enumerate(item_account):
                                        if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                                            retained_sum_credit += iAccount.functional_end_balance
                                        if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                                            retained_sum_debit += iAccount.functional_end_balance
                                    retained_amount = retained_sum_debit + retained_sum_credit
                                    total_retained += retained_amount
                                if len(rpt_acc_grp_list) > 0:
                                    custom_acc = self.getCustomAccGroup(rpt_acc_grp_list, r_account)
                                    mAccount_disctinct_list.append(
                                        {"code": custom_acc['custom_acc_code'], "name": custom_acc['custom_acc_name'],
                                         "amount": retained_amount})
                                else:
                                    row += 1
                                    if skip_count == 0:
                                        last_seg_account = r_account.account_segment
                                        last_seg_account_name = r_account.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        seg_total = 0
                                    if last_seg_account == r_account.account_segment:
                                        last_seg_account_name = r_account.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        seg_total += retained_amount
                                        skip_count += 1
                                        if skip_count == segment_count:  # print last item
                                            last_seg_account_name = r_account.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                            worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                            worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                                            skip_count = 0
                                            row += 1
                                    else:
                                        worksheet.write(row, col, last_seg_account + '         ' + last_seg_account_name)
                                        worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                                        last_seg_account = r_account.account_segment
                                        last_seg_account_name = r_account.name.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                        seg_total = retained_amount
                            if len(rpt_acc_grp_list) <= 0:
                                row += 1

                            NetPurchase_account_history(company_id, array_data[0], array_data[1], sum_profit_finish,
                                                        [], FlagReport, filter_type, from_val, to_val, report_type)
                            if len(rpt_acc_grp_list) > 0:
                                mAccount_disctinct_list.append({"code": "0000", "name": str('PROFIT (LOSS) FOR PERIOD '),
                                                                "amount": sum_profit_finish[0]})
                            else:
                                worksheet.write(row, col, '         PROFIT (LOSS) FOR PERIOD ')
                                worksheet.write(row, col + 2, wrap_separator(sum_profit_finish[0], 'BS-SE'), right_line)

                            total += sum_profit_finish[0] + total_retained
                            if len(rpt_acc_grp_list) <= 0:
                                row += 1

                    if len(rpt_acc_grp_list) > 0:
                        for custom_account in mAccount_disctinct_list:
                            if custom_account['code'] == '0000':
                                row += 1
                                worksheet.write(row, col + 1, custom_account['name'])
                                worksheet.write(row, col + 2, wrap_separator(custom_account['amount'], mAccount.profit_loss_group.code), right_line)
                            if skip_count == 0:
                                last_seg_account = custom_account['code'][:4]
                                last_seg_account_name = custom_account['name'].replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                seg_total = 0
                            if last_seg_account == custom_account['code'][:4]:
                                last_seg_account_name = custom_account['name'].replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                seg_total += custom_account['amount']
                                skip_count += 1
                                if skip_count == segment_count:  # print last item
                                    last_seg_account_name = custom_account['name'].replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                    worksheet.write(row, col, last_seg_account)
                                    worksheet.write(row, col + 1, last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                                    skip_count = 0
                                else:
                                    row -= 1
                            else:
                                worksheet.write(row, col, last_seg_account)
                                worksheet.write(row, col + 1, last_seg_account_name)
                                worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)
                                last_seg_account = custom_account['code'][:4]
                                last_seg_account_name = custom_account['name'].replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                seg_total = custom_account['amount']
                                if i == count - 1:
                                    row += 1
                                    worksheet.write(row, col, last_seg_account)
                                    worksheet.write(row, col + 1, last_seg_account_name)
                                    worksheet.write(row, col + 2, wrap_separator(seg_total, mAccount.profit_loss_group.code), right_line)

                    sum_credit = sum_debit = total_account = 0
                    if (i == account_item_list.__len__() - 1):
                        if m_account_group == 'BS-CA':
                            worksheet.write(row + 2, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 2, col + 2, wrap_separator(total), border_top_bot)
                            total_long_term += total
                            row += 3

                        elif mFilter == 'BS-CL':
                            worksheet.write(row + 2, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 2, col + 2, wrap_separator(total, 'BS-CL'), border_top_bot)
                            total_long_term = (total_long_term + total)
                            worksheet.write(row + 3, col + 2, wrap_separator(total_long_term, 'BS-LL'), border_top_bot)
                            row += 3
                        elif mFilter == 'BS-LL':
                            worksheet.write(row + 1, col, m_total)
                            worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-LL'), border_top_bot)
                            worksheet.write(row + 3, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 3, col + 2, wrap_separator(total_long_term, 'BS-LL'), border_top_bot)
                            total_long_term = 0
                            row += 5

                        elif mFilter == 'BS-SE':
                            worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-SE'), border_top_bot)
                            total_long_term += total
                            row += 3
                        else:
                            total_long_term += total
                            worksheet.write(row + 1, col, '')
                            worksheet.write(row + 1, col + 2, wrap_separator(total), border_top_bot)
                            worksheet.write(row + 3, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 3, col + 2, wrap_separator(total), border_top_bot)
                            row += 5
                    row += 1
        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def WriteToExcelforSegment(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Balance Sheet")
        row = 7
        col = 0
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
            'bottom': 1
        })
        border_top_bot = workbook.add_format({
            'align': 'right',
            'bottom': 1,
            'top': 1
        })
        array_data = str(issue_date).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        company = Company.objects.get(pk=company_id)
        format_date_report = str(issue_to.day) + '/' + str(issue_to.month) + '/' + str(issue_to.year)
        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'BALANCE SHEET', merge_format)
        worksheet.merge_range('A5:C5', 'AS AT ' +
                              format_date_report, merge_format)
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(2, 0, 17)

        filter_array = []
        filter_array.append('BS-FA')
        filter_array.append('BS-NA')
        filter_array.append('BS-CA')
        filter_array.append('BS-CL')
        filter_array.append('BS-LL')
        filter_array.append('BS-SE')

        total = total_long_term = 0
        sum_credit = sum_debit = total_account = 0
        rpt_acc_grp_list = self.createCustomAccGroupList(company_id)

        segment_code_range = get_segment_filter_range(company_id, int(from_val), int(to_val), 'id')
        for segment_code in segment_code_range:
            segment = CostCenters.objects.get(pk=segment_code)
            worksheet.write(row, col + 1, segment.name)
            row += 3
            worksheet.write(row, 2, company.currency.code, center_line)
            row += 2
            for j, mFilter in enumerate(filter_array):
                account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0, segment_code_id=segment_code,
                                                           account_type=int(ACCOUNT_TYPE_DICT['Balance Sheet']),
                                                           profit_loss_group__code=mFilter).order_by('code').distinct()
                m_account_group = m_name_group = ''
                sum_total_account = 0
                custom_acc_code = None
                custom_acc_code2 = None
                if account_item_list:
                    total = 0
                    if (j != 0):
                        if mFilter == 'BS-FA':
                            m_name_group = ' FIXED ASSETS'
                        total = total_account = 0
                    if mFilter == 'BS-FA':
                        m_name_group = 'FIXED ASSETS, AT COST LESS DEPRECIATION'
                        m_total = 'FIXED ASSETS'
                    elif mFilter == 'BS-NA':
                        m_name_group = ' NON ASSETS '
                        m_total = ' NON ASSETS '
                    elif mFilter == 'BS-CA':
                        m_name_group = 'CURRENT ASSETS:'
                        m_total = 'CURRENT ASSETS:'
                    elif mFilter == 'BS-CL':
                        m_name_group = 'CURRENT LIABILITIES:'
                        m_total = 'CURRENT LIABILITIES:'
                    elif mFilter == 'BS-LL':
                        m_name_group = 'LONG-TERM LIABILITY :'
                        m_total = 'LONG-TERM LIABILITY :'
                    elif mFilter == 'BS-SE':
                        m_name_group = "SHAREHOLDERS' EQUITY:"
                        m_total = "SHAREHOLDERS' EQUITY:"
                        worksheet.write(row, col, 'REPRESENTED BY:-         ')
                        row += 2
                    worksheet.write(row, col, m_name_group)
                    row += 1

                    for i, mAccount in enumerate(account_item_list):
                        mAccount_disctinct_list = []
                        mAccount_disctinct_obj = {}
                        if (m_account_group != mAccount.profit_loss_group.code):
                            if (i != 0):
                                if mAccount.profit_loss_group.code == 'BS-FA':
                                    m_name_group = ' FIXED ASSETS'

                            m_account_group = mAccount.profit_loss_group.code
                        if m_account_group == mAccount.profit_loss_group.code:
                            # process new data
                            item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                         account_id=mAccount.id, source_currency_id=company.currency_id)
                            if issue_from:
                                item_account = item_account.filter(
                                    period_month__exact=int(array_data[1]))
                            if issue_to:
                                item_account = item_account.filter(
                                    period_year__exact=int(array_data[0]))
                            # sum debit,sum credit
                            if item_account:
                                for j, iAccount in enumerate(item_account):
                                    if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                                        sum_credit += iAccount.functional_end_balance
                                    if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                                        sum_debit += iAccount.functional_end_balance
                                total_account = sum_debit + sum_credit
                                if report_type == dict(REPORT_TYPE)['Provisional']:
                                    prov_posted = self.getProvisionalPosted(mAccount.id, company_id, int(array_data[0]),
                                                                            int(array_data[1]))
                                    if mAccount.id == prov_posted['account_id']:
                                        total_account += Decimal(
                                            prov_posted['functional'])
                                total += total_account
                            if mAccount.profit_loss_group.code == 'BS-FA':
                                if len(rpt_acc_grp_list) > 0:
                                    custom_acc = self.getCustomAccGroup(
                                        rpt_acc_grp_list, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        sum_total_account = total_account
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        sum_total_account += total_account
                                    mAccount_disctinct_obj['code'] = custom_acc_code
                                    mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                    mAccount_disctinct_obj['amount'] = sum_total_account
                                    mAccount_disctinct_list.append(
                                        mAccount_disctinct_obj)
                                else:
                                    worksheet.write(
                                        row, col, mAccount.code + '         ' + mAccount.name)
                                    worksheet.write(
                                        row, col + 2, wrap_separator(total_account), right_line)
                            elif mAccount.profit_loss_group.code == 'BS-NA' or mAccount.profit_loss_group.code == 'BS-CA':
                                if len(rpt_acc_grp_list) > 0:
                                    custom_acc = self.getCustomAccGroup(
                                        rpt_acc_grp_list, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        sum_total_account = total_account
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        sum_total_account += total_account
                                    mAccount_disctinct_obj['code'] = custom_acc_code
                                    mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                    mAccount_disctinct_obj['amount'] = sum_total_account
                                    mAccount_disctinct_list.append(
                                        mAccount_disctinct_obj)
                                else:
                                    worksheet.write(
                                        row, col, mAccount.code + '         ' + mAccount.name)
                                    worksheet.write(
                                        row, col + 2, wrap_separator(total_account), right_line)
                            elif mAccount.profit_loss_group.code == 'BS-CL' or mAccount.profit_loss_group.code == 'BS-LL':
                                if len(rpt_acc_grp_list) > 0:
                                    custom_acc = self.getCustomAccGroup(
                                        rpt_acc_grp_list, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        sum_total_account = total_account
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        sum_total_account += total_account
                                    mAccount_disctinct_obj['code'] = custom_acc_code
                                    mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                    mAccount_disctinct_obj['amount'] = sum_total_account
                                    mAccount_disctinct_list.append(
                                        mAccount_disctinct_obj)
                                else:
                                    worksheet.write(
                                        row, col, mAccount.code + '         ' + mAccount.name)
                                    worksheet.write(
                                        row, col + 2, wrap_separator(total_account, mAccount.profit_loss_group.code), right_line)
                            elif mAccount.profit_loss_group.code == 'BS-SE':
                                if len(rpt_acc_grp_list) > 0:
                                    custom_acc = self.getCustomAccGroup(
                                        rpt_acc_grp_list, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        sum_total_account = total_account
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        sum_total_account += total_account
                                    mAccount_disctinct_obj['code'] = custom_acc_code
                                    mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                    mAccount_disctinct_obj['amount'] = sum_total_account
                                    mAccount_disctinct_list.append(
                                        mAccount_disctinct_obj)
                                else:
                                    worksheet.write(
                                        row, col, mAccount.code + '         ' + mAccount.name)
                                    worksheet.write(
                                        row, col + 2, wrap_separator(total_account, mAccount.profit_loss_group.code), right_line)

                            # call PROFIT(LOSS)FOR PERIOD: only in 1 month
                            if m_account_group == 'BS-SE':
                                FlagReport = 0
                                sum_profit_finish = []
                                total_retained = retained_sum_credit = retained_sum_debit = 0
                                # Get amount of Retained Earnings Accounts
                                retained_accounts = Account.objects.filter(company_id=company_id, is_active=True,
                                                                           is_hidden=0, segment_code_id=segment_code,
                                                                           account_type=int(
                                                                               ACCOUNT_TYPE_DICT['Retained Earning']))
                                for r_account in retained_accounts:
                                    item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                                 account_id=r_account.id, source_currency_id=company.currency_id)
                                    if issue_from:
                                        item_account = item_account.filter(
                                            period_month__exact=int(array_data[1]))
                                    if issue_to:
                                        item_account = item_account.filter(
                                            period_year__exact=int(array_data[0]))

                                    # sum debit,sum credit
                                    retained_amount = 0
                                    if item_account:
                                        for j, iAccount in enumerate(item_account):
                                            if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                                                retained_sum_credit += iAccount.functional_end_balance
                                            if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                                                retained_sum_debit += iAccount.functional_end_balance
                                        retained_amount = retained_sum_debit + retained_sum_credit
                                        total_retained += retained_amount
                                    if len(rpt_acc_grp_list) > 0:
                                        custom_acc = self.getCustomAccGroup(
                                            rpt_acc_grp_list, r_account)
                                        mAccount_disctinct_list.append(
                                            {"code": custom_acc['custom_acc_code'], "name": custom_acc['custom_acc_name'],
                                             "amount": retained_amount})
                                    else:
                                        row += 1
                                        worksheet.write(
                                            row, col, r_account.code + '         ' + r_account.name)
                                        worksheet.write(
                                            row, col + 2, wrap_separator(retained_amount, mAccount.profit_loss_group.code), right_line)
                                if len(rpt_acc_grp_list) <= 0:
                                    row += 1

                                NetPurchase_account_history(company_id, array_data[0], array_data[1], sum_profit_finish,
                                                            [], FlagReport, filter_type, from_val, to_val, report_type)
                                if len(rpt_acc_grp_list) > 0:
                                    mAccount_disctinct_list.append({"code": "", "name": str('PROFIT (LOSS) FOR PERIOD '),
                                                                    "amount": sum_profit_finish[0]})
                                else:
                                    worksheet.write(
                                        row, col, '         PROFIT (LOSS) FOR PERIOD ')
                                    worksheet.write(
                                        row, col + 2, wrap_separator(sum_profit_finish[0]), right_line)

                                total += sum_profit_finish[0] + total_retained
                                if len(rpt_acc_grp_list) <= 0:
                                    row += 1

                        if len(rpt_acc_grp_list) > 0:
                            for custom_account in mAccount_disctinct_list:
                                if custom_account['code'] != custom_acc_code2:
                                    custom_acc_code2 = custom_account['code']
                                    # if m_account_group=='BS-SE':
                                    #     row-=5
                                    if custom_account['code'][:4] == '3500':
                                        row += 1
                                    if custom_account['code'][:4] == '3900':
                                        row += 1
                                    if custom_account['code'][:4] == '':
                                        row += 1
                                    worksheet.write(
                                        row, col, custom_account['code'])
                                    worksheet.write(
                                        row, col + 1, custom_account['name'])
                                    worksheet.write(
                                        row, col + 2, wrap_separator(custom_account['amount'], mAccount.profit_loss_group.code), right_line)
                                else:
                                    row -= 1
                                    worksheet.write(
                                        row, col, custom_account['code'])
                                    worksheet.write(
                                        row, col + 1, custom_account['name'])
                                    worksheet.write(
                                        row, col + 2, wrap_separator(custom_account['amount'], mAccount.profit_loss_group.code), right_line)

                        sum_credit = sum_debit = total_account = 0
                        if (i == account_item_list.__len__() - 1):
                            if m_account_group == 'BS-CA':
                                worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                                worksheet.write(row + 1, col + 2, wrap_separator(total), border_top_bot)
                                total_long_term += total
                                row += 3

                            elif mFilter == 'BS-CL':
                                worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                                worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-CL'), border_top_bot)
                                total_long_term = (total_long_term + total)
                                worksheet.write(row + 3, col + 2, wrap_separator(total_long_term, 'BS-LL'), border_top_bot)
                                total_long_term = 0
                                row += 3
                            elif mFilter == 'BS-LL':
                                worksheet.write(row + 1, col, m_total)
                                worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-CL'), border_top_bot)
                                worksheet.write(row + 3, col, 'TOTAL      ' + m_total)
                                worksheet.write(row + 3, col + 2, wrap_separator(total_long_term, 'BS-LL'), border_top_bot)
                                total_long_term = 0
                                row += 5

                            elif mFilter == 'BS-SE':
                                worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                                worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-SE'), border_top_bot)
                                # total_long_term += total
                                total_long_term = 0
                                row += 3
                            else:
                                total_long_term += total
                                worksheet.write(row + 1, col, '')
                                worksheet.write(row + 1, col + 2, wrap_separator(total), border_top_bot)
                                worksheet.write(row + 3, col, 'TOTAL      ' + m_total)
                                worksheet.write(row + 3, col + 2, wrap_separator(total), border_top_bot)
                                row += 5
                        row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def WriteToExcelOnlyForAccount(self, company_id, issue_date, report_type, filter_type, from_val, to_val):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Balance Sheet")
        row = 7
        col = 0
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
            'bottom': 1
        })
        border_top_bot = workbook.add_format({
            'align': 'right',
            'bottom': 1,
            'top': 1
        })
        array_data = str(issue_date).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        company = Company.objects.get(pk=company_id)
        format_date_report = str(issue_to.day) + '/' + str(issue_to.month) + '/' + str(issue_to.year)
        worksheet.merge_range('A3:C3', company.name, merge_format)
        worksheet.merge_range('A4:C4', 'BALANCE SHEET', merge_format)
        worksheet.merge_range('A5:C5', 'AS AT ' +
                              format_date_report, merge_format)
        worksheet.write(6, 2, company.currency.code, center_line)
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(2, 0, 17)

        filter_array = []
        filter_array.append('BS-FA')
        filter_array.append('BS-NA')
        filter_array.append('BS-CA')
        filter_array.append('BS-CL')
        filter_array.append('BS-LL')
        filter_array.append('BS-SE')

        total = total_long_term = 0
        sum_credit = sum_debit = total_account = 0
        rpt_acc_grp_list = self.createCustomAccGroupList(company_id)

        for j, mFilter in enumerate(filter_array):
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Balance Sheet']),
                                                       profit_loss_group__code=mFilter).order_by('code').distinct()
            m_account_group = m_name_group = ''
            sum_total_account = 0
            custom_acc_code = None
            custom_acc_code2 = None
            if account_item_list:
                total = 0
                if (j != 0):
                    if mFilter == 'BS-FA':
                        m_name_group = ' FIXED ASSETS'
                    total = total_account = 0
                if mFilter == 'BS-FA':
                    m_name_group = 'FIXED ASSETS, AT COST LESS DEPRECIATION'
                    m_total = 'FIXED ASSETS'
                elif mFilter == 'BS-NA':
                    m_name_group = ' NON ASSETS '
                    m_total = ' NON ASSETS '
                elif mFilter == 'BS-CA':
                    m_name_group = 'CURRENT ASSETS:'
                    m_total = 'CURRENT ASSETS:'
                elif mFilter == 'BS-CL':
                    m_name_group = 'CURRENT LIABILITIES:'
                    m_total = 'CURRENT LIABILITIES:'
                elif mFilter == 'BS-LL':
                    m_name_group = 'LONG-TERM LIABILITY :'
                    m_total = 'LONG-TERM LIABILITY :'
                elif mFilter == 'BS-SE':
                    m_name_group = "SHAREHOLDERS' EQUITY:"
                    m_total = "SHAREHOLDERS' EQUITY:"
                    worksheet.write(row, col, 'REPRESENTED BY:-         ')
                    row += 2
                worksheet.write(row, col, m_name_group)
                row += 1

                for i, mAccount in enumerate(account_item_list):
                    mAccount_disctinct_list = []
                    mAccount_disctinct_obj = {}
                    if (m_account_group != mAccount.profit_loss_group.code):
                        if (i != 0):
                            if mAccount.profit_loss_group.code == 'BS-FA':
                                m_name_group = ' FIXED ASSETS'

                        m_account_group = mAccount.profit_loss_group.code
                    if m_account_group == mAccount.profit_loss_group.code:
                        # process new data
                        item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                     account_id=mAccount.id, source_currency_id=company.currency_id)
                        if issue_from:
                            item_account = item_account.filter(
                                period_month__exact=int(array_data[1]))
                        if issue_to:
                            item_account = item_account.filter(
                                period_year__exact=int(array_data[0]))
                        # sum debit,sum credit
                        if item_account:
                            for j, iAccount in enumerate(item_account):
                                if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                                    sum_credit += iAccount.functional_end_balance
                                if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                                    sum_debit += iAccount.functional_end_balance
                            total_account = sum_debit + sum_credit
                            if report_type == dict(REPORT_TYPE)['Provisional']:
                                prov_posted = self.getProvisionalPosted(mAccount.id, company_id, int(array_data[0]),
                                                                        int(array_data[1]))
                                if mAccount.id == prov_posted['account_id']:
                                    total_account += Decimal(
                                        prov_posted['functional'])
                            total += total_account
                        if mAccount.profit_loss_group.code == 'BS-FA':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(
                                    rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(
                                    mAccount_disctinct_obj)
                            else:
                                worksheet.write(
                                    row, col, mAccount.code + '         ' + mAccount.name)
                                worksheet.write(
                                    row, col + 2, wrap_separator(total_account), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-NA' or mAccount.profit_loss_group.code == 'BS-CA':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(
                                    rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(
                                    mAccount_disctinct_obj)
                            else:
                                worksheet.write(
                                    row, col, mAccount.code + '         ' + mAccount.name)
                                worksheet.write(
                                    row, col + 2, wrap_separator(total_account), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-CL' or mAccount.profit_loss_group.code == 'BS-LL':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(
                                    rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(
                                    mAccount_disctinct_obj)
                            else:
                                worksheet.write(
                                    row, col, mAccount.code + '         ' + mAccount.name)
                                worksheet.write(
                                    row, col + 2, wrap_separator(total_account, mAccount.profit_loss_group.code), right_line)
                        elif mAccount.profit_loss_group.code == 'BS-SE':
                            if len(rpt_acc_grp_list) > 0:
                                custom_acc = self.getCustomAccGroup(
                                    rpt_acc_grp_list, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    sum_total_account = total_account
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    sum_total_account += total_account
                                mAccount_disctinct_obj['code'] = custom_acc_code
                                mAccount_disctinct_obj['name'] = custom_acc['custom_acc_name']
                                mAccount_disctinct_obj['amount'] = sum_total_account
                                mAccount_disctinct_list.append(
                                    mAccount_disctinct_obj)
                            else:
                                worksheet.write(
                                    row, col, mAccount.code + '         ' + mAccount.name)
                                worksheet.write(
                                    row, col + 2, wrap_separator(total_account, mAccount.profit_loss_group.code), right_line)

                        # call PROFIT(LOSS)FOR PERIOD: only in 1 month
                        if m_account_group == 'BS-SE':
                            FlagReport = 0
                            sum_profit_finish = []
                            total_retained = retained_sum_credit = retained_sum_debit = 0
                            # Get amount of Retained Earnings Accounts
                            retained_accounts = Account.objects.filter(company_id=company_id, is_active=True,
                                                                       is_hidden=0,
                                                                       account_type=int(
                                                                           ACCOUNT_TYPE_DICT['Retained Earning']))
                            for r_account in retained_accounts:
                                item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                             account_id=r_account.id, source_currency_id=company.currency_id)
                                if issue_from:
                                    item_account = item_account.filter(
                                        period_month__exact=int(array_data[1]))
                                if issue_to:
                                    item_account = item_account.filter(
                                        period_year__exact=int(array_data[0]))

                                # sum debit,sum credit
                                retained_amount = 0
                                if item_account:
                                    for j, iAccount in enumerate(item_account):
                                        if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                                            retained_sum_credit += iAccount.functional_end_balance
                                        if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                                            retained_sum_debit += iAccount.functional_end_balance
                                    retained_amount = retained_sum_debit + retained_sum_credit
                                    total_retained += retained_amount
                                if len(rpt_acc_grp_list) > 0:
                                    custom_acc = self.getCustomAccGroup(
                                        rpt_acc_grp_list, r_account)
                                    mAccount_disctinct_list.append(
                                        {"code": custom_acc['custom_acc_code'], "name": custom_acc['custom_acc_name'],
                                            "amount": retained_amount})
                                else:
                                    row += 1
                                    worksheet.write(
                                        row, col, r_account.code + '         ' + r_account.name)
                                    worksheet.write(
                                        row, col + 2, wrap_separator(retained_amount, m_account_group), right_line)
                            if len(rpt_acc_grp_list) <= 0:
                                row += 1

                            NetPurchase_account_history(company_id, array_data[0], array_data[1], sum_profit_finish,
                                                        [], FlagReport, filter_type, from_val, to_val, report_type)
                            if len(rpt_acc_grp_list) > 0:
                                mAccount_disctinct_list.append({"code": "", "name": str('PROFIT (LOSS) FOR PERIOD '),
                                                                "amount": sum_profit_finish[0]})
                            else:
                                worksheet.write(
                                    row, col, '         PROFIT (LOSS) FOR PERIOD ')
                                worksheet.write(
                                    row, col + 2, wrap_separator(sum_profit_finish[0], m_account_group), right_line)

                            total += sum_profit_finish[0] + total_retained
                            if len(rpt_acc_grp_list) <= 0:
                                row += 1

                    if len(rpt_acc_grp_list) > 0:
                        for custom_account in mAccount_disctinct_list:
                            if custom_account['code'] != custom_acc_code2:
                                custom_acc_code2 = custom_account['code']
                                # if m_account_group=='BS-SE':
                                #     row-=5
                                if (custom_account['code'] == '3500'):
                                    row += 1
                                worksheet.write(
                                    row, col, custom_account['code'])
                                worksheet.write(
                                    row, col + 1, custom_account['name'])
                                worksheet.write(
                                    row, col + 2, wrap_separator(custom_account['amount'], mAccount.profit_loss_group.code), right_line)
                            else:
                                row -= 1
                                worksheet.write(
                                    row, col, custom_account['code'])
                                worksheet.write(
                                    row, col + 1, custom_account['name'])
                                worksheet.write(
                                    row, col + 2, wrap_separator(custom_account['amount'], mAccount.profit_loss_group.code), right_line)

                    sum_credit = sum_debit = total_account = 0
                    if (i == account_item_list.__len__() - 1):
                        if m_account_group == 'BS-CA':
                            worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 1, col + 2, wrap_separator(total), border_top_bot)
                            total_long_term += total
                            row += 3

                        elif mFilter == 'BS-CL':
                            worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-CL'), border_top_bot)
                            total_long_term = (total_long_term + total)
                            row += 3
                        elif mFilter == 'BS-LL':
                            worksheet.write(row + 1, col, m_total)
                            worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-CL'), border_top_bot)
                            worksheet.write(row + 3, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 3, col + 2, wrap_separator(total_long_term, 'BS-LL'), border_top_bot)
                            total_long_term = 0
                            row += 5

                        elif mFilter == 'BS-SE':
                            worksheet.write(row + 1, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 1, col + 2, wrap_separator(total, 'BS-SE'), border_top_bot)
                            total_long_term += total
                            row += 3
                        else:
                            total_long_term += total
                            worksheet.write(row + 1, col, '')
                            worksheet.write(row + 1, col + 2, wrap_separator(total), border_top_bot)
                            worksheet.write(row + 3, col, 'TOTAL      ' + m_total)
                            worksheet.write(row + 3, col + 2, wrap_separator(total), border_top_bot)
                            row += 5
                    row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
