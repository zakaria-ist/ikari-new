from reportlab.lib.units import *
from reportlab.pdfgen import canvas


class NumberedPage(canvas.Canvas):
    _adjusted_height = 0
    _adjusted_width = 0
    _adjusted_caption = ''

    def __init__(self,  *args, **kwargs):
        self._adjusted_height = kwargs.pop('adjusted_height', 0)
        self._adjusted_width = kwargs.pop('adjusted_width', 0)
        self._adjusted_caption = kwargs.pop('adjusted_caption', '')
        self.x_position = kwargs.pop('x_position', 211 * mm - 32 + self._adjusted_width)
        self.y_position = kwargs.pop('y_position', 15 * mm + (0.2 * inch) + 600 + self._adjusted_height)
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be

        self.setFont("Arial", 10)
        self.drawRightString(self.x_position, self.y_position, self._adjusted_caption + "%d/%d" % (self._pageNumber, page_count))
