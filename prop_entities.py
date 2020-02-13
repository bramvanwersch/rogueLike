import pygame
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
        self._layer = utilities.PLAYER_LAYER1

    def interact(self):
        self.player.right_arm.equip(self.weapon)
        self.kill()

