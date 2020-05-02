import pygame, random
from pygame.locals import *
import utilities, entities, game_map, prop_entities, constants
from game_images import image_sheets
import numpy as np

MIN_LEAF_SIZE = 4
MAX_LEAF_SIZE = 10
MAX_ROOMS = 12

def build_map(size, **kwargs):
    #TODO add things to make the randomisation more random, equal x y sides and chortest path direction
    game_map = [[0 for _ in range(size[0])] for _ in range(size[1])]
    scx, scy = random.randint(0, size[0] - 1), random.randint(0, int(size[1] * (1/3)))
    ecx, ecy = random.randint(0, size[0] - 1), size[1] - 1 - random.randint(0, int(size[1] * (1/3)))
    game_map[scy][scx] = 2
    game_map[ecy][ecx] = -1
    #generate simplest path
    dx = ecx - scx
    dy = ecy - scy
    for i in range(1,abs(dx) + 1):
        if dx < 0:
            i *= -1
        game_map[scy][scx + i] = 1
    for i in range(1,abs(dy)):
        if dy < 0:
            i *= -1
        game_map[scy + i][scx + dx] = 1
    total_rooms = 0
    for row in game_map:
        for value in row:
            if value != 0:
                total_rooms += 1
    # draw random points on the map and connect to existing rooms while there are less then certain amount of rooms
    assert MAX_ROOMS <= size[0] * size[1]
    while total_rooms < MAX_ROOMS:
        point = (random.randint(0, size[0] -1),random.randint(0, size[1] -1))
        extra_rooms = 1
        if game_map[point[1]][point[0]] == 0:
            game_map[point[1]][point[0]] = -9
            #while not connected
            while True:
                surrounding_points = []
                if point[1] - 1 >= 0:
                    if game_map[point[1] -1][point[0]] > 0:
                        break
                    elif game_map[point[1] -1][point[0]] == 0:
                        surrounding_points.append((point[0], point[1] - 1))
                if point[0] + 1 < len(game_map[0]):
                    if game_map[point[1]][point[0] + 1] > 0:
                        break
                    elif game_map[point[1]][point[0] + 1] == 0:
                        surrounding_points.append((point[0] + 1, point[1]))
                if point[1] + 1 < len(game_map):
                    if game_map[point[1] + 1][point[0]] > 0:
                        break
                    elif game_map[point[1] +1][point[0]] == 0:
                        surrounding_points.append((point[0], point[1] + 1))
                if point[0] - 1 >= 0:
                    if game_map[point[1]][point[0] - 1] > 0:
                        break
                    elif game_map[point[1]][point[0] - 1] == 0:
                        surrounding_points.append((point[0] - 1, point[1]))
                if not surrounding_points:
                    break
                point = random.choice(surrounding_points)
                game_map[point[1]][point[0]] = -9
                extra_rooms += 1
            #replace all -9s by 1s
            for y, row in enumerate(game_map):
                for x, value in enumerate(row):
                    if value == -9:
                        game_map[y][x] = 1
        total_rooms += extra_rooms
    # create room layouts by changing all values that are not 0 into room instances
    for y, row in enumerate(game_map):
        for x, value in enumerate(row):
            if value == 1:
                room = Room(pygame.Rect(x, y, int(constants.DEFAULT_LEVEL_SIZE.width / 100),
                                        int(constants.DEFAULT_LEVEL_SIZE.height / 100)), value,
                            get_connecting_rooms(game_map, (x,y)), **kwargs)
            elif value == 2:
                room = StartingRoom(pygame.Rect(x, y, int(constants.DEFAULT_LEVEL_SIZE.width / 200),
                                                int(constants.DEFAULT_LEVEL_SIZE.height / 200)), value,
                                    get_connecting_rooms(game_map, (x,y)), **kwargs)
            elif value == -1:
                room = BossRoom(pygame.Rect(x, y, int(constants.DEFAULT_LEVEL_SIZE.width / 100),
                                            int(constants.DEFAULT_LEVEL_SIZE.height / 100)), value,
                                get_connecting_rooms(game_map, (x,y)), **kwargs)
            else:
                continue
            game_map[y][x] = room
    # if utilities.warnings:
    #     print("Room with value -1 is not handled yet.")
    return game_map

def get_connecting_rooms(game_map, point):
    """
    Figures out what rooms are next to the room at point that need to be connected with a path.
    :param game_map: matrix representation of the room layout
    :param point: an x,y point within the coordinates of the game map that tells the location of the current room being
    evaluated
    :return: an array of lenght 4 that has True when there is a connection in the order [up, right, down, left]
    """
    surrounding_points = [False, False, False, False]
    if point[1] - 1 >= 0 and game_map[point[1] - 1][point[0]] != 0:
        surrounding_points[0] = True
    if point[0] + 1 < len(game_map[0]) and game_map[point[1]][point[0] + 1] != 0:
        surrounding_points[1] = True
    if point[1] + 1 < len(game_map) and game_map[point[1] + 1][point[0]] != 0:
        surrounding_points[2] = True
    if point[0] - 1 >= 0 and game_map[point[1]][point[0] - 1] != 0:
        surrounding_points[3] = True
    return surrounding_points

