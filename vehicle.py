import pygame, math, random
from constants import *

class Jeep(pygame.sprite.Sprite):
    def __init__(self, terrain, economy_manager):
        super().__init__()
        self.terrain = terrain
        self.econ    = economy_manager

        size = (int(TILE_SIZE*1.5), TILE_SIZE)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(OLIVE)
        self.rect  = self.image.get_rect()

        self.grid_path = []
        self.path_idx  = 0
        self.state     = "idle"
        self.capacity  = 4
        self.passengers = []

        ex, ey = terrain.grid_to_world(terrain.entrance_tile)
        self.position = (ex, ey)
        self.rect.center = self.position
        self.speed = 3.0 * (TILE_SIZE/32)

    def update(self, dt):
        if self.state == "idle":
            waiting = [t for t in self.econ.tourists 
                       if self.terrain.world_to_grid(t.position)==self.terrain.entrance_tile]
            if waiting:
                for t in waiting[:self.capacity]:
                    self.passengers.append(t)
                    self.econ.tourists.remove(t)
                    self.econ.tourists_group.remove(t)
                route = self.terrain.find_path(
                    self.terrain.entrance_tile,
                    self.terrain.exit_tile
                )
                self.grid_path = route
                self.path_idx = 0
                self.state = "to_exit"
        elif self.state in ("to_exit","to_entrance"):
            if self.path_idx < len(self.grid_path):
                target = self.terrain.grid_to_world(self.grid_path[self.path_idx])
                self._move_toward(target, dt)
                if math.hypot(self.position[0]-target[0], self.position[1]-target[1]) < 2:
                    self.path_idx += 1
            else:
                if self.state=="to_exit":
                    for _ in self.passengers: 
                        self.econ.daily_income += self.econ.entrance_fee
                        self.econ.game_state.add_funds(self.econ.entrance_fee)
                    self.passengers.clear()
                    route = self.terrain.find_path(
                        self.terrain.exit_tile,
                        self.terrain.entrance_tile
                    )
                    self.grid_path = route
                    self.path_idx = 0
                    self.state = "to_entrance"
                else:
                    self.state = "idle"

        self.rect.center = self.position

    def _move_toward(self, target, dt):
        dx = target[0]-self.position[0]
        dy = target[1]-self.position[1]
        dist = math.hypot(dx,dy)
        if dist>0:
            dx, dy = dx/dist, dy/dist
            self.position = (
                self.position[0] + dx*self.speed*dt,
                self.position[1] + dy*self.speed*dt
            )

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
        self.game_state.add_funds(-cost)
        jeep = Jeep(self.terrain, self.econ)
        self.vehicles.add(jeep)
        self.game_state.add_notification("Purchased a safari jeep!")
        return True

    def update(self, dt):
        for v in self.vehicles:
            v.update(dt)

    def render(self, screen, camera_offset):
        for v in self.vehicles:
            sx = v.position[0] - camera_offset[0]
            sy = v.position[1] - camera_offset[1]
            if -100 < sx < SCREEN_WIDTH+100 and -100 < sy < SCREEN_HEIGHT+100:
                rect = v.image.get_rect(center=(sx,sy))
                screen.blit(v.image, rect)
