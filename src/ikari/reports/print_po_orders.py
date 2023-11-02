from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from orders.models import Order, OrderItem, OrderDelivery
from customers.models import Delivery
from contacts.models import Contact
from companies.models import Company
from functools import partial
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime
from utilities.common import get_order_filter_range, update_po_address, round_number, get_decimal_place

rowHeights = 13


class Print_PO_Orders:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, print_header, company_id):
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
        company = Company.objects.get(pk=company_id)

        # ===========================Header Image ===========================
        if print_header == '1':
            canvas.line(40, doc.height + doc.topMargin - 45, doc.width + doc.leftMargin + 20,
                        doc.height + doc.topMargin - 45)
            logo_exist = False
            if company:
                if company.header_logo:
                    try:
                        path_header_logo = s.MEDIA_ROOT + str(company.header_logo)
                        canvas.drawImage(path_header_logo, 65, doc.height + doc.topMargin - 35, 500, 60)
                        logo_exist = True
                    except Exception as e:
                        print(e)
                        logo_exist = False

                if not logo_exist:
                    header_data = []
                    row1_info1 = Paragraph(company.name.upper() if company.name else '',
                                           styles['CustomHeader'])
                    header_data.append([row1_info1])

                    row2_info1 = Paragraph(company.address if company.address else '', styles['LeftAlign'])
                    header_data.append([row2_info1])

                    row3_info1 = "TEL: " + company.phone if company.phone else ''
                    row3_info1 = row3_info1 + "        " + "FAX: " + company.fax if company.fax else ''
                    header_data.append([row3_info1])

                    row4_info1 = "GST Co Reg No : " + company.company_number if company.company_number else ''
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
                    header_table.drawOn(canvas, doc.leftMargin + 60, doc.height + doc.topMargin - 40)
        # ===========================Header Title ===========================
        header_data = []
        row1_info1 = Paragraph("PURCHASE ORDER", styles['CustomTitle'])
        row1_info2 = ''
        header_data.append([row1_info1, row1_info2])

        header_table = Table(header_data, colWidths=[470, 60])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 12, doc.height + doc.topMargin - h - 60)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, from_order_id, to_order_id, print_header, address, company_id, remove_address, signature, part_group):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(s.BASE_DIR, "static/fonts/arial-italic.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=60, topMargin=130, bottomMargin=42, pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ItalicText', fontName=s.REPORT_FONT_ITALIC, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomHeaderStyle', fontName=s.REPORT_FONT_BOLD, fontSize=18, leading=22,
                                  alignment=TA_CENTER))
        # Our container for 'Flowable' objects
        elements = []
        item_key = 'document_number'

        if from_order_id and int(from_order_id) is not 0:
            from_order = Order.objects.get(pk=int(from_order_id))
            doc_no_from = from_order.document_number
        else:
            doc_no_from = ''

        if to_order_id and int(to_order_id) is not 0:
            to_order = Order.objects.get(pk=int(to_order_id))
            doc_no_to = to_order.document_number
        else:
            doc_no_to = ''

        doc_numbers = get_order_filter_range(2, company_id, doc_no_from, doc_no_to, item_key)

        for doc_no in doc_numbers:
            order = Order.objects.filter(document_number=doc_no, is_hidden=0).first()
            order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                       order__id=order.id).order_by('line_number')

            # ===========================Header Title===========================
            pageNumber = 1
            header_table, title_table = self.print_order_header(order, company_id, pageNumber)
            elements.append(header_table)
            elements.append(title_table)

            # Draw Content of PDF
            footer_line_count = 0
            delivery_info = None
            if int(remove_address):
                update_po_address(order.id)
            else:
                if int(address):
                    try:
                        delivery_info = Delivery.objects.get(is_hidden=0, id=int(address))
                        update_po_address(order.id, int(address))
                    except Exception as e:
                        print(e)
                        delivery_info = None
                else:
                    try:
                        delivery_info = OrderDelivery.objects.get(is_hidden=0, order_id=order.id)
                        if delivery_info.delivery_id:
                            delivery_info = Delivery.objects.get(pk=delivery_info.delivery_id)
                    except Exception as e:
                        print(e)
                        delivery_info = None

                if delivery_info:
                    delivery_data = []
                    delivery_data.append(['SHIP TO : ', Paragraph(delivery_info.name if delivery_info.name else '', styles['LeftAlign'])])
                    delivery_data.append(['', Paragraph(delivery_info.address.replace('\n', '<br />\n') if delivery_info.address else '',
                                                        styles['LeftAlign'])])
                    try:
                        delivery_data.append(['', Paragraph(delivery_info.attention if delivery_info.attention else '', styles['LeftAlign'])])
                    except Exception as e:
                        print(e)
                    delivery_data.append(['', Paragraph(delivery_info.phone if delivery_info.phone else '', styles['LeftAlign'])])

                    delivery_table = Table(delivery_data, colWidths=[70, 480])
                    footer_line_count = footer_line_count + 4

            # ===========================Remarks Data============================
            remark_data = []
            remark_data.append(['REMARK : ', Paragraph(order.remark.replace('\n', '<br />\n') if order.remark else '', styles['LeftAlign'])])
            remark_data.append(['', ''])
            remark_data.append(
                [Paragraph('Please CONFIRM your acknowledgement with in 3 days of Purchase Order issued date. '
                           'Failure to do so will be considered as your acceptance of all terms on the face of the '
                           'Purchase Order.', styles['LeftAlign']), ''])
            remark_data.append(['', ''])
            remark_table = Table(remark_data, colWidths=[70, 480])
            footer_line_count = footer_line_count + 5
            # ===========================Signature Data============================
            sign_data = []
            if int(signature):
                sign_data.append(['CONFIRMED BY : ', Paragraph('for', styles['ItalicText']), order.company.name.upper(), ''])
                if order and order.company:
                    if order.company.footer_logo:
                        try:
                            path_footer_logo = s.MEDIA_ROOT + str(order.company.footer_logo)
                            sign_data.append(['', '', Image(path_footer_logo, 170, 50), ''])
                        except Exception as e:
                            sign_data.append(['', '', '', ''])
                            sign_data.append(['', '', '', ''])
                            sign_data.append(['', '', '', ''])
                            print(e)
                    sign_data.append(['PLEASE STAMP, SIGN & RETURN THE DUPLICATE.', '', 'AUTHORISED SIGNATURE', ''])
            else:
                sign_data.append(['CONFIRMED BY : ', '', '', ''])
                if order and order.company:
                    sign_data.append(['', '', '', ''])
                    sign_data.append(['', '', 'This is a Computer generated Purchase order', ''])
                    sign_data.append(['', '', 'No Signature is required', ''])
                    sign_data.append(['PLEASE STAMP, SIGN & RETURN THE DUPLICATE.', '', order.company.name.upper(), ''])

            sign_table = Table(sign_data, colWidths=[240, 70, 200, 30])
            footer_line_count = footer_line_count + 5

            # ===========================Order Items Data ===========================
            item_list_data = []
            total_quantity = 0
            line_count = 0
            for index, my_item in enumerate(order_item_list):
                item_list_data = []
                item_data = []
                total_quantity += my_item.quantity
                if not my_item.price:
                    my_item.price = 0

                # if my_item.wanted_date:
                decimal_place = get_decimal_place(my_item.order.currency)
                date_wanted = my_item.wanted_date.strftime('%d/%m/%Y') if my_item.wanted_date else datetime.date.today().strftime('%d/%m/%Y')
                item_data = [my_item.line_number, my_item.item.code, date_wanted,
                             intcomma("%.2f" % round_number(my_item.quantity)),
                             intcomma("%.5f" % round_number(my_item.price, 5)),
                             intcomma(decimal_place % round_number(my_item.amount))]
                item_list_data.append(item_data)
                line_count = line_count + 1
                item_table = Table(item_list_data, colWidths=[20, 210, 80, 75, 75, 75], rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                    ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                    ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                elements.append(item_table)

                item_list_data = []
                item_desc = []
                if my_item.item.name:
                    if len(my_item.item.name) > 45:
                        item_desc = my_item.item.name.split(' ', 1)
                        if len(item_desc) == 1:
                            item_desc = my_item.item.name.split('-', 1)
                    else:
                        item_desc = [my_item.item.name]
                else:
                    item_desc = ['']
                
                if len(item_desc[0]) > 45:
                    item_desc = [my_item.item.name[:45], my_item.item.name[45:]]
                if int(part_group):
                    item_data = [item_desc[0], my_item.customer_po_no, '', 'MODEL: ' + my_item.item.category.name if my_item.item.category else 'MODEL: ', '']
                else:
                    item_data = [item_desc[0], my_item.customer_po_no, '', '', '']
                item_list_data.append(item_data)
                line_count = line_count + 1
                
                if len(item_desc) > 1:
                    item_desc = [item_desc[1][:45], item_desc[1][45:]]
                    for x in range(0, len(item_desc)):
                        item_data = [item_desc[x], '', '', '', '']
                        item_list_data.append(item_data)
                        line_count = line_count + 1

                remark = my_item.description
                if remark and remark != '':
                    item_data = [remark, '', '', '', '']
                    item_list_data.append(item_data)
                    line_count = line_count + 1

                # Empty line
                item_data = ['', '', '', '', '']
                item_list_data.append(item_data)
                line_count = line_count + 1
                # Create the table
                item_table = Table(item_list_data, colWidths=[230, 80, 75, 75, 75], rowHeights=rowHeights)
                item_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(item_table)
                if line_count >= 30:
                    elements.append(PageBreak())
                    pageNumber = pageNumber + 1
                    header_table, title_table = self.print_order_header(order, company_id, pageNumber)
                    elements.append(header_table)
                    elements.append(title_table)
                    line_count = 0
            # ===========================Footer Data============================
            decimal_place = get_decimal_place(order.currency)
            footer_data = []
            footer_data.append(['', '', 'TOTAL:', intcomma("%.2f" % round_number(total_quantity)), '', intcomma(decimal_place % round_number(order.subtotal))])

            footer_table = Table(footer_data, colWidths=[30, 190, 90, 75, 75, 75], rowHeights=rowHeights)
            footer_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
                 ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(footer_table)
            line_count = line_count + 1
            if line_count >= 31:
                elements.append(PageBreak())
                pageNumber = pageNumber + 1
                header_table, title_table = self.print_order_header(order, company_id, pageNumber)
                elements.append(header_table)
                elements.append(title_table)
                line_count = 0
            # ===========================Delivery Data============================
            if line_count >= 32 - footer_line_count:
                elements.append(PageBreak())
                pageNumber = pageNumber + 1
                header_table, title_table = self.print_order_header(order, company_id, pageNumber)
                elements.append(header_table)
                elements.append(title_table)
                line_count = 0

            if delivery_info:
                delivery_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('SPAN', (0, -1), (0, -1)),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ]))
                elements.append(delivery_table)
            # ===========================Remarks Data============================
            remark_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('SPAN', (0, -2), (1, -2)),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))
            elements.append(remark_table)
            # ===========================Signature Data============================

            if sign_data:
                sign_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                     ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                     ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                     ('ALIGN', (-2, 3), (-2, -1), 'CENTER'),
                     ('LINEABOVE', (0, -1), (0, -1), 0.25, colors.black),
                     ('LINEABOVE', (-2, -1), (-2, -1), 0.25, colors.black),
                     ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                     ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ('RIGHTPADDING', (-1, -1), (-1, -1), 20),
                     ]))
                elements.append(sign_table)
            elements.append(PageBreak())

        # ===========================End Coding============================
        doc.build(elements, onFirstPage=partial(self._header_footer, print_header=print_header, company_id=company_id),
                  onLaterPages=partial(self._header_footer, print_header=print_header, company_id=company_id))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def print_order_header(self, order, company_id, pageNumber):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='LeftAlign', fontName=s.REPORT_FONT, fontSize=s.REPORT_FONT_SIZE, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='CustomTitle', fontName=s.REPORT_FONT_BOLD, fontSize=18, leading=22,
                                  alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CustomHeader', fontName='Times-BoldItalic', fontSize=18, leading=18,
                                  alignment=TA_LEFT))
        if order:
            header_data = []
            row1_info1 = "MESSERS:"
            row1_info2 = Paragraph('P/O NO. : ' + order.document_number, styles['LeftAlign'])
            header_data.append([row1_info1, row1_info2])
            row2_info1 = order.supplier.name if order.supplier and order.supplier.name else ''
            row2_info2 = Paragraph('DATE   : ' + order.document_date.strftime('%d %b %Y').upper(), styles['LeftAlign'])
            header_data.append([row2_info1, row2_info2])

            row4_info1 = Paragraph(order.supplier.address if order.supplier else '', styles['LeftAlign'])
            row4_info2 = 'TERMS  : ' + str(order.supplier.term_days) + ' days' if order.supplier else '0' + ' days'
            header_data.append([row4_info1, row4_info2])
            row5_info1 = 'ATTN : '
            row5_info2 = "PAGE     : " + str(pageNumber)
            if order.supplier:
                contact = Contact.objects.filter(is_hidden=0, company_id=company_id, supplier_id=order.supplier.id).first()
                if contact:
                    row5_info1 = row5_info1 + contact.name
            header_data.append([row5_info1, row5_info2])

            header_table = Table(header_data, colWidths=[365, 170], rowHeights=15)
            header_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                 ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
                 ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
                 ('FONT', (1, 0), (1, 0), s.REPORT_FONT_BOLD),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))

            title_data = []
            title_row1 = ['LN.', 'PART NO.', 'DELIVERY DATE', 'QUANTITY', 'UNIT PRICE', 'AMOUNT']
            title_data.append(title_row1)
            title_row2 = ['', 'DESCRIPTION', 'CUSTOMER P/O NO.', '(PCS)', '(' + order.currency.code + ')', '(' + order.currency.code + ')']
            title_data.append(title_row2)
            title_row2 = ['', 'REMARKS', '', '', '', '']
            title_data.append(title_row2)
            # Create the table
            title_table = Table(title_data, colWidths=[20, 210, 95, 70, 70, 70], rowHeights=rowHeights)
            title_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
                 ('LINEABOVE', (0, 0), (-1, 0), 0.25, colors.black),
                 ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
                 ('ALIGN', (3, 0), (-1, 0), 'RIGHT'),
                 ('FONTSIZE', (0, 0), (-1, -1), s.REPORT_FONT_SIZE),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ]))

            return header_table, title_table
