import pygame
import random
import noise
from constants import *

class TerrainGenerator:
    def __init__(self, game_state, size=64):
        self.game_state = game_state
        self.size = size
        self.tile_size = TILE_SIZE
        self.water_threshold = 0.3
        self.grass_threshold = 0.7
        self.rocky_threshold = 0.9
        
        self.terrain_grid = self.generate_terrain_grid()
        
        self.terrain_surface = pygame.Surface((size * self.tile_size, size * self.tile_size), pygame.SRCALPHA)
        self.vegetation_surface = pygame.Surface((size * self.tile_size, size * self.tile_size), pygame.SRCALPHA)
        self.entrance_tile = (0, self.size // 2)
        self.exit_tile = (self.size - 1, self.size // 2)
        self.create_terrain_surfaces()
    
    def generate_terrain_grid(self):
        """Generate a 2D terrain grid using Perlin noise"""
        terrain_grid = []
        
        seed = random.randint(0, 1000)
        scale = 10.0
        octaves = 4
        persistence = 0.5
        lacunarity = 2.0
        
        for y in range(self.size):
            row = []
            for x in range(self.size):
                nx = x / self.size - 0.5
                ny = y / self.size - 0.5
                
                noise_value = noise.pnoise2(
                    nx * scale, 
                    ny * scale, 
                    octaves=octaves, 
                    persistence=persistence, 
                    lacunarity=lacunarity,
                    repeatx=1024,
                    repeaty=1024,
                    base=seed
                )
                
                noise_value = (noise_value + 1) / 2
                
                dist_from_center = ((x - self.size/2)**2 + (y - self.size/2)**2)**0.5
                center_factor = max(0, 1 - (dist_from_center / (self.size/3)))
                basin_effect = center_factor * 0.4
                noise_value = max(0, noise_value - basin_effect)
                
                if noise_value < self.water_threshold:
                    terrain_type = "water"
                elif noise_value < self.grass_threshold:
                    terrain_type = "grass"
                elif noise_value < self.rocky_threshold:
                    terrain_type = "rocky"
                else:
                    terrain_type = "mountain"
                
                row.append({
                    "type": terrain_type,
                    "value": noise_value
                })
            terrain_grid.append(row)
        
        return terrain_grid
    
    def create_terrain_surfaces(self):
        """Create pre-rendered surfaces for the terrain"""
        self.terrain_surface.fill((50, 150, 50))
        
        for y in range(self.size):
            for x in range(self.size):
                tile_data = self.terrain_grid[y][x]
                tile_x = x * self.tile_size
                tile_y = y * self.tile_size
                
                if tile_data["type"] == "water":
                    pygame.draw.rect(self.terrain_surface, LIGHT_BLUE, 
                                    (tile_x, tile_y, self.tile_size, self.tile_size))
                
                elif tile_data["type"] == "rocky":
                    pygame.draw.rect(self.terrain_surface, GRAY, 
                                    (tile_x, tile_y, self.tile_size, self.tile_size))
                
                elif tile_data["type"] == "mountain":
                    pygame.draw.rect(self.terrain_surface, DARK_GRAY, 
                                    (tile_x, tile_y, self.tile_size, self.tile_size))
        
        random.seed(42)
        
        num_trees = int(self.size * self.size * 0.01)
        num_bushes = int(self.size * self.size * 0.02)
        
        tree_color = DARK_GREEN
        bush_color = GREEN
        
        for _ in range(num_trees):
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            
            if self.terrain_grid[y][x]["type"] == "grass":
                tree_x = x * self.tile_size + self.tile_size * 0.1
                tree_y = y * self.tile_size 
                tree_width = self.tile_size * 0.8
                tree_height = self.tile_size * 1.2
                
                pygame.draw.rect(self.vegetation_surface, BROWN, 
                                (tree_x + tree_width/3, tree_y + tree_height/2, tree_width/3, tree_height/2))
                pygame.draw.circle(self.vegetation_surface, tree_color, 
                                 (int(tree_x + tree_width/2), int(tree_y + tree_height/3)), 
                                 int(tree_width/2))
        
        for _ in range(num_bushes):
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            
            if self.terrain_grid[y][x]["type"] == "grass":
                bush_x = x * self.tile_size + self.tile_size * 0.25
                bush_y = y * self.tile_size + self.tile_size * 0.25
                bush_size = self.tile_size * 0.5
                
                pygame.draw.circle(self.vegetation_surface, bush_color, 
                                 (int(bush_x + bush_size/2), int(bush_y + bush_size/2)), 
                                 int(bush_size/2))
    
    def world_to_grid(self, world_pos):
        """Convert world position to grid position"""
        grid_x = int((world_pos[0] + self.size * self.tile_size / 2) / self.tile_size)
        grid_y = int((world_pos[1] + self.size * self.tile_size / 2) / self.tile_size)
        
        grid_x = max(0, min(grid_x, self.size - 1))
        grid_y = max(0, min(grid_y, self.size - 1))
        
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_pos):
        """Convert grid position to world position"""
        world_x = grid_pos[0] * self.tile_size - self.size * self.tile_size / 2 + self.tile_size / 2
        world_y = grid_pos[1] * self.tile_size - self.size * self.tile_size / 2 + self.tile_size / 2
        
        return (world_x, world_y)
    
    def get_terrain_at_position(self, world_pos):
        """Get the terrain type at the given world position"""
        grid_x, grid_y = self.world_to_grid(world_pos)
        return self.terrain_grid[grid_y][grid_x]["type"]
    
    def is_water_at_position(self, world_pos):
        """Check if there is water at the given position"""
        return self.get_terrain_at_position(world_pos) == "water"
    
    def is_suitable_for_building(self, world_pos):
        """Check if the given position is suitable for building"""
        return self.get_terrain_at_position(world_pos) == "grass"
    
    def render(self, screen, camera_offset):
        """Render the terrain with camera offset"""
        viewport_rect = pygame.Rect(
            camera_offset[0], 
            camera_offset[1], 
            SCREEN_WIDTH, 
            SCREEN_HEIGHT
        )
        
        terrain_rect = pygame.Rect(
            viewport_rect.x + self.size * self.tile_size / 2,
            viewport_rect.y + self.size * self.tile_size / 2, 
            viewport_rect.width, 
            viewport_rect.height
        )
        
        screen.blit(self.terrain_surface, (-camera_offset[0] - self.size * self.tile_size / 2, 
                                          -camera_offset[1] - self.size * self.tile_size / 2))
        screen.blit(self.vegetation_surface, (-camera_offset[0] - self.size * self.tile_size / 2, 
                                            -camera_offset[1] - self.size * self.tile_size / 2))
    
    def save_terrain(self, filename="terrain.json"):
        """Save terrain data to a file"""
        serialized_grid = []
        for row in self.terrain_grid:
            serialized_row = []
            for tile in row:
                serialized_row.append({
                    "type": tile["type"],
                    "value": tile["value"]
                })
            serialized_grid.append(serialized_row)
            
        terrain_data = {
            "size": self.size,
            "terrain_grid": serialized_grid
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
            self.terrain_grid = terrain_data["terrain_grid"]
            
            self.terrain_surface = pygame.Surface((self.size * self.tile_size, self.size * self.tile_size), pygame.SRCALPHA)
            self.vegetation_surface = pygame.Surface((self.size * self.tile_size, self.size * self.tile_size), pygame.SRCALPHA)
            self.create_terrain_surfaces()
            
            return True
        except Exception as e:
            print(f"Error loading terrain: {str(e)}")
            return False

    def find_path(self, start, goal):
        from heapq import heappop, heappush

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            neighbors = [(current[0] + dx, current[1] + dy) 
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]]

            for neighbor in neighbors:
                if not (0 <= neighbor[0] < self.size and 0 <= neighbor[1] < self.size):
                    continue
                if self.terrain_grid[neighbor[1]][neighbor[0]]["type"] != "path":
                    continue
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score, neighbor))
                    came_from[neighbor] = current
        return []
