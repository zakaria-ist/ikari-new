import datetime
import xlsxwriter
from companies.models import Company
from utilities.common import validate_date_to_from
from .print_SR8500 import get_all_list, get_all_qty


class Print_SR8500_XLS:

    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, delivery_from, delivery_to, part_no, location):
        return self.stock_balance(company_id, delivery_from, delivery_to, part_no, location)

    def stock_balance(self, company_id, delivery_from, delivery_to, part_no, location):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Stock Balance")

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

        company = Company.objects.get(pk=company_id)
        worksheet.merge_range('A3:D3', 'SR8500 Sales and Purchase System', merge_format)
        worksheet.merge_range('A4:D4', company.name, merge_format)
        worksheet.merge_range('A5:D5', "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'), merge_format)

        worksheet.write(10, 0, 'PART NO.', left_bold)
        worksheet.write(10, 1, 'ON HAND QTY', right_bold)
        worksheet.write(10, 2, 'OUTSTANDING S/O QTY', right_bold)
        worksheet.write(10, 3, 'OUTSTANDING P/O QTY', right_bold)
        worksheet.write(10, 4, 'BALANCE QTY', right_bold)

        for x in range(5):
            worksheet.set_column(x, x, 20)

        row = 11
        col = 0

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)

        part_list, so_order_item_list, po_order_item_list = get_all_list(company_id, location,
                                                                         part_no, delivery_from_obj, delivery_to_obj)

        on_hand_qty = so_qty = po_qty = balance_qty = 0
        grand_on_hand_qty = grand_so_qty = grand_po_qty = grand_balance_qty = 0

        for item in part_list:
            on_hand_qty, so_qty, po_qty, balance_qty = get_all_qty(on_hand_qty, so_qty,
                                                                   po_qty, balance_qty, item, so_order_item_list, po_order_item_list, location)

            if on_hand_qty == 0 and so_qty == 0 and po_qty == 0 and balance_qty == 0:
                pass
            else:
                worksheet.write(row, col, item['item__code'], left_line)
                worksheet.write(row, col + 1, on_hand_qty, dec_format)
                worksheet.write(row, col + 2, so_qty, dec_format)
                worksheet.write(row, col + 3, po_qty, dec_format)
                worksheet.write(row, col + 4, balance_qty, dec_format)
                row += 1

                grand_on_hand_qty += on_hand_qty
                grand_so_qty += so_qty
                grand_po_qty += po_qty
                grand_balance_qty += balance_qty

        # Actions after the for loop
        worksheet.write(row, col, 'Grand Total :', left_line)
        worksheet.write(row, col + 1, grand_on_hand_qty, dec_format)
        worksheet.write(row, col + 2, grand_so_qty, dec_format)
        worksheet.write(row, col + 3, grand_po_qty, dec_format)
        worksheet.write(row, col + 4, grand_balance_qty, dec_format)
        row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
