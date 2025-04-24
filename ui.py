import pygame
from constants import *
from components import Button
from utils import distance

class UIManager:
    def __init__(self, game_state, animal_manager, building_manager, economy_manager):
        self.game_state = game_state
        self.animal_manager = animal_manager
        self.building_manager = building_manager
        self.economy_manager = economy_manager
        
        self.selected_building = None
        self.close_button = None
        self.build_menu_active = False
        self.animal_overview_active = False
        
        self.build_buttons = []
        self.time_buttons = []
        
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.medium_font = pygame.font.SysFont('Arial', 18)
        self.large_font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 32)
        
        self.notification_surface = pygame.Surface((int(SCREEN_WIDTH * 0.3), int(SCREEN_HEIGHT * 0.15)), pygame.SRCALPHA)
        
        self.create_menu_buttons()
    
    def create_menu_buttons(self):
        """Create the UI buttons"""
        button_y = SCREEN_HEIGHT - 40
        self.time_buttons = [
            Button(SCREEN_WIDTH//2 - 90, button_y, 60, 30, "Pause", GRAY, LIGHT_GRAY, 
                  action=lambda: self.game_state.set_game_speed(0)),
            Button(SCREEN_WIDTH//2 - 30, button_y, 60, 30, "Normal", GRAY, LIGHT_GRAY, 
                  action=lambda: self.game_state.set_game_speed(1)),
            Button(SCREEN_WIDTH//2 + 30, button_y, 60, 30, "Fast", GRAY, LIGHT_GRAY, 
                  action=lambda: self.game_state.set_game_speed(3))
        ]
        
        menu_x = 10
        menu_y = 60
        button_spacing = 40
        
        self.build_buttons = [
            Button(menu_x, menu_y, 30, 30, "F", ORANGE, LIGHT_RED, 
                  action=lambda: self.select_building("feeding_station")),
            Button(menu_x, menu_y + button_spacing, 30, 30, "W", BLUE, (100, 100, 255), 
                  action=lambda: self.select_building("water_station")),
            Button(menu_x, menu_y + button_spacing*2, 30, 30, "P", BROWN, (200, 150, 100), 
                  action=lambda: self.select_building("path")),
            Button(menu_x, menu_y + button_spacing*3, 30, 30, "V", LIGHT_GRAY, WHITE, 
                  action=lambda: self.select_building("viewing_platform")),
        ]
        
        if hasattr(self.economy_manager, 'vehicle_manager') and self.economy_manager.vehicle_manager:
            self.build_buttons.append(
                Button(menu_x, menu_y + button_spacing*4, 30, 30, "J", OLIVE, (200, 200, 100), 
                      action=lambda: self.economy_manager.vehicle_manager.purchase_jeep())
            )
        
        self.build_toggle_button = Button(menu_x, 10, 100, 30, "Build Menu", GREEN, LIGHT_GREEN, 
                                         action=self.toggle_build_menu)
        
        self.animal_overview_button = Button(menu_x + 110, 10, 140, 30, "Animal Overview", YELLOW, (255, 255, 150), 
                                          action=self.toggle_animal_overview)
    
    def toggle_build_menu(self):
        """Toggle the building menu"""
        self.build_menu_active = not self.build_menu_active
        
        for button in self.build_buttons:
            button.active = self.build_menu_active
    
    def toggle_animal_overview(self):
        """Toggle the animal overview panel"""
        self.animal_overview_active = not self.animal_overview_active
    
    def select_building(self, building_type):
        """Select a building type for placement"""
        self.selected_building = building_type
        self.game_state.add_notification(f"Selected {building_type} for placement. Click on the map to build.")
    
    def place_selected_building(self, position):
        """Place the selected building at the given position"""
        if self.selected_building:
            self.building_manager.place_building(self.selected_building, position)
    
    def draw_resource_display(self, screen):
        """Draw the resource display (money, etc.)"""
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 50))
        
        money_text = self.large_font.render(f"${self.game_state.funds:.2f}", True, GREEN)
        screen.blit(money_text, (SCREEN_WIDTH//2 - 150, 10))
        
        eco_text = self.large_font.render(f"Ecosystem: {self.game_state.ecosystem_balance:.1f}%", True, WHITE)
        screen.blit(eco_text, (SCREEN_WIDTH//2, 10))
        
        tourists = len(self.economy_manager.tourists)
        stars = "★" * int(self.economy_manager.avg_review_score) + "☆" * (5 - int(self.economy_manager.avg_review_score))
        tourist_text = self.large_font.render(f"Tourists: {tourists} ({stars})", True, YELLOW)
        screen.blit(tourist_text, (SCREEN_WIDTH//2 + 250, 10))
    
    def draw_time_display(self, screen):
        """Draw the time display"""
        day_text = f"Day {self.game_state.day}"
        hour = int(self.game_state.time_of_day)
        minute = int((self.game_state.time_of_day - hour) * 60)
        time_text = f"{hour:02d}:{minute:02d}"
        
        full_text = self.large_font.render(f"{day_text} - {time_text}", True, WHITE)
        screen.blit(full_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 70))
        
        for button in self.time_buttons:
            button.draw(screen)
    
    def draw_notification_area(self, screen):
        """Draw the notification area"""
        self.notification_surface.fill((0, 0, 0, 150))
        
        if self.game_state.notifications:
            notifications = self.game_state.notifications[-3:]
            y_offset = 10
            
            title = self.medium_font.render("Notifications", True, WHITE)
            self.notification_surface.blit(title, (10, y_offset))
            y_offset += 25
            
            for notification in notifications:
                time_text = self.small_font.render(f"{notification['time']}: ", True, LIGHT_GRAY)
                msg_text = self.small_font.render(notification['message'], True, WHITE)
                
                self.notification_surface.blit(time_text, (10, y_offset))
                self.notification_surface.blit(msg_text, (70, y_offset))
                
                y_offset += 20
        
        screen.blit(self.notification_surface, (SCREEN_WIDTH - self.notification_surface.get_width() - 10, 
                                              SCREEN_HEIGHT - self.notification_surface.get_height() - 10))
    
    def draw_build_menu(self, screen):
        """Draw the build menu"""
        self.build_toggle_button.draw(screen)
        
        if self.build_menu_active:
            menu_width = 150
            menu_height = 250
            pygame.draw.rect(screen, (0, 0, 0, 180), (5, 55, menu_width, menu_height), border_radius=5)
            
            title = self.medium_font.render("Build Menu", True, WHITE)
            screen.blit(title, (50, 60))
            
            for button in self.build_buttons:
                button.draw(screen)
            
            mouse_pos = pygame.mouse.get_pos()
            for i, button in enumerate(self.build_buttons):
                if button.rect.collidepoint(mouse_pos) and button.active:
                    tooltip_text = ""
                    if i == 0:
                        tooltip_text = "Feeding Station - $500"
                    elif i == 1:
                        tooltip_text = "Water Station - $400"
                    elif i == 2:
                        tooltip_text = "Path - $100"
                    elif i == 3:
                        tooltip_text = "Viewing Platform - $700"
                    elif i == 4:
                        tooltip_text = "Jeep - $1000"
                    
                    if tooltip_text:
                        tooltip = self.small_font.render(tooltip_text, True, WHITE)
                        tooltip_bg = pygame.Rect(mouse_pos[0], mouse_pos[1] - 25, tooltip.get_width() + 10, 25)
                        pygame.draw.rect(screen, DARK_GRAY, tooltip_bg)
                        screen.blit(tooltip, (mouse_pos[0] + 5, mouse_pos[1] - 20))
    
    def draw_animal_overview(self, screen):
        """Draw the animal overview panel"""
        self.animal_overview_button.draw(screen)
        
        if self.animal_overview_active:
            panel_width = 400
            panel_height = 300
            panel_x = (SCREEN_WIDTH - panel_width) // 2
            panel_y = (SCREEN_HEIGHT - panel_height) // 2
            
            pygame.draw.rect(screen, (0, 0, 0, 200), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)
            
            title = self.title_font.render("Animal Overview", True, WHITE)
            screen.blit(title, (panel_x + (panel_width - title.get_width()) // 2, panel_y + 10))
            
            self.close_button = Button(panel_x + panel_width - 30, panel_y + 10, 20, 20, "X", RED, LIGHT_RED, 
                                    action=self.toggle_animal_overview)
            self.close_button.draw(screen)

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
            
            y_pos = panel_y + 50
            spacing = 30
            
            for species, stats in species_stats.items():
                species_text = self.medium_font.render(f"{species.capitalize()}: {stats['population']}", True, WHITE)
                screen.blit(species_text, (panel_x + 20, y_pos))
                
                bar_x = panel_x + 200
                bar_y = y_pos + 5
                bar_width = 150
                bar_height = 15
                
                pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
                
                health_width = max(0, bar_width * stats['avg_health'] / 100)
                health_color = self.get_health_color(stats['avg_health'])
                pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
                
                health_text = self.small_font.render(f"{stats['avg_health']:.1f}%", True, BLACK)
                screen.blit(health_text, (bar_x + bar_width // 2 - health_text.get_width() // 2, bar_y))
                
                y_pos += spacing
            
            eco_balance_text = self.medium_font.render(f"Ecosystem Balance: {self.game_state.ecosystem_balance:.1f}%", True, WHITE)
            screen.blit(eco_balance_text, (panel_x + 20, panel_y + panel_height - 40))
    
    def get_health_color(self, health):
        """Get a color based on health percentage"""
        if health > 80:
            return GREEN
        elif health > 50:
            return YELLOW
        elif health > 30:
            return ORANGE
        else:
            return RED
    
    def draw_building_preview(self, screen, camera_offset, mouse_pos):
        """Draw a preview of the building at mouse position"""
        if not self.selected_building:
            return
            
        world_x = mouse_pos[0] + camera_offset[0]
        world_y = mouse_pos[1] + camera_offset[1]
        world_pos = (world_x, world_y)
        
        config = self.building_manager.building_config[self.selected_building]
        
        width = int(config['scale'][0] * TILE_SIZE)
        height = int(config['scale'][1] * TILE_SIZE)
        
        preview = pygame.Surface((width, height), pygame.SRCALPHA)
        
        color_with_alpha = (*config['color'][:3], 150)
        preview.fill(color_with_alpha)
        
        screen_pos = (mouse_pos[0] - width // 2, mouse_pos[1] - height // 2)
        
        screen.blit(preview, screen_pos)
        
        valid_position = (self.building_manager.terrain.is_suitable_for_building(world_pos) and
                        not self.building_manager.is_position_occupied(world_pos))
        
        indicator_color = GREEN if valid_position else RED
        pygame.draw.rect(screen, indicator_color, (screen_pos[0], screen_pos[1], width, height), 2)
    
    def draw_cursor_info(self, screen, camera_offset, mouse_pos):
        """Draw information about what's under the cursor"""
        world_x = mouse_pos[0] + camera_offset[0]
        world_y = mouse_pos[1] + camera_offset[1]
        world_pos = (world_x, world_y)
        
        terrain_type = self.building_manager.terrain.get_terrain_at_position(world_pos)
        
        info_text = f"Terrain: {terrain_type.capitalize()}"
        
        for building in self.building_manager.buildings:
            if distance(building.position, world_pos) < TILE_SIZE:
                if hasattr(building, "health"):
                    info_text += f" | {building.building_type.capitalize()} (Health: {building.health:.0f}%)"
                else:
                    info_text += f" | {building.building_type.capitalize()}"
                break

        for animal in self.animal_manager.animals:
            if distance(animal.position, world_pos) < TILE_SIZE:
                info_text += f" | {animal.species.capitalize()} (H:{animal.health:.0f}% F:{animal.hunger:.0f}% W:{animal.thirst:.0f}%)"
                break
        
        info_surface = self.small_font.render(info_text, True, WHITE)
        screen.blit(info_surface, (10, SCREEN_HEIGHT - 20))
    
    def draw(self, screen, camera_offset, mouse_pos):
        """Draw all UI elements"""
        self.draw_resource_display(screen)
        self.draw_time_display(screen)
        self.draw_notification_area(screen)
        self.draw_build_menu(screen)
        
        if self.animal_overview_active:
            self.draw_animal_overview(screen)
        else:
            self.animal_overview_button.draw(screen)
        
        if self.selected_building:
            self.draw_building_preview(screen, camera_offset, mouse_pos)
        
        self.draw_cursor_info(screen, camera_offset, mouse_pos)
    
    def handle_event(self, event, camera_offset):
        """Handle UI events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.build_toggle_button.handle_event(event)
            self.animal_overview_button.handle_event(event)
            
            for button in self.time_buttons:
                if button.handle_event(event):
                    return True

            if self.build_menu_active:
                for button in self.build_buttons:
                    if button.handle_event(event):
                        return True

            if self.animal_overview_active and self.close_button:
                if self.close_button.handle_event(event):
                    return True

            if self.selected_building and not self.animal_overview_active:
                mouse_pos = pygame.mouse.get_pos()
                world_x = mouse_pos[0] + camera_offset[0]
                world_y = mouse_pos[1] + camera_offset[1]
                world_pos = (world_x, world_y)

                self.place_selected_building(world_pos)
                return True

        return False
