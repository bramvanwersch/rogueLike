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
        self.command_tree = {"set":self.__create_set_tree(),"create":{}, "delete":{}}
        self.screen.scenes["Console"].event_sprite.command_tree = self.command_tree
        #last thing to execute no response after this
        self.run()

    def run(self):
        # Main Loop
        while utilities.going:
            n1 = self.screen.scene.name
            self.screen.scene = self.screen.scenes[utilities.scene_name]
            n2 = self.screen.scene.name
            self.main_sprite = self.screen.scene.event_sprite
            #if a new line is commited in the command window and it is not processed, process it.
            if n2 == "Console":
                # every time the console opens update certain tree lists.
                if n2 == "Console" and n1 != n2:
                    self.__update_tree()
                if not self.main_sprite.processed:
                    self.__process_commands(str(self.main_sprite.process_line))
                    self.screen.scene.event_sprite.processed = True
            GAME_TIME.tick(60)
            self.screen.scene.handle_events(pygame.event.get())
            self.screen.scene.update()
            self.stage.update()
            self.screen.scene.draw()
            pygame.display.update()
        pygame.quit()

    def __update_tree(self):
        #function for things in the tree that need updating. Mostly enemies that change per room.
        self.command_tree["set"]["enemies"] = {str(enemie).lower(): self.__create_attribute_tree(enemie, enemie.attributes()) for enemie in self.stage.enemy_sprite_group.sprites()}

    def __create_set_tree(self):
        tree = {}
        tree["game_rule"] = self.__create_attribute_tree(game_rules, game_rules.attributes())
        tree["player"] = self.__create_attribute_tree(self.screen.player, self.screen.player.attributes())
        tree["enemies"] = {str(enemie).lower(): self.__create_attribute_tree(enemie, enemie.attributes()) for enemie in self.stage.enemy_sprite_group.sprites()}
        return tree

    def __create_attribute_tree(self,target, attributes):
        tree = {}
        for atr in attributes:
            try:
                new_target = getattr(target, atr)
                tree[atr.lower()] = self.__create_attribute_tree(new_target, new_target.attributes())
            except AttributeError:
                tree[atr] = False
        return tree

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
        elif commands[0] == "print":
            self.__process_print(commands[1:])
        else:
            self.main_sprite.add_error_message("No valid command choose one of the following: SET, CREATE, DELETE.")
        #MOVE
        #PRINT

    def __process_set(self, commands):
        if len(commands) < 3:
            self.main_sprite.add_error_message("Expected al least 3 arguments to SET command [FROM, NAME, VALUE].")
            return
        if commands[0] == "game_rule":
            self.__execute(game_rules, commands[1:])
        elif commands[0] == "player":
            self.__execute(self.screen.player, commands[1:])
        elif commands[0] == "enemies":
            for e in self.stage.enemy_sprite_group.sprites():
                if str(e) == commands[1]:
                    break
            self.__execute(e, commands[2:])
        elif commands[0] == "entities":
            pass
        elif commands[0] == "stage":
            pass
        else:
            self.main_sprite.add_error_message("Unknown FROM location. Choose one of the following: game_rule, player, enemys, entities, stage")

    def __process_create(self, commands):
        pass

    def __process_delete(self, commands):
        pass

    def __process_print(self, commands):
        if len(commands) < 3:
            self.main_sprite.add_error_message("Expected al least 3 arguments to SET command [FROM, NAME, VALUE].")
            return

    def __execute(self, target, commands):
        for i, name in enumerate(commands[:-1]):
            if hasattr(target, name):
                if i < len(commands[:-1]) - 1:
                    target = getattr(target, name)
                else:
                    try:
                        value = self.__convert_to_type(type(getattr(target, name)), commands[-1])
                    except ValueError:
                        self.main_sprite.add_error_message("wrong type for {}.{} expected type: {}".format(str(target), commands[0], str(type(getattr(target, name)))))
                        return
                    setattr(target, name, value)
                    self.main_sprite.add_conformation_message("{}.{} is/are set to {}".format(target, commands[-2], commands[-1]))
                    #not neccesairy but should not continue after EVER
                    break
            else:
                self.main_sprite.add_error_message("{} has no attribute {}.".format(target, name))
                break

    def __convert_to_type(self, type, s):
        try:
            if type is bool:
                return self.__string_to_bool(s)
            elif type is int:
                return int(s)
            elif type is float:
                return float(s)
            elif type is list:
                return self.__string_to_list(s)
            elif game_rules.warnings:
                print("No case for value of type {}".format(type))
        except ValueError:
            raise ValueError
        raise ValueError

    def __string_to_bool(self, value):
        if value == "true" or value == "t":
            return True
        elif value == "false" or value == "f":
            return False
        else:
            raise(ValueError)

    def __string_to_list(self, value):
        """
        only a one dimensional list is expected
        """
        if not "[" in value or "(" in value:
            raise ValueError
        value = value.replace("[","").replace("]","")
        the_list = [val.strip() for val in value.split(",")]
        return the_list

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



