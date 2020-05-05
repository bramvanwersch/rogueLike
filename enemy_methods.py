import math, random

import constants, projectiles
from entities import LivingEntity
from game_images import image_sheets, animations

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
    SPEED = 5
    image_size = (16,16)
    def __init__(self, pos, player, tiles, *groups, **kwargs):
        image = image_sheets["enemies"].image_at((240, 0), pps = self.PPS)
        Enemy.__init__(self, pos, player, *groups, speed = self.SPEED, tiles = tiles, image = image, **kwargs)
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
    SPEED = 4
    image_size = (32, 16)
    def __init__(self, pos, player,tiles, *groups, **kwargs):
        self.animation = animations["move_BadBat"].copy()
        Enemy.__init__(self, pos, player, *groups, speed = self.SPEED, tiles = tiles, image = self.animation.image[0], **kwargs)

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
    HEALTH = 2000
    HEALTH_REGEN = 1000
    SPEED = 0
    image_size = (16,32)
    def __init__(self, pos, player, tiles, *groups, **kwargs):
        image = image_sheets["enemies"].image_at((0, 48), scale = self.SIZE, size = self.image_size, color_key = (255, 255, 255))
        Enemy.__init__(self, pos, player, *groups, health = self.HEALTH, health_regen = self.HEALTH_REGEN, speed = self.SPEED, tiles = tiles, image = image, **kwargs)


class BlowMan(Enemy):
    _PPS = constants.PPS_BLOWMAN
    PROJECTILE_SIZE = (50,25)
    SHOOT_PLAYER_DISTANCE = 600
    SHOOTING_COOLDOWN = 50
    SPEED = 4
    PROJECTILE_SPEED = 20
    image_size = (16, 32)
    def __init__(self, pos, player,tiles, *groups, **kwargs):
        image = image_sheets["enemies"].image_at((96, 16), pps = self.PPS, size = self.image_size, color_key = (255, 255, 255))
        self.arrow = image_sheets["enemies"].image_at((0, 0), scale = self.PROJECTILE_SIZE, color_key = (255, 255, 255))
        Enemy.__init__(self, pos, player, *groups, tiles = tiles, size = [50,80], speed = self.SPEED, image = image, **kwargs)
        #make sure path is calculated at start of creation
        self.shooting_animation = animations["attack_BlowMan"].copy()
        self.shooting_animation.set_speed(int(self.SHOOTING_COOLDOWN / len(self.shooting_animation.animation_images)))
        self.walking_animation = animations["walk_BlowMan"].copy()
        self.take_weapon_animation = animations["take_weapon_BlowMan"].copy()
        self.remove_weapon_animation = animations["remove_weapon_BlowMan"].copy()
        self.passed_frames = random.randint(0,60)
        self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
        self.move_tile = self.path.pop(-1)
        self.shooting = False
        #current max
        self.shoot_player_distance = self.SHOOT_PLAYER_DISTANCE
        self.projectile_speed = self.PROJECTILE_SPEED
        self.collision = True
        self.vision_line = []
        self.projectiles = []

    def update(self, *args):
        super().update(*args)
        for p in self.projectiles:
            if p.dead:
                self.projectiles.remove(p)
        if self.shooting:
            if self.shooting_animation.finished:
                try:
                    self.projectiles.append(projectiles.HomingProjectile(self.rect.center, self.player.rect.center, self.player, super().groups()[0], tiles = self.tiles,
                                            start_move= int((self.rect.height * 1) / self.projectile_speed + 1), size = [10,10]))
                    # self.projectiles.append(projectiles.EnemyProjectile(self.rect.center, self.player.rect.center, self.player,
                    #                                                     super().groups()[0], size = [50, 10], tiles = self.tiles, speed = self.projectile_speed, image = self.arrow,
                    #                                                     bounding_size=[10,10], damage = 10, start_move= int((self.rect.height * 0.5) / self.projectile_speed + 1)))
                except IndexError:
                    #happens when the projectile is spawned same frame as the enemy dies just skip IK bad practice
                    pass
                self.shooting = False
                self.shooting_animation.reset()
        self.__run_animations()

    def move(self):
        if self.remove_weapon_animation.finished:
            super().move()

    def __run_animations(self):
        if self.shooting and not self.take_weapon_animation.finished:
            self.take_weapon_animation.update()
            self.change_image(self.take_weapon_animation.image)
            self.remove_weapon_animation.reset()
        elif self.shooting :
            self.shooting_animation.update()
            self.change_image(self.shooting_animation.image)
        elif not self.shooting and not self.remove_weapon_animation.finished:
            self.remove_weapon_animation.update()
            self.change_image(self.remove_weapon_animation.image)
        elif self.speedx != 0 and self.speedy != 0:
            self.walking_animation.update()
            self.change_image(self.walking_animation.image)
            self.take_weapon_animation.reset()
        else:
            self.change_image([self.orig_image, self.flipped_image])

    def _use_brain(self):
        if not self.move_tile:
            self.destination_coord =  self.player.bounding_box.center
        else:
            self.destination_coord = self.move_tile.center
        super()._use_brain()
        if constants.game_rules.vision_line:
            self.vision_line = self.tiles.line_of_sight(self.bounding_box.center, self.player.bounding_box.center)[1]
        # eucledian distance lower then 600 stand still and shoot and also check if there is a direct line of sight
        if math.sqrt((self.rect.x - self.player.rect.x)**2 + (self.rect.y - self.player.rect.y)**2) < self.shoot_player_distance and\
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

    def attributes(self):
        ats = super().attributes()
        return ats + ['shooting_cooldown', 'shoot_player_distance','projectile_speed']

class BushMan(Enemy):
    _PPS = constants.PPS_BUSHMAN
    AWAKE_DISTANCE = 400
    PATHING_RECALCULATING_SPEED = 30
    SPEED = 14
    image_size = (16, 16)
    def __init__(self, pos, player,tiles, *groups, **kwargs):
        image = image_sheets["enemies"].image_at((0, 80), pps = self.PPS, size = self.image_size, color_key = (255, 255, 255))
        Enemy.__init__(self, pos, player, *groups, image = image, tiles=tiles, speed = self.SPEED, **kwargs)
        self.sleeping = True
        self.idle_animation = animations["idle_BushMan"].copy()
        self.wake_up_animation = animations["wake_BushMan"].copy()
        self.walking_animation = animations["walk_BushMan"].copy()
        self.idle_animation.finished = True
        self.passed_frames = random.randint(0, self.PATHING_RECALCULATING_SPEED)
        self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
        self.move_tile = self.path.pop(-1)
        #make it an instance aswell as a class variable so you can change for an instance but also all classes
        self.awake_distance = self.AWAKE_DISTANCE

    def update(self):
        super().update()
        #awake when the player moves within a certain distance or the player damages the bushman
        if (self.sleeping and (math.sqrt((self.rect.x - self.player.rect.x)**2 + (self.rect.y - self.player.rect.y)**2))\
                < self.awake_distance) or (self.sleeping and self.damaged):
            self.sleeping = False
            self.passed_frames = random.randint(0, self.PATHING_RECALCULATING_SPEED)
            self.path = self.tiles.pathfind(self.player.bounding_box, self.bounding_box)
            self.move_tile = self.path.pop(-1)
        elif not self.sleeping and not self.visible[0]:
            self.sleeping = True
            self.damaged = False
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

    def attributes(self):
        ats = super().attributes()
        return ats +['sleeping','awake_distance']