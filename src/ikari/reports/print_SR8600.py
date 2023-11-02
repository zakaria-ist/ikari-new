import calendar
import datetime
import os
import math
from functools import partial
from django.conf import settings as s
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import F, Value as V
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from companies.models import Company
from currencies.models import ExchangeRate
from orders.models import OrderItem
from items.models import Item
from reports.numbered_page import NumberedPage
from suppliers.models import SupplierItem
from utilities.constants import EXCHANGE_RATE_TYPE, ORDER_TYPE, ORDER_STATUS
from utilities.common import round_number, get_decimal_place

colWidths = [40, 45, 65, 0, 80, 0, 38, 20, 35, 40,
             35, 20, 30, 45, 50, 35, 50, 45, 45, 45, 50]


class Print_SR8600:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, company_id, first_day, last_day):
        pdfmetrics.registerFont(
            TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(
            TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Draw header of PDF
        company = Company.objects.get(pk=company_id)
        # 1st row
        header_data = []
        row1_info1 = "SR8600 Sales and Purchase System"
        row1_info2 = "MONTHLY GROSS PROFIT REPORT AS AT " + \
            first_day.strftime('%B %Y').upper()
        header_data.append([row1_info1, row1_info2])
        # 2nd row
        company = Company.objects.get(pk=company_id)
        row2_info1 = company.name
        row2_info2 = "Group By Customer No., Supplier & Part No."
        header_data.append([row2_info1, row2_info2])
        # 3rd row
        row3_info1 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        row3_info2 = ""
        header_data.append([row3_info1, row3_info2])
        # 4st row
        row4_info1 = "Issued Date : [" + first_day.strftime('%d/%m/%Y') + "] To [" + \
                     last_day.strftime('%d/%m/%Y') + "]"
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2])

        header_table = Table(header_data, colWidths=[400, 410], rowHeights=12)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('SIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE_2),
             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
             ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
             ('BOTTOMPADDING', (0, -1), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 2), (-1, 2), 0),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 5,
                            doc.height + doc.topMargin - h)

        table_data = []
        # # 1ST ROW
        table_header = ['', '', '', '', '', '', '', '<---------------------BUYING PRICE----------------->', '', '', '',
                        '<----------------SELLING PRICE-------------------->', '', '', '', '', '', '', '', 'SALES', '']
        table_data.append(table_header)
        # 2ND ROW
        table_header = ['CUST.', 'SUPP.', 'PART', '', 'PART NO.', '', 'MODEL', 'CURR', 'EXCH.', 'UNIT', 'LC. PRICE', 'CURR',
                        'EXCH.', 'UNIT', 'LC. PRICE', 'PROFIT', 'QTY/M', 'TOTAL', 'SALES', 'TURN OVER', 'PROFIT']
        table_data.append(table_header)
        # 3RD ROW
        table_header = ['', '', 'DESCRIPTION', '', '', '', '', '', 'RATE', 'PRICE', company.currency.code, '', 'RATE',
                        'PRICE', company.currency.code, '', '', 'PROFIT', 'TURN OVER', '(Local Price)', '(%)']
        table_data.append(table_header)

        item_header_table = Table(
            table_data, colWidths=colWidths, rowHeights=10)
        item_header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('SIZE', (0, 0), (-1, -1), 5),
             ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('TOPPADDING', (1, 0), (-1, -1), 10),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
             ('ALIGN', (10, -1), (10, -1), 'CENTER'),
             ('ALIGN', (12, -1), (12, -1), 'CENTER'),
             ('ALIGN', (20, 0), (20, -1), 'CENTER'),
             ('ALIGN', (19, 0), (19, -1), 'CENTER'),
             ('ALIGN', (18, 0), (18, -1), 'CENTER'),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('SPAN', (7, 0), (10, 0)),
             ('SPAN', (11, 0), (14, 0)),
             ]))
        w1, h1 = item_header_table.wrap(doc.width, doc.topMargin)
        item_header_table.drawOn(
            canvas, doc.leftMargin - 8, doc.height + doc.topMargin - h - h1)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, company_id, from_month, from_year, to_month, to_year):
        pdfmetrics.registerFont(
            TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(
            TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=22, leftMargin=22,
                                topMargin=118, bottomMargin=42, pagesize=landscape(A4))
        # Our container for 'Flowable' objects
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold',
                   fontName=s.REPORT_FONT_BOLD, fontSize=6, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign',
                   fontName=s.REPORT_FONT_BOLD, fontSize=6, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign',
                   fontName=s.REPORT_FONT, fontSize=6, alignment=TA_RIGHT))

        # Our container for 'Flowable' objects
        elements = []

        # Draw Content of PDF
        first_day = datetime.date(int(from_year), int(from_month), 1)
        last_day = datetime.date(int(to_year), int(
            to_month), calendar.monthrange(int(to_year), int(to_month))[1])
        order_item_list = OrderItem.objects \
            .select_related('order').select_related('item').select_related('supplier').select_related('order__customer')\
            .filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                    order__order_type=dict(ORDER_TYPE)['SALES INVOICE']) \
            .filter(order__document_date__gte=first_day, order__document_date__lte=last_day) \
            .exclude(order__customer__isnull=True, item__isnull=True, order__status=dict(ORDER_STATUS)['Draft'])\
            .order_by('order__customer__code', 'supplier__code', 'item__code', 'last_purchase_price', 'price')
        company_currency = ''
        company = Company.objects.filter(id=company_id).last()
        decimal_place_f = get_decimal_place(company.currency)
        if company.currency:
            company_currency = company.currency.id

        line = 0
        quantity = 0
        total_all_turnover = 0
        total_all_profit = 0
        total_all_quantity = 0
        total_all_profit_tax = 0
        total_all_turnover_local = 0
        price_buy = 0
        price_sell = 0
        exchange_rate_buy = 0
        exchange_rate_sell = 0
        dummy_exchange_rate_buy = 0
        code = ''
        part_no = ''
        curr_buy = ''

        if order_item_list.exists():
            for i, cus in enumerate(order_item_list):
                refer_doc = getReferDoc(cus, first_day, last_day)
                if refer_doc:
                    cus.last_purchase_price = getPurchasePrice(refer_doc)
                    cus.save()
                    curr_buy = refer_doc.supplier.currency.code
                    dummy_exchange_rate_buy = getExchangeRate(
                        company_currency, cus, refer_doc, first_day)

                if i == 0:
                    code = cus.order.customer.code if cus.order.customer else ''
                    part_no = cus.item.code
                    price_buy = cus.last_purchase_price
                    price_sell = cus.price
                    exchange_rate_buy = dummy_exchange_rate_buy
                    exchange_rate_sell = cus.order.exchange_rate

                if (code == cus.order.customer.code) & (part_no == cus.item.code) \
                        & (price_buy == cus.last_purchase_price) & (price_sell == cus.price) & (exchange_rate_buy == dummy_exchange_rate_buy) \
                        & (exchange_rate_sell == cus.order.exchange_rate):

                    if cus.quantity is not None:
                        quantity += cus.quantity
                else:
                    if quantity > 0:
                        item_table, total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local = self.print_Data(
                            company_currency, company_id, order_item_list[i -
                                                                          1], quantity, total_all_profit,
                            total_all_quantity, total_all_turnover, total_all_turnover_local, price_buy, curr_buy,
                            exchange_rate_buy, exchange_rate_sell, decimal_place_f)

                        if (total_all_profit > 0) & (total_all_turnover > 0):
                            total_all_profit_tax += (total_all_profit /
                                                     total_all_turnover) * 100

                        elements.append(item_table)
                        line += 1

                    if cus.quantity is not None:
                        quantity = cus.quantity
                    else:
                        quantity = 0

                    if (code != cus.order.customer.code) & (line > 0):
                        table_data = [['', '', '', '', '', '', '', '',
                                       '', '', '', '', '', '', '', '', '', '', '']]
                        item_table = Table(table_data, colWidths=colWidths)
                        item_table.setStyle(TableStyle(
                            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                             ('LEFTPADDING', (0, 0), (-1, -1), 0),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                             ('TOPPADDING', (0, -1), (-1, -1), - 22),
                             ]))
                        elements.append(item_table)
                    code = cus.order.customer.code
                    part_no = cus.item.code
                    price_buy = cus.last_purchase_price
                    price_sell = cus.price
                    exchange_rate_buy = dummy_exchange_rate_buy
                    exchange_rate_sell = cus.order.exchange_rate
                if i == order_item_list.__len__() - 1:
                    if quantity > 0:
                        item_table, total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local = self.print_Data(
                            company_currency, company_id, order_item_list[i], quantity, total_all_profit,
                            total_all_quantity, total_all_turnover, total_all_turnover_local, price_buy, curr_buy,
                            exchange_rate_buy, exchange_rate_sell, decimal_place_f)
                        elements.append(item_table)
                        total_all_profit_tax = (
                            total_all_profit / total_all_turnover_local) * 100 if total_all_turnover_local else 0

                    item_table = self.print_GrandTotal(styles, total_all_profit, total_all_profit_tax,
                                                       total_all_quantity, total_all_turnover_local, decimal_place_f)
                    elements.append(item_table)

        if elements.__len__() == 0:
            table_data = [['', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '']]
            table_body = Table(table_data, colWidths=colWidths)
            table_body.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent)
                 ]))
            elements.append(table_body)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, company_id=company_id, first_day=first_day,
                                      last_day=last_day),
                  onLaterPages=partial(self._header_footer, company_id=company_id, first_day=first_day,
                                       last_day=last_day),
                  canvasmaker=partial(NumberedPage, adjusted_height=-140, adjusted_width=255))

        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def print_Data(self, company_currency, company_id, order_item, quantity, total_all_profit,
                   total_all_quantity, total_all_turnover, total_all_turnover_local, purchase_price, curr_buy,
                   exchange_rate_buy, exchange_rate_sell, decimal_place_f):
        table_data = []
        table_cal_data = []
        create_row(order_item, quantity, company_currency, company_id, table_data, table_cal_data,
                   purchase_price, curr_buy, exchange_rate_buy, exchange_rate_sell, decimal_place_f)
        total_all_quantity += table_cal_data[0][0]
        total_all_profit += table_cal_data[0][1]
        total_all_turnover += table_cal_data[0][2]
        total_all_turnover_local += table_cal_data[0][3]

        item_table = Table(table_data, colWidths=colWidths, rowHeights=9)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
             ]))
        return item_table, total_all_profit, total_all_quantity, total_all_turnover, total_all_turnover_local

    def print_GrandTotal(self, styles, total_all_profit, total_all_profit_tax, total_all_quantity,
                         total_all_turnover_local, decimal_place_f):
        total_all_profit_tax = math.floor(
            total_all_profit_tax * 10 ** 4) / 10 ** 4
        table_data = []
        table_data.append(
            [Paragraph('Grand Total: ', styles["RightAlignBold"]),
             Paragraph(intcomma("%.2f" % total_all_quantity),
                       styles["RightAlign"]),
             Paragraph(intcomma(decimal_place_f %
                       total_all_profit), styles["RightAlign"]),
             '',
             Paragraph(intcomma(decimal_place_f %
                       total_all_turnover_local), styles["RightAlign"]),
             Paragraph(intcomma("%.4f" % total_all_profit_tax) +
                       '%', styles["RightAlign"])
             ])
        item_table = Table(table_data, colWidths=[578, 50, 45, 45, 45, 50])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
             ]))
        return item_table


