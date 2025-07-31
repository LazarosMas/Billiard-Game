import pygame
import math
import pymunk
import pymunk.pygame_util
import time
import sys
import json
from datetime import datetime
from common_classes import Ball, Gameover, Define_borders, Setup_collisions_french, Draw_cue, Draw_power_bar, Adjust_power, Draw_shot_line, Are_balls_moving, Game_pause, Screen_message
pygame.init()

class French:
    def __init__(self, screen, frame_clock, freeplay, game, menu):
        self.screen_size = (1280, 720)
        self.table_size = (1052, 608)
        self.screen = screen
        self.frame_clock = frame_clock
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
            self.table_surface = pygame.image.load("Pictures/Green_Table_french.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)
        elif self.options[1] == 'red':
            self.table_surface = pygame.image.load("Pictures/Red_Table_french.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)
        else:
            self.table_surface = pygame.image.load("Pictures/Blue_Table_french.png").convert_alpha()
            self.table_surface = pygame.transform.smoothscale(self.table_surface, self.table_size)

        self.player1_name = self.options[2]
        self.player2_name = self.options[3]

        self.ball_hit_s = pygame.mixer.Sound('Sounds/Ball_hit.mp3')
        self.ball_to_ball = pygame.mixer.Sound('Sounds/ball_to_ball.mp3')
        pygame.mixer.music.load('Sounds/background_music.mp3') 
        if self.sounds and not pygame.mixer.music.get_busy(): 
            pygame.mixer.music.play(-1)

        self.message_font1 = pygame.font.Font('ghostclan.ttf', 50)
        self.message_font2 = pygame.font.Font('ghostclan.ttf', 40)
        self.message_font3 = pygame.font.Font('ghostclan.ttf', 20)
        self.message_font4 = pygame.font.Font('ghostclan.ttf', 25)

        self.player1_turns = 0
        self.player2_turns = 0
        self.player1_points = 0
        self.player2_points = 0
        self.player1 = []
        self.player2 = []

        self.white_ball = None
        self.yellow_ball = None
        self.red_ball = None

        self.game_pause = Game_pause(self.screen, self.game, self.menu, self.sounds)
        self.space = pymunk.Space()
        self.space.gravity = (0, 0) 
        self.define_borders = Define_borders(self.space, 'french')
        self.define_borders.borders()
        self.setup_collisions = Setup_collisions_french(self.space, self.ball_to_ball_collision)
        self.are_balls_moving = Are_balls_moving()
        self.power_direction = 1
        self.power = 0
        self.max_power = 1100
        self.draw_power_bar = Draw_power_bar(self.screen, self.screen_size, self.max_power)
        self.adjust_power = Adjust_power(self.max_power)
        self.draw_shot_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball) 
        self.freeplay = freeplay

        self.balls = []
        self.setup_balls()

        self.turn_selection = True
        self.player1_distance = None
        self.player2_distance = None
        self.player1_turn = True
        self.player2_turn = False

        self.ball_shot = False

        self.first_contact = None
        self.second_contact = None
        self.game_screen(frame_clock)


    def screen_message(self, screen, mes_pos):
        if not self.freeplay:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(500, 7, 490, 50))
            Screen_message(self.message_font1, "French Billiard", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 340, 177, 25))
            if self.player1_turn:
                Screen_message(self.message_font3, f"{self.player1_name}'s turn", (3, 352), (128, 128, 128), align="midleft").draw(self.screen)
            else: Screen_message(self.message_font3, f"{self.player2_name}'s turn", (3, 352), (128, 128, 128), align="midleft").draw(self.screen)

            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 60, 220, 35))
            Screen_message(self.message_font2, self.player1_name, (10, 75), (255, 255, 255), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 180, 220, 35))
            Screen_message(self.message_font2, self.player2_name, (10, 195), (255, 255, 255), align="midleft").draw(self.screen)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, 300, 220, 35))
            Screen_message(self.message_font4, "Game message", (3, 316), (212, 45, 45), align="midleft").draw(self.screen)
            
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 100, 150, 25))
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 220, 150, 25))
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 130, 165, 25))
            pygame.draw.rect(screen, (191, 190, 184), pygame.Rect(0, 250, 165, 25))
            Screen_message(self.message_font4, f"Points: {self.player1_points}", (5, 112), (128, 128, 128), align="midleft").draw(self.screen)
            Screen_message(self.message_font4, f"Points: {self.player2_points}", (5, 232), (128, 128, 128), align="midleft").draw(self.screen)
            
            if self.player1_turn:
                Screen_message(self.message_font4, f"{self.player1_name}'s turn", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)
            else:
                Screen_message(self.message_font4, f"{self.player2_name}'s turn", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)

        else:
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(560, 7, 350, 50))
            Screen_message(self.message_font1, "Freeplay", (750, 30), (255, 255, 255), align="center").draw(self.screen)
            Screen_message(self.message_font4, "Freeplay! No fouls are applied!", (mes_pos, 700), (128, 128, 128), align="midleft").draw(self.screen)

    
    def setup_balls(self):
        white_pos = [538, 247]
        white_ball = Ball(white_pos, 12, 1, self.space, "Pictures/White.png", 'white')
        self.white_ball = white_ball
        self.balls.append(white_ball)

        yellow_pos = [538, 469]
        yellow_ball = Ball(yellow_pos, 12, 1, self.space, "Pictures/Yellow.png", 'yellow')
        self.yellow_ball = yellow_ball
        self.balls.append(yellow_ball)

        red_pos = [979, 359]
        red_ball = Ball(red_pos, 12, 1, self.space, "Pictures/Red.png", 'red')
        self.red_ball = red_ball
        self.balls.append(red_ball)

        
    def draw_balls(self, screen):
        for ball in self.balls:
            ball.draw(screen)


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

        if self.second_contact is not None:
            return True
        if self.player1_turn:
            player_ball = self.white_ball.shape
            other_ball1 = self.balls[1].shape 
            other_ball2 = self.balls[2].shape 
        else:
            player_ball = self.yellow_ball.shape
            other_ball1 = self.balls[0].shape 
            other_ball2 = self.balls[2].shape 

        if player_ball == ball_a:
            if self.first_contact is None:  
                if ball_b == other_ball1 or ball_b == other_ball2:
                    self.first_contact = ball_b
            else:
                if ball_b == other_ball1 or ball_b == other_ball2:
                    self.second_contact = ball_b
        elif player_ball == ball_b:
            if self.first_contact is None:  
                if ball_a == other_ball1 or ball_a == other_ball2:
                    self.first_contact = ball_b
            else:
                if ball_a == other_ball1 or ball_a == other_ball2:
                    self.second_contact = ball_b
        return True
    

    def hit_white_ball(self, direction_speed):
        if self.white_ball:
            if self.sounds: 
                self.ball_hit_s.play()
            self.balls[0].body.apply_impulse_at_world_point(direction_speed, self.balls[0].body.position)
            self.ball_shot = True


    def hit_yellow_ball(self, direction_speed):
        if self.yellow_ball:
            if self.sounds:   
                self.ball_hit_s.play()
            self.balls[1].body.apply_impulse_at_world_point(direction_speed, self.balls[1].body.position)
            self.ball_shot = True


    def change_turn(self):
        if self.first_contact and self.second_contact and self.first_contact != self.second_contact:
            if self.player1_turn:
                self.player1_points += 1
            else:
                self.player2_points += 1
        else:
            self.player1_turn = not self.player1_turn
            self.player2_turn = not self.player2_turn

        self.first_contact = None
        self.second_contact = None


    def remove_ball(self, ball_shape):
        if ball_shape in self.space.shapes:
            self.space.remove(ball_shape, ball_shape.body)
        #remove the ball from pymunk's space

        self.balls = [ball for ball in self.balls if ball.shape != ball_shape]
        #remove the ball from the balls list


    def first_turn(self, p1, p2, balls_moving):
        if not self.freeplay:
            if self.player1_turn and not p1:
                pygame.mouse.set_pos(600, 247)
            elif self.player2_turn and not p2:
                pygame.mouse.set_pos(600, 469)
            if p1 and p2 and not balls_moving:
                white_pos = self.balls[0].body.position
                yellow_pos = self.balls[1].body.position
                if white_pos[0] <= yellow_pos[0]:
                    self.player1_turn = True
                    self.player2_turn = False
                else:
                    self.player2_turn = True
                    self.player1_turn = False
                self.turn_selection = False
                for i in range (0, 3):
                    self.remove_ball(self.balls[0].shape)
                self.setup_balls()
                self.draw_player1_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball)
                self.draw_player2_line = Draw_shot_line(self.screen, self.space, self.table_size, self.yellow_ball)
            #bug fix
    #func for defining who gets to play first


    def game_screen(self, frame_clock):
        mouse_visible = True
        cue_visible = True
        ball_movable = True
        holding_left_click = False
        mes_pos = 1280
        game_paused = False
        draw_cue = Draw_cue(self.screen)
        self.draw_player1_line = Draw_shot_line(self.screen, self.space, self.table_size, self.white_ball)
        self.draw_player2_line = Draw_shot_line(self.screen, self.space, self.table_size, self.yellow_ball)
        
        last_movement_time = time.time() - 1  # A slight delay 
        x = 0.0
        dt = 1/60.0  # Fixed time step

        player1_turn_hit = False
        player2_turn_hit = False

        while self.game:
            frame_time = frame_clock.tick(60) / 1000.0  # Convert to seconds
            x += frame_time
            while x >= dt:
                self.space.step(dt)
                x -= dt
            pygame.time.get_ticks()
            self.screen.blit(self.gameback_surface, (0, 0))
            self.screen.blit(self.table_surface, (232,56))
            
            mes_pos -= 2
            if mes_pos < -500: mes_pos = 1280

            self.screen_message(self.screen, mes_pos)
            self.draw_balls(self.screen)
            self.draw_power_bar.draw_power(self.power)


            mouse_pos = pygame.mouse.get_pos()
            white_pos = self.balls[0].body.position
            yellow_pos = self.balls[1].body.position
            if (315 <= mouse_pos[0] <= 1200) and (136 <= mouse_pos[1] <= 580):
                if mouse_visible:
                    pygame.mouse.set_visible(False)
                    mouse_visible = False
            else:
                if not mouse_visible:
                    pygame.mouse.set_visible(True)
                    mouse_visible = True
            #as long as mouse is within table's borders, it's invincible


            balls_moving = self.are_balls_moving.check_french(self.balls)
            if not balls_moving:
                if self.player1_points == 50:
                    date_time_score = datetime.now()
                    score_date = date_time_score.strftime("%x")
                    p1 = [score_date, self.player1_name, self.player1_turns, self.player1_points]
                    p2 = [self.player2_name, self.player2_turns, self.player2_points]
                    self.player1.extend(p1)
                    self.player2.extend(p2)
                    self.game = False
                elif self.player2_points == 50:
                    date_time_score = datetime.now()
                    score_date = date_time_score.strftime("%x")
                    p1 = [self.player1_name, self.player1_turns, self.player1_points]
                    p2 = [score_date, self.player2_name, self.player2_turns, self.player2_points]
                    self.player1.extend(p1)
                    self.player2.extend(p2)
                    self.game = False
                cue_visible = True
                ball_movable = True
                if self.ball_shot:
                    self.change_turn()
                    self.ball_shot = False
                if self.player1_turn or self.freeplay:
                    draw_cue.draw_c(white_pos, mouse_pos, cue_visible)
                    self.draw_player1_line.draw(white_pos, mouse_pos)
                else:
                    draw_cue.draw_c(yellow_pos, mouse_pos, cue_visible)
                    self.draw_player2_line.draw(yellow_pos, mouse_pos)
            else:
                cue_visible = False
                ball_movable = False
            
            if holding_left_click:
                self.power, self.power_direction = self.adjust_power.adjust(self.power, self.power_direction)

            if self.turn_selection:
                self.first_turn(player1_turn_hit, player2_turn_hit, balls_moving)

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
                
                if event.type == pygame.MOUSEBUTTONDOWN and ball_movable:
                    if event.button == 1:  # Left click press
                        holding_left_click = True
                        # Start adjusting power when left click
                if event.type == pygame.MOUSEBUTTONUP and ball_movable:
                    if event.button == 1:
                        # Release the left click and apply the impulse
                        holding_left_click = False
                        click_pos = pymunk.Vec2d(mouse_pos[0], mouse_pos[1]) 
                        white_pos = self.balls[0].body.position
                        if self.player1_turn or self.freeplay:
                            direction = click_pos - white_pos
                        else:
                            direction = click_pos - yellow_pos
                        distance = direction.length
                        # Calculate direction from white ball to mouse release position
                        if distance > 0:
                            direction = direction.normalized()
                            speed = self.power 
                            direction_speed = direction * speed
                            if self.player1_turn or self.freeplay:
                                self.hit_white_ball(direction_speed)
                                self.player1_turns += 1
                                if self.turn_selection:
                                    player1_turn_hit = True
                            else:
                                self.hit_yellow_ball(direction_speed)
                                self.player2_turns += 1
                                if self.turn_selection:
                                    player2_turn_hit = True
                            self.shot = True
                            #Calculate the power to hit the white ball
                        self.power = 0
                        self.power_direction = 1 
                        # Reset the power after the hit
                    if event.button == 3:  # Right click
                        holding_left_click = False
                        # Cancel the power adjustment
                        self.power = 0
                        self.power_direction = 1
            pygame.display.update()


        if self.player1_points >= 50:
            winner = self.player1_name
            gameover_screen = Gameover(self.screen, winner, self.game, self.menu, 'french', self.player1, self.player2, self.sounds)
            if gameover_screen.display() == 'menu':
                return
        elif self.player2_points >= 50: 
            winner = self.player2_name
            gameover_screen = Gameover(self.screen, winner, self.game, self.menu, 'french', self.player1, self.player2, self.sounds)
            if gameover_screen.display() == 'menu':
                return