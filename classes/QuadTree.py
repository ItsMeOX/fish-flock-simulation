import pygame
from typing import List
from .Fish import Fish
from constants import *

class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def contains(self, fish):
        return (fish.x - self.x) ** 2 + (fish.y - self.y) ** 2 <= self.r ** 2

    def intersect_rect(self, boundary):
        boundary_center_x = (boundary.x1 + boundary.x2) / 2
        boundary_center_y = (boundary.y1 + boundary.y2) / 2
        boundary_width = boundary.x2 - boundary.x1
        boundary_height = boundary.y2 - boundary.y1

        distance_x = abs(self.x - boundary_center_x)
        distance_y = abs(self.y - boundary_center_y)

        if distance_x > boundary_width/2+self.r: return False
        if distance_y > boundary_height/2+self.r: return False

        if distance_x <= boundary_width/2: return True
        if distance_y <= boundary_height/2: return True

        cornerDistance = (distance_x-boundary_width/2)**2 + (distance_y-boundary_height/2)**2

        return cornerDistance <= self.r**2

    def intersect_circle(self, boundary):
        distance = (boundary.x - self.x) ** 2 + (boundary.y - self.y) ** 2
        return distance <= (boundary.r * 2) ** 2

class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def contains(self, fish):
        return self.x1 <= fish.x <= self.x2 and self.y1 <= fish.y <= self.y2

class QuadTree:
    def __init__(self, boundary, screen, capacity = 4):
        self.boundary = boundary
        self.capacity = capacity
        self.other_fishes = []
        self.divided = False
        self.topLeft = self.topRight = self.bottomLeft = self.bottomRight = None

        self.screen = screen

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.boundary.x1, self.boundary.y1, self.boundary.x2-self.boundary.x1, self.boundary.y2-self.boundary.y1), 1)
        if self.divided:
            self.topLeft.draw(screen)
            self.topRight.draw(screen)
            self.bottomLeft.draw(screen)
            self.bottomRight.draw(screen)

    def insert(self, fish):
        if not self.boundary.contains(fish):
            return False
        
        if len(self.other_fishes) < self.capacity:
            self.other_fishes.append(fish)
            return True
        
        if not self.divided:
            x1 = self.boundary.x1
            x2 = self.boundary.x2
            y1 = self.boundary.y1
            y2 = self.boundary.y2
            self.topLeft = QuadTree(Rectangle(x1, y1, (x1+x2)/2, (y1+y2)/2), self.screen, self.capacity)
            self.topRight = QuadTree(Rectangle((x1+x2)/2, y1, x2, (y1+y2)/2), self.screen, self.capacity)
            self.bottomLeft = QuadTree(Rectangle(x1, (y1+y2)/2, (x1+x2)/2, y2), self.screen, self.capacity)
            self.bottomRight = QuadTree(Rectangle((x1+x2)/2, (y1+y2)/2, x2, y2), self.screen, self.capacity)
            self.divided = True

        return self.topLeft.insert(fish) or self.topRight.insert(fish) or self.bottomLeft.insert(fish) or self.bottomRight.insert(fish)
    
    def debug(self):
        def dfs(node):
            res = len(node.other_fishes)
            
            if node.divided:
                res += dfs(node.topLeft)
                res += dfs(node.topRight)
                res += dfs(node.bottomLeft)
                res += dfs(node.bottomRight)
            return res
        print(dfs(self))



    def query(self, obj, radius) -> List[Fish]:
        '''
        obj: fish / fishfood etc
        radius: query radius
        '''
        res = []

        def dfs(node, obj, radius):        
            if not Circle(obj.x, obj.y, radius).intersect_rect(node.boundary):
                return

            for other_fish in node.other_fishes:
                if Circle(obj.x, obj.y, radius).intersect_circle(Circle(other_fish.x, other_fish.y, radius)):
                    res.append(other_fish)

            if node.divided:
                dfs(node.topLeft, obj, radius)
                dfs(node.topRight, obj, radius)
                dfs(node.bottomLeft, obj, radius)
                dfs(node.bottomRight, obj, radius)

        dfs(self, obj, radius)
        return res