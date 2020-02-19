import pygame, random, math
import numpy as np
from pygame.locals import *
import entities, utilities, weapon, constants
from constants import *
from entities import LivingEntity

class Player(LivingEntity):
    def __init__(self, pos, start_weapon, *groups):
        idle_image = pygame.transform.scale(utilities.load_image("player.bmp", (255, 255, 255)), (60,120))
        LivingEntity.__init__(self, idle_image, pos,damage=5)
        self.walking_animation = utilities.Animation("player_walk0.bmp","player_walk1.bmp","player_walk2.bmp","player_walk1.bmp",
                                                     "player_walk0.bmp","player_walk3.bmp","player_walk4.bmp","player_walk3.bmp",
                                                     scale = (60,120))
        self.idle_animation = utilities.MarkedAnimation("player_idle1.bmp","player_idle2.bmp","player_idle3.bmp","player_idle4.bmp",
                                                        "player_idle4.bmp","player_idle3.bmp","player_idle2.bmp","player_idle1.bmp",
                                                        scale = (60,120), speed = 40, marked_frames=[2,3,4,5])
        self.dead_animation = utilities.MarkedAnimation("player_idle1.bmp","player_dead2.bmp","player_dead3.bmp",
                                                        "player_dead4.bmp","player_dead5.bmp","player_dead6.bmp",
                                                        "player_dead7.bmp","player_dead8.bmp","player_dead9.bmp",
                                                        "player_dead10.bmp","player_dead11.bmp",
                                                        scale = (60,120), speed = [15,15,15,15,15,15,15,15,15,15,100],
                                                        marked_frames=[3,4,5,6,7,8,9,10])
        self.events = []
        self.inventory = Inventory()
        self._layer = utilities.PLAYER_LAYER2
        self.inventory.add(start_weapon)
        self.right_arm = RightArm((self.rect.centerx - 8, self.rect.centery - 8))
        self.equip(start_weapon)
        self.left_arm = LeftArm((self.rect.centerx - 8, self.rect.centery - 8))
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
             K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z]
        self.pressed_keys = {key : False for key in l}

    def _get_bounding_box(self):
        """
        Create a bounding box smaller then the player for collission checking with objects in the surroundings
        :return: a pygame.Rect object that is smaller then the self.rect object with the same bottom value and a
        new centered x value.
        """
        bb = self.rect.inflate((-self.rect.width * 0.2, - self.rect.height * 0.4))
        bb.center = (bb.centerx, bb.centery + bb.top - self.rect.top)
        return bb

    def update(self, *args):
        """
        Processes user input to make the player do actions.
        """
        super().update(*args)
        if self.dead:
            return
        self.handle_user_input()
        if self.flipped:
            self.right_arm.move_arm((self.rect.centerx - 5, self.rect.centery))
            self.left_arm.move_arm((self.rect.centerx - 5, self.rect.centery +14))
        elif not self.flipped:
            self.right_arm.move_arm((self.rect.centerx + 2, self.rect.centery + 2))
        self.animations()

    def handle_user_input(self):
        for event in self.events:
            if event.type == KEYDOWN:
                self.pressed_keys[event.key] = True
            elif event.type == KEYUP:
                self.pressed_keys[event.key] = False

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
        if self.pressed_keys[A_LEFT]:
            if not self.flipped:
                self.flipped = not self.flipped
            if not self.right_arm.attacking:
                self.right_arm.do_attack()
        if self.pressed_keys[A_RIGHT]:
            if self.flipped:
                self.flipped = not self.flipped
            if not self.right_arm.attacking:
                self.right_arm.do_attack()

    def do_flip(self):
        if self.flipped:
            self.image = self.flipped_image
        else:
            self.image = self.orig_image
        if self.right_arm.flipped != self.flipped:
            self.right_arm.flip()
            self.left_arm.flip()

    def die(self):
        self.dead_animation.update()
        if self.dead_animation.marked:
            self.right_arm.visible = [False, False]
            self.left_arm.visible = [False, False]
        self._change_image(self.dead_animation.image)

    def animations(self):
        if self.right_arm.attacking:
            self.idle_animation.cycles += 1
        if int(self.speedx) != 0 or int(self.speedy) != 0:
            self.walking_animation.update()
            self._change_image(self.walking_animation.image)
            self.idle_animation.cycles += 1
        else:
            #idle animation plays at random every 500 frames of inactivity
            self.walking_animation.reset()
            if self.idle_animation.cycles == 0:
                self.idle_animation.update()
                if self.idle_animation.marked:
                    self.right_arm.visible = [False, True]
                    self.left_arm.visible = [False, self.left_arm.visible[1]]
                self._change_image(self.idle_animation.image)
            elif random.randint(1, 500) == 1:
                self.idle_animation.reset()
            else:
                self._change_image([self.image, self.flipped_image])

    def equip(self, weapon):
        """
        Things to do when the player equips a new weapon
        :param weapon:
        :return:
        """
        self.right_arm.equip(weapon)
        self.speed = 10 *(1- self.right_arm.weapon.weight / 250)
        self.inventory.equiped = weapon

