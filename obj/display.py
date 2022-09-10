import pygame as pg
from mutagen.easyid3 import EasyID3 # for extracting metadata
from mutagen.mp3 import MP3

from obj.settings import FONT_COLOR, LIST_BORDER_COLOR, INFO_BORDER_COLOR, LIST_FONTSIZE_REG, LIST_FONTSIZE_BOLD
from obj.data import FONT_TYPE_REG, FONT_TYPE_BOLD

'''
Okay we really need to think about this. How are we going to build a list of songs combined with metadata
if it exists per file. Do we only extract metadata at the point of blitting? Or do we build a list with
metadata included.

1st try metadata extraction;
if no metadata, blit the filename and unknowns
'''

class ListUI:
    def __init__(self, win, x, y, w, h, song_paths, now_playing_index):

        self.win = win
        self.rect = pg.Rect(x, y, w, h)
        self.border = self.rect.copy()

        self.song_paths = song_paths
        # If metadata doesn't exist, we at least want the filename
        self.song_titles = self._get_titles_list(self.song_paths)
       
        self.now_playing_index = now_playing_index
        self.now_playing = self.song_titles[self.now_playing_index]
        # self._extract_metadata(self.song_paths[self.now_playing_index])

        # fonts
        self.font_list = pg.font.Font(FONT_TYPE_REG, LIST_FONTSIZE_REG )
        self.font_list_bold = pg.font.Font(FONT_TYPE_BOLD, LIST_FONTSIZE_BOLD)

    def _get_title(self, full_path):
        _, _, _, title = self._extract_metadata(full_path)
        return title

    def _get_titles_list(self, song_paths):
        song_titles = []
        
        filenames = [song_path.rsplit('\\') for song_path in song_paths]
        for list in filenames:
            # Keep last indexed value of the split filepaths; then split off filetype, keep the 0 index value of that
            # Due to filtering in the setup process all files will have a proper extension
            song_titles.append(list[-1].rsplit('.')[0])    
        return song_titles

    def _generate_titles(self):
        titles = [name for name in self.song_titles]
        for title in titles:
            yield title

    def _extract_metadata(self, filepath):
        
        meta = MP3(filepath, ID3=EasyID3)
        
        if meta['artist']: artist = meta['artist']
        else: artist = 'Unknown'

        if meta['album']: album = meta['album']
        else: album = 'Unknown'

        if meta['tracknumber']: track = meta['tracknumber']
        else: track = '#'

        if meta['title']: title = meta['title']
        else: title = self.song_titles[self.now_playing_index]
        return artist, album, track, title

    def update(self, new_index):
        self.now_playing = self.song_titles[new_index]

    def draw(self):
        pg.draw.rect(self.win, LIST_BORDER_COLOR, self.rect, 1)

        song_playing_txt = self.font_list_bold.render(self.now_playing, True, FONT_COLOR)
        self.win.blit(song_playing_txt, (self.rect.x + 5, self.rect.y + 5))

class NowPlaying:
    def __init__(self, win, x, y, w, h, song_paths, now_playing_index):

        self.win = win
        self.rect = pg.Rect(x, y, w, h)

        self.song_paths = song_paths
        self.song_titles = self._get_titles_list(self.song_paths)
        self.now_playing_index = now_playing_index

        self.artist = self._get_meta('artist')
        self.album = self._get_meta('album')
        self.song = self._get_meta('title')

    def _get_titles_list(self, song_paths):
        song_titles = []
        
        filenames = [song_path.rsplit('\\') for song_path in song_paths]
        for list in filenames:
            # Keep last indexed value of the split filepaths; then split off filetype, keep the 0 index value of that
            # Due to filtering in the setup process all files will have a proper extension
            song_titles.append(list[-1].rsplit('.')[0])    
        return song_titles

    def _get_meta(self, key):
        
        meta = MP3(self.song_paths[self.now_playing_index], ID3=EasyID3)
        
        if key == 'artist' and meta['artist']: 
            return meta['artist']
        elif key == 'artist':
            return 'Unknown Artist'

        if key == 'album' and meta['album']:
            return meta['album']
        elif key == 'album':
            return 'Unknown Album'

        if key == 'title' and meta['title']:
            return meta['title']
        elif key == 'title':
            return self.song_titles[self.now_playing_index]

    def update(self, new_index):

        if self.now_playing_index != new_index:           
            self.now_playing_index = new_index
            self.artist = self._get_meta('artist')
            self.album = self._get_meta('album')
            self.song = self._get_meta('title')

    def draw(self):
        pg.draw.rect(self.win, INFO_BORDER_COLOR, self.rect, 1)

        # song_playing_txt = self.font_list_bold.render(self.now_playing, True, FONT_COLOR)
        # self.win.blit(song_playing_txt, (self.rect.x + 5, self.rect.y + 5))