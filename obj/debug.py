import pygame
pygame.init()

# Constants
BG_COLOR = 'black'
FONT_COLOR = 'white'
FONT_SIZE = 20
TOPLEFT = (10,30)
FONT = None  # None for pygame default font
ANTIALIAS = True

# This method converts list of strings to a multi-line overlay,
# with rect at position topleft = (x,y) = TOPLEFT
# Must input as a list of strings even if single line

def debug(multistring_list, x=TOPLEFT[0], y=TOPLEFT[1], font_size=FONT_SIZE):
    f = pygame.font.Font(FONT, font_size)  
    display_surf = pygame.display.get_surface()
    line_height = pygame.font.Font.get_linesize(f)

    for index, line in enumerate(multistring_list):
        debug_surf = f.render(str(line), ANTIALIAS, FONT_COLOR)
        position = (x, y + index*line_height)
        debug_rect = debug_surf.get_rect(topleft=position)
        pygame.draw.rect(display_surf, BG_COLOR, debug_rect)
        display_surf.blit(debug_surf, debug_rect)