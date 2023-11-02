from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from items.models import Item
from orders.models import OrderItem
from locations.models import LocationItem
from reports.numbered_page import NumberedPage
from django.conf import settings as s
from django.db.models import Q, F, Sum, Value
from django.db.models.functions import Coalesce
from utilities.constants import ORDER_STATUS, ORDER_TYPE
import datetime
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from functools import partial
from utilities.common import validate_date_to_from, get_company_name_and_current_period

colWidths = [155, 100, 100, 100, 70]
rowHeights = 13


class Print_SR8500:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, delivery_from, delivery_to, part_no, company_name, current_period, location,
                       part_no_from='', part_no_to='', customer_code_from='', customer_code_to=''):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        # 1st row
        header_data = []
        row1_info1 = "SR8500 Sales & Purchase System"
        # if int(location):
        row1_info2 = "Outstanding Balance & Stock Status Report By Location as at " + current_period
        # else:
        #     row1_info2 = "Outstanding Balance & Stock Status Report as at " + current_period
        header_data.append([row1_info1, row1_info2, ''])

        # 2nd row
        row2_info1 = company_name
        row2_info2 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row2_info3 = "Grouped by Part No."
        header_data.append([row2_info1, row2_info2, row2_info3])

        empty_data = '[] - []'
        general_data = ''

        # 3rd row
        pt_list = eval(part_no)
        if len(pt_list):
            part_no_from = Item.objects.get(pk=pt_list[0]).code
            part_no_to = Item.objects.get(pk=pt_list[-1]).code
            general_data = '[' + part_no_from + '] - [' + part_no_to + ']'
        else:
            general_data = empty_data

        row4_info1 = "Part No.: " + general_data

        current_year = datetime.datetime.now().year
        delivery_from_year = datetime.datetime.strptime(delivery_from, '%d-%m-%Y').year
        delivery_to_year = datetime.datetime.strptime(delivery_to, '%d-%m-%Y').year
        if current_year - delivery_from_year <= 99 and delivery_to_year <= current_year:
            row4_info2 = "Wanted Date : [" + delivery_from + "]" + " - [" + delivery_to + "]"
        elif current_year - delivery_from_year <= 99:
            row4_info2 = "Wanted Date : [" + delivery_from + "]" + " - [_/_/_]"
        elif delivery_to_year <= current_year:
            row4_info2 = "Wanted Date : [_/_/_]" + " - [" + delivery_to + "]"
        else:
            row4_info2 = "Wanted Date : [_/_/_]" + " - [_/_/_]"

        header_data.append([row4_info2, row4_info1, ''])

        header_table = Table(header_data, colWidths=[210, 200, 317])
        header_table.setStyle(TableStyle(
            [('SPAN', (1, 0), (2, 0)),
             ('ALIGN', (1, 0), (-1, -4), 'RIGHT'),
             ('ALIGN', (2, 0), (-1, -3), 'RIGHT'),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('TOPPADDING', (0, 2), (-1, -2), 5),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 7, doc.height + doc.topMargin - h)

        table_data = []
        table_header = ['Part No.', 'On Hand Qty', 'Outstanding S/O Qty', 'Outstanding P/O Qty',  'Balance Qty']
        table_data.append(table_header)

        global colWidths
        item_header_table = Table(table_data, colWidths=colWidths)

        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('ALIGN', (0, 0), (0, 0), 'LEFT'),
             ('ALIGN', (1, 0), (4, 0), 'RIGHT'),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(canvas, doc.leftMargin - 5, doc.height + doc.topMargin - h - h1 - 5)

        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, delivery_from, delivery_to, part_no, location):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42, topMargin=105, bottomMargin=42, pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterAlignBold', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CenterAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="Justify", fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_JUSTIFY))

        delivery_from_obj, delivery_to_obj = validate_date_to_from(delivery_from, delivery_to)

        elements = []

        part_list, so_order_item_list, po_order_item_list = get_all_list(company_id, location, part_no, delivery_from_obj, delivery_to_obj)

        on_hand_qty = so_qty = po_qty = balance_qty = 0
        grand_on_hand_qty = grand_so_qty = grand_po_qty = grand_balance_qty = 0

        for item in part_list:

            on_hand_qty, so_qty, po_qty, balance_qty = get_all_qty(on_hand_qty, so_qty,
                                                                   po_qty, balance_qty, item, so_order_item_list, po_order_item_list, location)

            part_info = []
            if on_hand_qty == 0 and so_qty == 0 and po_qty == 0 and balance_qty == 0:
                pass
            else:
                part_info.append([Paragraph(item['item__code'], styles['LeftAlign']),
                                  Paragraph(intcomma("%.2f" % on_hand_qty), styles['RightAlign']),
                                  Paragraph(intcomma("%.2f" % so_qty), styles['RightAlign']),
                                  Paragraph(intcomma("%.2f" % po_qty), styles['RightAlign']),
                                  Paragraph(intcomma("%.2f" % balance_qty), styles['RightAlign'])])

                item_table = Table(part_info, colWidths=colWidths, rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                        ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                        ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ]))
                elements.append(item_table)

                grand_on_hand_qty += on_hand_qty
                grand_so_qty += so_qty
                grand_po_qty += po_qty
                grand_balance_qty += balance_qty

            on_hand_qty = so_qty = po_qty = balance_qty = 0

        # Actions after the for loop
        table_data = []
        # Print Grand Total
        table_data.append([Paragraph('Grand Total :', styles['RightAlignBold']),
                           Paragraph(intcomma("%.2f" % grand_on_hand_qty), styles['RightAlign']),
                           Paragraph(intcomma("%.2f" % grand_so_qty), styles['RightAlign']),
                           Paragraph(intcomma("%.2f" % grand_po_qty), styles['RightAlign']),
                           Paragraph(intcomma("%.2f" % grand_balance_qty), styles['RightAlign'])])

        item_table = Table(table_data, colWidths=colWidths)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('ALIGN', (0, 0), (0, 0), 'LEFT'),
             ('ALIGN', (1, 0), (4, 0), 'RIGHT'),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        elements.append(item_table)

        company_name, current_period = get_company_name_and_current_period(company_id)

        if not delivery_from_obj:
            delivery_from_obj = ''
        else:
            delivery_from_obj = delivery_from_obj.strftime('%d-%m-%Y')

        if not delivery_to_obj:
            delivery_to_obj = ''
        else:
            delivery_to_obj = delivery_to_obj.strftime('%d-%m-%Y')

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, delivery_from=delivery_from_obj,
                                      delivery_to=delivery_to_obj, part_no=part_no,
                                      company_name=company_name, current_period=current_period, location=location),
                  onLaterPages=partial(self._header_footer, delivery_from=delivery_from_obj,
                                       delivery_to=delivery_to_obj, part_no=part_no,
                                       company_name=company_name, current_period=current_period, location=location),
                  canvasmaker=partial(NumberedPage, adjusted_height=97))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


