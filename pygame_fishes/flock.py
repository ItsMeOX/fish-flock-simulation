import pygame
from random import uniform
from typing import List
import requests
import time

# from db.api import Firebase
from classes.Fish import Fish
from classes.FishFood import FishFood
from classes.Lure import Lure
from classes.QuadTree import *
from constants import *
    
try:
    from gesture_detector.detector_v2 import app
except Exception as e:
    print(e)

# Firebase initialization
# Test
# firebase = Firebase()
# response = requests.get(firebase.get_imageURL('ItsMeOX', 'fish'))
# img = pygame.image.load(BytesIO(response.content))

# Pygame & window initialization
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
alpha_srf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Object lists initialization
fishes: List[Fish] = []
for _ in range(FISH_COUNT):
    fishes.append(Fish(20, 20, screen=screen))
    
fishfoods: List[FishFood] = []

lures: List[Lure] = []

stomps: List[Circle] = []

# Game variable
running = True
bg = pygame.image.load('./assets/water_bg.png').convert()
bg = pygame.transform.smoothscale(bg, screen.get_size())
dt = clock.tick(FPS) / 1000 #deltaTime
cursor_circle_color = (255, 255, 255)
last_cursor_color_change = time.time()

# Main loop
while running:
    # Background filling
    alpha_srf.fill(pygame.Color(0, 0, 0, 0))
    screen.fill(BG_COLOR)
    screen.blit(bg, (0, 0))

    # Getting mouse information
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, cursor_circle_color, (mouse_x, mouse_y), QUERY_DIST, 1)
    # If stomped, paint cursor red for 0.3 seconds
    if time.time() - last_cursor_color_change > 0.3:
        cursor_circle_color = (255, 255, 255)
        last_cursor_color_change = time.time()

    # Game close event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            stomps.append(Circle(mouse_x, mouse_y, STOMP_DIST))
            cursor_circle_color = (255, 0, 0)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                fishfoods.append(FishFood(mouse_x, mouse_y, screen))
            elif event.key == pygame.K_g:
                lures.append(Lure(mouse_x, mouse_y, screen, alpha_srf))
            
    # Fish quadtree initialization & popularizing
    fish_quadTree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), screen)
    for fish in fishes:
        fish_quadTree.insert(fish)

    # Process fish food (remove if eaten by fish)
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

    # Fish lure quadtree initialization & popularizing
    lure_quadTree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), screen)
    for lure in lures:
        lure_quadTree.insert(lure)

    # Stomp quad tree initialization & popularizing
    stomp_quadTree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), screen)
    for stomp in stomps:
        stomp_quadTree.insert(stomp)

    # Process & move each fish
    for fish in fishes:
        neighbour_fishes = fish_quadTree.query(fish, QUERY_DIST) #n^2 -> nlogn avg (n^2 at worst)

        #TODO: Not done yet
        if fish.targeted_food: # only find food when fish did not target any food
            neighbour_foods = [fish.targeted_food]
        else:
            neighbour_foods = fishfood_quadTree.query(fish, FISHFOOD_DIST)

        neighbour_lures = lure_quadTree.query(fish, LURE_ATTRACT_DIST)

        neighbour_stomps = stomp_quadTree.query(fish, STOMP_DIST)

        fish.update(neighbour_fishes, neighbour_foods, neighbour_lures, neighbour_stomps, dt, mouse_x, mouse_y)
        fish.draw()

    # Clear stomp every frame
    stomps.clear()

    remain_lure = []
    for lure in lures:
        neighbour_fishes = fish_quadTree.query(lure, BAITED_DIST)
        lure.update()
        baited_fish = lure.get_baited_fish(neighbour_fishes)
        if not baited_fish:
            remain_lure.append(lure)
        else:
            fishes.remove(baited_fish)
            print(baited_fish)

        lure.draw()
    lures = remain_lure

        

    # Update and set FPS & deltaTime
    pygame.display.update()
    dt = clock.tick(FPS) / 1000