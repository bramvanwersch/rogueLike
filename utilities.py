import os,pygame, random
from pygame.locals import *
from pygame.compat import geterror


#some global constants
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(MAIN_DIR, "data")
#TODO make forest props as a list of filenames of bitmaps.
STAGE1_PROPS = [""]
height = 1000
SCREEN_SIZE = pygame.Rect(0,0,int(height /9 * 16), height)
TOP_LAYER = 2
DEFAULT_LEVEL_SIZE = pygame.Rect(0,0, 2000,1000)

seed = 5

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

def load_props(stage):
    """
    Loads all props for a certain stage and puts them in a dictionary for easy use.
    :param stage: an integer for stage that the props are needed for
    :return: a dictionary containing prop names as keys and pygame.image instances as values.
    """
    props = {}
    #TODO add for other stages when they are made.
    if stage == 1:
        files = STAGE1_PROPS
    else:
        raise NameError("Unknown stage {}".format(stage))
    for filename in files:
        #remove the .bmp extension
        props[filename[:-4]] = load_image(filename, (255,255,255))
    return props

def generate_map():
    stagemap = ["".join(["P_"]* int(DEFAULT_LEVEL_SIZE.width / 100))]*int(DEFAULT_LEVEL_SIZE.height /100)
    print(len(stagemap), len(stagemap[0]))
    return stagemap

