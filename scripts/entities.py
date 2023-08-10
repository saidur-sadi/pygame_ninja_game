import pygame


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
        
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            
        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0: # we are moving horizontally
            self.set_action('run')
        else:
            self.set_action('idle')

            