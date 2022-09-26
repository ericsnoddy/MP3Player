# TinyAmp, a lightweight mp3 player
    #### Video Demo:  <URL HERE>
    #### Description:
        # Opens a music folder preferably no more than a few hundred titles
        # Default opens to random title (see settings.py for OPEN_RANDOM_MODE)
        # buttons, sliders, and scrollable list fully interactive to play mp3s
        # metadata is scraped and displayed if available
        # Up/Down arrows and up/down mousewheel scrolls list
        # page up/ page down scrolls list        
        # toggle play mode between regular, random, loop w bottom left button
        # command line args open mp3 player in set play mode:
        ### -R or -r opens in random mode
        ### -L or -l opens in loop mode
        ### -? helps user with commands

        # sample public domain mp3s are included as the default folder
        # all licensing info in assets/Licensing.txt and assets/Xolonium License.txt

Let's explore the program.

###

mp3player/project.py

project.py contains the main method. The main class handles intitialization of the pygame module, which is a third 
party game-oriented module for manipulating sprites, handling mouse/keyboard inputs, and managing the FPS rate of 
animation. The main class contains the fundmental structure of the program: it inits the display window, console.py
Console class, and helper modules; parses command line arguments; and handles input events. The main structure is a 
program loop that loops console.run() until a quit event is detected. Inside the main program loop is the event loop 
which handles queued events such as keyboard and mouse button presses.

def init_pygame() inits the display window size and caption, inits the framerate clock, and returns these objs to main.

def parse_argv() detects the play mode from optional command line arguments and passes to the Console.

def event_handler() handles inputs. The majority of inputs are mouse click collisions with drawn sprites. Sprites are 
filtered by label and tested for click collision, and if 'legal' collisions are detected, main() redirects the command 
to Console. None of the media functions take place in the event_handler() itself. Note most buttons clicks come with a 
cooldown period; since the program loops ~60 FPS we do not want to allow spamming of mouseclicks, so we must limit 
their input by timing them.

###

obj/console.py

The meat of the program, this handles the vast majority of media functions, in addition to init of sprites, images, 
sliders, fonts, everything asset related. It handles many internal functions for importing files, graphics, and other 
data and settings. It handles the init setup for getting the music folder and init the now_playing display and the 
list UI. Console also handles the main update and draw methods for all the sprites/sprite groups, for all the sliders 
and objects, etc. console.run() method is run every program loop (see main.py). Example methods include all the media 
functions: mute(), play(), skip() etc. All these button-click functions take a button sprite object as an input; these 
button sprites are specialized classes, some inherited from others, all inheriting from pygame.Sprite. (see button.py)

console.py handles song over events, quitting, metadata extraction (using display.py method), displaying the song 
duration and length, and heeding a signal to change to song based on list UI clicks. All of the media buttons should 
behave exactly as traditional for mp3 player programs. There are no keyboard shortcuts other than for scrolling the 
list available at this time.

###

obj/button.py

This file contains all the Button sprite classes. Buttons generally handle just a few operations: tracking a cooldown 
timer, calculating whether a mouseclick collides within the radius of button to activate it, saves the activation 
status of the button--an active button is a negative image of the inactive button. Here are the buttons and their 
inheritance:

ToggleButton(pygame.sprite.Sprite) - A button that activates on click, deactivates on second click
----HoldButton(ToggleButton) - A button that is active when held and inactive when not held
----MuteButton(ToggleButton) - Customized to return a volume - tracks a saved volume variable
----StopButton(ToggleButton) - Customized to begin in the activated state
----QuickButton(ToggleButton) - customized to be active only during cooldown period
--------SeekButton(QuickButton) - customized QuickButton to have very short cooldown
ModeButton(pygame.sprite.Sprite) - toggles between 3 states instead of 2 states. Relays toggle state to Console.

##

obj/slider.py





