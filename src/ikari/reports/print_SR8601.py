import calendar
import datetime
import os
from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from companies.models import Company
from customers.models import Customer
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
from reports.print_SR8600 import getExchangeRate, getReferDoc, setSupplierAndPurchasePrice
from utilities.common import get_company_name_and_current_period, round_number, get_decimal_place
from utilities.constants import ORDER_STATUS, ORDER_TYPE

colWidths = [110, 230, 80, 130]
rowHeights = 13


class Print_SR8601:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, first_day, last_day, company_name, current_period):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        canvas.saveState()

        header_data = []
        row1_info1 = "SR8601 Sales and Purchase System"
        row1_info2 = "MONTHLY GROSS PROFIT SUMMARY REPORT AS AT " + first_day.strftime('%B %Y').upper()
        header_data.append([row1_info1, row1_info2])

        row2_info1 = company_name
        row2_info2 = "GROUP BY CUSTOMER"
        header_data.append([row2_info1, row2_info2])
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        row4_info1 = "Issued Date : [" + first_day.strftime('%d/%m/%Y') + "] To [" + \
                     last_day.strftime('%d/%m/%Y') + "]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[265, 280], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 15, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['CUSTOMER CODE & NAME', '', 'TOTAL PROFIT', 'TOTAL SALES TURNOVER']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, 0), 9),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('SPAN', (0, 0), (1, 0)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - h1 - 5)
        canvas.restoreState()

    def print_report(self, company_id, from_month, from_year, to_month, to_year):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=42,
                                leftMargin=42,
                                topMargin=105,
                                bottomMargin=42,
                                pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))

        first_day = datetime.date(int(from_year), int(from_month), 1)
        last_day = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])
        company_currency = ''

        company = Company.objects.filter(id=company_id).last()
        decimal_place_f = get_decimal_place(company.currency)

        if company.currency:
            company_currency = company.currency.id

        order_item_list = OrderItem.objects \
            .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .filter(order__document_date__gte=first_day, order__document_date__lte=last_day) \
            .exclude(order__customer__isnull=True, item__isnull=True, order__status=dict(ORDER_STATUS)['Draft'])\
            .select_related('order', 'item', 'supplier', 'order__customer')

        # setSupplierAndPurchasePrice(order_item_list)

        order_item_list = order_item_list.order_by('order__customer__code', 'supplier__code', 'item__code',
                                                   'last_purchase_price', 'price')

        elements = []
        table_data = []
        item_data = dict()
        customer_code = ''
        price_buy = price_sell = exchange_rate_buy = dummy_exchange_rate_buy = 0
        quantity = 0
        first_row = True

        if order_item_list.exists():
            for order_item in order_item_list:
                refer_doc = getReferDoc(order_item, first_day, last_day)

                if refer_doc:
                    dummy_exchange_rate_buy = getExchangeRate(company_currency, order_item, refer_doc, first_day)

                if first_row:
                    customer_code = order_item.order.customer.code
                    item_code = order_item.item.code
                    price_buy = order_item.last_purchase_price
                    price_sell = order_item.price
                    exchange_rate_buy = dummy_exchange_rate_buy

                if order_item.quantity is not None:
                    if order_item.order.customer.code not in item_data:
                        item_data[order_item.order.customer.code] = dict()

                    if order_item.item.code not in item_data[order_item.order.customer.code]:
                        item_data[order_item.order.customer.code][order_item.item.code] = []

                    if (customer_code == order_item.order.customer.code) & (item_code == order_item.item.code) & \
                            (price_buy == order_item.last_purchase_price) & (price_sell == order_item.price):
                        if order_item.quantity is not None:
                            quantity += order_item.quantity
                            exchange_rate_sell = order_item.order.exchange_rate if order_item.order.exchange_rate else 1
                    else:
                        if quantity > 0:
                            item_data[customer_code][item_code].append({
                                'buy_exchange_rate': exchange_rate_buy,
                                'buy_price': round_number(price_buy, 5),
                                'buy_local_price': round_number(price_buy * exchange_rate_buy, 5),  # local price purchase
                                'sell_exchange_rate': exchange_rate_sell,
                                'sell_price': price_sell,
                                'sell_local_price': round_number(price_sell * exchange_rate_sell, 5),  # local price sell
                                'profit': round_number(round_number(price_sell * exchange_rate_sell, 5) - (
                                    round_number(price_buy * exchange_rate_buy, 5)), 5),  # profit
                                'quantity': quantity
                            })

                        if order_item.quantity is not None:
                            quantity = order_item.quantity
                        else:
                            quantity = 0

                        price_buy = order_item.last_purchase_price
                        price_sell = order_item.price
                        exchange_rate_buy = dummy_exchange_rate_buy
                        customer_code = order_item.order.customer.code
                        item_code = order_item.item.code
                        exchange_rate_sell = order_item.order.exchange_rate if order_item.order.exchange_rate else 1

                first_row = False

            item_data[customer_code][item_code].append({
                'buy_exchange_rate': exchange_rate_buy,
                'buy_price': round_number(price_buy, 5),
                'buy_local_price': round_number(price_buy * exchange_rate_buy, 5),  # local price purchase
                'sell_exchange_rate': exchange_rate_sell,
                'sell_price': price_sell,
                'sell_local_price': round_number(price_sell * exchange_rate_sell, 5),  # local price sell
                'profit': round_number(round_number(price_sell * exchange_rate_sell, 5) - (round_number(price_buy * exchange_rate_buy, 5)), 5),  # profit
                'quantity': quantity
            })

            total_all_profit = total_all_turnover = 0

            customer_list = Customer.objects.filter(is_hidden=0, company_id=company_id, customer_type=1) \
                .order_by('code', 'name') \
                .exclude(name__isnull=True)

            for customer in customer_list:
                total_quantity = 0
                total_profit = 0
                sales_turnover = 0
                sales_local_turnover = 0

                if customer.code in item_data:
                    for item_row in item_data[customer.code]:
                        for row in item_data[customer.code][item_row]:
                            total_quantity += round_number(row['quantity'], 2)
                            total_profit += round_number(row['quantity'] * row['profit'], 2)
                            sales_turnover += round_number(row['quantity'] * row['sell_price'], 2)
                            sales_local_turnover += round_number(row['quantity'] * row['sell_local_price'], 2)

                    customer_profit = total_profit
                    customer_turnover = sales_local_turnover

                    table_data.append([customer.code, customer.name,
                                       Paragraph(intcomma(decimal_place_f % round_number(customer_profit)), styles["RightAlign"]),
                                       Paragraph(intcomma(decimal_place_f % round_number(customer_turnover)), styles["RightAlign"])])

                    total_all_profit += customer_profit
                    total_all_turnover += customer_turnover
                else:
                    table_data.append([customer.code, customer.name, Paragraph(intcomma("%.2f" % 0), styles["RightAlign"]),
                                       Paragraph(intcomma("%.2f" % 0), styles["RightAlign"])])

            table_data.append(['', '', Paragraph(intcomma(decimal_place_f % round_number(total_all_profit)), styles["RightAlignBold"]),
                               Paragraph(intcomma(decimal_place_f % round_number(total_all_turnover)), styles["RightAlignBold"])])

            if table_data.__len__() > 0:
                item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                     ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('LINEABOVE', (0, -1), (-1, -1), 0.25, colors.black),
                     ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)

        if table_data.__len__() == 0:
            table_data.append(['', '', '', ''])
            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ]))
            elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)
        # current_period = datetime.datetime.strptime(str(year) + '-' + str(month), '%Y-%m')
        # current_period = datetime.datetime.strptime(current_period, '%Y-%m')
        # current_period = current_period.strftime('%B %Y')
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, first_day=first_day, last_day=last_day,
                                      company_name=company_name,
                                      current_period=current_period),
                  onLaterPages=partial(self._header_footer, first_day=first_day, last_day=last_day,
                                       company_name=company_name,
                                       current_period=current_period),
                  canvasmaker=partial(NumberedPage, adjusted_height=95))

        pdf = buffer.getvalue()
        buffer.close()

        return pdf
