import os,pygame, random
from pygame.locals import *
from pygame.compat import geterror
from constants import SCREEN_SIZE, DEFAULT_LEVEL_SIZE, DATA_DIR

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
        screen_player_x = SCREEN_SIZE[2] / 2 - 1 * (DEFAULT_LEVEL_SIZE.width - SCREEN_SIZE[2] / 2 - coord[0])
    elif coord[0] - SCREEN_SIZE[2] / 2 > 0:
        screen_player_x = SCREEN_SIZE[2] / 2
    else:
        screen_player_x = coord[0]
    if (DEFAULT_LEVEL_SIZE.height - SCREEN_SIZE[3] / 2) - coord[1] + 150 < 0:
        screen_player_y = SCREEN_SIZE[3] / 2 - 1 * (DEFAULT_LEVEL_SIZE.height - SCREEN_SIZE[3] / 2 - coord[1]) - 150
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

