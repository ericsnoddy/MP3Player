WIDTH = 400
HEIGHT = 600
FPS = 60

# spacing
PAD = 32 # edge padding
BPAD = 8 # pad between buttons (row & col)
BSIZE = 42 # button size

# spacing setup
ROWPAD = (WIDTH - BSIZE*7 - BPAD*6) // 2
ROWSLOT = BSIZE + BPAD
ROW1_Y = HEIGHT - BPAD*3 - BSIZE*3  
ROW2_Y = HEIGHT - BPAD*2 - BSIZE*2
ROW3_Y = HEIGHT - BPAD - BSIZE

# UI - program is designed to fit 28 rows of 12px height text + 1px padding
UI_HEIGHT = 338
LIST_FONTSIZE = 10
LIST_ROW_HEIGHT = 12    # LIST_FONTSIZE + 2px

NP_FONTSIZE_TITLE = 20
NP_FONTSIZE_ARTIST = 16
NP_FONTSIZE_ALBUM = 13

# other aesthetics
FONT_COLOR = FONT_COLOR_TITLE = '#FFD700'
FONT_COLOR_ARTIST = '#DAB800'
FONT_COLOR_ALBUM = '#B89B00'
LIST_FONT_COLOR = "#C8C8C8"

BAR_COLOR = FONT_COLOR
BAR_BORDER_COLOR = '#A6A8AC'
LIST_BORDER_COLOR = INFO_BORDER_COLOR = BAR_BORDER_COLOR

MENU_W = 150
MENU_H = 100

# initial volume (out of 100) and seek increment in seconds
VOL_START = 75
SEEK_INCR = 10  # seconds

# True: 1st load is random, False: 1st load is index 0
OPEN_RANDOM_MODE = True