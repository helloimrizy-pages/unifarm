import pygame
from building import Building
from constants import *
from utils import distance

class BuildingManager:
    def __init__(self, game_state, terrain):
        self.game_state = game_state
        self.terrain = terrain
        self.buildings = []
        self.buildings_group = pygame.sprite.Group()
        
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
    
    def place_building(self, building_type, position):
        """Place a new building at the specified position"""
        cost = self.building_config[building_type]["cost"]
        if self.game_state.funds < cost:
            self.game_state.add_notification(f"Not enough funds to build {building_type}")
            return None
        
        if not self.terrain.is_suitable_for_building(position):
            self.game_state.add_notification(f"Cannot build {building_type} on this terrain")
            return None
        
        if self.is_position_occupied(position):
            self.game_state.add_notification(f"Cannot build {building_type} here: space occupied")
            return None
        
        building = Building(building_type, position, self)
        self.buildings_group.add(building)
        return building
    
    def is_position_occupied(self, position):
        """Check if the position is already occupied by another building"""
        for building in self.buildings:
            if distance(building.position, position) < TILE_SIZE * 2:
                return True
        return False
    
    def update(self, dt):
        """Update all buildings"""
        for building in list(self.buildings):
            building.step(dt)
            
            if building.health <= 0:
                self.remove_building(building)
    
    def remove_building(self, building):
        """Remove a building from the game"""
        if building in self.buildings:
            self.buildings.remove(building)
            self.buildings_group.remove(building)
            self.game_state.add_notification(f"{building.building_type} has broken down completely")
    
    def render(self, screen, camera_offset):
        """Render all buildings with camera offset"""
        for building in self.buildings:
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
        
        path_count = len([b for b in self.buildings if b.building_type == "path"])
        platform_count = len([b for b in self.buildings if b.building_type == "viewing_platform"])
        
        base_score = min(80, path_count * 5 + platform_count * 15)
        
        avg_health = sum(b.health for b in self.buildings) / len(self.buildings)
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
