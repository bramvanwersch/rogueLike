import pygame, random, math
import utilities, constants
from game_images import sheets

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, *groups, **kwargs):
        """
        Class for all entities, these are all images that need to move or change
        :param image: The image of the sprite
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
            self.image = pygame.Surface((100,100)).convert()
            self.image.fill((255, 0, 179))
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
    def __init__(self, pos, player, *groups, **kwargs):
        Entity.__init__(self, pos, *groups, **kwargs)
        self.player = player

    def update(self, *args):
        super().update(*args)
        if self.visible[0] and self.player.pressed_keys[constants.INTERACT]:
            if self.rect.colliderect(self.player.rect):
                self.interact()

    #implemented by inheriting methods
    def interact(self):
        pass

class LivingEntity(Entity):
    def __init__(self, pos, *groups, health = 100, damage = 10, health_regen = 1, speed = 10, tiles = [], xp = 100, **kwargs):
        """
        Collection of methods for enemies and player alike
        """
        Entity.__init__(self, pos, *groups, **kwargs)
        self.max_speed = speed
        self.speedx, self.speedy = 0,0
        self.health = [health, health]
        self.damage = 10
        #second regen
        self.xp = xp
        self.health_regen = health_regen
        self._layer = utilities.PLAYER_LAYER1
        self.text_values = []
        self.dead = False
        self.immune = [False,0]
        self.flipped_image = pygame.transform.flip(self.image, True, False)
        self.damage_color = "red"
        self.healing_color = "green"
        self.tiles = tiles
        self.debug_color = random.choice(constants.DISTINCT_COLORS)

    def update(self, *args):
        super().update(*args)
        if self.dead:
            self._dead_sequence()
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

    def _dead_sequence(self):
        if self.dead and hasattr(self,"dead_animation"):
            if self.dead_animation.cycles == 0:
                self.die()
            else:
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
            self._die()

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
            self.rect.x += self.speedx
        if not ycol:
            self.rect.y += self.speedy

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

    def create_text(self, text, **kwargs):
        """
        Create text above the enitiy often signifying damage or similar effects
        :param text: the text to be displayed
        :param **kwargs: can contain a color to color the text
        """
        self.text_values.append(TextSprite(text, self.rect.midtop, super().groups()[0], **kwargs))

    def _die(self):
        self.dead = True

class Enemy(LivingEntity):
    def __init__(self, pos, player, *groups, **kwargs):
        LivingEntity.__init__(self, pos, *groups, **kwargs)
        self.player = player
        self.damage_color = "blue"
        self.previous_acctack_cycle = 0

    def update(self,*args):
        super().update(*args)
        if not self.dead:
            self._use_brain()
            self._check_player_hit()
            self._check_self_hit()

    def _die(self):
        super()._die()
        self.player.xp[0] += self.xp

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
        if self.player.right_arm.attacking and self.rect.colliderect(self.player.right_arm.bounding_box) and\
                self.previous_acctack_cycle != self.player.right_arm.attack_cycle:
            self._change_health(- self.player.right_arm.damage)
            self.previous_acctack_cycle = self.player.right_arm.attack_cycle

class RedSquare(Enemy):
    def __init__(self, pos, player, tiles, *groups):
        image = sheets["enemies"].image_at((240,0), scale = (50,50))
        Enemy.__init__(self, pos, player, *groups, speed = 5, tiles = tiles, image = image)
        #make sure path is calculated at start of creation
        self.passed_frames = random.randint(0,60)
        self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
        self.move_tile = self.path.pop(-1)

    def _use_brain(self):
        #update every per second
        if self.passed_frames < 60 and self.path:
            self.passed_frames += 1
        else:
            solid_sprite_coords = [sprite.rect.center for sprite in super().groups()[0].sprites() if sprite.collision]
            self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box, solid_sprite_coords = solid_sprite_coords)
            self.passed_frames = 0
            self.move_tile = self.path.pop(-1)
        #if path is empty or there is no solution
        if not self.move_tile:
            return
        if self.move_tile.coord == [int(self.bounding_box.x / 100), int(self.bounding_box.y / 100)]:
            self.move_tile = self.path.pop(-1)
        if self.move_tile.centerx > self.bounding_box.centerx - self.max_speed and self.move_tile.centerx < self.bounding_box.centerx + self.max_speed :
            self.speedx = 0
        elif self.move_tile.centerx < self.bounding_box.centerx:
            self.speedx -= self.max_speed
        elif self.move_tile.centerx > self.bounding_box.centerx:
            self.speedx += self.max_speed
        if self.move_tile.centery < self.bounding_box.centery + self.max_speed and self.move_tile.centery > self.bounding_box.centery - self.max_speed:
            self.speedy = 0
        elif self.move_tile.centery < self.bounding_box.centery:
            self.speedy -= self.max_speed
        elif self.move_tile.centery > self.bounding_box.centery:
            self.speedy += self.max_speed

class BadBat(Enemy):
    def __init__(self, pos, player,tiles, *groups):
        animation_images = sheets["enemies"].images_at_rectangle((16,0,224,16), scale = (100,50), size = (32,16),
                                                                 color_key = (255,255,255))
        animation_sequence = animation_images + animation_images[::-1]
        self.animation = utilities.Animation(*animation_sequence, start_frame="random")
        Enemy.__init__(self, pos, player, *groups, speed = 4,tiles = tiles, image = self.animation.image[0])

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
    def __init__(self, pos, player, tiles, *groups):
        image = sheets["enemies"].image_at((0,48), scale = (50,100), size = (16,32), color_key = (255,255,255))
        Enemy.__init__(self, pos, player, *groups, health = 2000, health_regen = 1000, speed = 0, tiles = tiles, image = image)

class Archer(Enemy):
    def __init__(self, pos, player,tiles, *groups):
        image = sheets["enemies"].image_at((0,16), scale = (60,120), size = (16,32), color_key = (255,255,255))
        Enemy.__init__(self, pos, player, *groups, tiles = tiles, size = [50,80], speed = 4, image = image)
        self.shot_player_distance = 600
        #make sure path is calculated at start of creation
        self.passed_frames = random.randint(0,60)
        # self.shooting_animation = utilities.Animation()
        self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
        self.move_tile = self.path.pop(-1)
        self.shooting = False
        self.shooting_cooldown = 50
        self.collision = True
        self.vision_line = []

    def update(self, *args):
        super().update(*args)
        if self.shooting and self.shooting_cooldown <= 0:
            #update animation
            # self.shooting_animation.update()
            # if self.shooting_animation.cycles > 0:
            self.shooting = False
            LinearProjectile(self.rect.center, self.player, super().groups()[0], size = [50, 10], tiles = self.tiles, speed = 20)
            self.shooting_cooldown = 50
        elif self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1

    def _use_brain(self):
        #manhaten distance lower then 600 stand still and shoot and also check if there is a direct line of sight
        if utilities.VISION_LINE:
            self.vision_line = self.tiles.line_of_sight(self.bounding_box.center, self.player.bounding_box.center)[1]
        if abs(self.rect.x - self.player.rect.x) + abs(self.rect.y - self.player.rect.y) < self.shot_player_distance and\
            self.tiles.line_of_sight(self.bounding_box.center, self.player.bounding_box.center)[0]:
            self.speedy, self.speedx = 0,0
            self.shooting = True
            return
        if self.passed_frames < 60 and self.path:
            self.passed_frames += 1
        else:
            solid_sprite_coords = [sprite.rect.center for sprite in super().groups()[0].sprites() if sprite.collision]
            self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box, solid_sprite_coords = solid_sprite_coords)
            self.passed_frames = 0
            self.move_tile = self.path.pop(-1)
        #if path is empty or there is no solution
        if not self.move_tile:
            return
        if self.move_tile.coord == [int(self.bounding_box.x / 100), int(self.bounding_box.y / 100)]:
            self.move_tile = self.path.pop(-1)
        if self.move_tile.centerx > self.bounding_box.centerx - self.max_speed * 2\
                and self.move_tile.centerx < self.bounding_box.centerx + self.max_speed * 2:
            self.speedx = 0
        elif self.move_tile.centerx < self.bounding_box.centerx:
            self.speedx -= self.max_speed
        elif self.move_tile.centerx > self.bounding_box.centerx:
            self.speedx += self.max_speed
        if self.move_tile.centery < self.bounding_box.centery + self.max_speed * 2\
                and self.move_tile.centery > self.bounding_box.centery - self.max_speed * 2:
            self.speedy = 0
        elif self.move_tile.centery < self.bounding_box.centery:
            self.speedy -= self.max_speed
        elif self.move_tile.centery > self.bounding_box.centery:
            self.speedy += self.max_speed

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the player for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        bb = self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.4))
        return bb

class LinearProjectile(Enemy):
    def __init__(self, start_pos, player, *groups, p_type = "arrow", accuracy = 80, **kwargs):
        arrow = sheets["enemies"].image_at((0,0), scale =(50,25), color_key = (255,255,255))
        self.projectile_offset = pygame.Vector2(0,0)
        Enemy.__init__(self, start_pos, player, *groups, image = arrow, xp = 0, health = 10,**kwargs)
        self.accuracy = accuracy
        self.dest = list(self.player.bounding_box.center)
        self.rect.center = start_pos
        if self.dest < list(self.rect.topleft):
            self.max_speed = - self.max_speed
        self.__configure_trajectory()
        self.dead_timer = 60
        #make implementation of this

    def __configure_trajectory(self):
        # in the case of a linear relationship. is always the same but for now leave like this.
        #https://math.stackexchange.com/questions/656500/given-a-point-slope-and-a-distance-along-that-slope-easily-find-a-second-p
        # delta y / delta x
        inacuracy = 100 - self.accuracy
        if random.randint(1,2) == 1:
            self.dest[0] += random.randint(0, inacuracy)
            self.dest[1] += random.randint(0, inacuracy)
        else:
            self.dest[0] -= random.randint(0, inacuracy)
            self.dest[1] -= random.randint(0, inacuracy)
        try:
            a = (self.dest[1] - self.rect.y) / (self.dest[0] - self.rect.x)
        except ZeroDivisionError:
            a = 0
        self.speedx = self.max_speed * 1 / math.sqrt(1 + a**2)
        self.speedy = self.max_speed * a / math.sqrt(1 + a**2)
        self.projectile_offset = pygame.Vector2(- int(self.rect.width * 0.5), int(self.rect.height * 0.25))
        if self.max_speed < 0:
            self.image = self.flipped_image
            self.projectile_offset = pygame.Vector2(int(self.rect.width * 0.5), int(self.rect.height * 0.25))
        #orient the arrow the rigth way
        if self.speedx != 0 and self.speedy != 0:
            rad = math.atan(self.speedy / self.speedx)
            degree = rad * 180 / math.pi
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.image, - degree)
            self.projectile_offset = self.projectile_offset.rotate(degree)
            self.rect = self.image.get_rect(center = old_center)

    def _use_brain(self):
        """
        ensure no unnecesairy calculations
        TODO also make sure this is not neccesairy. Probably needs a layer of abstraction inbetween or just hijack methods
        """
        pass

    def do_flip(self):
        """
        make sure the image does not flip
        TODO make a better sytem for this. This is kind of dumb.
        """
        pass

    def _get_bounding_box(self):
        """
        Return a rectangle at the tip of the arrow to make sure the arrow does not collide with unexpected places
        :return: a pygame.Rect object
        """
        return pygame.Rect(*(self.rect.center - self.projectile_offset), 10, 10)

    def move(self):
        if any(self._check_collision(sprites = False)):
            self._die()
        self.rect.topleft += pygame.Vector2(self.speedx,self.speedy)

    def _check_player_hit(self):
        if self.player.bounding_box.colliderect(self.bounding_box) and not self.player.immune[0]:
            self.player.set_immune()
            self.player._change_health(- self.damage)
            self._die()

class TextSprite(Entity):
    def __init__(self,text, pos, *groups, **kwargs):
        image = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20).render(str(text), True, pygame.Color(kwargs["color"]))
        Entity.__init__(self, pos, *groups, image = image)
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
