from orders.models import OrderItem
from companies.models import Company
import xlsxwriter
from django.db.models import Q, F, Value as V
from django.db.models.functions import Coalesce
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from decimal import Decimal
from utilities.common import validate_date_to_from, round_number


class Print_SR7202_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, delivery_from, delivery_to, supplier_no):
        return self.outstanding_po_balance(company_id, delivery_from, delivery_to, supplier_no)

    def outstanding_po_balance(self, company_id, delivery_from, delivery_to, supplier_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("PO Balance by Supp")

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
        worksheet.write(row, 9, 'PPOD_WANTD', right_bold)
        worksheet.write(row, 10, 'PPOD_LRCDT', right_bold)
        worksheet.write(row, 11, 'PPOD_REFNO', right_bold)
        worksheet.write(row, 12, 'PPOD_REFLN', right_bold)
        worksheet.write(row, 13, 'PPOD_UPRICE', right_bold)
        worksheet.write(row, 14, 'PPOD_QTY', right_bold)
        worksheet.write(row, 15, 'PPOD_RCQTY', right_bold)
        worksheet.write(row, 16, 'PPOD_BLNCQTY', right_bold)
        worksheet.write(row, 17, 'PPOD_CUSTPO', left_bold)
        worksheet.write(row, 18, 'MPTH_GROUP', left_bold)
        worksheet.write(row, 19, 'PPOD_SCHDT', right_bold)
        worksheet.write(row, 20, 'PPOD_REM', right_bold)
        for x in range(21):
            worksheet.set_column(x, x, 12)

        row += 1
        col = 0
        exchange_rate = 0

        order_item_list = OrderItem.objects.select_related('order').select_related('item').filter(
            is_hidden=0, order__is_hidden=0, order__company_id=company_id,
            order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
            .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
            .exclude(quantity=F('receive_quantity')) \
            .annotate(balance_qty=Coalesce(F('quantity'), V(0)) - Coalesce(F('receive_quantity'), V(0))) \
            .order_by('supplier__code', 'order__document_number', 'line_number')

        order_item_list = order_item_list.filter(wanted_date__range=(delivery_from_obj.strftime('%Y-%m-%d'),
                                                                     delivery_to_obj.strftime('%Y-%m-%d')))

        supp_list = eval(supplier_no)
        if len(supp_list):
            order_item_list = order_item_list.filter(order__supplier_id__in=supp_list)

        m_supplier_no = ''
        m_document_no = ''
        doc_qty = doc_receive_qty = doc_balance_qty = 0  # sum qty of each Order
        sup_qty = sup_receive_qty = sup_balance_qty = 0  # sum qty of each supplier
        grand_qty = grand_receive_qty = grand_balance_qty = 0  # total sum
        doc_org_amount = doc_loc_amount = 0
        sup_org_amount = sup_loc_amount = gt_loc = 0

        for i, mItem in enumerate(order_item_list):
            if float(mItem.balance_qty) > 0:
                grand_qty += float(mItem.quantity) if mItem.quantity else 0
                grand_receive_qty += float(mItem.receive_quantity) if mItem.receive_quantity else 0
                grand_balance_qty += float(mItem.balance_qty)

            # check to print first row of supplier
            if m_supplier_no != mItem.supplier.code and float(mItem.balance_qty) > 0:
                # Start new Customer PO Total
                sup_qty = sup_receive_qty = sup_balance_qty = 0
                sup_org_amount = sup_loc_amount = 0
                m_supplier_no = mItem.supplier.code

            # check to print first row of Order
            if m_document_no != mItem.order.document_number and float(mItem.balance_qty) > 0:
                m_document_no = mItem.order.document_number
                doc_qty = doc_receive_qty = doc_balance_qty = 0
                doc_org_amount = doc_loc_amount = 0
                exchange_rate = Decimal(mItem.order.exchange_rate) if mItem.order.exchange_rate else 1

            # check to print next row of Order
            if m_supplier_no == mItem.supplier.code \
                    and m_document_no == mItem.order.document_number \
                    and float(mItem.balance_qty) > 0:
                item_price = mItem.price if mItem.price else 0
                item_quantity = float(mItem.quantity) if mItem.quantity else 0
                receive_quantity = float(mItem.receive_quantity) if mItem.receive_quantity else 0

                doc_qty += item_quantity
                doc_receive_qty += receive_quantity
                doc_balance_qty += float(mItem.balance_qty)

                doc_org_amount += round_number(mItem.balance_qty * item_price)
                doc_loc_amount += round_number(mItem.balance_qty * item_price * exchange_rate)
                gt_loc += round_number(mItem.balance_qty * item_price * exchange_rate)

                sup_qty += item_quantity
                sup_receive_qty += receive_quantity
                sup_balance_qty += float(mItem.balance_qty)

                sup_org_amount += round_number(mItem.balance_qty * item_price)
                sup_loc_amount += round_number(mItem.balance_qty * item_price * exchange_rate)

                worksheet.write(row, col, mItem.order.supplier.code, left_line)
                worksheet.write(row, col + 1, 'P/O', left_line)
                worksheet.write(row, col + 2, mItem.order.document_number if mItem.order.document_number else '', left_line)
                worksheet.write(row, col + 3, mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ', right_line)
                worksheet.write(row, col + 4, exchange_rate, rate_format)
                worksheet.write(row, col + 5, mItem.order.transport_responsibility if mItem.order.transport_responsibility else '', left_bold)
                worksheet.write(row, col + 6, mItem.order.via if mItem.order.via else '', left_bold)
                worksheet.write(row, col + 7, str(mItem.line_number), right_line)
                worksheet.write(row, col + 8, mItem.item.code if mItem.item.code else '', left_line)
                worksheet.write(row, col + 9, mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ', right_line)
                worksheet.write(row, col + 10, mItem.last_receive_date.strftime("%d/%m/%Y") if mItem.last_receive_date else ' / / ', right_line)
                worksheet.write(row, col + 11, str(mItem.refer_number), right_line)
                worksheet.write(row, col + 12, str(mItem.refer_line), right_line)
                worksheet.write(row, col + 13, item_price, price_format)
                worksheet.write(row, col + 14, item_quantity, dec_format)
                worksheet.write(row, col + 15, receive_quantity, dec_format)
                worksheet.write(row, col + 16, mItem.balance_qty, dec_format)
                worksheet.write(row, col + 17, mItem.customer_po_no, left_line)
                worksheet.write(row, col + 18, mItem.item.category.code if mItem.item.category else '', left_line)
                worksheet.write(row, col + 19, mItem.schedule_date.strftime("%d/%m/%Y") if mItem.schedule_date else ' / / ', right_line)
                worksheet.write(row, col + 20, mItem.order.remark if mItem.order.remark else '', right_line)
                row = row + 1

            if i + 1 < order_item_list.__len__():
                if m_document_no == mItem.order.document_number and float(mItem.balance_qty) > 0 and \
                        order_item_list[i + 1].order.document_number != mItem.order.document_number:
                    doc_qty = doc_receive_qty = doc_balance_qty = 0

                if order_item_list[i + 1].supplier.code != mItem.supplier.code and float(sup_balance_qty) > 0:
                    sup_qty = sup_receive_qty = sup_balance_qty = 0

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
