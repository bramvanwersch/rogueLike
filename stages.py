import pygame, random
from pygame.locals import *

import game_images
import utilities, enemy_methods, game_map, prop_entities, enemy_methods, constants, bosses, entities
from constants import game_rules
from game_images import image_sheets

class BasicStage:
    def __init__(self, updater, player, weapons = []):
        self.interacting_group = pygame.sprite.Group()
        self.transition_group = pygame.sprite.Group()
        self.enemy_sprite_group = pygame.sprite.Group()
        self.room_group = pygame.sprite.Group()
        # self.weapons = weapons
        self.updater = updater
        self.player = player
        #values are set here to indicat that these are class varaibles. They are defined using the set room function
        self.background = None
        self.room_props = None
        #find the start room and set the stage to that room
        for x in self.stage_rooms_map:
            for room in x:
                #set the innitial values
                if isinstance(room, game_map.Room) and room.room_type == 2:
                    self.current_room = room
                    self.background = entities.Entity((0, 0), self.updater, image=room.room_layout.background_image, visible = [True, False])
                    self.room_props = entities.Entity((0, 0), self.updater,  image=room.room_layout.room_image, visible = [True, False])
                    self.set_room(room)
                    break

    def update(self):
        if len(self.enemy_sprite_group.sprites()) <= 0:
            for sprite in self.transition_group.sprites():
                sprite.interactable = True

    #function purely defined as an action function for connecting rooms
    def action(self):
        pr = self.player.rect
        cr = self.current_room.rect

        if pr.x > 0.75 * cr.width * constants.TILE_SIZE[0]:
            room = self.stage_rooms_map[cr[1]][cr[0] + 1]
            self.player.rect.topleft = (110, room.connections[3][1] * constants.TILE_SIZE[1])
        elif pr.x < 0.25 * cr.width * constants.TILE_SIZE[0]:
            room = self.stage_rooms_map[cr[1]][cr[0] - 1]
            self.player.rect.topleft = (room.rect.width * constants.TILE_SIZE[0] - 110 - self.player.rect.width, room.connections[1][1] * constants.TILE_SIZE[1])
        elif pr.y > 0.75 * cr.height * constants.TILE_SIZE[1]:
            room = self.stage_rooms_map[cr[1] + 1][cr[0]]
            self.player.rect.topleft = (room.connections[0][0] * constants.TILE_SIZE[0], 110)
        elif pr.y < 0.25 * cr.height * constants.TILE_SIZE[1]:
            room = self.stage_rooms_map[cr[1] - 1][cr[0]]
            self.player.rect.topleft = (room.connections[2][0] * constants.TILE_SIZE[0], room.rect.height * constants.TILE_SIZE[1] - 110 - self.player.rect.height)
        self.set_room(room)

    def set_room(self, room):
        #reset room parameters
        self.current_room.finished = True

        self.background.change_image((room.room_layout.background_image, room.room_layout.background_image))
        self.room_props.change_image((room.room_layout.room_image,room.room_layout.room_image))
        #remove all the interacting enemy_methods
        self.__remove_sprites()
        #update the tiles for the player. The enemies should be spawned per room.
        self.current_room = room
        self.player.tiles = self.current_room.tiles
        for tile in self.current_room.tiles.interactable_tiles:
            if tile.action:
                enemy_methods.InteractingEntity(tile.topleft, self.player, self.updater, self.interacting_group,
                                           action = tile.action)
            elif tile.action_desc:
                if tile.action_desc == "room_transition":
                    topleft = list(tile.topleft)
                    tis = self.animation_images[0][0].get_rect()
                    if tile.coord[0] == 0:
                        topleft[1] -= (tis.height - constants.TILE_SIZE[1]) * 0.5
                    elif tile.coord[0] == self.current_room.tiles.size[0] - 1:
                        topleft[0] -= tis.width - constants.TILE_SIZE[0]
                        topleft[1] -= (tis.height - constants.TILE_SIZE[1]) * 0.5
                    elif tile.coord[1] == 0:
                        topleft[0] -= (tis.width - constants.TILE_SIZE[0]) * 0.5
                    elif tile.coord[1] == self.current_room.tiles.size[1] - 1:
                        topleft[0] -= (tis.width - constants.TILE_SIZE[0])* 0.5
                        topleft[1] -= tis.height - constants.TILE_SIZE[1]
                    entities.InteractingEntity(topleft, self.player, self.updater, self.transition_group, self.interacting_group, self.room_group,
                                               action=self.action, visible = [True, True], image = self.animation_images[0][0],
                                               interactable=False, trigger_cooldown=[30,30],
                                               animation=game_images.Animation(*self.animation_images, repetition=1, speed = 7))
            elif game_rules.warnings:
                print("Interacting tile with no interaction specified!!!")
        if not game_rules.peacefull and not self.current_room.finished:
            for enemie in self.current_room.enemies:
                self.add_enemy(*enemie)

    def __remove_sprites(self):
        for sprite in self.room_group.sprites():
            sprite.dead = True
        self.room_group.empty()

    def get_random_weapons(self, amnt = 1):
        weapons = []
        for i in range(amnt):
            weapons.append(self.weapons.pop(-i))
        return weapons

    def add_enemy(self, name, pos):
        if name == "RedSquare":
            enemy_methods.RedSquare(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group, self.room_group, center = True)
        elif name == "BadBat":
            enemy_methods.BadBat(pos, self.player, self.current_room.tiles, self.updater,self.enemy_sprite_group, self.room_group, center = True)
        elif name == "Dummy":
            enemy_methods.TestDummy(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group, self.room_group, center = True)
        elif name == "BlowMan":
            enemy_methods.BlowMan(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group, self.room_group, center = True)
        elif name == "BushMan":
            enemy_methods.BushMan(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group, self.room_group, center = True)
        elif name == "Stoner":
            bosses.Stoner(pos, self.player, self.updater, self.enemy_sprite_group, self.room_group, tiles = self.current_room.tiles, center = True)
        elif game_rules.warnings:
            print("Warning unknown enemy: "+ name)

