import pygame
pygame.init()

# Attributes
BG_COLOR = (0,0,0)
FONT_COLOR = (255,255,255)
TOPLEFT = (10,10)
FONT = None  # None for pygame default font
ANTIALIAS = True

# This method converts the input list to a string and displays it
# as a rect at position topleft = (x,y), default included
# Must input a list (single strings get chopped)

def debug(info_list, x = TOPLEFT[0], y = TOPLEFT[1]):
    f = pygame.font.Font(FONT,30)  
    display_surf = pygame.display.get_surface()
    line_height = pygame.font.Font.get_linesize(f)

    for index, line in enumerate(info_list):
        debug_surf = f.render(str(line), ANTIALIAS, FONT_COLOR)
        position = (20, TOPLEFT[1] + index * line_height)
        debug_rect = debug_surf.get_rect(topleft = position)
        pygame.draw.rect(display_surf, BG_COLOR, debug_rect)
        display_surf.blit(debug_surf, debug_rect)