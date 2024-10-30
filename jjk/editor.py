import pygame, sys
import json
from scripts.utils import load_images
from scripts.tilemap import TileMap
RENDER_SCALE = 2.0

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.move = [False, False, False, False]

        self.assets = {
            "street" : load_images("street"),
            "city_background" : load_images("city_background"),
            "spawner" : load_images("spawner"),
        }

        self.Tilemap = TileMap(self)
        self.tilelist = list(self.assets)
        self.tilegroup = 0
        self.tilevariant = 0
        
        self.scroll = [0, 0]

        self.click = False
        self.rightclick = False
        self.shift = False
        self.ongrid = True

        try:
            self.Tilemap.load("maps/0.json")
        except FileNotFoundError:
            print('nuh uh')
    
    def run(self):
        while True:
            self.scroll[0] += (self.move[1] - self.move[0]) *2
            self.scroll[1] += (self.move[3] - self.move[2]) *2 
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            current_tile = self.assets[self.tilelist[self.tilegroup]][self.tilevariant].copy()
            current_tile.set_alpha(100)
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] /RENDER_SCALE, mpos[1]/RENDER_SCALE)
            tile_pos = int((mpos[0]+self.scroll[0])//self.Tilemap.tilesize), int((mpos[1]+self.scroll[1])//self.Tilemap.tilesize)
            if self.click and self.ongrid:
                self.Tilemap.tilemap[str(tile_pos[0]) +";" + str(tile_pos[1])] = {"type": self.tilelist[self.tilegroup], 'variant': self.tilevariant, "pos": tile_pos}
            if self.rightclick:
                tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])
                if tile_loc in self.Tilemap.tilemap:
                    del self.Tilemap.tilemap[tile_loc]
                for tile in self.Tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.Tilemap.offgrid_tiles.remove(tile)
            self.display.blit(self.assets["city_background"][0], (100, 100))

            self.display.fill((0, 0, 0))
            self.Tilemap.render(self.display, render_scroll)
            if self.ongrid:
                self.display.blit(current_tile, (tile_pos[0]*self.Tilemap.tilesize-self.scroll[0], tile_pos[1]*self.Tilemap.tilesize-self.scroll[1]))
            else:
                self.display.blit(current_tile, mpos)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                        if not self.ongrid:
                            self.Tilemap.offgrid_tiles.append({"type": self.tilelist[self.tilegroup], 'variant': self.tilevariant, "pos": (mpos[0]+self.scroll[0], mpos[1]+self.scroll[1])})
                    if event.button == 3:
                        self.rightclick = True
                    if not self.shift:
                        if event.button == 4:
                            self.tilevariant = (self.tilevariant+1) % len(self.assets[self.tilelist[self.tilegroup]])
                        if event.button == 5:
                            self.tilevariant = (self.tilevariant+1) % len(self.assets[self.tilelist[self.tilegroup]])
                    else:
                        if event.button == 4:
                            self.tilevariant = 0
                            self.tilegroup = (self.tilegroup+1) % len(self.tilelist)
                        if event.button == 5:
                            self.tilevariant = 0
                            self.tilegroup = (self.tilegroup+1) % len(self.tilelist)
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.click = False
                    if event.button == 3:
                        self.rightclick = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.move[0] = True
                    if event.key == pygame.K_d:
                        self.move[1] = True
                    if event.key == pygame.K_w:
                        self.move[2] = True
                    if event.key == pygame.K_s:
                        self.move[3] = True
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.Tilemap.save("maps/0.json")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.move[0] = False
                    if event.key == pygame.K_d:
                        self.move[1] = False
                    if event.key == pygame.K_w:
                        self.move[2] = False
                    if event.key == pygame.K_s:
                        self.move[3] = False
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.shift = False
            pygame.display.update()
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.clock.tick(60)

Game().run()