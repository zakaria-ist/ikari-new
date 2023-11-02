from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import Order, OrderItem, OrderDelivery
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_JUSTIFY
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from contacts.models import Contact

MAX_LINE = 25


def remove_none(param):
    if param is None or param == 'None' or param == 'none':
        param = ''
    return param


class Print_DO_Order:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, order_id, print_header, company_id, measure):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Draw header of PDF
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomTitle', fontName=s.REPORT_FONT_BOLD, fontSize=18, leading=22, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CustomHeader', fontName='Times-BoldItalic', fontSize=18, leading=18, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, leading=12))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='JustifyAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, alignment=TA_RIGHT))
        order = Order.objects.get(pk=order_id)

        # ===========================Header Image ===========================
        if print_header == '1':
            if order and order.company:
                canvas.line(40, doc.height + doc.topMargin - 45, doc.width + doc.leftMargin + 20,
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

                    row3_info1 = "TEL: " + order.company.phone if order.company.phone else ''
                    row3_info1 = row3_info1 + "        " + "FAX: " + order.company.fax if order.company.fax else ''
                    header_data.append([row3_info1])

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

        # ===========================Customer & Supplier Data===========================
        header_data = []
        row1_info1 = Paragraph("DELIVERY ORDER", styles['CustomTitle'])
        header_data.append([row1_info1])

        header_table = Table(header_data, colWidths=[530])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 12, doc.height + doc.topMargin - h - 50)

        header_data = []
        header_data.append(["MESSERS:"])
        contact = Contact.objects.filter(is_hidden=0, company_id=company_id, customer_id=order.customer.id).first()
        order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id).first()

        if order_delivery:
            if order_delivery.delivery_id:
                row1_info1 = ''
                row1_info2 = order.customer.name if order.customer.name else ''
                row1_info2 += '\n' + order_delivery.delivery.name if order_delivery.delivery.name else ''
                row2_info1 = ''
                row2_info2 = Paragraph(remove_none(order_delivery.delivery.address.replace('\n', '<br />\n') if order_delivery.delivery.address else ''),
                                       styles['CustomStyle'])
                attention = order_delivery.delivery.attention if order_delivery.delivery.attention else ''
                phone = order_delivery.delivery.phone if order_delivery.delivery.phone else ''
            else:
                row1_info1 = ''
                row1_info2 = order.customer.name if order.customer.name else ''
                row1_info2 += '\n' + order_delivery.name if order_delivery.name else ''
                row2_info1 = ''
                row2_info2 = Paragraph(remove_none(order_delivery.address.replace('\n', '<br />\n') if order_delivery.address else ''),
                                       styles['CustomStyle'])
                attention = order_delivery.attention if order_delivery.attention else contact.name if contact else ''
                phone = order_delivery.phone if order_delivery.phone else ''
        elif contact:
            row1_info1 = ''
            row1_info2 = Paragraph(remove_none(contact.company_name if contact.company_name else ''), styles['CustomStyle'])
            row2_info1 = ''
            row2_info2 = Paragraph(remove_none(contact.address.replace('\n', '<br />\n') if contact.address else ''),
                                   styles['CustomStyle'])
            attention = contact.name if contact.name else ''
            phone = contact.phone if contact.phone else ''

        header_data.append([row1_info1, row1_info2])
        header_data.append(['', ''])
        header_data.append([row2_info1, row2_info2])
        header_data.append(['', ''])
        header_data.append(['', ''])
        header_data.append(['', ''])
        row5_info2 = 'ATTN: ' + attention
        row5_info2 += '\nTEL   : ' + phone
        header_data.append(['', row5_info2])
        header_table = Table(header_data, colWidths=[20, 330], rowHeights=14)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 17),
             ('BOTTOMPADDING', (0, -1), (-1, -1), 20),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 22, doc.height + doc.topMargin - h - 80)

        # ===========================Order Master ========================
        header_data = []
        row1_info1 = 'D/O NO                :'
        row1_info2 = remove_none(order.document_number)
        header_data.append([row1_info1, row1_info2])

        row2_info1 = 'DATE                   :'
        row2_info2 = order.document_date.strftime('%d %b %Y').upper() if order.document_date else ' / / '
        header_data.append([row2_info1, row2_info2])

        row3_info1 = 'SHIPPED'
        row3_info2 = ' '
        header_data.append([row3_info1, row3_info2])

        row4_info1 = Paragraph('FROM : ', styles['RightAlign'])
        row4_info2 = order.ship_from.name if order.ship_from else ''
        header_data.append([row4_info1, row4_info2])

        row5_info1 = Paragraph('TO : ', styles['RightAlign'])
        row5_info2 = order.ship_to.name if order.ship_to else ''
        header_data.append([row5_info1, row5_info2])

        row6_info1 = Paragraph('VIA :', styles['RightAlign'])
        row6_info2 = order.via if order.via else ''
        header_data.append([row6_info1, row6_info2])

        header_data.append(['PAGE                  :', ''])

        header_table = Table(header_data, colWidths=[85, 135], rowHeights=14)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin + 300, doc.height + doc.topMargin - h - 80)
        title_data = []
        title_row1 = ['LN', 'CARTON NO.', 'PART NO.', 'CUSTOMER P/O NO.', 'QUANTITY']
        title_data.append(title_row1)
        title_row2 = ['', '', 'DESCRIPTION', '', '(' + measure + ')']
        title_data.append(title_row2)

        title_table = Table(title_data, colWidths=[28, 80, 205, 140, 80])
        title_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (4, -1), 'CENTER'),
             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('LINEBELOW', (0, 1), (-1, 1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 5),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w, h = title_table.wrap(doc.width, doc.topMargin)
        title_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - 210)

    def print_report(self, order_id, print_header, company_id, part_group):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=42,
                                leftMargin=60,
                                topMargin=285,
                                bottomMargin=42,
                                pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Regular', fontName=s.REPORT_FONT, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=10, leading=12))
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='JustifyAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='BoldText', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        # Our container for 'Flowable' objects
        elements = []
        order = Order.objects.get(pk=order_id)
        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id, order_id=order_id
                                                   ).select_related('order').order_by('line_number')

        # Draw Content of PDF
        # ===========================Order Items Data ===========================
        item_list_data = []
        total_carton = 0
        total_quantity = 0
        measure = ''
        # GET MEASURE
        measure = order_item_list.first().item.purchase_measure.code if order_item_list.first().item \
            and order_item_list.first().item.purchase_measure \
            else ''
        line_count = 0
        if order_item_list:
            for index, my_item in enumerate(order_item_list):
                if my_item.carton_no:
                    total_carton += 1
                if my_item.quantity:
                    quantity = float(my_item.quantity) if my_item.quantity else 0
                    total_quantity += quantity
                item_data = [my_item.line_number if my_item.line_number else '',
                             my_item.carton_no if my_item.carton_no else '',
                             my_item.item.code if my_item.item.code else '',
                             my_item.customer_po_no if my_item.customer_po_no else '',
                             intcomma("%.2f" % quantity)]
                item_list_data.append(item_data)
                line_count += 1
                item_desc = my_item.item.short_description if my_item.item.short_description else ''

                if int(part_group):
                    item_data = ['', '', item_desc, 'MODEL: ' + my_item.item.category.name if my_item.item.category else 'MODEL: ', '']
                    item_list_data.append(item_data)
                    line_count += 1
                else:
                    item_data = ['', '', item_desc, '', '']
                    item_list_data.append(item_data)
                    line_count += 1

                if line_count > MAX_LINE:
                    line_count = 0

        # Create the table
        item_table = Table(item_list_data, colWidths=[28, 80, 205, 140, 80], rowHeights=15)
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (4, 0), (4, -1), 'CENTER'),
             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 5),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0

        item_list_data = []
        item_data = ['', '', 'TOTAL:', intcomma("%.2f" % total_quantity)]
        item_list_data.append(item_data)
        item_table = Table(item_list_data, colWidths=[68, 70, 250, 145])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('ALIGN', (0, 0), (3, 0), 'RIGHT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 5),
             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
             ('LINEABOVE', (0, 0), (3, 0), 0.5, colors.black),
             ('LINEBELOW', (0, 0), (3, 0), 0.5, colors.black),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(item_table)
        line_count += 1
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0
        item_list_data = []
        item_list_data.append(
            [Paragraph('REMARKS:', styles['BoldText']), ''])
        item_list_data.append(
            [Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '', styles['LeftAlign']),
             ''])
        # Create the table
        item_table = Table(item_list_data, colWidths=[390, 145])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
             ('LEFTPADDING', (0, 0), (-1, -1), 5),
             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        line_count += 8
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0
        elements.append(item_table)
        # ===========================Signature Data============================
        sign_data = []
        sign_data.append(
            ['Received the above items in good order & condition ',
             Paragraph('for', styles['ItalicText']),
             order.company.name.upper() if order.company.name else ''])
        sign_data.append(['', '', ''])
        if order and order.company:
            if order.company.footer_logo:
                try:
                    path_footer_logo = s.MEDIA_ROOT + str(order.company.footer_logo)
                    sign_data.append(['', '', Image(path_footer_logo, 140, 50)])
                except Exception as e:
                    sign_data.append(['', '', ''])
                    sign_data.append(['', '', ''])
                    print(e)
            else:
                sign_data.append(['', '', ''])
                sign_data.append(['', '', ''])

        information = "SHOP & CUSTOMER" + "'S" + " SIGNATURE/DATE."
        sign_data.append([information, '', "AUTHORISED SIGNATURE"])
        sign_table = Table(sign_data, colWidths=[288, 30, 215])
        sign_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
             ('LINEABOVE', (0, -1), (0, -1), 0.25, colors.black),
             ('LINEABOVE', (-1, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        line_count += 4
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0
        elements.append(sign_table)
        # ===========================End Coding============================
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, order_id=order_id, print_header=print_header, company_id=company_id, measure=measure),
                  onLaterPages=partial(self._header_footer, order_id=order_id, print_header=print_header, company_id=company_id, measure=measure),
                  canvasmaker=partial(NumberedPage, adjusted_height=-33, adjusted_width=-102, adjusted_caption=''))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
