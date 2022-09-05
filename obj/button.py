import pygame as pg
from math import sin

from obj.settings import BUTTONS

class Button(pg.sprite.Sprite):
    def __init__(self, label, x, y):
        super().__init__()

        self.image = self.inactive_image = pg.image.load(BUTTONS[label]).convert_alpha()
        self.active_image = pg.image.load(BUTTONS[label + '_']).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x,y))
        self.radius = self.rect.width // 2
        self.label = label
        self.click_time = None
        self.click_cooldown = 400
        self.can_click = True
        self.is_active = False

    def activate(self, activate = True):
        self.is_active = activate

    def log_click(self):
        self.click_time = pg.time.get_ticks()
        self.can_click = False

    def cooldown(self):
        current_time = pg.time.get_ticks()

        if not self.can_click:
            if current_time - self.click_time >= self.click_cooldown:
                self.can_click = True

    def is_clicked(self, mouse_pos):
        dx = self.rect.centerx - mouse_pos[0]
        dy = self.rect.centery - mouse_pos[1]
        sq = dx**2 + dy**2
        if sq < self.radius**2:
            return True
        else:
            return False

    def update(self):
        if self.is_active:
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()

class QuickButton(Button):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)

    def update(self):
        if not self.can_click:
            self.is_active = True
            self.image = self.active_image
        else:
            self.is_active = False
            self.image = self.inactive_image
           
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()

class MuteButton(Button):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)

        self.saved_volume = pg.mixer.music.get_volume()

    def toggle_mute(self):
        current_volume = pg.mixer.music.get_volume()
        if self.is_active:
            pg.mixer.music.set_volume(self.saved_volume)
            self.is_active = False
        else:
            self.saved_volume = current_volume
            pg.mixer.music.set_volume(0)
            self.is_active = True

class VolumeButton(Button):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)

        self.volup_active = False
        self.voldown_active = False

    def volumize(self, sign):
        volume = pg.mixer.music.get_volume()
        if sign == '+' and volume + 0.01 <= 1:            
            self.volup_active = True
        if sign == '-' and volume - 0.005 >= 0:            
            self.voldown_active = True

    def update(self):
        volume = pg.mixer.music.get_volume()
        if self.volup_active:
            pg.mixer.music.set_volume(volume + 0.01)
            self.image = self.active_image
        elif self.voldown_active:
            # No idea why pg wants to decrement faster than increment but I had to halve the speed
            pg.mixer.music.set_volume(volume - 0.005)
            self.image = self.active_image           
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

