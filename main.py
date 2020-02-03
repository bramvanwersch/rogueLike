#!/usr/bin/env python
# Import Modules
import os, pygame, random
import weapon, utilities, entities
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
    partsfile = os.path.join(utilities.data_dir, "parts.csv")
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

def run():
    #create starting seed for consistent replayability using a seed.
    random.seed(utilities.seed)
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Monkey Fever")
    pygame.mouse.set_visible(True)

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    #background color
    background.fill((250, 250, 250))

    # Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Load game objects here
    clock = pygame.time.Clock()
    weaponparts = load_parts()
    #method for grouping sprites to be updated togeter
    player = entities.Player(0, screen.get_rect().y)
    allsprites = pygame.sprite.RenderPlain((player))

    # Main Loop
    going = True
    while going:
        clock.tick(60)
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
        player.events = events
        allsprites.update()
        # Draw Everything --> clears screen and draws. Is not super efficient
        screen.blit(background, (0, 0))
        loc = [0,0]
        for _ in range(10):
            w1 = get_random_weapon(weaponparts[0])
            screen.blit(w1.image,loc)
            loc[0] += 50
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()