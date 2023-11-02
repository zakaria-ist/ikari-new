from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from items.models import Item, ItemCategory
from customers.models import CustomerItem
from suppliers.models import SupplierItem
from reports.numbered_page import NumberedPage
import datetime
from django.conf import settings as s
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from functools import partial

rowHeights = 14
colWidths = [115, 115, 160, 100, 160, 100, 60]


class Print_SL2201:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, part_list, group_list):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SL2201 Sales / Purchase System"
        row1_info2 = "Part Sales & Purchase File Listing"
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = ""
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4th row
        if len(part_list):
            row4_info1 = "Print Selection : [Part No.]"
        elif len(group_list):
            row4_info1 = "Print Selection : [Part Group]"
        else:
            row4_info1 = ""
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])
        # 5th row
        if len(part_list):
            item1 = Item.objects.get(pk=part_list[0]).code
            item2 = Item.objects.get(pk=part_list[-1]).code
            row5_info1 = "Part No.: [" + item1 + "][" + item2 + "]"
        elif len(group_list):
            item1 = ItemCategory.objects.get(pk=group_list[0]).code
            item2 = ItemCategory.objects.get(pk=group_list[-1]).code
            row5_info1 = "Part Group: [" + item1 + "][" + item2 + "]"
        else:
            row5_info1 = ""
        row5_info2 = ""
        header_data.append([row5_info1, row5_info2])

        header_table = Table(header_data, colWidths=[265, 273], rowHeights=rowHeights)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('FONTSIZE', (1, 0), (1, 0), 14),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_header = []
        table_header.append(['Part No.', 'Part Description', 'Supplier', 'Buying Price', 'Customer', 'Selling Price', 'Part Group'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 10, doc.height + doc.topMargin - h - h1 - 5)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, part_code, part_group, customer_no, supplier_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN,
                                leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN + 30,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []
        # Draw Content of PDF
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
        # if parts_list.count() > 7000:
        #     parts_list = parts_list[:7000]
        for mItem in parts_list.iterator():
            cust_item = cust_items.filter(item_id=mItem.id).first()
            supp_item = supp_items.filter(item_id=mItem.id).first()

            supp_curr = '   '
            supp_price = intcomma("%.5f" % 0)
            supplier = ''
            if supp_item:
                supp_curr = supp_item.currency.code
                supp_price = intcomma("%.5f" % supp_item.purchase_price)
                supplier = supp_item.supplier.code + ' / ' + supp_item.supplier.name

            cust_curr = '   '
            cust_price = intcomma("%.5f" % 0)
            customer = ''
            if cust_item:
                cust_curr = cust_item.currency.code
                cust_price = intcomma("%.5f" % cust_item.sales_price)
                customer = cust_item.customer.code + ' / ' + cust_item.customer.name

            table_data = []
            table_data.append([
                mItem.code[:21],
                mItem.short_description[:19] if mItem.short_description else '',
                supplier[0:26],
                supp_curr + '     ' + supp_price,
                customer[0:26],
                cust_curr + '     ' + cust_price,
                mItem.category.code[:12] if mItem.category else ''])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

        # Create the table
        if len(elements) == 0:
            table_data = []
            table_data.append(['', '', '', '', ''])
            item_table = Table(table_data, colWidths=[30, 65, 130, 155, 150], rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, part_list=part_list, group_list=group_list),
                  onLaterPages=partial(self._header_footer, company_id=company_id, part_list=part_list, group_list=group_list),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
