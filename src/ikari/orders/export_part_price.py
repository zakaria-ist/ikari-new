from django.contrib.humanize.templatetags.humanize import intcomma
from companies.models import Company
import xlsxwriter
from suppliers.models import SupplierItem
from customers.models import CustomerItem
from utilities.common import round_number


class EXPORT_PURCHASE_PRICE_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, supplier_list, part_grp_list, part_no_list):
        return self.part_puchase_price(company_id,  supplier_list, part_grp_list, part_no_list)

    def part_puchase_price(self, company_id,  supplier_list, part_grp_list, part_no_list):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("PO Issue Report")

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

        row = 0
        worksheet.write(row, 0, 'SUPPLIER_CD', left_bold)
        worksheet.write(row, 1, 'SUPPLIER', left_bold)
        worksheet.write(row, 2, 'PAYTERM', right_bold)
        worksheet.write(row, 3, 'MODEL', left_bold)
        worksheet.write(row, 4, 'PART_NO', left_bold)
        worksheet.write(row, 5, 'PART_NAME', left_bold)
        worksheet.write(row, 6, 'QTY', left_bold)
        worksheet.write(row, 7, 'CURRENCY', left_bold)
        worksheet.write(row, 8, 'PURCHASE_PRICE', right_bold)
        worksheet.write(row, 9, 'EFFECTIVE_DATE', right_bold)
        worksheet.write(row, 10, 'NEW_PRICE', right_bold)

        for x in range(11):
            worksheet.set_column(x, x, 12)

        row += 1

        order_item_list = SupplierItem.objects.filter(is_hidden=0, is_active=1, supplier__company_id=company_id, supplier__is_hidden=0,
                                                      item__company_id=company_id, item__is_hidden=0) \
            .select_related('item', 'supplier')\
            .order_by('supplier__code')

        sp_list = eval(supplier_list)
        if len(sp_list):
            order_item_list = order_item_list.filter(supplier_id__in=sp_list)
        pt_list = eval(part_no_list)
        if len(pt_list):
            order_item_list = order_item_list.filter(item_id__in=pt_list)
        pg_list = eval(part_grp_list)
        if len(pg_list):
            order_item_list = order_item_list.filter(
                item__category_id__in=pg_list)

        for i, mItem in enumerate(order_item_list):
            worksheet.write(
                row, 0, mItem.supplier.code if mItem.supplier_id else '', left_line)
            worksheet.write(
                row, 1, mItem.supplier.name if mItem.supplier_id else '', left_line)
            worksheet.write(
                row, 2, mItem.supplier.term_days if mItem.supplier_id and mItem.supplier.term_days else '', right_line)
            worksheet.write(
                row, 3, mItem.item.category.code if mItem.item.category else '', left_line)
            worksheet.write(
                row, 4, mItem.item.code if mItem.item_id else '', left_line)
            worksheet.write(
                row, 5, mItem.item.short_description if mItem.item.short_description else '', left_line)
            worksheet.write(
                row, 6, mItem.quantity if mItem.quantity else '0', right_line)
            worksheet.write(
                row, 7, mItem.supplier.currency.code if mItem.supplier_id and mItem.supplier.currency else '', left_line)
            worksheet.write(row, 8, intcomma("%.5f" % round_number(
                mItem.purchase_price, 5)) if mItem.purchase_price else '', right_line)
            worksheet.write(row, 9, mItem.effective_date.strftime(
                "%Y-%m-%d") if mItem.effective_date else '//', right_line)
            worksheet.write(row, 10, intcomma("%.5f" % round_number(
                mItem.new_price, 5)) if mItem.new_price else '', right_line)
            row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data


