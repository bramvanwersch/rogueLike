import pygame, random, math
import numpy as np
from pygame.locals import *
import entities, utilities, weapon
from entities import LivingEntity

class Player(LivingEntity):
    def __init__(self, pos, *groups):
        self.idle_image = pygame.transform.scale(utilities.load_image("player.bmp", (255, 255, 255)), (60,120))
        LivingEntity.__init__(self, self.idle_image, pos, health_regen=100)
        self.walking_animation = utilities.Animation("player_walk0.bmp","player_walk1.bmp","player_walk2.bmp","player_walk1.bmp",
                                                     "player_walk0.bmp","player_walk3.bmp","player_walk4.bmp","player_walk3.bmp",
                                                     scale = (60,120))
        self.idle_animation = utilities.MarkedAnimation("player_idle1.bmp","player_idle2.bmp","player_idle3.bmp","player_idle4.bmp",
                                                  "player_idle4.bmp","player_idle3.bmp","player_idle2.bmp","player_idle1.bmp",
                                                  scale = (60,120), speed = 40, marked_frames=[3,4,5,6])
        self.events = []
        self.inventory = Inventory()
        self._layer = utilities.PLAYER_LAYER2
        start_weapon = weapon.AbstractWeapon(utilities.load_image("starter_stick.bmp"))
        self.right_arm = RightArm(start_weapon, (self.rect.centerx - 8, self.rect.centery - 8))
        self.left_arm = LeftArm((self.rect.centerx - 8, self.rect.centery - 8))
        self.pressed_up, self.pressed_down, self.pressed_forward, self.pressed_backwad = False, False, False, False

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
                if event.key == K_k:
                    if not self.right_arm.attacking:
                        self.right_arm.do_attack()
                if event.key == K_a or event.key == K_LEFT:
                    self.pressed_backwad = True
                if event.key == K_d or event.key == K_RIGHT:
                    self.pressed_forward = True
                if event.key == K_w or event.key == K_UP:
                    self.pressed_up = True
                if event.key == K_s or event.key == K_DOWN:
                    self.pressed_down = True

            elif event.type == KEYUP:
                if event.key == K_a or event.key == K_LEFT:
                    self.pressed_backwad = False
                if event.key == K_d or event.key == K_RIGHT:
                    self.pressed_forward = False
                if event.key == K_w or event.key == K_UP:
                    self.pressed_up = False
                if event.key == K_s or event.key == K_DOWN:
                    self.pressed_down = False
        if self.pressed_forward and self.pressed_backwad:
            self.speedx = 0
        else:
            if self.pressed_forward:
                self.speedx += 0.1 * self.max_speed
            if self.pressed_backwad:
                self.speedx -= 0.1 * self.max_speed
            if not self.pressed_backwad and not self.pressed_forward:
                self.speedx *= 0.1
        if self.pressed_down and self.pressed_up:
            self.speedy = 0
        else:
            if self.pressed_up:
                self.speedy -= 0.1 * self.max_speed
            if self.pressed_down:
                self.speedy += 0.1 * self.max_speed
            if not self.pressed_up and not self.pressed_down:
                self.speedy *= 0.1

    def do_flip(self):
        orig_flip = self.flipped
        super().do_flip()
        if orig_flip != self.flipped:
            self.right_arm.flip()
            self.left_arm.flip()

    def animations(self):
        if self.right_arm.attacking:
            self.idle_animation.reset()
        if int(self.speedx) != 0 or int(self.speedy) != 0:
            self.walking_animation.update()
            self._change_image(self.walking_animation.image)
            self.idle_animation.reset()
        else:
            #idle animation plays at random every 500 frames of inactivity
            self.walking_animation.reset()
            if self.idle_animation.cycles == 0:
                self.idle_animation.update()
                if self.idle_animation.marked:
                    self.right_arm.visible = False
                    self.left_arm.visible = False
                else:
                    self.right_arm.visible = True
                    self.left_arm.visible = True
                self._change_image(self.idle_animation.image)
            elif random.randint(1, 500) == 1:
                self.idle_animation.reset()
            else:
                self._change_image(self.idle_image)

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
        self._layer = utilities.BOTTOM_LAYER

    def flip(self):
        """
        When the right side is shown the left arm is invisible otherwise it will be visible
        :return:
        """
        self.flipped = not self.flipped
        if self.flipped:
            self.visible = True
            super().groups()[0].change_layer(self,utilities.PLAYER_LAYER2)
        else:
            self.visible = False
            super().groups()[0].change_layer(self,utilities.BOTTOM_LAYER)


    def move_arm(self, pos):
        self.rect.center = pos

class RightArm(GenericArm):
    def __init__(self, weapon, pos):
        GenericArm.__init__(self, pos)
        self.equip(weapon)
        self.attacking = False
        #for tracking the original image when rotating
        self.orig_image = self.image
        self.angle = 0
        #dont touch the numbers they are great and just work
        self.offset = pygame.Vector2(int(self.rect.width * 0.5) -10, int(self.rect.height * 0.5)- 2)
        self.offset2 = pygame.Vector2(int(self.rect.width * 0.5) - 10, int(self.rect.height * 0.5) - 35)


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

    def do_attack(self):
        self.attacking = True
        self.angle = 150

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

    def flip(self):
        super().flip()
        self.orig_image = pygame.transform.flip(self.orig_image, True, False)

    def equip(self, weapon):
        """
        Equip a weapon
        :param weapon: an instance of a AbstractWeapon class or further
        """
        self.weapon = weapon
        weapon_image = pygame.transform.scale(self.weapon.image, (int(self.weapon.image.get_rect().width * 0.7),
                                                                  int(self.weapon.image.get_rect().height * 0.8)))
        weapon_image = pygame.transform.rotate(weapon_image, 90)
        weapon_image = pygame.transform.flip(weapon_image, True, False)
        self.image = self.__create_weapon_arm(weapon_image)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center = self.rect.center)
        self.offset = pygame.Vector2(int(self.rect.width * 0.5) -10, int(self.rect.height * 0.5)- 2)
        self.offset2 = pygame.Vector2(int(self.rect.width * 0.5) - 10, int(self.rect.height * 0.5) - 35)

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
        pass