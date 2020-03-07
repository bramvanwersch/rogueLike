import pygame, random, numpy
import utilities

MIN_LEAF_SIZE = 4
MAX_LEAF_SIZE = 10
MAX_ROOMS = 12

def build_map(size):
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
            print(point)
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
                point = random.choice(surrounding_points)
                game_map[point[1]][point[0]] = -9
                extra_rooms += 1
            #replace all -9 by 1s
            for y, row in enumerate(game_map):
                for x, value in enumerate(row):
                    if value == -9:
                        game_map[y][x] = 1
        total_rooms += extra_rooms
    utilities.fancy_matrix_print(game_map)


#binary space partitioning
def build_room(wheights = [1]):
    did_split = True
    leafs = [Leaf((0,0),(int((utilities.DEFAULT_LEVEL_SIZE.width - 200) / 100), int((utilities.DEFAULT_LEVEL_SIZE.height - 200) / 100)))]
    while did_split:
        did_split = False
        for l in leafs:
            if l.left_leaf == None and l.rigth_leaf == None:
                if l.rect.width > MAX_LEAF_SIZE or l.rect.height > MAX_LEAF_SIZE or random.randint(1,4) == 1:
                    if l.split():
                        leafs.append(l.rigth_leaf)
                        leafs.append(l.left_leaf)
                        did_split = True
    #create wheighted array for consistent random with a seed.
    wheighted_array = [[i +1]* wheights[i] for i in range(len(wheights))]
    wheighted_array = [number for row in wheighted_array for number in row]
    leafs[0].create_blob(wheighted_array)
    final_map = leafs[0].get_map()
    for i, row in enumerate(final_map):
        final_map[i] = [1] + row + [1]
    final_map = [[1]* len(final_map[0])] + final_map + [[1]* len(final_map[0])]
    return determine_pictures(final_map)

def add_path(room_map):
    pass

def determine_pictures(room_map):
    """
    Determine the pictures that should go in place for each generated tile. Add numbers that determine the texture of
    the pictures
    :param room_map: a matrix that represents the game map. 0 is no tile 1 and higher is a specific texture tile.
    :return: a matrix of the same dimensions now filled  in with string where there were numbers other then zero for the
    texture of each of these tiles.
    """
    picture_map = [[0 for x in range(len(room_map[0]))] for y in range(len(room_map))]
    for y, row in enumerate(room_map):
        for x, number in enumerate(row):
            if number == 0:
                continue
            else:
                st = [0,0,0,0]
                if y - 1 < 0 or room_map[y - 1][x] == number:
                    st[0] = 1
                if x + 1 >= len(row) or room_map[y][x + 1] == number:
                    st[1] = 1
                if y + 1 >= len(room_map) or room_map[y + 1][x] == number:
                    st[2] = 1
                if x - 1 < 0 or room_map[y][x - 1] == number:
                    st[3] = 1
                name = get_picture_code(st)
                # check for corner cases
                if name == "m":
                    if y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_map) and x + 1 < len(row)\
                            and room_map[y - 1][x - 1] == 0 and room_map[y + 1][x + 1] == 0:
                        name = "tbd"
                    elif y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_map) and x + 1 < len(row) \
                            and (room_map[y - 1][x + 1] == 0) and (room_map[y + 1][x - 1] == 0):
                        name = "btd"
                    elif y + 1 < len(room_map) and x - 1 >= 0 and (room_map[y + 1][x - 1] == 0):
                        name = "blic"
                    elif y + 1 < len(room_map) and x + 1 < len(row) and (room_map[y + 1][x + 1] == 0):
                        name = "bric"
                    elif y - 1 >= 0 and x + 1 < len(row) and (room_map[y - 1][x + 1] == 0):
                        name = "tric"
                    elif y - 1 >= 0 and x - 1 >= 0 and (room_map[y - 1][x - 1] == 0):
                        name = "tlic"
                elif name == "rs":
                    if y - 1 >= 0 and x - 1 >= 0 and x + 1 < len(row) \
                         and room_map[y - 1][x - 1] == 0 and room_map[y][x + 1] == 0:
                        name = "rtlc"
                    elif y + 1 < len(room_map) and x - 1 >= 0 and x + 1 < len(row) \
                        and room_map[y + 1][x - 1] == 0 and room_map[y][x + 1] == 0:
                        name = "rblc"
                elif name == "bs":
                    if y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_map)\
                        and room_map[y - 1][x - 1] == 0 and room_map[y - 1][x] == 0:
                        name = "btlc"
                    elif y - 1 >= 0 and x + 1 < len(row) and y + 1 < len(room_map)\
                        and room_map[y - 1][x + 1] == 0 and room_map[y - 1][x] == 0:
                        name = "btrc"
                elif name == "ls":
                    if y - 1 >= 0 and x - 1 >= 0 and x + 1 < len(row)\
                        and room_map[y - 1][x + 1] == 0 and room_map[y][x - 1] == 0:
                        name = "ltrc"
                    elif y + 1 < len(room_map) and x - 1 >= 0 and x + 1 < len(row) \
                            and room_map[y + 1][x + 1] == 0 and room_map[y][x - 1] == 0:
                        name = "lbrc"
                elif name == "ts":
                    if y - 1 >= 0 and x - 1 >= 0 and y + 1 < len(room_map)\
                        and room_map[y + 1][x - 1] == 0 and room_map[y - 1][x] == 0:
                        name = "tblc"
                    elif y - 1 >= 0 and x - 1 < len(row) and y + 1 < len(room_map) \
                            and room_map[y + 1][x + 1] == 0 and room_map[y - 1][x] == 0:
                        name = "tbrc"

                picture_map[y][x] = name + str(number)
    return picture_map

def get_picture_code(st):
    if st == [1,1,0,0]:
        return "blc"
    if st == [0,1,1,0]:
        return "tlc"
    if st == [0,0,1,1]:
        return "trc"
    if st == [1,0,0,1]:
        return "brc"
    if st == [1,1,1,0]:
        return "ls"
    if st == [0,1,1,1]:
        return "ts"
    if st == [1,0,1,1]:
        return "rs"
    if st == [1,1,0,1]:
        return "bs"
    return "m"

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
    build_map((5,5))
