from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4, letter, landscape
from reports.numbered_page import NumberedPage
from functools import partial
from django.conf import settings as s
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class Print_Nothing:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Release the canvas
        canvas.restoreState()

    def print_not_found(self, error_type=None):
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(s.BASE_DIR, "static/fonts/arial.ttf")))
        pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(s.BASE_DIR, "static/fonts/arial-bold.ttf")))

        no_data_found = 'No data found '
        msg = no_data_found
        if error_type:
            msg += 'on the selected ' + error_type
        buffer = self.buffer
        self.pagesize = landscape(A4)
        doc = SimpleDocTemplate(buffer, rightMargin=s.REPORT_RIGHT_MARGIN, leftMargin=s.REPORT_LEFT_MARGIN, topMargin=s.REPORT_TOP_MARGIN,
                                bottomMargin=s.REPORT_BOTTOM_MARGIN, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_RIGHT, fontSize=30))
        styles.add(ParagraphStyle(name='LeftAlignBold', fontName=s.REPORT_FONT_BOLD, alignment=TA_LEFT, fontSize=30))
        text_to_print = Paragraph(msg, styles['Title'])
        elements = []
        elements.append(text_to_print)
        doc.build(elements,
                  onFirstPage=partial(self._header_footer),
                  onLaterPages=partial(self._header_footer),
                  canvasmaker=partial(NumberedPage, adjusted_height=s.REPORT_PAGE_NO_HEIGHT, adjusted_width=255))
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf
