
import unittest
import weapon
import main
import pygame

class TestWeapon(unittest.TestCase):

    def test_create_weapon_image(self):
        pygame.init()
        screen = pygame.display.set_mode((1900, 1200))
        parts = main.load_parts()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        # background color
        background.fill((200, 200, 200))
        screen.blit(background, (0, 0))
        pygame.display.flip()
        weaponparts = {"blade":parts["testblade"],"guard":parts["testguard"],
                       "handle":parts["testhandle"],"pommel":parts["testpommel"]}
        w1 = weapon.MeleeWeapon(weaponparts)
        screen.blit(w1.image,(0,0))
        pygame.display.flip()
        going = True
        while going:
            pass

if __name__ == "__main__":
    unittest.main()
