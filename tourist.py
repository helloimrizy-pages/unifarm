import pygame
import random
import math
from constants import *
from utils import distance

class Tourist(pygame.sprite.Sprite):
    def __init__(self, position, economy_manager):
        super().__init__()
        
        size = int(TILE_SIZE * 0.8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PINK, (size//2, size//2), size//2)
        
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.position = position
        self.manager = economy_manager
        self.terrain = economy_manager.terrain
        self.game_state = economy_manager.game_state
        
        self.speed = random.uniform(2.0, 4.0) * (TILE_SIZE / 32)
        self.satisfaction = random.uniform(50, 70)
        self.spending_rate = random.uniform(5, 15)
        self.visit_duration = random.uniform(5, 15)
        self.time_spent = 0
        
        self.target_position = None
        self.path = []
        self.path_index = 0
        self.waiting_time = 0
    
    def step(self, dt):
        """Update tourist behavior"""
        self.time_spent += dt / 60
        
        self.update_satisfaction(dt)
        
        self.move(dt)
        
        if self.time_spent % 1.0 < dt / 60:
            self.spend_money()
        
        if self.time_spent >= self.visit_duration:
            self.leave()
            return True
        
        return False
    
    def update_satisfaction(self, dt):
        """Update satisfaction based on surroundings"""
        self.satisfaction -= 0.5 * dt / 60
        
        nearby_animals = [a for a in self.manager.animals.animals 
                          if distance(self.position, a.position) < TILE_SIZE * 10]
        
        if nearby_animals:
            species_seen = set(a.species for a in nearby_animals)
            self.satisfaction += len(species_seen) * 2 * dt / 60
            
            for animal in nearby_animals:
                if animal.species == "elephant" or animal.species == "lion":
                    self.satisfaction += 1 * dt / 60
        
        nearby_buildings = [b for b in self.manager.buildings.buildings 
                           if distance(self.position, b.position) < TILE_SIZE * 3]
        
        on_path = any(b.building_type == "path" for b in nearby_buildings)
        at_platform = any(b.building_type == "viewing_platform" for b in nearby_buildings)
        
        if on_path:
            self.satisfaction += 0.2 * dt / 60
        else:
            self.satisfaction -= 1.0 * dt / 60
        
        if at_platform:
            self.satisfaction += 2.0 * dt / 60
        
        self.satisfaction = max(0, min(100, self.satisfaction))
        
        if self.satisfaction > 80:
            color = GREEN
        elif self.satisfaction > 50:
            color = YELLOW
        elif self.satisfaction > 30:
            color = ORANGE
        else:
            color = RED
            
        size = int(TILE_SIZE * 0.8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
    
    def move(self, dt):
        """Move around the park"""

        if self.waiting_time > 0:
            self.waiting_time -= dt
            return

        if self.path and self.path_index < len(self.path):
            self.target_position = self.path[self.path_index]
            if distance(self.position, self.target_position) < TILE_SIZE / 2:
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.path = []
                    self.target_position = None
                    self.waiting_time = random.uniform(5, 20)
                    return

        if not self.target_position or distance(self.position, self.target_position) < TILE_SIZE:
            self.choose_new_target()
            self.waiting_time = random.uniform(5, 20)
            return

        direction_x = self.target_position[0] - self.position[0]
        direction_y = self.target_position[1] - self.position[1]
        dir_length = math.sqrt(direction_x**2 + direction_y**2)
        if dir_length > 0:
            direction_x /= dir_length
            direction_y /= dir_length

        speed = self.speed * dt
        move_x = direction_x * speed
        move_y = direction_y * speed
        new_pos = (self.position[0] + move_x, self.position[1] + move_y)

        if not self.terrain.is_water_at_position(new_pos):
            self.position = new_pos
            self.rect.center = self.position

    
    def choose_new_target(self):
        """Choose a new target to move towards"""

        if not self.path:
            start_tile = self.terrain.world_to_grid(self.position)
            path = self.terrain.find_path(start_tile, self.terrain.exit_tile)
            if path:
                self.path = [self.terrain.grid_to_world(p) for p in path]
                self.path_index = 0
                self.target_position = self.path[self.path_index]
                return
            else:
                self.path = []

        paths = [b for b in self.manager.buildings.buildings 
                if b.building_type == "path"]
        platforms = [b for b in self.manager.buildings.buildings 
                    if b.building_type == "viewing_platform"]
        animals = self.manager.animals.animals

        if random.random() < 0.7 and paths:
            target = random.choice(paths)
            self.target_position = target.position
        elif random.random() < 0.8 and platforms:
            target = random.choice(platforms)
            self.target_position = target.position
        elif random.random() < 0.9 and animals:
            target = random.choice(animals)
            self.target_position = target.position
        else:
            terrain_size = self.terrain.size * TILE_SIZE
            x = random.uniform(-terrain_size / 2, terrain_size / 2)
            y = random.uniform(-terrain_size / 2, terrain_size / 2)
            while self.terrain.is_water_at_position((x, y)):
                x = random.uniform(-terrain_size / 2, terrain_size / 2)
                y = random.uniform(-terrain_size / 2, terrain_size / 2)
            self.target_position = (x, y)

    
    def spend_money(self):
        """Tourist spends money based on their satisfaction"""
        spending = self.spending_rate * (self.satisfaction / 50)
        
        self.manager.game_state.add_funds(spending)
    
    def leave(self):
        """Tourist leaves the park"""
        if self in self.manager.tourists:
            self.manager.tourists.remove(self)
            self.manager.tourists_group.remove(self)
        
        review_score = max(1, min(5, int(self.satisfaction / 20)))
        self.manager.add_review(review_score)
