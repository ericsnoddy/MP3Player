# standard library
import sys

# third party
import pygame as pg
from pygame.locals import *

# local
from obj.settings import WIDTH, HEIGHT, FPS
from obj.console import Console

def main():

    # parse command-line arguments (for now only used to program play mode as 'rand' or 'loop')
    play_mode = parse_argv(sys.argv)

    # init
    win, clock = init_pygame()    

    # pass display and command line args
    console = Console(win, play_mode)

    # program loop
    running = True
    while running:

        console.run()

        # event loop
        for event in pg.event.get():
            if event.type == pg.QUIT or not console.running:
                running = False
            
            # handle input
            event_handler(console, event)
        
        # update the display
        pg.display.update()

        # tick the clock; used to cap FPS
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

            # btn.can_click is a cooldown timer that disallows click spamming (needed b/c click event is updated ~60x/sec)
            if btn.label == 'mode' and btn.can_click:
                console.toggle_mode(btn)

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

        # buttons 4 & 5 are mousewheel up and down, respectively
        if event.button == 4: console.scroll('up')
        if event.button == 5: console.scroll('down')

        # handle list and setup clicks
        if event.button == 1: console.handle_misc_clicks(event.pos)

    if event.type == MOUSEBUTTONUP:

        # Check if volup or down is active; deactivate if so
        vols = [btn for btn in console.buttons.sprites() if btn.label[0:3] == 'vol']

        for vol in vols:
            if vol.is_active:
                vol.activate(False)

    # keyboard shortcuts
    if event.type == KEYDOWN:
        if event.key == K_UP: console.scroll('up')
        elif event.key == K_PAGEUP: console.scroll('up', page=True)
        elif event.key == K_DOWN: console.scroll('down')
        elif event.key == K_PAGEDOWN: console.scroll('down', page=True)

    # catch custom flag
    if event.type == console.SONG_OVER:
        console.song_over()

def parse_argv(args):

    # command line args can be used to set the play mode
    # error 2 means user called -? for help; error 1 means syntax error (eg, both -L and -R called)
    error = False

    if len(args) == 2:            

        if '-r' in args or '-R' in args:
            return 'rand'

        elif '-l' in args or '-L' in args:
            return 'loop'

        elif '-?' in args:
            error = 2
            
        else:
            error = 1
    
    elif len(args) > 2 and '-?' not in args:
        error = 1
    elif '-?' in args: 
        error = 2

    if error == 1:
        print("Invalid command-line argument. '-?' for help.")
    elif error == 2:
        print("-R or -r for random mode XOR -L or -l for loop mode.")

    if error:
        pg.quit()
        sys.exit()
    else:
        return 'reg'

def init_pygame():
    
    # initialize all pg modules
    pg.init()

    # init display and caption
    win = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption('TinyAmp')

    # init clock module for capping the framerate
    clock = pg.time.Clock()

    return win, clock

if __name__ == '__main__':
    main()