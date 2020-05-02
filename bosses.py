import pygame

from game_images import image_sheets, animations
import entities

class Stoner(entities.Enemy):
    SIZE = (500,500)
    def __init__(self, pos, player, *groups, **kwargs):
        image = image_sheets["enemies"].image_at((0,96), size=(80,64), color_key=(255,255,255), scale=self.SIZE)
        entities.Enemy.__init__(self, pos, player, *groups, image = image, speed = 0, health = 1000, **kwargs)


    def _get_bounding_box(self):
        return self.rect.inflate((-0.4 * self.rect.width, -0.1 * self.rect.height))
