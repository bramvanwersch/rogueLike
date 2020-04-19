import os,pygame, random
from pygame.locals import *
from pygame.compat import geterror
import game_map

#test constant
WARNINGS = True
BOUNDING_BOXES = False
NR_ENTITIES = True
FPS = True
ENTITY_PATHS = False
VISION_LINE = False
PEACEFULL = False

#some global constants
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, "data")
BACKGROUND_COLOR = (165,103,10)

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
height = 1000
GAME_TIME = pygame.time.Clock()

#drawing methods
SCREEN_SIZE = pygame.Rect(0,0,int(height /9 * 17), height)
TEXT_LAYER = 4 # one above the top layer
PLAYER_LAYER2 = 3
PLAYER_LAYER1 = 2
MIDDLE_LAYER = 1
BOTTOM_LAYER = -1
DEFAULT_LEVEL_SIZE = pygame.Rect(0,0, 2000,2000)

#game settings
seed = random.randint(0,1000)
scene_name = "Main"
going = True

def fancy_matrix_print(matrix):
    s = ""
    for row in matrix:
        for value in row:
            if isinstance(value, game_map.Room):
                s += "{:>3}".format(value.room_type)
            else:
                s += "{:>3}".format(value)
        s += "\n"
    print(s)

def get_screen_relative_coordinate(coord):
    if (DEFAULT_LEVEL_SIZE.width - SCREEN_SIZE[2] / 2) - coord[0] < 0:
        screen_player_x = SCREEN_SIZE[2] / 2 - 1 * ( DEFAULT_LEVEL_SIZE.width - SCREEN_SIZE[2] / 2 - coord[0])
    elif coord[0] - SCREEN_SIZE[2] / 2 > 0:
        screen_player_x = SCREEN_SIZE[2] / 2
    else:
        screen_player_x = coord[0]
    if (DEFAULT_LEVEL_SIZE.height - SCREEN_SIZE[3] / 2) - coord[1] + 150 < 0:
        screen_player_y = SCREEN_SIZE[3] / 2 - 1 * ( DEFAULT_LEVEL_SIZE.height - SCREEN_SIZE[3] / 2 - coord[1]) - 150
    elif coord[1] - SCREEN_SIZE[3] / 2 > 0:
        screen_player_y = SCREEN_SIZE[3] / 2
    else:
        screen_player_y = coord[1]
    return (screen_player_x, screen_player_y)

def get_wheighted_array(array, wheights):
    """
    Create an array that has each ellement of the orignal array times the amount of the wheight in it.
    :param array: an array of presumably unique values
    :param wheights: an array of integers the same lenght as the array of values
    :return: an array that is the lenght of the sum of the integers in the wheights array
    """
    assert len(array) == len(wheights)
    wheighted_array = [[value]* wheights[i] for i, value in enumerate(array)]
    wheighted_array = [number for row in wheighted_array for number in row]
    return wheighted_array

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
    def __init__(self, *images, speed = 10, color = (255, 255, 255), scale = (0, 0), repetition ="continuous", start_frame = 0):
        """
        Stores an animation to be progressed when calling the update of the animation
        :param images: list of all the images to be played in sequence
        :param speed: the amount of updates needed before the next image is saved
        :param color: the color of the images that need to be transparant
        :param scale: a scale factor to apply to all the animation images
        :param start_frame: the frame to start on or the keyword 'random' to start at a random frame
        """
        if isinstance(images[0], tuple):
            self.animation_images = images
        else:
            flipped_images = [pygame.transform.flip(img, True, False) for img in images]
            self.animation_images = list(zip(images, flipped_images))
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
        self.repetition = repetition
        self.finished = False

    def update(self):
        """
        Function to be called every update to progress the animation. This methods loops endlesly when called
        """
        #allows for configuring an animation for a certain amount of cycles.
        if not self.repetition == "continuous" and self.cycles >= self.repetition:
            self.finished = True
            #make sure to end and add a flag to allow to stop refreshing.
            return
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
        self.finished = False

class MarkedAnimation(Animation):
    def __init__(self, *images, speed = 10, color = (255, 255, 255), scale = (0, 0), start_frame = 0, marked_frames = []):
        """
        allows some marked frames that then can be tracked by the marked property
        :param marked_frames: a list of integers of marked frames
        """
        Animation.__init__(self, *images, speed = speed, color = color, scale = scale, start_frame=start_frame)
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
