#!/usr/bin/env python
import os, pygame, random

from constants import game_rules, DEFAULT_LEVEL_SIZE, DATA_DIR, SCREEN_SIZE, GAME_TIME
import weapon, utilities, camera, menu_methods, game_images, player_methods
from pygame.locals import *
from pygame.compat import geterror

class MainWindow:
    def __init__(self, size):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 40)

        global screen
        screen = pygame.display.set_mode(size, DOUBLEBUF)  # | FULLSCREEN)
        screen.set_alpha(None)
        game_images.load()

        pygame.display.set_caption("Playing a game are we now?")
        pygame.mouse.set_visible(True)
        self.rect = screen.get_rect()

        #player setup
        self.player = player_methods.Player((150, 500))
        self.game_sprites = camera.CameraAwareLayeredUpdates(self.player, DEFAULT_LEVEL_SIZE)

        self.scenes = self.setup_scenes()
        self.scene = self.scenes["Main"]

    def setup_scenes(self):
        self.player.right_arm.add(self.game_sprites)
        self.player.left_arm.add(self.game_sprites)
        
        # pause menu
        pause_sprites = pygame.sprite.LayeredUpdates()
        pause_menu = menu_methods.MenuPane((*self.rect.center, int(self.rect.width * 0.4), int(self.rect.height * 0.8)),
                                           utilities.load_image("Menu//paused_screen_menu.bmp", (255, 255, 255)),
                                           pause_sprites, title="Paused")
        buttonResume = menu_methods.Button(text="Resume")
        pause_menu.add_widget(("c", 100), buttonResume)

        def resume_action():
            utilities.scene_name = "Main"

        buttonResume.set_action(resume_action, MOUSEBUTTONDOWN)
        buttonResume.set_action(resume_action, K_RETURN)

        buttonRestart = menu_methods.Button(text="Restart")
        pause_menu.add_widget(("c", 150), buttonRestart)

        def restart_action():
            # if utilities.warnings:
            #     print("restart is disabled because of a memory bug at the moment")
            utilities.scene_name = "Main"
            setup_board()

        buttonRestart.set_action(restart_action, MOUSEBUTTONDOWN)
        buttonRestart.set_action(restart_action, K_RETURN)

        buttonOptions = menu_methods.Button(text="Options")
        pause_menu.add_widget(("c", 200), buttonOptions)

        def option_action():
            print("needs implementation")

        buttonOptions.set_action(option_action, MOUSEBUTTONDOWN)
        buttonOptions.set_action(option_action, K_RETURN)

        buttonQuit = menu_methods.Button(text="Quit")
        pause_menu.add_widget(("c", 250), buttonQuit)

        def quit_action():
            utilities.going = False

        buttonQuit.set_action(quit_action, MOUSEBUTTONDOWN)
        buttonQuit.set_action(quit_action, K_RETURN)

        # inventory
        inventory_sprites = pygame.sprite.LayeredUpdates()
        inventory_menu = menu_methods.MenuPane((*self.rect.center, int(self.rect.width * 0.8), int(self.rect.height * 0.8)),
                                               utilities.load_image("Menu//inventory.bmp", (255, 255, 255)),
                                               inventory_sprites, title="Inventory")

        item_list = menu_methods.WeaponListDisplay((250, 550), self.player.inventory, inventory_sprites, title="Weapons:")
        text_lbl = menu_methods.Label((900, 550))

        def show_weapon_text(*args):
            text_lbl.set_image(*args)

        def equip_weapon(*args):
            self.player.equip(*args)

        item_list.list_functions = {"SELECTION": show_weapon_text, K_e: equip_weapon}
        inventory_menu.add_widget((100, 100), item_list, center=False)
        inventory_menu.add_widget((400, 150), text_lbl, center=False)

        # Console menu
        con = menu_methods.ConsoleWindow(pygame.Rect(0, 0, self.rect.width, int(self.rect.height * 0.6)))

        scenes = {"Main": MainScene(self.game_sprites, self.player, self.rect),
                  "Pause": PauseScene(pause_sprites, pause_menu, pause_menu.rect),
                  "Inventory": InventoryScene(inventory_sprites, inventory_menu, inventory_menu.rect),
                  "Console": ConsoleScene(None, con, con.rect)}
        return scenes

