#!/usr/bin/env python
import os, pygame, random, inspect, re

from constants import game_rules, GAME_TIME, DATA_DIR, SCREEN_SIZE
import main, utilities, stages, weapon, game_images, entities, prop_entities, bosses
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
        self.command_tree = {"set":self.__create_set_tree(),"create":self.__create_create_tree(), "delete":{},
                             "print":self.__create_print_tree(),"scripts": self.__create_script_tree()}
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
            if n2 == "Console":
                # every time the console opens update certain tree lists.
                if n2 == "Console" and n1 != n2:
                    self.__update_tree()
                # if a new line is commited in the command window and it is not processed, process it.
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
        self.command_tree["set"]["room_entities"] = {str(enemie): self.__create_attribute_tree(enemie, enemie.attributes(), func = "attributes") for enemie in self.stage.room_group.sprites()}
        self.command_tree["print"]["room_entities"] = {str(enemie): self.__create_attribute_tree(enemie, vars(enemie)) for enemie in self.stage.room_group.sprites()}

    def __create_set_tree(self):
        tree = {}
        tree["game_rule"] = self.__create_attribute_tree(game_rules, game_rules.attributes(), func = "attributes")
        tree["player"] = self.__create_attribute_tree(self.screen.player, self.screen.player.attributes(), func = "attributes")
        tree["room_entities"] = {str(enemie): self.__create_attribute_tree(enemie, enemie.attributes(), func = "attributes") for enemie in self.stage.room_group.sprites()}
        #assumes all class variables are upper case and no methods are.
        tree["entities"] = self.__get_class_variables(entities, prop_entities, bosses)
        return tree

    def __create_print_tree(self):
        tree = {}
        tree["game_rule"] = self.__create_attribute_tree(game_rules, vars(game_rules))
        tree["player"] = self.__create_attribute_tree(self.screen.player, vars(self.screen.player).keys())
        tree["room_entities"] = {str(enemie): self.__create_attribute_tree(enemie, vars(enemie)) for enemie in self.stage.room_group.sprites()}
        tree["entities"] = self.__get_class_variables(entities, prop_entities, bosses)
        tree["stage"] = self.__create_attribute_tree(self.stage, vars(self.stage))
        tree["weapon"] = {key: {name: self.__create_attribute_tree(val, vars(val)) for name, val in self.weapon_parts[key].items()} for key in self.weapon_parts.keys()}
        return tree

    def __create_create_tree(self):
        tree = {}
        tree["weapon"] = {key: {part : "create weapon" for part in self.weapon_parts[key]} for key in self.weapon_parts.keys()}
        tree["entity"] = {class_name[0]: False for module in [entities, prop_entities, bosses] for class_name in inspect.getmembers(module, inspect.isclass)   }
        return tree

    def __create_script_tree(self):
        partsfile = os.path.join(DATA_DIR, "scripts.sf")
        f = open(partsfile, "r")
        lines = f.readlines()
        f.close()
        tree = {}
        for line in lines:
            name, command_line = line.split(":")
            tree[name] = command_line
        return tree

    def __get_class_variables(self, *modules):
        ent_dict = {}
        for module in modules:
            for name in inspect.getmembers(module, inspect.isclass):
                class_varaibles = {}
                for val in dir(name[1]):
                    if val.isupper() and not val.startswith("_"):
                        class_varaibles[val] = False
                if len(class_varaibles) > 0:
                    ent_dict[name[0]] = class_varaibles
        return ent_dict

    def __create_attribute_tree(self, target, attributes, func = None):
        tree = {}
        for atr in attributes:
            try:
                new_target = getattr(target, atr)
                if func:
                    atr_func = getattr(new_target, func)
                    new_attributes = atr_func()
                else:
                    new_attributes = vars(new_target)
                tree[atr.lower()] = self.__create_attribute_tree(new_target, new_attributes, func = func)
            except(AttributeError, TypeError):
                tree[atr] = False
        return tree

    def __process_commands(self, text):
        try:
            commands_list = self.__text_to_commands(text)
        except ValueError as e:
            self.main_sprite.add_error_message(str(e))
            return
        for commands in commands_list:
            commands = commands.strip().split(" ")
            if commands[0] == "set":
                self.__process(commands)
            elif commands[0] == "create":
                self.__process_create(commands)
            elif commands[0] == "delete":
                self.__process_delete(commands)
            elif commands[0] == "print":
                #make sure that the last part of the command is executed.
                self.__process(commands + [" "])
            elif commands[0] == "scripts":
                if commands[1] in self.command_tree["scripts"]:
                    self.__process_commands(self.command_tree["scripts"][commands[1]])
                else:
                    self.main_sprite.add_error_message("No script known by name {}".format(commands[1]))
            else:
                self.main_sprite.add_error_message("{} is not a valid command. Choose one of the following: set, delete, create, print.".format(commands[0]))

    def __text_to_commands(self, text):
        text = text.strip()
        lists = {}
        tuples = {}
        if text.count("]") != text.count("["):
            raise ValueError("Uneven amount of open and closing brackets.")
        #first get all lists within lists
        count = 0
        while True:
            matches = re.findall("\[[^\[]+?\]", text)
            if matches:
                for match in matches:
                    text = text.replace(match, ",list" + str(count))
                    lists["list" + str(count)] = match
                    count += 1
            else:
                break
        #then get all commands conveyed by those lists
        return self.__get_command_list(text, lists)

    def __get_command_list(self, text, lists):
        text = text.split(",")
        fl = []
        for i in range(len(text)):
            if text[i] in lists:
                text[i] = self.__get_command_list(lists[text[i]][1:-1], lists)
                for val in text[i]:
                    combined = text[i - 1].strip() + " " + val.strip()
                    fl.append(combined)
                    #remove the shorter version from the final_list
                    if text[i-1] in fl:
                        fl.remove(text[i-1])
            else:
                fl.append(text[i])
        return fl

    def __process(self, commands):
        if len(commands) < 3:
            self.main_sprite.add_error_message("Expected al least 3 arguments to SET command [FROM, NAME, VALUE].")
            return
        if commands[1] == "game_rule":
            self.__execute(game_rules, commands)
        elif commands[1] == "player":
            self.__execute(self.screen.player, commands)
        elif commands[1] == "room_entities":
            enemie = None
            for e in self.stage.room_group.sprites():
                if str(e) == commands[2]:
                    enemie = e
                    break
            if enemie:
                self.__execute(enemie, commands, 2)
            else:
                self.main_sprite.add_error_message("Unknown enemy {}.".format(commands[2]))
        elif commands[1] == "entities":
            correct_class = None
            for c in inspect.getmembers(entities, inspect.isclass):
                if c[0] == commands[2]:
                    correct_class = c[1]
                    break
            if correct_class:
                self.__execute(correct_class, commands, 2)
            else:
                self.main_sprite.add_error_message("Unknown entity class {}.".format(commands[2]))
        elif commands[1] == "stage":
            self.__execute(self.stage, commands)
        elif commands[1] == "weapon":
            self.__execute(self.weapon_parts[commands[2]][commands[3]], commands, 3)
        else:
            self.main_sprite.add_error_message("{} is not a valid FROM location. Choose one of the following: game_rule, player, room_entities, entities".format(commands[1]))

    def __execute(self, target, commands, from_l = 1):
        for i, name in enumerate(commands[1 + from_l:-1]):
            if hasattr(target, name):
                if i < len(commands[1 + from_l:-1]) - 1:
                    target = getattr(target, name)
                else:
                    if commands[0] == "set":
                        try:
                            value = self.__convert_to_type(type(getattr(target, name)), commands[-1],
                                                           getattr(target, name), target)
                        except ValueError as e:
                            self.main_sprite.add_error_message(str(e))
                            return
                        if type(getattr(target, name)) is property:
                            getattr(target, name).fset(target, value)
                        else:
                            setattr(target, name, value)
                        self.main_sprite.add_conformation_message("{} is set to {}".format(".".join(commands[1:-1]), value))
                    elif commands[0] == "print":
                        val = getattr(target, name)
                        if type(val) is property:
                            val = getattr(target, name).fget(target)
                        self.main_sprite.add_conformation_message("The value of {} is: {}".format(".".join(commands[1:-1]), val))
            else:
                self.main_sprite.add_error_message("{} has no attribute {}.".format(target, name))
                break

    def __convert_to_type(self, type_s, s, orig_value = None, target = None):
        try:
            if type_s is str:
                return s
            elif type_s is bool:
                return self.__string_to_bool(s)
            elif type_s is int:
                return int(s)
            elif type_s is float:
                return float(s)
            elif type_s is list:
                return self.__string_to_list(s, [type(val) for val in orig_value])
            elif type_s is tuple:
                return self.__string_to_list(s, [type(val) for val in orig_value])
            elif type_s is property:
                return self.__convert_to_type(type(orig_value.fget(target)), s)
            elif game_rules.warnings:
                print("No case for value of type_s {}".format(type_s))
        except ValueError as e:
            raise e
        raise ValueError("cannot convert to type_s {}. No known method.".format(type_s))

    def __string_to_bool(self, value):
        value = value.lower()
        if value == "true" or value == "t":
            return True
        elif value == "false" or value == "f":
            return False
        else:
            raise ValueError("expected a boolean to be either: true, t, false or f (case insensitive)".format(value))

    def __string_to_list(self, value, types):
        """
        only a one dimensional list is expected
        """
        if not "(" in value:
            raise ValueError("expected a list to be of form (val1;val2;..)")
        value = value.replace("(", "").replace(")", "")
        the_list = [val.strip() for val in value.split(";")]
        if len(types) != len(the_list):
            raise ValueError("list is of wrong length. Expected a list of lenght {}.".format(len(types)))
        for i, val_type in enumerate(types):
            try:
                user_value = the_list[i]
                if val_type != str:
                    user_value = user_value.strip()
                correct_typed_value = self.__convert_to_type(val_type, user_value)
                the_list[i] = correct_typed_value
            except ValueError:
                raise ValueError("expected value of type {} at index {}. Cannot convert {} to {}.".format(val_type, i,the_list[i],val_type))
        return the_list

    def __process_create(self, commands):
        try:
            if commands[1] == "weapon":
                self.__create_weapon(commands)
            elif commands[1] == "entity":
                self.__create_entity(commands)
            else:
                self.main_sprite.add_error_message("{} is not a valid WHAT location. Choose one of the following: weapon, entity".format(commands[1]))
        except ValueError as e:
            self.main_sprite.add_error_message(str(e))

    def __create_weapon(self, commands):
        weapon_parts = {"body": "Random", "barrel": "Random", "stock": "Random", "magazine": "Random", "accesory": "Random"}
        if len(commands) % 2 != 0:
            raise ValueError("When specifying a weapon part also specify the name.")
        for i in range(2, len(commands), 2):
            part = commands[i]
            part_name = commands[i+1]
            weapon_parts[part] = part_name
        weapon = self.get_weapon_by_parts(weapon_parts)
        prop_entities.LootableWeapon(self.screen.player.rect.center, self.screen.player, weapon, self.screen.game_sprites)
        self.main_sprite.add_conformation_message("The following weapon was created: {}".format(str(weapon)))

    def __create_entity(self, commands):
        if len(commands) < 4:
            raise ValueError("Expected at least 4 commands CREATE WHAT NAME LOCATION.")
        try:
            location = self.__string_to_list(commands[3], [int,int])
        except ValueError as e:
            raise ValueError("Incorrect location format. {}".format(str(e)))
        self.stage.add_enemy(commands[2], location)
        self.main_sprite.add_conformation_message("Added entity {} at x:{} y:{}".format(commands[2], *location))

    def __process_delete(self, commands):
        pass

    def __load_parts(self):
        """
        Pre loads the immages defined for the weapon parts
        :return: return a dictionary of parts containing a list of dictionaries with an entry for each part.
        """
        partsfile = os.path.join(DATA_DIR, "parts.csv")
        f = open(partsfile, "r")
        lines = f.readlines()
        f.close()
        body, barrel, stock, magazine, accesory = {}, {}, {}, {}, {}
        projectileweaponparts = {"body": body, "barrel": barrel, "stock": stock, "magazine": magazine, "accesory": accesory}
        # first line is descriptors
        dictnames = list(x.strip() for x in lines[0].replace("\n", "").split(","))
        for line in lines[1:]:
            information = line.replace("\n", "").split(",")
            data = {dictnames[x]: i.strip() for x, i in enumerate(information) if i.strip()}
            if data["type"] == "body":
                body[data["name"]] = weapon.WeaponPart(data)
            elif data["type"] == "barrel":
                barrel[data["name"]] = weapon.WeaponPart(data)
            elif data["type"] == "stock":
                stock[data["name"]] = weapon.WeaponPart(data)
            elif data["type"] == "magazine":
                magazine[data["name"]] = weapon.WeaponPart(data)
            elif data["type"] == "accesory":
                accesory[data["name"]] = weapon.WeaponPart(data)
        return projectileweaponparts

    def get_random_weapon(self):
        weapon_parts = {"body": None, "barrel": None, "stock": None, "magazine": None, "accesory": None}
        for part_group in self.weapon_parts.keys():
            part_list = list(self.weapon_parts[part_group].values())
            weapon_parts[part_group] = random.choice(part_list)
        return weapon.Weapon(weapon_parts)

    def get_weapon_by_parts(self, part_names):
        weapon_parts = {"body": None, "barrel": None, "stock": None, "magazine": None, "accesory": None}
        for part, item_name in part_names.items():
            if item_name in ["Random", None, ""] :
                part_list = list(self.weapon_parts[part].values())
                weapon_parts[part] = random.choice(part_list)
            else:
                weapon_parts[part] = self.weapon_parts[part][item_name]
        return weapon.Weapon(weapon_parts)

if __name__ == "__main__":
    c = Console()



