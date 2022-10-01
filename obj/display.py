# third party
import pygame as pg
from pygame.locals import *
from mutagen.easyid3 import EasyID3 # for extracting metadata
from mutagen.mp3 import MP3

# local
from obj.settings import (
    FONT_COLOR,
    FONT_COLOR_TITLE,
    FONT_COLOR_ARTIST,
    FONT_COLOR_ALBUM,
    LIST_BORDER_COLOR, 
    INFO_BORDER_COLOR, 
    LIST_FONTSIZE,
    LIST_ROW_HEIGHT,
    LIST_FONT_COLOR,
    NP_FONTSIZE_TITLE, 
    NP_FONTSIZE_ARTIST, 
    NP_FONTSIZE_ALBUM,
)
from obj.data import FONT_TYPE_REG, FONT_TYPE_BOLD

class NowPlaying:
    def __init__(self, win, x, y, w, h, song_paths, now_playing_index):

        # display window and default rectangle
        self.win = win
        self.rect = pg.Rect(x, y, w, h)

        # file info and currently
        self.song_paths = song_paths
        self.titles = self._get_titles_list(self.song_paths)
        self.now_playing_index = now_playing_index

        # get initial metadata
        self.artist = self.get_meta('artist', self.now_playing_index)
        self.album = self.get_meta('album', self.now_playing_index)
        self.song = self.get_meta('title', self.now_playing_index)

        # fonts
        self.song_font = pg.font.Font(FONT_TYPE_BOLD, NP_FONTSIZE_TITLE)        
        self.artist_font = pg.font.Font(FONT_TYPE_REG, NP_FONTSIZE_ARTIST)        
        self.album_font = pg.font.Font(FONT_TYPE_REG, NP_FONTSIZE_ALBUM)

    ## Public Functions
    #
    def get_meta(self, key, playing_index):
        
        try:
            # mutagen method for making an MP3 obj with metadata Dict we can read
            # the values of the Dict are Lists, so we return the 0 index.
            meta = MP3(self.song_paths[playing_index], ID3=EasyID3)
        except:
            return 'Unknown'
        
        if key == 'title':
            try:
                song = meta['title'][0]
            except:
                song = self.titles[playing_index]
            return song
            
        elif key == 'album':
            try:
                album = meta['album'][0]
            except:
                album = 'Unknown Album'
            return album

        elif key == 'artist':
            try:
                artist = meta['artist'][0]
            except:
                artist = 'Unknown Artist'
            return artist

        elif key == 'track':
            try:
                track = meta['tracknumber'][0]
            except:
                track = '#'
            return track

        elif key == 'length':
            try:
                length = meta.info.length
            except:
                length = 0
            return length

    ## Private Functions
    #
    def _get_titles_list(self, song_paths):
        song_titles = []
        
        filenames = [song_path.rsplit('\\') for song_path in song_paths]
        for list in filenames:
            # Keep last indexed value of the split filepaths; then split off filetype, keep the 0 index value of that
            # Due to filtering in the setup process all files will have a proper extension
            song_titles.append(list[-1])    
        return song_titles

    def _get_scaled_text(self, old_text_width, font_type, font_color, text):

        # set the default font size for each category
        if text == self.song: fontsize = NP_FONTSIZE_TITLE
        elif text == self.artist: fontsize = NP_FONTSIZE_ARTIST
        else: fontsize = NP_FONTSIZE_ALBUM

        # overwrite the font size to rescale the text when it doesn't fit the display
        new_font_size = int(((self.rect.width - 4) / old_text_width) * fontsize)
        new_font = pg.font.Font(font_type, new_font_size)
        meta_text = new_font.render(text, True, font_color)
        width = meta_text.get_width()

        # return the renderd text w/ font_type and font_color + text width
        return meta_text, width

    ## Update and Run
    #
    def update(self, new_index):

        if self.now_playing_index != new_index:           
            self.now_playing_index = new_index

            # refresh the metadata if a new song begins (self.now_playing_index has changed)
            self.artist = self.get_meta('artist', self.now_playing_index)
            self.album = self.get_meta('album', self.now_playing_index)
            self.song = self.get_meta('title', self.now_playing_index)

            # reset font size
            self.song_font = pg.font.Font(FONT_TYPE_BOLD, NP_FONTSIZE_TITLE)        
            self.artist_font = pg.font.Font(FONT_TYPE_REG, NP_FONTSIZE_ARTIST)        
            self.album_font = pg.font.Font(FONT_TYPE_REG, NP_FONTSIZE_ALBUM)

    def draw(self):

        # draw the border
        pg.draw.rect(self.win, INFO_BORDER_COLOR, self.rect, 1)

        # render the metadata for each category into text and get its width
        song_txt = self.song_font.render(self.song, True, FONT_COLOR_TITLE)
        song_w = song_txt.get_width()

        # if text too wide, scale the font size
        if song_w > self.rect.width - 8:
            song_txt, song_w = self._get_scaled_text(song_w, FONT_TYPE_BOLD, FONT_COLOR_TITLE, self.song)
        
        # Repeat for artist and center between title and album
        artist_txt = self.artist_font.render(self.artist, True, FONT_COLOR_ARTIST)
        artist_w = artist_txt.get_width()

        if artist_w > self.rect.width - 8:
            artist_txt, artist_w = self._get_scaled_text(artist_w, FONT_TYPE_REG, FONT_COLOR_TITLE, self.artist)
        
        # repeat for album at bottom of rect
        album_txt = self.album_font.render(self.album, True, FONT_COLOR_ALBUM)
        album_w = album_txt.get_width()

        if album_w > self.rect.width - 8:
            album_txt, album_w = self._get_scaled_text(album_w, FONT_TYPE_REG, FONT_COLOR_TITLE, self.album)

        # DISPLAY TITLE
        self.win.blit(song_txt, (self.rect.x + 4, self.rect.top + 4))

        # DISPLAY ARTIST
        self.win.blit(artist_txt, (self.rect.x + 4, self.rect.top + NP_FONTSIZE_TITLE + 12))

        # DISPLAY ALBUM
        self.win.blit(album_txt, (self.rect.x + 4, self.rect.bottom - NP_FONTSIZE_ALBUM - 4))

