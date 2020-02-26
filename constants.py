import pygame, os
from pygame.constants import *

#global constants
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, "data")

#key constants
UP = K_w
DOWN = K_s
RIGHT = K_d
LEFT = K_a

A_UP = K_UP
A_DOWN = K_DOWN
A_LEFT = K_LEFT
A_RIGHT = K_RIGHT

INTERACT = K_e
DODGE = K_SPACE

