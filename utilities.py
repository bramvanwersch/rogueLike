import os,pygame, random
from pygame.locals import *
from pygame.compat import geterror

#test constant
FAST = True
TEST = False

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
BOTTOM_LAYER = -1
DEFAULT_LEVEL_SIZE = pygame.Rect(0,0, 2000,2000)
seed = 2

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
        """
        Stores an animation to be progressed when calling the update of the animation
        :param image_names: list of all the images to be played in sequence
        :param speed: the amount of updates needed before the next image is saved
        :param color: the color of the images that need to be transparant
        :param scale: a scale factor to apply to all the animation images
        :param start_frame: the frame to start on or the keyword 'random' to start at a random frame
        """
        self.animation_images = [pygame.transform.scale(load_image(name, color), scale) for name in image_names]
        self.frame_count = 0
        if isinstance(speed, list):
            assert len(speed) == len(self.animation_images)
            self.speed = speed
        else:
            self.speed = [speed]* len(self.animation_images)
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
        if self.frame_count % self.speed[self.current_frame] == 0:
            self.current_frame += 1
            self.frame_count = 0
        if self.current_frame >= len(self.animation_images):
            self.current_frame = 0
            self.cycles += 1
            return
        self.image = self.animation_images[self.current_frame]

    def reset(self):
        """
        resets the animation to the beginning state
        """
        self.frame_count = 0
        self.current_frame = 0
        self.image = self.animation_images[0]
        self.cycles = 0

class MarkedAnimation(Animation):
    def __init__(self, *image_names, speed = 10, color = (255,255,255), scale = (0,0), start_frame = 0, marked_frames = []):
        """
        allows some marked frames that then can be tracked by the marked property
        :param marked_frames: a list of integers of marked frames
        """
        Animation.__init__(self, *image_names, speed = speed, color = color, scale = scale, start_frame=start_frame)
        #list of frames that can be tracked by the special property
        self.marked_frames = marked_frames
        self.marked = False

    def update(self):
        super().update()
        if self.current_frame in self.marked_frames:
            self.marked = True
        else:
            self.marked = False

    def reset(self):
        super().reset()
        self.marked = False

# class AttackAnimation(Animation):
#     def __init__(self, image, speed = 10, color = (255,255,255), scale = (0,0), start_frame = 0, anglerange = [0,50],
#                  number_of_frames = 5 ):
#         self.__image = image
#         self.animation_images = [image]
#         Animation.__init__(self, [], speed = speed, color = color, scale = scale, start_frame=start_frame)
#         self.animation_images = [image]
#         self.number_of_frames = number_of_frames
#         self.angle_range = anglerange
#
#     def update(self):
#         """
#         Function to be called every update to progress the animation. This methods loops endlesly when called
#         """
#         self.frame_count += 1
#         if self.frame_count % self.speed == 0:
#             self.image = pygame.transform.rotate(self.__image, self.angle_range[1] / self.number_of_frames + self.angle_range[0])
#             self.current_frame += 1
#         if self.current_frame >= number:
#             self.current_frame = 0
#             self.frame_count = 0
#             self.cycles += 1