def get_all_list(company_id, location, part_no, delivery_from_obj, delivery_to_obj):

    if location:
        part_list = LocationItem.objects.select_related('item').select_related('location').filter(
            is_hidden=False, item__company_id=company_id, location_id=int(location))
    else:
        part_list = LocationItem.objects.select_related('item').filter(is_hidden=False, item__company_id=company_id)

    
    try:
        pt_list = eval(part_no)
        if len(pt_list):
            part_list = part_list.filter(item__id__in=pt_list)
    except Exception as e:
        print(e)
    if location:
        # part_list = part_list.order_by('item__code').values('item__code', 'onhand_qty', 'location_id')
        part_list = part_list.order_by('item__code').values('item__code', 'location_id').annotate(total_onhand_qty=Sum('onhand_qty'))
    else:
        # part_list = part_list.order_by('item__code').values('item__code', 'onhand_qty')
        part_list = part_list.order_by('item__code').values('item__code').annotate(total_onhand_qty=Sum('onhand_qty'))

    so_order_item_list = OrderItem.objects.select_related('order').select_related('item').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                                                 wanted_date__range=(delivery_from_obj.strftime(
                                                                                                     '%Y-%m-%d'), delivery_to_obj.strftime('%Y-%m-%d')),
                                                                                                 order__order_type=dict(ORDER_TYPE)['SALES ORDER']) \
        .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
        .exclude(quantity=F('delivery_quantity')) \
        .order_by('item__code').values('item__code', 'quantity', 'delivery_quantity', 'location_id')

    po_order_item_list = OrderItem.objects.select_related('order').select_related('item').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                                                 wanted_date__range=(delivery_from_obj.strftime(
                                                                                                     '%Y-%m-%d'), delivery_to_obj.strftime('%Y-%m-%d')),
                                                                                                 order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER']) \
        .exclude(Q(order__status=dict(ORDER_STATUS)['Draft'])) \
        .exclude(quantity=F('receive_quantity')) \
        .order_by('item__code').values('item__code', 'quantity', 'receive_quantity', 'location_id')

    return part_list, so_order_item_list, po_order_item_list


def get_all_qty(on_hand_qty, so_qty, po_qty, balance_qty, item, so_order_item_list, po_order_item_list, location=None):
    # on hand quantity
    # on_hand_qty = item['onhand_qty']
    on_hand_qty = item['total_onhand_qty']
    if on_hand_qty == None:
        on_hand_qty = 0

    # Calculating the S/O orders
    if location:
        so_order = so_order_item_list.filter(item__code=item['item__code'], location_id=int(location)
                                             ).aggregate(quantity=Coalesce(Sum('quantity'), Value(0)), delivered_quantity=Coalesce(Sum('delivery_quantity'), Value(0)))
    else:
        so_order = so_order_item_list.filter(item__code=item['item__code'],
                                             ).aggregate(quantity=Coalesce(Sum('quantity'), Value(0)), delivered_quantity=Coalesce(Sum('delivery_quantity'), Value(0)))

    # Get the Outstanding Value
    so_qty = so_order['quantity'] - so_order['delivered_quantity']

    # Calculating the P/O orders
    po_order = po_order_item_list.filter(item__code=item['item__code'],
                                         ).aggregate(quantity=Coalesce(Sum('quantity'), Value(0)), received_quantity=Coalesce(Sum('receive_quantity'), Value(0)))

    # Get the Outstanding Value
    po_qty = po_order['quantity'] - po_order['received_quantity']

    balance_qty = (on_hand_qty + po_qty) - so_qty

    return on_hand_qty, so_qty, po_qty, balance_qty
