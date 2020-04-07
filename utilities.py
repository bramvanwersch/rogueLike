import os,pygame, random
from pygame.locals import *
from pygame.compat import geterror


#test constant
BOUNDING_BOXES = False
NR_ENTITIES = True
FPS = True
ENTITY_PATHS = False
VISION_LINE = False

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
               "top_bottom_left_corner","top_bottom_right_corner"]
PATH_NAMES = ["straight_horizontal", "straight_vertical","center"]
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
          s += "{:>3}".format(value)
        s += "\n"
    print(s)

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
        if not isinstance(image_names[0], pygame.Surface):
            animation_images = [pygame.transform.scale(load_image(name, color), scale) for name in image_names]
            flipped_images = [pygame.transform.flip(img, True, False) for img in animation_images]
            self.animation_images = list(zip(animation_images,flipped_images))
        else:
            flipped_images = [pygame.transform.flip(img, True, False) for img in image_names]
            self.animation_images = list(zip(image_names,flipped_images))
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
