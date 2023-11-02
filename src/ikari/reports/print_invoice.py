from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import Order, OrderItem, OrderDelivery
from contacts.models import Contact
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from companies.models import Company


colWidths = [30, 170, 175, 110, 45]
MAX_LINE = 27


class Print_Invoice:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, order_id, print_header, company_id):
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
        header_data = []
        row2_info1 = "MESSERS:"
        header_data.append([row2_info1, ''])
        if order:
            # order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
            #                                               order_id=order_id).first()
            row5_info1 = 'ATTN: '
            if order.customer:
                contact = Contact.objects.filter(is_hidden=0, company_id=company_id, customer_id=order.customer.id).first()

                customer_name = order.customer.name if order.customer.name else ''
                # customer_name += '<br />' + order_delivery.name if order_delivery and order_delivery.name else ''
                row3_info1 = Paragraph(customer_name if customer_name else '', styles['LeftAlign'])
                row4_info1 = Paragraph(order.customer.address.replace('\n', '<br />\n') if order.customer.address else '', styles['LeftAlign'])
                row5_info1 = row5_info1 + contact.attention if contact else row5_info1

            header_data.append(['', row3_info1])
            # header_data.append(['', ''])
            header_data.append(['', row4_info1])

            header_data.append(['', ''])
            header_data.append(['', ''])
            header_data.append(['', ''])
            header_data.append(['', row5_info1])

        header_table = Table(header_data, colWidths=[20, 330], rowHeights=15)
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

        # == == == == == == == == == == == == == =Header Title RIGHT== == == == == == == == == == == == == =
        header_data = []
        if order:
            row3_info2 = 'CO.REG.NO.'
            row3_info3 = ': ' + order.company.company_number if order.company.company_number else ''
            header_data.append([row3_info2, row3_info3])

            row4_info2 = 'INVOICE NO.'
            row4_info3 = ': ' + order.document_number if order.document_number else ''
            header_data.append([row4_info2, row4_info3])

            row5_info2 = 'DATE'
            row5_info3 = ': ' + order.document_date.strftime('%d %b %Y').upper()
            header_data.append([row5_info2, row5_info3])

            row6_info2 = 'TERMS'
            row6_info3 = ': ' + str(order.customer.payment_term) + ' days' if order.customer else '0' + ' days'
            header_data.append([row6_info2, row6_info3])

            row7_info2 = 'DELIVERY'
            row7_info3 = ': ' + order.note if order.note else ''
            header_data.append([row7_info2, row7_info3])

            row8_info2 = 'PAYMENT'
            row8_info3 = ': '
            header_data.append([row8_info2, row8_info3])

            header_data.append(['PAGE', ': '])

        header_table = Table(header_data, colWidths=[63, 137], rowHeights=15)
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin + 340, doc.height + doc.topMargin - h - 80)
        # ===========================Order Title ===========================
        title_data = []
        title_row1 = ['LN.', 'CUST. P/O NO.', 'PART NO', 'QUANTITY', '']
        title_data.append(title_row1)
        title_row2 = ['', 'S/O NO.', 'DESCRIPTION', '', '']
        title_data.append(title_row2)
        # title_row2 = ['', 'REMARKS', '', '', '', '']
        # title_data.append(title_row2)
        # Create the table
        title_table = Table(title_data, colWidths=colWidths)
        title_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
             ('ALIGN', (3, 0), (4, 0), 'CENTER'),
             ('SPAN', (3, 0), (4, 0)),
             ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
             ]))
        w, h = title_table.wrap(doc.width, doc.topMargin)
        title_table.drawOn(canvas, doc.leftMargin - 20, doc.height + doc.topMargin - h - 192)
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
                                topMargin=268,
                                bottomMargin=42,
                                pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='BoldText', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomHeaderStyle', fontName=s.REPORT_FONT_BOLD, fontSize=s.REPORT_FONT_SIZE, leading=22,
                                  alignment=TA_CENTER))
        # Our container for 'Flowable' objects
        elements = []
        company = Company.objects.get(id=company_id)
        order = Order.objects.get(id=order_id)
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
                                       intcomma("%.2f" % my_item.quantity), my_item.item.report_measure.code])
                item_table = Table(item_list_data, colWidths=colWidths, rowHeights=20)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
                     ('ALIGN', (4, 0), (4, 0), 'LEFT'),
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
                                           my_item.item.short_description[:30] if my_item.item.short_description else '', ''])
                    item_list_data.append(['', '',
                                           'MODEL: ' + my_item.item.category.name if my_item.item.category else 'MODEL: ', '', ''])
                else:
                    item_list_data.append(['', my_item.refer_number if my_item.refer_number else '',
                                           my_item.item.short_description if my_item.item.short_description else '', '', ''])

                # Create the table
                item_table = Table(item_list_data, colWidths=colWidths, rowHeights=15)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (3, 0), (-1, -1), 'LEFT'),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ]))
                elements.append(item_table)
                line_count += 1
                if line_count > MAX_LINE:
                    elements.append(PageBreak())
                    line_count = 0
            # ===========================Footer Data============================
            footer_data = []
            footer_data.append(['', '', 'TOTAL :',
                                intcomma("%.2f" % total_quantity), ''])

            footer_table = Table(footer_data, colWidths=colWidths, rowHeights=20)
            footer_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                 ('TOPPADDING', (0, 0), (-1, 0), 5),
                 ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ]))
            elements.append(footer_table)
            line_count += 1
            if line_count > MAX_LINE:
                elements.append(PageBreak())
                line_count = 0

            # ===========================Remarks + Signature/Footer Data============================
            remark_data = []
            remark_data.append(['', '', ''])
            remark_data.append(['', '', ''])
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
                        remark_data.append(['', '', ''])
                        remark_data.append(['', '', ''])
                        print(e)
                else:
                    remark_data.append([Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '', styles['LeftAlign']),
                                        '', ''])
                    remark_data.append(['', '', ''])
                    remark_data.append(['', '', ''])
            if 'IKARI ENTERPRISE PTE LTD' in order.company.name:
                remark_data.append(['', '', 'Shibata Mitsuhito / Managing Director'])
            else:
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
                 ('TOPPADDING', (0, 0), (-1, 0), 10),
                 ('LINEABOVE', (-2, -1), (-1, -1), 0.25, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.transparent),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ]))
            line_count += 7
            if line_count > MAX_LINE:
                elements.append(PageBreak())
                line_count = 0
            elements.append(remark_table)
        # ===========================End Coding============================
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, order_id=order_id, print_header=print_header, company_id=company_id),
                  onLaterPages=partial(self._header_footer, order_id=order_id, print_header=print_header, company_id=company_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=-37, adjusted_width=-78, adjusted_caption=''))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
