import pygame, utilities
from pygame.locals import *

BACKGROUND_COLOR = (165,103,10)

class Widget(pygame.sprite.Sprite):
    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.font30 = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 30)
        self.font25 = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 25)
        self.font20 = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20)
        self.action_function = None
        self.selectable = False

    def action(self, e):
        pass

    def set_pos(self, pos, center = False):
        if center:
            self.rect.center = pos
        else:
            self.rect.topleft = pos

class MenuPane(Widget):
    def __init__(self, rect, image, *groups, title = None, **kwargs):
        Widget.__init__(self, *groups, **kwargs)
        self.menu_group = groups[0]
        self.image = pygame.transform.scale(image, (rect[2], rect[3]))
        self.rect = self.image.get_rect(center = (rect[0], rect[1]))
        self.widgets = []
        #index of selected widget in the widgets list
        self.selectable_widgets = []
        self.selected_widget = 0
        self.events = []
        self._layer = utilities.BOTTOM_LAYER
        if title:
            self._set_title(title)

    def _set_title(self, title, font = 30):
        """
        Sets a title at the top of the menupane
        :param title: the text to be displayed as title
        """
        if font == 30:
            title = self.font30.render(title, True, (0,0,0))
        elif font == 25:
            title = self.font20.render(title, True, (0,0,0))
        elif font == 20:
            title = self.font10.render(title, True, (0,0,0))
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
                    self._change_selected_widget()
                elif event.key == K_s or event.key == K_DOWN:
                    self._change_selected_widget(False)
                else:
                    selected_widget_events.append(event)
        if self.selectable_widgets:
            self.widgets[self.selected_widget].action(selected_widget_events)
        #activate the widgets that are also menu panes or inheriting from
        for widget in self.widgets:
            if isinstance(widget, MenuPane):
                widget.events = self.events

    def _change_selected_widget(self, up = True):
        if not self.selectable_widgets: return
        self.selectable_widgets[self.selected_widget].set_selected(False)
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
        self.selectable_widgets[self.selected_widget].set_selected(True)

    def add_widget(self, pos, widget, center = True):
        widget.add(self.menu_group)
        widget.set_pos(self._get_relative_postion(pos), center = center)
        self.widgets.append(widget)
        if widget.selectable:
            self.selectable_widgets.append(widget)
            self.selectable_widgets.sort(key = lambda x: x.rect.y)

    def _get_relative_postion(self, pos):
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

class Button(Widget):
    def __init__(self, text = "", text_color = (0,0,0), highlight_color = (252, 151, 0)):
        Widget.__init__(self)
        #create a selected and unselected image to swich between
        text = self.font30.render(text, True, text_color, BACKGROUND_COLOR)
        unselected_surface = pygame.Surface((text.get_rect().width + 14, text.get_rect().height + 14))
        unselected_surface.fill(BACKGROUND_COLOR)
        self.rect = unselected_surface.blit(text, (text.get_rect().x + 7, text.get_rect().y + 7))
        self.unselected_image = unselected_surface

        selected_surface = unselected_surface.copy()
        pygame.draw.rect(selected_surface,(0,0,0), selected_surface.get_rect(), 3)
        self.selected_image = selected_surface

        self.image = self.unselected_image
        self.text = text
        self.selectable = True
        self.selected = False

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

class ListDisplay(MenuPane):
    def __init__(self, size, inventory, *groups, title = None):
        image = pygame.Surface(size)
        pygame.draw.rect(image,(0,0,0), image.get_rect(),3)
        MenuPane.__init__(self, (0,0,*size), image, *groups)
        self.inventory = inventory
        self.items = inventory.items.copy()
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(BACKGROUND_COLOR)
        if title:
            pygame.draw.rect(self.image, (0, 0, 0), (0, 30, self.rect.width, self.rect.height - 30), 8)
            self._set_title(title, 25)
            self.title = True
        else:
            pygame.draw.rect(self.image,(0,0,0), (0, 0, *self.rect.size),8)
            self.title = False

    def update(self, *args):
        super().update(*args)
        if self.items != self.inventory.items:
            print("")
            self.items = self.inventory.items.copy()
            self.__make_list_display()

    def __make_list_display(self):
        self.widgets = []
        self.selectable_widgets = []
        offset = 0
        if self.title:
            offset = 70
        for i, item in enumerate(self.items):
            size = (self.rect.width - 20, 60)
            #reverse size because image will be flipped before placing in the label
            lbl = SelectableLabel(item.image, size)
            self.add_widget(("c", offset + i*60), lbl)

class SelectableLabel(Widget):
    def __init__(self, image, size, Border = True):
        Widget.__init__(self)
        self.selectable = True
        self.image, self.selected_image = self.__make_images(image, size)
        self.unselected_image = self.image
        self.rect = pygame.Rect(0,0,*size)

    def set_selected(self, selected):
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.unselected_image

    def __make_images(self, image, size):
        image = pygame.transform.flip(pygame.transform.rotate(image, 90), True, False)
        image = pygame.transform.scale(image, (int(1.5* image.get_rect().width),int(1.5* image.get_rect().height)))

        img = pygame.Surface(size)
        img.fill(BACKGROUND_COLOR)
        ir = image.get_rect()

        #get topleft x and y coordiante that give a centered image
        tlx = int((size[0] - ir.width) / 2)
        tly = int((size[1] - ir.height) / 2)

        img.blit(image,(tlx,tly))
        imgsel = img.copy()
        pygame.draw.rect(imgsel, (0, 0, 0), (0, 0, *imgsel.get_rect().size), 5)
        return img, imgsel