def create_row(order_item, quantity, company_currency, company_id, table_data, table_cal_data, purchase_price, curr_buy, exchange_rate_buy, exchange_rate_sell, decimal_place_f):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlignBold',
               fontName=s.REPORT_FONT_BOLD, fontSize=5, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='LeftAlign',
               fontName=s.REPORT_FONT, fontSize=5, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='RightAlign',
               fontName=s.REPORT_FONT, fontSize=5, alignment=TA_RIGHT))

    total_all_turnover_1 = 0
    total_all_profit_1 = 0
    total_all_quantity_1 = 0
    local_price_buy = 0
    total_all_turnover_local_1 = 0
    local_price_sell = round_number(order_item.price * exchange_rate_sell, 5)
    local_price_buy = round_number(
        purchase_price * exchange_rate_buy, 5) if purchase_price else 0
    profit = local_price_sell - local_price_buy
    total_profit = round_number(quantity * profit)
    total_turnover = round_number(order_item.price * quantity)
    total_turnover_local = round_number(local_price_sell * quantity)
    profit_percentage = profit / \
        (local_price_sell / 100) if local_price_sell else 0
    total_all_turnover_1 += total_turnover
    total_all_profit_1 += total_profit
    total_all_quantity_1 += quantity
    total_all_turnover_local_1 += total_turnover_local

    table_cal_data.append([total_all_quantity_1, total_all_profit_1,
                          total_all_turnover_1, total_all_turnover_local_1])

    item_desc = ''
    if order_item.item.short_description:
        item_desc = order_item.item.short_description[:16]
    elif order_item.item.name:
        item_desc = order_item.item.name[:16]
    table_data.append(
        [
            Paragraph(order_item.order.customer.code if order_item.order.customer else '',
                      styles["LeftAlign"]),
            Paragraph(
                order_item.supplier.code if order_item.supplier else '', styles["LeftAlign"]),
            Paragraph(item_desc, styles["LeftAlign"]), '',
            Paragraph(order_item.item.code[:18], styles["LeftAlign"]), '',
            Paragraph(
                order_item.item.category.code[:7] if order_item.item.category else '', styles["LeftAlign"]),
            Paragraph(
                order_item.supplier.currency.code if order_item.supplier else '', styles["RightAlign"]),
            Paragraph(intcomma("%.4f" % exchange_rate_buy)
                      if exchange_rate_buy else '0.0000', styles["RightAlign"]),
            Paragraph(intcomma("%.5f" % round_number(purchase_price, 5))
                      if purchase_price else '0.00000', styles["RightAlign"]),
            Paragraph(intcomma("%.5f" % round_number(local_price_buy, 5))
                      if local_price_buy else '0.00000', styles["RightAlign"]),
            Paragraph(order_item.order.currency.code, styles["RightAlign"]),
            Paragraph(intcomma("%.4f" % exchange_rate_sell)
                      if exchange_rate_sell else '0.0000', styles["RightAlign"]),
            Paragraph(intcomma("%.5f" % round_number(order_item.price, 5)) if order_item.price else '0.00000',
                      styles["RightAlign"]),
            Paragraph(intcomma("%.5f" % round_number(local_price_sell, 5))
                      if local_price_sell else '0.00000', styles["RightAlign"]),
            Paragraph(intcomma("%.5f" % round_number(profit, 5))
                      if profit else '0.00000', styles["RightAlign"]),
            Paragraph(intcomma("%.2f" % quantity)
                      if quantity else '0.00', styles["RightAlign"]),
            Paragraph(intcomma(decimal_place_f % round_number(total_profit))
                      if total_profit else '0.00', styles["RightAlign"]),
            Paragraph(intcomma(decimal_place_f % round_number(total_turnover))
                      if total_turnover else '0.00', styles["RightAlign"]),
            Paragraph(intcomma(decimal_place_f % round_number(total_turnover_local)) if total_turnover_local else '0.00',
                      styles["RightAlign"]),
            Paragraph(intcomma("%.4f" % round_number(profit_percentage, 4)) + '%' if profit_percentage else '0.0000%',
                      styles["RightAlign"]),
        ])


