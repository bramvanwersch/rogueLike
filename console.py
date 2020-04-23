#!/usr/bin/env python
import os, pygame, random
import main, utilities, stages, weapon, game_images
from pygame.locals import *
from pygame.compat import geterror

class Console:
    def __init__(self):
        random.seed(utilities.seed)
        pygame.init()

        self.screen = main.MainWindow(utilities.SCREEN_SIZE.size)
        self.stage = stages.ForestStage(self.screen.game_sprites, self.screen.player)
        self.weapon_parts = self.__load_parts()
        start_weapon = self.get_weapon_by_parts({"body": "test_body", "barrel": "less_big_boy_barrel",
                                                        "stock": "hook_stock","magazine": "round_magazine",
                                                        "accesory": "big_scope_accesory"})
        self.screen.player.equip(start_weapon)
        self.screen.player.inventory.add(start_weapon)
        self.run()

    def run(self):
        # Main Loop
        while utilities.going:
            self.screen.scene = self.screen.scenes[utilities.scene_name]
            utilities.GAME_TIME.tick(60)
            self.screen.scene.handle_events(pygame.event.get())
            self.screen.scene.update()
            self.stage.update()
            self.screen.scene.draw()
            pygame.display.update()
        pygame.quit()

    def __load_parts(self):
        """
        Pre loads the immages defined for the weapon parts
        :return: return a dictionary of parts containing a list of dictionaries with an entry for each part.
        """
        partsfile = os.path.join(utilities.DATA_DIR, "info//parts.csv")
        f = open(partsfile, "r")
        lines = f.readlines()
        f.close()
        projectileweaponparts = {"body": [], "barrel": [], "stock": [], "magazine": [], "accesory": []}
        # first line is descriptors
        dictnames = list(x.strip() for x in lines[0].replace("\n", "").split(","))
        for line in lines[1:]:
            information = line.replace("\n", "").split(",")
            data = {dictnames[x]: i.strip() for x, i in enumerate(information) if i.strip()}
            projectileweaponparts[data["part type"]].append(weapon.WeaponPart(data))
        return projectileweaponparts

    def get_random_weapon(self):
        """
        Gives a random weapon randoming from a pool of random self.weapon_parts. This is different for melee and projectile weapons
        NOTE: projectile implementation is incomplete
        :param parts: a dictionary of melee or projectile parts containing all available parts for a certain weaponthat can
        be assembled into a weapon.
        :param melee: a boolean telling if the weapon is a melee or a projectile weapon
        :return: an instance of a weapon class.
        """
        weapon_parts = {"body": None, "barrel": None, "stock": None, "magazine": None, "accesory": None}
        for part_group in self.weapon_parts.keys():
            part_list = parts[part_group]
            weapon_parts[part_group] = random.choice(part_list)
        return weapon.Weapon(weapon_parts)

    def get_weapon_by_parts(self, part_names):
        weapon_parts = {"body": None, "barrel": None, "stock": None, "magazine": None, "accesory": None}
        for part_group in self.weapon_parts.keys():
            part_list = self.weapon_parts[part_group]
            for part in part_list:
                if part.name.strip() == part_names[part_group]:
                    weapon_parts[part_group] = part
        return weapon.Weapon(weapon_parts)

# class Console:
#     def __init__(self,rect):
#         background_image = pygame.Surface(rect.size)
#         background_image.fill((48, 48, 48))
#         self.image = background_image
#         self.rect = rect
#         self.events = []
#         self.text_log = []
#         self.text = ">"
#         self.font20 = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 20)
#
#     def update(self):
#         for event in self.events:
#             if event.type == KEYDOWN:
#                 if event.key == K_BACKSPACE:
#                     if len(self.text) > 1:
#                         self.text = self.text[:-1]
#                 else:
#                     self.text += event.unicode
#                 if event.key == K_RETURN:
#                     self.text_log.append(self.text)
#                     self.__process_line(self.text)
#                     self.text = ">"
#         self.image = pygame.Surface(self.rect.size)
#         self.image.fill((48, 48, 48))
#         text = self.font20.render(self.text, False, (0,255,0))
#         self.image.blit(text, (10, self.rect.height - text.get_size()[1]))
#         for i, line in enumerate(reversed(self.text_log)):
#             if self.rect.height - text.get_size()[1] * (i + 2) < 0:
#                 break
#             text = self.font20.render(line, False, (0,255,0))
#             self.image.blit(text, (10, self.rect.height - text.get_size()[1] * (i + 2)))
#
#     def __process_line(self, text):
#         #remove start
#         text = text[1:]
#


if __name__ == "__main__":
    c = Console()