class Room:
    def __init__(self, rect, room_type, connections, **kwargs):
        """
        Class for creating a full room including the background and pictures associated with it.
        :param rect: The rectangle where the room is located. The coordinate of the room is te location on the map
        :param room_type: the name of the room
        :param connections: list of lenght 4 telling the coordinates of a connected room or False when there is no
        connection
        :param room_layout: matrix of numbers signifying where solid tiles are located
        :param kwargs: list of optional parameters, mainly parameters for pictures to used to make the rooms.
        """
        self.rect = rect
        self.room_type = room_type
        self.room_layout = RoomLayout(self.rect, connections, **kwargs)
        #for convenience
        self.tiles = self.room_layout.tiles
        self.connections = self.room_layout.connections
        self.enemies = self._choose_enemies(kwargs["enemies"], kwargs["spawn_weights"],kwargs["spawn_amnt_range"])
        self.finished = False

    def _choose_enemies(self, enemies, spawn_weights, spawn_amnt_range):
        enemie_choices = utilities.get_wheighted_array(enemies, spawn_weights)
        enemies = []
        for _ in range(random.randint(*spawn_amnt_range)):
            enemie_choice  = random.choice(enemie_choices)
            collide = True
            #random a location until the enemy fits
            while collide:
                test_rect = pygame.Rect(random.randint(0,self.rect.width * 100), random.randint(0,self.rect.height * 100),
                                        *enemie_choice[1])
                collide = self.tiles.solid_collide(test_rect, False)
            enemies.append([enemie_choice[0], test_rect.topleft])
        return enemies

class StartingRoom(Room):
    def __init__(self, rect, room_type, connections, **kwargs):
        #change anything about the kwargs
        kwargs["room_layout"] = self.__get_room_layout(rect)
        Room.__init__(self, rect, room_type, connections, **kwargs)
        #kind of cheaty way of doing this. --> resetting the enemies to empty
        self.enemies = []

    def __get_room_layout(self, rect):
        layout = [[0] * rect.width for _ in range(rect.height)]
        for y in range(rect.height):
            for x in range(rect.width ):
                if y == 0 or y == rect.height - 1 or x == 0 or x == rect.width - 1:
                    layout[y][x] = 1
        return layout

class BossRoom(Room):
    def __init__(self, rect, room_type, connections, **kwargs):
        kwargs["room_layout"] = self.__get_room_layout(rect)
        kwargs["spawn_amnt_range"] = [kwargs["spawn_amnt_range"][0] + 10, kwargs["spawn_amnt_range"][1] + 10]
        Room.__init__(self, rect, room_type, connections, **kwargs)
        self.enemies = random.choice(kwargs["bosses"])

    def __get_room_layout(self, rect):
        layout = [[0] * rect.width for _ in range(rect.height)]
        for y in range(rect.height):
            for x in range(rect.width ):
                if y == 0 or y == rect.height - 1 or x == 0 or x == rect.width - 1:
                    layout[y][x] = 1
        return layout

