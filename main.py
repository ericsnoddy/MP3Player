import pygame as pg
import sys
from pygame.locals import *

from obj.settings import WIDTH, HEIGHT, FPS
from obj.console import Console

def main():
    
    # gather and parse command-line arguments
    # args = parse_args(sys.argv)

    # init
    win, clock = init_pygame()
    console = Console(win)  # will pass argv 

    # program loop
    running = True
    while running:

        console.run()

        # event loop
        for event in pg.event.get():
            if event.type == pg.QUIT or not console.running:
                running = False
            
            event_handler(console, event)        
        
        # update the display
        pg.display.update()

        # tick the clock to maintain FPS
        clock.tick(FPS)

    pg.quit()
    sys.exit()

def event_handler(console, event):

    if event.type == MOUSEBUTTONDOWN:

        # get clicked sprite (by filtering all sprites for click event - will return only single sprite)
        clicked = [btn for btn in console.buttons.sprites() if btn.is_clicked(event.pos)]

        for btn in clicked:
            if btn.label == 'power':
                console.power_down()

            if btn.label == 'mute' and btn.can_click:
                console.mute(btn)

            if btn.label == 'stop' and btn.can_click:
                console.stop(btn)

            if btn.label == 'play' and btn.can_click:
                console.play(btn)

            if btn.label == 'pause' and btn.can_click:
                console.pause(btn)

            if btn.label == 'prev' or btn.label == 'next':
                if btn.can_click:
                    console.skip(btn)

            if btn.label[0:3] == 'vol':                
                console.volumize(btn)

            if btn.label == 'rew' or btn.label == 'ff':
                if btn.can_click:
                    console.seek(btn)
        
        if console.volbar.is_clicked(event.pos):
            console.adjust_volbar(event.pos[0])
            
        elif console.progbar.is_clicked(event.pos):
            console.adjust_progbar(event.pos[0])

    if event.type == MOUSEBUTTONUP:

        # Check if volup or down is active; deactivate if so
        vols = [btn for btn in console.buttons.sprites() if btn.label[0:3] == 'vol']

        for vol in vols:
            if vol.is_active:
                vol.activate(False)

    # catch custom flag
    if event.type == console.SONG_OVER:
        console.song_over()

# def parse_args(argsv):
#     return [sys.argv[i] for i in range (1, len(sys.argv))]

def init_pygame():
    
    # initialize all pg modules
    pg.init()

    # init display module and caption
    win = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption('Thinamp')

    # init clock module for capping the framerate
    clock = pg.time.Clock()

    return win, clock

if __name__ == '__main__':
    main()