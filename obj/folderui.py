from socket import SO_LINGER
import pygame
import re

from obj.settings import HEIGHT, WIDTH, BSIZE, PAD

class FolderUI:
    def __init__(self, *song_data):

        self.win = pygame.display.get_surface()
        self.artist = None
        self.album = None
        self.song = None
        
        if len(song_data) == 1:
            self.song = song_data[0]
        elif len(song_data) == 2:
            self.album = song_data[0]
            self.song = song_data[1]
        else:
            self.artist = song_data[0]
            self.album = song_data[1]
            self.song = song_data[2]

    def get_duration(self, duration):
        tot_secs = (duration / 1000 )
        hours = int((tot_secs / 3600) % 24)
        mins = int((tot_secs / 60) % 60)
        secs = int(tot_secs % 60)

        return '{}:{:02.0f}:{:02.0f}'.format(hours, mins, secs)
    
    def display(self, duration):
        self.win.blit(duration, ((WIDTH - PAD*2 - duration.get_width()) // 2 + PAD, PAD))







    


    