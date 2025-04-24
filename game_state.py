import pygame
import json
from datetime import datetime
from constants import *

class GameSpeed:
    PAUSED = 0
    HOUR   = 1
    DAY    = 6
    WEEK   = 18

    LABELS = {
        PAUSED: "Paused",
        HOUR:   "Hour",
        DAY:    "Day",
        WEEK:   "Week"
    }
class GameState:
    def __init__(self, difficulty="medium", day=1, time_of_day=0, funds=None, ecosystem_balance=100):
        self.difficulty = difficulty
        self.day = day
        self.time_of_day = time_of_day
        self.game_speed = 0
        self.time_elapsed = 0

        self.load_difficulty_settings()

        if funds is not None:
            self.funds = funds

        self.animal_stats = {}
        self.ecosystem_balance = ecosystem_balance
        self.notifications = []
    
    @classmethod
    def load(cls, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(
            difficulty=data["difficulty"],
            day=data["day"],
            time_of_day=data["time_of_day"],
            funds=data["funds"],
            ecosystem_balance=data["ecosystem_balance"]
        )
    
    def load_difficulty_settings(self):
        self.settings = {
            "easy": {
                "starting_funds": 10000,
                "animal_need_rate": 0.7,
                "tourist_rate": 1.3,
                "building_costs": 0.8,
                "win_profit_target": 20000
            },
            "medium": {
                "starting_funds": 7000,
                "animal_need_rate": 1.0,
                "tourist_rate": 1.0,
                "building_costs": 1.0,
                "win_profit_target": 25000
            },
            "hard": {
                "starting_funds": 5000,
                "animal_need_rate": 1.3,
                "tourist_rate": 0.7,
                "building_costs": 1.2,
                "win_profit_target": 30000
            }
        }
        
        self.difficulty_settings = self.settings[self.difficulty]
        self.funds = self.difficulty_settings["starting_funds"]
        self.profit_target = self.difficulty_settings["win_profit_target"]
    
    def update(self, dt):
        self.time_elapsed += dt
        self.time_of_day += dt * 0.2
        
        if self.time_of_day >= 24:
            self.time_of_day = 0
            self.day += 1
            self.add_notification(f"Day {self.day} has begun")
    
    def set_game_speed(self, speed):
        """Toggle pause/resume and track last non‐zero speed."""
        if speed == GameSpeed.PAUSED and self.game_speed == GameSpeed.PAUSED:
            speed = self.last_nonzero_speed
        elif speed != GameSpeed.PAUSED:
            self.last_nonzero_speed = speed

        self.game_speed = speed
        self.add_notification(f"Game speed: {GameSpeed.LABELS[speed]}")

    
    def add_funds(self, amount):
        """Add or subtract funds"""
        self.funds += amount
        return self.funds
    
    def add_notification(self, message):
        """Add a notification to the queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.notifications.append({"time": timestamp, "message": message})
        
        if len(self.notifications) > 10:
            self.notifications.pop(0)
    
    def update_ecosystem_balance(self, animal_stats):
        """Update ecosystem balance based on animal health and population"""
        self.animal_stats = animal_stats
        
        if not animal_stats:
            self.ecosystem_balance = 0
            return
        
        total_health = 0
        species_count = 0
        
        for species, stats in animal_stats.items():
            if stats["population"] > 0:
                species_count += 1
                total_health += stats["avg_health"] * stats["population"]
        
        total_animals = sum(stats["population"] for stats in animal_stats.values())
        
        if total_animals > 0:
            avg_health = total_health / total_animals
            self.ecosystem_balance = min(100, (avg_health * 0.7) + (species_count / len(animal_stats) * 100 * 0.3))
        else:
            self.ecosystem_balance = 0
    
    def check_win_condition(self):
        """Check if the player has met the win conditions"""
        return self.funds >= self.profit_target and self.ecosystem_balance >= 75
    
    def check_lose_condition(self):
        """Check if the player has lost the game"""
        return self.funds < 0 or self.ecosystem_balance < 20
    
    def save_game(self, filename="savegame.json"):
        """Save current game state to a file"""
        save_data = {
            "difficulty": self.difficulty,
            "day": self.day,
            "time_of_day": self.time_of_day,
            "funds": self.funds,
            "ecosystem_balance": self.ecosystem_balance,
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f)
        
        self.add_notification(f"Game saved to {filename}")
        return True
    
    def load_game(self, filename="savegame.json"):
        """Load game state from a file"""
        if not path.exists(filename):
            self.add_notification(f"Save file {filename} not found")
            return False
        
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.difficulty = save_data["difficulty"]
            self.day = save_data["day"]
            self.time_of_day = save_data["time_of_day"]
            self.funds = save_data["funds"]
            self.ecosystem_balance = save_data["ecosystem_balance"]
            
            self.load_difficulty_settings()
            
            self.add_notification(f"Game loaded from {filename}")
            return True
        except Exception as e:
            self.add_notification(f"Error loading game: {str(e)}")
            return False
