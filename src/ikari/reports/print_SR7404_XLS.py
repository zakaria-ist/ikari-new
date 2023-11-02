import xlsxwriter
from orders.models import OrderItem
from django.db.models import F
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from utilities.common import validate_date_to_from, get_company_name_and_current_period


class Print_SR7404_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, delivery_from, delivery_to, customer_no, part_no, part_group):
        return self.outstanding_so_balance(company_id, delivery_from, delivery_to, customer_no, part_no, part_group)

    def outstanding_so_balance(self, company_id, delivery_from, delivery_to, customer_no, part_no, part_group):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("SO Balance by Part No")

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
        price_format = workbook.add_format({'num_format': '#,##0.00000'})
        rate_format = workbook.add_format({'num_format': '#,##0.00000000'})

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)

        row = 0
        worksheet.write(row, 0, 'SSOD_PARTNO', left_bold)
        worksheet.write(row, 1, 'SSOD_PARTDESC', left_bold)
        worksheet.write(row, 2, 'SSOH_CUSCD.', left_bold)
        worksheet.write(row, 3, 'SSOH_TRNCD', left_bold)
        worksheet.write(row, 4, 'SSOH_DOCNO', left_bold)
        worksheet.write(row, 5, 'SSOH_DOCDT', left_bold)
        worksheet.write(row, 6, 'SSOH_XRATE', left_bold)
        worksheet.write(row, 7, 'SSOD_LINE', right_bold)
        worksheet.write(row, 8, 'SSOD_WANTD', right_bold)
        worksheet.write(row, 9, 'SSOD_LDLDT', right_bold)
        worksheet.write(row, 10, 'SSOD_PODOC', left_bold)
        worksheet.write(row, 11, 'SSOD_REFLN', right_bold)
        worksheet.write(row, 12, 'SSOD_UPRICE', right_bold)
        worksheet.write(row, 13, 'SSOD_QTY', right_bold)
        worksheet.write(row, 14, 'SSOD_INVQTY', right_bold)
        worksheet.write(row, 15, 'SSOD_BALQTY', right_bold)
        worksheet.write(row, 16, 'SSOD_CUSTPO', left_bold)
        worksheet.write(row, 17, 'SSOD_SCHDT', right_bold)
        worksheet.write(row, 18, 'SSOD_REM', right_bold)
        for x in range(20):
            worksheet.set_column(x, x, 12)

        row += 1
        col = 0

        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
            .select_related('order', 'item', 'order__currency', 'order__customer')\
            .exclude(order__status__in=[dict(ORDER_STATUS)['Delivered'], dict(ORDER_STATUS)['Draft']]) \
            .exclude(quantity__lte=F('delivery_quantity')) \
            .annotate(balance_qty=F('quantity') - F('delivery_quantity')) \
            .order_by('item__code', 'wanted_date', 'order__customer__code', 'line_number')

        po_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(reference_id__isnull=True)\
            .select_related('order')

        order_item_list = order_item_list.filter(wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                     delivery_to_obj.strftime('%Y-%m-%d')))

        part_list = eval(part_no)
        if len(part_list):
            order_item_list = order_item_list.filter(item_id__in=part_list)
        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)
        grp_list = eval(part_group)
        if len(grp_list):
            order_item_list = order_item_list.filter(item__category_id__in=grp_list)

        m_item_code = ''
        acc_qty = acc_receive_qty = acc_balance_qty = 0  # sum qty of each part
        grand_total_qty = grand_total_receive_qty = grand_total_balance_qty = 0

        for i, mItem in enumerate(order_item_list):
            if m_item_code != mItem.item.code and float(mItem.balance_qty) > 0:
                m_item_code = mItem.item.code
                acc_qty = acc_receive_qty = acc_balance_qty = 0  # sum qty of each part

            #   check on next row data
            if m_item_code == mItem.item.code and float(mItem.balance_qty) > 0:
                item_quantity = float(mItem.quantity) if mItem.quantity else 0
                delivery_quantity = float(mItem.delivery_quantity) if mItem.delivery_quantity else 0
                grand_total_qty += item_quantity
                grand_total_receive_qty += delivery_quantity
                grand_total_balance_qty += float(mItem.balance_qty)
                acc_qty += item_quantity
                acc_receive_qty += delivery_quantity
                acc_balance_qty += float(mItem.balance_qty)

                po_item = po_items.filter(reference_id=mItem.order.id, refer_line=mItem.line_number).last()

                worksheet.write(row, col, mItem.item.code if mItem.item.code else '', left_line)
                worksheet.write(row, col + 1, mItem.item.short_description if mItem.item.short_description else '', left_line)
                worksheet.write(row, col + 2, mItem.order.customer.code, left_line)
                worksheet.write(row, col + 3, 'S/O', left_line)
                worksheet.write(row, col + 4, mItem.order.document_number, left_line)
                worksheet.write(row, col + 5, mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ', right_line)
                worksheet.write(row, col + 6, mItem.order.exchange_rate, rate_format)
                worksheet.write(row, col + 7, str(mItem.line_number), right_line)

                worksheet.write(row, col + 8, mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ', right_line)
                worksheet.write(row, col + 9, mItem.last_delivery_date.strftime("%d/%m/%Y") if mItem.last_delivery_date else ' / / ', right_line)
                worksheet.write(row, col + 10, po_item.order.document_number if po_item else '', left_line)
                worksheet.write(row, col + 11, po_item.refer_line if po_item else '0', right_line)
                worksheet.write(row, col + 12, mItem.price, price_format)
                worksheet.write(row, col + 13, mItem.quantity, dec_format)
                worksheet.write(row, col + 14, delivery_quantity, dec_format)
                worksheet.write(row, col + 15, mItem.balance_qty, dec_format)
                worksheet.write(row, col + 16, mItem.customer_po_no, left_line)
                worksheet.write(row, col + 17, mItem.schedule_date.strftime("%d/%m/%Y") if mItem.schedule_date else ' / / ', right_line)
                worksheet.write(row, col + 18, mItem.order.remark if mItem.order.remark else '', right_line)
                row = row + 1

            if i + 1 < order_item_list.__len__():
                if order_item_list[i + 1].item.code != m_item_code and float(acc_balance_qty) > 0:
                    acc_qty = acc_receive_qty = acc_balance_qty = 0

            if not float(acc_balance_qty) == 0:
                acc_qty = acc_receive_qty = acc_balance_qty = 0

        company_name, current_period = get_company_name_and_current_period(company_id)

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
