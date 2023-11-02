import calendar
import datetime
import os
from decimal import Decimal
from functools import partial
from django.db.models import Q
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
from currencies.models import ExchangeRate
from companies.models import Company, CostCenters
from reports.numbered_page import NumberedPage
from transactions.models import Transaction
from utilities.common import wrap_text, get_segment_filter_range
from utilities.constants import STATUS_TYPE_DICT, BALANCE_TYPE_DICT, REPORT_TYPE, ACCOUNT_TYPE_DICT, \
    SEGMENT_FILTER_DICT, MONTHS_STR_DICT


class Print_GLProfitLoss:
    def __init__(self, buffer, pagesize, report_type):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
        self.report_type = report_type
        self.pl_custom_acc_grp = None

    @staticmethod
    def _header_footer(canvas, doc, issue_from):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # 1st row
        header_data = []
        row1_info1 = datetime.datetime.now().strftime('%d/%m/%Y %r')
        row1_info2 = ""
        header_data.append([row1_info1, row1_info2])

        header_table = Table(header_data, colWidths=[280, 330, 200])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, issue_from, filter_type, from_val, to_val):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = portrait(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=80, bottomMargin=42, pagesize=portrait(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=11))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT_BOLD, textColor=colors.red, alignment=TA_RIGHT, fontSize=11))
        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        # design interface header
        array_data = str(issue_from).split('-')
        issue_from = datetime.date(int(array_data[0]), int(array_data[1]), 1)
        issue_to = datetime.date(int(array_data[0]), int(array_data[1]),
                                 calendar.monthrange(int(array_data[0]), int(array_data[1]))[1])
        company = Company.objects.get(pk=company_id)
        frst_line, scnd_line, thrd_line, frth_line = get_exchange_rate_header(issue_from, company_id)
        if SEGMENT_FILTER_DICT['Account'] == filter_type:  # account
            table_data.append(['', company.name, frst_line])
            table_data.append(['', 'TRADING AND PROFIT AND LOSS ACCOUNT', scnd_line])
            table_data.append(['', "FOR THE MONTH OF " + issue_to.strftime('%d/%m/%Y'), thrd_line])
            table_data.append(['', '', frth_line])
            table_data.append(['', '', ''])

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
            elements.append(item_table)

        # end design interface header
        # get account
        account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                   account_type=int(ACCOUNT_TYPE_DICT['Income Statement'])). \
            order_by('account_group_id').distinct()

        if account_item_list:
            self.pl_custom_acc_grp = createCustomAccGroupList(company_id)

            # the first to check group report net sale
            table_data = []
            FlagReport = 1
            sum_profit_finish = []
            if SEGMENT_FILTER_DICT['Segment'] == filter_type:  # segment
                segment_code_range = get_segment_filter_range(company_id, int(from_val), int(to_val), 'id')
                for segment_code in segment_code_range:
                    NetPurchase_account_history(company_id, array_data[0], array_data[1], sum_profit_finish,
                                                elements, FlagReport, filter_type, from_val, to_val,
                                                self.report_type, self.pl_custom_acc_grp, segment_code, issue_to)
                    elements.append(PageBreak())
            else:
                table_data = []
                table_data.append(['', '', '', '', '', ''])
                table_data.append(['', '', 'CURRENT', '', 'YEAR TO', ''])
                table_data.append(['', '', 'MONTH', '', 'DATE', ''])
                table_data.append(['', '', company.currency.code, '', company.currency.code, ''])
                item_table = Table(table_data, colWidths=[10, 350, 70, 10, 70, 10])
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('LINEBELOW', (2, -1), (4, -1), 0.25, colors.black),
                     ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                     ]))
                elements.append(item_table)
                table_data = []

                NetPurchase_account_history(company_id, array_data[0], array_data[1], sum_profit_finish,
                                            elements, FlagReport, filter_type, from_val, to_val,
                                            self.report_type, self.pl_custom_acc_grp)

        # end process data
        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75, 60, 85, 90, 130])
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, issue_from=issue_from
                                      ),
                  onLaterPages=partial(self._header_footer, issue_from=issue_from),
                  canvasmaker=partial(NumberedPage, adjusted_height=140))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf


# LESS : COST OF GOODS SOLD
def NetPurchase_account_history(company_id, year, month, sum_profit_finish,
                                elements, FlagReport,
                                filter_type=SEGMENT_FILTER_DICT['Account'],
                                from_val="", to_val="",
                                report_type=dict(REPORT_TYPE)['Standard'],
                                custom_acc_grp=None, segment_code_id=0, issue_to=datetime.datetime.now()):
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

    # Our container for 'Flowable' objects
    month = int(month)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlignBlack', fontName=s.REPORT_FONT, alignment=TA_RIGHT, fontSize=11))
    styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=11))
    styles.add(
        ParagraphStyle(name='RightAlignRed', fontName=s.REPORT_FONT_BOLD, textColor=colors.red, alignment=TA_RIGHT,
                       fontSize=11))
    # get account
    filter_array = []
    # sale
    filter_array.append('PL-NETSALE')

    # purchase
    filter_array.append('PL-PURCH')

    # cost of good sold
    filter_array.append('PL-COGS')

    # OTHER INCOME OTHER REVENUE
    filter_array.append('PL-REVENUE')

    #  EXPENDITURE
    filter_array.append('PL-EXPENSE')

    #  TOTAL EXCH GAIN/(LOSS)
    filter_array.append('PL-EXC')

    colWidths = [10, 80, 240, 10, 80, 10, 80, 10]

    total_good_sold_change = total_good_sold_balance = 0
    total_profit_change = total_profit_balance = 0
    total_revenue_change = total_revenue_balance = 0
    # NET PROFIT / (LOSS)BEFORE TAXES / EXCH DIFF
    total_net_profit_change = total_net_profit_balance = 0
    #  NET PROFIT/(LOSS) AFTER INCOME TAXES
    total_net_profit_tax_change = total_net_profit_tax_balance = 0
    # elements = []
    company = Company.objects.get(pk=company_id)
    if SEGMENT_FILTER_DICT['Segment'] == filter_type and segment_code_id:

        # print segment header
        frst_line, scnd_line, thrd_line, frth_line = get_exchange_rate_header(issue_from, company_id)
        table_data = []
        segment = CostCenters.objects.get(pk=segment_code_id)
        table_data.append(['', company.name + ' - ' + segment.name, frst_line])
        table_data.append(['', 'TRADING AND PROFIT AND LOSS ACCOUNT', scnd_line])
        table_data.append(['', "FOR THE MONTH OF " + issue_to.strftime('%d/%m/%Y'), thrd_line])
        table_data.append(['', '', frth_line])
        table_data.append(['', '', ''])
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
        elements.append(item_table)

        table_data = []
        table_data.append(['', '', '', '', '', ''])
        table_data.append(['', '', 'CURRENT', '', 'YEAR TO', ''])
        table_data.append(['', '', 'MONTH', '', 'DATE', ''])
        table_data.append(['', '', company.currency.code,
                           '', company.currency.code, ''])
        item_table = Table(table_data, colWidths=[10, 360, 70, 5, 70, 5])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                ('LINEBELOW', (2, -1), (4, -1), 0.25, colors.black),
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
             ]))
        elements.append(item_table)

    table_data = []
    is_stock_closing = 0
    acc_stock = ''
    name_stock = ''
    sum_net_stock = 0
    sum_balance_stock = 0
    is_4550_grouped = False
    last_segment = CostCenters.objects.filter(company_id=company_id).last()
    segment_code = last_segment.code if last_segment else ''
    for j, mFilter in enumerate(filter_array):
        if SEGMENT_FILTER_DICT['Account'] == filter_type:  # account
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Income Statement']),
                                                       profit_loss_group__code=mFilter).order_by('account_segment').distinct()
        else:
            account_item_list = Account.objects.filter(company_id=company_id, is_active=True, is_hidden=0,
                                                       segment_code_id=segment_code_id,
                                                       account_type=int(ACCOUNT_TYPE_DICT['Income Statement']),
                                                       profit_loss_group__code=mFilter).order_by('code').distinct()

        if account_item_list:
            if mFilter == 'PL-COGS':
                table_data.append(['', '', '', '', '', '', '', ''])
                table_data.append(
                    ['', 'LESS : COST OF GOODS SOLD',
                     '', '', '', '', '', ''])
            if mFilter == 'PL-EXPENSE':
                table_data.append(['', '', '', '', '', '', '', ''])
                table_data.append(
                    ['', 'LESS : EXPENDITURE',
                     '', '', '', '', '', ''])
        total_change = total_balance = 0
        sum_change = sum_balance = 0
        total_sum_change = total_sum_balance = 0
        custom_acc_code = None
        if account_item_list:
            # the first to check group report net sale
            # group Sale code is 13
            for i, mAccount in enumerate(account_item_list):
                item_account_q = AccountHistory.objects.filter(company_id=company_id, is_hidden=0,
                                                               account_id=mAccount.id, period_month__exact=month,
                                                               period_year__exact=year)
                item_account = item_account_q.filter(Q(source_currency_id=company.currency_id) | Q(source_currency_id__isnull=True))
                sum_change = sum_balance = 0
                if item_account:
                    prov_posted_amount_per_account = 0
                    for j, iAccount in enumerate(item_account):
                        if report_type == dict(REPORT_TYPE)['Provisional']:
                            prov_posted_amount_per_account = getProvisionalPostedAmount(company_id, year, month,
                                                                                        mFilter, mAccount.id,
                                                                                        iAccount.source_currency_id)
                        sum_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                        sum_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)
                        total_change += iAccount.functional_net_change + Decimal(prov_posted_amount_per_account)
                        total_balance += iAccount.functional_end_balance + Decimal(prov_posted_amount_per_account)
                        str_sum_change, style_sum_change = wrap_text(sum_change, mFilter)
                        str_sum_balance, style_sum_balance = wrap_text(sum_balance, mFilter)
                    if FlagReport == 1:
                        if mFilter == 'PL-EXC':
                            if SEGMENT_FILTER_DICT['Account'] == filter_type and company.use_segment:  # account
                                try:
                                    last_data = table_data.pop()
                                except:
                                    last_data = None
                                    table_data.append(
                                        ['', mAccount.account_segment,
                                         Paragraph(str(mAccount.name).replace(segment_code, '').replace(
                                             '-', '').replace('/', ''), styles['Normal']), '',
                                         Paragraph(str_sum_change, styles[style_sum_change]), '',
                                         Paragraph(str_sum_balance, styles[style_sum_balance]), ''])
                                if last_data:
                                    if last_data[1] == mAccount.account_segment:
                                        if str(last_data[4].text).find(')') > 0:
                                            temp_change = Decimal(str(last_data[4].text).replace(
                                                ',', '').replace('(', '').replace(')', ''))
                                            last_sum_change = Decimal.copy_negate(temp_change) + sum_change
                                        else:
                                            last_sum_change = Decimal(str(last_data[4].text).replace(
                                                ',', '').replace('(', '').replace(')', '')) + sum_change
                                        if str(last_data[6].text).find(')') > 0:
                                            temp_balance = Decimal(str(last_data[6].text).replace(
                                                ',', '').replace('(', '').replace(')', ''))
                                            last_sum_balance = Decimal.copy_negate(temp_balance) + sum_balance
                                        else:
                                            last_sum_balance = Decimal(str(last_data[6].text).replace(
                                                ',', '').replace('(', '').replace(')', '')) + sum_balance
                                        str_sum_change, style_sum_change = wrap_text(last_sum_change)
                                        str_sum_balance, style_sum_balance = wrap_text(last_sum_balance)
                                        table_data.append(
                                            ['', mAccount.account_segment,
                                             Paragraph(str(mAccount.name).replace(segment_code, '').replace(
                                                 '-', '').replace('/', ''), styles['Normal']), '',
                                             Paragraph(str_sum_change, styles[style_sum_change]), '',
                                             Paragraph(str_sum_balance, styles[style_sum_balance]), ''])
                                    else:
                                        table_data.append(last_data)
                                        table_data.append(
                                            ['', mAccount.account_segment,
                                             Paragraph(str(mAccount.name).replace(segment_code, '').replace(
                                                 '-', '').replace('/', ''), styles['Normal']), '',
                                             Paragraph(str_sum_change, styles[style_sum_change]), '',
                                             Paragraph(str_sum_balance, styles[style_sum_balance]), ''])

                            else:
                                table_data.append(
                                    ['',
                                     mAccount.code,
                                     Paragraph(str(mAccount.name), styles['Normal']),
                                     '',
                                     Paragraph(str_sum_change, styles[style_sum_change]),
                                     '',
                                     Paragraph(str_sum_balance, styles[style_sum_balance]),
                                     ''])
                            if custom_acc_grp and len(custom_acc_grp) > 0:
                                table_data = table_data[:-1]
                                custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                if custom_acc['custom_acc_code'] != custom_acc_code:
                                    total_sum_change = sum_change
                                    total_sum_balance = sum_balance
                                    custom_acc_code = custom_acc['custom_acc_code']
                                else:
                                    total_sum_change += sum_change
                                    total_sum_balance += sum_balance
                                    table_data = table_data[:-1]
                                cus_sum_change, cus_style_sum_change = wrap_text(total_sum_change, mFilter)
                                cus_sum_balance, cus_style_sum_balance = wrap_text(total_sum_balance, mFilter)
                                table_data.append(['', custom_acc_code,
                                                   Paragraph(str(custom_acc['custom_acc_name']), styles['Normal']), '',
                                                   Paragraph(cus_sum_change, styles[cus_style_sum_change]), '',
                                                   Paragraph(cus_sum_balance, styles[cus_style_sum_balance]), ''])
                        else:
                            if SEGMENT_FILTER_DICT['Account'] == filter_type and company.use_segment:  # account
                                try:
                                    last_data = table_data.pop()
                                except:
                                    last_data = None
                                    table_data.append(
                                        ['', mAccount.account_segment,
                                         Paragraph(str(mAccount.name).replace(segment_code, '').replace(
                                             '-', '').replace('/', ''), styles['Normal']), '',
                                         Paragraph(str_sum_change, styles[style_sum_change]), '',
                                         Paragraph(str_sum_balance, styles[style_sum_balance]), ''])
                                if last_data:
                                    if last_data[1] == mAccount.account_segment:
                                        if str(last_data[4].text).find(')') > 0:
                                            temp_change = Decimal(str(last_data[4].text).replace(
                                                ',', '').replace('(', '').replace(')', ''))
                                            last_sum_change = Decimal.copy_negate(temp_change) + sum_change
                                        else:
                                            last_sum_change = Decimal(str(last_data[4].text).replace(
                                                ',', '').replace('(', '').replace(')', '')) + sum_change
                                        if str(last_data[6].text).find(')') > 0:
                                            temp_balance = Decimal(str(last_data[6].text).replace(
                                                ',', '').replace('(', '').replace(')', ''))
                                            last_sum_balance = Decimal.copy_negate(temp_balance) + sum_balance
                                        else:
                                            last_sum_balance = Decimal(str(last_data[6].text).replace(
                                                ',', '').replace('(', '').replace(')', '')) + sum_balance
                                        str_sum_change, style_sum_change = wrap_text(last_sum_change)
                                        str_sum_balance, style_sum_balance = wrap_text(last_sum_balance)
                                        table_data.append(
                                            ['', mAccount.account_segment,
                                             Paragraph(str(mAccount.name).replace(segment_code, '').replace(
                                                 '-', '').replace('/', ''), styles['Normal']), '',
                                             Paragraph(str_sum_change, styles[style_sum_change]), '',
                                             Paragraph(str_sum_balance, styles[style_sum_balance]), ''])
                                    else:
                                        table_data.append(last_data)
                                        table_data.append(
                                            ['', mAccount.account_segment,
                                             Paragraph(str(mAccount.name).replace(segment_code, '').replace(
                                                 '-', '').replace('/', ''), styles['Normal']), '',
                                             Paragraph(str_sum_change, styles[style_sum_change]), '',
                                             Paragraph(str_sum_balance, styles[style_sum_balance]), ''])
                            else:
                                table_data.append(['', mAccount.code, Paragraph(str(mAccount.name), styles['Normal']), '',
                                                   Paragraph(str_sum_change, styles[style_sum_change]), '',
                                                   Paragraph(str_sum_balance, styles[style_sum_balance]), ''])
                                if custom_acc_grp and len(custom_acc_grp) > 0:
                                    table_data = table_data[:-1]
                                    custom_acc, is_4550_grouped = getCustomAccGroup(custom_acc_grp, mAccount)
                                    if custom_acc['custom_acc_code'] != custom_acc_code:
                                        total_sum_change = sum_change
                                        total_sum_balance = sum_balance
                                        custom_acc_code = custom_acc['custom_acc_code']
                                    else:
                                        total_sum_change += sum_change
                                        total_sum_balance += sum_balance
                                        table_data = table_data[:-1]
                                    cus_sum_change, cus_style_sum_change = wrap_text(total_sum_change, mFilter)
                                    cus_sum_balance, cus_style_sum_balance = wrap_text(total_sum_balance, mFilter)
                                    table_data.append(['', custom_acc_code,
                                                       Paragraph(str(custom_acc['custom_acc_name']), styles['Normal']), '',
                                                       Paragraph(cus_sum_change, styles[cus_style_sum_change]), '',
                                                       Paragraph(cus_sum_balance, styles[cus_style_sum_balance]), ''])
                                if mAccount.code == '4550':
                                    is_stock_closing = 1
                                    acc_stock = mAccount.code
                                    name_stock = mAccount.name
                                    sum_net_stock = sum_change
                                    sum_balance_stock = sum_balance
                                    if not is_4550_grouped:
                                        table_data = table_data[:-1]

        if (mFilter == 'PL-PURCH') | (mFilter == 'PL-COGS'):
            total_good_sold_change += total_change
            total_good_sold_balance += total_balance

            # get sum group   GROSS PROFIT
        if mFilter == 'PL-NETSALE':
            total_profit_change += total_change
            total_profit_balance += total_balance
        if mFilter == 'PL-COGS':
            total_profit_change += total_good_sold_change
            total_profit_balance += total_good_sold_balance

            # out put sum group  COST OF GOODS SOLD, GROSS PROFIT
        if mFilter == 'PL-REVENUE':
            total_revenue_change = total_profit_change + total_change
            total_revenue_balance = total_profit_balance + total_balance

            # NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF
        if mFilter == 'PL-EXPENSE':
            total_net_profit_change = total_revenue_change + total_change
            total_net_profit_balance = total_revenue_balance + total_balance

            # NET PROFIT/(LOSS) AFTER INCOME TAXES
        if mFilter == 'PL-EXC':
            total_net_profit_tax_change = total_net_profit_change + total_change
            total_net_profit_tax_balance = total_net_profit_balance + total_balance
            sum_profit_finish.append(total_net_profit_tax_balance)
        if FlagReport == 1:
            if table_data:
                if mFilter == 'PL-COGS':
                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP')
                         ]))
                    elements.append(item_table)
                    table_data = []
                    if is_stock_closing:
                        if not is_4550_grouped:
                            table_data.append(['', '', '', '',
                                               intcomma(
                                                   "%.2f" % (total_good_sold_change - Decimal(sum_net_stock))).replace(
                                                   "-", ""), '',
                                               intcomma("%.2f" % (
                                                   total_good_sold_balance - Decimal(sum_balance_stock))).replace("-",
                                                                                                                  ""),
                                               ''])

                            table_data.append(['', acc_stock, Paragraph(str(name_stock), styles['Normal']), '',
                                               intcomma("%.2f" % sum_net_stock).replace("-", ""), '',
                                               intcomma("%.2f" % sum_balance_stock).replace("-", ""), ''])

                    table_data.append(
                        ['', ' COST OF GOODS SOLD',
                         '', '',
                         intcomma("%.2f" % total_good_sold_change).replace(
                             "-", ""),
                         '', intcomma("%.2f" % total_good_sold_balance).replace(
                             "-", ""), ''])
                    table_data.append(['', '', '', '', '', '', '', ''])
                    if total_profit_change > 0:
                        table_data.append(['',
                                           Paragraph(str(' GROSS PROFIT '), styles['Normal']), '', '',
                                           Paragraph(
                                               '(' + intcomma("%.2f" % total_profit_change).replace("-", "") + ')',
                                               styles['RightAlignRed']), '',
                                           intcomma("%.2f" % total_profit_balance).replace("-", ""), ''])
                    else:
                        table_data.append(['',
                                           Paragraph(str(' GROSS PROFIT '), styles['Normal']), '', '',
                                           intcomma("%.2f" % total_profit_change).replace("-", ""), '',
                                           intcomma("%.2f" % total_profit_balance).replace("-", ""), ''])

                    table_data.append(['', '', '', '', '', '', '', ''])
                    table_data.append(['', 'ADD: OTHER INCOME', '', '', '', '', '', ''])
                    item_table = Table(table_data, colWidths=colWidths)
                    item_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                         ('LINEABOVE', (4, 0), (6, 0), 0.25, colors.black),
                         ('LINEABOVE', (4, 2), (6, 2), 0.25, colors.black),
                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                         ('LINEABOVE', (4, 4), (6, 4), 0.25, colors.black),

                         ]))
                    elements.append(item_table)
                    table_data = []
                else:
                    if mFilter == 'PL-REVENUE':
                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ]))
                        elements.append(item_table)
                        table_data = []
                        table_data.append(
                            ['', ' OTHER REVENUE  ', '', '',
                             intcomma("%.2f" % total_change).replace(
                                 "-", ""),
                             '', intcomma("%.2f" % total_balance).replace(
                                 "-", ""), ''])
                        table_data.append(
                            ['', '', '', '', '', '', '', ''])
                        table_data.append(
                            ['', ' TOTAL REVENUE ', '', '',
                             intcomma("%.2f" % total_revenue_change).replace(
                                 "-", ""),
                             '', intcomma("%.2f" % total_revenue_balance).replace(
                                 "-", ""), ''])
                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                             ('LINEABOVE', (4, 0), (6, 0), 0.25, colors.black),
                             ('LINEABOVE', (4, -1), (6, -1), 0.25, colors.black),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ]))
                        elements.append(item_table)
                        table_data = []
                    else:
                        # LESS: COST OF GOODS SOLD
                        if mFilter == 'PL-COGS':
                            table_data.append(
                                ['', '', '', '',
                                 intcomma("%.2f" % total_change).replace(
                                     "-", ""),
                                 '', intcomma("%.2f" % total_balance).replace(
                                     "-", ""), ''])
                            item_table = Table(table_data, colWidths=colWidths)
                            item_table.setStyle(TableStyle(
                                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                 ('LINEABOVE', (4, -1), (6, -1), 0.25, colors.black),
                                 ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                 ]))
                            elements.append(item_table)
                            table_data = []
                        else:
                            # LESS:  TOTAL EXPENDITURE
                            if mFilter == 'PL-EXPENSE':
                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                     ]))
                                elements.append(item_table)
                                table_data = []
                                table_data.append(
                                    ['', 'TOTAL EXPENDITURE', '', '',
                                     intcomma("%.2f" % total_change).replace(
                                         "-", ""),
                                     '', intcomma("%.2f" % total_balance).replace(
                                         "-", ""), ''])
                                table_data.append(['', '', '', '', '', '', '', ''])
                                if total_net_profit_change > 0 and total_net_profit_balance > 0:
                                    table_data.append(
                                        ['', ' NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ', '', '',
                                         Paragraph('(' + intcomma("%.2f" % total_net_profit_change).replace(
                                             "-", "") + ')', styles['RightAlignRed']), '',
                                         Paragraph('(' + intcomma("%.2f" % total_net_profit_balance).replace(
                                             "-", "") + ')', styles['RightAlignRed']), ''])
                                elif total_net_profit_change > 0:
                                    table_data.append(
                                        ['', ' NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ', '', '',
                                         Paragraph('(' + intcomma("%.2f" % total_net_profit_change).replace(
                                             "-", "") + ')', styles['RightAlignRed']), '',
                                         intcomma("%.2f" % total_net_profit_balance).replace(
                                             "-", ""), ''])
                                elif total_net_profit_balance > 0:
                                    table_data.append(
                                        ['', ' NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ', '', '',
                                         intcomma("%.2f" % total_net_profit_change).replace(
                                             "-", ""), '',
                                         Paragraph('(' + intcomma("%.2f" % total_net_profit_balance).replace(
                                             "-", "") + ')', styles['RightAlignRed']), ''])
                                else:
                                    table_data.append(
                                        ['', ' NET PROFIT/(LOSS) BEFORE TAXES/EXCH DIFF ', '', '',
                                         intcomma("%.2f" % total_net_profit_change).replace(
                                             "-", ""),
                                         '', intcomma("%.2f" % total_net_profit_balance).replace(
                                             "-", ""), ''])
                                table_data.append(['', '', '', '', '', '', '', ''])
                                item_table = Table(table_data, colWidths=colWidths)
                                item_table.setStyle(TableStyle(
                                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                     ('LINEABOVE', (4, 0), (6, 0), 0.25, colors.black),
                                     ('LINEABOVE', (4, 2), (6, 2), 0.25, colors.black),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                     ]))
                                elements.append(item_table)
                                table_data = []
                            else:
                                #  TOTAL EXCH GAIN/(LOSS)
                                if mFilter == 'PL-EXC':
                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                         ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                         ]))
                                    elements.append(item_table)
                                    table_data = []

                                    str_total_change, style_total_change = wrap_text(total_change, mFilter)
                                    str_total_balance, style_total_balance = wrap_text(total_balance, mFilter)
                                    str_total_net_profit_tax_change, style_total_net_profit_tax_change = wrap_text(
                                        total_net_profit_tax_change, mFilter)
                                    str_total_net_profit_tax_balance, style_total_net_profit_tax_balance = wrap_text(
                                        total_net_profit_tax_balance, mFilter)

                                    table_data.append(
                                        ['',
                                         ' TOTAL EXCH GAIN/(LOSS) ', '', '',
                                         Paragraph(str_total_change, styles[style_total_change]),
                                         '',
                                         Paragraph(str_total_balance, styles[style_total_balance]),
                                         ''])
                                    table_data.append(['', '', '', '', '', '', '', ''])
                                    table_data.append(
                                        ['',
                                         ' NET PROFIT/(LOSS) AFTER INCOME TAXES ', '', '',
                                         Paragraph(str_total_net_profit_tax_change,
                                                   styles[style_total_net_profit_tax_change]), '',
                                         Paragraph(str_total_net_profit_tax_balance,
                                                   styles[style_total_net_profit_tax_balance]), ''])
                                    table_data.append(['', '', '', '', '', '', '', ''])
                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                         ('LINEABOVE', (4, 0), (6, 0), 0.25, colors.black),
                                         ('LINEBELOW', (4, 2), (6, 2), 0.25, colors.black),
                                         ('LINEBELOW', (4, -1), (6, -1), 0.25, colors.black),
                                         ('BOTTOMPADDING', (0, 2), (-1, -1), 5),
                                         ('TOPPADDING', (0, -1), (-1, -1), -13),
                                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                         ('LINEBELOW', (4, 1), (6, 1), 0.25, colors.black),

                                         ]))
                                    elements.append(item_table)
                                    table_data = []
                                else:
                                    table_data.append(
                                        ['', Paragraph(str(' NET SALES '), styles['Normal']), '', '',
                                         intcomma("%.2f" % total_change).replace(
                                             "-", ""),
                                         '', intcomma("%.2f" % total_balance).replace(
                                            "-", ""), ''])
                                    item_table = Table(table_data, colWidths=colWidths)
                                    item_table.setStyle(TableStyle(
                                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                         ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                         ('LINEABOVE', (4, -1), (6, -1), 0.25, colors.black),
                                         ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                         ]))
                                    elements.append(item_table)
                                    table_data = []


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