def getPurchasePrice(doc):
    purchase_price = doc.price
    if doc.order.order_type in [dict(ORDER_TYPE)['SALES ORDER'], dict(ORDER_TYPE)['PURCHASE ORDER']]:
        try:
            part = Item.objects.get(pk=doc.item_id)
            if part and part.last_purchase_price:
                purchase_price = part.last_purchase_price
            else:
                part_purchase_price = SupplierItem.objects. \
                    filter(is_hidden=0, is_active=1, supplier_id=doc.supplier_id, item_id=doc.item_id) \
                    .values('item_id', 'effective_date') \
                    .annotate(new_price=Coalesce(F('new_price'), V(0))) \
                    .annotate(purchase_price=Coalesce(F('purchase_price'), V(0))) \
                    .last()

                if not part_purchase_price['effective_date']:
                    purchase_price = part_purchase_price['purchase_price'] if part_purchase_price[
                        'purchase_price'] else 0.00000
                elif part_purchase_price['effective_date'].strftime('%Y-%m-%d') <= datetime.datetime.now().strftime(
                        '%Y-%m-%d'):
                    purchase_price = part_purchase_price['new_price'] if part_purchase_price['new_price'] else \
                        part_purchase_price['purchase_price']
                else:
                    purchase_price = part_purchase_price['purchase_price'] if part_purchase_price[
                        'purchase_price'] else 0.00000
        except:
            pass
    return purchase_price


