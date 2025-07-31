import pygame
import json
pygame.init()
#Importing and initializing pygame
white = (255, 255, 255)
color = white


class Buttons:
    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720))
        self.buttons_font = pygame.font.Font('ghostclan.ttf', 40)

    def create_button(self, font, text, pos, colr, screen, n):
        message = font.render(text, True, colr)
        if n ==1:
            message_rect = message.get_rect(center = pos)
        else: message_rect = message.get_rect(midleft = pos)
        screen.blit(message, message_rect)
        return message_rect

    def menu_draw(self, screen):        
        start_button_rec = self.create_button(self.buttons_font, "START", (400, 600), color, self.screen, 1)
        options_button_rec = self.create_button(self.buttons_font, "OPTIONS", (640, 612), color, self.screen, 1)
        exit_button_rec = self.create_button(self.buttons_font, "EXIT", (880, 600), color, self.screen, 1)
        tutorial_button_rec = self.create_button(self.buttons_font, "TUTORIAL", (160, 550), color, self.screen, 1)
        highscore_button_rec = self.create_button(self.buttons_font, "HIGH SCORES", (1120, 550), color, self.screen, 1)
        return(start_button_rec, options_button_rec, exit_button_rec, tutorial_button_rec, highscore_button_rec)
  #Drawing main_menu buttons  
    def exit_menu(self, screen):
        yes_button_rec = self.create_button(self.buttons_font, "YES", (520, 500), color, self.screen, 1)
        no_button_rec = self.create_button(self.buttons_font, "NO", (760, 500), color, self.screen, 1)
        return(yes_button_rec, no_button_rec)
    #Drawing exit and start game buttons
    def options_menu(self, screen, sound, table_color, name1, name2):
        if table_color == 'green':
            t_color = (0, 255, 0)
        elif table_color == 'red':
            t_color = (255, 0, 0)
        else:
            t_color = (0, 0, 255)
        sound_button_rec = self.create_button(self.buttons_font, "SOUND:", (50, 350), color, self.screen, 2)
        return_but_rec = self.create_button(self.buttons_font, "RETURN", (1050, 670), color, self.screen, 2)
        table_button_rec = self.create_button(self.buttons_font, "COLOR:", (50, 400), color, self.screen, 2)
        colors_rec = self.create_button(self.buttons_font, table_color, (200, 400), t_color, self.screen, 2)
        name_button_rec = self.create_button(self.buttons_font, "NAME 1:", (50, 500), color, self.screen, 2)
        name1_button_rec = self.create_button(self.buttons_font, "NAME 2:", (50, 550), color, self.screen, 2)
        player1_rec = self.create_button(self.buttons_font, name1, (220, 500), color, self.screen, 2)
        player2_rec = self.create_button(self.buttons_font, name2, (220, 550), color, self.screen, 2)
        if sound == 'enabled':
            s = self.create_button(self.buttons_font, "ENABLED", (200, 350), color, self.screen, 2)
        else: s = self.create_button(self.buttons_font, "DISABLED", (200, 350), color, self.screen, 2)
        return(sound_button_rec, table_button_rec, return_but_rec, name_button_rec, name1_button_rec)
    #Drawing options buttons  
    def start_menu(self, screen):
        eight_ball_button_rec = self.create_button(self.buttons_font, "8-BALL", (70, 280), color, self.screen, 2)
        nine_ball_button_rec = self.create_button(self.buttons_font, "9-BALL", (70, 380), color, self.screen, 2)
        french_button_rec = self.create_button(self.buttons_font, "FRENCH", (70, 480), color, self.screen, 2)
        snooker_button_rec = self.create_button(self.buttons_font, "SNOOKER", (70, 580), color, self.screen, 2)
        back_button_rec = self.create_button(self.buttons_font, "BACK", (1100, 670), color, self.screen, 2)
        return(eight_ball_button_rec, nine_ball_button_rec, french_button_rec, snooker_button_rec, back_button_rec)

    def game_mode(self, screen):
        pvp_button_rec = self.create_button(self.buttons_font, "PvP", (470, 430), color, self.screen, 2)
        freeplay_button_rec = self.create_button(self.buttons_font, "Freeplay", (730, 430), color, self.screen, 2)
        back_button_rec = self.create_button(self.buttons_font, "BACK", (1125, 675), color, self.screen, 2)
        return(pvp_button_rec, freeplay_button_rec, back_button_rec)

    def eightball_high(self, screen):
        back_button_rec = self.create_button(self.buttons_font, "BACK", (1125, 675), color, self.screen, 2)
        return(back_button_rec)
    

    def check(self, mouse_pos, rec):
        if mouse_pos[0] in range(rec.left, rec.right) and mouse_pos[1] in range(rec.top, rec.bottom):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False
    #A function checking if our mouse position collides with our buttons rectangles position
    


