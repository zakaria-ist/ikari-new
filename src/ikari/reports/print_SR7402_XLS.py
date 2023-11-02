import xlsxwriter
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from django.db.models import F
from utilities.common import validate_date_to_from, get_company_name_and_current_period, round_number


class Print_SR7402_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, delivery_from, delivery_to, customer_no):
        return self.outstanding_so_balance(company_id, delivery_from, delivery_to, customer_no)

    def outstanding_so_balance(self, company_id, delivery_from, delivery_to, customer_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("SO Balance by Cus")

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
        worksheet.write(row, 3, 'SSOH_DOCDT', left_bold)
        worksheet.write(row, 4, 'SSOH_XRATE', left_bold)
        worksheet.write(row, 5, 'SSOD_LINE', right_bold)
        worksheet.write(row, 6, 'SSOD_PARTNO', right_bold)
        worksheet.write(row, 7, 'SSOD_WANTD', right_bold)
        worksheet.write(row, 8, 'SSOD_LDLDT', right_bold)
        worksheet.write(row, 9, 'SSOD_PODOC', left_bold)
        worksheet.write(row, 10, 'SSOD_REFLN', right_bold)
        worksheet.write(row, 11, 'SSOD_UPRICE', right_bold)
        worksheet.write(row, 12, 'SSOD_QTY', right_bold)
        worksheet.write(row, 13, 'SSOD_DLQTY', right_bold)
        worksheet.write(row, 14, 'SSOD_BALQTY', right_bold)
        worksheet.write(row, 15, 'SSOD_CUSTPO', left_bold)
        worksheet.write(row, 16, 'SSOD_SCHDT', right_bold)
        worksheet.write(row, 17, 'SSOD_REM', right_bold)
        for x in range(18):
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
            .annotate(balance=F('quantity') - F('delivery_quantity')) \
            .order_by('order__customer__code', 'order__document_number', 'line_number')

        po_items = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(reference_id__isnull=True)\
            .select_related('order')

        cust_list = eval(customer_no)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)

        m_customer_no = ''
        m_document_no = ''
        doc_qty = doc_delivery_qty = doc_balance_qty = 0  # sum qty of each Order
        cus_qty = cus_delivery_qty = cus_balance_qty = cus_loc_amount = 0  # sum qty of each supplier
        grand_qty = grand_delivery_qty = grand_balance_qty = 0  # total sum
        doc_org_amount = doc_loc_amount = 0
        cus_org_amount = grand_loc = 0
        for i, mItem in enumerate(order_item_list):
            exchange_rate = mItem.order.exchange_rate
            grand_loc += round_number((mItem.quantity - mItem.delivery_quantity) * mItem.price * exchange_rate)  # mItem.amount * exchange_rate

            if float(mItem.balance) > 0:
                grand_qty += mItem.quantity
                grand_delivery_qty += mItem.delivery_quantity
                grand_balance_qty += mItem.balance

            # check to print first row of supplier
            if m_customer_no != mItem.order.customer.code and float(mItem.balance) > 0:
                # Start new Customer PO Total
                table_customer_no_data = []
                cus_qty = cus_delivery_qty = cus_balance_qty = cus_org_amount = cus_loc_amount = 0
                m_customer_no = mItem.order.customer.code
                table_customer_no_data.append([mItem.order.customer.code, mItem.order.customer.name, '', '', '', ''])

            # check to print first row of Order
            if m_document_no != mItem.order.document_number and float(mItem.balance) > 0:
                m_document_no = mItem.order.document_number
                doc_qty = doc_delivery_qty = doc_balance_qty = 0
                doc_org_amount = doc_loc_amount = 0

            # check to print next row of Order
            if m_customer_no == mItem.order.customer.code \
                    and m_document_no == mItem.order.document_number \
                    and float(mItem.balance) > 0:
                doc_qty += mItem.quantity
                doc_delivery_qty += mItem.delivery_quantity
                doc_balance_qty += float(mItem.balance)

                doc_org_amount += round_number(mItem.balance * mItem.price)
                doc_loc_amount = round_number(doc_org_amount * exchange_rate)

                cus_qty += mItem.quantity
                cus_delivery_qty += mItem.delivery_quantity
                cus_balance_qty += mItem.balance

                cus_org_amount += mItem.amount
                cus_loc_amount += round_number(mItem.balance * mItem.price * exchange_rate)

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
                worksheet.write(row, col + 9, po_item.order.document_number if po_item else '', left_line)
                worksheet.write(row, col + 10, po_item.refer_line if po_item else '0', right_line)
                worksheet.write(row, col + 11, mItem.price, price_format)
                worksheet.write(row, col + 12, mItem.quantity, dec_format)
                worksheet.write(row, col + 13, mItem.delivery_quantity, dec_format)
                worksheet.write(row, col + 14, mItem.balance, dec_format)
                worksheet.write(row, col + 15, mItem.customer_po_no, left_line)
                worksheet.write(row, col + 16, mItem.schedule_date.strftime("%d/%m/%Y") if mItem.schedule_date else ' / / ', right_line)
                worksheet.write(row, col + 17, mItem.order.remark if mItem.order.remark else '', right_line)
                row = row + 1

            if i == order_item_list.__len__() - 1:
                cus_qty = cus_delivery_qty = cus_balance_qty = cus_loc_amount = 0

        company_name, current_period = get_company_name_and_current_period(company_id)

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
