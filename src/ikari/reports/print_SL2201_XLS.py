from items.models import Item
from customers.models import CustomerItem
from suppliers.models import SupplierItem
import xlsxwriter


class Print_SL2201_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, part_code, part_group, customer_no, supplier_no):
        return self.item_price(company_id, part_code, part_group, customer_no, supplier_no)

    def item_price(self, company_id, part_code, part_group, customer_no, supplier_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Item Price")

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
        worksheet.write(row, 4, 'CUST_CODE', left_bold)
        worksheet.write(row, 5, 'SELL_PRICE', right_bold)
        worksheet.write(row, 6, 'SELL_EFFDT', left_bold)
        worksheet.write(row, 7, 'SELL_NEWPR', right_bold)
        worksheet.write(row, 8, 'LEADTIME', right_bold)
        worksheet.write(row, 9, 'PRITY', right_bold)
        worksheet.write(row, 10, 'RATIO', right_bold)
        worksheet.write(row, 11, 'COUNTRY', left_bold)
        worksheet.write(row, 12, 'GROUP_NAME', left_bold)
        worksheet.write(row, 13, 'CUST_NAME', left_bold)
        worksheet.write(row, 14, 'CUST_CURR', left_bold)
        worksheet.write(row, 15, 'SUPP_CODE', left_bold)
        worksheet.write(row, 16, 'SUPP_NAME', left_bold)
        worksheet.write(row, 17, 'SUPP_CURR', left_bold)
        worksheet.write(row, 18, 'BUY_PRICE', right_bold)
        worksheet.write(row, 19, 'BUY_EFFDT', left_bold)
        worksheet.write(row, 20, 'BUY_NEWPR', right_bold)
        for x in range(21):
            worksheet.set_column(x, x, 12)

        row += 1

        parts_list = Item.objects.filter(is_hidden=0, company_id=company_id, is_active=1)\
                        .select_related('sales_measure', 'inv_measure', 'report_measure', 'sale_currency')\
                        .select_related('category', 'purchase_measure', 'purchase_currency', 'country')\
                        .order_by('code')

        part_list = eval(part_code)
        if len(part_list):
            parts_list = parts_list.filter(id__in=part_list)
        group_list = eval(part_group)
        if len(group_list):
            parts_list = parts_list.filter(category_id__in=group_list)

        item_ids = parts_list.values_list('id', flat=True)
        cust_items = CustomerItem.objects.filter(is_hidden=0, is_active=1, item_id__in=item_ids)\
                        .select_related('item', 'currency', 'customer')
        cust_list = eval(customer_no)
        if len(cust_list):
            cust_items = cust_items.filter(customer_id__in=cust_list)
        cust_ids = cust_items.values_list('item_id', flat=True)
        supp_items = SupplierItem.objects.filter(is_hidden=0, is_active=1, item_id__in=item_ids)\
                        .select_related('item', 'currency', 'supplier')
        supp_list = eval(supplier_no)
        if len(supp_list):
            supp_items = supp_items.filter(supplier_id__in=supp_list)
        supp_ids = supp_items.values_list('item_id', flat=True)
        parts_list = parts_list.filter(id__in=cust_ids)
        parts_list = parts_list.filter(id__in=supp_ids)
        for mItem in parts_list.iterator():
            cust_item = cust_items.filter(item_id=mItem.id).first()
            supp_item = supp_items.filter(item_id=mItem.id).first()

            worksheet.write(row, 0, mItem.code, left_line)
            worksheet.write(row, 1, mItem.short_description if mItem.short_description else '', left_line)
            worksheet.write(row, 2, mItem.category.code if mItem.category else '', left_line)
            worksheet.write(row, 3, mItem.inv_measure.code if mItem.inv_measure else '', left_line)
            worksheet.write(row, 4, cust_item.customer.code if cust_item else '', left_line)
            worksheet.write(row, 5, cust_item.sales_price if cust_item and cust_item.sales_price else 0.00000, price_format)
            worksheet.write(row, 6, cust_item.effective_date.strftime("%d/%m/%Y") if cust_item and cust_item.effective_date else ' / / ', left_line)
            worksheet.write(row, 7, cust_item.new_price if cust_item and cust_item.new_price else 0.00000, price_format)
            worksheet.write(row, 8, cust_item.leading_days if cust_item else '0', right_line)
            worksheet.write(row, 9, '', right_line)
            worksheet.write(row, 10, float(mItem.ratio) if mItem.ratio else 1, num_format)
            worksheet.write(row, 11, mItem.country.code if mItem.country else '', left_line)
            worksheet.write(row, 12, mItem.category.name if mItem.category else '', left_line)
            worksheet.write(row, 13, cust_item.customer.name if cust_item else '', left_line)
            worksheet.write(row, 14, cust_item.customer.currency.code if cust_item and cust_item.customer.currency
                        else mItem.sale_currency.code if mItem.sale_currency else '', left_line)
            worksheet.write(row, 15, supp_item.supplier.code if supp_item else '', left_line)
            worksheet.write(row, 16, supp_item.supplier.name if supp_item else '', left_line)
            worksheet.write(row, 17, supp_item.supplier.currency.code if supp_item and supp_item.supplier.currency
                        else mItem.purchase_currency.code if mItem.purchase_currency else '', left_line)
            worksheet.write(row, 18, supp_item.purchase_price if supp_item and supp_item.purchase_price else 0.00000, price_format)
            worksheet.write(row, 19, supp_item.effective_date.strftime("%d/%m/%Y") if supp_item and supp_item.effective_date else ' / / ', left_line)
            worksheet.write(row, 20, supp_item.new_price if supp_item and supp_item.new_price else 0.00000, price_format)
            row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
