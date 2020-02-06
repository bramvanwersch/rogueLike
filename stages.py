import pygame
import utilities, entities, game_map
import random
import numpy as np

class BasicStage:
    def __init__(self, updater):
        self.tile_sprites = pygame.sprite.Group()
        #layer updater or camera where the tile instances need to be added to.
        self.updater = updater
        self.stage_map = game_map.build_map()
        self.background = Background(self.tile_images, self.updater)

    def load_unload_tiles(self, playercenter):
        #TODO optimize this by using matrix and exclusion to check around the character instead of all tiles.
        #roughly an area twice the screen size is loaded
        range_rect = pygame.Rect(0,0,utilities.SCREEN_SIZE.width * 2 , utilities.SCREEN_SIZE.height * 2)
        range_rect.center = playercenter
        for i,tile in enumerate(self.tile_sprites.sprites()):
            if tile.visible and not range_rect.colliderect(tile.rect):
                tile.visible = False
            elif not tile.visible and range_rect.colliderect(tile.rect):
                tile.visible = True

class Stage1(BasicStage):
    """
    Forest stage starting of
    """
    def __init__(self, updater):
        self.tile_images = [utilities.load_image("stage1_tile1.bmp",), utilities.load_image("stage1_tile2.bmp")]
        self.tree_images = {name[:-4]: pygame.transform.scale(utilities.load_image(name, (255,255,255)), (100,100)) for name in utilities.TREE_IMAGES}
        BasicStage.__init__(self, updater)
        # self.props = utilities.load_props(1)

    def create_tiles(self):
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
                    t = SolidTile(image,(x * 100, y * 100), self.tile_sprites, self.updater)

class Background(entities.Entity):
    def __init__(self, images, *groups):
        """
        Creates a large immage as the background for the stage.
        :param location: start location of image
        :param images: images to make the background out of.
        :param groups: groups fro comaera movement.
        """
        image = self.__create_background_image(images)
        self.background_group = pygame.sprite.Group()
        entities.Entity.__init__(self, image, (0,0), self.background_group, *groups)

    def __create_background_image(self, images):
        """
        Concatenate images into a large nunpy matrix to be trsnalted back into an image by randomly drawing from a pool
        of images. Provided to this function
        :param images: pygame image
        :return: a pygame image.
        """
        pygame.surfarray.use_arraytype("numpy")
        c180onvertedimages = [pygame.transform.rotate(image, 180) for image in images]
        pp0 = [pygame.surfarray.pixels3d(image) for image in images]
        pp180 = [pygame.surfarray.pixels3d(image) for image in c180onvertedimages]
        partspixels = pp0  + pp180
        image_rows = []
        for i in range(int(utilities.DEFAULT_LEVEL_SIZE.width / 100 + 1)):
            image_row = []
            for j in range(int(utilities.DEFAULT_LEVEL_SIZE.height / 100 + 1)):
                image_row.append(random.choice(partspixels))
            image_rows.append(np.concatenate(image_row, 1))
        final_arr = np.concatenate(image_rows)
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
        self.collision = False

class SolidTile(BasicTile):
    def __init__(self, image, pos, *groups):
        """
        Tile other entities cannot move trough.
        :param pos: see Entity
        :param image: see Entity
        :param groups: see Entity
        """
        entities.SolidEntity.__init__(self, image, pos, *groups)
