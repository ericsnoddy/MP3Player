from os import walk
from os.path import join
from random import randrange

import pygame as pg
from pygame.locals import *
from tkinter import filedialog
from mutagen.oggvorbis import OggVorbis

from obj.settings import WIDTH, HEIGHT, PAD, BPAD, BSIZE, BG_DEFAULT, FONT_TYPE_REG, FONT_TYPE_BOLD, FONT_COLOR, VOL_START
from obj.button import Button, QuickButton, VolumeButton, MuteButton
from obj.debug import debug

class Console:
    def __init__(self, win):

        self.debug = True
        self.font_debug = pg.font.Font(FONT_TYPE_REG, 6)

        self.running = True
        self.win = win

        # audio
        pg.mixer.init()
        pg.mixer.music.set_volume(VOL_START)

        self.bg = pg.image.load(BG_DEFAULT).convert()
        self.font_reg = pg.font.Font(FONT_TYPE_REG, 14)
        self.font_goodbye = pg.font.Font(FONT_TYPE_BOLD, 50)
        self.font_list = pg.font.Font(FONT_TYPE_REG, 8)
        self.font_list_bold = pg.font.Font(FONT_TYPE_BOLD, 10)

        # default flags and user setup
        self.setup_mode = True
        self.show_setup_button = True
        self.music_folder = None
        self.collection = []
        self.song_paths = []

        # Now playing
        self.now_playing_index = 0
        self.song_in_progress = False
        self.song_playing = False
        self.song_pos = 0
        self.song_length = 0
        self.skip_time = 0        
        self.time_stamp = 0

        # All the text that can be pre-rendered
        self.setup_txt = self.font_reg.render('Select music folder', True, FONT_COLOR)
        self.goodbye_txt = self.font_goodbye.render('Ciao!', True, FONT_COLOR)

        # buttons (requires self.setup_txt)
        self.buttons = pg.sprite.Group()
        self.setup_button = pg.sprite.GroupSingle()
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
        self.setup_button.add(Button('menu', centeringx, centeringy))

        # Spacing for icons (sprites)
        rowpad = (WIDTH - BSIZE*7 - BPAD*6) // 2
        rowslot = BSIZE + BPAD
        row1_y = HEIGHT - BPAD*3 - BSIZE*3  
        row2_y = HEIGHT - BPAD*2 - BSIZE*2
        row3_y = HEIGHT - BPAD - BSIZE        

        # add buttons to sprite group
        self.buttons.add(
            Button('power', (WIDTH - BSIZE) // 2, row3_y),
            MuteButton('mute', WIDTH - rowpad - BSIZE, row2_y),
            QuickButton('stop', rowpad + 2*rowslot, row1_y),
            Button('play', rowpad + 3*rowslot, row1_y),
            Button('pause', rowpad + 4*rowslot, row1_y), 
            QuickButton('prev', rowpad, row1_y),
            QuickButton('next', rowpad + 6*rowslot, row1_y),
            VolumeButton('voldown', rowpad + rowslot, row2_y),
            VolumeButton('volup', WIDTH - rowpad - BSIZE - rowslot, row2_y),
            QuickButton('rew', rowpad + rowslot, row1_y), 
            QuickButton('ff', rowpad + 5*rowslot, row1_y),
            Button('menu', rowpad, row2_y),            
        )    

    def click_handler(self):
        if self.event.type == MOUSEBUTTONDOWN:
            clicked = [button for button in self.buttons.sprites() if button.is_clicked(self.event.pos)]
           
            for b in clicked:
                if b.label == 'power':
                    self.say_goodbye()

                if b.label == 'voldown':
                    b.volumize('-')
                    self.activate(False, 'mute')

                if b.label == 'volup':
                    b.volumize('+')
                    self.activate(False, 'mute')

                if b.label == 'mute' and b.can_click:
                    b.log_click()
                    b.toggle_mute()

                if b.label == 'stop' and b.can_click and self.song_in_progress:
                    b.log_click()
                    b.activate()
                    self.activate(False, 'play', 'pause', 'mute')
                    self.song_in_progress = False
                    self.song_playing = False
                    pg.mixer.music.stop()
                    self.song_pos = 0

                if b.label == 'play' and b.can_click and not self.song_playing:
                    b.log_click()
                    b.activate()
                    if self.song_in_progress:
                        self.song_playing = True
                        self.activate(False, 'pause')
                        pg.mixer.music.unpause()
                    elif not self.song_in_progress:
                        self.song_in_progress = True
                        self.song_playing = True
                        self.activate(False, 'stop')
                        self.load_song()
                        pg.mixer.music.play()

                if b.label == 'prev' or b.label == 'next':
                    if b.can_click:
                        b.log_click()          
                        self.activate('play')
                        self.activate(False, 'stop', 'pause')
                        self.song_in_progress = True
                        self.song_playing = True
                        self.song_pos = 0

                        if b.label == 'prev' and self.now_playing_index > 0:
                            self.load_song('prev')
                            pg.mixer.music.play()
                        if b.label == 'next' and self.now_playing_index < len(self.collection) - 1:
                            self.load_song('next')
                            pg.mixer.music.play()

                if b.label == 'pause' and b.can_click and self.song_in_progress:
                    b.log_click()
                    if self.song_playing:
                        self.song_playing = False
                        b.activate()
                        self.activate(False, 'play')
                        pg.mixer.music.pause()
                    else:
                        self.song_playing = True
                        b.activate(False)
                        self.activate(True, 'play')
                        pg.mixer.music.unpause()

                if b.label == 'rew' or b.label == 'ff':
                    if b.can_click and self.song_in_progress:
                        b.log_click()
                        if b.label == 'rew':
                            self.song_pos = self.seek_position(self.song_pos, rewind = 10)
                            pg.mixer.music.play(0, self.song_pos)
                        else:
                            position = self.seek_position(self.song_pos, forward = 10)
                            try:
                                pg.mixer.music.play(0, position)
                            except:
                                pass
                            else:
                                self.song_pos = position                   
                    
        if self.event.type == MOUSEBUTTONUP:
            get_vol_buttons = [button for button in self.buttons.sprites() if button.label[0:3] == 'vol']
            for vol in get_vol_buttons:
                vol.volup_active = False
                vol.voldown_active = False

    def activate(self, activate, *butt_labels):

        butts = [
            [b for b in self.buttons.sprites() if b.label == 'stop'][0],
            [b for b in self.buttons.sprites() if b.label == 'play'][0],
            [b for b in self.buttons.sprites() if b.label == 'pause'][0],
            [b for b in self.buttons.sprites() if b.label == 'mute'][0]]

        for butt in butts:
            if butt.label in butt_labels:
                if activate:
                    butt.is_active = True
                else:
                    butt.is_active = False

                    # janky solution to returning saved volume if song is played-muted-stopped-played 
                    if butt.label == 'mute':
                        pg.mixer.music.set_volume(butt.saved_volume)

    def load_song(self, selection = 'random'):   
        if selection == 'random':
            self.now_playing_index = randrange(0, len(self.song_paths))            
        if selection == 'prev':
            self.now_playing_index -= 1
        if selection == 'next':
            self.now_playing_index += 1

        song = OggVorbis(self.song_paths[self.now_playing_index])
        self.song_length = song.info.length
        pg.mixer.music.load(self.song_paths[self.now_playing_index])           

    def seek_position(self, start_pos, rewind=0, forward=0):
        position = pg.mixer.music.get_pos() / 1000 + start_pos - rewind + forward
        return position if position >= 0 else 0

    # def seek(self, direction):
    #     # -1 rew, 1 ff
    #     position = pg.mixer.music.get_pos() / 1000 + start_pos - rewind + forward
    #     new_pos = total_secs + direction * 15
    #     if new_pos >= 0 and new_pos < self.song_length:
    #         self.skip_time += direction * 15
    #         pg.mixer.music.play(0, new_pos)    

    def display_duration(self):
        position = round(self.seek_position(self.song_pos), 2)
        hours = "{:0>2d}".format(int(position // 3600))
        mins = "{:0>2d}".format(int(position // 60))
        secs = "{:0>2d}".format(int(position % 60))
        tenths = int(10 * (position % 60 - int(position % 60)))

        time_played_text = self.font_goodbye.render(f'{hours}:{mins}:{secs}.{tenths}', True, FONT_COLOR)
        self.win.blit(time_played_text, ((WIDTH - PAD*2 - time_played_text.get_width()) // 2 + PAD, PAD))

    def say_goodbye(self):

        self.win.blit(self.bg, (0,0))
        self.win.blit(self.goodbye_txt, 
                ((WIDTH - self.goodbye_txt.get_width()) // 2, 
                (HEIGHT - self.goodbye_txt.get_height()) // 2))

        pg.display.update()
        if self.song_playing:
            pg.mixer.music.fadeout(3000)
        pg.time.delay(3000)        
        self.running = False

    def event_handler(self, event):
        self.event = event
        self.click_handler()

    def run(self):
        self.win.blit(self.bg, (0,0))

        if not self.setup_mode:
            self.buttons.update()
            self.buttons.draw(self.win)

            #duration display            
            self.display_duration()            
        else:    
            self.setup()

        if self.debug:
            if self.collection:                
                pass
