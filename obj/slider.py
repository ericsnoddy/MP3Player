import pygame as pg
from obj.debug import debug

from obj.settings import BAR_BORDER_COLOR, FONT_COLOR 

class Slider():
    def __init__(self, x, y, width, height, current_value, max_value):
        super().__init__()

        self.win = pg.display.get_surface()
        self.rect = pg.Rect(x, y, width, height)
        self.rect_border = pg.Rect(x, y, width, height)
        self.current_value = current_value
        self.max_value = max_value

        self.adjust_slider(self.current_value)

    def adjust_slider(self, new_value):
        self.rect.width = self.rect_border.width * (new_value / self.max_value)
        self.current_value = new_value        

    def show_slider(self):
        pg.draw.rect(self.win, FONT_COLOR, self.rect)
        pg.draw.rect(self.win, BAR_BORDER_COLOR, self.rect_border, 2)
