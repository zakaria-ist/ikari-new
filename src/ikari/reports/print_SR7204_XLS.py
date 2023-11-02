import xlsxwriter
from orders.models import OrderItem
from django.db.models import Q, F, Value as V
from django.db.models.functions import Coalesce
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from decimal import Decimal
from utilities.common import validate_date_to_from, get_company_name_and_current_period


class Print_SR7204_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, delivery_from, delivery_to, supplier_no, part_no):
        return self.outstanding_po_balance(company_id, delivery_from, delivery_to, supplier_no, part_no)

    def outstanding_po_balance(self, company_id, delivery_from, delivery_to, supplier_no, part_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("PO Balance by Part No")

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
        worksheet.write(row, 0, 'PPOH_SUPCD.', left_bold)
        worksheet.write(row, 1, 'PPOH_TRNCD', left_bold)
        worksheet.write(row, 2, 'PPOH_DOCNO', left_bold)
        worksheet.write(row, 3, 'PPOH_DOCDT', left_bold)
        worksheet.write(row, 4, 'PPOH_XRATE', left_bold)
        worksheet.write(row, 5, 'PPOH_TRESP', left_bold)
        worksheet.write(row, 6, 'PPOH_SPVIA', left_bold)
        worksheet.write(row, 7, 'PPOD_LINE', right_bold)
        worksheet.write(row, 8, 'PPOD_PARTNO', right_bold)
        worksheet.write(row, 9, 'PPOD_PART_DESC', right_bold)
        worksheet.write(row, 10, 'PPOD_WANTD', right_bold)
        worksheet.write(row, 11, 'PPOD_LRCDT', right_bold)
        worksheet.write(row, 12, 'PPOD_REFNO', right_bold)
        worksheet.write(row, 13, 'PPOD_REFLN', right_bold)
        worksheet.write(row, 14, 'PPOD_UPRICE', right_bold)
        worksheet.write(row, 15, 'PPOD_QTY', right_bold)
        worksheet.write(row, 16, 'PPOD_RCQTY', right_bold)
        worksheet.write(row, 17, 'PPOD_BLNCQTY', right_bold)
        worksheet.write(row, 18, 'PPOD_CUSTPO', left_bold)
        worksheet.write(row, 19, 'SUP_CUR', left_bold)
        worksheet.write(row, 20, 'PPOD_SCHDT', right_bold)
        for x in range(21):
            worksheet.set_column(x, x, 12)

        row += 1
        col = 0

        order_item_list = OrderItem.objects.select_related('order').select_related('item').filter(
            is_hidden=0, order__is_hidden=0, order__company_id=company_id,
            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('receive_quantity')) \
            .annotate(balance_qty=Coalesce(F('quantity'), V(0)) - Coalesce(F('receive_quantity'), V(0))) \
            .order_by('item__code', 'wanted_date', 'line_number')

        order_item_list = order_item_list.filter(wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                     delivery_to_obj.strftime('%Y-%m-%d')))

        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(supplier_id__in=supp_list)

        part_list = eval(part_no)
        if len(part_list):
            order_item_list = order_item_list.filter(item__id__in=part_list)

        m_item_code = ''
        acc_qty = acc_receive_qty = acc_balance_qty = 0  # sum qty of each part
        grand_total_qty = grand_total_receive_qty = grand_total_balance_qty = 0

        for i, mItem in enumerate(order_item_list):
            if m_item_code != mItem.item.code and float(mItem.balance_qty) > 0:
                m_item_code = mItem.item.code
                acc_qty = acc_receive_qty = acc_balance_qty = 0  # sum qty of each part
                exchange_rate = Decimal(mItem.order.exchange_rate) if mItem.order.exchange_rate else 1

            #   check on next row data
            if m_item_code == mItem.item.code and mItem.order and float(mItem.balance_qty) > 0:
                item_price = mItem.price if mItem.price else 0
                item_quantity = float(mItem.quantity) if mItem.quantity else 0
                receive_quantity = float(mItem.receive_quantity) if mItem.receive_quantity else 0
                grand_total_qty += item_quantity
                grand_total_receive_qty += receive_quantity
                grand_total_balance_qty += float(mItem.balance_qty)
                acc_qty += item_quantity
                acc_receive_qty += receive_quantity
                acc_balance_qty += float(mItem.balance_qty)

                worksheet.write(row, col, mItem.order.supplier.code, left_line)
                worksheet.write(row, col + 1, 'P/O', left_line)
                worksheet.write(row, col + 2, mItem.order.document_number if mItem.order.document_number else '', left_line)
                worksheet.write(row, col + 3, mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ', right_line)
                worksheet.write(row, col + 4, exchange_rate, rate_format)
                worksheet.write(row, col + 5, mItem.order.transport_responsibility if mItem.order.transport_responsibility else '', left_bold)
                worksheet.write(row, col + 6, mItem.order.via if mItem.order.via else '', left_bold)
                worksheet.write(row, col + 7, str(mItem.line_number), right_line)
                worksheet.write(row, col + 8, mItem.item.code if mItem.item.code else '', left_line)
                worksheet.write(row, col + 9, mItem.item.short_description if mItem.item.short_description else '', left_line)
                worksheet.write(row, col + 10, mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ', right_line)
                worksheet.write(row, col + 11, mItem.last_receive_date.strftime("%d/%m/%Y") if mItem.last_receive_date else ' / / ', right_line)
                worksheet.write(row, col + 12, str(mItem.refer_number), right_line)
                worksheet.write(row, col + 13, str(mItem.refer_line), right_line)
                worksheet.write(row, col + 14, item_price, price_format)
                worksheet.write(row, col + 15, item_quantity, dec_format)
                worksheet.write(row, col + 16, receive_quantity, dec_format)
                worksheet.write(row, col + 17, mItem.balance_qty, dec_format)
                worksheet.write(row, col + 18, mItem.customer_po_no, left_line)
                worksheet.write(row, col + 19, mItem.order.supplier.currency.code, left_line)
                worksheet.write(row, col + 20, mItem.schedule_date.strftime("%d/%m/%Y") if mItem.schedule_date else ' / / ', right_line)
                row = row + 1

        if not float(acc_balance_qty) == 0:
            acc_qty = acc_receive_qty = acc_balance_qty = 0

        company_name, current_period = get_company_name_and_current_period(company_id)

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
