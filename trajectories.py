import pygame, random, math
import utilities

class Trajectory:
    def __init__(self, start_pos, rect, image, *groups, **kwargs):
        self.rect = rect
        self.image = image
        self.accuracy = kwargs["accuracy"]

class LinearTrajectory(Trajectory):
    MAX_INACCURACY = 0.2 * math.pi #90 degrees
    def __init__(self, start_pos, dest_pos, rect, image, *groups, max_speed = 10, **kwargs):
        Trajectory.__init__(self, start_pos, rect, image, *groups, **kwargs)
        self.projectile_offset = pygame.Vector2(0,0)
        self.start = start_pos
        self.dest = list(dest_pos)
        self.max_speed = max_speed
        if self.dest[0] < start_pos[0]:
            self.max_speed = - self.max_speed
        self.speedx, self.speedy = 0, 0
        self.projectile_offset = pygame.Vector2(0,0)
        self.__configure_trajectory()

    def __configure_trajectory(self):
        inacuracy = 100 - self.accuracy
        delta_x = (self.dest[0] - self.start[0])
        delta_y = (self.dest[1] - self.start[1])
        diagonal = math.sqrt(delta_x**2 + delta_y**2)
        rad = math.atan(delta_y / delta_x)
        change = self.MAX_INACCURACY * (random.randint(0, inacuracy) / 100)
        if random.randint(1,2) == 1:
            change *= -1
        new_rad = rad + change
        new_delta_x = abs(math.cos(new_rad) * diagonal)
        new_delta_y = math.sin(new_rad) * diagonal
        try:
            a = new_delta_y / new_delta_x
        except ZeroDivisionError:
            #rare case where delta x = 0
            #make a sufficiently large so it goes straight up or down
            if self.dest[1] - self.start[1] > 0:
                a = 10000
            else:
                a = -10000
        #https://math.stackexchange.com/questions/656500/given-a-point-slope-and-a-distance-along-that-slope-easily-find-a-second-p
        self.speedx = self.max_speed * 1 / math.sqrt(1 + a**2)
        self.speedy = self.max_speed * a / math.sqrt(1 + a**2)
        self.projectile_offset = pygame.Vector2(- int(self.rect.width * 0.5), int(self.rect.height * 0.25))
        if self.max_speed < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.projectile_offset = pygame.Vector2(int(self.rect.width * 0.5), int(self.rect.height * 0.25))
        #orient the arrow the rigth way
        if self.speedx != 0:
            rad = math.atan(self.speedy / self.speedx)
            degree = rad * 180 / math.pi
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.image, - degree)
            self.projectile_offset = self.projectile_offset.rotate(degree)
            self.rect = self.image.get_rect(center = old_center)
