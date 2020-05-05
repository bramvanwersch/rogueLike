import pygame, random, math
import numpy as np
from pygame.locals import *
import entities, utilities, weapon, constants, projectiles
from game_images import image_sheets, animations
from constants import *

class Player(entities.LivingEntity):
    _PPS = PPS_PLAYER
    image_size = (16,32)
    def __init__(self, pos, *groups):
        idle_image = image_sheets["player"].image_at((0, 0), color_key = (255, 255, 255), pps=self.PPS)
        entities.LivingEntity.__init__(self, pos,damage=5, image = idle_image)
        self.walking_animation = animations["walk_Player"]
        self.idle_animation = animations["idle_Player"]
        self.dead_animation = animations["dead_Player"]
        self.events = []
        self.inventory = Inventory()
        self._layer = constants.PLAYER_LAYER2
        arm = image_sheets["player"].image_at((32, 32), scale = (15, 35))
        self.right_arm = RightArm((self.rect.centerx - 8, self.rect.centery - 8), image = arm)
        self.left_arm = LeftArm((self.rect.centerx - 8, self.rect.centery - 8), image = arm)
        self.pressed_keys = {key : False for key in constants.KEYBOARD_KEYS}
        self.dodge_cd = 0
        self.xp = [0,1000]
        self.level = 1

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the player for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        b = self.rect.bottom
        bb = self.rect.inflate((-self.rect.width * 0.25, - self.rect.height * 0.2))
        bb.bottom = b
        return bb

    def update(self, *args):
        """
        Processes user input to make the player do actions.
        """
        super().update(*args)
        if self.dead:
            return
        if self.xp[0] >= self.xp[1]:
            self.next_level()
        self.handle_user_input()
        #move arms witht the body
        if self.flipped:
            self.right_arm.update_arm((self.rect.centerx , self.rect.centery + 5))
            self.left_arm.update_arm((self.rect.centerx - 5, self.rect.centery +14))
        elif not self.flipped:
            self.right_arm.update_arm((self.rect.centerx + 3, self.rect.centery + 7))
        for p in self.right_arm.projectiles:
            if p.dead:
                self.right_arm.projectiles.remove(p)
        self.animations()

    def next_level(self):
        self.level += 1
        self.xp = [self.xp[0] - self.xp[1], int(self.xp[1] * 1.25)]

    def handle_user_input(self):
        """
        Go past all the events not processed by the main programe and do actions accordingly
        :return: None
        """
        for event in self.events:
            if event.type == KEYDOWN:
                self.pressed_keys[event.key] = True
            elif event.type == KEYUP:
                self.pressed_keys[event.key] = False
            elif event.type == MOUSEBUTTONDOWN:
                self.pressed_keys["mouse1"] = True
            elif event.type == MOUSEBUTTONUP:
                self.pressed_keys["mouse1"] = False
#moving
        if self.pressed_keys[RIGHT] and self.pressed_keys[LEFT]:
            self.speedx = 0
        else:
            if self.pressed_keys[RIGHT]:
                self.speedx += 0.1 * self.max_speed
            if self.pressed_keys[LEFT]:
                self.speedx -= 0.1 * self.max_speed
            if not self.pressed_keys[LEFT] and not self.pressed_keys[RIGHT]:
                self.speedx = 0
        if self.pressed_keys[DOWN] and self.pressed_keys[UP]:
            self.speedy = 0
        else:
            if self.pressed_keys[UP]:
                self.speedy -= 0.1 * self.max_speed
            if self.pressed_keys[DOWN]:
                self.speedy += 0.1 * self.max_speed
            if not self.pressed_keys[UP] and not self.pressed_keys[DOWN]:
                self.speedy  = 0
