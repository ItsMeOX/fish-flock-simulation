import pygame

class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def contains(self, fish):
        return (fish.x - self.x) ** 2 + (fish.y - self.y) ** 2 <= self.r ** 2

    def intersect(self, boundary):
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

class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def contains(self, fish):
        return self.x1 <= fish.x <= self.x2 and self.y1 <= fish.y <= self.y2

    def intersect(self, boundary):
        return max(self.x1, boundary.x1) <= min(self.x2, boundary.x2)

class QuadTree:
    def __init__(self, boundary, capacity = 4):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False
        self.topLeft = self.topRight = self.bottomLeft = self.bottomRight = None

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
        
        if len(self.points) < self.capacity:
            self.points.append((fish.x, fish.y))
            return True
        
        if not self.divided:
            x1 = self.boundary.x1
            x2 = self.boundary.x2
            y1 = self.boundary.y1
            y2 = self.boundary.y2
            self.topLeft = QuadTree(Rectangle(x1, y1, (x1+x2)/2, (y1+y2)/2), self.capacity)
            self.topRight = QuadTree(Rectangle((x1+x2)/2, y1, x2, (y1+y2)/2), self.capacity)
            self.bottomLeft = QuadTree(Rectangle(x1, (y1+y2)/2, (x1+x2)/2, y2), self.capacity)
            self.bottomRight = QuadTree(Rectangle((x1+x2)/2, (y1+y2)/2, x2, y2), self.capacity)
            self.divided = True

        return self.topLeft.insert(fish) or self.topRight.insert(fish) or self.bottomLeft.insert(fish) or self.bottomRight.insert(fish)
    
    def query(self, fish, res = []):
        if not res:
            res = []
        
        if not self.boundary.contains(fish) or not Circle(fish.x, fish.y, 30).intersect(self.boundary):
            return
        
        for point in self.points:
            res.append(point)

        if self.divided:
            self.topLeft.query(fish, res)
            self.topRight.query(fish, res)
            self.bottomLeft.query(fish, res)
            self.bottomRight.query(fish, res)

        return res
        
