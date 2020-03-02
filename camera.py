import pygame
from pygame import *
import player_methods
from utilities import SCREEN_SIZE

# thanks to https://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame
class CameraAwareLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self, target, world_size):
        """
        Class that allows a so called camera to follow the player when he moves across the map. It stops at the borders
        :param target: the target to center the camera around
        :param world_size: the size of the level in which the target is moving
        """
        super().__init__()
        self.target = target
        self.cam = pygame.Vector2(0, 0)
        self.world_size = world_size
        if self.target:
            self.add(target)

    def update(self, *args):
        super().update(*args)
        if self.target:
            x = -self.target.rect.center[0] + SCREEN_SIZE.width/2
            y = -self.target.rect.center[1] + SCREEN_SIZE.height/2
            self.cam += (pygame.Vector2((x, y)) - self.cam) #* 0.1 # provides slowly following camera
            self.cam.x = max(-(self.world_size.width-SCREEN_SIZE.width), min(0, self.cam.x)) # stop mving at the side of the board
            self.cam.y = max(-(self.world_size.height-SCREEN_SIZE.height + 150), min(0, self.cam.y))

    def draw(self, surface):
        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            if not spr.visible[0]:
                continue
            rec = spritedict[spr]
            newrect = surface_blit(spr.image, spr.rect.move(self.cam))
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty