import pygame, random

from game_images import image_sheets, animations
from constants import *
import entities

class Stoner(entities.Enemy):
    _PPS = PPS_STONER
    def __init__(self, pos, player, *groups, **kwargs):
        self.orig_base_image = image_sheets["stoner_boss"].image_at((0,0), size=(80,64), color_key=(255,255,255), pps=self.PPS)
        self.orig_mouth = image_sheets["stoner_boss"].image_at((80,0), size=(32,16), color_key=(255,255,255), pps=self.PPS)
        self.orig_left_eye = image_sheets["stoner_boss"].image_at((0,64), size=(16,16), color_key=(255,255,255), pps=self.PPS)
        self.orig_right_eye = pygame.transform.flip(self.orig_left_eye, True, False)
        self.orig_left_arm = image_sheets["stoner_boss"].image_at((80,16), size=(16,32), color_key=(255,255,255), pps=self.PPS)
        self.orig_right_arm = image_sheets["stoner_boss"].image_at((80, 48), size=(16, 32), color_key=(255, 255, 255), pps=self.PPS)
        self.base_image, self.mouth, self.left_eye, self.right_eye, self.left_arm, self.right_arm = \
            self.orig_base_image, self.orig_mouth, self.orig_left_eye, self.orig_right_eye, self.orig_left_arm, self.orig_right_arm
        self.smile_animation = animations["smile_Stoner"]
        image = self.__get_image()
        entities.Enemy.__init__(self, pos, player, *groups, speed = 0, health = 1000, **kwargs)
        #track if any of the parts changed to make sure to only blit a new boss image when needed
        self.an_image_changed = False

    def _get_bounding_box(self):
        return self.rect.inflate((-0.4 * self.rect.width, -0.1 * self.rect.height))

    def update(self,*args):
        super().update()
        self.__run_anmimations()
        if self.an_image_changed:
            img = self.__get_image()
            self.change_image((img, img))
        self.an_image_changed = False

    def __run_anmimations(self):
        if not self.smile_animation.finished:
            self.smile_animation.update()
            if self.smile_animation.changed_image:
                self.mouth = self.smile_animation.image[0]
                self.an_image_changed = True
        if random.randint(0,20) == 1 and self.smile_animation.finished  :
            self.smile_animation.reset()

    def __get_image(self):
        #make sure no pointers
        image = pygame.Surface((self.orig_base_image.get_rect().size))
        image.fill((255,255,255))
        image.blit(self.orig_base_image, (0,0))
        ir = image.get_rect()
        image.blit(self.mouth, (ir.centerx - 0.5 * self.mouth.get_rect().width, ir.centery - 0.5 * self.mouth.get_rect().height))
        image.blit(self.left_eye, (ir.centerx - self.left_eye.get_rect().width, ir.centery - 0.70 * ir.centery))
        image.blit(self.right_eye, (ir.centerx, ir.centery - 0.70 * ir.centery))
        image.blit(self.left_arm, (ir.left + 12, ir.centery - 0.18 * ir.centery))
        image.blit(self.right_arm, (ir.right - 12 - self.right_arm.get_rect().width, ir.centery - 0.18 * ir.centery))
        image.set_colorkey((255,255,255), RLEACCEL)
        image = image.convert_alpha()
        return image