import pygame, random
import utilities

MIN_LEAF_SIZE = 4
MAX_LEAF_SIZE = 10

#binary space partitioning
def build_map():
    did_split = True
    leafs = [Leaf((0,0),(int((utilities.DEFAULT_LEVEL_SIZE.width - 400) / 100), int((utilities.DEFAULT_LEVEL_SIZE.height - 400) / 100)))]
    while did_split:
        did_split = False
        for l in leafs:
            if l.left_leaf == None and l.rigth_leaf == None:
                if l.rect.width > MAX_LEAF_SIZE or l.rect.height > MAX_LEAF_SIZE or random.randint(1,4) == 1:
                    if l.split():
                        leafs.append(l.rigth_leaf)
                        leafs.append(l.left_leaf)
                        did_split = True
    leafs[0].create_blob()
    final_map = leafs[0].get_map()
    for i, row in enumerate(final_map):
        final_map[i] = [1,0] + row + [0,1]
    final_map = [[1]* len(final_map[0]),[1]+ [0]* (len(final_map[0]) -2) + [1]] + final_map + [[1]+ [0]* (len(final_map[0]) -2) + [1],[1]* len(final_map[0])]
    return determine_pictures(final_map)

def determine_pictures(game_map):
    for y, row in enumerate(game_map):
        for x, number in enumerate(row):
            if number == 0:
                continue
            elif number == 1:
                st = [0,0,0,0]
                if y - 1 < 0 or game_map[y -1][x] != 0:
                    st[0] = 1
                if x + 1 >= len(row) or game_map[y][x+1] != 0:
                    st[1] = 1
                if y + 1 >= len(game_map) or game_map[y + 1][x] != 0:
                    st[2] = 1
                if x - 1 < 0 or game_map[y][x - 1] != 0:
                    st[3] = 1
                name = get_picture_code(st)
                # check for corner cases
                if name == "m":
                    if y + 1 < len(game_map) and x - 1 >= 0 and (game_map[y+1][x-1] == 0):
                        name = "blic"
                    elif y + 1 < len(game_map) and x + 1 < len(row) and (game_map[y+1][x+1] == 0):
                        name = "bric"
                    elif y - 1 >= 0 and x + 1 < len(row) and (game_map[y - 1][x + 1] == 0):
                        name = "tric"
                    elif y - 1 >= 0 and x - 1 >= 0 and (game_map[y-1][x-1] == 0):
                        name = "tlic"

                game_map[y][x] = name
    return game_map

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

    def create_blob(self):
        if self.left_leaf != None and self.rigth_leaf != None:
            if self.left_leaf != None:
                self.left_leaf.create_blob()
            if self.rigth_leaf != None:
                self.rigth_leaf.create_blob()
        else:
            self.leaf_map = [[0 for x in range(self.rect.width)] for y in range(self.rect.height)]
            if random.randint(1,1) == 1:
                #minimum size is 3
                blobw = random.randint(3, self.rect.width - 1)
                blobh = random.randint(3, self.rect.height - 1)
                blobx = random.randint(self.rect.x, self.rect.right - blobw)
                bloby = random.randint(self.rect.y, self.rect.bottom - blobh)
                #create a blobmap within the leaf size that is atleast 2 by 2
                for y in range(bloby - self.rect.y, bloby - self.rect.y + blobh - 1,1):
                    for x in range(blobx - self.rect.x, blobx - self.rect.x +blobw - 1,1):
                        #determines how likely branching is from the original blob
                        if random.randint(1,3) == 1:
                            self.leaf_map[y][x] = 1
                            self.leaf_map[y][x + 1] = 1
                            self.leaf_map[y + 1][x] = 1
                            self.leaf_map[y + 1][x + 1] = 1

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
    leafs = build_map()
    print("final:")
    print(len(leafs[0]), len(leafs))
    print(leafs)
