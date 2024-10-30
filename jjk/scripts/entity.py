import pygame
import random

class Physics_Entity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.stun = 0

        self.hp = 50

        self.action = ""
        self.anim_offset = [0, 0]
        self.flip = False
        self.animation = self.game.assets[self.type + "/" + "idle"].copy()
        self.last_movement = [0, 0]
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement = (0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.velocity[1] = min(5, self.velocity[1]+0.1)
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0]-0.1)
        if self.velocity[0] < 0:
            self.velocity[0] = min(0, self.velocity[0] +0.1)
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        self.last_movement = movement

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        self.animation.update()
    
    def render(self, surf, scroll=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0]-scroll[0]+self.anim_offset[0], self.pos[1]-scroll[1]+self.anim_offset[1]))

class enemy(Physics_Entity):
    def __init__(self, game, pos, size):
        super().__init__(game, "cursed_spirit", pos, size)
        self.walking = 0
        self.attack = 0

    def update(self, tilemap, scroll):
        movement = (0,0)
        no_block_ahead = not tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1]+50))
        player_dist = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1]-self.pos[1])
        walled = self.collisions["left"] or self.collisions["right"]
        insight = (self.flip and player_dist[0] < 0) or (not self.flip and player_dist[0] > 0)
        detected = abs(player_dist[0]) < self.detecting_range and insight
        attack = (abs(player_dist[0]) < self.attack_range) and insight
        self.stun = max(0, self.stun-1)
        if not self.stun:
            if attack:
                if not self.attack:
                    self.attack = 120
                self.attack = max(0, self.attack-1)
                if not self.attack:
                    self.velocity[1] = -2
                    if self.flip:
                        self.velocity[0] = -3
                    else:
                        self.velocity[0] = 3 
                    self.game.hitbox.append([[self.pos[0]-scroll[0], self.pos[1]-scroll[1]], self.velocity, self.size, [self.velocity[0], 0], "enemy", 5, 60, 5])
            else:
                self.attack = 0
            if self.walking and not attack:
                if (no_block_ahead or walled or 0.995 < random.random()) and not detected:
                    self.flip = not self.flip
                elif self.velocity[0] == 0:
                    movement = (movement[0]-1 if self.flip else movement[0]+1,movement[1])
                self.walking = max(self.walking-1,0)
            elif random.random() < 0.1 and not attack: 
                self.walking = random.randint(30, 120)
        super().update(tilemap, movement)
    
    def render(self, surf, scroll=(0,0)):
        super().render(surf, scroll)

class grade4_0(enemy):
    def __init__(self, game, pos, size):
        self.detecting_range = 100
        self.attack_range = 50
        super().__init__(game, pos, size)

class player(Physics_Entity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.punching = 0
        self.punch_count = 0
        self.special = {"up": 0, "side": 0, "down":0, "neutral": 0}
        self.cursed_energy = 0

    def update(self, tilemap, movement=(0,0)):

        super().update(tilemap, movement)
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            self.set_action("wall_slide")
            if self.collisions['right']:
                self.flip = True
            else:
                self.flip = False

        self.punching = max(self.punching -1, 0)

        if self.dashing > 0:
            self.dashing = max(self.dashing -1, 0)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing+1)
        if abs(self.dashing) > 890:
            self.velocity[0] = abs(self.dashing)/self.dashing*8
            if abs(self.dashing) == 891:
                self.velocity[0] *= 0.1
        for key in self.special:
            self.special[key] = max(0, self.special[key]-1)
        if pygame.key.get_pressed()[pygame.K_o] and movement == (0, 0):
            if not (pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_d]):
                self.set_action("focus")
                self.cursed_energy += 20/60
                self.special["neutral"] = 1
        print(self.cursed_energy)


        if not self.wall_slide and self.punching <= 5 and self.special["up"] <= 1190 and self.special["side"] <= 1490 and self.special["neutral"] == 0:
            if self.air_time > 4:
                self.set_action("jump")
            elif movement[0] != 0:
                self.set_action("walk")
            else:
                self.set_action("idle")
    
    def render(self, surf, scroll=(0, 0)):
        super().render(surf, scroll)

    def jump(self):
        if self.wall_slide:
            if not self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.jumps = max(0, self.jumps-1)
                self.air_time = 5
                return True
            if self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.jumps = max(0, self.jumps-1)
                self.air_time = 5
                return True

        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -900
            else:
                self.dashing = 900
    
    def punch(self, scroll= (0,0)):
        alts = pygame.key.get_pressed()
        size = (5, 50)
        vel = [-5 if self.flip else 5, 0]
        stun = 10
        if self.flip:
            pos = [self.rect().centerx-10-scroll[0], self.pos[1]-scroll[1]]
        else:
            pos = [self.rect().centerx +10-scroll[0], self.pos[1]-scroll[1]]
        if not self.punching:
            self.punching = 15
            time = 10
            if self.punch_count < 3:
                self.set_action("punch_" + str(self.punch_count))
                power = [0.5 * self.punch_count+2 * (-1 if self.flip else 1), 0]
                hploss = self.punch_count + 2
            else:
                if alts[pygame.K_w]:
                    self.velocity[1] = -2
                    hploss = 5
                    power = [1 * (-1 if self.flip else 1), -5]
                    self.set_action("uppercut")
                elif alts[pygame.K_s]:
                    hploss = 4
                    power = [0, 2]
                    self.set_action("groundslam")
                else:
                    hploss = 6
                    power = [5 * (-1 if self.flip else 1), 0]
                    self.set_action("frontsmash")

            self.punch_count = (self.punch_count+1)%4
            self.game.hitbox.append([pos, vel, size, power, "player", hploss, time, stun])

    def cursed_technique(self, scroll= (0,0)):
        alts = pygame.key.get_pressed()
        size = (5, 50)
        vel = [-5 if self.flip else 5, 0]
        time = 10
        stun = 10
        black_flash = 0
        if self.flip:
            pos = [self.rect().centerx-10-scroll[0], self.pos[1]-scroll[1]]
        else:
            pos = [self.rect().centerx +10-scroll[0], self.pos[1]-scroll[1]]
            time = 10
        if alts[pygame.K_w] and not self.special["up"]:
            self.special["up"] = 1200
            self.velocity[1] = -2
            hploss = 12 + self.cursed_energy * 0.1
            power = [1 * (-1 if self.flip else 1), -5]
            self.set_action("uppercut")
            self.game.hitbox.append([pos, vel, size, power, "player", hploss, time, stun])
        elif (alts[pygame.K_d] or alts[pygame.K_a]) and not self.special["side"]:
            if random.randint(0,100)+self.cursed_energy/4 >= 100:
                black_flash = 1
            self.special["side"] = 1500
            hploss = 16 + self.cursed_energy * 0.2
            power = [5 * (-1 if self.flip else 1), 0]
            self.set_action("divfist")
            extras = []
            if black_flash == 1:
                extras = [(255, 0, 0), "black_flash"]
                hploss *= 1.5
            
            self.game.hitbox.append([pos, vel, size, power, "player", hploss, time, stun, extras])