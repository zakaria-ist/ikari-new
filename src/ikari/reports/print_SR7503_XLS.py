import datetime
import xlsxwriter
from django.db.models import Q
from orders.models import OrderItem
from suppliers.models import Supplier
from companies.models import Company
from utilities.common import round_number, get_decimal_place
from utilities.constants import ORDER_STATUS, ORDER_TYPE


class Print_SR7503_XLS(object):
    """docstring for Print_SR7503_XLS"""

    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, issue_from, issue_to, customer_po, part_group, part_no, is_confirm):
        return self.good_received_by_supp(company_id, issue_from, issue_to, customer_po, part_group, part_no, is_confirm)

    def good_received_by_supp(self, company_id, issue_from, issue_to, customer_po, part_group, part_no, is_confirm):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("good_received_by_supplier")

        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })

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

        row = 0
        worksheet.write(row, 0, 'PART NO', left_bold)
        worksheet.write(row, 1, 'PART DESC.', left_bold)
        worksheet.write(row, 2, 'UOM', left_bold)
        worksheet.write(row, 3, 'PART GROUP', left_bold)
        worksheet.write(row, 4, 'TRANS. CODE', left_bold)
        worksheet.write(row, 5, 'DOCUMENT NO', left_bold)
        worksheet.write(row, 6, 'DOCUMENT LINE', right_bold)
        worksheet.write(row, 7, 'SUPPLIER CODE', left_bold)
        worksheet.write(row, 8, 'SUPPLIER NAME', left_bold)
        worksheet.write(row, 9, 'CUSTOMER PO', left_bold)
        worksheet.write(row, 10, 'QUANTITY', right_bold)
        worksheet.write(row, 11, 'UNIT PRICE', right_bold)
        worksheet.write(row, 12, 'EXCHANGE RATE', right_bold)
        worksheet.write(row, 13, 'TAX EXCHANGE RATE', right_bold)
        worksheet.write(row, 14, 'AMOUNT', right_bold)
        worksheet.write(row, 15, 'CONFIRM FLAG', right_bold)

        for x in range(14):
            worksheet.set_column(x, x, 14)

        row += 1
        col = 0

        # company = Company.objects.get(pk=company_id)
        if issue_from is not '0' and issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(issue_from, issue_to)
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')
        elif issue_from is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(issue_from)
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')
        elif issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(issue_to)
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')
        else:
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']
                                                          ) \
                .select_related('order', 'item', 'supplier', 'order__customer')\
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code')

        cust_po_list = eval(customer_po)
        if len(cust_po_list):
            customer_item_list = customer_item_list.filter(customer_po_no__in=cust_po_list)
        group_list = eval(part_group)
        if len(group_list):
            customer_item_list = customer_item_list.filter(item__category__id__in=group_list)
        part_list = eval(part_no)
        if len(part_list):
            customer_item_list = customer_item_list.filter(item_id__in=part_list)

        if is_confirm == 'Y':  # pgrh_updfg
            customer_item_list = customer_item_list.filter(order__is_confirm=is_confirm)

        for i, item in enumerate(customer_item_list):
            # decimal_place = get_decimal_place(item.order.currency)
            is_decimal = item.order.currency.is_decimal
            worksheet.write(row, col, item.item.code, left_line)
            worksheet.write(row, col + 1, item.item.short_description if item.item.short_description else '', left_line)
            worksheet.write(row, col + 2, item.item.purchase_measure.code if item.item.purchase_measure else '', left_line)
            worksheet.write(row, col + 3, item.item.category.code if item.item.category else '', left_line)
            worksheet.write(row, col + 4, 'PIV', left_line)
            worksheet.write(row, col + 5, item.order.document_number, left_line)
            worksheet.write(row, col + 6, item.line_number, right_line)
            worksheet.write(row, col + 7, item.supplier.code if item.supplier.code else '', left_line)
            worksheet.write(row, col + 8, item.supplier.name if item.supplier.name else '', left_line)
            worksheet.write(row, col + 9, item.customer_po_no, left_line)
            worksheet.write(row, col + 10, item.quantity, dec_format)
            worksheet.write(row, col + 11, item.price, price_format)
            worksheet.write(row, col + 12, item.order.exchange_rate, rate_format)
            worksheet.write(row, col + 13, item.order.exchange_rate, rate_format)
            worksheet.write(row, col + 14, round_number(item.amount), dec_format if is_decimal else num_format)
            worksheet.write(row, col + 15, 'N', right_line)
            row = row + 1


        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
