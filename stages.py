import pygame
import utilities, entities, game_map
import random
import numpy as np

class BasicStage:
    def __init__(self, updater):
        self.size = "" #TODO see if implementation is needed
        #matrix for storing discovered tiles
        self.tile_sprites = pygame.sprite.Group()
        #create empty matrix for tile objects
        self.tiles = []
        #layer updater or camera where the tile instances need to be added to.
        self.updater = updater
        self.stage_map = game_map.build_map()
        self.background = Background(self.tile_images, self.tile_sprites, self.updater)

    def add_tile(self, pos, image, *groups):
        #choose random amount of props
        # amnt = random.randint(0,5)
        # props = random.sample(props, amnt)
        tile = PathTile(pos,image, *groups) # TODO needs proper fixing
        self.tiles.append(tile)

    def load_unload_tiles(self, playercenter):
        #TODO optimize this by using matrix and exclusion to check around the character instead of all tiles.
        #roughly an area twice the screen size is loaded
        range_rect = pygame.Rect(0,0,utilities.SCREEN_SIZE.width * 2 , utilities.SCREEN_SIZE.height * 2)
        range_rect.center = playercenter
        for i,tile in enumerate(self.tiles):
            if tile.visible and not range_rect.colliderect(tile.rect):
                tile.visible = False
            elif not tile.visible and range_rect.colliderect(tile.rect):
                tile.visible = True

class Stage1(BasicStage):
    """
    Forest stage starting of
    """
    size = 2000 # number of tiles
    def __init__(self, updater):
        self.tile_images = [utilities.load_image("stage1_tile1.bmp",), utilities.load_image("stage1_tile2.bmp")]
        BasicStage.__init__(self, updater)
        self.forest_image = utilities.load_image("test_forest.bmp")
        # self.props = utilities.load_props(1)

    def create_tiles(self):
        for y, line in enumerate(self.stage_map):
            for x, letter in enumerate(line):
                if letter == 1:
                    self.add_tile((x * 100, y * 100),self.forest_image, self.tile_sprites, self.updater)

class Background(entities.Entity):
    def __init__(self, images, *groups):
        """
        Creates a large immage as the background for the stage.
        :param location: start location of image
        :param images: images to make the background out of.
        :param groups: groups fro comaera movement.
        """
        image = self.__create_background_image(images)
        entities.Entity.__init__(self, image, (0,0), *groups)

    def __create_background_image(self, images):
        """
        Concatenate images into a large nunpy matrix to be trsnalted back into an image by randomly drawing from a pool
        of images.sas
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
    def __init__(self, pos, image, *groups):
        """
        The basic tile which is a rectangle of a 100 by a 100 that contains relevant information for that rectangle
        :param x: the x coordinate of the top left corner
        :param y: the y coordinate of the top left corner
        """
        entities.Entity.__init__(self, image, pos, *groups)

    def contains(self, rect):
        """
        Wrapper function for testing tile containment.
        :param rect: a rectangle that is supposed to be contained in this tile.
        :return: boolean
        """
        return self.rect.contains(rect)

class PathTile(BasicTile):
    def __init__(self, pos, image, *groups):
        """
        For stage1 tiles holding specific images
        :param x: see BasicTile
        :param y: see BasicTile
        :param props: a list of props that are present on this tile.
        """
        BasicTile.__init__(self, pos, image, *groups)
        self.props = ""

class BorderTile(BasicTile):
    def __init__(self, pos, image, *groups):
        BasicTile.__init__(self, pos, image, *groups)
