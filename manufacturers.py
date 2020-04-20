import random

def get_manufacturer(name):
    if name == "Hock":
        return HocManufactorer()
    elif name == "Vockar":
        return VockarManufactorer()
    elif name == "Majina":
        return MajinaManufactorer()
    elif name == "Bright":
        return BrightManufactorer()
    elif name == "Sternwel":
        return SternwelManufactorer()
    elif name == "Jenkins":
        return JenkinsManufactorer()

class AbstractManufactorer:
    def __init__(self):
        self.reload_speed = 2 #seconds
        self.fire_rate = 2 # per second
        self._base_damage = 5 #per bulet is more for
        self._accuracy = 60 #means that 60% of the shots are on target
        self.magazine_size = 10 # not relevant for melee weapons
        self.weight = 10 #kgs
        self.level = 1 # get player level. Means nothing at the moment

    @property
    def damage(self):
        return self._base_damage * self.level

    @property
    def accuracy(self):
        if self._accuracy >= 100:
            return 100
        return self._accuracy

    @property
    def dps(self):
        return self.damage * self.fire_rate

class HocManufactorer(AbstractManufactorer):
    """
    Gives good reload speed, magazine size, fire rate and accuracy at the cost of damage
    """
    def __init__(self):
        AbstractManufactorer.__init__(self)
        self.reload_speed *= 0.5
        self._base_damage *= 0.7
        self.fire_rate *= 2
        self._accuracy *= 1.2
        self.magazine_size *= 3

class VockarManufactorer(AbstractManufactorer):
    """
    Good accuracy and damage at the cost of reload and fire rate
    """
    def __init__(self):
        AbstractManufactorer.__init__(self)
        self.reload_speed *= 1.5
        self._base_damage *= 1.5
        self.fire_rate *= 0.5
        self._accuracy *= 2
        self.weight *= 0.6

class MajinaManufactorer(AbstractManufactorer):
    """
    Good reload speed and very leightwheight. This comes at the cost of damage and magazine size.
    """
    def __init__(self):
        AbstractManufactorer.__init__(self)
        self.reload_speed *= 0.3
        self._base_damage *= 0.6
        self.magazine_size *= 0.6
        self.weight *= 0.1

class BrightManufactorer(AbstractManufactorer):
    """
    Deal allot of damage but are punished in almost every other aspect
    """
    def __init__(self):
        AbstractManufactorer.__init__(self)
        self._base_damage *= 2
        self._accuracy *= 0.3
        self.magazine_size *= 0.5
        self.weight *= 3

class JenkinsManufactorer(AbstractManufactorer):
    """
    Decent and default
    """
    def __init__(self):
        AbstractManufactorer.__init__(self)

class SternwelManufactorer(AbstractManufactorer):
    def __init__(self):
        AbstractManufactorer.__init__(self)
        self._base_damage *= 0.7
        self._accuracy *= 0.8
        self.magazine_size *= 2
        self.weight *= 0.8
        self.element = random.choice(("fire","water","earth","air","EXPLOSION"))
