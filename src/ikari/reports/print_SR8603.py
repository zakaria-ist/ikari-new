import calendar
import datetime
import os
from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from companies.models import Company
from orders.models import OrderItem
from reports.numbered_page import NumberedPage
from reports.print_SR8600 import getExchangeRate, getReferDoc, setSupplierAndPurchasePrice
from utilities.common import round_number, get_decimal_place
from utilities.constants import ORDER_TYPE, ORDER_STATUS


class Print_SR8603:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, first_day, last_day):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "SR8603 Sales and Purchase System"
        row1_info2 = "MONTHLY GROSS PROFIT DETAIL REPORT AS AT " + first_day.strftime('%B %Y').upper()
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Group By Customer No., Supplier & Part No."
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        row4_info1 = "Issued Date : [" + first_day.strftime('%d/%m/%Y') + "] To [" + \
                     last_day.strftime('%d/%m/%Y') + "]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[400, 410])
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
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_header = ['', '', '', '', '', '', '', '<---------------------BUYING PRICE----------------->', '', '', '',
                        '<----------------SELLING PRICE-------------------->', '', '', '', '', '', '', '', '', 'SALES']
        table_data.append(table_header)
        # 2ND ROW
        table_header = ['CUSTOMER', 'SUPPLIER', 'PART', '', 'PART NO.', '', 'MODEL', 'CURR', 'EXCH.', 'UNIT', 'LOCAL PRICE',
                        'CURR', 'EXCH.', 'UNIT', 'LOCAL PRICE', 'PROFIT', 'QTY/M', 'TOTAL', 'SALES', 'PROFIT', 'VOLUME']
        table_data.append(table_header)
        # 3RD ROW
        table_header = ['', '', 'DESCRIPTION', '', '', '', '', '', 'RATE', 'PRICE', company.currency.code, '', 'RATE',
                        'PRICE', company.currency.code, '', '', 'PROFIT', 'TURN OVER', '(%)', '(%)']
        table_data.append(table_header)

        item_header_table = Table(table_data, colWidths=[45, 40, 65, 5, 60, 5, 30, 25, 30, 45, 50, 25, 30, 45, 50, 35, 50, 40, 45, 45, 35])
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('SIZE', (0, 0), (-1, -1), 7),
             ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (1, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('ALIGN', (10, -1), (10, -1), 'CENTER'),
             ('ALIGN', (12, -1), (12, -1), 'CENTER'),
             ('ALIGN', (20, 0), (20, -1), 'CENTER'),
             ('ALIGN', (19, 0), (19, -1), 'CENTER'),
             ('ALIGN', (18, 0), (18, -1), 'CENTER'),
             ('SPAN', (7, 0), (10, 0)),
             ('SPAN', (11, 0), (14, 0)),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, from_month, from_year, to_month, to_year):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22, topMargin=170, bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=7, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT_BOLD, fontSize=7, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=7, alignment=TA_RIGHT))

        # Our container for 'Flowable' objects
        elements = []

        # Draw Content of PDF
        first_day = datetime.date(int(from_year), int(from_month), 1)
        last_day = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])
        order_item_list = OrderItem.objects \
            .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .filter(order__document_date__gte=first_day, order__document_date__lte=last_day) \
            .exclude(order__customer__isnull=True, item__isnull=True, order__status=dict(ORDER_STATUS)['Draft'])\
            .select_related('order', 'item', 'supplier', 'order__customer')

        company_currency = ''
        company = Company.objects.filter(id=company_id).last()
        if company.currency:
            company_currency = company.currency.id
        decimal_place_f = get_decimal_place(company.currency)

        line = 0
        quantity = 0
        total_all_turnover = total_all_profit = total_all_quantity = total_all_profit_tax = total_all_turnover_local = 0
        code = part_no = ''
        price_buy = price_sell = exchange_rate_buy = dummy_exchange_rate_buy = 0
        curr_buy = ''
        if order_item_list.exists():
            oi_list = []
            # setSupplierAndPurchasePrice(order_item_list)
            order_item_list = order_item_list.order_by('order__customer__code', 'supplier__code', 'item__code',
                                                       'last_purchase_price', 'price')

            for i, cus in enumerate(order_item_list):
                refer_doc = getReferDoc(cus, first_day, last_day)
                if refer_doc:
                    curr_buy = refer_doc.order.currency.code
                    dummy_exchange_rate_buy = getExchangeRate(company_currency, cus, refer_doc, first_day)

                if i == 0:
                    code = cus.order.customer.code if cus.order.customer else ''
                    part_no = cus.item.code
                    price_buy = cus.last_purchase_price
                    price_sell = cus.price
                    exchange_rate_buy = dummy_exchange_rate_buy

                if (code == cus.order.customer.code) & (part_no == cus.item.code) \
                        & (price_buy == cus.last_purchase_price) & (price_sell == cus.price):
                    if cus.quantity is not None:
                        quantity += cus.quantity
                else:
                    if quantity > 0:
                        k = i - 1
                        line += 1
                        total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local = self.calculate_report_row_element(
                            company_currency, company_id, k, order_item_list, quantity, total_all_profit,
                            total_all_quantity, total_all_turnover, total_all_turnover_local, price_buy, curr_buy,
                            exchange_rate_buy, oi_list, decimal_place_f)

                        if (total_all_profit > 0) & (total_all_turnover > 0):
                            total_all_profit_tax += (total_all_profit / total_all_turnover) * 100

                    if cus.quantity is not None:
                        quantity = cus.quantity
                    else:
                        quantity = 0

                    code = cus.order.customer.code if cus.order.customer else ''
                    part_no = cus.item.code
                    price_buy = cus.last_purchase_price
                    price_sell = cus.price
                    exchange_rate_buy = dummy_exchange_rate_buy

                if i == order_item_list.__len__() - 1:
                    k = i
                    if quantity > 0:
                        total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local = self.calculate_report_row_element(
                            company_currency, company_id, k, order_item_list, quantity, total_all_profit,
                            total_all_quantity, total_all_turnover, total_all_turnover_local, price_buy, curr_buy,
                            exchange_rate_buy, oi_list, decimal_place_f)
                        total_all_profit_tax = (
                            total_all_profit * 100) / total_all_turnover_local if total_all_turnover_local else 0

                    report_row = self.generate_report_row(oi_list)
                    elements.append(report_row)

                    item_table = self.print_GrandTotal(styles, total_all_profit, total_all_profit_tax,
                                                       total_all_quantity, total_all_turnover_local, decimal_place_f)
                    elements.append(item_table)

        if elements.__len__() == 0:
            report_row = self.generate_report_row()
            elements.append(report_row)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, first_day=first_day,
                                      last_day=last_day),
                  onLaterPages=partial(self._header_footer, company_id=company_id, first_day=first_day,
                                       last_day=last_day),
                  canvasmaker=partial(NumberedPage, adjusted_height=-155, adjusted_width=255))

        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def generate_report_row(self, oi_list=None):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=7, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=7, alignment=TA_RIGHT))
        table_data = [['']]
        report_row = Table(table_data, colWidths=[810])
        report_row.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (0, -1), (-1, -1), - 22),
             ]))

        if oi_list:
            table_data = []
            customer = ''
            sales_turn_over_sum = 0
            for i, oi in enumerate(oi_list):
                customer, sales_turn_over_sum, sales_volume = self.calculate_sales_volume(i, customer, sales_turn_over_sum, oi_list)
                table_data.append([Paragraph(customer, styles["LeftAlign"]), Paragraph(oi['supplier'], styles["LeftAlign"]),
                                   Paragraph(oi['item_code'], styles["LeftAlign"]), '', Paragraph(oi['item_name'], styles["LeftAlign"]), '',
                                   Paragraph(oi['item_cat'], styles["LeftAlign"]), Paragraph(oi['curr_buy'], styles["RightAlign"]),
                                   Paragraph(oi['exchange_rate_buy'], styles["RightAlign"]), Paragraph(oi['purchase_price'], styles["RightAlign"]),
                                   Paragraph(oi['local_price_buy'], styles["RightAlign"]), Paragraph(oi['curr_sell'], styles["RightAlign"]),
                                   Paragraph(oi['exchange_rate_sell'], styles["RightAlign"]), Paragraph(oi['price_sell'], styles["RightAlign"]),
                                   Paragraph(oi['local_price_sell'], styles["RightAlign"]), Paragraph(oi['profit'], styles["RightAlign"]),
                                   Paragraph(oi['quantity'], styles["RightAlign"]), Paragraph(oi['total_profit'], styles["RightAlign"]),
                                   Paragraph(oi['total_turnover_local'], styles["RightAlign"]), Paragraph(oi['profit_percentage'], styles["RightAlign"]),
                                   Paragraph(intcomma("%.4f" % round_number(sales_volume, 4)) if sales_volume else '0.0000', styles["RightAlign"])])

            report_row = Table(table_data, colWidths=[37, 37, 74, 2, 77, 2, 36, 20, 30, 45, 50, 25, 30, 45, 45, 35, 40, 40, 45, 45, 40], rowHeights=12)
            report_row.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                 ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ]))

        return report_row

    def calculate_report_row_element(self, company_currency, company_id, k, order_item_list, quantity, total_all_profit,
                                     total_all_quantity, total_all_turnover, total_all_turnover_local, purchase_price,
                                     curr_buy, exchange_rate_buy, oi_list, decimal_place_f):
        exchange_rate_sell = order_item_list[k].order.exchange_rate if order_item_list[k].order.exchange_rate else 1
        local_price_sell = round_number(round_number(order_item_list[k].price, 4) * exchange_rate_sell, 4)
        local_price_buy = round_number(round_number(purchase_price, 4) * exchange_rate_buy, 4)
        profit = round_number(local_price_sell, 4) - round_number(local_price_buy, 4)
        total_profit = quantity * profit
        total_turnover = round_number(order_item_list[k].price, 4) * quantity
        total_turnover_local = round_number(local_price_sell, 4) * quantity
        profit_percentage = profit / (round_number(local_price_sell, 4) / 100) if local_price_sell else 0

        total_all_profit += total_profit
        total_all_quantity += quantity
        total_all_turnover += total_turnover
        total_all_turnover_local += total_turnover_local

        obj = {}
        obj['customer'] = order_item_list[k].order.customer.code if order_item_list[k].order.customer else ''
        obj['supplier'] = order_item_list[k].supplier.code if order_item_list[k].supplier else ''
        obj['item_code'] = order_item_list[k].item.name[:16]
        obj['item_name'] = order_item_list[k].item.code[:17]
        obj['item_cat'] = order_item_list[k].item.category.code if order_item_list[k].item.category else ''
        obj['curr_buy'] = curr_buy
        obj['exchange_rate_buy'] = intcomma("%.4f" % round_number(exchange_rate_buy, 4)) if exchange_rate_buy else '0.0000'
        obj['purchase_price'] = intcomma("%.5f" % round_number(purchase_price, 5)) if purchase_price else '0.00000'
        obj['local_price_buy'] = intcomma("%.5f" % round_number(local_price_buy, 5)) if local_price_buy else '0.00000'
        obj['curr_sell'] = order_item_list[k].order.currency.code
        obj['exchange_rate_sell'] = intcomma("%.4f" % round_number(exchange_rate_sell, 4)) if exchange_rate_sell else '0.0000'
        obj['price_sell'] = intcomma("%.5f" % round_number(order_item_list[k].price, 5)) if order_item_list[k].price else '0.00000'
        obj['local_price_sell'] = intcomma("%.5f" % round_number(local_price_sell, 5)) if local_price_sell else '0.00000'
        obj['profit'] = intcomma("%.5f" % round_number(profit, 5)) if profit else '0.00000'
        obj['quantity'] = intcomma("%.2f" % quantity) if quantity else '0.00'
        obj['total_profit'] = intcomma(decimal_place_f % round_number(total_profit)) if total_profit else '0.00'
        obj['total_turnover_local'] = intcomma(decimal_place_f % round_number(total_turnover_local)) if total_turnover_local else '0.00'
        obj['profit_percentage'] = intcomma("%.4f" % round_number(profit_percentage, 4)) if profit_percentage else '0.0000'
        oi_list.append(obj)

        return total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local

    def print_GrandTotal(self, styles, total_all_profit, total_all_profit_tax, total_all_quantity,
                         total_all_turnover_local, decimal_place_f):
        table_data = []
        table_data.append([Paragraph('Grand Total: ', styles["RightAlignBold"]),
                           Paragraph(intcomma("%.2f" % round_number(total_all_quantity)), styles["RightAlign"]),
                           Paragraph(intcomma(decimal_place_f % round_number(total_all_profit)), styles["RightAlign"]),
                           Paragraph(intcomma(decimal_place_f % round_number(total_all_turnover_local)), styles["RightAlign"]),
                           Paragraph(intcomma("%.4f" % round_number(total_all_profit_tax, 4)) + '%', styles["RightAlign"]), ''])

        item_table = Table(table_data, colWidths=[590, 50, 40, 45, 45, 35])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
             ('VALIGN', (0, 0), (-1, -1), 'TOP')
             ]))
        return item_table

    def get_sum_of_sales_turn_over(self, customer, oi_list):
        sales_turn_over_sum = 0
        for oi in oi_list:
            if customer == oi['customer']:
                sales_turn_over_sum += float(oi['total_turnover_local'].replace(',', ''))
        return sales_turn_over_sum

    def calculate_sales_volume(self, i, customer, sales_turn_over_sum, oi_list):
        sales_volume = 0
        if i == 0:
            customer = oi_list[i]['customer']
            sales_turn_over_sum = self.get_sum_of_sales_turn_over(customer, oi_list)
        if customer != oi_list[i]['customer']:
            customer = oi_list[i]['customer']
            sales_turn_over_sum = self.get_sum_of_sales_turn_over(customer, oi_list)
        if sales_turn_over_sum:
            sales_volume = (float(oi_list[i]['total_turnover_local'].replace(',', '')) / sales_turn_over_sum) * 100
        return customer, sales_turn_over_sum, sales_volume
