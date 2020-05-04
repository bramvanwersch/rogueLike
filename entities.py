import pygame, random

import constants
from game_images import animations


class Entity(pygame.sprite.Sprite):
    _PPS = constants.PPS_BASE
    #size of the image in the sprite sheet
    image_size = (100,100)
    def __init__(self, pos, *groups, visible = [True,True], center = False, **kwargs):
        """
        Class for all entities, these are all images that need to move or change
        :param pos: the topleft corner of the rectangle of the image
        :param groups: a sprite group the sprite belongs to.
        """
        pygame.sprite.Sprite.__init__(self, *groups)
        if "image" in kwargs and isinstance(kwargs["image"], pygame.Surface):
            self.image = kwargs["image"]
        elif "size" in kwargs:
            self.image = pygame.Surface(kwargs["size"]).convert()
            self.image.fill((255, 0, 179))
        else:
            self.image = pygame.Surface(self.image_size).convert()
            self.image.fill((255, 0, 179))
        # if the sprite should be visible at the current moment. and if it should be able to be unloaded
        self.visible = visible
        self.orig_image = self.image
        if center   :
            self.rect = self.image.get_rect(center=pos)
        else:
            self.rect = self.image.get_rect(topleft = pos)
        # if an entity has collision or if the player can just move trough it.
        self.collision = False
        if "collision" in kwargs:
            self.collision = kwargs["collision"]
        self.bounding_box = self._get_bounding_box()
        self.flipped = False
        #variable that can be flipped to kill the entity to make sure the entity dies before executing
        self.dead = False
        #varaible that tracks if the previous
        self.message_cooldown = 60
        #need to track this to make sure that movement is float accurate

    def update(self, *args):
        """
        updates the bounding box of every entity every frame
        :return:
        """
        super().update(*args)
        if self.dead:
            self._die()
            return
        self.bounding_box = self._get_bounding_box()

    def _die(self):
        self.kill()

    def _get_bounding_box(self):
        """
        Every entity has a bounding box the default is the current rectangle of the sprite.
        """
        return self.rect

    def change_image(self, image):
        if self.flipped:
            self.image = image[1]
        else:
            self.image = image[0]
        imr = self.image.get_rect()
        self.rect = pygame.Rect((*self.rect.topleft, imr.width, imr.height))

    def run_animation(self):
        self.animation.update()
        self.change_image(self.animation.image)

    def attributes(self):
        """
        List of attributes that can be changed trought the console at runtime. At least a list that makes sense
        """
        return ['visible', 'bounding_box','dead']

    def __str__(self):
        return "{}_at_{}-{}".format(type(self).__name__, self.rect.centerx, self.rect.centery)

    @constants.classproperty
    def SIZE(self):
        return (self._PPS * self.image_size[0], self._PPS * self.image_size[1])

    @property
    def PPS(self):
        return self._PPS

    @PPS.setter
    def PPS(self, pps):
        self._PPS = pps
        for animation in animations:
            if self.__name__ in animation:
                animations[animation].scale((round(pps * self.image_size[0]), round(pps * self.image_size[1])))

class InteractingEntity(Entity):
    def __init__(self, pos, player, *groups, action = None, interactable = True, trigger_cooldown = [0,0], animation = None, **kwargs):
        """
        Entity that preforms an action when a player is pressing the interaction key and colliding with the entity
        """
        Entity.__init__(self, pos, *groups, **kwargs)
        self.player = player
        #can be set to a function to give functionality to the entity
        self.interactable = interactable
        self.action_function = action
        #list of lenght 2 first being current cooldown second being the reset cooldown
        self.trigger_cooldown = trigger_cooldown
        self.animation = animation

    def update(self, *args):
        super().update(*args)
        if self.dead:
            return
        if self.action_function and self.interactable and self.player.pressed_keys[constants.INTERACT] and \
                self.trigger_cooldown[0] <= 0:
            if self.rect.colliderect(self.player.rect):
                if self.animation and self.animation.finished:
                    self.action_function()
                    self.trigger_cooldown[0] = self.trigger_cooldown[1]
                else:
                    self.action_function()
                    self.trigger_cooldown[0] = self.trigger_cooldown[1]
        elif not self.interactable and self.player.pressed_keys[constants.INTERACT] and self.message_cooldown <= 0:
            if self.rect.colliderect(self.player.rect):
                TextSprite("KILL ALL!", self.player.rect.topleft, super().groups()[0], color= "orange")
                self.message_cooldown = 60
        if self.message_cooldown > 0:
            self.message_cooldown -= 1
        if self.trigger_cooldown[0] > 0:
            self.trigger_cooldown[0] -= 1
        #run animation when the object becomes interactable
        if self.animation:
            if self.interactable and not self.animation.finished:
                self.run_animation()

