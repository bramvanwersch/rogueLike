#!/usr/bin/env python
import os, pygame, random
import weapon, utilities, entities, stages, camera, player_methods
from pygame.locals import *
from pygame.compat import geterror

visible_ents = 0

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
        if sprite.visible and not range_rect.colliderect(sprite.rect):
            sprite.visible = False
        elif not sprite.visible and range_rect.colliderect(sprite.rect):
            sprite.visible = True
        if sprite.visible:
            visible_ents += 1
    return visible_ents

def draw_bounding_boxes(screen, player):
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

def run():
    #create starting seed for consistent replayability using a seed.
    random.seed(utilities.seed)
    pygame.init()

    screen = pygame.display.set_mode((utilities.SCREEN_SIZE.width, utilities.SCREEN_SIZE.height), DOUBLEBUF) #| FULLSCREEN)
    screen.set_alpha(None)

    pygame.display.set_caption("Welcome to the forest")
    pygame.mouse.set_visible(True)

    FONT = pygame.font.Font(None, 30)

    weaponparts = load_parts()

    player = player_methods.Player((150, 500))
    ents = camera.CameraAwareLayeredUpdates(player, utilities.DEFAULT_LEVEL_SIZE)
    player.right_arm.add(ents)
    player.left_arm.add(ents)
    player.right_arm.equip(get_random_weapon(weaponparts[0]))
    # player.arm.equip(get_random_weapon(weaponparts[0]))
    #
    # player.arm.equip(get_random_weapon(weaponparts[0]))
    #
    # player.arm.equip(get_random_weapon(weaponparts[0]))


    #setup the stage
    stage = stages.ForestStage(ents, player)
    player.tiles = stage.tiles

    # stage.add_enemy("dummy", (600, 500))
    # stage.add_enemy("red square", (600,500))
    for i in range(10):
        stage.add_enemy("bad bat", (400 + i * 20,500 + i * 20))
    # Main Loop
    going = True
    while going:
        utilities.GAME_TIME.tick(200)
        if not player.dead:
            ve = load_unload_sprites(player, screen)
        events = []
        # Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            else:
                events.append(event)

        screen.fill([0,0,0])
        # player.arm.equip(get_random_weapon(weaponparts[0]))

        player.events = events
        ents.update()
        ents.draw(screen)

        # loc = [0,0]
        # for _ in range(10):
        #     w1 = get_random_weapon(weaponparts[0])
        #     w1.image = pygame.transform.scale(w1.image, (int(w1.image.get_rect().width * 0.7), int(w1.image.get_rect().height * 0.7)))
        #     screen.blit(w1.image,loc)
        #     loc[0] += 50
        if utilities.FPS:
            fps = FONT.render(str(int(utilities.GAME_TIME.get_fps())), True, pygame.Color('black'))
            screen.blit(fps, (10, 10))
        if utilities.TEST and not player.dead:
            ve =  FONT.render(str(ve), True,pygame.Color('black'))
            screen.blit(ve,(10,25))
            draw_bounding_boxes(screen, player)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    run()