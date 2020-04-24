#!/usr/bin/env python
import os, pygame, random

from constants import game_rules, GAME_TIME, DATA_DIR, SCREEN_SIZE
import main, utilities, stages, weapon, game_images
from pygame.locals import *
from pygame.compat import geterror

class Console:
    def __init__(self):
        random.seed(utilities.seed)
        pygame.init()

        self.screen = main.MainWindow(SCREEN_SIZE.size)
        self.stage = stages.ForestStage(self.screen.game_sprites, self.screen.player)
        self.weapon_parts = self.__load_parts()
        start_weapon = self.get_weapon_by_parts({"body": "test_body", "barrel": "less_big_boy_barrel",
                                                        "stock": "hook_stock","magazine": "round_magazine",
                                                        "accesory": "big_scope_accesory"})
        self.screen.player.equip(start_weapon)
        self.screen.player.inventory.add(start_weapon)

        self.main_sprite = self.screen.scene.event_sprite

        #last thing to execute no response after this
        self.run()

    def run(self):
        # Main Loop
        while utilities.going:
            self.screen.scene = self.screen.scenes[utilities.scene_name]
            self.main_sprite = self.screen.scene.event_sprite
            #if a new line is commited in the command window and it is not processed, process it.
            if utilities.scene_name == "Console" and not self.main_sprite.processed:
                self.__process_commands(str(self.main_sprite.process_line))
                self.screen.scene.event_sprite.processed = True
            GAME_TIME.tick(60)
            self.screen.scene.handle_events(pygame.event.get())
            self.screen.scene.update()
            self.stage.update()
            self.screen.scene.draw()
            pygame.display.update()
        pygame.quit()

    def __process_commands(self, text):
        commands = text.split(" ")
        commands = list(command.lower() for command in commands)
        #SET
        if commands[0] == "set":
            self.__process_set(commands[1:])
        elif commands[0] == "create":
            self.__process_create(commands[1:])
        elif commands[0] == "delete":
            self.__process_delete(commands[1:])
        else:
            self.main_sprite.add_error_message("No valid command choose one of the following: SET, CREATE, DELETE.")
        #MOVE
        #PRINT

    def __process_set(self, commands):
        if len(commands) < 3:
            self.main_sprite.add_error_message("Expected al least 3 arguments to SET command [FROM, NAME, VALUE].")
            return
        if commands[0] == "game_rule":
            try:
                self.__execute(game_rules, [commands[1], self.__string_to_bool(commands[2])])
            except ValueError:
                self.main_sprite.add_error_message("{} is not a valid value for {}".format(commands[2], commands[1]))
        elif commands[0] == "player":
            pass
        elif commands[0] == "enemys":
            pass
        elif commands[0] == "entities":
            pass
        elif commands[0] == "stage":
            pass
        else:
            self.main_sprite.add_error_message("Unknown FROM location. Choose one of the following: game_rule, player, enemys, entities, stage")

    def __execute(self, target, commands):
        if hasattr(target, str(commands[0])):
            setattr(target, commands[0], commands[1])
            self.main_sprite.add_conformation_message("{} are set to {}".format(commands[0], commands[1]))
        else:
            self.main_sprite.add_error_message("target has no attribute {}.".format(commands[0]))

    def __string_to_bool(self, value):
        if value == "true" or value == "t":
            return True
        elif value == "false" or value == "f":
            return False
        else:
            raise(ValueError)

    def __process_create(self, commands):
        pass

    def __process_delete(self, commands):
        pass

    def __load_parts(self):
        """
        Pre loads the immages defined for the weapon parts
        :return: return a dictionary of parts containing a list of dictionaries with an entry for each part.
        """
        partsfile = os.path.join(DATA_DIR, "info//parts.csv")
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


if __name__ == "__main__":
    c = Console()



