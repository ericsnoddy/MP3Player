import pygame as pg

from obj.settings import FONT_COLOR, LIST_BORDER_COLOR, LIST_FONTSIZE_REG, LIST_FONTSIZE_BOLD 
from obj.data import FONT_TYPE_REG, FONT_TYPE_BOLD

class ListUI:
    def __init__(self, win, x, y, w, h, song_paths, now_playing_index):

        self.win = win
        self.rect = pg.Rect(x, y, w, h)
        self.border = self.rect.copy()

        self.song_paths = song_paths
        self.song_titles = self._get_titles_list(self.song_paths)
        self.now_playing_index = now_playing_index
        self.now_playing = self.song_titles[self.now_playing_index]

        # fonts
        self.font_list = pg.font.Font(FONT_TYPE_REG, LIST_FONTSIZE_REG )
        self.font_list_bold = pg.font.Font(FONT_TYPE_BOLD, LIST_FONTSIZE_BOLD)

    def _get_titles_list(self, song_paths):
        song_titles = []
        filenames = [song_path.rsplit('\\') for song_path in song_paths]
        for list in filenames:
            # of the split names we want the last indexed value; then split off the filetype and keep the 0 index value
            # Due to filtering in the setup process all files will have a proper extension
            song_titles.append(list[-1].rsplit('.')[0])
        return song_titles

    def _generate_titles(self):
        titles = [name for name in self.song_titles]
        for title in titles:
            yield title

    def update(self, new_index):
        self.now_playing = self.song_titles[new_index]

    def draw(self):
        # pg.draw.rect(self.win, 'black', self.rect)
        pg.draw.rect(self.win, LIST_BORDER_COLOR, self.rect, 1)

        song_playing_txt = self.font_list_bold.render(self.now_playing, True, FONT_COLOR)
        self.win.blit(song_playing_txt, (self.rect.x + 5, self.rect.y + 5))