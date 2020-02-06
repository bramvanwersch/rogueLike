import pygame
from pygame.locals import *
import utilities

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.visible = True
        self.collision = False

    @property
    def bounding_box(self):
        return self.rect

class SolidEntity(Entity):
    """
    Adds field so all entities become solid when inheriting from this class
    """
    def __init__(self, image, pos, *groups):
        Entity.__init__(self, image, pos, *groups)
        self.collision = True

class Player(Entity):
    def __init__(self, pos, *groups):
        Entity.__init__(self, utilities.load_image("player.bmp",(255,255,255 )), pos)
        self.speedx, self.speedy = 0,0
        self.speed = 10
        self.events = []
        #overwrite the rect that is normaly calculated to make it a little smaller
        self._layer = utilities.TOP_LAYER

    @property
    def bounding_box(self):
        bb = self.rect.inflate((-self.rect.width * 0.8, - self.rect.height * 0.5))
        bb.center = (bb.centerx, bb.centery + bb.top - self.rect.top)
        return bb

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
        #get sprites overlapping with bottom
        # overlapping_sprites = super().groups()[0].get_sprites_at(self.__bottem_center_coord())
        # for sprite in overlapping_sprites:
        #     if sprite.collision:
        #         return
        if not self.__x_collison():
            self.rect.x += self.speedx
        if not self.__y_collison():
            self.rect.y += self.speedy

    def __x_collison(self):
        if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
            return True
        x_rect = self.bounding_box.move((self.speedx, 0))
        overlapping_sprites = [sprite for sprite in super().groups()[0].sprites() if sprite.visible and sprite.bounding_box.colliderect(x_rect)]
        for sprite in overlapping_sprites:
            if sprite.collision:
                return True
        return False

    def __y_collison(self):
        if (self.rect.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
            return True
        y_rect = self.bounding_box.move((0, self.speedy))
        overlapping_sprites = [sprite for sprite in super().groups()[0].sprites() if sprite.bounding_box.colliderect(y_rect)]
        for sprite in overlapping_sprites:
            if sprite.collision:
                return True
        return False

    def __bottem_center_coord(self):
        """
        Gives the coordinate of the center of the bottom of the rectangle of the sprite. Where the current entity is
        moving towards.
        :return: a position in form (x,y)
        """
        return (self.rect.center[0] + self.speedx, self.rect.center[1] + self.speedy)


