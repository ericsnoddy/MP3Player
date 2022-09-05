import pygame

pygame.init()
song = R'C:\Users\Eric\Music\Clutch\1991 - Pitchfork\01 - Arcadia.mp3'
pygame.mixer.music.load('example.ogg')
pygame.mixer.music.play()
pygame.mixer.music.set_endevent(pygame.QUIT)

display = pygame.display.set_mode((300, 200))
display.fill('orange')
pygame.display.flip()

display_font = pygame.font.SysFont('Arial', 40)
start_pos = 0

def calc_position(start_pos, rewind=0, forward=0):
    position = pygame.mixer.music.get_pos() / 1000 + start_pos - rewind + forward
    return position if position >= 0 else 0

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            elif e.key == pygame.K_r:
                start_pos = 0
                pygame.mixer.music.play()
            elif e.key == pygame.K_LEFT:
                start_pos = calc_position(start_pos, rewind=10)
                pygame.mixer.music.play(0, start_pos)
            elif e.key == pygame.K_RIGHT:
                start_pos = calc_position(start_pos, forward=10)
                try:
                    pygame.mixer.music.play(0, start_pos)
                except:
                    running = False

    current_pos = round(calc_position(start_pos), 2)
    minutes = "{:0>2d}".format(int(current_pos // 60))
    seconds = "{:0>2d}".format(int(current_pos % 60))
    tenths = int(10 * (current_pos % 60 - int(current_pos % 60)))

    time_played_text = display_font.render(f'Pos: {minutes}:{seconds}.{tenths}', True, 'black')
    
    display.fill('orange')
    display.blit(time_played_text, (10, 10))
    
    pygame.display.flip()
