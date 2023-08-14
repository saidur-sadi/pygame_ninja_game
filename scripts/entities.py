import pygame
import math
import random
from scripts.particle import Particle
from scripts.spark import Spark


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False,
                           'right': False, 'left': False}
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False  # right and left
        self.set_action('idle')

        self.last_movement = [0, 0]

        self.dashing = 0

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type +
                                              '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        # collisons are reset every reset
        self.collisions = {'up': False, 'down': False,
                           'right': False, 'left': False}
        # force(movement) + veclocity = final movement
        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

        # update pos based on the movement
        # handle collisions x and y seperately is recommended
        self.pos[0] += frame_movement[0]  # update player position
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:  # moving right
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True

                self.pos[0] = entity_rect.x  # attach player to the tile
                # why don't use rect to represent the entity's position in the first place?
                # reason: rect in pygame only works with int

        self.pos[1] += frame_movement[1]  # update player position
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:  # moving down
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y  # attach player to the tile

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        # max velocity is set to 5: avoid consistent acceleration
        # example: jump
        # up phase: taken velocity is from negative number to 0
        # down phase: from 0 to max.5 or hit the ground
        # y direction veclocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # down/up collision stops the entity, sets the vertical velocity to 0
        # in order to to accerlerate gradually
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # surf.blit(self.game.assets['player'], (self.pos[0]-offset[0], self.pos[1]-offset[1]))
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (
                        movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                # flip if not physical tiles around
                self.flip = not self.flip
            # cut to 0 over time if walking
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0],
                       self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        # spawen sparks (left)
                        for i in range(4):
                            self.game.sparks.append(Spark(
                                self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append(
                            [[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        # spawen sparks (right)
                        for i in range(4):
                            self.game.sparks.append(Spark(
                                self.game.projectiles[-1][0], random.random() - 0.5, 2+random.random()))

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)  # half a sec to 2 sec
        super().update(tilemap, movement=movement)
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(
                        Spark(self.rect().center, angle, 2 + random.random()))
                    # angle of particle is opposite
                    self.game.particles.append(Particle(self.game, 'particle', self.game.player.rect().center, velocity=[
                        math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    # big sparks
                self.game.sparks.append(
                    Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(
                    Spark(self.rect().center, math.pi, 5 + random.random()))
                return True

    def render(self, surf, offset=(0, 0)):

        super().render(surf, offset)
        if self.flip:
            # flip gun as well
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect(
            ).centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect(
            ).centerx + 4 - offset[0], self.rect().centery - offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        # prevent falling forever
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1  # reset jump

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:  # we are moving horizontally
                self.set_action('run')
            else:
                self.set_action('idle')

        # burst
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        if self.dashing > 0:
            self.dashing = max(0, self.dashing-1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing+1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                # achieve sudden stop of dash
                # also serves as cool down
                self.velocity[0] *= 0.1
                # make stream move along
            pvelocity = [abs(self.dashing) /
                         self.dashing * random.random() * 3, 0]
            self.game.particles.append(
                Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        # make wall push back naturally
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5  # pushed away from way
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5  # pushed away from way
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5  # bigger than 4
            return True

    def render(self, surf, offset=(0, 0)):
        # make player invisible ?
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
