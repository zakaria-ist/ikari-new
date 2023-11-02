import xlsxwriter
from orders.models import OrderItem
from companies.models import Company
from utilities.common import validate_date_to_from, round_number
from utilities.constants import ORDER_STATUS, ORDER_TYPE


class Print_SR7103_XLS(object):
    """docstring for Print_SR7103_XLS"""

    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, date_from, date_to, cust_po, part_no, customer_code, is_confirm):
        return self.sales_analysis_customer_code(company_id, date_from, date_to, cust_po, part_no, customer_code, is_confirm)

    def sales_analysis_customer_code(self, company_id, date_from, date_to, cust_po, part_no, customer_code, is_confirm):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Sales_Analysis")

        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter'
        })
        right_line = workbook.add_format({
            'align': 'right'
        })
        right_bold = workbook.add_format({
            'align': 'right',
            'bold': True,
        })
        right_bold_dec = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'bold': True,
        })

        right_bold_num = workbook.add_format({
            'num_format': '#,##0',
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

        delivery_from_obj, delivery_to_obj = validate_date_to_from(date_from, date_to)

        company = Company.objects.get(pk=company_id)

        row = 0
        worksheet.write(row, 1, 'Customer Code & Name', title_format)
        row += 1
        worksheet.write(row, 2, 'Document No.', left_bold)
        worksheet.write(row, 3, 'Doc. Date', left_bold)
        worksheet.write(row, 4, 'Curr.', left_bold)
        worksheet.write(row, 5, 'Exch. Rate', left_bold)
        worksheet.write(row, 6, 'Ln', left_bold)
        worksheet.write(row, 7, 'Delivery Qty', right_bold)
        worksheet.write(row, 8, 'Unit Price', right_bold)
        worksheet.write(row, 9, 'Amount (ORG)', right_bold)
        worksheet.write(row, 10, 'Cfm', right_bold)
        row += 1
        worksheet.write(row, 2, 'Customer PO No.', left_bold)
        worksheet.write(row, 3, 'Part No.', left_bold)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 18)
        worksheet.set_column(3, 3, 18)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 15)

        row += 2
        col = 1

        stock_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                              order__order_type=dict(ORDER_TYPE)['SALES INVOICE'],
                                              order__document_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                           delivery_to_obj.strftime('%Y-%m-%d'))) \
            .exclude(order__status=dict(ORDER_STATUS)['Draft']) \
            .select_related('item', 'order', 'order__customer')\
            .order_by('order__customer__code', 'order__document_number').distinct()

        cust_list = eval(customer_code)
        if len(cust_list):
            stock_list = stock_list.filter(order__customer_id__in=cust_list)
        cust_po_list = eval(cust_po)
        if len(cust_po_list):
            stock_list = stock_list.filter(customer_po_no__in=cust_po_list)
        part_list = eval(part_no)
        if len(part_list):
            stock_list = stock_list.filter(item__code__in=part_list)

        sum_qty = sum_amount = sum_loc = 0
        sum_all_qty = sum_all_loc = 0
        company = Company.objects.get(pk=company_id)
        # decimal_place_f = get_decimal_place(company.currency)
        is_decimal_f = company.currency.is_decimal
        if stock_list:
            customer_id = ''
            m_currency = company.currency
            for i, item in enumerate(stock_list):
                if item.order.customer_id != customer_id and item.order.customer_id != '':
                    customer_id = item.order.customer_id
                    if i != 0:
                        # decimal_place = get_decimal_place(m_currency)
                        is_decimal = m_currency.is_decimal
                        worksheet.write(row, col + 3, 'Customer', right_bold)
                        worksheet.write(row, col + 4, 'Total:', left_bold)
                        worksheet.write(row, col + 5, '(QTY):', left_bold)
                        worksheet.write(row, col + 6, sum_qty, right_bold_dec)
                        worksheet.write(row, col + 7, 'Amt(ORG):', right_bold)
                        worksheet.write(row, col + 8, round_number(sum_amount),
                                        right_bold_dec if is_decimal else right_bold_num)
                        row = row + 1
                        worksheet.write(row, col + 7, '(Loc):', right_bold)
                        worksheet.write(row, col + 8, round_number(sum_loc),
                                        right_bold_dec if is_decimal_f else right_bold_num)
                        row = row + 2

                        sum_qty = sum_amount = sum_loc = 0

                    worksheet.write(row, col, item.order.customer.code, title_format)
                    worksheet.write(row, col + 3, item.order.customer.name, title_format)
                    row = row + 1

                # decimal_place = get_decimal_place(item.order.currency)
                is_decimal = item.order.currency.is_decimal
                worksheet.write(row, col + 1, item.order.document_number, left_line)
                worksheet.write(row, col + 2, item.order.document_date.strftime('%d-%m-%Y'), left_line)
                worksheet.write(row, col + 3, item.order.currency.code, left_line)
                worksheet.write(row, col + 4, item.order.exchange_rate, left_line)
                worksheet.write(row, col + 5, item.line_number, left_line)
                worksheet.write(row, col + 6, item.quantity, dec_format)
                worksheet.write(row, col + 7, round_number(item.price, 5), price_format)
                worksheet.write(row, col + 8, round_number(item.amount),
                                dec_format if is_decimal else num_format)
                worksheet.write(row, col + 9, 'N', right_line)
                row = row + 1

                m_currency = item.order.currency
                sum_qty += item.quantity
                sum_amount += item.amount
                sum_loc += round_number(item.amount * item.order.exchange_rate)
                sum_all_qty += item.quantity
                sum_all_loc += round_number(item.amount * item.order.exchange_rate)

                worksheet.write(row, col + 1, item.customer_po_no if item.customer_po_no else '', left_line)
                worksheet.write(row, col + 2, item.item.code, left_line)
                row = row + 1

            if stock_list.__len__() - 1 == i:
                # decimal_place = get_decimal_place(m_currency)
                is_decimal = m_currency.is_decimal
                worksheet.write(row, col + 3, 'Customer', right_bold)
                worksheet.write(row, col + 4, 'Total:', left_bold)
                worksheet.write(row, col + 5, '(QTY):', left_bold)
                worksheet.write(row, col + 6, sum_qty, right_bold_dec)
                worksheet.write(row, col + 7, 'Amt(ORG):', right_bold)
                worksheet.write(row, col + 8, round_number(sum_amount),
                                right_bold_dec if is_decimal else right_bold_num)
                row = row + 1
                worksheet.write(row, col + 7, '(Loc):', right_bold)
                worksheet.write(row, col + 8, round_number(
                    sum_loc),  right_bold_dec if is_decimal_f else right_bold_num)
                row = row + 2
                worksheet.write(row, col + 4, 'Grand Total', right_bold)
                worksheet.write(row, col + 6, sum_all_qty, right_bold_dec)
                worksheet.write(row, col + 8, round_number(sum_all_loc),
                    right_bold_dec if is_decimal_f else right_bold_num)
                row = row + 2

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