buttons_main = Buttons()

class Menu():
    def __init__(self, screen, frame_clock, menu, eightball, french, snooker, nineball, tutorial, freeplay):
        self.menu = menu
        self.main_menu = True  
        self.start_menu = False
        self.game_mode_menu = False
        self.options_menu = False       
        self.exit_menu = False
        self.highscore_menu = False
        self.eightball_highscore_menu = False
        self.eightball = eightball
        self.nineball_highscore_menu = False
        self.french = french
        self.french_highscore_menu = False
        self.snooker_highscore_menu = False
        self.snooker = snooker
        self.nineball = nineball
        self.tutorial = tutorial
        self.freeplay = freeplay
        
        #Setting our boolean menu variables in order to check which of our menus must be viewed
        self.screen_size = (1280, 720)
        self.billiard_font = pygame.font.Font('ghostclan.ttf', 100)
        self.message_font = pygame.font.Font('ghostclan.ttf', 20)
        self.sec_menu_font = pygame.font.Font('ghostclan.ttf', 50)
        #Setting text fonds
        self.menu_surface = pygame.image.load("Pictures/Menu.png").convert_alpha()
        self.menu_surface = pygame.transform.scale(self.menu_surface, self.screen_size)
        self.other_menus_surface = pygame.image.load("Pictures/Menu_b.png").convert_alpha()
        self.other_menus_surface = pygame.transform.scale(self.other_menus_surface, self.screen_size)
        #Importing our menu background images
        self.message = self.message_font.render("A GAME MADE BY LAZAROS MASLOUNKAS", True, white)
        self.text_surface = self.billiard_font.render('Billiard Game', True, white)
        self.text_rect = self.text_surface.get_rect(center=(1280/2, 100))
        self.start_surface = self.sec_menu_font.render('Choose the game type:', True, white)
        self.start_rect = self.start_surface.get_rect(center= (1280/2, 150))
        self.game_mode_surface = self.sec_menu_font.render("Select Game Mode:", True, white)
        self.game_mode_rect = self.game_mode_surface.get_rect(center=(1280/2, 150))
        self.options_surface = self.billiard_font.render('OPTIONS', True, white)
        self.options_rect = self.options_surface.get_rect(center = (1280/2, 100))
        self.exit_surface = self.sec_menu_font.render('Do you wish to exit?', True, white)
        self.exit_rect = self.exit_surface.get_rect(center=(1280/2, 300))
        self.highscore_surface = self.billiard_font.render('Highscore', True, white)
        self.highscore_rect = self.highscore_surface.get_rect(center=(1280/2, 150))
        self.eightscore_surface = self.billiard_font.render('8-ball highscores', True, white)
        self.eightscore_rect = self.eightscore_surface.get_rect(center=(1280/2, 150))
        self.ninescore_surface = self.billiard_font.render('9-ball highscores', True, white)
        self.ninescore_rect = self.ninescore_surface.get_rect(center=(1280/2, 150))
        self.frenchscore_surface = self.billiard_font.render('french highscores', True, white)
        self.frenchscore_rect = self.frenchscore_surface.get_rect(center=(1280/2, 150))
        self.snookerscore_surface = self.billiard_font.render('snooker highscores', True, white)
        self.snookerscore_rect = self.snookerscore_surface.get_rect(center=(1280/2, 150))
        self.enter = self.message_font.render("Type your name and press ENTER!", True, white)
        self.date = self.message_font.render('DATE', True, (255, 128, 128))
        self.winner = self.message_font.render('Winner', True, (255, 128, 128))
        self.looser = self.message_font.render('Looser', True, (255, 128, 128))
        self.balls = self.message_font.render('Potted Balls', True, (255, 128, 128))
        self.turns = self.message_font.render('TURNS', True, (255, 128, 128))
        self.fouls = self.message_font.render('FOULS', True, (255, 128, 128))
        self.points = self.message_font.render('SCORE', True, (255, 128, 128))

        #Setting our screen messanges that are not buttons
        
        pygame.mixer.music.load('Sounds//music_menu.ogg') 
        self.button_sel = pygame.mixer.Sound("Sounds/button_select.ogg")
        self.start_g = pygame.mixer.Sound("Sounds/game_start.ogg")
        #Importing some sound files

        with open('saves/options_data.json') as file:
            data = json.load(file)
        if data[0] == 'enabled':
            self.sounds = True
        else: self.sounds = False
        if self.sounds and not pygame.mixer.music.get_busy(): 
            pygame.mixer.music.play(-1)


    def check_ev(self, screen, frame_clock):
        if self.sounds == False: 
            pygame.mixer.pause()
        else: pygame.mixer.unpause()
        while True:
            if self.main_menu:
                self.main_menu_screen(screen, frame_clock)
            elif self.start_menu:
                self.start_screen(screen, frame_clock)
            elif self.game_mode_menu:
                self.game_mode_screen(screen, frame_clock)
            elif self.options_menu:
                self.options_screen(screen, frame_clock)
            elif self.exit_menu:
                self.exit_screen(screen, frame_clock)
            elif self.highscore_menu:
                self.highscore_screen(screen, frame_clock)
            elif self.eightball_highscore_menu:
                self.eightball_highscore(screen, frame_clock)
            elif self.nineball_highscore_menu:
                self.nineball_highscore(screen, frame_clock)
            elif self.french_highscore_menu:
                self.french_highscore(screen, frame_clock)
            elif self.snooker_highscore_menu:
                self.snooker_highscore(screen, frame_clock)
            else:
                return False
    #Using our previous conditions in order to check which menu is to display
        
    def main_menu_screen(self,screen, frame_clock):
        message_pos = 1280
        while self.main_menu:
            screen.blit(self.menu_surface, (0, 0))
            screen.blit(self.text_surface, self.text_rect)
            message_pos -= 2
            if message_pos < -450: message_pos = 1280
            screen.blit(self.message, (message_pos, 700))
            x = pygame.mouse.get_pos()
    #Setting a moving message at the bottom of the screen
            st, me, ex, tut, hg = buttons_main.menu_draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, st):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds == True:
                            self.button_sel.play()
                        self.main_menu = False
                        self.start_menu = True
                elif buttons_main.check(x, me):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds == True:
                            self.button_sel.play()
                        self.main_menu = False
                        self.options_menu = True
                elif buttons_main.check(x, ex):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds == True:
                            self.button_sel.play()
                        self.main_menu = False
                        self.exit_menu = True
                elif buttons_main.check(x, tut):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds == True:
                            self.button_sel.play()
                        self.main_menu = False
                        self.tutorial = True
                elif buttons_main.check(x, hg):
                     if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds == True:
                            self.button_sel.play()
                        self.main_menu = False
                        self.highscore_menu = True
    #Checking if the user wants to exit our game with the X button (or alt+F4) and if "clicks" any button thats changes our menu
            pygame.display.update()
            frame_clock.tick(60)
    #Updating our display and setting FPS to 60
    
    def start_screen(self, screen, frame_clock):
        while self.start_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.start_surface, self.start_rect)
    #Setting our start menu (A menu that asks user if he wants to start playing)
            x = pygame.mouse.get_pos()
            #yes, no = buttons_main.exit_menu(screen)
            eightball, nineball, french, snooker, back = buttons_main.start_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, eightball):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click press
                            pass
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.eightball = True
                            if self.sounds: self.button_sel.play()
                            self.start_menu = False
                            self.game_mode_menu = True
                elif buttons_main.check(x, nineball):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click press
                            pass
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.nineball = True
                            if self.sounds: self.button_sel.play()
                            self.start_menu = False
                            self.game_mode_menu = True
                elif buttons_main.check(x, french):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click press
                            pass
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.french = True
                            if self.sounds: self.button_sel.play()
                            self.start_menu = False
                            self.game_mode_menu = True
                elif buttons_main.check(x, snooker):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click press
                            pass
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.snooker = True
                            if self.sounds: self.button_sel.play()
                            self.start_menu = False
                            self.game_mode_menu = True
                elif buttons_main.check(x, back):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.start_menu = False
                        self.main_menu = True
    #Checking if the user wants to exit our game with the X button (or alt+F4) and if "clicks" any button that either starts the game or takes us back to main menu
            pygame.display.update()
            frame_clock.tick(60)
    #Updating our display and setting FPS to 60


    def game_mode_screen(self, screen, frame_clock):
        while self.game_mode_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.game_mode_surface, self.game_mode_rect)

            pvp_button_rec, freeplay_button_rec, back_button_rec = buttons_main.game_mode(screen)

            x = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, pvp_button_rec):
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            if self.sounds: self.start_g.play()
                            self.freeplay = False
                            self.game_mode_menu = False
                            return
                elif buttons_main.check(x, freeplay_button_rec):
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            if self.sounds: self.start_g.play()
                            self.freeplay = True
                            self.game_mode_menu = False
                            return
                elif buttons_main.check(x, back_button_rec):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.eightball = False
                        self.nineball = False
                        self.snooke = False
                        self.french = False
                        self.game_mode_menu = False
                        self.start_menu = True

            pygame.display.update()
            frame_clock.tick(60)

    
    def options_screen(self, screen, frame_clock):
        with open('saves/options_data.json', 'r') as file:
                options = json.load(file)
        typing_active1 = False
        typing_active2 = False
        message_pos = 1280
        while self.options_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.options_surface, self.options_rect)
            message_pos -= 2
            if message_pos < -450: message_pos = 1280
            if typing_active1 or typing_active2:
                screen.blit(self.enter, (message_pos, 700))
    #Setting our options menu, where the user is able to enable or disable all sounds, and go back to main menu
            x = pygame.mouse.get_pos()
            sound, table, retur, name1, name2 = buttons_main.options_menu(screen, options[0], options[1], options[2], options[3])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, sound):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if options[0] == 'enabled':
                            self.sounds = False
                            pygame.mixer.music.stop()
                            options[0] = 'disabled'
                        else:
                            self.sounds = True
                            pygame.mixer.music.play(-1)
                            options[0] = 'enabled'
                elif buttons_main.check(x, table):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if options[1] == 'green':
                            options[1] = 'red'
                        elif options[1] == 'red':
                            options[1] = 'blue'
                        else: options[1] = 'green'
                elif buttons_main.check(x, name1):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        typing_active1 = True
                        typing_active2 = False
                elif buttons_main.check(x, name2):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        typing_active2 = True
                        typing_active1 = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        typing_active2 = False
                        typing_active1 = False
                elif buttons_main.check(x, retur):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        typing_active2 = False
                        typing_active1 = False
                        if self.sounds: self.button_sel.play()
                        with open('saves/options_data.json', 'w') as file:
                            json.dump(options, file, indent=4)
                        self.options_menu = False
                        self.main_menu = True
                if typing_active1:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            if len(options[2]) >= 0:
                                options[2] = options[2][:-1]
                        elif len(options[2]) < 12:
                            options[2] += event.unicode
                elif typing_active2:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            if len(options[3]) >= 0:
                                options[3] = options[3][:-1]
                        elif len(options[3]) < 12:
                            options[3] += event.unicode
            if self.sounds == False:
                pygame.mixer.pause()
            else: pygame.mixer.unpause()
            pygame.display.update()
            frame_clock.tick(60)

    def exit_screen(self, screen, frame_clock):
        while self.exit_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.text_surface, self.text_rect)
            screen.blit(self.exit_surface, self.exit_rect)
        #Checking if user wants to exit the game
            x = pygame.mouse.get_pos()
            yes, no = buttons_main.exit_menu(screen) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, yes):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        pygame.quit()
                        exit()
                elif buttons_main.check(x, no):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.exit_menu = False
                        self.main_menu = True
            pygame.display.update()
            frame_clock.tick(60)
    #Updating our display and setting FPS to 60       


    def highscore_screen(self, screen, frame_clock):
        while self.highscore_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.highscore_surface, self.highscore_rect)
            x = pygame.mouse.get_pos()
            eightball, nineball, french, snooker, back = buttons_main.start_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, eightball):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.start_g.play()
                        self.eightball_highscore_menu = True
                        self.highscore_menu = False
                elif buttons_main.check(x, nineball):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.start_g.play()
                        self.nineball_highscore_menu = True
                        self.highscore_menu = False
                elif buttons_main.check(x, french):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.start_g.play()
                        self.french_highscore_menu = True
                        self.highscore_menu = False
                elif buttons_main.check(x, snooker):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.start_g.play()
                        self.snooker_highscore_menu = True
                        self.highscore_menu = False
                elif buttons_main.check(x, back):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.highscore_menu = False
                        self.main_menu = True
            pygame.display.update()
            frame_clock.tick(60)

    
    def eightball_highscore(self, screen, frame_clock):
        with open('saves/eightballw_score.json', 'r') as file:
            winners = json.load(file)
        
        with open('saves/eightballl_score.json', 'r') as file:
            loosers = json.load(file) 
        while self.eightball_highscore_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.eightscore_surface, self.eightscore_rect)
            screen.blit(self.date, (10, 260))
            screen.blit(self.winner, (160, 260))
            screen.blit(self.balls, (310, 260))
            screen.blit(self.turns, (10, 460))
            screen.blit(self.fouls, (160, 460))
            screen.blit(self.points, (310, 460))
            screen.blit(self.looser, (840, 260))
            screen.blit(self.balls, (990, 260))
            screen.blit(self.turns, (840, 460))
            screen.blit(self.fouls, (990, 460))
            screen.blit(self.points, (1140, 460))

            x, y, y1 = 10, 300, 500
            for w in winners:
                for i in range (0, 6):
                    txt = self.message_font.render(f'{w[i]}', True, white)
                    if i < 3:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if x > 310:
                        x = 10
                x = 10
                y += 30
                y1 += 30
            x, y, y1 = 840, 300, 500
            for l in loosers:
                for i in range (0, 5):
                    txt = self.message_font.render(f'{l[i]}', True, white)
                    if i < 2:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if i == 1:
                        x = 840
                x = 840
                y += 30
                y1 += 30
            back = buttons_main.eightball_high(screen)
            x = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, back):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.eightball_highscore_menu = False
                        self.highscore_menu = True

            pygame.display.update()
            frame_clock.tick(60)

    def nineball_highscore(self, screen, frame_clock):
        with open('saves/nineballw_score.json', 'r') as file:
            winners = json.load(file)
        
        with open('saves/nineballl_score.json', 'r') as file:
            loosers = json.load(file) 
        while self.nineball_highscore_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.ninescore_surface, self.ninescore_rect)
            screen.blit(self.date, (10, 260))
            screen.blit(self.winner, (160, 260))
            screen.blit(self.balls, (310, 260))
            screen.blit(self.turns, (10, 460))
            screen.blit(self.fouls, (160, 460))
            screen.blit(self.points, (310, 460))
            screen.blit(self.looser, (840, 260))
            screen.blit(self.balls, (990, 260))
            screen.blit(self.turns, (840, 460))
            screen.blit(self.fouls, (990, 460))
            screen.blit(self.points, (1140, 460))

            x, y, y1 = 10, 300, 500
            for w in winners:
                for i in range (0, 6):
                    txt = self.message_font.render(f'{w[i]}', True, white)
                    if i < 3:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if x > 310:
                        x = 10
                x = 10
                y += 30
                y1 += 30
            x, y, y1 = 840, 300, 500
            for l in loosers:
                for i in range (0, 5):
                    txt = self.message_font.render(f'{l[i]}', True, white)
                    if i < 2:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if i == 1:
                        x = 840
                x = 840
                y += 30
                y1 += 30
            back = buttons_main.eightball_high(screen)
            x = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, back):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.nineball_highscore_menu = False
                        self.highscore_menu = True

            pygame.display.update()
            frame_clock.tick(60)
    
    def french_highscore(self, screen, frame_clock):
        with open('saves/frenchw_score.json', 'r') as file:
            winners = json.load(file)
        
        with open('saves/frenchl_score.json', 'r') as file:
            loosers = json.load(file) 
        while self.french_highscore_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.frenchscore_surface, self.frenchscore_rect)
            screen.blit(self.date, (10, 260))
            screen.blit(self.winner, (160, 260))
            screen.blit(self.turns, (310, 260))
            screen.blit(self.points, (160, 460))
            screen.blit(self.looser, (950, 260))
            screen.blit(self.turns, (1100, 260))
            screen.blit(self.points, (950, 460))

            x, y, y1 = 10, 300, 500
            for w in winners:
                for i in range (0, 4):
                    txt = self.message_font.render(f'{w[i]}', True, white)
                    if i < 3:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if x > 310:
                        x = 160
                x = 10
                y += 30
                y1 += 30
            x, y, y1 = 950, 300, 500
            for l in loosers:
                for i in range (0, 3):
                    txt = self.message_font.render(f'{l[i]}', True, white)
                    if i < 2:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if i == 1:
                        x = 950
                x = 950
                y += 30
                y1 += 30
            back = buttons_main.eightball_high(screen)
            x = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, back):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.french_highscore_menu = False
                        self.highscore_menu = True

            pygame.display.update()
            frame_clock.tick(60)

    def snooker_highscore(self, screen, frame_clock):
        with open('saves/snookerw_score.json', 'r') as file:
            winners = json.load(file)
        
        with open('saves/snookerl_score.json', 'r') as file:
            loosers = json.load(file) 
        while self.snooker_highscore_menu:
            screen.blit(self.other_menus_surface, (0, 0))
            screen.blit(self.ninescore_surface, self.ninescore_rect)
            screen.blit(self.date, (10, 260))
            screen.blit(self.winner, (160, 260))
            screen.blit(self.balls, (310, 260))
            screen.blit(self.turns, (10, 460))
            screen.blit(self.fouls, (160, 460))
            screen.blit(self.points, (310, 460))
            screen.blit(self.looser, (840, 260))
            screen.blit(self.balls, (990, 260))
            screen.blit(self.turns, (840, 460))
            screen.blit(self.fouls, (990, 460))
            screen.blit(self.points, (1140, 460))

            x, y, y1 = 10, 300, 500
            for w in winners:
                for i in range (0, 6):
                    txt = self.message_font.render(f'{w[i]}', True, white)
                    if i < 3:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if x > 310:
                        x = 10
                x = 10
                y += 30
                y1 += 30
            x, y, y1 = 840, 300, 500
            for l in loosers:
                for i in range (0, 5):
                    txt = self.message_font.render(f'{l[i]}', True, white)
                    if i < 2:
                        screen.blit(txt, (x, y))
                    else:
                        screen.blit(txt, (x, y1))
                    x += 150
                    if i == 1:
                        x = 840
                x = 840
                y += 30
                y1 += 30
            back = buttons_main.eightball_high(screen)
            x = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif buttons_main.check(x, back):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: self.button_sel.play()
                        self.snooker_highscore_menu = False
                        self.highscore_menu = True

            pygame.display.update()
            frame_clock.tick(60)