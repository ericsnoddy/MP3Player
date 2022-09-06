import pygame as pg

from obj.settings import BUTTONS

class ToggleButton(pg.sprite.Sprite):
    def __init__(self, label, x, y):
        super().__init__()

        self.image = self.inactive_image = pg.image.load(BUTTONS[label]).convert_alpha()
        self.active_image = pg.image.load(BUTTONS[label + '_']).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x,y))
        self.radius = self.rect.width // 2
        self.label = label
        self.click_time = None
        self.click_cooldown = 250
        self.can_click = True
        self.is_active = False

    def is_clicked(self, mouse_pos):
        dx = self.rect.centerx - mouse_pos[0]
        dy = self.rect.centery - mouse_pos[1]
        sq = dx**2 + dy**2
        return True if sq < self.radius**2 else False

    def log_click(self):
        self.click_time = pg.time.get_ticks()
        self.can_click = False

    def activate(self, activate = True):
        self.is_active = activate

    def _cooldown(self):
        current_time = pg.time.get_ticks()

        if not self.can_click:
            if current_time - self.click_time >= self.click_cooldown:
                self.can_click = True

    def update(self):
        if self.is_active:
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self._cooldown()

class QuickButton(ToggleButton):
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
        self._cooldown()

class HoldButton(ToggleButton):
    def __init__(self, label, x, y, active_func):
        super().__init__(label, x, y)

        self.active_func = active_func

    def update(self):
        if self.is_active:
            self.active_func(self)
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

class MuteButton(ToggleButton):
    def __init__(self, label, x, y, volume):
        super().__init__(label, x, y)

        self.saved_volume = volume

    def toggle_mute(self, volume):
        if self.is_active:
            self.is_active = False
            return self.saved_volume
            
        else:
            self.saved_volume = volume
            self.is_active = True
            return 0

class StopButton(ToggleButton):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)

        self.is_active = True

class SeekButton(QuickButton):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)
        
        self.click_cooldown = 50