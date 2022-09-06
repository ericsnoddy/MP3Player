import pygame as pg
import sys
from pygame.locals import *

from obj.settings import WIDTH, HEIGHT, FPS, CAPTION
from obj.console import Console

def init_pygame():
    
    # initialize all pg modules
    pg.init()

    WIN = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(CAPTION)
    clock = pg.time.Clock()

    return WIN, clock

def main():
    
    WIN, clock = init_pygame()
    console = Console(WIN)

    running = True
    # program loop
    while running:

        console.run()

        # event loop
        for event in pg.event.get():
            if event.type == pg.QUIT or not console.running:
                running = False
            
            event_handler(console, event)        
        
        pg.display.update()
        clock.tick(FPS)

    pg.quit()
    sys.exit()

def event_handler(console, event):

    if event.type == MOUSEBUTTONDOWN:

        clicked = [btn for btn in console.buttons.sprites() if btn.is_clicked(event.pos)]
        for btn in clicked:
            if btn.label == 'power':
                console.power_down()

            if btn.label == 'mute' and btn.can_click:
                btn.log_click()
                console.mute(btn)

            if btn.label == 'stop' and btn.can_click:
                btn.log_click()
                console.stop(btn)

            if btn.label == 'play' and btn.can_click:
                btn.log_click()
                console.play(btn)

            if btn.label == 'pause' and btn.can_click:
                btn.log_click()
                console.pause(btn)

            if btn.label == 'prev' or btn.label == 'next':
                if btn.can_click:
                    btn.log_click()
                    console.skip(btn)

            if btn.label[0:3] == 'vol':                
                console.volumize(btn)

            if btn.label == 'rew' or btn.label == 'ff':
                if btn.can_click:
                    btn.log_click()
                    console.seek(btn)

    if event.type == MOUSEBUTTONUP:

        vols = [btn for btn in console.buttons.sprites() if btn.label[0:3] == 'vol']        
        for vol in vols:
            if vol.is_active:
                vol.activate(False)

    if event.type == pg.event.Event(console.SONG_OVER):
        console.song_over()

if __name__ == '__main__':
    main()