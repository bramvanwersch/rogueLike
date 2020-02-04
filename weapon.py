#!/usr/bin/env python
# Import Modules
import os, pygame
import numpy as np
import utilities, entities
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

class AbstractWeapon(entities.Entity):
    def __init__(self, image):
        #default pos will need to be assigned when relevant
        entities.Entity.__init__(self,image, pos = (0,0))

class MeleeWeapon(AbstractWeapon):
    def __init__(self, weaponparts):
        AbstractWeapon.__init__(self, self.__create_weapon_image())
        self.parts = weaponparts

    def __create_weapon_image(self):
        """
        Create a combined image that includes all the weapon parts.
        :return: an image and repsective rectangle size.
        """
        pygame.surfarray.use_arraytype("numpy")
        #the weapon parts as an array numpy matrixes containing pixels
        partspixels = [pygame.surfarray.pixels3d(self.parts[x].image) for x in self.parts]
        #widest component is the guard
        width = partspixels[1].shape[0]
        lenght = sum(x.shape[1] for x in partspixels)
        #make final pixel array consisting of width lenght and 3 for rgb values
        final_arr = np.full((width, lenght, 3), 255)
        trl = 0
        # requires size of the parts to be even number of pixels to properly work.
        for pa in partspixels:
            hw = width / 2
            final_arr[int(hw - pa.shape[0]/2):int(hw + pa.shape[0]/2),trl:int(trl + pa.shape[1])] = pa
            trl += pa.shape[1]
        image = pygame.surfarray.make_surface(final_arr)
        #set all the white white pixels transparant
        image.set_colorkey((255,255,255), RLEACCEL)
        return image

class ProjectileWeapon(AbstractWeapon):
    def __init__(self):
        AbstractWeapon.__init__(self)

class AbstractPart:
    def __init__(self, data):
        self.image = utilities.load_image(data["imageName"])
        self.type = data["partType"]
        self.name = data["name"]

class MeleePart(AbstractPart):
    def __init__(self, data):
        AbstractPart.__init__(self, data)

class ProjectilePart(AbstractPart):
    def __init__(self, data):
        AbstractPart.__init__(self, data)