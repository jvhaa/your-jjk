import pygame, sys, random, math

from scripts.entity import Physics_Entity, player, grade4_0
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import TileMap
from scripts.stars import stars
from scripts.particle import Particle
from scripts.sparks import Spark

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('jjk')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.move = [False, False]

        self.assets = {
            "street" : load_images("street"),
            "background" : load_image("night.png"),
            "stars" : load_images("Stars"),
            "city_background" : load_images("city_background"),
            "spawner" : load_images("spawner"),
            "cursed_spirit/idle" : Animation(load_images("curse"), 3, True),
            "player/idle" : Animation(load_images("idle"), 1, True),
            "player/walk" : Animation(load_images("walk"), 10, True),
            "player/jump" : Animation(load_images("jump"), 1, True),
            "player/wall_slide": Animation(load_images("wall_slide"), 1, True),
            "player/punch_0" : Animation(load_images("punch1"), 5, False),
            "player/punch_1" : Animation(load_images("punch2"), 5, False),
            "player/punch_2" : Animation(load_images("punch3"), 5, False),
            "player/groundslam" : Animation(load_images("groundslam"), 5, False),
            "player/frontsmash" : Animation(load_images("frontsmash"), 5, False),
            "player/uppercut" : Animation(load_images("punch1"), 5, False),
            "player/divfist" : Animation(load_images("divfist"), 10, False),
            "player/focus" : Animation(load_images("focus"), 1, False),
            "particle/lights" : Animation(load_images("particle/lights"), 1, True),
            "particle/black_flash": Animation(load_images("particle/black_flash"), 10)
        }

        self.player = player(self, (100, 0), (25, 37))
        self.Tilemap = TileMap(self)
        self.stars = stars(self.assets["stars"])
        self.hitbox = []
        
        self.scroll = [0, 0]
        self.load_map(0)
        
    def run(self):
        while True:

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.light:
                if random.random()* 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random()*rect.width, rect.y + random.random()*rect.height)
                    self.particles.append(Particle(self, "lights", pos, (random.randint(-1, 1)/10, 0.1)))

            self.display.fill((0, 0, 0))

            self.stars.render(self.display, render_scroll)
            self.stars.update()

            self.display.blit(self.assets["background"], (0, 0))

            for hitbox in self.hitbox.copy():
                hitbox[0][0] += hitbox[1][0]
                hitbox[0][1] += hitbox[1][1]
                pygame.draw.rect(self.display, (255, 0, 0), pygame.Rect(hitbox[0][0], hitbox[0][1], hitbox[2][0], hitbox[2][1]))
                self.hitbox[self.hitbox.index(hitbox)][6] -= 1
                if hitbox[6] <= 0: 
                    self.hitbox.remove(hitbox)
                if hitbox[4] == "player": 
                    for enemies in self.enemies:
                        e_rect = enemies.rect()
                        e_rect.x -= render_scroll[0]
                        e_rect.y -= render_scroll[1]
                        if pygame.Rect(hitbox[0][0], hitbox[0][1], hitbox[2][0], hitbox[2][1]).colliderect(e_rect) and not enemies.stun:
                            enemies.hp -= hitbox[5]
                            enemies.velocity = hitbox[3]
                            enemies.stun = hitbox[7]
                            color = (255, 255, 255)

                            if len(hitbox) > 8:
                                color = hitbox[8][0]
                                part = hitbox[8][1]
                                self.particles.append(Particle(self, part, (hitbox[0][0]+render_scroll[0], hitbox[0][1]+render_scroll[1]), (0,0), 0))
                            for i in range(4):
                                if hitbox[1][0] > 0:
                                    self.sparks.append(Spark([enemies.rect().x, enemies.rect().centery], (random.random()*0.6 - 1)*math.pi, 3, color))
                                if hitbox[1][0] < 0:
                                    self.sparks.append(Spark([enemies.rect().x+enemies.rect().width, enemies.rect().centery], (-0.5 + random.random()*0.6)*math.pi, 3, color))
                else:
                    p_rect = self.player.rect()
                    p_rect.x -= render_scroll[0]
                    p_rect.y -= render_scroll[1]
                    if pygame.Rect(hitbox[0][0], hitbox[0][1], hitbox[2][0], hitbox[2][1]).colliderect(p_rect):
                            self.player.hp -= hitbox[5]
                            self.player.velocity = hitbox[3]
                            self.hitbox.remove(hitbox)
                            for i in range(4):
                                if hitbox[1][0] > 0:
                                    self.sparks.append(Spark([self.player.rect().x, self.player.rect().centery], (random.random()*0.6 - 1)*math.pi, 3))
                                if hitbox[1][0] < 0:
                                    self.sparks.append(Spark([self.player.rect().x+self.player.rect().width, self.player.rect().centery], (-0.5 + random.random()*0.6)*math.pi, 3))


            for enemy in self.enemies.copy():
                enemy.update(self.Tilemap, render_scroll)
                enemy.render(self.display, render_scroll)
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    for i in range(8):
                        self.sparks.append(Spark(enemies.rect().center, random.random()-0.5+math.pi, 4))

            self.player.update(self.Tilemap, ((self.move[1]-self.move[0]), 0))
            self.player.render(self.display, render_scroll)

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, render_scroll)
                if kill == True:
                    self.sparks.remove(spark)

            for particle in self.particles.copy():
                kill = particle.update()     
                particle.render(self.display, render_scroll)
                if kill == True:
                    self.particles.remove(particle)

            self.Tilemap.render(self.display, render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.move[0] = True
                    if event.key == pygame.K_d:
                        self.move[1] = True
                    if event.key == pygame.K_w:
                        self.player.jump()
                    if event.key == pygame.K_q:
                        self.player.dash()
                    if event.key == pygame.K_p:
                        self.player.punch(render_scroll)
                    if event.key == pygame.K_o:
                        self.player.cursed_technique(render_scroll)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.move[0] = False
                    if event.key == pygame.K_d:
                        self.move[1] = False
            pygame.display.update()
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.clock.tick(60)
            
    def load_map(self, map_id):
        self.Tilemap.load("maps/" + str(map_id) + ".json")

        self.enemies = []
        self.light = []
        self.particles = []
        self.sparks = []
    
        for street_light in self.Tilemap.extract([("city_background", 0)], True):
            self.light.append(pygame.Rect(street_light['pos'][0], street_light['pos'][1]+10, 10, 10))
        
        for spawner in self.Tilemap.extract([("spawner", 0), ("spawner", 1)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
            elif spawner["variant"] == 1:
                self.enemies.append(grade4_0(self, spawner['pos'], (20, 20)))

Game().run()