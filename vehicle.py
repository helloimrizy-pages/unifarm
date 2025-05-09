import pygame, math, os
from constants import *

class Jeep(pygame.sprite.Sprite):
    def __init__(self, terrain, economy_manager):
        super().__init__()
        self.terrain = terrain
        self.econ    = economy_manager

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(current_dir, "assets")
            image_path = os.path.join(assets_dir, "jeep.png")
            loaded_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading jeep image: {image_path} - {e}")
            print("Falling back to default colored rectangle for Jeep.")
            loaded_image = pygame.Surface((int(TILE_SIZE*1.5), TILE_SIZE), pygame.SRCALPHA)
            loaded_image.fill(OLIVE)

        desired_width = int(TILE_SIZE * 1.5)
        desired_height = TILE_SIZE
        self.base_image = pygame.transform.scale(loaded_image, (desired_width, desired_height))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rotation = 0


        self.grid_path = []
        self.path_idx  = 0
        self.state     = "idle"
        self.capacity  = 4
        self.passengers = []
        self.has_started_a_trip = False

        ex, ey = terrain.grid_to_world(terrain.entrance_tile)
        self.position = [ex, ey]
        self.rect.center = self.position
        self.speed = 3.0 * (TILE_SIZE/32)

    def update(self, dt):
        if self.state == "idle":
            current_jeep_grid_pos = self.terrain.world_to_grid(self.position)
            if current_jeep_grid_pos == self.terrain.entrance_tile:
                pickup_radius = 1.5 * TILE_SIZE
                candidate_tourists = []
                for t in self.econ.tourists:
                    dist_to_jeep = math.hypot(self.position[0] - t.position[0],
                                              self.position[1] - t.position[1])
                    if dist_to_jeep < pickup_radius:
                        candidate_tourists.append(t)

                if candidate_tourists:
                    picked_up_this_frame = 0
                    tourists_to_board = []
                    for t in candidate_tourists:
                        if len(self.passengers) < self.capacity:
                            tourists_to_board.append(t)
                            self.passengers.append(t)
                            picked_up_this_frame += 1
                        else:
                            break
                    if tourists_to_board:
                        for t_boarded in tourists_to_board:
                            if t_boarded in self.econ.tourists:
                                self.econ.tourists.remove(t_boarded)
                            if t_boarded in self.econ.tourists_group:
                                self.econ.tourists_group.remove(t_boarded)

                    if len(self.passengers) >= self.capacity:
                        route = self.terrain.find_path(
                            self.terrain.entrance_tile,
                            self.terrain.exit_tile
                        )
                        if route:
                            self.grid_path = route
                            self.path_idx = 0
                            self.state = "to_exit"
                            self.has_started_a_trip = True

        elif self.state == "to_exit":
            if self.path_idx < len(self.grid_path):
                target_grid_pos = self.grid_path[self.path_idx]
                target_world_pos = self.terrain.grid_to_world(target_grid_pos)
                self._move_toward(target_world_pos, dt)
                if math.hypot(self.position[0] - target_world_pos[0],
                              self.position[1] - target_world_pos[1]) < self.speed * dt * 1.1:
                    self.position[0] = target_world_pos[0]
                    self.position[1] = target_world_pos[1]
                    self.path_idx += 1
            else:
                for p in self.passengers:
                    p.satisfaction = min(100, p.satisfaction + 30)
                    p.position = list(self.terrain.grid_to_world(self.terrain.exit_tile))
                    p.rect.center = p.position
                    if p not in self.econ.tourists:
                        self.econ.tourists.append(p)
                    if p not in self.econ.tourists_group:
                        self.econ.tourists_group.add(p)
                    p.choose_new_target()
                self.passengers.clear()
                route = self.terrain.find_path(
                    self.terrain.exit_tile,
                    self.terrain.entrance_tile
                )
                if route:
                    self.grid_path = route
                    self.path_idx = 0
                    self.state = "to_entrance"
                else:
                    self.state = "idle"
                    self.grid_path = []

        elif self.state == "to_entrance":
            if self.path_idx < len(self.grid_path):
                target_grid_pos = self.grid_path[self.path_idx]
                target_world_pos = self.terrain.grid_to_world(target_grid_pos)
                self._move_toward(target_world_pos, dt)
                if math.hypot(self.position[0] - target_world_pos[0],
                              self.position[1] - target_world_pos[1]) < self.speed * dt * 1.1:
                    self.position[0] = target_world_pos[0]
                    self.position[1] = target_world_pos[1]
                    self.path_idx += 1
            else:
                self.state = "idle"
                self.grid_path = []


        if self.image is not self.base_image:
            self.image = self.base_image
        self.rect = self.image.get_rect(center=tuple(self.position))

    def _move_toward(self, target_world_pos, dt):
        dx = target_world_pos[0] - self.position[0]
        dy = target_world_pos[1] - self.position[1]
        dist = math.hypot(dx,dy)

        if dist > 0:
            norm_dx = dx / dist
            norm_dy = dy / dist
            self.position[0] += norm_dx * self.speed * dt
            self.position[1] += norm_dy * self.speed * dt

class VehicleManager:
    def __init__(self, game_state, building_manager, terrain, economy_manager):
        self.game_state = game_state
        self.buildings = building_manager
        self.terrain   = terrain
        self.econ      = economy_manager
        self.vehicles = pygame.sprite.Group()

    def purchase_jeep(self):
        cost = 1000
        if self.game_state.funds < cost:
            self.game_state.add_notification("Not enough funds for jeep")
            return False

        route_to_exit = self.terrain.find_path(
            self.terrain.entrance_tile,
            self.terrain.exit_tile
        )

        self.game_state.add_funds(-cost)
        jeep = Jeep(self.terrain, self.econ)
        self.vehicles.add(jeep)
        self.game_state.add_notification("Purchased a safari jeep!")
        return True

    def update(self, dt):
        jeeps_to_remove = []
        for v in self.vehicles:
            v.update(dt)

            if v.state == "idle" and not v.passengers:
                current_jeep_grid_pos = self.terrain.world_to_grid(v.position)
                if current_jeep_grid_pos == self.terrain.entrance_tile:
                    if v.has_started_a_trip:
                        jeeps_to_remove.append(v)

        for jeep in jeeps_to_remove:
            self.vehicles.remove(jeep)

    def render(self, screen, camera_offset):
        for v in self.vehicles:
            sx = v.position[0] - camera_offset[0]
            sy = v.position[1] - camera_offset[1]
            if -100 < sx < SCREEN_WIDTH+100 and -100 < sy < SCREEN_HEIGHT+100:
                rect = v.image.get_rect(center=(sx,sy))
                screen.blit(v.image, rect)