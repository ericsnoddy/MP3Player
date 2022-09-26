# third party
import pygame as pg

# local
from obj.data import BUTTONS

class ToggleButton(pg.sprite.Sprite):
    def __init__(self, label, x, y):
        super().__init__()

        self.image = pg.image.load(BUTTONS[label]).convert_alpha()
        self.active_image = pg.image.load(BUTTONS[label + '_']).convert_alpha()
        self.inactive_image = self.image
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




class HoldButton(ToggleButton):
    def __init__(self, label, x, y, do_while_hold_click_func):
        super().__init__(label, x, y)

        # passed functions don't initialize with ()
        self.do_while_hold_click_func = do_while_hold_click_func

    def update(self):
        if self.is_active:
            self.do_while_hold_click_func(self)
            self.image = self.active_image
        else:
            self.image = self.inactive_image
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))




class MuteButton(ToggleButton):
    def __init__(self, label, x, y, volume):
        super().__init__(label, x, y)

        self.saved_volume = volume

    # toggling mute returns a new volume value
    # so console doesn't have to track a saved volume
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




class QuickButton(ToggleButton):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)

    def update(self):
        # Use the cooldown period as the activation timer
        if not self.can_click:
            self.is_active = True
            self.image = self.active_image
        else:
            self.is_active = False
            self.image = self.inactive_image
           
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self._cooldown()




class SeekButton(QuickButton):
    def __init__(self, label, x, y):
        super().__init__(label, x, y)
        
        self.click_cooldown = 25




class ModeButton(pg.sprite.Sprite):
    def __init__(self, label, x, y, play_mode):
        super().__init__()

        self.inactive_images = [
            pg.image.load(BUTTONS['reg']).convert_alpha(),
            pg.image.load(BUTTONS['loop']).convert_alpha(),
            pg.image.load(BUTTONS['rand']).convert_alpha()
        ]

        self.active_images = [
            pg.image.load(BUTTONS['reg_']).convert_alpha(),
            pg.image.load(BUTTONS['loop_']).convert_alpha(),
            pg.image.load(BUTTONS['rand_']).convert_alpha()
        ]

        self.play_mode = play_mode
        self.mode_index = self._init_mode()        

        self.image = self.inactive_images[self.mode_index]
        self.rect = self.image.get_rect(topleft = (x,y))

        self.radius = self.rect.width // 2
        self.label = label
        self.click_time = None
        self.click_cooldown = 50
        self.can_click = True
        self.is_active = False

    def toggle_mode(self):

        if self.play_mode == 'reg':
            self.play_mode = 'loop'
            self.mode_index = 1
        elif self.play_mode == 'loop':
            self.play_mode = 'rand'
            self.mode_index = 2
        else:
            self.play_mode = 'reg'
            self.mode_index = 0

        return self.play_mode

    def is_clicked(self, mouse_pos):
        dx = self.rect.centerx - mouse_pos[0]
        dy = self.rect.centery - mouse_pos[1]
        sq = dx**2 + dy**2
        return True if sq < self.radius**2 else False

    def log_click(self):
        self.click_time = pg.time.get_ticks()
        self.can_click = False
    
    def _init_mode(self):
        
        # Here indices are assigned, preferring a List over a Dict to toggle through. 
        match self.play_mode:
            case 'reg':
                return 0
            case 'loop':
                return 1
            case 'rand':
                return 2

    def _cooldown(self):
        current_time = pg.time.get_ticks()

        if not self.can_click:
            if current_time - self.click_time >= self.click_cooldown:
                self.can_click = True

    def update(self):
        if not self.can_click:
            self.is_active = True
            self.image = self.active_images[self.mode_index]
        else:
            self.is_active = False
            self.image = self.inactive_images[self.mode_index]
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self._cooldown()
