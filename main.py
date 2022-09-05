import pygame as pg
import sys
from pygame.locals import *

from obj.settings import WIDTH, HEIGHT, FPS, CAPTION
from obj.console import Console

def main():
    
    WIN, clock = init_pygame()
    console = Console(WIN)

    # program loop
    while True:

        # event loop
        for event in pg.event.get():
            if event.type == pg.QUIT or not console.running:
                pg.mixer.quit()
                pg.quit()
                sys.exit()
            
            console.event_handler(event)
        console.run()
        pg.display.update()
        clock.tick(FPS)

def init_pygame():
    
    # initialize all pg modules
    pg.init()
    pg.mixer.init()

    WIN = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(CAPTION)
    clock = pg.time.Clock()

    return WIN, clock

if __name__ == '__main__':
    main()