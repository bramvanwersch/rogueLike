import pygame
import utilities

class BasicStage:
    def __init__(self, size):
        self.size = size
        #matrix for storing discovered tiles
        self.map = [[]]

class Stage1(BasicStage):
    """
    Forest stage starting of
    """
    size = 2000 # number of tiles
    def __init__(self):
        BasicStage.__init__(self, size)
        # TODO needs proper name
        self.props = utilities.load_props(1)


class BasicTile:
    def __init__(self, x ,y):
        """
        The basic tile which is a rectangle of a 100 by a 100 that contains relevant information for that rectangle
        :param x: the x coordinate of the top left corner
        :param y: the y coordinate of the top left corner
        """
        self.rect = pygame.rect.Rect(x, y, 100, 100)

    def contains(self, rect):
        """
        Wrapper function for testing tile containment.
        :param rect: a rectangle that is supposed to be contained in this tile.
        :return: boolean
        """
        return self.rect.contains(rect)

class Stage1Tile(BasicTile):
    def __init__(self, x, y, props):
        """
        For stage1 tiles holding specific images
        :param x: see BasicTile
        :param y: see BasicTile
        :param props: a list of props that are present on this tile.
        """
        BasicTile.__init__(self, x, y)
        #TODO make this immage of 100 by 100 pixels.
        self.image, self.image_rect = utilities.load_image("forest_ground.bmp")
        self.props = props