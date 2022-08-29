import pygame, sys
from pygame.locals import *
from tkinter import filedialog
from os import scandir

from obj.settings import WIDTH, PAD, BG_DEFAULT, FONT_TYPE_REG, FONT_TYPE_USER, FONT_COLOR, BUTTONS
from obj.button import Button

class Console:
    def __init__(self, win):

        self.win = win
        self.bg = pygame.image.load(BG_DEFAULT).convert()
        self.font_reg = pygame.font.Font(FONT_TYPE_REG, 14)
        self.user_reg = pygame.font.Font(FONT_TYPE_USER, 14)

        # default flags and user data - could use last in list as a flag the process is complete
        self.setup_mode = True
        self.show_setup_button = True
        self.player_ok = False
        self.music_folder = ''
        self.collection = {}
        self.profile_name = ''

        # setup text, so it's only rendered once during init
        self.text1 = self.font_reg.render('Select music folder', True, FONT_COLOR)
        self.text2 = self.font_reg.render('Building collection...', True, FONT_COLOR)
        self.text3 = self.font_reg.render('Name your profile', True, FONT_COLOR)

        # buttons (requires self.text1)
        self.buttons = pygame.sprite.Group()
        self.setup_button = pygame.sprite.GroupSingle()
        self.group_buttons()

    def setup(self):

        if not self.music_folder:
            self.win.blit(self.text1, ((WIDTH - PAD*2 - self.text1.get_width()) // 2 + PAD, PAD))

            if self.event.type == MOUSEBUTTONDOWN and [s for s in self.setup_button if s.is_clicked(self.event.pos)]:                                
                self.music_folder = filedialog.askdirectory( title='Select root music folder' )
                if self.music_folder:
                    self.show_setup_button = False

        elif not self.collection:
            self.win.blit(self.text2, ((WIDTH - PAD*2 - self.text2.get_width()) // 2 + PAD, PAD))
            self.build_collection()

        elif not self.profile_name:
            self.win.blit(self.text3, ((WIDTH - PAD*2 - self.text3.get_width()) // 2 + PAD, PAD))
            self.profile_name = self.get_user_text()

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
        voldown = pygame.image.load(BUTTONS['voldown']).convert_alpha()
        volup = pygame.image.load(BUTTONS['volup']).convert_alpha()

        # add setup icon to GroupSingle sprite group
        menu_pos = ((WIDTH - PAD*2 - menu.get_width()) // 2 + PAD, 
                            PAD + self.text1.get_height() + PAD) 
        self.setup_button.add(Button(menu, menu_pos[0], menu_pos[1], 'load', 'load folder'))

        # add buttons to sprite group
        self.buttons.add(
            Button(menu, 0, 0, 'menu', 'Menu'),
            Button(stop, 0, 0, 'stop', 'Stop'),
            Button(play, 0, 0, 'play', 'Play'),
            Button(pause, 0, 0, 'pause', 'Pause'),
            Button(rew, 0, 0, 'rew', 'Rewind'),
            Button(ff, 0, 0, 'ff', 'Fast Forward'),
            Button(prev, 0, 0, 'prev', 'Previous'),
            Button(next, 0, 0, 'next', 'Next'),
            Button(mute, 0 ,0, 'mute', 'Mute'),
            Button(voldown, 0, 0, 'voldown', 'Volume Down'),
            Button(volup, 0, 0, 'volup', 'Volume Up'))

    def get_user_text(self):
        return
        
    def event_handler(self, event):
        self.event = event

    def run(self):
        self.win.blit(self.bg, (0,0))

        if self.setup_mode:
            self.setup()
        
        if self.show_setup_button:
            self.setup_button.draw(self.win)
        
        if self.player_ok:
            self.buttons.draw(self.win)
