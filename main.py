#!/usr/bin/env python
import os, pygame, random
import weapon, utilities, entities, stages, camera, player_methods, menu_methods, game_images
from pygame.locals import *
from pygame.compat import geterror

def get_random_weapon(parts):
    """
    Gives a random weapon randoming from a pool of random parts. This is different for melee and projectile weapons
    NOTE: projectile implementation is incomplete
    :param parts: a dictionary of melee or projectile parts containing all available parts for a certain weaponthat can
    be assembled into a weapon.
    :param melee: a boolean telling if the weapon is a melee or a projectile weapon
    :return: an instance of a weapon class.
    """
    weapon_parts = {"body":None,"barrel":None,"stock":None,"magazine":None,"accesory":None}
    for part in parts.keys():
        part_dict = parts[part]
        weapon_parts[part] = random.choice(part_dict)
    return weapon.Weapon(weapon_parts)

def load_parts():
    """
    Pre loads the immages defined for the weapon parts
    :return: return a dictionary of parts containing a list of dictionaries with an entry for each part.
    """
    partsfile = os.path.join(utilities.DATA_DIR, "info//parts.csv")
    f = open(partsfile,"r")
    lines = f.readlines()
    f.close()
    projectileweaponparts = {"body":[],"barrel":[],"stock":[],"magazine":[],"accesory":[]}
    #first line is descriptors
    dictnames = list(x.strip() for x in lines[0].replace("\n","").split(","))
    for line in lines[1:]:
        information = line.replace("\n","").split(",")
        data = {dictnames[x] : i.strip() for x,i in enumerate(information) if i.strip()}
        projectileweaponparts[data["part type"]].append(weapon.WeaponPart(data))
    return projectileweaponparts

def load_unload_sprites(player):
    """
    Method for loading only sprites in an area around the player to reduce potential lag and other problems.
    :param player: the player object
    """
    sprites = player.groups()[0].sprites()
    c = player.rect.center
    if c[0] + sr.width / 2 - utilities.DEFAULT_LEVEL_SIZE.width > 0:
        x = 1+ (c[0] + sr.width / 2 - utilities.DEFAULT_LEVEL_SIZE.width) / (sr.width / 2)
    elif sr.width / 2 - c[0]  > 0:
        x = 1 + (sr.width / 2 - c[0]) / (sr.width / 2)
    else:
        x = 1
    if c[1] + sr.height / 2 - utilities.DEFAULT_LEVEL_SIZE.height > 0:
        y = 1+ (c[1] + sr.height / 2 - utilities.DEFAULT_LEVEL_SIZE.width) / (sr.height / 2)
    elif sr.height / 2 - c[1]  > 0:
        y = 1 + (sr.height / 2 - c[1]) / (sr.height / 2)
    else:
        y = 1
    range_rect = pygame.Rect(0,0,int(utilities.SCREEN_SIZE.width * x) , int(utilities.SCREEN_SIZE.height * y))
    range_rect.center = player.rect.center
    visible_ents = 0
    for i,sprite in enumerate(sprites):
        if all(sprite.visible) and not range_rect.colliderect(sprite.rect):
            sprite.visible = [False,True]
        elif sprite.visible[1] and not sprite.visible[0] and range_rect.colliderect(sprite.rect):
            sprite.visible = [True, True]
        if sprite.visible:
            visible_ents += 1
    return visible_ents

def draw_bounding_boxes(player):
    """
    Draw boxes around all tiles and sprites for debugging purposes.
    :param screen: the screen the game is being displayed on
    :param player: the player object
    """
    sprites = player.groups()[0].sprites()
    c = player.rect.center
    for sprite in sprites:
        if sprite.visible:
            bb = sprite.bounding_box
            x, y = get_player_relative_screen_coordinate(player, bb.topleft)
            if hasattr(sprite, "debug_color"):
                pygame.draw.rect(screen, sprite.debug_color, (int(x), int(y), bb.width, bb.height), 5)
            else:
                pygame.draw.rect(screen, (0,0,0), (int(x), int(y), bb.width, bb.height), 5)
    for tile in player.tiles.solid_tiles:
        bb = tile
        x, y = get_player_relative_screen_coordinate(player, tile.topleft)
        pygame.draw.rect(screen, (0,0,0), (int(x), int(y), tile.width, tile.height), 5)

def draw_path(player):
    """
    Draw the pathfinding path the sprite has calculated at the current moment between itself and its destination
    :param player: the player object
    """
    sprites = player.groups()[0].sprites()
    path_sprites = [sprite for sprite in sprites if hasattr(sprite, "path")]
    c = player.rect.center
    for sprite in path_sprites:
        if len(sprite.path) > 0:
            center_points = []
            enemy_tile = sprite.tiles[int(sprite.rect.centery / 100)][int(sprite.rect.centerx / 100)]
            for tile in sprite.path + [enemy_tile]:
                x, y = get_player_relative_screen_coordinate(player, tile.center)
                center_points.append((int(x),int(y)))
            pygame.draw.lines(screen, sprite.debug_color, False, center_points, 4)

