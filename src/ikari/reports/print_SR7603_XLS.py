import xlsxwriter
from orders.models import OrderItem
from utilities.constants import ORDER_STATUS, ORDER_TYPE
from django.db.models import Q


class Print_SR7603_XLS:
    def __init__(self, buffer):
        self.buffer = buffer

    def WriteToExcel(self, company_id, issue_from, issue_to, wanted_from, wanted_to, customer_code, document_no, customer_po, part_no, sort_by):
        return self.so_issue_report(company_id, issue_from, issue_to, wanted_from, wanted_to, customer_code, document_no, customer_po, part_no, sort_by)

    def so_issue_report(self, company_id, issue_from, issue_to, wanted_from, wanted_to, customer_code, document_no, customer_po, part_no, sort_by):
        output = self.buffer
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("SO Issue Report")

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

        # company = Company.objects.filter(id=company_id).last()

        row = 0
        worksheet.write(row, 0, 'SSOH_CUSCD', left_bold)
        worksheet.write(row, 1, 'MCUS_CUSNM', left_bold)
        worksheet.write(row, 2, 'MCUS_CUSCR', left_bold)
        worksheet.write(row, 3, 'SSOH_TRNCD', left_bold)
        worksheet.write(row, 4, 'SSOH_DOCNO', left_bold)
        worksheet.write(row, 5, 'SSOH_DOCDT', right_bold)
        worksheet.write(row, 6, 'SSOD_PARTNO', left_bold)
        worksheet.write(row, 7, 'MPTH_IDESC', left_bold)
        worksheet.write(row, 8, 'SSOD_WANTD', right_bold)
        worksheet.write(row, 9, 'SSOD_CUSTPO', left_bold)
        worksheet.write(row, 10, 'SSOD_LINE', right_bold)
        worksheet.write(row, 11, 'SSOH_XRATE', right_bold)
        worksheet.write(row, 12, 'SSOD_QTY', right_bold)
        worksheet.write(row, 13, 'SSOD_UPRICE', right_bold)

        for x in range(14):
            worksheet.set_column(x, x, 12)

        row += 1

        order_by = "order__customer__code"
        if sort_by == 'customer':
            order_by = "order__customer__code"
        elif sort_by == 'document':
            order_by = "order__document_number"
        elif sort_by == 'customer_po':
            order_by = "customer_po_no"
        elif sort_by == 'part_no':
            order_by = "item__code"
        elif sort_by == 'wanted_date':
            order_by = "wanted_date"
        # get delivery date
        if issue_from is not '0' and issue_to is not '0':
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                       order__document_date__range=(issue_from, issue_to)
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)
        elif issue_from is not '0':
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                       order__document_date__gte=(issue_from)
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)
        elif issue_to is not '0':
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                                                       order__document_date__lte=(issue_to)
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)
        else:
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__order_type=dict(ORDER_TYPE)['SALES ORDER']
                                                       ) \
                .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
                .order_by(order_by)

        if wanted_from is not '0' and wanted_to is not '0':
            order_item_list = order_item_list.filter(wanted_date__range=(wanted_from, wanted_to))
        if wanted_from is not '0':
            order_item_list = order_item_list.filter(wanted_date__gte=wanted_from)
        if wanted_to is not '0':
            order_item_list = order_item_list.filter(wanted_date__lte=wanted_to)

        cust_list = eval(customer_code)
        if len(cust_list):
            order_item_list = order_item_list.filter(order__customer_id__in=cust_list)
        doc_list = eval(document_no)
        if len(doc_list):
            order_item_list = order_item_list.filter(order_id__in=doc_list)
        pt_list = eval(part_no)
        if len(pt_list):
            order_item_list = order_item_list.filter(item_id__in=pt_list)
        po_list = eval(customer_po)
        if len(po_list):
            order_item_list = order_item_list.filter(id__in=po_list)

        for i, mItem in enumerate(order_item_list):
            worksheet.write(row, 0, mItem.order.customer.code if mItem.order.customer_id else '', left_line)
            worksheet.write(row, 1, mItem.order.customer.name if mItem.order.customer_id else '', left_line)
            worksheet.write(row, 2, mItem.order.currency.code if mItem.order.currency_id else '', left_line)
            worksheet.write(row, 3, 'S/O', left_line)
            worksheet.write(row, 4, mItem.order.document_number, left_line)
            worksheet.write(row, 5, mItem.order.document_date.strftime("%d/%m/%Y") if mItem.order.document_date else ' / / ', right_line)
            worksheet.write(row, 6, mItem.item.code if mItem.item_id else '', left_line)
            worksheet.write(row, 7, mItem.item.short_description if mItem.item.short_description else '', left_line)
            worksheet.write(row, 8, mItem.wanted_date.strftime("%d/%m/%Y") if mItem.wanted_date else ' / / ', right_line)
            worksheet.write(row, 9, mItem.customer_po_no, left_line)
            worksheet.write(row, 10, str(mItem.line_number), right_line)
            worksheet.write(row, 11, mItem.order.exchange_rate, rate_format)
            worksheet.write(row, 12, mItem.quantity if mItem.quantity else 0.00, dec_format)
            worksheet.write(row, 13, mItem.price if mItem.price else 0.00000, price_format)
            row += 1

        workbook.close()
        xlsx_data = output.getvalue()
        return xlsx_data
