import sys
import pygame
import random
import math
from datetime import datetime
import noise
import json
from os import path
from collections import defaultdict

from game_state import GameState
from terrain import TerrainGenerator
from building_manager import BuildingManager
from animal_manager import AnimalManager
from vehicle import VehicleManager
from economy_manager import EconomyManager
from ui import UIManager
from constants import *

UI_STATE_MAIN_MENU = "main_menu"
UI_STATE_SETTINGS = "settings"
UI_STATE_GAMEPLAY = "gameplay"

pygame.init()
ui_state = UI_STATE_MAIN_MENU
pygame.font.init()

def main(difficulty='medium'):
    """Main game function"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Safari Park - Pygame Edition")
    clock = pygame.time.Clock()

    game_state = GameState(difficulty)
    terrain    = TerrainGenerator(game_state)
    buildings  = BuildingManager(game_state, terrain)
    animals    = AnimalManager(game_state, terrain)
    economy    = EconomyManager(game_state, animals, buildings)
    vehicles   = VehicleManager(game_state, buildings, terrain, economy)
    ui         = UIManager(game_state, animals, buildings, economy)

    animals.set_building_manager(buildings)
    animals.update_animal_stats()
    economy.vehicle_manager = vehicles
    ui.create_menu_buttons()

    camera_offset = [0, 0]
    camera_speed  = 500

    running = True
    game_state.set_game_speed(1)

    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        keys      = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            camera_offset[1] -= camera_speed * dt
        if keys[pygame.K_s]:
            camera_offset[1] += camera_speed * dt
        if keys[pygame.K_a]:
            camera_offset[0] -= camera_speed * dt
        if keys[pygame.K_d]:
            camera_offset[0] += camera_speed * dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_state.set_game_speed(0)
                elif event.key == pygame.K_2:
                    game_state.set_game_speed(1)
                elif event.key == pygame.K_3:
                    game_state.set_game_speed(3)
                elif event.key == pygame.K_b:
                    ui.toggle_build_menu()
                elif event.key == pygame.K_TAB:
                    ui.toggle_animal_overview()
                elif event.key == pygame.K_f and ui.build_menu_active:
                    ui.select_building('feeding_station')
                elif event.key == pygame.K_w and ui.build_menu_active:
                    ui.select_building('water_station')
                elif event.key == pygame.K_p and ui.build_menu_active:
                    ui.select_building('path')
                elif event.key == pygame.K_v and ui.build_menu_active:
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
            pygame.draw.rect(screen, (0,100,0,200),
                             (SCREEN_WIDTH//4, SCREEN_HEIGHT//4,
                              SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            win_text = ui.title_font.render("You Win!", True, WHITE)
            screen.blit(win_text,
                        (SCREEN_WIDTH//2 - win_text.get_width()//2,
                         SCREEN_HEIGHT//2 - win_text.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(5000)
            running = False

        if game_state.check_lose_condition():
            pygame.draw.rect(screen, (100,0,0,200),
                             (SCREEN_WIDTH//4, SCREEN_HEIGHT//4,
                              SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            lose_text = ui.title_font.render("Game Over", True, WHITE)
            screen.blit(lose_text,
                        (SCREEN_WIDTH//2 - lose_text.get_width()//2,
                         SCREEN_HEIGHT//2 - lose_text.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(5000)
            running = False

        screen.fill(BLACK)
        terrain.render(screen, camera_offset)
        buildings.render(screen, camera_offset)
        animals.render(screen, camera_offset)
        economy.render(screen, camera_offset)
        vehicles.render(screen, camera_offset)
        ui.draw(screen, camera_offset, mouse_pos)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        difficulty = sys.argv[1].lower()
        if difficulty not in ['easy', 'medium', 'hard']:
            print("Invalid difficulty. Using 'medium' instead.")
            difficulty = 'medium'
    else:
        difficulty = 'medium'

    main(difficulty)
