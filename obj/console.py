import pygame, sys
from pygame.locals import *
from tkinter import filedialog
from os import scandir
from random import randrange

from obj.settings import WIDTH, HEIGHT, PAD, BPAD, BSIZE, BG_DEFAULT, FONT_TYPE_REG,  FONT_TYPE_BOLD, FONT_COLOR, VOL_START
from obj.button import Button, VolumeButton, StopButton, MuteButton, PlayButton, PauseButton

class Console:
    def __init__(self, win):

        self.running = True
        self.win = win

        # audio
        pygame.mixer.init()
        pygame.mixer.music.set_volume(VOL_START)

        self.bg = pygame.image.load(BG_DEFAULT).convert()
        self.font_reg = pygame.font.Font(FONT_TYPE_REG, 14)
        self.font_goodbye = pygame.font.Font(FONT_TYPE_BOLD, 50)

        # default flags and user setup
        self.setup_mode = True
        self.show_setup_button = True
        self.music_folder = ''
        self.collection = {}
        self.collection_type = None     # see build_collection() comments

        # Now playing
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
                self.music_folder = filedialog.askdirectory( title='Select root music folder' )

        elif not self.collection:
            self.build_collection()
        else:
            self.setup_mode = False

    def build_collection(self):
        
        # Build a dictionary into one of the following templates depending on how collection is organized:
        # self.collection_type = {}
        # 'dict1' = { artist : { album : [songs] } }
        # 'dict2' = { album : [songs] }
        # 'dict3' = { '_songs' : [songs] }    <--- (list as single entry)

        artists = [ folder.name for folder in scandir(self.music_folder) if folder.is_dir() ]
        if artists:
            for artist in artists:
                albums = [ folder.name for folder in scandir(self.music_folder + '\\' + artist) if folder.is_dir() ]
                if albums:
                    for album in albums:
                        song_list = [ file.path for file in scandir(self.music_folder + '\\' + artist + '\\' + album) if file.is_file() ]
                        self.collection.update( { artist : { album : song_list }} )
                        self.collection_type = 'dict1'
                else:
                    song_list = [ file.path for file in scandir(self.music_folder + '\\' + artist) if file.is_file() ]
                    self.collection.update( { artist : song_list } )
                    self.collection_type = 'dict2'
        else:
            song_list = [ file.path for file in scandir(self.music_folder) if file.is_file() ]
            self.collection.update( { '_songs' : song_list } )
            self.collection_type = 'dict3'

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
            PlayButton('play', rowpad + 3*rowslot, row1_y, 'Play'),
            PauseButton('pause', rowpad + 4*rowslot, row1_y, 'Pause'), 
            # Button('prev', rowpad, row1_y, 'Previous'),
            # Button('next', rowpad + 6*rowslot, row1_y, 'Next'),
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
                    self.activate_butts(False, 'mute')

                if b.label == 'volup':
                    b.volumize('+')
                    self.activate_butts(False, 'mute')

                if b.label == 'mute' and b.can_click:
                    b.log_click()
                    b.toggle_mute()

                if b.label == 'stop' and b.can_click and self.song_playing:
                    b.log_click()                     
                    b.stop_playback()
                    self.activate_butts(False, 'play', 'mute')
                    self.song_in_progress = False
                    self.song_playing = False
                    self.duration = 0
                    self.start_time = 0
                    self.paused_time = 0
                    self.off_time = 0

                if b.label == 'play' and b.can_click:
                    b.log_click()       
                    song = self.get_random()             
                    if not self.song_in_progress:                        
                        pygame.mixer.music.load(song)
                        self.song_in_progress = True
                        self.song_playing = True
                        b.start_play(song)
                        self.activate_butts(False, 'stop')
                        self.start_time = pygame.time.get_ticks()                        
                    elif self.song_in_progress and not self.song_playing:                        
                        self.activate_butts(False, 'stop', 'pause')
                        b.start_play(song)
                        self.song_playing = True
                        self.off_time += pygame.time.get_ticks() - self.paused_time
                        self.paused_time = 0

                if b.label == 'pause' and b.can_click:
                    b.log_click()
                    b.toggle_button()
                    if self.song_playing:
                        self.song_playing = False
                        self.paused_time = pygame.time.get_ticks()
                        self.activate_butts(False, 'play')
                    else:
                        self.song_playing = True
                        self.paused_time = 0
                        self.activate_butts(True, 'play')
                    
        if self.event.type == MOUSEBUTTONUP:
            get_vol_buttons = [button for button in self.buttons.sprites() if button.label[0:3] == 'vol']
            for vol in get_vol_buttons:
                if vol.is_active:
                    vol.is_active = False
                    vol.volup_active = False
                    vol.voldown_active = False

    def activate_butts(self, activate = False, *butt_labels):

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

    def get_random(self):
        if self.collection_type == 'dict3':
            i = randrange(0, len(self.collection['_songs']))
            return self.collection['_songs'][i]

    def get_duration(self):
        tot_secs = (self.duration / 1000 )
        hours = int((tot_secs / 3600) % 24)
        mins = int((tot_secs / 60) % 60)
        secs = int(tot_secs % 60)

        return '{}:{:02.0f}:{:02.0f}'.format(hours, mins, secs)

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
        
