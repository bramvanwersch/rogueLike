#!/usr/bin/env python
# Import Modules
import os, pygame
import weapon, utilities, entities
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

def load_parts():
    """
    Pre loads the immages defined for the weapon parts
    :return: a dictionary containing the information pre defined in a csv file containing the information for each
    weapon in a part Object
    """
    partsfile = os.path.join(utilities.data_dir, "parts.csv")
    f = open(partsfile,"r")
    lines = f.readlines()
    f.close()
    weaponparts = {}
    dictnames = lines[0].replace("\n","").split(",")
    for line in lines[1:]:
        information = line.replace("\n","").split(",")
        data = {dictnames[x] : i for x,i in enumerate(information)}
        if data["type"] == "melee":
            weaponparts[data["name"]] = weapon.MeleePart(data)
        elif data["type"] == "projectile":
            weaponparts[data["name"]] = weapon.ProjectilePart(data)
    return weaponparts

def run():
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
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()