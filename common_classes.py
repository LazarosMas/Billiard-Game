import pygame
import math
import pymunk
import pymunk.pygame_util
import time
import sys
import json
from datetime import datetime

class Ball:
    def __init__(self, position, radius, mass, space, image, ball_type):
        self.image = pygame.image.load(image).convert_alpha()
        self.diameter = radius * 2
        self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
        self.ball_type = ball_type
        # Create the ball body in Pymunk
        self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        self.body.position = position
        self.body.damping = 0.5 # This will slow down the ball over time

        static_body = space.static_body
        pivot = pymunk.PivotJoint(static_body, self.body, (0, 0),(0, 0))
        pivot.max_bias = 0 
        pivot.max_force = 85 # emulate linear friction

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9  # Increase friction to reduce sliding
        self.shape.collision_type = 1 # Assign collision type for balls
        space.add(self.body, self.shape, pivot)

    def draw(self, screen):
        ball_pos = self.body.position
        ball_rect = self.image.get_rect(center=(int(ball_pos.x), int(ball_pos.y)))
        screen.blit(self.image, ball_rect)
#Class for creating ball objects 


class Define_borders:
        def __init__(self, space, table_type):
            self.space = space
            self.borders_segments = []   
            
            if table_type != 'french':
                self.static_borders = [
                    [(349, 136), (724, 136)],  # Top left border
                    [(725, 136), (738, 106)],
                    [(792, 136), (778, 106)],
                    [(792, 136), (1165, 136)], #Top Right border
                    [(349, 136), (319, 106)],
                    [(315, 176), (285, 146)], 
                    [(315, 176), (315, 543)],  # Left border
                    [(315, 543), (285, 573)],
                    [(352, 580), (322, 610)],
                    [(352, 580), (723, 580)],  # Bottom left border
                    [(724, 580), (738, 610)], 
                    [(793, 580), (779, 610)], 
                    [(794, 580), (1164, 580)],  #Bottom Right border
                    [(1164, 580), (1194, 610)],
                    [(1200, 543), (1230, 573)],
                    [(1200, 177), (1200, 543)],  # Right border
                    [(1200, 177), (1230, 147)],
                    [(1165, 136), (1197, 106)]
                ]
            else:
                self.static_borders = [
                    [(312, 134), (1203, 134)], #Top Border
                    [(312, 134), (312, 584)], #Left Border
                    [(312, 584), (1203, 584)], #Bottom Border
                    [(1203, 134), (1203, 584)] # Right Border
                ]
        def borders(self):
            # Add borders as static lines in pymunk
            for border in self.static_borders:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                shape = pymunk.Segment(body, border[0], border[1], 1)  # 1 is the thickness of the line
                shape.elasticity = 0.8
                shape.friction = 0.5
                shape.collision_type = 3  # Assign a new collision type for borders
                self.space.add(body, shape)
                # Store the border segments as Vec2d objects for intersection calculations
                self.borders_segments.append((pymunk.Vec2d(*border[0]), pymunk.Vec2d(*border[1])))
#Class for setting table's borders


class Define_hole_collisions:
        def __init__(self, space):
            self.space = space
            self.hole_positions = [(303, 124), (758, 104), (1213, 124), (303, 593), (758, 614), (1213, 593)] 
            self.hole_radius = 24
        def define(self):
            for hole in self.hole_positions:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)  # Static body 
                body.position = hole
                shape = pymunk.Circle(body, self.hole_radius)
                shape.sensor = True  # Set shape as a sensor
                shape.collision_type = 2  # Set collision type to 2 for holes
                self.space.add(body, shape)
            return self.hole_positions
#Class for setting holes for the table


class Are_balls_moving:
    def __init__(self):
        self.threshold = 0.01
    
    def check(self, balls, balls_stable, check_for_foul, not_fist_touch):
        for ball in balls:
            if ball.body.velocity.length > self.threshold:
                balls_stable = False
                return True
        check_for_foul()
        not_first_touch = True
        balls_stable = True
        return False

    def check_snooker(self, reds, balls, balls_stable, check_for_foul, not_fist_touch):
        for ball in balls + reds:
            if ball.body.velocity.length > self.threshold:
                balls_stable = False
                return True
        check_for_foul()
        not_first_touch = True
        balls_stable = True
        return False

    def check_french(self, balls):
        for ball in balls:
            if ball.body.velocity.length > self.threshold:
                return True
        return False
