import pygame, random
from pygame.locals import *
import utilities, entities, game_map, prop_entities
from game_images import sheets

class BasicStage:
    def __init__(self, updater, player, weapons = []):
        self.interacting_group = pygame.sprite.Group()
        self.transition_group = pygame.sprite.Group()
        self.enemy_sprite_group = pygame.sprite.Group()
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
                    self.background = entities.Entity((0, 0), self.updater, image=room.room_layout.background_image)
                    self.room_props = entities.Entity((0, 0), self.updater,  image=room.room_layout.room_image)
                    self.set_room(room)
                    break

    def update(self):
        #function for checking updates relating to stages.
        if len(self.enemy_sprite_group.sprites()) <= 0:
            self.current_room.finished = True
            for sprite in self.transition_group.sprites():
                sprite.visible = [False,False]
                sprite.collision = False

    #function purely defined as an action function for connecting rooms
    def action(self):
        if not self.current_room.finished:
            return
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
        self.background.image = room.room_layout.background_image
        self.room_props.image = room.room_layout.room_image
        #remove all the interacting entities
        for sprite in self.interacting_group.sprites():
            sprite.kill()
        self.interacting_group.empty()
        self.transition_group.empty()
        #remove all enemie sprites to be sure.
        for sprite in self.enemy_sprite_group.sprites():
            sprite.dead = True
        #update the tiles for the player. The enemies should be spawned per room.
        self.current_room = room
        self.player.tiles = self.current_room.tiles
        for tile in self.current_room.tiles.interactable_tiles:
            if tile.action:
                entities.InteractingEntity(tile.topleft, self.player, self.updater, self.interacting_group,
                                           action = tile.action)
            elif tile.action_desc:
                if tile.action_desc == "room_transition":
                    entities.InteractingEntity(tile.topleft, self.player, self.updater, self.transition_group, self.interacting_group,
                                               action=self.action, visible = [True, True], collision = True)
            elif utilities.WARNINGS:
                print("Interacting tile with no interaction specified!!!")
        if not utilities.PEACEFULL and not self.current_room.finished:
            for enemie in self.current_room.enemies:
                self.add_enemy(*enemie)

    def get_random_weapons(self, amnt = 1):
        weapons = []
        for i in range(amnt):
            weapons.append(self.weapons.pop(-i))
        return weapons

    def add_enemy(self, name, pos):
        if name == "red square":
            entities.RedSquare(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group)
        elif name == "bad bat":
            entities.BadBat(pos, self.player, self.current_room.tiles, self.updater,self.enemy_sprite_group)
        elif name == "dummy":
            entities.TestDummy(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group)
        elif name == "archer":
            entities.Archer(pos, self.player, self.current_room.tiles, self.updater, self.enemy_sprite_group)
        else:
            print("Warning unknown enemy: "+ name)

class ForestStage(BasicStage):
    def __init__(self, updater, player, **kwargs):
        background_images = sheets["forest"].images_at((208,16),(224,16),(240,16), (0,32), scale = (100,100))
        forest_images = sheets["forest"].images_at_rectangle((0,0,256,16), (0,16,208,16), (32,80,112,16), scale = (100,100))
        lake_images = sheets["forest"].images_at_rectangle((0,48,256,16), (0,64,208,16), (144,80,112,16), scale = (100,100))
        path_images = sheets["forest"].images_at_rectangle((0,96,240,16), scale = (100,100))
        fd = {name + "_forest": forest_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        ld = {name + "_lake": lake_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        pd = {name + "_path": path_images[i] for i, name in enumerate(utilities.PATH_NAMES)}
        tile_images = {**fd, **ld, **pd}
        props = sheets["forest"].images_at_rectangle((16,32,160,16), scale = (100,100))
        self.stage_rooms_map = game_map.build_map((5, 5), solid_tile_weights = [8, 2], background_images = background_images,
                                        tile_images = tile_images, props = props, solid_tile_names = ["forest", "lake"],
                                        enemies = [["red square", entities.RedSquare.SIZE], ["bad bat",entities.BadBat.SIZE],
                                                   ["archer",entities.Archer.SIZE]], spawn_weights = [1,2,1],
                                        spawn_amnt_range = [0,5])
        BasicStage.__init__(self, updater, player, **kwargs)



