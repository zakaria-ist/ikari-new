from items.models import Item
from suppliers.models import SupplierItem
from companies.models import Company
import xlsxwriter


class Print_SL2100_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, part_code, part_group, supplier_no):
        return self.item_price(company_id, part_code, part_group, supplier_no)

    def item_price(self, company_id, part_code, part_group, supplier_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Supplier Item Price")

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

        num_format = workbook.add_format({'num_format': '#,##0'})
        price_format = workbook.add_format({'num_format': '#,##0.00000'})

        # company = Company.objects.filter(id=company_id).last()

        row = 0
        worksheet.write(row, 0, 'PART_NO', left_bold)
        worksheet.write(row, 1, 'PART_DESC', left_bold)
        worksheet.write(row, 2, 'PART_GROUP.', left_bold)
        worksheet.write(row, 3, 'UOM', left_bold)
        worksheet.write(row, 4, 'SUPP_CODE', left_bold)
        worksheet.write(row, 5, 'SUPP_NAME', left_bold)
        worksheet.write(row, 6, 'SUPP_CURR', left_bold)
        worksheet.write(row, 7, 'BUY_PRICE', right_bold)
        worksheet.write(row, 8, 'BUY_EFFDT', left_bold)
        worksheet.write(row, 9, 'BUY_NEWPR', right_bold)
        worksheet.write(row, 10, 'LEADTIME', right_bold)
        worksheet.write(row, 11, 'PRITY', right_bold)
        worksheet.write(row, 12, 'RATIO', right_bold)
        worksheet.write(row, 13, 'COUNTRY', left_bold)
        worksheet.write(row, 14, 'GROUP_NAME', left_bold)
        for x in range(15):
            worksheet.set_column(x, x, 12)

        row += 1

        supp_items = SupplierItem.objects.filter(is_hidden=0, is_active=1, item__company_id=company_id)\
            .select_related('item', 'item__category', 'currency', 'supplier').order_by('item__code')\
            .exclude(item_id__isnull=True)
        
        part_list = eval(part_code)
        group_list = eval(part_group)
        supp_list = eval(supplier_no)
        if len(supp_list):
            supp_items = supp_items.filter(supplier_id__in=supp_list)
        if len(part_list):
            supp_items = supp_items.filter(item_id__in=part_list)
        if len(group_list):
            supp_items = supp_items.filter(item__category_id__in=group_list)
        for mItem in supp_items.iterator():
            worksheet.write(row, 0, mItem.item.code, left_line)
            worksheet.write(row, 1, mItem.item.short_description if mItem.item.short_description else '', left_line)
            worksheet.write(row, 2, mItem.item.category.code if mItem.item.category else '', left_line)
            worksheet.write(row, 3, mItem.item.purchase_measure.code if mItem.item.purchase_measure else '', left_line)
            worksheet.write(row, 4, mItem.supplier.code if mItem.supplier else '', left_line)
            worksheet.write(row, 5, mItem.supplier.name if mItem.supplier.name else '', left_line)
            worksheet.write(row, 6, mItem.supplier.currency.code if mItem.supplier.currency
                            else mItem.item.purchase_currency.code if mItem.item.purchase_currency else '', left_line)
            worksheet.write(row, 7, mItem.purchase_price if mItem.purchase_price else 0.00000, price_format)
            worksheet.write(row, 8, mItem.effective_date.strftime("%d/%m/%Y") if mItem.effective_date else ' / / ', left_line)
            worksheet.write(row, 9, mItem.new_price if mItem.new_price else 0.00000, price_format)
            worksheet.write(row, 10, mItem.leading_days if mItem.leading_days else '0', right_line)
            worksheet.write(row, 11, '', right_line)
            worksheet.write(row, 12, mItem.item.ratio if mItem.item.ratio else 1, num_format)
            worksheet.write(row, 13, mItem.item.country.code if mItem.item.country else '', left_line)
            worksheet.write(row, 14, mItem.item.category.name if mItem.item.category else '', left_line)
            row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
