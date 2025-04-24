import pygame
import random
import math
from constants import *
from utils import distance

class Animal(pygame.sprite.Sprite):
    def __init__(self, species, position, terrain, animal_manager):
        super().__init__()
        
        config = animal_manager.species_config[species]
        
        width = int(config['scale'][0] * TILE_SIZE)
        height = int(config['scale'][1] * TILE_SIZE)
        
        self.base_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.base_image.fill(animal_manager.species_colors[species])
        
        pygame.draw.circle(self.base_image, BLACK, 
                          (int(width * 0.7), int(height * 0.5)), 
                          int(width * 0.15))
        
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.species = species
        self.position = position
        self.terrain = terrain
        self.manager = animal_manager
        self.game_state = animal_manager.game_state
        self.age = random.uniform(0.2, 1.0)
        self.group_id = random.randint(1000, 9999)
        self.speed = max(30, config['speed'] * self.age * (TILE_SIZE / 32))

        
        self.hunger = random.randint(50, 80)
        self.thirst = random.randint(50, 80)
        self.health = random.randint(70, 100)
        self.energy = random.randint(70, 100)
        
        self.state = "idle"
        self.target = None
        self.target_position = None
        self.wandering = False
        self.wander_timer = 0
        self.need_threshold = 70
        
        self.rotation = 0
        
        self.need_rate = self.game_state.difficulty_settings["animal_need_rate"]
    
    def step(self, dt):
        """Update animal state and perform actions"""
        self.hunger += 0.5 * dt * self.need_rate
        self.thirst += 0.7 * dt * self.need_rate
        self.energy -= 0.3 * dt
        
        self.hunger = min(100, self.hunger)
        self.thirst = min(100, self.thirst)
        self.energy = min(100, self.energy)
        
        if self.hunger > 90 or self.thirst > 90:
            self.health -= 0.5 * dt
        else:
            self.health = min(100, self.health + 0.1 * dt)
        
        self.decide_action()
        
        if self.state == "seeking_food":
            self.seek_food(dt)
        elif self.state == "seeking_water":
            self.seek_water(dt)
        elif self.state == "resting":
            self.rest(dt)
        else:
            self.wander(dt)
        
        self.rect.center = self.position
    
    def decide_action(self):
        """Decide what action to take based on current needs"""
        if self.health < 20:
            if self.hunger > self.thirst:
                self.state = "seeking_food"
            else:
                self.state = "seeking_water"
            return
        
        if self.energy < 20:
            self.state = "resting"
            return
        
        if self.hunger > self.need_threshold:
            self.state = "seeking_food"
        elif self.thirst > self.need_threshold:
            self.state = "seeking_water"
        elif not self.wandering:
            self.state = "idle"
    
    def seek_food(self, dt):
        """Seek out food sources"""
        if not self.is_feeding_station(self.target):
            feeding_stations = [b for b in self.manager.buildings.buildings 
                               if b.building_type == "feeding_station"]
            
            if feeding_stations:
                closest = min(feeding_stations, key=lambda b: distance(self.position, b.position))
                self.target = closest
                self.target_position = closest.position
            else:
                grass_locations = self.find_grass_locations()
                if grass_locations:
                    self.target_position = random.choice(grass_locations)
                else:
                    self.state = "idle"
                    return
        
        if self.target_position:
            self.move_to_target(dt)
            
            if distance(self.position, self.target_position) < TILE_SIZE * 2:
                self.hunger = max(0, self.hunger - 30)
                self.state = "idle"
                self.target = None
                self.target_position = None

    @staticmethod
    def is_water_station(target):
        try:
            return getattr(target, "building_type", None) == "water_station" or \
                (isinstance(target, dict) and target.get("building_type") == "water_station")
        except:
            return False

    @staticmethod
    def is_feeding_station(target):
        try:
            return getattr(target, "building_type", None) == "feeding_station" or \
                (isinstance(target, dict) and target.get("building_type") == "feeding_station")
        except:
            return False
        
    def seek_water(self, dt):
        """Seek out water sources"""
        if not self.is_water_station(self.target):
            water_stations = [b for b in self.manager.buildings.buildings 
                            if b.building_type == "water_station"]

            if water_stations:
                closest = min(water_stations, key=lambda b: distance(self.position, b.position))
                self.target = closest
                self.target_position = closest.position
            else:
                water_locations = self.find_water_locations()
                if water_locations:
                    self.target_position = random.choice(water_locations)
                    self.target = {'position': self.target_position, 'building_type': 'natural_water'}
                else:
                    self.state = "idle"
                    return

        if self.target_position:
            blocked = not self.move_to_target(dt)
            
            if not blocked and distance(self.position, self.target_position) < TILE_SIZE * 2:
                self.thirst = max(0, self.thirst - 40)
                self.state = "idle"
                self.target = None
                self.target_position = None
            elif blocked:
                self.target_position = None
                self.target = None
    
    def rest(self, dt):
        """Rest to regain energy"""
        self.wandering = False
        
        self.energy += 1.0 * dt
        
        if self.energy > 80:
            self.state = "idle"
    
    def wander(self, dt):
        if not self.wandering:
            if hasattr(self, "group_center") and self.group_center:
                gx, gy = self.group_center
                jitter = TILE_SIZE * 3
                x = gx + random.uniform(-jitter, jitter)
                y = gy + random.uniform(-jitter, jitter)
                self.target_position = (x, y)
            else:
                wander_range = 10 * TILE_SIZE
                x = self.position[0] + random.uniform(-wander_range, wander_range)
                y = self.position[1] + random.uniform(-wander_range, wander_range)
                self.target_position = (x, y)
            self.wandering = True
            self.wander_timer = random.uniform(5, 15)

        if self.wandering:
            self.move_to_target(dt)
            self.wander_timer -= dt

            if self.target_position and (distance(self.position, self.target_position) < TILE_SIZE or self.wander_timer <= 0):
                self.wandering = False
                self.wander_timer = random.uniform(2, 5)

    def move_to_target(self, dt):
        """Move toward target position"""
        if not self.target_position:
            return False

        direction_x = self.target_position[0] - self.position[0]
        direction_y = self.target_position[1] - self.position[1]
        
        dir_length = math.hypot(direction_x, direction_y)
        if dir_length == 0:
            return False

        direction_x /= dir_length
        direction_y /= dir_length
        
        speed = self.speed * dt
        move_x = direction_x * speed
        move_y = direction_y * speed
        new_pos = (self.position[0] + move_x, self.position[1] + move_y)

        if (self.terrain.is_water_at_position(new_pos) and 
            self.species != "crocodile" and 
            self.state != "seeking_water"):
            return False


        self.position = new_pos
        self.rect.center = self.position
        self.rotation = math.degrees(math.atan2(direction_y, direction_x))
        self.image = pygame.transform.rotate(self.base_image, -self.rotation + 90)

        return True

    def find_grass_locations(self):
        """Find suitable grass locations for food"""
        grass_locations = []
        
        search_radius = 20 * TILE_SIZE
        step = 5 * TILE_SIZE
        
        for x_offset in range(-int(search_radius), int(search_radius) + 1, int(step)):
            for y_offset in range(-int(search_radius), int(search_radius) + 1, int(step)):
                pos = (self.position[0] + x_offset, self.position[1] + y_offset)
                if self.terrain.get_terrain_at_position(pos) == "grass":
                    grass_locations.append(pos)
        
        return grass_locations
    
    def find_water_locations(self):
        """Find suitable water locations for drinking"""
        water_locations = []
        
        search_radius = 30 * TILE_SIZE
        step = 5 * TILE_SIZE
        
        for x_offset in range(-int(search_radius), int(search_radius) + 1, int(step)):
            for y_offset in range(-int(search_radius), int(search_radius) + 1, int(step)):
                pos = (self.position[0] + x_offset, self.position[1] + y_offset)
                if self.terrain.is_water_at_position(pos):
                    water_locations.append(pos)
        
        return water_locations

