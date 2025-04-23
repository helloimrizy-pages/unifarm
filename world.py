from ursina import Entity, load_texture, color, Plane
import random
import noise
import json

class TerrainGenerator:
    def __init__(self, game_state, size=64, height_scale=5):
        self.game_state = game_state
        self.size = size
        self.height_scale = height_scale
        self.terrain_entity = None
        self.water_entities = []
        self.vegetation_entities = []
        
        self.water_level = 0.3
        self.grass_level = 0.6
        self.rocky_level = 0.8
        
        self.height_map = self.generate_height_map()
        self.terrain_types = self.classify_terrain()
        
        self.create_terrain()
        self.add_water()
        self.add_vegetation()
    
    def generate_height_map(self):
        """Generate a procedural height map using Perlin noise"""
        height_map = []
        
        seed = random.randint(0, 1000)
        scale = 10.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        
        for z in range(self.size):
            row = []
            for x in range(self.size):
                nx = x / self.size - 0.5
                nz = z / self.size - 0.5
                y = noise.pnoise2(nx * scale, 
                                  nz * scale, 
                                  octaves=octaves, 
                                  persistence=persistence, 
                                  lacunarity=lacunarity,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed)
                
                y = (y + 0.5) * self.height_scale
                
                dist_from_center = ((x - self.size/2)**2 + (z - self.size/2)**2)**0.5
                center_factor = max(0, 1 - (dist_from_center / (self.size/3)))
                basin = center_factor * 2
                
                y = max(0, y - basin)
                
                row.append(y)
            height_map.append(row)
        
        return height_map
    
    def classify_terrain(self):
        """Classify terrain types based on height"""
        terrain_types = []
        for z in range(self.size):
            row = []
            for x in range(self.size):
                height = self.height_map[z][x]
                
                if height < self.water_level:
                    terrain_type = "water"
                elif height < self.grass_level:
                    terrain_type = "grass"
                elif height < self.rocky_level:
                    terrain_type = "rocky"
                else:
                    terrain_type = "mountain"
                
                row.append(terrain_type)
            terrain_types.append(row)
        
        return terrain_types
    
    def create_terrain(self):
        """Create the 3D terrain entity"""
        self.terrain_entity = Entity(
            model=Plane(subdivisions=(self.size, self.size)),
            scale=(self.size, 1, self.size),
            position=(0, 0, 0),
            collider='mesh',
            name='terrain'
        )

        verts = self.terrain_entity.model.vertices
        for i, vert in enumerate(verts):
            x = int((vert[0] + 0.5) * self.size)
            z = int((vert[2] + 0.5) * self.size)
            x = max(0, min(x, self.size - 1))
            z = max(0, min(z, self.size - 1))
            height = self.height_map[z][x]
            verts[i] = (vert[0], height, vert[2])
        self.terrain_entity.model.vertices = verts
        self.terrain_entity.model.generate()

        # use the built-in white cube texture, tinted green
        self.terrain_entity.texture = load_texture('white_cube')
        self.terrain_entity.color   = color.green.tint(-.3)

    
    def add_water(self):
        """Add water entities at water locations"""
        water_plane = Entity(
            model=Plane(subdivisions=(1,1)),
            scale=(self.size*1.2, 1, self.size*1.2),
            position=(0, self.water_level-0.1, 0),
            texture=load_texture('white_cube'),
            color=color.rgba(0, 150, 255, 150),
            name='water'
        )
        self.water_entities.append(water_plane)

    def add_vegetation(self):
        """Add trees and bushes to the terrain"""
        random.seed(42)

        num_trees = int(self.size * self.size * 0.01)
        num_bushes = int(self.size * self.size * 0.02)

        for _ in range(num_trees):
            x = random.randint(0, self.size - 1)
            z = random.randint(0, self.size - 1)

            if self.terrain_types[z][x] == "grass":
                height = self.height_map[z][x]
                world_x = x - self.size / 2
                world_z = z - self.size / 2

                # Tree trunk
                trunk = Entity(
                    model='cube',
                    scale=(0.3, 0.8, 0.3),
                    position=(world_x, height + 0.4, world_z),
                    color=color.brown,
                    name='tree_trunk'
                )

                # Tree canopy
                canopy = Entity(
                    model='sphere',
                    scale=(1, 1, 1),
                    position=(world_x, height + 1.2, world_z),
                    color=color.green,
                    name='tree_canopy'
                )

                self.vegetation_entities.append(trunk)
                self.vegetation_entities.append(canopy)

        for _ in range(num_bushes):
            x = random.randint(0, self.size - 1)
            z = random.randint(0, self.size - 1)

            if self.terrain_types[z][x] == "grass":
                height = self.height_map[z][x]

                bush = Entity(
                    model='sphere',
                    scale=(0.8, 0.5, 0.8),
                    position=(x - self.size/2, height + 0.25, z - self.size/2),
                    color=color.rgba(0, 100, 0, 255),
                    name='bush'
                )
                self.vegetation_entities.append(bush)

    
    def get_height_at_position(self, position):
        """Get the terrain height at the given world position"""
        x = int(position[0] + self.size/2)
        z = int(position[2] + self.size/2)
        x = max(0, min(x, self.size - 1))
        z = max(0, min(z, self.size - 1))
        return self.height_map[z][x]
    
    def get_terrain_type_at_position(self, position):
        """Get the terrain type at the given world position"""
        x = int(position[0] + self.size/2)
        z = int(position[2] + self.size/2)
        x = max(0, min(x, self.size - 1))
        z = max(0, min(z, self.size - 1))
        return self.terrain_types[z][x]
    
    def is_water_at_position(self, position):
        """Check if there is water at the given position"""
        return self.get_terrain_type_at_position(position) == "water"
    
    def is_suitable_for_building(self, position):
        """Check if the given position is suitable for building"""
        return self.get_terrain_type_at_position(position) == "grass"
    
    def save_terrain(self, filename="terrain.json"):
        """Save terrain data to a file"""
        terrain_data = {
            "size": self.size,
            "height_scale": self.height_scale,
            "height_map": self.height_map,
            "terrain_types": self.terrain_types
        }
        with open(filename, 'w') as f:
            json.dump(terrain_data, f)
        return True
    
    def load_terrain(self, filename="terrain.json"):
        """Load terrain data from a file"""
        try:
            with open(filename, 'r') as f:
                terrain_data = json.load(f)
            self.size = terrain_data["size"]
            self.height_scale = terrain_data["height_scale"]
            self.height_map = terrain_data["height_map"]
            self.terrain_types = terrain_data["terrain_types"]
            self.create_terrain()
            self.add_water()
            self.add_vegetation()
            return True
        except Exception as e:
            print(f"Error loading terrain: {str(e)}")
            return False
