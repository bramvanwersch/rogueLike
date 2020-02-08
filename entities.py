import pygame, random
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

class LivingEntity(Entity):
    def __init__(self, image, pos, *groups, health = [100,100], damage = 10, health_regen = 1):
        """
        Collection of methods for enemies and player alike
        """
        Entity.__init__(self, image, pos, *groups)
        self.speed = 10
        self.speedx, self.speedy = 0,0
        self.health = health
        self.damage = damage
        #second regen
        self.health_regen = health_regen
        self.facing_right = True
        self._layer = utilities.TOP_LAYER
        self.text_values = []
        self.dead = False
        self.immune = [False,0]

    def update(self, *args):
        super().update(*args)
        if self.dead:
            return
        elif self.health[0] <= 0:
            self.image = pygame.transform.rotate(self.image, 90)
            self.dead = True
            return
        if (self.facing_right and self.speedx < 0) or (not self.facing_right and self.speedx > 0):
            self.flip_image()
        self.move()
        if self.health[0] < self.health[1]:
            self._change_health((utilities.GAME_TIME.get_time() / 1000) * self.health_regen)
        for val in self.text_values:
            if val.destroy:
                super().groups().remove(val)
        if self.immune[0] and self.immune[1] <= 0:
            self.immune[0] = False
        if self.immune[0]:
            self.immune[1] -= 1

    def _change_health(self, amnt):
        self.health[0] += amnt
        if self.health[0] > self.health[1]:
            self.health[0] = self.health[1]

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
        xcol, ycol = self._check_collision()
        if not xcol:
            self.rect.x += self.speedx
        if not ycol:
            self.rect.y += self.speedy

    def _check_collision(self):
        """
        Check the collision of x and y simoultaniously and return if x and y have collision
        :return:
        """
        xcol, ycol = False, False
        #check for x and y collison as long as any of the two are false.
        while (not xcol or not ycol):
            if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
                xcol = True
            if (self.rect.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
                ycol = True
            x_rect = self.bounding_box.move((self.speedx, 0))
            y_rect = self.bounding_box.move((0, self.speedy))
            for sprite in super().groups()[0]:
                if sprite.bounding_box.colliderect(x_rect) and sprite.collision:
                    xcol = True
                if sprite.bounding_box.colliderect(y_rect) and sprite.collision:
                    ycol = True
            break;
        return [xcol, ycol]

    def create_text(self, text, **kwargs):
        """
        Create text above the enitiy often signifying damage or similar effects
        :param text: the text to be displayed
        :param **kwargs: can contain a color to make the text
        """
        self.text_values.append(TextSprite(text, self.rect.midtop, super().groups()[0], **kwargs))

class Player(LivingEntity):
    def __init__(self, pos, *groups):

        LivingEntity.__init__(self, utilities.load_image("player.bmp", (255, 255, 255)), pos)
        self.events = []

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

class Enemy(LivingEntity):
    def __init__(self,image, pos, player, *groups):
        LivingEntity.__init__(self, image, pos, *groups)
        self.player = player

    def update(self,*args):
        """
        Basic movement towards the player.
        """
        super().update(*args)
        playercenter = self.player.rect.center
        if self.player.rect.right < self.bounding_box.left:
            self.speedx = - self.speed
        elif self.player.rect.left > self.bounding_box.right:
            self.speedx = self.speed
        else:
            self.speedx = 0
        if self.player.rect.bottom < self.bounding_box.top:
            self.speedy = - self.speed
        elif self.player.rect.top > self.bounding_box.bottom:
            self.speedy = self.speed
        else:
            self.speedy = 0
        self._check_player_hit()

    def _check_player_hit(self):
        if self.bounding_box.colliderect(self.player.bounding_box) and not self.player.immune[0]:
            self.player.create_text(- self.damage, color = "red")
            self.player.set_immune()
            self.player._change_health(- self.damage)

class RedSquare(Enemy):
    def __init__(self, pos, player, *groups):
        Enemy.__init__(self, utilities.load_image("red_square_enemy.bmp"), pos, player, *groups)
        self.speed = 5

class BadBat(Enemy):
    def __init__(self, pos, player, *groups):
        self.animation = utilities.Animation("bad_bat-1.bmp","bad_bat0.bmp","bad_bat1.bmp","bad_bat2.bmp","bad_bat3.bmp","bad_bat4.bmp")
        Enemy.__init__(self, self.animation.image, pos, player, *groups)
        self.speed = 4

    def update(self, *args):
        super().update(*args)
        self.animation.update()
        self.image = self.animation.image
        if (self.facing_right):
            self.flip_image()

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the bat for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        return self.rect.inflate((-self.rect.width * 0.8, - self.rect.height * 0.2))

    def _check_collision(self):
        """
        Check the collision of x and y simoultaniously and return if x and y have collision
        :return:
        """
        xcol, ycol = False, False
        #check for x and y collison as long as any of the two are false.
        while (not xcol or not ycol):
            if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
                xcol = True
            if (self.rect.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
                ycol = True
            x_rect = self.bounding_box.move((self.speedx, 0))
            y_rect = self.bounding_box.move((0, self.speedy))
            for sprite in super().groups()[1]:
                if sprite.bounding_box.colliderect(x_rect) and self != sprite:
                    xcol = True
                if sprite.bounding_box.colliderect(y_rect) and self != sprite:
                    ycol = True
            break;
        return [xcol, ycol]

class TextSprite(Entity):
    def __init__(self,text, pos, *groups, **kwargs):
        image = pygame.font.Font(None, 30).render(str(text), True, pygame.Color(kwargs["color"]))
        Entity.__init__(self, image, pos, *groups)
        #current, maximum in ms
        self.lifespan = [0,2000]
        self.destroy = False
        self._layer = utilities.TEXT_LAYER

    def update(self,*args):
        super().update(*args)
        self.lifespan[0] += utilities.GAME_TIME.get_time()
        if self.lifespan[0] >= self.lifespan[1]:
            self.kill()
        self.rect.y -= 5
