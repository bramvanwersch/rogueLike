import pygame, random, math
import utilities, constants, trajectories
from game_images import sheets

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, *groups, visible = [True,True], **kwargs):
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
            self.image = pygame.Surface((100,100)).convert()
            self.image.fill((255, 0, 179))
        # if the sprite should be visible at the current moment. and if it should be able to be unloaded
        self.visible = visible
        self.orig_image = self.image
        self.rect = self.image.get_rect(topleft = pos)
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
    def __init__(self, pos, player, *groups, action = None, **kwargs):
        """
        Entity that preforms an action when a player is pressing the interaction key and colliding with the entity
        """
        Entity.__init__(self, pos, *groups, **kwargs)
        self.player = player
        #can be set to a function to give functionality to the entity
        self.interactable = True
        self.action_function = action

    def update(self, *args):
        super().update(*args)
        if self.action_function and self.interactable and self.player.pressed_keys[constants.INTERACT]:
            if self.rect.colliderect(self.player.rect):
                self.action_function()

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
        pass
        # if self.player.right_arm.attacking and self.rect.colliderect(self.player.right_arm.bounding_box) and\
        #         self.previous_acctack_cycle != self.player.right_arm.attack_cycle:
        #     self._change_health(- self.player.right_arm.damage)
        #     self.previous_acctack_cycle = self.player.right_arm.attack_cycle

class RedSquare(Enemy):
    SIZE = (50,50)
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
    SIZE = (100,50)
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

    def _check_collision(self, height = False):
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
    SIZE = (50,100)
    def __init__(self, pos, player, tiles, *groups):
        image = sheets["enemies"].image_at((0,48), scale = (50,100), size = (16,32), color_key = (255,255,255))
        Enemy.__init__(self, pos, player, *groups, health = 2000, health_regen = 1000, speed = 0, tiles = tiles, image = image)

class Archer(Enemy):
    SIZE = (60,120)
    def __init__(self, pos, player,tiles, *groups):
        image = sheets["enemies"].image_at((0,16), scale = (60,120), size = (16,32), color_key = (255,255,255))
        self.arrow = sheets["enemies"].image_at((0,0), scale =(50,25), color_key = (255,255,255))
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
        self.projectiles = []

    def update(self, *args):
        super().update(*args)
        for p in self.projectiles:
            if p.dead:
                self.projectiles.remove(p)
        if self.shooting and self.shooting_cooldown <= 0:
            #update animation
            # self.shooting_animation.update()
            # if self.shooting_animation.cycles > 0:
            self.shooting = False
            self.projectiles.append(EnemyProjectile(self.rect.center, self.player, super().groups()[0], size = [50, 10],
                                                    tiles = self.tiles, speed = 20, image = self.arrow))
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

    def _die(self):
        for p in self.projectiles:
            p.dead = True

class Projectile(LivingEntity):
    def __init__(self, start_pos, *groups, **kwargs):
        LivingEntity.__init__(self, start_pos, *groups, **kwargs)
        self.rect.center = start_pos

    def _get_bounding_box(self):
        """
        Return a rectangle at the tip of the arrow to make sure the arrow does not collide with unexpected places
        :return: a pygame.Rect object
        """
        if not hasattr(self, "trajectory"):
            return self.rect
        return pygame.Rect(*(self.rect.center - self.trajectory.projectile_offset), 10,10)

    def move(self):
        if any(self._check_collision(sprites = False)):
            self._die()
        self.rect.topleft += pygame.Vector2(self.trajectory.speedx,self.trajectory.speedy)

    def __configure_trajectory(self):
        pass

class EnemyProjectile(Projectile):
    def __init__(self, start_pos, player, *groups, **kwargs):
        Projectile.__init__(self, start_pos, *groups, **kwargs)
        self.player = player
        self.trajectory = self.__configure_trajectory()

    def do_flip(self):
        """
        make sure the image does not flip
        TODO make a better sytem for this. This is kind of dumb.
        """
        pass

    def update(self, *args):
        super().update()
        self._check_player_hit()

    def _check_player_hit(self):
        if self.player.bounding_box.colliderect(self.bounding_box) and not self.player.immune[0]:
            self.player.set_immune()
            self.player._change_health(- self.damage)
            self._die()

    def __configure_trajectory(self):
        trajectory = trajectories.LinearTrajectory(self.rect.center, self.player.rect.center, self.rect, self.image, super().groups()[0],
                                                   max_speed=20)
        self.image = trajectory.image
        self.rect = trajectory.rect
        return trajectory


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
