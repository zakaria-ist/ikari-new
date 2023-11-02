from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from items.models import Item, ItemCategory
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
colWidths = [110, 135, 30, 60, 50, 65, 40, 60]


class Print_SL2100:
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
        row1_info1 = "SL2100 Sales / Purchase System"
        row1_info2 = "Part Purchase File Listing"
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Grouped by Part No."
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
        table_header.append(['Part No.', 'Description', '', 'Part Group', 'Std Curr', 'Std Price', 'M\'Ment', 'Last Updated'])
        table_header.append(['Country Origin', 'Short Description', '', '', 'Min Order Qty', '', '', ''])
        table_header.append(['Supp. Code & Name', '', 'Curr', 'Effect Date', 'New Price', 'Purch. Price', 'Lead', 'Date Updated'])

        item_header_table = Table(table_header, colWidths=colWidths, rowHeights=rowHeights)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 2), (-1, 2), 0.25, colors.black),
             ('ALIGN', (0, 1), (0, 1), 'CENTER'),
             ('ALIGN', (0, 2), (0, 2), 'CENTER'),
             ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - h1 + 25)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, part_code, part_group, supplier_no):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=130, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []
        table_data = []

        # Draw Content of PDF
        # parts_list = Item.objects.filter(is_hidden=0, company_id=company_id, is_active=1)\
        #     .select_related('category', 'purchase_measure', 'purchase_currency', 'country')\
        #     .order_by('code')

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
        # if supp_items.count() > 7000:
        #     supp_items = supp_items[:7000]
        for mItem in supp_items.iterator():
            table_data = []
            table_data.append([
                mItem.item.code, mItem.item.name[:40] if mItem.item.name else '', '', 
                mItem.item.category.code if mItem.item.category else '',
                mItem.currency.code if mItem.currency else mItem.item.purchase_currency.code if mItem.item.purchase_currency else '',
                intcomma("%.5f" % mItem.item.purchase_price), mItem.item.purchase_measure.code if mItem.item.purchase_measure else '',
                mItem.item.update_date.strftime("%d/%m/%Y") if mItem.item.update_date else ' / / '])
            table_data.append([mItem.item.country.code if mItem.item.country else '', mItem.item.short_description if mItem.item.short_description else '',
                             '', '', mItem.item.minimun_order if mItem.item.minimun_order else 0.00, '', '', ''])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
                 ('ALIGN', (0, 1), (0, 1), 'CENTER'),
                 ('ALIGN', (4, 0), (7, 0), 'RIGHT'),
                 ('ALIGN', (4, 1), (7, 1), 'RIGHT'),
                 ('TOPPADDING', (0, 0), (7, 0), 10),
                 ('LEFTPADDING', (0, 0), (-1, -1), 0),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

            # if supp_item:
            table_data = []
            table_data.append([
                mItem.supplier.code + '    ' + mItem.supplier.name if mItem.supplier.name else '', 
                '', mItem.currency.code if mItem.currency else '',
                mItem.effective_date.strftime("%d/%m/%Y") if mItem.effective_date else ' / / ',
                intcomma("%.5f" % mItem.new_price if mItem.new_price else 0.00000),
                intcomma("%.5f" % mItem.purchase_price if mItem.purchase_price else 0.00000),
                mItem.leading_days if mItem.leading_days else '0', mItem.update_date.strftime("%d/%m/%Y") if mItem.update_date else ' / / '])

            item_table = Table(table_data, colWidths=colWidths, rowHeights=rowHeights)
            item_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (4, 0), (7, 0), 'RIGHT'),
                    ('SPAN', (0, 0), (1, 0)),
                    ('BOTTOMPADDING', (0, 0), (7, 0), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
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
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(item_table)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, part_list=part_list, group_list=group_list),
                  onLaterPages=partial(self._header_footer, company_id=company_id, part_list=part_list, group_list=group_list),
                  canvasmaker=partial(NumberedPage, adjusted_height=100))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
