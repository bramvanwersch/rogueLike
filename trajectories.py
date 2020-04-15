import pygame, random, math
import utilities

class Trajectory:
    def __init__(self, start_pos, rect, image, *groups, accuracy = 80, **kwargs):
        self.rect = rect
        self.image = image
        self.accuracy = accuracy

class LinearTrajectory(Trajectory):
    def __init__(self, start_pos, dest_pos, rect, image, *groups, max_speed = 10, **kwargs):
        Trajectory.__init__(self, start_pos, rect, image, *groups, **kwargs)
        self.projectile_offset = pygame.Vector2(0,0)
        self.dest = list(dest_pos) #list(self.player.bounding_box.center)
        self.max_speed = max_speed
        if self.dest < list(self.rect.topleft):
            self.max_speed = - self.max_speed
        self.speedx, self.speedy = 0, 0
        self.projectile_offset = pygame.Vector2(0,0)
        self.__configure_trajectory()

    def __configure_trajectory(self):
        #https://math.stackexchange.com/questions/656500/given-a-point-slope-and-a-distance-along-that-slope-easily-find-a-second-p
        # delta y / delta x
        inacuracy = 100 - self.accuracy
        if random.randint(1,2) == 1:
            self.dest[0] += random.randint(0, inacuracy)
            self.dest[1] += random.randint(0, inacuracy)
        else:
            self.dest[0] -= random.randint(0, inacuracy)
            self.dest[1] -= random.randint(0, inacuracy)
        try:
            a = (self.dest[1] - self.rect.y) / (self.dest[0] - self.rect.x)
        except ZeroDivisionError:
            a = 0
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
