
from ursina import *
from world      import TerrainGenerator
from animals    import AnimalManager
from buildings  import BuildingManager
from economy    import EconomyManager
from ui         import UIManager
from game_state import GameState

Text.default_font = 'assets/fonts/DejaVuSans.ttf'

def input(key):
    global build_mode, selected_building
    if key == '1':   game_state.set_game_speed(0)
    elif key == '2': game_state.set_game_speed(1)
    elif key == '3': game_state.set_game_speed(3)
    elif key == 'b':
        build_mode = not build_mode
        ui.toggle_build_menu(build_mode)
    elif key == 'tab':
        ui.toggle_animal_overview()
    elif key == 'left mouse down' and build_mode and selected_building:
        if mouse.hovered_entity and mouse.hovered_entity.name == 'terrain':
            buildings.place_building(selected_building, mouse.world_point)
    elif build_mode:
        if key == 'f': selected_building = 'feeding_station'
        if key == 'w': selected_building = 'water_station'
        if key == 'p': selected_building = 'path'
        if key == 'v': selected_building = 'viewing_platform'

def update():
    if held_keys['w']: camera_pivot.position += (0,0,camera_speed*time.dt)
    if held_keys['s']: camera_pivot.position -= (0,0,camera_speed*time.dt)
    if held_keys['a']: camera_pivot.position -= (camera_speed*time.dt,0,0)
    if held_keys['d']: camera_pivot.position += (camera_speed*time.dt,0,0)
    if held_keys['q']: camera_pivot.rotation_y -= rotation_speed*time.dt
    if held_keys['e']: camera_pivot.rotation_y += rotation_speed*time.dt

    if game_state.game_speed > 0:
        ts = game_state.game_speed
        animals .update(time.dt*ts)
        buildings.update(time.dt*ts)
        economy .update(time.dt*ts)
        game_state.update(time.dt*ts)

    if game_state.check_win_condition():  ui.show_win_screen()
    if game_state.check_lose_condition(): ui.show_lose_screen()
    ui.update()

def main(difficulty='medium'):
    global game_state, terrain, animals, buildings, economy, ui
    global camera_pivot, camera_speed, rotation_speed
    global build_mode, selected_building

    app = Ursina()
    window.title = "Safari - Wildlife Management Sim"
    window.borderless = False
    window.exit_button.visible = True
    window.fps_counter.enabled = True

    game_state = GameState(difficulty)
    terrain    = TerrainGenerator(game_state)
    buildings  = BuildingManager( game_state, terrain)
    animals    = AnimalManager(   game_state, terrain)
    economy    = EconomyManager(  game_state, animals, buildings)
    ui         = UIManager(       game_state, animals, buildings, economy)
    animals.set_building_manager(buildings)
    animals.update_animal_stats()

    camera_pivot = Entity()
    camera.parent      = camera_pivot
    camera.position    = (0,20,-20)
    camera.rotation_x  = 40

    camera_speed   = 10
    rotation_speed = 50
    build_mode     = False
    selected_building = None

    game_state.set_game_speed(0)
    app.run()

if __name__ == '__main__':
    import sys
    main(sys.argv[1].lower() if len(sys.argv)>1 else 'medium')
