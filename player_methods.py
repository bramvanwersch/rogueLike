import pygame, random, math
import numpy as np
from pygame.locals import *
import entities, utilities, weapon, constants
from game_images import sheets
from constants import *
from entities import LivingEntity

class Player(LivingEntity):
    def __init__(self, pos, start_weapon, *groups):
        idle_image = sheets["player"].image_at((0,0), color_key = (255,255,255), scale = (60,120))
        LivingEntity.__init__(self, pos,damage=5, image = idle_image)
        walking_images = sheets["player"].images_at((0,0),(224,0),(240,0),(0,32),(16,32),
                                                     color_key = (255,255,255), scale = (60,120))
        idle_images = sheets["player"].images_at((0,0),(176,0),(192,0),(208,0),
                                                  color_key = (255,255,255), scale = (60,120))
        dead_images = sheets["player"].images_at((16,0),(176,0),(32,0),(48,0),(64,0),(80,0),(96,0),(112,0),(128,0),
                                                  (144,0),(160,0),(48,32),(64,32),color_key = (255,255,255), scale = (60,120))
        self.walking_animation = utilities.Animation(walking_images[0],walking_images[1],walking_images[2],
                                                     walking_images[1],walking_images[0],walking_images[3],
                                                     walking_images[4],walking_images[3])
        self.idle_animation = utilities.MarkedAnimation(idle_images[0],idle_images[1],idle_images[2],idle_images[3],
                                                        idle_images[3],idle_images[2],idle_images[1],idle_images[0],
                                                        speed = 40, marked_frames=[2,3,4,5])
        self.dead_animation = utilities.MarkedAnimation(*dead_images, marked_frames=[3,4,5,6,7,8,9,10])
        self.events = []
        self.inventory = Inventory()
        self._layer = utilities.PLAYER_LAYER2
        self.inventory.add(start_weapon)
        arm = sheets["player"].image_at((32,32) ,scale = (15,35))
        self.right_arm = RightArm((self.rect.centerx - 8, self.rect.centery - 8), image = arm)
        self.equip(start_weapon)
        self.left_arm = LeftArm((self.rect.centerx - 8, self.rect.centery - 8), image = arm)
        l = [KEYDOWN, KEYUP, KMOD_ALT, KMOD_CAPS, KMOD_CTRL, KMOD_LALT, KMOD_LCTRL, KMOD_LMETA, KMOD_LSHIFT, KMOD_META,
             KMOD_MODE, KMOD_NONE, KMOD_NUM, KMOD_RALT, KMOD_RCTRL, KMOD_RMETA, KMOD_RSHIFT, KMOD_SHIFT, K_0, K_1, K_2,
             K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_AMPERSAND, K_ASTERISK, K_AT, K_BACKQUOTE, K_BACKSLASH, K_BACKSPACE,
             K_BREAK, K_CAPSLOCK, K_CARET, K_CLEAR, K_COLON, K_COMMA, K_DELETE, K_DOLLAR, K_DOWN, K_END, K_EQUALS,
             K_ESCAPE, K_EURO, K_EXCLAIM, K_F1, K_F10, K_F11, K_F12, K_F13, K_F14, K_F15, K_F2, K_F3, K_F4, K_F5, K_F6,
             K_F7, K_F8, K_F9, K_FIRST, K_GREATER, K_HASH, K_HELP, K_HOME, K_INSERT, K_KP0, K_KP1, K_KP2, K_KP3, K_KP4,
             K_KP5, K_KP6, K_KP7, K_KP8, K_KP9, K_KP_DIVIDE, K_KP_ENTER, K_KP_EQUALS, K_KP_MINUS, K_KP_MULTIPLY,
             K_KP_PERIOD, K_KP_PLUS, K_LALT, K_LAST, K_LCTRL, K_LEFT, K_LEFTBRACKET, K_LEFTPAREN, K_LESS, K_LMETA,
             K_LSHIFT, K_LSUPER, K_MENU, K_MINUS, K_MODE, K_NUMLOCK, K_PAGEDOWN, K_PAGEUP, K_PAUSE, K_PERIOD, K_PLUS,
             K_POWER, K_PRINT, K_QUESTION, K_QUOTE, K_QUOTEDBL, K_RALT, K_RCTRL, K_RETURN, K_RIGHT, K_RIGHTBRACKET,
             K_RIGHTPAREN, K_RMETA, K_RSHIFT, K_RSUPER, K_SCROLLOCK, K_SEMICOLON, K_SLASH, K_SPACE, K_SYSREQ, K_TAB,
             K_UNDERSCORE, K_UNKNOWN, K_UP, K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o,
             K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z,"mouse1"]
        self.pressed_keys = {key : False for key in l}
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
            self.right_arm.move_arm((self.rect.centerx , self.rect.centery + 5))
            self.left_arm.move_arm((self.rect.centerx - 5, self.rect.centery +14))
        elif not self.flipped:
            self.right_arm.move_arm((self.rect.centerx + 3, self.rect.centery + 7))
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
#dodge
        if self.pressed_keys[DODGE] and self.dodge_cd <= 0:
            self.__dodge()
        else:
            self.dodge_cd -= 1
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


    def __dodge(self):
        #TODO not finished yet
        dd = 250
        m_r = self.rect
        if self.pressed_keys[LEFT]:
            m_r = m_r.move(-dd,0)
        if self.pressed_keys[RIGHT]:
            m_r = m_r.move(dd, 0)
        if self.pressed_keys[UP]:
            m_r = m_r.move(0, -dd)
        if self.pressed_keys[DOWN]:
            m_r = m_r.move(0, dd)
        if not self.tiles.solid_collide(m_r):
            self.rect = m_r
        self.dodge_cd = 50

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
        :return: None
        """
        if int(self.speedx) != 0 or int(self.speedy) != 0:
            self.walking_animation.update()
            self.change_image(self.walking_animation.image)
            self.idle_animation.cycles += 1
        else:
            #idle animation plays at random every 500 frames of inactivity
            self.walking_animation.reset()
            if self.idle_animation.cycles == 0:
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
        self.speed = 10 *(1- self.right_arm.weapon.weight / 250)
        self.inventory.equiped = weapon

class GenericArm(entities.Entity):
    def __init__(self, pos, **kwargs):
        self.arm = kwargs["image"]
        entities.Entity.__init__(self, pos, **kwargs)
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self._layer = utilities.PLAYER_LAYER2

    def flip(self):
        """
        Flips the image and puts it on the layer behind the player if the image is flipped as to not move the weapon
        between hands
        """
        self.flipped = not self.flipped
        self.image = pygame.transform.flip(self.image, True, False)
        if self.flipped:
            super().groups()[0].change_layer(self,utilities.PLAYER_LAYER1)
        else:
            super().groups()[0].change_layer(self,utilities.PLAYER_LAYER2)

class LeftArm(GenericArm):
    def __init__(self, pos, **kwargs):
        GenericArm.__init__(self, pos, **kwargs)
        self._layer = utilities.PLAYER_LAYER2
        self.visible = [False, False]

    def flip(self):
        """
        When the right side is shown the left arm is invisible otherwise it will be visible
        """
        self.flipped = not self.flipped
        if self.flipped:
            self.visible = [True, True]
            super().groups()[0].change_layer(self,utilities.PLAYER_LAYER2)
        else:
            self.visible = [False, False]
            super().groups()[0].change_layer(self,utilities.BOTTOM_LAYER)

    def move_arm(self, pos):
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
        self.bullet = sheets["weapons"].image_at((160,0), size = (32,16), color_key = (255,255,255))

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
        if self.attack_cooldown > 0:
            self.attack_cooldown -= utilities.GAME_TIME.get_time() / 1000
            return
        bullet_image = pygame.transform.scale(self.bullet, (20,20))
        self.projectiles.append(entities.PlayerProjectile(self.rect.center, pygame.mouse.get_pos(), super().groups()[0],
                            tiles = tiles, damage = self.weapon.damage, speed = 20, accuracy = self.weapon.accuracy,
                            image = self.bullet))
        self.attack_cooldown = 1 / self.weapon.fire_rate

    def rotate(self):
        """
        Rotate an image and calculate a new position based on a offset and an angle.
        """
        self.image = pygame.transform.rotozoom(self.orig_image, - self.angle, 1)
        offset_rotated = self.offset.rotate(self.angle)
        #weapon offset rotated
        if not self.flipped:
            self.rect = self.image.get_rect(center=self.rect.center + offset_rotated)
        elif self.flipped:
            self.rect = self.image.get_rect(center=self.rect.center - offset_rotated)
        #ensure the bounding box is synced with the image location
        self.bounding_box = self.rect

    def flip(self):
        super().flip()
        self.orig_image = pygame.transform.flip(self.orig_image, True, False)

    def equip(self, weapon):
        """
        Equip a weapon
        :param weapon: an instance of a AbstractWeapon class or further
        """
        self.weapon = weapon
        weapon_image = self.weapon.image
        # weapon_image = pygame.transform.rotate(weapon_image, 90)
        # weapon_image = pygame.transform.flip(weapon_image, True, False)
        image = pygame.Surface((weapon_image.get_rect().width, weapon_image.get_rect().height))
        ir = image.get_rect()
        image.fill((255,255,255))

        image.blit(weapon_image, (0, image.get_rect().height - weapon_image.get_rect().height), weapon_image.get_rect())
        image = pygame.transform.scale(image, (round(0.8*image.get_rect().width), round(0.8*image.get_rect().height)))
        rotated_arm = pygame.transform.rotate(self.arm, 40)
        image.blit(rotated_arm,(25,20), rotated_arm.get_rect())
        image.set_colorkey((255,255,255), pygame.RLEACCEL)
        image = image.convert_alpha()
        self.image = image#self.__create_weapon_arm(weapon_image)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center = self.rect.center)
        self.damage = weapon.damage

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