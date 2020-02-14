import pygame, random, math
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
        self.orig_image = self.image
        self.rect = self.image.get_rect(topleft = pos)
        # if the sprite should be visible at the current moment. and if it should be able to be unloaded
        self.visible = [True, True]
        # if an entity has collision or if the player can just move trough it.
        self.collision = False
        self.bounding_box = self._get_bounding_box()
        self.flipped = False

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

    def _change_image(self, image):
        if self.flipped:
            self.image = image[1]
        else:
            self.image = image[0]

class InteractingEntity(Entity):
    """
    Changes collision field so entity becomes solid and the player or other entitities cannot move trought it
    """
    def __init__(self, image, pos, player, *groups):
        Entity.__init__(self, image, pos, *groups)
        self.player = player

    def update(self, *args):
        super().update(*args)
        if self.visible[0] and self.player.interacting:
            if self.rect.colliderect(self.player.rect):
                self.interact()

    #implemented by inheriting methods
    def interact(self):
        pass

class LivingEntity(Entity):
    def __init__(self, image, pos, *groups, health = 100, damage = 10, health_regen = 1, speed = 10, tiles = []):
        """
        Collection of methods for enemies and player alike
        """
        Entity.__init__(self, image, pos, *groups)
        self.max_speed = speed
        self.speedx, self.speedy = 0,0
        self.health = [health, health]
        self.damage = 10
        #second regen
        self.health_regen = health_regen
        self._layer = utilities.PLAYER_LAYER1
        self.text_values = []
        self.dead = False
        self.immune = [False,0]
        self.flipped_image = pygame.transform.flip(self.image, True, False)
        self.damage_color = "red"
        self.healing_color = "green"
        self.tiles = tiles

    def update(self, *args):
        super().update(*args)
        if self.dead and hasattr(self,"dead_animation"):
            if self.dead_animation.cycles == 0:
                self.die()
            else:
                self.kill()
            return
        elif self.dead:
            self.kill()
            return
        self.move()
        self.do_flip()
        # regen health
        if self.health[0] < self.health[1]:
            self._change_health((utilities.GAME_TIME.get_time() / 1000) * self.health_regen)
        #regulate i frames
        if self.immune[0] and self.immune[1] <= 0:
            self.immune[0] = False
        if self.immune[0]:
            self.immune[1] -= 1

    def set_immune(self, time = 10):
        """
        Makes a LivingEntity immune to damage for a set amount of frames
        :param time: the default frames to be immune. Expected to be an integer
        """
        self.immune = [True, time]

    def do_flip(self):
        if (self.flipped and self.speedx > 0) or (not self.flipped and self.speedx < 0):
            self.flipped = not self.flipped
            if self.flipped:
                self.image = self.flipped_image
            else:
                self.image = self.orig_image

    def _change_health(self, amnt):
        """
        changes the health of the entity by a positive or negative value. Cannot heal over max and is declared dead if
        hp is at or below 0
        :param amnt: of health to change to.
        """
        self.health[0] += amnt
        if amnt < 0:
            self.create_text(str(amnt), color = self.damage_color)
        if self.health[0] > self.health[1]:
            self.health[0] = self.health[1]
        if self.health[0] <= 0:
            self.dead = True

    def move(self):
        """
        moves the character at walking speed (normal speed) when the new location is not outside the defined bounds. Also
        checks if the current speed is an acceptable one and if to high resets it to the max_speed.
        """
        if self.speedx > self.max_speed:
            self.speedx = self.max_speed
        elif self.speedx < - self.max_speed:
            self.speedx = -self.max_speed
        if self.speedy > self.max_speed:
            self.speedy = self.max_speed
        elif self.speedy < - self.max_speed:
            self.speedy = -self.max_speed
        xcol, ycol = self._check_collision()

        if not xcol:
            self.rect.x += self.speedx
        if not ycol:
            self.rect.y += self.speedy

    def _check_collision(self):
        """
        Check the collision of x and y simoultaniously and return if x or y have collision
        :return: a list of 2 booleans for [xcol, ycol]
        """
        xcol, ycol = False, False
        #check for x and y collison as long as any of the two are false.
        while (not xcol or not ycol):
            if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > utilities.DEFAULT_LEVEL_SIZE.right):
                xcol = True
            if (self.bounding_box.top + self.speedy < 0 or self.rect.bottom + self.speedy > utilities.DEFAULT_LEVEL_SIZE.bottom):
                ycol = True
            if self.speedx > 0:
                x_rect = self.bounding_box.move((self.speedx + 1, 0))
            else:
                x_rect = self.bounding_box.move((self.speedx - 1, 0))
            if self.speedy > 0:
                y_rect = self.bounding_box.move((0, self.speedy + 1))
            else:
                y_rect = self.bounding_box.move((0, self.speedy - 1))
            if self.tiles.solid_collide(x_rect):
                xcol = True
            if self.tiles.solid_collide(y_rect):
                ycol = True
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
        :param **kwargs: can contain a color to color the text
        """
        self.text_values.append(TextSprite(text, self.rect.midtop, super().groups()[0], **kwargs))

class Enemy(LivingEntity):
    def __init__(self,image, pos, player, *groups, **kwargs):
        LivingEntity.__init__(self, image, pos, *groups, **kwargs)
        self.player = player
        self.damage_color = "blue"

    def update(self,*args):
        """
        Basic movement towards the player.
        """
        super().update(*args)
        self._use_brain()
        self._check_player_hit()
        self._check_self_hit()

    def _use_brain(self):
        if self.player.bounding_box.right < self.bounding_box.left:
            self.speedx -= 0.1 * self.max_speed
        elif self.player.bounding_box.left > self.bounding_box.right:
            self.speedx += 0.1 * self.max_speed
        else:
            self.speedx *= 0.9
        if self.player.bounding_box.bottom < self.bounding_box.top:
            self.speedy -= 0.1 * self.max_speed
        elif self.player.bounding_box.top > self.bounding_box.bottom:
            self.speedy += 0.1 * self.max_speed
        else:
            self.speedy *= 0.9

    def _check_player_hit(self):
        if self.player.bounding_box.colliderect(self.bounding_box) and not self.player.immune[0]:
            self.player.set_immune()
            self.player._change_health(- self.damage)

    def _check_self_hit(self):
        if self.player.right_arm.attacking and self.rect.colliderect(self.player.right_arm.bounding_box) and not self.immune[0]:
            self.set_immune()
            self._change_health(- self.damage)

class RedSquare(Enemy):
    def __init__(self, pos, player, tiles, *groups):
        Enemy.__init__(self, utilities.load_image("red_square_enemy.bmp"), pos, player, *groups, speed = 5, tiles = tiles)

class BadBat(Enemy):
    def __init__(self, pos, player,tiles, *groups):
        self.animation = utilities.Animation("bad_bat-1.bmp","bad_bat0.bmp","bad_bat1.bmp","bad_bat2.bmp","bad_bat3.bmp",
                                             "bad_bat4.bmp", scale = (100,50), start_frame="random")
        Enemy.__init__(self, self.animation.image[0], pos, player, *groups, speed = 4,tiles = tiles)

    def update(self, *args):
        super().update(*args)
        self.animation.update()
        self._change_image(self.animation.image)

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
            if self.speedx > 0:
                x_rect = self.bounding_box.move((self.speedx + 1, 0))
            else:
                x_rect = self.bounding_box.move((self.speedx - 1, 0))
            if self.speedy > 0:
                y_rect = self.bounding_box.move((0, self.speedy + 1))
            else:
                y_rect = self.bounding_box.move((0, self.speedy - 1))
            for sprite in super().groups()[1]:
                if sprite.bounding_box.colliderect(x_rect) and self != sprite:
                    xcol = True
                if sprite.bounding_box.colliderect(y_rect) and self != sprite:
                    ycol = True
            break;
        return [xcol, ycol]

class TestDummy(Enemy):
    def __init__(self, pos, player,tiles, *groups):
        image = pygame.transform.scale(utilities.load_image("dummy.bmp", (255,255,255)),(50,100))
        Enemy.__init__(self,image , pos, player, *groups,health=2000,health_regen=1000, speed = 0,tiles = tiles)

class TextSprite(Entity):
    def __init__(self,text, pos, *groups, **kwargs):
        image = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20).render(str(text), True, pygame.Color(kwargs["color"]))
        Entity.__init__(self, image, pos, *groups)
        #current, maximum in ms
        self.lifespan = [0,1000]
        self.destroy = False
        self._layer = utilities.TEXT_LAYER

    def update(self,*args):
        super().update(*args)
        self.lifespan[0] += utilities.GAME_TIME.get_time()
        if self.lifespan[0] >= self.lifespan[1]:
            self.kill()
        self.rect.y -= 2
