import pygame
from pygame.locals import *
import utilities

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.visible = True

class Player(Entity):
    def __init__(self, pos, *groups):
        Entity.__init__(self, utilities.load_image("player.bmp",(255,255,255 )), pos)
        self.speedx, self.speedy = 0,0
        self.speed = 10
        self.events = []
        self._layer = utilities.TOP_LAYER

    def update(self):
        """
        Processes user input to make the player do actions.
        :return:
        """
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
        self.__walk()

    def __walk(self):
        """
        moves the character at walking speed (normal speed) when the new location is not outside the defined bounds
        """
        if not (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
            self.rect.x += self.speedx
        if not (self.rect.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
            self.rect.y += self.speedy


    def center_coordinate(self):
        #TODO test this method
        return self.rect.center