class RoomLayout:
    def __init__(self, rect, connections, **kwargs):
        self.rect = rect
        #value tracked here for easy ways of changing. At this point just tracks a constant
        self.f_offset = 0.25
        self.propnmbr = 50
        self.connections = [False,False,False,False]
        #specify your own layout for certain rooms.
        if "room_layout" in kwargs:
            room_layout = kwargs["room_layout"]
        else:
            room_layout = self.build_room_map(kwargs["solid_tile_weights"])
        room_layout_and_path = self.add_path(room_layout, connections, len(kwargs["solid_tile_names"]) + 1)
        self.room_layout = self.determine_pictures(room_layout_and_path, len(kwargs["solid_tile_names"]))
        self.tiles = TileGroup((self.rect.width, self.rect.height))
        self.__create_tiles(kwargs["tile_images"], list(kwargs["solid_tile_names"] + ["path"]))
        self.tiles.setup()
        self.background_image = self.__create_background_image(kwargs["background_images"])
        self.room_image = self.__create_props_and_tiles_image(kwargs["props"])

    # split up a room using binary space partinioning and create a randomized room
    def build_room_map(self, wheights=[1]):
        did_split = True
        leafs = [Leaf((0, 0), (
        int((self.rect.width * constants.TILE_SIZE[0] - 200) / 100), int((self.rect.height * constants.TILE_SIZE[1] - 200) / 100)))]
        while did_split:
            did_split = False
            for l in leafs:
                if l.left_leaf == None and l.rigth_leaf == None:
                    if l.rect.width > MAX_LEAF_SIZE or l.rect.height > MAX_LEAF_SIZE or random.randint(1, 4) == 1:
                        if l.split():
                            leafs.append(l.rigth_leaf)
                            leafs.append(l.left_leaf)
                            did_split = True
        # create wheighted array for consistent random with a seed.
        wheighted_array = utilities.get_wheighted_array([1, 2], wheights)
        leafs[0].create_blob(wheighted_array)
        final_map = leafs[0].get_map()
        # create border around map.
        for i, row in enumerate(final_map):
            final_map[i] = [1] + row + [1]
        final_map = [[1] * len(final_map[0])] + final_map + [[1] * len(final_map[0])]
        return final_map

    def add_path(self, room_layout, connections, amnt_stage_names):
        """
        Generates a path that connects rooms. The function chooses a coordinate on the side of the room within a range
        and a middle coordinate for the path to move towards. It stops generatign new path blocks when it hits a path
        block or finds the middle coordinate
        :param room_layout: a map that has the layout of the room
        :param connections: a boolean tuple of lenght 4 telling if there is a connecting room or not in order N,E,S,W
        :param amnt_stage_names: an integer that tells how many different textures there are for the blobs. The paths
        get a number one bigger then this one.
        :return: the room layout matrix with an extra path
        """
        #middle of room
        xl, yl = round(self.rect.width / 2) - 1,round(self.rect.height / 2) - 1
        #take a center that is offset slightly from the actual center to make the paths connect to.
        target_center = (xl + random.randint(-1 * round(xl* self.f_offset), round(xl * self.f_offset)),
                         yl + random.randint(-1 * round(yl* self.f_offset), round(yl * self.f_offset)))
        #for each connection that a room has there is a path connected from the side of the room to the target center.
        for num, connection in enumerate(connections):
            if not connection:
                continue
            # coordinates that signify the startpoint of the path
            y0, x0 = 0, 0
            horizontal = True
            #setting the restrictions for choosing path
            if num in [1,3]:
                #halfway trough the room
                y0 = yl + random.randint(-1 * round(yl* self.f_offset), round(yl * self.f_offset))
                if num == 1:
                    x0 = self.rect.width - 1
                self.connections[num] = (x0, y0)
            else: # 0 or 2
                x0 = xl + random.randint(-1 * round(xl* self.f_offset), round(xl * self.f_offset))
                horizontal = False
                if num == 2:
                    y0 = self.rect.height - 1
                self.connections[num] = (x0, y0)
            dx = target_center[0] - x0
            dy = target_center[1] - y0
            if horizontal:
                for i in range(abs(dx)):
                    if dx < 0:
                        i *= -1
                    if room_layout[y0][x0 + i] == amnt_stage_names:
                        break
                    room_layout[y0][x0 + i] = amnt_stage_names
                for i in range(abs(dy) + 1):
                    if dy < 0:
                        i *= - 1
                    if room_layout[y0 + i][x0 + dx] == amnt_stage_names:
                        break
                    room_layout[y0 + i][x0 + dx] = amnt_stage_names
            #when going from top to bottom first draw the vertical line then the horizontal one from where the vertical
            #ended
            else:
                for i in range(abs(dy)):
                    if dy < 0:
                        i *= -1
                    if room_layout[y0 + i][x0] == amnt_stage_names:
                        break
                    room_layout[y0 + i][x0] = amnt_stage_names
                for i in range(abs(dx) + 1):
                    if dx < 0:
                        i *= -1
                    if room_layout[y0 + dy][x0 + i] == amnt_stage_names:
                        break
                    room_layout[y0 + dy][x0 + i] = amnt_stage_names
        return room_layout

    def determine_pictures(self, room_layout, amnt_stage_names):
        """
        Determine the pictures that should go in place for each generated tile. Add numbers that determine the texture of
        the pictures
        :param room_map: a matrix that represents the game map. 0 is no tile 1 and higher is a specific texture tile.
        :return: a matrix of the same dimensions now filled  in with string where there were numbers other then zero for the
        texture of each of these tiles.
        """
        #copy the pictures into a new map to make sure that calculations can be perforemed correctly using the numbers
        picture_map = [[0 for x in range(len(room_layout[0]))] for y in range(len(room_layout))]
        for y, row in enumerate(room_layout):
            for x, number in enumerate(row):
                if number != 0:
                    st = [0, 0, 0, 0]
                    if y - 1 < 0 or room_layout[y - 1][x] == number:
                        st[0] = 1
                    if x + 1 >= len(row) or room_layout[y][x + 1] == number:
                        st[1] = 1
                    if y + 1 >= len(room_layout) or room_layout[y + 1][x] == number:
                        st[2] = 1
                    if x - 1 < 0 or room_layout[y][x - 1] == number:
                        st[3] = 1
                    name = self.__get_picture_code(st)
                    #list of tiles that should not be regarded
                    empty_tiles = [0, amnt_stage_names + 1]
                    if name == "m" and number <= amnt_stage_names :
                        if y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_layout) and x + 1 < len(row) \
                                and room_layout[y - 1][x - 1] != number and room_layout[y + 1][x + 1] != number:
                            name = "tbd"
                        elif y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_layout) and x + 1 < len(row) \
                                and (room_layout[y - 1][x + 1] != number) and (room_layout[y + 1][x - 1] != number):
                            name = "btd"
                        elif y + 1 < len(room_layout) and x - 1 >= 0 and (room_layout[y + 1][x - 1] != number):
                            name = "blic"
                        elif y + 1 < len(room_layout) and x + 1 < len(row) and (room_layout[y + 1][x + 1] != number):
                            name = "bric"
                        elif y - 1 >= 0 and x + 1 < len(row) and (room_layout[y - 1][x + 1] != number):
                            name = "tric"
                        elif y - 1 >= 0 and x - 1 >= 0 and (room_layout[y - 1][x - 1] != number):
                            name = "tlic"
                    elif name == "rs" and number <= amnt_stage_names :
                        if y - 1 >= 0 and x - 1 >= 0 and x + 1 < len(row) \
                                and room_layout[y - 1][x - 1] != number and room_layout[y][x + 1] != number:
                            name = "rtlc"
                        elif y + 1 < len(room_layout) and x - 1 >= 0 and x + 1 < len(row) \
                                and room_layout[y + 1][x - 1] != number and room_layout[y][x + 1] != number:
                            name = "rblc"
                    elif name == "bs" and number <= amnt_stage_names :
                        if y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_layout) \
                                and room_layout[y - 1][x - 1] != number and room_layout[y + 1][x] != number:
                            name = "btlc"
                        elif y - 1 >= 0 and x + 1 < len(row) and y + 1 < len(room_layout) \
                                and room_layout[y - 1][x + 1] != number and room_layout[y + 1][x] != number:
                            name = "btrc"
                    elif name == "ls" and number <= amnt_stage_names:
                        if y - 1 >= 0 and x - 1 >= 0 and x + 1 < len(row) \
                                and room_layout[y - 1][x + 1] != number and room_layout[y][x - 1] != number:
                            name = "ltrc"
                        elif y + 1 < len(room_layout) and x - 1 >= 0 and x + 1 < len(row) \
                                and room_layout[y + 1][x + 1] != number and room_layout[y][x - 1] != number:
                            name = "lbrc"
                    elif name == "ts" and number <= amnt_stage_names:
                        if y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_layout) \
                                and room_layout[y + 1][x - 1] != number and room_layout[y - 1][x] != number:
                            name = "tblc"
                        elif y - 1 >= 0 and x + 1 < len(row) and y + 1 < len(room_layout) \
                                and room_layout[y + 1][x + 1] != number and room_layout[y - 1][x] != number:
                            name = "tbrc"

                    picture_map[y][x] = name + str(number)
        return picture_map

    def __get_picture_code(self, st):
        """
        Determine a picture code based on the four surrounding tiles.
        :param st: an array of lenght 4 containing a 1 if a there is another solid tile NESW or 0 otherwise
        :return: a str code that telss what type of image needs to be in place
        """
        if st == [1, 1, 0, 0]:
            return "blc"
        if st == [0, 1, 1, 0]:
            return "tlc"
        if st == [0, 0, 1, 1]:
            return "trc"
        if st == [1, 0, 0, 1]:
            return "brc"
        if st == [1, 1, 1, 0]:
            return "ls"
        if st == [0, 1, 1, 1]:
            return "ts"
        if st == [1, 0, 1, 1]:
            return "rs"
        if st == [1, 1, 0, 1]:
            return "bs"
        if st == [1, 0, 0, 0]:
            return "tsc"
        if st == [0, 1, 0, 0]:
            return "rsc"
        if st == [0, 0, 1, 0]:
            return "bsc"
        if st == [0, 0, 0, 1]:
            return "lsc"
        if st == [0, 0, 0, 0]:
            return "sin"
        if st == [1, 0, 1, 0]:
            return "tab"
        if st == [0, 1, 0, 1]:
            return "ral"
        return "m"

    def __create_tiles(self, tile_images, stage_names):
        """
        Add solid tiles to the tile group (self.tiles) with adding the tiles the pictures are also configured
        :param tile_images: dictionary with image names for the solid tiles
        :param stage_names: names corresponding to the numbers appended to the end of the string notifying what type of
        image needs to be associated with the solid tile.
        """
        for y, line in enumerate(self.room_layout):
            for x, letter in enumerate(line):
                image = None
                if letter != 0:
                    number = int(letter[-1]) -1
                    letter = letter[:-1]
                if letter == "blc":
                    image = tile_images["bottom_left_corner_" + stage_names[number]]
                elif letter == "tlc":
                    image = tile_images["top_left_corner_" + stage_names[number]]
                elif letter == "trc":
                    image = tile_images["top_right_corner_" + stage_names[number]]
                elif letter == "brc":
                    image = tile_images["bottom_right_corner_" + stage_names[number]]
                elif letter == "blic":
                    image = tile_images["bottom_left_icorner_" + stage_names[number]]
                elif letter == "tlic":
                    image = tile_images["top_left_icorner_" + stage_names[number]]
                elif letter == "tric":
                    image = tile_images["top_right_icorner_" + stage_names[number]]
                elif letter == "bric":
                    image = tile_images["bottom_right_icorner_" + stage_names[number]]
                elif letter == "ls":
                    image = random.choice([tile_images[key] for key in tile_images if "left_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "ts":
                    image = random.choice([tile_images[key] for key in tile_images if "top_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "rs":
                    image = random.choice([tile_images[key] for key in tile_images if "right_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "bs":
                    image = random.choice([tile_images[key] for key in tile_images if "bottom_straight" in \
                                           key and stage_names[number] in key])
                elif letter == "m":
                    image = random.choice([tile_images[key] for key in tile_images if "middle" in \
                                           key and stage_names[number] in key])
                elif letter == "tbd":
                    image = tile_images["diagonal_top_bottom_" + stage_names[number]]
                elif letter == "btd":
                    image = tile_images["diagonal_bottom_top_" + stage_names[number]]
                elif letter == "btrc":
                    image = tile_images["bottom_top_right_corner_" + stage_names[number]]
                elif letter == "btlc":
                    image = tile_images["bottom_top_left_corner_" + stage_names[number]]
                elif letter == "rtlc":
                    image = tile_images["right_top_left_corner_" + stage_names[number]]
                elif letter == "rblc":
                    image = tile_images["right_bottom_left_corner_" + stage_names[number]]
                elif letter == "ltrc":
                    image = tile_images["left_top_right_corner_" + stage_names[number]]
                elif letter == "lbrc":
                    image = tile_images["left_bottom_right_corner_" + stage_names[number]]
                elif letter == "tblc":
                    image = tile_images["top_bottom_left_corner_" + stage_names[number]]
                elif letter == "tbrc":
                    image = tile_images["top_bottom_right_corner_" + stage_names[number]]
                elif letter == "tsc":
                    image = tile_images["only_top_" + stage_names[number]]
                elif letter == "rsc":
                    image = tile_images["only_right_" + stage_names[number]]
                elif letter == "bsc":
                    image = tile_images["only_bottom_" + stage_names[number]]
                elif letter == "lsc":
                    image = tile_images["only_left_" + stage_names[number]]
                elif letter == "sin":
                    image = tile_images["single_" + stage_names[number]]
                elif letter == "tab":
                    image = tile_images["left_right_open_" + stage_names[number]]
                elif letter == "ral":
                    image = tile_images["bottom_top_open_" + stage_names[number]]
                pos = (x * 100, y * 100)
                if image:
                    #in case of a path tile
                    if number == len(stage_names) - 1:
                        #for all the path tiles at the edge of the room, they become interactable to allow the player to
                        #move to the next room
                        if y == len(self.room_layout) - 1 or x == len(line) - 1 or y == 0 or x == 0:
                            self.tiles[y][x] = InteractableTile(image, pos, action_desc="room_transition")
                        else:
                            self.tiles[y][x] = ImageTile(image, pos)
                    elif number == 0:
                        self.tiles[y][x] = SolidTile(image, pos, high = True)
                    else:
                        self.tiles[y][x] = SolidTile(image, pos)
                else:
                    self.tiles[y][x] = BasicTile(pos)
        # finishtile = FinishTile((int((self.tiles.size[0] - 2) * 100), int(self.tiles.size[1] / 2 * 100)), self.player, self.updater)
        #temporary
        # chest = prop_entities.Chest((int((self.tiles.size[0] - 2) * 100), int((self.tiles.size[1] / 2 -2)* 100)),\
        #                             self.player,self.get_random_weapons(5), self.updater)
        # self.tiles[int(self.tiles.size[1] / 2)][int(self.tiles.size[0] - 2)] = finishtile
        # self.tiles.finish_tiles.append(finishtile)

        #do some calculatuions after all tiles are added to speed up calculations later on.

    def __create_background_image(self, images):
        pygame.surfarray.use_arraytype("numpy")
        c180onvertedimages = [pygame.transform.rotate(image, 180) for image in images]
        pp0 = [pygame.surfarray.pixels3d(image) for image in images]
        pp180 = [pygame.surfarray.pixels3d(image) for image in c180onvertedimages]
        partspixels = pp0 + pp180
        image_rows = []
        for i in range(self.rect.width):
            image_row = []
            for j in range(self.rect.height):
                image_row.append(random.choice(partspixels))
            image_rows.append(np.concatenate(image_row, 1))
        final_arr = np.concatenate(image_rows)

        image = pygame.surfarray.make_surface(final_arr)
        image = image.convert()
        return image

    def __create_props_and_tiles_image(self, props):
        ps = props[0].get_rect().width
        max_props = min(int(self.rect.width * constants.TILE_SIZE[0] / ps), int(self.rect.height * constants.TILE_SIZE[1] / ps))
        xcoords = [random.randint(0, int(self.rect.width * constants.TILE_SIZE[0] / ps) - 1) for _ in
                   range(self.propnmbr * 2)]
        ycoords = [random.randint(0, int(self.rect.height * constants.TILE_SIZE[1] / ps) - 1) for _ in
                   range(self.propnmbr * 2)]
        prop_coords = []
        combcoords = list(zip(xcoords, ycoords))
        for coord in combcoords:
            if coord not in prop_coords:
                prop_coords.append(coord)
        if len(prop_coords) > self.propnmbr:
            prop_coords = prop_coords[0:self.propnmbr]
        prop_coords = [(coord[0] * ps, coord[1] * ps) for coord in prop_coords]
        all_coords = prop_coords + self.tiles.non_zero_tiles
        all_coords.sort(key=lambda x: self.__sort_on_y_coord(x))
        image = pygame.Surface((self.rect.width * constants.TILE_SIZE[0], self.rect.height * constants.TILE_SIZE[1]))
        image.fill((255, 255, 255))
        for coord in all_coords:
            if isinstance(coord, ImageTile):
                image.blit(coord.image, (coord.rect.topleft))
            elif not isinstance(coord, BasicTile):
                image.blit(random.choice(props), (coord[0], coord[1]))
        image.set_colorkey((255, 255, 255), RLEACCEL)
        image = image.convert()
        return image

    def __sort_on_y_coord(self, val):
        if isinstance(val, BasicTile):
            return val.y
        else:
            return val[1]
        
class TileGroup:
    def __init__(self, size):
        """
        Class for managing the tiles as a group and calculating fast collisions or other things
        """
        #dont make fcking pointers
        self.tiles = [[0] *size[0] for _ in range(size[1])]
        self.non_zero_tiles = []
        self.solid_tiles = []
        self.interactable_tiles = []
        self.__truth_map = [[True] *size[0] for _ in range(size[1])]

    def __getitem__(self, i):
        return self.tiles[i]

    def setup(self):
        self.__calculate_truth_map()
        self.__configure_bounding_boxes()
        self.__save_tile_groups()

    def __save_tile_groups(self):
        self.non_zero_tiles = [tile for row in self.tiles for tile in row if isinstance(tile, BasicTile)]
        self.solid_tiles = [tile for row in self.tiles for tile in row if isinstance(tile, SolidTile)]
        self.interactable_tiles = [tile for row in self.tiles for tile in row if isinstance(tile, InteractableTile)]

    @property
    def size(self):
        return (len(self.tiles[0]),len(self.tiles))

    def solid_collide(self, rect, height = True):
        """
        Fast method for calculating collision by checking the 4 corners and seeing with what tiles they overlap. This
        makes it at most 4 checks for collision. Also checks for out of bounds
        :param rect: a rectangle that is checked for an overlap
        :param height tells if there should be checked for height when checking collision
        :return: a boolean indicating a collsion (True) or not (False)
        """
        xtl, ytl = [int(c/100) for c in rect.topleft]
        try:
            tile = self.tiles[ytl][xtl]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                elif height:
                    return False
                return True
            xtr, ytr = [int(c/100) for c in rect.topright]
            tile = self.tiles[ytr][xtr]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                elif height:
                    return False
                return True
            xbl, ybl = [int(c/100) for c in rect.bottomleft]
            tile = self.tiles[ybl][xbl]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                elif height:
                    return False
                return True
            xbr, ybr = [int(c/100) for c in rect.bottomright]
            tile = self.tiles[ybr][xbr]
            if isinstance(tile, SolidTile) and tile.colliderect(rect):
                if height and tile.high:
                    return True
                elif height:
                    return False
                return True
        #if index error is raised then you are outside the board.
        except IndexError:
            return True
        return False

    def line_of_sight(self, start_point, end_point):
        xs, ys = start_point
        xe, ye = end_point
        points = [(xs,ys)]
        try:
            a = (ye - ys) / (xe - xs)
            b = - a * xs + ys
        except ZeroDivisionError:
            return False, []

        xdirection = 1
        if xs > xe:
            xdirection = -1
        for x in range(0, abs(xs - xe), 25):
            newx =  xs + x * xdirection
            resp = a * newx + b
            points.append((newx, resp))
            if self.tiles[int(resp/ 100)][int(newx / 100)].solid and self.tiles[int(resp/ 100)][int(newx / 100)].high:
                return False, points
        return True, points

    def pathfind(self, player_rect, enemy_rect, solid_sprite_coords = []):
        """
        Pathfind a path from the player towards the enemy. This has certain benefits regarding certain configurations
        :param player_rect: the rectangle of the player
        :param enemy_rect: the rectange of the enemy
        :return: a list of tile coordinates that constitute the path enemy should move
        """
        x,y = int(player_rect.centerx / 100), int(player_rect.centery / 100)
        start_tile = self.tiles[y][x]
        dest_tile = self.tiles[int(enemy_rect.centery / 100)][int(enemy_rect.centerx / 100)]
        #check if the enemy is on a solid tile this makes it so the enemy should not move
        if not self.__truth_map[int(enemy_rect.y / 100)][int(enemy_rect.x / 100)] and \
                enemy_rect.colliderect(self.tiles[int(enemy_rect.y / 100)][int(enemy_rect.x / 100)].bounding_box):
            return [None]
        #add starting tile to values to make it available for x,y coordinates
        current_truth_map = [row.copy() for row in self.__truth_map]
        #add solid enemies to the truth map to ensure they move around one another.
        for coord in solid_sprite_coords:
            current_truth_map[int(coord[1] / 100)][int(coord[0] / 100)] = False
        paths = [[start_tile],[start_tile],[start_tile],[start_tile]]
        cur_dist = self.__tile_dist(start_tile, dest_tile)
        walked_tiles = [[],[],[],[]]
        final_path = [None]
        while cur_dist > 1 and len(paths) > 0:
            for i, path in enumerate(paths):
                available_tiles = []
                x,y = path[-1].coord
                if not x + 1 >= len(self.tiles[0]) and current_truth_map[y][x + 1] and self.tiles[y][x + 1] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y][x + 1])
                if not x - 1 < 0 and current_truth_map[y][x - 1] and self.tiles[y][x - 1] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y][x - 1])
                if not y + 1 >= len(self.tiles) and current_truth_map[y + 1][x] and self.tiles[y + 1][x] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y + 1][x])
                if not y - 1 < 0 and current_truth_map[y - 1][x] and self.tiles[y - 1][x] not in walked_tiles[i]:
                    available_tiles.append(self.tiles[y - 1][x])
                if available_tiles:
                    #swap tile order to make an if statement check be before the others
                    available_tiles = available_tiles[i:] + available_tiles[:i]
                    tile = min(available_tiles, key = lambda x: self.__tile_dist(x, dest_tile))
                    walked_tiles[i].append(tile)
                    path.append(tile)
                    cur_dist = self.__tile_dist(tile, dest_tile)
                    final_path = path
                else:
                    #TODO look into these cases and see if it is worth fixing them.
                    # print("break")
                    paths.remove(path)
                    final_path = path
        return final_path

    def __tile_dist(self,t1, t2):
        """
        Manhatten distance between two tiles, t1 and t2
        """
        return abs(t1.coord[0] - t2.coord[0]) + abs(t1.coord[1] - t2.coord[1])

    def __calculate_truth_map(self):
        """
        Function for making a matrix that tells if a tile is solid or not. Should only be called when creating the tile
        group innitially
        """
        for y, row in enumerate(self.tiles):
            for x, val in enumerate(row):
                if isinstance(val, SolidTile):
                    self.__truth_map[y][x] = False

    def __configure_bounding_boxes(self):
        """
        Calulated the bounding boxes of all the solid tiles to allow players to move slightly in them creating a better
        moving environment. This function should only be called when innitialising the tile group class.
        """
        for row in self.tiles:
            for tile in row:
                if isinstance(tile, SolidTile):
                    sur_tiles = [True,True,True,True]
                    x,y = tile.coord
                    if y - 1 > 0 and not isinstance(self.tiles[y - 1][x], SolidTile):
                        sur_tiles[0] = False
                    if x + 1 < len(self.tiles[0]) and not isinstance(self.tiles[y][x + 1], SolidTile):
                        sur_tiles[1] = False
                    if y + 1 < len(self.tiles) and not isinstance(self.tiles[y + 1][x], SolidTile):
                        sur_tiles[2] = False
                    if x - 1 > 0 and not isinstance(self.tiles[y][x - 1], SolidTile):
                        sur_tiles[3] = False
                    tile.set_bounding_box(sur_tiles)

    def __board_to_tile_coordinates(self, *coords):
        board_coords = []
        for coord in coords:
            board_coords.append([int(coord[0] / 100), int(coord[1] / 100)])
        return board_coords

