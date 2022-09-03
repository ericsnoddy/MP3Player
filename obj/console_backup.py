from os import walk
from os.path import join
from random import randrange

import pygame
from pygame.locals import *
from tkinter import filedialog
from mutagen.oggvorbis import OggVorbis

from obj.settings import WIDTH, HEIGHT, PAD, BPAD, BSIZE, BG_DEFAULT, FONT_TYPE_REG,  FONT_TYPE_BOLD, FONT_COLOR, VOL_START, SEEK_INCR
from obj.button import Button, QuickButton, VolumeButton, MuteButton
from obj.debug import debug

class Console:
    def __init__(self, win):

        self.debug = True
        self.font_debug = pygame.font.Font(FONT_TYPE_REG, 6)

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
        self.now_playing_index = 0
        self.song_in_progress = False
        self.song_playing = False
        self.skip_time = 0
        self.song_length = 0
        self.time_stamp = 0
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
            MuteButton('mute', WIDTH - rowpad - BSIZE, row2_y, 'Mute'),
            QuickButton('stop', rowpad + 2*rowslot, row1_y, 'Stop'),
            Button('play', rowpad + 3*rowslot, row1_y, 'Play'),
            Button('pause', rowpad + 4*rowslot, row1_y, 'Pause'), 
            QuickButton('prev', rowpad, row1_y, 'Previous'),
            QuickButton('next', rowpad + 6*rowslot, row1_y, 'Next'),
            VolumeButton('voldown', rowpad + rowslot, row2_y, 'Volume Down'),
            VolumeButton('volup', WIDTH - rowpad - BSIZE - rowslot, row2_y, 'Volume Up'),
            Button('rew', rowpad + rowslot, row1_y, 'Rewind'), 
            Button('ff', rowpad + 5*rowslot, row1_y, 'Fast Forward'),
            Button('menu', rowpad, row2_y, 'Menu'),       
            
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
                    self.activate(False, 'play', 'pause')
                    self.song_in_progress = False
                    self.song_playing = False
                    self.reset_progress()
                    pygame.mixer.music.stop()

                if b.label == 'play' and b.can_click and not self.song_playing:
                    b.log_click()
                    b.activate()
                    if self.song_in_progress:
                        self.song_playing = True
                        self.activate(False, 'pause')
                        pygame.mixer.music.unpause()
                        self.off_time += pygame.time.get_ticks() - self.paused_time
                        self.paused_time = 0
                    elif not self.song_in_progress:
                        self.song_in_progress = True
                        self.song_playing = True
                        self.activate(False, 'stop')
                        self.load_and_play()
                        self.off_time = 0
                        self.start_time = pygame.time.get_ticks()

                if b.label == 'prev' or b.label == 'next':
                    if b.can_click:
                        b.log_click()
                        self.reset_progress()                   
                        self.activate('play')
                        self.activate(False, 'stop', 'pause')
                        self.song_in_progress = True
                        self.song_playing = True
                        self.start_time = pygame.time.get_ticks()

                        if b.label == 'prev' and self.now_playing_index > 0:
                            self.load_and_play('prev')
                        if b.label == 'next' and self.now_playing_index < len(self.collection) - 1:
                            self.load_and_play('next')

                if b.label == 'pause' and b.can_click and self.song_in_progress:
                    b.log_click()
                    if self.song_playing:
                        self.song_playing = False
                        b.activate()
                        self.activate(False, 'play')
                        self.paused_time = pygame.time.get_ticks()
                        pygame.mixer.music.pause()
                    else:
                        self.song_playing = True
                        b.activate(False)
                        self.activate(True, 'play')
                        self.paused_time = 0
                        pygame.mixer.music.unpause()

                if b.label == 'rew' or b.label == 'ff':
                    if b.can_click and self.song_in_progress:
                        if b.label == 'rew': 
                            self.seek(-1)
                        else: 
                            self.seek(1)
                    
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

    def load_and_play(self, selection = 'random'):   
        if selection == 'random':
            self.now_playing_index = randrange(0, len(self.song_paths))            
        if selection == 'prev':
            self.now_playing_index -= 1
        if selection == 'next':
            self.now_playing_index += 1

        song = OggVorbis(self.song_paths[self.now_playing_index])
        self.song_length = song.info.length
        pygame.mixer.music.load(self.song_paths[self.now_playing_index])
        pygame.mixer.music.play()   

    def seek(self, direction):
        # -1 rew, 1 ff
        total_secs = self.time_stamp // 1000
        new_pos = total_secs + direction * 15
        if new_pos >= 0 and new_pos < self.song_length:
            self.skip_time += direction * 15
            pygame.mixer.music.set_pos(new_pos)    

    def format_duration(self, duration):
        tot_secs = (duration / 1000 )
        hours = int((tot_secs / 3600) % 24)
        mins = int((tot_secs / 60) % 60)
        secs = int(tot_secs % 60)

        return '{}:{:02.0f}:{:02.0f}'.format(hours, mins, secs)

    def reset_progress(self):
        self.time_stamp = 0
        self.start_time = 0
        self.paused_time = 0
        self.off_time = 0
        self.skip_time = 0

    def say_goodbye(self):

        self.win.blit(self.bg, (0,0))
        self.win.blit(self.goodbye_txt, 
                ((WIDTH - self.goodbye_txt.get_width()) // 2, 
                (HEIGHT - self.goodbye_txt.get_height()) // 2))

        pygame.display.update()
        if self.song_playing:
            pygame.mixer.music.fadeout(3000)
        pygame.time.delay(3000)        
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
            if self.song_in_progress:
                self.time_stamp = pygame.time.get_ticks() - self.off_time - self.start_time  + (self.skip_time * 1000)                 
                if not self.song_playing:
                    self.off_time = pygame.time.get_ticks() - self.paused_time

            duration = self.font_goodbye.render(self.format_duration(self.time_stamp), True, FONT_COLOR)
            self.win.blit(duration, ((WIDTH - PAD*2 - duration.get_width()) // 2 + PAD, PAD))
        else:    
            self.setup()

        if self.debug:
            if self.collection:
                now = pygame.time.get_ticks()
                ts = self.time_stamp
                st = self.start_time
                ot = self.off_time
                pt = self.paused_time
                skt = self.skip_time

                debug(['{} = {} - {} - {} + {}'.format(ts, now, ot, st, skt),
                        '{} = {} - {}'.format(ot, now, pt)
                        ])
            
