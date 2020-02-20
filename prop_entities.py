import pygame, random
import entities, utilities


class Chest(entities.InteractingEntity):
    def __init__(self, pos, player, loot, *groups):
        image = pygame.transform.scale(utilities.load_image("chest.bmp", (255,255,255)), (80,80))
        entities.InteractingEntity.__init__(self, pos, player, *groups, image = image)
        self.open_image = pygame.transform.scale(utilities.load_image("chest_open.bmp", (255,255,255)), (80,80))
        self._layer = utilities.MIDDLE_LAYER
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

    def interact(self):
        if not self.open:
            self.image = self.open_image
            self.open = True

    def __spawn_weapon(self):
        loot = self.loot.pop(-1)
        LootableWeapon(self.rect.center, self.player, loot, self.groups())

class LootableWeapon(entities.InteractingEntity):
    def __init__(self, pos, player, weapon, *groups):
        self.weapon = weapon
        entities.InteractingEntity.__init__(self, pos, player, *groups, image = self.weapon.image)
        self.rect = self.weapon.image.get_rect(center = pos)
        self.orig_rect = self.rect
        self.xchange = random.randint(-16,16) / 10
        self.ychange = random.randint(-16, 16)
        self._layer = utilities.PLAYER_LAYER1
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

    def interact(self):
        if self.lootable:
            self.player.inventory.add(self.weapon)
            self.kill()

