#!/usr/bin/env python
import os, pygame, random
import weapon, utilities, entities, stages, camera
from pygame.locals import *
from pygame.compat import geterror

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

def load_unload_sprites(player):
    """
    Method for loading only sprites in an area around the player to reduce potential lag and other problems.
    """
    sprites = player.groups()[0].sprites()
    #roughly an area twice the screen size is loaded
    range_rect = pygame.Rect(0,0,int(utilities.SCREEN_SIZE.width * 2) , int(utilities.SCREEN_SIZE.height * 2))
    range_rect.center = player.rect.center
    for i,tile in enumerate(sprites):
        if tile.visible and not range_rect.colliderect(tile.rect):
            tile.visible = False
        elif not tile.visible and range_rect.colliderect(tile.rect):
            tile.visible = True

def run():
    #create starting seed for consistent replayability using a seed.
    random.seed(utilities.seed)
    pygame.init()
    font = pygame.font.Font(None, 30)
    screen = pygame.display.set_mode((utilities.SCREEN_SIZE.width, utilities.SCREEN_SIZE.height), DOUBLEBUF)
    pygame.display.set_caption("Welcome to the forest")
    pygame.mouse.set_visible(True)

    player = entities.Player((0, 500))
    ents = camera.CameraAwareLayeredUpdates(player, utilities.DEFAULT_LEVEL_SIZE)

    #setup the stage
    stage = stages.ForestStage(ents, player)
    stage.create_tiles()
    # stage.add_enemy("red square", (600,500))
    for i in range(10):
        stage.add_enemy("bad bat", (400 + i * 100,500 + i * 100))

    clock = pygame.time.Clock()
    weaponparts = load_parts()
    # Main Loop
    going = True
    while going:
        clock.tick(200)
        events = []
        # Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == MOUSEBUTTONDOWN:
                print("Click")
            elif event.type == MOUSEBUTTONUP:
                print("un-Click")
            else:
                events.append(event)

        screen.fill([255, 255, 255])

        #load the tiles around the player and generate new ones if needed.
        load_unload_sprites(player)
        player.events = events
        ents.update()
        ents.draw(screen)
        # loc = [0,0]
        # for _ in range(10):
        #     w1 = get_random_weapon(weaponparts[0])
        #     screen.blit(w1.image,loc)
        #     loc[0] += 50
        fps = font.render(str(int(clock.get_fps())), True, pygame.Color('black'))
        screen.blit(fps, (10,10))
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    run()