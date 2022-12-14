# standard library
from os import walk
from os.path import join
from random import randrange

# third party
import pygame as pg
from pygame.locals import *
from tkinter import filedialog as fd    # pip install tk

# local
from obj.slider import Slider
from obj.display import ListUI, NowPlaying
from obj.button import ToggleButton, QuickButton, HoldButton, MuteButton, ModeButton, StopButton, SeekButton
from obj.data import BG_DEFAULT, FONT_TYPE_REG, FONT_TYPE_BOLD
from obj.settings import (
    WIDTH, 
    HEIGHT, 
    PAD, 
    BPAD, 
    BSIZE,
    ROWPAD,
    ROWSLOT,
    ROW1_Y,
    ROW2_Y,
    ROW3_Y,
    UI_HEIGHT,
    FONT_COLOR, 
    VOL_START,
    SEEK_INCR,
    OPEN_RANDOM_MODE,
)

class Console:
    def __init__(self, win, play_mode):

        # if the console stops running, main() will quit
        self.running = True

        # get the display surface
        self.win = win

        # audio init - set_volume takes a float between 0 and 1; I divide a volume value by 100 for a convenient standard
        pg.mixer.init()
        self.volume = VOL_START
        pg.mixer.music.set_volume(self.volume / 100)

        # background
        self.bg = pg.image.load(BG_DEFAULT).convert()

        # fonts
        self.font_reg = pg.font.Font(FONT_TYPE_REG, 14)
        self.font_duration = pg.font.Font(FONT_TYPE_BOLD, 8)
        self.font_goodbye = pg.font.Font(FONT_TYPE_BOLD, 50)

        # default flags and user setup
        self.setup_mode = True
        self.music_folder = None
        self.song_paths = []

        # console player flags
        self.song_in_progress = False
        self.now_playing_index = 0
        self.song_offset = 0    # tracks the time duration of playing song minus pause time and rew/ff
        self.song_length = 0

        # mode settings
        # # 'reg' -> 'loop' -> 'rand' -> 'reg' ...
        # Determined by main.py parsing command line args
        self.play_mode = play_mode

        # custom flag for event handler - song has ended its duration
        self.SONG_OVER = pg.USEREVENT+1
        pg.mixer.music.set_endevent(self.SONG_OVER)

        # All the text that can be pre-rendered for performance
        self.setup_txt = self.font_reg.render('Browse to .mp3 folders', True, FONT_COLOR)
        self.setup_txt2 = self.font_reg.render('An especially large collection may cause lag', True, FONT_COLOR)
        self.goodbye_txt = self.font_goodbye.render('Ciao!', True, FONT_COLOR)

        # button sprite group & slider bar setup
        self.buttons = pg.sprite.Group()
        self.setup_button = pg.sprite.GroupSingle()
        self.setup_button_clicked = False   # work around to prevent first click not always registering (???)
        self._group_btns()
        self._init_bars()
        # see setup() for file display ui init - it reqs file list
        
    def setup(self):
        if not self.music_folder:
            # display setup text and button
            self.win.blit(self.setup_txt, ((WIDTH - PAD*2 - self.setup_txt.get_width()) // 2 + PAD, PAD))
            self.setup_button.draw(self.win)
            self.win.blit(self.setup_txt2, ((WIDTH - PAD*2 - self.setup_txt2.get_width()) // 2 + PAD, PAD + self.setup_txt.get_height() + PAD + BSIZE + PAD))

            # get folder - see event_handler in main() and flag in self.handle_misc_clicks()
            if self.setup_button_clicked:
                self.music_folder = fd.askdirectory( title='Navigate to MP3 Folder' )

        # do not proceed without proper filepath to music folder
        elif not self.song_paths:
            for root, _, files in walk(self.music_folder):
                for filename in files:
                    if filename.endswith('.mp3'):                    
                        self.song_paths.append(join(root, filename))

            # no valid filetypes - start over
            if len(self.song_paths) == 0:
                self.music_folder = None
        else:
            # initialize the list and infobar ui
            self._init_ui()

            # load first track and end setup mode
            if OPEN_RANDOM_MODE:
                self.now_playing_index = randrange(0, len(self.song_paths))
            else:
                self.now_playing_index = 0

            pg.mixer.music.load(self.song_paths[self.now_playing_index])

            # scrolls the list to the current selected song
            self.list_ui.scrolly_from_index(self.now_playing_index)

            self._log_song_length()            
            self.setup_mode = False

    def mute(self, mute_btn):
        mute_btn.log_click()

        # toggle button, adjust volume bar, adjust volume; toggle_mute returns 0 or saved volume (int out of 100)
        self.volume = mute_btn.toggle_mute(self.volume)

        # adjust the volume bar to the new volume
        self.volbar.value_to_pos(self.volume, 100)
        pg.mixer.music.set_volume(self.volume / 100)

    def stop(self, stop_btn):
        stop_btn.log_click()

        if self.song_in_progress:          

            self.song_in_progress = False

            # deactivate/activate relevant btns
            play_btn = self._get_button('play')
            play_btn.activate(False)

            pause_btn = self._get_button('pause')
            pause_btn.activate(False)

            stop_btn.activate()
            pg.mixer.music.stop()

    def play(self, play_btn):
        play_btn.log_click()

        # the song is started but not currently playing; 
        # unpause the mixer if paused, else play the selected song
        if self.song_in_progress and not pg.mixer.music.get_busy():
            pause_btn = self._get_button('pause')
            if pause_btn.is_active:
                self.pause(pause_btn)
            else:
                self.song_in_progress = False
                self.play(play_btn)
        
        # if "play" but song is not started, activate play btn, deactivate stop btn, play currently loaded song
        elif not self.song_in_progress:
            play_btn.activate()
            self.song_in_progress = True
            stop_btn = self._get_button('stop')
            if stop_btn.is_active:
                stop_btn.activate(False)
            pg.mixer.music.play()

    def pause(self, pause_btn):
        pause_btn.log_click()

        # see README.md for closer look at this method
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
        skip_btn.log_click()

        # skip logic: if song is started and currently playing, load a new song and play it
        # if song is started but not currently playing, load a new song but do not start playing
        # if song is not started load the next song but do not start playing
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

    def seek(self, seek_btn, incr=SEEK_INCR):
        seek_btn.log_click()

        if seek_btn.label == 'rew':
            self.song_offset = self._get_position(self.song_offset, rew=incr)            

        if seek_btn.label == 'ff':
            self.song_offset = self._get_position(self.song_offset, ff=incr)
        
        if pg.mixer.music.get_busy():
            # 0 sets the number of loops (loop mode is handled differently in this program); 
            # song_offset is the current song pos in seconds
            pg.mixer.music.play(0, self.song_offset)

    def volumize(self, vol_btn):
        vol_btn.activate()

        mute_btn = self._get_button('mute')
        if mute_btn.is_active:
            # mute_btn is a specialized ToggleButton that can be held down
            # this updates volume on the fly and adjusts the volume bar
            self.volume = mute_btn.toggle_mute(self.volume)   

        if vol_btn.label == 'volup' and self.volume < 100:
            self.volume += 1
        if vol_btn.label == 'voldown' and self.volume > 0:
            self.volume -= 1

        self.volbar.value_to_pos(self.volume, 100)        
        pg.mixer.music.set_volume(self.volume / 100)        

    def toggle_mode(self, mode_btn):
        mode_btn.log_click()

        # pass-thru function between main.py and ModeButton obj
        self.play_mode = mode_btn.toggle_mode()

    def adjust_volbar(self, click_x):

        # pos_to_value gets new volume value based on x-axis mouse click if collision detected
        # it readjusts the volbar to the new volume
        self.volume = self.volbar.pos_to_value(click_x, 100)
        pg.mixer.music.set_volume(self.volume / 100)
        self.volbar.value_to_pos(self.volume, 100)
        mute_btn  = self._get_button('mute')
        if mute_btn.is_active:
            mute_btn.activate(False)

    def adjust_progbar(self, click_x):
        # This returns the position mark in seconds we need to seek to
        new_position = self.progbar.pos_to_value(click_x, self.song_length)
        current_position = self._get_position(self.song_offset)

        # We can use the seek function with calculated seek increments; added default flag to seek() for seek_incr
        if new_position > current_position:
            ff_btn = self._get_button('ff')
            self.seek(ff_btn, incr=(new_position - current_position))
        elif new_position < current_position:
            rew_btn = self._get_button('rew')
            self.seek(rew_btn, incr=(current_position - new_position))

    def scroll(self, direction, page=False):

        # pass-thru method between main() and ListUI obj
        self.list_ui.scroll(direction, page)

    def handle_misc_clicks(self, mouse_pos):

        # The only way I could discover to avoid first click not always detecting is to
        # avoid the pesky pg.mouse.get_pressed() - get mouse event from queue instead
        if self.setup_mode:
            setup_btn = self.setup_button.sprite
            if setup_btn.is_clicked(mouse_pos):
                self.setup_button_clicked = True

        # This runs a check if a collision occurs, signals a change and new index on click
        # actual click handling is managed by self._heed_list_signal()
        else:
            self.list_ui.change_index_click_detection(mouse_pos)        

    def song_over(self):
        # don't cycle if the song was stopped by the user
        stop_btn = self._get_button('stop')
        if not stop_btn.is_active:

            # otherwise load the next song automatically
            self.song_in_progress = False
            self._load_song('auto next')
            play_btn = self._get_button('play')
            self.play(play_btn)

    def power_down(self):
        self.win.blit(self.bg, (0,0))
        self.win.blit(self.goodbye_txt, 
                ((WIDTH - self.goodbye_txt.get_width()) // 2, 
                (HEIGHT - self.goodbye_txt.get_height()) // 2))

        pg.display.update()

        # if a song is playing, fade out the volume over 3 seconds
        if pg.mixer.music.get_busy():
            pg.mixer.music.fadeout(3000)
        pg.time.delay(3000)

        # alert main() that the console has quit
        self.running = False

    ## PRIVATE METHODS
    ##
    def _get_formatted_duration(self):


        position = round(self._get_position(self.song_offset), 2)

        # decimal formatting and conversion of seconds into mins/secs/tenths
        # return a formatted string
        mins = "{:0>2d}".format(int(position // 60))
        secs = "{:0>2d}".format(int(position % 60))
        tenths = int(10 * (position % 60 - int(position % 60)))

        return f'{mins}:{secs}.{tenths}'

    def _get_position(self, start_pos, rew=0, ff=0):

        # This deceptively simple method took a very, very long time to figure out; pygame does not 
        # have an easy way of tracking the time position of the song in general; it can only track 
        # how long the current sound has been playing. So we use various global offsets to keep
        # track of down time and adjust the position accordingly. position 0 = start of song.

        if not self.song_in_progress: pos = 0
        else: pos = pg.mixer.music.get_pos()    # get how long sound playing in ms
        
        position = pos / 1000 + start_pos - rew + ff    # offset with the passed input start_pos and re/ff incr

        if position < 0:
            # do not rew prior to the start of song
            return 0
        elif position > self.song_length:
            # do not ff past the end of the song
            return self.song_length - 1
        else:
            return position

    def _get_formatted_song_length(self):
        
        # this looks almost identical to _get_formatted_duration() and is an oversight on my part;
        # these methods can be combined b/c the only difference is the input position; here it is
        # the total song duration and in the other it is a function to get song position
        position = self.song_length

        mins = "{:0>2d}".format(int(position // 60))
        secs = "{:0>2d}".format(int(position % 60))
        tenths = int(10 * (position % 60 - int(position % 60)))

        return f'{mins}:{secs}.{tenths}'

    def _display_duration(self):

        # elapsed time
        time_played_text = self.font_duration.render(self._get_formatted_duration(), True, FONT_COLOR)
        self.win.blit(time_played_text, (5, ROW1_Y - BSIZE - 2*BPAD + 30))

        # song length
        time_played_text = self.font_duration.render(self._get_formatted_song_length(), True, FONT_COLOR)
        self.win.blit(time_played_text, (self.progbar.rect_border.right + 4, ROW1_Y - BSIZE - 2*BPAD + 30))
        
    def _load_song(self, selection='pass'):

        # LOAD LOGIC
        # Regular mode: 'prev' and 'next' and 'auto next' increment index by 1
        # Rand mode: 'prev and 'next' and 'auto next' generate random index
        # Loop mode: 'prev' and 'next' increment index by 1 but 'auto next' restarts same index
        # Any mode: 'list' loads the list-changed index

        if self.play_mode == 'reg' or self.play_mode == 'loop':
            same_index = self.now_playing_index

            if selection == 'prev' and self.now_playing_index - 1 >= 0:
                self.now_playing_index -= 1
            elif selection == 'prev':
                # restart 0 index track if 0 index track playing + 'prev'
                self.now_playing_index = 0

            if selection == 'next' and self.now_playing_index + 1 < len(self.song_paths):
                self.now_playing_index += 1
            elif selection == 'next':
                # do nothing if index is out of range, ie, the last song in the track
                selection == 'pass'

            if selection == 'auto next':
                if self.play_mode == 'reg':
                    self._load_song('next')
                elif self.play_mode == 'loop':
                    # play same index
                    self.now_playing_index = same_index

        if self.play_mode == 'rand':

            if selection == 'prev' or selection == 'next' or selection == 'auto next':
                # do not skip to the same index
                new_index = randrange(0, len(self.song_paths))
                if new_index != self.now_playing_index:
                    self.now_playing_index = new_index

        if selection == 'list':
            # overwrite any index change thus far
            self.now_playing_index = self.list_ui.change_index

        if selection != 'pass':
            self.song_offset = 0
            try:    # make sure file is not corrupt/unreadable, else go to next song
                pg.mixer.music.load(self.song_paths[self.now_playing_index])
                self._log_song_length()

                # scroll list to the currently selected song if row not visible
                self.list_ui.scrolly_from_index(self.now_playing_index)
            except:
                next_btn = self._get_button('next')
                self.skip(next_btn)                 

    def _log_song_length(self):

        # borrow a method from NowPlaying obj to get the song duration in seconds
        self.song_length = self.now_playing.get_meta('length', self.now_playing_index)

    def _heed_list_signal(self):

        # Here the console listens for a change song signal from ListUI obj
        if self.list_ui.change_signal:
            self._load_song('list')
            play_btn = self._get_button('play')
            self.play(play_btn)
            self.list_ui.change_signal = False

    def _get_button(self, label):

        # method for retrieving a button sprite in order for other buttons to interact with it
        btns = []
        for btn in self.buttons.sprites():
            if btn.label == label:
                btns.append(btn)
        return btns[0]

    def _group_btns(self):
        # add setup icon to GroupSingle sprite group
        centeringx = (WIDTH - PAD*2 - BSIZE) // 2 + PAD
        centeringy = PAD + self.setup_txt.get_height() + PAD

        # Add sprite to a SpriteSingle group. This is for convenient interaction
        self.setup_button.add(ToggleButton('menu', centeringx, centeringy))

        # add buttons to sprite group - passed functions do not include ()
        self.buttons.add(            
            QuickButton('prev', ROWPAD, ROW1_Y),
            HoldButton('voldown', ROWPAD + ROWSLOT, ROW2_Y, self.volumize),
            StopButton('stop', ROWPAD + 2*ROWSLOT, ROW1_Y),
            ToggleButton('play', ROWPAD + 3*ROWSLOT, ROW1_Y),
            ToggleButton('pause', ROWPAD + 4*ROWSLOT, ROW1_Y),
            SeekButton('ff', ROWPAD + 5*ROWSLOT, ROW1_Y),
            QuickButton('next', ROWPAD + 6*ROWSLOT, ROW1_Y),
            HoldButton('volup', WIDTH - ROWPAD - BSIZE - ROWSLOT, ROW2_Y, self.volumize),
            SeekButton('rew', ROWPAD + ROWSLOT, ROW1_Y),             
            MuteButton('mute', WIDTH - ROWPAD - BSIZE, ROW2_Y, self.volume),            
            ModeButton('mode', ROWPAD, ROW2_Y, self.play_mode),
            ToggleButton('power', (WIDTH - BSIZE) // 2, ROW3_Y),  
        )

    def _init_bars(self):
        # volume bar - reqs the current volume and the max volume
        x = ROWPAD + 2*ROWSLOT
        w = WIDTH - ROWPAD - BSIZE - ROWSLOT - BPAD - x
        self.volbar = Slider(x, ROW2_Y + 10, w, BSIZE - 20, self.volume, 100)

        # song progress bar - reqs the current song position and the total song length
        self.progbar = Slider(BSIZE + BPAD, ROW1_Y - BSIZE + 2*BPAD, WIDTH - 2*(BSIZE + BPAD), BPAD - 1, self._get_position(self.song_offset), self.song_length)

    def _init_ui(self):

        # init file display ui - reqs the song filepaths and the currently selected song (index)
        self.list_ui = ListUI(self.win, PAD//2, 2*PAD + 10, WIDTH - PAD, UI_HEIGHT, self.song_paths, self.now_playing_index)   
        # Now Playing infobar
        self.now_playing = NowPlaying(self.win, PAD//2, 2, WIDTH - PAD, 70, self.song_paths, self.now_playing_index)

    ## RUN CONSOLE
    ##
    def run(self):

        # display the background
        self.win.blit(self.bg, (0,0))

        if self.running:
            if self.setup_mode:
                self.setup()
            else:
                # button sprites
                self.buttons.update()
                self.buttons.draw(self.win)

                # duration display
                self._display_duration()

                # clickable volume and progress bars
                self.volbar.draw()
                self.progbar.value_to_pos(self._get_position(self.song_offset), self.song_length)
                self.progbar.draw()

                # clickable songlist - listen for change signal from self.list_ui obj
                self._heed_list_signal()
                self.list_ui.update(self.now_playing_index)
                self.list_ui.draw()

                # now playing info display
                self.now_playing.update(self.now_playing_index)
                self.now_playing.draw()