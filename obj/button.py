import pygame
from math import sin

from obj.settings import BUTTONS

class Button(pygame.sprite.Sprite):
    def __init__(self, label, x, y, description):
        super().__init__()

        self.image = self.inactive_image = pygame.image.load(BUTTONS[label]).convert_alpha()
        self.active_image = pygame.image.load(BUTTONS[label + '_']).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x,y))
        self.radius = self.rect.width // 2
        self.label = label
        self.description = description
        self.click_time = None
        self.click_cooldown = 200
        self.can_click = True
        self.is_active = False

    def toggle_active(self):
        if self.is_active:
            self.is_active = False
        else:
            self.is_active = True

    def log_click(self):
        self.click_time = pygame.time.get_ticks()
        self.can_click = False

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

    def update(self):
        if self.is_active:
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()

class MuteButton(Button):
    def __init__(self, label, x, y, description):
        super().__init__(label, x, y, description)

        self.saved_volume = pygame.mixer.music.get_volume()

    def toggle_mute(self):
        current_volume = pygame.mixer.music.get_volume()
        if current_volume > 0:
            self.saved_volume = current_volume
            pygame.mixer.music.set_volume(0)
            self.is_active = True
        elif current_volume == 0 and self.saved_volume > 0:
            pygame.mixer.music.set_volume(self.saved_volume)
            self.is_active = False

class VolumeButton(Button):
    def __init__(self, label, x, y, description):
        super().__init__(label, x, y, description)

        self.volup_active = False
        self.voldown_active = False

    def volumize(self, sign = '+'):
        volume = pygame.mixer.music.get_volume()
        print(volume)
        if sign == '+' and volume + 0.01 <= 2:            
            self.is_active = True
            self.volup_active = True
        elif sign == '-' and volume - 0.01 >= -2:            
            self.is_active = True
            self.voldown_active = True

    def update(self):
        if self.is_active:
            volume = pygame.mixer.music.get_volume()
            if self.volup_active:
                pygame.mixer.music.set_volume(volume + 0.01)
            elif self.voldown_active:
                pygame.mixer.music.set_volume(volume - 0.01)
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

class StopButton(Button):
    def __init__(self, label, x, y, description):
        super().__init__(label, x, y, description)

    def stop_playback(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.is_active = True

    def update(self):
        if not self.can_click:
            self.is_active = True

        if self.is_active:
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()

class PlayButton(Button):
    def __init__(self, label, x, y, description):
        super().__init__(label, x, y, description)

    def start_play(self, song):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
            self.is_active = True

class PauseButton(Button):
    def __init__(self, x, y, label, description):
        super().__init__(x, y, label, description)

        self.pulse_ms = 200
        self.pulse_start = None     # no need to init
        self.pulse_on = True

    def toggle_button(self):
        if self.is_active:
            pygame.mixer.music.unpause()
            self.is_active = False
            if not self.pulse_on:
                self.pulse_on = True
                self.image.set_alpha(255)            
        else:
            pygame.mixer.music.pause()
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
            self.image = self.active_image
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
            self.pulse_alpha()
        else:
            self.image = self.inactive_image
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.cooldown()