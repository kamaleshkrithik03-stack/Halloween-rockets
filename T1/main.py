import os
import sys
import math
import random
import pygame 
from pygame.math import Vector2 
import config as cfg

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
pygame.display.set_caption("halloween edition of the TVC rocket -it is now much harder")
clock = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("Consolas", 12)
FONT_MED = pygame.font.SysFont("Consolas", 15, bold=True)
FONT_LARGE = pygame.font.SysFont("Consolas", 20, bold=True)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, val, label, fmt="{:.2f}"):
        self.Rect = pygame.Rect(x, y, w, h)
        
