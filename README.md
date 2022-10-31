##### TinyAmp, a lightweight mp3 player
    #### Video Demo:  https://youtu.be/_zttJiD64MY
    #### Author: Eric A. Snoddy
    #### Description:
        # Opens a music folder preferably no more than a few hundred titles
        # Default opens to random title (see settings.py for OPEN_RANDOM_MODE)
        # buttons, sliders, and scrollable list fully interactive to play mp3s
        # metadata is scraped and displayed if available
        # Up/Down arrows and up/down mousewheel scrolls list
        # page up/ page down scrolls list        
        # toggle play mode between regular, random, loop w bottom left button
        # command line args open mp3 player in set play mode:
        # -R or -r opens in random mode
        # -L or -l opens in loop mode
        # -? helps user with commands

        # ** sample public domain mp3s are included as the default folder
        # ** all licensing info in assets/Licensing.txt

##### LIBRARY DEPENDENCIES - pip install

pygame

tk

mutagen

###### SKILLS NECESSARY TO COMPLETE THIS PROJECT

# CS50 LESSONS:

functions, variables, loops, exceptions, libraries, unit tests, OOP

constants and importing from local files

classes and inheritance; class instantiation and attributes

super().__init__()

file structure; dotted file structure

importing images from folder

parsing command line arguments

public vs private methods

keeping classes as independent as possible; a clear purpose for every file

performance considerations

# PYGAME:

sprites and sprite groups, images, 'surfaces' and 'rectangles', drawing and updating

click detection/collisions

game and event loop; capping the framerate

user the pygame.mixer.music module

gathering input from the user: keyboard/mouse

clickable/scrollable GUI

rendering fonts/text

passing functions as well as variables

preventing input spam (eg, one click counting as a dozen due to program loop rate)

setting custom event flags

# GENERAL:

image editing

GUI design elemnts

###### LET'S EXPLORE THE PROGRAM

# imported modules:

# import pygame as pg
# tk (tkinter)
# mutagen

pygame is a richly featured third party game-oriented module for manipulating sprites, handling mouse/keyboard 
inputs, and managing the FPS rate of animation. It uses "surface" and "rectangle" objects to display images and fonts
at set coordinates, among other tools. tkinter, a popular user dialog module, is used here to retrieve music folder 
from the user. mutagen is a third party module for manipulating song files; it's needed to extract metadata including 
song length, as pygame music has limited functionality in this area. (Calculating a song's time position is a real pain 
that involves tracking how long current sound has been playing and offsets such as rewind and pause length.)

# mp3player/project.py

project.py contains the main method. main() handles init of the pygame module, parsing command line args, init and 
running of the Console class obj which contains the bulk of the program, helper modules, and handling all inputs from 
the keyboard and mouse. The main structure is a program loop that loops console.run() until a quit event is detected. 
Inside the main program loop is the event loop which handles queued events such as keyboard and mouse button presses.

def init_pygame() inits the display window size and caption, inits the framerate clock, and returns these objs to main.

def parse_argv() detects the play mode from optional command line arguments and passes the result to Console.

def event_handler() handles inputs. The majority of inputs are mouse click collisions with drawn sprites. Sprites are 
filtered by label and tested for click collision, and if 'legal' collisions are detected, main() redirects the command 
to Console. None of the media functions take place in the event_handler() itself. 

Most buttons come with a cooldown period; since the program loops ~60 FPS we do not want to allow spamming of mouse
clicks, so input is time-limited and checked via an "is_clicked" method and "can_click" attribute. The code for 
checking sprite collisions is a one-line filter run only if a MOUSEBUTTONDOWN event is detected, shown here with 
example:



if event.type == MOUSEBUTTONDOWN:

    clicked = [btn for btn in console.buttons.sprites() if btn.is_clicked(event.pos)]
    
    for btn in clicked:
    
        ...
        
        if btn.label == 'mode' and btn.can_click:
        
            console.toggle_mode(btn))
            
        ...



The relevant button is returned when the mouse click position is checked against each button's is_clicked method. Then
the filtered button obj is sent to the corresponding method in console.py to perform the intended media function. 
Default cooldown period derived from the base ToggleButton class is 250ms but some buttons have altered cooldown 
periods.

At the end of every program loop, the screen is updated and the clock is ticked at a rate which forces the program to
closely approximate the FPS in settings.py (program default is 60 FPS). This is to ensure consistent framerate across 
devices.

# obj/console.py

The meat of the program, this handles the vast majority of media functions, in addition to init of sprites, images, 
sliders, fonts, everything asset related. It handles many internal functions for importing files, graphics, and other 
data and settings. It handles the init setup for getting the music folder and init the now_playing display and the 
list UI. Console also handles the main update and draw methods for all the sprites/sprite groups, for all the sliders 
and objects, etc. console.run() method is run every program loop (see main.py). Example methods include all the media 
functions: mute(), play(), skip() etc. All these button-click functions take a button sprite object as an input; these 
button sprites are specialized classes, some inherited from others, all inheriting from pygame.Sprite. (see button.py)
The buttons do not handle the media functions themselves, except in rare circumstances as convenience dictated. 

Many of the media functions in console.py must interact with each other. Since media function methods input only the 
button intended for the primary function--eg, the stop_btn obj when stop button is activated--I wrote a private method 
self.\_get_button(btn) that retrieves the relevent buttons for interacting from within other subclasses. In the method 
console.stop(stop_btn), eg, we need to deactivate play and pause if those buttons are active at the time the stop 
button is clicked:


