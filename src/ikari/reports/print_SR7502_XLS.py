from companies.models import Company
import xlsxwriter
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
import datetime
from django.db.models import Q
from utilities.common import round_number, get_decimal_place


class Print_SR7502_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, issue_from, issue_to, code):
        return self.gross_profit(company_id, issue_from, issue_to, code)

    def gross_profit(self, company_id, issue_from, issue_to, code):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("SR7502")

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

        # worksheet.merge_range('A3:D3', 'SR7502 Sales and Purchase System', merge_format)
        # worksheet.merge_range('A4:D4', company.name, merge_format)
        # worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)
        # worksheet.merge_range('A7:D7', "Current Period : [" + current_period.strftime("%B %Y") + "]" if issue_from is not '0' else '', merge_format)

        row = 0
        worksheet.write(row, 0, 'CLASS.', left_bold)
        worksheet.write(row, 1, 'PART NO.', left_bold)
        worksheet.write(row, 2, 'DOCUMENT_DATE', right_bold)
        worksheet.write(row, 3, 'CUSTOMER_PO', left_bold)
        worksheet.write(row, 4, 'QUANTITY', right_bold)
        worksheet.write(row, 5, 'ORIGINAL_AMOUNT', right_bold)
        worksheet.write(row, 6, 'LOCAL_AMOUNT', right_bold)
        for x in range(7):
            worksheet.set_column(x, x, 15)

        row += 1
        col = 0

        if issue_from is not '0' and issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__range=(issue_from, issue_to)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code', 'customer_po_no')
        elif issue_from is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__gte=(issue_from)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code', 'customer_po_no')
        elif issue_to is not '0':
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                                                          order__document_date__lte=(issue_to)
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code', 'customer_po_no')
        else:
            customer_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE']
                                                          ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by('item__code', 'customer_po_no')

        code_list = eval(code)
        if len(code_list):
            customer_item_list = customer_item_list.filter(item_id__in=code_list)

        m_code = ''
        cust_po_no = ''
        doc_date = ''
        part_quantity = part_amount = part_amount_loc = 0
        # decimal_place = "%.2f"
        is_decimal = True
        for i, mItem in enumerate(customer_item_list):
            if i == 0:
                m_code = mItem.item.code
                # decimal_place = get_decimal_place(mItem.order.currency)
                is_decimal = mItem.order.currency.is_decimal
            if m_code != mItem.item.code:
                worksheet.write(row, col, m_code[0:3], left_line)
                worksheet.write(row, col + 1, m_code, left_line)
                worksheet.write(row, col + 2, doc_date.strftime('%d/%m/%Y'), right_line)
                worksheet.write(row, col + 3, cust_po_no, left_line)
                worksheet.write(row, col + 4, part_quantity, dec_format)
                worksheet.write(row, col + 5, round_number(part_amount), dec_format if is_decimal else num_format)
                worksheet.write(row, col + 6, round_number(part_amount_loc), dec_format if is_decimal else num_format)
                row = row + 1
                part_quantity = part_amount = part_amount_loc = 0
                m_code = mItem.item.code
            if m_code == mItem.item.code:
                exchange_rate = mItem.order.exchange_rate if mItem.order else 1
                cust_po_no = mItem.customer_po_no
                doc_date = mItem.order.document_date
                part_quantity += mItem.quantity
                part_amount += mItem.amount
                part_amount_loc += round_number(mItem.amount * exchange_rate)

                # decimal_place = get_decimal_place(mItem.order.currency)
                is_decimal = mItem.order.currency.is_decimal

            if i == customer_item_list.__len__() - 1:
                # Print last row part No Total
                worksheet.write(row, col, m_code[0:3], left_line)
                worksheet.write(row, col + 1, m_code, left_line)
                worksheet.write(row, col + 2, doc_date.strftime('%d/%m/%Y'), right_line)
                worksheet.write(row, col + 3, cust_po_no, left_line)
                worksheet.write(row, col + 4, part_quantity, dec_format)
                worksheet.write(row, col + 5, round_number(part_amount), dec_format if is_decimal else num_format)
                worksheet.write(row, col + 6, round_number(part_amount_loc), dec_format if is_decimal else num_format)
                row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
