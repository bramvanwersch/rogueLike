import pygame, random

import constants
from game_images import sheets
import entities, utilities


class Chest(entities.InteractingEntity):
    def __init__(self, pos, player, loot, *groups):
        image = sheets["forest"].image_at((0,80), scale = (80,80), color_key = (255,255,255))
        def action():
            if not self.open:
                self.image = self.open_image
                self.open = True
        entities.InteractingEntity.__init__(self, pos, player, *groups, image = image, action = action)
        self.open_image = sheets["forest"].image_at((16,80), scale = (80,80), color_key = (255,255,255))
        self._layer = constants.MIDDLE_LAYER
        #list of loot in a chest
        self.loot = loot
        self.cooldown = 0
        self.open = False

    def update(self, *args):
        """
        Spew out weapons until the loot is empty
        :param args:
        :return:
        """
        super().update(*args)
        if self.open and len(self.loot) and self.cooldown == 0:
            self.__spawn_weapon()
            self.cooldown = 30
        elif self.cooldown > 0:
            self.cooldown -= 1

    def __spawn_weapon(self):
        loot = self.loot.pop(-1)
        LootableWeapon(self.rect.center, self.player, loot, self.groups())

class LootableWeapon(entities.InteractingEntity):
    def __init__(self, pos, player, weapon, *groups):
        self.weapon = weapon
        def action():
            if self.lootable:
                self.player.inventory.add(self.weapon)
                self.kill()
        entities.InteractingEntity.__init__(self, pos, player, *groups, image = self.weapon.image, action = action)
        self.rect = self.weapon.image.get_rect(center = pos)
        self.orig_rect = self.rect
        self.xchange = random.randint(-16,16) / 10
        self.ychange = random.randint(-16, 16)
        self._layer = constants.PLAYER_LAYER1
        #current waiting time the time to wait.
        self.cooldown_timer = [0, 30]
        self.lootable = False

    def update(self, *args):
        super().update(*args)
        if not self.lootable:
            #vertex = a(x+b)**2 -c --> (-b,c)
            y_offset = int(0.44 * ((self.cooldown_timer[0] - 15) ** 2) - 100) + self.ychange
            x_offset = int(self.xchange * self.cooldown_timer[0])
            self.rect = self.orig_rect.move(x_offset,y_offset)
            self.cooldown_timer[0] += 1
            if self.cooldown_timer[0] == self.cooldown_timer[1]:
                self.lootable = True


