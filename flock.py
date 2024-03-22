import pygame
from random import randint, random, uniform
import math
import time
from QuadTree import *

BG_COLOR = (0, 0, 0)
FPS = 144
WIDTH = 800
HEIGHT = 600
FISH_COUNT = 100
SEPARATION_DIST = 20
ALIGNMENT_DIST = 30
COHESION_DIST = 10
BORDER_DIST = 30
SEPARATION_MOUSE_DIST = 30
SEPARATION_SCALE = 0.1
ALIGNMENT_SCALE = 0.15
COHESION_SCALE = 0.12
a = 1
QUERY_DIST = max(BORDER_DIST, COHESION_DIST, ALIGNMENT_DIST, SEPARATION_DIST, SEPARATION_MOUSE_DIST)

# Initialize the game
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Fish:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = uniform(-1.5, 1.5)*0.6
        self.vel_y = uniform(-1.5, 1.5)*0.6
        self.color = (255, 255, 255)
        self.current_sprite_index = randint(0, 12)
        self.sprites = []
        self.last_frame = time.time()

        for i in range(13):
            cur_image = pygame.image.load(f'./assets/fish2/{i}.png').convert_alpha()
            cur_image = pygame.transform.scale(cur_image, (cur_image.get_width()//5, cur_image.get_height()//5))
            self.sprites.append(cur_image)

        self.image = self.sprites[self.current_sprite_index]

    def draw(self, neighbour_fishes):
        self.x += self.vel_x
        self.y += self.vel_y

        separation_dvx, separation_dvy = self.separation(neighbour_fishes)
        self.vel_x += separation_dvx
        self.vel_y += separation_dvy

        alignment_dvx, alignment_dvy = self.alignment(neighbour_fishes)
        old_vel_magnitude = util.magnitude(self.vel_x, self.vel_y)
        self.vel_x += alignment_dvx
        self.vel_y += alignment_dvy
        new_vel_magnitude = util.magnitude(self.vel_x, self.vel_y)
        self.vel_x = self.vel_x / new_vel_magnitude * old_vel_magnitude
        self.vel_y = self.vel_y / new_vel_magnitude * old_vel_magnitude

        cohesion_dvx, cohesion_dvy = self.cohesion(neighbour_fishes)
        old_vel_magnitude = util.magnitude(self.vel_x, self.vel_y)
        self.vel_x += cohesion_dvx * 0.015
        self.vel_y += cohesion_dvy * 0.015
        new_vel_magnitude = util.magnitude(self.vel_x, self.vel_y)
        self.vel_x = self.vel_x / new_vel_magnitude * old_vel_magnitude
        self.vel_y = self.vel_y / new_vel_magnitude * old_vel_magnitude

        ###
        # pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), SEPARATION_DIST, 1)
        # upper = [[self.x, self.y], [self.x-6, self.y-8], [self.x, self.y-28], [self.x+6, self.y-8]]
        # lower = [[self.x, self.y],[self.x-6, self.y+8],[self.x+6, self.y+8]]
        # points = [[self.x, self.y-8],[self.x-4, self.y+8],[self.x+4, self.y+8]]
        # self.orientate(points)
        # pygame.draw.polygon(screen, self.color, points)

        # self.orientate(upper)
        # self.orientate(lower)
        # pygame.draw.polygon(screen, self.color, upper)
        # pygame.draw.polygon(screen, self.color, lower)
        ###

        self.image = self.sprites[self.current_sprite_index]
        if time.time() - self.last_frame > 0.05:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprites)
            self.last_frame = time.time()

        #!test
        radian = math.atan2(self.vel_y, -self.vel_x) - math.pi/2  # + math.pi/2
        rotated_image = pygame.transform.rotate(self.image,math.degrees(radian) - 20)

        screen.blit(rotated_image, (self.x-rotated_image.get_width()/2, self.y-rotated_image.get_height()/2))


    def orientate(self, points):
        radian = math.atan2(self.vel_y, -self.vel_x) + math.pi/2

        for i, point in enumerate(points):
            x = point[0]
            y = point[1]
            points[i] = [
                    (x - self.x) * math.cos(radian) + (y - self.y) * math.sin(radian) + self.x, 
                    -(x - self.x) * math.sin(radian) + (y - self.y) * math.cos(radian) + self.y
                    ]

    def separation(self, neighbour_fishes):
        separation_velocity = [0, 0]
        boid_count = 0

        for fish in neighbour_fishes:
            if fish == self: continue
            distance = util.distance(self.x, self.y, fish.x, fish.y)
            if distance <= SEPARATION_DIST:
                delta_x = self.x - fish.x
                delta_y = self.y - fish.y
                normalized_delta_x, normalized_delta_y = util.normalize(delta_x, delta_y)

                separation_velocity[0] += normalized_delta_x/distance
                separation_velocity[1] += normalized_delta_y/distance
                boid_count += 1

        # right
        if WIDTH - self.x <= BORDER_DIST:
            separation_velocity[0] -= 1/(WIDTH - self.x + 0.1)
        # left
        if self.x <= BORDER_DIST:
            separation_velocity[0] += 1/(self.x+0.1)
        # top
        if self.y <= BORDER_DIST:
            separation_velocity[1] += 1/(self.y+0.1)
        # down
        if HEIGHT - self.y <= BORDER_DIST:
            separation_velocity[1] -= 1/(HEIGHT - self.y + 0.1)

        # mouse
        distance = util.distance(self.x, self.y, mouse_x, mouse_y)
        if distance <= SEPARATION_MOUSE_DIST:
            delta_x = self.x - mouse_x
            delta_y = self.y - mouse_y
            normalized_delta_x, normalized_delta_y = util.normalize(delta_x, delta_y)

            separation_velocity[0] -= 5*normalized_delta_x/distance
            separation_velocity[1] -= 5*normalized_delta_y/distance
            boid_count += 1

        if boid_count:
            separation_velocity[0] /= boid_count
            separation_velocity[1] /= boid_count

        separation_velocity[0] *= SEPARATION_SCALE
        separation_velocity[1] *= SEPARATION_SCALE

        return separation_velocity

    def alignment(self, neighbour_fishes):
        alignment_velocity = [0, 0]
        boid_count = 0

        for fish in neighbour_fishes:
            if fish == self: continue
            distance = util.distance(fish.x, fish.y, self.x, self.y)
            if distance <= ALIGNMENT_DIST:
                alignment_velocity[0] += fish.vel_x
                alignment_velocity[1] += fish.vel_y
                boid_count += 1

        if boid_count:
            alignment_velocity[0] /= boid_count
            alignment_velocity[1] /= boid_count
        
        alignment_velocity[0] *= ALIGNMENT_SCALE
        alignment_velocity[1] *= ALIGNMENT_SCALE
        
        return alignment_velocity

    def cohesion(self, neighbour_fishes):
        cohesion_velocity = [0, 0]
        boid_count = 0

        for fish in neighbour_fishes:
            if fish == self: continue
            distance = util.distance(self.x, self.y, fish.x, fish.y)
            if distance <= COHESION_DIST:
                delta_x = fish.x - self.x
                delta_y = fish.y - self.y
                cohesion_velocity[0] += delta_x
                cohesion_velocity[1] += delta_y
                boid_count += 1
        
        if boid_count:
            cohesion_velocity[0] /= boid_count
            cohesion_velocity[1] /= boid_count
            cohesion_velocity[0] -= self.x
            cohesion_velocity[1] -= self.y
            magnitude = util.magnitude(cohesion_velocity[0], cohesion_velocity[1])
            cohesion_velocity[0] /= magnitude
            cohesion_velocity[1] /= magnitude

        cohesion_velocity[0] *= COHESION_SCALE
        cohesion_velocity[1] *= COHESION_SCALE
        return cohesion_velocity

class Util:
    def distance(self, x1, y1, x2, y2):
        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def normalize(self, v1, v2):
        magnitude = self.magnitude(v1, v2)
        return (v1/magnitude, v2/magnitude)
    
    def magnitude(self, v1, v2):
        return (v1**2 + v2**2)**0.5

util = Util()

fishes = []

for _ in range(FISH_COUNT):
    fishes.append(Fish(25, 25))

running = True
bg = pygame.image.load('./assets/water_bg.png').convert()
bg = pygame.transform.smoothscale(bg, screen.get_size())
debug_fish = fishes[0]

while running:
    screen.fill(BG_COLOR)
    screen.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, (255, 255, 255), (mouse_x, mouse_y), SEPARATION_MOUSE_DIST, 1)

    quadTree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), QUERY_DIST)
    for fish in fishes:
        quadTree.insert(fish)

    for fish in fishes:
        neighbour_fishes = quadTree.query(fish) #n^2 -> nlogn avg (n^2 at worst)

        if fish.x < 0:
            fish.x = WIDTH
            fish.vel_x = uniform(-1.5, -0.5)*0.8
        elif fish.x >= WIDTH:
            fish.x = 0
            fish.vel_x = uniform(0.5, 1.5)*0.8
        elif fish.y < 0:
            fish.y = HEIGHT
            fish.vel_y = uniform(-1.5, -0.5)*0.8
        elif fish.y >= HEIGHT:
            fish.y = 0
            fish.vel_y = uniform(0.5, 1.5)*0.8

        fish.draw(neighbour_fishes=neighbour_fishes)

    pygame.display.update()

    # set FPS
    clock.tick(FPS)