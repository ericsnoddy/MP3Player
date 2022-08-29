import pygame, sys
from pygame.locals import *
from tkinter import filedialog
from os import scandir

from obj.settings import WIDTH, HEIGHT, PAD, BPAD, BSIZE, BG_DEFAULT, FONT_TYPE_REG,  FONT_COLOR, BUTTONS
from obj.button import Button, MuteButton

class Console:
    def __init__(self, win):

        self.win = win
        self.bg = pygame.image.load(BG_DEFAULT).convert()
        self.font_reg = pygame.font.Font(FONT_TYPE_REG, 14)

        # default flags and user data
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

    def console(self):
        pass



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
        pause = pygame.image.load(BUTTONS['pause']).convert_alpha()
        rew = pygame.image.load(BUTTONS['rew']).convert_alpha()
        ff = pygame.image.load(BUTTONS['ff']).convert_alpha()
        prev = pygame.image.load(BUTTONS['prev']).convert_alpha()
        next = pygame.image.load(BUTTONS['next']).convert_alpha()
        mute = pygame.image.load(BUTTONS['mute']).convert_alpha()
        muted = pygame.image.load(BUTTONS['muted']).convert_alpha()
        voldown = pygame.image.load(BUTTONS['voldown']).convert_alpha()
        volup = pygame.image.load(BUTTONS['volup']).convert_alpha()

        # add setup icon to GroupSingle sprite group
        centeringx = (WIDTH - PAD*2 - menu.get_width()) // 2 + PAD
        centeringy = PAD + self.setup_txt.get_height() + PAD
        self.setup_button.add(Button(menu, centeringx, centeringy, 'load', 'load folder'))

        # add buttons to sprite group
        # button locations were worked out manually on paper
        # PREV - REW - STOP - PLAY - PAUSE - FF - NEXT
        # VOLDOWN - VOLBAR - VOLUP - MUTE(D)
        # MENU - POWER

        row3_y = HEIGHT - BPAD - BSIZE
        row2_y = HEIGHT - BPAD*2 - BSIZE*2
        row1_y = HEIGHT - BPAD*3 - BSIZE*3

        self.buttons.add(
            Button(prev, 0, row1_y, 'prev', 'Previous'),
            Button(rew, 0, row1_y, 'rew', 'Rewind'),
            Button(stop, 0, row1_y, 'stop', 'Stop'),
            Button(play, 0, row1_y, 'play', 'Play'),
            Button(pause, 0, row1_y, 'pause', 'Pause'),
            Button(ff, 0, row1_y, 'ff', 'Fast Forward'),
            Button(next, 0, row1_y, 'next', 'Next'),

            Button(voldown, 0, row2_y, 'voldown', 'Volume Down'),
            Button(volup, 0, row2_y, 'volup', 'Volume Up')),
            MuteButton(0, row2_y, 'mute', 'Mute' ),
            Button(menu, 0, row3_y, 'menu', 'Menu'),
            Button(power, 0, row3_y, 'power', 'Power Off'),

            
            

            
            
            
            
            

    def event_handler(self, event):
        self.event = event

    def run(self):
        self.win.blit(self.bg, (0,0))

        if self.setup_mode:
            self.setup()
        else:
            self.buttons.draw(self.win)
            self.console()    
        

