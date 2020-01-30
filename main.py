#!/usr/bin/env python
# Import Modules
import os, pygame
import weapon
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound

def load_parts():
    """
    Pre loads the immages defined for the weapon parts
    :return: a dictionary containing the information pre defined in a csv file containing the information for each
    weapon in a part Object
    """
    partsfile = os.path.join(data_dir, "parts.csv")
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
    screen = pygame.display.set_mode((468, 60))
    pygame.display.set_caption("Monkey Fever")
    pygame.mouse.set_visible(True)

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    #background color
    background.fill((250, 250, 250))

    # Put Text On The Background, Centered
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Pummel The Chimp, And Win $$$", 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width() / 2)
        background.blit(text, textpos)

    # Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Load game objects here
    clock = pygame.time.Clock()
    weaponparts = load_parts()
    #method for grouping sprites to be updated togeter
    allsprites = pygame.sprite.RenderPlain(())

    # Main Loop
    going = True
    while going:
        clock.tick(60)

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

        allsprites.update()

        # Draw Everything --> clears screen and draws. Is not super efficient
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()