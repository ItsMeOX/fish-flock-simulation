from random import uniform

from .Util import Util
from constants import *

class Rules:
    def __init__(self):
        '''
            obj: fish / fishfoods
            neighbour_fishes: queries neighbour fishes surrounding obj from quad tree
        '''
        self.util = Util()

    def separation(self, obj, neighbour_fishes, neighbour_foods, neighbour_lures, neighbour_stomps, mouse_x, mouse_y):
        separation_velocity = [0, 0]
        boid_count = 0

        for fish in neighbour_fishes:
            if fish == obj: continue
            distance = self.util.distance(obj.x, obj.y, fish.x, fish.y)
            if distance <= SEPARATION_DIST:
                delta_x = obj.x - fish.x
                delta_y = obj.y - fish.y
                normalized_delta_x, normalized_delta_y = self.util.normalize(delta_x, delta_y)

                separation_velocity[0] += normalized_delta_x/distance
                separation_velocity[1] += normalized_delta_y/distance
                boid_count += 1

        for fish_food in neighbour_foods:
            delta_x = obj.x - fish_food.x
            delta_y = obj.y - fish_food.y
            normalized_delta_x, normalized_delta_y = self.util.normalize(delta_x, delta_y)

            distance = self.util.distance(obj.x, obj.y, fish_food.x, fish_food.y)
            separation_velocity[0] -= 3*normalized_delta_x/distance
            separation_velocity[1] -= 3*normalized_delta_y/distance
            boid_count += 1
            break

        for stomp in neighbour_stomps:
            delta_x = obj.x - stomp.x
            delta_y = obj.y - stomp.y
            normalized_delta_x, normalized_delta_y = self.util.normalize(delta_x, delta_y)

            distance = self.util.distance(obj.x, obj.y, stomp.x, stomp.y)
            separation_velocity[0] += 2000*normalized_delta_x/distance
            separation_velocity[1] += 2000*normalized_delta_y/distance
            boid_count += 1

        # for lure in neighbour_lures:
        #     delta_x = obj.x - lure.x
        #     delta_y = obj.y - lure.y
        #     normalized_delta_x, normalized_delta_y = self.util.normalize(delta_x, delta_y)

        #     distance = self.util.distance(obj.x, obj.y, lure.x, lure.y)
        #     separation_velocity[0] -= normalized_delta_x/distance
        #     separation_velocity[1] -= normalized_delta_y/distance
        #     boid_count += 1
        #     break

        # right
        if WIDTH - obj.x <= BORDER_DIST:
            separation_velocity[0] -= 2/(WIDTH - obj.x + 0.1)
        # left
        if obj.x <= BORDER_DIST:
            separation_velocity[0] += 2/(obj.x+0.1)
        # top
        if obj.y <= BORDER_DIST:
            separation_velocity[1] += 2/(obj.y+0.1)
        # down
        if HEIGHT - obj.y <= BORDER_DIST:
            separation_velocity[1] -= 2/(HEIGHT - obj.y + 0.1)

        # mouse
        distance = self.util.distance(obj.x, obj.y, mouse_x, mouse_y)
        if distance <= SEPARATION_MOUSE_DIST:
            delta_x = obj.x - mouse_x
            delta_y = obj.y - mouse_y
            normalized_delta_x, normalized_delta_y = self.util.normalize(delta_x, delta_y)

            separation_velocity[0] -= 2*normalized_delta_x/distance
            separation_velocity[1] -= 2*normalized_delta_y/distance
            boid_count += 1

        if boid_count:
            separation_velocity[0] /= boid_count
            separation_velocity[1] /= boid_count

        separation_velocity[0] *= SEPARATION_SCALE
        separation_velocity[1] *= SEPARATION_SCALE

        return separation_velocity

    def alignment(self, obj, neighbour_fishes, neighbour_foods, neighbour_lures):
        alignment_velocity = [0, 0]
        boid_count = 0

        for fish in neighbour_fishes:
            if fish == obj: continue
            distance = self.util.distance(fish.x, fish.y, obj.x, obj.y)
            if distance <= ALIGNMENT_DIST:
                alignment_velocity[0] += fish.vel_x
                alignment_velocity[1] += fish.vel_y
                boid_count += 1

        for food in neighbour_foods:
            alignment_velocity[0] += (food.x - obj.x) * food.attractiveness
            alignment_velocity[1] += (food.y - obj.y) * food.attractiveness
            boid_count += 1

        for lure in neighbour_lures:
            alignment_velocity[0] += 0.005*(lure.x - obj.x)
            alignment_velocity[1] += 0.005*(lure.y - obj.y)
            boid_count += 1

        if boid_count:
            alignment_velocity[0] /= boid_count
            alignment_velocity[1] /= boid_count
        
        alignment_velocity[0] *= ALIGNMENT_SCALE
        alignment_velocity[1] *= ALIGNMENT_SCALE
        
        return alignment_velocity

    def cohesion(self, obj, neighbour_fishes):
        cohesion_velocity = [0, 0]
        boid_count = 0

        for fish in neighbour_fishes:
            if fish == obj: continue
            distance = self.util.distance(obj.x, obj.y, fish.x, fish.y)
            if distance <= COHESION_DIST:
                delta_x = fish.x - obj.x
                delta_y = fish.y - obj.y
                cohesion_velocity[0] += delta_x
                cohesion_velocity[1] += delta_y
                boid_count += 1
        
        if boid_count:
            cohesion_velocity[0] /= boid_count
            cohesion_velocity[1] /= boid_count
            cohesion_velocity[0] -= obj.x
            cohesion_velocity[1] -= obj.y
            magnitude = self.util.magnitude(cohesion_velocity[0], cohesion_velocity[1])
            cohesion_velocity[0] /= magnitude
            cohesion_velocity[1] /= magnitude

        cohesion_velocity[0] *= COHESION_SCALE
        cohesion_velocity[1] *= COHESION_SCALE
        return cohesion_velocity
