import datetime
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.dateparse import parse_date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from currencies.models import ExchangeRate
from customers.models import Customer
from django.conf import settings as s
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial
from utilities.common import round_number, get_decimal_place


class Print_SR7405:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, delivery_from, delivery_to, customer_code, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # First row
        header_data = []
        row1_info1 = "SR7405 Sales and Purchase System"
        row1_info2 = "Forecast Outstanding S/O Balance Report As At " + datetime.datetime.now().strftime('%B %Y')
        header_data.append([row1_info1, row1_info2])

        # Second row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Customer"
        header_data.append([row2_info1, row2_info2])
        # Third row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # Empty row
        # header_data.append(['', ''])
        # row4
        row4_info1 = "Transaction Code : [SALE ORDER]"
        row4_info2 = "Wanted Date : [" + parse_date(delivery_from).strftime('%d/%m/%Y') + "] [" + \
                     parse_date(delivery_to).strftime('%d/%m/%Y') + "]"
        header_data.append([row4_info1, row4_info2])
        if customer_code != '' and customer_code is not None and customer_code != '0':
            header_data.append(["Customer Code : [" + customer_code + "]", ""])
        else:
            header_data.append(["Customer Code : [] - []", ""])
        # Empty row
        # header_data.append(['', ''])

        header_table = Table(header_data, colWidths=[265, 268])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
             ('BOTTOMPADDING', (0, 2), (-1, 2), 10),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 2, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['', '', '', '', '<-----------FORECAST---------->', '']
        table_header1 = ['Customer Code & Name', '', 'Curr', 'Outstanding Qty', 'Original Amount', 'Local Amount']
        table_data.append(table_header)
        table_data.append(table_header1)

        item_header_table = Table(table_data, colWidths=[80, 190, 50, 50, 80, 75])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 2), (-1, 2), 0.25, colors.black),
             ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
             ('SPAN', (0, 1), (1, 1)),
             ('SPAN', (4, 0), (5, 0)),
             ('ALIGN', (4, 0), (5, 0), 'CENTER'),
             ('ALIGN', (2, -1), (2, -1), 'LEFT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, customer_code=None):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=46, topMargin=180, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=10, leading=12))

        # Draw Content of PDF
        cust_item_all = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
        cust_item = cust_item_all
        if customer_code != '' and customer_code is not None and customer_code != '0':
            if str(customer_code).__contains__('*'):
                customer_code = str(customer_code).replace('*', '')
            if str(customer_code).__contains__(','):
                arr_code = str(customer_code).split(',')
                if arr_code.__len__() > 0:
                    cust_item = cust_item.filter(code__contains=str(arr_code[0]).strip())
                    for my_code in arr_code:
                        cust_item = cust_item | cust_item_all.filter(code__contains=my_code.strip())
            else:
                cust_item = cust_item.filter(code__contains=customer_code.strip())
        # Get list of customers code
        cust_list = cust_item.values_list('code', flat=True).distinct()

        # Modify to follow new database structure
        err = False
        if cust_list.count() > 0:
            cust_list = list(cust_list)
            cust_list.sort()
            total_outstanding = 0
            total_localamt = 0
            company = Company.objects.get(pk=company_id)
            company_curr_code = company.currency.code
            company_curr_name = company.currency.name

            decimal_place_f = get_decimal_place(company.currency)

            for cust in cust_list:
                # list orderitems purchased from the supplier
                orderitems_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                           order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                           order__customer__code__exact=cust,
                                                           order__status__gte=dict(ORDER_STATUS)['Sent'])\
                    .select_related('order', 'item', 'order__currency')
                if delivery_from and orderitems_list:
                    orderitems_list = orderitems_list.filter(wanted_date__gte=delivery_from)
                if delivery_to and orderitems_list:
                    orderitems_list = orderitems_list.filter(wanted_date__lte=delivery_to)
                len1 = orderitems_list.count()
                if len1 > 0:
                    # list of currency from orders
                    currency_codes_list = orderitems_list.values_list('order__currency__code', flat=True).distinct()
                    len2 = currency_codes_list.count()
                    if len2 > 0:
                        for curr in currency_codes_list:
                            # group/filter orderitem by supplier and currency
                            orderitem_currency = orderitems_list.filter(order__currency__code__exact=curr)
                            if orderitem_currency:
                                cust_name = orderitem_currency.first().order.customer.name
                                try:
                                    currency = Currency.objects.get(code=curr)
                                    decimal_place = get_decimal_place(currency)
                                except:
                                    decimal_place = "%.2f"
                                out_qty = 0
                                org_amt = 0
                                local_amt = 0
                                # calculate outstanding qty of orders by from this customer and currency
                                for oic in orderitem_currency:
                                    if (oic.quantity - oic.delivery_quantity) > 0:
                                        amt = oic.quantity - oic.delivery_quantity
                                        out_qty += amt
                                        org_amt += oic.price
                                        # calc orginal amount. get ex_rate at the wanted date
                                        if curr == company_curr_code:
                                            rate = 1
                                        else:
                                            try:
                                                rate = ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                                                   from_currency__code=curr,
                                                                                   to_currency__code=company_curr_code,
                                                                                   exchange_date__month=oic.wanted_date.month,
                                                                                   exchange_date__year=oic.wanted_date.year,
                                                                                   flag='ACCOUNTING')\
                                                    .last().rate
                                            except:
                                                rate = 0
                                                err = True
                                        local_amt += round_number(rate * oic.price * amt)
                                total_outstanding += out_qty
                                total_localamt += local_amt
                                if out_qty > 0:
                                    table_data.append([cust, Paragraph(cust_name, styles['CustomStyle']), curr,
                                                       intcomma("%.2f" % out_qty),
                                                       intcomma(decimal_place % round_number(org_amt)),
                                                       intcomma(decimal_place_f % round_number(local_amt))])
            if total_outstanding != 0:
                table_data.append(['', '', 'Grand Total :',
                                   intcomma("%.2f" % total_outstanding), '',
                                   intcomma(decimal_place_f % round_number(total_localamt))])
        if table_data.__len__() == 0:  # if there's no data to print
            table_data.append(['', '', '', '', '', ''])
            data_sum = ['', '', 'Grand Total :', '', '', '']
            table_data.append(data_sum)

        # Create the table
        item_table = Table(table_data, colWidths=[62, 190, 35, 83, 78, 76])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -2), s.REPORT_FONT),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('SPAN', (0, -1), (1, -1)),
             ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
             ('FONT', (0, -1), (0, -1), s.REPORT_FONT_BOLD),
             ('LINEABOVE', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD),
             ]))
        elements.append(item_table)
        if err:
            # print error if cannot get any of exchange rate
            table_data = [['Error!!! Cannot get at least one exchange rate', '', '', '', '', '']]
            item_table = Table(table_data, colWidths=[62, 190, 35, 60, 101, 76])
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -2), s.REPORT_FONT),
                 ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                 ('SPAN', (0, -1), (1, -1)),
                 ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
                 ('FONT', (0, -1), (0, -1), s.REPORT_FONT_BOLD),
                 ('LINEABOVE', (0, -1), (-1, -1), 0.25, colors.black),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONT', (0, -1), (-1, -1), s.REPORT_FONT_BOLD),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ]))
            elements.append(item_table)
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from, delivery_to=delivery_to,
                                      customer_code=customer_code, company_id=company_id),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from, delivery_to=delivery_to,
                                       customer_code=customer_code, company_id=company_id),
                  canvasmaker=NumberedPage)
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
