import pygame
import json

NEIGBOUR_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (0, 0), (0,-2)]
PHYSICS_TILE = {"street"}

class TileMap:
    def __init__(self, game, tilesize = 50):
        self.game = game
        self.tilesize = tilesize
        self.tilemap = {}
        self.offgrid_tiles = []

        for i in range(10):
            self.tilemap[str(0+i) +";3"] = {"type":"street", "variant" : 0, "pos" : (0+i, 3)}
    
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= self.tilesize
                matches[-1]["pos"][1] *= self.tilesize
                if not keep:
                    del self.tilemap[loc]
        return matches
    
    def solid_check(self, pos):
        tile_loc = str(int(pos[0]//self.tilesize)) + ";" + str(int(pos[1]//self.tilesize))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]["type"] in PHYSICS_TILE:
                return self.tilemap[tile_loc]["type"]

                

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0]//self.tilesize), int(pos[1]//self.tilesize))
        for offset in NEIGBOUR_OFFSET:
            check_loc = str(tile_loc[0] + offset[0]) + ";" + str(tile_loc[1] + offset[1]) 
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile["type"] in PHYSICS_TILE:
                rects.append(pygame.Rect(tile["pos"][0] *self.tilesize, tile["pos"][1] * self.tilesize, self.tilesize, self.tilesize))
        return rects
    
    def save(self, path):
        f = open(path, "w")
        json.dump({"tilemap": self.tilemap, "tilesize":self.tilesize, "offgrid_tiles":self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, "r")
        world = json.load(f)
        f.close()
        self.tilemap = world["tilemap"]
        self.tilesize = world["tilesize"]
        self.offgrid_tiles = world["offgrid_tiles"]

    def render(self, surf, scroll = (0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile["type"]][tile["variant"]], (tile['pos'][0]-scroll[0], tile['pos'][1] -scroll[1]))

        for x in range(scroll[0]//self.tilesize, (scroll[0] + surf.get_width())//self.tilesize+1):
            for y in range(scroll[1]//self.tilesize, (scroll[1] + surf.get_height())//self.tilesize+1):
                loc = str(x) + ";" + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile["type"]][tile["variant"]], (tile['pos'][0]* self.tilesize-scroll[0], tile['pos'][1] *self.tilesize-scroll[1]))
       
