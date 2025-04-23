from ursina import *
import random
import json
import math

class Animal(Entity):
    def __init__(self, species, position, terrain, animal_manager):
        config = animal_manager.species_config[species]
        
        super().__init__(
            model=config['model'],
            texture=config['texture'],
            scale=config['scale'],
            position=position,
            collider='box',
            name=f"{species}_{id(self)}"
        )
        
        self.species = species
        self.terrain = terrain
        self.manager = animal_manager
        self.game_state = animal_manager.game_state
        self.age = random.uniform(0.2, 1.0)
        self.speed = config['speed'] * self.age
        
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
        if not self.target or self.target.name != "feeding_station":
            feeding_stations = [b for b in self.manager.buildings.buildings 
                               if b.building_type == "feeding_station"]
            
            if feeding_stations:
                closest = min(feeding_stations, key=lambda b: distance(self, b))
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
            
            if distance(self.position, self.target_position) < 2:
                self.hunger = max(0, self.hunger - 30)
                self.state = "idle"
                self.target = None
                self.target_position = None
    
    def seek_water(self, dt):
        """Seek out water sources"""
        if not self.target or (self.target.name != "water_station" and self.target.name != "water"):
            water_stations = [b for b in self.manager.buildings.buildings 
                             if b.building_type == "water_station"]
            
            if water_stations:
                closest = min(water_stations, key=lambda b: distance(self, b))
                self.target = closest
                self.target_position = closest.position
            else:
                water_locations = self.find_water_locations()
                if water_locations:
                    self.target_position = random.choice(water_locations)
                    self.target = Entity(position=self.target_position, name="water")
                else:
                    self.state = "idle"
                    return
        
        if self.target_position:
            self.move_to_target(dt)
            
            if distance(self.position, self.target_position) < 2:
                self.thirst = max(0, self.thirst - 40)
                self.state = "idle"
                self.target = None
                self.target_position = None
    
    def rest(self, dt):
        """Rest to regain energy"""
        self.wandering = False
        
        self.energy += 1.0 * dt
        
        if self.energy > 80:
            self.state = "idle"
    
    def wander(self, dt):
        """Wander around aimlessly"""
        if not self.wandering:
            wander_range = 10
            x = self.x + random.uniform(-wander_range, wander_range)
            z = self.z + random.uniform(-wander_range, wander_range)
            
            if self.terrain.is_water_at_position((x, 0, z)) and self.species != "crocodile":
                self.wandering = False
                return
            
            self.target_position = Vec3(x, 0, z)
            self.wandering = True
            self.wander_timer = random.uniform(5, 15)
        
        if self.wandering:
            self.move_to_target(dt)
            
            self.wander_timer -= dt
            
            if distance(self.position, self.target_position) < 1 or self.wander_timer <= 0:
                self.wandering = False
                self.wander_timer = random.uniform(2, 5)
    
    def move_to_target(self, dt):
        """Move toward target position"""
        if not self.target_position:
            return
        
        direction = self.target_position - self.position
        
        target_y = self.terrain.get_height_at_position(self.target_position)
        self.target_position = Vec3(self.target_position.x, target_y, self.target_position.z)
        
        if direction.length() > 0:
            direction = direction.normalized()
        
        speed = self.speed * dt
        self.position += direction * speed
        
        terrain_height = self.terrain.get_height_at_position(self.position)
        self.y = terrain_height
        
        if direction.length() > 0:
            self.look_at(self.position + direction)
            self.rotation_x = 0
    
    def find_grass_locations(self):
        """Find suitable grass locations for food"""
        grass_locations = []
        
        search_radius = 20
        for x in range(-search_radius, search_radius + 1, 5):
            for z in range(-search_radius, search_radius + 1, 5):
                pos = Vec3(self.x + x, 0, self.z + z)
                if self.terrain.get_terrain_type_at_position(pos) == "grass":
                    pos.y = self.terrain.get_height_at_position(pos)
                    grass_locations.append(pos)
        
        return grass_locations
    
    def find_water_locations(self):
        """Find suitable water locations for drinking"""
        water_locations = []
        
        search_radius = 30
        for x in range(-search_radius, search_radius + 1, 5):
            for z in range(-search_radius, search_radius + 1, 5):
                pos = Vec3(self.x + x, 0, self.z + z)
                if self.terrain.is_water_at_position(pos):
                    pos.y = self.terrain.get_height_at_position(pos)
                    water_locations.append(pos)
        
        return water_locations


