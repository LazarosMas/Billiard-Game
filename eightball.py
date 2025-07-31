import pygame
import math
import pymunk
import pymunk.pygame_util
import time
import sys
import json
from datetime import datetime
from common_classes import Ball, Gameover, Define_borders, Define_hole_collisions, Setup_collisions, Draw_cue, Draw_power_bar, Adjust_power, Draw_shot_line, Are_balls_moving, Game_pause, Screen_message
pygame.init()


class Eightball:
    def __init__(self, screen, frame_clock, freeplay, game, menu):
        self.screen_size = (1280, 720)
        self.table_size = (1052, 608)
        self.screen = screen
        self.frame_clock = frame_clock
        self.freeplay = freeplay
        self.game = game
        self.menu = menu


        self.message_font1 = pygame.font.Font('ghostclan.ttf', 50)
        self.message_font2 = pygame.font.Font('ghostclan.ttf', 40)
        self.message_font3 = pygame.font.Font('ghostclan.ttf', 20)
        self.message_font4 = pygame.font.Font('ghostclan.ttf', 25)

        self.gameback_surface = pygame.image.load("Pictures/Background.png").convert_alpha()
        self.gameback_surface = pygame.transform.smoothscale(self.gameback_surface, self.screen_size)

        with open('saves/options_data.json', 'r') as file:
            self.options = json.load(file)

        if self.options[0] == 'enabled':
            self.sounds = True
        else:
            self.sounds = False

        if self.options[1] == 'green':
            self.table_surface = pygame.image.load("Pictures/Green_Table.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)
        elif self.options[1] == 'red':
            self.table_surface = pygame.image.load("Pictures/Red_Table.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)
        else:
            self.table_surface = pygame.image.load("Pictures/Blue_Table.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)

        self.player1_name = self.options[2]
        self.player2_name = self.options[3]

        self.ball_in_s = pygame.mixer.Sound("Sounds/ball_in.mp3")
        self.ball_hit_s = pygame.mixer.Sound('Sounds/Ball_hit.mp3')
        self.ball_to_ball = pygame.mixer.Sound('Sounds/ball_to_ball.mp3')
        pygame.mixer.music.load('Sounds/background_music.mp3') 
        if self.sounds and not pygame.mixer.music.get_busy(): 
            pygame.mixer.music.play(-1)
        #Setting sounds

        self.player1_turn = True
        self.player2_turn = False 
        self.turn_solids = False
        self.turn_stripes = False
        #Booleans that are going to be used to control turns 

        self.player1_turns = 0
        self.player2_turns = 0
        self.player1_potted_balls = 0
        self.player2_potted_balls = 0
        self.player1_fouls = 0
        self.player2_fouls = 0
        self.player1 = []
        self.player2 = []
        self.winner = None
        #Variables that are goint to be used for final score
        
        self.gameover = False
        
        self.space = pymunk.Space()
        self.space.gravity = (0, 0) 
        #Setting pymunk space
        
        self.solids_remaining = 7
        self.stripes_remaining = 7
        self.black = True
        self.just_black = False
        self.white_ball_image = pygame.image.load("Pictures/White.png").convert_alpha()
        self.white_ball_image = pygame.transform.smoothscale(self.white_ball_image, (24, 24))  # Diameter=12*2
        self.white_in_hole = False
        self.balls = []
        self.setup_balls()

        self.placing_white_ball = False  # placement
        self.first_collision = None
        self.first_break = True
        self.shot = False
        self.not_first_touch = True
        self.assigned_balls = False
        self.ball_changed = False

        self.power = 0  # Starting power value
        self.max_power = 1100  # Maximum power
        self.power_direction = 1  # Power direction (1 = increasing, -1 = decreasing)
        self.holding_left_click = False  # player is holding the left click
        self.balls_stable = True
        
        self.foul = False
        self.foul_message = False

        self.player1_balls = "-"
        self.player2_balls = "-"

        self.player_1_hole = None
        self.player_2_hole = None
        self.hole_selection = False
        #variables for hole selection

        self.start_time = pygame.time.get_ticks()  # Record the start time of the game

        self.in_borders = False
        self.define_borders = Define_borders(self.space, 'eightball')
        self.define_borders.borders()
        #Define borders
        self.define_hole_positions = Define_hole_collisions(self.space)
        self.holes = self.define_hole_positions.define()
        #Define holes
        self.setup_collisions = Setup_collisions(self.space, self.not_first_touch, self.handle_ball_hole_collision, self.ball_to_ball_collision)
        self.setup_collisions.collisions()
        #Controlling the collisions

        self.draw_power_bar = Draw_power_bar(self.screen, self.screen_size, self.max_power)
        self.adjust_power = Adjust_power(self.max_power)
        self.draw_shot_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball)
        self.are_balls_moving = Are_balls_moving()
        self.game_pause = Game_pause(self.screen, self.game, self.menu, self.sounds)
        # Start the game loop
        self.game_screen(screen, frame_clock)


    def setup_balls(self):
        white_pos = [538, 359]
        black_pos = [979, 359]
        self.solids = [(935, 359), (957, 347), (979, 384), (1001, 321), (1001, 371), (1023, 408), (1023, 333)]
        self.stripes = [(957, 372), (979, 334), (1001, 396), (1001, 346), (1023, 308), (1023, 358), (1023, 383)]

        white_ball = Ball(white_pos, 12, 1, self.space, "Pictures/White.png", 'white')
        self.white_ball = white_ball
        self.balls.append(white_ball)

        for i, pos in enumerate(self.solids):
            self.balls.append(Ball(pos, 12, 1, self.space, f"Pictures/{i+1}.png", 'solids'))

        black_ball = Ball(black_pos, 12, 1, self.space, "Pictures/8.png", 'black')
        self.black_ball = black_ball
        self.balls.append(black_ball)

        for i, pos in enumerate(self.stripes):
            self.balls.append(Ball(pos, 12, 1, self.space, f"Pictures/{i+9}.png", 'stripes'))
#calling the Ball class in order to create our balls

    def draw_balls(self, screen):
        for ball in self.balls:
            ball.draw(screen)
#draw the balls

    def handle_ball_hole_collision(self, arbiter, space, data):
        ball_shape = arbiter.shapes[0]  
        potted_ball = None
        for b in self.balls:
            if b.shape == ball_shape:
                potted_ball = b
                break

        if ball_shape == self.white_ball.shape:
            self.foul = True
            self.foul_message = False
            self.placing_white_ball = True  
#if the white ball collides with one with the holes, there is a foul and player gets to place the white ball
        elif potted_ball:
            hole_positions = [(303, 124), (758, 104), (1213, 124), 
                          (303, 593), (758, 614), (1213, 593)]
            potted_hole = min(hole_positions, key=lambda pos: math.dist(pos, potted_ball.body.position))
            # Get the closest hole to the potted ball
            if not self.freeplay and potted_ball.ball_type == 'black':
                date_time_score = datetime.now()
                score_date = date_time_score.strftime("%x")
                valid_hole = False
                if self.player1_turn:
                    if self.player_1_hole == potted_hole:
                        valid_hole = True
                    if self.player1_balls == 'black' and not self.foul and valid_hole:
                        self.winner = self.player1_name
                        self.player1_potted_balls += 3
                    else:
                        self.winner = self.player2_name
                if self.player2_turn:
                    if self.player_2_hole == potted_hole:
                        valid_hole = True
                    if self.player2_balls == 'black' and not self.foul and valid_hole:
                        self.winner = self.player2_name
                        self.player1_potted_balls += 3
                    else:
                        self.winner = self.player1_name
                player1_score = self.player1_potted_balls - (0.25 * self.player1_fouls)
                player2_score = self.player2_potted_balls - (0.25 * self.player2_fouls)
                if self.winner == self.player1_name:
                    p1 = [score_date, self.player1_name, self.player1_potted_balls, self.player1_turns, self.player1_fouls, player1_score]
                    p2 = [self.player1_name, self.player2_potted_balls, self.player2_turns, self.player2_fouls, player2_score]
                else:
                    p1 = [self.player1_name, self.player1_potted_balls, self.player1_turns, self.player1_fouls, player1_score]
                    p2 = [score_date, self.player2_name, self.player2_potted_balls, self.player2_turns, self.player2_fouls, player2_score]
                self.player1.extend(p1)
                self.player2.extend(p2)
                self.gameover = True
#if the black ball collides with one of the holes, and it's not a freeplay, the gameover is called
            elif not self.freeplay and not self.assigned_balls:
                if self.player1_turn:
                    if potted_ball.ball_type == 'solids':
                        self.player1_balls = 'solids'
                        self.player2_balls = 'stripes'
                        self.solids_remaining -= 1
                        self.turn_solids = True
                        self.player1_potted_balls += 1
                    elif potted_ball.ball_type == 'stripes':
                        self.player1_balls = 'stripes'
                        self.player2_balls = 'solids'
                        self.stripes_remaining -= 1
                        self.turn_stripes = True
                        self.player1_potted_balls += 1
                elif self.player2_turn:
                    if potted_ball.ball_type == 'solids':
                        self.player1_balls = 'stripes'
                        self.player2_balls = 'solids'
                        self.solids_remaining -= 1
                        self.turn_solids = True
                        self.player2_potted_balls += 1
                    elif potted_ball.ball_type == 'stripes':
                        self.player1_balls = 'solids'
                        self.player2_balls = 'stripes'
                        self.stripes_remaining -= 1
                        self.turn_stripes = True
                        self.player2_potted_balls += 1
                self.assigned_balls = True
                self.ball_changed = True
#After the first stripe of solid collision, the balls are assigned to the players
            elif not self.freeplay:
                #bugfix
                if potted_ball.ball_type == 'solids':
                    self.solids_remaining -= 1
                    self.turn_solids = True
                    if self.player1_turn and self.player1_balls == 'solids':
                        self.player1_potted_balls += 1
                    elif self.player2_turn and self.player2_balls == 'solids':
                        self.player2_potted_balls += 1
                elif potted_ball.ball_type == 'stripes':
                    self.stripes_remaining -= 1
                    self.turn_stripes = True
                    if self.player1_turn and self.player1_balls == 'stripes':
                        self.player1_potted_balls += 1
                    elif self.player2_turn and self.player2_balls == 'stripes':
                        self.player2_potted_balls += 1
        if self.sounds:
            self.ball_in_s.play()
        self.remove_ball(ball_shape)
#call the remove_ball func
        return False


    def ball_to_ball_collision(self, arbiter, space, data):
        ball_a, ball_b = arbiter.shapes
        velocity_a = ball_a.body.velocity.length 
        velocity_b = ball_b.body.velocity.length 
        speed = abs(velocity_a - velocity_b)
        max_speed = 1100 
        volume = min(speed / max_speed, 1.0)  # Ensure volume is between 0.0 and 1.0
        self.ball_to_ball.set_volume(volume)
        if self.sounds:       
            self.ball_to_ball.play()
#The volume is based on the impact
        if self.first_collision is not None:
            return True  
 
        if ball_a != self.white_ball.shape and ball_b != self.white_ball.shape:
            return True
        elif ball_a == self.white_ball.shape:
            self.not_first_touch = False
            for b in self.balls:
                if b.shape == ball_b:
                    self.first_collision = b.ball_type
                    break
        elif ball_b == self.white_ball.shape:
            self.not_first_touch = False
            for b in self.balls:
                if b.shape == ball_a:
                    self.first_collision = b.ball_type
                    break
#Checking which ball type (solid, stripe or black) the white ball hit first
        return True


    def remove_ball(self, ball_shape):
        if ball_shape in self.space.shapes:
            self.space.remove(ball_shape, ball_shape.body)
        #remove the ball from pymunk's space

        self.balls = [ball for ball in self.balls if ball.shape != ball_shape]
        #remove the ball from the balls list


    def screen_message(self, screen, mes_pos):
        if not self.freeplay:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "Eightball", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 340, 177, 25))
            if self.player1_turn:
                Screen_message(self.message_font3, f"{self.player1_name}'s turn", (3, 352), (128, 128, 128), align="midleft").draw(self.screen)
            else: Screen_message(self.message_font3, f"{self.player2_name}'s turn", (3, 352), (128, 128, 128), align="midleft").draw(self.screen)

            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 60, 220, 35))
            Screen_message(self.message_font2, self.player1_name, (10, 75), (255, 255, 255), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 220, 35))
            Screen_message(self.message_font2, self.player2_name, (10, 195), (255, 255, 255), align="midleft").draw(self.screen)

            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 300, 220, 35))
            Screen_message(self.message_font3, "Game message", (3, 316), (212, 45, 45), align="midleft").draw(self.screen)
            if not self.assigned_balls:
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 100, 177, 25))
                Screen_message(self.message_font3, "Not assigned", (10, 112), (128, 128, 128), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 220, 177, 25))
                Screen_message(self.message_font3, "Not assigned", (10, 232), (128, 128, 128), align="midleft").draw(self.screen)
            #while and of the solids and stripes are still on play, show "Not assigned" while and of the solids and stripes are still on play
            else:
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 100, 150, 25))
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 220, 150, 25))
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 130, 185, 25))
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 250, 185, 25))
                Screen_message(self.message_font4, f"{self.player1_balls}", (25, 112), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font4, f"{self.player2_balls}", (25, 232), (128, 128, 128), align="midleft").draw(self.screen)
                if self.player1_balls == 'solids':
                    Screen_message(self.message_font4, f"Remaining: {self.solids_remaining}", (10, 142), (0, 0, 0), align="midleft").draw(self.screen)
                elif self.player2_balls == 'solids':
                    Screen_message(self.message_font4, f"Remaining: {self.solids_remaining}", (10, 262), (0, 0, 0), align="midleft").draw(self.screen)
                if self.player1_balls == 'stripes':
                    Screen_message(self.message_font4, f"Remaining: {self.stripes_remaining}", (10, 142), (0, 0, 0), align="midleft").draw(self.screen)
                elif self.player2_balls == 'stripes':
                    Screen_message(self.message_font4, f"Remaining: {self.stripes_remaining}", (10, 262), (0, 0, 0), align="midleft").draw(self.screen)
                if self.player1_balls == 'black':
                    Screen_message(self.message_font4, "Just 1 ball", (10, 142), (0, 0, 0), align="midleft").draw(self.screen)
                if self.player2_balls == 'black':
                    Screen_message(self.message_font4, "Just 1 ball", (10, 262), (0, 0, 0), align="midleft").draw(self.screen)   
                #Show what type of ball each player has to pot

            if self.foul_message:
                if self.player1_turn:
                    Screen_message(self.message_font4, f"Foul! {self.player1_name} white ball placement", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
                else:
                    Screen_message(self.message_font4, f"Foul! {self.player2_name} white ball placement", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            elif self.first_break:
                Screen_message(self.message_font4, f"{self.player1_name}'s turn! Time for break!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            else:
                if self.player1_turn:
                    Screen_message(self.message_font4, f"{self.player1_name}'s turn", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
                    
                else:
                    Screen_message(self.message_font4, f"{self.player2_name}'s turn", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
        else:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "Freeplay", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            Screen_message(self.message_font4, "Freeplay! No fouls are applied!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)



    def draw_hole_g(self):
        hole_positions = [(303, 124), (758, 104), (1213, 124), (303, 593), (758, 614), (1213, 593)]
        chosen = False
        self.hole_selection = True
        while not chosen: 
            pygame.mouse.set_visible(True)
            mouse_position = pygame.mouse.get_pos()
            for a,b in hole_positions:
                pygame.draw.circle(self.screen, (255,255,255), (a, b), 24, 0)
                distance = math.sqrt((mouse_position[0] - a) ** 2 + (mouse_position[1] - b) ** 2)
                if distance <= 24:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click press
                        pass
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for a, b in hole_positions:
                            distance = math.sqrt((mouse_position[0] - a) ** 2 + (mouse_position[1] - b) ** 2)
                            if distance <= 24:
                                chosen = True
                                player_hole = (a, b)
                                break
            pygame.display.update()
            self.frame_clock.tick(60)
        self.hole_selection = False
        return player_hole
        

    def hit_white_ball(self, direction_speed):
        if self.sounds:
            self.ball_hit_s.play()
        self.balls[0].body.apply_impulse_at_world_point(direction_speed, self.balls[0].body.position)
    #Hit the white ball towards a target
    

    def check_for_foul(self):
        if not self.first_break and self.shot and not self.freeplay:
            if self.first_collision is None and not self.ball_changed:
            # No collision occurred; it's a foul
                self.foul = True
                self.foul_message = True
            elif not self.assigned_balls:
                if self.first_collision != 'solids' and self.first_collision != 'stripes':
                    self.foul = True
                    self.foul_message = True
            else:
                if self.player1_turn:
                    if self.first_collision != self.player1_balls and not self.ball_changed:
                        self.foul = True
                        self.foul_message = True
                elif self.player2_turn:
                    if self.first_collision != self.player2_balls and not self.ball_changed:
                        self.foul = True
                        self.foul_message = True
        self.ball_changed = False
    #Check if the player hits with whiteball his assigned balls first

    def check_for_black(self):
        if self.assigned_balls:
            if self.solids_remaining <= 0:
                if self.player1_balls == 'solids':
                    self.player1_balls = 'black'
                    self.ball_changed = True
                    if not self.foul:
                        self.just_black = True
                elif self.player2_balls == 'solids':
                    self.player2_balls = 'black'
                    self.ball_changed = True
                    if not self.foul:
                        self.just_black = True
            if self.stripes_remaining <= 0:
                if self.player1_balls == 'stripes':
                    self.player1_balls = 'black'
                    self.ball_changed = True
                    if not self.foul:
                        self.just_black = True
                elif self.player2_balls == 'stripes':
                    self.player2_balls = 'black'
                    self.ball_changed = True
                    if not self.foul:
                        self.just_black = True
            if self.player1_balls == 'black' and self.player_1_hole is None:
                self.player_1_hole = self.draw_hole_g()
            if self.player2_balls == 'black' and self.player_2_hole is None:
                self.player_2_hole = self.draw_hole_g()
#bug fix

    def change_turn(self):
        if self.first_break:
            self.first_break = False
        if self.player1_turn:
            if self.player1_balls == 'solids':
                if not self.turn_solids or self.foul:
                    self.player1_turn = not self.player1_turn
                    self.player2_turn = not self.player2_turn
            elif self.player1_balls == 'stripes':
                if not self.turn_stripes or self.foul:
                    self.player1_turn = not self.player1_turn
                    self.player2_turn = not self.player2_turn
            else:
                self.player1_turn = not self.player1_turn
                self.player2_turn = not self.player2_turn
        elif self.player2_turn:
            if self.player2_balls == 'solids':
                if not self.turn_solids or self.foul:
                    self.player2_turn = not self.player2_turn
                    self.player1_turn = not self.player1_turn
            elif self.player2_balls == 'stripes':
                if not self.turn_stripes or self.foul:
                    self.player2_turn = not self.player2_turn
                    self.player1_turn = not self.player1_turn
            else:
                self.player1_turn = not self.player1_turn
                self.player2_turn = not self.player2_turn
        self.turn_solids = False
        self.turn_stripes = False
        #Checks at the end of the turn, if player has potted his assigned balls, and if he didn't, turn changes




    def game_screen(self, screen, frame_clock):
        game_paused = False
        cue_visible = True #bool to check if cue should be visible
        white_ball_movable = True #bool to check if player can hit the white ball
        mouse_visible = True 
        draw_cue = Draw_cue(self.screen) #call to draw the cue
        mes_pos = 1280
        
        last_movement_time = time.time() - 1  # A slight delay 
        x = 0.0
        dt = 1/60.0  # Fixed time step

        while self.game:
            frame_time = frame_clock.tick(60) / 1000.0  # Convert to seconds
            x += frame_time
            while x >= dt:
                self.space.step(dt)
                x -= dt
            pygame.time.get_ticks()

            screen.blit(self.gameback_surface, (0, 0))
            screen.blit(self.table_surface, (232,56))
            self.draw_balls(self.screen)
            self.screen_message(self.screen, mes_pos)

            mes_pos -= 2
            if mes_pos < -500: mes_pos = 1280
            #makes a moving message

            mouse_pos = pygame.mouse.get_pos()
            if (315 <= mouse_pos[0] <= 1200) and (136 <= mouse_pos[1] <= 580) and not game_paused and not self.hole_selection:
                if mouse_visible:
                    pygame.mouse.set_visible(False)
                    mouse_visible = False
            else:
                if not mouse_visible:
                    pygame.mouse.set_visible(True)
                    mouse_visible = True
            #as long as mouse is within table's borders, it's invincible

            if not self.placing_white_ball and not self.hole_selection:
                white_pos = self.balls[0].body.position  
            draw_cue.draw_c(white_pos, mouse_pos, cue_visible)
            #take the position of white ball and use it to draw the cue

            self.draw_power_bar.draw_power(self.power)

            balls_moving = self.are_balls_moving.check(self.balls, self.balls_stable, self.check_for_foul, self.not_first_touch)  
            # Check if any ball is moving

            if not balls_moving and self.shot and not self.hole_selection: #if the player shot the ball and balls stopped moving
                if self.foul:
                    if self.player1_turn:
                        self.player1_fouls += 1
                    else:
                        self.player2_fouls += 1
                    if self.white_ball.shape in self.space.shapes:
                        self.space.remove(self.white_ball.shape, self.white_ball.body)
                        self.balls = [ball for ball in self.balls if ball.shape != self.white_ball.shape]
                    self.placing_white_ball = True
                    #When the balls stops moving, if there is a foul, the next player places the ball
                if not self.freeplay: 
                    self.check_for_black()
                    if not self.just_black:
                        self.change_turn()
                    else:
                        self.just_black = False
                self.foul = False
                self.shot = False
                #Reseting the first shot
                self.first_collision = None

            if (self.placing_white_ball or (self.freeplay and self.white_ball.shape not in self.space.shapes)) and self.in_borders and not balls_moving:
                white_ball_rect = self.white_ball_image.get_rect(center=mouse_pos)
                screen.blit(self.white_ball_image, white_ball_rect)
            #at the whiteball placement, the white ball appears only in table's borders

            if self.holding_left_click and not self.hole_selection:
                self.power, self.power_direction = self.adjust_power.adjust(self.power, self.power_direction)
            #while holding the left click, starts the power adjustment of the ball 

            if cue_visible and not self.placing_white_ball:
                self.draw_shot_line.draw(white_pos, mouse_pos)
            #draw the white line
            
            if balls_moving or self.placing_white_ball or self.hole_selection:
                cue_visible = False  
                white_ball_movable = False  
                last_movement_time = time.time()  
            else:
                if time.time() - last_movement_time > 1:
                    cue_visible = True  
                    white_ball_movable = True  
            #after the balls stops moving, the cue is visible again, and player can play

            if not self.freeplay and self.gameover: 
                gameover_screen = Gameover(self.screen, self.winner, self.game, self.menu, 'eightball', self.player1, self.player2, self.sounds)
                if gameover_screen.display() == 'menu':
                    return
            #checks for gameover

            if self.player_1_hole and self.player1_turn:
                pygame.draw.circle(self.screen, (255,255,255), self.player_1_hole, 24, 0)
            if self.player_2_hole and self.player2_turn:
                pygame.draw.circle(self.screen, (255,255,255), self.player_2_hole, 24, 0)
            #Draws the selected hole to pot the ball

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu, self.game, self.sounds = self.game_pause.p(game_paused)
                        if self.sounds and not pygame.mixer.music.get_busy():  # Play only if not already playing
                            pygame.mixer.music.play(-1)
                        elif not self.sounds or not self.game:
                            pygame.mixer.music.stop()
                #checks for exit or pause

                if self.player1_turn or self.player2_turn:
                    if event.type == pygame.MOUSEBUTTONDOWN and white_ball_movable and not self.hole_selection:
                        if event.button == 1:  # Left click press
                            self.holding_left_click = True
                            # Start adjusting power when left click

                    if event.type == pygame.MOUSEBUTTONUP and white_ball_movable and not self.hole_selection:
                        if event.button == 1:  # Left click release
                            # Release the left click and apply the impulse
                            self.holding_left_click = False
                            click_pos = pymunk.Vec2d(mouse_pos[0], mouse_pos[1]) 
                            white_pos = self.balls[0].body.position
                            direction = click_pos - white_pos
                            distance = direction.length
                            # Calculate direction from white ball to mouse release position
                            if distance > 0:
                                direction = direction.normalized()
                                speed = self.power 
                                direction_speed = direction * speed
                                self.hit_white_ball(direction_speed)
                                self.shot = True
                                #Calculate the power to hit the white ball
                                if self.player1_turn:
                                    self.player1_turns += 1
                                else:
                                    self.player2_turns += 1
                            self.power = 0
                            self.power_direction = 1 
                            # Reset the power after the hit
                            
                        if event.button == 3:  # Right click
                            self.holding_left_click = False
                            # Cancel the power adjustment
                            self.power = 0
                            self.power_direction = 1

                if self.placing_white_ball:
                    borders_left, borders_right = 328, 1187
                    borders_top, borders_bottom = 147, 567
                    if (borders_left < mouse_pos[0] < borders_right and borders_top < mouse_pos[1] < borders_bottom):
                        self.in_borders = True
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            overlap = False
                            for ball in self.balls:
                                distance = (pymunk.Vec2d(ball.body.position[0], ball.body.position[1]) - mouse_pos).length
                                if distance < (ball.shape.radius + 12):  # 12 is the radius of the balls
                                    overlap = True
                                    break
                            #checks at the ball placement if the mouse, aka white ball overlaps with the other balls
                            if not overlap:
                                new_white_ball = Ball((mouse_pos[0], mouse_pos[1]), 12, 1, self.space, "Pictures/White.png", 'white')
                                self.white_ball = new_white_ball  
                                self.balls.insert(0, new_white_ball)

                                self.draw_shot_line.white_ball = self.white_ball
                            #places the new white ball
                                self.foul_message = False
                                self.placing_white_ball = False
                                self.foul = False
                    else:
                        self.in_borders = False 

            
            pygame.display.update()