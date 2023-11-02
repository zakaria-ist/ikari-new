import calendar
import datetime
import xlsxwriter
from companies.models import Company
from orders.models import OrderItem
from reports.print_SR8600 import setSupplierAndPurchasePrice, getReferDoc, getExchangeRate
from suppliers.models import Supplier
from utilities.common import get_company_name_and_current_period, round_number
from utilities.constants import ORDER_STATUS, ORDER_TYPE


class Print_SR8602_XLS:
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

        worksheet.merge_range('A3:D3', 'SR8602 Sales and Purchase System', merge_format)
        worksheet.merge_range('A4:D4', company.name, merge_format)
        worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)

        worksheet.write(10, 0, 'SUPPLIER_CODE', left_bold)
        worksheet.write(10, 1, 'SUPPLIER_NAME', left_bold)
        worksheet.write(10, 2, 'TOTAL_BUTING_PRICE', right_bold)

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
        price_buy = price_sell = exchange_rate_buy = dummy_exchange_rate_buy = 0
        quantity = 0
        first_row = True
        exchange_rate_sell = 0
        supplier_code = item_code = ''
        if order_item_list.exists():
            for order_item in order_item_list:
                refer_doc = getReferDoc(order_item, first_day, last_day)

                if refer_doc:
                    dummy_exchange_rate_buy = getExchangeRate(company_currency, order_item, refer_doc, first_day)

                if first_row:
                    supplier_code = order_item.supplier.code if order_item.supplier else \
                        order_item.reference.supplier.code if order_item.reference.supplier else ''
                    item_code = order_item.item.code
                    price_buy = order_item.last_purchase_price
                    price_sell = order_item.price
                    exchange_rate_buy = dummy_exchange_rate_buy

                if order_item.quantity is not None:
                    supp_code = order_item.supplier.code if order_item.supplier else \
                        order_item.reference.supplier.code if order_item.reference.supplier else ''
                    if supp_code not in item_data:
                        item_data[supp_code] = dict()

                    if order_item.item.code not in item_data[supp_code]:
                        item_data[supp_code][order_item.item.code] = []

                    if (supplier_code == supp_code) & (item_code == order_item.item.code) & \
                            (price_buy == order_item.last_purchase_price):
                        if order_item.quantity is not None:
                            quantity += order_item.quantity
                            exchange_rate_sell = order_item.order.exchange_rate if order_item.order.exchange_rate else 1
                    else:
                        if quantity > 0:
                            item_data[supplier_code][item_code].append({
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
                        supplier_code = supp_code
                        item_code = order_item.item.code
                        exchange_rate_sell = order_item.order.exchange_rate if order_item.order.exchange_rate else 1

                first_row = False

            item_data[supplier_code][item_code].append({
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

            total_all_turnover = 0

            supplier_list = Supplier.objects.filter(is_hidden=0, company_id=company_id) \
                .order_by('code', 'name')

            for supplier in supplier_list:
                total_quantity = 0
                total_profit = 0
                sales_turnover = 0
                sales_local_turnover = 0
                buy_turnover = 0
                buy_local_turnover = 0

                if supplier.code in item_data:
                    for item_row in item_data[supplier.code]:
                        for roww in item_data[supplier.code][item_row]:
                            buy_unit_price = round_number(roww['buy_price'], 5)
                            buy_local_price = round_number(roww['buy_local_price'], 5)
                            total_quantity += round_number(roww['quantity'], 2)
                            total_profit += round_number(roww['quantity'] * roww['profit'], 2)
                            sales_turnover += round_number(roww['quantity'] * roww['sell_price'], 2)
                            sales_local_turnover += round_number(roww['quantity'] * roww['sell_local_price'], 2)
                            buy_turnover += round_number(roww['quantity'] * buy_unit_price, 2)
                            buy_local_turnover += round_number(roww['quantity'] * buy_local_price, 2)

                    supplier_turnover = buy_local_turnover

                    worksheet.write(row, col, supplier.code, left_line)
                    worksheet.write(row, col + 1, supplier.name, left_line)
                    worksheet.write(row, col + 2, round_number(supplier_turnover),
                                    dec_format if is_decimal else num_format)
                    row = row + 1

                    total_all_turnover += supplier_turnover
                else:
                    worksheet.write(row, col, supplier.code, left_line)
                    worksheet.write(row, col + 1, supplier.name, left_line)
                    worksheet.write(row, col + 2, 0.00,
                                    dec_format if is_decimal else num_format)
                    row = row + 1

            worksheet.write(row, col + 2, round_number(total_all_turnover), dec_format)
            row = row + 1

        company_name, current_period = get_company_name_and_current_period(company_id)

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
