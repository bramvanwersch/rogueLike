#!/usr/bin/env python
import os, pygame, random
import weapon, utilities, entities, stages, camera, player_methods, menu_methods
from pygame.locals import *
from pygame.compat import geterror

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,40)


def get_random_weapon(parts, melee = True):
    """
    Gives a random weapon randoming from a pool of random parts. This is different for melee and projectile weapons
    NOTE: projectile implementation is incomplete
    :param parts: a dictionary of melee or projectile parts containing all available parts for a certain weaponthat can
    be assembled into a weapon.
    :param melee: a boolean telling if the weapon is a melee or a projectile weapon
    :return: an instance of a weapon class.
    """
    weaponparts = {"blade":"","guard":"","handle":"","pommel":""}
    for name in parts.keys():
        try:
            partdict = parts[name]
            partname = random.choice(list(partdict.keys()))
            weaponparts[name] = parts[name][partname]
        except KeyError as e:
            raise Exception("Weapon part missing. Major problem should not occur.") from e
    if melee:
        return weapon.MeleeWeapon(weaponparts)
    return weapon.ProjectileWeapon(weaponparts)

def load_parts():
    """
    Pre loads the immages defined for the weapon parts
    :return: return a tuple containing projectile and melee parts in seperate dictionaries that contain a dictionary
    for each part consisting of part classes.
    """
    partsfile = os.path.join(utilities.DATA_DIR, "info//parts.csv")
    f = open(partsfile,"r")
    lines = f.readlines()
    f.close()
    meleeweaponparts, projectileweaponparts = {"blade" : {},"guard" : {},"handle" : {},"pommel" : {}}, {}
    dictnames = lines[0].replace("\n","").split(",")
    for line in lines[1:]:
        information = line.replace("\n","").split(",")
        data = {dictnames[x] : i for x,i in enumerate(information)}
        if data["type"] == "melee":
            try:
                meleepart = weapon.MeleePart(data)
                meleeweaponparts[meleepart.type][meleepart.name] = meleepart
            except KeyError as e:
                raise Exception("Unknown part name found.") from e
        elif data["type"] == "projectile":
            weaponparts[data["name"]] = weapon.ProjectilePart(data)
    return (meleeweaponparts, projectileweaponparts)

def load_unload_sprites(player,screen):
    """
    Method for loading only sprites in an area around the player to reduce potential lag and other problems.
    """
    sprites = player.groups()[0].sprites()
    sprites = player.groups()[0].sprites()
    c = player.rect.center
    sr = screen.get_rect()
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

def draw_bounding_boxes(screen, player):
    """
    Draw boxes around all tiles and sprites for debugging purposes.
    :param screen: the screen the game is being displayed on
    :param player: the player that is the center of the screen
    """
    sprites = player.groups()[0].sprites()
    c = player.rect.center
    sr = screen.get_rect()
    for sprite in sprites:
        if sprite.visible:
            bb = sprite.bounding_box
            if utilities.DEFAULT_LEVEL_SIZE.width - c[0] - sr.width / 2 < 0:
                x = sr.width - (utilities.DEFAULT_LEVEL_SIZE.width - bb.x)
            elif c[0] - sr.width / 2 > 0:
                x = bb.x - (c[0] - sr.width / 2)
            else:
                x = bb.x
            if utilities.DEFAULT_LEVEL_SIZE.height - c[1] - sr.height / 2 < 0:
                y = sr.height - (utilities.DEFAULT_LEVEL_SIZE.height - bb.y)
            elif c[1] - sr.height / 2 > 0:
                y = bb.y - (c[1] - sr.height / 2)

            else:
                y = bb.y
            pygame.draw.rect(screen, (0,0,0), (int(x), int(y), bb.width, bb.height), 5)
    for tile in player.tiles.get_non_zero_tiles():
        bb = tile
        if utilities.DEFAULT_LEVEL_SIZE.width - c[0] - sr.width / 2 < 0:
            x = sr.width - (utilities.DEFAULT_LEVEL_SIZE.width - bb.x)
        elif c[0] - sr.width / 2 > 0:
            x = bb.x - (c[0] - sr.width / 2)
        else:
            x = bb.x
        if utilities.DEFAULT_LEVEL_SIZE.height - c[1] - sr.height / 2 < 0:
            y = sr.height - (utilities.DEFAULT_LEVEL_SIZE.height - bb.y)
        elif c[1] - sr.height / 2 > 0:
            y = bb.y - (c[1] - sr.height / 2)

        else:
            y = bb.y
        pygame.draw.rect(screen, (0,0,0), (int(x), int(y), bb.width, bb.height), 5)

random.seed(utilities.seed)
pygame.init()
FONT = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20)

screen = pygame.display.set_mode((utilities.SCREEN_SIZE.width, utilities.SCREEN_SIZE.height),
                                 DOUBLEBUF)  # | FULLSCREEN)
screen.set_alpha(None)
sr = screen.get_rect()

pygame.display.set_caption("Welcome to the forest")
pygame.mouse.set_visible(True)

# pre random some weapons
weaponparts = load_parts()

#setup the board and player sprites
def setup_board():
    weapons = [get_random_weapon(weaponparts[0]) for _ in range(20)]

    player = player_methods.Player((150, 500), get_random_weapon(weaponparts[0]))
    game_sprites = camera.CameraAwareLayeredUpdates(player, utilities.DEFAULT_LEVEL_SIZE)
    player.right_arm.add(game_sprites)
    player.left_arm.add(game_sprites)

    global stage
    stage = stages.ForestStage(game_sprites, player, weapons=weapons)
    player.tiles = stage.tiles

    # stage.add_enemy("dummy", (600, 500))
    # TODO needs to be moved to different place
    # stage.add_enemy("red square", (600, 500))
    stage.add_enemy("archer", (100,100))
    # for i in range(5):
    #     stage.add_enemy("archer", (400 + i * 20, 500 + i * 20))

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
        utilities.scene_name = "Main"
        setup_board()
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
            self.nr_loaded_sprites = load_unload_sprites(self.event_sprite, screen)

    def draw(self):
        screen.fill([0, 0, 0])
        super().draw()
        if utilities.FPS:
            fps = FONT.render(str(int(utilities.GAME_TIME.get_fps())), True, pygame.Color('black'))
            screen.blit(fps, (10, 10))
        if utilities.TEST and not self.event_sprite.dead:
            ve =  FONT.render(str(self.nr_loaded_sprites), True,pygame.Color('black'))
            screen.blit(ve,(10,25))
            draw_bounding_boxes(screen, self.event_sprite)

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
        utilities.GAME_TIME.tick(200)
        scene.handle_events(pygame.event.get())
        scene.update()
        scene.draw()
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    run()