from django.contrib.humanize.templatetags.humanize import intcomma
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from orders.models import Order, OrderItem, OrderDelivery
from reports.numbered_page import NumberedPage
from functools import partial
import datetime
from django.conf import settings as s
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities.constants import ORDER_TYPE
from contacts.models import Contact
from utilities.common import round_number


class Print_Order:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc, order_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Draw header of PDF
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=10, leading=12))
        styles.add(ParagraphStyle(name='CustomHeaderStyle', fontName=s.REPORT_FONT_BOLD, fontSize=18, leading=22, alignment=TA_CENTER))
        order = Order.objects.get(pk=order_id)
        # ===========================Header Title===========================
        header_data = []
        row1_info1 = order.company.name
        row1_info2 = ""
        row1_info3 = "Date : " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        header_data.append([row1_info1, row1_info2, row1_info3])

        row2_info1 = "Address : "
        if order.company.address:
            row2_info1 = Paragraph("Address : " + order.company.address, styles['CustomStyle'])
        row2_info2 = ""
        if int(order.order_type) == dict(ORDER_TYPE)['SALES ORDER']:
            row2_info2 = "SALES ORDER"
        elif int(order.order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
            row2_info2 = "PURCHASE ORDER"
        elif int(order.order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
            row2_info2 = "GOOD RECEIVE"
        elif int(order.order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
            row2_info2 = Paragraph("DELIVERY ORDER " + '<br/>' + "INVOICE", styles['CustomHeaderStyle'])
        row2_info3 = ""
        header_data.append([row2_info1, row2_info2, row2_info3])

        row4_info1 = "Phone : "
        if order.company.phone:
            row4_info1 = "Phone : " + order.company.phone
        if order.company.fax:
            row4_info1 = row4_info1 + "     Fax : " + order.company.fax
        row4_info2 = ""
        header_data.append([row4_info1, row4_info2, ''])

        row3_info1 = "Email : "
        if order.company.email:
            row3_info1 = "Email : " + order.company.email
        row3_info2 = ""
        row3_info3 = ""
        header_data.append([row3_info1, row3_info2, row3_info3])

        header_data.append(['', '', ''])

        header_table = Table(header_data, colWidths=[200, 200, 150])
        header_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (1, 1), (1, 1), 'CENTER'),
             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
             ('FONTSIZE', (1, 1), (1, 1), 18),
             ('FONT', (1, 1), (1, 1), s.REPORT_FONT_BOLD),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 17),
             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('SPAN', (1, 1), (1, -1)),
             ]))

        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin - 12, doc.height + doc.topMargin - h)
        # Release the canvas
        canvas.restoreState()

    def print_report(self, order_id, company_id):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=42,
                                leftMargin=46,
                                topMargin=142,
                                bottomMargin=42,
                                pagesize=self.pagesize)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CustomStyle', fontName=s.REPORT_FONT, fontSize=10, leading=12))
        # Our container for 'Flowable' objects
        elements = []
        order = Order.objects.get(pk=order_id)
        order_item_list = OrderItem.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                   order_id=order_id)

        # Draw Content of PDF
        # ===========================Customer & Supplier Data===========================
        if int(order.order_type) == dict(ORDER_TYPE)['SALES ORDER']:
            customer_data = []
            row0_info1 = "CUSTOMER INFO"
            row0_info2 = ""
            customer_data.append([row0_info1, row0_info2])

            row1_info1 = "Name :"
            row1_info2 = Paragraph(order.customer.name.upper(), styles['CustomStyle'])
            customer_data.append([row1_info1, row1_info2])

            row2_info1 = "Address : "
            row2_info2 = ""
            if order.customer.address:
                row2_info2 = Paragraph(order.customer.address.replace('\r', ''), styles['CustomStyle'])
            customer_data.append([row2_info1, row2_info2])

            row3_info1 = "Email : "
            row3_info2 = order.customer.email
            customer_data.append([row3_info1, row3_info2])

            row4_info1 = "Phone : "
            row4_info2 = order.customer.phone
            if order.customer.fax:
                row4_info2 = row4_info2 + "          Fax : " + order.customer.fax
            customer_data.append([row4_info1, row4_info2])

            customer_table = Table(customer_data, colWidths=[100, 450])
            customer_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (0, 0), 10),
                 ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ]))
            elements.append(customer_table)
        elif int(order.order_type) == dict(ORDER_TYPE)['PURCHASE ORDER']:
            supplier_data = []
            row0_info1 = "SUPPLIER INFO"
            row0_info2 = ""
            supplier_data.append([row0_info1, row0_info2])

            row1_info1 = "Name :"
            row1_info2 = order.supplier.name.upper() if order.supplier.name else ''
            supplier_data.append([row1_info1, row1_info2])

            row2_info1 = "Address : "
            row2_info2 = ""
            if order.supplier.address:
                row2_info2 = Paragraph(order.supplier.address.replace('\r', ''), styles['CustomStyle'])
            supplier_data.append([row2_info1, row2_info2])

            row3_info1 = "Email : "
            row3_info2 = order.supplier.email
            supplier_data.append([row3_info1, row3_info2])
            row4_info1 = "Phone: "
            row4_info2 = order.supplier.phone
            if order.supplier.fax:
                row4_info2 = row4_info2 + "          Fax : " + order.supplier.fax
            supplier_data.append([row4_info1, row4_info2])

            supplier_table = Table(supplier_data, colWidths=[100, 450])
            supplier_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (0, 0), 10),
                 ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ]))
            elements.append(supplier_table)
        elif int(order.order_type) == dict(ORDER_TYPE)['PURCHASE INVOICE']:
            supplier_data = []
            row0_info1 = "SUPPLIER INFO"
            row0_info2 = ""
            supplier_data.append([row0_info1, row0_info2])

            row1_info1 = "Name :"
            row1_info2 = order.supplier.name.upper() if order.supplier.name else ''
            supplier_data.append([row1_info1, row1_info2])

            row2_info1 = "Address : "
            row2_info2 = ""
            if order.supplier.address:
                row2_info2 = Paragraph(order.supplier.address.replace('\r', ''), styles['CustomStyle'])
            supplier_data.append([row2_info1, row2_info2])

            row3_info1 = "Email : "
            row3_info2 = order.supplier.email
            supplier_data.append([row3_info1, row3_info2])
            row4_info1 = "Phone: "
            row4_info2 = order.supplier.phone
            if order.supplier.fax:
                row4_info2 = row4_info2 + "          Fax : " + order.supplier.fax
            supplier_data.append([row4_info1, row4_info2])

            supplier_table = Table(supplier_data, colWidths=[100, 450])
            supplier_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (0, 0), 10),
                 ('FONT', (0, 0), (0, 0), s.REPORT_FONT_BOLD),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ]))
            elements.append(supplier_table)
        elif int(order.order_type) == dict(ORDER_TYPE)['SALES INVOICE']:
            contact = Contact.objects.filter(is_hidden=0, company_id=company_id, customer_id=order.customer.id).first()
            order_delivery = OrderDelivery.objects.filter(is_hidden=0, order__is_hidden=0, order__company_id=company_id,
                                                          order_id=order_id).first()

            customer_data = []
            row0_info1 = "CUSTOMER INFO"
            row0_info2 = ""
            row0_info3 = "DELIVERY INFO"
            row0_info4 = ""
            customer_data.append([row0_info1, row0_info2, row0_info3, row0_info4])

            row1_info1 = "Name :"
            row1_info2 = Paragraph(order.customer.name.upper(), styles['CustomStyle'])
            row1_info3 = "Name :"
            row1_info4 = ""
            if order_delivery:
                row1_info4 = Paragraph(order_delivery.name.upper(), styles['CustomStyle'])
            elif contact:
                row1_info4 = Paragraph(contact.name.upper(), styles['CustomStyle'])
            customer_data.append([row1_info1, row1_info2, row1_info3, row1_info4])

            row2_info1 = "Address : "
            row2_info2 = ""
            if order.customer.address:
                row2_info2 = Paragraph(order.customer.address.replace('\r', ''), styles['CustomStyle'])
            row2_info3 = "Address :"
            row2_info4 = ""
            if order_delivery and order_delivery.address:
                row2_info4 = Paragraph(order_delivery.address.replace('\r', ''), styles['CustomStyle'])
            elif contact and contact.address:
                row2_info4 = Paragraph(contact.address.replace('\r', ''), styles['CustomStyle'])
            customer_data.append([row2_info1, row2_info2, row2_info3, row2_info4])

            row3_info1 = "Email : "
            row3_info2 = order.customer.email
            row3_info3 = "Email :"
            row3_info4 = ""
            customer_data.append([row3_info1, row3_info2, row3_info3, row3_info4])

            row4_info1 = "Phone : "
            row4_info2 = order.customer.phone
            row4_info3 = "Phone :"
            row4_info4 = ""
            if order_delivery:
                row4_info4 = order_delivery.phone
            elif contact:
                row4_info4 = contact.phone
            customer_data.append([row4_info1, row4_info2, row4_info3, row4_info4])

            customer_table = Table(customer_data, colWidths=[50, 220, 50, 230])
            customer_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
                 ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
                 ('FONTSIZE', (0, 0), (3, 0), 10),
                 ('FONT', (0, 0), (3, 0), s.REPORT_FONT_BOLD),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                 ]))
            elements.append(customer_table)
        # ===========================Order Master ========================
        master_data = []
        master_data.append(['', '', '', '', '', ''])
        row0_info1 = "INVOICE INFO"
        master_data.append([row0_info1, '', '', '', '', ''])

        row1_info1 = "Document Number :"
        row1_info2 = order.document_number
        row1_info3 = ""
        row1_info4 = ""
        row1_info5 = "Debit Account : "
        row1_info6 = ""  # order.debit_account.name
        master_data.append([row1_info1, row1_info2, row1_info3, row1_info4, row1_info5, row1_info6])

        row2_info1 = "Document Date :  "
        row2_info2 = order.document_date.strftime('%d/%m/%Y')
        row2_info3 = ""
        row2_info4 = ""
        row2_info5 = "Credit Account : "
        row2_info6 = ""  # order.credit_account.name
        master_data.append([row2_info1, row2_info2, row2_info3, row2_info4, row2_info5, row2_info6])

        row3_info1 = "Cost Center : "
        if order.cost_center:
            row3_info2 = order.cost_center.name
        row3_info3 = ""
        row3_info4 = ""
        row3_info5 = ""
        row3_info6 = ""
        master_data.append([row3_info1, row3_info2, row3_info3, row3_info4, row3_info5, row3_info6])
        master_data.append(['', '', '', '', '', ''])

        master_table = Table(master_data, colWidths=[100, 100, 80, 80, 80, 110])
        master_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('FONTSIZE', (0, 1), (0, 1), 10),
             ('FONT', (0, 1), (0, 1), s.REPORT_FONT_BOLD),
             ]))
        elements.append(master_table)
        # ===========================Order Items Data ===========================
        item_list_data = []
        currency_header = ['', '', '', '', '', 'Currency : ' + order.currency.code]
        item_list_data.append(currency_header)
        data_header = ['Line', 'Item Code', 'Item Name', 'Quantity', 'Price', 'Total']
        item_list_data.append(data_header)
        for index, my_item in enumerate(order_item_list):
            item_data = []
            if not my_item.price:
                my_item.price = 0
            item_data = [my_item.line_number, my_item.item.code, my_item.item.name, intcomma(float(round_number(my_item.quantity))),
                         intcomma("%.5f" % round_number(my_item.price, 5)) + ' ' + order.currency.code,
                         intcomma("%.2f" % round_number(my_item.amount)) + ' ' + order.currency.code]
            item_list_data.append(item_data)

        # Create the table
        item_table = Table(item_list_data, colWidths=[30, 80, 190, 75, 80, 80])
        item_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT),
             ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
             ('FONT', (0, 0), (-1, 0), s.REPORT_FONT_BOLD),
             ('LINEBELOW', (0, -1), (-1, -1), 0.25, colors.black),
             ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
             ('LINEBELOW', (0, 1), (-1, 1), 0.25, colors.black),
             ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 5),
             ]))
        elements.append(item_table)
        # ===========================Footer Data============================
        footer_data = []
        row1_info1 = "Subtotal : "
        row1_info2 = intcomma("%.2f" % round_number(order.subtotal)) + ' ' + order.currency.code
        footer_data.append([row1_info1, row1_info2])

        row2_info1 = "Tax : "
        row2_info2 = intcomma("%.2f" % round_number(order.tax_amount)) + ' ' + order.currency.code
        footer_data.append([row2_info1, row2_info2])

        row4_info1 = "Total : "
        row4_info2 = intcomma("%.2f" % round_number(order.total)) + ' ' + order.currency.code
        footer_data.append([row4_info1, row4_info2])

        footer_table = Table(footer_data, colWidths=[400, 150])
        footer_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('BOX', (0, 0), (-1, -1), 0.25, colors.transparent),
             ('FONT', (0, 0), (-1, -1), s.REPORT_FONT_BOLD),
             ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
             ('RIGHTPADDING', (-1, 0), (-1, -1), 12),
             ]))
        elements.append(footer_table)
        doc.build(elements,
                  onFirstPage=partial(self._header_footer, order_id=order_id),
                  onLaterPages=partial(self._header_footer, order_id=order_id),
                  canvasmaker=partial(NumberedPage, adjusted_height=60))

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
