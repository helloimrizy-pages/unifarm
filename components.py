import pygame
import sys
import random
import math
import noise
import json
from datetime import datetime
from os import path
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK, font_size=20, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', font_size)
        self.action = action
        self.active = True
    
    def draw(self, screen):
        if not self.active:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=5)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if not self.active:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False