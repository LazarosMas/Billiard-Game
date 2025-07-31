import pygame
from game_menu import Menu
from eightball import Eightball
from french import French    
from snooker import Snooker
from nineball import Nineball
from tutorial import Tutorial
from sys import exit

pygame.init()
pygame.mixer.init()

menu = True
game = False
screen_size = (1280, 720)

screen = pygame.display.set_mode(screen_size)
#Setting our game screen size to 1280x720 pixels 
frame_clock = pygame.time.Clock()
#Creating a clock object in order to keep track of time
pygame.display.set_caption("Billiard")
#Setting program's name as "Billiard"
freeplay = False
eightball = False
snooker = False
french = False
nineball = False
tutorial = False


while True:
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        while menu:
            open_menu = Menu(screen, frame_clock, menu, eightball, french, snooker, nineball, tutorial, freeplay)
            if open_menu.check_ev(screen, frame_clock) == False:
                pygame.mixer.music.stop()
                eightball = open_menu.eightball
                french = open_menu.french
                snooker = open_menu.snooker
                nineball = open_menu.nineball
                freeplay = open_menu.freeplay
                tutorial = open_menu.tutorial
                menu = False
                game = True
                break
        while game:
            if eightball:
                start_game = Eightball(screen, frame_clock, freeplay, game, menu)
            elif french:
                start_game = French(screen, frame_clock, freeplay, game, menu)  
            elif snooker:
                start_game = Snooker(screen, frame_clock, freeplay, game, menu)
            elif nineball:
                start_game = Nineball(screen, frame_clock, freeplay, game, menu)
            elif tutorial:
                start_game = Tutorial(screen, frame_clock, game, menu)
            eightball = False
            french = False
            snooker = False
            nineball = False
            game = False
            tutorial = False
            menu = True
    pygame.display.update()
    frame_clock.tick(60)