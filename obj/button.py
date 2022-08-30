import pygame
from math import sin

from obj.settings import BUTTONS, BSIZE

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

class ActiveButton(Button):
    def __init__(self, x, y, label, description):
        super().__init__(pygame.Surface((BSIZE, BSIZE)), x, y, label, description)

        self.inactive_img = pygame.image.load(BUTTONS[label]).convert_alpha()
        self.active_img = pygame.image.load(BUTTONS[label + '_']).convert_alpha()
        self.is_active = False

        self.image = self.inactive_img

    def toggle_button(self):
        if self.is_active:
            self.is_active = False
        else:
            self.is_active = True

    def update(self):
        if self.is_active:
            self.image = self.active_img
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        else:
            self.image = self.inactive_img
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()

class PauseButton(ActiveButton):
    def __init__(self, x, y, label, description):
        super().__init__(x, y, label, description)

        self.pulse_ms = 200
        self.pulse_start = None     # no need to init
        self.pulse_on = True

    def toggle_button(self):
        if self.is_active:
            self.is_active = False
            if not self.pulse_on:
                self.pulse_on = True
                self.image.set_alpha(255)            
        else:
            self.is_active = True
            self.pulse_start = pygame.time.get_ticks()            

    def pulse_alpha(self):
        if not self.pulse_start:
            self.pulse_start = pygame.time.get_ticks()

        delta = pygame.time.get_ticks() - self.pulse_start

        if delta % self.pulse_ms == 0:
            if self.pulse_on:
                self.image.set_alpha(255)
                self.pulse_on = False
            else:
                self.image.set_alpha(0)
                self.pulse_on = True

    def update(self):
        if self.is_active:
            self.image = self.active_img
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
            self.pulse_alpha()
        else:
            self.image = self.inactive_img
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()

class PlayButton(ActiveButton):
    def __init__(self, x, y, label, description):
        super().__init__(x, y, label, description)

        self.start_time = 0
        self.stop_time = 0
        self.play_offset = 0
        self.duration = 0
        self.song_in_progress = False

    def get_clock(self):
        tot_secs = (self.duration / 1000 )
        hours = int((tot_secs / 3600) % 24)
        mins = int((tot_secs / 60) % 60)
        secs = int(tot_secs % 60)

        return '{}:{:02.0f}:{:02.0f}'.format(hours, mins, secs)

    def start_clock(self):
        self.is_active = True
        self.play_offset += pygame.time.get_ticks() - self.stop_time

    def stop_clock(self):
        self.is_active = False
        self.stop_time = pygame.time.get_ticks()

    def start_song(self):
        self.is_active = True
        self.song_in_progress = True
        self.start_time = pygame.time.get_ticks()
        
    def stop_song(self):
        self.is_active = False
        self.song_in_progress = False
        self.start_time = 0
        self.play_offset = 0
        self.duration = 0

    def update(self):
        if self.is_active:
            self.image = self.active_img
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
            self.duration = pygame.time.get_ticks() - self.start_time - self.play_offset
        else:
            self.image = self.inactive_img
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
            
        self.cooldown()

class MuteButton(ActiveButton):
    def __init__(self, x, y, label, description):
        super().__init__(x, y, label, description)

        self.saved_volume = pygame.mixer.music.get_volume()

    def save_volume(self, volume):
        self.saved_volume = volume