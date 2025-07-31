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

class Snooker:
    def __init__(self, screen, frame_clock, freeplay, game, menu):
        self.screen_size = (1280, 720)
        self.table_size = (1052, 608)
        self.screen = screen
        self.frame_clock = frame_clock
        self.freeplay = freeplay
        self.game = game
        self.menu = menu
        
        self.gameback_surface = pygame.image.load("Pictures/Background.png").convert_alpha()
        self.gameback_surface = pygame.transform.smoothscale(self.gameback_surface, self.screen_size)

        with open('saves/options_data.json', 'r') as file:
            self.options = json.load(file)

        if self.options[0] == 'enabled':
            self.sounds = True
        else:
            self.sounds = False

        if self.options[1] == 'green':
            self.table_surface = pygame.image.load("Pictures/Green_Table_Snooker.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)
        elif self.options[1] == 'red':
            self.table_surface = pygame.image.load("Pictures/Red_Table_Snooker.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)
        else:
            self.table_surface = pygame.image.load("Pictures/Blue_Table_Snooker.png").convert_alpha()
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

        self.player1_turn = True
        self.player2_turn = False
        self.to_change_turn = True


        self.player1_turns = 0
        self.player2_turns = 0
        self.player1_points = 0
        self.player2_points = 0
        self.player1_potted_balls = 0
        self.player2_potted_balls = 0
        self.player1_fouls = 0
        self.player2_fouls = 0
        self.player1 = []
        self.player2 = []
        self.winner = None
        self.gameover = False
        #Game over variables

        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  #there's no gravity

        self.gameover_setup = Gameover(self.screen, self.winner, self.game, self.menu, 'snooker', self.player1, self.player2, self.sounds)


        self.foul = False
        self.white_in_hole_foul = False
        self.foul_message = False
        self.message_1 = False
        self.message_2 = False
        self.message_num = False
        self.points_message = False

        self.pot_reds = True
        self.pot_balls = False
        #Variables to control which ball to hit

        
        self.placing_white_ball = False
        self.black_in_play = True
        self.r_ball = None

        
        self.first_collision = None
        
        self.reds = []
        self.balls = []
        self.balls_points = [2, 3, 4, 5, 6, 7]
        self.balls_pos = [(538, 455), (538, 270), (538, 359), (758, 359), (905, 359), (1100, 359)]   
        self.not_first_touch = True
        self.balls_stable = True
        self.shot = False
        self.are_balls_moving = Are_balls_moving()
        self.setup_balls()

        self.power = 0  # Initial power value
        self.max_power = 1100  # Maximum power
        self.power_direction = 1  # Power growth direction (1 = increasing, -1 = decreasing)
        self.holding_left_click = False  # Whether the player is holding the left click
        self.draw_power_bar = Draw_power_bar(self.screen, self.screen_size, self.max_power)
        self.adjust_power = Adjust_power(self.max_power)
        self.draw_shot_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball) 
        
        self.game_pause = Game_pause(self.screen, self.game, self.menu, self.sounds)
        
        
        self.potted_ball = None
        self.pot_number = None
        self.wrong_pot = False
        self.in_borders = False

        self.define_borders = Define_borders(self.space, 'snooker')
        self.define_borders.borders()
        self.define_holes = Define_hole_collisions(self.space)
        self.define_holes.define()

        self.setup_collisions = Setup_collisions(self.space, self.not_first_touch, self.handle_ball_hole_collision, self.ball_to_ball_collision)
        self.setup_collisions.collisions()


        self.game_screen(self.screen, self.frame_clock)
        
    

    def setup_balls(self):
        white_pos = [500, 300]
        reds_pos = [(935, 359), (957, 347), (979, 384), (1001, 321), (1001, 371), (1023, 408), (1023, 333), 
                    (979, 359), (957, 372), (979, 334), (1001, 396), (1001, 346), (1023, 308), (1023, 358), (1023, 383)]
        white_ball = Ball(white_pos, 12, 1, self.space, "Pictures/White.png", 'white')
        self.white_ball = white_ball
        self.balls.append(white_ball)

        for i in reds_pos:
            self.reds.append(Ball(i, 12, 1, self.space, f"Pictures/Snooker/1.png", 'red'))
        for i, pos in enumerate(self.balls_pos):
            self.balls.append(Ball(pos, 12, 1, self.space, f"Pictures/Snooker/{i+2}.png", f"{i+2}"))

    
    def draw_balls(self, screen):
        for ball in self.balls:
            ball.draw(screen)
        for red in self.reds:
            red.draw(screen)


    def handle_ball_hole_collision(self, arbiter, space, data):
        ball_shape = arbiter.shapes[0]  
        potted_ball = None
        r_ball = False

        if ball_shape == self.white_ball.shape:
            self.white_in_hole_foul = True
            self.foul_message = True
            self.placing_white_ball = True
            if self.player1_turn:
                self.player1_fouls += 1
            else:
                self.player2_fouls += 1  
        else:
            if len(self.reds) > 0: #if there are reds in play
                for r in self.reds:
                    if r.shape == ball_shape:
                        potted_ball = r
                        r_ball = True
                        if self.pot_reds and not self.foul:
                            self.points_message = True
                            if self.player1_turn:
                                self.player1_points += 1
                                self.player1_potted_balls +=1
                            else:
                                self.player2_points += 1
                                self.player2_potted_balls += 1
                            self.to_change_turn = False
                        else:
                            if self.player1_turn:
                                self.player2_points += 4
                                self.player1_fouls += 1
                            else:
                                self.player1_points +=4
                                self.player2_fouls += 1
                        break
            if not r_ball: #if a red wasn't potted
                for i, b in enumerate(self.balls):
                    if b.shape == ball_shape:
                        potted_ball = b
                        self.potted_ball = i
                        if len(self.reds) > 0:
                            if self.pot_balls and not self.foul:
                                if self.player1_turn:
                                    self.player1_points += int(potted_ball.ball_type)
                                    self.player1_potted_balls += 1
                                else:
                                    self.player2_points += int(potted_ball.ball_type)
                                    self.player2_potted_balls += 1
                                self.to_change_turn = False
                            else:
                                if int(potted_ball.ball_type) <= 4:
                                    if self.player1_turn:
                                        self.player2_points += 4
                                        self.player1_fouls += 1
                                    else:
                                        self.player1_points += 4
                                        self.player2_fouls += 1
                                else:
                                    if self.player1_turn:
                                        self.player2_points += int(potted_ball.ball_type)
                                        self.player1_fouls += 1
                                    else:
                                        self.player1_points += int(potted_ball.ball_type)
                                        self.player2_fouls += 1
                        else:
                            if self.balls[1].ball_type == potted_ball.ball_type and not self.foul:
                                if self.player1_turn:
                                    self.player1_points += int(potted_ball.ball_type)
                                    self.player1_potted_balls += 1
                                else:
                                    self.player2_points += int(potted_ball.ball_type)
                                    self.player2_potted_balls += 1
                            else:
                                if self.player2_turn:
                                    self.player1_points += int(potted_ball.ball_type)
                                    self.player2_fouls += 1
                                else:
                                    self.player2_points += int(potted_ball.ball_type)
                                    self.player1_fouls += 1
                            if int(potted_ball.ball_type) == 7:
                                self.black_in_play = False
                        break

        if self.sounds:     
            self.ball_in_s.play()
        self.remove_ball(ball_shape)
#call the remove_ball func
        return False
    

    def remove_ball(self, ball_shape):
        if ball_shape in self.space.shapes:
            self.space.remove(ball_shape, ball_shape.body)
        #remove the ball from pymunk's space

        self.balls = [ball for ball in self.balls if ball.shape != ball_shape]
        self.reds = [ball for ball in self.reds if ball.shape != ball_shape]
        #remove the ball from the balls list


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
            for r in self.reds:
                if r.shape == ball_b:
                    self.r_ball = r.shape
                    self.first_collision = r.ball_type
                    break
            if self.r_ball is None:
                for b in self.balls:
                    if b.shape == ball_b:
                        self.first_collision = b.ball_type
                        break
        elif ball_b == self.white_ball.shape:
            self.not_first_touch = False
            for r in self.reds: 
                if r.shape == ball_a:
                    self.r_ball = r.shape
                    self.first_collision = r.ball_type
                    break
            if self.r_ball is None:
                for b in self.balls:
                    if b.shape == ball_a:
                        self.first_collision = b.ball_type
                        break
#Checking which ball type (solid, stripe or black) the white ball hit first
        return True


    def hit_white_ball(self, direction_speed):
        if self.sounds: 
            self.ball_hit_s.play()
        self.balls[0].body.apply_impulse_at_world_point(direction_speed, self.balls[0].body.position)
    #Hit the white ball towards a target


    def check_for_foul(self):
        if self.shot:
            if self.first_collision is None:
            # No collision occurred; it's a foul
                self.foul = True
                self.foul_message = True
                if self.player1_turn:
                    self.player1_fouls += 1
                else:
                     self.player2_fouls += 1
            elif len(self.reds) > 0:
                if self.first_collision != 'red' and self.pot_reds:
                    self.foul = True
                    self.foul_message = True
                    self.message_1 = True
                    if self.player1_turn:
                        self.player1_fouls += 1
                    else:
                        self.player2_fouls += 1
                elif self.first_collision == 'red' and self.pot_balls:
                    self.foul = True
                    self.foul_message = True
                    self.message_2 = True
                    if self.player1_turn:
                        self.player1_fouls += 1
                    else:
                        self.player2_fouls += 1
            elif len(self.reds) == 0:
                if self.first_collision !='red': #bug fix
                    if int(self.first_collision) != int(self.pot_number):
                        self.foul = True
                        self.foul_message = True
                        self.message_num = True
                        if self.player1_turn:
                            self.player1_fouls += 1
                        else:
                            self.player2_fouls += 1
        self.ball_changed = False


    def change_turn(self):
        self.foul_points()
        if self.to_change_turn or self.foul or self.white_in_hole_foul:
            self.player1_turn = not self.player1_turn
            self.player2_turn = not self.player2_turn
            if len(self.reds) > 0:
                self.pot_reds = True
                self.pot_balls = False
        elif len(self.reds) > 0:
            self.pot_reds = not self.pot_reds
            self.pot_balls = not self.pot_balls
        elif len(self.reds) == 0: 
            self.pot_reds = False
            self.pot_balls = True
        self.to_change_turn = True
        self.wrong_pot = False


    def foul_points(self):
        if self.player1_turn: 
            if self.white_in_hole_foul:
                self.player2_points += 4
            if self.first_collision is None:
                self.player2_points += 4
            elif self.pot_reds and self.first_collision != 'red':
                self.player2_points += 4
            elif self.pot_balls and self.first_collision == 'red':
                self.player2_points += 4
            elif self.pot_number:
                if int(self.first_collision) != int(self.pot_number):  
                    self.player2_points += 4

        elif self.player2_turn:
            if self.white_in_hole_foul:
                self.player1_points += 4
            if self.first_collision is None:
                self.player1_points += 4
            elif self.pot_reds and self.first_collision != 'red':
                self.player1_points += 4
            elif self.pot_balls and self.first_collision == 'red':
                self.player1_points += 4 
            elif self.pot_number:
                if int(self.first_collision) != int(self.pot_number):  
                    self.player1_points += 4
    #func for giving foul points

    def screen_message(self, screen, mes_pos):
        if not self.freeplay:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "SNOOKER", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 340, 177, 25))
            if self.player1_turn:
                Screen_message(self.message_font3, f"{self.options[2]}'s turn", (3, 352), (128, 128, 128), align="midleft").draw(self.screen)
            else: Screen_message(self.message_font3, f"{self.options[3]}'s turn", (3, 352), (128, 128, 128), align="midleft").draw(self.screen)

            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 60, 220, 35))
            Screen_message(self.message_font2, self.options[2], (10, 75), (255, 255, 255), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 220, 35))
            Screen_message(self.message_font2, self.options[3], (10, 195), (255, 255, 255), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 300, 220, 35))
            Screen_message(self.message_font4, "Game message", (3, 316), (212, 45, 45), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 100, 160, 25))
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 220, 160, 25))
            Screen_message(self.message_font4, "POINTS:", (5, 112), (128, 128, 128), align="midleft").draw(self.screen)
            Screen_message(self.message_font4, "POINTS:", (5, 232), (128, 128, 128), align="midleft").draw(self.screen)
            
            if self.pot_reds:
                Screen_message(self.message_font4, "TIME FOR RED BALL", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            else:
                Screen_message(self.message_font4, "TIME FOR COLORED BALL", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            
        else:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "Freeplay", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            Screen_message(self.message_font4, "Freeplay! No fouls are applied!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
        

    def game_screen(self, screen, frame_clock):
        cue_visible = True #bool to check if cue should be visible
        white_ball_movable = True #bool to check if player can hit the white ball
        last_movement_time = time.time() - 1  # A slight delay 
        x = 0.0
        dt = 1/60.0  # Fixed time step

        mouse_visible = True 
        draw_cue = Draw_cue(self.screen) #call to draw the cue
        mes_pos = 1280
        game_paused = False
        white_ball_image = pygame.image.load("Pictures/White.png").convert_alpha()
        white_ball_image = pygame.transform.smoothscale(white_ball_image, (24, 24))  # Diameter=12*2
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

            mouse_pos = pygame.mouse.get_pos()
            if (315 <= mouse_pos[0] <= 1200) and (136 <= mouse_pos[1] <= 580) and not game_paused:
                if mouse_visible:
                    pygame.mouse.set_visible(False)
                    mouse_visible = False
            else:
                if not mouse_visible:
                    pygame.mouse.set_visible(True)
                    mouse_visible = True
            #as long as mouse is within table's borders, it's invincible


            if not self.placing_white_ball:
                white_pos = self.balls[0].body.position  
            draw_cue.draw_c(white_pos, mouse_pos, cue_visible)
            #take the position of white ball and use it to draw the cue

            self.draw_power_bar.draw_power(self.power)

            mes_pos -= 2
            if mes_pos < -500: mes_pos = 1280
            #makes a moving message
            self.screen_message(self.screen, mes_pos)

            if cue_visible and not self.placing_white_ball:
                self.draw_shot_line.draw(white_pos, mouse_pos)
            #draw the white line

            if self.holding_left_click:
                self.power, self.power_direction = self.adjust_power.adjust(self.power, self.power_direction)
            #while holding the left click, starts the power adjustment of the ball 

            balls_moving = self.are_balls_moving.check_snooker(self.reds, self.balls, self.balls_stable, self.check_for_foul, self.not_first_touch)
            # Check if any ball is moving
            

            if self.placing_white_ball and self.in_borders and not balls_moving:
                white_ball_rect = white_ball_image.get_rect(center=mouse_pos)
                screen.blit(white_ball_image, white_ball_rect)
            #at the whiteball placement, the white ball appears only in table's borders

            
            if balls_moving or self.placing_white_ball:
                cue_visible = False  
                white_ball_movable = False  
                last_movement_time = time.time()  
            else:
                if time.time() - last_movement_time > 1:
                    cue_visible = True  
                    white_ball_movable = True  
            #after the balls stops moving, the cue is visible again, and player can play


            if not balls_moving and self.shot: #if the player shot the ball and balls stopped moving
                if not self.freeplay:
                    if not self.freeplay and not self.black_in_play: 
                        date_time_score = datetime.now()
                        score_date = date_time_score.strftime("%x")                      
                        if self.player1_points > self.player2_points:
                            self.winner = self.player1_name
                            p1 = [score_date, self.player1_name, self.player1_potted_balls, self.player1_turns, self.player1_fouls, self.player1_points]
                            p2 = [self.player2_name, self.player2_potted_balls, self.player2_turns, self.player2_fouls, self.player2_points]
                        else:
                            self.winner = self.player2_name
                            p1 = [self.player1_name, self.player1_potted_balls, self.player1_turns, self.player1_fouls, self.player1_points]
                            p2 = [score_date, self.player2_name, self.player2_potted_balls, self.player2_turns, self.player2_fouls, self.player2_points]
                        self.player1.extend(p1)
                        self.player2.extend(p2)
                        pygame.mixer.music.stop()
                        gameover_screen = Gameover(self.screen, self.winner, self.game, self.menu, "snooker", self.player1, self.player2, self.sounds)
                        if gameover_screen.display() == 'menu':
                            return
                    if self.white_in_hole_foul:
                        if self.white_ball.shape in self.space.shapes:
                            self.space.remove(self.white_ball.shape, self.white_ball.body)
                            self.balls = [ball for ball in self.balls if ball.shape != self.white_ball.shape]
                        self.placing_white_ball = True
                        #When the balls stops moving, if there is a foul, the next player places the ball
                    self.change_turn()
                    if len(self.reds) == 0:
                        self.pot_number = 10
                        for b in self.balls:
                            if b.ball_type == 'white':
                                pass
                            elif int(b.ball_type) < int(self.pot_number):
                                self.pot_number = b.ball_type

                    self.foul = False 
                self.shot = False
                self.first_collision = None
                self.r_ball = None

                if self.potted_ball is not None and len(self.reds) > 0:
                    pos = self.balls_pos[self.potted_ball - 1]
                    returned_ball = Ball(pos, 12, 1, self.space, f"Pictures/Snooker/{self.potted_ball+1}.png", f"{self.potted_ball+1}")
                    self.balls.insert(self.potted_ball, returned_ball)
                    self.potted_ball = None


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
                    center_d = pymunk.Vec2d(535, 362)  # Center of the "D"
                    radius_d = 95  # Radius of the "D"
                    
                    if (mouse_pos - center_d).length <= radius_d and mouse_pos[0] <= 537:
                        # Ensure mouse is within the "D" and below the baulk line
                        pygame.mouse.set_visible(False)
                        self.in_borders = True
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            overlap = False
                            overlap1 = False
                            for ball in self.balls:
                                distance = (pymunk.Vec2d(ball.body.position[0], ball.body.position[1]) - mouse_pos).length
                                if distance < (ball.shape.radius + 12):  # 12 is the radius of the balls
                                    overlap = True
                                    break
                            for ball in self.reds:
                                distance = (pymunk.Vec2d(ball.body.position[0], ball.body.position[1]) - mouse_pos).length
                                if distance < (ball.shape.radius + 12):  # 12 is the radius of the balls
                                    overlap1 = True
                                    break
                            #checks at the ball placement if the mouse, aka white ball overlaps with the other balls
                            if not overlap and not overlap1:
                                new_white_ball = Ball((mouse_pos[0], mouse_pos[1]), 12, 1, self.space, "Pictures/White.png", 'white')
                                self.white_ball = new_white_ball  
                                self.balls.insert(0, new_white_ball)

                                self.draw_shot_line.white_ball = self.white_ball
                            #places the new white ball
                                self.foul_message = False
                                self.placing_white_ball = False
                                self.white_in_hole_foul = False  #bug
                                self.foul = False
                    else:
                        self.in_borders = False 
                        pygame.mouse.set_visible(True)


            pygame.display.update()