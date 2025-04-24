import pygame
import json
from building import Building

from constants import *
from utils import distance
from types import SimpleNamespace
class BuildingManager:
    def __init__(self, game_state, terrain):
        self.game_state = game_state
        self.terrain = terrain
        self.buildings = []
        self.buildings_group = pygame.sprite.Group()
        self.pending_building_type = None
        
        self.entrance_tile = None
        self.exit_tile     = None

        self.building_config = {
            "feeding_station": {
                "scale": (2, 2),
                "cost": 500,
                "maintenance_cost": 50,
                "color": ORANGE,
                "effectiveness": 1.0
            },
            "water_station": {
                "scale": (2, 2),
                "cost": 400,
                "maintenance_cost": 40,
                "color": BLUE,
                "effectiveness": 1.0
            },
            "path": {
                "scale": (1, 1),
                "cost": 100,
                "maintenance_cost": 10,
                "color": BROWN,
                "effectiveness": 1.0
            },
            "viewing_platform": {
                "scale": (3, 3),
                "cost": 700,
                "maintenance_cost": 50,
                "color": LIGHT_GRAY,
                "effectiveness": 1.0
            },
            "tree": {
                "scale": (1, 2),
                "cost": 50,
                "maintenance_cost": 5,
                "color": DARK_GRAY,
            },
            "bush": {
                "scale": (1, 0.5),
                "cost": 30,
                "maintenance_cost": 3,
                "color": GREEN,
            },
            "flower": {
                "scale": (0.5, 0.5),
                "cost": 20,
                "maintenance_cost": 2,
                "color": (128, 0, 255),
            },
            "pond": {
                "scale": (2, 2),
                "cost": 100,
                "maintenance_cost": 10,
                "color": LIGHT_BLUE,
            },
            "road": {
                "scale": (1, 1),
                "cost": 100,
                "maintenance_cost": 5,
                "color": BROWN,
            },
        }
    
    def place_building(self, building_type, world_pos):
        self.pending_building_type = building_type

        if self.is_position_occupied(world_pos):
            self.game_state.add_notification("Can't build there!")
            return False

        cost = self.building_config[building_type]["cost"]
        self.game_state.add_funds(-cost)

        if building_type == "path":
            gx, gy = self.terrain.world_to_grid(world_pos)
            self.terrain.terrain_grid[gy][gx]["type"] = "path"

            tx, ty = gx * TILE_SIZE, gy * TILE_SIZE
            pygame.draw.rect(self.terrain.terrain_surface,
                            self.building_config["path"]["color"],
                            (tx, ty, TILE_SIZE, TILE_SIZE))

            cell = (gx, gy)
            self.buildings.append(SimpleNamespace(
                building_type="path",
                position=self.terrain.grid_to_world(cell),
                rect=pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE),
                grid_pos=cell
            ))

            if self.entrance_tile is None:
                self.entrance_tile = cell
                self.terrain.entrance_tile = cell

            self.exit_tile = cell
            self.terrain.exit_tile = cell

            self.game_state.add_notification(f"Built road for ${cost}")
            return True


        b = Building(building_type, world_pos, self)
        self.buildings.append(b)
        self.game_state.add_notification(f"Built {building_type} for ${cost}")
        return True


    def snap_to_grid(self, position):
        grid_x, grid_y = self.world_to_grid(position)
        return self.grid_to_world((grid_x, grid_y))

    def is_position_occupied(self, world_pos):
            """
            True only if new building’s rect would *overlap* an existing one.
            Adjacent (=touching) is OK.
            """
            cfg = self.building_config.get(self.pending_building_type, {})
            w = int(cfg.get("scale",(1,1))[0] * TILE_SIZE)
            h = int(cfg.get("scale",(1,1))[1] * TILE_SIZE)
            new_rect = pygame.Rect(0,0,w,h)
            new_rect.center = world_pos

            for b in self.buildings:
                if new_rect.colliderect(b.rect):
                    return True
            return False
    
    def update(self, dt):
        """Update all non-road buildings each frame."""
        for b in list(self.buildings):
            if getattr(b, "building_type", None) != "path":
                b.step(dt)
    
    def remove_building(self, building):
        """Remove a building from the game"""
        if building in self.buildings:
            self.buildings.remove(building)
            self.buildings_group.remove(building)
            self.game_state.add_notification(f"{building.building_type} has broken down completely")
    
    def render(self, screen, camera_offset):
        """Render all buildings with camera offset"""
        for building in self.buildings:
            if not hasattr(building, "image"):
                continue

            screen_pos = (building.position[0] - camera_offset[0], 
                        building.position[1] - camera_offset[1])
            
            if (screen_pos[0] < -100 or screen_pos[0] > SCREEN_WIDTH + 100 or
                screen_pos[1] < -100 or screen_pos[1] > SCREEN_HEIGHT + 100):
                continue
            
            rect = building.image.get_rect()
            rect.center = screen_pos
            
            screen.blit(building.image, rect)
    
    def get_monthly_maintenance_cost(self):
        """Calculate the total monthly maintenance cost for all buildings"""
        total_cost = 0
        for building in self.buildings:
            cost = self.building_config[building.building_type]["maintenance_cost"]
            health_factor = 1 + (1 - building.health / 100) 
            total_cost += cost * health_factor
        
        return total_cost
    
    def calculate_tourist_infrastructure_score(self):
        """Calculate a score for tourist infrastructure"""
        if not self.buildings:
            return 0

        path_count = len([b for b in self.buildings if getattr(b, "building_type", None) == "path"])
        platform_count = len([b for b in self.buildings if getattr(b, "building_type", None) == "viewing_platform"])

        base_score = min(80, path_count * 5 + platform_count * 15)

        buildings_with_health = [b for b in self.buildings if hasattr(b, "health")]

        if not buildings_with_health:
            return base_score

        avg_health = sum(b.health for b in buildings_with_health) / len(buildings_with_health)
        health_factor = avg_health / 100

        return base_score * health_factor
    
    def save_buildings(self, filename="buildings.json"):
        """Save building data to a file"""
        building_data = []
        
        for building in self.buildings:
            data = {
                "building_type": building.building_type,
                "position": [building.position[0], building.position[1]],
                "health": building.health
            }
            building_data.append(data)
        
        with open(filename, 'w') as f:
            json.dump(building_data, f)
        
        return True
    
    def load_buildings(self, filename="buildings.json"):
        """Load building data from a file"""
        try:
            with open(filename, 'r') as f:
                building_data = json.load(f)
            
            for building in list(self.buildings):
                self.remove_building(building)
            
            for data in building_data:
                position = (data["position"][0], data["position"][1])
                building = Building(data["building_type"], position, self)
                building.health = data["health"]
                self.buildings_group.add(building)
            
            return True
        except Exception as e:
            print(f"Error loading buildings: {str(e)}")
            return False
