import pygame, utilities

class MenuPane(pygame.sprite.Sprite):
    def __init__(self, rect_size, image, *groups, name = None):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = pygame.transform.scale(image, (rect_size[2],rect_size[3]))
        self.rect = self.image.get_rect(center = (rect_size[0], rect_size[1]))
        self.name = name
        self.widgets = []
        self.events = []

class Widget(pygame.sprite.Sprite):
    def __init__(self,text = "", image = None):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.font = pygame.font.Font(None, 30)
        print(pygame.font.get_fonts())
        if not image:
            self.image = pygame.Surface()
        else:
            self.image = image