class LivingEntity(Entity):
    DAMAGE_COLOR = "red"
    HEALING_COLOR = "green"
    HEALTH = 100
    DAMAGE = 10
    HEALTH_REGEN = 1
    SPEED = 10
    XP = 100
    def __init__(self, pos, *groups, health = HEALTH, damage = DAMAGE, health_regen = HEALTH_REGEN, speed = SPEED, tiles = [], xp = XP, **kwargs):
        """
        Collection of methods for enemies and player alike
        """
        Entity.__init__(self, pos, *groups, **kwargs)
        self.max_speed = speed
        self.speedx, self.speedy = 0,0
        self.health = [health, health]
        self.damage = damage
        #second regen
        self.xp = xp
        self.health_regen = health_regen
        self._layer = constants.PLAYER_LAYER1
        self.text_values = []
        self.immune = [False,0]
        self.flipped_image = pygame.transform.flip(self.image, True, False)
        self.tiles = tiles
        self.debug_color = random.choice(constants.DISTINCT_COLORS)
        self.damage_color = self.DAMAGE_COLOR
        self.healing_color = self.HEALING_COLOR
        self.damaged = False

    def update(self, *args):
        super().update(*args)
        if self.dead:
            return
        self.move()
        self.do_flip()
        # regen health
        if self.health[0] < self.health[1]:
            self.change_health((constants.GAME_TIME.get_time() / 1000) * self.health_regen)
        #regulate i frames
        if self.immune[0] and self.immune[1] <= 0:
            self.immune[0] = False
        if self.immune[0]:
            self.immune[1] -= 1

    def _dead_sequence(self):
        if self.dead and hasattr(self,"dead_animation"):
            if self.dead_animation.cycles > 0:
                self.kill()
        elif self.dead and hasattr(self, "dead_timer"):
            self.dead_timer -= 1
            if self.dead_timer <= 0:
                self.kill()
        else:
            self.kill()

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

    def change_health(self, amnt):
        """
        changes the health of the entity by a positive or negative value. Cannot heal over max and is declared dead if
        hp is at or below 0
        :param amnt: of health to change to.
        """
        self.health[0] += amnt
        if amnt < 0:
            self.damaged = True
        if amnt < 0:
            self.create_text(str(amnt), color = self.damage_color)
        if self.health[0] > self.health[1]:
            self.health[0] = self.health[1]
        if self.health[0] <= 0:
            self.dead = True

    def move(self):
        if self.speedx > self.max_speed:
            self.speedx = self.max_speed
        elif self.speedx < - self.max_speed:
            self.speedx = -self.max_speed
        if self.speedy > self.max_speed:
            self.speedy = self.max_speed
        elif self.speedy < - self.max_speed:
            self.speedy = -self.max_speed
        xcol, ycol = self._check_collision(height = False)

        if not xcol:
            self.rect.centerx += self.speedx
        if not ycol:
            self.rect.centery += self.speedy

    def _check_collision(self, height = True, sprites = True):
        """
        Check the collision of x and y simoultaniously and return if x or y have collision
        :param height boolean telling if the height of tiles should be taken into account.
        :param sprites boolean telling if sprites should be checked for collision
        :return: a list of 2 booleans for [xcol, ycol]
        """
        xcol, ycol = False, False
        #check for x and y collison as long as any of the two are false.
        while (not xcol or not ycol):
            if (self.bounding_box.left + self.speedx < 0 or self.bounding_box.right + self.speedx > self.tiles.size[0] * constants.TILE_SIZE[0]):
                xcol = True
            if (self.bounding_box.top + self.speedy < 0 or self.bounding_box.bottom + self.speedy > self.tiles.size[1] * constants.TILE_SIZE[1]):
                ycol = True
            if self.speedx > 0:
                x_rect = self.bounding_box.move((self.speedx + 1, 0))
            else:
                x_rect = self.bounding_box.move((self.speedx - 1, 0))
            if self.speedy > 0:
                y_rect = self.bounding_box.move((0, self.speedy + 1))
            else:
                y_rect = self.bounding_box.move((0, self.speedy - 1))
            if self.tiles.solid_collide(x_rect, height):
                xcol = True
            if self.tiles.solid_collide(y_rect, height):
                ycol = True
            if sprites:
                for sprite in super().groups()[0]:
                    if sprite.collision and sprite != self and sprite.bounding_box.colliderect(x_rect):
                        xcol = True
                    if sprite.collision and sprite != self and sprite.bounding_box.colliderect(y_rect):
                        ycol = True
            break;
        return [xcol, ycol]

    def create_text(self, text, color):
        """
        Create current_line above the enitiy often signifying damage or similar effects
        :param text: the current_line to be displayed
        """
        self.text_values.append(TextSprite(text, self.rect.midtop, super().groups()[0], color = color))

    def _die(self):
        self._dead_sequence()

    def attributes(self):
        ats = super().attributes()
        return ats + ['max_speed', 'health','health_regen','immune','damage','xp']

class TextSprite(Entity):
    COLOR = "black"
    def __init__(self, text, pos, *groups, color = COLOR, **kwargs):
        image = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 20).render(str(text), True, pygame.Color(color))
        #give a bit of random offset
        pos = (random.randint(pos[0] -5, pos[0] + 5), random.randint(pos[1] -5, pos[1] + 5))
        Entity.__init__(self, pos, *groups, image = image)
        #current, maximum in ms
        self.lifespan = [0,1000]
        self.destroy = False
        self._layer = constants.TEXT_LAYER

    def update(self,*args):
        super().update(*args)
        self.lifespan[0] += constants.GAME_TIME.get_time()
        if self.lifespan[0] >= self.lifespan[1]:
            self.kill()
        self.rect.y -= 2
