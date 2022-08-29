import pygame, sys
from pygame.locals import *
from tkinter import filedialog
from os import scandir

from obj.settings import WIDTH, HEIGHT, PAD, BPAD, BSIZE, BG_DEFAULT, FONT_TYPE_REG,  FONT_TYPE_BOLD, FONT_COLOR, VOL_START, VOL_INCR, BUTTONS
from obj.button import Button, MuteButton, PauseButton

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
        self.setup_mode = False
        self.show_setup_button = True
        self.player_ok = False
        self.music_folder = ''
        self.collection = {}

        # Setup process
        self.setup_txt = self.font_reg.render('Select music folder', True, FONT_COLOR)

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
        # Dict1 = { artist : { album : [songs] } }
        # Dict2 = { album : [songs] }
        # Dict3 = { '_songs' : [songs] }    <--- (list as single entry)

        artists = [ folder.name for folder in scandir(self.music_folder) if folder.is_dir() ]
        if artists:
            for artist in artists:
                albums = [ folder.name for folder in scandir(self.music_folder + '\\' + artist) if folder.is_dir() ]
                if albums:
                    for album in albums:
                        song_list = [ file.path for file in scandir(self.music_folder + '\\' + artist + '\\' + album) if file.is_file() ]
                        self.collection.update( { artist : { album : song_list }} )
                else:
                    song_list = [ file.path for file in scandir(self.music_folder + '\\' + artist) if file.is_file() ]
                    self.collection.update( { artist : song_list } )
        else:
            song_list = [ file.path for file in scandir(self.music_folder) if file.is_file() ]
            self.collection.update( { '_songs' : song_list } )

    def group_buttons(self):
        # load images
        menu = pygame.image.load(BUTTONS['menu']).convert_alpha()
        power = pygame.image.load(BUTTONS['power']).convert_alpha()
        stop = pygame.image.load(BUTTONS['stop']).convert_alpha()
        play = pygame.image.load(BUTTONS['play']).convert_alpha()
        rew = pygame.image.load(BUTTONS['rew']).convert_alpha()
        ff = pygame.image.load(BUTTONS['ff']).convert_alpha()
        prev = pygame.image.load(BUTTONS['prev']).convert_alpha()
        next = pygame.image.load(BUTTONS['next']).convert_alpha()
        voldown = pygame.image.load(BUTTONS['voldown']).convert_alpha()
        volup = pygame.image.load(BUTTONS['volup']).convert_alpha()

        # add setup icon to GroupSingle sprite group
        centeringx = (WIDTH - PAD*2 - menu.get_width()) // 2 + PAD
        centeringy = PAD + self.setup_txt.get_height() + PAD
        self.setup_button.add(Button(menu, centeringx, centeringy, 'load', 'load folder'))

        # add buttons to sprite group
        # button locations were worked out manually on paper
        # PREV - REW - STOP - PLAY - PAUSE - FF - NEXT
        #    VOLDOWN - [VOLBAR] - VOLUP - MUTE(D)
        #               MENU - POWER

        rowpad = (WIDTH - BSIZE*7 - BPAD*6) // 2 # L and R padding
        rowslot = BSIZE + BPAD

        row1_y = HEIGHT - BPAD*3 - BSIZE*3  
        row2_y = HEIGHT - BPAD*2 - BSIZE*2
        row3_y = HEIGHT - BPAD - BSIZE        

        self.buttons.add(
            Button(prev, rowpad, row1_y, 'prev', 'Previous'),
            Button(rew, rowpad + rowslot, row1_y, 'rew', 'Rewind'),
            Button(stop, rowpad + 2*rowslot, row1_y, 'stop', 'Stop'),
            Button(play, rowpad + 3*rowslot, row1_y, 'play', 'Play'),
            PauseButton(rowpad + 4*rowslot, row1_y, 'pause', 'Pause'),
            Button(ff, rowpad + 5*rowslot, row1_y, 'ff', 'Fast Forward'),
            Button(next, rowpad + 6*rowslot, row1_y, 'next', 'Next'),
            Button(menu, rowpad, row2_y, 'menu', 'Menu'),
            Button(voldown, rowpad + rowslot, row2_y, 'voldown', 'Volume Down'),
            Button(volup, WIDTH - rowpad - BSIZE - rowslot, row2_y, 'volup', 'Volume Up'),
            MuteButton(WIDTH - rowpad - BSIZE, row2_y, 'mute', 'Mute' ),
            Button(power, (WIDTH - BSIZE) // 2, row3_y, 'power', 'Power Off'))    

    def click_handler(self):
        if self.event.type == MOUSEBUTTONDOWN:
            clicked = [button for button in self.buttons.sprites() if button.is_clicked(self.event.pos)]
            volume = pygame.mixer.music.get_volume()
            
            for b in clicked:
                if b.label == 'power':
                    self.say_goodbye()

                if b.label == 'voldown':
                    if volume - 0.01 >= -0.1:
                        pygame.mixer.music.set_volume(volume - 0.01)

                if b.label == 'volup':
                    if volume + 0.01 <= 1.1:
                        pygame.mixer.music.set_volume(volume + 0.01)

                # Need a cooldown
                if b.label == 'pause' and b.can_click:
                    b.click_time = pygame.time.get_ticks()
                    b.toggle_pause()
                    b.can_click = False
                    pygame.mixer.music.pause()                    

                if b.label == 'paused' and b.can_click:
                    b.click_time = pygame.time.get_ticks()
                    b.toggle_pause()
                    b.can_click = False
                    pygame.mixer.music.unpause()
                    

    def event_handler(self, event):
        self.event = event

    def say_goodbye(self):

        self.win.blit(self.bg, (0,0))

        goodbye_txt = self.font_goodbye.render('Ciao!', True, FONT_COLOR)
        self.win.blit(goodbye_txt, 
                ((WIDTH - goodbye_txt.get_width()) // 2, 
                (HEIGHT - goodbye_txt.get_height()) // 2))

        pygame.display.update()
        pygame.time.delay(3000)
        self.running = False

    def run(self):
        self.win.blit(self.bg, (0,0))

        if self.setup_mode:
            self.setup()
        else:
            self.buttons.update()
            self.buttons.draw(self.win)
            self.click_handler()

