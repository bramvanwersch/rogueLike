import pygame, random
import entities, utilities


class Chest(entities.InteractingEntity):
    def __init__(self, pos, player,loot, *groups):
        image = pygame.transform.scale(utilities.load_image("chest.bmp", (255,255,255)), (80,80))
        entities.InteractingEntity.__init__(self, image, pos, player, *groups)
        self.open = pygame.transform.scale(utilities.load_image("chest_open.bmp", (255,255,255)), (80,80))
        self._layer = utilities.MIDDLE_LAYER
        self.loot = loot[0]
        self.looted = False

    def interact(self):
        if not self.looted:
            self.image = self.open
            #make it work for multiple items.
            LootableWeapon(self.rect.center, self.player, self.loot, self.groups())
            self.looted = True

class LootableWeapon(entities.InteractingEntity):
    def __init__(self, pos, player, weapon, *groups):
        self.weapon = weapon
        entities.InteractingEntity.__init__(self, self.weapon.image, pos, player, *groups)
        self.rect = self.weapon.image.get_rect(center = pos)
        self.orig_rect = self.rect
        self.xchange = random.randint(-30,30)
        print(self.xchange)
        self._layer = utilities.PLAYER_LAYER1
        #amount of frames to wait before you can pickup the weapon ensuring it is not immediatly in youre hand
        self.cooldown_timer = 30
        self.lootable = False

    def update(self, *args):
        super().update(*args)
        if not self.lootable:
            #vertex = a(x+b)**2 -c --> (-b,c)
            y_offset = 0.44 * ((self.cooldown_timer - 15) ** 2) - 100
            x_offset = self.xchange - (self.xchange - self.cooldown_timer)
            self.rect = self.orig_rect.move(x_offset,y_offset)
            self.cooldown_timer -= 1
            if self.cooldown_timer == 0:
                self.lootable = True

    def interact(self):
        #TODO make sure that the weapon is garbage collected
        if self.lootable:
            self.player.right_arm.equip(self.weapon)
            self.kill()