#Class for checking for fouls and ball movement


class Setup_collisions:
    def __init__(self, space, not_first_touch, handle_ball_hole_collision, ball_to_ball_collision):
        self.space = space
        self.not_first_touch = not_first_touch
        self.handle_ball_hole_collision = handle_ball_hole_collision
        self.ball_to_ball_collision = ball_to_ball_collision
        # Set up collision handler for ball and hole collisions
        self.handler = self.space.add_collision_handler(1, 2)
        self.handler.begin = self.handle_ball_hole_collision

    def collisions(self):
        if self.not_first_touch:
            ball_ball_handler = self.space.add_collision_handler(1, 1)
            ball_ball_handler.begin = self.ball_to_ball_collision

    def cushions(self, ball_to_cushion):
        ball_cushion = self.space.add_collision_handler(1, 3)
        ball_cushion.begin = ball_to_cushion
#Class for controlling the collisions


class Setup_collisions_french:
    def __init__(self, space, ball_to_ball_collision):
        self.space = space
        self.ball_to_ball_collision = ball_to_ball_collision
        # Set up collision handler for ball and hole collisions
        ball_ball_handler = self.space.add_collision_handler(1, 1)
        ball_ball_handler.begin = self.ball_to_ball_collision
#Class for controlling the collisions for the french game


