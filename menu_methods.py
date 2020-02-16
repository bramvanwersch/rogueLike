import pygame, utilities
from pygame.locals import *

class MenuPane(pygame.sprite.Sprite):
    def __init__(self, rect_size, image, *groups, title = None):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.menu_group = groups[0]
        self.image = pygame.transform.scale(image, (rect_size[2],rect_size[3]))
        self.rect = self.image.get_rect(center = (rect_size[0], rect_size[1]))
        self.widgets = []
        #index of selected widget in the widgets list
        self.selected_widget = 0
        self.events = []
        self._layer = utilities.BOTTOM_LAYER
        if title:
            self.__set_title(title)

    def __set_title(self, title):
        """
        Sets a title at the top of the menupane
        :param title: the text to be displayed as title
        """
        font = pygame.font.Font(utilities.DATA_DIR + "//Menu//font//manaspc.ttf", 30)
        title = font.render(title, True, (0,0,0))
        tr = title.get_rect()
        self.image.blit(title, (int(0.5 * self.rect.width - 0.5 * tr.width),10))

    def update(self, *args):
        x,y = pygame.mouse.get_pos()
        selected_widget_events = []
        for event in self.events:
            if event.type == MOUSEBUTTONDOWN:
                for widget in self.widgets:
                    if widget.rect.collidepoint(x,y):
                        widget.action([event])
                        break;
            if event.type == KEYDOWN:
                # if event.key == K_a or event.key == K_LEFT:
                #     self.pressed_backwad = True
                # if event.key == K_d or event.key == K_RIGHT:
                #     self.pressed_forward = True
                if event.key == K_w or event.key == K_UP:
                    self.__change_selectd_widget()
                elif event.key == K_s or event.key == K_DOWN:
                    self.__change_selectd_widget(False)
                else:
                    selected_widget_events.append(event)
        if self.widgets:
            self.widgets[self.selected_widget].action(selected_widget_events)

    def __change_selectd_widget(self, up = True):
        self.widgets[self.selected_widget].set_selected(False)
        if up:
            if self.selected_widget <= 0:
                self.selected_widget = len(self.widgets) - 1
            else:
                self.selected_widget -= 1
        else:
            if self.selected_widget >= len(self.widgets) -1:
                self.selected_widget = 0
            else:
                self.selected_widget += 1
        self.widgets[self.selected_widget].set_selected(True)

    def add_widget(self, pos, widget):
        widget.add(self.menu_group)
        widget.set_pos(self.__get_relative_postion(pos), center = True)
        self.widgets.append(widget)
        self.widgets.sort(key = lambda x: x.rect.y)

    def __get_relative_postion(self, pos):
        moved_pos = [*pos]
        if pos[0] == "center" or pos[0] == "c":
            moved_pos[0] = self.rect.x + int(self.rect.width / 2)
        else:
            moved_pos[0] += self.rect.x
        if pos[1] == "center" or pos[1] == "c":
            moved_pos[1] = self.rect.y + int(self.rect.height / 2)
        else:
            moved_pos[1] += self.rect.y
        return moved_pos

class Widget(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 30)
        self.action_function = None

    def action(self, e):
        pass

class Button(Widget):
    def __init__(self,pos = (0,0), text = "", text_color = (0,0,0), background_color = (165,103,10), highlight_color = (252, 151, 0)):
        Widget.__init__(self, pos)
        #create a selected and unselected image to swich between
        text = self.font.render(text, True, text_color, background_color)
        unselected_surface = pygame.Surface((text.get_rect().width + 14, text.get_rect().height + 14))
        unselected_surface.fill(background_color)
        self.rect = unselected_surface.blit(text, (text.get_rect().x + 7, text.get_rect().y + 7))
        self.unselected_image = unselected_surface

        selected_surface = unselected_surface.copy()
        pygame.draw.rect(selected_surface,(0,0,0), selected_surface.get_rect(), 3)
        self.selected_image = selected_surface

        self.image = self.unselected_image
        self.text = text
        self.rect = self.image.get_rect(topleft = pos)
        self.selected = False

    def set_pos(self, pos, center = False):
        if center:
            self.rect.center = pos
        else:
            self.rect.topleft = pos

    def set_action(self, action_function):
        self.action_function = action_function

    def set_selected(self, selected):
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.unselected_image

    def action(self, events):
        for e in events:
            if e.type == MOUSEBUTTONDOWN:
                self.action_function()
            elif e.key == K_RETURN:
                self.action_function()

