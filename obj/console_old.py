import pygame
from pygame.locals import *
from tkinter import filedialog
from os import walk
from os.path import join
from random import randrange

from obj.settings import WIDTH, HEIGHT, PAD, BPAD, BSIZE, BG_DEFAULT, FONT_TYPE_REG,  FONT_TYPE_BOLD, FONT_COLOR, VOL_START
from obj.button import Button, VolumeButton, StopButton, MuteButton, PauseButton, SkipButton

class Console:
    def __init__(self, win):

        self.debug = True

        self.running = True
        self.win = win

        # audio
        pygame.mixer.init()
        pygame.mixer.music.set_volume(VOL_START)

        self.bg = pygame.image.load(BG_DEFAULT).convert()
        self.font_reg = pygame.font.Font(FONT_TYPE_REG, 14)
        self.font_goodbye = pygame.font.Font(FONT_TYPE_BOLD, 50)
        self.font_list = pygame.font.Font(FONT_TYPE_REG, 8)
        self.font_list_bold = pygame.font.Font(FONT_TYPE_BOLD, 10)

        # default flags and user setup
        self.setup_mode = True
        self.show_setup_button = True
        self.music_folder = None
        self.collection = []
        self.song_paths = []

        # Now playing
        self.now_playing_index = None
        self.song_in_progress = False
        self.song_playing = False
        self.duration = 0
        self.start_time = 0
        self.paused_time = 0
        self.off_time = 0

        # All the text that can be pre-rendered
        self.setup_txt = self.font_reg.render('Select music folder', True, FONT_COLOR)
        self.goodbye_txt = self.font_goodbye.render('Ciao!', True, FONT_COLOR)

        # buttons (requires self.setup_txt)
        self.buttons = pygame.sprite.Group()
        self.setup_button = pygame.sprite.GroupSingle()
        self.group_buttons()

    def setup(self):
        if not self.music_folder:
            self.win.blit(self.setup_txt, ((WIDTH - PAD*2 - self.setup_txt.get_width()) // 2 + PAD, PAD))
            self.setup_button.draw(self.win)

            if self.event.type == MOUSEBUTTONDOWN and [s for s in self.setup_button if s.is_clicked(self.event.pos)]:
                self.music_folder = filedialog.askdirectory( title='Select music folder' )

        elif not self.collection:
            for root, _, files in walk(self.music_folder):
                for name in files:
                    # Creates 2 lists that are index-synced; one for just file names, and one for full filepath
                    self.song_paths.append(join(root, name))
                    self.collection.append(name)
        else:
            self.setup_mode = False

    def group_buttons(self):
        # add setup icon to GroupSingle sprite group
        centeringx = (WIDTH - PAD*2 - BSIZE) // 2 + PAD
        centeringy = PAD + self.setup_txt.get_height() + PAD
        self.setup_button.add(Button('menu', centeringx, centeringy, 'load folder'))

        # Spacing for icons (sprites)
        rowpad = (WIDTH - BSIZE*7 - BPAD*6) // 2
        rowslot = BSIZE + BPAD
        row1_y = HEIGHT - BPAD*3 - BSIZE*3  
        row2_y = HEIGHT - BPAD*2 - BSIZE*2
        row3_y = HEIGHT - BPAD - BSIZE        

        # add buttons to sprite group
        self.buttons.add(
            Button('power', (WIDTH - BSIZE) // 2, row3_y, 'Power Off'),
            VolumeButton('voldown', rowpad + rowslot, row2_y, 'Volume Down'),
            VolumeButton('volup', WIDTH - rowpad - BSIZE - rowslot, row2_y, 'Volume Up'),
            MuteButton('mute', WIDTH - rowpad - BSIZE, row2_y, 'Mute'),
            StopButton('stop', rowpad + 2*rowslot, row1_y, 'Stop'),
            Button('play', rowpad + 3*rowslot, row1_y, 'Play'),
            PauseButton('pause', rowpad + 4*rowslot, row1_y, 'Pause'), 
            SkipButton('prev', rowpad, row1_y, 'Previous'),
            SkipButton('next', rowpad + 6*rowslot, row1_y, 'Next'),
            # Button('next', rowpad + rowslot, row1_y, 'Rewind'), 
            # Button('ff', rowpad + 5*rowslot, row1_y, 'Fast Forward'),
            # Button('menu', rowpad, row2_y, 'Menu'),                     
            
        )    

    def click_handler(self):
        if self.event.type == MOUSEBUTTONDOWN:
            clicked = [button for button in self.buttons.sprites() if button.is_clicked(self.event.pos)]
           
            for b in clicked:
                if b.label == 'power':
                    self.say_goodbye()

                if b.label == 'voldown':
                    b.volumize('-')
                    self.toggle_butts(False, 'mute')

                if b.label == 'volup':
                    b.volumize('+')
                    self.toggle_butts(False, 'mute')

                if b.label == 'mute' and b.can_click:
                    b.log_click()
                    b.toggle_mute()

                if b.label == 'stop' and b.can_click and self.song_playing:
                    b.log_click()                     
                    b.stop_playback()
                    self.toggle_butts(False, 'play', 'mute')
                    self.song_in_progress = False
                    self.song_playing = False
                    self.reset_duration()
                    # if not song playing do nothing

                if b.label == 'play' and b.can_click:
                    b.log_click()                               
                    if not self.song_in_progress:                        
                        self.load_song('random')
                        b.toggle_active()
                        self.toggle_butts(False, 'stop')
                        self.start_time = pygame.time.get_ticks()      
                        self.song_in_progress = True
                        self.song_playing = True            
                    elif self.song_in_progress and not self.song_playing:                        
                        self.toggle_butts(False, 'stop', 'pause')
                        self.toggle_butts(True, 'play')
                        pygame.mixer.music.unpause()
                        self.song_playing = True
                        self.off_time += pygame.time.get_ticks() - self.paused_time
                        self.paused_time = 0
                    # if song in progress and playing do nothing

                if b.label == 'pause' and b.can_click:
                    b.log_click()
                    if self.song_playing:
                        self.song_playing = False
                        self.paused_time = pygame.time.get_ticks()
                        self.toggle_butts(False, 'play')
                        b.toggle_pause()
                    elif not self.song_playing and self.song_in_progress:
                        self.song_playing = True
                        self.paused_time = 0
                        self.toggle_butts(True, 'play')
                        b.toggle_pause()
                    # If not song in progress do nothing

                if b.label == 'prev' or b.label == 'next' and b.can_click:
                    b.log_click()
                    b.toggle_active()
                    self.reset_duration()
                    if b.label == 'prev':
                        self.load_song('prev')
                    elif b.label == 'next':
                        self.load_song('next')
                    
        if self.event.type == MOUSEBUTTONUP:
            get_vol_buttons = [button for button in self.buttons.sprites() if button.label[0:3] == 'vol']
            for vol in get_vol_buttons:
                if vol.is_active:
                    vol.is_active = False
                    vol.volup_active = False
                    vol.voldown_active = False

    def toggle_butts(self, activate = False, *butt_labels):

        butts = [
            [b for b in self.buttons.sprites() if b.label == 'stop'][0],
            [b for b in self.buttons.sprites() if b.label == 'play'][0],
            [b for b in self.buttons.sprites() if b.label == 'pause'][0],
            [b for b in self.buttons.sprites() if b.label == 'mute'][0]
        ]

        for butt in butts:
            if butt.label in butt_labels:
                if activate:
                    butt.is_active = True
                else:
                    butt.is_active = False

    def load_song(self, selection = 'random'):   
        if selection == 'random':
            i = randrange(0, len(self.song_paths))
            self.now_playing_index = i     
            pygame.mixer.music.load(self.song_paths[i])
            pygame.mixer.music.play()        

        elif selection == 'prev':
            if self.now_playing_index > 0:
                self.now_playing_index -= 1
                pygame.mixer.music.load(self.song_paths[self.now_playing_index])   
                pygame.mixer.music.play()        

        elif selection == 'next':
            if self.now_playing_index < len(self.song_paths) - 1:
                self.now_playing_index += 1
                pygame.mixer.music.load(self.song_paths[self.now_playing_index])
                pygame.mixer.music.play()

    def get_duration(self):
        tot_secs = (self.duration / 1000 )
        hours = int((tot_secs / 3600) % 24)
        mins = int((tot_secs / 60) % 60)
        secs = int(tot_secs % 60)

        return '{}:{:02.0f}:{:02.0f}'.format(hours, mins, secs)

    def reset_duration(self):
        self.duration = 0
        self.start_time = 0
        self.paused_time = 0
        self.off_time = 0

    def event_handler(self, event):
        self.event = event
        self.click_handler()

    def say_goodbye(self):

        self.win.blit(self.bg, (0,0))
        self.win.blit(self.goodbye_txt, 
                ((WIDTH - self.goodbye_txt.get_width()) // 2, 
                (HEIGHT - self.goodbye_txt.get_height()) // 2))

        pygame.display.update()
        pygame.time.delay(3000)
        self.running = False

    def run(self):
        self.win.blit(self.bg, (0,0))

        if not self.setup_mode:
            self.buttons.update()
            self.buttons.draw(self.win)

            now = pygame.time.get_ticks()
            if self.song_in_progress:
                self.duration = now - self.start_time - self.off_time

            duration = self.font_goodbye.render(self.get_duration(), True, FONT_COLOR)
            if self.song_in_progress and not self.song_playing:
                self.off_time = pygame.time.get_ticks() - self.paused_time     
            self.win.blit(duration, ((WIDTH - PAD*2 - duration.get_width()) // 2 + PAD, PAD))
        else:    
            self.setup()