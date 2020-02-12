import pygame
from pygame.locals import *
import utilities, entities, game_map
import random
import numpy as np

class BasicStage:
    def __init__(self, updater, player):
        self.tile_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        #layer updater or camera where the tile instances need to be added to.
        self.updater = updater
        self.player = player
        self.tiles = []
        self.stage_map = game_map.build_map()

    def _create_tiles(self, stage_name):
        for y, line in enumerate(self.stage_map):
            for x, letter in enumerate(line):
                image = None
                if letter == "blc":
                    image = self.tile_images["bottom_left_corner_" + stage_name]
                if letter == "tlc":
                    image = self.tile_images["top_left_corner_" + stage_name]
                if letter == "trc":
                    image = self.tile_images["top_right_corner_" + stage_name]
                if letter == "brc":
                    image = self.tile_images["bottom_right_corner_" + stage_name]
                if letter == "blic":
                    image = self.tile_images["bottom_left_icorner_" + stage_name]
                if letter == "tlic":
                    image = self.tile_images["top_left_icorner_" + stage_name]
                if letter == "tric":
                    image = self.tile_images["top_right_icorner_" + stage_name]
                if letter == "bric":
                    image = self.tile_images["bottom_right_icorner_" + stage_name]
                if letter == "ls":
                    image = random.choice((self.tile_images["left_straight1_" + stage_name],
                                           self.tile_images["left_straight2_" + stage_name],
                                           self.tile_images["left_straight3_" + stage_name]))
                if letter == "ts":
                    image = random.choice((self.tile_images["top_straight1_" + stage_name],
                                           self.tile_images["top_straight2_" + stage_name],
                                           self.tile_images["top_straight3_" + stage_name]))
                if letter == "rs":
                    image = random.choice((self.tile_images["right_straight1_" + stage_name],
                                           self.tile_images["right_straight2_" + stage_name],
                                           self.tile_images["right_straight3_" + stage_name]))
                if letter == "bs":
                    image = random.choice((self.tile_images["bottom_straight1_" + stage_name],
                                           self.tile_images["bottom_straight2_" + stage_name],
                                           self.tile_images["bottom_straight3_" + stage_name]))
                if letter == "m":
                    image = random.choice((self.tile_images["middle1_" + stage_name],
                                           self.tile_images["middle2_" + stage_name],
                                           self.tile_images["middle3_" + stage_name]))
                if image:
                    self.tiles.append(BasicTile(image, (x * 100, y * 100)))

    def add_enemy(self, name, pos):
        if name == "red square":
            entities.RedSquare(pos, self.player, self.tiles, self.updater, self.enemy_sprites)
        elif name == "bad bat":
            entities.BadBat(pos, self.player, self.tiles, self.updater,self.enemy_sprites)
        elif name == "dummy":
            entities.TestDummy(pos, self.player, self.tiles, self.updater, self.enemy_sprites)
        else:
            print("Warning unknown enemy: "+ name)

class ForestStage(BasicStage):
    """
    Forest stage starting of
    """
    def __init__(self, updater, player):
        BasicStage.__init__(self, updater, player)
        self.background_images = [pygame.transform.scale(self.load_image(x), (100, 100)) for x in utilities.FOREST_TILES]
        self.tile_images = {name[:-4]: pygame.transform.scale(self.load_image(name), (100, 100)) for name in utilities.TREE_IMAGES}
        self.props = [pygame.transform.scale(self.load_image(name), (100,100)) for name in utilities.FOREST_PROPS]
        self._create_tiles("forest")
        self.background = Background(self.background_images,self.props, self.tiles,"background", self.updater)
        self.tile_props = Background(self.background_images,self.props, self.tiles,"prop tiles", self.updater)

    def load_image(self, imagename, colorkey=None):
        """
        Automatcally applies the forest asset folder to the requested image making naming easier.
        :param imagename: name of image
        :param colorkey: key for alpha channel
        :return: pygame.image object
        """
        return utilities.load_image("Forest//" + imagename, colorkey)

