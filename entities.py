import pygame
from pygame.locals import *
import utilities

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        #bounds where the entity can move, default is the screen size.
    #     self.bounds = self.__make_bounds(bounds)
    #
    # def __make_bounds(self, bounds):
    #     if bounds == "default":
    #         screen = pygame.display.get_surface()
    #         return screen.get_rect()
    #     else:
    #         return pygame.rect.Rect(*bounds)


class Player(Entity):
    def __init__(self, pos, *groups):
        Entity.__init__(self, utilities.load_image("player.bmp",(255,255,255 )), pos)
        self.speedx, self.speedy = 0,0
        self.speed = 10
        self.events = []

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
        oldpos = self.rect.copy()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def center_coordinate(self):
        #TODO test this method
        return self.rect.center