def draw_vision_line(player):
    """
    Draw a line that indicates the vision line of sprites that have a vision tracking attribute.
    :param player: the player object
    """
    sprites = player.groups()[0].sprites()
    path_sprites = [sprite for sprite in sprites if hasattr(sprite, "vision_line")]
    c = player.rect.center
    for sprite in path_sprites:
        if len(sprite.vision_line) > 1:
            center_points = []
            for point in sprite.vision_line:
                x, y = get_player_relative_screen_coordinate(player, point)
                center_points.append((int(x), int(y)))
            pygame.draw.lines(screen, sprite.debug_color, False, center_points, 4)

def get_player_relative_screen_coordinate(player, coord):
    """
    Calculate a coordinate that is relative to the player position on the current dimensions of the screen. This helps
    placing debugging boxes and lines at the correct coordinates relative to the coordinates of the player.
    :param player: the player object
    :param coord: the coordinate that has to be calculated relative to the player
    :return: a coordinate relative to the player on the current screen.
    """
    c = player.rect.center
    if utilities.DEFAULT_LEVEL_SIZE.width - c[0] - sr.width / 2 < 0:
        x = sr.width - (utilities.DEFAULT_LEVEL_SIZE.width - coord[0])
    elif c[0] - sr.width / 2 > 0:
        x = coord[0] - (c[0] - sr.width / 2)
    else:
        x = coord[0]
    if utilities.DEFAULT_LEVEL_SIZE.height - c[1] - sr.height / 2 + 150 < 0:
        y = sr.height - (utilities.DEFAULT_LEVEL_SIZE.height - coord[1]) - 150
    elif c[1] - sr.height / 2 > 0:
        y = coord[1] - (c[1] - sr.height / 2)
    else:
        y = coord[1]
    return (x,y)

def draw_player_interface(player, interface_image):
    """
    Draws the interface for the player that changes based on the players current stats.
    :param player: the player object of the game
    :param interface_image: the image that is the framework of the playe rinterface
    """
    fraction_health = player.health[0] / player.health[1]
    fraction_xp = player.xp[0] / player.xp[1]
    pygame.draw.rect(screen, (255,0,0), (160, sr.height - 100, int((sr.width - 600 - 160) * fraction_health), 50))
    pygame.draw.rect(screen, (55, 255, 0), (160, sr.height - 40, int((sr.width - 600 - 160) * fraction_xp), 25))
    screen.blit(interface_image,(0, sr.height  - 150))

def get_inventory_frame():
    """
    Function for creating a surface that is the general frame of the player interface. This is created once to reduce
    blit and draw calls.
    :return: a pygame.Surface object.
    """
    surf = pygame.Surface((sr.width, 150))
    surf.fill((255,255,255))
    #character display
    pygame.draw.rect(surf, (128,128,128), (5, 5, 135, 135), 5)
    #heath bar
    pygame.draw.rect(surf, (128,128,128), (160, 50, sr.width - 600 - 160, 50), 3)

    #xp bar
    width = round((sr.width - 600 - 160) / 10)
    for x in range(160, sr.width - 610, width):
        pygame.draw.rect(surf, (128, 128, 128), (x, 110, width, 25), 3)

    #item display
    x += width + 20
    pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
    x += 145
    pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
    x += 145
    pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
    x += 145
    pygame.draw.rect(surf, (128, 128, 128), (x, 5, 135, 135), 5)
    surf.set_colorkey((255,255,255), pygame.RLEACCEL)
    return surf.convert_alpha()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,40)

random.seed(utilities.seed)
pygame.init()
FONT = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20)

screen = pygame.display.set_mode((utilities.SCREEN_SIZE.width, utilities.SCREEN_SIZE.height),DOUBLEBUF)  # | FULLSCREEN)
screen.set_alpha(None)
sr = screen.get_rect()
game_images.load()

pygame.display.set_caption("Welcome to the forest")
pygame.mouse.set_visible(True)

# pre random some weapons
weaponparts = load_parts()

