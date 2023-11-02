import calendar
import datetime
import xlsxwriter
from companies.models import Company
from customers.models import Customer
from orders.models import OrderItem
from reports.print_SR8600 import getExchangeRate, getReferDoc, setSupplierAndPurchasePrice
from utilities.common import get_company_name_and_current_period, round_number
from utilities.constants import ORDER_STATUS, ORDER_TYPE


class Print_SR8601_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, from_month, from_year, to_month, to_year):
        return self.monthly_gross_profit(company_id, from_month, from_year, to_month, to_year)

    def monthly_gross_profit(self, company_id, from_month, from_year, to_month, to_year):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Gross Profit")

        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })

        right_line = workbook.add_format({
            'align': 'right'
        })

        right_bold = workbook.add_format({
            'align': 'right',
            'bold': True,
        })

        left_line = workbook.add_format({
            'align': 'left'
        })

        left_bold = workbook.add_format({
            'align': 'left',
            'bold': True,
        })

        dec_format = workbook.add_format({'num_format': '#,##0.00'})
        num_format = workbook.add_format({'num_format': '#,##0'})

        first_day = datetime.date(int(from_year), int(from_month), 1)
        last_day = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])

        company_currency = ''

        company = Company.objects.filter(id=company_id).last()
        # decimal_place_f = get_decimal_place(company.currency)
        is_decimal = company.currency.is_decimal

        if company.currency:
            company_currency = company.currency.id

        worksheet.merge_range('A3:D3', 'SR8601 Sales and Purchase System', merge_format)
        worksheet.merge_range('A4:D4', company.name, merge_format)
        worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)

        worksheet.write(10, 0, 'CUSTOMER_CODE', left_bold)
        worksheet.write(10, 1, 'CUSTOMER_NAME', left_bold)
        worksheet.write(10, 2, 'TOTAL_PROFIT', right_bold)
        worksheet.write(10, 3, 'TOTAL_SALES_TURNOVER', right_bold)

        for x in range(4):
            worksheet.set_column(x, x, 20)

        row = 11
        col = 0

        order_item_list = OrderItem.objects \
            .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .filter(order__document_date__gte=first_day, order__document_date__lte=last_day) \
            .exclude(order__customer__isnull=True, item__isnull=True, order__status=dict(ORDER_STATUS)['Draft'])\
            .select_related('order', 'item', 'supplier', 'order__customer')

        # setSupplierAndPurchasePrice(order_item_list)

        order_item_list = order_item_list.order_by('order__customer__code', 'supplier__code', 'item__code',
                                                   'last_purchase_price', 'price')

        item_data = dict()
        customer_code = item_code = ''
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
                'profit': round_number(round_number(price_sell * exchange_rate_sell, 5) - (round_number(price_buy * exchange_rate_buy, 5)),
                                       5),  # profit
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
                        for roww in item_data[customer.code][item_row]:
                            total_quantity += round_number(roww['quantity'], 2)
                            total_profit += round_number(roww['quantity'] * roww['profit'], 2)
                            sales_turnover += round_number(roww['quantity'] * roww['sell_price'], 2)
                            sales_local_turnover += round_number(roww['quantity'] * roww['sell_local_price'], 2)

                    customer_profit = total_profit
                    customer_turnover = sales_local_turnover

                    worksheet.write(row, col, customer.code, left_line)
                    worksheet.write(row, col + 1, customer.name, left_line)
                    worksheet.write(row, col + 2, round_number(customer_profit), dec_format if is_decimal else num_format)
                    worksheet.write(row, col + 3, round_number(customer_turnover), dec_format if is_decimal else num_format)
                    row = row + 1

                    total_all_profit += customer_profit
                    total_all_turnover += customer_turnover
                else:
                    worksheet.write(row, col, customer.code, left_line)
                    worksheet.write(row, col + 1, customer.name, left_line)
                    worksheet.write(row, col + 2, 0.00, dec_format if is_decimal else num_format)
                    worksheet.write(row, col + 3, 0.00, dec_format if is_decimal else num_format)
                    row = row + 1

            worksheet.write(row, col + 2, round_number(total_all_profit), dec_format if is_decimal else num_format)
            worksheet.write(row, col + 3, round_number(total_all_turnover), dec_format if is_decimal else num_format)
            row = row + 1

        company_name, current_period = get_company_name_and_current_period(company_id)

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
