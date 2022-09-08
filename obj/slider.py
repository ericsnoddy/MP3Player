import pygame as pg
from obj.debug import debug

from obj.settings import BAR_BORDER_COLOR, BAR_COLOR

class Slider:
    def __init__(self, x, y, width, height, initial_value, initial_max):

        self.win = pg.display.get_surface()
        self.rect = pg.Rect(x, y, width, height)
        self.rect_border = pg.Rect(x, y, width, height)
        self.initial_value = initial_value
        self.max_value = initial_max

        self.value_to_pos(self.initial_value, self.max_value)

    def is_clicked(self, mouse_pos):
        return True if self.rect_border.collidepoint(mouse_pos) else False

    def pos_to_value(self, click_x, max_value):
        # inverse ratio
        return int((click_x - self.rect.x) * max_value / self.rect_border.width)

    def value_to_pos(self, new_value, max_value):
        try:
            # ratio
            self.rect.width = self.rect_border.width * (new_value / max_value)
        except ZeroDivisionError:
            self.rect.width = 0

    def draw(self):
        pg.draw.rect(self.win, BAR_COLOR, self.rect)
        pg.draw.rect(self.win, BAR_BORDER_COLOR, self.rect_border, 2)


