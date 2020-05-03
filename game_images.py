import os, pygame, random

import entities
from constants import *
from pygame.locals import *
from pygame.compat import geterror

#variable containing all Spritesheets
image_sheets = {}
animations = {}

def load():
    """
    Loads all the available image_sheets into memory and saves them by a descriptive name in a dictionary
    :return:
    """
    global image_sheets

    #images
    image_sheets["player"] = Spritesheet("sprite_sheets\\player_sprite_sheet.bmp", (16, 32))
    image_sheets["forest"] = Spritesheet("sprite_sheets\\forest_stage_sprite_sheet.bmp", (16, 16))
    image_sheets["enemies"] = Spritesheet("sprite_sheets\\enemy_sprite_sheet.bmp", (16, 16))
    image_sheets["weapons"] = Spritesheet("sprite_sheets\\weapons_sprite_sheet.bmp", (16, 16))
    image_sheets["stoner_boss"] = Spritesheet("sprite_sheets\\stoner_boss.bmp", (16,16))

    global animations
    #animations
    #badbat
    bat_move_animation = image_sheets["enemies"].images_at_rectangle((16, 0, 224, 16), pps = PPS_BASE, size=(32, 16), color_key=(255, 255, 255))
    bat_move_animation = bat_move_animation + bat_move_animation[::-1]
    animations["move_BadBat"] = Animation(*bat_move_animation, start_frame="random")

    #bushman
    bush_normal_img = image_sheets["enemies"].image_at((0, 80), pps=PPS_BUSHMAN, size=(16, 16), color_key=(255, 255, 255))
    idle_imgs_bush = image_sheets["enemies"].images_at_rectangle((16, 80, 96, 16), pps=PPS_BUSHMAN, size=(16, 16), color_key=(255, 255, 255))
    wake_imgs_bush = image_sheets["enemies"].images_at_rectangle((112, 80, 48, 16), pps=PPS_BUSHMAN, size=(16, 16), color_key=(255, 255, 255))
    walk_imgs_bush = image_sheets["enemies"].images_at_rectangle((160, 80, 48, 16), pps=PPS_BUSHMAN, size=(16, 16), color_key=(255, 255, 255))
    animations["idle_BushMan"] = Animation(*idle_imgs_bush[:4], idle_imgs_bush[2], *idle_imgs_bush[4:], bush_normal_img, speed=[50, 50, 30, 30, 30, 50, 50, 50], repetition=1)
    animations["wake_BushMan"] = Animation(*idle_imgs_bush[:3], *wake_imgs_bush, speed=10, repetition=1)
    animations["walk_BushMan"] = Animation(walk_imgs_bush[0], walk_imgs_bush[1], walk_imgs_bush[0], walk_imgs_bush[2], speed=10)

    #player
    walking_images_player = image_sheets["player"].images_at((0, 0), (224, 0), (240, 0), (0, 32), (16, 32), color_key=(255, 255, 255), pps=PPS_PLAYER)
    idle_images_player = image_sheets["player"].images_at((0, 0), (176, 0), (192, 0), (208, 0), color_key=(255, 255, 255), pps=PPS_PLAYER)
    dead_images_player = image_sheets["player"].images_at((16, 0), (176, 0), (32, 0), (48, 0), (64, 0), (80, 0), (96, 0), (112, 0), (128, 0), (144, 0), (160, 0), (48, 32), (64, 32), color_key=(255, 255, 255),pps=PPS_PLAYER)
    animations["walk_Player"] = Animation(walking_images_player[0], walking_images_player[1], walking_images_player[2],walking_images_player[1], walking_images_player[0], walking_images_player[3],walking_images_player[4], walking_images_player[3])
    animations["idle_Player"] = MarkedAnimation(idle_images_player[0], idle_images_player[1], idle_images_player[2], idle_images_player[3],idle_images_player[3], idle_images_player[2], idle_images_player[1], idle_images_player[0],speed=40, marked_frames=[2, 3, 4, 5], repetition=1)
    animations["dead_Player"] = MarkedAnimation(*dead_images_player, marked_frames=[3, 4, 5, 6, 7, 8, 9, 10])

    #blowMan
    attack_imgs_blow = image_sheets["enemies"].images_at_rectangle((0,16,48,32), size=(16,32), color_key=(255,255,255), pps=PPS_BLOWMAN)
    walking_imgs_blow = image_sheets["enemies"].images_at_rectangle((96,16,80,32), size=(16,32), color_key=(255,255,255), pps=PPS_BLOWMAN)
    take_weapon_imgs_blow = image_sheets["enemies"].images_at_rectangle((48,16,48,32), size=(16,32), color_key=(255,255,255),pps=PPS_BLOWMAN)
    animations["attack_BlowMan"] = Animation(attack_imgs_blow[0],attack_imgs_blow[1],attack_imgs_blow[0],attack_imgs_blow[2], speed = 20, repetition = 1)
    animations["walk_BlowMan"] = Animation(walking_imgs_blow[0],walking_imgs_blow[1],walking_imgs_blow[2],walking_imgs_blow[1],walking_imgs_blow[0],
                                              walking_imgs_blow[3],walking_imgs_blow[4],walking_imgs_blow[3])
    animations["take_weapon_BlowMan"] = Animation(*take_weapon_imgs_blow[::-1], repetition = 1)
    animations["remove_weapon_BlowMan"] = Animation(*take_weapon_imgs_blow, repetition = 1)

    #Stoner (Boss)
    smile_imgs = image_sheets["stoner_boss"].images_at_rectangle((80,0,160,16), size=(32,16), color_key=(255,255,255), pps = PPS_STONER)
    animations["smile_Stoner"] = 3

