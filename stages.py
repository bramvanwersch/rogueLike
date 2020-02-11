import pygame
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
        self.stage_map = game_map.build_map()
        self.background = Background(self.tile_images,self.props, self.updater)

    def add_enemy(self, name, pos):
        if name == "red square":
            entities.RedSquare(pos, self.player, self.updater, self.enemy_sprites)
        elif name == "bad bat":
            entities.BadBat(pos, self.player, self.updater, self.enemy_sprites)
        elif name == "dummy":
            entities.TestDummy(pos, self.player, self.updater, self.enemy_sprites)
        else:
            print("Warning unknown enemy: "+ name)

class ForestStage(BasicStage):
    """
    Forest stage starting of
    """
    def __init__(self, updater, player):
        self.tile_images = [pygame.transform.scale(self.load_image(x), (100,100)) for x in utilities.FOREST_TILES]
        self.tree_images = {name[:-4]: pygame.transform.scale(self.load_image(name, (255,255,255)), (100,100)) for name in utilities.TREE_IMAGES}
        self.props = [pygame.transform.scale(self.load_image(name), (100,100)) for name in utilities.FOREST_PROPS]
        BasicStage.__init__(self, updater, player)

    def load_image(self, imagename, colorkey=None):
        """
        Automatcally applies the forest asset folder to the requested image making naming easier.
        :param imagename: name of image
        :param colorkey: key for alpha channel
        :return: pygame.image object
        """
        return utilities.load_image("Forest//" + imagename, colorkey)

    def create_tiles(self):
        """
        adds tiles with images to the playing field according to a map that was generated that calculated where these
        images are supposed to be.
        """
        #TODO make the method more uniform to be used by different stages and collections of pictures.
        for y, line in enumerate(self.stage_map):
            for x, letter in enumerate(line):
                image = None
                if letter == "blc":
                    image = self.tree_images["bottom_left_corner_forest"]
                if letter == "tlc":
                    image = self.tree_images["top_left_corner_forest"]
                if letter == "trc":
                    image = self.tree_images["top_right_corner_forest"]
                if letter == "brc":
                    image = self.tree_images["bottom_right_corner_forest"]
                if letter == "blic":
                    image = self.tree_images["bottom_left_icorner_forest"]
                if letter == "tlic":
                    image = self.tree_images["top_left_icorner_forest"]
                if letter == "tric":
                    image = self.tree_images["top_right_icorner_forest"]
                if letter == "bric":
                    image = self.tree_images["bottom_right_icorner_forest"]
                if letter == "ls":
                    image = random.choice((self.tree_images["left_straight_forest1"],
                                          self.tree_images["left_straight_forest2"],
                                          self.tree_images["left_straight_forest3"]))
                if letter == "ts":
                    image = random.choice((self.tree_images["top_straight_forest1"],
                                          self.tree_images["top_straight_forest2"],
                                          self.tree_images["top_straight_forest3"]))
                if letter == "rs":
                    image = random.choice((self.tree_images["right_straight_forest1"],
                                          self.tree_images["right_straight_forest2"],
                                          self.tree_images["right_straight_forest3"]))
                if letter == "bs":
                    image = random.choice((self.tree_images["bottom_straight_forest1"],
                                          self.tree_images["bottom_straight_forest2"],
                                          self.tree_images["bottom_straight_forest3"]))
                if letter == "m":
                    image = random.choice((self.tree_images["middle_forest1"],
                                          self.tree_images["middle_forest2"],
                                          self.tree_images["middle_forest3"]))
                if image:
                    SolidTile(image,(x * 100, y * 100), self.updater, self.tile_sprites)

class Background(entities.Entity):
    def __init__(self, images,props, *groups):
        """
        Creates a large immage as the background for the stage.
        :param location: start location of image
        :param images: images to make the background out of.
        :param groups: groups fro comaera movement.
        """
        self.propnmbr = 150
        image = self.__create_background_image(images, props)
        self.background_group = pygame.sprite.Group()
        entities.Entity.__init__(self, image, (0,0), self.background_group, *groups)

    def __create_background_image(self, images, props):
        """
        Concatenate images into a large nunpy matrix to be trsnalted back into an image by randomly drawing from a pool
        of images provided to this function. This function is mainly a way of saving time and collecting all the
        background noise into one place
        :param images: pygame image
        :return: a pygame image.
        """
        pygame.surfarray.use_arraytype("numpy")
        c180onvertedimages = [pygame.transform.rotate(image, 180) for image in images]
        pp0 = [pygame.surfarray.pixels3d(image) for image in images]
        pp180 = [pygame.surfarray.pixels3d(image) for image in c180onvertedimages]
        partspixels = pp0  + pp180
        proppixels = [pygame.surfarray.pixels3d(image) for image in props]
        image_rows = []
        for i in range(int(utilities.DEFAULT_LEVEL_SIZE.width / 100 + 1)):
            image_row = []
            for j in range(int(utilities.DEFAULT_LEVEL_SIZE.height / 100 + 1)):
                image_row.append(random.choice(partspixels))
            image_rows.append(np.concatenate(image_row, 1))
        final_arr = np.concatenate(image_rows)

        #place props in the background for fast fps. Substantialy increases load times (slow array looping)
        if not utilities.FAST:
            ps = props[0].get_rect().width
            max_props = min(int(utilities.DEFAULT_LEVEL_SIZE.width / ps),int(utilities.DEFAULT_LEVEL_SIZE.height / ps))
            xcoords = [random.randint(0,int(utilities.DEFAULT_LEVEL_SIZE.width / ps)) for _ in range(self.propnmbr * 2)]
            ycoords = [random.randint(0,int(utilities.DEFAULT_LEVEL_SIZE.height / ps)) for _ in range(self.propnmbr * 2)]
            prop_coords = []
            combcoords = list(zip(xcoords, ycoords))
            for coord in combcoords:
                if coord not in prop_coords:
                    prop_coords.append(coord)
            if len(prop_coords) > 50:
                prop_coords = prop_coords[0:50]

            # places props in the background and makes sure that each white pixel is made into the background color.
            # is a quit expensive process
            for i in range(len(prop_coords)):
                prop = random.choice(proppixels)
                for y, row in enumerate(prop):
                    for x, val in enumerate(row):
                        if np.array_equal(val,[255,255,255]): continue
                        final_arr[prop_coords[i][1] * ps + y][prop_coords[i][0] * ps + x] = val


        image = pygame.surfarray.make_surface(final_arr)
        image = image.convert()
        return image

class BasicTile(entities.Entity):
    def __init__(self, image, pos, *groups):
        """
        The basic tile which is a rectangle of a 100 by a 100 that contains relevant information for that rectangle
        :param x: the x coordinate of the top left corner
        :param y: the y coordinate of the top left corner
        """
        entities.Entity.__init__(self, image, pos, *groups)

class SolidTile(BasicTile):
    def __init__(self, image, pos, *groups):
        """
        Tile other entities cannot move trough.
        :param pos: see Entity
        :param image: see Entity
        :param groups: see Entity
        """
        entities.SolidEntity.__init__(self, image, pos, *groups)
        self._layer = utilities.MIDDLE_LAYER

    def _get_bounding_box(self):
        bb = self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.2))
        bb.center = (bb.centerx, bb.centery + self.rect.top - bb.top)
        return bb


