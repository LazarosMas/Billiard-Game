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

class Nineball:
    def __init__(self, screen, frame_clock, freeplay, game, menu):
        self.screen_size = (1280, 720)
        self.table_size = (1052, 608)
        self.screen = screen
        self.frame_clock = frame_clock
        self.game = game
        self.menu = menu
        self.freeplay = freeplay

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
        
        self.ball_hit_s = pygame.mixer.Sound('Sounds/Ball_hit.mp3')
        self.ball_to_ball = pygame.mixer.Sound('Sounds/ball_to_ball.mp3')
        self.ball_in_s = pygame.mixer.Sound("Sounds/ball_in.mp3")
        pygame.mixer.music.load('Sounds/background_music.mp3') 
        if self.sounds and not pygame.mixer.music.get_busy(): 
            pygame.mixer.music.play(-1)

        self.message_font1 = pygame.font.Font('ghostclan.ttf', 50)
        self.message_font2 = pygame.font.Font('ghostclan.ttf', 40)
        self.message_font3 = pygame.font.Font('ghostclan.ttf', 20)
        self.message_font4 = pygame.font.Font('ghostclan.ttf', 25)

        
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # Since there's no gravity in a pool game

        self.player1_turn = True
        self.player2_turn = False
        self.to_change_turn = True
        self.turn_selection = True

        self.first_break = True

        self.not_first_touch = True

        self.player1_turns = 0
        self.player2_turns = 0
        self.player1_potted_balls = 0
        self.player2_potted_balls = 0
        self.player1_fouls = 0
        self.player2_fouls = 0
        self.winner = None
        self.player1 = []
        self.player2 = []
        #variables for game over
        self.gameover = False

        self.white_ball_image = pygame.image.load("Pictures/White.png").convert_alpha()
        self.white_ball_image = pygame.transform.smoothscale(self.white_ball_image, (24, 24))
        self.white_ball = None
        self.white_in_hole = False
        self.placing_white_ball = False 

        self.in_borders = False

        self.foul = False
        self.foul_message = False
        self.shot = False  


        self.ball_potted = False
        self.pushout_after_break = None
        self.pushout_decision = None
        self.pushout_shot = False
        self.pushout_accept = None
        self.pushout_steps = 0

        self.first_collision = None
        self.power = 0  # Starting power value
        self.max_power = 1100  # Max power
        self.power_direction = 1 
        self.holding_left_click = False  #the player is holding the left click

        self.pos1 = None
        self.pos2 = None

        self.balls_pos = [(935, 359), (979, 384), (979, 334), (1023, 358), (957, 347), (957, 372), (1001, 371), (1001, 346), (979, 359)]
        self.balls_stable = True
        self.ball_to_hit = 1
        self.balls_remaining = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.balls = []
        self.setup_balls()

        self.balls_to_cushion = 0
        self.potted_balls = []
        self.potted_9 = False

        self.define_borders = Define_borders(self.space, 'nineball')
        self.define_borders.borders()

        self.define_hole_positions = Define_hole_collisions(self.space)
        self.holes = self.define_hole_positions.define()    

        self.setup_collisions = Setup_collisions(self.space, self.not_first_touch, self.ball_hole_collision, self.ball_to_ball_collision)
        self.setup_collisions.collisions()
        self.setup_collisions.cushions(self.ball_to_cushion)

        self.draw_power_bar = Draw_power_bar(self.screen, self.screen_size, self.max_power)
        self.adjust_power = Adjust_power(self.max_power)
        self.draw_shot_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball) 

        self.are_balls_moving = Are_balls_moving()
        self.game_pause = Game_pause(self.screen, self.game, self.menu, self.sounds)

        self.game_screen(self.screen, self.frame_clock)



    def setup_balls(self):
        white_pos = [538, 359]
        white_ball = Ball(white_pos, 12, 1, self.space, "Pictures/White.png", 'white')
        self.white_ball = white_ball
        self.balls.append(white_ball)

        if not self.turn_selection or self.freeplay:
            for i, pos in enumerate(self.balls_pos):
                self.balls.append(Ball(pos, 12, 1, self.space, f"Pictures/{i+1}.png", i+1))


    def draw_balls(self, screen):
        for ball in self.balls:
            ball.draw(screen)


    def ball_hole_collision(self, arbiter, space, data):
        ball_shape = arbiter.shapes[0]  
        potted_ball = None

        for b in self.balls:
            if b.shape == ball_shape:
                potted_ball = b
                break

        if ball_shape == self.white_ball.shape:
            self.foul = True
            self.foul_message = True
            self.placing_white_ball = True  