#setup the board and player sprites
def setup_board():
    #generate 20 random weapons
    weapons = [get_random_weapon(weaponparts) for _ in range(20)]

    player = player_methods.Player((150, 500), get_random_weapon(weaponparts))
    game_sprites = camera.CameraAwareLayeredUpdates(player, utilities.DEFAULT_LEVEL_SIZE)
    player.right_arm.add(game_sprites)
    player.left_arm.add(game_sprites)

    global stage
    stage = stages.ForestStage(game_sprites, player, weapons=weapons)
    stage.add_enemy("archer",(500,500))

    #pause menu
    pause_sprites = pygame.sprite.LayeredUpdates()
    pause_menu = menu_methods.MenuPane((*sr.center,int(sr.width * 0.4),int(sr.height * 0.8)),
                                       utilities.load_image("Menu//paused_screen_menu.bmp", (255,255,255)),
                                       pause_sprites, title = "Paused")
    buttonResume = menu_methods.Button(text = "Resume")
    pause_menu.add_widget(("c",100), buttonResume)
    def resume_action():
        utilities.scene_name = "Main"
    buttonResume.set_action(resume_action, MOUSEBUTTONDOWN)
    buttonResume.set_action(resume_action, K_RETURN)

    buttonRestart = menu_methods.Button(text = "Restart")
    pause_menu.add_widget(("c", 150), buttonRestart)
    def restart_action():
        if utilities.WARNINGS:
            print("restart is disabled because of a memory bug at the moment")
        # utilities.scene_name = "Main"
        # setup_board()
    buttonRestart.set_action(restart_action, MOUSEBUTTONDOWN)
    buttonRestart.set_action(restart_action, K_RETURN)

    buttonOptions = menu_methods.Button(text = "Options")
    pause_menu.add_widget(("c", 200), buttonOptions)
    def option_action():
        print("needs implementation")
    buttonOptions.set_action(option_action, MOUSEBUTTONDOWN)
    buttonOptions.set_action(option_action, K_RETURN)

    buttonQuit = menu_methods.Button(text= "Quit")
    pause_menu.add_widget(("c",250), buttonQuit)
    def quit_action():
        utilities.going = False
    buttonQuit.set_action(quit_action, MOUSEBUTTONDOWN)
    buttonQuit.set_action(quit_action, K_RETURN)

    #inventory
    inventory_sprites = pygame.sprite.LayeredUpdates()
    inventory_menu = menu_methods.MenuPane((*sr.center,int(sr.width * 0.8),int(sr.height * 0.8)),
                                           utilities.load_image("Menu//inventory.bmp",(255,255,255)),
                                           inventory_sprites, title = "Inventory")

    item_list = menu_methods.WeaponListDisplay((250, 550), player.inventory, inventory_sprites, title ="Weapons:")
    text_lbl = menu_methods.Label((900,550))
    def show_weapon_text(*args):
        text_lbl.set_image(*args)
    def equip_weapon(*args):
        player.equip(*args)
    item_list.list_functions = {"SELECTION": show_weapon_text, K_e : equip_weapon}
    inventory_menu.add_widget((100,100), item_list, center = False)
    inventory_menu.add_widget((400,150), text_lbl, center = False)

    global scenes
    scenes = {"Main": MainScene(game_sprites,player),
              "Pause": PauseScene(pause_sprites, pause_menu),
              "Inventory": InventoryScene(inventory_sprites, inventory_menu)}

class Scene():
    def __init__(self, sprites, event_sprite):
        self.sprites = sprites
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
    def __init__(self, sprites, event_sprite):
        Scene.__init__(self, sprites, event_sprite)
        self.nr_loaded_sprites = 0
        self.inventory_frame = get_inventory_frame()

    def handle_events(self, events):
        player_events = []
        for event in events:
            if event.type == QUIT:
                utilities.going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                utilities.scene_name = "Pause"
                #go to pause scene
            elif event.type == KEYDOWN and event.key == K_i:
                utilities.scene_name = "Inventory"
            else:
                player_events.append(event)
        self.event_sprite.events = player_events
        if not self.event_sprite.dead:
            self.nr_loaded_sprites = load_unload_sprites(self.event_sprite)

    def draw(self):
        screen.fill([0, 0, 0])
        super().draw()
        if utilities.FPS:
            fps = FONT.render(str(int(utilities.GAME_TIME.get_fps())), True, pygame.Color('black'))
            screen.blit(fps, (10, 10))
        if utilities.NR_ENTITIES:
            ve = FONT.render(str(self.nr_loaded_sprites), True, pygame.Color('black'))
            screen.blit(ve, (10, 25))
        if not self.event_sprite.dead:
            draw_player_interface(self.event_sprite, self.inventory_frame)
            if utilities.BOUNDING_BOXES:
                draw_bounding_boxes(self.event_sprite)
            if utilities.ENTITY_PATHS:
                draw_path(self.event_sprite)
            if utilities.VISION_LINE:
                draw_vision_line(self.event_sprite)

class PauseScene(Scene):
    def __init__(self, sprites, event_sprite):
        Scene.__init__(self, sprites, event_sprite)

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
    def __init__(self, sprites, event_sprite):
        Scene.__init__(self, sprites, event_sprite)

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

def run():
    # Main Loop
    setup_board()

    while utilities.going:
        scene = scenes[utilities.scene_name]
        utilities.GAME_TIME.tick(60)
        scene.handle_events(pygame.event.get())
        scene.update()
        scene.draw()
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    run()