class ListUI(NowPlaying):
    def __init__(self, win, x, y, w, h, song_paths, now_playing_index):
        super().__init__(win, x, y, w, h, song_paths, now_playing_index)

        # subsurface of self.win, the size of our list rectangle
        self.win_sub = self.win.subsurface(self.rect)
        self.scroll_y = 0

        self.now_playing = self.titles[self.now_playing_index]
        # create a transparent surface the size of our display (minus padding) and size of library
        self.list_surf = pg.Surface((self.rect.width - 4, len(self.titles) * LIST_ROW_HEIGHT), pg.SRCALPHA)

        # click cooldown
        self.can_click = False
        self.click_time = pg.time.get_ticks()
        self.click_cooldown = 300

        # need a way to signal console to change songs on list click
        self.change_signal = False
        self.change_index = self.now_playing_index

    def scroll(self, direction, page=False):

        # we want the scroll increments divisible by the LIST_ROW_HEIGHT
        mouse_scroll = LIST_ROW_HEIGHT * 4
        page_scroll = mouse_scroll * 6

        if direction == 'up': 
            if page:
                # do not scroll up if we're at top of list
                self.scroll_y = min(self.scroll_y + page_scroll, 0)
            else:
                self.scroll_y = min(self.scroll_y + mouse_scroll, 0)
        elif direction == 'down':
            if page:
                # do not scroll down past showing at least the ultimate title
                self.scroll_y = max(self.scroll_y - page_scroll, -(self.list_surf.get_height()) + LIST_ROW_HEIGHT)
            else:
                self.scroll_y = max(self.scroll_y - mouse_scroll, -(self.list_surf.get_height()) + LIST_ROW_HEIGHT)

    def change_index_click_detection(self, mouse_pos):

        # if a collision is detected with the list and it's "legal" to click, get the row (song) index
        if self.rect.collidepoint(mouse_pos) and self.can_click:
            self._log_click()

            mouse_y = mouse_pos[1]
            # Derive the index of the song by tracking the y position and its offset and dividing by the row height
            row_index = (mouse_y - (self.rect.top + 1) - self.scroll_y) // LIST_ROW_HEIGHT

            # If the list is clicked below the lowest title, assume the lowest title
            if row_index >= len(self.titles):
                row_index = len(self.titles) - 1

            # Signal to console to change the song
            if self.now_playing_index != row_index:
                self.change_signal = True
                self.change_index = row_index
    
    def scrolly_from_index(self, index):
        # scrolls list if input index is not in visible range
        min_index = -(self.scroll_y) // LIST_ROW_HEIGHT
        max_index = min_index + 27  # There are 28 rows visible
        if index < min_index or index > max_index:
            self.scroll_y = -(LIST_ROW_HEIGHT * index)

    ## PRIVATE METHODS
    ## 
    def _enumerate_list(self):

        f = pg.font.Font(FONT_TYPE_REG, LIST_FONTSIZE)
        f_ = pg.font.Font(FONT_TYPE_BOLD, LIST_FONTSIZE)

        # 'erase' the previous draw for a clean re-draw
        self.list_surf.fill((0))

        y = 1   # 1 px padding
        for index, _ in enumerate(self.titles):
            artist = self.get_meta('artist', index)
            song = self.get_meta('title', index)

            row = f'{artist} - {song}'

            if self.now_playing_index != index:
                self.list_surf.blit(f.render(row, True, LIST_FONT_COLOR), (0, y))
            else: 
                self.list_surf.blit(f_.render(row, True, FONT_COLOR), (0, y))
            y += LIST_ROW_HEIGHT  # font is rendered with 1 px padding

    def _log_click(self):
        self.click_time = pg.time.get_ticks()
        self.can_click = False

    def _cooldown(self):
        current_time = pg.time.get_ticks()

        if not self.can_click:
            if current_time - self.click_time >= self.click_cooldown:
                self.can_click = True

    ## CONTINUOUS METHODS
    ##
    def update(self, new_index):
        if self.now_playing_index != new_index:
            self.now_playing_index = new_index

            # only re-render the list on song change
            # This is the biggest weakness of the program as it's heavy on processing
            self._enumerate_list()

        # deny click spamming by allowing a click once every 300ms
        self._cooldown()

    def draw(self):

        # draw the list border and display the list surface with scroll_y offset (a negative number)
        pg.draw.rect(self.win, LIST_BORDER_COLOR, self.rect, 1)
        self.win_sub.blit(self.list_surf, (4, self.scroll_y))