class AnimalManager:
    def __init__(self, game_state, terrain):
        self.game_state = game_state
        self.terrain = terrain
        self.animals = []
        self.buildings = None
        
        self.species_config = {
            "elephant": {
                "model": "cube",
                "texture": "white_cube",
                "scale": (2, 2, 3),
                "speed": 3.0,
                "preferred_terrain": "grass",
                "food_consumption": 2.0,
                "water_consumption": 3.0,
                "tourist_appeal": 3.0
            },
            "lion": {
                "model": "cube",
                "texture": "white_cube",
                "scale": (1, 1, 2),
                "speed": 5.0,
                "preferred_terrain": "grass",
                "food_consumption": 1.5,
                "water_consumption": 1.0,
                "tourist_appeal": 3.5
            },
            "zebra": {
                "model": "cube",
                "texture": "white_cube",
                "scale": (1, 1.5, 2),
                "speed": 4.0,
                "preferred_terrain": "grass",
                "food_consumption": 1.0,
                "water_consumption": 1.0,
                "tourist_appeal": 2.0
            }
        }
        
        self.species_colors = {
            "elephant": color.gray,
            "lion": color.yellow,
            "zebra": color.white
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
    
    def spawn_animal(self, species):
        """Spawn a new animal of the given species"""
        spawn_position = self.find_spawn_position(species)
        
        animal = Animal(species, spawn_position, self.terrain, self)
        animal.color = self.species_colors[species]
        
        self.animals.append(animal)
        
        return animal
    
    def find_spawn_position(self, species):
        """Find a suitable spawn position for the given species"""
        size = self.terrain.size
        max_attempts = 50
        
        for _ in range(max_attempts):
            x = random.uniform(-size/2, size/2)
            z = random.uniform(-size/2, size/2)
            pos = Vec3(x, 0, z)
            
            terrain_type = self.terrain.get_terrain_type_at_position(pos)
            
            if species == "crocodile" and terrain_type == "water":
                pos.y = self.terrain.get_height_at_position(pos)
                return pos
            elif terrain_type == "grass":
                pos.y = self.terrain.get_height_at_position(pos)
                return pos
        
        return Vec3(0, 1, 0)
    
    def update(self, dt):
        """Update all animals"""
        for animal in list(self.animals):
            animal.step(dt)
            
            if animal.health <= 0:
                self.remove_animal(animal)
        
        self.update_animal_stats()
        
        self.try_natural_spawning(dt)
    
    def remove_animal(self, animal):
        """Remove an animal from the simulation"""
        if animal in self.animals:
            self.animals.remove(animal)
            destroy(animal)
    
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
    
    def save_animals(self, filename="animals.json"):
        """Save animal data to a file"""
        animal_data = []
        
        for animal in self.animals:
            data = {
                "species": animal.species,
                "position": [animal.x, animal.y, animal.z],
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
                pos = Vec3(*data["position"])
                animal = Animal(data["species"], pos, self.terrain, self)
                animal.hunger = data["hunger"]
                animal.thirst = data["thirst"]
                animal.health = data["health"]
                animal.energy = data["energy"]
                animal.state = data["state"]
                animal.color = self.species_colors[data["species"]]
                self.animals.append(animal)
            
            return True
        except Exception as e:
            print(f"Error loading animals: {str(e)}")
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