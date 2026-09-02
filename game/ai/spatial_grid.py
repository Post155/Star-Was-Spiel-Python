"""
spatial_grid.py
Simple uniform grid for neighbor/obstacle queries. Not highly optimized but reduces O(N^2) queries.
"""
from collections import defaultdict
import math

class SpatialGrid:
    def __init__(self, world_rect, cell_size=300):
        self.cell_size = max(1, int(cell_size))
        self.origin_x = world_rect[0]
        self.origin_y = world_rect[1]
        self.cols = max(1, int(math.ceil((world_rect[2]) / self.cell_size)))
        self.rows = max(1, int(math.ceil((world_rect[3]) / self.cell_size)))
        self.cells = defaultdict(list)

    def _cell_coords(self, x, y):
        cx = int((x - self.origin_x) // self.cell_size)
        cy = int((y - self.origin_y) // self.cell_size)
        return cx, cy

    def clear(self):
        self.cells.clear()

    def insert(self, obj, pos):
        cx, cy = self._cell_coords(pos[0], pos[1])
        self.cells[(cx,cy)].append((obj, pos))

    def query_radius(self, pos, radius):
        cx, cy = self._cell_coords(pos[0], pos[1])
        rad_cells = int(math.ceil(radius / self.cell_size))
        results = []
        for dx in range(-rad_cells, rad_cells+1):
            for dy in range(-rad_cells, rad_cells+1):
                for (o, p) in self.cells.get((cx+dx, cy+dy), []):
                    results.append((o, p))
        return results