def getExchangeRate(company_currency, doc, refer_doc, report_start_date):
    exchange_rate = 1
    if refer_doc.order.order_type != dict(ORDER_TYPE)['SALES ORDER']:
        if refer_doc.order.currency_id != int(company_currency):
            try:
                if refer_doc.supplier.currency_id == refer_doc.order.currency_id \
                        and refer_doc.order.exchange_rate \
                        and refer_doc.order.order_type in [dict(ORDER_TYPE)['PURCHASE INVOICE']]:
                    exchange_rate = refer_doc.order.exchange_rate
                else:
                    exchange_date = parse_date(str(report_start_date))
                    exchange_rate = ExchangeRate.objects. \
                        filter(
                            from_currency_id=refer_doc.supplier.currency_id,
                            to_currency_id=company_currency,
                            exchange_date__month=exchange_date.month,
                            exchange_date__year=exchange_date.year,
                            flag=EXCHANGE_RATE_TYPE['3'], is_hidden=False) \
                        .last().rate
            except:
                pass
    else:
        if refer_doc.supplier.currency_id != int(company_currency):
            try:
                exchange_date = parse_date(str(report_start_date))
                exchange_rate = ExchangeRate.objects. \
                    filter(
                        from_currency_id=refer_doc.supplier.currency_id,
                        to_currency_id=company_currency,
                        exchange_date__month=exchange_date.month,
                        exchange_date__year=exchange_date.year,
                        flag=EXCHANGE_RATE_TYPE['3'], is_hidden=False) \
                    .last().rate
            except Exception as e:
                print(e)

    return exchange_rate