class Scene():
    def __init__(self, sprites, event_sprite, rect):
        self.sprites = sprites
        self.rect = rect
        self.event_sprite = event_sprite

    def handle_events(self):
        pass

    def update(self):
        for sprite in self.sprites.sprites():
            self.sprites.change_layer(sprite, sprite._layer)
        self.sprites.update()

    def draw(self):
        self.sprites.draw(screen)

class MainScene(Scene):
    def __init__(self, sprites, event_sprite, rect):
        Scene.__init__(self, sprites, event_sprite, rect)
        self.nr_loaded_sprites = 0
        self.inventory_frame = self.get_inventory_frame()
        self.font20 = pygame.font.Font(DATA_DIR + "//Menu//font//manaspc.ttf", 20)
        self.dynamic_images = [menu_methods.WeaponDisplay(pygame.Rect(self.rect.width - 140, self.rect.height - 145,135,135), event_sprite)]
        self.name = "Main"

    def handle_events(self, events):
        player_events = []
        for event in events:
            if event.type == QUIT:
                utilities.going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                utilities.scene_name = "Pause"
            elif event.type == KEYDOWN and event.key == K_i:
                utilities.scene_name = "Inventory"
            elif event.type == KEYDOWN and event.key == K_c and pygame.key.get_mods() & KMOD_LCTRL:
                utilities.scene_name = "Console"
            else:
                player_events.append(event)
        self.event_sprite.events = player_events
        if not self.event_sprite.dead:
            self.nr_loaded_sprites = self.load_unload_sprites()

    def draw(self):
        screen.fill([0, 0, 0])
        super().draw()
        if game_rules.fps:
            fps = self.font20.render(str(int(GAME_TIME.get_fps())), True, pygame.Color('black'))
            screen.blit(fps, (10, 10))
        if game_rules.nr_entities:
            ve = self.font20.render(str(self.nr_loaded_sprites), True, pygame.Color('black'))
            screen.blit(ve, (10, 25))
        if not self.event_sprite.dead:
            self.draw_player_interface()
            if game_rules.bounding_boxes:
                self.draw_bounding_boxes()
            if game_rules.entity_paths:
                self.draw_path()
            if game_rules.vision_line:
                self.draw_vision_line()
            if game_rules.aim_line:
                self.draw_shoot_line()

    def load_unload_sprites(self):
        """
        Method for loading only sprites in an area around the self.event_sprite to reduce potential lag and other problems.
        :param self.event_sprite: the self.event_sprite object
        """
        sprites = self.event_sprite.groups()[0].sprites()
        c = self.event_sprite.rect.center
        if c[0] + self.rect.width / 2 - DEFAULT_LEVEL_SIZE.width > 0:
            x = 1 + (c[0] + self.rect.width / 2 - DEFAULT_LEVEL_SIZE.width) / (self.rect.width / 2)
        elif self.rect.width / 2 - c[0] > 0:
            x = 1 + (self.rect.width / 2 - c[0]) / (self.rect.width / 2)
        else:
            x = 1
        if c[1] + self.rect.height / 2 - DEFAULT_LEVEL_SIZE.height > 0:
            y = 1 + (c[1] + self.rect.height / 2 - DEFAULT_LEVEL_SIZE.width) / (self.rect.height / 2)
        elif self.rect.height / 2 - c[1] > 0:
            y = 1 + (self.rect.height / 2 - c[1]) / (self.rect.height / 2)
        else:
            y = 1
        range_rect = pygame.Rect(0, 0, int(SCREEN_SIZE.width * x), int(SCREEN_SIZE.height * y))
        range_rect.center = self.event_sprite.rect.center
        visible_ents = 0
        for i, sprite in enumerate(sprites):
            if all(sprite.visible) and not range_rect.colliderect(sprite.rect):
                sprite.visible = [False, True]
            elif sprite.visible[1] and not sprite.visible[0] and range_rect.colliderect(sprite.rect):
                sprite.visible = [True, True]
            if sprite.visible:
                visible_ents += 1
        return visible_ents

    def draw_bounding_boxes(self):
        """
        Draw boxes around all tiles and sprites for debugging purposes.
        :param screen: the screen the game is being displayed on
        :param player: the player object
        """
        sprites = self.event_sprite.groups()[0].sprites()
        c = self.event_sprite.rect.center
        for sprite in sprites:
            if sprite.visible:
                bb = sprite.bounding_box
                x, y = self.get_player_relative_screen_coordinate(bb.topleft)
                if hasattr(sprite, "debug_color"):
                    pygame.draw.rect(screen, sprite.debug_color, (int(x), int(y), bb.width, bb.height), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (int(x), int(y), bb.width, bb.height), 5)
        for tile in self.event_sprite.tiles.solid_tiles:
            bb = tile
            x, y = self.get_player_relative_screen_coordinate(tile.topleft)
            pygame.draw.rect(screen, (0, 0, 0), (int(x), int(y), tile.width, tile.height), 5)

    def draw_path(self):
        """
        Draw the pathfinding path the sprite has calculated at the current moment between itself and its destination
        :param player: the player object
        """
        sprites = self.event_sprite.groups()[0].sprites()
        path_sprites = [sprite for sprite in sprites if hasattr(sprite, "path")]
        c = self.event_sprite.rect.center
        for sprite in path_sprites:
            if len(sprite.path) > 0:
                center_points = []
                enemy_tile = sprite.tiles[int(sprite.rect.centery / 100)][int(sprite.rect.centerx / 100)]
                for tile in sprite.path + [enemy_tile]:
                    x, y = self.get_player_relative_screen_coordinate(tile.center)
                    center_points.append((int(x), int(y)))
                pygame.draw.lines(screen, sprite.debug_color, False, center_points, 4)

    def draw_vision_line(self):
        """
        Draw a line that indicates the vision line of sprites that have a vision tracking attribute.
        :param player: the player object
        """
        sprites = self.event_sprite.groups()[0].sprites()
        path_sprites = [sprite for sprite in sprites if hasattr(sprite, "vision_line")]
        c = self.event_sprite.rect.center
        for sprite in path_sprites:
            if len(sprite.vision_line) > 1:
                center_points = []
                for point in sprite.vision_line:
                    x, y = self.get_player_relative_screen_coordinate(point)
                    center_points.append((int(x), int(y)))
                pygame.draw.lines(screen, sprite.debug_color, False, center_points, 4)

    def draw_shoot_line(self):
        sprites = player.groups()[0].sprites()
        path_sprites = [sprite for sprite in sprites if hasattr(sprite, "vision_line")]
        c = self.event_sprite.rect.center
        start_point = self.get_player_relative_screen_coordinate(self.event_sprite.right_arm.rect.center)
        end_point = pygame.mouse.get_pos()
        pygame.draw.lines(screen, (0, 0, 0), False, (start_point, end_point), 4)

    def get_player_relative_screen_coordinate(self, coord):
        """
        Calculate a coordinate that is relative to the player position on the current dimensions of the screen. This helps
        placing debugging boxes and lines at the correct coordinates relative to the coordinates of the player.
        :param player: the player object
        :param coord: the coordinate that has to be calculated relative to the player
        :return: a coordinate relative to the player on the current screen.
        """
        c = self.event_sprite.rect.center
        if DEFAULT_LEVEL_SIZE.width - c[0] - self.rect.width / 2 < 0:
            x = self.rect.width - (DEFAULT_LEVEL_SIZE.width - coord[0])
        elif c[0] - self.rect.width / 2 > 0:
            x = coord[0] - (c[0] - self.rect.width / 2)
        else:
            x = coord[0]
        if DEFAULT_LEVEL_SIZE.height - c[1] - self.rect.height / 2 + 150 < 0:
            y = self.rect.height - (DEFAULT_LEVEL_SIZE.height - coord[1]) - 150
        elif c[1] - self.rect.height / 2 > 0:
            y = coord[1] - (c[1] - self.rect.height / 2)
        else:
            y = coord[1]
        return (x, y)

    def draw_player_interface(self):
        """
        Draws the interface for the player that changes based on the players current stats.
        :param player: the player object of the game
        :param interface_image: the image that is the framework of the playe rinterface
        """
        fraction_health = self.event_sprite.health[0] / self.event_sprite.health[1]
        fraction_xp = self.event_sprite.xp[0] / self.event_sprite.xp[1]
        pygame.draw.rect(screen, (255, 0, 0), (160, self.rect.height - 100, int((self.rect.width - 600 - 160) * fraction_health), 50))
        pygame.draw.rect(screen, (55, 255, 0), (160, self.rect.height - 40, int((self.rect.width - 600 - 160) * fraction_xp), 25))
        for widget in self.dynamic_images:
            widget.update()
            screen.blit(widget.image, widget.rect.topleft)
        screen.blit(self.inventory_frame, (0, self.rect.height - 150))

    def get_inventory_frame(self):
        """
        Function for creating a surface that is the general frame of the player interface. This is created once to reduce
        blit and draw calls.
        :return: a pygame.Surface object.
        """
        surf = pygame.Surface((self.rect.width, 150))
        surf.fill((255, 255, 255))
        # character display
        pygame.draw.rect(surf, (128, 128, 128), (5, 5, 135, 135), 5)
        # heath bar
        pygame.draw.rect(surf, (128, 128, 128), (160, 50, self.rect.width - 600 - 160, 50), 3)

        # xp bar
        width = round((self.rect.width - 600 - 160) / 10)
        for x in range(160, self.rect.width - 610, width):
            pygame.draw.rect(surf, (128, 128, 128), (x, 110, width, 25), 3)

        # item display
        x += width + 20
        pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
        x += 145
        pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
        x += 145
        pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
        x += 145
        pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
        surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        return surf.convert_alpha()


