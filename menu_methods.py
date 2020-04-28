import pygame, utilities
from pygame.locals import *

import constants


class Widget(pygame.sprite.Sprite):
    def __init__(self, *groups, background_color = (165,103,10), **kwargs):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.background_color = background_color
        self.font30 = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 30)
        self.font25 = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 25)
        self.font20 = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 20)
        self.action_functions = {}
        self.selectable = False

    def action(self, e):
        """
        You can define a set of action functions linked to keys these are then executed when the widget is selected. If
        it is marked with SELECTION the action function is activated upon selection
        :param e: a list of events that passed the menu pane loop
        """
        if "SELECTION" in self.action_functions:
            self.action_functions["SELECTION"]()
        for event in e:
            if event.type in self.action_functions:
                self.action_functions[event.type]()
            if event.type == KEYDOWN:
                if event.key in self.action_functions:
                    self.action_functions[event.key]()

    def set_action(self, action_function, key):
        """
        Bind a function to a key that is called when the widget is selected. There is an optional keyword SELECTION that
        makes sure that the function is called upon selection and each frame after while the widget is selected
        :param action_function: a function defenition
        :param key: a key typically an integer representing a key as defined in pygame.locals
        """
        self.action_functions[key] = action_function

    def set_pos(self, pos, center = False):
        if center:
            self.rect.center = pos
        else:
            self.rect.topleft = pos

