import calendar
import datetime
import os
from functools import partial
from django.db.models import Q
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.dateparse import parse_date
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from accounts.models import Account, AccountHistory
from companies.models import Company
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import STATUS_TYPE_DICT, TRANSACTION_TYPES, ACCOUNT_TYPE_DICT, BALANCE_TYPE_DICT
from utilities.common import round_number


class Print_GLTrialNetSheet:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, issue_from, issue_to, is_activity):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = ""
        row1_info2 = datetime.datetime.now().strftime('%d/%m/%Y %r')
        row1_info3 = company.name
        header_data.append([row1_info1, row1_info2, row1_info3])

        # # 2nd row
        row2_info1 = ""
        row2_info2 = "Report (GLTRLR1N)"
        row2_info3 = "Net Changes from  " + parse_date(str(issue_from)).strftime('%d/%m/%Y') + ' To ' + parse_date(
            str(issue_to)).strftime('%d/%m/%Y')
        header_data.append([row2_info1, row2_info2, row2_info3])
        # # 3rd row
        row3_info1 = ""
        row3_info2 = "In Functional Currency " + str(company.currency.code)
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])
        # # 4rd row
        row4_info1 = ""
        row4_info2 = ""
        row4_info3 = ""
        header_data.append([row4_info1, row4_info2, row4_info3])
        # # 5rd row
        # short = "[-]"
        # if int(acc_from) > 0 and int(acc_end) > 0:
        #     short = "[Account No.]"
        # row5_info1 = ""
        # row5_info2 = "Sort By"
        # row5_info3 = short
        # header_data.append([row5_info1, row5_info2, row5_info3])
        # # 6rd row
        str_is_activity = "[Yes]"
        if int(is_activity) == 0:
            str_is_activity = "[No]"
        row6_info1 = ""
        row6_info2 = "Include Accounts With No Activity"
        row6_info3 = str_is_activity
        header_data.append([row6_info1, row6_info2, row6_info3])
        header_table = Table(header_data, colWidths=[90, 280, 330, 110])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 0), (0, -1), 'LEFT'),
             ('ALIGN', (2, 0), (1, 1), 'CENTER'),
             ('FONT', (1, 1), (1, -1), s.REPORT_FONT_BOLD),
             ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
             ('FONT', (-1, 1), (-1, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 80, doc.height + doc.topMargin - h)
        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _header_last_footer(canvas, doc, company_id, issue_from, issue_to):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = ""
        row1_info2 = datetime.datetime.now().strftime('%d/%m/%Y %r')
        row1_info3 = company.name
        header_data.append([row1_info1, row1_info2, row1_info3])

        # # 2nd row
        row2_info1 = ""
        row2_info2 = "Report (GLTRLR1N)"
        row2_info3 = "Net Changes from  " + parse_date(str(issue_from)).strftime('%d/%m/%Y') + ' To ' + parse_date(
            str(issue_to)).strftime('%d/%m/%Y')
        header_data.append([row2_info1, row2_info2, row2_info3])
        # # 3rd row
        row3_info1 = ""
        row3_info2 = "In Functional Currency " + str(company.currency.code)
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])

        header_table = Table(header_data, colWidths=[90, 280, 330, 110])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 0), (0, -1), 'LEFT'),
             ('ALIGN', (2, 0), (1, 1), 'CENTER'),
             ('FONT', (1, 1), (1, -1), s.REPORT_FONT_BOLD),
             ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
             ('FONT', (-1, 1), (-1, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 80, doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_data.append(['', '', '', '', '', '', '', '', '', ''])
        table_data.append(['', '', '', '', '', '', '', '', '', ''])
        table_data.append(
            ['', '', '', '', '', '--------------Opening Balance--------------', '', '', '', '',
             '--------------Ending Balance--------------', '', '', ''])
        table_data.append(
            ['', 'Account Number', '', 'Description', '', 'Debits', '', 'Credits', '', 'Net Changes', '', 'Debits', '',
             'Credits'])

        item_header_table = Table(table_data, colWidths=[90, 75, 5, 175, 5, 110, 5, 80, 5, 80,
                                                         5, 80, 5, 80])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (5, -1), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
             ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
             ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
             ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
             ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
             ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
             ('LINEBELOW', (13, -1), (13, -1), 0.25, colors.black),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 75, doc.height + doc.topMargin + 20 - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, acc_list, is_activity):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=150, leftMargin=40, topMargin=135,
                                bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=11))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))
        styles.add(ParagraphStyle(name='RedNumber', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=11,
                                  textColor=colors.red))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        # design interface header
        is_activity_str = '[No]'
        if is_activity == '1':
            is_activity_str = '[Yes]'
        table_data.append(['', 'Include Net Income (Loss) Total for Listed Accounts', is_activity_str, ''])
        table_data.append(['', 'For Year-Period', "[" + issue_from + "]" + "[" + issue_to + "]", ''])
        
        acc_list = eval(acc_list)
        if len(acc_list):
            account_list = Account.objects.filter(id__in=acc_list).order_by('code')
        else:
            account_list = Account.objects.filter(is_hidden=False, company_id=company_id).order_by('code')

        table_data.append(['', 'From Account No.', "[" + account_list[0].code + "] To [" + account_list[len(account_list)-1].code + "]", ''])

        table_data.append(['', 'Use Rolled Up Amounts', '[No]', ''])
        item_table = Table(table_data, colWidths=[90, 280, 330, 110])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (1, 1), (1, -1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('TOPPADDING', (0, 0), (-1, 0), 0),
             ]))
        elements.append(item_table)

        table_data = []
        table_data.append(
            ['', '', '', '', '', '--------------Opening Balance--------------', '', '', '', '',
             '--------------Ending Balance--------------', '', '', ''])
        table_data.append(
            ['', 'Account Number', '', 'Description', '', 'Debits', '', 'Credits', '', 'Net Changes', '', 'Debits', '',
             'Credits'])
        item_table = Table(table_data, colWidths=[90, 75, 5, 175, 5, 110, 5, 80, 5, 80,
                                                  5, 80, 5, 80])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (1, 0), (1, 0), 12),
             ('ALIGN', (4, -1), (-1, -1), 'RIGHT'),
             ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
             ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
             ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
             ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
             ('LINEBELOW', (9, -1), (9, -1), 0.25, colors.black),
             ('LINEBELOW', (11, -1), (11, -1), 0.25, colors.black),
             ('LINEBELOW', (13, -1), (13, -1), 0.25, colors.black),
             ]))
        elements.append(item_table)
        table_data = []
        # end design interface header

        # process table_data
        array_data = str(issue_from).split('-')
        array_data_to = str(issue_to).split('-')
        if array_data[1] in ['ADJ', 'CLS']:
            issue_from = datetime.date(int(array_data[0]), 12, 1)
        else:
            issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        if array_data_to[1] in ['ADJ', 'CLS']:
            issue_to = datetime.date(int(array_data_to[0]), 12,
                                    calendar.monthrange(int(array_data_to[0]), 12)[1])
        else:
            issue_to = datetime.date(int(array_data_to[0]), int(array_data_to[1]),
                                    calendar.monthrange(int(array_data_to[0]), int(array_data_to[1]))[1])
        
        account_item_list = account_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        account_item_list = account_item_list.exclude(deactivate_period__lte=issue_from).values('id').order_by('code').distinct()

        total_debit = total_credit = total_debit_to = total_credit_to = total_net = sum_net = 0
        table_data = []
        sum_debit = sum_credit = 0
        mFinalDebit = mFinalCredit = mFinalDebit_to = mFinalCredit_to = 0

        # for Net Income calculation
        open_total_income = open_total_income_debit = open_total_income_credit = 0
        end_total_income = end_total_income_debit = end_total_income_credit = 0

        mCode = ''
        mCountCode = 0
        company = Company.objects.get(pk=company_id)
        if company.currency.is_decimal:
            decimal_place = "%.2f"
        else:
            decimal_place = "%.0f"
        if account_item_list:
            for acct in account_item_list:
                mAccount = account_list.filter(id=acct['id']).first()
                item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0, account_id=mAccount.id)\
                    .exclude(source_currency_id__isnull=True)

                if mCode != mAccount.code:
                    mCountCode += 1
                    mCode = mAccount.code
                    sum_debit = []
                    sum_credit = []
                # call function for from_month
                get_data(item_account, sum_credit, sum_debit, mAccount.balance_type, array_data[0], array_data[1], 1)
                mFinalDebit = sum_debit[0]
                total_debit += mFinalDebit
                mFinalCredit = sum_credit[0]
                total_credit += mFinalCredit
                # call function for to_month
                sum_debit_to = []
                sum_credit_to = []
                get_data(item_account, sum_credit_to, sum_debit_to, mAccount.balance_type, array_data_to[0],
                         array_data_to[1],
                         2)
                mFinalDebit_to = sum_debit_to[0]
                total_debit_to += mFinalDebit_to
                mFinalCredit_to = sum_credit_to[0]
                total_credit_to += mFinalCredit_to
                # calculation sum net change for every account
                total_net_change = []
                get_net(item_account, total_net_change, issue_from, issue_to)
                sum_net = total_net_change[0]
                total_net += sum_net

                table_data = []

                a = Paragraph(str(mAccount.code), styles['Normal'])

                if mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                    open_credit_balance = ''
                    end_credit_balance = ''
                    if sum_debit[0] >= 0:
                        open_debit_balance = intcomma(decimal_place % round_number(sum_debit[0])).replace("-", "")
                    else:
                        open_debit_balance = Paragraph(intcomma(decimal_place % round_number(sum_debit[0])).replace("-", ""),
                                                       styles['RedNumber'])
                    if sum_debit_to[0] >= 0:
                        end_debit_balance = intcomma(decimal_place % round_number(sum_debit_to[0])).replace("-", "")
                    else:
                        end_debit_balance = Paragraph(intcomma(decimal_place % round_number(sum_debit_to[0])).replace("-", ""),
                                                      styles['RedNumber'])

                    # if account is Income Statement type, calculate for Net Income
                    if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                        open_total_income_debit += sum_debit[0]
                        end_total_income_debit += sum_debit_to[0]

                elif mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                    open_debit_balance = ''
                    end_debit_balance = ''
                    if sum_credit[0] <= 0:
                        open_credit_balance = intcomma(decimal_place % round_number(sum_credit[0])).replace("-", "")
                    else:
                        open_credit_balance = Paragraph(intcomma(decimal_place % round_number(sum_credit[0])).replace("-", ""),
                                                        styles['RedNumber'])
                    if sum_credit_to[0] <= 0:
                        end_credit_balance = intcomma(decimal_place % round_number(sum_credit_to[0])).replace("-", "")
                    else:
                        end_credit_balance = Paragraph(intcomma(decimal_place % round_number(sum_credit_to[0])).replace("-", ""),
                                                       styles['RedNumber'])

                    # if account is Income Statement type, calculate for Net Income
                    if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                        open_total_income_credit += sum_credit[0]
                        end_total_income_credit += sum_credit_to[0]

                table_data.append(['',
                                   a, '',
                                   Paragraph(str(mAccount.name), styles['Normal']), '',
                                   open_debit_balance,
                                   '',
                                   open_credit_balance,
                                   '',
                                   intcomma(decimal_place % round_number(total_net_change[0]) if total_net_change else ''),
                                   '',
                                   end_debit_balance,
                                   '',
                                   end_credit_balance])

                item_table = Table(table_data, colWidths=[90, 75, 5, 175, 5, 110, 5, 80, 5, 80,
                                                          5, 80, 5, 80])
                # 6column
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ]))
                elements.append(item_table)

                sum_debit = sum_credit = 0
                mFinalDebit = mFinalCredit = 0

            table_data = []
            table_data.append(['', '', '', 'Total:', '', intcomma(decimal_place % round_number(total_debit)).replace("-", ""),
                               '', intcomma(decimal_place % round_number(total_credit)).replace("-", ""), '', intcomma(decimal_place %
                                                                                                                       round_number(total_net)), '', intcomma(decimal_place % round_number(total_debit_to)).replace("-", ""), '',
                               intcomma(decimal_place % round_number(total_credit_to)).replace("-", "")])
        # calculate Net Incom for the period

        open_total_income = open_total_income_debit + open_total_income_credit
        end_total_income = end_total_income_debit + end_total_income_credit

        total_income = end_total_income - open_total_income
        if total_income >= 0:
            table_data.append(['', '', '', 'Net Income (Loss) for Accounts Listed:', '', '', '',
                               '', '', '', '', intcomma(decimal_place % round_number(total_income)).replace("-", ""), '', ''])
        else:
            table_data.append(['', '', '', 'Net Income (Loss) for Accounts Listed:', '', '', '',
                               '', '', '', '', '', '',
                               intcomma(decimal_place % round_number(total_income)).replace("-", "")])

        table_data.append(['', str(mCountCode if mCountCode else '') + ' accounts printed',
                           '', '', '', '', '', '', '', '',
                           '', '', '', ''])
        item_table = Table(table_data, colWidths=[90, 75, 5, 175, 5, 110, 5, 80, 5, 80,
                                                  5, 80, 5, 80])
        # 6column
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (5, 0), (5, 0), 0.25, colors.black),
             ('LINEBELOW', (7, 0), (7, 0), 0.25, colors.black),
             ('LINEBELOW', (9, 0), (9, 0), 0.25, colors.black),
             ('LINEBELOW', (11, 0), (11, 0), 0.25, colors.black),
             ('LINEBELOW', (13, 0), (13, 0), 0.25, colors.black),
             ('LINEABOVE', (5, 0), (5, 0), 0.25, colors.black),
             ('LINEABOVE', (7, 0), (7, 0), 0.25, colors.black),
             ('LINEABOVE', (9, 0), (9, 0), 0.25, colors.black),
             ('LINEABOVE', (11, 0), (11, 0), 0.25, colors.black),
             ('LINEABOVE', (13, 0), (13, 0), 0.25, colors.black),
             ('LINEBELOW', (11, 1), (11, 1), 0.25, colors.black),
             ('LINEBELOW', (13, 1), (13, 1), 0.25, colors.black),
             ]))
        elements.append(item_table)

        # # end store

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[90, 155, 5, 190, 5, 150, 5, 150, 50])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                      issue_to=issue_to, is_activity=is_activity),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                       issue_to=issue_to),
                  canvasmaker=partial(NumberedPage, adjusted_height=-110, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


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
