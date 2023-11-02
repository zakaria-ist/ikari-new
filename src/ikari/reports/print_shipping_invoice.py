from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import currencies.models
from orders.models import Order, OrderItem, OrderDelivery
from customers.models import Delivery
from contacts.models import Contact
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company
from utilities.common import round_number, get_decimal_place


colWidths = [30, 110, 160, 60, 25, 75, 74]
MAX_LINE = 35


def remove_none(param):
    if param is None or param == 'None' or param == 'none':
        param = ''
    return param


class Print_Shipping_Invoice:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, order_id, print_header, company_id, address):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Draw header of PDF
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomTitle', fontName=s.REPORT_FONT_BOLD, fontSize=18, leading=22,
                                  alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CustomHeader', fontName='Times-BoldItalic', fontSize=18, leading=18,
                                  alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, leading=12))
        order = Order.objects.get(pk=order_id)

        # ===========================Header Image ===========================
        if print_header == '1':
            if order and order.company:
                canvas.line(40, doc.height + doc.topMargin - 45, doc.width + doc.leftMargin + 21,
                            doc.height + doc.topMargin - 45)
                logo_exist = False
                if order.company.header_logo:
                    try:
                        path_header_logo = s.MEDIA_ROOT + str(order.company.header_logo)
                        canvas.drawImage(path_header_logo, 65, doc.height + doc.topMargin - 35, 500, 60)
                        logo_exist = True
                    except Exception as e:
                        print(e)
                        logo_exist = False

                if not logo_exist:
                    header_data = []
                    row1_info1 = Paragraph(order.company.name.upper() if order.company.name else '', styles['CustomHeader'])
                    header_data.append([row1_info1])

                    row2_info1 = Paragraph(order.company.address if order.company.address else '', styles['LeftAlign'])
                    header_data.append([row2_info1])

                    # row3_info1 = "TEL: " + order.company.phone if order.company.phone else ''
                    # row3_info1 = row3_info1 + "        " + "FAX: " + order.company.fax if order.company.fax else ''
                    # header_data.append([row3_info1])

                    row4_info1 = "GST Co Reg No : " + order.company.company_number if order.company.company_number else ''
                    header_data.append([row4_info1])

                    header_table = Table(header_data, colWidths=[430])
                    header_table.setStyle(TableStyle(
                        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                         ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                         ('BOTTOMPADDING', (0, -1), (-1, -1), 0),
                         ('TOPPADDING', (0, -1), (-1, -1), 0),
                         ]))

                    w, h = header_table.wrap(doc.width, doc.topMargin)
                    header_table.drawOn(canvas, doc.leftMargin + 70, doc.height + doc.topMargin - 40)
        # ===========================Header Title ===========================
        header_data = []
        row1_info1 = Paragraph("INVOICE", styles['CustomTitle'])
        header_data.append([row1_info1])

        header_table = Table(header_data, colWidths=[530], rowHeights=20)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 22, doc.height + doc.topMargin - h - 60)

        # ===========================Header Title Left===========================
        order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id).first()
        header_data = []

        if int(address):
            try:
                delivery_info = Delivery.objects.get(is_hidden=0, id=int(address))
            except Exception as e:
                print(e)
                delivery_info = None
        else:
            delivery_info = None

        row2_info1 = "MESSERS:"
        header_data.append([row2_info1, ''])

        if delivery_info:
            customer_name = order.customer.name if order.customer.name else ''
            address_info1 = Paragraph(remove_none(delivery_info.address.replace('\n', '<br />\n')
                                                  if delivery_info.address else ''), styles['CustomStyle'])
            attention = delivery_info.attention if delivery_info.attention else ''
            phone = delivery_info.phone if delivery_info.phone else ''
        elif order_delivery and order_delivery.delivery_id:
            customer_name = order.customer.name if order.customer.name else ''
            customer_name += '\n' + order_delivery.name if order_delivery.name else ''
            address_info1 = Paragraph(remove_none(order_delivery.delivery.address.replace('\n', '<br />\n')
                                                  if order_delivery.delivery.address else ''), styles['CustomStyle'])
            attention = order_delivery.delivery.attention if order_delivery.delivery.attention else ''
            phone = order_delivery.delivery.phone if order_delivery.delivery.phone else ''
        else:
            customer_name = order.customer.name if order.customer.name else ''
            address_info1 = ''
            attention = ''
            phone = ''

        header_data.append(['', customer_name])
        header_data.append(['', ''])
        header_data.append(['', ''])
        header_data.append(['', address_info1])
        header_data.append(['', ''])
        header_data.append(['', ''])
        row5_info1 = 'ATTN: ' + attention
        # row5_info1 += '\nTEL   : ' + phone
        header_data.append(['', row5_info1])

        header_table = Table(header_data, colWidths=[20, 330], rowHeights=15)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 17),
             ('BOTTOMPADDING', (0, -1), (-1, -1), 0),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 22, doc.height + doc.topMargin - h - 80)
        

        # == == == == == == == == == == == == == =Header Title RIGHT== == == == == == == == == == == == == =
        header_data = []
        if order:
            row3_info2 = 'CO.REG.NO.'
            row3_info3 = ': ' + order.company.company_number if order.company.company_number else ': '
            header_data.append([row3_info2, row3_info3])

            row4_info2 = 'INVOICE NO.'
            row4_info3 = ': ' + order.document_number if order.document_number else ': '
            header_data.append([row4_info2, row4_info3])

            row5_info2 = 'DATE'
            row5_info3 = ': ' + order.document_date.strftime('%d %b %Y').upper()
            header_data.append([row5_info2, row5_info3])

            row6_info2 = 'TERMS'
            row6_info3 = ': ' + str(order.customer.payment_term) + ' days' if order.customer else ': ' + '0 days'
            header_data.append([row6_info2, row6_info3])

            row7_info2 = 'DELIVERY'
            row7_info3 = ': ' + order.note if order.note else ': '
            header_data.append([row7_info2, row7_info3])

            # if pay_mode == '1':
            #     row8_info2 = 'PAY MODE'
            #     row8_info3 = ': ' + order.payment_mode.code if order.payment_mode else ': '
            #     header_data.append([row8_info2, row8_info3])
            # else:
            row8_info2 = ''
            row8_info3 = ''
            header_data.append([row8_info2, row8_info3])

            # row9_info2 = 'REMARK'
            # row9_info3 = ': ' + order.remark.replace('\n', ' ')[:12] if order.remark else ': '
            # header_data.append([row9_info2, row9_info3])
            row9_info2 = ''
            row9_info3 = ''
            header_data.append([row9_info2, row9_info3])

            header_data.append(['PAGE', ': '])

        header_table = Table(header_data, colWidths=[63, 137], rowHeights=12)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin + 340, doc.height + doc.topMargin - h - 80)
        # ===========================Order Title ===========================

        item = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                        order_id=order_id).last()
        uom = item.item.purchase_measure.code if item.item.purchase_measure else 'PCS'
        title_data = []
        title_row1 = ['LN.', 'CUST. P/O NO.', 'PART NO', 'QUANTITY', '', 'UNIT PRICE', 'AMOUNT']
        title_data.append(title_row1)
        title_row2 = ['', 'S/O NO.', 'DESCRIPTION', '(' + uom + ')', '',
                      '(' + order.currency.code + ')', '(' + order.currency.code + ')']
        title_data.append(title_row2)
        title_table = Table(title_data, colWidths=colWidths)
        title_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (4, 0), (4, 0), 'RIGHT'),
             ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
             ]))
        w, h = title_table.wrap(doc.width, doc.topMargin)
        title_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - 200)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, order_id, print_header, company_id, part_group, address):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=42,
                                leftMargin=60,
                                topMargin=260,
                                bottomMargin=42,
                                pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='BoldText', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomHeaderStyle', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, leading=22,
                                  alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, leading=12))
        # Our container for 'Flowable' objects
        elements = []
        company = Company.objects.get(id=company_id)
        decimal_place_f = get_decimal_place(company.currency)
        order = Order.objects.get(id=order_id)
        decimal_place = get_decimal_place(order.currency)
        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id).order_by('line_number')
        line_count = 0
        if company and order and order_item_list:
            # Draw Content of PDF
            # ===========================Order Items Data ===========================
            total_quantity = 0
            for index, my_item in enumerate(order_item_list):
                item_list_data = []
                total_quantity += my_item.quantity
                item_list_data.append([intcomma("%.0f" % my_item.line_number),
                                       my_item.customer_po_no, my_item.item.code,
                                       intcomma("%.2f" % round_number(my_item.quantity)), '',
                                       intcomma("%.5f" % round_number(my_item.price, 5)),
                                       intcomma(decimal_place % round_number(my_item.amount))])
                item_table = Table(item_list_data, colWidths=colWidths, rowHeights=13)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
                     ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ('TOPPADDING', (0, 0), (-1, -1), 3),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ]))
                elements.append(item_table)
                line_count += 1
                if line_count > MAX_LINE:
                    elements.append(PageBreak())
                    line_count = 0
                item_list_data = []

                if int(part_group):
                    item_list_data.append(['', my_item.refer_number if my_item.refer_number else '',
                                           my_item.item.name if my_item.item.name else '',
                                           'MODEL: ' + my_item.item.category.name if my_item.item.category else 'MODEL: ', '', '', ''])
                else:
                    item_list_data.append(['', my_item.refer_number if my_item.refer_number else '',
                                           my_item.item.name if my_item.item.name else '', '', '', '', ''])

                # Create the table
                item_table = Table(item_list_data, colWidths=colWidths, rowHeights=13)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('SPAN', (3, 0), (-1, -1)),
                     ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ]))
                elements.append(item_table)
                line_count += 1
                if line_count > MAX_LINE:
                    elements.append(PageBreak())
                    line_count = 0
            # ===========================Footer Data============================
            footer_data = []
            footer_data.append(['', '', 'TOTAL:',
                                intcomma("%.2f" % round_number(total_quantity)), '', '', ''])

            footer_table = Table(footer_data, colWidths=colWidths, rowHeights=20)
            footer_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                 ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ]))
            elements.append(footer_table)
            line_count += 1
            if line_count > MAX_LINE:
                elements.append(PageBreak())
                line_count = 0
            # ===========================Remarks Data============================
            if int(order.currency_id) == int(company.currency_id):
                exchange_rate = 1
            else:
                try:
                    exchange_rate = currencies.models.ExchangeRate.objects.filter(company_id=company_id, is_hidden=0,
                                                                                  from_currency_id=order.currency_id,
                                                                                  to_currency_id=company.currency_id,
                                                                                  exchange_date__month=order.document_date.month,
                                                                                  exchange_date__year=order.document_date.year,
                                                                                  flag='ACCOUNTING').last()
                    if exchange_rate:
                        exchange_rate = exchange_rate.rate
                    else:
                        exchange_rate = 1
                except currencies.models.ExchangeRate.DoesNotExist:
                    exchange_rate = 0

            remark_data = []
            remark_data.append([Paragraph('LOCAL EQUIVALENT AMT', styles['BoldText']), Paragraph(':', styles['BoldText']), '',
                                '', ''])
            remark_data.append(['EXCHANGE RATE', ':',
                                intcomma("%.4f" % round_number(float(exchange_rate), 4)), '',
                                'TOTAL B/F TAX ', ':',
                                intcomma(decimal_place % round_number(float(order.subtotal)))])
            remark_data.append(['INVOICE B/F TAX (' + company.currency.code + ')', ':',
                                intcomma(decimal_place_f % round_number(float(order.subtotal * exchange_rate))), '', 'ADD GST @ ' +
                                (intcomma("%.4f" % round_number(float(order.tax.rate))) if order.tax else '0.00')
                                + '%', ':',
                                intcomma(decimal_place % round_number(float(order.tax_amount)))])
            remark_data.append(['GST AMOUNT (' + company.currency.code + ')', ':',
                                intcomma(decimal_place_f % round_number(float(order.tax_amount * exchange_rate))), '', 'TOTAL AFTER TAX', ':',
                                intcomma(decimal_place % round_number(float(order.total)))])
            remark_data.append(['NETT AMOUNT (' + company.currency.code + ')', ':',
                                intcomma(decimal_place_f % round_number(float(order.total * exchange_rate))), '', ''])
            remark_table = Table(remark_data, colWidths=[130, 13, 100, 75, 107, 13, 101])
            remark_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                 ('RIGHTPADDING', (1, 0), (1, -1), 0),
                 ('LINEBELOW', (-1, -3), (-1, -2), 1, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('TOPPADDING', (0, 0), (-1, -1), 0),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                 ]))
            elements.append(remark_table)
            line_count += 5
            if line_count > MAX_LINE:
                elements.append(PageBreak())
                line_count = 0

            # ===========================Remarks + Signature/Footer Data============================
            remark_data = []
            remark_data.append([Paragraph('REMARKS:', styles['BoldText']),
                                Paragraph('for', styles['ItalicText']),
                                Paragraph(order.company.name.upper(), styles['LeftAlign'])])

            image = ''
            if order and order.company:
                if order.company.footer_logo:
                    try:
                        path_footer_logo = s.MEDIA_ROOT + str(order.company.footer_logo)
                        image = Image(path_footer_logo, 170, 50)
                        remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '', styles['LeftAlign']),
                                            '', image])
                    except Exception as e:
                        remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '', styles['LeftAlign']),
                                            '', ''])
                        print(e)
                else:
                    remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '', styles['LeftAlign']),
                                        '', ''])

            remark_data.append(['', '', 'AUTHORISED SIGNATURE'])
            remark_table = Table(remark_data, colWidths=[320, 25, 190])
            remark_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                 ('SPAN', (1, 1), (1, -2)),
                 ('ALIGN', (-2, -2), (-1, -1), 'CENTER'),
                 ('RIGHTPADDING', (-1, 1), (-1, 1), 0),
                 ('ALIGN', (-1, 1), (-1, 1), 'CENTER'),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('TOPPADDING', (0, 0), (-1, 0), 10),
                 ('LINEABOVE', (-2, -1), (-1, -1), 0.25, colors.black),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ]))
            line_count += 4
            if line_count > MAX_LINE:
                elements.append(PageBreak())
                line_count = 0
            elements.append(remark_table)
        # ===========================End Coding============================
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, order_id=order_id, print_header=print_header,
                                      company_id=company_id, address=address),
                  onLaterPages=partial(self._header_footer, order_id=order_id, print_header=print_header,
                                       company_id=company_id, address=address),
                  canvasmaker=partial(NumberedPage, adjusted_height=-31, adjusted_width=-78, adjusted_caption=''))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
