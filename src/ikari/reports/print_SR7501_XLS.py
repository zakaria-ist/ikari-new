from companies.models import Company
import xlsxwriter
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
import datetime
from django.db.models import Q
from utilities.common import round_number, get_decimal_place


class Print_SR7501_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, issue_from, issue_to, supplier_no):
        return self.gross_profit(company_id, issue_from, issue_to, supplier_no)

    def gross_profit(self, company_id, issue_from, issue_to, supplier_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("SR7501")

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

        if issue_from is not '0':
            current_period = datetime.datetime.strptime(issue_from, '%Y-%m-%d')

        # company = Company.objects.get(id=company_id)

        # worksheet.merge_range('A3:D3', 'SR7501 Sales and Purchase System', merge_format)
        # worksheet.merge_range('A4:D4', company.name, merge_format)
        # worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)
        # worksheet.merge_range('A7:D7', "Current Period : [" + current_period.strftime("%B %Y") + "]" if issue_from is not '0' else '', merge_format)

        row = 0
        worksheet.write(row, 0, 'SUPPLIER_CODE', left_bold)
        worksheet.write(row, 1, 'SUPPLIER_NAME', left_bold)
        worksheet.write(row, 2, 'SUPPLIER_CURRENCY', left_bold)
        worksheet.write(row, 3, 'PART NO.', left_bold)
        worksheet.write(row, 4, 'CUSTOMER_PO', left_bold)
        worksheet.write(row, 5, 'QUANTITY', right_bold)
        worksheet.write(row, 6, 'ORIGINAL_AMOUNT', right_bold)
        worksheet.write(row, 7, 'LOCAL_AMOUNT', right_bold)
        for x in range(8):
            worksheet.set_column(x, x, 15)

        row += 1
        col = 0

        if issue_from is not '0' and issue_to is not '0':
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(issue_from, issue_to)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')
        elif issue_from is not '0':
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(issue_from)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')
        elif issue_to is not '0':
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(issue_to)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')
        else:
            supplier_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('supplier__code', 'item__code', 'customer_po_no')

        supplier_list = eval(supplier_no)
        if len(supplier_list):
            supplier_item_list = supplier_item_list.filter(supplier_id__in=supplier_list)

        s_curr = s_name = s_code = i_code = ''
        cust_po_no = ''
        item_quantity = item_amount = item_amount_loc = 0
        # decimal_place = "%.2f"
        is_decimal = True
        for i, mItem in enumerate(supplier_item_list):
            if i == 0:
                s_code = mItem.supplier.code
                s_name = mItem.supplier.name if mItem.supplier.name else ''
                s_curr = mItem.supplier.currency.code
                i_code = mItem.item.code
                cust_po_no = mItem.customer_po_no
                # decimal_place = get_decimal_place(mItem.supplier.currency)
                is_decimal = mItem.supplier.currency.is_decimal
            if i_code != mItem.item.code:
                if item_quantity > 0:
                    worksheet.write(row, col, s_code, left_line)
                    worksheet.write(row, col + 1, s_name, left_line)
                    worksheet.write(row, col + 2, s_curr, left_line)
                    worksheet.write(row, col + 3, i_code, left_line)
                    worksheet.write(row, col + 4, cust_po_no, left_line)
                    worksheet.write(row, col + 5, item_quantity, dec_format)
                    worksheet.write(row, col + 6, round_number(item_amount), dec_format if is_decimal else num_format)
                    worksheet.write(row, col + 7, round_number(item_amount_loc), dec_format if is_decimal else num_format)
                    row = row + 1
                item_quantity = item_amount = item_amount_loc = 0
                i_code = mItem.item.code
                cust_po_no = mItem.customer_po_no
                s_code = mItem.supplier.code
                s_name = mItem.supplier.name
                s_curr = mItem.supplier.currency.code

            if i_code == mItem.item.code:
                if cust_po_no != mItem.customer_po_no:
                    if item_quantity > 0:
                        worksheet.write(row, col, s_code, left_line)
                        worksheet.write(row, col + 1, s_name, left_line)
                        worksheet.write(row, col + 2, s_curr, left_line)
                        worksheet.write(row, col + 3, i_code, left_line)
                        worksheet.write(row, col + 4, cust_po_no, left_line)
                        worksheet.write(row, col + 5, item_quantity, dec_format)
                        worksheet.write(row, col + 6, round_number(item_amount), dec_format if is_decimal else num_format)
                        worksheet.write(row, col + 7, round_number(item_amount_loc), dec_format if is_decimal else num_format)
                        row = row + 1
                    item_quantity = item_amount = item_amount_loc = 0
                    i_code = mItem.item.code
                    cust_po_no = mItem.customer_po_no
                    s_code = mItem.supplier.code
                    s_name = mItem.supplier.name if mItem.supplier.name else ''
                    s_curr = mItem.supplier.currency.code

                if cust_po_no == mItem.customer_po_no:
                    exchange_rate = mItem.order.exchange_rate if mItem.order else 1
                    cust_po_no = mItem.customer_po_no
                    item_quantity += mItem.quantity
                    item_amount += mItem.amount
                    item_amount_loc += round_number(mItem.amount * exchange_rate)

                    # decimal_place = get_decimal_place(mItem.supplier.currency)
                    is_decimal = mItem.supplier.currency.is_decimal

            if i == supplier_item_list.__len__() - 1:
                # Print last row part No Total
                worksheet.write(row, col, s_code, left_line)
                worksheet.write(row, col + 1, s_name, left_line)
                worksheet.write(row, col + 2, s_curr, left_line)
                worksheet.write(row, col + 3, i_code, left_line)
                worksheet.write(row, col + 4, cust_po_no, left_line)
                worksheet.write(row, col + 5, item_quantity, dec_format)
                worksheet.write(row, col + 6, round_number(item_amount), dec_format if is_decimal else num_format)
                worksheet.write(row, col + 7, round_number(item_amount_loc), dec_format if is_decimal else num_format)
                row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