class BasicTile:
    def __init__(self, pos):
        self.rect = pygame.Rect(*pos,100,100)
        self.solid = False

    def __getattr__(self, name):
        return self.rect.__getattribute__(name)

    @property
    def coord(self):
        return [int(self.x / 100), int(self.y / 100)]

    def __str__(self):
        return str(self.coord[0]) + "," + str(self.coord[1])

class ImageTile(BasicTile):
    def __init__(self, image, pos):
        """
        abstraction level to allow for easier blitting of images on the room background these tiles contain an image
        but do not have collision
        :param image: the image that will be displayed on this tile
        :param pos: see BasicImage
        """
        BasicTile.__init__(self, pos)
        self.image = image

class SolidTile(ImageTile):
    def __init__(self, image, pos, high = False):
        ImageTile.__init__(self, image, pos)
        #is chamged after all the tiles are added
        self.bounding_box = self.rect
        self.high = high
        self.solid = True

    def __getattr__(self, name):
        return self.bounding_box.__getattribute__(name)

    def set_bounding_box(self, surrounding_tiles):
        bb = pygame.Rect(self.rect)
        if not surrounding_tiles[0] and not surrounding_tiles[2]:
            bb = bb.inflate(0, -int(self.rect.height * 0.4))
        elif not surrounding_tiles[0]:
            bb = bb.inflate((0, - int(self.rect.height * 0.2)))
            bb.bottom = self.rect.bottom
        elif not surrounding_tiles[2]:
            bb = bb.inflate((0, - int(self.rect.height * 0.2)))
            bb.top = self.rect.top
        if not surrounding_tiles[1] and not surrounding_tiles[3]:
            bb = bb.inflate((-int(self.rect.width * 0.4), 0))
        elif not surrounding_tiles[1]:
            bb = bb.inflate((-int(self.rect.width * 0.2), 0))
            bb.left = self.rect.left
        elif not surrounding_tiles[3]:
            bb = bb.inflate((-int(self.rect.width * 0.2), 0))
            bb.right = self.rect.right
        self.bounding_box = bb