class EXPORT_SALE_PRICE_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, customer_list, part_grp_list, part_no_list, include_supp):
        return self.part_sale_price(company_id,  customer_list, part_grp_list, part_no_list, include_supp)

    def part_sale_price(self, company_id,  customer_list, part_grp_list, part_no_list, include_supp):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Part Sales Price")

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

        include_supp = int(include_supp)

        row = 0
        worksheet.write(row, 0, 'CUSTOMER_CD', left_bold)
        worksheet.write(row, 1, 'CUSTOMER', left_bold)
        worksheet.write(row, 2, 'PAYTERM', right_bold)
        worksheet.write(row, 3, 'MODEL', left_bold)
        worksheet.write(row, 4, 'PART_NO', left_bold)
        worksheet.write(row, 5, 'PART_NAME', left_bold)
        worksheet.write(row, 6, 'QTY', left_bold)
        worksheet.write(row, 7, 'CURRENCY', left_bold)
        worksheet.write(row, 8, 'SALES_PRICE', right_bold)
        worksheet.write(row, 9, 'EFFECTIVE_DATE', right_bold)
        worksheet.write(row, 10, 'NEW_PRICE', right_bold)
        if include_supp:
            worksheet.write(row, 11, 'SUPPLIER_CD', left_bold)
            worksheet.write(row, 12, 'PURCHASE_PRICE', right_bold)

        for x in range(13):
            worksheet.set_column(x, x, 12)

        row += 1

        order_item_list = CustomerItem.objects.filter(is_hidden=0, is_active=1, customer__company_id=company_id, customer__is_hidden=0,
                                                      item__company_id=company_id, item__is_hidden=0) \
            .select_related('item', 'customer')\
            .order_by('customer__code')

        sp_list = eval(customer_list)
        if len(sp_list):
            order_item_list = order_item_list.filter(customer_id__in=sp_list)
        pt_list = eval(part_no_list)
        if len(pt_list):
            order_item_list = order_item_list.filter(item_id__in=pt_list)
        pg_list = eval(part_grp_list)
        if len(pg_list):
            order_item_list = order_item_list.filter(
                item__category_id__in=pg_list)

        item_ids = order_item_list.values_list('item_id', flat=True)

        if include_supp:
            supp_item_list = SupplierItem.objects.filter(item_id__in=item_ids) \
                .select_related('supplier')\
                .order_by('supplier__code')
        else:
            supp_item_list = SupplierItem.objects.none()

        for i, mItem in enumerate(order_item_list):
            worksheet.write(
                row, 0, mItem.customer.code if mItem.customer else '', left_line)
            worksheet.write(
                row, 1, mItem.customer.name if mItem.customer else '', left_line)
            worksheet.write(
                row, 2, mItem.customer.payment_term if mItem.customer and mItem.customer.payment_term else '', right_line)
            worksheet.write(
                row, 3, mItem.item.category.code if mItem.item.category else '', left_line)
            worksheet.write(
                row, 4, mItem.item.code if mItem.item_id else '', left_line)
            worksheet.write(
                row, 5, mItem.item.short_description if mItem.item.short_description else '', left_line)
            worksheet.write(row, 6, '0', right_line)
            worksheet.write(
                row, 7, mItem.customer.currency.code if mItem.customer and mItem.customer.currency else '', left_line)
            worksheet.write(row, 8, intcomma("%.5f" % round_number(
                mItem.sales_price, 5)) if mItem.sales_price else '', right_line)
            worksheet.write(row, 9, mItem.effective_date.strftime(
                "%Y-%m-%d") if mItem.effective_date else '//', right_line)
            worksheet.write(row, 10, intcomma("%.5f" % round_number(
                mItem.new_price, 5)) if mItem.new_price else '', right_line)
            if include_supp:
                supp_item = supp_item_list.filter(
                    item_id=mItem.item.id).first()
                if supp_item:
                    worksheet.write(
                        row, 11, supp_item.supplier.code if supp_item.supplier else '', left_line)
                    worksheet.write(row, 12, intcomma("%.5f" % round_number(
                        supp_item.purchase_price, 5)) if supp_item.purchase_price else '', right_line)
            row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
