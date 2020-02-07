import pygame
from pygame.locals import *
import utilities

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        """
        Class for all entities, these are all images that need to move or change
        :param image: The image of the sprite
        :param pos: the topleft corner of the rectangle of the image
        :param groups: a sprite group the sprite belongs to.
        """
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        # if the sprite should be visible at the current moment.
        self.visible = True
        # if an entity has collision or if the player can just move trough it.
        self.collision = False
        self.bounding_box = self._get_bounding_box()

    def update(self, *args):
        """
        updates the bounding box of every entity every frame
        :return:
        """
        super().update(*args)
        self.bounding_box = self._get_bounding_box()

    def _get_bounding_box(self):
        """
        Every entity has a bounding box the default is the current rectangle of the sprite.
        """
        return self.rect

class SolidEntity(Entity):
    """
    Changes collision field so entity becomes solid and the player or other entitities cannot move trought it
    """
    def __init__(self, image, pos, *groups):
        Entity.__init__(self, image, pos, *groups)
        self.collision = True

class MovingEntity(Entity):
    def __init__(self, image, pos, *groups):
        """
        Collection of methods for enemies and player alike
        """
        Entity.__init__(self, image, pos, *groups)
        self.speed = 10
        self.speedx, self.speedy = 0,0
        self.events = []
        self.facing_right = True
        self._layer = utilities.TOP_LAYER

    def update(self, *args):
        super().update(*args)
        if (self.facing_right and self.speedx < 0) or (not self.facing_right and self.speedx > 0):
            self.flip_image()
        self.move()

    def flip_image(self):
        """
        Flips the self.image along the x axis, can be used to make a entity face the other way.
        """
        self.image = pygame.transform.flip(self.image, True, False)
        self.facing_right = not self.facing_right

    def move(self):
        """
        moves the character at walking speed (normal speed) when the new location is not outside the defined bounds
        """
        if not self._x_collison():
            self.rect.x += self.speedx
        if not self._y_collison():
            self.rect.y += self.speedy

    def _x_collison(self):
        """
        Checks if an entity will collide with the border of the map or another entity for the x direction
        :return: a boolean telling if the entity will collide or not
        """
        if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
            return True
        x_rect = self.bounding_box.move((self.speedx, 0))
        overlapping_sprites = [sprite for sprite in Entity.groups(self)[0].sprites() if sprite.visible and sprite.bounding_box.colliderect(x_rect)]
        for sprite in overlapping_sprites:
            if sprite.collision:
                return True
        return False

    def _y_collison(self):
        """
        Checks if an entity will collide with the border of the map or another entity for the y direction
        :return: a boolean telling if the entity will collide or not
        """
        if (self.rect.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
            return True
        y_rect = self.bounding_box.move((0, self.speedy))
        overlapping_sprites = [sprite for sprite in super().groups()[0].sprites() if sprite.bounding_box.colliderect(y_rect)]
        for sprite in overlapping_sprites:
            if sprite.collision:
                return True
        return False

class Player(MovingEntity):
    def __init__(self, pos, *groups):
        MovingEntity.__init__(self, utilities.load_image("player.bmp",(255,255,255 )), pos)

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

class Enemy(MovingEntity):
    def __init__(self,image, pos, player, *groups):
        MovingEntity.__init__(self, image, pos, *groups)
        self.player = player

    def update(self,*args):
        """
        Basic movement towards the player.
        """
        super().update(*args)
        playercenter = self.player.rect.center
        if self.player.rect.right < self.rect.left:
            self.speedx = - self.speed
        elif self.player.rect.left > self.rect.right:
            self.speedx = self.speed
        else:
            self.speedx = 0
        if self.player.rect.bottom < self.rect.top:
            self.speedy = - self.speed
        elif self.player.rect.top > self.rect.bottom:
            self.speedy = self.speed
        else:
            self.speedy = 0

class RedSquare(Enemy):
    def __init__(self, pos, player, *groups):
        Enemy.__init__(self, utilities.load_image("red_square_enemy.bmp"), pos, player, *groups)
        self.speed = 5

class BadBat(Enemy):
    def __init__(self, pos, player, *groups):
        self.animation = Animation("bad_bat-1.bmp","bad_bat0.bmp","bad_bat1.bmp","bad_bat2.bmp","bad_bat3.bmp","bad_bat4.bmp")
        Enemy.__init__(self, self.animation.image, pos, player, *groups)
        self.speed = 4

    def update(self, *args):
        super().update(*args)
        self.animation.update()
        self.image = self.animation.image
        if (self.facing_right):
            self.flip_image()

    def _x_collison(self):
        """
        checks for out of bounds of the map only
        """
        if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
            return True
        return False

    def _y_collison(self):
        """
        checks for out of bounds of the map only
        """
        if (self.rect.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
            return True
        return False

class Animation:
    def __init__(self, speed = 10, *image_names):
        halfanimation = [pygame.transform.scale(utilities.load_image(name, (255,255,255)), (100,50)) for name in image_names]
        self.animation_images = halfanimation + halfanimation[1:-1:-1]
        self.frame_count = 0
        self.current_frame = 0
        self.image = self.animation_images[0]

    def update(self):
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            self.image = self.animation_images[self.current_frame]
            self.current_frame += 1
        if self.current_frame >= len(self.animation_images):
            self.current_frame = 0
            self.frame_count = 0