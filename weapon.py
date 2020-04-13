#!/usr/bin/env python
# Import Modules
import pygame
import utilities, entities, manufacturers
from game_images import sheets
from pygame.locals import *
from pygame.compat import geterror

class Weapon:
    def __init__(self, parts):
        #default pos will need to be assigned when relevant
        self.parts = parts
        self.image = self.__create_weapon_image()
        self.font25 = pygame.font.Font(utilities.DATA_DIR +"//Menu//font//manaspc.ttf", 25)
        self.damage, self.reload_speed, self.fire_rate, self.weight = self.__calculate_stats()

    def __create_weapon_image(self):
        """
        Create a combined image that includes all the weapon parts.
        :return: an image and repsective rectangle size.
        """
        width = sum(self.parts[key].rect.width for key in ["stock", "body", "barrel"])
        height = sum(self.parts[key].rect.height for key in ["accesory","body","magazine"])
        image = pygame.Surface((width, height))
        image.fill((255,255,255))
        image.blit(self.parts["body"].image, (self.parts["stock"].rect.width,
                                              self.parts["accesory"].rect.height))
        acc_loc = self.parts["stock"].rect.width + self.parts["body"].contact_points[0] - self.parts["accesory"].contact_points[2]
        image.blit(self.parts["accesory"].image, (acc_loc, 0))
        stock_loc = self.parts["accesory"].rect.height + self.parts["body"].contact_points[3] - self.parts["stock"].contact_points[1]
        image.blit(self.parts["stock"].image, (0,stock_loc))
        barrel_loc = self.parts["accesory"].rect.height + self.parts["body"].contact_points[1] - self.parts["barrel"].contact_points[3]
        image.blit(self.parts["barrel"].image, (self.parts["stock"].rect.width + self.parts["body"].rect.width, barrel_loc))
        magazine_loc = self.parts["stock"].rect.width + self.parts["body"].contact_points[2] - self.parts["magazine"].contact_points[0]
        image.blit(self.parts["magazine"].image, (magazine_loc, self.parts["accesory"].rect.height + self.parts["body"].rect.height))
        image = image.convert()
        return image

    def __calculate_stats(self):
        #handle determines the manufactorer of the melee weapon
        manufactorer = manufacturers.get_manufacturer(self.parts["body"].manufacturer)
        damage =  manufactorer.damage
        reload_speed = manufactorer.reload_speed
        fire_rate = manufactorer.fire_rate
        weight = manufactorer.weight
        for part in self.parts:
            damage += self.parts[part].damage
            reload_speed += self.parts[part].reload_speed
            fire_rate += self.parts[part].fire_rate
            weight += self.parts[part].weight
        if damage < 1:
            damage = 1
        if reload_speed < 0.1:
            reload_speed = 0.1
        if fire_rate < 0.5:
            fire_rate = 0.5
        return damage, reload_speed, fire_rate, weight


    def __create_inventory_text(self):
        text_surface = pygame.Surface((900,550))
        text_surface.fill(utilities.BACKGROUND_COLOR)

        name = self.font25.render("Damage:", True, (0,0,0))
        value = self.font25.render(str(self.damage), True, (0,0,0))
        text_surface.blit(name, (0,0))
        text_surface.blit(value, (250, 0))

        name = self.font25.render("Reload speed:", True, (0,0,0))
        value = self.font25.render(str(self.reload_speed), True, (0,0,0))
        text_surface.blit(name, (0,50))
        text_surface.blit(value, (250, 50))

        name = self.font25.render("Attacks/s:", True, (0,0,0))
        value = self.font25.render(str(self.fire_rate), True, (0,0,0))
        text_surface.blit(name, (0,100))
        text_surface.blit(value, (250, 100))

        name = self.font25.render("Weight:", True, (0,0,0))
        value = self.font25.render(str(self.weight), True, (0,0,0))
        text_surface.blit(name, (0,150))
        text_surface.blit(value, (250, 150))

        name = self.font25.render("Parts:", True, (0,0,0))
        text_surface.blit(name, (0,200))

        for i, part in enumerate(self.parts):
            name = self.font25.render(" - {} ({})".format(self.parts[part].name, self.parts[part].manufacturer), True, (0,0,0))
            text_surface.blit(name, (0,250 + 50 * i))
        return text_surface

class WeaponPart:
    def __init__(self, data):
        self.damage,self.reload_speed,self.fire_rate,self.weight, self.accuracy = 0,0,0,0,0
        self.element, self.bullet_pattern, self.bullets_per_shot = None, None, None
        self.type = data["part type"]
        self.name = data["name"]
        self.manufacturer = data["manufacturer"]
        loc = list(int(x) for x in data["rect"].split("-"))
        self.image = sheets["weapons"].image_at((loc[0],loc[1]), color_key= (255,255,255), size = (loc[2], loc[3]))
        self.rect = self.image.get_rect()
        self.__set_data_values(data)

        #order of NESW
        self.contact_points = [None,None,None,None]
        self.__set_contact_points(data)

    def __set_data_values(self, data):
        if "damage" in data:
            self.damage = int(data["damage"])
        if "reload speed" in data:
            self.reload_speed = int(data["reload speed"])
        if "fire rate" in data:
            self.fire_rate = int(data["fire rate"])
        if "weight" in data:
            self.weight = int(data["weight"])
        if "accuracy" in data:
            self.accuracy = int(data["accuracy"])
        if "magazine size" in data:
            self.magazine_size = int(data["magazine size"])
        if "element" in data:
            self.element = data["element"]
        if "bullets per shot" in data:
            self.bullets_per_shot = int(data["bullets per shot"])
        if "bullet pattern" in data:
            self.bullet_pattern = data["bullet pattern"]


    def __set_contact_points(self, data):
        for i, key in enumerate(["N","E","S","W"]):
            if "contact" + key in data:
                #save the average since this is what is going to be used anyway.
                self.contact_points[i] = round(sum(int(x) for x in data["contact" + key].split("-")) / 2)