#attacking
        if self.pressed_keys["mouse1"]:
            self.right_arm.do_attack(self.tiles)
        if self.pressed_keys[RELOAD] and self.right_arm.weapon:
            self.right_arm.weapon.reload()

    def do_flip(self):
        """
        Flips an image based on the direction the player is attacking in. Also flips the arms accordingly.
        :return: None
        """
        if pygame.mouse.get_pos()[0] < utilities.get_screen_relative_coordinate(self.rect.center)[0]:
            if not self.flipped:
                self.flipped = not self.flipped
        else:
            if self.flipped:
                self.flipped = not self.flipped
        if self.flipped:
            self.image = self.flipped_image
        else:
            self.image = self.orig_image
        if self.right_arm.flipped != self.flipped:
            self.right_arm.flip()
            self.left_arm.flip()

    def _die(self):
        """
        Function repeaditly called when the player is dead.
        :return: None
        """
        super()._die()
        for p in self.right_arm.projectiles:
            p.dead = True
        self.dead_animation.update()
        if self.dead_animation.marked:
            self.right_arm.visible = [False, False]
            self.left_arm.visible = [False, False]
        self.change_image(self.dead_animation.image)

    def animations(self):
        """
        Runs an animation based on the current actions of the player.
        """
        if int(self.speedx) != 0 or int(self.speedy) != 0:
            self.walking_animation.update()
            self.change_image(self.walking_animation.image)
            self.idle_animation.cycles += 1
        else:
            #idle animation plays at random every 500 frames of inactivity
            self.walking_animation.reset()
            #while shooting do not idle
            if self.pressed_keys["mouse1"]:
                self.idle_animation.cycles = 1
                return
            if not self.idle_animation.finished:
                self.idle_animation.update()
                if self.idle_animation.marked:
                    self.right_arm.visible = [False, True]
                    self.left_arm.visible = [False, self.left_arm.visible[1]]
                self.change_image(self.idle_animation.image)
            elif random.randint(1, 500) == 1:
                self.idle_animation.reset()
            else:
                self.change_image([self.image, self.flipped_image])

    def equip(self, weapon):
        """
        Things to do when the player equips a new weapon
        :param weapon:
        """
        self.right_arm.equip(weapon)
        self.inventory.equiped = weapon

    def attributes(self):
        ats = super().attributes()
        return ats + ['inventory', 'right_arm', 'left_arm','level']

class GenericArm(entities.Entity):
    def __init__(self, pos, **kwargs):
        self.arm = kwargs["image"]
        entities.Entity.__init__(self, pos, **kwargs)
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self._layer = constants.PLAYER_LAYER2

    def flip(self):
        """
        Flips the image and puts it on the layer behind the player if the image is flipped as to not move the weapon
        between hands
        """
        self.flipped = not self.flipped
        if self.flipped:
            super().groups()[0].change_layer(self, constants.PLAYER_LAYER1)
        else:
            super().groups()[0].change_layer(self, constants.PLAYER_LAYER2)

    def update_arm(self, *args):
        self.move_arm(*args)

class LeftArm(GenericArm):
    def __init__(self, pos, **kwargs):
        GenericArm.__init__(self, pos, **kwargs)
        self._layer = constants.PLAYER_LAYER2
        self.visible = [False, False]

    def flip(self):
        """
        When the right side is shown the left arm is invisible otherwise it will be visible
        """
        self.flipped = not self.flipped
        if self.flipped:
            self.visible = [True, True]
            super().groups()[0].change_layer(self, constants.PLAYER_LAYER2)
        else:
            self.visible = [False, False]
            super().groups()[0].change_layer(self, constants.BOTTOM_LAYER)

    def move_arm(self, *pos):
        self.rect.center = pos

