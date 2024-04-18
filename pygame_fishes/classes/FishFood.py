import pygame
from random import uniform, randint

from .Rules import Rules
from constants import *

#temp
SPEED = 0.5

class FishFood:
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.r = 2
        self.attractiveness = randint(1, 3)
        self.vel_x = uniform(-SPEED, SPEED)
        self.vel_y = uniform(-SPEED, SPEED)
        self.screen = screen
        self.rules = Rules()

    def update(self):
        self.vel_x = uniform(-SPEED, SPEED)
        self.vel_y = uniform(-SPEED, SPEED)
        self.x += self.vel_x
        self.y += self.vel_y
        self.check_out_of_bound()

    def draw(self):
        # (88, 57, 39) -> Brown
        pygame.draw.circle(self.screen, (88, 57, 39), (self.x, self.y), self.r) 

    def check_out_of_bound(self):
        if self.x < 0:
            self.x = WIDTH
            self.vel_x = uniform(-SPEED, -SPEED)
        elif self.x >= WIDTH:
            self.x = 0
            self.vel_x = uniform(SPEED, SPEED)
        elif self.y < 0:
            self.y = HEIGHT
            self.vel_y = uniform(-SPEED, -SPEED)
        elif self.y >= HEIGHT:
            self.y = 0
            self.vel_y = uniform(SPEED, SPEED)