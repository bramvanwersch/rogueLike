import pygame, os
from pygame.constants import *

class GameRules:
    """
    Simple class for defining game_rule variables that can be changed from the console
    """
    def __init__(self):
        self.warnings = True
        self.bounding_boxes = False
        self.nr_entities = True
        self.fps = True
        self.entity_paths = False
        self.vision_line = False
        self.peacefull = False
        self.aim_line = False

    def attributes(self):
        return list(vars(self).keys())

game_rules = GameRules()

DISTINCT_COLORS = [(0,0,0), (255,255,255), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255), (255,0,255),
                   (192,192,192), (128,128,128), (128,0,0), (128,128,0), (0,128,0), (128,0,128), (0,128,128), (0,0,128),
                   (128,0,0), (139,0,0), (165,42,42), (178,34,34), (220,20,60), (255,0,0), (255,99,71), (255,127,80),
                   (205,92,92), (240,128,128), (233,150,122), (250,128,114), (255,160,122), (255,69,0), (255,140,0),
                   (255,165,0), (255,215,0), (184,134,11), (218,165,32), (238,232,170), (189,183,107), (240,230,140),
                   (128,128,0), (255,255,0), (154,205,50), (85,107,47), (107,142,35), (124,252,0), (127,255,0),
                   (173,255,47), (0,100,0), (0,128,0), (34,139,34), (0,255,0), (50,205,50), (144,238,144), (152,251,152),
                   (143,188,143), (0,250,154), (0,255,127), (46,139,87), (60,179,113), (32,178,170), (47,79,79),
                   (0,128,128), (0,139,139), (0,255,255), (0,255,255), (224,255,255), (0,206,209), (64,224,208),
                   (72,209,204), (175,238,238), (127,255,212), (176,224,230), (95,158,160), (70,130,180), (100,149,237),
                   (0,191,255), (30,144,255), (173,216,230), (135,206,235), (135,206,250), (25,25,112), (0,0,128),
                   (0,0,139), (0,0,205), (0,0,255), (65,105,225), (138,43,226), (75,0,130), (72,61,139), (106,90,205),
                   (123,104,238), (147,112,219), (139,0,139), (148,0,211), (153,50,204), (186,85,211), (128,0,128),
                   (216,191,216), (221,160,221), (238,130,238), (255,0,255), (218,112,214), (199,21,133), (219,112,147),
                   (255,20,147), (255,105,180), (139,69,19), (160,82,45), (210,105,30), (205,133,63), (244,164,96),
                   (222,184,135), (210,180,140), (188,143,143)]
TILE_SIZE = [100,100]

KEYBOARD_KEYS = [KEYDOWN, KEYUP, KMOD_ALT, KMOD_CAPS, KMOD_CTRL, KMOD_LALT, KMOD_LCTRL, KMOD_LMETA, KMOD_LSHIFT, KMOD_META,
             KMOD_MODE, KMOD_NONE, KMOD_NUM, KMOD_RALT, KMOD_RCTRL, KMOD_RMETA, KMOD_RSHIFT, KMOD_SHIFT, K_0, K_1, K_2,
             K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_AMPERSAND, K_ASTERISK, K_AT, K_BACKQUOTE, K_BACKSLASH, K_BACKSPACE,
             K_BREAK, K_CAPSLOCK, K_CARET, K_CLEAR, K_COLON, K_COMMA, K_DELETE, K_DOLLAR, K_DOWN, K_END, K_EQUALS,
             K_ESCAPE, K_EURO, K_EXCLAIM, K_F1, K_F10, K_F11, K_F12, K_F13, K_F14, K_F15, K_F2, K_F3, K_F4, K_F5, K_F6,
             K_F7, K_F8, K_F9, K_FIRST, K_GREATER, K_HASH, K_HELP, K_HOME, K_INSERT, K_KP0, K_KP1, K_KP2, K_KP3, K_KP4,
             K_KP5, K_KP6, K_KP7, K_KP8, K_KP9, K_KP_DIVIDE, K_KP_ENTER, K_KP_EQUALS, K_KP_MINUS, K_KP_MULTIPLY,
             K_KP_PERIOD, K_KP_PLUS, K_LALT, K_LAST, K_LCTRL, K_LEFT, K_LEFTBRACKET, K_LEFTPAREN, K_LESS, K_LMETA,
             K_LSHIFT, K_LSUPER, K_MENU, K_MINUS, K_MODE, K_NUMLOCK, K_PAGEDOWN, K_PAGEUP, K_PAUSE, K_PERIOD, K_PLUS,
             K_POWER, K_PRINT, K_QUESTION, K_QUOTE, K_QUOTEDBL, K_RALT, K_RCTRL, K_RETURN, K_RIGHT, K_RIGHTBRACKET,
             K_RIGHTPAREN, K_RMETA, K_RSHIFT, K_RSUPER, K_SCROLLOCK, K_SEMICOLON, K_SLASH, K_SPACE, K_SYSREQ, K_TAB,
             K_UNDERSCORE, K_UNKNOWN, K_UP, K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o,
             K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z,"mouse1"]

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
RELOAD = K_r

height = 1000
SCREEN_SIZE = pygame.Rect(0,0,int(height /9 * 17), height)
TEXT_LAYER = 4 # one above the top layer
PLAYER_LAYER2 = 3
PLAYER_LAYER1 = 2
MIDDLE_LAYER = 1
BOTTOM_LAYER = -1
DEFAULT_LEVEL_SIZE = pygame.Rect(0,0, 2000,2000)
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, "data")
TILE_NAMES = ["bottom_left_corner","bottom_left_icorner",
               "bottom_right_corner","bottom_right_icorner",
               "top_right_corner", "top_right_icorner",
               "top_left_corner","top_left_icorner",
               "right_straight1","right_straight2",
               "left_straight1","left_straight2",
               "top_straight1","top_straight2",
               "bottom_straight1","bottom_straight2",
               "middle1","middle2","middle3",
               "diagonal_top_bottom","diagonal_bottom_top",
               "bottom_top_left_corner","bottom_top_right_corner",
               "right_top_left_corner","right_bottom_left_corner",
               "left_top_right_corner","left_bottom_right_corner",
               "top_bottom_left_corner","top_bottom_right_corner",
               "single", "only_top", "only_right", "only_bottom", "only_left",
               "left_right_open","bottom_top_open"]
PATH_NAMES = ["only_left","only_bottom","only_top","only_right",
              "bottom_left_corner","bottom_right_corner","top_right_corner","top_left_corner",
              "bottom_top_open", "left_right_open","middle",
              "left_straight","right_straight","top_straight", "bottom_straight"]
GAME_TIME = pygame.time.Clock()