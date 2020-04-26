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
        return "{}_at_{},{}".format(type(self).__name__, self.rect.centerx, self.rect.centery)

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
            self.create_text(str(amnt), color = self.DAMAGE_COLOR)
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

    def create_text(self, text, **kwargs):
        """
        Create current_line above the enitiy often signifying damage or similar effects
        :param text: the current_line to be displayed
        :param **kwargs: can contain a color to color the current_line
        """
        self.text_values.append(TextSprite(text, self.rect.midtop, super().groups()[0], **kwargs))

    def _die(self):
        self._dead_sequence()

    def attributes(self):
        ats = super().attributes()
        return ats + ['max_speed', 'health','health_regen','immune']

class Enemy(LivingEntity):
    DAMAGE_COLOR = "blue"
    def __init__(self, pos, player, *groups, **kwargs):
        LivingEntity.__init__(self, pos, *groups, **kwargs)
        self.player = player
        self.previous_acctack_cycle = 0
        self.destination_coord = self.player.bounding_box.center

    def update(self,*args):
        super().update(*args)
        self.destination_coord = self.player.bounding_box.center
        if not self.dead:
            self._use_brain()
            self._check_player_hit()

    def _die(self):
        super()._die()
        self.player.xp[0] += self.xp

    def _use_brain(self):
        if self.destination_coord[0] > self.bounding_box.centerx - self.max_speed and self.destination_coord[0] < self.bounding_box.centerx + self.max_speed:
            self.speedx = 0.9
        elif self.destination_coord[0] < self.bounding_box.centerx:
            self.speedx -= 0.1 * self.max_speed
        elif self.destination_coord[0] > self.bounding_box.centerx:
            self.speedx += 0.1 * self.max_speed

        if self.destination_coord[1] < self.bounding_box.centery + self.max_speed and self.destination_coord[1] > self.bounding_box.centery - self.max_speed:
            self.speedy *= 0.9
        elif self.destination_coord[1] < self.bounding_box.centery:
            self.speedy -= 0.1 * self.max_speed
        elif self.destination_coord[1] > self.bounding_box.centery:
            self.speedy += 0.1 * self.max_speed

    def _check_player_hit(self):
        if self.player.bounding_box.colliderect(self.bounding_box) and not self.player.immune[0]:
            self.player.set_immune()
            self.player.change_health(- self.damage)

class RedSquare(Enemy):
    SIZE = (50,50)
    SPEED = 5
    def __init__(self, pos, player, tiles, *groups):
        image = sheets["enemies"].image_at((240,0), scale = self.SIZE)
        Enemy.__init__(self, pos, player, *groups, speed = self.SPEED, tiles = tiles, image = image)
        #make sure path is calculated at start of creation
        self.passed_frames = random.randint(0,60)
        self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
        self.move_tile = self.path.pop(-1)

    def _use_brain(self):
        #no movement stay in the same spot
        if not self.move_tile:
            self.destination_coord = self.player.bounding_box.center

        else:
            self.destination_coord = self.move_tile.center
        super()._use_brain()
        if self.passed_frames < 60 and self.path:
            self.passed_frames += 1
        else:
            solid_sprite_coords = [sprite.rect.center for sprite in super().groups()[0].sprites() if sprite.collision]
            self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box, solid_sprite_coords = solid_sprite_coords)
            self.passed_frames = 0
            self.move_tile = self.path.pop(-1)
        if self.move_tile and self.move_tile.coord == [int(self.bounding_box.x / 100), int(self.bounding_box.y / 100)]:
            self.move_tile = self.path.pop(-1)

class BadBat(Enemy):
    SIZE = (100,50)
    SPEED = 4
    def __init__(self, pos, player,tiles, *groups):
        animation_images = sheets["enemies"].images_at_rectangle((16,0,224,16), scale = self.SIZE, size = (32,16),
                                                                 color_key = (255,255,255))
        animation_sequence = animation_images + animation_images[::-1]
        self.animation = utilities.Animation(*animation_sequence, start_frame="random")
        Enemy.__init__(self, pos, player, *groups, speed = self.SPEED, tiles = tiles, image = self.animation.image[0])

    def update(self, *args):
        super().update(*args)
        self.animation.update()
        self.change_image(self.animation.image)

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the bat for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        return self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.2))

    def _check_collision(self, height = False):
        """
        Check the collision of x and y simoultaniously and return if x and y have collision
        :return:
        """
        xcol, ycol = False, False
        #check for x and y collison as long as any of the two are false.
        while (not xcol or not ycol):
            if (self.rect.left + self.speedx < 0 or self.rect.right + self.speedx > self.tiles.size[0] * constants.TILE_SIZE[0]):
                xcol = True
            if (self.bounding_box.top + self.speedy < 0 or self.rect.bottom + self.speedy > self.tiles.size[1] * constants.TILE_SIZE[1]):
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
    HEALTH = 2000
    HEALTH_REGEN = 1000
    SPEED = 0
    def __init__(self, pos, player, tiles, *groups):
        image = sheets["enemies"].image_at((0,48), scale = self.SIZE, size = (16,32), color_key = (255,255,255))
        Enemy.__init__(self, pos, player, *groups, health = self.HEALTH, health_regen = self.HEALTH_REGEN, speed = self.SPEED, tiles = tiles, image = image)

