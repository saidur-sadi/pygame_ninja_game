import sys
import pygame

from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.cloud import Clouds


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja')
        self.screen = pygame.display.set_mode((640, 480))

        # we render on this smaller displayer, and scale up to the bigger screen
        self.display = pygame.Surface((320, 240))  # default black

        # May want to restrict frame for games since every frame is rendered
        # individually and we don't want out CPU to be overloaded
        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'))
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]

    def run(self):
        while True:
            # Fill the screen: everything from last fram will be replace with this color
            # Create a rectangle with: top left pos, width and height
            # self.display.fill((14, 219, 248))
            self.display.blit(self.assets['background'], (0, 0))

            self.scroll[0] += (self.player.rect().centerx -
                               self.display.get_width() / 2 - self.scroll[0]) / 30

            self.scroll[1] += (self.player.rect().centery -
                               self.display.get_height() / 2 - self.scroll[1]) / 30

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            # avoid subpixel movement for the camera
            self.tilemap.render(self.display, offset=render_scroll)

            # movement[1] == 0 since we move left and right
            self.player.update(
                self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            # blit essentially copy the memory to the position
            # we can blit any surface to to others
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # click X on the window
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:  # magic: negative velocity == jump
                        self.player.velocity[1] = -3
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)  # 60 fps


Game().run()
