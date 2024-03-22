import pygame
from random import uniform
from typing import List

from classes.QuadTree import *
from classes.Fish import Fish
from classes.FishFood import FishFood
from constants import *

# Pygame & window initialization
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Object lists initialization
fishes: List[Fish] = []
for _ in range(FISH_COUNT):
    fishes.append(Fish(20, 20, screen=screen))
    
fishfoods: List[FishFood] = []

# Game variable
running = True
bg = pygame.image.load('./assets/water_bg.png').convert()
bg = pygame.transform.smoothscale(bg, screen.get_size())
dt = clock.tick(FPS) / 1000 #deltaTime

# Main loop
while running:
    # Background filling
    screen.fill(BG_COLOR)
    screen.blit(bg, (0, 0))

    # Getting mouse information
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, (255, 255, 255), (mouse_x, mouse_y), QUERY_DIST, 1)

    # Game close event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                fishfoods.append(FishFood(mouse_x, mouse_y, screen))

    # Fish quadtree initialization & popularizing
    fish_quadTree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), screen)
    for fish in fishes:
        fish_quadTree.insert(fish)

    # Process fish food
    remain_fishfood = []
    for fish_food in fishfoods:
        eaten = fish_quadTree.query(Circle(fish_food.x, fish_food.y, fish_food.r+11), fish_food.r+11)
        if not eaten:
            remain_fishfood.append(fish_food)
    fishfoods = remain_fishfood

    # Fish food quadtree initialization & popularizing
    fishfood_quadTree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), screen)
    for fish_food in fishfoods:
        fishfood_quadTree.insert(fish_food)
        fish_food.update()
        fish_food.draw()

    # Process & move each fish
    for fish in fishes:
        neighbour_fishes = fish_quadTree.query(fish, QUERY_DIST) #n^2 -> nlogn avg (n^2 at worst)
        if fish.targeted_food: # only find food when fish did not target any food
            neighbour_foods = [fish.targeted_food]
        else:
            neighbour_foods = fishfood_quadTree.query(fish, FISHFOOD_DIST)

        fish.update(neighbour_fishes, neighbour_foods, dt, mouse_x, mouse_y)
        fish.draw()

    # Update and set FPS & deltaTime
    pygame.display.update()
    dt = clock.tick(FPS) / 1000