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
        self.weapons = weapons
        self.updater = updater
        self.player = player
        self.tiles = TileGroup()

    def _create_tiles(self, stage_names):
        for y, line in enumerate(self.stage_map):
            for x, letter in enumerate(line):
                image = None
                if letter != 0:
                    number = int(letter[-1]) -1
                    letter = letter[:-1]
                if letter == "blc":
                    image = self.tile_images["bottom_left_corner_" + stage_names[number]]
                elif letter == "tlc":
                    image = self.tile_images["top_left_corner_" + stage_names[number]]
                elif letter == "trc":
                    image = self.tile_images["top_right_corner_" + stage_names[number]]
                elif letter == "brc":
                    image = self.tile_images["bottom_right_corner_" + stage_names[number]]
                elif letter == "blic":
                    image = self.tile_images["bottom_left_icorner_" + stage_names[number]]
                elif letter == "tlic":
                    image = self.tile_images["top_left_icorner_" + stage_names[number]]
                elif letter == "tric":
                    image = self.tile_images["top_right_icorner_" + stage_names[number]]
                elif letter == "bric":
                    image = self.tile_images["bottom_right_icorner_" + stage_names[number]]
                elif letter == "ls":
                    image = random.choice([self.tile_images[key] for key in self.tile_images if "left_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "ts":
                    image = random.choice([self.tile_images[key] for key in self.tile_images if "top_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "rs":
                    image = random.choice([self.tile_images[key] for key in self.tile_images if "right_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "bs":
                    image = random.choice([self.tile_images[key] for key in self.tile_images if "bottom_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "m":
                    image = random.choice([self.tile_images[key] for key in self.tile_images if "middle" in \
                                           key and stage_names[number] in key])
                elif letter == "tbd":
                    image = self.tile_images["diagonal_top_bottom_" + stage_names[number]]
                elif letter == "btd":
                    image = self.tile_images["diagonal_bottom_top_" + stage_names[number]]
                elif letter == "btrc":
                    image = self.tile_images["bottom_top_right_corner_" + stage_names[number]]
                elif letter == "btlc":
                    image = self.tile_images["bottom_top_left_corner_" + stage_names[number]]
                elif letter == "rtlc":
                    image = self.tile_images["right_top_left_corner_" + stage_names[number]]
                elif letter == "rblc":
                    image = self.tile_images["right_bottom_left_corner_" + stage_names[number]]
                elif letter == "ltrc":
                    image = self.tile_images["left_top_right_corner_" + stage_names[number]]
                elif letter == "lbrc":
                    image = self.tile_images["left_bottom_right_corner_" + stage_names[number]]
                elif letter == "tblc":
                    image = self.tile_images["top_bottom_left_corner_" + stage_names[number]]
                elif letter == "tbrc":
                    image = self.tile_images["top_bottom_right_corner_" + stage_names[number]]
                if image:
                    if number == 0:
                        self.tiles[y][x] = SolidTile(image, (x * 100, y * 100), high = True)
                    else:
                        self.tiles[y][x] = SolidTile(image, (x * 100, y * 100))
                else:
                    self.tiles[y][x] = BasicTile((x * 100, y * 100))
        finishtile = FinishTile((int((self.tiles.size[0] - 2) * 100), int(self.tiles.size[1] / 2 * 100)), self.player, self.updater)
        #temporary
        chest = prop_entities.Chest((int((self.tiles.size[0] - 2) * 100), int((self.tiles.size[1] / 2 -2)* 100)),\
                                    self.player,self.get_random_weapons(5), self.updater)
        # self.tiles[int(self.tiles.size[1] / 2)][int(self.tiles.size[0] - 2)] = finishtile
        # self.tiles.finish_tiles.append(finishtile)
        #do some calculatuions after all tiles are added to speed up calculations
        self.tiles.setup()

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
        BasicStage.__init__(self, updater, player, **kwargs)
        self.stage_map = game_map.build_map(wheights = [8,2])
        self.background_images = sheets["forest"].images_at((208,16),(224,16),(240,16), (0,32), scale = (100,100))

        #create a dictionary with named tile variant to make an easy way of creating the map.
        forest_images = sheets["forest"].images_at_rectangle((0,0,256,16), (0,16,208,16), scale = (100,100))
        lake_images = sheets["forest"].images_at_rectangle((0,48,256,16), (0,64,208,16), scale = (100,100))
        fd = {name + "_forest": forest_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        ld = {name + "_lake": lake_images[i] for i, name in enumerate(utilities.TILE_NAMES)}
        self.tile_images = {**fd, **ld}
        self.props = sheets["forest"].images_at_rectangle((16,32,160,16), scale = (100,100))

        self._create_tiles(["forest","lake"])

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
        self.propnmbr = 50
        if type == "background":
            image = self.__create_background_image(back_images)
        elif type == "prop tiles":
            image = self.__create_props_and_tiles_image(props, tiles)
        self.background_group = pygame.sprite.Group()
        entities.Entity.__init__(self, (0,0), self.background_group, *groups, image = image)

    def __create_background_image(self, images):
        pygame.surfarray.use_arraytype("numpy")
        c180onvertedimages = [pygame.transform.rotate(image, 180) for image in images]
        pp0 = [pygame.surfarray.pixels3d(image) for image in images]
        pp180 = [pygame.surfarray.pixels3d(image) for image in c180onvertedimages]
        partspixels = pp0  + pp180
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
        ps = props[0].get_rect().width

        max_props = min(int(utilities.DEFAULT_LEVEL_SIZE.width / ps),int(utilities.DEFAULT_LEVEL_SIZE.height / ps))
        xcoords = [random.randint(0,int(utilities.DEFAULT_LEVEL_SIZE.width / ps)-1) for _ in range(self.propnmbr * 2)]
        ycoords = [random.randint(0,int(utilities.DEFAULT_LEVEL_SIZE.height / ps)-1) for _ in range(self.propnmbr * 2)]
        prop_coords = []
        combcoords = list(zip(xcoords, ycoords))
        for coord in combcoords:
            if coord not in prop_coords:
                prop_coords.append(coord)
        if len(prop_coords) > self.propnmbr:
            prop_coords = prop_coords[0:self.propnmbr]
        prop_coords = [(coord[0] * ps, coord[1] * ps) for coord in prop_coords]
        non_zero_tiles = tiles.get_non_zero_tiles()
        all_coords = prop_coords + non_zero_tiles
        all_coords.sort(key = lambda x: self.__sort_on_y_coord(x))
        image = pygame.Surface((utilities.DEFAULT_LEVEL_SIZE.width, utilities.DEFAULT_LEVEL_SIZE.height))
        image.fill((255,255,255))
        final_arr = np.full((utilities.DEFAULT_LEVEL_SIZE.width, utilities.DEFAULT_LEVEL_SIZE.height, 3), 255)
        for coord in all_coords:
            if isinstance(coord, SolidTile):
                image.blit(coord.image, (coord.rect.topleft))
            elif not isinstance(coord, BasicTile):
                image.blit(random.choice(props), (coord[0],coord[1]))
        image.set_colorkey((255,255,255), RLEACCEL)
        image = image.convert()
        return image

    def __sort_on_y_coord(self, val):
        if isinstance(val, BasicTile):
            return val.y
        elif isinstance(val, FinishTile):
            return val.rect.y
        else:
            return val[1]

class TileGroup:
    def __init__(self):
        """
        Class for managing the tiles as a group and calculating fast collisions or other things
        """
        #dont make fcking pointers
        self.tiles = [[0] *int(utilities.DEFAULT_LEVEL_SIZE.width / 100) for _ in range(int(utilities.DEFAULT_LEVEL_SIZE.height / 100))]
        self.finish_tiles = []
        self.__truth_map = [[True] *int(utilities.DEFAULT_LEVEL_SIZE.width / 100) for _ in range(int(utilities.DEFAULT_LEVEL_SIZE.height / 100))]

    def __getitem__(self, i):
        return self.tiles[i]

    def setup(self):
        self.__calculate_truth_map()
        self.__configure_bounding_boxes()

    def get_non_zero_tiles(self):
        return [tile for row in self.tiles for tile in row if isinstance(tile, BasicTile)]

    @property
    def size(self):
        return (len(self.tiles[0]),len(self.tiles))

    def finish_collide(self, rect):
        #propably one tile
        for finish in self.finish_tiles:
            if finish.colliderect(rect):
                return True
        return False

    def solid_collide(self, rect, height = True):
        """
        Fast method for calculating collision by checking the 4 cornors and seeing with what tiles they overlap. This
        makes it at most 4 checks for collision. Also checks for out of bounds
        :param rect: a rectangle that is checked for an overlap
        :param height tells if there should be checked for height when checking collision
        :return: a boolean indicating a collsion (True) or not (False)
        """
        xtl, ytl = [int(c/100) for c in rect.topleft]
        try:
            tile = self.tiles[ytl][xtl]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                elif height:
                    return False
                return True
            xtr, ytr = [int(c/100) for c in rect.topright]
            tile = self.tiles[ytr][xtr]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                else:
                    return False
                return True
            xbl, ybl = [int(c/100) for c in rect.bottomleft]
            tile = self.tiles[ybl][xbl]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                else:
                    return False
                return True
            xbr, ybr = [int(c/100) for c in rect.bottomright]
            tile = self.tiles[ybr][xbr]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                else:
                    return False
                return True
        #if index error is raised then you are outside the board.
        except IndexError:
            return True
        return False

    def pathfind(self, player_rect, dest_rect):
        x,y = int(player_rect.x / 100), int(player_rect.y / 100)
        start_tile = self.tiles[y][x]
        dest_tile = self.tiles[int(dest_rect.y/100)][int(dest_rect.x/100)]
        if not self.__truth_map[y][x]:
            return [None]
        #add starting tile to values to make it available for x,y coordinates
        paths = [[start_tile],[start_tile],[start_tile],[start_tile]]
        cur_dist = self.__tile_dist(start_tile, dest_tile)
        walked_tiles = [[],[],[],[]]
        final_path = [None]
        while cur_dist > 0 and len(paths) > 0:
            for i, path in enumerate(paths):
                available_tiles = []
                x,y = path[-1].coord
                if not x + 1 >= len(self.tiles[0]) and self.__truth_map[y][x + 1] and self.tiles[y][x + 1] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y][x + 1])
                if not x - 1 < 0 and self.__truth_map[y][x - 1] and self.tiles[y][x - 1] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y][x - 1])
                if not y + 1 >= len(self.tiles) and self.__truth_map[y + 1][x] and self.tiles[y + 1][x] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y + 1][x])
                if not y - 1 < 0 and self.__truth_map[y - 1][x] and self.tiles[y - 1][x] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y - 1][x])
                if available_tiles:
                    #swap tile order to make an if statement check be before the others
                    available_tiles = available_tiles[i:] + available_tiles[:i]
                    tile = min(available_tiles, key = lambda x: self.__tile_dist(x, dest_tile))
                    walked_tiles[i].append(tile)
                    path.append(tile)
                    cur_dist = self.__tile_dist(tile, dest_tile)
                    final_path = path
                else:
                    #TODO look into these cases and see if it is worth fixing them.
                    # print("break")
                    paths.remove(path)
                    final_path = path
        return final_path

    def __tile_dist(self,t1, t2):
        """
        Manhatten distance between two tiles, t1 and t2
        """
        return abs(t1.coord[0] - t2.coord[0]) + abs(t1.coord[1] - t2.coord[1])

    def __all_min_tiles(self,dest_tile, tiles):
        if len(tiles) == 1:
            return tiles
        min_tiles = [tiles[0]]
        for tile in tiles:
            if self.__tile_dist(dest_tile, tile) < self.__tile_dist(dest_tile, min_tiles[0]):
                min_tiles = [tile]
            elif self.__tile_dist(dest_tile, tile) == self.__tile_dist(dest_tile, min_tiles[0]):
                min_tiles.append(tile)
        return min_tiles

    def __calculate_truth_map(self):
        """
        Function for making a matrix that tells if a tile is solid or not.
        """
        for y, row in enumerate(self.tiles):
            for x, val in enumerate(row):
                if isinstance(val, SolidTile):
                    self.__truth_map[y][x] = False

    def __configure_bounding_boxes(self):
        for row in self.tiles:
            for tile in row:
                if isinstance(tile, SolidTile):
                    sur_tiles = [True,True,True,True]
                    x,y = tile.coord
                    if y - 1 > 0 and not isinstance(self.tiles[y - 1][x], SolidTile):
                        sur_tiles[0] = False
                    if x + 1 < len(self.tiles[0]) and not isinstance(self.tiles[y][x + 1], SolidTile):
                        sur_tiles[1] = False
                    if y + 1 < len(self.tiles) and not isinstance(self.tiles[y + 1][x], SolidTile):
                        sur_tiles[2] = False
                    if x - 1 > 0 and not isinstance(self.tiles[y][x - 1], SolidTile):
                        sur_tiles[3] = False
                    tile.set_bounding_box(sur_tiles)

class BasicTile:
    def __init__(self, pos):
        """
        The basic tile which is a rectangle of a 100 by a 100 that contains relevant information for that rectangle
        :param x: the x coordinate of the top left corner
        :param y: the y coordinate of the top left corner
        """
        self.rect = pygame.Rect(*pos,100,100)

    def __getattr__(self, name):
        return self.rect.__getattribute__(name)

    @property
    def coord(self):
        return [int(self.x / 100), int(self.y / 100)]

    def __str__(self):
        return str(self.coord[0]) + "," + str(self.coord[1])

class SolidTile(BasicTile):
    def __init__(self, image, pos, high = False):
        BasicTile.__init__(self, pos)
        #is chamged after all the tiles are added
        self.bounding_box = self.rect
        self.image = image
        self.high = high

    def __getattr__(self, name):
        return self.bounding_box.__getattribute__(name)

    def set_bounding_box(self, surrounding_tiles):
        bb = pygame.Rect(self.rect)
        # print(bb)
        if not surrounding_tiles[0]:
            bb = bb.inflate((0, - int(self.rect.height * 0.2)))
            bb.bottom = self.rect.bottom
        elif not surrounding_tiles[2]:
            bb = bb.inflate((0, - int(self.rect.height * 0.2)))
            bb.top = self.rect.top
        if not surrounding_tiles[1]:
            bb = bb.inflate((-int(self.rect.width * 0.2), 0))
            bb.left = self.rect.left
        elif not surrounding_tiles[3]:
            bb = bb.inflate((-int(self.rect.width * 0.2), 0))
            bb.right = self.rect.right
        self.bounding_box = bb

class FinishTile(entities.InteractingEntity):
    def __init__(self, pos, player, *groups):
        image = sheets["forest"].image_at((240,32), scale = (80,80), color_key = (255,255,255))
        entities.InteractingEntity.__init__(self, pos, player, *groups, image = image)
        self._layer = utilities.MIDDLE_LAYER

    def interact(self):
        print("interacting")

    @property
    def coord(self):
        return [int(self.rect.x / 100), int(self.rect.y / 100)]