class Archer(Enemy):
    SIZE = (60,120)
    PROJECTILE_SIZE = (50,25)
    SHOOT_PLAYER_DISTANCE = 600
    SPEED = 4
    def __init__(self, pos, player,tiles, *groups):
        image = sheets["enemies"].image_at((0,16), scale = self.SIZE, size = (16,32), color_key = (255,255,255))
        self.arrow = sheets["enemies"].image_at((0,0), scale = self.PROJECTILE_SIZE, color_key = (255,255,255))
        Enemy.__init__(self, pos, player, *groups, tiles = tiles, size = [50,80], speed = self.SPEED, image = image)
        #make sure path is calculated at start of creation
        self.passed_frames = random.randint(0,60)
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
            try:
                self.projectiles.append(EnemyProjectile(self.rect.center, self.player.rect.center, self.player,
                                                    super().groups()[0], size = [50, 10],tiles = self.tiles, speed = 20,
                                                    image = self.arrow, bounding_size=[10,10], damage = 10))
            except IndexError:
                #happens when the projectile is spawned same frame as the enemy dies just skip IK bad practice
                pass
            self.shooting_cooldown = 50
        elif self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1

    def _use_brain(self):
        if not self.move_tile:
            self.destination_coord =  self.player.bounding_box.center
        else:
            self.destination_coord = self.move_tile.center
        super()._use_brain()
        if constants.game_rules.vision_line:
            self.vision_line = self.tiles.line_of_sight(self.bounding_box.center, self.player.bounding_box.center)[1]
        # eucledian distance lower then 600 stand still and shoot and also check if there is a direct line of sight
        if math.sqrt((self.rect.x - self.player.rect.x)**2 + (self.rect.y - self.player.rect.y)**2) < self.SHOOT_PLAYER_DISTANCE and\
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
        if self.move_tile and self.move_tile.coord == [int(self.bounding_box.x / 100), int(self.bounding_box.y / 100)]:
            self.move_tile = self.path.pop(-1)

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the player for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        bb = self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.4))
        return bb

    def _die(self):
        super()._die()
        for p in self.projectiles:
            p.dead = True

class BushMan(Enemy):
    SIZE = (100,100)
    AWAKE_DISTANCE = 400
    PATHING_RECALCULATING_SPEED = 30
    SPEED = 14
    def __init__(self, pos, player,tiles, *groups):
        image = sheets["enemies"].image_at((0,80), scale = self.SIZE, size = (16,16), color_key = (255,255,255))
        Enemy.__init__(self, pos, player, *groups, image = image, tiles=tiles, speed = self.SPEED)
        self.sleeping = True
        idle_imgs = sheets["enemies"].images_at_rectangle((16,80,96,16), scale = self.SIZE, size = (16,16), color_key = (255,255,255))
        wake_imgs = sheets["enemies"].images_at_rectangle((112,80,48,16), scale = self.SIZE, size = (16,16),color_key = (255,255,255))
        walk_imgs = sheets["enemies"].images_at_rectangle((160,80,48,16), scale = self.SIZE, size = (16,16),color_key = (255,255,255))
        self.idle_animation = utilities.Animation(*idle_imgs[:4], idle_imgs[2], *idle_imgs[4:], image, speed = [50,50,30,30,30,50,50,50], repetition=1)
        self.wake_up_animation = utilities.Animation(*idle_imgs[:3],*wake_imgs, speed = 10, repetition=1)
        self.walking_animation = utilities.Animation(walk_imgs[0], walk_imgs[1], walk_imgs[0], walk_imgs[2], speed = 10)
        self.idle_animation.finished = True
        self.passed_frames = random.randint(0, self.PATHING_RECALCULATING_SPEED)
        self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
        self.move_tile = self.path.pop(-1)

    def update(self):
        super().update()
        #awake when the player moves within a certain distance
        if self.sleeping and (math.sqrt((self.rect.x - self.player.rect.x)**2 + (self.rect.y - self.player.rect.y)**2))\
                < self.AWAKE_DISTANCE:
            self.sleeping = False
            self.passed_frames = random.randint(0, self.PATHING_RECALCULATING_SPEED)
            self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
            self.move_tile = self.path.pop(-1)
        elif not self.sleeping and not self.visible[0]:
            self.sleeping = True
            self.speedy, self.speedx = 0,0
            self.wake_up_animation.reset()
            self.change_image([self.orig_image, self.flipped_image])
        self.__run_animations()

    def __run_animations(self):
        if self.sleeping:
            if not self.idle_animation.finished:
                self.idle_animation.update()
                self.change_image(self.idle_animation.image)
            elif random.randint(1, 500) == 1:
                self.idle_animation.reset()
            else:
                self.change_image([self.image, self.flipped_image])
        else:
            if not self.wake_up_animation.finished:
                self.wake_up_animation.update()
                self.change_image(self.wake_up_animation.image)
            elif self.speedx != 0 or self.speedy != 0:
                self.walking_animation.update()
                self.change_image(self.walking_animation.image)

    def _use_brain(self):
        if self.sleeping or not self.wake_up_animation.finished:
            return
        if not self.move_tile:
            self.destination_coord = self.player.bounding_box.center
        else:
            self.destination_coord = self.move_tile.center
        super()._use_brain()
        if self.passed_frames <  self.PATHING_RECALCULATING_SPEED and self.path:
            self.passed_frames += 1
        else:
            solid_sprite_coords = [sprite.rect.center for sprite in super().groups()[0].sprites() if sprite.collision]
            self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box, solid_sprite_coords = solid_sprite_coords)
            self.passed_frames = 0
            self.move_tile = self.path.pop(-1)
        if self.move_tile and self.move_tile.coord == [round(self.bounding_box.x / 100), round(self.bounding_box.y / 100)]:
            self.move_tile = self.path.pop(-1)

    def _get_bounding_box(self):
        return self.rect.inflate(0.75, 0.75)

