import os,pygame
from constants import *
from pygame.locals import *
from pygame.compat import geterror

sheets = {}

def load():
    """
    Loads all the available sheets into memory and saves them by a descriptive name in a dictionary
    :return:
    """
    global sheets
    sheets["player"] = Spritesheet("player_sprite_sheet.bmp",(16,32))

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

class Spritesheet:
    def __init__(self, filename, size):
        self.sheet = load_image(filename)
        self.image_size = size

    def image_at(self, coord, color_key = None, scale = None):
        rect = pygame.Rect(*coord, *self.image_size)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pygame.RLEACCEL)
            image = image.convert_alpha()
        if scale is not None:
            image = pygame.transform.scale(image, scale)
        return image

    def images_at(self, *coords, color_key = None, scale = None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, color_key, scale) for rect in coords]