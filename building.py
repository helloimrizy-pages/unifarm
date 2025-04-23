import pygame
from constants import *

class Building(pygame.sprite.Sprite):
    def __init__(self, building_type, position, building_manager):
        super().__init__()
        
        config = building_manager.building_config[building_type]
        
        width = int(config['scale'][0] * TILE_SIZE)
        height = int(config['scale'][1] * TILE_SIZE)
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(config['color'])
        
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.building_type = building_type
        self.position = position
        self.game_state = building_manager.game_state
        self.building_manager = building_manager
        self.terrain = building_manager.terrain
        
        self.health = 100
        self.last_maintenance = 0
        
        building_manager.buildings.append(self)
        
        cost = config['cost']
        building_manager.game_state.add_funds(-cost)
        building_manager.game_state.add_notification(f"Built {building_type} for ${cost}")
    
    def step(self, dt):
        """Update building state"""
        self.health -= 0.1 * dt
        
        if self.health < 30:
            if self.building_type == "feeding_station":
                self.health -= 0.2 * dt
        
        terrain_type = self.terrain.get_terrain_at_position(self.position)
        if terrain_type == "water":
            self.health -= 0.3 * dt
        
        self.health = max(0, self.health)
        
        if self.health < 30:
            config = self.building_manager.building_config[self.building_type]
            base_color = config['color']
            new_color = lerp_color(base_color, RED, 0.5)
            
            width, height = self.image.get_size()
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill(new_color)
    
    def perform_maintenance(self):
        """Perform maintenance on the building"""
        damage = 100 - self.health
        cost = damage * 0.5
        
        if self.game_state.funds >= cost:
            self.game_state.add_funds(-cost)
            
            self.health = 100
            
            config = self.building_manager.building_config[self.building_type]
            
            width, height = self.image.get_size()
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill(config['color'])
            
            self.game_state.add_notification(f"Repaired {self.building_type} for ${cost:.2f}")
            return True
        else:
            self.game_state.add_notification(f"Not enough funds to repair {self.building_type}")
            return False