#if the white ball collides with one with the holes, there is a foul and player gets to place the white ball
        elif potted_ball:
            for i in self.balls_remaining:
                if int(potted_ball.ball_type) == i:
                    self.balls_remaining.remove(i)
                    self.ball_potted = True
                    self.potted_balls.append(int(i))
                    break
        if self.sounds: 
            self.ball_in_s.play()
        self.remove_ball(ball_shape)
        if potted_ball.ball_type != 'white':    
            if int(potted_ball.ball_type) == 9:
                if self.pushout_steps == 2 or self.pushout_steps == 3:
                    self.balls.append(Ball((979, 359), 12, 1, self.space, "Pictures/9.png", 9))
                else:
                    self.potted_9 = True
    #call the remove_ball func
        return False


    def ball_to_ball_collision(self, arbiter, space, data): 
        ball_a, ball_b = arbiter.shapes
        velocity_a = ball_a.body.velocity.length 
        velocity_b = ball_b.body.velocity.length 
        speed = abs(velocity_a - velocity_b)
        max_speed = 1000 
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
        elif ball_b == self.white_ball.shape:
            self.not_first_touch = False
            for b in self.balls:
                if b.shape == ball_a:
                    self.first_collision = b.ball_type
#Checking which ball type (solid, stripe or black) the white ball hit first
        return True 
    

    def remove_ball(self, ball_shape):
        if ball_shape in self.space.shapes:
            self.space.remove(ball_shape, ball_shape.body)
        #remove the ball from pymunk's space

        self.balls = [ball for ball in self.balls if ball.shape != ball_shape]
        #remove the ball from the balls list


    def ball_to_cushion(self, arbiter, space, data):
        ball_shape = arbiter.shapes[0]

        self.balls_to_cushion += 1
        return True


    def hit_white_ball(self, direction_speed):
        if self.sounds: 
            self.ball_hit_s.play()
        self.balls[0].body.apply_impulse_at_world_point(direction_speed, self.balls[0].body.position)
    #Hit the white ball towards a target


    def check_for_foul(self):
        if self.pushout_steps == 2 or self.pushout_steps == 3:  # Ignore all fouls except white ball in hole during push-out
            if self.placing_white_ball:
                self.foul = True  # White ball in hole still counts as foul
            else:
                self.foul = False  # Ignore other fouls during push-out
        elif not self.turn_selection:
            if self.first_collision == None:
                self.foul = True
            elif int(self.first_collision) != self.ball_to_hit:
                self.foul = True
            elif self.placing_white_ball:
                self.foul = True
            else:
                self.foul = False


    def break_check(self):
        self.first_break = False
        if self.balls_to_cushion < 4 and not self.ball_potted:
            if not self.white_in_hole:
                if self.white_ball.shape in self.space.shapes:
                    self.space.remove(self.white_ball.shape, self.white_ball.body)
                    self.balls = [ball for ball in self.balls if ball.shape != self.white_ball.shape]
                self.foul = True
                self.placing_white_ball = True
            else:
                self.foul = True
        elif not self.foul and (self.balls_to_cushion >=4 or self.ball_potted):
            self.pushout_after_break = True
            self.pushout_steps = 1


    def change_turn(self):
        if self.to_change_turn or self.foul:
            self.player1_turn = not self.player1_turn
            self.player2_turn = not self.player2_turn


    def first_turn(self, p1, p2, balls_moving):
        if not balls_moving:
            white_pos = self.balls[0].body.position
            if self.player1_turn and self.shot:
                self.pos1 = white_pos
                self.player1_turn = False
                self.player2_turn = True
                p1 = True
                self.remove_ball(self.balls[0].shape)
                self.shot = False
                self.setup_balls()
                self.draw_shot_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball)
                white_pos = self.balls[0].body.position
                
            elif self.player2_turn and self.shot:
                self.pos2 = white_pos
                p2 = True
                self.remove_ball(self.balls[0].shape)
                self.turn_selection = False
                self.setup_balls()
                self.draw_shot_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball)
                self.shot = False
                self.balls_to_cushion = 0

                if self.pos1[0] < self.pos2[0]:
                    self.player1_turn = True
                    self.player2_turn = False
                else:
                    self.player1_turn = False
                    self.player2_turn = True


    def screen_message(self, screen, mes_pos):
        if not self.freeplay:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "Nineball", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 60, 225, 35))
            Screen_message(self.message_font4, "Game message", (5, 75), (212, 45, 45), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 105, 190, 25))
            if self.player1_turn:
                Screen_message(self.message_font3, f"{self.player1_name}'s turn", (10, 118), (128, 128, 128), align="midleft").draw(self.screen)
            else: Screen_message(self.message_font3, f"{self.player2_name}'s turn", (10, 118), (128, 128, 128), align="midleft").draw(self.screen)

            if self.turn_selection:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Turn selection:", (3, 193), (212, 45, 45), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 215, 190, 75))
                Screen_message(self.message_font3, "Hit cue-ball as", (5, 228), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "close to left", (5, 243), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "cushion as po-", (5, 258), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "ssible", (5, 273), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font4, "Hit cue-ball as close to left cushion as possible to play first", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)

            elif self.first_break:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Time for break!", (3, 193), (212, 45, 45), align="midleft").draw(self.screen)
                Screen_message(self.message_font4, "Hit the 1 ball, as hard as possible", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            
            elif self.pushout_steps == 1:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Pushout!", (3, 193), (212, 45, 45), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 215, 190, 75))
                Screen_message(self.message_font3, "Press 1 for", (5, 228), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "Pushout or 2", (5, 243), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "To cancel it", (5, 258), (128, 128, 128), align="midleft").draw(self.screen)
            elif self.pushout_steps == 2:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Pushout", (5, 193), (212, 45, 45), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 215, 190, 75))
                Screen_message(self.message_font3, "Hit the ball", (5, 228), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "Freely", (5, 243), (128, 128, 128), align="midleft").draw(self.screen)
            elif self.pushout_steps == 3:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Pushout", (5, 193), (212, 45, 45), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 215, 190, 75))
                Screen_message(self.message_font3, "Press 1 to", (5, 228), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "accept or 2", (5, 243), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font3, "to decline", (5, 258), (128, 128, 128), align="midleft").draw(self.screen)
            
            elif self.placing_white_ball:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Foul", (40, 193), (212, 45, 45), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 215, 190, 25))
                Screen_message(self.message_font3, "Ball placement", (5, 228), (128, 128, 128), align="midleft").draw(self.screen)
                Screen_message(self.message_font4, "Place the cue ball at the table", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            else:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 190, 25))
                Screen_message(self.message_font3, "Message:", (30, 193), (212, 45, 45), align="midleft").draw(self.screen)
                pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 215, 190, 25))
                Screen_message(self.message_font3, "Have fun!", (30, 228), (128, 128, 128), align="midleft").draw(self.screen)
                if self.player1_turn:
                    Screen_message(self.message_font4, f"{self.player1_name}, Try your best!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
                else:
                    Screen_message(self.message_font4, f"{self.player2_name}, Try your best!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            
        else:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "Freeplay", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            Screen_message(self.message_font4, "Freeplay! No fouls are applied!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)


    def game_screen(self, screen, frame_clock):
        last_movement_time = time.time() - 1  # A slight delay
        x = 0.0
        dt = 1/60.0  # Fixed time step

        draw_cue = Draw_cue(self.screen)
        cue_visible = True
        white_ball_movable = True #bool to check if player can hit the white ball
        game_paused = False
        player1_turn_hit = False
        player2_turn_hit = False
        mes_pos = 1280

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
            self.screen_message(screen, mes_pos)
            
            mes_pos -= 2
            if mes_pos < -500: mes_pos = 1280
            #makes a moving message
            self.screen_message(self.screen, mes_pos)

            mouse_pos = pygame.mouse.get_pos()

            if not self.placing_white_ball:
                white_pos = self.balls[0].body.position  
            draw_cue.draw_c(white_pos, mouse_pos, cue_visible)
            #take the position of white ball and use it to draw the cue
            balls_moving = self.are_balls_moving.check(self.balls, self.balls_stable, self.check_for_foul, self.not_first_touch)  
            # Check if any ball is moving

            self.draw_power_bar.draw_power(self.power)

            if not self.turn_selection and not balls_moving and self.shot and not self.freeplay: #if the player shot the ball and balls stopped moving
                if self.first_break:
                    self.break_check()
                elif self.potted_9:
                    if self.player1_turn:
                        if not self.foul:
                            self.winner = self.player1_name
                        else:
                            self.winner = self.player2_name
                    elif self.player2_turn:
                        if not self.foul:
                            self.winner = self.player2_name
                        else:
                            self.winner = self.player1_name
                    self.gameover = True
                elif self.foul:
                    if self.player1_turn:
                        self.player1_fouls += 1
                    else:
                        self.player2_fouls += 1
                    if self.white_ball.shape in self.space.shapes:
                        self.space.remove(self.white_ball.shape, self.white_ball.body)
                        self.balls = [ball for ball in self.balls if ball.shape != self.white_ball.shape]
                    self.placing_white_ball = True
                    #When the balls stops moving, if there is a foul, the next player places the ball
                if self.player1_turn:
                    self.player1_potted_balls += len(self.potted_balls)
                else:
                    self.player2_potted_balls += len(self.potted_balls)
        
                if self.foul or (self.ball_to_hit not in self.potted_balls):
                    self.change_turn()
                self.potted_balls = []
                self.ball_to_hit = min(self.balls_remaining)
                self.foul = False
                self.shot = False
                self.ball_potted = False
                self.balls_to_cushion = 0
                #Reseting the first shot
                self.first_collision = None

            if self.turn_selection and not self.freeplay:
                pygame.mouse.set_pos(560, 359)
                pygame.mouse.set_visible(False)
                self.first_turn(player1_turn_hit, player2_turn_hit, balls_moving)

            if (not self.first_break or self.freeplay) and self.placing_white_ball and self.in_borders and not balls_moving:
                white_ball_rect = self.white_ball_image.get_rect(center=mouse_pos)
                screen.blit(self.white_ball_image, white_ball_rect)
            #at the whiteball placement, the white ball appears only in table's borders

            if self.holding_left_click:
                self.power, self.power_direction = self.adjust_power.adjust(self.power, self.power_direction)
            #while holding the left click, starts the power adjustment of the ball

            if cue_visible and not self.placing_white_ball:
                self.draw_shot_line.draw(white_pos, mouse_pos)
            #draw the white line

            if balls_moving or self.placing_white_ball:
                cue_visible = False  
                white_ball_movable = False  
                last_movement_time = time.time()  
            else:
                if time.time() - last_movement_time > 1:
                    cue_visible = True  
                    white_ball_movable = True  
            #after the balls stops moving, the cue is visible again, and player can play

            if self.gameover and not self.freeplay:
                date_time_score = datetime.now()
                score_date = date_time_score.strftime("%x")
                player1_score = self.player1_potted_balls - (0.25 * self.player1_fouls)
                player2_score = self.player2_potted_balls - (0.25 * self.player2_fouls)
                if self.winner == self.player1_name:
                    p1 = [score_date, self.player1_name, self.player1_potted_balls, self.player1_turns, self.player1_fouls, player1_score]
                    p2 = [self.player2_name, self.player2_potted_balls, self.player2_turns, self.player2_fouls, player2_score]
                else:
                    p1 = [self.player1_name, self.player1_potted_balls, self.player1_turns, self.player1_fouls, player1_score]
                    p2 = [score_date, self.player2_name, self.player2_potted_balls, self.player2_turns, self.player2_fouls, player2_score]
                self.player1.extend(p1)
                self.player2.extend(p2)
                gameover_screen = Gameover(self.screen, self.winner, self.game, self.menu, 'nineball', self.player1, self.player2, self.sounds)
                if gameover_screen.display() == 'menu':
                    return
            #checks for gameover


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

                if self.player1_turn or self.player2_turn and (self.pushout_steps in [0, 2, 4]):
                    if event.type == pygame.MOUSEBUTTONDOWN and white_ball_movable:
                        if event.button == 1:  # Left click press
                            self.holding_left_click = True
                            # Start adjusting power when left click

                    if event.type == pygame.MOUSEBUTTONUP and white_ball_movable:
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
                                if self.pushout_decision == True and self.pushout_steps == 2:
                                    self.pushout_shot = True
                                    self.pushout_steps = 3
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

                if self.pushout_after_break and not self.freeplay:
                    if self.pushout_decision is None and self.pushout_steps == 1:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                self.pushout_decision = True
                                self.pushout_steps = 2
                            elif event.key == pygame.K_2:
                                self.pushout_decision = False
                                self.pushout_steps = 4
                    elif self.pushout_accept is None and self.pushout_steps == 3:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                self.pushout_accept = True
                                self.pushout_steps = 4
                            elif event.key == pygame.K_2:
                                self.pushout_accept = False
                                self.pushout_steps = 4
                                self.player1_turn = not self.player1_turn
                                self.player2_turn = not self.player2_turn

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