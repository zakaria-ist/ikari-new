from items.models import Item
from customers.models import CustomerItem
from companies.models import Company
import xlsxwriter


class Print_SL2200_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, part_code, part_group, customer_no):
        return self.item_price(company_id, part_code, part_group, customer_no)

    def item_price(self, company_id, part_code, part_group, customer_no):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Customer Item Price")

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

        price_format = workbook.add_format({'num_format': '#,##0.00000'})
        rate_format = workbook.add_format({'num_format': '#,##0.00000000'})

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
        worksheet.write(row, 12, 'CUST_NAME', left_bold)
        worksheet.write(row, 13, 'CUST_CURR', left_bold)
        for x in range(15):
            worksheet.set_column(x, x, 12)

        row += 1

        part_list = eval(part_code)
        group_list = eval(part_group)
        cust_items = CustomerItem.objects.filter(is_hidden=0, is_active=1, item__company_id=company_id)\
            .select_related('item', 'item__category', 'currency', 'customer')
        cust_list = eval(customer_no)
        if len(cust_list):
            cust_items = cust_items.filter(customer_id__in=cust_list)
        if len(part_list):
            cust_items = cust_items.filter(item_id__in=part_list)
        if len(group_list):
            cust_items = cust_items.filter(item__category_id__in=group_list)
        
        for mItem in cust_items.iterator():
            worksheet.write(row, 0, mItem.item.code, left_line)
            worksheet.write(row, 1, mItem.item.short_description if mItem.item.short_description else '', left_line)
            worksheet.write(row, 2, mItem.item.category.code if mItem.item.category else '', left_line)
            worksheet.write(row, 3, mItem.item.inv_measure.code if mItem.item.inv_measure else '', left_line)
            worksheet.write(row, 4, mItem.customer.code if mItem.customer else '', left_line)
            worksheet.write(row, 5, mItem.sales_price if mItem.sales_price else 0.00000, price_format)
            worksheet.write(row, 6, mItem.effective_date.strftime("%d/%m/%Y") if mItem.effective_date else ' / / ', left_line)
            worksheet.write(row, 7, mItem.new_price if mItem.new_price else 0.00000, price_format)
            worksheet.write(row, 8, mItem.leading_days if mItem.leading_days else '0', right_line)
            worksheet.write(row, 9, '', right_line)
            worksheet.write(row, 10, mItem.item.ratio if mItem.item.ratio else 1.00000000, rate_format)
            worksheet.write(row, 11, mItem.item.country.code if mItem.item.country else '', left_line)
            worksheet.write(row, 12, mItem.customer.name if mItem.customer.name else '', left_line)
            worksheet.write(row, 13, mItem.customer.currency.code if mItem.customer.currency
                            else mItem.item.sale_currency.code if mItem.item.sale_currency else '', left_line)
            row = row + 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
