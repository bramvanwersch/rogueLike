import pygame, random

import enemy_methods
from game_images import image_sheets, animations
from constants import *
import entities

class Stoner(enemy_methods.Enemy):
    _PPS = PPS_STONER
    def __init__(self, pos, player, *groups, **kwargs):
        self.orig_base_image = image_sheets["stoner_boss"].image_at((0,0), size=(80,64), color_key=(255,255,255), pps=self.PPS)
        self.orig_mouth = image_sheets["stoner_boss"].image_at((144,16), size=(32,16), color_key=(255,255,255), pps=self.PPS)
        self.orig_left_eye = image_sheets["stoner_boss"].image_at((0,64), size=(16,16), color_key=(255,255,255), pps=self.PPS)
        self.orig_right_eye = pygame.transform.flip(self.orig_left_eye, True, False)
        self.orig_left_arm = image_sheets["stoner_boss"].image_at((0,80), size=(32,32), color_key=(255,255,255), pps=self.PPS)
        self.orig_right_arm = image_sheets["stoner_boss"].image_at((0, 112), size=(32, 32), color_key=(255, 255, 255), pps=self.PPS)
        self.base_image, self.mouth, self.left_eye, self.right_eye, self.left_arm, self.right_arm = \
            self.orig_base_image, self.orig_mouth, self.orig_left_eye, self.orig_right_eye, self.orig_left_arm, self.orig_right_arm
        self.smile_animation = animations["smile_Stoner"]
        self.left_lift_animation = animations["lift_left_arm_Stoner"]
        image = self.__get_image()
        enemy_methods.Enemy.__init__(self, pos, player, *groups, image = image, speed = 0, health = 1000, **kwargs)
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
        if random.randint(0,500) == 1 and self.smile_animation.finished  :
            self.smile_animation.reset()
        if not self.left_lift_animation.finished:
            self.left_lift_animation.update()
            if self.left_lift_animation.changed_image:
                self.left_arm = self.left_lift_animation.image[0]
                self.an_image_changed = True
        if self.left_lift_animation.finished:
            self.left_lift_animation.reset()

    def __get_image(self):
        #make sure no pointers
        image = pygame.Surface((round(self.orig_base_image.get_rect().width +  1.3 * self.left_arm.get_rect().width),
                                self.orig_base_image.get_rect().height))
        image.fill((255,255,255))
        ir = image.get_rect()
        image.blit(self.left_arm, (ir.left, ir.centery - 0.1 * ir.height))
        image.blit(self.right_arm, (ir.right - self.right_arm.get_rect().width, ir.centery - 0.1 * ir.height))
        image.blit(self.orig_base_image, (int(0.65 * self.left_arm.get_rect().width),0))
        image.blit(self.mouth, (ir.centerx - 0.5 * self.mouth.get_rect().width, ir.centery - 0.5 * self.mouth.get_rect().height))
        image.blit(self.left_eye, (ir.centerx - self.left_eye.get_rect().width, ir.centery - 0.70 * ir.centery))
        image.blit(self.right_eye, (ir.centerx, ir.centery - 0.70 * ir.centery))
        image.set_colorkey((255,255,255), RLEACCEL)
        image = image.convert_alpha()
        return image