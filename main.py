import pygame, sys
from pygame.locals import *

from obj.settings import WIDTH, HEIGHT, FPS, CAPTION
from obj.console import Console

def main():
    
    WIN, clock = init_pygame()
    console = Console(WIN)

    # program loop
    while True:

        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT or not console.running:
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            
            console.event_handler(event)

        console.run()

        pygame.display.update()
        clock.tick(FPS)

def init_pygame():
    
    # initialize all pygame modules
    pygame.init()

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()

    return WIN, clock

if __name__ == '__main__':
    main()