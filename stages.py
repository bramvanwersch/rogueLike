import pygame
from pygame.locals import *
import utilities, entities, game_map, prop_entities
from game_images import sheets

class BasicStage:
    def __init__(self, updater, player, weapons = []):
        self.interacting_group = pygame.sprite.Group()
        # self.weapons = weapons
        self.updater = updater
        self.player = player
        #values are set here to indicat that these are class varaibles. They are defined using the set room function
        self.background = None
        self.room_props = None
        self.tiles = None
        #find the start room and set the stage to that room
        for x in self.stage_rooms_map:
            for room in x:
                #set the innitial values
                if isinstance(room, game_map.Room) and room.room_type == 2:
                    self.current_room = room
                    self.background = entities.Entity((0, 0), self.updater, image=room.background_image)
                    self.room_props = entities.Entity((0, 0), self.updater,  image=room.room_image)
                    self.set_room(room)
                    break

    #function purely defined as an action function for connecting rooms
    def action(self):
        pr = self.player.rect
        cr = self.current_room.rect
        if pr.x > 0.75 * cr.width * 100:
            room = self.stage_rooms_map[cr[1]][cr[0] + 1]
            self.player.rect.topleft = (110, room.connections[3][1] * 100)
        elif pr.x < 0.25 * cr.width * 100:
            room = self.stage_rooms_map[cr[1]][cr[0] - 1]
            self.player.rect.topleft = (cr.width * 100 - 110 - self.player.rect.width, room.connections[1][1] * 100)
        elif pr.y > 0.75 * cr.height * 100:
            room = self.stage_rooms_map[cr[1] + 1][cr[0]]
            self.player.rect.topleft = (room.connections[0][0] * 100, 110)
        elif pr.y < 0.25 * cr.height * 100:
            room = self.stage_rooms_map[cr[1] - 1][cr[0]]
            self.player.rect.topleft = (room.connections[2][0] * 100, cr.height * 100 - 110 - self.player.rect.height)
        self.set_room(room)

    def set_room(self, room):
        self.background.image = room.background_image
        self.room_props.image = room.room_image
        self.tiles = room.tiles
        #remove all the interacting entities
        for sprite in self.interacting_group.sprites():
            sprite.kill()
        self.interacting_group.empty()
        #update the tiles for the player. The enemies should be spawned per room.
        self.player.tiles = self.tiles
        self.current_room = room
        for tile in self.tiles.interactable_tiles:
            if tile.action:
                entities.InteractingEntity(tile.topleft, self.player, self.updater, self.interacting_group,
                                           action = tile.action)
            elif tile.action_desc:
                if tile.action_desc == "room_transition":
                    entities.InteractingEntity(tile.topleft, self.player, self.updater, self.interacting_group,
                                               action=self.action, visible = [False, False])
            elif utilities.WARNINGS:
                print("Interacting tile with no interaction specified!!!")

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
    def __init__(self, updater, player, **kwargs):
        background_images = sheets["forest"].images_at((208,16),(224,16),(240,16), (0,32), scale = (100,100))

        #create a dictionary with named tile variant to make an easy way of creating the map.
        forest_images = sheets["forest"].images_at_rectangle((0,0,256,16), (0,16,208,16), (32,80,112,16), scale = (100,100))
        lake_images = sheets["forest"].images_at_rectangle((0,48,256,16), (0,64,208,16), (144,80,112,16), scale = (100,100))
        path_images = sheets["forest"].images_at_rectangle((0,96,240,16), scale = (100,100))
        fd = {name + "_forest": forest_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        ld = {name + "_lake": lake_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        pd = {name + "_path": path_images[i] for i, name in enumerate(utilities.PATH_NAMES)}
        tile_images = {**fd, **ld, **pd}
        props = sheets["forest"].images_at_rectangle((16,32,160,16), scale = (100,100))
        self.stage_rooms_map = game_map.build_map((5, 5), wheights = [8, 2], background_images = background_images,
                                                  tile_images = tile_images, props = props, solid_tile_names = ["forest", "lake"])
        BasicStage.__init__(self, updater, player, **kwargs)



