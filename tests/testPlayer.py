from pygame.locals import *
import unittest
import entities
import main
import pygame

class TestPlayer(unittest.TestCase):

    def setup_player(self):
        pygame.init()
        screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Monkey Fever")
        pygame.mouse.set_visible(True)

        # Create The Backgound
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        # background color
        background.fill((250, 250, 250))

        # Display The Background
        screen.blit(background, (0, 0))
        pygame.display.flip()

        # Load game objects here
        clock = pygame.time.Clock()
        # method for grouping sprites to be updated togeter
        p = entities.Player(0,0)
        allsprites = pygame.sprite.RenderPlain((p))

        # Main Loop
        going = True
        going = True
        while going:
            clock.tick(60)
            events = []
            # Handle Input Events
            for event in pygame.event.get():
                if event.type == QUIT:
                    going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    going = False
                elif event.type == MOUSEBUTTONDOWN:
                    print("Click")
                elif event.type == MOUSEBUTTONUP:
                    print("un-Click")
                else:
                    events.append(event)
            p.events = events
            allsprites.update()

            # Draw Everything --> clears screen and draws. Is not super efficient
            screen.blit(background, (0, 0))
            allsprites.draw(screen)
            pygame.display.flip()

        pygame.quit()

    def test_player(self):
        self.setup_player()
        #p = entities.Player(0,0,(0,0,100,100))



if __name__ == "__main__":
    unittest.main()





