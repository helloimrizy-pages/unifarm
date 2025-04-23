from ursina import *
import json
import math

class Building(Entity):
    def __init__(self, building_type, position, building_manager):
        config = building_manager.building_config[building_type]
        
        super().__init__(
            model=config['model'],
            texture=config['texture'],
            scale=config['scale'],
            position=position,
            collider='box',
            name=f"{building_type}_{id(self)}"
        )
        
        self.building_type = building_type
        self.game_state = building_manager.game_state
        self.building_manager = building_manager
        self.terrain = building_manager.terrain
        
        if building_type == "feeding_station":
            self.color = color.orange
        elif building_type == "water_station":
            self.color = color.blue
        elif building_type == "path":
            self.color = color.brown
        elif building_type == "viewing_platform":
            self.color = color.light_gray
        
        self.health = 100
        self.last_maintenance = 0
        
        self.y = self.terrain.get_height_at_position(position)
        
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
        
        terrain_type = self.terrain.get_terrain_type_at_position(self.position)
        if terrain_type == "water":
            self.health -= 0.3 * dt
        
        self.health = max(0, self.health)
        
        if self.health < 30:
            self.color = color.lerp(self.color, color.red, 0.5)
    
    def perform_maintenance(self):
        """Perform maintenance on the building"""
        damage = 100 - self.health
        cost = damage * 0.5
        
        if self.game_state.funds >= cost:
            self.game_state.add_funds(-cost)
            
            self.health = 100
            
            config = self.building_manager.building_config[self.building_type]
            self.color = config['color']
            
            self.game_state.add_notification(f"Repaired {self.building_type} for ${cost:.2f}")
            return True
        else:
            self.game_state.add_notification(f"Not enough funds to repair {self.building_type}")
            return False


class BuildingManager:
    def __init__(self, game_state, terrain):
        self.game_state = game_state
        self.terrain = terrain
        self.buildings = []
        
        self.building_config = {
            "feeding_station": {
                "model": "cube",
                "texture": "white_cube",
                "scale": (2, 1, 2),
                "cost": 500,
                "maintenance_cost": 50,
                "color": color.orange,
                "effectiveness": 1.0
            },
            "water_station": {
                "model": "cylinder",
                "texture": "white_cube",
                "scale": (2, 0.5, 2),
                "cost": 400,
                "maintenance_cost": 40,
                "color": color.blue,
                "effectiveness": 1.0
            },
            "path": {
                "model": "cube",
                "texture": "white_cube",
                "scale": (1, 0.2, 1),
                "cost": 100,
                "maintenance_cost": 10,
                "color": color.brown,
                "effectiveness": 1.0
            },
            "viewing_platform": {
                "model": "cube",
                "texture": "white_cube",
                "scale": (3, 1, 3),
                "cost": 700,
                "maintenance_cost": 50,
                "color": color.light_gray,
                "effectiveness": 1.0
            },
            "tree": {
                "model":    "cube",
                "texture":  "white_cube",
                "scale":    (1, 2, 1),
                "cost":     50,
                "maintenance_cost": 5,
                "color":    color.dark_gray,
            },
            "bush": {
                "model":    "sphere",
                "texture":  "white_cube",
                "scale":    (1, 0.5, 1),
                "cost":     30,
                "maintenance_cost": 3,
                "color":    color.green,
            },
            "flower": {
                "model":    "quad",
                "texture":  "white_cube",
                "scale":    (0.5, 0.5, 0.5),
                "cost":     20,
                "maintenance_cost": 2,
                "color":    color.hsv(0.8,1,1),  # a pinkish hue
            },
            "pond": {
                "model":    "Plane",
                "texture":  "white_cube",
                "scale":    (2, 1, 2),
                "cost":     100,
                "maintenance_cost": 10,
                "color":    color.rgba(0, 100, 255, 150),
            },
            "road": {
                "model":    "cube",
                "texture":  "white_cube",
                "scale":    (1, 0.1, 1),
                "cost":     100,
                "maintenance_cost": 5,
                "color":    color.brown,
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
        return building
    
    def is_position_occupied(self, position):
        """Check if the position is already occupied by another building"""
        for building in self.buildings:
            if distance(building.position, position) < 2:
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
            self.game_state.add_notification(f"{building.building_type} has broken down completely")
            destroy(building)
    
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
                "position": [building.x, building.y, building.z],
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
                pos = Vec3(*data["position"])
                building = Building(data["building_type"], pos, self)
                building.health = data["health"]
            
            return True
        except Exception as e:
            print(f"Error loading buildings: {str(e)}")
            return False


def distance(a, b):
    """Calculate distance between two entities or positions"""
    if hasattr(a, 'position'):
        pos_a = a.position
    else:
        pos_a = a
    
    if hasattr(b, 'position'):
        pos_b = b.position
    else:
        pos_b = b
    
    return math.sqrt((pos_a.x - pos_b.x)**2 + (pos_a.z - pos_b.z)**2)