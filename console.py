import pygame
import utilities
from pygame.locals import *

class Console:
    def __init__(self,rect):
        background_image = pygame.Surface(rect.size)
        background_image.fill((48, 48, 48))
        self.image = background_image
        self.rect = rect
        self.events = []
        self.text_log = []
        self.text = ">"
        self.font20 = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20)

    def update(self):
        for event in self.events:
            if event.type == KEYDOWN:
                text_key = pygame.key.name(event.key)
                if len(text_key) == 1:
                    self.text += text_key
                if event.key == K_RETURN:
                    self.text_log.append(self.text)
                    self.text = ">"
        self.image = pygame.Surface(self.rect.size)
        self.image.fill((48, 48, 48))
        text = self.font20.render(self.text, False, (0,255,0))
        self.image.blit(text, (10, self.rect.height - text.get_size()[1]))
        for i, line in enumerate(reversed(self.text_log)):
            if self.rect.height - text.get_size()[1] * (i + 2) < 0:
                break
            text = self.font20.render(line, False, (0,255,0))
            self.image.blit(text, (10, self.rect.height - text.get_size()[1] * (i + 2)))




