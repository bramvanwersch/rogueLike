import pygame

from game_images import image_sheets, animations
import entities

class Stoner(entities.Enemy):
    SIZE = (500, int(500 / 80 * 64))
    WPS = 500 / 80
    def __init__(self, pos, player, *groups, **kwargs):
        self.base_image = image_sheets["stoner_boss"].image_at((0,0), size=(80,64), color_key=(255,255,255), scale=self.SIZE)
        self.mouth = image_sheets["stoner_boss"].image_at((80,0), size=(32,16), color_key=(255,255,255), scale=(int(self.WPS * 32), int(self.WPS * 16)))
        self.left_eye = image_sheets["stoner_boss"].image_at((0,64), size=(16,16), color_key=(255,255,255), scale=(int(self.WPS * 16), int(self.WPS * 16)))
        self.right_eye = pygame.transform.flip(self.left_eye, True, False)
        self.left_arm = image_sheets["stoner_boss"].image_at((80,16), size=(16,32), color_key=(255,255,255), scale=(int(self.WPS * 16), int(self.WPS * 32)))
        self.right_arm = image_sheets["stoner_boss"].image_at((80, 48), size=(16, 32), color_key=(255, 255, 255), scale=(int(self.WPS * 16), int(self.WPS * 32)))
        image = self.__get_image()
        entities.Enemy.__init__(self, pos, player, *groups, image = image, speed = 0, health = 1000, **kwargs)


    def _get_bounding_box(self):
        return self.rect.inflate((-0.4 * self.rect.width, -0.1 * self.rect.height))

    def update(self,*args):
        super().update()
        self.image = self.__get_image()

    def __get_image(self):
        image = self.base_image
        ir = image.get_rect()
        image.blit(self.mouth, (ir.centerx - 0.5 * self.mouth.get_rect().width, ir.centery - 0.5 * self.mouth.get_rect().height))
        image.blit(self.left_eye, (ir.centerx - self.left_eye.get_rect().width, ir.centery - 0.70 * ir.centery))
        image.blit(self.right_eye, (ir.centerx, ir.centery - 0.70 * ir.centery))
        image.blit(self.left_arm, (ir.left + 12, ir.centery - 0.18 * ir.centery))
        image.blit(self.right_arm, (ir.right - 12 - self.right_arm.get_rect().width, ir.centery - 0.18 * ir.centery))
        return image

