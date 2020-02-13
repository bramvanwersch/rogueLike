import pygame
import entities


class Chest(entities.InteractingEntity):
    def __init__(self, pos, player, *groups):
        image = pygame.transform.scale(utilities.load_image("chest.bmp", (255,255,255)), (80,80))
        entities.InteractingEntity.__init__(self, image, pos, player, *groups)
        self.open = pygame.transform.scale(utilities.load_image("chest_open.bmp", (255,255,255)), (80,80))

    def interact(self):
        pass