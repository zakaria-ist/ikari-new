from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib import colors
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reports.helpers.aged_trial_report import get_due_period, get_ar_transactions, calculate_total_amount
from customers.models import Customer
from datetime import datetime
from accounting.models import Journal, AROptions
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import DOCUMENT_TYPES_IN_REPORT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT
from utilities.common import round_number, get_customer_filter_range


class Print_AR_customers:
    def __init__(self, buffer, pagesize):

        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    def print_report(self, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, paid_full):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=17, bottomMargin=42, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='background', fontName='Helvetica', fontSize=s.REPORT_FONT_SIZE,
                                  leading=12, backColor=colors.grey, textColor=colors.black, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='background_header', fontName='Helvetica', fontSize=14,
                                  leading=18, backColor=colors.grey, textColor=colors.transparent, alignment=TA_CENTER))
        company = Company.objects.get(pk=company_id)
        # Our container for 'Flowable' objects

        elements = []
        open_doc = 1 if int(doc_type) == 1 else 2
        journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
        if open_doc == 1:
            journal_item_list = Journal.objects.filter(company_id=company_id, is_hidden=0, batch__batch_type=dict(TRANSACTION_TYPES)['AR Invoice'],
                                                       batch__status=open_doc, is_fully_paid=0, document_date__lte=cutoff_date)

            if cus_no != '0':
                id_cus_range = cus_no.split(',')
                cust_id_from = int(id_cus_range[0])
                cust_id_to = int(id_cus_range[1])
                if cust_id_from > 0 and cust_id_to > 0:
                    customer_code_range = get_customer_filter_range(company_id,
                                                                    int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                                                    int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')

                    journal_item_list = journal_item_list.filter(customer_id__in=customer_code_range)
            adjustment_journal_list = []
            journal_amount_list = {}
        else:
            ar_collections = get_ar_transactions(is_detail_report=True, company_id=company_id, cus_no=cus_no, cutoff_date=cutoff_date, date_type=date_type,
                                                 paid_full=paid_full, doc_type_array=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])

            journal_item_list = ar_collections.journal_item_list
            adjustment_journal_list = ar_collections.adjustment_journal_list
            journal_amount_list = ar_collections.journal_amount_list
        journal_customer = journal_item_list.values('customer_id').order_by('customer_id').distinct()
        max_hunk = 10
        no = 1
        if journal_customer:
            for exp in journal_customer:
                journal_cust = Customer.objects.get(pk=exp['customer_id'])
                table_data = []
                table_data.append([company.name, Paragraph('STATEMENT', styles['background_header']), ''])

                item_table = Table(table_data, colWidths=[270, 270, 270])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                                ('FONT', (0, 0), (0, -1), s.REPORT_FONT_BOLD),
                                                ('TOPPADDING', (0, 0), (-1, -1), 0),
                                                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                                                ('ALIGN', (2, 0), (2, 0), 'CENTER'), ]))
                elements.append(item_table)

                table_data = []
                table_data.append([company.address, 'Customers No.:', '', journal_cust.code])
                table_data.append([company.country.name + ' ' + company.postal_code, 'Page:', '', ''])
                table_data.append(['', 'Date:', '', datetime.strptime(cutoff_date, '%Y-%m-%d').strftime("%d-%m-%Y"), ''])

                item_table = Table(table_data, colWidths=[600, 55, 50, 50])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -10), 0.25, colors.grey),
                                                ('BOX', (1, 0), (-1, -1), 0.25, colors.grey),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ]))
                elements.append(item_table)

                table_data = []
                table_data.append(['SOLD', '', '', 'REMIT TO ADDRESS :', '', ''])
                table_data.append(['TO:', journal_cust.name, '', journal_cust.address, '', ''])
                table_data.append(['', '', '', journal_cust.postal_code, '', ''])

                item_table = Table(table_data, colWidths=[70, 80, 400, 140, 60, 55])
                item_table.setStyle(TableStyle([('LEFTPADDING', (1, -1), (-1, -1), 0.25, colors.red),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('TOPPADDING', (0, 0), (0, -1), 9),
                                                ('BOTTOMPADDING', (0, 0), (0, -1), 5),
                                                ('BOX', (3, 1), (-1, -1), 0.25, colors.grey),
                                                ]))
                elements.append(item_table)

                table_data = []
                table_data.append([Paragraph('.', styles['background']),  Paragraph('.', styles['background']), Paragraph('.', styles['background']),
                                   Paragraph('.', styles['background']), Paragraph('.', styles['background']), Paragraph('.', styles['background'])])

                item_table = Table(table_data, colWidths=[135, 165, 80, 115, 80,  140])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -10), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)
                age = [31, 61, 91]
                age_period = {'current': 0, '1st': 31, '2nd': 61, '3rd': 91}
                ar_options = AROptions.objects.filter(company_id=company_id)
                if ar_options:
                    ar_options = ar_options.last()
                    age = [ar_options.aging_period_1, ar_options.aging_period_2, ar_options.aging_period_3]
                    age_period['current'] = 0
                    age_period['1st'] = age[0]
                    age_period['2nd'] = age[1]
                    age_period['3rd'] = age[2]

                list_journal = journal_item_list.filter(customer_id=exp['customer_id'])
                count_j = int(list_journal.count())
                sum_amount = 0
                total_current = total_1st = total_2nd = total_3rd = total_4th = 0
                sum_cus_current = sum_cus_1st = sum_cus_2nd = sum_cus_3rd = sum_cus_4th = sum_all_cus = 0
                if list_journal:
                    for journal in list_journal:
                        day_due = journal.due_date
                        day_age = datetime.strptime(age_from, '%Y-%m-%d').date()
                        key = str(journal.id)
                        if key in journal_amount_list:
                            total_amount = journal_amount_list[key]
                        else:
                            total_amount = journal.has_outstanding(cutoff_date, False)[1]
                        is_decimal = journal.currency.is_decimal if journal.currency else True

                        if is_decimal:
                            decimal_place = "%.2f"
                        else:
                            decimal_place = "%.0f"

                        if total_amount != 0:
                            adj_data = None
                            if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
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

                            elif journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                                if adjustment_journal_list and str(journal.id) in adjustment_journal_list.keys():
                                    adj_data = adjustment_journal_list[str(journal.id)]

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

                            sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                            sum_cus_current += total_current
                            sum_cus_1st += total_1st
                            sum_cus_2nd += total_2nd
                            sum_cus_3rd += total_3rd
                            sum_cus_4th += total_4th
                            sum_all_cus += sum_amount

                        document_type_dict = dict(DOCUMENT_TYPES_IN_REPORT)
                        if sum_amount != 0:
                            table_data = []
                            if journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice'] or journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                                table_data.append([journal.document_number, journal.document_date.strftime("%d-%m-%Y"),
                                                document_type_dict.get(journal.document_type) if journal.document_type else '',
                                                journal.reference,  journal.posting_date.strftime("%d-%m-%Y"),
                                                intcomma(decimal_place % round_number(sum_amount))])
                            elif adj_data:
                                table_data.append(['AD0000000000000' + str(adj_data['doc']) if adj_data['doc'] else '',
                                                adj_data['doc_date'].strftime("%d-%m-%Y") if adj_data['doc_date'] else ' / / ',
                                                'AD', journal.document_number,  journal.posting_date.strftime("%d-%m-%Y"),
                                                intcomma(decimal_place % round_number(sum_amount))])

                            elif journal.document_type == DOCUMENT_TYPE_DICT['Adjustment']:
                                table_data.append(['AD0000000000000' + journal.document_number, journal.document_date.strftime("%d-%m-%Y"),
                                                'AD', journal.reference,  journal.posting_date, intcomma(decimal_place % round_number(sum_amount))])

                            item_table = Table(table_data, colWidths=[180, 120, 80, 115, 80,  140])
                            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
                                                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                                            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                                                            ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                                            ]))
                            elements.append(item_table)
                            no += 1
                        sum_amount = total_current = total_1st = total_2nd = total_3rd = total_4th = 0

                # End of jounal_item_list_per_customer loop
                if count_j < max_hunk:
                    hunk = max_hunk - count_j
                    for line in range(1, hunk):
                        table_data = []
                        table_data.append(['', '', '', '', '', ''])
                        item_table = Table(table_data, colWidths=[180, 120, 80, 115, 80,  140])
                        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey)]))
                        elements.append(item_table)

                table_data = []
                table_data.append(['', '', '', '', '', '', '', '',  '', '', ''])
                item_table = Table(table_data, colWidths=[130, 5, 160, 5, 75, 5, 110, 5, 75, 5, 140])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('TOPPADDING', (0, 0), (-1, 0), 10),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                                ]))
                elements.append(item_table)
                is_decimal = journal_cust.currency.is_decimal if journal_cust.currency else True
                if is_decimal:
                    decimal_place = "%.2f"
                else:
                    decimal_place = "%.0f"
                if journal_cust.credit_limit:
                    credit_limit_now = journal_cust.credit_limit - sum_all_cus
                else:
                    journal_cust.credit_limit = 0
                    credit_limit_now = sum_all_cus
                table_data = []
                table_data.append(['IN - Invoice', '', 'DB - Debit Note', '', 'CR - Credit Note', 'IT - Interest Payable',
                                   '', '', '', 'Total :', '', intcomma(decimal_place % round_number(sum_all_cus))])

                table_data.append(['PY - Applied Receipt', '', 'ED - Earned Discount', '', 'AD - Adjustment', 'PI - Prepayment',
                                   '', '', '', 'Credit limit :', '', intcomma(decimal_place % round_number(journal_cust.credit_limit))])

                table_data.append(['UC - Unapplied Cash', '', 'RF - Refund', '', '', '', '', '', '',
                                   'credit available :', '', intcomma(decimal_place % round_number(credit_limit_now))])

                item_table = Table(table_data, colWidths=[115, 5, 105, 5, 90, 75, 5, 90, 5, 75, 5, 140])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -10), 0.25, colors.grey),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ]))
                elements.append(item_table)

                first_p = str(age_period['current'] + 1) + ' To ' + str(age_period['1st'])
                second_p = str(age_period['1st'] + 1) + ' To ' + str(age_period['2nd'])
                third_p = str(age_period['2nd'] + 1) + ' To ' + str(age_period['3rd'])
                over_p = 'Over ' + str(age_period['3rd'])
                table_data = []
                table_data.append(['Current O/Due', first_p + ' Days O/Due', second_p + ' Days O/Due', third_p + ' Days O/Due',  over_p + ' Days O/Due'])

                table_data.append([intcomma(decimal_place % round_number(sum_cus_current)), intcomma(decimal_place % round_number(sum_cus_1st)),
                                   intcomma(decimal_place % round_number(sum_cus_2nd)), intcomma(decimal_place % round_number(sum_cus_3rd)),
                                   intcomma(decimal_place % round_number(sum_cus_4th))])

                item_table = Table(table_data, colWidths=[144, 144, 144, 144, 140])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
                                                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                                ]))
                elements.append(item_table)
                table_data = []
                table_data.append(['', '', '', ''])

                item_table = Table(table_data, colWidths=[600, 50, 50, 70])
                item_table.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0),
                                                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                                ('TOPPADDING', (0, 0), (0, -1), 5),
                                                ('BOTTOMPADDING', (0, 0), (0, -1), 5),
                                                ]))
                elements.append(item_table)
                # else:  # if there's no order in the selected month
                if elements.__len__() == 0:
                    table_data = [['', '', '', '', '', '', '', '', '']]
                    table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75, 60, 85, 90, 130])
                    table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                                                    ]))
                    elements.append(table_body)
                elements.append(PageBreak())
            # End of jounal_item_list_customer loop
        else:
            table_data = []
            table_data.append(['', 'NO DATA FOUND', ''])
            item_table = Table(table_data, colWidths=[270, 270, 270])
            item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                            ('FONT', (0, 0), (0, -1), s.REPORT_FONT_BOLD),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                                            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                                            ('ALIGN', (2, 0), (2, 0), 'CENTER')
                                            ]))
            elements.append(item_table)
        doc.build(elements, canvasmaker=partial(NumberedPage, adjusted_height=-138, adjusted_width=175))
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def print_report_email(self, company_id, report_type, age_from, cutoff_date, cus_no, date_type, doc_type, curr_list, id_customers, paid_full):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=17, bottomMargin=42, pagesize=landscape(A4))
        is_sending = 0
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=s.REPORT_FONT_SIZE))
        styles.add(ParagraphStyle(name='background_header', fontName='Helvetica', fontSize=14, leading=18, backColor=colors.grey,
                                  textColor=colors.transparent, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='background', fontName='Helvetica', fontSize=s.REPORT_FONT_SIZE, leading=12,
                                  backColor=colors.grey, textColor=colors.transparent, alignment=TA_CENTER))

        company = Company.objects.get(pk=company_id)
        elements = []
        # Our container for 'Flowable' objects

        open_doc = 1 if int(doc_type) == 1 else 2

        if open_doc == 1:
            journal_item_list = Journal.objects.filter(company_id=company_id, is_hidden=0, batch__batch_type=dict(TRANSACTION_TYPES)['AR Invoice'],
                                                       batch__status=open_doc, is_fully_paid=0, customer_id=id_customers, document_date__lte=cutoff_date)

            if cus_no != '0':
                id_cus_range = cus_no.split(',')
                cust_id_from = int(id_cus_range[0])
                cust_id_to = int(id_cus_range[1])
                if cust_id_from > 0 and cust_id_to > 0:
                    customer_code_range = get_customer_filter_range(company_id,
                                                                    int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                                                    int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')

                    journal_item_list = journal_item_list.filter(customer_id__in=customer_code_range)
            adjustment_journal_list = []
            journal_amount_list = {}
        else:
            journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
            ar_collections = get_ar_transactions(is_detail_report=True, company_id=company_id, cus_no=cus_no, cutoff_date=cutoff_date, date_type=date_type,
                                                 paid_full=paid_full, doc_type_array=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
            journal_item_list = ar_collections.journal_item_list
            journal_item_list = journal_item_list.filter(customer_id=id_customers)
            adjustment_journal_list = ar_collections.adjustment_journal_list
            journal_amount_list = ar_collections.journal_amount_list

        max_hunk = 10
        no = 1

        # Our container for 'Flowable' objects
        journal_cust = Customer.objects.get(pk=id_customers)
        table_data = []
        table_data.append([company.name, Paragraph('STATEMENT', styles['background_header']), ''])

        item_table = Table(table_data, colWidths=[270, 270, 270])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                                        ('FONT', (0, 0), (0, -1), s.REPORT_FONT_BOLD),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                                        ('ALIGN', (2, 0), (2, 0), 'CENTER')
                                        ]))
        elements.append(item_table)

        table_data = []
        table_data.append([company.address, 'Customers No.:', '', journal_cust.code])
        table_data.append([company.country.name + ' ' + company.postal_code, 'Page:', '', ''])
        table_data.append(['', 'Date:', '', datetime.strptime(cutoff_date, '%Y-%m-%d').strftime("%d-%m-%Y"), ''])

        item_table = Table(table_data, colWidths=[600, 55, 50, 50])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -10), 0.25, colors.grey),
                                        ('BOX', (1, 0), (-1, -1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD)]))
        elements.append(item_table)

        table_data = []
        table_data.append(['SOLD', '', '', 'REMIT TO ADDRESS :', '', ''])
        table_data.append(['TO:', journal_cust.name, '', journal_cust.address, '', ''])
        table_data.append(['', '', '', journal_cust.postal_code, '', ''])
        table_data.append(['', '', '', '', '', ''])

        item_table = Table(table_data, colWidths=[70, 80, 400, 140, 60, 55])
        item_table.setStyle(TableStyle([('LEFTPADDING', (1, -1), (-1, -1), 0.25, colors.red),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (0, -1), 9),
                                        ('BOTTOMPADDING', (0, 0), (0, -1), 5),
                                        ('BOX', (3, 1), (-1, -1), 0.25, colors.grey),
                                        ]))
        elements.append(item_table)

        table_data = []
        table_data.append([Paragraph('DOCUMENT NUMBER', styles['background']),  Paragraph('DOCUMENT DATE', styles['background']),
                           Paragraph('Type', styles['background']),  Paragraph('REFERENCE/APPLIED NUMBER', styles['background']),
                           Paragraph('DUE DATE', styles['background']), Paragraph('AMOUNT', styles['background'])])

        item_table = Table(table_data, colWidths=[155, 125, 80, 215, 80, 110])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -10), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                                        ]))
        elements.append(item_table)

        count_j = int(journal_item_list.count())
        age = [31, 61, 91]
        age_period = {'current': 0, '1st': 31, '2nd': 61, '3rd': 91}
        ar_options = AROptions.objects.filter(company_id=company_id)
        if ar_options:
            ar_options = ar_options.last()
            age = [ar_options.aging_period_1, ar_options.aging_period_2, ar_options.aging_period_3]
            age_period['current'] = 0
            age_period['1st'] = age[0]
            age_period['2nd'] = age[1]
            age_period['3rd'] = age[2]
        sum_amount = 0
        total_current = total_1st = total_2nd = total_3rd = total_4th = 0
        sum_cus_current = sum_cus_1st = sum_cus_2nd = sum_cus_3rd = sum_cus_4th = sum_all_cus = 0
        if journal_item_list:
            is_sending = 1
            for journal in journal_item_list:
                day_due = journal.due_date
                day_age = datetime.strptime(age_from, '%Y-%m-%d').date()
                key = str(journal.id)
                if key in journal_amount_list:
                    total_amount = journal_amount_list[key]
                else:
                    total_amount = journal.has_outstanding(cutoff_date, False)[1]

                is_decimal = journal.currency.is_decimal if journal.currency else True
                if is_decimal:
                    decimal_place = "%.2f"
                else:
                    decimal_place = "%.0f"

                if total_amount != 0:
                    adj_data = None
                    if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
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

                    elif journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                        if str(journal.id) in adjustment_journal_list.keys():
                            adj_data = adjustment_journal_list[str(journal.id)]

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

                    sum_amount = total_current + total_1st + total_2nd + total_3rd + total_4th
                    sum_cus_current += total_current
                    sum_cus_1st += total_1st
                    sum_cus_2nd += total_2nd
                    sum_cus_3rd += total_3rd
                    sum_cus_4th += total_4th
                    sum_all_cus += sum_amount

                document_type_dict = dict(DOCUMENT_TYPES_IN_REPORT)
                table_data = []
                if journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice'] or journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                    table_data.append([journal.document_number, journal.document_date.strftime("%d-%m-%Y"),
                                       document_type_dict.get(journal.document_type) if journal.document_type else '',
                                       journal.reference,  journal.posting_date.strftime("%d-%m-%Y"),
                                       intcomma(decimal_place % round_number(sum_amount))])
                elif adj_data:
                    table_data.append(['AD0000000000000' + str(adj_data['doc']) if adj_data['doc'] else '',
                                       adj_data['doc_date'].strftime("%d-%m-%Y") if adj_data['doc_date'] else ' / / ',
                                       'AD', journal.document_number,  journal.posting_date.strftime("%d-%m-%Y"),
                                       intcomma(decimal_place % round_number(sum_amount))])

                elif journal.document_type == DOCUMENT_TYPE_DICT['Adjustment']:
                    table_data.append(['AD0000000000000' + journal.document_number, journal.document_date.strftime("%d-%m-%Y"),
                                       'AD', journal.reference,  journal.posting_date, intcomma(decimal_place % round_number(sum_amount))])

                item_table = Table(table_data, colWidths=[180, 120, 80, 115, 80,  140])
                item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
                                                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                                                ('ALIGN', (5, 0), (-1, -1), 'RIGHT')
                                                ]))
                elements.append(item_table)
                no += 1
                sum_amount = total_current = total_1st = total_2nd = total_3rd = total_4th = 0
            if count_j < max_hunk:
                hunk = max_hunk - count_j
                for line in range(1, hunk):
                    table_data = []
                    table_data.append(['', '', '', '', '', ''])
                    item_table = Table(table_data, colWidths=[180, 120, 80, 115, 80,  140])
                    item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey)]))
                    elements.append(item_table)

        table_data = []
        table_data.append(['', '', '', '', '', '', '', '',  '', '', ''])
        item_table = Table(table_data, colWidths=[130, 5, 160, 5, 75, 5, 110, 5, 75, 5, 140])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, 0), 10),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                        ]))
        elements.append(item_table)
        is_decimal = journal_cust.currency.is_decimal if journal_cust.currency else True
        if is_decimal:
            decimal_place = "%.2f"
        else:
            decimal_place = "%.0f"
        if journal_cust.credit_limit:
            credit_limit_now = journal_cust.credit_limit - sum_all_cus
        else:
            journal_cust.credit_limit = 0
            credit_limit_now = sum_all_cus
        table_data = []
        table_data.append(['IN - Invoice', '', 'DB - Debit Note', '', 'CR - Credit Note', 'IT - Interest Payable',
                           '', '', '', 'Total :', '', intcomma(decimal_place % round_number(sum_all_cus))])

        table_data.append(['PY - Applied Receipt', '', 'ED - Earned Discount', '', 'AD - Adjustment', 'PI - Prepayment',
                           '', '', '', 'Credit limit :', '', intcomma(decimal_place % round_number(journal_cust.credit_limit))])

        table_data.append(['UC - Unapplied Cash', '', 'RF - Refund', '', '', '', '', '', '',
                           'credit available :', '', intcomma(decimal_place % round_number(credit_limit_now))])

        item_table = Table(table_data, colWidths=[115, 5, 105, 5, 90, 75, 5, 90, 5, 125, 5, 140])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -10), 0.25, colors.grey),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ]))
        elements.append(item_table)

        first_p = str(age_period['current'] + 1) + ' To ' + str(age_period['1st'])
        second_p = str(age_period['1st'] + 1) + ' To ' + str(age_period['2nd'])
        third_p = str(age_period['2nd'] + 1) + ' To ' + str(age_period['3rd'])
        over_p = 'Over ' + str(age_period['3rd'])
        table_data = []
        table_data.append(['Current O/Due', first_p + ' Days O/Due', second_p + ' Days O/Due', third_p + ' Days O/Due',  over_p + ' Days O/Due'])

        table_data.append([intcomma(decimal_place % round_number(sum_cus_current)), intcomma(decimal_place % round_number(sum_cus_1st)),
                           intcomma(decimal_place % round_number(sum_cus_2nd)), intcomma(decimal_place % round_number(sum_cus_3rd)),
                           intcomma(decimal_place % round_number(sum_cus_4th))])

        item_table = Table(table_data, colWidths=[144, 144, 144, 144, 140])
        item_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                                        ]))
        elements.append(item_table)
        table_data = []
        table_data.append(['', '', '', ''])

        item_table = Table(table_data, colWidths=[600, 50, 50, 70])
        item_table.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (0, -1), 5),
                                        ('BOTTOMPADDING', (0, 0), (0, -1), 5),
                                        ]))
        elements.append(item_table)
        # else:  # if there's no order in the selected month
        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=[60, 90, 110, 105, 75, 60, 85, 90, 130])
            table_body.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                                            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                                            ]))
            elements.append(table_body)
        # End of jounal_item_list_customer loop
        doc.build(elements, canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))
        pdf = buffer.getvalue()
        return pdf, is_sending
