import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right':False, 'left': False}

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=(0, 0)):
        # collisons are reset every reset
        self.collisions = {'up': False, 'down': False, 'right':False, 'left': False}
        # force(movement) + veclocity = final movement
        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])


        # update pos based on the movement
        # handle collisions x and y seperately is recommended
        self.pos[0] += frame_movement[0] # update player position
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0: # moving right
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                    
                self.pos[0] = entity_rect.x # attach player to the tile
                # why don't use rect to represent the entity's position in the first place?
                # reason: rect in pygame only works with int
        
        self.pos[1] += frame_movement[1] # update player position
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0: # moving down
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y # attach player to the tile
        
        # max velocity is set to 5: avoid consistent acceleration
        # example: jump
        # up phase: taken velocity is from negative number to 0
        # down phase: from 0 to max.5 or hit the ground 
        self.velocity[1] = min(5, self.velocity[1] + 0.1) # y direction veclocity
        
        # down/up collision stops the entity, sets the vertical velocity to 0
        # in order to to accerlerate gradually
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
                    
    def render(self, surf):
        surf.blit(self.game.assets['player'], self.pos)
