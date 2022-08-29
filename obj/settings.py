from os.path import join

WIDTH = 400
HEIGHT = 600
PAD = 32
FPS = 60

BG_DEFAULT = join('assets', 'bg', 'space.png')
CAPTION = 'Music Player'
FONT_TYPE_REG = join('assets', 'fonts', 'Xolonium-Regular.otf')
FONT_TYPE_USER = None
FONT_COLOR = '#FFD700'

BUTTON_RADIUS = 21
BUTTONS = {
    'menu': join('assets', 'buttons', 'menu.png'),
    'stop': join('assets', 'buttons', 'stop.png'),
    'play': join('assets', 'buttons', 'play.png'),
    'pause': join('assets', 'buttons', 'pause.png'),
    'rew': join('assets', 'buttons', 'rew.png'),
    'ff': join('assets', 'buttons', 'ff.png'),
    'prev': join('assets', 'buttons', 'prev.png'),
    'next': join('assets', 'buttons', 'next.png'),
    'power': join('assets', 'buttons', 'power.png'),
    'mute': join('assets', 'buttons', 'mute.png'),
    'voldown': join('assets', 'buttons', 'voldown.png'),
    'volup': join('assets', 'buttons', 'volup.png')
}