class RightArm(GenericArm):
    def __init__(self, pos, **kwargs):
        GenericArm.__init__(self, pos, **kwargs)
        #for tracking the original image when rotating
        self.orig_image = self.image
        self.angle = 0
        #tracks the number of attacks and helps enemies track damage
        self.attack_cooldown = 0
        self.projectiles = []
        self.offset = pygame.Vector2(20,-5)
        self.orig_bullet = image_sheets["weapons"].image_at((160, 0), size = (32, 16), color_key = (255, 255, 255))
        self.bullet_image = self.orig_bullet
        self.weapon = None
        self.bullet_start_distance = 0

    def update_arm(self, *args):
        super().update_arm(*args)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= constants.GAME_TIME.get_time() / 1000
        if self.weapon:
            if self.weapon.reloading and self.reload_cooldown <= 0:
                self.weapon.reload(start = False)
            elif self.weapon.reloading:
                self.reload_cooldown -= constants.GAME_TIME.get_time() / 1000
            else:
                self.reload_cooldown = self.weapon.reload_speed

    def move_arm(self, pos):
        """
        They player class tells where to put the arm relative to the player. Then the arm is rotated based on the
        current angle. This method is called every update from the player class.
        :param pos: position to move the arm to.
        """
        self.rect.center = pos
        mx, my = pygame.mouse.get_pos()
        screen_player_x,screen_player_y = utilities.get_screen_relative_coordinate(self.rect.center)
        if mx == screen_player_x:
            return
        rad = math.atan((my - screen_player_y) / (mx - screen_player_x))
        self.angle = (rad / math.pi) * 180
        self.rotate()

    def do_attack(self, tiles):
        """
        spawn a bullet of the center of the player in the direction of the mouse pointer
        """
        #dont fire when any of these actions are happening
        if self.attack_cooldown > 0 or self.weapon.magazine <= 0 or (self.weapon.magazine <= 0 and self.weapon.reloading):
            if self.weapon.magazine <= 0 and not self.weapon.reloading:
                self.weapon.reload()
        else:
            for _ in range(self.weapon.bullets_per_shot):
                self.projectiles.append(projectiles.PlayerProjectile(self.rect.center, pygame.mouse.get_pos(), super().groups()[0],
                                                                     tiles = tiles, damage = self.weapon.damage, speed = 20, accuracy = self.weapon.accuracy,
                                                                     image = self.bullet_image, start_move= self.bullet_start_distance))
            self.weapon.magazine -= self.weapon.bullets_per_shot
            self.attack_cooldown = 1 / self.weapon.fire_rate
            if self.weapon.reloading:
                self.reload_cooldown = self.weapon.reload_speed
                self.weapon.reloading = False

    def rotate(self):
        """
        Rotate an image and calculate a new position based on a offset and an angle.
        """
        if self.flipped:
            self.image = pygame.transform.rotozoom(self.orig_flipped_image, - self.angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.orig_image, - self.angle, 1)
        offset_rotated = self.offset.rotate(self.angle)
        #weapon offset rotated
        if self.weapon:
            pass
        if not self.flipped:
            self.rect = self.image.get_rect(center=self.rect.center + offset_rotated)
        elif self.flipped:
            self.rect = self.image.get_rect(center=self.rect.center - offset_rotated)
        #ensure the bounding box is synced with the image location
        self.bounding_box = self.rect

    def flip(self):
        super().flip()
        if self.flipped:
            self.image = self.orig_flipped_image
        else:
            self.image = self.orig_image

    def equip(self, weapon):
        """
        Equip a weapon
        :param weapon: an instance of a AbstractWeapon class or further
        """
        self.weapon = weapon
        weapon_image = self.weapon.image
        # weapon_image = pygame.transform.rotate(weapon_image, 90)
        # weapon_image = pygame.transform.flip(weapon_image, True, False)
        weapon_image = pygame.transform.scale(weapon_image, (round(0.8*weapon_image.get_rect().width), round(0.8*weapon_image.get_rect().height)))
        weapon_image.set_colorkey((255,255,255), pygame.RLEACCEL)
        image = pygame.Surface((weapon_image.get_rect().width, weapon_image.get_rect().height))
        flipped_image = pygame.Surface((weapon_image.get_rect().width, weapon_image.get_rect().height))
        ir = image.get_rect()
        rotated_arm = pygame.transform.rotate(self.arm, 40)
        ra = rotated_arm.get_rect()
        #make the surface fit the biggest size either arm or the weapon
        if ra.width + 25 > ir.width and ra.height + 20 > ir.height:
            image = pygame.Surface((ra.width + 25, ra.height + 20))
            flipped_image = pygame.Surface((ra.width + 25, ra.height + 20))
        elif ra.width + 25 > ir.width:
            image = pygame.Surface((ra.width + 25, ir.height))
            flipped_image = pygame.Surface((ra.width + 25, ir.height))
        elif ra.height + 20 > ir.height:
            image = pygame.Surface((ir.width, ra.height + 20))
            flipped_image = pygame.Surface((ir.width, ra.height + 20))
        image.fill((255,255,255))
        flipped_image.fill((255,255,255))

        image.blit(weapon_image, (0, image.get_rect().height - weapon_image.get_rect().height), weapon_image.get_rect())
        image.blit(rotated_arm,(25,20), rotated_arm.get_rect())
        image.set_colorkey((255,255,255), pygame.RLEACCEL)
        flipped_image.blit(rotated_arm,(25,20), rotated_arm.get_rect())
        flipped_image.blit(weapon_image, (0, image.get_rect().height - weapon_image.get_rect().height), weapon_image.get_rect())
        flipped_image.set_colorkey((255,255,255), pygame.RLEACCEL)

        image = image.convert_alpha()
        flipped_image = pygame.transform.flip(flipped_image, True, False)
        flipped_image = flipped_image.convert_alpha()

        self.image = image#self.__create_weapon_arm(weapon_image)
        self.orig_flipped_image = flipped_image
        self.orig_image = self.image
        self.rect = self.image.get_rect(center = self.rect.center)

        #load th bullet
        self.bullet_image = pygame.transform.scale(self.orig_bullet, (30,20))

        #set values for the weapon
        self.damage = weapon.damage
        self.reload_cooldown = self.weapon.reload_speed
        self.offset = pygame.Vector2(self.rect.width * 0.5 - 30, -6)
        self.bullet_start_distance =  int((self.rect.width * 0.5) / 20 + 1)
        pd = int((Player.SIZE[1] * 0.5) / 20 + 1)
        if pd > self.bullet_start_distance:
            self.bullet_start_distance = pd

    def attributes(self):
        ats = super().attributes()
        return ats + ['damage','reload_cooldown']

class Inventory:
    def __init__(self):
        self.size = 16
        self.items = []
        self.weight = 0
        self.equiped = None

    def add(self, item):
        if len(self.items) <= self.size:
            self.items.append(item)
            self.weight += item.weight

    def remove(self, item):
        self.items.remove(item)
        self.weight -= item.weight

    def attributes(self):
        return ['size','wheight']