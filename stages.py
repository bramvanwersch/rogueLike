import pygame
import utilities, entities
import random

class BasicStage:
    def __init__(self, updater):
        self.size = "" #TODO see if implementation is needed
        #matrix for storing discovered tiles
        self.tiles = pygame.sprite.Group()
        #layer updater or camera where the tile instances need to be added to.
        self.updater = updater

    def add_tile(self, pos):
        #choose random amount of props
        # amnt = random.randint(0,5)
        # props = random.sample(props, amnt)
       Stage1Tile(pos, self.tile_image, self.tiles, self.updater)

class Stage1(BasicStage):
    """
    Forest stage starting of
    """
    size = 2000 # number of tiles
    def __init__(self, updater):
        BasicStage.__init__(self, updater)
        # TODO needs proper name
        # self.props = utilities.load_props(1)
        self.tile_image = utilities.load_image("forest_ground.bmp")


class BasicTile(entities.Entity):
    def __init__(self, pos, image, *groups):
        """
        The basic tile which is a rectangle of a 100 by a 100 that contains relevant information for that rectangle
        :param x: the x coordinate of the top left corner
        :param y: the y coordinate of the top left corner
        """
        entities.Entity.__init__(self, image, pos, *groups)
        # tests if a certain tile should be visible
        self.visible = True

    def contains(self, rect):
        """
        Wrapper function for testing tile containment.
        :param rect: a rectangle that is supposed to be contained in this tile.
        :return: boolean
        """
        return self.rect.contains(rect)

class Stage1Tile(BasicTile):
    def __init__(self, pos, image, *groups):
        """
        For stage1 tiles holding specific images
        :param x: see BasicTile
        :param y: see BasicTile
        :param props: a list of props that are present on this tile.
        """
        BasicTile.__init__(self, pos, image, *groups)
        self.props = ""