class Projectile(LivingEntity):
    ACCURACY = 80
    def __init__(self, start_pos, end_pos, *groups, accuracy = ACCURACY, **kwargs):
        LivingEntity.__init__(self, start_pos, *groups, **kwargs)
        self.rect.center = start_pos
        self.pos = list(self.rect.center)
        self.accuracy = accuracy
        self.trajectory = self._configure_trajectory(start_pos, end_pos)
        if "bounding_size" in kwargs:
            self.bb_size = kwargs["bounding_size"]
        else:
            self.bb_size = (self.rect.width, self.rect.height)

    def update(self, *args):
        super().update()
        if not self.dead:
            self._check_hit()

    def _check_hit(self):
        for sprite in super().groups()[0].sprites():
            if isinstance(sprite, Enemy) and not sprite.immune[0] and sprite != self and not self.dead:
                if sprite.rect.colliderect(self.rect):
                    sprite.change_health(- self.damage)
                    self.dead = True

    def move(self):
        if any(self._check_collision(sprites = False)):
            self.dead = True
        self.pos[0] += self.trajectory.speedx
        self.pos[1] += self.trajectory.speedy
        self.rect.center = self.pos

    def _configure_trajectory(self, start_pos, end_pos):
        trajectory = trajectories.LinearTrajectory(start_pos, end_pos, self.rect, self.image, super().groups()[0],
                                                   max_speed=self.max_speed, accuracy = self.accuracy)
        self.image = trajectory.image
        self.rect = trajectory.rect
        self.pos = list(self.rect.center)
        return trajectory

class PlayerProjectile(Projectile):
    def __init__(self, start_pos, end_pos, *groups, **kwargs):
        Projectile.__init__(self, start_pos, end_pos, *groups, **kwargs)

    def _configure_trajectory(self, start_pos, end_pos):
        """
        Original trajectory but now containing a screen relative coordinate
        :param start_pos:
        :param end_pos:
        """
        trajectory = trajectories.LinearTrajectory(utilities.get_screen_relative_coordinate(start_pos), end_pos, self.rect,
                                                   self.image, super().groups()[0],max_speed=self.max_speed, accuracy = self.accuracy)
        self.image = trajectory.image
        self.rect = trajectory.rect
        self.pos = list(self.rect.center)
        return trajectory

class EnemyProjectile(Projectile):
    def __init__(self, start_pos, end_pos, player, *groups, **kwargs):
        Projectile.__init__(self, start_pos, end_pos, *groups, **kwargs)
        self.player = player

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
        if not hasattr(self, "trajectory"):
            return self.rect
        return pygame.Rect(*(self.rect.center - self.trajectory.projectile_offset), *(self.bb_size))

    def _check_hit(self):
        if self.player.bounding_box.colliderect(self.bounding_box) and not self.player.immune[0]:
            self.player.change_health(-self.damage)
            self.player.set_immune()
            self.dead = True

class TextSprite(Entity):
    def __init__(self,text, pos, *groups, **kwargs):
        image = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 20).render(str(text), True, pygame.Color(kwargs["color"]))
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