def load_image(name, colorkey=None):
    fullname = os.path.join(DATA_DIR, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
        image = image.convert_alpha()
    return image

class Spritesheet:
    def __init__(self, filename, size):
        self.sheet = load_image(filename)
        self.image_size = size

    def image_at(self, coord, color_key = None, scale = None, size = None, pps = None):
        """
        Return an a rectangle from the sprite sheet at a given location
        :param coord: the topleft coordinate of the rectangle
        :param color_key: color to be transparant
        :param scale: the scale of the image in pixels
        :param size: overwrites the self.image_size
        :return: a pygame surface object.
        """
        if size is not None:
            rect = pygame.Rect(*coord, *size)
        else:
            rect = pygame.Rect(*coord, *self.image_size)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pygame.RLEACCEL)
            image = image.convert_alpha()
        if scale is not None:
            image = pygame.transform.scale(image, scale)
        #pixels per scale unit
        elif pps is not None:
            scale = (round(pps * rect.width), round(pps * rect.height))
            image = pygame.transform.scale(image, scale)
        return image

    def images_at(self, *coords, **kwargs):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(coord, **kwargs) for coord in coords]

    def images_at_rectangle(self, *rects, **kwargs):
        """
        specify rectangles from where images need to be extracted. The rectangles need to be multiples of the size
        dimensions
        :param rects: tuple of lenght 4 or pygame.Rect objects
        :param kwargs: the optional variables that can be supplied to the images_at function.
        :return: a list of images in the rectanges in the order of the specified rectangles aswell as
        """
        images = []
        if "size" in kwargs:
            size = kwargs["size"]
        else:
            size = self.image_size
        for rect in rects:
            assert rect[2] % size[0] == 0 and rect[3] % size[1] == 0
            for y in range(int(rect[3] / size[1])):
                for x in range(int(rect[2] / size[0])):
                    images.append(self.image_at((rect[0] + x * size[0],rect[1] + y * size[1]), **kwargs))
        return images

class Animation:
    def __init__(self, *images, speed = 10, repetition ="continuous", start_frame = 0, scale = None):
        """
        Stores an animation to be progressed when calling the update of the animation
        :param images: list of all the images to be played in sequence
        :param speed: the amount of updates needed before the next image is saved
        :param color: the color of the images that need to be transparant
        :param scale: a scale factor to apply to all the animation images
        :param start_frame: the frame to start on or the keyword 'random' to start at a random frame
        """
        if isinstance(images[0], tuple):
            self.animation_images = images
        else:
            flipped_images = [pygame.transform.flip(img, True, False) for img in images]
            self.animation_images = list(zip(images, flipped_images))
        self.set_speed(speed)
        self.frame_count = 0
        self.start_frame = start_frame
        self.__set_current_frame()
        self.image = self.animation_images[self.current_frame]
        self.cycles = 0
        self.repetition = repetition
        self.finished = False

    def update(self):
        """
        Function to be called every update to progress the animation. This methods loops endlesly when called
        """
        #allows for configuring an animation for a certain amount of cycles.
        if not self.repetition == "continuous" and self.cycles >= self.repetition:
            self.finished = True
            #make sure to end and add a flag to allow to stop refreshing.
            return
        self.frame_count += 1
        if self.frame_count % self.speed[self.current_frame] == 0:
            self.current_frame += 1
            self.frame_count = 0
        if self.current_frame >= len(self.animation_images):
            self.current_frame = 0
            self.cycles += 1
            return
        self.image = self.animation_images[self.current_frame]

    def __set_current_frame(self):
        if self.start_frame == "random":
            self.current_frame = random.randint(0,len(self.animation_images) -1)
        else:
            self.current_frame = self.start_frame

    def reset(self):
        """
        resets the animation to the beginning state
        """
        self.frame_count = 0
        self.__set_current_frame()
        self.image = self.animation_images[0]
        self.cycles = 0
        self.finished = False

    def set_speed(self, speed):
        if isinstance(speed, list):
            assert len(speed) == len(self.animation_images)
            self.speed = speed
        else:
            self.speed = [speed]* len(self.animation_images)

    def scale(self, scale):
        """
        Function for rescaling animations when the size of an entity is changed
        :param scale: a tuple of lenght 2 that defines to waht dimensions the image has to be scaled. Repeaded scaling will morph the images
        :return:
        """
        for i, images in enumerate(self.animation_images):
            self.animation_images[i] = (pygame.transform.scale(images[0], scale),pygame.transform.scale(images[1], scale))


    def copy(self):
        return Animation(*self.animation_images, speed = self.speed, repetition=self.repetition, start_frame=self.start_frame)

class MarkedAnimation(Animation):
    def __init__(self, *images, marked_frames = [], **kwargs):
        """
        allows some marked frames that then can be tracked by the marked property
        :param marked_frames: a list of integers of marked frames
        """
        Animation.__init__(self, *images, **kwargs)
        #list of frames that can be tracked by the special property
        self.marked_frames = marked_frames
        self.marked = False

    def update(self):
        super().update()
        if self.current_frame in self.marked_frames:
            self.marked = True
        else:
            self.marked = False

    def reset(self):
        super().reset()
        self.marked = False

    def copy(self):
        return MarkedAnimation(*self.animation_images, speed = self.speed, repetition=self.repetition, start_frame=self.start_frame, marked_frames = self.marked_frames)