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

# mp3player/project.py

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

At the end of every program loop, the screen is updated and the clock is ticked at a rate which forces the program to
closely approximate the FPS in settings.py (default is 60 FPS). This is to ensure consistent framerate across devices.

###

# obj/console.py

The meat of the program, this handles the vast majority of media functions, in addition to init of sprites, images, 
sliders, fonts, everything asset related. It handles many internal functions for importing files, graphics, and other 
data and settings. It handles the init setup for getting the music folder and init the now_playing display and the 
list UI. Console also handles the main update and draw methods for all the sprites/sprite groups, for all the sliders 
and objects, etc. console.run() method is run every program loop (see main.py). Example methods include all the media 
functions: mute(), play(), skip() etc. All these button-click functions take a button sprite object as an input; these 
button sprites are specialized classes, some inherited from others, all inheriting from pygame.Sprite. (see button.py)
The buttons do not handle the media functions themselves, except in rare circumstances as convenience dictated.

console.py handles song-over events, exiting, metadata extraction (using display.py method), displaying the song 
duration and length, and heeding a signal to change to song based on list UI clicks. All of the media buttons should 
behave exactly as traditional for mp3 player programs. Some of the console's public methods are just pass-through
functions acting as a communication mediary between main.py input handling and obj classes such as slider.py. 

console.py/__init__() sets up many variables and objs from flags to pre-rendered text to sprite groups. It must be
passed the display window and the play mode from init in main.py. When self.setup_mode is True (program first run),
the song list is enumerated with file paths from selected root folder, and the list UI and NowPlaying objs are
initiated with the song file paths. At the end of setup, a song is loaded, highlighted in the list, and ready for play.

Many of the media functions in console.py must interact with each other. For example, when the play button is activated,
the stop button must deactivate. Since media function methods input only the button intended for the primary function--
eg, the stop_btn obj when stop button is activated--I wrote a private method self._get_button(btn) that retrieves the
relevent buttons for interacting from within other subclasses. In the method console.stop(stop_btn), eg, we need to 
deactivate play and pause if those buttons are active when stop button is clicked:

    play_btn = self._get_button('play')
    play_btn.activate(False)

    pause_btn = self._get_button('pause')
    pause_btn.activate(False)

console.run() contains all of the update and draw functions which loop every frame.

###

# obj/button.py

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

pygame sprites are objects that have an "image" and a "rectangle" atrribute. a rectangle in pygame is a specific region
of the screen given by coordinates which can then be "blitted" or drawn onto a "surface".

##

# obj/slider.py

Contains 2 classes:

Slider - an interactive bar showing ratio of current level to max level, tracks mouse clicks to update value
----Scroller(Slider) - unused, bare subclass at this time; may become a scroll-bar for the list in the future.

##

# obj/settings.py
# obj/data.py

Program constants (eg display WIDTH; FONTSIZE) and file path information convenient to have in one place to share among 
modules. Manipulating variables such as space padding in one place made visual design easier. Existence of settings.py
constants does not necessarily mean the program is scalable by altering these constants; such manipulation would be
very experimental.

##

# obj/display.py

Two important classes:

NowPlaying - This class displays song information for the currently selected song; title, artist, album. If the text
is too long for the window it scales the text to fit. NowPlaying information is extracted from metadata, else displays
Unknown. metadata extraction is also a helper fucntion for console to get song length

----ListUI(NowPlaying) - This class inherits from NowPlaying but is substantially different. inits a clickable and 
scrollable UI list upon which is rendered the titles of all the songs in the music root folder and its subdirectories, 
and highlights the currently plaing song. The list auto-scrolls when a new track starts that is not currently visible. 
Clicking a row will load and play the song. The biggest drawback of TinyAmp's structure is that the list must be re-
rendered every time a song changes. This causes unacceptable lag with especially large libraries and I was never able
to code a good workaround for this while maintaining visually highlighting the current playing song as well as updating
the highlighting when a new song plays. Perhaps I'll figure it out in future versions.

## 

# obj/__init__.py

From python documentation: "The __init__.py files are required to make Python treat directories containing the file as 
packages. This prevents directories with a common name, such as string, unintentionally hiding valid modules that occur 
later on the module search path. In the simplest case, __init__.py can just be an empty file....

"Users of the package can import individual modules from the package, for example."

##

# assets/bg
# assets/fonts
# assets/buttons

Contains the .png image files and .otf fonts used in the program. Licensing for all assets is contained in the root 
folder file called 'Licensing.txt'. I had to do some photshopping to get buttons into their final form, cut out from
a "sheet" and placed onto transparent backgrounds.

## 

# public_domain_mp3s/*.mp3

This is not a necessary folder and contains only sample public domain music for demo purposes. This folder is the
program default folder suggestion in this cs50 version of the program but any folder containing mp3s or subfolders
of mp3s can be opted.

##

# imported modules:

# import pygame as pg
# tk (tkinter)
# mutagen

pygame is described above. tkinter, a popular user dialog module, is used only to retrieve music folder from the user.
mutagen is a third party module for manipulating song files; needed to extract metadata including song length, as
pygame music has limited functionality in this area. (Calculating song's time position is a real pain that 
involves tracking how long current sound has been playing with offsets such as rewinding and pausing.)