def \_get_button(self, label):

    btns = []
    
    for btn in self.buttons.sprites():
    
        if btn.label == label:
        
            btns.append(btn)
            
    return btns[0]



Here is an example media function:



def pause(self, pause_btn):

    \# log the click time to begin cooldown period
    
    pause_btn.log_click()

    \# get the play button obj
    
    play_btn = self._get_button('play')

    \# global flag for song has been started is True and pygame check for song is playing (not paused) is True
    
    if self.song_in_progress and pg.mixer.music.get_busy():

        \# if both True, activate the pause button; deactivate the play button; pause the mixer 
        
        pause_btn.activate()            
        
        play_btn.activate(False)
        
        pg.mixer.music.pause()

    \# if the song has been started but it's not currently playing it must be paused; unpause the mixer
    
    elif self.song_in_progress:
    
        pause_btn.activate(False)
        
        play_btn.activate()
        
        pg.mixer.music.unpause()

    \# if a song has not been started do nothing


console.py handles song-over events, exiting, metadata extraction (using display.py method), displaying the song 
duration and length, and heeding a signal to change to song based on list UI clicks. All of the media buttons should 
behave exactly as traditional for mp3 player programs. Some of the console's public methods are just pass-through
functions acting as a communication mediary between main.py input handling and obj classes such as slider.py, in 
order to keep the code clean and readable:



def scroll(self, direction, page=False):

    self.list_ui.scroll(direction, page)



console.py/__init__() sets up many variables and objs from flags to pre-rendered text to sprite groups. It must be
passed the display window and the play mode from init in main.py. When self.setup_mode is True (program first run),
the song list is enumerated with file paths from selected root folder, and the list UI and NowPlaying objs are
initiated with the song file paths. At the end of setup, a song is loaded, highlighted in the list, and ready for play.


console.run() contains all of the update and draw functions which loop every frame.

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

An example class function, is_clicked(mouse_pos) looks like this, a Pythagorean distance formula using the button 
radius:

def is_clicked(self, mouse_pos):

    dx = self.rect.centerx - mouse_pos[0]
    
    dy = self.rect.centery - mouse_pos[1]
    
    sq = dx**2 + dy**2
    
    return True if sq < self.radius**2 else False

# obj/slider.py

Contains 2 classes:

Slider - an interactive bar showing ratio of current level to max level, tracks mouse clicks to update value
----Scroller(Slider) - unused, bare subclass at this time; may become a scroll-bar for the list in the future.

The slider can take a mouse click's x position and turn it into a new value (for adjusting the volume, say), or
it can in reverse take a value and adjust the slider's x position fill (for restoring the volume from mute, say).
Another use is the progress bar; a mouse click can change the time position of the currently playing song.

# obj/settings.py
# obj/data.py

Program constants (eg display WIDTH; FONTSIZE) and file path information convenient to have in one place to share among 
modules. Manipulating variables such as space padding in one place made visual design easier. Existence of settings.py
constants does not necessarily mean the program is scalable by altering these constants; such manipulation would be
very experimental.

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

The list is rendered row by row as follows:


def \_enumerate_list(self):

    ...

    y = 1   # 1 px padding
    
    for index, _ in enumerate(self.titles):
    
        artist = self.get_meta('artist', index)
        
        song = self.get_meta('title', index)

        row = f'{artist} - {song}'

        if self.now_playing_index != index:

            \# if the song changes, re-render which song is displayed with highlight text
            
            \# blit is the method for drawing image rectangles onto surfaces
            
            self.list_surf.blit(f.render(row, True, LIST_FONT_COLOR), (0, y))
        else: 
            self.list_surf.blit(f_.render(row, True, FONT_COLOR), (0, y))
        y += LIST_ROW_HEIGHT 


Another function calculates the index based on mouseclick collisions with the list surface for changing the song via 
the clickable/scrollable list:


 def change_index_click_detection(self, mouse_pos):

    \# pygame function to detect rect collisions
    
    if self.rect.collidepoint(mouse_pos) and self.can_click:
    
        self._log_click()
        
        mouse_y = mouse_pos[1]

        \# Derive the index of the song by tracking the y position and its offset and dividing by the row height
        
        row_index = (mouse_y - (self.rect.top + 1) - self.scroll_y) // LIST_ROW_HEIGHT


# obj/__init__.py

From python documentation: "The __init__.py files are required to make Python treat directories containing the file as 
packages. This prevents directories with a common name, such as string, unintentionally hiding valid modules that occur 
later on the module search path. In the simplest case, __init__.py can just be an empty file....

"Users of the package can import individual modules from the package, for example."

# assets/bg
# assets/fonts
# assets/buttons

Contains the .png image files and .otf fonts used in the program. Licensing for all assets is contained in the root 
folder file called 'Licensing.txt'. I had to do some photshopping to get buttons into their final form, cut out from
a "sheet" and placed onto transparent backgrounds.

# public_domain_mp3s/*.mp3

This is not a necessary folder and contains only sample public domain music for demo purposes. This folder is the
program default folder suggestion in this cs50 version of the program but any folder containing mp3s or subfolders
of mp3s can be opted.

2022 Eric A. Snoddy
