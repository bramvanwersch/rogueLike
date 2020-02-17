#!/usr/bin/env python
# Import Modules
import os, pygame
import numpy as np
import utilities, entities, manufacturers
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

class AbstractWeapon:
    def __init__(self, image):
        #default pos will need to be assigned when relevant
        #TODO at some point this transform needs to go and the images cobined using blitting.
        self.image = pygame.transform.scale(image, (int(image.get_rect().width * 0.7),int(image.get_rect().height * 0.8)))
        self.rect = self.image.get_rect()

class MeleeWeapon(AbstractWeapon):
    def __init__(self, weaponparts):
        self.parts = weaponparts
        AbstractWeapon.__init__(self, self.__create_weapon_image())
        self.damage, self.reload_speed, self.fire_rate, self.weight = self.__calculate_stats()

    def __calculate_stats(self):
        #handle determines the manufactorer of the melee weapon
        manufactorer = manufacturers.get_manufacturer(self.parts["handle"].manufacturer)
        damage =  manufactorer.damage
        reload_speed = manufactorer.reload_speed
        fire_rate = manufactorer.fire_rate
        weight = manufactorer.weight
        for part in self.parts:
            damage += self.parts[part].damage
            reload_speed += self.parts[part].reload_speed
            fire_rate += self.parts[part].fire_rate
            weight += self.parts[part].weight
        return damage, reload_speed, fire_rate, weight

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
        # image = pygame.transform.scale(image, (int(image.get_rect()[2] * 0.8), int(image.get_rect()[3] * 0.8)))
        image = image.convert()
        return image

class ProjectileWeapon(AbstractWeapon):
    def __init__(self):
        AbstractWeapon.__init__(self)

class AbstractPart:
    def __init__(self, data):
        self.image = utilities.load_image(data["imageName"])
        self.type = data["partType"]
        self.name = data["name"]
        self.damage = int(data["damage"])
        self.manufacturer = data["manufacturer"]
        self.reload_speed = int(data["reload speed"])
        self.fire_rate = int(data["fire rate"])
        self.weight = int(data["wheight"])

class MeleePart(AbstractPart):
    def __init__(self, data):
        AbstractPart.__init__(self, data)

class ProjectilePart(AbstractPart):
    def __init__(self, data):
        AbstractPart.__init__(self, data)