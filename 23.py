#!/usr/bin/env python3

import functools
from sys import stderr, stdin
from typing import List

def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

valid_next_directions = {
    '>': ((1, 0),),
    '<': ((-1, 0),),
    '^': ((0, -1),),
    'v': ((0, 1),),
    '.': ((1, 0), (-1, 0), (0, 1), (0, -1)),
}

class Grid(object):
    def __init__(self, input_data: List[str]):
        self.grid = input_data

    def find_start(self):
        y = 0
        x = self.grid[y].index('.')
        assert(x != -1)
        return (x, y)

    def find_end(self):
        y = len(self.grid) - 1
        x = self.grid[y].index('.')
        assert(x != -1)
        return (x, y)

    def longest_path(self, start, end):
        # Now, do a breadth-first search to find all reachable cells
        to_visit = [(start, 0, set())]
        total_dist = None
        while to_visit:
            pos, dist, visited = to_visit.pop(0)
            x, y = pos
            assert((x, y) not in visited)
            visited.add((x, y))
            if (x, y) == end:
                total_dist = dist
            first = True
            for dx, dy in valid_next_directions[self.grid[y][x]]:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= len(self.grid[0]):
                    continue
                if ny < 0 or ny >= len(self.grid):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.grid[ny][nx] == '#':
                    continue
                to_visit.append(((nx, ny), dist + 1, visited if first else visited.copy()))
                first = False
        return total_dist

def main():
    input_data = [line.rstrip() for line in stdin.read().splitlines()]
    grid = Grid(input_data)

    start = grid.find_start()
    end = grid.find_end()
    print(grid.longest_path(start, end))


if __name__ == '__main__':
    main()
