import pygame
from math import sin

from obj.settings import ACTIVE_BUTTONS, BSIZE

class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y, label, description):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft = (x,y))
        self.radius = self.rect.width // 2
        self.label = label
        self.description = description
        self.click_time = None
        self.click_cooldown = 200
        self.can_click = True

    def cooldown(self):
        current_time = pygame.time.get_ticks()

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

class MuteButton(Button):
    def __init__(self, x, y, label, description):
        super().__init__(pygame.Surface((BSIZE, BSIZE)), x, y, label, description)

        self.mute = pygame.image.load(ACTIVE_BUTTONS['mute'])
        self.muted = pygame.image.load(ACTIVE_BUTTONS['muted'])
        self.is_muted = False

        self.image = self.mute
        self.rect = self.image.get_rect(topleft = (x,y))

    def update(self):
        if self.is_muted:
            self.image = self.muted
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        else:
            self.image = self.mute
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

class PauseButton(Button):
    def __init__(self, x, y, label, description):
        super().__init__(pygame.Surface((BSIZE, BSIZE)), x, y, label, description)

        self.pause = pygame.image.load(ACTIVE_BUTTONS['pause'])
        self.paused = pygame.image.load(ACTIVE_BUTTONS['paused'])
        self.is_paused = False

        self.image = self.pause
        self.rect = self.image.get_rect(topleft = (x,y))

        self.pulse_ms = 100
        self.pulse_start = None     # no need to init
        self.pulse_on = True

    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            if not self.pulse_on:
                self.pulse_on = True
                self.image.set_alpha(255)            
        else:
            self.is_paused = True
            self.pulse_start = pygame.time.get_ticks()            

    def pulse_alpha(self):
        if not self.pulse_start:
            self.pulse_start = pygame.time.get_ticks()

        delta = pygame.time.get_ticks() - self.pulse_start

        if delta % self.pulse_ms == 0:
            if self.pulse_on:
                self.image.set_alpha(0)
                self.pulse_on = False
            else:
                self.image.set_alpha(255)
                self.pulse_on = True

    def update(self):
        if self.is_paused:
            self.image = self.paused
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
            self.pulse_alpha()
        else:
            self.image = self.pause
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

        self.cooldown()