class InteractableTile(ImageTile):
    def __init__(self, image, pos, action = None, action_desc = None):
        ImageTile.__init__(self, image, pos)
        #define an action or define a descriptor that signifies an action that needs to be defined in the stage level.
        self.action = action
        self.action_desc = action_desc

#methods for generating a single room containing blobs in them that the player cannot move trough. Spaced in a way that
#always allows for the player to reach al places of the map with the exception of some openings that can occur at the
#edges.
class Leaf:
    def __init__(self, loc, dim):
        self.rect = pygame.Rect((*loc ,*dim))
        self.left_leaf = None
        self.rigth_leaf = None
        self.leaf_map = None
        #track the direction of the split for reconstruction
        self.hsplit = False

    def split(self):
        if self.left_leaf != None and self.rigth_leaf != None:
            return False #already split
        self.hsplit = random.randint(1,2) == 1
        if self.rect.width >= self.rect.height and self.rect.width / self.rect.height >= 1.25:
            self.hsplit = False
        elif self.rect.height >= self.rect.width and self.rect.height / self.rect.width >= 1.25:
            self.hsplit = True
        maximum = self.rect.height - MIN_LEAF_SIZE if self.hsplit else self.rect.width - MIN_LEAF_SIZE
        if maximum <= MIN_LEAF_SIZE:
            return False
        split = random.randint(MIN_LEAF_SIZE, maximum)
        if self.hsplit:
            self.left_leaf = Leaf(self.rect.topleft, (self.rect.width, split))
            self.rigth_leaf = Leaf((self.rect.x,self.rect.y + split), (self.rect.width, self.rect.height - split))
        else:
            self.left_leaf = Leaf(self.rect.topleft, (split,self.rect.height))
            self.rigth_leaf = Leaf((self.rect.x + split,self.rect.y), (self.rect.width - split, self.rect.height))
        return True

    def create_blob(self, wheighted_array):
        if self.left_leaf != None and self.rigth_leaf != None:
            if self.left_leaf != None:
                self.left_leaf.create_blob(wheighted_array)
            if self.rigth_leaf != None:
                self.rigth_leaf.create_blob(wheighted_array)
        else:
            self.leaf_map = [[0 for x in range(self.rect.width)] for y in range(self.rect.height)]
            #minimum size is 3
            blobw = random.randint(3, self.rect.width - 1)
            blobh = random.randint(3, self.rect.height - 1)
            blobx = random.randint(self.rect.x, self.rect.right - blobw)
            bloby = random.randint(self.rect.y, self.rect.bottom - blobh)
            number = random.choice(wheighted_array)
            #create a blobmap within the leaf size that is atleast 2 by 2
            for y in range(bloby - self.rect.y, bloby - self.rect.y + blobh - 1,1):
                for x in range(blobx - self.rect.x, blobx - self.rect.x +blobw - 1,1):
                    #determines how likely branching is from the original blob
                    if random.randint(1,3) == 1:
                        self.leaf_map[y][x] = number
                        self.leaf_map[y][x + 1] = number
                        self.leaf_map[y + 1][x] = number
                        self.leaf_map[y + 1][x + 1] = number

    def get_map(self):
        final_map = [[0 for x in range(self.rect.width)] for y in range(self.rect.height)]
        if self.left_leaf != None and self.rigth_leaf != None:
            mapl = self.left_leaf.get_map()
            mapr = self.rigth_leaf.get_map()
            if self.hsplit:
                final_map = mapl + mapr
            else:
                for y in range(len(mapr)):
                    final_map[y] = mapl[y] + mapr[y]
            self.leaf_map = final_map
        return self.leaf_map

if __name__ == "__main__":
    build_map((5,5), wheights = [8,2])
