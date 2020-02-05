import pygame, random
import utilities

MIN_LEAF_SIZE = 5
MAX_LEAF_SIZE = 10

#binary space partitioning
def build_map():
    did_split = True
    leafs = [Leaf((0,0),(int(utilities.DEFAULT_LEVEL_SIZE.width / 100), int(utilities.DEFAULT_LEVEL_SIZE.height / 100)))]
    while did_split:
        did_split = False
        for l in leafs:
            if l.left_leaf == None and l.rigth_leaf == None:
                #bigger then max size or 75% chance
                # print("test2")
                if l.rect.width > MAX_LEAF_SIZE or l.rect.height > MAX_LEAF_SIZE or random.randint(1,4) == 1:
                    if l.split():
                        leafs.append(l.rigth_leaf)
                        leafs.append(l.left_leaf)
                        did_split = True
    leafs[0].create_blob()
    # count = 0
    # for l in leafs:
    #     if l.blob_map:
    #         count += 1
    # print(count)
    final_map = leafs[0].get_map()
    return final_map

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
