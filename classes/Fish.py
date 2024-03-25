from random import uniform, randint
import time
import pygame
import math

from .Util import *
from .Rules import Rules
from constants import *

class Fish:
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.vel_x = uniform(-1.5, 1.5)*0.6
        self.vel_y = uniform(-1.5, 1.5)*0.6
        self.color = (255, 255, 255)
        self.current_sprite_index = randint(0, 12)
        self.sprites = []
        self.last_frame = time.time()
        self.targeted_food = None

        self.screen: pygame.Surface = screen
        self.util = Util()
        self.rules = Rules()

        for i in range(13):
            cur_image = pygame.image.load(f'./assets/fish2/{i}.png').convert_alpha()
            cur_image = pygame.transform.scale(cur_image, (cur_image.get_width()//5, cur_image.get_height()//5))
            self.sprites.append(cur_image)

        self.image = self.sprites[self.current_sprite_index]

    def update(self, neighbour_fishes, neighbour_foods, neighbour_lures, neighbour_stomps, dt, mouse_x, mouse_y):
        self.x += self.vel_x
        self.y += self.vel_y

        separation_dvx, separation_dvy = self.rules.separation(self, neighbour_fishes, neighbour_foods, neighbour_lures, neighbour_stomps, mouse_x, mouse_y)
        self.vel_x += separation_dvx
        self.vel_y += separation_dvy

        alignment_dvx, alignment_dvy = self.rules.alignment(self, neighbour_fishes, neighbour_foods, neighbour_lures)
        old_vel_magnitude = self.util.magnitude(self.vel_x, self.vel_y)
        self.vel_x += alignment_dvx
        self.vel_y += alignment_dvy
        new_vel_magnitude = self.util.magnitude(self.vel_x, self.vel_y)
        self.vel_x = self.vel_x / new_vel_magnitude * old_vel_magnitude
        self.vel_y = self.vel_y / new_vel_magnitude * old_vel_magnitude

        cohesion_dvx, cohesion_dvy = self.rules.cohesion(self, neighbour_fishes)
        old_vel_magnitude = self.util.magnitude(self.vel_x, self.vel_y)
        self.vel_x += cohesion_dvx * 0.015
        self.vel_y += cohesion_dvy * 0.015
        new_vel_magnitude = self.util.magnitude(self.vel_x, self.vel_y)
        self.vel_x = self.vel_x / new_vel_magnitude * old_vel_magnitude
        self.vel_y = self.vel_y / new_vel_magnitude * old_vel_magnitude

        ###
        # pygame.draw.circle(self.screen, (255, 255, 255), (self.x, self.y), SEPARATION_DIST, 1)
        # upper = [[self.x, self.y], [self.x-6, self.y-8], [self.x, self.y-28], [self.x+6, self.y-8]]
        # lower = [[self.x, self.y],[self.x-6, self.y+8],[self.x+6, self.y+8]]
        # points = [[self.x, self.y-8],[self.x-4, self.y+8],[self.x+4, self.y+8]]
        # self.orientate(points)
        # pygame.draw.polygon(self.screen, self.color, points)

        # self.orientate(upper)
        # self.orientate(lower)
        # pygame.draw.polygon(self.screen, self.color, upper)
        # pygame.draw.polygon(self.screen, self.color, lower)
        ###

        self.check_out_of_bound()

        self.image = self.sprites[self.current_sprite_index]
        if time.time() - self.last_frame > 0.05:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprites)
            self.last_frame = time.time()

    
    def draw(self):
        radian = math.atan2(self.vel_y, - self.vel_x) - math.pi/2  # + math.pi/2
        rotated_image = pygame.transform.rotate(self.image,math.degrees(radian) - 20)
        self.screen.blit(rotated_image, (self.x-rotated_image.get_width()/2, self.y-rotated_image.get_height()/2))

    def check_out_of_bound(self):
        if self.x < 0:
            self.x = WIDTH
            self.vel_x = uniform(-1.5, -0.5)*0.8
        elif self.x >= WIDTH:
            self.x = 0
            self.vel_x = uniform(0.5, 1.5)*0.8
        elif self.y < 0:
            self.y = HEIGHT
            self.vel_y = uniform(-1.5, -0.5)*0.8
        elif self.y >= HEIGHT:
            self.y = 0
            self.vel_y = uniform(0.5, 1.5)*0.8

    def orientate(self, points):
        radian = math.atan2(self.vel_y, -self.vel_x) + math.pi/2

        for i, point in enumerate(points):
            x = point[0]
            y = point[1]
            points[i] = [
                    (x - self.x) * math.cos(radian) + (y - self.y) * math.sin(radian) + self.x, 
                    -(x - self.x) * math.sin(radian) + (y - self.y) * math.cos(radian) + self.y
                    ]

    