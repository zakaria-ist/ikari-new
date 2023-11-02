from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import Order, OrderItem, OrderDelivery
from companies.models import Company
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from contacts.models import Contact
from utilities.common import round_number

colWidths_main = [45, 45, 135, 148, 62, 50, 50]
colWidths_muto = [45, 45, 125, 128, 62, 40, 45, 45]
MAX_LINE = 24


def remove_none(param):
    if param is None or param == 'None' or param == 'none':
        param = ''
    return param


class Print_Packing_List:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, order_id, print_header, company_id, uom, is_muto):
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
                canvas.line(40, doc.height + doc.topMargin - 45, doc.width + doc.leftMargin + 22,
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
                    row1_info1 = Paragraph(order.company.name.upper() if order.company.name else '',
                                           styles['CustomHeader'])
                    header_data.append([row1_info1])

                    row2_info1 = Paragraph(order.company.address if order.company.address else '', styles['LeftAlign'])
                    header_data.append([row2_info1])

                    row3_info1 = "TEL: " + order.company.phone if order.company.phone else ''
                    row3_info1 = row3_info1 + "        " + "FAX: " + order.company.fax if order.company.fax else ''
                    header_data.append([row3_info1])

                    row4_info1 = "GST / Co Reg No : " + order.company.company_number if order.company.company_number else ''
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
        row1_info1 = Paragraph("PACKING LIST", styles['CustomTitle'])
        header_data.append([row1_info1])

        header_table = Table(header_data, colWidths=[530])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 12, doc.height + doc.topMargin - h - 50)

        # ===========================Header Title Left===========================
        contact = Contact.objects.filter(is_hidden=0, company_id=company_id, customer_id=order.customer.id).first()
        order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                      order_id=order_id).first()
        header_data = []

        row2_info1 = "SHIPPED TO :"
        header_data.append([row2_info1, ''])

        if order_delivery:
            if order_delivery.delivery_id:
                customer_name = order.customer.name if order.customer.name else ''
                customer_name += '\n' + order_delivery.delivery.name if order_delivery.delivery.name else ''
                address_info1 = Paragraph(remove_none(order_delivery.delivery.address.replace('\n', '<br />\n')
                                                      if order_delivery.delivery.address else ''), styles['CustomStyle'])
                attention = order_delivery.delivery.attention if order_delivery.delivery.attention else ''
                phone = order_delivery.delivery.phone if order_delivery.delivery.phone else ''
            else:
                customer_name = order.customer.name if order.customer.name else ''
                customer_name += '\n' + order_delivery.name if order_delivery.name else ''
                address_info1 = Paragraph(remove_none(order_delivery.address.replace('\n', '<br />\n')
                                                      if order_delivery.address else ''), styles['CustomStyle'])
                attention = order_delivery.attention if order_delivery.attention else contact.name if contact else ''
                phone = order_delivery.phone if order_delivery.phone else ''
        elif contact:
            customer_name = Paragraph(remove_none(contact.company_name if contact.company_name else ''), styles['CustomStyle'])
            address_info1 = Paragraph(remove_none(contact.address.replace('\n', '<br />\n') if contact.address else ''), styles['CustomStyle'])
            attention = contact.name if contact.name else ''
            phone = contact.phone if contact.phone else ''

        header_data.append(['', customer_name])
        header_data.append(['', ''])
        header_data.append(['', ''])
        header_data.append(['', address_info1])
        header_data.append(['', ''])
        header_data.append(['', ''])
        header_data.append(['', ''])
        row5_info1 = 'ATTN: ' + attention
        row5_info1 += '\nTEL   : ' + phone
        header_data.append(['', row5_info1])

        header_table = Table(header_data, colWidths=[20, 330], rowHeights=14)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 17),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('VALIGN', (0, 0), (0, 0), 'BOTTOM'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 22, doc.height + doc.topMargin - h - 80)

        # == == == == == == == == == == == == == =Header Title RIGHT== == == == == == == == == == == == == =
        header_data = []
        if order:
            row3_info2 = 'PACKING NO.'
            row3_info3 = ': ' + order.document_number if order.document_number else ''
            header_data.append([row3_info2, row3_info3])

            row4_info2 = 'DATE'
            row4_info3 = ': ' + order.document_date.strftime('%d %b %Y').upper() if order.document_date else ''
            header_data.append([row4_info2, row4_info3])

            row5_info2 = 'INVOICE NO.'
            row5_info3 = ': ' + order.document_number if order.document_number else ''
            header_data.append([row5_info2, row5_info3])

            row6_info2 = 'DELIVERY'
            row6_info3 = ': ' + order.note if order.note else ''
            header_data.append([row6_info2, row6_info3])

            row7_info2 = 'SHIPPED'
            row7_info3 = ' '
            header_data.append([row7_info2, row7_info3])

            row8_info2 = Paragraph('FROM', styles['RightAlign'])
            row8_info3 = ': ' + (order.ship_from.name if order.ship_from else '')
            header_data.append([row8_info2, row8_info3])

            row9_info2 = Paragraph('TO', styles['RightAlign'])
            row9_info3 = ': ' + (order.ship_to.name if order.ship_to else '')
            header_data.append([row9_info2, row9_info3])

            row10_info2 = Paragraph('VIA', styles['RightAlign'])
            row10_info3 = ': ' + (order.via if order.via else '')
            header_data.append([row10_info2, row10_info3])

            header_data.append(['PAGE', ': '])

        header_table = Table(header_data, colWidths=[85, 135], rowHeights=14)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin + 300, doc.height + doc.topMargin - h - 72)
        # ===========================Order Title ===========================
        title_data = []
        if is_muto:
            title_row1 = ['CTN NO.', 'P/L NO.', 'PART NO', 'CUSTOMER P/O NO.', 'QUANTITY', 'TOTAL', 'NET WT.', 'GRS WT.']
            title_data.append(title_row1)
            title_row2 = ['COUNTRY', 'M3', 'DESCRIPTION', '', Paragraph('(' + uom + ')', styles['RightAlign']),
                        Paragraph('CTN', styles['RightAlign']), Paragraph('(KGS)', styles['RightAlign']), Paragraph('(KGS)', styles['RightAlign'])]
            title_data.append(title_row2)
        else:
            title_row1 = ['CTN NO.', 'P/L NO.', 'PART NO', 'CUSTOMER P/O NO.',
                          Paragraph('QUANTITY', styles['RightAlign']), Paragraph('TOTAL', styles['RightAlign']), Paragraph('NET WGHT', styles['RightAlign'])]
            title_data.append(title_row1)
            title_row2 = ['COUNTRY', 'M3', 'DESCRIPTION', '', Paragraph('(' + uom + ')', styles['RightAlign']),
                        Paragraph('CTN', styles['RightAlign']), Paragraph('(KGS)', styles['RightAlign'])]
            title_data.append(title_row2)
        # Create the table
        colWidths = colWidths_main
        if is_muto:
            colWidths = colWidths_muto
        title_table = Table(title_data, colWidths=colWidths, rowHeights=18)
        title_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        w, h = title_table.wrap(doc.width, doc.topMargin)
        title_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - 220)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, order_id, print_header, company_id, part_group):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=42,
                                leftMargin=60,
                                topMargin=295,
                                bottomMargin=42,
                                pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='BoldText', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomHeaderStyle', fontName=s.REPORT_FONT_BOLD, fontSize=18, leading=22,
                                  alignment=TA_CENTER))
        # Our container for 'Flowable' objects
        elements = []
        is_muto = False
        colWidths = colWidths_main
        company = Company.objects.get(pk=company_id)
        if 'MUTO SINGAPORE' in company.name:
            is_muto = True
        if is_muto:
            colWidths = colWidths_muto
        order = Order.objects.get(pk=order_id)
        order_item_list = OrderItem.objects.select_related('order').filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                                           order_id=order_id).order_by('line_number')

        # Draw Content of PDF
        # ===========================Order Items Data ===========================
        item_data = []
        my_style = [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
            ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        if is_muto:
            my_style = [
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (-4, 0), (-1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]

        total_qty = 0
        total_carton = 0
        total_weight = 0
        total_gr_weight = 0
        line_count = 0
        for item in order_item_list:
            quantity = item.quantity if item.quantity else 0
            carton = item.carton_total if item.carton_total else 0
            net_weight = item.net_weight if item.net_weight else 0
            gross_weight = item.gross_weight if item.gross_weight else 0
            m3_number = item.m3_number if item.m3_number else 0

            total_qty += quantity
            total_carton += carton
            total_weight += net_weight
            total_gr_weight += gross_weight
            if is_muto:
                item_data.append(
                    [item.carton_no if item.carton_no else 0, item.pallet_no if item.pallet_no else '',
                    item.item.code, Paragraph(item.customer_po_no, styles['LeftAlign']),
                    intcomma("%.2f" % round_number(quantity)),
                    intcomma("%.0f" % round_number(carton)),
                    intcomma("%.2f" % round_number(net_weight)),
                    intcomma("%.2f" % round_number(gross_weight))])
                if int(part_group):
                    item_data.append(
                        [item.origin_country.code if item.origin_country else '',
                        intcomma("%.2f" % round_number(m3_number)),
                        Paragraph(item.item.short_description, styles['LeftAlign']) if item.item.short_description else '', '',
                        '', 'MODEL: ' + item.item.category.name if item.item.category else 'MODEL: ', '', ''])
                else:
                    item_data.append(
                        [item.origin_country.code if item.origin_country else '',
                        intcomma("%.2f" % round_number(m3_number)),
                        Paragraph(item.item.short_description, styles['LeftAlign']) if item.item.short_description else '', '',
                        '', '', '', ''])
            else:
                item_data.append(
                    [item.carton_no if item.carton_no else 0, item.pallet_no if item.pallet_no else '',
                    item.item.code, Paragraph(item.customer_po_no, styles['LeftAlign']),
                    intcomma("%.2f" % round_number(quantity)),
                    intcomma("%.0f" % round_number(carton)),
                    intcomma("%.2f" % round_number(net_weight))])
                if int(part_group):
                    item_data.append(
                        [item.origin_country.code if item.origin_country else '',
                        intcomma("%.2f" % round_number(m3_number)),
                        Paragraph(item.item.short_description, styles['LeftAlign']) if item.item.short_description else '', '',
                        '', 'MODEL: ' + item.item.category.name if item.item.category else 'MODEL: ', ''])
                else:
                    item_data.append(
                        [item.origin_country.code if item.origin_country else '',
                        intcomma("%.2f" % round_number(m3_number)),
                        Paragraph(item.item.short_description, styles['LeftAlign']) if item.item.short_description else '', '',
                        '', '', ''])
            uom = item.item.inv_measure.code if item.item.inv_measure else 'PCS'
        item_data_small_table = Table(item_data, colWidths=colWidths, rowHeights=20)
        for i, row in enumerate(item_data):
            line_count += 1
            if line_count > MAX_LINE:
                line_count = 0
            if i % 2 != 0:
                my_style.append(('SPAN', (2, i), (3, i)), )

        item_data_small_table.setStyle(TableStyle(my_style))
        elements.append(item_data_small_table)
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0
        # ===========================Footer Data============================
        footer_data = []
        if is_muto:
            footer_data.append(['', '', '', 'TOTAL:',
                                intcomma("%.2f" % round_number(total_qty)),
                                intcomma("%.0f" % round_number(total_carton)),
                                intcomma("%.2f" % round_number(total_weight)),
                                intcomma("%.2f" % round_number(total_gr_weight))])
        else:
            footer_data.append(['', '', '', 'TOTAL:',
                                intcomma("%.2f" % round_number(total_qty)),
                                intcomma("%.0f" % round_number(total_carton)),
                                intcomma("%.2f" % round_number(total_weight))])

        footer_table = Table(footer_data, colWidths=colWidths, rowHeights=24)
        footer_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('TOPPADDING', (0, 0), (-1, 0), 5),
             ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        elements.append(footer_table)
        line_count += 1
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0
        # ===========================Remarks + Signature/Footer Data============================
        remark_data = []
        remark_data.append([Paragraph('REMARKS:', styles['BoldText']),
                            Paragraph('for', styles['ItalicText']),
                            Paragraph(order.company.name.upper(), styles['LeftAlign'])])
        if order and order.company:
            if order.company.footer_logo:
                try:
                    path_footer_logo = s.MEDIA_ROOT + str(order.company.footer_logo)
                    image = Image(path_footer_logo, 170, 50)
                    remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '',
                                                  styles['LeftAlign']), '', image])
                except Exception as e:
                    remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '',
                                                  styles['LeftAlign']), '', ''])
                    remark_data.append(['', '', ''])
                    remark_data.append(['', '', ''])
                    print(e)
            else:
                remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '',
                                              styles['LeftAlign']), '', ''])
                remark_data.append(['', '', ''])
                remark_data.append(['', '', ''])

        remark_data.append(['', '', 'AUTHORISED SIGNATURE'])
        remark_table = Table(remark_data, colWidths=[320, 25, 190])
        remark_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
             ('ALIGN', (-1, -2), (-1, -1), 'CENTER'),
             ('RIGHTPADDING', (-1, 1), (-1, 1), 0),
             ('ALIGN', (-1, 1), (-1, 1), 'RIGHT'),
             ('TOPPADDING', (0, 0), (-1, 0), 10),
             ('LINEABOVE', (-2, -1), (-1, -1), 0.25, colors.black),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ]))
        line_count += 6
        if line_count > MAX_LINE:
            elements.append(PageBreak())
            line_count = 0
        elements.append(remark_table)

        doc.build(elements,
                  onFirstPage=partial(self._header_footer, order_id=order_id, print_header=print_header, company_id=company_id, uom=uom, is_muto=is_muto),
                  onLaterPages=partial(self._header_footer, order_id=order_id, print_header=print_header, company_id=company_id, uom=uom, is_muto=is_muto),
                  canvasmaker=partial(NumberedPage, adjusted_height=-51, adjusted_width=-97, adjusted_caption=''))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
