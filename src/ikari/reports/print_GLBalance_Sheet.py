import calendar
import datetime
import os
from decimal import Decimal
from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from accounts.models import Account, AccountHistory, ReportGroup
from companies.models import Company, CostCenters
from reports.numbered_page import NumberedPage
from reports.print_GLProfit_Loss import NetPurchase_account_history, get_exchange_rate_header
from transactions.models import Transaction
from utilities.common import get_segment_filter_range, wrap_separator, get_number
from utilities.constants import STATUS_TYPE_DICT, BALANCE_TYPE_DICT, REPORT_TYPE, ACCOUNT_TYPE_DICT, \
    SEGMENT_FILTER_DICT, REPORT_TEMPLATE_TYPES_DICT


class Print_GLBalanceSheet:
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
        # 1st row
        header_data = []
        row1_info1 = datetime.datetime.now().strftime('%d/%m/%Y %r')
        row1_info2 = ""
        header_data.append([row1_info1, row1_info2])

        header_table = Table(header_data, colWidths=[280, 200, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('TOPPADDING', (0, 0), (-1, -1), -0.2),
             ('BOTTOMPADDING', (0, 0), (-1, -1), -0.2),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, report_type, filter_type, from_val, to_val):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = portrait(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=portrait(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=11))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))
        styles.add(ParagraphStyle(name='RedNumber', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=11,
                                  textColor=colors.red))

        # Draw Content of PDF
        # design interface header
        # condition input
        array_data = str(issue_from).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        self.company_id = company_id
        company = Company.objects.get(pk=company_id)

        elements = []

        if SEGMENT_FILTER_DICT['Segment'] == filter_type:
            segment_code_range = get_segment_filter_range(company_id, int(from_val), int(to_val), 'id')

            for segment_code in segment_code_range:
                table_content = self.print_balance_sheet_by_segment(
                    array_data, company, company_id,
                    filter_type, from_val, issue_from, issue_to,
                    report_type, segment_code, styles, to_val, elements)

                self.optimize_table(elements, table_content, False, segment_code)
                elements.append(PageBreak())

        else:
            table_content = self.print_balance_sheet_by_acc_code(
                array_data, company, company_id,
                filter_type, from_val, issue_from, issue_to,
                report_type, styles, to_val, elements)

            # self.print_content(elements, table_content)
            self.optimize_table(elements, table_content, True)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                      issue_to=issue_to
                                      ),
                  onLaterPages=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                       issue_to=issue_to),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def optimize_table(self, elements, table_content, increment=False, segment_code_id=0):
        company = Company.objects.get(pk=self.company_id)
        if company.use_segment:
            if segment_code_id:
                segment_code = CostCenters.objects.get(pk=segment_code_id).code
            else:
                last_segment = CostCenters.objects.filter(company_id=self.company_id).last()
                segment_code = last_segment.code if last_segment else ''

            new_table_content = []
            for content in table_content:
                table_name = content[0]
                table_data = content[1]
                if new_table_content == []:
                    new_table_content.append(content)
                    continue

                if len(table_data) != 1:
                    last_acc = last_amount = ''
                    i = 0
                    pop_index = []
                    appended = False
                    for list_data in table_data:
                        if len(list_data) != 6:  # We are only interested for list_data that contains account information
                            new_table_content.append([table_name, table_data])
                            appended = True
                            break

                        if segment_code_id == 0:  # code for only account filter
                            if list_data[1] is not '':
                                account = list_data[1]
                                if len(account) > 4:  # if length is more than 4 chars
                                    segment = account[4:]
                                account = account[:4]
                            else:
                                continue

                            description = list_data[2]

                            list_data[1] = account
                            try:
                                text = str(description.text)
                                text = text.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                list_data[2] = Paragraph(text, description.style)
                            except:
                                text = str(description)
                                text = text.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                                list_data[2] = text

                            if last_acc == account:
                                if list_data[4].find(')') > 0:
                                    list_data[4] = intcomma("%.2f" % (get_number(list_data[4]) + get_number(last_amount)))
                                    list_data[4] = '(' + list_data[4] + ')'
                                else:
                                    list_data[4] = intcomma("%.2f" % (get_number(list_data[4]) + get_number(last_amount)))
                                pop_index.append(i - 1)

                            last_acc = account
                            last_amount = list_data[4]
                            i += 1

                    for index in pop_index:
                        table_data.pop(index)  # removing duplicate account

                    if not appended:
                        new_table_content.append([table_name, table_data])

                else:
                    list_data = table_data[0]
                    if len(list_data) != 6:  # We are only interested for list_data that contains account information
                        new_table_content.append([table_name, table_data])
                        continue

                    account = list_data[1]
                    if len(account) > 4:  # if length is more than 4 chars
                        segment = account[4:]
                    account = account[:4]
                    description = list_data[2]

                    # Get the last record
                    last = new_table_content.pop()
                    last_table_name = last[0]
                    last_table_data = last[1]

                    # If last_data is not account info, put back and proceed to next one
                    if len(last_table_data) != 1:
                        new_table_content.append([last_table_name, last_table_data])
                        new_table_content.append([table_name, table_data])
                        continue

                    last_list_data = last_table_data[0]

                    if len(last_list_data) != 6:
                        new_table_content.append([last_table_name, last_table_data])
                        new_table_content.append([table_name, table_data])
                        continue

                    last_account = last_list_data[1][:4]

                    if account == last_account:
                        # Adjust the account code
                        table_data[0][1] = account
                        try:
                            text = str(description.text)
                            text = text.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                            table_data[0][2] = Paragraph(text, description.style)
                        except:
                            text = str(description)
                            text = text.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                            table_data[0][2] = text

                        # if we found duplicate, we push new data
                        if increment:  # we need to sum the amount when we push the data
                            if last_table_data[0][4].find(')') > 0 or table_data[0][4].find(')') > 0:
                                table_data[0][4] = intcomma("%.2f" % (get_number(table_data[0][4]) + get_number(last_table_data[0][4])))
                                table_data[0][4] = '(' + table_data[0][4] + ')'
                            else:
                                table_data[0][4] = intcomma("%.2f" % (get_number(table_data[0][4]) + get_number(last_table_data[0][4])))

                        new_table_content.append([table_name, table_data])

                    elif segment_code_id:
                        if segment == segment_code:
                            account = account + segment_code

                        table_data[0][1] = account
                        # otherwise we push both data
                        new_table_content.append([last_table_name, last_table_data])
                        new_table_content.append([table_name, table_data])

                    else:
                        table_data[0][1] = account
                        try:
                            text = str(description.text)
                            text = text.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                            table_data[0][2] = Paragraph(text, description.style)
                        except:
                            text = str(description)
                            text = text.replace(segment_code, '').rstrip(' ').rstrip('/').rstrip('-')
                            table_data[0][2] = text
                        # otherwise we push both data
                        new_table_content.append([last_table_name, last_table_data])
                        new_table_content.append([table_name, table_data])

            # End loop
            self.print_content(elements, new_table_content)
        else:
            self.print_content(elements, table_content)

    def print_content(self, elements, new_table_content):
        for content in new_table_content:
            elements.append(content[0](content[1]))

    def combine_data_per_table(self, sequence, whole_segments_table):
        # We are gonna work for data which has the same table
        current_table = []
        for one_segment in whole_segments_table:
            for content in one_segment:

                if content[0] == sequence:  # If we found the same table name
                    current_table.extend(content[1])  # Create a list consists of the data only

        return current_table

    def remove_duplicates(self, list_data):
        newlist = []
        for data in list_data:
            if data not in newlist:
                newlist.append(data)
        return newlist

    def print_balance_sheet_by_segment(self, array_data, company, company_id, filter_type, from_val, issue_from,
                                       issue_to,
                                       report_type, segment_code, styles, to_val, elements):
        # Our container for 'Flowable' objects
        frst_line, scnd_line, thrd_line, frth_line = get_exchange_rate_header(issue_from, company_id)

        table_content = []

        table_data = []
        segment = CostCenters.objects.get(pk=segment_code)
        table_data.append(['', company.name + ' - ' + segment.name, frst_line])
        table_data.append(['', 'BALANCE SHEET', scnd_line])
        table_data.append(['', "AS AT " + issue_to.strftime('%d/%m/%Y'), thrd_line])
        table_data.append(['', '', frth_line])

        table_content.append([self.table_heading, table_data])

        # end design interface header
        # code
        filter_array = self.init_filter_array()

        FlagMoney = 0
        total = total_long_term = 0
        sum_credit = sum_debit = total_account = 0
        rpt_acc_grp_list = self.createCustomAccGroupList(company_id)
        for j, mFilter in enumerate(filter_array):
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       segment_code_id=segment_code,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Balance Sheet']),
                                                       profit_loss_group__code=mFilter).order_by('code')

            m_account_group = m_name_group = ''
            sum_total_account = 0
            custom_acc_code = None
            custom_acc_code2 = None

            if not account_item_list:
                continue

            for i, mAccount in enumerate(account_item_list):
                mAccount_disctinct_list = []
                mAccount_disctinct_obj = {}
                table_data = []

                # check if difference group
                if m_account_group != mAccount.profit_loss_group.code:
                    m_total, table_data, total, total_account, total_long_term, FlagMoney = \
                        self.output_non_profit_loss_group(
                            FlagMoney, company, i,
                            mAccount, m_account_group, m_name_group,
                            table_content,
                            total, total_account, total_long_term)

                    m_account_group = mAccount.profit_loss_group.code

                # the another line if the same group to start calculation in AccountHistory Table
                if m_account_group == mAccount.profit_loss_group.code:
                    table_data, total, custom_acc_code, sum_total_account = self.process_profit_loss_group(
                        array_data, company_id, custom_acc_code,
                        elements, filter_type, from_val, issue_from, issue_to,
                        mAccount, mAccount_disctinct_list, mAccount_disctinct_obj, m_account_group,
                        report_type, rpt_acc_grp_list, styles,
                        sum_credit, sum_debit, sum_total_account,
                        to_val, total, total_account, segment_code)

                if len(rpt_acc_grp_list) > 0:
                    for custom_account in mAccount_disctinct_list:
                        if custom_account['code'] != custom_acc_code2:
                            custom_acc_code2 = custom_account['code']
                        else:
                            elements = elements[:-1]
                            table_content = table_content[:-1]

                        table_data.append(['', custom_account['code'], custom_account['name'], '',
                                           wrap_separator(custom_account['amount'], m_account_group), ''])

                table_content.append([self.table_profitloss, table_data])

                sum_credit = sum_debit = total_account = 0

                # the end line
                if i == account_item_list.__len__() - 1:
                    m_name_group, total_long_term = self.process_end_line(
                        mAccount, m_account_group, m_name_group, m_total,
                        table_content, total, total_long_term)

                    total = total_account = 0

        # end process data
        # else:  # if there's no order in the selected month
        if table_content.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_content.append([self.table_empty, table_data])

        return table_content

    def print_balance_sheet_by_acc_code(self, array_data, company, company_id, filter_type, from_val, issue_from,
                                        issue_to,
                                        report_type, styles, to_val, elements):
        # Our container for 'Flowable' objects
        frst_line, scnd_line, thrd_line, frth_line = get_exchange_rate_header(issue_from, company_id)

        table_content = []

        table_data = []
        table_data.append(['', company.name, frst_line])
        table_data.append(['', 'BALANCE SHEET', scnd_line])
        table_data.append(['', "AS AT " + issue_to.strftime('%d/%m/%Y'), thrd_line])
        table_data.append(['', '', frth_line])

        table_content.append([self.table_heading, table_data])

        # end design interface header
        # code
        filter_array = self.init_filter_array()

        FlagMoney = 0
        total = total_long_term = 0
        sum_credit = sum_debit = total_account = 0
        rpt_acc_grp_list = self.createCustomAccGroupList(company_id)
        for j, mFilter in enumerate(filter_array):
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Balance Sheet']),
                                                       profit_loss_group__code=mFilter).order_by('account_segment')

            m_account_group = m_name_group = ''
            sum_total_account = 0
            custom_acc_code = None
            custom_acc_code2 = None

            if not account_item_list:
                continue

            for i, mAccount in enumerate(account_item_list):
                mAccount_disctinct_list = []
                mAccount_disctinct_obj = {}
                table_data = []

                # check if difference group
                if m_account_group != mAccount.profit_loss_group.code:
                    m_total, table_data, total, total_account, total_long_term, FlagMoney = \
                        self.output_non_profit_loss_group(
                            FlagMoney, company, i,
                            mAccount, m_account_group, m_name_group,
                            table_content,
                            total, total_account, total_long_term)

                    m_account_group = mAccount.profit_loss_group.code

                # the another line if the same group to start calculation in AccountHistory Table
                if m_account_group == mAccount.profit_loss_group.code:
                    table_data, total, custom_acc_code, sum_total_account = self.process_profit_loss_group(
                        array_data, company_id, custom_acc_code,
                        elements, filter_type, from_val, issue_from, issue_to,
                        mAccount, mAccount_disctinct_list, mAccount_disctinct_obj, m_account_group,
                        report_type, rpt_acc_grp_list, styles,
                        sum_credit, sum_debit, sum_total_account,
                        to_val, total, total_account)

                if len(rpt_acc_grp_list) > 0:
                    for custom_account in mAccount_disctinct_list:
                        if custom_account['code'] != custom_acc_code2:
                            custom_acc_code2 = custom_account['code']
                        else:
                            elements = elements[:-1]
                            table_content = table_content[:-1]

                        table_data.append(['', custom_account['code'], custom_account['name'], '',
                                           wrap_separator(custom_account['amount'], m_account_group), ''])

                table_content.append([self.table_profitloss, table_data])

                sum_credit = sum_debit = total_account = 0

                # the end line
                if i == account_item_list.__len__() - 1:
                    m_name_group, total_long_term = self.process_end_line(
                        mAccount, m_account_group, m_name_group, m_total,
                        table_content, total, total_long_term)

                    total = total_account = 0

        # end process data
        # else:  # if there's no order in the selected month
        if table_content.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_content.append([self.table_empty, table_data])

        return table_content

    def process_profit_loss_group(self, array_data, company_id, custom_acc_code, elements, filter_type, from_val,
                                  issue_from, issue_to, mAccount, mAccount_disctinct_list, mAccount_disctinct_obj,
                                  m_account_group, report_type, rpt_acc_grp_list, styles, sum_credit, sum_debit,
                                  sum_total_account, to_val, total, total_account, segment_code=0):
        total, total_account = self.process_new_data(
            array_data, company_id,
            issue_from, issue_to,
            mAccount, report_type,
            sum_credit, sum_debit, total, total_account)

        table_data, total, custom_acc_code, sum_total_account = self.process_profit_loss(
            array_data, company_id, custom_acc_code, elements,
            filter_type, from_val, issue_from, issue_to,
            mAccount, mAccount_disctinct_list, mAccount_disctinct_obj, m_account_group,
            report_type, rpt_acc_grp_list, styles,
            sum_total_account, to_val, total, total_account, segment_code)

        return table_data, total, custom_acc_code, sum_total_account

    def process_end_line(self, mAccount, m_account_group, m_name_group, m_total, table_content, total, total_long_term):
        table_data = []
        if m_account_group == 'BS-CL':
            total_long_term = (total_long_term + total)
        else:
            total_long_term += total
        # get name for output total: ' FIXED ASSETS'
        if mAccount.profit_loss_group.code == 'BS-FA':
            m_name_group = ' FIXED ASSETS'
            table_data.append(['', '', '', '', wrap_separator(total, 'BS-FA'), ''])
            table_data.append(['', '', '', '', '', ''])
            table_data.append(['', '', 'TOTAL ' + str(m_total), '',
                               wrap_separator(total_long_term, 'BS-FA'), ''])
            table_data.append(['', '', '', '', '', ''])
        elif mAccount.profit_loss_group.code == 'BS-NA':
            m_name_group = ' NON ASSETS'
            table_data.append(['', '', '', '', wrap_separator(total, 'BS-NA'), ''])
            table_data.append(['', '', '', '', '', ''])
            table_data.append(['', '', 'TOTAL ' + str(m_total), '',
                               wrap_separator(total, 'BS-NA'), ''])
            table_data.append(['', '', '', '', '', ''])
        # TOTAL for  25.CURRENT LIABILITIES
        # output Total for group 26.LONG-TERM LIABILITY
        elif m_account_group in ('BS-LL', 'BS-CL'):
            table_data.append(
                ['', '', 'TOTAL ' + str(m_total), '', wrap_separator(total, 'BS-CL'), ''])
            table_data.append(['', '', '', '', '', ''])
            table_data.append(
                ['', '', '', '', wrap_separator(total_long_term, 'BS-LL'), ''])
            table_data.append(['', '', '', '', '', ''])
            total_long_term = 0
        else:
            if m_account_group == 'BS-SE':
                table_data.append(['', '', 'TOTAL ' + str(m_total), '',
                                   wrap_separator(total, 'BS-SE'), ''])
            else:
                table_data.append(['', '', 'TOTAL ' + str(m_total), '',
                                   wrap_separator(total), ''])
            if m_account_group != 'BS-SE':
                table_data.append(['', '', '', '', '', ''])
        if m_account_group == 'BS-LL':
            table_content.append([self.table_bs_ll, table_data])
        elif m_account_group == 'BS-SE':
            table_content.append([self.table_bs_se, table_data])
        else:
            table_content.append([self.table_bs, table_data])
        return m_name_group, total_long_term

    def process_profit_loss(self, array_data, company_id, custom_acc_code, elements, filter_type, from_val, issue_from,
                            issue_to, mAccount, mAccount_disctinct_list, mAccount_disctinct_obj, m_account_group,
                            report_type, rpt_acc_grp_list, styles, sum_total_account, to_val, total,
                            total_account, segment_code=0):
        table_data = []
        company = Company.objects.get(pk=company_id)
        # out put ACCUMULATED DEPRECIATION (case special to output name code)
        # Based on the Excel file to output correct amount (positive or negative number)
        if mAccount.profit_loss_group.code in ('BS-FA', 'BS-NA', 'BS-CA', 'BS-CL', 'BS-LL', 'BS-SE'):
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
                table_data.append(
                    ['', mAccount.code, Paragraph(str(mAccount.name), styles['Normal']), '',
                     wrap_separator(total_account, mAccount.profit_loss_group.code), ''])

        # call PROFIT(LOSS)FOR PERIOD: only in 1 month
        if m_account_group == 'BS-SE':
            FlagReport = 0
            sum_profit_finish = []
            total_retained = retained_sum_credit = retained_sum_debit = 0
            # Get amount of Retained Earnings Accounts
            if segment_code:
                retained_accounts = Account.objects.filter(company_id=company_id, is_active=True,
                                                           is_hidden=0, segment_code_id=segment_code,
                                                           account_type=int(
                                                               ACCOUNT_TYPE_DICT['Retained Earning']))
            else:
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
                    table_data.append(
                        ['', r_account.code, Paragraph(str(r_account.name), styles['Normal']), '',
                         wrap_separator(retained_amount, mAccount.profit_loss_group.code), ''])

            NetPurchase_account_history(company_id, array_data[0], array_data[1], sum_profit_finish,
                                        elements, FlagReport,
                                        filter_type, from_val, to_val,
                                        report_type)

            if len(rpt_acc_grp_list) > 0:
                mAccount_disctinct_list.append({"code": "", "name": str('PROFIT (LOSS) FOR PERIOD '),
                                                "amount": sum_profit_finish[0]})
            else:
                table_data.append(['', '', 'PROFIT (LOSS) FOR PERIOD ', '',
                                   wrap_separator(sum_profit_finish[0], 'BS-SE'), ''])

            total += sum_profit_finish[0] + total_retained
        return table_data, total, custom_acc_code, sum_total_account

    def process_new_data(self, array_data, company_id, issue_from, issue_to, mAccount, report_type, sum_credit,
                         sum_debit, total, total_account):
        company = Company.objects.get(pk=company_id)
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

        # end process new data
        return total, total_account

    def output_non_profit_loss_group(self, FlagMoney, company, i, mAccount, m_account_group, m_name_group,
                                     table_content, total, total_account, total_long_term):
        # get total
        if i != 0:
            # get name for output total
            if mAccount.profit_loss_group.code == 'BS-FA':
                m_name_group = ' FIXED ASSETS'

            # output Total for group 26.LONG-TERM LIABILITY
            total_long_term = self.content_append_liability(
                m_account_group, m_name_group,
                table_content,
                total, total_long_term)

            total = total_account = 0
            m_name_group = ''

        # get first data line output money: only output for first line of report
        if (i == 0) & (FlagMoney == 0):
            FlagMoney = 1
            self.content_append_money(company, table_content)
        m_name_group, m_total = self.get_name_group_total(mAccount, m_name_group)
        table_data = self.output_first_line(mAccount, m_name_group)
        table_content.append([self.table_asset, table_data])

        return m_total, table_data, total, total_account, total_long_term, FlagMoney

    def content_append_money(self, company, table_content):
        table_data = []
        table_data.append(['', '', company.currency.code, ''])
        table_content.append([self.table_money, table_data])

    def content_append_liability(self, m_account_group, m_name_group, table_content, total, total_long_term):
        if m_account_group == 'BS-LL':
            table_data, total_long_term = self.output_longterm_liability(
                total, total_long_term)
        else:
            table_data, total_long_term = self.output_current_liability(
                m_account_group, m_name_group,
                total, total_long_term)
        table_content.append([self.table_liability, table_data])
        return total_long_term

    def output_current_liability(self, m_account_group, m_name_group, total, total_long_term):
        # TOTAL for  25.CURRENT LIABILITIES
        if m_account_group == 'BS-CL':
            total_long_term = (total_long_term + total)
        else:
            total_long_term += total
        # output Total for all group
        table_data = []
        table_data.append(['', '', '', '', wrap_separator(total, 'BS-CL'), ''])
        table_data.append(['', '', '', '', '', ''])
        table_data.append(['', '', 'TOTAL ' + str(m_name_group), '', wrap_separator(total, 'BS-CL'), ''])
        table_data.append(['', '', '', '', '', ''])
        return table_data, total_long_term

    def output_longterm_liability(self, total, total_long_term):
        table_data = []
        table_data.append(['', '', '', '', wrap_separator(total, 'BS-LL'), ''])
        table_data.append(['', '', '', '', '', ''])
        table_data.append(
            ['', '', '', '', wrap_separator(total_long_term, 'BS-LL'), ''])
        table_data.append(['', '', '', '', '', ''])
        total_long_term = 0
        return table_data, total_long_term

    def output_first_line(self, mAccount, m_name_group):
        # output first line title of every group
        table_data = []
        # out put last round :SHAREHOLDERS' EQUITY:
        if mAccount.profit_loss_group.code == 'BS-SE':
            table_data.append(['', 'REPRESENTED BY:-', ''])
            table_data.append(['', '', ''])
        # check if group   1.NET ASSETS,TOTAL NON ASSETS: no need output title of group
        if mAccount.profit_loss_group.code != 'BS-NA':
            table_data.append(['', m_name_group, ''])
        else:
            table_data.append(['', '', ''])
        return table_data

    def get_name_group_total(self, mAccount, m_name_group):
        # check group name for output first line title of every group
        if mAccount.profit_loss_group.code == 'BS-FA':
            m_name_group = 'FIXED ASSETS, AT COST LESS DEPRECIATION'
            m_total = 'FIXED ASSETS'
        elif mAccount.profit_loss_group.code == 'BS-NA':
            m_name_group = ' NON ASSETS '
            m_total = ' NON ASSETS '
        elif mAccount.profit_loss_group.code == 'BS-CA':
            m_name_group = 'CURRENT ASSETS:'
            m_total = 'CURRENT ASSETS:'
        elif mAccount.profit_loss_group.code == 'BS-CL':
            m_name_group = 'CURRENT LIABILITIES:'
            m_total = 'CURRENT LIABILITIES:'
        elif mAccount.profit_loss_group.code == 'BS-LL':
            m_name_group = 'LONG-TERM LIABILITY :'
            m_total = 'LONG-TERM LIABILITY :'
        elif mAccount.profit_loss_group.code == 'BS-SE':
            m_name_group = "SHAREHOLDERS' EQUITY:"
            m_total = "SHAREHOLDERS' EQUITY:"

        return m_name_group, m_total

    def init_filter_array(self):
        # intial account group of report Balance Sheet
        filter_array = []
        # 23.FIXED ASSETS, AT COST LESS DEPRECIATION
        filter_array.append('BS-FA')
        # 1.NET ASSETS,TOTAL NON ASSETS
        filter_array.append('BS-NA')
        # 3.CURRENT ASSETS
        filter_array.append('BS-CA')
        # 25.CURRENT LIABILITIES
        filter_array.append('BS-CL')
        # 26.LONG-TERM LIABILITY
        filter_array.append('BS-LL')
        # 27.SHAREHOLDERS' EQUITY
        filter_array.append('BS-SE')
        return filter_array

    def table_empty(self, table_data):
        table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75,
                                                  60, 85, 90, 130
                                                  ])
        table_body.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
             ]))
        return table_body

    def table_balance_sheet(self, m_account_group, table_data):

        if m_account_group == 'BS-LL':
            item_table = self.table_bs_ll(table_data)
        elif m_account_group == 'BS-SE':
            item_table = self.table_bs_se(table_data)
        else:
            item_table = self.table_bs(table_data)
        return item_table

    def table_bs(self, table_data):
        item_table = Table(table_data, colWidths=[230, 50, 230, 50, 100, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LINEABOVE', (4, 0), (4, 0), 0.25, colors.black),
             ('LINEABOVE', (4, 2), (4, 2), 0.25, colors.black),
             ('LINEBELOW', (4, 2), (4, 2), 0.25, colors.black)
             ]))
        return item_table

    def table_bs_se(self, table_data):
        item_table = Table(table_data, colWidths=[230, 50, 230, 50, 100, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LINEABOVE', (4, 0), (4, 0), 0.25, colors.black),
             ('LINEABOVE', (4, 2), (4, 2), 0.25, colors.black),
             ('LINEBELOW', (4, 0), (4, 0), 4, colors.black),
             ('LINEBELOW', (1, 0), (5, 0), 2, colors.transparent)
             ]))
        return item_table

    def table_bs_ll(self, table_data):
        item_table = Table(table_data, colWidths=[230, 50, 230, 50, 100, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LINEABOVE', (4, 0), (4, 0), 0.25, colors.black),
             ('LINEBELOW', (4, 2), (4, 2), 4, colors.black),
             ('LINEBELOW', (1, 2), (5, 2), 2, colors.transparent)
             ]))
        return item_table

    def table_profitloss(self, table_data):
        item_table = Table(table_data, colWidths=[230, 80, 200, 50, 100, 200])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 0), (1, -1), 'LEFT'),
             ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP')
             ]))
        return item_table

    def table_asset(self, table_data):
        item_table = Table(table_data, colWidths=[180, 370, 250])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP')
             ]))
        return item_table

    def table_money(self, table_data):
        item_table = Table(table_data, colWidths=[180, 350, 100, 170])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (2, 0), (2, 0), 0.25, colors.black),
             ('ALIGN', (2, 0), (2, -1), 'CENTER'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'TOP')
             ]))
        return item_table

    def table_liability(self, table_data):
        item_table = self.table_bs(table_data)
        return item_table

    def table_heading(self, table_data):
        item_table = Table(table_data, colWidths=[100, 310, 100])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (0, 1), (0, -1), s.REPORT_FONT_BOLD),
             ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
             ]))
        return item_table

    def getProvisionalPosted(self, acc_id, company_id, p_perd_year, p_perd_month):
        prov_posted = {'account_id': 0, 'source': 0, 'functional': 0}
        provisional_transaction = Transaction.objects.filter(company_id=company_id, is_hidden=False,
                                                             journal__status=int(STATUS_TYPE_DICT['Prov. Posted']),
                                                             account_id=acc_id,
                                                             journal__perd_year__lte=p_perd_year,
                                                             journal__perd_month__lte=p_perd_month,
                                                             journal__is_hidden=False)
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
        rpt_acct_grp = ReportGroup.objects.filter(company_id=company_id, is_hidden=False,
                                                  report_template_type=REPORT_TEMPLATE_TYPES_DICT['Balance Sheet'])
        for rpt_acc_grp in rpt_acct_grp:
            rpt_acc_grp_obj = {'acc1_id': rpt_acc_grp.account_from.id,
                               'acc2_id': rpt_acc_grp.account_to.id if rpt_acc_grp.account_to else rpt_acc_grp.account_from.id,
                               'acc_code': rpt_acc_grp.account_code_text,
                               'acc_name': rpt_acc_grp.name}
            rpt_acc_grp_list.append(rpt_acc_grp_obj)
        return rpt_acc_grp_list

    def getCustomAccGroup(self, rpt_acc_grp_list, mAccount):
        custom_acc = {"custom_acc_code": None, "custom_acc_name": None}
        for custom_acct in rpt_acc_grp_list:
            if mAccount.id >= custom_acct['acc1_id'] and mAccount.id <= custom_acct['acc2_id']:
                custom_acc['custom_acc_code'] = custom_acct['acc_code']
                custom_acc['custom_acc_name'] = str(custom_acct['acc_name'])
                break
            else:
                custom_acc['custom_acc_code'] = mAccount.code
                custom_acc['custom_acc_name'] = str(mAccount.name)
        return custom_acc
