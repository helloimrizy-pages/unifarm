import pygame
import random
from animal import Animal
from constants import *

class AnimalManager:
    def __init__(self, game_state, terrain):
        self.game_state = game_state
        self.terrain = terrain
        self.animals = []
        self.animals_group = pygame.sprite.Group()
        self.buildings = None
        
        self.species_config = {
            "elephant": {
                "scale": (1.5, 1.5),
                "speed": 3.0,
                "preferred_terrain": "grass",
                "food_consumption": 2.0,
                "water_consumption": 3.0,
                "tourist_appeal": 3.0
            },
            "lion": {
                "scale": (1.0, 1.0),
                "speed": 5.0,
                "preferred_terrain": "grass",
                "food_consumption": 1.5,
                "water_consumption": 1.0,
                "tourist_appeal": 3.5
            },
            "zebra": {
                "scale": (1.2, 0.8),
                "speed": 4.0,
                "preferred_terrain": "grass",
                "food_consumption": 1.0,
                "water_consumption": 1.0,
                "tourist_appeal": 2.0
            }
        }
        
        self.species_colors = {
            "elephant": GRAY,
            "lion": YELLOW,
            "zebra": WHITE
        }
        
        self.initial_population = {
            "elephant": 5,
            "lion": 5,
            "zebra": 10
        }
        
        self.spawn_initial_animals()
    
    def set_building_manager(self, building_manager):
        """Set the building manager (needed to find food/water sources)"""
        self.buildings = building_manager
    
    def spawn_initial_animals(self):
        """Spawn the initial animal population"""
        for species, count in self.initial_population.items():
            for _ in range(count):
                self.spawn_animal(species)
    
    def spawn_animal(self, species, nearby=None, group_id=None):
        spawn_position = self.find_spawn_position(species, nearby)
        animal = Animal(species, spawn_position, self.terrain, self)
        if group_id is not None:
            animal.group_id = group_id
        else:
            animal.group_id = random.randint(1000, 9999)

        self.animals.append(animal)
        self.animals_group.add(animal)
        return animal

    def find_spawn_position(self, species, nearby=None):
        if nearby:
            for _ in range(20):
                dx = random.uniform(-TILE_SIZE * 3, TILE_SIZE * 3)
                dy = random.uniform(-TILE_SIZE * 3, TILE_SIZE * 3)
                pos = (nearby[0] + dx, nearby[1] + dy)
                terrain_type = self.terrain.get_terrain_at_position(pos)
                if species == "crocodile" and terrain_type == "water":
                    return pos
                elif terrain_type == "grass":
                    return pos

        for _ in range(100):
            x = random.uniform(-self.terrain.size * TILE_SIZE / 2, self.terrain.size * TILE_SIZE / 2)
            y = random.uniform(-self.terrain.size * TILE_SIZE / 2, self.terrain.size * TILE_SIZE / 2)
            pos = (x, y)
            terrain_type = self.terrain.get_terrain_at_position(pos)
            if species == "crocodile" and terrain_type == "water":
                return pos
            elif terrain_type == "grass":
                return pos

        return (0, 0)


    def update(self, dt):
        """Update all animals"""
        for animal in list(self.animals):
            animal.step(dt)
            
            if animal.health <= 0:
                self.remove_animal(animal)
        
        self.update_animal_stats()
        
        self.try_natural_spawning(dt)
        self.try_group_reproduction(dt)
        self.update_group_movement(dt)
    
    def remove_animal(self, animal):
        """Remove an animal from the simulation"""
        if animal in self.animals:
            self.animals.remove(animal)
            self.animals_group.remove(animal)
    
    def update_animal_stats(self):
        """Update game state with statistics about animal populations"""
        stats = {}
        
        for species in self.species_config:
            stats[species] = {
                "population": 0,
                "avg_health": 0,
                "avg_hunger": 0,
                "avg_thirst": 0
            }
        
        for animal in self.animals:
            species = animal.species
            stats[species]["population"] += 1
            stats[species]["avg_health"] += animal.health
            stats[species]["avg_hunger"] += animal.hunger
            stats[species]["avg_thirst"] += animal.thirst
        
        for species, data in stats.items():
            pop = data["population"]
            if pop > 0:
                data["avg_health"] /= pop
                data["avg_hunger"] /= pop
                data["avg_thirst"] /= pop
        
        self.game_state.update_ecosystem_balance(stats)
    
    def try_natural_spawning(self, dt):
        """Small chance for animals to naturally spawn"""
        if len(self.animals) >= 40:
            return
        
        species_counts = {}
        for animal in self.animals:
            species = animal.species
            species_counts[species] = species_counts.get(species, 0) + 1
        
        for species, config in self.species_config.items():
            current_count = species_counts.get(species, 0)
            
            max_count = self.initial_population.get(species, 5) * 1.5
            if current_count < max_count:
                if random.random() < 0.005 * dt:
                    self.spawn_animal(species)
                    self.game_state.add_notification(f"A new {species} has appeared!")
    
    def try_group_reproduction(self, dt):
        """Let animal groups reproduce if they meet conditions"""
        group_min_size = 3
        reproduction_cooldown = 30

        if not hasattr(self, "last_reproduction_time"):
            self.last_reproduction_time = {}

        species_groups = {}

        for animal in self.animals:
            if animal.age >= 0.8:
                key = (animal.species, animal.group_id)
                species_groups.setdefault(key, []).append(animal)

        for (species, group_id), group in species_groups.items():
            if len(group) >= group_min_size:
                last_time = self.last_reproduction_time.get((species, group_id), 0)
                if self.game_state.time_elapsed - last_time > reproduction_cooldown:
                    parent = random.choice(group)
                    self.spawn_animal(species, nearby=parent.position, group_id=group_id)
                    self.last_reproduction_time[(species, group_id)] = self.game_state.time_elapsed
                    self.game_state.add_notification(f"{species.capitalize()} group {group_id} reproduced!")

    def get_tourist_appeal(self):
        """Calculate the tourism appeal of the current animal population"""
        if not self.animals:
            return 0
        
        species_present = set([animal.species for animal in self.animals])
        base_appeal = len(species_present) * 30
        
        animal_appeal = 0
        for animal in self.animals:
            species_appeal = self.species_config[animal.species]["tourist_appeal"]
            health_factor = animal.health / 100
            animal_appeal += species_appeal * health_factor
        
        animal_appeal = animal_appeal / len(self.animals)
        
        total_appeal = base_appeal + (animal_appeal * 10)
        
        return min(100, total_appeal)
    
    def render(self, screen, camera_offset):
        """Render all animals with camera offset"""
        for animal in self.animals:
            screen_pos = (animal.position[0] - camera_offset[0], 
                         animal.position[1] - camera_offset[1])
            
            if (screen_pos[0] < -100 or screen_pos[0] > SCREEN_WIDTH + 100 or
                screen_pos[1] < -100 or screen_pos[1] > SCREEN_HEIGHT + 100):
                continue
            
            rect = animal.image.get_rect()
            rect.center = screen_pos
            
            screen.blit(animal.image, rect)
            
            if animal.health < 70:
                bar_width = animal.rect.width
                bar_height = 4
                bar_pos = (screen_pos[0] - bar_width/2, screen_pos[1] - animal.rect.height/2 - 10)
                
                pygame.draw.rect(screen, BLACK, 
                               (bar_pos[0], bar_pos[1], bar_width, bar_height))
                
                health_width = max(0, bar_width * animal.health / 100)
                health_color = GREEN if animal.health > 50 else YELLOW if animal.health > 25 else RED
                pygame.draw.rect(screen, health_color, 
                               (bar_pos[0], bar_pos[1], health_width, bar_height))
    
    def save_animals(self, filename="animals.json"):
        """Save animal data to a file"""
        animal_data = []
        
        for animal in self.animals:
            data = {
                "species": animal.species,
                "position": [animal.position[0], animal.position[1]],
                "hunger": animal.hunger,
                "thirst": animal.thirst,
                "health": animal.health,
                "energy": animal.energy,
                "state": animal.state
            }
            animal_data.append(data)
        
        with open(filename, 'w') as f:
            json.dump(animal_data, f)
        
        return True
    
    def load_animals(self, filename="animals.json"):
        """Load animal data from a file"""
        try:
            with open(filename, 'r') as f:
                animal_data = json.load(f)
            
            for animal in list(self.animals):
                self.remove_animal(animal)
            
            for data in animal_data:
                pos = (data["position"][0], data["position"][1])
                animal = Animal(data["species"], pos, self.terrain, self)
                animal.hunger = data["hunger"]
                animal.thirst = data["thirst"]
                animal.health = data["health"]
                animal.energy = data["energy"]
                animal.state = data["state"]
                self.animals.append(animal)
                self.animals_group.add(animal)
            
            return True
        except Exception as e:
            print(f"Error loading animals: {str(e)}")
            return False
        
    def update_group_movement(self, dt):
        group_centers = {}
        group_members = {}

        for animal in self.animals:
            key = (animal.species, animal.group_id)
            group_members.setdefault(key, []).append(animal)

        for key, members in group_members.items():
            if not members:
                continue
            avg_x = sum(a.position[0] for a in members) / len(members)
            avg_y = sum(a.position[1] for a in members) / len(members)
            group_centers[key] = (avg_x, avg_y)

            for animal in members:
                animal.group_center = group_centers[key]
