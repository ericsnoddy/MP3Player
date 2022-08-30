from os.path import join

WIDTH = 400
HEIGHT = 600
PAD = 32
BPAD = 8 # pad between buttons (row & col)
BSIZE = 42 # button size
FPS = 60

BG_DEFAULT = join('assets', 'bg', 'space.png')
CAPTION = 'Music Player'
FONT_TYPE_REG = join('assets', 'fonts', 'Xolonium-Regular.otf')
FONT_TYPE_BOLD = join('assets', 'fonts', 'Xolonium-Bold.otf')
FONT_COLOR = '#FFD700'

# VOL_START should be a multiple of VOL_INCR
VOL_START = 0.7
VOL_INCR = 0.01

BUTTONS = {
    # buttons
    'stop': join('assets', 'buttons', 'stop.png'),
    'prev': join('assets', 'buttons', 'prev.png'),
    'next': join('assets', 'buttons', 'next.png'),
    'power': join('assets', 'buttons', 'power.png'),

    # 'active' (invertible) buttons
    'menu': join('assets', 'buttons', 'menu.png'),
    'menu_': join('assets', 'buttons', 'menued.png'),
    'mute': join('assets', 'buttons', 'mute.png'),
    'mute_': join('assets', 'buttons', 'muted.png'),
    'pause': join('assets', 'buttons', 'pause.png'),
    'pause_': join('assets', 'buttons', 'paused.png'),
    'play': join('assets', 'buttons', 'play.png'),
    'play_': join('assets', 'buttons', 'playing.png'),
    'rew': join('assets', 'buttons', 'rew.png'),
    'rew_': join('assets', 'buttons', 'rewing.png'),
    'ff': join('assets', 'buttons', 'ff.png'),
    'ff_': join('assets', 'buttons', 'ffing.png'),
    'voldown': join('assets', 'buttons', 'voldown.png'),
    'voldown_': join('assets', 'buttons', 'voldowning.png'),
    'volup': join('assets', 'buttons', 'volup.png'),    
    'volup_': join('assets', 'buttons', 'voluping.png')
}