import pygame, random, math
import utilities

from entities import LivingEntity

class Projectile(LivingEntity):
    ACCURACY = 80
    def __init__(self, start_pos, end_pos, *groups, accuracy = ACCURACY, start_move  = 0, **kwargs):
        LivingEntity.__init__(self, start_pos, *groups, **kwargs)
        self.rect.center = start_pos
        self.pos = list(self.rect.center)
        self.accuracy = accuracy
        self.trajectory = self._configure_trajectory(start_pos, end_pos )
        self.move(start_move)
        if "bounding_size" in kwargs:
            self.bb_size = kwargs["bounding_size"]
        else:
            self.bb_size = (self.rect.width, self.rect.height)

    def update(self, *args):
        super().update()
        if not self.dead:
            self._check_hit()

    def _check_hit(self):
        for sprite in super().groups()[0].sprites():
            if sprite != self and not self.dead and hasattr(sprite, "change_health") and not isinstance(sprite, Projectile) and not sprite.immune[0]:
                if sprite.rect.colliderect(self.rect):
                    sprite.change_health(- self.damage)
                    self.dead = True

    def move(self, max_speed_times = 1):
        if any(self._check_collision(sprites = False)):
            self.dead = True
        self.pos[0] += self.trajectory.speedx * max_speed_times
        self.pos[1] += self.trajectory.speedy * max_speed_times
        self.rect.center = self.pos

    def _configure_trajectory(self, start_pos, end_pos):
        if not self.dead:
            trajectory = LinearTrajectory(start_pos, end_pos, self.rect, self.image, super().groups()[0],
                                                       max_speed=self.max_speed, accuracy = self.accuracy)
            self.image = trajectory.image
            self.rect = trajectory.rect
            self.pos = list(self.rect.center)
            return trajectory

class PlayerProjectile(Projectile):
    def __init__(self, start_pos, end_pos, *groups, **kwargs):
        Projectile.__init__(self, start_pos, end_pos, *groups, **kwargs)

    def _configure_trajectory(self, start_pos, end_pos):
        """
        Original trajectory but now containing a screen relative coordinate
        :param start_pos:
        :param end_pos:
        """
        trajectory = LinearTrajectory(utilities.get_screen_relative_coordinate(start_pos), end_pos, self.rect,
                                      self.image, super().groups()[0],max_speed=self.max_speed, accuracy = self.accuracy)
        self.image = trajectory.image
        self.rect = trajectory.rect
        self.pos = list(self.rect.center)
        return trajectory

class EnemyProjectile(Projectile):
    def __init__(self, start_pos, end_pos, player, *groups, **kwargs):
        Projectile.__init__(self, start_pos, end_pos, *groups, **kwargs)
        self.player = player

    def do_flip(self):
        """
        make sure the image does not flip
        TODO make a better sytem for this. This is kind of dumb.
        """
        pass

    def _get_bounding_box(self):
        """
        Return a rectangle at the tip of the arrow to make sure the arrow does not collide with unexpected places
        :return: a pygame.Rect object
        """
        if not hasattr(self, "trajectory"):
            return self.rect
        return pygame.Rect(*(self.rect.center - self.trajectory.projectile_offset), *(self.bb_size))

    def _check_hit(self):
        if self.player.bounding_box.colliderect(self.bounding_box) and not self.player.immune[0]:
            self.player.change_health(-self.damage)
            self.player.set_immune()
            self.dead = True

class HomingProjectile(Projectile):
    RECALCULATING_SPEED = 10
    ACCURACY = 100
    SPEED = 5
    def __init__(self, start_pos, end_pos, target, *groups, **kwargs):
        Projectile.__init__(self, start_pos, end_pos, *groups, speed = self.SPEED, accuracy = self.ACCURACY, **kwargs)
        self.passed_frames = 0
        self.target = target

    def update(self):
        super().update()
        if self.passed_frames <= self.RECALCULATING_SPEED:
            self.passed_frames += 1
        else:
            self.passed_frames= 0
            self.trajectory = self._configure_trajectory(self.rect.center, self.target.rect.center)
            self.image = self.orig_image

    def _check_hit(self):
        if self.target.bounding_box.colliderect(self.bounding_box) and not self.target.immune[0]:
            self.target.change_health(-self.damage)
            self.target.set_immune()
            self.dead = True

class Trajectory:
    def __init__(self, start_pos, rect, image, *groups, **kwargs):
        self.rect = rect
        self.image = image
        self.accuracy = kwargs["accuracy"]

class LinearTrajectory(Trajectory):
    MAX_INACCURACY = 0.1 * math.pi #90 degrees
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
        try:
            rad = math.atan(delta_y / delta_x)
        except ZeroDivisionError:
            rad = 0.5 * math.pi
        change = self.MAX_INACCURACY * (random.randint(0, inacuracy) / 100)
        if random.randint(1,2) == 1:
            change *= -1
        new_rad = rad + change
        new_delta_x = math.cos(new_rad) * self.max_speed
        new_delta_y = math.sin(new_rad) * self.max_speed
        self.speedx = new_delta_x
        self.speedy = new_delta_y
        self.projectile_offset = pygame.Vector2(- self.rect.width * 0.5, self.rect.height * 0.25)
        if self.max_speed < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.projectile_offset = pygame.Vector2(self.rect.width * 0.5, self.rect.height * 0.25)
        #orient the arrow the rigth way
        if self.speedx != 0:
            rad = math.atan(self.speedy / self.speedx)
            degree = rad * 180 / math.pi
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.image, - degree)
            self.projectile_offset = self.projectile_offset.rotate(degree)
            self.rect = self.image.get_rect(center = old_center)
