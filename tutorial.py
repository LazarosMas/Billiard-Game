import pygame
import pymunk
import pymunk.pygame_util
import time
import sys
import json

pygame.init()

class Tutorial:
    def __init__(self, screen, frame_clock, game, menu):
        self.screen = screen
        self.frame_clock = frame_clock
        self.game = game
        self.menu = menu

        with open('saves/options_data.json', 'r') as file:
            self.options = json.load(file)

        if self.options[0] == 'enabled':
            self.sounds = True
            pygame.mixer.music.load('Sounds/Tutorial.mp3')
        else:
            self.sounds = False
        
        self.tutorial_font = pygame.font.Font('ghostclan.ttf', 25)
        self.cont = self.tutorial_font.render("Press SPACE to continue", True, (255, 255, 255))
        self.quit = self.tutorial_font.render("Press ESC to quit the tutorial", True, (255, 255, 255)) 

        self.tutorial_phase = 0
        self.tutorial_image = []

        self.loading_images()
        self.game_screen(self.frame_clock)
    

    def loading_images(self):
        for i in range(0, 47):
            j = pygame.image.load(f"Pictures/Tutorial_pics/{i}.png").convert_alpha()
            self.tutorial_image.append(j)
    

    def game_screen(self, frame_clock):
        if self.sounds:
            pygame.mixer.music.play()
        while self.game:
            if self.tutorial_phase > 46: 
                self.game = False
                break
            self.screen.blit(self.tutorial_image[self.tutorial_phase], (0,0))
            pygame.draw.rect(self.screen, (0, 153, 153), pygame.Rect(5, 690, 390, 23))
            pygame.draw.rect(self.screen, (0, 153, 153), pygame.Rect(785, 690, 488, 23))
            self.screen.blit(self.cont, (10, 690))
            self.screen.blit(self.quit, (790, 690))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game = False 
                    elif event.key == pygame.K_SPACE:
                        self.tutorial_phase += 1
            
            pygame.display.update()
            frame_clock.tick(60)
        pygame.mixer.music.stop()