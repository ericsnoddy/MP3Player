from os import walk
from os.path import join
from random import randrange
from socket import SO_LINGER
import sys

import pygame as pg
from pygame.locals import *
from tkinter import filedialog
from mutagen.oggvorbis import OggVorbis

from obj.button import ToggleButton, QuickButton, HoldButton, MuteButton, StopButton, SeekButton
from obj.slider import Slider
from obj.settings import (
    WIDTH, 
    HEIGHT, 
    PAD, BPAD, 
    BSIZE, 
    BG_DEFAULT, 
    FONT_TYPE_REG, 
    FONT_TYPE_BOLD, 
    FONT_COLOR, 
    VOL_START, 
    VOL_MAX, 
    # VOL_INCR, 
    OPEN_RANDOM_MODE,
)

from obj.debug import debug

class Console:
    def __init__(self, win):

        self.debug = True
        self.font_debug = pg.font.Font(FONT_TYPE_REG, 6)

        self.running = True
        self.win = win

        # audio
        self.volume = VOL_START
        pg.mixer.music.set_volume(self.volume / VOL_MAX)

        self.bg = pg.image.load(BG_DEFAULT).convert()
        self.font_reg = pg.font.Font(FONT_TYPE_REG, 14)
        self.font_goodbye = pg.font.Font(FONT_TYPE_BOLD, 50)
        self.font_list = pg.font.Font(FONT_TYPE_REG, 8)
        self.font_list_bold = pg.font.Font(FONT_TYPE_BOLD, 10)

        # default flags and user setup
        self.setup_mode = True
        self.music_folder = None
        self.collection = []
        self.song_paths = []
        # self.collection = ['Boss Fight.ogg', "Child's Nightmare.ogg"]
        # self.song_paths = ['C:/Users/Eric/Workspace/test_music/Dark\\Boss Fight.ogg', "C:/Users/Eric/Workspace/test_music/Dark\\Child's Nightmare.ogg"]

        # player flags
        self.song_in_progress = False
        self.now_playing_index = 0
        self.song_offset = 0
        self.song_length = 0

        # for setting event for end of song
        self.SONG_OVER = pg.USEREVENT+1

        # All the text that can be pre-rendered
        self.setup_txt = self.font_reg.render('Select music folder', True, FONT_COLOR)
        self.goodbye_txt = self.font_goodbye.render('Ciao!', True, FONT_COLOR)

        # buttons (requires self.setup_txt)
        self.buttons = pg.sprite.Group()
        self.setup_button = pg.sprite.GroupSingle()
        self._group_buttons()

    def setup(self):
        if not self.music_folder:
            self.win.blit(self.setup_txt, ((WIDTH - PAD*2 - self.setup_txt.get_width()) // 2 + PAD, PAD))
            self.setup_button.draw(self.win)

            setup_btn = self.setup_button.sprite
            clicks = pg.mouse.get_pressed()            
            if clicks[0] and setup_btn.is_clicked(pg.mouse.get_pos()):
                self.music_folder = filedialog.askdirectory( title='Select music folder' )

        elif not self.collection:
            for root, _, files in walk(self.music_folder):
                for name in files:
                    # Creates 2 lists that are index-synced: one for full filepath, 
                    # and one for file names; so I don't have to deal with slicing later
                    if name.endswith('.ogg') or name.endswith('.mp3'):                    
                        self.song_paths.append(join(root, name))
                        self.collection.append(name)
            # no valid filetypes - start again
            if len(self.collection) == 0:
                self.music_folder = None
        else:
            if OPEN_RANDOM_MODE:
                self.now_playing_index = randrange(0, len(self.song_paths))
            # load first track:            
            pg.mixer.music.load(self.song_paths[self.now_playing_index])
            self._log_song_length()
            self.setup_mode = False  

    def mute(self, mute_btn):
        self.volume = mute_btn.toggle_mute(self.volume)
        pg.mixer.music.set_volume(self.volume)

    def stop(self, stop_btn):
        if self.song_in_progress:
            stop_btn.activate()
            self.song_in_progress = False
            self.song_offset = 0
            play_btn = self._get_button('play')
            play_btn.activate(False)
            pause_btn = self._get_button('pause')
            pause_btn.activate(False)
            pg.mixer.music.stop()

    def play(self, play_btn):
        if self.song_in_progress and not pg.mixer.music.get_busy():
            pause_btn = self._get_button('pause')
            if pause_btn.is_active:
                self.pause(pause_btn)
            else:
                self.song_in_progress = False
                self.play(play_btn)
        elif not self.song_in_progress:
            play_btn.activate()
            self.song_in_progress = True
            stop_btn = self._get_button('stop')
            if stop_btn.is_active:
                stop_btn.activate(False)
            pg.mixer.music.play()

    def pause(self, pause_btn):
        play_btn = self._get_button('play')
        if self.song_in_progress and pg.mixer.music.get_busy():
            pause_btn.activate()            
            play_btn.activate(False)
            pg.mixer.music.pause()
        elif self.song_in_progress:
            pause_btn.activate(False)
            play_btn.activate()
            pg.mixer.music.unpause()

    def skip(self, skip_btn):
        is_busy = pg.mixer.music.get_busy()
        if self.song_in_progress and is_busy:
            self._load_song(skip_btn.label)
            play_btn = self._get_button('play')
            self.play(play_btn)
        elif self.song_in_progress and not is_busy:
            self._load_song(skip_btn.label)
            pause_btn = self._get_button('pause')
            pause_btn.activate(False)
        else:
            self._load_song(skip_btn.label)

    def volumize(self, vol_btn):
        vol_btn.activate()

        mute_btn = self._get_button('mute')
        if mute_btn.is_active:
            mute_btn.toggle_mute()

        if vol_btn.label == 'volup' and self.volume < VOL_MAX:
            self.volume += 1
            pg.mixer.music.set_volume(self.volume / VOL_MAX)
        if vol_btn.label == 'voldown' and self.volume > 0:
            self.volume -= 1
            pg.mixer.music.set_volume(self.volume / VOL_MAX)  

    def seek(self, seek_btn):
        if seek_btn.label == 'rew':
            self.song_offset = self._get_position(self.song_offset, rew=10)            

        if seek_btn.label == 'ff':
            self.song_offset = self._get_position(self.song_offset, ff=10)
        pg.mixer.music.play(0, self.song_offset)

    def power_down(self):
        self.win.blit(self.bg, (0,0))
        self.win.blit(self.goodbye_txt, 
                ((WIDTH - self.goodbye_txt.get_width()) // 2, 
                (HEIGHT - self.goodbye_txt.get_height()) // 2))

        pg.display.update()
        if pg.mixer.music.get_busy():
            pg.mixer.music.fadeout(3000)
        pg.time.delay(3000)
        self.running = False

    ##
    ## PRIVATE METHODS
    ##
    def _song_over(self):
        pass

    def _get_duration(self):
        if not self.song_in_progress:
            position = self.song_length
        else:
            position = round(self._get_position(self.song_offset), 2)
        hours = "{:0>2d}".format(int(position // 3600))
        mins = "{:0>2d}".format(int(position // 60))
        secs = "{:0>2d}".format(int(position % 60))
        tenths = int(10 * (position % 60 - int(position % 60)))

        print(hours, mins, secs, tenths)
        return hours, mins, secs, tenths

    def _get_position(self, start_pos, rew=0, ff=0):
        position = pg.mixer.music.get_pos() / 1000 + start_pos - rew + ff
        if position < 0:
            return 0
        elif position > self.song_length:
            return self.song_length - 1
        else:
            return position

    def _load_song(self, selection='pass'):
        if selection == 'random':
            self.now_playing_index = randrange(0, len(self.song_paths))

        if selection == 'prev' and self.now_playing_index - 1 >= 0:
            self.now_playing_index -= 1

        if selection == 'next' and self.now_playing_index + 1 < len(self.song_paths):
            self.now_playing_index += 1
        elif selection == 'next':
            # do not restart the track
            selection = 'pass'

        # custom end event to alert when song is over (non-user only)
        pg.mixer.music.set_endevent(self.SONG_OVER)
        if selection != 'pass':
            self.song_offset = 0
            pg.mixer.music.load(self.song_paths[self.now_playing_index])
            self._log_song_length()      

    def _log_song_length(self):
        song = OggVorbis(self.song_paths[self.now_playing_index])
        self.song_length = song.info.length

    def _get_button(self, label):
        btns = []
        for btn in self.buttons.sprites():
            if btn.label == label:
                btns.append(btn)
        return btns[0]

    def _group_buttons(self):
        # add setup icon to GroupSingle sprite group
        centeringx = (WIDTH - PAD*2 - BSIZE) // 2 + PAD
        centeringy = PAD + self.setup_txt.get_height() + PAD
        self.setup_button.add(ToggleButton('menu', centeringx, centeringy))

        # Spacing for icons (sprites)
        rowpad = (WIDTH - BSIZE*7 - BPAD*6) // 2
        rowslot = BSIZE + BPAD
        row1_y = HEIGHT - BPAD*3 - BSIZE*3  
        row2_y = HEIGHT - BPAD*2 - BSIZE*2
        row3_y = HEIGHT - BPAD - BSIZE        

        # add buttons to sprite group
        self.buttons.add(
            
            QuickButton('prev', rowpad, row1_y),
            HoldButton('voldown', rowpad + rowslot, row2_y, self.volumize),
            StopButton('stop', rowpad + 2*rowslot, row1_y),
            ToggleButton('play', rowpad + 3*rowslot, row1_y),
            ToggleButton('pause', rowpad + 4*rowslot, row1_y),
            SeekButton('ff', rowpad + 5*rowslot, row1_y),
            QuickButton('next', rowpad + 6*rowslot, row1_y),
            HoldButton('volup', WIDTH - rowpad - BSIZE - rowslot, row2_y, self.volumize),
            SeekButton('rew', rowpad + rowslot, row1_y),             
            MuteButton('mute', WIDTH - rowpad - BSIZE, row2_y, self.volume),            
            # Button('menu', rowpad, row2_y),
            ToggleButton('power', (WIDTH - BSIZE) // 2, row3_y),  
        )  

    ##
    ## RUN CONSOLE
    ##
    def run(self):
        self.win.blit(self.bg, (0,0))

        if self.running:
            if not self.setup_mode:
                self.buttons.update()
                self.buttons.draw(self.win)

                # duration display
                hours, mins, secs, tenths = self._get_duration()
                time_played_text = self.font_goodbye.render(f'{hours}:{mins}:{secs}.{tenths}', True, FONT_COLOR)
                self.win.blit(time_played_text, ((WIDTH - PAD*2 - time_played_text.get_width()) // 2 + PAD, PAD))
            else: 
                self.setup()

        if debug:
            debug([f'sip: {self.song_in_progress}, off: {self.song_offset}, pos: {pg.mixer.music.get_pos()}'])