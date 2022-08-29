import pygame
from settings import MUTE_BUTTONS, BSIZE

class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y, label, description):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft = (x,y))
        self.radius = self.rect.width // 2
        self.label = label
        self.description = description

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

        self.mute = pygame.image.load(MUTE_BUTTONS['mute'])
        self.muted = pygame.image.load(MUTE_BUTTONS['muted'])
        self.mute_state = False

        self.image = self.muted
        self.rect = self.image.get_rect(topleft = (x,y))

    def update(self):
        if self.mute_state:
            self.image = self.muted
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        else:
            self.image = self.mute
            self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