class ForestStage(BasicStage):
    def __init__(self, updater, player, **kwargs):
        background_images = image_sheets["forest"].images_at((208, 16), (224, 16), (240, 16), (0, 32), scale = (100, 100))
        forest_images = image_sheets["forest"].images_at_rectangle((0, 0, 256, 16), (0, 16, 208, 16), (32, 80, 112, 16), scale = (100, 100))
        lake_images = image_sheets["forest"].images_at_rectangle((0, 48, 256, 16), (0, 64, 208, 16), (144, 80, 112, 16), scale = (100, 100))
        path_images = image_sheets["forest"].images_at_rectangle((0, 96, 240, 16), scale = (100, 100))
        fd = {name + "_forest": forest_images[i] for i, name in enumerate(constants.TILE_NAMES)}
        ld = {name + "_lake": lake_images[i] for i, name in enumerate(constants.TILE_NAMES)}
        pd = {name + "_path": path_images[i] for i, name in enumerate(constants.PATH_NAMES)}
        tile_images = {**fd, **ld, **pd}
        props = image_sheets["forest"].images_at_rectangle((16, 32, 160, 16), scale = (100, 100))
        imgs = image_sheets["forest"].images_at_rectangle((0, 112, 256, 32), size = (32, 32), scale = (130, 130), color_key= (255, 255, 255))
        fimgs = [pygame.transform.flip(img, True, False) for img in imgs]
        self.animation_images = list(zip(imgs, fimgs))
        self.stage_rooms_map = game_map.build_map((5, 5), solid_tile_weights = [8, 2], background_images = background_images,
                                                  tile_images = tile_images, props = props, solid_tile_names = ["forest", "lake"],
                                                  enemies = [["RedSquare", enemy_methods.RedSquare.SIZE], ["BadBat",enemy_methods.BadBat.SIZE],
                                                             ["BlowMan", enemy_methods.BlowMan.SIZE], ["BushMan", enemy_methods.BushMan.SIZE]],
                                                  spawn_weights = [1,2,1,4], spawn_amnt_range = [1,5], bosses = ["Stoner"])
        BasicStage.__init__(self, updater, player, **kwargs)



