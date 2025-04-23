from ursina import *
import random, math

class Vehicle(Entity):
    def __init__(self, start_pos, vehicle_manager):
        super().__init__(
            model='cube',
            scale=(1,0.5,2),
            color=color.azure,
            position=start_pos,
            collider='box',
            name=f"jeep_{id(self)}"
        )
        self.speed = 8.0
        self.manager = vehicle_manager
        # pick a random road tile or patrol path
        self.target = None

    def update(self):
        # simple random road‐constrained movement
        if not self.target or distance(self.position, self.target) < 1:
            # pick a random road from building_manager.buildings
            roads = [b for b in self.manager.building_manager.buildings if b.building_type=='road']
            if roads:
                self.target = random.choice(roads).position
        if self.target:
            dir = (self.target - self.position).normalized()
            self.position += dir * self.speed * time.dt
            self.y = self.manager.terrain.get_height_at_position(self.position)
            self.look_at(self.position + dir)

class VehicleManager:
    def __init__(self, game_state, building_manager, terrain):
        self.game_state = game_state
        self.building_manager = building_manager
        self.terrain = terrain
        self.vehicles = []

    def purchase_jeep(self):
        cost = 1000
        if self.game_state.funds < cost:
            self.game_state.add_notification("Not enough funds for a jeep")
            return
        self.game_state.add_funds(-cost)
        # spawn at entrance:
        start = Vec3(self.terrain.size/2, 0, 0)
        start.y = self.terrain.get_height_at_position(start)
        jeep = Vehicle(start, self)
        self.vehicles.append(jeep)
        self.game_state.add_notification("Purchased a safari jeep!")

    def update(self, dt):
            for v in self.vehicles:
                v.update()
