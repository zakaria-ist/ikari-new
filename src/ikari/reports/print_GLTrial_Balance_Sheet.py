import calendar
import datetime
import os
from functools import partial
from django.db.models import Q
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from accounting.models import FiscalCalendar
from accounts.models import Account, AccountHistory
from companies.models import Company
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.constants import BALANCE_TYPE_DICT, STATUS_TYPE_DICT, TRANSACTION_TYPES, ACCOUNT_TYPE_DICT


class Print_GLTrialBalanceSheet:
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

        fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, period=issue_to.month, fiscal_year=issue_to.year).last()
        if fsc_calendar:
            end_date = fsc_calendar.end_date.strftime('%d/%m/%Y')
        else:
            end_date = issue_to.strftime('%d/%m/%Y')

        # # 2nd row
        row2_info1 = ""
        row2_info2 = "Report (GLTRLR1)"
        row2_info3 = "Trial Balance as of  " + end_date
        header_data.append([row2_info1, row2_info2, row2_info3])
        # # 3rd row
        row3_info1 = ""
        row3_info2 = "In Functional Currency " + str(company.currency.code)
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])
        # # 4rd row
        header_data.append(["", "", ""])

        header_table = Table(header_data, colWidths=[10, 180, 270, 50])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 0), (0, -1), 'LEFT'),
             ('ALIGN', (2, 0), (2, 0), 'CENTER'),
             ('ALIGN', (2, 1), (2, 1), 'CENTER'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
             ('FONT', (2, 1), (2, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (2, 0), (2, 0), 11),
             ('FONTSIZE', (2, 1), (2, 1), 11),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)
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

        fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, period=issue_to.month, fiscal_year=issue_to.year).last()
        if fsc_calendar:
            end_date = fsc_calendar.end_date.strftime('%d/%m/%Y')
        else:
            end_date = issue_to.strftime('%d/%m/%Y')

        # # 2nd row
        row2_info1 = ""
        row2_info2 = "Report (GLTRLR1)"
        row2_info3 = "Trial Balance as of  " + end_date
        header_data.append([row2_info1, row2_info2, row2_info3])
        # # 3rd row
        row3_info1 = ""
        row3_info2 = "In Functional Currency " + str(company.currency.code)
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])

        header_table = Table(header_data, colWidths=[10, 180, 270, 50])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 0), (0, -1), 'LEFT'),
             ('ALIGN', (2, 0), (2, 0), 'CENTER'),
             ('ALIGN', (2, 1), (2, 1), 'CENTER'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('FONT', (2, 0), (2, 0), s.REPORT_FONT_BOLD),
             ('FONT', (2, 1), (2, 1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (2, 0), (2, 0), 11),
             ('FONTSIZE', (2, 1), (2, 1), 11),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_data.append(['', '', '', '', '', '', '', '', ''])
        table_data.append(['', '', '', '', '', '', '', '', ''])
        table_data.append(['', '', '', '', '', '', '', '', ''])
        table_data.append(['', 'Account Number ', '', 'Description ', '', 'Debits', '', 'Credits', ''])

        item_header_table = Table(table_data, colWidths=[5, 85, 5, 260, 5, 95, 5, 95, 3])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('LINEBELOW', (1, -1), (1, -1), 0.25, colors.black),
             ('LINEBELOW', (3, -1), (3, -1), 0.25, colors.black),
             ('LINEBELOW', (5, -1), (5, -1), 0.25, colors.black),
             ('LINEBELOW', (7, -1), (7, -1), 0.25, colors.black),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin + 50 - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, issue_to, acc_list, is_activity):

        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = A4
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=A4)
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RedNumber', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT, textColor=colors.red))

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        # design interface header
        table_data.append(['', 'Sort By', '[Account No.]', ''])
        is_activity_str = '[No]'
        if is_activity == '1':
            is_activity_str = '[Yes]'
        table_data.append(['', 'Include Accounts With No Activity', is_activity_str, ''])
        table_data.append(['', 'For Year-Period', "[" + issue_from + "]", ''])

        acc_list = eval(acc_list)
        if len(acc_list):
            account_list = Account.objects.filter(id__in=acc_list).order_by('code')
        else:
            account_list = Account.objects.filter(is_hidden=False, company_id=company_id).order_by('code')

        table_data.append(['', 'From Account No.', "[" + account_list[0].code + "] To [" + account_list[len(account_list)-1].code + "]", ''])

        table_data.append(['', 'Use Rolled Up Amounts', '[No]', ''])
        item_table = Table(table_data, colWidths=[10, 250, 200, 110])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             #  ('FONT', (1, 0), (1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (1, 0), (0, -1), 'LEFT'),
             ('ALIGN', (2, 0), (1, 1), 'CENTER'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))
        elements.append(item_table)

        table_data = []
        table_data.append(['', '', '', '', '', '', '', '', ''])
        table_data.append(['', 'Account Number', '', 'Description', '', 'Debits', '', 'Credits', ''])
        item_table = Table(table_data, colWidths=[5, 85, 5, 260, 5, 95, 5, 95, 3])
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
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)
             ]))
        elements.append(item_table)
        table_data = []
        # end design interface header

        company = Company.objects.get(pk=company_id)
        if company.currency.is_decimal:
            decimal_place = "%.2f"
        else:
            decimal_place = "%.0f"

        # process table_data
        array_data = str(issue_from).split('-')
        if array_data[1] in ['ADJ', 'CLS']:
            issue_from = datetime.date(int(array_data[0]), 12, 1)
            issue_to = datetime.date(int(array_data[0]), 12,
                                     calendar.monthrange(int(array_data[0]), 12)[1])
        else:
            issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
            issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                     calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])

        account_item_list = account_list.exclude(Q(is_active=False) & Q(deactivate_date=None))
        account_item_list = account_item_list.exclude(deactivate_period__lte=issue_from).values('id').order_by('code').distinct()

        total_debit = total_credit = 0
        total_income = total_income_debit = total_income_credit = 0
        table_data = []
        sum_debit = sum_credit = 0
        mCode = ''
        mCountCode = 0
        if account_item_list:
            for acct in account_item_list:
                mAccount = account_list.filter(id=acct['id']).first()
                if array_data[1] == 'ADJ':
                    item_account = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                                 source_currency__code=company.currency.code,
                                                                 account_id=mAccount.id,
                                                                 period_month__exact='ADJ',
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

                # sum debit,sum credit
                if item_account:
                    if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                        sum_credit += item_account.functional_end_balance
                    elif mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                        sum_debit += item_account.functional_end_balance

                table_data = []
                if mAccount.balance_type == BALANCE_TYPE_DICT['Credit']:
                    if sum_credit < 0:
                        mCountCode += 1
                        table_data.append(['', Paragraph(str(mAccount.code), styles['LeftAlign']), '',
                                           Paragraph(str(mAccount.name), styles['LeftAlign']), '', '', '',
                                           intcomma(decimal_place % sum_credit).replace("-", ""), ''])
                        total_credit += sum_credit
                    elif sum_credit > 0:
                        mCountCode += 1
                        table_data.append(['', Paragraph(str(mAccount.code), styles['LeftAlign']), '',
                                           Paragraph(str(mAccount.name), styles['LeftAlign']), '',
                                           intcomma(decimal_place % sum_credit), '', '', ''])

                        total_debit += sum_credit

                    # if account is Income Statement type, calculate for Net Income
                    if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                        total_income_credit += sum_credit

                elif mAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                    if sum_debit > 0:
                        mCountCode += 1
                        table_data.append(['', Paragraph(str(mAccount.code), styles['LeftAlign']), '',
                                           Paragraph(str(mAccount.name), styles['LeftAlign']), '',
                                           intcomma(decimal_place % sum_debit), '', '', ''])
                        total_debit += sum_debit
                    elif sum_debit < 0:
                        mCountCode += 1
                        table_data.append(['', Paragraph(str(mAccount.code), styles['LeftAlign']), '',
                                           Paragraph(str(mAccount.name), styles['LeftAlign']), '', '', '',
                                           intcomma(decimal_place % sum_debit).replace("-", ""), ''])

                        total_credit += sum_debit

                    # if account is Income Statement type, calculate for Net Income
                    if mAccount.account_type == ACCOUNT_TYPE_DICT['Income Statement']:
                        total_income_debit += sum_debit

                if len(table_data) > 0:
                    item_table = Table(table_data, colWidths=[10, 80, 5, 260, 5, 95, 5, 95, 3])
                    # 6column
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                         ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)
                         ]))
                    elements.append(item_table)

            table_data = []
            table_data.append(
                ['', '', '', 'Total:', '', intcomma(decimal_place % total_debit).replace("-", ""), '',
                 intcomma(decimal_place % total_credit).replace("-", ""), ''])

            total_income = total_income_debit + total_income_credit
            if total_income > 0:
                table_data.append(['', '', '', 'Net Income (Loss) for Accounts Listed:', '',
                                   intcomma(decimal_place % total_income if total_income else '').replace("-", ""), '', '',
                                   ''])
            elif total_income < 0:
                table_data.append(['', '', '', 'Net Income (Loss) for Accounts Listed:', '', '',
                                   '',
                                   intcomma(decimal_place % total_income if total_income else '').replace("-", ""), ''])
            table_data.append(
                ['', str(mCountCode if mCountCode else '') + ' accounts printed', '', '', '', '', '', '', ''])
            item_table = Table(table_data, colWidths=[10, 80, 5, 260, 5, 95, 5, 95, 3])
            # 6column
            if total_income > 0:
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
                     ('LINEABOVE', (5, 0), (5, 0), 0.25, colors.black),
                     ('LINEABOVE', (7, 0), (7, 0), 0.25, colors.black),
                     ('LINEBELOW', (5, 1), (5, 1), 0.25, colors.black),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)
                     ]))
            elif total_income < 0:
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
                     ('LINEABOVE', (5, 0), (5, 0), 0.25, colors.black),
                     ('LINEABOVE', (7, 0), (7, 0), 0.25, colors.black),
                     ('LINEBELOW', (7, 1), (7, 1), 0.25, colors.black),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)
                     ]))
            else:
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
                     ('LINEABOVE', (5, 0), (5, 0), 0.25, colors.black),
                     ('LINEABOVE', (7, 0), (7, 0), 0.25, colors.black),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE)
                     ]))
            elements.append(item_table)

            # # end store

        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[10, 80, 5, 260, 5, 95, 5, 95, 3])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, issue_from=issue_from,
                                      issue_to=issue_to),
                  onLaterPages=partial(self._header_last_footer, company_id=company_id, issue_from=issue_from,
                                       issue_to=issue_to),
                  canvasmaker=partial(NumberedPage, adjusted_height=130))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
