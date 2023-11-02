import calendar
import datetime
import xlsxwriter
from companies.models import Company
from orders.models import OrderItem
from reports.print_SR8600 import getExchangeRate, getReferDoc, setSupplierAndPurchasePrice
from utilities.common import round_number
from utilities.constants import ORDER_TYPE, ORDER_STATUS


class Print_SR8603_XLS:
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
        price_format = workbook.add_format({'num_format': '#,##0.00000'})
        rate_format = workbook.add_format({'num_format': '#,##0.0000000'})

        first_day = datetime.date(int(from_year), int(from_month), 1)
        last_day = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])
        company_currency = ''
        company = Company.objects.filter(id=company_id).last()
        if company.currency:
            company_currency = company.currency.id
        # decimal_place_f = get_decimal_place(company.currency)
        is_decimal = company.currency.is_decimal

        worksheet.merge_range('A3:D3', 'SR8602 Sales and Purchase System', merge_format)
        worksheet.merge_range('A4:D4', company.name, merge_format)
        worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)

        worksheet.write(10, 0, 'CUSTOMER', left_bold)
        worksheet.write(10, 1, 'SUPPLIER', left_bold)
        worksheet.write(10, 2, 'PART DESC.', left_bold)
        worksheet.write(10, 3, 'PART NO.', left_bold)
        worksheet.write(10, 4, 'MODEL', left_bold)
        worksheet.write(10, 5, 'BUY_CURR', right_bold)
        worksheet.write(10, 6, 'BUY_RATE', right_bold)
        worksheet.write(10, 7, 'BUY_PRICE', right_bold)
        worksheet.write(10, 8, 'BUY_LOCAL_PRICE', right_bold)
        worksheet.write(10, 9, 'SELL_CURR', right_bold)
        worksheet.write(10, 10, 'SELL_RATE', right_bold)
        worksheet.write(10, 11, 'SELL_PRICE', right_bold)
        worksheet.write(10, 12, 'SELL_LOCAL_PRICE', right_bold)
        worksheet.write(10, 13, 'PROFIT', right_bold)
        worksheet.write(10, 14, 'QTY/M', right_bold)
        worksheet.write(10, 15, 'TOTAL_PROFIT', right_bold)
        worksheet.write(10, 16, 'SALES_TURN_OVER', right_bold)
        worksheet.write(10, 17, 'PROFIT %', right_bold)
        worksheet.write(10, 18, 'VOLUME %', right_bold)
        for x in range(19):
            worksheet.set_column(x, x, 15)

        row = 11
        col = 0

        order_item_list = OrderItem.objects \
            .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .filter(order__document_date__gte=first_day, order__document_date__lte=last_day) \
            .exclude(order__customer__isnull=True, item__isnull=True, order__status=dict(ORDER_STATUS)['Draft'])\
            .select_related('order', 'item', 'supplier', 'order__customer')

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
                            exchange_rate_buy, oi_list)

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
                            exchange_rate_buy, oi_list)
                        total_all_profit_tax = (total_all_profit * 100) / total_all_turnover_local if total_all_turnover_local else 0

                    if oi_list:
                        customer = ''
                        sales_turn_over_sum = 0
                        for i, oi in enumerate(oi_list):
                            customer, sales_turn_over_sum, sales_volume = self.calculate_sales_volume(i, customer,
                                                                                                      sales_turn_over_sum, oi_list)
                            worksheet.write(row, col, customer, left_line)
                            worksheet.write(row, col + 1, oi['supplier'], left_line)
                            worksheet.write(row, col + 2, oi['item_code'], left_line)
                            worksheet.write(row, col + 3, oi['item_name'], left_line)
                            worksheet.write(row, col + 4, oi['item_cat'], left_line)
                            worksheet.write(row, col + 5, oi['curr_buy'], right_line)
                            worksheet.write(row, col + 6, oi['exchange_rate_buy'], rate_format)
                            worksheet.write(row, col + 7, oi['purchase_price'], price_format)
                            worksheet.write(row, col + 8, oi['local_price_buy'], price_format)
                            worksheet.write(row, col + 9, oi['curr_sell'], right_line)
                            worksheet.write(row, col + 10, oi['exchange_rate_sell'], rate_format)
                            worksheet.write(row, col + 11, oi['price_sell'], price_format)
                            worksheet.write(row, col + 12, oi['local_price_sell'], price_format)
                            worksheet.write(row, col + 13, oi['profit'], price_format)
                            worksheet.write(row, col + 14, oi['quantity'], dec_format)
                            worksheet.write(row, col + 15, oi['total_profit'], dec_format if is_decimal else num_format)
                            worksheet.write(row, col + 16, oi['total_turnover_local'], dec_format if is_decimal else num_format)
                            worksheet.write(row, col + 17, oi['profit_percentage'], price_format)
                            worksheet.write(row, col + 18, round_number(sales_volume, 4) if sales_volume else 0.00000, price_format)
                            row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

    def calculate_report_row_element(self, company_currency, company_id, k, order_item_list, quantity, total_all_profit,
                                     total_all_quantity, total_all_turnover, total_all_turnover_local, purchase_price,
                                     curr_buy, exchange_rate_buy, oi_list):
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
        obj['exchange_rate_buy'] = round_number(exchange_rate_buy, 5) if exchange_rate_buy else 0.00000
        obj['purchase_price'] = round_number(purchase_price, 5) if purchase_price else 0.00000
        obj['local_price_buy'] = round_number(local_price_buy, 5) if local_price_buy else 0.00000
        obj['curr_sell'] = order_item_list[k].order.currency.code
        obj['exchange_rate_sell'] = round_number(exchange_rate_sell, 7) if exchange_rate_sell else 0.0000000
        obj['price_sell'] = round_number(order_item_list[k].price, 5) if order_item_list[k].price else 0.00000
        obj['local_price_sell'] = round_number(local_price_sell, 5) if local_price_sell else 0.00000
        obj['profit'] = round_number(profit, 5) if profit else 0.00000
        obj['quantity'] = quantity if quantity else 0.00
        obj['total_profit'] = round_number(total_profit) if total_profit else 0.00
        obj['total_turnover_local'] = round_number(total_turnover_local) if total_turnover_local else 0.00
        obj['profit_percentage'] = round_number(profit_percentage, 4) if profit_percentage else 0.00000
        oi_list.append(obj)

        return total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local

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