def getReferDoc(doc, first_day, last_day):
    refer_doc = None
    so = get_SO_from_DO(doc)
    if so:
        refer_doc = so
        po = get_PO_from_SO(so, doc.quantity)
        # po = get_PO_from_SO(so)
        if po and po.exists():
            refer_doc = po.last()
            # gr = get_GR_from_PO(po, doc.quantity)
            gr = get_GR_from_PO(po, first_day, last_day, doc.quantity, doc.order.document_date)
            if gr:
                refer_doc = gr
    return refer_doc


def get_SO_from_DO(do):
    so = None
    try:
        oi = OrderItem.objects \
            .select_related('order').select_related('item') \
            .filter(order__is_hidden=0,
                    order__order_type=dict(ORDER_TYPE)['SALES ORDER'],
                    order_id=do.reference_id,
                    item_id=do.item_id,
                    is_hidden=0,
                    line_number=do.refer_line).order_by('order__document_date')
        so = oi.first() if oi else None
    except:
        pass
    return so


def get_PO_from_SO(so, qty=None):
    po = []
    try:
        oi = OrderItem.objects \
            .select_related('order').select_related('item') \
            .filter(order__is_hidden=0,
                    order__order_type=dict(ORDER_TYPE)['PURCHASE ORDER'],
                    reference_id=so.order_id,
                    is_hidden=0,
                    item_id=so.item_id).order_by('order__document_date')

        oi_filtered = []
        if oi and oi.exists() and qty:
            oi_filtered = oi.filter(quantity__exact=qty)

        if oi_filtered and oi_filtered.exists():
            po = oi_filtered
        else:
            # po = oi.last()
            po = oi

    except:
        pass
    return po


def get_GR_from_PO(po, first_day, last_day, qty, do_date=None):
    gr = None
    try:
        po_ids = po.values_list('order_id', flat=True)
        po_item_id = po.first().item_id
        oi = OrderItem.objects \
            .select_related('order').select_related('item') \
            .filter(order__is_hidden=0,
                    order__document_date__lte=last_day,
                    order__order_type=dict(ORDER_TYPE)['PURCHASE INVOICE'],
                    # reference_id=po.order_id,
                    reference_id__in=po_ids,
                    is_hidden=0,
                    # item_id=po.item_id)
                    item_id=po_item_id)\
            .order_by('order__document_date')

        oi_filtered = []
        if oi and oi.exists() and qty:
            if do_date:
                oi_filtered = oi.filter(
                    quantity__exact=qty, order__document_date=do_date)
                if not oi_filtered.exists():
                    oi_filtered = oi.filter(
                        quantity__exact=qty, order__document_date__lte=do_date)
            else:
                oi_filtered = oi.filter(quantity__exact=qty)

        if oi_filtered and oi_filtered.exists():
            gr = oi_filtered.last()
        else:
            if oi and oi.exists():
                gr = oi.last()

    except:
        print('ERROR: get_GR_from_PO')
    return gr


def setSupplierAndPurchasePrice(order_item_list):
    for order_item in order_item_list:
        if not order_item.supplier_id or not order_item.last_purchase_price:
            refer_doc = getReferDoc(order_item)
            if refer_doc:
                order_item.supplier_id = refer_doc.supplier_id
                order_item.last_purchase_price = getPurchasePrice(refer_doc)
                order_item.save()