def get_exchange_rate_header(issue_from, company_id):
    curr_month_exchange_rates = ExchangeRate.objects.filter(exchange_date=issue_from, company_id=company_id, is_hidden=0, flag='ACCOUNTING')
    array_data = str(issue_from).split('-')
    if int(array_data[1]) >= 1 and int(array_data[1]) <= 11:
        next_issue_from = datetime.date(int(array_data[0]), int(array_data[1]) + 1, 1)
    else:
        next_issue_from = datetime.date(int(array_data[0]) + 1, 1, 1)

    next_month_exchange_rates = ExchangeRate.objects.filter(exchange_date=next_issue_from, company_id=company_id, is_hidden=0, flag='ACCOUNTING')
    curr_usd_to_sgd = curr_month_exchange_rates.filter(from_currency__code='USD', to_currency__code='SGD').first()
    curr_yen_to_sgd = curr_month_exchange_rates.filter(from_currency__code='YEN', to_currency__code='SGD').first()
    next_usd_to_sgd = next_month_exchange_rates.filter(from_currency__code='USD', to_currency__code='SGD').first()
    next_yen_to_sgd = next_month_exchange_rates.filter(from_currency__code='YEN', to_currency__code='SGD').first()
    next_array_data = str(next_issue_from).split('-')

    if next_usd_to_sgd:
        frst_line = str(MONTHS_STR_DICT[next_array_data[1]]) + "'" + next_array_data[0] + ' - USD' + str(next_usd_to_sgd.rate)
    else:
        frst_line = str(MONTHS_STR_DICT[next_array_data[1]]) + "'" + next_array_data[0] + ' - USD'
    if next_yen_to_sgd:
        scnd_line = '                  YEN' + str(next_yen_to_sgd.rate)
    else:
        scnd_line = '                  YEN'
    if curr_usd_to_sgd:
        thrd_line = str(MONTHS_STR_DICT[array_data[1]]) + "'" + array_data[0] + ' - USD' + str(curr_usd_to_sgd.rate)
    else:
        thrd_line = str(MONTHS_STR_DICT[array_data[1]]) + "'" + array_data[0] + ' - USD'
    if curr_yen_to_sgd:
        frth_line = '                  YEN' + str(curr_yen_to_sgd.rate)
    else:
        frth_line = '                  YEN'

    return frst_line, scnd_line, thrd_line, frth_line