class Draw_cue:
    def __init__(self, screen):
        self.screen = screen
        self.cue_image_original = pygame.image.load("Pictures/Cue.png").convert_alpha()
        self.cue_image_original = pygame.transform.smoothscale(self.cue_image_original, (720, 500))  
    def draw_c(self, white_pos, mouse_pos, cue_visible):
        if not cue_visible:
            return
        cue = self.cue_image_original
        cue_angle = math.atan2(mouse_pos[1] - white_pos[1], mouse_pos[0] - white_pos[0])
        # Calculate the angle between the white ball and the mouse position
        cue_angle_degrees = math.degrees(cue_angle) 
        # Convert the angle from radians to degrees
        rotated_cue = pygame.transform.rotate(cue, -cue_angle_degrees)
        # Rotate the cue image around its center based on the calculated angle
        cue_length = cue.get_width()   
        offset_x = math.cos(cue_angle) * (cue_length //3)
        offset_y = math.sin(cue_angle) * (cue_length //3)
        # Calculate the new position for the cue
        cue_pos = (white_pos[0] - offset_x, white_pos[1] - offset_y)
        # Position the cue so its tip is looking at the white ball
        cue_rect = rotated_cue.get_rect(center=cue_pos)
        self.screen.blit(rotated_cue, cue_rect) 
#Class for drawing the cue


class Draw_power_bar():
    def __init__(self, screen, screen_size, max_power):
        self.screen = screen
        self.screen_size = screen_size
        self.max_power = max_power
        self.height = 200
        self.width = 20
    
    def draw_power(self, power):
        x = 50
        y =  450
        bar_height = int(power / self.max_power * self.height)
        pygame.draw.rect(self.screen, (255, 0, 0), (x, y + self.height - bar_height, self.width, bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, self.width, self.height), 2)
#Class for showing current power


class Adjust_power:
    def __init__(self, max_power):
        self.max_power = max_power

    def adjust(self, power, power_direction):
        power += power_direction * 10  # Increase or decrease power
        if power >= self.max_power or power <= 0:
            power_direction *= -1  # Reverse direction if max or min is reached
        return power, power_direction
#Class for adjusting the power
    

class Draw_shot_line:
    def __init__(self, screen, space, table_size, white_ball):
        self.screen = screen 
        self.space = space 
        self.table_width, self.table_height = table_size  
        self.white_ball = white_ball 
        self.max_distance = math.hypot(self.table_width, self.table_height)  # The longest possible shot distance

    def draw(self, white_pos, mouse_pos):
        white_ball_pos = pymunk.Vec2d(*white_pos)
        mouse_pos_vec = pymunk.Vec2d(*mouse_pos)

        direction = mouse_pos_vec - white_ball_pos
        if direction.length > 0:
            direction = direction.normalized()  # Make it a unit vector 
        else:
            direction = pymunk.Vec2d(0, 0)  # Avoid errors if the mouse is exactly on the ball

        end_pos = white_ball_pos + direction * self.max_distance
        # Extend the shot line to its maximum possible length

        possible_collisions = self.space.segment_query(white_ball_pos, end_pos, 4, pymunk.ShapeFilter())
        possible_collisions = sorted(possible_collisions, key=lambda col: col.alpha) 
        # Check for obstacles along the shot path

        collision_point = end_pos  
        for collision in possible_collisions:
            if collision.shape != self.white_ball.shape:  # Ignore self-collision
                collision_point = collision.point
                break

        start_point = (int(white_ball_pos.x), int(white_ball_pos.y))
        end_point = (int(collision_point.x), int(collision_point.y))

        pygame.draw.line(self.screen, (255, 255, 255), start_point, end_point, 2)

        impact_circle_radius = 10
        impact_position = pymunk.Vec2d(*end_point) - direction * impact_circle_radius
        impact_position_int = (int(impact_position.x), int(impact_position.y))
        pygame.draw.circle(self.screen, (123, 123, 123), impact_position_int, impact_circle_radius)


class Game_pause:
    def __init__(self, screen, game, menu, sounds):
        self.screen = screen
        self.game = game
        self.menu = menu
        self.sounds = sounds
        pause_font = pygame.font.Font('ghostclan.ttf', 50)
        buttons_font = pygame.font.Font('ghostclan.ttf', 35)
        self.bckgr = pygame.image.load("Pictures/pause.jpg").convert_alpha()
        self.bckgr = pygame.transform.smoothscale(self.bckgr, (1280, 1280)) 
        self.pause_text = pause_font.render("Paused", True, (255, 255, 255))
        self.pause_text_rec = self.pause_text.get_rect(center = (640, 200))
        self.continue_text = buttons_font.render("continue", True, (255, 255, 255))
        self.continue_text_rec = self.continue_text.get_rect(midleft = (50, 350))
        self.sound_button = buttons_font.render("SOUND:", True, (255, 255, 255))
        self.sound_button_rec = self.sound_button.get_rect(midleft = (50, 450))
        self.exit = buttons_font.render("To main menu", True, (255, 255, 255))
        self.exit_rec = self.exit.get_rect(center = (1100, 670))
        self.sound_enable = buttons_font.render("ENABLED", True, (50, 255, 50))
        self.sound_enable_rec = self.sound_enable.get_rect(midleft = (200, 450))
        self.sound_disable = buttons_font.render("DISABLED", True, (255, 50, 50))
        self.sound_disable_rec = self.sound_disable.get_rect(midleft = (200, 450))
        self.main_menu = False
        self.mainq = pause_font.render("Do you want to abandon the match,", True, (255, 255, 255))
        self.mainq_rec = self.mainq.get_rect(center = (640, 200))
        self.mainq1 = pause_font.render("And go to main menu?", True, (255, 255, 255))
        self.mainq1_rec = self.mainq1.get_rect(center = (640, 250))
        self.yes = pause_font.render("YES", True, (255, 50, 50))
        self.yes_rec = self.yes.get_rect(center = (500, 450))
        self.no = pause_font.render("NO", True, (50, 255, 50))
        self.no_rec = self.no.get_rect(center = (780, 450))
        self.button_sel = pygame.mixer.Sound("Sounds/button_select.ogg")
        with open('saves/options_data.json', 'r') as file:
            self.options = json.load(file)

    def p(self, game_paused):
        game_paused = True
        pygame.mouse.set_visible(True)
        while game_paused:
            self.screen.blit(self.bckgr, (0, 0))
            if not self.main_menu:
                mouse_pos = pygame.mouse.get_pos()
                self.screen.blit(self.pause_text, self.pause_text_rec)
                self.screen.blit(self.continue_text, self.continue_text_rec)
                self.screen.blit(self.sound_button, self.sound_button_rec)
                self.screen.blit(self.exit, self.exit_rec)
                if self.sounds:
                    self.screen.blit(self.sound_enable, self.sound_enable_rec)
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.unpause()
                else:
                    self.screen.blit(self.sound_disable, self.sound_disable_rec)
                    pygame.mixer.music.pause()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.sounds: 
                                self.button_sel.play()
                            pygame.mouse.set_visible(False)
                            with open('saves/options_data.json', 'w') as file:
                                json.dump(self.options, file, indent=4)
                            game_paused = False
                    elif mouse_pos[0] in range (self.sound_button_rec.left, self.sound_button_rec.right) and mouse_pos[1] in range (self.sound_button_rec.top, self.sound_button_rec.bottom):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.options[0] == 'enabled':
                                self.options[0] = 'disabled'
                            else:
                                self.options[0] = 'enabled'
                            self.sounds = not self.sounds
                    elif mouse_pos[0] in range (self.continue_text_rec.left, self.continue_text_rec.right) and mouse_pos[1] in range (self.continue_text_rec.top, self.continue_text_rec.bottom):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                pass
                        if event.type == pygame.MOUSEBUTTONUP:
                            if event.button == 1:
                                if self.sounds: 
                                    self.button_sel.play()
                                pygame.mouse.set_visible(False)
                                with open('saves/options_data.json', 'w') as file:
                                    json.dump(self.options, file, indent=4)
                                game_paused = False
                    elif mouse_pos[0] in range (self.exit_rec.left, self.exit_rec.right) and mouse_pos[1] in range (self.exit_rec.top, self.exit_rec.bottom):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pygame.mixer.music.stop()
                            self.main_menu = True
                            if self.sounds: 
                                self.button_sel.play()
            else:
                self.screen.blit(self.mainq, self.mainq_rec)
                self.screen.blit(self.mainq1, self.mainq1_rec)
                self.screen.blit(self.yes, self.yes_rec)
                self.screen.blit(self.no, self.no_rec)
                for event in pygame.event.get():
                    mouse_pos = pygame.mouse.get_pos()
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.main_menu = False
                            if self.sounds: 
                                self.button_sel.play()
                    elif mouse_pos[0] in range (self.yes_rec.left, self.yes_rec.right) and mouse_pos[1] in range (self.yes_rec.top, self.yes_rec.bottom):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            with open('saves/options_data.json', 'w') as file:
                                json.dump(self.options, file, indent=4)
                            self.main_menu = True
                            game_paused = False
                            if self.sounds: 
                                self.button_sel.play()
                            pygame.mixer.music.stop()
                            self.menu = True
                            self.game = False
                    elif mouse_pos[0] in range (self.no_rec.left, self.no_rec.right) and mouse_pos[1] in range (self.no_rec.top, self.no_rec.bottom):
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.main_menu = False
            pygame.display.flip()
            pygame.time.Clock().tick(15)  # Limit frame rate while paused
        return self.menu, self.game, self.sounds

    
class Gameover:
    def __init__(self, screen, winner, game, menu, game_type, p1, p2, sounds):
        self.screen_size = (1280, 720)
        self.screen = screen
        self.winner = winner
        self.menu = menu
        self.game = game
        self.game_type = game_type
        self.p1 = p1
        self.p2 = p2
        self.sounds = sounds
        self.gameover_surface = pygame.image.load("Pictures/Menu_b.png").convert_alpha()
        self.gameover_surface = pygame.transform.smoothscale(self.gameover_surface, self.screen_size)
        self.message1 = pygame.font.Font('ghostclan.ttf', 50)
        self.cont_message = pygame.font.Font('ghostclan.ttf', 30)
        self.message_font = pygame.font.Font('ghostclan.ttf', 20)
        self.gameover_message = self.message1.render('GAME OVER', True, (255,255,255))
        self.gameover_message_rect = self.gameover_message.get_rect(center = (1280/2, 100))
        self.winner_message = self.cont_message.render((f"{self.winner} WINS!"), True, (255,255,255))
        self.winner_message_rect = self.winner_message.get_rect(center = (1280/2, 200))
        self.cont = self.cont_message.render("continue", True, (255,255,255))
        self.cont_rect = self.cont.get_rect(center = (1280/2, 600))
        self.gameover_sound = pygame.mixer.Sound("Sounds/Game_Over.mp3")
        self.button_sel = pygame.mixer.Sound("Sounds/button_select.ogg")
        self.w = []
        self.l = []
        self.new_highscore = False
    
    def display(self):
        if self.sounds: 
            self.gameover_sound.play()
        self.load_json()
        while True:
            pygame.mouse.set_visible(True)
            mouse_pos = pygame.mouse.get_pos()
            self.screen.blit(self.gameover_surface, (0, 0))
            self.screen.blit(self.gameover_message, self.gameover_message_rect)
            self.screen.blit(self.winner_message, self.winner_message_rect)
            self.screen.blit(self.cont, self.cont_rect)
            if self.game_type == 'french':
                self.show_highscore_french()
            else:
                self.show_highscore()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif mouse_pos[0] in range (self.cont_rect.left, self.cont_rect.right) and mouse_pos[1] in range (self.cont_rect.top, self.cont_rect.bottom):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.sounds: 
                            self.button_sel.play()
                        return 'menu'
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            pygame.display.flip()
    
    def load_json(self):
        if self.game_type == 'eightball':
            with open('saves/eightballw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/eightballl_score.json', 'r') as file:
                loosers = json.load(file)
            if len(self.p1) == 6:
                if self.p1[-1] > winners[-1][-1]:
                    winners.pop()
                    winners.append(self.p1)
                    winners.sort(key=lambda w: w[-1], reverse=True)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p1:
                            loosers.insert(i, self.p2)
                            break
            else:
                if self.p2[-1] > winners[-1][-1]:
                    winners.pop()
                    winners.append(self.p2)
                    winners.sort(key=lambda w: w[-1], reverse=True)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p2:
                            loosers.insert(i, self.p1)
                            break
            with open('saves/eightballw_score.json', 'w') as file:
                json.dump(winners, file, indent=4)
            with open('saves/eightballl_score.json', 'w') as file:
                json.dump(loosers, file, indent=4)

        elif self.game_type == 'nineball':
            with open('saves/nineballw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/nineballl_score.json', 'r') as file:
                loosers = json.load(file)
            if self.winner == 'Player 1':
                if self.p1[-1] > winners[-1][-1]:
                    winners.pop()
                    winners.append(self.p1)
                    winners.sort(key=lambda w: w[-1], reverse=True)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p1:
                            loosers.insert(i, self.p2)
                            break
            else:
                if self.p2[-1] > winners[-1][-1]:
                    winners.pop()
                    winners.append(self.p2)
                    winners.sort(key=lambda w: w[-1], reverse=True)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p2:
                            loosers.insert(i, self.p1)
                            break
            with open('saves/nineballw_score.json', 'w') as file:
                json.dump(winners, file, indent=4)
            with open('saves/nineballl_score.json', 'w') as file:
                json.dump(loosers, file, indent=4)
        
        elif self.game_type == 'french':
            with open('saves/frenchw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/frenchl_score.json', 'r') as file:
                loosers = json.load(file)
            if self.winner == 'Player 1':
                if self.p1[-2] < winners[-1][-2]:
                    winners.pop()
                    winners.append(self.p1)
                    winners.sort(key=lambda w: w[-2], reverse=False)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p1:
                            loosers.insert(i, self.p2)
                            break
            else:
                if self.p2[-2] < winners[-1][-2]:
                    winners.pop()
                    winners.append(self.p2)
                    winners.sort(key=lambda w: w[-2], reverse=False)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p2:
                            loosers.insert(i, self.p1)
                            break
            with open('saves/frenchw_score.json', 'w') as file:
                json.dump(winners, file, indent=4)
            with open('saves/frenchl_score.json', 'w') as file:
                json.dump(loosers, file, indent=4)

        elif self.game_type == 'snooker':
            with open('saves/snookerw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/snookerl_score.json', 'r') as file:
                loosers = json.load(file)
            if self.winner == 'Player 1':
                if self.p1[-1] > winners[-1][-1]:
                    winners.pop()
                    winners.append(self.p1)
                    winners.sort(key=lambda w: w[-1], reverse=True)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p1:
                            loosers.insert(i, self.p2)
                            break
            else:
                if self.p2[-1] > winners[-1][-1]:
                    winners.pop()
                    winners.append(self.p2)
                    winners.sort(key=lambda w: w[-1], reverse=True)
                    loosers.pop()
                    for i, w in enumerate(winners):
                        if w == self.p2:
                            loosers.insert(i, self.p1)
                            break
            with open('saves/snookerw_score.json', 'w') as file:
                json.dump(winners, file, indent=4)
            with open('saves/snookerl_score.json', 'w') as file:
                json.dump(loosers, file, indent=4)
        
    def show_highscore(self):
        date = self.message_font.render('DATE', True, (255, 128, 128))
        winner = self.message_font.render('Winner', True, (255, 128, 128))
        looser = self.message_font.render('Looser', True, (255, 128, 128))
        balls = self.message_font.render('Potted Balls', True, (255, 128, 128))
        turns = self.message_font.render('TURNS', True, (255, 128, 128))
        fouls = self.message_font.render('FOULS', True, (255, 128, 128))
        points = self.message_font.render('SCORE', True, (255, 128, 128))

        if self.game_type == 'eightball':
            with open('saves/eightballw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/eightballl_score.json', 'r') as file:
                loosers = json.load(file) 
        elif self.game_type == 'nineball':
            with open('saves/nineballw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/nineballl_score.json', 'r') as file:
                loosers = json.load(file) 
        elif self.game_type == 'snooker':
            with open('saves/snookerw_score.json', 'r') as file:
                winners = json.load(file)
            with open('saves/snookerl_score.json', 'r') as file:
                loosers = json.load(file) 

        self.screen.blit(date, (10, 260))
        self.screen.blit(winner, (160, 260))
        self.screen.blit(balls, (310, 260))
        self.screen.blit(turns, (10, 460))
        self.screen.blit(fouls, (160, 460))
        self.screen.blit(points, (310, 460))
        self.screen.blit(looser, (840, 260))
        self.screen.blit(balls, (990, 260))
        self.screen.blit(turns, (840, 460))
        self.screen.blit(fouls, (990, 460))
        self.screen.blit(points, (1140, 460))
        x, y, y1 = 10, 300, 500
        for w in winners:
            for i in range (0, 6):
                txt = self.message_font.render(f'{w[i]}', True, (255, 255, 255))
                if i < 3:
                    self.screen.blit(txt, (x, y))
                else:
                    self.screen.blit(txt, (x, y1))
                x += 150
                if x > 310:
                    x = 10
            x = 10
            y += 30
            y1 += 30
        x, y, y1 = 840, 300, 500
        for l in loosers:
            for i in range (0, 5):
                txt = self.message_font.render(f'{l[i]}', True, (255, 255, 255))
                if i < 2:
                    self.screen.blit(txt, (x, y))
                else:
                    self.screen.blit(txt, (x, y1))
                x += 150
                if i == 1:
                    x = 840
            x = 840
            y += 30
            y1 += 30


    def show_highscore_french(self):
        date = self.message_font.render('DATE', True, (255, 128, 128))
        winner = self.message_font.render('Winner', True, (255, 128, 128))
        looser = self.message_font.render('Looser', True, (255, 128, 128))
        turns = self.message_font.render('TURNS', True, (255, 128, 128))
        points = self.message_font.render('SCORE', True, (255, 128, 128))

        with open('saves/frenchw_score.json', 'r') as file:
            winners = json.load(file)
        with open('saves/frenchl_score.json', 'r') as file:
            loosers = json.load(file)

        self.screen.blit(date, (10, 260))
        self.screen.blit(winner, (160, 260))
        self.screen.blit(turns, (310, 260))
        self.screen.blit(points, (160, 460))
        self.screen.blit(looser, (950, 260))
        self.screen.blit(turns, (1100, 260))
        self.screen.blit(points, (950, 460))
        x, y, y1 = 10, 300, 500
        for w in winners:
            for i in range (0, 4):
                txt = self.message_font.render(f'{w[i]}', True, (255, 255, 255))
                if i < 3:
                    self.screen.blit(txt, (x, y))
                else:
                    self.screen.blit(txt, (x, y1))
                x += 150
                if x > 310:
                    x = 160
            x = 10
            y += 30
            y1 += 30
        x, y, y1 = 950, 300, 500
        for l in loosers:
            for i in range (0, 3):
                txt = self.message_font.render(f'{l[i]}', True, (255, 255, 255))
                if i < 2:
                    self.screen.blit(txt, (x, y))
                else:
                    self.screen.blit(txt, (x, y1))
                x += 150
                if i == 1:
                    x = 950
            x = 950
            y += 30
            y1 += 30

class Screen_message:
    def __init__(self, font, text, pos, color, align = "center"):
        self.font = font
        self.text = text
        self.pos = pos
        self.color = color
        self.align = align

    def draw(self, screen):
        message = self.font.render(self.text, True, self.color)
        message_rect = message.get_rect()
        setattr(message_rect, self.align, self.pos)
        screen.blit(message, message_rect)