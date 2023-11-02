import xlsxwriter
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from django.db.models import F
from utilities.common import validate_date_to_from


class Print_SR7403_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, delivery_from, delivery_to, customer_no, supplier_no):
        return self.outstanding_so_balance(company_id, delivery_from, delivery_to, customer_no, supplier_no)

    def outstanding_so_balance(self, company_id, delivery_from, delivery_to, customer_no, supplier_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("SO Balance by Wanted Date")

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
        worksheet.write(row, 0, 'SSOH_CUSCD.', left_bold)
        worksheet.write(row, 1, 'SSOH_TRNCD', left_bold)
        worksheet.write(row, 2, 'SSOH_DOCNO', left_bold)
        worksheet.write(row, 3, 'SSOH_DOCDT', right_bold)
        worksheet.write(row, 4, 'SSOH_XRATE', right_bold)
        worksheet.write(row, 5, 'SSOD_LINE', right_bold)
        worksheet.write(row, 6, 'SSOD_PARTNO', left_bold)
        worksheet.write(row, 7, 'SSOD_WANTD', right_bold)
        worksheet.write(row, 8, 'SSOD_LDLDT', right_bold)
        worksheet.write(row, 9, 'SSOD_UPRICE', right_bold)
        worksheet.write(row, 10, 'SSOD_QTY', right_bold)
        worksheet.write(row, 11, 'SSOD_IVQTY', right_bold)
        worksheet.write(row, 12, 'SSOD_CUSTPO', left_bold)
        worksheet.write(row, 13, 'SSOD_SUPCD', left_bold)
        worksheet.write(row, 14, 'SSOD_PODOC', left_bold)
        worksheet.write(row, 15, 'SSOD_POLN', right_bold)
        worksheet.write(row, 16, 'SSOD_BALQTY', right_bold)
        for x in range(17):
            worksheet.set_column(x, x, 12)

        row += 1
        col = 0

        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                   order__status__gte=dict(ORDER_STATUS)['Sent'],
                                                   wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                       delivery_to_obj.strftime('%Y-%m-%d'))) \
            .select_related('order', 'item', 'order__currency', 'order__customer')\
            .exclude(quantity__lte=F('delivery_quantity')) \
            .annotate(balance_qty=F('quantity') - F('delivery_quantity')) \
            .order_by('wanted_date', 'order__document_number', 'line_number')

        po_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(reference_id__isnull=True)\
            .select_related('order')

        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)
        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(supplier_id__in=supp_list)

        for i, mItem in enumerate(order_item_list):
            exchange_rate = mItem.order.exchange_rate
            item_price = mItem.price if mItem.price else 0
            item_quantity = float(mItem.quantity) if mItem.quantity else 0
            delivery_quantity = float(mItem.delivery_quantity) if mItem.delivery_quantity else 0
            balance_qty = float(mItem.balance_qty) if mItem.balance_qty else 0

            po_item = po_items.filter(reference_id=mItem.order.id, refer_line=mItem.line_number).last()

            worksheet.write(row, col, mItem.order.customer.code, left_line)
            worksheet.write(row, col + 1, 'S/O', left_line)
            worksheet.write(row, col + 2, mItem.order.document_number, left_line)
            worksheet.write(row, col + 3, mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ', right_line)
            worksheet.write(row, col + 4, exchange_rate, rate_format)
            worksheet.write(row, col + 5, str(mItem.line_number), right_line)
            worksheet.write(row, col + 6, mItem.item.code if mItem.item.code else '', left_line)
            worksheet.write(row, col + 7, mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ', right_line)
            worksheet.write(row, col + 8, mItem.last_delivery_date.strftime("%d/%m/%Y") if mItem.last_delivery_date else ' / / ', right_line)
            worksheet.write(row, col + 9, item_price, price_format)
            worksheet.write(row, col + 10, item_quantity, dec_format)
            worksheet.write(row, col + 11, delivery_quantity, dec_format)
            worksheet.write(row, col + 12, mItem.customer_po_no, left_line)
            worksheet.write(row, col + 13, mItem.supplier.code, left_line)
            worksheet.write(row, col + 14, po_item.order.document_number if po_item else '', left_line)
            worksheet.write(row, col + 15, po_item.refer_line if po_item else '0', right_line)
            worksheet.write(row, col + 16, balance_qty, dec_format)
            row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