class MenuPane(Widget):
    def __init__(self, rect, image, *groups, title = None):
        """
        Creates a MenuPane that holds othger widgets and regulated selection of the widgets in the pane itself.
        :param rect: size of the pane
        :param image: image to be displayed on the pane
        :param groups: sprite group for this widget and widgets in this widget to be added to
        :param title: optional title
        """
        Widget.__init__(self, *groups)
        self.menu_group = groups[0]
        self.image = pygame.transform.scale(image, (rect[2], rect[3]))
        self.rect = self.image.get_rect(center = (rect[0], rect[1]))
        self.widgets = []
        #index of selected widget in the widgets list
        self.selectable_widgets = []
        self.selected_widget = 0
        self.events = []
        self._layer = constants.BOTTOM_LAYER
        if title:
            self._set_title(title)

    def _set_title(self, title, font = 30):
        """
        Sets a title at the top of the menupane
        :param title: the current_line to be displayed as title
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
        text = self.font30.render(text, True, text_color, self.background_color)
        unselected_surface = pygame.Surface((text.get_rect().width + 14, text.get_rect().height + 14))
        unselected_surface.fill(self.background_color)
        self.rect = unselected_surface.blit(text, (text.get_rect().x + 7, text.get_rect().y + 7))
        self.unselected_image = unselected_surface

        selected_surface = unselected_surface.copy()
        pygame.draw.rect(selected_surface,(0,0,0), selected_surface.get_rect(), 3)
        self.selected_image = selected_surface

        self.image = self.unselected_image
        self.text = text
        self.selectable = True
        self.selected = False

    def set_selected(self, selected):
        self.selected = selected
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.unselected_image

class WeaponListDisplay(MenuPane):
    def __init__(self, size, inventory, *groups, title = None):
        """
        MenuPane that is a list display of weapons the player has in his inventory
        :param size: the size of the pane for the weapons to be displayed on
        :param inventory: the inventory of the player
        :param groups: the sprite group this widget and widgets added by this widget have to be added to
        :param title: an optional title of the display.
        TODO make this more object oriented by implementing a List display class that has the basic functionality
        """
        image = pygame.Surface(size)
        pygame.draw.rect(image,(0,0,0), image.get_rect(),3)
        MenuPane.__init__(self, (0,0,*size), image, *groups)
        self.inventory = inventory
        #force an update when the sprite is updated if at creation weapons are put into the inventory
        self.items = []
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(self.background_color)
        #functions to be assigned to selectable objects made in this pane.
        self.list_functions = {}
        if title:
            pygame.draw.rect(self.image, (0, 0, 0), (0, 50, self.rect.width, self.rect.height - 50), 8)
            self._set_title(title, 30)
            self.title = True
        else:
            pygame.draw.rect(self.image,(0,0,0), (0, 0, *self.rect.size),8)
            self.title = False

    def update(self, *args):
        super().update(*args)
        if self.items != self.inventory.items:
            self.items = self.inventory.items.copy()
            self.__make_list_display()

    def __make_list_display(self):
        """
        Adds a weapon image for each weapon in the inventory including a current_line that displays some stats about the image
        """
        self.widgets = []
        self.selectable_widgets = []
        offset = 0
        if self.title:
            offset = 110
        for i, item in enumerate(self.items):
            size = (self.rect.width - 15, 100)
            #reverse size because image will be flipped before placing in the label
            lbl = WeaponItemLabel(item, size)
            self.add_widget(("c", offset + i*60), lbl)
            for key in self.list_functions:
                lbl.set_action(self.list_functions[key], key)

class Label(Widget):
    def __init__(self, size, *group, **kwargs):
        """
        Container class for holdign an image. The default is an image given by the default background color
        :param size: the size of the image. The new image has to be as big or bigger
        """
        Widget.__init__(self, *group, **kwargs)
        self.image = pygame.Surface(size)
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()

    def set_image(self, image):
        """
        change the image of the label
        :param image: pygame.Surface object
        """
        self.image = image

class SelectableLabel(Label):
    def __init__(self, image, size):
        """
        Extension of the label class that
        :param image:
        :param size:
        """
        Label.__init__(self, size)
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
        image = pygame.transform.scale(image, (int(1.4* image.get_rect().width),int(1.4* image.get_rect().height)))

        img = pygame.Surface(size)
        img.fill(self.background_color)
        ir = image.get_rect()

        #get topleft x and y coordiante that give a centered image
        tlx = int((size[0] - ir.width) / 2)
        tly = int((size[1] - ir.height) / 2)

        img.blit(image,(tlx,tly))
        img.set_colorkey((255,255,255), RLEACCEL)
        imgsel = img.copy()
        pygame.draw.rect(imgsel, (0, 0, 0), (0, 0, *imgsel.get_rect().size), 5)
        return img, imgsel

class WeaponItemLabel(SelectableLabel):
    def __init__(self, item, size, equiped = False):
        """
        Extension of the selected label class to have action functions that can take arguments
        :param item:
        :param size:
        :param equiped:
        """
        SelectableLabel.__init__(self, item.image, size)
        self.item = item
        if equiped:
            self.image.blit(self.font25.render("E",True, (0,0,0)))

    def action(self, e):
        """
        overwrite action function to have the selction function activate with an image
        """
        if "SELECTION" in self.action_functions:
            self.action_functions["SELECTION"](self.item.inventory_text)
        for event in e:
            if event.type in self.action_functions:
                self.action_functions[event.type]()
            if event.type == KEYDOWN:
                if event.key == K_e:
                    self.action_functions[event.key](self.item)
                elif event.key in self.action_functions:
                    self.action_functions[event.key]()

#methods for images that have a set location but change theire appearance over time.
#pretty much a chiller sprite
class DynamicSurface:
    def __init__(self, rect, background_color = (165,103,10), **kwargs):
        self.font18 = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 18)
        self.rect = rect
        self.background_color = background_color
        self.image = None

    def update(self):
        self.image = self._get_image()

    def _get_image(self):
        image = pygame.Surface((self.rect.size))
        image.fill(self.background_color)
        return image

class WeaponDisplay(DynamicSurface):
    def __init__(self, rect, player):
        self.player = player
        self.equiped = self.player.inventory.equiped
        self.weapon = self.equiped
        DynamicSurface.__init__(self, rect)

    def update(self):
        super().update()
        if self.player.inventory.equiped != self.equiped:
            self.equiped = self.player.inventory.equiped
            self.weapon = self.equiped

    def _get_image(self):
        image = super()._get_image()
        if self.weapon:
            ammo = self.font18.render("{} | {}".format(self.weapon.magazine, self.weapon.magazine_size) , True, (0, 0, 0))
            a_size = ammo.get_size()
            image.blit(self.weapon.image, (self.rect.width * 0.5 - self.weapon.image.get_rect().width * 0.5 ,0))
            image.blit(ammo, (self.rect.width * 0.5 - a_size[0] * 0.5, self.rect.height - a_size[1] - 10))
            if self.weapon.reloading:
                reloaded_progeress = round((1 - self.player.right_arm.reload_cooldown / self.weapon.reload_speed) * 9)
                reloading_text = self.font18.render(">" * reloaded_progeress ,True, (0,255,0))
                rts = reloading_text.get_size()
                image.blit(reloading_text,(self.rect.width * 0.5 - rts[0] * 0.5, self.rect.height - a_size[1] - rts[1] - 15))
        image = image.convert()
        return image

class ConsoleWindow(DynamicSurface):
    INNITIAL_KEY_REPEAT_SPEED = 200
    KEY_REPEAT_SPEED = 20
    def __init__(self, rect, **kwargs):
        DynamicSurface.__init__(self, rect, background_color = (75, 75, 75), **kwargs)
        self.text_log = TextLog()
        self.current_line = Line()
        self.blinker_speed = 500
        self.blinker_visible = [True, self.blinker_speed]
        self.events = []
        self.processed = True
        self.process_line = self.current_line
        self.command_tree = None
        self.pressed_keys = {key : False for key in constants.KEYBOARD_KEYS}
        self.active_keys = []
        #innitial, actual
        self.key_repeat_speed = [0,0]

    def update(self):
        super().update()
        self.blinker_visible[1] -= constants.GAME_TIME.get_time()
        if self.blinker_visible[1] <= 0:
            self.blinker_visible = [not self.blinker_visible[0], self.blinker_speed]
        for event in self.events:
            if event.type == KEYDOWN:
                self.pressed_keys[event.key] = True
                if len(event.unicode) == 1:
                    self.active_keys.append(event.unicode)
                self.key_repeat_speed = [self.INNITIAL_KEY_REPEAT_SPEED, 0]
            if event.type == KEYUP:
                self.pressed_keys[event.key] = False
                self.active_keys = []
        if self.key_repeat_speed[1] <= 0:
            self.key_repeat_speed[1] = self.KEY_REPEAT_SPEED
            if self.pressed_keys[K_BACKSPACE]:
                if len(self.current_line) > 0:
                    self.current_line.delete()
            elif self.pressed_keys[K_RETURN]:
                self.text_log.append(self.current_line)
                self.process_line = self.current_line
                self.processed = False
                self.current_line = Line()
                self.text_log.location = 0
            elif self.pressed_keys[K_UP]:
                self.current_line = self.text_log.line_up()
            elif self.pressed_keys[K_DOWN]:
                self.current_line = self.text_log.line_down()
            elif self.pressed_keys[K_LEFT]:
                self.current_line - 1
            elif self.pressed_keys[K_RIGHT]:
                self.current_line + 1
            elif self.pressed_keys[K_TAB]:
                self.__create_tab_information()
            else:
                if self.active_keys:
                    self.current_line.append("".join(self.active_keys))
        else:
            if self.key_repeat_speed[0] > 0:
                self.key_repeat_speed[0] -= constants.GAME_TIME.get_time()
            elif self.key_repeat_speed[1] > 0:
                self.key_repeat_speed[1] -= constants.GAME_TIME.get_time()


    def __create_tab_information(self):
        commands = str(self.current_line).split(" ")
        possible_commands_dict = self.command_tree
        for command in commands[:-1]:
            try:
                if possible_commands_dict[command]:
                    possible_commands_dict = possible_commands_dict[command]
                #hit the end of the tree so simply return nothing
                else:
                    return
            except KeyError:
                return
        if commands[-1] == "":
            possible_commands = list(possible_commands_dict.keys())
        #if it ends on a perfect command simply add a space to the line
        elif commands[-1] in possible_commands_dict.keys():
            self.current_line.append(" ")
            return
        else:
            possible_commands = [key for key in possible_commands_dict.keys() if key.startswith(commands[-1])]
        if len(possible_commands) == 1:
            self.current_line = Line(text = " ".join(commands[:-1] + possible_commands), color = self.current_line.color)
        elif len(possible_commands) > 0:
            mcl = max(len(command) for command in possible_commands)
            m1 = "{:<" + str(mcl + 2) + "}"
            m2 = m1 * len(possible_commands)
            message = m2.format(*possible_commands)
            self.text_log.append_um(Line(text=message, color = (0,0,255)))
            lpc = max(possible_commands, key = len)
            letters = ""
            for letter in lpc:
                letters += letter
                if not all(c.startswith(letters) for c in possible_commands):
                    letters = letters[:-1]
                    break
            self.current_line = Line(text=" ".join(commands[:-1] + [letters]), color=self.current_line.color)

    def _get_image(self):
        image = super()._get_image()
        text = self.current_line.render_str(blinker = self.blinker_visible[0], header = ">:")
        image.blit(text, (10, self.rect.height - text.get_size()[1]))
        prev_line_heigth = text.get_size()[1]
        for i, line in enumerate(iter(self.text_log)):
            if self.rect.height - prev_line_heigth < 0:
                break
            text = line.render_str()
            prev_line_heigth += text.get_size()[1]
            image.blit(text, (10, self.rect.height - prev_line_heigth))
        return image.convert()

    def add_error_message(self, text):
        message = "ERROR: "
        self.text_log.append_um(Line(text = message + text, color = (163, 28, 23)))

    def add_conformation_message(self, text):
        self.text_log.append_um(Line(text = text, color = (25, 118, 168)))

class TextLog:
    def __init__(self):
        self.user_log = {}
        self.warning_log = {}
        self.location = 0

    def __getitem__(self, key):
        return self.user_log[len(self.user_log) - key]

    def __len__(self):
        return len(self.user_log)

    def __iter__(self):
        combined_keys = list(self.user_log.keys()) + list(self.warning_log.keys())
        combined_keys.sort()
        combined = {**self.user_log, **self.warning_log}
        sorted_lines = reversed(list(combined[key] for key in combined_keys))
        return iter(sorted_lines)

    def append(self, value):
        self.user_log[len(self.user_log) + len(self.warning_log)] = value
        value.rendered_str = value.rendered_str

    def append_um(self, value):
        #append user messages like warnings and conformations
        self.warning_log[len(self.user_log) + len(self.warning_log)] = value
        value.rendered_str = value.rendered_str

    def line_up(self):
        if self.location < len(self.user_log):
            self.location += 1
        return list(self.user_log.values())[-self.location].copy()

    def line_down(self):
        if self.location > 0:
            self.location -= 1
        if self.location == 0:
            return Line()
        return list(self.user_log.values())[-self.location].copy()

class Line:
    MAX_LINE_SIZE = 155
    BACKGROUND_COLOR = (75, 75, 75)
    def __init__(self, text = "", color = (0,255,0)):
        self.color = color
        self.text = text
        self.line_location = len(self.text)
        self.rendered_str = None
        self.font18 = pygame.font.Font(constants.DATA_DIR + "//Menu//font//manaspc.ttf", 18)

    def __str__(self):
        return self.text

    def render_str(self, blinker = False, header = ""):
        if self.rendered_str:
            return self.rendered_str
        else:
            return self.__get_render_str(blinker, header)

    def __get_render_str(self, blinker, header):
        if blinker:
            t = "{}{}_{}".format(header, self.text[:self.line_location],self.text[self.line_location + 1:])
        else:
            t = "{}{}".format(header, self.text)
        #if line is bigger then max of screen seperate the words and put them on separate lines
        size = [utilities.SCREEN_SIZE.size[0],0]
        line_heigth = self.font18.size("k")[1]
        if len(t) > self.MAX_LINE_SIZE:
            words = t.split(" ")
            text = [""]
            l = 0
            for word in words:
                if l + len(word) < self.MAX_LINE_SIZE:
                    text[len(text) - 1] += word + " "
                    l += len(word) + 1
                else:
                    s = self.font18.size(text[len(text) - 1])
                    size[1] += line_heigth
                    l = 0
                    text.append("")
            size[1] += line_heigth
        else:
            text = [t]
            size = self.font18.size(t)
        surf = pygame.Surface((size[0] + 2, size[1] + 2))

        surf.fill(self.BACKGROUND_COLOR)
        for i, line in enumerate(text):
            rt = self.font18.render(line, True, self.color)
            surf.blit(rt, (0, rt.get_size()[1] * i))
        return surf

    def __len__(self):
        return len(self.text)

    def __add__(self, other):
        if self.line_location + other <= len(self.text):
            self.line_location += other

    def __sub__(self, other):
        if self.line_location - other >= 0:
            self.line_location -= other

    def append(self, value):
        self.text = self.text[:self.line_location] + value + self.text[self.line_location:]
        self.line_location += len(value)

    def delete(self):
        self.line_location -= 1
        self.text = self.text[:self.line_location] + self.text[self.line_location + 1:]

    def copy(self):
        return Line(text=self.text, color=self.color)