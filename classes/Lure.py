import pygame
import time
from typing import List, Union
from random import uniform, randint
from math import sin,cos,radians
from classes.Util import Util
from classes.Fish import Fish
from constants import *

class Lure:
    def __init__(self, x, y, screen, alpha_srf):
        self.x = x
        self.y = y
        self.r = 5
        self.screen = screen
        self.alpha_srf = alpha_srf
        self.util = Util()
        self.ripple = Ripple(self.x, self.y, screen, alpha_srf)

    def update(self):
        self.x += uniform(-0.05, 0.05)
        self.y += uniform(-0.05, 0.05)    
        self.ripple.update()

    def draw(self):
        pygame.draw.circle(self.screen, (247, 240, 240), (self.x, self.y), self.r)
        self.ripple.draw()

    def get_baited_fish(self, neighbour_fishes: List[Fish]) -> Union[Fish, None]:
        '''
        condition: fish slow and close enough to lure
        '''
        for fish in neighbour_fishes:
            slow_enough = self.util.magnitude(fish.vel_x, fish.vel_y) <= LURE_FISH_THRESHOLD_VEL
            close_enough = self.util.distance(fish.x, fish.y, self.x, self.y) <= BAITED_DIST
            if slow_enough and close_enough:
                return fish
            
        return None
    
class Ripple:
    def __init__(self, x, y, screen, alpha_srf):
        self.x = x
        self.y = y
        self.r = 0.1
        self.max_r = 100
        self.vel = uniform(0, 0.001)

        self.screen = screen
        self.alpha_srf: pygame.Surface = alpha_srf
        
        self.last_end = time.time()
        self.time_between_ripple = randint(10, 20)

    def update(self):
        if self.r > self.max_r:
            if time.time() - self.last_end > self.time_between_ripple:
                self.last_end = time.time()
                self.r = 0
                self.vel = 0
        else:
            self.r += self.vel
            self.vel += 0.0005

    def draw(self):
        color = pygame.Color(164, 212, 252, int(max(0, (1 - self.r/self.max_r)*200)))
        pygame.draw.circle(self.alpha_srf, color, (self.x, self.y), self.r, 1)
        pygame.draw.circle(self.alpha_srf, color, (self.x, self.y), self.r-uniform(20, 27), 1)
        self.screen.blit(self.alpha_srf, (0, 0))