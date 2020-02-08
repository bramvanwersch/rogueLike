import pygame
from pygame.locals import *
import entities, utilities
from entities import LivingEntity

class Player(LivingEntity):
    def __init__(self, pos, *groups):
        self.idle_image = pygame.transform.scale(utilities.load_image("player.bmp", (255, 255, 255)), (60,120))
        LivingEntity.__init__(self, self.idle_image, pos)
        self.walking_animation = utilities.Animation("player_walk0.bmp","player_walk1.bmp","player_walk2.bmp","player_walk1.bmp",
                                                     "player_walk0.bmp","player_walk3.bmp","player_walk4.bmp","player_walk3.bmp",
                                                     scale = (60,120))
        self.events = []
        self.inventory = Inventory()

    def set_immune(self, time = 10):
        """
        Makes a LivingEntity immune to damage for a set amount of frames
        :param time: the default frames to be immune. Expected to be an integer
        """
        self.immune = [True, time]

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the player for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        bb = self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.2))
        bb.center = (bb.centerx, bb.centery + bb.top - self.rect.top)
        return bb

    def update(self, *args):
        """
        Processes user input to make the player do actions.
        """
        super().update(*args)
        for event in self.events:
            if event.type == KEYDOWN:
                if event.key == K_a or event.key == K_LEFT:
                    self.speedx -= self.speed
                if event.key == K_d or event.key == K_RIGHT:
                    self.speedx += self.speed
                if event.key == K_w or event.key == K_UP:
                    self.speedy -= self.speed
                if event.key == K_s or event.key == K_DOWN:
                    self.speedy += self.speed

            elif event.type == KEYUP:
                if event.key == K_a or event.key == K_LEFT:
                    self.speedx +=  self.speed
                if event.key == K_d or event.key == K_RIGHT:
                    self.speedx -= self.speed
                if event.key == K_w or event.key == K_UP:
                    self.speedy += self.speed
                if event.key == K_s or event.key == K_DOWN:
                    self.speedy -= self.speed
        if self.speedx != 0 or self.speedy != 0:
            self.image = self.walking_animation.image
            # if (self.facing_right):
            #     self.flip_image()
            self.walking_animation.update()
        else:
            self.image = self.idle_image

class Inventory:
    def __init__(self):
        pass