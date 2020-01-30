#!/usr/bin/env python
# Import Modules
import os, pygame
import numpy as np
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
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
    return image, image.get_rect()

class AbstractWeapon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class MeleeWeapon(AbstractWeapon):
    def __init__(self, weaponparts):
        AbstractWeapon.__init__(self)
        #TODO fill this in when making a weapon
        self.parts = weaponparts
        self.image,self.rect = self.__create_weapon_image()

    def __create_weapon_image(self):
        pygame.surfarray.use_arraytype("numpy")
        #the weapon parts as an array numpy matrixes containing pixels
        partspixels = [pygame.surfarray.pixels3d(self.parts[x].image) for x in self.parts]
        #widest component is the guard
        width = partspixels[2].shape[0]
        lenght = sum(x.shape[1] for x in partspixels)
        #make final pixel array consisting of width lenght and 3 for rgb values
        final_arr = np.full((width, lenght, 3), 255)
        # final_arr[0:10,10:20] = partspixels[0]
        trl = 0
        # requires size of the parts to be even number of pixels to properly work.
        for pa in partspixels:
            hw = width / 2
            final_arr[int(hw - pa.shape[0]/2):int(hw + pa.shape[0]/2),trl:int(trl + pa.shape[1])] = pa
            trl += pa.shape[1]
        image = pygame.surfarray.make_surface(final_arr)
        return image, image.get_rect()

class ProjectileWeapon(AbstractWeapon):
    def __init__(self):
        AbstractWeapon.__init__(self)

class AbstractPart(pygame.sprite.Sprite):
    def __init__(self, data):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(data["imageName"])
        self.type = data["partType"]

class MeleePart(AbstractPart):
    def __init__(self, data):
        AbstractPart.__init__(self, data)

class ProjectilePart(AbstractPart):
    def __init__(self, data):
        AbstractPart.__init__(self, data)