class PauseScene(Scene):
    def __init__(self, sprites, event_sprite, rect):
        Scene.__init__(self, sprites, event_sprite, rect)
        self.name = "Pause"

    def handle_events(self, events):
        menu_events = []
        for event in events:
            if event.type == QUIT:
                utilities.going = False
            elif (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == KEYDOWN and event.key == K_i):
                utilities.scene_name = "Main"
            else:
                menu_events.append(event)
        self.event_sprite.events = menu_events

class InventoryScene(Scene):
    def __init__(self, sprites, event_sprite, rect):
        Scene.__init__(self, sprites, event_sprite, rect)
        self.name = "Inventory"

    def handle_events(self, events):
        inventory_events = []
        for event in events:
            if event.type == QUIT:
                utilities.going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                utilities.scene_name = "Main"
            else:
                inventory_events.append(event)
        self.event_sprite.events = inventory_events

class ConsoleScene(Scene):
    def __init__(self, sprites, event_sprite, rect):
        Scene.__init__(self, sprites, event_sprite, rect)
        self.name = "Console"

    def update(self):
        self.event_sprite.update()

    def handle_events(self, events):
        console_events = []
        for event in events:
            if event.type == QUIT:
                utilities.going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                utilities.scene_name = "Main"
            #ctrl plus c
            elif event.type == KEYDOWN and event.key == K_c and pygame.key.get_mods() & KMOD_LCTRL:
                utilities.scene_name = "Main"
            else:
                console_events.append(event)
        self.event_sprite.events = console_events

    def draw(self):
        screen.blit(self.event_sprite.image, self.event_sprite.rect)
