import pygame
from constants import *

class VehicleManager:
    def __init__(self, game_state, buildings, terrain):
        self.game_state = game_state
        self.buildings = buildings
        self.terrain = terrain
        self.vehicles = []
        self.vehicles_group = pygame.sprite.Group()
    
    def purchase_jeep(self):
        """Purchase a jeep for the park"""
        cost = 1000
        if self.game_state.funds < cost:
            self.game_state.add_notification("Not enough funds to purchase a jeep")
            return False
        
        self.game_state.add_funds(-cost)
        self.game_state.add_notification("Purchased a safari jeep!")
        
        # Create jeep sprite
        jeep = pygame.sprite.Sprite()
        jeep_size = (int(TILE_SIZE * 1.5), int(TILE_SIZE))
        jeep.image = pygame.Surface(jeep_size, pygame.SRCALPHA)
        jeep.image.fill(OLIVE)
        jeep.rect = jeep.image.get_rect()
        jeep.rect.center = (0, 0)
        jeep.position = (0, 0)
        
        self.vehicles.append(jeep)
        self.vehicles_group.add(jeep)
        return True
    
    def update(self, dt):
        """Update vehicles (minimal implementation)"""
        for vehicle in self.vehicles:
            if random.random() < 0.02:
                terrain_size = self.terrain.size * TILE_SIZE / 3
                target_x = random.uniform(-terrain_size, terrain_size)
                target_y = random.uniform(-terrain_size, terrain_size)
                
                # Set up movement animation (simplified)
                curr_x, curr_y = vehicle.position
                dx = (target_x - curr_x) / (5 * FPS) # Move over 5 seconds
                dy = (target_y - curr_y) / (5 * FPS)
                
                vehicle.dx = dx
                vehicle.dy = dy
                vehicle.move_timer = 5 * FPS
            
            if hasattr(vehicle, 'move_timer') and vehicle.move_timer > 0:
                # Continue animation
                vehicle.position = (vehicle.position[0] + vehicle.dx, 
                                   vehicle.position[1] + vehicle.dy)
                vehicle.rect.center = vehicle.position
                vehicle.move_timer -= 1
    
    def render(self, screen, camera_offset):
        """Render all vehicles with camera offset"""
        for vehicle in self.vehicles:
            # Check if vehicle is within visible area before rendering
            screen_pos = (vehicle.position[0] - camera_offset[0], 
                         vehicle.position[1] - camera_offset[1])
            
            # Skip rendering if completely off-screen
            if (screen_pos[0] < -100 or screen_pos[0] > SCREEN_WIDTH + 100 or
                screen_pos[1] < -100 or screen_pos[1] > SCREEN_HEIGHT + 100):
                continue
            
            # Calculate position accounting for image size and center
            rect = vehicle.image.get_rect()
            rect.center = screen_pos
            
            screen.blit(vehicle.image, rect)