class Background(entities.Entity):
    def __init__(self, back_images, props, tiles, type, *groups):
        """
        Creates a large immage as the background for the stage.
        :param location: start location of image
        :param back_images: images to make the background out of.
        :param groups: groups fro comaera movement.
        """
        self.propnmbr = 150
        if type == "background":
            image = self.__create_background_image(back_images, props, tiles)
        elif type == "prop tiles":
            image = self.__create_props_and_tiles_image(props, tiles)
        self.background_group = pygame.sprite.Group()
        entities.Entity.__init__(self, image, (0,0), self.background_group, *groups)

    def __create_background_image(self, images, props, tiles):
        pygame.surfarray.use_arraytype("numpy")
        c180onvertedimages = [pygame.transform.rotate(image, 180) for image in images]
        pp0 = [pygame.surfarray.pixels3d(image) for image in images]
        pp180 = [pygame.surfarray.pixels3d(image) for image in c180onvertedimages]
        partspixels = pp0  + pp180
        proppixels = [pygame.surfarray.pixels3d(image) for image in props]
        image_rows = []
        for i in range(int(utilities.DEFAULT_LEVEL_SIZE.width / 100 )):
            image_row = []
            for j in range(int(utilities.DEFAULT_LEVEL_SIZE.height / 100 )):
                image_row.append(random.choice(partspixels))
            image_rows.append(np.concatenate(image_row, 1))
        final_arr = np.concatenate(image_rows)

        image = pygame.surfarray.make_surface(final_arr)
        image = image.convert()
        return image

    def __create_props_and_tiles_image(self, props, tiles):
        pygame.surfarray.use_arraytype("numpy")
        ps = props[0].get_rect().width
        tile_coords = [tile.topleft for tile in tiles]
        max_props = min(int(utilities.DEFAULT_LEVEL_SIZE.width / ps),int(utilities.DEFAULT_LEVEL_SIZE.height / ps))
        xcoords = [random.randint(0,int(utilities.DEFAULT_LEVEL_SIZE.width / ps)) for _ in range(self.propnmbr * 2)]
        ycoords = [random.randint(0,int(utilities.DEFAULT_LEVEL_SIZE.height / ps)) for _ in range(self.propnmbr * 2)]
        prop_coords = []
        combcoords = list(zip(xcoords, ycoords))
        for coord in combcoords:
            if coord not in prop_coords:
                prop_coords.append(coord)
        if len(prop_coords) > self.propnmbr:
            prop_coords = prop_coords[0:self.propnmbr]
        prop_coords = [(coord[0] * ps, coord[1] * ps) for coord in prop_coords]
        all_coords = prop_coords + tiles
        all_coords.sort(key = lambda x: self.__sort_on_y_coord(x), reverse = True)
        final_arr = np.full((utilities.DEFAULT_LEVEL_SIZE.width, utilities.DEFAULT_LEVEL_SIZE.height, 3), 255)
        for coord in all_coords:
            if isinstance(coord, BasicTile):
                px = pygame.surfarray.pixels3d(coord.image)
                final_arr[coord.x :coord.x + coord.width, coord.y: coord.y + coord.height] = px
            #TODO add props part
        image = pygame.surfarray.make_surface(final_arr)
        image.set_colorkey((255,255,255), RLEACCEL)
        image = image.convert()
        return image

    def __sort_on_y_coord(self, val):
        if isinstance(val, BasicTile):
            return val.y
        else:
            return val[1]

        # places props in the background and makes sure that each white pixel is made into the background color.
        # is a quit expensive process
        # for i in range(len(prop_coords)):
        #     prop = random.choice(proppixels)
        #     for y, row in enumerate(prop):
        #         for x, val in enumerate(row):
        #             if np.array_equal(val,[255,255,255]): continue
        #             final_arr[prop_coords[i][1] * ps + y][prop_coords[i][0] * ps + x] = val
        #

class BasicTile:
    def __init__(self,image, pos):
        """
        The basic tile which is a rectangle of a 100 by a 100 that contains relevant information for that rectangle
        :param x: the x coordinate of the top left corner
        :param y: the y coordinate of the top left corner
        """
        self.rect = pygame.Rect(*pos,100,100)
        self.image = image

    def _get_bounding_box(self):
        bb = rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.2))
        bb.center = (bb.centerx, bb.centery + self.rect.top - bb.top)
        return bb

    def __getattr__(self, name):
        return self.rect.__getattribute__(name)

# class SolidTile(BasicTile):
#     def __init__(self, image, pos, *groups):
#         """
#         Tile other entities cannot move trough.
#         :param pos: see Entity
#         :param image: see Entity
#         :param groups: see Entity
#         """
#         entities.SolidEntity.__init__(self, image, pos, *groups)
#         self._layer = utilities.MIDDLE_LAYER
#
#     def _get_bounding_box(self):
#         bb = self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.2))
#         bb.center = (bb.centerx, bb.centery + self.rect.top - bb.top)
#         return bb