class GenericArm(entities.Entity):
    def __init__(self, pos):
        self.arm = pygame.transform.scale(utilities.load_image("player_arm.bmp"), (15,30))
        entities.Entity.__init__(self, self.arm, pos)
        self._layer = utilities.PLAYER_LAYER2
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.offset = pygame.Vector2(int(self.rect.width * 0.5) -10, int(self.rect.height * 0.5)- 2)
        self.offset2 = pygame.Vector2(int(self.rect.width * 0.5) - 10, int(self.rect.height * 0.5) - 35)

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
    def __init__(self, pos):
        GenericArm.__init__(self, pos)
        self._layer = utilities.PLAYER_LAYER2
        self.visible = [False, False]

    def flip(self):
        """
        When the right side is shown the left arm is invisible otherwise it will be visible
        :return:
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
    def __init__(self, pos):
        GenericArm.__init__(self, pos)
        self.attacking = False
        #for tracking the original image when rotating
        self.orig_image = self.image
        self.angle = 0
        #dont touch the numbers they are great and just work
        self.offset = pygame.Vector2(int(self.rect.width * 0.5) -10, int(self.rect.height * 0.5)- 2)
        self.offset2 = pygame.Vector2(int(self.rect.width * 0.5) - 10, int(self.rect.height * 0.5) - 35)
        #tracks the number of attacks and helps enemies track damage
        self.attack_cycle = 0
        self.attack_cooldown = 0

    def move_arm(self, pos):
        """
        They player class tells where to put the arm relative to the player. Then the arm is rotated based on the
        current angle. This method is called every update from the player class.
        :param pos: position to move the arm to.
        :return:
        """
        self.rect.center = pos
        if self.attacking:
            self.angle -= 10
            if self.angle < -30:
                self.attacking = False
                self.angle = 0
        self.rotate()
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1 / utilities.GAME_TIME.get_fps()

    def __get_angle_reduction(self):
        """
        Calculate the amount of distance a sword needs to move based on fps and attack speed when a player is attacking
        :return: a float representing the amount of degrees the arm has tot travel this frame
        """
        fps = utilities.GAME_TIME.get_fps()
        #amount degrees to be moved this second
        to_move = 180 * self.weapon.fire_rate
        return to_move / fps

    def do_attack(self):
        if self.attack_cooldown > 0:
            return
        self.attacking = True
        self.angle = 150
        self.attack_cycle += 1
        self.attack_cooldown = 1 / self.weapon.fire_rate

    def rotate(self):
        """
        Rotate an image and calculate a new position based on a offset and an angle.
        """
        if not self.flipped:
            if self.angle !=  0:
                self.image = pygame.transform.rotozoom(self.orig_image, self.angle, 1)
            else:
                self.image = self.orig_image
            offset_rotated = self.offset.rotate( - self.angle)
            self.rect = self.image.get_rect(center=self.rect.center + offset_rotated)
        elif self.flipped:
            if self.angle > 0:
                self.image = pygame.transform.rotozoom(self.orig_image, - self.angle, 1)
            else:
                self.image = self.orig_image
            offset_rotated2 = self.offset2.rotate(self.angle)
            self.rect = self.image.get_rect(center=self.rect.center - offset_rotated2)
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
        weapon_image = pygame.transform.rotate(weapon_image, 90)
        weapon_image = pygame.transform.flip(weapon_image, True, False)
        self.image = self.__create_weapon_arm(weapon_image)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center = self.rect.center)
        self.offset = pygame.Vector2(int(self.rect.width * 0.5) -10, int(self.rect.height * 0.5)- 2)
        self.offset2 = pygame.Vector2(int(self.rect.width * 0.5) - 10, int(self.rect.height * 0.5) - 35)
        self.damage = weapon.damage

    def __create_weapon_arm(self, weapon_image):
        """
        Combines the arm picture together with the weapon that is being equiped.
        :param weapon_image: image of the weapon that has to be equiped
        :return: a pygame surface containing the combination of an arm and the weapon
        """
        pygame.surfarray.use_arraytype("numpy")
        # the weapon parts as an array numpy matrixes containing pixels
        partspixels = [pygame.surfarray.pixels3d(image) for image in (weapon_image, self.arm)]
        # widest component is the guard
        width = partspixels[0].shape[0] + 5
        lenght = partspixels[1].shape[1] + 9
        # make final pixel array consisting of width lenght and 3 for rgb values
        final_arr = np.full((width, lenght, 3), [255,255,255])
        trl = 0
        final_arr[:-5,lenght - 28: lenght] = partspixels[0]
        final_arr[5:partspixels[1].shape[0] +5,: -9] = partspixels[1]
        image = pygame.surfarray.make_surface(final_arr)

        image.set_colorkey((255, 255, 255), RLEACCEL)
        image = image.convert_alpha()
        if self.flipped: image = pygame.transform.flip(image, True, False)
        return image

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