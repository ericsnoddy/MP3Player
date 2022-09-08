import pygame as pg

from obj.settings import FONT_COLOR, LIST_BORDER_COLOR, LIST_FONTSIZE_REG, LIST_FONTSIZE_BOLD 
from obj.data import FONT_TYPE_REG, FONT_TYPE_BOLD

class ListUI:
    def __init__(self, win, x, y, w, h, song_paths, now_playing_index):

        self.win = win
        self.rect = pg.Rect(x, y, w, h)
        self.border = self.rect.copy()

        self.song_paths = song_paths
        self.song_names = self._generate_titles(song_paths)
        print(self.song_names)
        self.now_playing_index = now_playing_index
        self.now_playing = self._splice_title(song_paths[now_playing_index])

        # fonts
        self.font_list = pg.font.Font(FONT_TYPE_REG, LIST_FONTSIZE_REG )
        self.font_list_bold = pg.font.Font(FONT_TYPE_BOLD, LIST_FONTSIZE_BOLD)

    def _generate_titles(self, song_paths):
        song_names = []
        filenames = [song_path.rsplit('\\') for song_path in song_paths]
        for list in filenames:
            # of the split names we want the last indexed value; then split off the filetype and keep the 0 index value
            song_names.append(list[-1].rsplit('.')[0])
        return song_names

    def _splice_title(self, song_path):
        # ex path = 'C:/Users/Eric/Music\Alanis Morissette\Jagged Little Pill [25th Anniversary Deluxe Edition]\01 - All I Really Want.mp3'
        song = song_path.rsplit('\\')        
        return song[-1].rsplit('.')[0]

    def generate_list(self):
        pass

    def update(self, new_index):
        self.now_playing = self._splice_title(self.song_paths[new_index])

    def draw(self):
        # pg.draw.rect(self.win, 'black', self.rect)
        pg.draw.rect(self.win, LIST_BORDER_COLOR, self.rect, 1)

        song_playing_txt = self.font_list_bold.render(self.now_playing, True, FONT_COLOR)
        self.win.blit(song_playing_txt, (self.rect.x + 5, self.rect.y + 5))