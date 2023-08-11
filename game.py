import sys
import pygame
import random
import math

from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.cloud import Clouds
from scripts.particle import Particle


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
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False)
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.leaf_spawners = []

        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(
                4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        self.partiles = []
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

            for rect in self.leaf_spawners:
                # spawn rate: bigger tree spawn more
                # multiply by big number make it not spawning every frame
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width,
                           rect.y + random.random() * rect.height)
                    self.partiles.append(
                        Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            # avoid subpixel movement for the camera
            self.tilemap.render(self.display, offset=render_scroll)

            # movement[1] == 0 since we move left and right
            self.player.update(
                self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            for particle in self.partiles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    # move particle back and forth naturally
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.partiles.remove(particle)

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
