from ursina import *
from ursina.prefabs.dropdown_menu import DropdownMenu
from ursina.prefabs.tooltip import Tooltip

class UIManager:
    def __init__(self, game_state, animal_manager, building_manager, economy_manager):
        self.game_state = game_state
        self.animal_manager = animal_manager
        self.building_manager = building_manager
        self.economy_manager = economy_manager
        
        self.ui = Entity(parent=camera.ui)
        
        self.create_resource_display()
        
        self.build_menu = None
        
        self.animal_overview = None
        
        self.create_time_controls()
        
        self.create_notification_area()
    
    def create_resource_display(self):
        """Create the display for resources (money, etc)"""
        self.resource_bar = Entity(
            parent=self.ui,
            model='quad',
            scale=(1, 0.05, 1),
            position=(0, 0.475, 0),
            color=color.dark_gray
        )
        
        self.money_text = Text(
            parent=self.resource_bar,
            text=f"${self.game_state.funds:.2f}",
            position=(-0.45, 0, 0),
            scale=0.7,
            color=color.lime
        )
        
        self.ecosystem_text = Text(
            parent=self.resource_bar,
            text=f"Ecosystem: {self.game_state.ecosystem_balance:.1f}%",
            position=(0, 0, 0),
            scale=0.7,
            color=color.white
        )
        
        self.tourist_text = Text(
            parent=self.resource_bar,
            text=f"Tourists: 0 (★★★☆☆)",
            position=(0.45, 0, 0),
            scale=0.7,
            color=color.yellow
        )
    
    def create_time_controls(self):
        """Create the time control buttons"""
        self.time_bar = Entity(
            parent=self.ui,
            model='quad',
            scale=(0.3, 0.05, 1),
            position=(0, -0.475, 0),
            color=color.dark_gray
        )
        
        self.time_text = Text(
            parent=self.time_bar,
            text=f"Day {self.game_state.day} - {int(self.game_state.time_of_day):02d}:00",
            position=(0, 0.2, 0),
            scale=0.7,
            color=color.white
        )
        
        self.pause_button = Button(
            parent=self.time_bar,
            model='circle',
            scale=0.15,
            position=(-0.12, 0, 0),
            color=color.gray,
            highlight_color=color.light_gray,
            text="❚❚",
            on_click=lambda: self.game_state.set_game_speed(0)
        )
        
        self.normal_button = Button(
            parent=self.time_bar,
            model='circle',
            scale=0.15,
            position=(0, 0, 0),
            color=color.gray,
            highlight_color=color.light_gray,
            text="▶",
            on_click=lambda: self.game_state.set_game_speed(1)
        )
        
        self.fast_button = Button(
            parent=self.time_bar,
            model='circle',
            scale=0.15,
            position=(0.12, 0, 0),
            color=color.gray,
            highlight_color=color.light_gray,
            text="▶▶",
            on_click=lambda: self.game_state.set_game_speed(3)
        )
    
    def create_notification_area(self):
        """Create the area for game notifications"""
        self.notification_panel = Entity(
            parent=self.ui,
            model='quad',
            scale=(0.3, 0.15, 1),
            position=(0.35, -0.35, 0),
            color=color.rgba(0, 0, 0, 150),
            visible=True
        )
        
        Text(
            parent=self.notification_panel,
            text="Notifications",
            position=(0, 0.45, 0),
            scale=0.7,
            color=color.white
        )
        
        self.notification_text = Text(
            parent=self.notification_panel,
            text="Welcome to your safari park!",
            position=(0, 0, 0),
            scale=0.5,
            color=color.light_gray,
            wordwrap=25
        )
    
    def toggle_build_menu(self, show):
        """Show or hide the building menu"""
        if show and not self.build_menu:
            self.build_menu = Entity(
                parent=self.ui,
                model='quad',
                scale=(0.2, 0.4, 1),
                position=(-0.4, 0, 0),
                color=color.rgba(0, 0, 0, 200)
            )
            
            Text(
                parent=self.build_menu,
                text="Build Menu",
                position=(0, 0.45, 0),
                scale=0.7,
                color=color.white
            )
            
            y_pos = 0.25
            spacing = 0.15
            
            self.feeding_button = Button(
                parent=self.build_menu,
                model='cube',
                scale=0.1,
                position=(0, y_pos, 0),
                color=color.orange,
                tooltip=Tooltip("Feeding Station\nCost: $500"),
                on_click=self.select_feeding_station
            )
            Text(parent=self.feeding_button, text="F", scale=10, color=color.black)
            y_pos -= spacing
            
            self.water_button = Button(
                parent=self.build_menu,
                model='cube',
                scale=0.1,
                position=(0, y_pos, 0),
                color=color.blue,
                tooltip=Tooltip("Water Station\nCost: $400"),
                on_click=self.select_water_station
            )
            Text(parent=self.water_button, text="W", scale=10, color=color.black)
            y_pos -= spacing
            
            self.path_button = Button(
                parent=self.build_menu,
                model='cube',
                scale=0.1,
                position=(0, y_pos, 0),
                color=color.brown,
                tooltip=Tooltip("Path\nCost: $100"),
                on_click=self.select_path
            )
            Text(parent=self.path_button, text="P", scale=10, color=color.black)
            y_pos -= spacing
            
            self.platform_button = Button(
                parent=self.build_menu,
                model='cube',
                scale=0.1,
                position=(0, y_pos, 0),
                color=color.gray,
                tooltip=Tooltip("Viewing Platform\nCost: $700"),
                on_click=self.select_viewing_platform
            )
            Text(parent=self.platform_button, text="V", scale=10, color=color.black)
        
        elif not show and self.build_menu:
            destroy(self.build_menu)
            self.build_menu = None
    
    def select_feeding_station(self):
        """Select the feeding station building type"""
        self.building_manager.place_building("feeding_station", mouse.world_point)
    
    def select_water_station(self):
        """Select the water station building type"""
        self.building_manager.place_building("water_station", mouse.world_point)
    
    def select_path(self):
        """Select the path building type"""
        self.building_manager.place_building("path", mouse.world_point)
    
    def select_viewing_platform(self):
        """Select the viewing platform building type"""
        self.building_manager.place_building("viewing_platform", mouse.world_point)
    
    def toggle_animal_overview(self):
        """Show or hide the animal overview panel"""
        if not self.animal_overview:
            self.animal_overview = Entity(
                parent=self.ui,
                model='quad',
                scale=(0.5, 0.6, 1),
                position=(0, 0, 0),
                color=color.rgba(0, 0, 0, 200)
            )
            
            Text(
                parent=self.animal_overview,
                text="Animal Overview",
                position=(0, 0.45, 0),
                scale=0.7,
                color=color.white
            )
            
            Button(
                parent=self.animal_overview,
                model='circle',
                scale=0.03,
                position=(0.45, 0.45, 0),
                color=color.red,
                highlight_color=color.dark_gray,
                text="X",
                on_click=self.toggle_animal_overview
            )
            
            self.animal_content = Entity(parent=self.animal_overview)
            self.update_animal_overview()
        else:
            destroy(self.animal_overview)
            self.animal_overview = None
    
    def update_animal_overview(self):
        """Update the animal overview panel with current stats"""
        if not self.animal_overview:
            return
        
        destroy(self.animal_content)
        self.animal_content = Entity(parent=self.animal_overview)
        
        species_stats = {}
        for species in self.animal_manager.species_config:
            group = [a for a in self.animal_manager.animals if a.species == species]
            pop = len(group)
            if pop:
                avg_health = sum(a.health for a in group) / pop
                avg_hunger = sum(a.hunger for a in group) / pop
                avg_thirst = sum(a.thirst for a in group) / pop
            else:
                avg_health = avg_hunger = avg_thirst = 0
            species_stats[species] = {
                "population": pop,
                "avg_health": avg_health,
                "avg_hunger": avg_hunger,
                "avg_thirst": avg_thirst
            }

        
        y_pos = 0.3
        spacing = 0.15
        
        for species, stats in species_stats.items():
            Text(
                parent=self.animal_content,
                text=f"{species.capitalize()}: {stats['population']}",
                position=(-0.2, y_pos, 0),
                scale=0.6,
                color=color.white
            )
            
            health_bg = Entity(
                parent=self.animal_content,
                model='quad',
                scale=(0.2, 0.03, 1),
                position=(0.15, y_pos, 0),
                color=color.dark_gray
            )
            
            health_fill = Entity(
                parent=health_bg,
                model='quad',
                scale=(stats['avg_health']/100, 0.8, 1),
                position=(-0.5 + stats['avg_health']/200, 0, 0),
                color=self.get_health_color(stats['avg_health'])
            )
            
            Text(
                parent=health_bg,
                text=f"{stats['avg_health']:.1f}%",
                position=(0, 0, 0),
                scale=1.5,
                color=color.black
            )
            
            y_pos -= spacing
    
    def get_health_color(self, health):
        """Get a color based on health percentage"""
        if health > 80:
            return color.green
        elif health > 50:
            return color.yellow
        elif health > 30:
            return color.orange
        else:
            return color.red
    
    def update(self):
        """Update UI elements"""
        self.money_text.text = f"${self.game_state.funds:.2f}"
        self.ecosystem_text.text = f"Ecosystem: {self.game_state.ecosystem_balance:.1f}%"
        
        tourists = len(self.economy_manager.tourists)
        stars = "★" * int(self.economy_manager.avg_review_score) + "☆" * (5 - int(self.economy_manager.avg_review_score))
        self.tourist_text.text = f"Tourists: {tourists} ({stars})"
        
        day_text = f"Day {self.game_state.day}"
        hour = int(self.game_state.time_of_day)
        minute = int((self.game_state.time_of_day - hour) * 60)
        time_text = f"{hour:02d}:{minute:02d}"
        self.time_text.text = f"{day_text} - {time_text}"
        
        if self.game_state.notifications:
            notifications = self.game_state.notifications[-3:]
            notification_text = "\n".join([f"{n['time']}: {n['message']}" for n in notifications])
            self.notification_text.text = notification_text
        
        if self.animal_overview:
            self.update_animal_overview()
    
    def show_win_screen(self):
        """Display the win screen"""
        self.win_screen = WindowPanel(
            title='Victory!',
            content=(
                f"Congratulations! You have successfully managed your safari park!\n\n"
                f"Final Balance: ${self.game_state.funds:.2f}\n"
                f"Ecosystem Balance: {self.game_state.ecosystem_balance:.1f}%\n"
                f"Days Elapsed: {self.game_state.day}\n"
                f"Tourist Rating: {self.economy_manager.avg_review_score:.1f}/5\n\n"
                f"Press [ESC] to exit or click New Game to start again."
            ),
            position=(0, 0, 0),
            scale=(0.6, 0.8),
            color=color.green.tint(-.2)
        )
        
        Button(
            parent=self.win_screen,
            text='New Game',
            position=(0, -0.2, 0),
            scale=(0.3, 0.05),
            color=color.azure,
            on_click=self.restart_game
        )
    
    def show_lose_screen(self):
        """Display the lose screen"""
        self.lose_screen = WindowPanel(
            title='Game Over',
            content=(
                f"Your safari park has failed!\n\n"
                f"Final Balance: ${self.game_state.funds:.2f}\n"
                f"Ecosystem Balance: {self.game_state.ecosystem_balance:.1f}%\n"
                f"Days Elapsed: {self.game_state.day}\n\n"
                f"Press [ESC] to exit or click Try Again to start over."
            ),
            position=(0, 0, 0),
            scale=(0.6, 0.8),
            color=color.red.tint(-.2)
        )
        
        Button(
            parent=self.lose_screen,
            text='Try Again',
            position=(0, -0.2, 0),
            scale=(0.3, 0.05),
            color=color.azure,
            on_click=self.restart_game
        )
    
    def restart_game(self):
        """Restart the game"""
        import os
        import sys
        
        difficulty = self.game_state.difficulty
        
        python = sys.executable
        os.execl(python, python, *sys.argv, difficulty)