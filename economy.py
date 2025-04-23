import random
import math
from ursina import *

class Tourist(Entity):
    def __init__(self, position, economy_manager):
        super().__init__(
            model='sphere',
            color=color.rgba(255, 105, 180, 255),
            scale=(0.5, 1, 0.5),
            position=position,
            name=f"tourist_{id(self)}"
        )
        
        self.manager = economy_manager
        self.terrain = economy_manager.terrain
        self.game_state = economy_manager.game_state
        
        self.speed = random.uniform(2.0, 4.0)
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
                         if distance(self, a) < 10]
        
        if nearby_animals:
            species_seen = set(a.species for a in nearby_animals)
            self.satisfaction += len(species_seen) * 2 * dt / 60
            
            for animal in nearby_animals:
                if animal.species == "elephant" or animal.species == "lion":
                    self.satisfaction += 1 * dt / 60
        
        nearby_buildings = [b for b in self.manager.buildings.buildings 
                           if distance(self, b) < 3]
        
        on_path = any(b.building_type == "path" for b in nearby_buildings)  # Changed from "walking_path" to "path"
        at_platform = any(b.building_type == "viewing_platform" for b in nearby_buildings)
        
        if on_path:
            self.satisfaction += 0.2 * dt / 60
        else:
            self.satisfaction -= 1.0 * dt / 60
        
        if at_platform:
            self.satisfaction += 2.0 * dt / 60
        
        self.satisfaction = max(0, min(100, self.satisfaction))
    
    def move(self, dt):
        """Move around the park"""
        if self.waiting_time > 0:
            self.waiting_time -= dt
            return
        
        if not self.target_position or distance(self, self.target_position) < 1:
            self.choose_new_target()
            self.waiting_time = random.uniform(5, 20)
            return
        
        direction = self.target_position - self.position
        if direction.length() > 0:
            direction = direction.normalized()
        
        speed = self.speed * dt
        self.position += direction * speed
        
        terrain_height = self.terrain.get_height_at_position(self.position)
        self.y = terrain_height + 1
        
        if direction.length() > 0:
            self.look_at(self.position + direction)
            self.rotation_x = 0
    
    def choose_new_target(self):
        """Choose a new target to move towards"""
        paths = [b for b in self.manager.buildings.buildings 
               if b.building_type == "path"]  # Changed from "walking_path" to "path"
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
            x = random.uniform(-self.terrain.size/2, self.terrain.size/2)
            z = random.uniform(-self.terrain.size/2, self.terrain.size/2)
            
            while self.terrain.is_water_at_position((x, 0, z)):
                x = random.uniform(-self.terrain.size/2, self.terrain.size/2)
                z = random.uniform(-self.terrain.size/2, self.terrain.size/2)
            
            self.target_position = Vec3(x, 0, z)
    
    def spend_money(self):
        """Tourist spends money based on their satisfaction"""
        spending = self.spending_rate * (self.satisfaction / 50)
        
        self.manager.game_state.add_funds(spending)
    
    def leave(self):
        """Tourist leaves the park"""
        if self in self.manager.tourists:
            self.manager.tourists.remove(self)
        
        review_score = max(1, min(5, int(self.satisfaction / 20)))
        self.manager.add_review(review_score)
        
        destroy(self)


class EconomyManager:
    def __init__(self, game_state, animal_manager, building_manager):
        self.game_state = game_state
        self.animals = animal_manager
        self.buildings = building_manager
        self.terrain = building_manager.terrain
        
        self.tourists = []
        self.reviews = []
        self.avg_review_score = 3.0
        self.daily_income = 0
        self.monthly_expenses = 0
        
        self.day_timer = 0
        self.month_timer = 0
        
        self.base_tourist_rate = 5
        self.tourist_modifier = self.game_state.difficulty_settings["tourist_rate"]
        self.entrance_fee = 20
    
    def update(self, dt):
        """Update economic systems"""
        self.day_timer += dt
        self.month_timer += dt
        
        if self.day_timer >= 120:
            self.day_timer = 0
            self.daily_update()
        
        if self.month_timer >= 120 * 30:
            self.month_timer = 0
            self.monthly_update()
        
        self.update_tourists(dt)
        
        self.spawn_tourists(dt)
    
    def daily_update(self):
        """Perform daily economic updates"""
        income = self.daily_income
        
        self.daily_income = 0
        
        self.game_state.add_notification(f"Daily revenue: ${income:.2f}")
    
    def monthly_update(self):
        """Perform monthly economic updates"""
        maintenance_cost = self.buildings.get_monthly_maintenance_cost()
        
        animal_food_cost = 0
        for animal in self.animals.animals:
            species_config = self.animals.species_config[animal.species]
            food_cost = species_config["food_consumption"] * 100
            animal_food_cost += food_cost
        
        staff_salary = 1000
        
        total_expenses = maintenance_cost + animal_food_cost + staff_salary
        
        self.game_state.add_funds(-total_expenses)
        
        self.monthly_expenses = 0
        
        self.game_state.add_notification(f"Monthly expenses: ${total_expenses:.2f}")
        self.game_state.add_notification(f"Current funds: ${self.game_state.funds:.2f}")
    
    def update_tourists(self, dt):
        """Update all tourists"""
        for tourist in list(self.tourists):
            if tourist.step(dt):
                pass
    
    def spawn_tourists(self, dt):
        """Spawn new tourists based on park reputation and time of day"""
        hour = (self.game_state.time_of_day) % 24
        
        if 8 <= hour <= 18:
            spawn_chance = 0.1 * dt
        else:
            spawn_chance = 0.01 * dt
        
        reputation_factor = (self.avg_review_score / 3)
        animal_appeal = self.animals.get_tourist_appeal() / 100
        infrastructure = self.buildings.calculate_tourist_infrastructure_score() / 100
        
        park_attractiveness = (reputation_factor * 0.3) + (animal_appeal * 0.5) + (infrastructure * 0.2)
        
        spawn_chance *= park_attractiveness * self.tourist_modifier
        
        max_tourists = 30
        current_tourists = len(self.tourists)
        if current_tourists >= max_tourists:
            return
        
        if random.random() < spawn_chance:
            entrance_x = self.terrain.size / 2 - 5
            entrance_z = 0
            entrance_pos = Vec3(entrance_x, 1, entrance_z)
            
            tourist = Tourist(entrance_pos, self)
            self.tourists.append(tourist)
            
            self.game_state.add_funds(self.entrance_fee)
            self.daily_income += self.entrance_fee
    
    def add_review(self, score):
        """Add a review score (1-5) and update average"""
        self.reviews.append(score)
        
        if len(self.reviews) > 100:
            self.reviews.pop(0)
        
        self.avg_review_score = sum(self.reviews) / len(self.reviews)
    
    def get_park_stats(self):
        """Get statistics about the park's performance"""
        return {
            "tourists": len(self.tourists),
            "review_score": self.avg_review_score,
            "animal_appeal": self.animals.get_tourist_appeal(),
            "infrastructure": self.buildings.calculate_tourist_infrastructure_score(),
            "daily_income": self.daily_income,
            "monthly_expenses": self.monthly_expenses
        }


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