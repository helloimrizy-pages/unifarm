import pygame
import random
from tourist import Tourist
from constants import *

class EconomyManager:
    def __init__(self, game_state, animal_manager, building_manager):
        self.game_state = game_state
        self.animals = animal_manager
        self.buildings = building_manager
        self.terrain = building_manager.terrain
        
        self.tourists = []
        self.tourists_group = pygame.sprite.Group()
        self.reviews = []
        self.avg_review_score = 3.0
        self.daily_income = 0
        self.monthly_expenses = 0
        
        self.day_timer = 0
        self.month_timer = 0
        
        self.base_tourist_rate = 5
        self.tourist_modifier = self.game_state.difficulty_settings["tourist_rate"]
        self.entrance_fee = 20
        
        self.vehicle_manager = None
    
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

        self.game_state.evaluate_monthly_win_conditions(
            visitor_count = len(self.tourists),
            herbivores    = self.count_species(["elephant", "zebra"]),
            carnivores    = self.count_species(["lion"])
        )
    
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
            terrain_size = self.terrain.size * TILE_SIZE
            entrance_x = terrain_size / 2 - 5 * TILE_SIZE
            entrance_y = 0
            entrance_pos = (entrance_x, entrance_y)
            
            tourist = Tourist(entrance_pos, self)
            self.tourists.append(tourist)
            self.tourists_group.add(tourist)
            
            self.game_state.add_funds(self.entrance_fee)
            self.daily_income += self.entrance_fee
    
    def add_review(self, score):
        """Add a review score (1-5) and update average"""
        self.reviews.append(score)
        
        if len(self.reviews) > 100:
            self.reviews.pop(0)
        
        self.avg_review_score = sum(self.reviews) / len(self.reviews) if self.reviews else 3.0
    
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
        
    def render(self, screen, camera_offset):
        """Render all tourists with camera offset"""
        for tourist in self.tourists:
            screen_pos = (tourist.position[0] - camera_offset[0], 
                         tourist.position[1] - camera_offset[1])
            
            if (screen_pos[0] < -50 or screen_pos[0] > SCREEN_WIDTH + 50 or
                screen_pos[1] < -50 or screen_pos[1] > SCREEN_HEIGHT + 50):
                continue
            
            rect = tourist.image.get_rect()
            rect.center = screen_pos
            
            screen.blit(tourist.image, rect)