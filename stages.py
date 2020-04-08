import pygame, sys
from pygame.locals import *
import utilities, entities, game_map, prop_entities
from game_images import sheets
import random
import numpy as np

class BasicStage:
    def __init__(self, updater, player, weapons = []):
        self.enemy_sprites = pygame.sprite.Group()
        #layer updater or camera where the tile instances need to be added to.
        # self.weapons = weapons
        self.updater = updater
        self.player = player
        room1 = self.stage_map[list(self.stage_map.keys())[1]]
        self.background = entities.Entity((0,0), self.updater, image = room1.background_image)
        self.room_props = entities.Entity((0,0), self.updater, image = room1.room_image)
        self.tiles = room1.tiles

    def get_random_weapons(self, amnt = 1):
        weapons = []
        for i in range(amnt):
            weapons.append(self.weapons.pop(-i))
        return weapons

    def add_enemy(self, name, pos):
        if name == "red square":
            entities.RedSquare(pos, self.player, self.tiles, self.updater, self.enemy_sprites)
        elif name == "bad bat":
            entities.BadBat(pos, self.player, self.tiles, self.updater,self.enemy_sprites)
        elif name == "dummy":
            entities.TestDummy(pos, self.player, self.tiles, self.updater, self.enemy_sprites)
        elif name == "archer":
            entities.Archer(pos, self.player, self.tiles, self.updater, self.enemy_sprites)
        else:
            print("Warning unknown enemy: "+ name)

class ForestStage(BasicStage):
    """
    Forest stage starting of
    """
    def __init__(self, updater, player, **kwargs):
        background_images = sheets["forest"].images_at((208,16),(224,16),(240,16), (0,32), scale = (100,100))

        #create a dictionary with named tile variant to make an easy way of creating the map.
        forest_images = sheets["forest"].images_at_rectangle((0,0,256,16), (0,16,208,16), scale = (100,100))
        lake_images = sheets["forest"].images_at_rectangle((0,48,256,16), (0,64,208,16), scale = (100,100))
        path_images = sheets["forest"].images_at_rectangle((208,64,48,16), scale = (100,100))
        fd = {name + "_forest": forest_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        ld = {name + "_lake": lake_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        pd = {name: path_images[i] for i, name in enumerate(utilities.PATH_NAMES)}
        tile_images = {**fd, **ld, **pd}
        props = sheets["forest"].images_at_rectangle((16,32,160,16), scale = (100,100))
        self.stage_map = game_map.build_map((5,5), wheights = [8, 2], background_images = background_images,
                                            tile_images = tile_images, props = props, solid_tile_names = ["forest", "lake"])
        BasicStage.__init__(self, updater, player, **kwargs)



