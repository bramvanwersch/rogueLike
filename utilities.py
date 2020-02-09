import os,pygame, random
from pygame.locals import *
from pygame.compat import geterror

#test constant
FAST = True

#some global constants
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, "data")

FOREST_TILES = ["forest_tile1.bmp","forest_tile2.bmp","forest_tile3.bmp","forest_tile4.bmp",]
FOREST_PROPS = ["bush1.bmp","bush2.bmp","fern1.bmp","fern2.bmp","fern3.bmp","fern4.bmp",
                "stone1.bmp","stone2.bmp","stone3.bmp","stone4.bmp"]
TREE_IMAGES = ["bottom_left_corner_forest.bmp","bottom_left_icorner_forest.bmp",
               "bottom_right_corner_forest.bmp","bottom_right_icorner_forest.bmp",
               "top_right_corner_forest.bmp", "top_right_icorner_forest.bmp",
               "top_left_corner_forest.bmp","top_left_icorner_forest.bmp",
               "right_straight_forest1.bmp","right_straight_forest2.bmp","right_straight_forest3.bmp",
               "left_straight_forest1.bmp","left_straight_forest2.bmp","left_straight_forest3.bmp",
               "top_straight_forest1.bmp","top_straight_forest2.bmp","top_straight_forest3.bmp",
               "bottom_straight_forest1.bmp","bottom_straight_forest2.bmp","bottom_straight_forest3.bmp",
               "middle_forest1.bmp","middle_forest2.bmp","middle_forest3.bmp"]

height = 1000
GAME_TIME = pygame.time.Clock()

SCREEN_SIZE = pygame.Rect(0,0,int(height /9 * 16), height)
TEXT_LAYER = 4 # one above the top layer
PLAYER_LAYER2 = 3
PLAYER_LAYER1 = 2
MIDDLE_LAYER = 1
DEFAULT_LEVEL_SIZE = pygame.Rect(0,0, 2500,2500)
seed = 1

def load_image(name, colorkey=None):
    fullname = os.path.join(DATA_DIR, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
        image = image.convert_alpha()
    return image

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(DATA_DIR, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound

class Animation:
    def __init__(self, *image_names, speed = 10, color = (255,255,255), scale = (0,0), start_frame = 0):
        self.animation_images = [pygame.transform.scale(load_image(name, color), scale) for name in image_names]
        self.frame_count = 0
        self.speed = speed
        if start_frame == "random":
            self.current_frame = random.randint(0,len(self.animation_images) -1)
        else:
            self.current_frame = start_frame
        self.image = self.animation_images[0]
        self.cycles = 0

    def update(self):
        """
        Function to be called every update to progress the animation. This methods loops endlesly when called
        """
        self.frame_count += 1
        if self.frame_count % self.speed == 0:
            self.image = self.animation_images[self.current_frame]
            self.current_frame += 1
        if self.current_frame >= len(self.animation_images):
            self.current_frame = 0
            self.frame_count = 0
            self.cycles += 1

    def reset(self):
        """
        resets the animation to the beginning state
        """
        self.frame_count = 0
        self.current_frame = 0
        self.image = self.animation_images[0]
        self.cycles = 0