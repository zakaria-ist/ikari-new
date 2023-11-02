import calendar
import datetime
import xlsxwriter
from django.db.models import F, Value as V
from django.db.models.functions import Coalesce
from companies.models import Company
from orders.models import OrderItem
from suppliers.models import SupplierItem
from utilities.constants import ORDER_TYPE, ORDER_STATUS
from utilities.common import round_number
from reports.print_SR8600 import getExchangeRate, getReferDoc, getPurchasePrice


class Print_SR8600_XLS:

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

        company = Company.objects.get(pk=company_id)
        # decimal_place_f = get_decimal_place(company.currency)
        is_decimal = company.currency.is_decimal
        worksheet.merge_range('A3:D3', 'SR8600 Sales and Purchase System', merge_format)
        worksheet.merge_range('A4:D4', company.name, merge_format)
        worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)

        worksheet.write(10, 0, 'CUSTOMER', left_bold)
        worksheet.write(10, 1, 'SUPPLIER', left_bold)
        worksheet.write(10, 2, 'PART DESC.', left_bold)
        worksheet.write(10, 3, 'PART NO.', left_bold)
        worksheet.write(10, 4, 'MODEL', left_bold)
        worksheet.write(10, 5, 'BUY_CURR', left_bold)
        worksheet.write(10, 6, 'BUY_RATE', right_bold)
        worksheet.write(10, 7, 'BUY_PRICE', right_bold)
        worksheet.write(10, 8, 'BUY_LOCAL_PRICE', right_bold)
        worksheet.write(10, 9, 'SELL_CURR', left_bold)
        worksheet.write(10, 10, 'SELL_RATE', right_bold)
        worksheet.write(10, 11, 'SELL_PRICE', right_bold)
        worksheet.write(10, 12, 'SELL_LOCAL_PRICE', right_bold)
        worksheet.write(10, 13, 'PROFIT', right_bold)
        worksheet.write(10, 14, 'QTY/M', right_bold)
        worksheet.write(10, 15, 'TOTAL_PROFIT', right_bold)
        worksheet.write(10, 16, 'SALES_TURN_OVER', right_bold)
        worksheet.write(10, 17, 'SALES_TURN_OVER_LOCAL', right_bold)
        worksheet.write(10, 18, 'PROFIT_PERCENT', right_bold)
        for x in range(19):
            worksheet.set_column(x, x, 15)

        row = 11
        col = 0

        first_day = datetime.date(int(from_year), int(from_month), 1)
        last_day = datetime.date(int(to_year), int(to_month), calendar.monthrange(int(to_year), int(to_month))[1])
        order_item_list = OrderItem.objects \
            .select_related('order').select_related('item') \
            .select_related('supplier').select_related('order__customer') \
            .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .filter(order__document_date__gte=first_day, order__document_date__lte=last_day) \
            .exclude(order__customer__isnull=True, item__isnull=True, order__status=dict(ORDER_STATUS)['Draft'])

        company_currency = ''
        company = Company.objects.filter(id=company_id).last()
        if company.currency:
            company_currency = company.currency.id

        line = 0
        quantity = 0
        total_all_turnover = total_all_profit = total_all_quantity = total_all_profit_tax = total_all_turnover_local = 0
        code = part_no = ''
        price_buy = price_sell = exchange_rate_buy = dummy_exchange_rate_buy = 0
        exchange_rate_sell = 0
        curr_buy = ''
        if order_item_list.exists():
            order_item_list = order_item_list.order_by('order__customer__code', 'supplier__code', 'item__code',
                                                       'last_purchase_price', 'price')

            for i, cus in enumerate(order_item_list):
                refer_doc = getReferDoc(cus, first_day, last_day)
                if refer_doc:
                    cus.last_purchase_price = getPurchasePrice(refer_doc)
                    cus.save()
                    curr_buy = refer_doc.order.currency.code
                    dummy_exchange_rate_buy = getExchangeRate(company_currency, cus, refer_doc, first_day)

                if i == 0:
                    code = cus.order.customer.code if cus.order.customer else ''
                    part_no = cus.item.code
                    price_buy = cus.last_purchase_price
                    price_sell = cus.price
                    exchange_rate_buy = dummy_exchange_rate_buy
                    exchange_rate_sell = cus.order.exchange_rate

                if (code == cus.order.customer.code) & (part_no == cus.item.code) \
                        & (price_buy == cus.last_purchase_price) & (price_sell == cus.price) \
                        & (exchange_rate_sell == cus.order.exchange_rate):
                    if cus.quantity is not None:
                        quantity += cus.quantity
                else:
                    if quantity > 0:
                        k = i - 1
                        total_all_turnover_1 = total_all_profit_1 = total_all_quantity_1 = local_price_buy = total_all_turnover_local_1 = 0
                        local_price_sell = round_number(order_item_list[k].price * exchange_rate_sell, 5)
                        local_price_buy = round_number(price_buy * exchange_rate_buy, 5)
                        profit = local_price_sell - local_price_buy
                        total_profit = round_number(quantity * profit)
                        total_turnover = round_number(order_item_list[k].price * quantity)
                        total_turnover_local = round_number(local_price_sell * quantity)
                        profit_percentage = profit / (local_price_sell / 100) if local_price_sell else 0
                        total_all_turnover_1 += total_turnover
                        total_all_profit_1 += total_profit
                        total_all_quantity_1 += quantity
                        total_all_turnover_local_1 += total_turnover_local

                        item_desc = ''
                        if order_item_list[k].item.short_description:
                            item_desc = order_item_list[k].item.short_description[:16]
                        elif order_item_list[k].item.name:
                            item_desc = order_item_list[k].item.name[:16]
                        worksheet.write(row, col, order_item_list[k].order.customer.code if order_item_list[k].order.customer else '', left_line)
                        worksheet.write(row, col + 1, order_item_list[k].supplier.code if order_item_list[k].supplier else '', left_line)
                        worksheet.write(row, col + 2, item_desc, left_line)
                        worksheet.write(row, col + 3, order_item_list[k].item.code[:17], left_line)
                        worksheet.write(row, col + 4, order_item_list[k].item.category.code if order_item_list[k].item.category else '', left_line)
                        worksheet.write(row, col + 5, order_item_list[k].supplier.currency.code if order_item_list[k].supplier else '', left_line)
                        worksheet.write(row, col + 6, round_number(exchange_rate_buy, 7) if exchange_rate_buy else 0.0000000, rate_format)
                        worksheet.write(row, col + 7, round_number(price_buy, 5) if price_buy else 0.00000, price_format)
                        worksheet.write(row, col + 8, round_number(local_price_buy, 5) if local_price_buy else 0.00000, price_format)
                        worksheet.write(row, col + 9, order_item_list[k].order.currency.code, left_line)
                        worksheet.write(row, col + 10, round_number(exchange_rate_sell, 7) if exchange_rate_sell else 0.0000000, rate_format)
                        worksheet.write(row, col + 11, round_number(order_item_list[k].price, 5) if order_item_list[k].price else 0.00000, price_format)
                        worksheet.write(row, col + 12, round_number(local_price_sell, 5) if local_price_sell else 0.00000, price_format)
                        worksheet.write(row, col + 13, round_number(profit, 5) if profit else 0.00000, price_format)
                        worksheet.write(row, col + 14, quantity if quantity else 0.00, dec_format)
                        worksheet.write(row, col + 15, round_number(total_profit) if total_profit else 0.00, dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 16, round_number(total_turnover) if total_turnover else 0.00, dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 17, round_number(total_turnover_local)
                                        if total_turnover_local else 0.00, dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 18, str(round_number(profit_percentage, 5)) +
                                        '%' if profit_percentage else '0.0000%', right_line)
                        row = row + 1

                        total_all_quantity += total_all_quantity_1
                        total_all_profit += total_all_profit_1
                        total_all_turnover += total_all_turnover_1
                        total_all_turnover_local += total_all_turnover_local_1

                        if (total_all_profit > 0) & (total_all_turnover > 0):
                            total_all_profit_tax += (total_all_profit / total_all_turnover) * 100

                        line += 1

                    if cus.quantity is not None:
                        quantity = cus.quantity
                    else:
                        quantity = 0

                    if (code != cus.order.customer.code) & (line > 0):
                        pass

                    code = cus.order.customer.code
                    part_no = cus.item.code
                    price_buy = cus.last_purchase_price
                    price_sell = cus.price
                    exchange_rate_buy = dummy_exchange_rate_buy
                    exchange_rate_sell = cus.order.exchange_rate
                if i == order_item_list.__len__() - 1:
                    k = i
                    if quantity > 0:

                        total_all_turnover_1 = total_all_profit_1 = total_all_quantity_1 = local_price_buy = total_all_turnover_local_1 = 0
                        # exchange_rate_sell = order_item_list[k].order.exchange_rate if order_item_list[k].order.exchange_rate else 1
                        local_price_sell = round_number(order_item_list[k].price * exchange_rate_sell, 5)
                        local_price_buy = round_number(price_buy * exchange_rate_buy, 5)
                        profit = local_price_sell - local_price_buy
                        total_profit = round_number(quantity * profit)
                        total_turnover = round_number(order_item_list[k].price * quantity)
                        total_turnover_local = round_number(local_price_sell * quantity)
                        profit_percentage = profit / (local_price_sell / 100) if local_price_sell else 0
                        total_all_turnover_1 += total_turnover
                        total_all_profit_1 += total_profit
                        total_all_quantity_1 += quantity
                        total_all_turnover_local_1 += total_turnover_local

                        worksheet.write(row, col, order_item_list[k].order.customer.code if order_item_list[k].order.customer else '', left_line)
                        worksheet.write(row, col + 1, order_item_list[k].supplier.code if order_item_list[k].supplier else '', left_line)
                        worksheet.write(row, col + 2, order_item_list[k].item.name[:16], left_line)
                        worksheet.write(row, col + 3, order_item_list[k].item.code[:17], left_line)
                        worksheet.write(row, col + 4, order_item_list[k].item.category.code if order_item_list[k].item.category else '', left_line)
                        worksheet.write(row, col + 5, order_item_list[k].supplier.currency.code if order_item_list[k].supplier else '', left_line)
                        worksheet.write(row, col + 6, round_number(exchange_rate_buy, 7) if exchange_rate_buy else 0.0000000, rate_format)
                        worksheet.write(row, col + 7, round_number(price_buy, 5) if price_buy else 0.00000, price_format)
                        worksheet.write(row, col + 8, round_number(local_price_buy, 5) if local_price_buy else 0.00000, price_format)
                        worksheet.write(row, col + 9, order_item_list[k].order.currency.code, left_line)
                        worksheet.write(row, col + 10, round_number(exchange_rate_sell, 7) if exchange_rate_sell else 0.0000000, rate_format)
                        worksheet.write(row, col + 11, round_number(order_item_list[k].price, 5) if order_item_list[k].price else 0.00000, price_format)
                        worksheet.write(row, col + 12, round_number(local_price_sell, 5) if local_price_sell else 0.00000, price_format)
                        worksheet.write(row, col + 13, round_number(profit, 5) if profit else 0.00000, price_format)
                        worksheet.write(row, col + 14, quantity if quantity else 0.00, dec_format)
                        worksheet.write(row, col + 15, round_number(total_profit) if total_profit else 0.00, dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 16, round_number(total_turnover) if total_turnover else 0.00, dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 17, round_number(total_turnover_local)
                                        if total_turnover_local else 0.00, dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 18, str(round_number(profit_percentage, 5)) +
                                        '%' if profit_percentage else '0.0000%', right_line)
                        row = row + 1

                        total_all_quantity += total_all_quantity_1
                        total_all_profit += total_all_profit_1
                        total_all_turnover += total_all_turnover_1
                        total_all_turnover_local += total_all_turnover_local_1

                        total_all_profit_tax = (total_all_profit * 100) / total_all_turnover_local if total_all_turnover_local else 0

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data

