import pygame, utilities

class MenuPane(pygame.sprite.Sprite):
    def __init__(self, rect_size, image, *groups, name = None):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.menu_group = groups[0]
        self.image = pygame.transform.scale(image, (rect_size[2],rect_size[3]))
        self.rect = self.image.get_rect(center = (rect_size[0], rect_size[1]))
        self.name = name
        self.widgets = []
        self.events = []

    def add_widget(self, pos, widget):
        widget.add(self.menu_group)
        widget.set_pos(self.__get_relative_postion(pos))
        self.widgets.append(widget)

    def __get_relative_postion(self, pos):
        moved_pos = [*pos]
        moved_pos[0] += self.rect.x
        moved_pos[1] += self.rect.y
        return moved_pos

class Widget(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.font = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 30)


class Button(Widget):
    def __init__(self,pos = (0,0), text = "", text_color = (0,0,0), background_color = (165,103,10), *groups):
        Widget.__init__(self, pos, *groups)
        self.image = self.font.render(text, True, text_color, background_color)
        self.text = text
        self.rect = self.image.get_rect(topleft = pos)

    def set_pos(self, pos):
        self.rect.topleft = pos


