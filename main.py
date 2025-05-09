import sys
import pygame
import argparse
from pathlib import Path
from game_state import GameState, GameSpeed
from terrain import TerrainGenerator
from building_manager import BuildingManager
from animal_manager import AnimalManager
from vehicle import VehicleManager
from economy_manager import EconomyManager
from ui import UIManager
from game_over_screen import game_over_screen
from constants import *

pygame.init()
pygame.font.init()

def main(
        difficulty: str = "medium",
        game_state: GameState = None,
        terrain: TerrainGenerator = None,
        buildings: BuildingManager = None,
        animals: AnimalManager = None,
        economy: EconomyManager = None,
        vehicles: VehicleManager = None,
        ui: UIManager = None,
):
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Safari Park - Pygame Edition")
    clock = pygame.time.Clock()

    if game_state is None:
        game_state = GameState(difficulty)
    if terrain is None:
        terrain = TerrainGenerator(game_state)
    if buildings is None:
        buildings = BuildingManager(game_state, terrain)
    if animals is None:
        animals = AnimalManager(game_state, terrain)
    if economy is None:
        economy = EconomyManager(game_state, animals, buildings)
    if vehicles is None:
        vehicles = VehicleManager(game_state, buildings, terrain, economy)
    if ui is None:
        ui = UIManager(game_state, animals, buildings, economy, terrain)

    animals.set_building_manager(buildings)
    animals.update_animal_stats()
    economy.vehicle_manager = vehicles
    ui.create_menu_buttons()

    camera_offset = [0, 0]
    camera_speed = 500
    running = True
    game_state.set_game_speed(GameSpeed.HOUR)

    night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    max_night_alpha = 150

    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]: camera_offset[1] -= camera_speed * dt
        if keys[pygame.K_s]: camera_offset[1] += camera_speed * dt
        if keys[pygame.K_a]: camera_offset[0] -= camera_speed * dt
        if keys[pygame.K_d]: camera_offset[0] += camera_speed * dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_state.set_game_speed(GameSpeed.PAUSED)
                elif event.key == pygame.K_2:
                    game_state.set_game_speed(GameSpeed.HOUR)
                elif event.key == pygame.K_3:
                    game_state.set_game_speed(GameSpeed.DAY)
                elif event.key == pygame.K_4:
                    game_state.set_game_speed(GameSpeed.WEEK)
                elif event.key == pygame.K_b:
                    ui.toggle_build_menu()
                elif event.key == pygame.K_TAB:
                    ui.toggle_animal_overview()
                elif ui.build_menu_active and event.key == pygame.K_f:
                    ui.select_building('feeding_station')
                elif ui.build_menu_active and event.key == pygame.K_w:
                    ui.select_building('water_station')
                elif ui.build_menu_active and event.key == pygame.K_p:
                    ui.select_building('path')
                elif ui.build_menu_active and event.key == pygame.K_v:
                    ui.select_building('viewing_platform')

            if ui.handle_event(event, camera_offset):
                continue

        if game_state.game_speed > 0:
            ts = game_state.game_speed
            animals.update(dt * ts)
            buildings.update(dt * ts)
            economy.update(dt * ts)
            vehicles.update(dt * ts)
            game_state.update(dt * ts)

        if game_state.check_win_condition():
            result = game_over_screen(screen, ui.title_font, "You Win!")
            if result == 'restart':
                return main(difficulty, game_state=None)
            else:
                break

        if game_state.check_lose_condition():
            result = game_over_screen(screen, ui.title_font, "Game Over")
            if result == 'restart':
                return main(difficulty, game_state=None)
            else:
                break

        screen.fill(BLACK)
        terrain.render(screen, camera_offset)
        buildings.render(screen, camera_offset)
        animals.render(screen, camera_offset)
        economy.render(screen, camera_offset)
        vehicles.render(screen, camera_offset)
        ui.draw(screen, camera_offset, mouse_pos)

        current_hour = game_state.time_of_day
        current_alpha = 0

        if 18 <= current_hour < 20:
            progress = (current_hour - 18) / (20 - 18)
            current_alpha = int(progress * max_night_alpha)
        elif current_hour >= 20 or current_hour < 4:
            current_alpha = max_night_alpha
        elif 4 <= current_hour < 6:
            progress = (current_hour - 4) / (6 - 4)
            current_alpha = int((1 - progress) * max_night_alpha)
        else:
            current_alpha = 0

        current_alpha = max(0, min(max_night_alpha, current_alpha))

        night_overlay.fill((0, 0, 0, current_alpha))
        screen.blit(night_overlay, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--load", "-l",
        help="Path to a saved game folder",
        type=str
    )
    parser.add_argument(
        "--difficulty", "-d",
        help="Difficulty level (if starting new)",
        default="medium"
    )
    args = parser.parse_args()

    if args.load:
        save_dir = Path(args.load)

        game_state = GameState.load(save_dir / "savegame.json")

        terrain = TerrainGenerator(game_state)
        terrain.load_terrain(save_dir / "terrain.json")

        buildings = BuildingManager(game_state, terrain)
        buildings.load_buildings(save_dir / "buildings.json")

        animals = AnimalManager(game_state, terrain)
        animals.load_animals(save_dir / "animals.json")

        economy = EconomyManager(game_state, animals, buildings)
        vehicles = VehicleManager(game_state, buildings, terrain, economy)
        ui = UIManager(game_state, animals, buildings, economy, terrain)

        main(
            difficulty=game_state.difficulty,
            game_state=game_state,
            terrain=terrain,
            buildings=buildings,
            animals=animals,
            economy=economy,
            vehicles=vehicles,
            ui=ui
        )
    else:
        main(difficulty=args.difficulty)